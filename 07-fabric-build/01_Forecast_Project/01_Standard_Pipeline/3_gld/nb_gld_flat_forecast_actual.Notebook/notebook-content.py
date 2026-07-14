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
# META     }
# META   }
# META }

# CELL ********************

# ============================================================================
# [GLD] nb_etl_gld_flat_forecast_actual
# Gold: Flat Forecast vs Actual (UNION ALL for accuracy reporting)
#
# Sources:
#   - slv_actual_demand_monthly (invoiced + open orders)
#   - slv_forecast_demand_monthly (snapshot-based forecast)
#   - slv_naive_forecast_monthly (rolling naive benchmark)
#
# Transformations:
#   - UNION ALL three SLV fact tables
#   - Standardize columns across sources
#   - Single grain: Item × Warehouse × CustomerGroup × FiscalMonth × Status × Version
#
# Load Type: overwrite (full reload every run)
# ============================================================================

TARGET_TABLE = 'gld_flat_forecast_actual'

LAKEHOUSE = "SupplyChain_Lakehouse"
SCHEMA    = "dbo"
DB        = f'{LAKEHOUSE}.{SCHEMA}'

SQL_AGGREGATE = f'''
/* ── Actual Demand ── */
SELECT
    TRIM(id_item_sku) AS id_item_sku,
    TRIM(code_warehouse) AS code_warehouse,
    TRIM(code_customer_group) AS code_customer_group,
    CAST(dt_fsc_month_first AS DATE) AS dt_fsc_month_first,
    CAST(dt_fsc_month_last AS DATE) AS dt_fsc_month_last,
    'Actual demand' AS code_horizon,
    TRIM(code_status) AS code_status,
    TRIM(name_version) AS name_version,
    CAST(qty_demand AS DOUBLE) AS qty
FROM {DB}.slv_actual_demand_monthly

UNION ALL

/* ── Forecast Demand ── */
SELECT
    TRIM(id_item_sku) AS id_item_sku,
    TRIM(code_warehouse) AS code_warehouse,
    TRIM(code_customer_group) AS code_customer_group,
    CAST(dt_fsc_month_first AS DATE) AS dt_fsc_month_first,
    CAST(dt_fsc_month_last AS DATE) AS dt_fsc_month_last,
    TRIM(code_horizon) AS code_horizon,
    TRIM(code_status) AS code_status,
    TRIM(code_version) AS name_version,
    CAST(qty_forecast AS DOUBLE) AS qty
FROM {DB}.slv_forecast_demand_monthly

UNION ALL

/* ── Naive Forecast ── */
SELECT
    TRIM(id_item_sku) AS id_item_sku,
    TRIM(code_warehouse) AS code_warehouse,
    TRIM(code_customer_group) AS code_customer_group,
    CAST(dt_fsc_month_first AS DATE) AS dt_fsc_month_first,
    CAST(dt_fsc_month_last AS DATE) AS dt_fsc_month_last,
    'Naive forecast' AS code_horizon,
    TRIM(code_status) AS code_status,
    TRIM(name_version) AS name_version,
    CAST(qty_demand AS DOUBLE) AS qty
FROM {DB}.slv_naive_forecast_monthly
'''

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

notebookutils.notebook.run(
    "gld_engine",
    7200,
    {
        "TARGET_TABLE":   TARGET_TABLE,
        "SQL_AGGREGATE":  SQL_AGGREGATE
    }
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
