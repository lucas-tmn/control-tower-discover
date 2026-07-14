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

# MAGIC %%sql
# MAGIC MERGE INTO SupplyChain_Lakehouse.dbo.utl_pipeline_metadata AS target
# MAGIC USING (
# MAGIC     SELECT 
# MAGIC         -- ========== Existing v5 columns ==========
# MAGIC         'GLD'                                       AS layer,
# MAGIC         'notebook'                                  AS artifact_type,
# MAGIC         'gld_flat_forecast_actual'                  AS table_name,
# MAGIC         '4abb9011-9b6a-4882-adca-4ba93389f245'      AS notebook_name,
# MAGIC         'Daily'                                     AS frequency,
# MAGIC         3                                           AS scheduled_hour,
# MAGIC         CAST('2020-01-01 00:00:00' AS TIMESTAMP)    AS next_run_time,
# MAGIC         1                                           AS is_active,
# MAGIC         'overwrite'                                 AS load_type,
# MAGIC         NULL                                        AS watermark_column,
# MAGIC         NULL                                        AS last_watermark_value,
# MAGIC         NULL                                        AS primary_key,
# MAGIC         5                                           AS execution_order,
# MAGIC         'slv_actual_demand_monthly,slv_forecast_demand_monthly,slv_naive_forecast_monthly' AS source_tables,
# MAGIC         -- ========== NEW warehouse loader columns ==========
# MAGIC         1                                           AS load_to_wh,
# MAGIC         'test_sp'                                   AS wh_target_schema,
# MAGIC         'fact_flat_forecast_actual'                 AS wh_target_table
# MAGIC ) AS source
# MAGIC ON target.table_name = source.table_name
# MAGIC WHEN MATCHED THEN UPDATE SET
# MAGIC     -- Existing columns
# MAGIC     target.layer                = source.layer,
# MAGIC     target.artifact_type        = source.artifact_type,
# MAGIC     target.notebook_name        = source.notebook_name,
# MAGIC     target.frequency            = source.frequency,
# MAGIC     target.scheduled_hour       = source.scheduled_hour,
# MAGIC     target.next_run_time        = source.next_run_time,
# MAGIC     target.is_active            = source.is_active,
# MAGIC     target.load_type            = source.load_type,
# MAGIC     target.watermark_column     = source.watermark_column,
# MAGIC     target.last_watermark_value = source.last_watermark_value,
# MAGIC     target.primary_key          = source.primary_key,
# MAGIC     target.execution_order      = source.execution_order,
# MAGIC     target.source_tables        = source.source_tables,
# MAGIC     -- NEW warehouse columns
# MAGIC     target.load_to_wh           = source.load_to_wh,
# MAGIC     target.wh_target_schema     = source.wh_target_schema,
# MAGIC     target.wh_target_table      = source.wh_target_table,
# MAGIC     -- Reset operational state (như template cũ)
# MAGIC     target.last_load_date       = NULL,
# MAGIC     target.rows_loaded          = NULL,
# MAGIC     target.status               = 'new',
# MAGIC     target.error_message        = NULL,
# MAGIC     target.pipeline_notes       = 'Initial registration'
# MAGIC WHEN NOT MATCHED THEN INSERT (
# MAGIC     layer, artifact_type, table_name, notebook_name,
# MAGIC     frequency, scheduled_hour, next_run_time, is_active,
# MAGIC     load_type, watermark_column, last_watermark_value, primary_key,
# MAGIC     execution_order, source_tables,
# MAGIC     load_to_wh, wh_target_schema, wh_target_table,
# MAGIC     last_load_date, rows_loaded, status, error_message, pipeline_notes
# MAGIC )
# MAGIC VALUES (
# MAGIC     source.layer, source.artifact_type, source.table_name, source.notebook_name,
# MAGIC     source.frequency, source.scheduled_hour, source.next_run_time, source.is_active,
# MAGIC     source.load_type, source.watermark_column, source.last_watermark_value, source.primary_key,
# MAGIC     source.execution_order, source.source_tables,
# MAGIC     source.load_to_wh, source.wh_target_schema, source.wh_target_table,
# MAGIC     NULL, NULL, 'new', NULL, 'Initial registration'
# MAGIC );

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC UPDATE SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
# MAGIC SET 
# MAGIC     load_to_wh       = 1,
# MAGIC     wh_target_schema = 'test_sp',
# MAGIC     wh_target_table  = 'fact_flat_forecast_actual'
# MAGIC WHERE table_name = 'gld_flat_forecast_actual';

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC UPDATE SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
# MAGIC SET load_to_wh = 0
# MAGIC WHERE table_name = 'gld_flat_forecast_actual';

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC UPDATE SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
# MAGIC SET 
# MAGIC     load_to_wh       = 0,
# MAGIC     wh_target_schema = NULL,
# MAGIC     wh_target_table  = NULL
# MAGIC WHERE 1=1
# MAGIC --table_name = 'gld_flat_forecast_actual';

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC UPDATE SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
# MAGIC SET wh_target_schema = 'dim'
# MAGIC WHERE table_name = 'ref_calendar';

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC UPDATE SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
# MAGIC SET wh_target_table = 'dim_calendar_v2'
# MAGIC WHERE table_name = 'ref_calendar';

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# MAGIC %%sql
# MAGIC UPDATE SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
# MAGIC SET 
# MAGIC     load_to_wh       = 0,
# MAGIC     next_run_time = NULL
# MAGIC WHERE 1=1
# MAGIC -- table_name = 'ref_calendar';

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
