# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {}
# META }

# CELL ********************

pip install streamlit

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

"""
Data Dictionary App - Streamlit UI
Connect to Local SQL Server or Fabric Lakehouse, scan all tables, display & edit metadata.

Run: streamlit run data_dictionary_app.py
"""

import os
import struct
import pyodbc
import streamlit as st
import pandas as pd
import json
from datetime import datetime
from pathlib import Path
from sqlalchemy import create_engine, text

# ════════════════════════════════════════
# Page Config
# ════════════════════════════════════════
st.set_page_config(
    page_title="Data Dictionary",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════
# Environment Configs
# ════════════════════════════════════════
FABRIC_SERVER = "7woj2wroypauvkpn72b56t46ju-qp6ntsfwdaou5atebne65u3p4a.datawarehouse.fabric.microsoft.com"

ENV_CONFIGS = {
    "local": {
        "label": "Local SQL Server",
        "fabric": False,
        "odbc": (
            "DRIVER={SQL Server};"
            "Server=.;"
            "Database=forecast_furniture;"
            "Trusted_Connection=yes;"
            "Encrypt=no;"
            "TrustServerCertificate=yes;"
            "Command Timeout=0"
        ),
    },
    "fabric_dev": {
        "label": "Fabric - SupplyChain_Lakehouse_Dev",
        "fabric": True,
        "odbc": (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"Server={FABRIC_SERVER},1433;"
            "Database=SupplyChain_Lakehouse;"
            "Encrypt=yes;"
            "TrustServerCertificate=no"
        ),
    },
    "fabric_prod": {
        "label": "Fabric - SupplyChain_Lakehouse (Prod)",
        "fabric": True,
        "odbc": (
            "DRIVER={ODBC Driver 18 for SQL Server};"
            f"Server={FABRIC_SERVER},1433;"
            "Database=SupplyChain_Lakehouse;"
            "Encrypt=yes;"
            "TrustServerCertificate=no"
        ),
    },
}

# Azure AD token for Fabric SQL endpoint
SQL_COPT_SS_ACCESS_TOKEN = 1256  # pyodbc constant for access token


@st.cache_resource(ttl=2400)  # token valid ~1hr, refresh every 40min
def _get_fabric_token():
    """Get Azure AD token for Fabric SQL endpoint using azure-identity."""
    from azure.identity import DefaultAzureCredential
    credential = DefaultAzureCredential()
    token = credential.get_token("https://database.windows.net/.default")
    return token.token


# ════════════════════════════════════════
# Connection
# ════════════════════════════════════════
def _is_fabric() -> bool:
    return st.session_state.env.startswith("fabric")


def _get_fabric_connection():
    """Create a pyodbc connection to Fabric with Azure AD token."""
    token = _get_fabric_token()
    token_bytes = token.encode("utf-16-le")
    token_struct = struct.pack(f"<I{len(token_bytes)}s", len(token_bytes), token_bytes)
    odbc_string = ENV_CONFIGS[st.session_state.env]["odbc"]
    return pyodbc.connect(odbc_string, attrs_before={SQL_COPT_SS_ACCESS_TOKEN: token_struct})


@st.cache_resource
def get_engine(env_key: str):
    """SQLAlchemy engine for local SQL Server only."""
    odbc_string = ENV_CONFIGS[env_key]["odbc"]
    return create_engine(f"mssql+pyodbc:///?odbc_connect={odbc_string}")


def run_query(sql: str) -> pd.DataFrame:
    if _is_fabric():
        conn = _get_fabric_connection()
        try:
            return pd.read_sql(sql, conn)
        finally:
            conn.close()
    with get_engine(st.session_state.env).connect() as conn:
        return pd.read_sql(text(sql), conn)


def run_non_query(sql: str):
    if _is_fabric():
        conn = _get_fabric_connection()
        try:
            conn.execute(sql)
            conn.commit()
        finally:
            conn.close()
        return
    with get_engine(st.session_state.env).connect() as conn:
        conn.execute(text(sql))
        conn.commit()


def run_non_query_params(sql: str, params: dict):
    if _is_fabric():
        # Convert :param style to ? style for pyodbc
        import re
        param_names = re.findall(r":(\w+)", sql)
        sql_qmark = re.sub(r":(\w+)", "?", sql)
        values = [params[name] for name in param_names]
        conn = _get_fabric_connection()
        try:
            conn.execute(sql_qmark, values)
            conn.commit()
        finally:
            conn.close()
        return
    with get_engine(st.session_state.env).connect() as conn:
        conn.execute(text(sql), params)
        conn.commit()


# ════════════════════════════════════════
# Constants & Layer Detection
# ════════════════════════════════════════
LAYER_PREFIXES = {
    "brz": "brz",
    "slv": "slv", "gld": "gld", "ref": "ref",
    "dq": "dq", "dd": "dd", "utl": "utl",
}
EXCLUDE_PREFIXES = ["dd_", "br2"]

LAYER_COLORS = {
    "brz": "#fbbf24", "slv": "#7dd3fc", "gld": "#fde047",
    "ref": "#86efac", "dq": "#c084fc", "utl": "#94a3b8", "other": "#94a3b8",
}


def _safe_get(row, key, default=None):
    """Safely get a value from a pandas row, returning default if key missing or NaN."""
    try:
        val = row[key]
        return default if pd.isna(val) else val
    except (KeyError, IndexError):
        return default


def detect_layer(table_name: str) -> str:
    for prefix, layer in LAYER_PREFIXES.items():
        if table_name.startswith(prefix + "_"):
            return layer
    return "other"


# ════════════════════════════════════════
# DDL: Ensure dd_tables & dd_columns exist
# ════════════════════════════════════════
def ensure_dd_tables():
    if _is_fabric():
        # Fabric SQL endpoint is read-only for DDL via ODBC.
        # dd_tables/dd_columns must be created in Fabric notebook.
        # Try both with and without dbo schema.
        last_err = None
        for prefix in ("dbo.", "SupplyChain_Lakehouse.dbo.", ""):
            try:
                run_query(f"SELECT TOP 1 table_name FROM {prefix}dd_tables")
                return  # found
            except Exception as e:
                last_err = e
                continue
        # Show actual error to help debug
        st.warning(
            f"Cannot read `dd_tables` from Fabric. Error: `{last_err}`\n\n"
            "Possible causes:\n"
            "- Tables `dd_tables`/`dd_columns` not created yet → run `nb_dd_run` notebook in Fabric\n"
            "- Connection issue → check ODBC Driver 18, Azure AD login\n"
            "- SQL endpoint not enabled for this Lakehouse"
        )
        return

    # Local SQL Server - create if not exists
    run_non_query("""
        IF OBJECT_ID('dbo.dd_tables', 'U') IS NULL
        CREATE TABLE dbo.dd_tables (
            table_name        NVARCHAR(255) NOT NULL PRIMARY KEY,
            layer             NVARCHAR(50)  NOT NULL,
            row_count         BIGINT,
            column_count      INT,
            description       NVARCHAR(MAX),
            business_owner    NVARCHAR(255),
            source_system     NVARCHAR(255),
            refresh_frequency NVARCHAR(100),
            tags              NVARCHAR(MAX),
            scanned_at        NVARCHAR(50)  NOT NULL,
            updated_at        NVARCHAR(50),
            updated_by        NVARCHAR(255)
        )
    """)
    run_non_query("""
        IF OBJECT_ID('dbo.dd_columns', 'U') IS NULL
        CREATE TABLE dbo.dd_columns (
            table_name       NVARCHAR(255) NOT NULL,
            column_name      NVARCHAR(255) NOT NULL,
            data_type        NVARCHAR(100) NOT NULL,
            ordinal_position INT           NOT NULL,
            is_nullable      NVARCHAR(10),
            is_primary_key   BIT DEFAULT 0,
            description      NVARCHAR(MAX),
            business_name    NVARCHAR(255),
            sample_values    NVARCHAR(MAX),
            null_percentage  FLOAT,
            distinct_count   BIGINT,
            scanned_at       NVARCHAR(50)  NOT NULL,
            updated_at       NVARCHAR(50),
            updated_by       NVARCHAR(255),
            PRIMARY KEY (table_name, column_name)
        )
    """)


# ════════════════════════════════════════
# Scanner
# ════════════════════════════════════════
def list_tables() -> list[str]:
    df = run_query("""
        SELECT TABLE_NAME
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_TYPE = 'BASE TABLE'
        ORDER BY TABLE_NAME
    """)
    names = df["TABLE_NAME"].tolist()
    return [n for n in names if not any(n.startswith(p) for p in EXCLUDE_PREFIXES)]


def get_primary_keys(table_name: str) -> set[str]:
    df = run_query(f"""
        SELECT kcu.COLUMN_NAME
        FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS tc
        JOIN INFORMATION_SCHEMA.KEY_COLUMN_USAGE kcu
          ON tc.CONSTRAINT_NAME = kcu.CONSTRAINT_NAME
        WHERE tc.TABLE_NAME = '{table_name}'
          AND tc.CONSTRAINT_TYPE = 'PRIMARY KEY'
    """)
    return set(df["COLUMN_NAME"].tolist()) if not df.empty else set()


def scan_one_table(table_name: str) -> tuple[dict, pd.DataFrame]:
    now = datetime.now().isoformat()
    rc = run_query(f"SELECT COUNT(*) AS cnt FROM [dbo].[{table_name}]")
    row_count = int(rc["cnt"].iloc[0])

    cols = run_query(f"""
        SELECT COLUMN_NAME, DATA_TYPE, ORDINAL_POSITION, IS_NULLABLE
        FROM INFORMATION_SCHEMA.COLUMNS
        WHERE TABLE_SCHEMA = 'dbo' AND TABLE_NAME = '{table_name}'
        ORDER BY ORDINAL_POSITION
    """)

    tbl_meta = {
        "table_name": table_name,
        "layer": detect_layer(table_name),
        "row_count": row_count,
        "column_count": len(cols),
        "scanned_at": now,
    }
    return tbl_meta, cols


def scan_columns(table_name: str, cols_df: pd.DataFrame, row_count: int) -> list[dict]:
    now = datetime.now().isoformat()
    pks = get_primary_keys(table_name)
    results = []

    # Build batch query for null% and distinct count
    if not cols_df.empty and row_count > 0:
        agg_parts = []
        for _, row in cols_df.iterrows():
            cn = row["COLUMN_NAME"]
            agg_parts.append(
                f"SUM(CASE WHEN [{cn}] IS NULL THEN 1 ELSE 0 END) AS [{cn}__nulls], "
                f"COUNT(DISTINCT [{cn}]) AS [{cn}__dist]"
            )
        agg_sql = f"SELECT COUNT(*) AS total_rows, {', '.join(agg_parts)} FROM [dbo].[{table_name}]"
        try:
            stats = run_query(agg_sql)
            stats_row = stats.iloc[0]
        except Exception:
            stats_row = None
    else:
        stats_row = None

    for _, row in cols_df.iterrows():
        cn = row["COLUMN_NAME"]

        null_pct = None
        dist_count = None
        if stats_row is not None and row_count > 0:
            try:
                nulls = int(stats_row[f"{cn}__nulls"])
                null_pct = round(nulls / row_count * 100, 2)
                dist_count = int(stats_row[f"{cn}__dist"])
            except Exception:
                pass

        # Sample values
        sample = None
        try:
            sdf = run_query(
                f"SELECT DISTINCT TOP 5 CAST([{cn}] AS NVARCHAR(200)) AS val "
                f"FROM [dbo].[{table_name}] WHERE [{cn}] IS NOT NULL"
            )
            if not sdf.empty:
                sample = " | ".join(sdf["val"].astype(str).tolist())
        except Exception:
            pass

        results.append({
            "table_name": table_name,
            "column_name": cn,
            "data_type": row["DATA_TYPE"],
            "ordinal_position": int(row["ORDINAL_POSITION"]),
            "is_nullable": row["IS_NULLABLE"],
            "is_primary_key": 1 if cn in pks else 0,
            "null_percentage": null_pct,
            "distinct_count": dist_count,
            "sample_values": sample,
            "scanned_at": now,
        })

    return results


# ════════════════════════════════════════
# Save / Load
# ════════════════════════════════════════
def load_existing_table_descs() -> dict:
    try:
        df = run_query("""
            SELECT table_name, description, business_owner, source_system,
                   refresh_frequency, tags, updated_at, updated_by
            FROM dbo.dd_tables
        """)
        return {row["table_name"]: row.to_dict() for _, row in df.iterrows()}
    except Exception:
        return {}


def load_existing_col_descs() -> dict:
    try:
        df = run_query("""
            SELECT table_name, column_name, description, business_name,
                   is_primary_key, updated_at, updated_by
            FROM dbo.dd_columns
        """)
        return {
            (row["table_name"], row["column_name"]): row.to_dict()
            for _, row in df.iterrows()
        }
    except Exception:
        return {}


def save_scan_results(tables: list[dict], columns: list[dict]):
    old_tbl = load_existing_table_descs()
    old_col = load_existing_col_descs()

    # Merge table descriptions
    for t in tables:
        if t["table_name"] in old_tbl:
            old = old_tbl[t["table_name"]]
            for f in ("description", "business_owner", "source_system",
                       "refresh_frequency", "tags", "updated_at", "updated_by"):
                t[f] = old.get(f) or t.get(f)

    # Merge column descriptions
    for c in columns:
        key = (c["table_name"], c["column_name"])
        if key in old_col:
            old = old_col[key]
            for f in ("description", "business_name", "is_primary_key",
                       "updated_at", "updated_by"):
                c[f] = old.get(f) or c.get(f)

    # Upsert tables
    for t in tables:
        for k in ["table_name", "layer", "row_count", "column_count", "description",
                   "business_owner", "source_system", "refresh_frequency", "tags",
                   "scanned_at", "updated_at", "updated_by"]:
            t.setdefault(k, None)

        run_non_query_params("""
            MERGE dbo.dd_tables AS target
            USING (SELECT :table_name AS table_name) AS source
            ON target.table_name = source.table_name
            WHEN MATCHED THEN UPDATE SET
                layer = :layer, row_count = :row_count, column_count = :column_count,
                description = :description, business_owner = :business_owner,
                source_system = :source_system, refresh_frequency = :refresh_frequency,
                tags = :tags, scanned_at = :scanned_at,
                updated_at = :updated_at, updated_by = :updated_by
            WHEN NOT MATCHED THEN INSERT
                (table_name, layer, row_count, column_count, description, business_owner,
                 source_system, refresh_frequency, tags, scanned_at, updated_at, updated_by)
            VALUES (:table_name, :layer, :row_count, :column_count, :description,
                    :business_owner, :source_system, :refresh_frequency, :tags,
                    :scanned_at, :updated_at, :updated_by);
        """, t)

    # Upsert columns
    for c in columns:
        for k in ["table_name", "column_name", "data_type", "ordinal_position",
                   "is_nullable", "is_primary_key", "description", "business_name",
                   "sample_values", "null_percentage", "distinct_count", "scanned_at",
                   "updated_at", "updated_by"]:
            c.setdefault(k, None)

        run_non_query_params("""
            MERGE dbo.dd_columns AS target
            USING (SELECT :table_name AS table_name, :column_name AS column_name) AS source
            ON target.table_name = source.table_name AND target.column_name = source.column_name
            WHEN MATCHED THEN UPDATE SET
                data_type = :data_type, ordinal_position = :ordinal_position,
                is_nullable = :is_nullable, is_primary_key = :is_primary_key,
                description = :description, business_name = :business_name,
                sample_values = :sample_values, null_percentage = :null_percentage,
                distinct_count = :distinct_count, scanned_at = :scanned_at,
                updated_at = :updated_at, updated_by = :updated_by
            WHEN NOT MATCHED THEN INSERT
                (table_name, column_name, data_type, ordinal_position, is_nullable,
                 is_primary_key, description, business_name, sample_values,
                 null_percentage, distinct_count, scanned_at, updated_at, updated_by)
            VALUES (:table_name, :column_name, :data_type, :ordinal_position,
                    :is_nullable, :is_primary_key, :description, :business_name,
                    :sample_values, :null_percentage, :distinct_count,
                    :scanned_at, :updated_at, :updated_by);
        """, c)


def load_dd_tables() -> pd.DataFrame:
    try:
        df = run_query("SELECT * FROM dbo.dd_tables ORDER BY layer, table_name")
        if _is_fabric():
            df = _apply_table_overrides(df)
        return df
    except Exception:
        return pd.DataFrame()


def load_dd_columns(table_name: str | None = None) -> pd.DataFrame:
    try:
        if table_name:
            df = run_query(
                f"SELECT * FROM dbo.dd_columns WHERE table_name = '{table_name}' "
                f"ORDER BY ordinal_position"
            )
        else:
            df = run_query("SELECT * FROM dbo.dd_columns ORDER BY table_name, ordinal_position")
        if _is_fabric():
            df = _apply_column_overrides(df)
        return df
    except Exception:
        return pd.DataFrame()


def update_table_fields(table_name: str, fields: dict):
    if _is_fabric():
        _save_table_override(table_name, fields)
        return
    now = datetime.now().isoformat()
    fields["updated_at"] = now
    set_parts = ", ".join(f"{k} = :{k}" for k in fields)
    fields["_table_name"] = table_name
    run_non_query_params(
        f"UPDATE dbo.dd_tables SET {set_parts} WHERE table_name = :_table_name",
        fields,
    )


def update_column_fields(table_name: str, column_name: str, fields: dict):
    if _is_fabric():
        _save_column_override(table_name, column_name, fields)
        return
    now = datetime.now().isoformat()
    fields["updated_at"] = now
    set_parts = ", ".join(f"{k} = :{k}" for k in fields)
    fields["_table_name"] = table_name
    fields["_column_name"] = column_name
    run_non_query_params(
        f"UPDATE dbo.dd_columns SET {set_parts} "
        f"WHERE table_name = :_table_name AND column_name = :_column_name",
        fields,
    )


def export_json() -> str:
    tables = load_dd_tables()
    columns = load_dd_columns()
    result = []
    for _, row in tables.iterrows():
        t = row.to_dict()
        tbl_cols = columns[columns["table_name"] == row["table_name"]]
        t["columns"] = tbl_cols.to_dict("records")
        result.append(t)
    return json.dumps(result, indent=2, default=str)


# ════════════════════════════════════════
# Local Overrides (for Fabric read-only mode)
# ════════════════════════════════════════
OVERRIDES_FILE = Path(__file__).parent / "dd_overrides.json"


def _load_overrides() -> dict:
    """Load local overrides from JSON file."""
    if OVERRIDES_FILE.exists():
        return json.loads(OVERRIDES_FILE.read_text(encoding="utf-8"))
    return {"tables": {}, "columns": {}}


def _save_overrides(data: dict):
    """Save local overrides to JSON file."""
    OVERRIDES_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _save_table_override(table_name: str, fields: dict):
    """Save table-level edits to local JSON."""
    ov = _load_overrides()
    ov["tables"].setdefault(table_name, {})
    ov["tables"][table_name].update({k: v for k, v in fields.items() if v})
    ov["tables"][table_name]["updated_at"] = datetime.now().isoformat()
    _save_overrides(ov)


def _save_column_override(table_name: str, column_name: str, fields: dict):
    """Save column-level edits to local JSON."""
    ov = _load_overrides()
    key = f"{table_name}::{column_name}"
    ov["columns"].setdefault(key, {"table_name": table_name, "column_name": column_name})
    ov["columns"][key].update({k: v for k, v in fields.items() if v is not None})
    ov["columns"][key]["updated_at"] = datetime.now().isoformat()
    _save_overrides(ov)


def _apply_table_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """Merge local overrides into dd_tables DataFrame."""
    ov = _load_overrides()
    if not ov["tables"] or df.empty:
        return df
    df = df.copy()
    for tbl_name, fields in ov["tables"].items():
        mask = df["table_name"] == tbl_name
        if mask.any():
            for k, v in fields.items():
                if k in df.columns:
                    df.loc[mask, k] = v
    return df


def _apply_column_overrides(df: pd.DataFrame) -> pd.DataFrame:
    """Merge local overrides into dd_columns DataFrame."""
    ov = _load_overrides()
    if not ov["columns"] or df.empty:
        return df
    df = df.copy()
    for _, fields in ov["columns"].items():
        tbl = fields.get("table_name")
        col = fields.get("column_name")
        mask = (df["table_name"] == tbl) & (df["column_name"] == col)
        if mask.any():
            for k, v in fields.items():
                if k in df.columns and k not in ("table_name", "column_name"):
                    df.loc[mask, k] = v
    return df


def _generate_fabric_code() -> str | None:
    """Generate self-contained Python code for Fabric notebook."""
    ov = _load_overrides()
    if not ov["tables"] and not ov["columns"]:
        return None

    # Build the MERGE statements directly - no dependency on dd_update functions
    db = "SupplyChain_Lakehouse.dbo"
    lines = [
        "# ════════════════════════════════════════",
        "# Auto-generated from Data Dictionary App",
        "# Paste into a Fabric notebook cell and run",
        "# ════════════════════════════════════════",
        f'DB = "{db}"',
        "from datetime import datetime",
        "now = datetime.now().isoformat()",
        "",
    ]

    # Table updates via Spark SQL MERGE
    for tbl, fields in ov.get("tables", {}).items():
        clean = {k: v for k, v in fields.items() if k != "updated_at" and v}
        if not clean:
            continue
        clean["updated_at"] = "' + now + '"
        set_parts = ", ".join(f"{k} = '{v}'" for k, v in clean.items())
        safe_tbl = tbl.replace("'", "''")
        lines.append(f"spark.sql(f'''")
        lines.append(f"    MERGE INTO {{DB}}.dd_tables AS t")
        lines.append(f"    USING (SELECT '{safe_tbl}' AS table_name) AS s")
        lines.append(f"    ON t.table_name = s.table_name")
        lines.append(f"    WHEN MATCHED THEN UPDATE SET {set_parts}")
        lines.append(f"''')")
        lines.append(f"print('Updated table: {tbl}')")
        lines.append("")

    # Column updates via Spark SQL MERGE
    for _, fields in ov.get("columns", {}).items():
        tbl = fields["table_name"]
        col = fields["column_name"]
        clean = {k: v for k, v in fields.items()
                 if k not in ("table_name", "column_name", "updated_at") and v is not None}
        if not clean:
            continue
        clean["updated_at"] = "' + now + '"
        set_parts = ", ".join(f"{k} = '{v}'" for k, v in clean.items())
        safe_tbl = tbl.replace("'", "''")
        safe_col = col.replace("'", "''")
        lines.append(f"spark.sql(f'''")
        lines.append(f"    MERGE INTO {{DB}}.dd_columns AS t")
        lines.append(f"    USING (SELECT '{safe_tbl}' AS table_name, '{safe_col}' AS column_name) AS s")
        lines.append(f"    ON t.table_name = s.table_name AND t.column_name = s.column_name")
        lines.append(f"    WHEN MATCHED THEN UPDATE SET {set_parts}")
        lines.append(f"''')")
        lines.append(f"print('Updated column: {tbl}.{col}')")
        lines.append("")

    lines.append("print('Done!')")
    return "\n".join(lines)


def _clear_overrides():
    """Clear all local overrides after syncing to Fabric."""
    _save_overrides({"tables": {}, "columns": {}})


# ════════════════════════════════════════
# AI Suggestions (Groq - free)
# ════════════════════════════════════════
# Get free API key at: https://console.groq.com/keys
# Set env var: GROQ_API_KEY=your_key

GROQ_MODEL = "llama-3.3-70b-versatile"
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")


def _call_ai(prompt: str, max_tokens: int = 2000) -> str:
    """Call Groq API."""
    import requests as req
    api_key = GROQ_API_KEY
    r = req.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.2,
        },
        timeout=30,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def _parse_json_response(text: str):
    """Extract JSON from AI response (handles markdown code blocks)."""
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def ai_suggest_table(table_name: str, layer: str, columns_df: pd.DataFrame) -> dict:
    """Ask AI to suggest table metadata based on name and columns."""
    col_info = []
    for _, row in columns_df.head(30).iterrows():
        parts = [f"{row.get('column_name', '?')} ({row.get('data_type', '?')})"]
        sample = _safe_get(row, "sample_values")
        if sample:
            parts.append(f"samples: {sample}")
        col_info.append(" - ".join(parts))

    prompt = f"""You are a data dictionary assistant for a supply chain analytics lakehouse.

Table: {table_name}
Layer: {layer} (brz=raw/bronze, slv=cleaned/silver, gld=aggregated/gold, ref=reference/master)
Columns:
{chr(10).join(col_info)}

Based on the table name, layer, column names, data types and sample values, suggest:
1. description: A concise English business description (1-2 sentences)
2. business_owner: Which team likely owns this (e.g. "Supply Chain", "Sales", "Finance", "Analytics")
3. source_system: The likely source system
4. tags: Comma-separated relevant tags
5. refresh_frequency: One of: hourly, daily, weekly, monthly, ad-hoc

Respond in JSON format only, no explanation:
{{"description": "...", "business_owner": "...", "source_system": "...", "tags": "...", "refresh_frequency": "..."}}"""

    return _parse_json_response(_call_ai(prompt, 500))


