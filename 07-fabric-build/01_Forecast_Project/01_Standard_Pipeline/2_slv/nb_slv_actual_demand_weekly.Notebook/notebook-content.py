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

TARGET_TABLE = 'slv_actual_demand_weekly'

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

/* ── Part 1: Invoiced ── */
SELECT
    INV.id_item_sku,
    INV.code_warehouse,
    CASE WHEN CAL.dt_fsc_week_first < '2025-04-01' THEN 'AFICONS'
        ELSE INV.code_customer_group 
    END AS code_customer_group,
    CAL.dt_fsc_week_first,
    CAL.dt_fsc_week_last,
    SUM(INV.qty_shipped)                                 AS qty_demand,
    SUM(INV.amt_net_sales)                               AS amt_demand,
    'Invoice'                                            AS code_status,
    'Actual Demand'                                      AS name_version

FROM {DB}.slv_invoice_detail_line_level                   AS INV
INNER JOIN {DB}.ref_calendar                              AS CAL
    ON  CAL.dt_date = DATEADD(DAY, -INV.num_lead_time_days, INV.dt_current_request)
CROSS JOIN current_fiscal                                AS CF

WHERE
    INV.qty_shipped > 0
    AND CAL.num_fsc_year BETWEEN CF.num_fsc_year - 3 AND CF.num_fsc_year + 1

GROUP BY
    INV.id_item_sku,
    INV.code_warehouse,
    CASE WHEN CAL.dt_fsc_week_first < '2025-04-01' THEN 'AFICONS'
        ELSE INV.code_customer_group 
    END,
    CAL.dt_fsc_week_first,
    CAL.dt_fsc_week_last

UNION ALL

/* ── Part 2: Open Orders (Allocated = '2') ── */
SELECT
    OO.id_item_sku,
    OO.code_warehouse,
    CASE WHEN CAL.dt_fsc_week_first < '2025-04-01' THEN 'AFICONS'
        ELSE CG.code_customer_group 
    END AS code_customer_group,
    CAL.dt_fsc_week_first,
    CAL.dt_fsc_week_last,
    SUM(OO.qty_open_order)                               AS qty_demand,
    SUM(OO.amt_open_order)                               AS amt_demand,
    'Open Order'                                         AS code_status,
    'Actual Demand'                                      AS name_version

FROM {DB}.slv_open_order_line_level                       AS OO

INNER JOIN {DB}.ref_calendar                              AS CAL
    ON  CAL.dt_date = DATEADD(DAY, -OO.num_lead_time_days, OO.dt_current_request)

LEFT JOIN {DB}.ref_customer_account_group                      AS CG
    ON  CG.id_customer = OO.id_customer

CROSS JOIN current_fiscal                                AS CF

WHERE
    OO.code_allocation_flag = '2'
    AND CAL.num_fsc_year BETWEEN CF.num_fsc_year - 3 AND CF.num_fsc_year + 1

GROUP BY
    OO.id_item_sku,
    OO.code_warehouse,
    CASE WHEN CAL.dt_fsc_week_first < '2025-04-01' THEN 'AFICONS'
        ELSE CG.code_customer_group 
    END,
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
