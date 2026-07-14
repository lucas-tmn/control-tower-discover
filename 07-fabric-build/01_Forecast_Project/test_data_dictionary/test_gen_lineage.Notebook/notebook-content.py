# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

"""
Fabric Notebook Lineage Scanner
================================
Convention-aware parser for SupplyChain notebooks.
Understands the brz_engine / slv_engine / gld_engine delegation pattern.

Run as a Fabric notebook (uses mssparkutils for auth + Fabric REST API).
"""

import requests, json, base64, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
import notebookutils.mssparkutils as mssparkutils

# --- Auth ---
token = mssparkutils.credentials.getToken("https://api.fabric.microsoft.com")
headers = {"Authorization": f"Bearer {token}"}

# --- Config ---
workspace_id = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"
prefix = "nb_"
max_workers = 3  # keep low to avoid Fabric API rate limits

# ============================================================
# REGEX PATTERNS
# ============================================================

# Variable assignments
RE_TARGET_TABLE = re.compile(
    r'''TARGET_TABLE\s*=\s*(?:f?["']([^"']+)["'])''')
RE_SOURCE_TABLE = re.compile(
    r'''SOURCE_TABLE\s*=\s*(?:f?["']([^"']+)["'])''')

# SQL variable blocks (triple-quoted f-strings)
RE_SQL_TRANSFORM = re.compile(
    r'''SQL_TRANSFORM\s*=\s*f?(?:'{3}|"{3})(.*?)(?:'{3}|"{3})''', re.DOTALL)
RE_SQL_AGGREGATE = re.compile(
    r'''SQL_AGGREGATE\s*=\s*f?(?:'{3}|"{3})(.*?)(?:'{3}|"{3})''', re.DOTALL)
RE_COLUMN_SQL = re.compile(
    r'''COLUMN_SQL\s*=\s*(?:f?(?:'{3}|"{3})(.*?)(?:'{3}|"{3})|f?["'](.*?)["'])''', re.DOTALL)

# SQL table references
RE_FROM_JOIN = re.compile(
    r'''(?:FROM|(?:LEFT|RIGHT|INNER|OUTER|CROSS|FULL)\s+(?:OUTER\s+)?JOIN|JOIN)'''
    r'''\s+(?:\{[^}]*\}\.)?`?([a-zA-Z_]\w*(?:\.\w+)*)`?''',
    re.IGNORECASE)
RE_CTE = re.compile(
    r'''(?:WITH|,)\s+([a-zA-Z_]\w*)\s+AS\s*\(''', re.IGNORECASE)

# Cross-notebook calls
RE_NOTEBOOK_RUN = re.compile(
    r'''notebookutils\.notebook\.run\(\s*["']([^"']+)["']''')
RE_PERCENT_RUN = re.compile(
    r'''^%run\s+(\S+)''', re.MULTILINE)

# Inline brz patterns (for custom notebooks that don't use brz_engine)
RE_SAVE_AS_TABLE = re.compile(r'''\.saveAsTable\(\s*(?:["']([^"']+)["']|(\w+))''')
RE_READ_LOAD = re.compile(r'''\.read\.format\([^)]*\).*?\.load\(''', re.DOTALL)
RE_SPARK_SQL = re.compile(
    r"""spark\.sql\(\s*(?:f?\"\"\"(.*?)\"\"\"|f?'''(.*?)'''|f?\"([^\"]*)\"|f?'([^']*)')\s*\)""",
    re.DOTALL)

# Comments
RE_LINE_COMMENT = re.compile(r'--.*')
RE_BLOCK_COMMENT = re.compile(r'/\*.*?\*/', re.DOTALL)

SKIP_WORDS = frozenset({
    'select', 'where', 'set', 'if', 'table', 'view', 'as', 'on', 'and', 'or',
    'not', 'null', 'true', 'false', 'case', 'when', 'then', 'else', 'end',
    'group', 'order', 'by', 'having', 'limit', 'union', 'all', 'distinct',
    'exists', 'between', 'like', 'in', 'is', 'dual', 'temp', 'temporary',
    'raw_source',  # brz_engine temp view, not a real table
})


# Fabric .py notebook markers
RE_FABRIC_MARKER = re.compile(
    r'^(?:#|--)\s*(?:MAGIC|META\b|CELL\s*\*|METADATA\s*\*|Fabric notebook source).*$',
    re.MULTILINE)
RE_MAGIC_PREFIX = re.compile(r'^(?:#|--)\s*MAGIC\s?', re.MULTILINE)


# ============================================================
# PARSING
# ============================================================

def clean_py_format(code):
    """Strip Fabric .py notebook markers to get clean code."""
    code = RE_FABRIC_MARKER.sub('', code)
    code = RE_MAGIC_PREFIX.sub('', code)
    return code