def ai_suggest_columns(table_name: str, layer: str, columns_df: pd.DataFrame) -> list[dict]:
    """Ask AI to suggest column descriptions and business names."""
    col_info = []
    for _, row in columns_df.iterrows():
        parts = [row.get("column_name", "?"), row.get("data_type", "?")]
        sample = _safe_get(row, "sample_values")
        if sample:
            parts.append(f"samples: {sample}")
        null_pct = _safe_get(row, "null_percentage")
        if null_pct is not None:
            parts.append(f"null: {null_pct}%")
        col_info.append(" | ".join(parts))

    prompt = f"""You are a data dictionary assistant for a supply chain analytics lakehouse.

Table: {table_name} (layer: {layer})
Columns:
{chr(10).join(col_info)}

Column naming convention:
- id_* = identifiers/keys, code_* = category codes, name_* = descriptive text
- dt_* = date, ts_* = timestamp, amt_* = monetary, qty_* = quantity
- num_* = count, val_* = values, pct_* = percentage, is_* = boolean, sk_* = surrogate key

For each column, suggest:
- description: Concise English description
- business_name: Human-readable English business name

Respond as a JSON array only, no explanation:
[{{"column_name": "...", "description": "...", "business_name": "..."}}, ...]"""

    return _parse_json_response(_call_ai(prompt, 2000))


