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
# Source: Direct ABFS path
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/Wholesale_Codis_AFI/EXTORD"

# Target:
TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "brz_Wholesale_Codis_AFI__EXTORD" 

# Performance Tuning
NUM_PARTITIONS = 400 

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"

print(f"Starting unified Migration & Transformation for: {full_target_path}")
start_time = time.time()

try:
    # 1. READ SOURCE DATA
    print("Reading source data via ABFSS...")
    df_raw = spark.read.format("delta").load(SOURCE_PATH)

    # 2. TRANSFORM DATA (Gộp logic Silver vào đây)
    # Filter: Loại bỏ XORDNO null
    df_filtered = df_raw.filter(F.col("XORDNO").isNotNull())

    print("Applying Silver transformations (Trimming, Casting, Date Formatting)...")
    df_transformed = df_filtered.select(
        # Keys & Identifiers
        F.trim(F.col("XORDNO")).alias("id_order"),
        F.trim(F.col("CUSTNO")).alias("id_customer"),
        F.trim(F.col("SHPTO#")).alias("code_ship_to"),
        F.col("CSRPID").cast("int").alias("id_csr"),

        # Order Attributes
        F.trim(F.col("ORDARR")).alias("code_order_arrangement"),
        F.trim(F.col("ORTYPE")).alias("code_order_type"),
        F.trim(F.col("ORDUSE")).alias("code_order_use"),
        F.trim(F.col("ORDREF")).alias("code_order_reference"),
        F.col("ORDLNK").cast("int").alias("num_order_link"),
        F.col("NOSETS").cast("int").alias("num_sets"),
        F.trim(F.col("ORDUSR")).alias("name_order_user"),

        # Order Type Flags
        F.trim(F.col("OTTYP1")).alias("code_order_type_1"),
        F.trim(F.col("OTTYP2")).alias("code_order_type_2"),
        F.trim(F.col("OTTYP3")).alias("code_order_type_3"),
        F.trim(F.col("OTTYP4")).alias("code_order_type_4"),

        # Scheduling & Dates
        F.to_date(F.col("RQSDAT").cast("string"), "yyyyMMdd").alias("dt_requested_ship"),
        F.to_date(F.col("TKNDAT").cast("string"), "yyyyMMdd").alias("dt_taken"),
        F.to_date(F.col("FRZDAT").cast("string"), "yyyyMMdd").alias("dt_freeze"),
        F.to_date(F.col("HDATE").cast("string"), "yyyyMMdd").alias("dt_hold"),
        F.to_date(F.col("CAPRDT").cast("string"), "yyyyMMdd").alias("dt_capacity"),
        F.to_date(F.col("CBDDAT").cast("string"), "yyyyMMdd").alias("dt_cbd"),
        F.to_date(F.col("DATMNT").cast("string"), "yyyyMMdd").alias("dt_maintenance"),
        F.trim(F.col("TIMMNT")).alias("code_time_maintenance"),

        # Shipping & Location
        F.trim(F.col("WHSE")).alias("code_warehouse"),
        F.trim(F.col("SHPNAM")).alias("name_ship_to"),
        F.trim(F.col("ZIPCOD")).alias("code_zip"),
        F.trim(F.col("EXTCTY")).alias("code_city"),
        F.trim(F.col("EXTSTE")).alias("code_state"),
        F.trim(F.col("TERRCD")).alias("code_territory"),
        F.trim(F.col("ARZONE")).alias("code_ar_zone"),
        F.col("ARSEQ").cast("int").alias("num_ar_sequence"),
        F.to_date(F.col("ARDATE").cast("string"), "yyyyMMdd").alias("dt_ar"),

        # Trip & Routing
        F.col("TRPNO").cast("int").alias("num_trip"),
        F.col("DROP#").cast("int").alias("num_drop"),
        F.col("TRIP#").cast("int").alias("num_trip_sequence"),
        F.trim(F.col("ADVTSP")).alias("code_advance_transport"),

        # Contact
        F.trim(F.col("CONTAC")).alias("name_contact"),
        F.trim(F.col("PHONE#")).alias("code_phone"),

        # Credit & Approval
        F.trim(F.col("CREDVW")).alias("code_credit_review"),
        F.trim(F.col("APVCHK")).alias("code_approval_check"),
        F.trim(F.col("APPROV")).alias("name_approver"),
        F.col("RCVCSH").cast("int").alias("num_received_cash"),
        F.trim(F.col("CROVRD")).alias("code_credit_override"),
        F.to_date(F.col("CROVDT").cast("string"), "yyyyMMdd").alias("dt_credit_override"),
        F.trim(F.col("CRANOV")).alias("code_credit_analysis_override"),

        # Pricing & Commission
        F.trim(F.col("COMMCO")).alias("code_commission"),
        F.trim(F.col("DSCNCO")).alias("code_discount"),
        F.trim(F.col("PRICCO")).alias("code_price"),
        F.trim(F.col("FRGHCO")).alias("code_freight"),
        F.trim(F.col("PRMNBR")).alias("code_promo"),

        # Maintenance
        F.col("MNTCNT").cast("int").alias("num_maintenance_count"),
        F.trim(F.col("USRMNT")).alias("name_maintenance_user"),
        F.trim(F.col("HLDUSR")).alias("name_hold_user"),
        F.trim(F.col("REFNUM")).alias("code_reference_number")
    )

    # 3. PERFORMANCE TUNING (Repartition)
    print(f"Applying repartition logic: {NUM_PARTITIONS} tasks...")
    df_final = df_transformed.repartition(NUM_PARTITIONS)

    # 4. WRITE TO TARGET
    print(f"Writing transformed data to {full_target_path}...")
    df_final.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Migration and Transformation completed in {execution_time} minutes.")

except Exception as e:
    print(f"Process failed: {str(e)}")
    raise

# --------------------------------------------------------------------------
# MAINTENANCE
# --------------------------------------------------------------------------
print("Running OPTIMIZE command...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
