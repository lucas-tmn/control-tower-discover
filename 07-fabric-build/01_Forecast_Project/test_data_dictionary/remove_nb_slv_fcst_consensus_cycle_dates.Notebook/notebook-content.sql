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

-- MAGIC %%sql
-- MAGIC /* SILVER LAYER: FORECAST OFFICIAL SNAPSHOT DATE- DIM TABLE
-- MAGIC    Target: dbo.slv_forecast_cycle
-- MAGIC    Logic: FORECAST OFFICIAL SNAPSHOT DATE - DIM TABLE
-- MAGIC */
-- MAGIC 
-- MAGIC CREATE OR REPLACE TABLE dbo.slv_forecast_cycle AS
-- MAGIC SELECT
-- MAGIC     TRIM(CycleName)                                      AS code_cycle,
-- MAGIC     TRIM(CycleDescription)                               AS name_cycle_description,
-- MAGIC     CAST(CycleMonthLastDate AS DATE)                      AS dt_cycle_month_last,
-- MAGIC     CAST(FcstSnapshot AS DATE)                            AS dt_forecast_snapshot,
-- MAGIC     TRIM(ExceptionNote)                                   AS name_exception_note,
-- MAGIC     CAST(Modified AS TIMESTAMP)                           AS ts_modified,
-- MAGIC     CAST(Created AS TIMESTAMP)                            AS ts_created
-- MAGIC 
-- MAGIC FROM dbo.brz_fcstconsensuscycledates
-- MAGIC WHERE CycleName IS NOT NULL

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
