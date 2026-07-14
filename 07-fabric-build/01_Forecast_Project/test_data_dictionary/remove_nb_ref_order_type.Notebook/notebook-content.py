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
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/Wholesale_Codis_AFI/AAORDTYP"

TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "ref_order_type"

NUM_PARTITIONS = 400

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"

print(f"Starting transformation + load for: {full_target_path}")
start_time = time.time()

try:
    # ----------------------------------------------------------------------
    # READ SOURCE
    # ----------------------------------------------------------------------
    print("Reading source data...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # ----------------------------------------------------------------------
    # APPLY SILVER LOGIC DIRECTLY IN BRONZE
    # ----------------------------------------------------------------------
    print("Applying transformation logic...")

    df_clean = df.filter(F.col("OTCODE").isNotNull()).select(

        F.trim("OTCODE").alias("code_order_type"),
        F.trim("OTDES1").alias("name_order_type"),
        F.trim("OTDES2").alias("name_order_type_short"),
        F.trim("OORDCL").alias("code_order_class"),
        F.col("OOTCAT").cast("int").alias("num_order_category"),

        F.when(F.trim("OROUTE") == "Y", True).otherwise(False).alias("is_route_eligible"),
        F.when(F.trim("OADCHG") == "Y", True).otherwise(False).alias("is_additional_charge"),
        F.when(F.trim("OARFLG") == "Y", True).otherwise(False).alias("is_auto_replenish"),
        F.when(F.trim("OWNEXP") == "Y", True).otherwise(False).alias("is_will_notify_expedite"),
        F.when(F.trim("OMINEXC") == "Y", True).otherwise(False).alias("is_minimum_exception"),

        F.trim("OREQMNT").alias("code_requirement_type"),

        F.when(F.trim("OFDESCH") == "Y", True).otherwise(False).alias("is_force_delivery_schedule"),
        F.when(F.trim("OFDRIMS") == "Y", True).otherwise(False).alias("is_force_delivery_rims"),

        F.trim("OTRPTYP").alias("code_transport_type"),
        F.col("OZNLTIM").cast("int").alias("num_zone_lead_time_days"),

        F.when(F.trim("OSPECHND") == "Y", True).otherwise(False).alias("is_special_handling"),
        F.when(F.trim("OAUTORSCH") == "Y", True).otherwise(False).alias("is_auto_reschedule"),
        F.when(F.trim("OUSRDFN") == "Y", True).otherwise(False).alias("is_user_defined"),

        F.trim("OTUSER").alias("name_modified_by"),
        F.to_date(F.col("OTDATE").cast("string"), "yyyyMMdd").alias("dt_modified")
    )

    # ----------------------------------------------------------------------
    # PERFORMANCE OPTIMIZATION
    # ----------------------------------------------------------------------
    print(f"Repartitioning into {NUM_PARTITIONS} partitions...")
    df_final = df_clean.repartition(NUM_PARTITIONS)

    # ----------------------------------------------------------------------
    # WRITE TO BRONZE TABLE (OVERWRITE)
    # ----------------------------------------------------------------------
    print("Writing data to bronze table...")

    df_final.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Completed successfully in {execution_time} minutes.")

except Exception as e:
    print(f"Process failed: {str(e)}")
    raise

# --------------------------------------------------------------------------
# MAINTENANCE
# --------------------------------------------------------------------------
print("Running OPTIMIZE...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
