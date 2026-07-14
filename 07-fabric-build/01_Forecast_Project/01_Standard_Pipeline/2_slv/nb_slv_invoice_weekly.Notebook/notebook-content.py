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

TARGET_TABLE = 'slv_invoice_weekly'

LAKEHOUSE = "SupplyChain_Lakehouse"
SCHEMA    = "dbo"
DB        = f'{LAKEHOUSE}.{SCHEMA}'

SQL_TRANSFORM = f'''
WITH current_fiscal AS (
    SELECT num_fsc_year
    FROM {DB}.ref_calendar
    WHERE dt_date = CURRENT_DATE()
    LIMIT 1
)

SELECT
    /* ── Grain Keys ── */
    INV.id_account_ship_to,
    INV.id_item_sku,
    INV.code_warehouse,
    INV.code_customer_group,
    CAL.dt_fsc_week_first,
    CAL.dt_fsc_week_last,

    /* ── Measures ── */
    SUM(INV.qty_shipped)                                 AS qty_shipped,
    SUM(INV.amt_net_sales)                               AS amt_net_sales,
    SUM(INV.amt_invoice)                                 AS amt_invoice,
    SUM(INV.amt_freight)                                 AS amt_freight,
    COUNT(*)                                             AS num_invoice_lines,
    COUNT(DISTINCT INV.id_invoice)                       AS num_distinct_invoices

FROM {DB}.slv_invoice_detail_line_level              AS INV

INNER JOIN {DB}.ref_calendar                              AS CAL
    ON  CAL.dt_date = INV.dt_invoice

CROSS JOIN current_fiscal                                AS CF

WHERE
    INV.qty_shipped > 0
    AND CAL.num_fsc_year >= CF.num_fsc_year - 3

GROUP BY
    INV.id_account_ship_to,
    INV.id_item_sku,
    INV.code_warehouse,
    INV.code_customer_group,
    CAL.dt_fsc_week_first,
    CAL.dt_fsc_week_last
'''

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

notebookutils.notebook.run(
    "slv_engine",
    7200,
    {
        "TARGET_TABLE":   TARGET_TABLE,
        "SQL_TRANSFORM":  SQL_TRANSFORM
    }
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