# ════════════════════════════════════════
# Custom CSS
# ════════════════════════════════════════
st.markdown("""
<style>
    .layer-badge {
        display: inline-block;
        padding: 2px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 700;
        font-family: monospace;
    }
    .metric-card {
        background: #1e293b;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        color: #e2e8f0;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        margin-top: 4px;
    }
    div[data-testid="stSidebar"] .stRadio label {
        font-size: 13px !important;
    }
</style>
""", unsafe_allow_html=True)


# ════════════════════════════════════════
# Initialize session state
# ════════════════════════════════════════
if "env" not in st.session_state:
    st.session_state.env = "local"
if "selected_table" not in st.session_state:
    st.session_state.selected_table = None


# ════════════════════════════════════════
# Sidebar
# ════════════════════════════════════════
with st.sidebar:
    st.title("📖 Data Dictionary")

    # Environment selector
    env_options = list(ENV_CONFIGS.keys())
    env_labels = [ENV_CONFIGS[k]["label"] for k in env_options]
    current_idx = env_options.index(st.session_state.env)
    selected_env = st.selectbox(
        "Environment",
        env_options,
        index=current_idx,
        format_func=lambda k: ENV_CONFIGS[k]["label"],
    )
    if selected_env != st.session_state.env:
        st.session_state.env = selected_env
        st.session_state.selected_table = None
        st.rerun()

    st.caption(ENV_CONFIGS[st.session_state.env]["label"])

    # Ensure dd_tables exist for this env
    try:
        ensure_dd_tables()
    except Exception as e:
        st.error(f"Connection failed: `{type(e).__name__}: {e}`")
        st.stop()

    # Scan button (disabled for Fabric - scan via notebook)
    if st.button("🔄 Scan Database", use_container_width=True, type="primary",
                 disabled=_is_fabric()):
        tables_to_scan = list_tables()
        all_tables = []
        all_columns = []
        progress = st.progress(0, text="Scanning...")

        for i, name in enumerate(tables_to_scan):
            progress.progress(
                (i + 1) / len(tables_to_scan),
                text=f"Scanning {name}... ({i+1}/{len(tables_to_scan)})",
            )
            try:
                tbl_meta, cols_df = scan_one_table(name)
                all_tables.append(tbl_meta)
                col_results = scan_columns(name, cols_df, tbl_meta["row_count"])
                all_columns.extend(col_results)
            except Exception as e:
                st.warning(f"Skip {name}: {e}")

        save_scan_results(all_tables, all_columns)
        progress.empty()
        st.success(f"Scanned {len(all_tables)} tables, {len(all_columns)} columns")
        st.rerun()

    st.divider()

    # Load data
    dd_tables = load_dd_tables()

    if dd_tables.empty:
        st.info("No data yet. Click **Scan Database** to start.")
        st.stop()

    # Coverage stats
    total_tables = len(dd_tables)
    described_tables = dd_tables["description"].notna().sum() if "description" in dd_tables.columns else 0
    tbl_coverage = round(described_tables / total_tables * 100) if total_tables else 0

    col1, col2 = st.columns(2)
    col1.metric("Tables", total_tables)
    col2.metric("Coverage", f"{tbl_coverage}%")

    st.divider()

    # Search
    search = st.text_input("🔍 Search tables", placeholder="Type to filter...")

    # Layer filter
    layers = sorted(dd_tables["layer"].unique().tolist())
    layer_filter = st.multiselect("Filter by layer", layers, default=layers)

    st.divider()

    # Filter tables
    filtered = dd_tables[dd_tables["layer"].isin(layer_filter)]
    if search:
        mask = (
            filtered["table_name"].str.contains(search, case=False, na=False)
            | filtered["description"].str.contains(search, case=False, na=False)
        )
        filtered = filtered[mask]

    # Table list
    table_names = filtered["table_name"].tolist()
    if table_names:
        # Build display labels with layer prefix
        labels = []
        for _, row in filtered.iterrows():
            layer_tag = row["layer"].upper()
            name = row["table_name"]
            rc = _safe_get(row, "row_count")
            rows = f"{int(rc):,}" if rc is not None else "?"
            labels.append(f"[{layer_tag}] {name} ({rows} rows)")

        selected_idx = st.radio(
            "Tables",
            range(len(table_names)),
            format_func=lambda i: labels[i],
            label_visibility="collapsed",
        )
        st.session_state.selected_table = table_names[selected_idx]
    else:
        st.warning("No tables match your filter.")
        st.session_state.selected_table = None

    st.divider()

    # Export
    st.download_button(
        "📥 Export JSON",
        data=export_json(),
        file_name="data_dictionary.json",
        mime="application/json",
        use_container_width=True,
    )

    # Fabric: show pending overrides & generate code
    if _is_fabric():
        ov = _load_overrides()
        n_tbl = len(ov["tables"])
        n_col = len(ov["columns"])
        if n_tbl or n_col:
            st.divider()
            st.warning(f"Pending edits: {n_tbl} tables, {n_col} columns")
            code = _generate_fabric_code()
            if code:
                st.download_button(
                    "📋 Download Code for Fabric",
                    data=code,
                    file_name="dd_updates.py",
                    mime="text/x-python",
                    use_container_width=True,
                )
                with st.expander("Preview generated code"):
                    st.code(code, language="python")
                if st.button("🗑 Clear pending edits", use_container_width=True):
                    _clear_overrides()
                    st.rerun()


