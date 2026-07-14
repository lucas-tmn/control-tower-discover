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

from pyspark.sql.functions import regexp_replace

df = spark.read.format("delta").table("SupplyChain_Lakehouse.dbo.utl_pipeline_metadata")

df_updated = df.withColumn("table_name", regexp_replace("table_name", "_2$", ""))

df_updated.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("SupplyChain_Lakehouse.dbo.utl_pipeline_metadata")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import current_timestamp

df = spark.read.format("delta").table("SupplyChain_Lakehouse.dbo.utl_pipeline_metadata")

df_updated = df.withColumn("next_run_time", current_timestamp())

df_updated.write.format("delta").mode("overwrite").option("overwriteSchema", "true").saveAsTable("SupplyChain_Lakehouse.dbo.utl_pipeline_metadata")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