def extract_cells(ipynb_json):
    """Extract code cell source from ipynb JSON."""
    parts = []
    for cell in ipynb_json.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        src = cell.get("source", [])
        if isinstance(src, list):
            parts.append("".join(src))
        elif isinstance(src, str):
            parts.append(src)
    return "\n".join(parts)


def extract_tables_from_sql(sql):
    """Extract table names from SQL, stripping DB prefix and CTEs."""
    sql = RE_LINE_COMMENT.sub('', sql)
    sql = RE_BLOCK_COMMENT.sub('', sql)

    # Remove {DB}. or SupplyChain_Lakehouse.dbo. prefix (handled by regex)
    cte_names = {m.lower() for m in RE_CTE.findall(sql)}
    tables = set(RE_FROM_JOIN.findall(sql))
    tables = {t for t in tables if t.lower() not in SKIP_WORDS | cte_names and len(t) > 2}
    return sorted(tables)


def parse_notebook(nb_name, code):
    """
    Convention-aware parsing. Returns dict with:
      layer, target_table, source_table, reads, writes, calls_engine, calls_notebooks
    """
    result = {
        "layer": None,
        "target_table": None,
        "source_table": None,
        "reads": [],
        "writes": [],
        "calls_engine": None,
        "calls_notebooks": [],
    }

    # --- Detect layer from name ---
    name_lower = nb_name.lower()
    if name_lower.startswith("nb_brz_"):
        result["layer"] = "brz"
    elif name_lower.startswith("nb_ref_"):
        result["layer"] = "ref"
    elif name_lower.startswith("nb_slv_"):
        result["layer"] = "slv"
    elif name_lower.startswith("nb_gld_"):
        result["layer"] = "gld"
    elif name_lower.startswith("nb_sp_"):
        result["layer"] = "sp"
    elif name_lower.startswith("nb_utl_"):
        result["layer"] = "utl"

    # --- Extract variable assignments ---
    m = RE_TARGET_TABLE.search(code)
    if m:
        result["target_table"] = m.group(1)

    m = RE_SOURCE_TABLE.search(code)
    if m:
        result["source_table"] = m.group(1)

    # --- Detect engine calls ---
    for m in RE_NOTEBOOK_RUN.finditer(code):
        called = m.group(1)
        if called.endswith("_engine"):
            result["calls_engine"] = called
        else:
            result["calls_notebooks"].append(called)

    for m in RE_PERCENT_RUN.finditer(code):
        called = m.group(1)
        if called.endswith("_engine"):
            result["calls_engine"] = called
        else:
            result["calls_notebooks"].append(called)

    # --- Parse based on convention ---
    layer = result["layer"]
    target = result["target_table"]

    if target:
        result["writes"].append(target)

    if layer in ("brz", "ref"):
        # brz/ref: reads from external source, writes TARGET_TABLE
        src = result["source_table"]
        if src:
            result["reads"].append(f"[external] {src}")

        # Also check COLUMN_SQL for any extra table refs (beyond raw_source)
        m = RE_COLUMN_SQL.search(code)
        if m:
            sql = m.group(1) or m.group(2) or ""
            extra = extract_tables_from_sql(sql)
            result["reads"].extend(extra)

    elif layer == "slv":
        # slv: reads from SQL_TRANSFORM, writes TARGET_TABLE
        m = RE_SQL_TRANSFORM.search(code)
        if m:
            sql = m.group(1)
            result["reads"] = extract_tables_from_sql(sql)

    elif layer == "gld":
        # gld: reads from SQL_AGGREGATE, writes TARGET_TABLE
        m = RE_SQL_AGGREGATE.search(code)
        if m:
            sql = m.group(1)
            result["reads"] = extract_tables_from_sql(sql)

    elif layer == "sp":
        # sp: orchestrator, no direct table I/O
        pass

    elif layer == "utl":
        # utl: utility, may have direct spark.sql
        pass

    # --- Fallback: if no convention match, scan for inline patterns ---
    if not result["reads"] and not result["source_table"] and layer not in ("sp",):
        # Check for spark.sql() calls
        for m in RE_SPARK_SQL.finditer(code):
            sql = m.group(1) or m.group(2) or m.group(3) or m.group(4) or ""
            if sql.strip():
                tables = extract_tables_from_sql(sql)
                result["reads"].extend(tables)
        # Deduplicate
        result["reads"] = sorted(set(result["reads"]))

    return result


# ============================================================
# API: fetch notebook definitions
# ============================================================

