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
# MAGIC /* ═══════════════════════════════════════════════════════════════
# MAGIC    REFERENCE TABLE: FORECAST HORIZON
# MAGIC    Target: dbo.ref_forecast_horizon
# MAGIC 
# MAGIC    Purpose:
# MAGIC      Static lookup of forecast horizon codes used across
# MAGIC      forecast accuracy and demand planning tables.
# MAGIC 
# MAGIC    Grain:  code_horizon (unique)
# MAGIC    ═══════════════════════════════════════════════════════════════ */
# MAGIC CREATE OR REPLACE TABLE dbo.ref_forecast_horizon (
# MAGIC     code_horizon STRING,
# MAGIC     num_rank     INT
# MAGIC );
# MAGIC 
# MAGIC INSERT INTO dbo.ref_forecast_horizon VALUES
# MAGIC     ('2W',      1),
# MAGIC     ('30Days',  2),
# MAGIC     ('60Days',  3),
# MAGIC     ('90Days',  4),
# MAGIC     ('120Days', 5);

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
