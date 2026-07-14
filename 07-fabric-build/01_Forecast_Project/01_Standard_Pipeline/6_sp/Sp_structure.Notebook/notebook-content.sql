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
-- MAGIC ALTER TABLE dbo.utl_pipeline_metadata ADD COLUMNS (
-- MAGIC     load_to_wh         INT,
-- MAGIC     wh_target_schema   STRING,
-- MAGIC     wh_target_table    STRING
-- MAGIC )

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

-- MAGIC %%sql
-- MAGIC DESCRIBE TABLE dbo.utl_pipeline_metadata

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

-- MAGIC %%sql
-- MAGIC -- ============================================================
-- MAGIC -- Step A: Reset toàn bộ về 0 (mặc định không load)
-- MAGIC -- ============================================================
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 0,
-- MAGIC     wh_target_schema = NULL,
-- MAGIC     wh_target_table = NULL;

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

-- MAGIC %%sql
-- MAGIC -- ============================================================
-- MAGIC -- Step B: Bật cờ + đặt target name cho 7 bảng pilot
-- MAGIC -- Schema target: test_sp
-- MAGIC -- ============================================================
-- MAGIC 
-- MAGIC -- 5 bảng REF → dim_*
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'dim_calendar'
-- MAGIC WHERE table_name = 'ref_calendar';
-- MAGIC 
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'dim_customer_grouping'
-- MAGIC WHERE table_name = 'ref_customer_grouping';
-- MAGIC 
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'dim_forecast_horizon'
-- MAGIC WHERE table_name = 'ref_forecast_horizon';
-- MAGIC 
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'dim_product'
-- MAGIC WHERE table_name = 'ref_product';
-- MAGIC 
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'dim_warehouse'
-- MAGIC WHERE table_name = 'ref_warehouse';
-- MAGIC 
-- MAGIC -- 2 bảng GLD → fact_*
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'fact_flat_forecast_actual'
-- MAGIC WHERE table_name = 'gld_flat_forecast_actual';
-- MAGIC 
-- MAGIC UPDATE dbo.utl_pipeline_metadata
-- MAGIC SET load_to_wh = 1,
-- MAGIC     wh_target_schema = 'test_sp',
-- MAGIC     wh_target_table = 'fact_forecast_kpi'
-- MAGIC WHERE table_name = 'gld_forecast_kpi_metric';

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

-- MAGIC %%sql
-- MAGIC -- Phải thấy đúng 7 dòng
-- MAGIC SELECT 
-- MAGIC     table_name,
-- MAGIC     layer,
-- MAGIC     load_to_wh,
-- MAGIC     wh_target_schema,
-- MAGIC     wh_target_table
-- MAGIC FROM dbo.utl_pipeline_metadata
-- MAGIC WHERE load_to_wh = 1
-- MAGIC ORDER BY layer, table_name

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }

-- CELL ********************

-- MAGIC %%sql
-- MAGIC -- Trên Lakehouse notebook
-- MAGIC DESCRIBE TABLE dbo.gld_flat_forecast_actual

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
