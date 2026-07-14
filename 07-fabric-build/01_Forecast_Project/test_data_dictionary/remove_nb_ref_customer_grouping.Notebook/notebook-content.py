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
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/Wholesale_ProductSourcing_AFI/CustomerGrouping"

TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "ref_customer_grouping"

NUM_PARTITIONS = 400

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

print(f"Starting Bronze transformation for: {full_target_path}")
start_time = time.time()

try:
    # ----------------------------------------------------------------------
    # READ SOURCE
    # ----------------------------------------------------------------------
    print("Reading source data via ABFSS...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # ----------------------------------------------------------------------
    # APPLY SILVER LOGIC DIRECTLY IN BRONZE
    # ----------------------------------------------------------------------
    print("Applying Silver logic (clean + rename columns)...")

    df_clean = (
        df
        .filter(F.col("CustomerNumber").isNotNull())
        .select(
            F.trim(F.col("CustomerGroup")).alias("code_customer_group")
        )
        .distinct()
    )

    # ----------------------------------------------------------------------
    # OPTIMIZE DISTRIBUTION
    # ----------------------------------------------------------------------
    print(f"Repartitioning into {NUM_PARTITIONS} partitions...")
    df_optimized = df_clean.repartition(NUM_PARTITIONS)

    # ----------------------------------------------------------------------
    # WRITE BACK TO BRONZE (OVERWRITE TABLE)
    # ----------------------------------------------------------------------
    print("Writing cleaned data back to Bronze table...")

    df_optimized.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Bronze transformation completed in {execution_time} minutes.")

except Exception as e:
    print(f"Process failed: {str(e)}")
    raise

# --------------------------------------------------------------------------
# MAINTENANCE
# --------------------------------------------------------------------------
print("Running OPTIMIZE for better performance...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
