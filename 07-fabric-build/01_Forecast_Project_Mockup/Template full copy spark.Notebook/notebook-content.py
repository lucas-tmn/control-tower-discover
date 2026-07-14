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
# META           "id": "584e7d2c-46ca-49dc-bb6c-68df6ef4f424"
# META         },
# META         {
# META           "id": "62a3081e-4093-4f46-856c-f50aa58732fa"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

import time

# --------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------
# Source: Direct ABFS path to avoid namespace or shortcut resolution errors
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/SupplyChain_Enh_1/DemandForecastSnapshotDaily"

# Target: Explicit 3-level namespace (Catalog.Schema.Table)
TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "brz_SupplyChain_Enh_1__DemandForecastSnapshotDaily"

# Performance Tuning: Suggested 400-800 partitions for 600M+ rows
NUM_PARTITIONS = 400 

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"

print(f"Starting data migration for: {full_target_path}")
start_time = time.time()

try:
    # Read from source using physical path
    print("Reading source data via ABFSS...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # Distribute workload across executors
    print(f"Applying repartition logic: {NUM_PARTITIONS} tasks...")
    df_optimized = df.repartition(NUM_PARTITIONS)

    # Explicit write to target Lakehouse
    print("Writing data to target destination...")
    df_optimized.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Migration completed successfully in {execution_time} minutes.")

except Exception as e:
    print(f"Migration failed: {str(e)}")
    raise

# --------------------------------------------------------------------------
# MAINTENANCE
# --------------------------------------------------------------------------
# Consolidate small files and apply V-Order compression for Fabric
print("Running OPTIMIZE command for performance maintenance...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

from pyspark.sql.functions import format_number

# --------------------------------------------------------------------------
# VALIDATION PARAMETERS
# --------------------------------------------------------------------------
# Ensure this matches the target in Part 1
VALIDATION_TARGET = "SupplyChain_Lakehouse.dbo.brz_SupplyChain_Enh_1__DemandForecastSnapshotDaily"

print(f"Running data validation for: {VALIDATION_TARGET}")

# 1. Row Count Verification
# Spark uses Delta metadata for high-performance counting
df_target = spark.table(VALIDATION_TARGET)
total_count = df_target.count()

print("-" * 30)
print(f"Total Row Count: {total_count:,}")
print("-" * 30)

# 2. Storage and Health Check
# Review file count and table size on OneLake
print("Storage Details:")
display(spark.sql(f"DESCRIBE DETAIL {VALIDATION_TARGET}").select("format", "sizeInBytes", "numFiles", "partitionColumns"))

# 3. Data Integrity Sample
# Preview schema and top records
print("Schema Definition:")
df_target.printSchema()

print("Data Preview (Top 5 records):")
display(df_target.limit(5))

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
