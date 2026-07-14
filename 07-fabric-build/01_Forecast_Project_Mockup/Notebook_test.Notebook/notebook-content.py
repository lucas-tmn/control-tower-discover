# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "62a3081e-4093-4f46-856c-f50aa58732fa",
# META       "default_lakehouse_name": "SupplyChain_Lakehouse",
# META       "default_lakehouse_workspace_id": "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0",
# META       "known_lakehouses": [
# META         {
# META           "id": "62a3081e-4093-4f46-856c-f50aa58732fa"
# META         }
# META       ]
# META     },
# META     "warehouse": {
# META       "default_warehouse": "9a31b24e-3e73-9b7e-46a7-d907e146ffe2",
# META       "known_warehouses": [
# META         {
# META           "id": "9a31b24e-3e73-9b7e-46a7-d907e146ffe2",
# META           "type": "Datawarehouse"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

import requests, json, base64, re, time

token = mssparkutils.credentials.getToken("https://api.fabric.microsoft.com")
workspace_id = spark.conf.get("trident.workspace.id")
headers = {"Authorization": f"Bearer {token}"}

url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items?type=Notebook"
notebooks = requests.get(url, headers=headers).json().get("value", [])

def extract_tables(content):
    tables_read = set()
    tables_write = set()
    
    # Remove single-line comments
    content = re.sub(r'--.*', '', content)
    # Remove block comments
    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
    
    # Collect CTE names to exclude
    cte_names = set(re.findall(
        r'(?:WITH|,)\s+([a-zA-Z_]\w*)\s+AS\s*\(', content, re.IGNORECASE
    ))
    
    # Write targets: CREATE OR REPLACE TABLE / INSERT INTO
    for m in re.findall(
        r'(?:CREATE\s+(?:OR\s+REPLACE\s+)?TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?)([a-zA-Z_]\w*(?:\.\w+)*)',
        content, re.IGNORECASE
    ):
        tables_write.add(m)
    
    for m in re.findall(
        r'(?:INSERT\s+(?:INTO|OVERWRITE)\s+(?:TABLE\s+)?)([a-zA-Z_]\w*(?:\.\w+)*)',
        content, re.IGNORECASE
    ):
        tables_write.add(m)
    
    # .saveAsTable / .insertInto
    for m in re.findall(r'\.(?:saveAsTable|insertInto)\(["\']([^"\']+)["\']\)', content):
        tables_write.add(m)
    
    # Read sources: FROM / JOIN (all types)
    for m in re.findall(
        r'(?:FROM|(?:LEFT|RIGHT|INNER|OUTER|CROSS|FULL)\s+(?:OUTER\s+)?JOIN|JOIN)\s+([a-zA-Z_]\w*(?:\.\w+)*)',
        content, re.IGNORECASE
    ):
        tables_read.add(m)
    
    # spark.read.table / spark.table
    for m in re.findall(r'spark\.(?:read\.)?table\(["\']([^"\']+)["\']\)', content):
        tables_read.add(m)
    
    # Filter
    skip = {
        'select','where','set','if','table','view','as','on','and','or',
        'not','null','true','false','case','when','then','else','end',
        'group','order','by','having','limit','union','all','distinct',
        'exists','between','like','in','is','dual','temp','temporary',
        'current_fiscal','cf'  # common CTE aliases
    }
    skip.update({c.lower() for c in cte_names})
    
    tables_read = {t for t in tables_read if t.lower() not in skip and len(t) > 2}
    tables_write = {t for t in tables_write if t.lower() not in skip and len(t) > 2}
    
    # Remove write targets from read (don't self-reference)
    tables_read -= tables_write
    
    return sorted(tables_read), sorted(tables_write)

def get_notebook_content(nb_id):
    defn_url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks/{nb_id}/getDefinition"
    r = requests.post(defn_url, headers=headers)
    
    if r.status_code == 200:
        return r.json()
    if r.status_code == 202:
        loc = r.headers.get("Location") or r.headers.get("location")
        if loc:
            for _ in range(20):
                time.sleep(3)
                poll = requests.get(loc, headers=headers)
                if poll.status_code == 200:
                    data = poll.json()
                    if data.get("status") == "Succeeded":
                        return data
                    if data.get("status") == "Failed":
                        return None
    return None

results = {}

for nb in sorted(notebooks, key=lambda x: x["displayName"]):
    nb_name = nb["displayName"]
    defn = get_notebook_content(nb["id"])
    
    if not defn:
        print(f"SKIP (no content): {nb_name}")
        continue
    
    # Try to get notebook content from parts
    full_content = ""
    parts = defn.get("definition", {}).get("parts", [])
    
    for part in parts:
        payload = part.get("payload", "")
        if not payload:
            continue
        
        # Try base64 decode
        try:
            decoded = base64.b64decode(payload).decode("utf-8")
        except:
            decoded = payload
        
        # Parse as ipynb JSON (cells -> source)
        try:
            nb_json = json.loads(decoded)
            if "cells" in nb_json:
                for cell in nb_json["cells"]:
                    src = cell.get("source", [])
                    if isinstance(src, list):
                        full_content += "\n".join(src) + "\n"
                    elif isinstance(src, str):
                        full_content += src + "\n"
                continue
        except:
            pass
        
        # If not JSON, use raw content
        full_content += decoded + "\n"
    
    if full_content.strip():
        reads, writes = extract_tables(full_content)
        if reads or writes:
            results[nb_name] = {"reads": reads, "writes": writes}

# Print
print(f"\n{'='*60}")
print(f"LINEAGE: {len(results)} notebooks with dependencies")
print(f"{'='*60}")

for nb_name, info in sorted(results.items()):
    print(f"\n📓 {nb_name}")
    if info["writes"]:
        print(f"  WRITES → {', '.join(info['writes'])}")
    if info["reads"]:
        for t in info["reads"]:
            print(f"  READS  ← {t}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
