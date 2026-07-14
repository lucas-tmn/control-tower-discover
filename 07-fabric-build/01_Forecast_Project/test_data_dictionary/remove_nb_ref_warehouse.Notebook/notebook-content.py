# Fabric notebook source

# METADATA ********************

# META {
# META   "kernel_info": {
# META     "name": "synapse_pyspark"
# META   },
# META   "dependencies": {
# META     "lakehouse": {
# META       "default_lakehouse": "584e7d2c-46ca-49dc-bb6c-68df6ef4f424",
# META       "default_lakehouse_name": "Enterprise_Lakehouse",
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
from pyspark.sql import functions as F

# --------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/SupplyChain_DW/DimAFIWarehouses"

TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "ref_warehouse"

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
    # ----------------------------------------------------------------------
    # STEP 1: READ SOURCE
    # ----------------------------------------------------------------------
    print("Reading source data via ABFSS...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # ----------------------------------------------------------------------
    # STEP 2: APPLY SILVER LOGIC (MERGED INTO BRONZE)
    # ----------------------------------------------------------------------
    print("Applying transformation logic (previous Silver layer)...")

    df_transformed = (
        df.filter(F.col("AFIWarehousesKey").isNotNull())
        .select(
            F.col("AFIWarehousesKey").cast("int").alias("sk_warehouse"),
            F.trim(F.col("WarehouseCode")).alias("code_warehouse"),
            F.trim(F.col("IntransitWarehouse")).alias("code_intransit_warehouse"),
            F.trim(F.col("ContainerDirectWarehouse")).alias("code_container_direct"),
            F.col("ControlledWarehouse").cast("int").alias("is_controlled_warehouse"),
            F.trim(F.col("WarehouseLocation")).alias("name_warehouse_location"),
            F.trim(F.col("WarehouseOrderGroup")).alias("name_warehouse_order_group"),
            F.col("FinanceInventoryReportFlag").cast("int").alias("is_finance_inventory_report")
        )
    )

    # ----------------------------------------------------------------------
    # STEP 3: REPARTITION FOR PERFORMANCE
    # ----------------------------------------------------------------------
    print(f"Applying repartition logic: {NUM_PARTITIONS} tasks...")
    df_optimized = df_transformed.repartition(NUM_PARTITIONS)

    # ----------------------------------------------------------------------
    # STEP 4: WRITE TO BRONZE TABLE (UPDATED STRUCTURE)
    # ----------------------------------------------------------------------
    print("Writing transformed data directly into Bronze table...")

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
# STEP 5: OPTIMIZE TABLE (FABRIC PERFORMANCE)
# --------------------------------------------------------------------------
print("Running OPTIMIZE command for performance maintenance...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
