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
# Source: Direct ABFS path
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/Customers/ShippingLocations"

# Target: New Consolidated Table Name
TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "ref_customer_shipping_location"

NUM_PARTITIONS = 400
CUTOFF_DATE = "2023-01-01"

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"
print(f"Starting consolidated migration for: {full_target_path}")
start_time = time.time()

try:
    # 1. READ SOURCE
    print("Reading source data via ABFSS...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # 2. INITIAL FILTER (Time & Null Keys)
    # Lọc dtec >= 2023-01-01 và cslCustomerNumber IS NOT NULL
    print(f"Filtering records (dtec >= {CUTOFF_DATE})...")
    
    dtec_dtype = df.schema["dtec"].dataType
    if not isinstance(dtec_dtype, (T.TimestampType, T.DateType)):
        df = df.withColumn("dtec_ts", F.to_timestamp(F.col("dtec"), "yyyy-MM-dd'T'HH:mm:ss.SSSXXX"))
    else:
        df = df.withColumn("dtec_ts", F.col("dtec"))

    df_filtered = df.filter(
        (F.col("dtec_ts") >= F.lit(CUTOFF_DATE).cast("timestamp")) & 
        (F.col("cslCustomerNumber").isNotNull())
    )

    # 3. TRANSFORM & RENAME (Silver Logic)
    print("Applying Silver transformation logic (Trimming, Casting, Renaming)...")
    
    df_transformed = df_filtered.select(
        # Keys & Identifiers
        F.trim(F.col("cslCustomerNumber")).alias("id_customer"),
        F.trim(F.col("cslShiptoNumber")).alias("code_ship_to"),
        F.col("cslMapicsSequenceNumber").cast("int").alias("num_mapics_sequence"),
        F.trim(F.col("cslName")).alias("name_ship_to"),
        
        # Address
        F.trim(F.col("csmShpa1")).alias("name_address_1"),
        F.trim(F.col("csmShpa2")).alias("name_address_2"),
        F.trim(F.col("csmShpa3")).alias("name_address_3"),
        F.trim(F.col("csmShpzp")).alias("code_zip"),
        F.trim(F.col("csmShpst")).alias("code_state"),
        F.trim(F.col("csmShpco")).alias("code_country"),
        F.trim(F.col("csmCounty")).alias("code_county"),
        
        # Contact
        F.trim(F.col("csmPhone")).alias("code_phone"),
        F.trim(F.col("csmFaxTn")).alias("code_fax"),
        F.trim(F.col("csmContact")).alias("name_contact"),
        F.trim(F.col("csmWebsite")).alias("code_website"),
        F.trim(F.col("csmEmail")).alias("code_email"),
        F.trim(F.col("csmCsPhone")).alias("code_cs_phone"),
        F.trim(F.col("csmcsFax")).alias("code_cs_fax"),
        F.trim(F.col("csmcsContact")).alias("name_cs_contact"),
        F.trim(F.col("csmcsEmail")).alias("code_cs_email"),
        
        # Sales & Pricing
        F.trim(F.col("cslCommissionCode")).alias("code_commission"),
        F.trim(F.col("cslFreightCode")).alias("code_freight"),
        F.trim(F.col("cslPriceCode")).alias("code_price"),
        F.trim(F.col("cslDiscountCode")).alias("code_discount"),
        F.col("cslCommissionSplit").cast("decimal(10,4)").alias("pct_commission_split"),
        
        # Warehouse & Territory
        F.trim(F.col("cslDefaultWarehouse")).alias("code_default_warehouse"),
        F.trim(F.col("cslShippingTerritory")).alias("code_shipping_territory"),
        F.trim(F.col("cslBusinessType")).alias("code_business_type"),
        F.trim(F.col("cslShipType")).alias("code_ship_type"),
        
        # Transcom
        F.trim(F.col("cslTranscomPrimaryID")).alias("id_transcom_primary"),
        F.trim(F.col("cslTranscomAlternateID")).alias("id_transcom_alternate"),
        
        # Comments & Memo
        F.trim(F.col("cslComment1")).alias("name_comment_1"),
        F.trim(F.col("cslComment2")).alias("name_comment_2"),
        F.trim(F.col("cslMemo")).alias("name_memo"),
        F.trim(F.col("csmDirections")).alias("name_directions"),
        F.trim(F.col("csmCrossStreet")).alias("name_cross_street"),
        
        # CRM & IDs
        F.trim(F.col("cslCrmID")).alias("id_crm"),
        F.trim(F.col("cslBuyerAddressID")).alias("id_buyer_address"),
        F.trim(F.col("cslPartyLocationID")).alias("id_party_location"),
        F.trim(F.col("cslRouteAddressID")).alias("id_route_address"),
        F.trim(F.col("cslReturnAddressID")).alias("id_return_address"),
        F.trim(F.col("cslReturnAddressName")).alias("name_return_address"),
        
        # MSA & Region
        F.trim(F.col("csmMsa_Fips")).alias("code_msa_fips"),
        F.trim(F.col("csmRMCityNumber")).alias("code_rm_city"),
        
        # Tax & Segment
        F.trim(F.col("cslTaxExempt")).alias("code_tax_exempt"),
        F.col("cslCustomerSegment").cast("int").alias("num_customer_segment"),
        
        # Default Order Types
        F.trim(F.col("cslDefaultOrderType1")).alias("code_default_order_type_1"),
        F.trim(F.col("cslDefaultOrderType2")).alias("code_default_order_type_2"),
        F.trim(F.col("cslDefaultOrderType3")).alias("code_default_order_type_3"),
        F.trim(F.col("cslDefaultOrderType4")).alias("code_default_order_type_4"),
        
        # Shipping & Delivery
        F.col("csmShled").cast("int").alias("num_ship_lead_days"),
        F.trim(F.col("cslDeliveryUnitOfMeasure")).alias("code_delivery_uom"),
        F.col("cslDeliveryUnitOfMeasureFence").cast("decimal(10,2)").alias("val_delivery_uom_fence"),
        F.trim(F.col("cslExpressShippingMethod")).alias("code_express_shipping_method"),
        F.col("cslExpressHandlingCharge").cast("decimal(10,3)").alias("pct_express_handling_charge"),
        F.col("cslExpressMinimum").cast("decimal(10,2)").alias("amt_express_minimum"),
        F.col("cslExpressMaximum").cast("decimal(10,2)").alias("amt_express_maximum"),
        F.trim(F.col("cslExpressServiceContractNumber")).alias("code_express_service_contract"),
        
        # Flags
        F.when(F.trim(F.col("cslBlockRepOrderEntry")) == "1", True).otherwise(False).alias("is_block_rep_order_entry"),
        F.trim(F.col("cslAllowFax")).alias("code_allow_fax"),
        F.trim(F.col("cslDirectConsumer")).alias("code_direct_consumer"),
        F.trim(F.col("cslDirectIncludeShipto")).alias("code_direct_include_shipto"),
        F.trim(F.col("cslExportsLCLConsolidationFlag")).alias("code_exports_lcl_consolidation"),
        F.trim(F.col("cslExportsDocumentCountry")).alias("code_exports_document_country"),
        F.trim(F.col("cslExportsProductOnPallets")).alias("code_exports_product_on_pallets"),
        F.trim(F.col("cslExportsAppointmentsRequired")).alias("code_exports_appointments_required"),
        F.trim(F.col("cslHasDock")).alias("code_has_dock"),
        F.trim(F.col("cslUseNegotiatedFreightRate")).alias("code_use_negotiated_freight_rate"),
        F.trim(F.col("cslUseStandardFreightRate")).alias("code_use_standard_freight_rate"),
        F.trim(F.col("cslDoNotRepriceOrders")).alias("code_do_not_reprice_orders"),
        F.trim(F.col("cslPricingUseOfflineFiles")).alias("code_pricing_use_offline_files"),
        
        # Language & Dates
        F.trim(F.col("cslDefaultLanguage")).alias("code_default_language"),
        F.col("cslTerritoryEffectivityDate").cast("timestamp").alias("dt_territory_effectivity"),
        F.trim(F.col("cslHasDockUserDate")).alias("name_has_dock_user_date"),
        F.col("cslLastStatusChangeDate").cast("timestamp").alias("dt_last_status_change"),
        
        # Status & Audit
        F.trim(F.col("acrec")).alias("code_record_status"),
        F.trim(F.col("csmAppcd")).alias("code_app"),
        F.col("csmChgAddr").cast("int").alias("num_change_address"),
        F.col("csmChgShip").cast("int").alias("num_change_ship"),
        F.col("csmChgShipExt").cast("int").alias("num_change_ship_ext"),
        F.col("csmChgCust").cast("int").alias("num_change_customer"),
        F.col("commAudit").cast("int").alias("num_commission_audit"),
        F.col("commAudit2").cast("int").alias("num_commission_audit_2"),
        
        # Source Audit
        F.trim(F.col("usra")).alias("name_created_by"),
        F.col("dtea").cast("timestamp").alias("ts_created"),
        F.trim(F.col("usrc")).alias("name_modified_by"),
        F.col("dtec").cast("timestamp").alias("ts_modified")
    )

    # 4. REPARTITION & WRITE
    print(f"Repartitioning to {NUM_PARTITIONS} tasks...")
    df_optimized = df_transformed.repartition(NUM_PARTITIONS)
    
    print(f"Writing data to {full_target_path}...")
    df_optimized.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    # 5. CLEANUP SILVER (Xóa bảng Silver cũ nếu tồn tại)
    print("Cleaning up old Silver table...")
    spark.sql(f"DROP TABLE IF EXISTS {TARGET_SCHEMA}.slv_customer_shipping_location")

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Success! Consolidated migration completed in {execution_time} minutes.")

except Exception as e:
    print(f"Migration failed: {str(e)}")
    raise

# --------------------------------------------------------------------------
# MAINTENANCE
# --------------------------------------------------------------------------
print("Optimizing target table...")
spark.sql(f"OPTIMIZE {full_target_path}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
