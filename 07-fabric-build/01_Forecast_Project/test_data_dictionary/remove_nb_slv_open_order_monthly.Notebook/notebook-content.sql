-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "synapse_pyspark"
-- META   },
-- META   "dependencies": {
-- META     "lakehouse": {
-- META       "default_lakehouse": "62a3081e-4093-4f46-856c-f50aa58732fa",
-- META       "default_lakehouse_name": "SupplyChain_Lakehouse",
-- META       "default_lakehouse_workspace_id": "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0",
-- META       "known_lakehouses": [
-- META         {
-- META           "id": "62a3081e-4093-4f46-856c-f50aa58732fa"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- CELL ********************

/* SILVER LAYER: OPEN ORDERS MONTHLY - AGG TABLE
   Target: dbo.slv_open_order_monthly
   Source: dbo.slv_open_order_line_level + ref_calendar + ref_customer_grouping
   Grain:  id_item_sku × code_warehouse × code_customer_group × num_fsc_month_year
   Range:  3 fiscal years back → 1 fiscal year forward
*/

CREATE OR REPLACE TABLE dbo.slv_open_order_monthly AS

WITH current_fiscal AS (
    SELECT num_fsc_year
    FROM dbo.ref_calendar
    WHERE dt_date = CURRENT_DATE()
    LIMIT 1
)

SELECT
    /* ── Grain Keys ── */
    OO.id_item_sku,
    OO.code_warehouse,
    CG.code_customer_group,
    CAL.dt_fsc_month_first,
    CAL.dt_fsc_month_last,

    /* ── Quantities ── */
    SUM(OO.qty_open_order)                               AS qty_open_order,
    SUM(OO.qty_backorder)                                AS qty_backorder,

    /* ── Amounts ── */
    SUM(OO.amt_open_order)                               AS amt_open_order,
    SUM(OO.amt_backorder)                                AS amt_backorder,

    /* ── Line Counts ── */
    COUNT(*)                                             AS num_order_lines,
    COUNT(DISTINCT OO.id_order)                          AS num_distinct_orders,

    /* ── Past Due ── */
    SUM(CASE WHEN OO.code_past_due_flag = 'Past Due'
             THEN OO.qty_open_order ELSE 0 END)          AS qty_past_due,
    SUM(CASE WHEN OO.code_past_due_flag = 'Past Due'
             THEN OO.amt_open_order ELSE 0 END)          AS amt_past_due

FROM dbo.slv_open_order_line_level                       AS OO

INNER JOIN dbo.ref_calendar                              AS CAL
    ON  CAL.dt_date = OO.dt_current_request

LEFT JOIN dbo.ref_customer_grouping                      AS CG
    ON  CG.id_customer = OO.id_customer

CROSS JOIN current_fiscal                                AS CF

WHERE
    CAL.num_fsc_year BETWEEN CF.num_fsc_year - 3 AND CF.num_fsc_year + 1

GROUP BY
    OO.id_item_sku,
    OO.code_warehouse,
    CG.code_customer_group,
    CAL.dt_fsc_month_first,
    CAL.dt_fsc_month_last

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