# ════════════════════════════════════════
# Main Area
# ════════════════════════════════════════
selected = st.session_state.selected_table

if selected is None:
    # Overview
    st.header("Database Overview")

    dd_all_cols = load_dd_columns()
    total_cols = len(dd_all_cols)
    described_cols = dd_all_cols["description"].notna().sum() if not dd_all_cols.empty else 0
    col_coverage = round(described_cols / total_cols * 100) if total_cols else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Tables", total_tables)
    m2.metric("Total Columns", total_cols)
    m3.metric("Table Coverage", f"{tbl_coverage}%")
    m4.metric("Column Coverage", f"{col_coverage}%")

    st.subheader("Tables by Layer")
    agg_dict = {"table_name": ("table_name", "count")}
    if "row_count" in dd_tables.columns:
        agg_dict["total_rows"] = ("row_count", "sum")
    if "column_count" in dd_tables.columns:
        agg_dict["avg_columns"] = ("column_count", "mean")
    layer_summary = dd_tables.groupby("layer").agg(**agg_dict).reset_index()
    if "avg_columns" in layer_summary.columns:
        layer_summary["avg_columns"] = layer_summary["avg_columns"].round(1)
    st.dataframe(layer_summary, use_container_width=True, hide_index=True)

    st.subheader("All Tables")
    display_cols = ["table_name", "layer", "row_count", "column_count",
                    "description", "business_owner", "scanned_at"]
    available = [c for c in display_cols if c in dd_tables.columns]
    display_df = dd_tables[available]
    st.dataframe(display_df, use_container_width=True, hide_index=True)