def get_notebook_content(nb_id):
    defn_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks/{nb_id}/getDefinition"
    r = requests.post(defn_url, headers=headers)

    if r.status_code == 200:
        return r.json()
    if r.status_code == 202:
        loc = r.headers.get("Location") or r.headers.get("location")
        retry_after = int(r.headers.get("Retry-After", "3"))
        if loc:
            for _ in range(60):
                time.sleep(retry_after)
                poll = requests.get(loc, headers=headers)
                if poll.status_code == 200:
                    data = poll.json()
                    status = data.get("status", "")
                    if status == "Succeeded":
                        # Result may be inline or at /result endpoint
                        if "definition" in data:
                            return data
                        result_url = loc.rstrip("/") + "/result"
                        result = requests.get(result_url, headers=headers)
                        if result.status_code == 200:
                            return result.json()
                        return None
                    if status == "Failed":
                        return None
                elif poll.status_code == 202:
                    continue  # still in progress
    if r.status_code == 429:
        time.sleep(int(r.headers.get("Retry-After", "10")))
        return get_notebook_content(nb_id)
    return None


def decode_notebook(defn):
    """Decode API response → code string. Handles both .ipynb JSON and .py formats."""
    parts_code = []
    for part in defn.get("definition", {}).get("parts", []):
        payload = part.get("payload", "")
        if not payload:
            continue
        try:
            decoded = base64.b64decode(payload).decode("utf-8")
        except Exception:
            decoded = payload
        try:
            nb_json = json.loads(decoded)
            if "cells" in nb_json:
                parts_code.append(extract_cells(nb_json))
                continue
        except Exception:
            pass
        # Fallback: .py format or raw code (Fabric notebook Python export)
        parts_code.append(clean_py_format(decoded))
    return "\n".join(parts_code)


def scan_notebook(nb):
    nb_name = nb["displayName"]
    defn = get_notebook_content(nb["id"])
    if not defn:
        return nb_name, None
    code = decode_notebook(defn)
    if not code.strip():
        return nb_name, None
    return nb_name, parse_notebook(nb_name, code)


# ============================================================
# MAIN
# ============================================================

# 1. List notebooks
url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items?type=Notebook"
all_notebooks = requests.get(url, headers=headers).json().get("value", [])
notebooks = [nb for nb in all_notebooks if nb["displayName"].startswith(prefix)]
print(f"Found {len(notebooks)} notebooks with prefix '{prefix}' (total: {len(all_notebooks)})")

# 2. Scan in parallel
results = {}
with ThreadPoolExecutor(max_workers=max_workers) as executor:
    futures = {executor.submit(scan_notebook, nb): nb["displayName"] for nb in notebooks}
    for future in as_completed(futures):
        nb_name = futures[future]
        try:
            name, data = future.result()
            if data and (data["reads"] or data["writes"]):
                results[name] = data
                print(f"  OK: {name} [{data['layer']}] "
                      f"(reads={len(data['reads'])}, writes={len(data['writes'])})")
            elif data:
                print(f"  SKIP: {name} (no table I/O)")
            else:
                print(f"  SKIP: {name} (empty/unreadable)")
        except Exception as e:
            print(f"  ERROR: {nb_name} - {e}")

# 3. Build lineage
write_map = {}  # table -> [notebook_names that write it]
for nb_name, info in results.items():
    for t in info["writes"]:
        write_map.setdefault(t, []).append(nb_name)

print(f"\n{'='*70}")
print(f"TABLE LINEAGE: {len(results)} notebooks")
print(f"{'='*70}")

for nb_name, info in sorted(results.items()):
    layer_tag = f"[{info['layer']}]" if info['layer'] else ""
    print(f"\n  {nb_name} {layer_tag}")
    if info["writes"]:
        print(f"    WRITES -> {', '.join(info['writes'])}")
    if info["reads"]:
        for t in info["reads"]:
            print(f"    READS  <- {t}")

# 4. Cross-notebook lineage links
links = []
for nb_name, info in results.items():
    for t in info["reads"]:
        if t.startswith("[external]"):
            continue
        if t in write_map:
            for producer in write_map[t]:
                if producer != nb_name:
                    links.append((producer, t, nb_name))

if links:
    print(f"\n{'='*70}")
    print("CROSS-NOTEBOOK LINEAGE LINKS")
    print(f"{'='*70}")
    for producer, table, consumer in sorted(links):
        print(f"  {producer}  --[{table}]-->  {consumer}")
else:
    print(f"\n(No cross-notebook lineage links found)")

# 5. Summary
print(f"\n{'='*70}")
print("SUMMARY")
print(f"{'='*70}")
layers = {}
for info in results.values():
    l = info.get("layer") or "other"
    layers[l] = layers.get(l, 0) + 1
for l, c in sorted(layers.items()):
    print(f"  {l}: {c} notebooks")
print(f"  Total links: {len(links)}")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
