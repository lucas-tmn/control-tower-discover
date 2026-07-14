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
from pyspark.sql import types as T

# --------------------------------------------------------------------------
# CONFIGURATION
# --------------------------------------------------------------------------
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/Customers/AccountMaster"

TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "ref_customer_account"   # giữ nguyên tên bronze hiện tại

NUM_PARTITIONS = 400
CUTOFF_DATE = "2023-01-01"

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

spark.conf.set("spark.sql.parquet.datetimeRebaseModeInRead", "CORRECTED")
spark.conf.set("spark.sql.parquet.int96RebaseModeInRead", "CORRECTED")
spark.conf.set("spark.sql.parquet.datetimeRebaseModeInWrite", "CORRECTED")
spark.conf.set("spark.sql.parquet.int96RebaseModeInWrite", "CORRECTED")

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"
print(f"Starting migration + transformation for: {full_target_path}")

start_time = time.time()

try:
    # ------------------------------------------------------------------
    # READ SOURCE
    # ------------------------------------------------------------------
    print("Reading source data...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # ------------------------------------------------------------------
    # FILTER DATE (logic cũ)
    # ------------------------------------------------------------------
    dtec_dtype = df.schema["dtec"].dataType

    if isinstance(dtec_dtype, (T.TimestampType, T.DateType)):
        df_filtered = df.filter(F.col("dtec") >= F.lit(CUTOFF_DATE).cast("timestamp"))
    else:
        df_filtered = df.filter(
            F.to_timestamp(F.col("dtec"), "yyyy-MM-dd'T'HH:mm:ss.SSSXXX")
            >= F.lit(CUTOFF_DATE).cast("timestamp")
        )

    print(f"Records after filter: {df_filtered.count():,}")

    # ------------------------------------------------------------------
    # SILVER LOGIC → MERGE INTO BRONZE
    # ------------------------------------------------------------------
    print("Applying silver transformation logic...")

    df_final = df_filtered.select(

        # Keys
        F.trim("cmaCustomerNumber").alias("id_customer"),
        F.trim("cmaCustomerName").alias("name_customer"),
        F.trim("cmaDBAName").alias("name_dba"),

        # Contact
        F.trim("cmaContact").alias("name_contact"),
        F.trim("cmaPhone").alias("code_phone"),
        F.trim("cmaFaxtn").alias("code_fax"),
        F.trim("cmaEmail").alias("code_email"),

        # Territory
        F.trim("cmaPrimaryTerritory").alias("code_territory"),
        F.trim("cmaCreditTerritoryID").alias("id_credit_territory"),
        F.trim("cmaDeductTerritoryID").alias("id_deduct_territory"),
        F.trim("cmaCustomerChannelID").alias("code_customer_channel"),
        F.trim("cmaCustomerClassCode").alias("code_customer_class"),

        # Credit
        F.col("cmaCreditLimitAmount").cast("decimal(14,2)").alias("amt_credit_limit"),
        F.trim("cmaTermsCode").alias("code_terms"),
        F.col("cmaTermsDays").cast("int").alias("num_terms_days"),
        F.col("cmaPercentAvailableCredit").cast("decimal(10,2)").alias("pct_available_credit"),
        F.trim("cmaCreditAuthorizationCode").alias("code_credit_authorization"),
        F.trim("cmaMinimumFreightCode").alias("code_minimum_freight"),
        F.col("cmaMinPreapprovalAmount").cast("decimal(14,2)").alias("amt_min_preapproval"),
        F.trim("cmaCreditAddessCode").alias("code_credit_address"),
        F.col("cmaLateChargePercent").cast("decimal(10,4)").alias("pct_late_charge"),

        # Flags
        (F.trim("cmaCancelBackOrders") == "1").alias("is_cancel_backorders"),
        (F.trim("cmaAllowPartialShipment") == "1").alias("is_allow_partial_shipment"),
        (F.trim("cmaAllowAllowanceCredits") == "1").alias("is_allow_allowance_credits"),
        (F.trim("cmaDocumentationHold") == "Y").alias("is_documentation_hold"),
        (F.trim("cmaPARSByPurchaser") == "Y").alias("is_pars_by_purchaser"),
        (F.trim("cma10DigitScheduleB") == "Y").alias("is_10_digit_schedule_b"),
        (F.trim("cmaInheritBlocking") == "1").alias("is_inherit_blocking"),

        # Codes
        F.trim("cmaLanguageCode").alias("code_language"),
        F.trim("cmaStatementCode").alias("code_statement"),
        F.trim("cmaItemCrossReferenceCode").alias("code_item_cross_reference"),
        F.trim("cmaCurrencyCode").alias("code_currency"),
        F.trim("cmaRFCTaxIdNumber").alias("code_tax_id"),
        F.trim("cmaAppcd").alias("code_app"),
        F.trim("cmaHomestoreFacingWhse").alias("code_homestore_facing_warehouse"),

        # Insurance
        F.trim("cmaTypeOfInsurance").alias("code_insurance_type"),
        F.when(F.col("cmaInsExpirationDate") < "1900-01-01", None)
            .otherwise(F.col("cmaInsExpirationDate").cast("timestamp"))
            .alias("dt_insurance_expiration"),

        F.col("cmaInsCoverageRequested").cast("decimal(14,2)").alias("amt_insurance_coverage_requested"),
        F.col("cmaInsCoverageApproved").cast("decimal(14,2)").alias("amt_insurance_coverage_approved"),
        F.trim("cmaInsuranceStatus").alias("code_insurance_status"),

        # Status
        F.trim("acrec").alias("code_record_status"),
        F.trim("cmaBillingAddressID").alias("id_billing_address"),
        F.trim("cmaMemo").alias("name_memo"),

        # Audit
        F.col("cmaChgCustAr").cast("int").alias("num_change_customer_ar"),
        F.col("cmaChgCust").cast("int").alias("num_change_customer"),
        F.col("cmaChgCustExt").cast("int").alias("num_change_customer_ext"),
        F.col("cmaCommAudit").cast("int").alias("num_commission_audit"),

        # Dates
        F.when(F.col("cmaTerritoryChangeDate") < "1900-01-01", None)
            .otherwise(F.col("cmaTerritoryChangeDate").cast("timestamp"))
            .alias("dt_territory_change"),

        F.when(F.col("cmaLastStatusChangeDate") < "1900-01-01", None)
            .otherwise(F.col("cmaLastStatusChangeDate").cast("timestamp"))
            .alias("dt_last_status_change"),

        # Source audit
        F.trim("usra").alias("name_created_by"),
        F.when(F.col("dtea") < "1900-01-01", None)
            .otherwise(F.col("dtea").cast("timestamp"))
            .alias("ts_created"),

        F.trim("usrc").alias("name_modified_by"),
        F.when(F.col("dtec") < "1900-01-01", None)
            .otherwise(F.col("dtec").cast("timestamp"))
            .alias("ts_modified")
    ).filter(F.col("id_customer").isNotNull())

    # ------------------------------------------------------------------
    # PERFORMANCE OPTIMIZATION
    # ------------------------------------------------------------------
    df_final = df_final.repartition(NUM_PARTITIONS)

    # ------------------------------------------------------------------
    # WRITE TO BRONZE (overwrite schema)
    # ------------------------------------------------------------------
    print("Writing transformed data directly into Bronze table...")

    df_final.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Completed successfully in {execution_time} minutes")

except Exception as e:
    print(f"FAILED: {str(e)}")
    raise

# --------------------------------------------------------------------------
# OPTIMIZE
# --------------------------------------------------------------------------
print("Running OPTIMIZE...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