else:
    # Table detail view
    tbl_row = dd_tables[dd_tables["table_name"] == selected].iloc[0]
    layer = tbl_row["layer"]
    color = LAYER_COLORS.get(layer, "#94a3b8")

    # Header
    st.markdown(
        f'<span class="layer-badge" style="background:{color}20;color:{color}">'
        f'{layer.upper()}</span> <b style="font-size:24px">{selected}</b>',
        unsafe_allow_html=True,
    )

    # Quick stats
    s1, s2, s3 = st.columns(3)
    rc = _safe_get(tbl_row, "row_count")
    cc = _safe_get(tbl_row, "column_count")
    s1.metric("Rows", f"{int(rc):,}" if rc is not None else "?")
    s2.metric("Columns", int(cc) if cc is not None else "?")
    sa = _safe_get(tbl_row, "scanned_at")
    s3.metric("Last Scanned", str(sa)[:19] if sa is not None else "Never")

    st.divider()

    # Editable table metadata
    st.subheader("Table Metadata")

    # AI suggest for table
    if st.button("🤖 AI Suggest Table Info", key="ai_tbl"):
        try:
            with st.spinner("Asking Gemini..."):
                dd_cols_for_ai = load_dd_columns(selected)
                suggestion = ai_suggest_table(selected, layer, dd_cols_for_ai)
                st.session_state[f"ai_tbl_{selected}"] = suggestion
        except Exception as e:
            st.error(f"AI error: {e}")

    # Apply AI suggestion if available
    ai_tbl = st.session_state.get(f"ai_tbl_{selected}", {})

    with st.form(f"table_meta_{selected}"):
        fc1, fc2 = st.columns(2)
        desc = fc1.text_area(
            "Description",
            value=ai_tbl.get("description") or _safe_get(tbl_row, "description", ""),
            height=80,
        )
        owner = fc2.text_input(
            "Business Owner",
            value=ai_tbl.get("business_owner") or _safe_get(tbl_row, "business_owner", ""),
        )
        fc3, fc4, fc5 = st.columns(3)
        source = fc3.text_input(
            "Source System",
            value=ai_tbl.get("source_system") or _safe_get(tbl_row, "source_system", ""),
        )
        freq_options = ["", "hourly", "daily", "weekly", "monthly", "ad-hoc", "real-time"]
        ai_freq = ai_tbl.get("refresh_frequency", "")
        cur_freq = ai_freq if ai_freq in freq_options else _safe_get(tbl_row, "refresh_frequency", "")
        freq = fc4.selectbox(
            "Refresh Frequency",
            freq_options,
            index=freq_options.index(cur_freq) if cur_freq in freq_options else 0,
        )
        tags = fc5.text_input(
            "Tags (comma-separated)",
            value=ai_tbl.get("tags") or _safe_get(tbl_row, "tags", ""),
        )

        if st.form_submit_button("💾 Save Table Info", type="primary"):
            update_table_fields(selected, {
                "description": desc or None,
                "business_owner": owner or None,
                "source_system": source or None,
                "refresh_frequency": freq or None,
                "tags": tags or None,
            })
            st.success("Table metadata saved!")
            st.rerun()

    st.divider()

    # Column grid
    st.subheader("Columns")
    dd_cols = load_dd_columns(selected)

    if dd_cols.empty:
        st.info("No column data. Run a scan first.")
    else:
        # AI suggest for columns
        if st.button("🤖 AI Suggest All Columns", key="ai_cols"):
            try:
                with st.spinner("Asking Gemini..."):
                    suggestions = ai_suggest_columns(selected, layer, dd_cols)
                    st.session_state[f"ai_cols_{selected}"] = {
                        s["column_name"]: s for s in suggestions
                    }
            except Exception as e:
                st.error(f"AI error: {e}")

        # Apply AI column suggestions into display_df
        ai_cols = st.session_state.get(f"ai_cols_{selected}", {})

        # Prepare editable dataframe
        edit_cols = [
            "column_name", "data_type", "is_primary_key", "is_nullable",
            "null_percentage", "distinct_count", "sample_values",
            "description", "business_name",
        ]
        display_df = dd_cols[[c for c in edit_cols if c in dd_cols.columns]].copy()

        # Apply AI suggestions to empty fields
        if ai_cols:
            for idx, row in display_df.iterrows():
                cn = row.get("column_name", "")
                if cn in ai_cols:
                    s = ai_cols[cn]
                    if "description" in display_df.columns and pd.isna(row.get("description")):
                        display_df.at[idx, "description"] = s.get("description", "")
                    if "business_name" in display_df.columns and pd.isna(row.get("business_name")):
                        display_df.at[idx, "business_name"] = s.get("business_name", "")

        # Convert is_primary_key to bool for checkbox
        if "is_primary_key" in display_df.columns:
            display_df["is_primary_key"] = display_df["is_primary_key"].astype(bool)

        column_config = {
            "column_name": st.column_config.TextColumn("Column", disabled=True),
            "data_type": st.column_config.TextColumn("Type", disabled=True),
            "is_primary_key": st.column_config.CheckboxColumn("PK", width="small"),
            "is_nullable": st.column_config.TextColumn("Nullable", disabled=True, width="small"),
            "null_percentage": st.column_config.NumberColumn("Null %", format="%.1f", disabled=True),
            "distinct_count": st.column_config.NumberColumn("Distinct", disabled=True),
            "sample_values": st.column_config.TextColumn("Samples", disabled=True, width="large"),
            "description": st.column_config.TextColumn("Description", width="large"),
            "business_name": st.column_config.TextColumn("Business Name"),
        }

        edited = st.data_editor(
            display_df,
            column_config=column_config,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key=f"col_editor_{selected}",
        )

        if st.button("💾 Save Column Edits", type="primary"):
            changes = 0
            for idx in range(len(edited)):
                orig_row = display_df.iloc[idx]
                edit_row = edited.iloc[idx]
                col_name = orig_row["column_name"]
                updates = {}
                for field in ["description", "business_name", "is_primary_key"]:
                    if field in orig_row and field in edit_row:
                        ov = orig_row[field]
                        ev = edit_row[field]
                        # Normalize for comparison
                        if pd.isna(ov):
                            ov = None
                        if pd.isna(ev):
                            ev = None
                        if field == "is_primary_key":
                            ov = bool(ov) if ov is not None else False
                            ev = bool(ev) if ev is not None else False
                            if ov != ev:
                                updates[field] = 1 if ev else 0
                        elif str(ov or "") != str(ev or ""):
                            updates[field] = ev
                if updates:
                    update_column_fields(selected, col_name, updates)
                    changes += 1

            if changes:
                st.success(f"Saved {changes} column(s)!")
                st.rerun()
            else:
                st.info("No changes detected.")


# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
