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
SOURCE_PATH = "abfss://c8d9fc83-18b6-4e1d-8264-0b49eed36fe0@onelake.dfs.fabric.microsoft.com/584e7d2c-46ca-49dc-bb6c-68df6ef4f424/Tables/SupplyChain_DW/DimCurrentProductDetails"

TARGET_LH = "SupplyChain_Lakehouse"
TARGET_SCHEMA = "dbo"
TARGET_TABLE = "ref_product"

NUM_PARTITIONS = 400

# --------------------------------------------------------------------------
# SPARK ENGINE OPTIMIZATION
# --------------------------------------------------------------------------
spark.conf.set("spark.sql.adaptive.enabled", "true")
spark.conf.set("spark.microsoft.delta.optimizeWrite.enabled", "true")
spark.conf.set("spark.microsoft.delta.vorder.enabled", "true")

full_target_path = f"{TARGET_LH}.{TARGET_SCHEMA}.{TARGET_TABLE}"

print(f"Starting migration + transformation: {full_target_path}")
start_time = time.time()

try:
    # ------------------------------------------------------------------
    # READ SOURCE
    # ------------------------------------------------------------------
    print("Reading source data...")
    df = spark.read.format("delta").load(SOURCE_PATH)

    # ------------------------------------------------------------------
    # TRANSFORMATION (Silver logic merged into Bronze)
    # ------------------------------------------------------------------
    print("Applying transformation logic...")

    df_clean = df.select(

        # Keys
        F.col("CurrentProductDetailsKey").cast("int").alias("sk_product"),
        F.trim("ItemSKU").alias("id_item_sku"),
        F.trim("Item").alias("id_item"),
        F.trim("SCPItem").alias("id_scp_item"),

        # Descriptions
        F.trim("ItemDescription").alias("name_item_description"),
        F.trim("Colors").alias("name_color"),
        F.col("QtyInBox").cast("int").alias("num_qty_in_box"),
        F.trim("UOM").alias("code_uom"),

        # Series
        F.trim("SeriesNumber").alias("code_series"),
        F.trim("ExtSeriesNumber").alias("code_ext_series"),
        F.trim("ItemExtSeriesNumber").alias("code_item_ext_series"),
        F.trim("SeriesName").alias("name_series"),
        F.trim("SeriesColor").alias("name_series_color"),
        F.trim("SeriesDescription").alias("name_series_description"),

        # Concatenated
        F.trim("Item-Description-Series").alias("name_item_desc_series"),
        F.trim("SH-Item-Description-Series").alias("name_sh_item_desc_series"),
        F.trim("SH-Series-Description").alias("name_sh_series_description"),
        F.trim("Item-Description-Series-ItemColor").alias("name_item_desc_series_color"),

        # Classification
        F.trim("ItemClassCode").alias("code_item_class"),
        F.trim("ItemClassName").alias("name_item_class"),
        F.trim("ItemClass").alias("name_item_class_full"),
        F.trim("ItemCode").alias("code_item"),
        F.trim("ItemGrouping").alias("name_item_grouping"),
        F.trim("ItemStyleCode").alias("code_item_style"),
        F.trim("ItemStyleGroup").alias("name_item_style_group"),
        F.trim("ItemStyle").alias("name_item_style"),

        # Classification - Product Line & Category
        F.trim("ProductLine").alias("name_product_line"),
        F.trim("RetailCategoryCode").alias("code_retail_category"),
        F.trim("RetailCategoryDescription").alias("name_retail_category"),
        F.trim("MerchandisingCategory").alias("name_merchandising_category"),
        F.trim("ChildStyleDescription").alias("name_child_style"),
        F.trim("ParentStyleDescription").alias("name_parent_style"),
        F.trim("PricePoint").alias("name_price_point"),
        F.trim("AssociationCode").alias("code_association"),

        # Classification - Sales
        F.trim("SalesClassCode").alias("code_sales_class"),
        F.trim("SalesClassDescription").alias("name_sales_class_description"),
        F.trim("SalesClass").alias("name_sales_class"),
        F.trim("AFISalesCategoryCode").alias("code_afi_sales_category"),
        F.trim("AFISalesCategory").alias("name_afi_sales_category"),
        F.trim("AFISalesDivisionCode").alias("code_afi_sales_division"),
        F.trim("AFISalesDivision").alias("name_afi_sales_division"),
        F.trim("AFIFinanceDivision").alias("name_afi_finance_division"),

        # Classification - Discount
        F.trim("DiscountClassCode").alias("code_discount_class"),
        F.trim("DiscountClassDescription").alias("name_discount_class_description"),
        F.trim("DiscountClass").alias("name_discount_class"),

        # Classification - Commission
        F.trim("CommissionClassCode").alias("code_commission_class"),
        F.trim("CommissionClassDescription").alias("name_commission_class_description"),
        F.trim("CommissionClass").alias("name_commission_class"),

        # Classification - Freight
        F.trim("FreightClassCode").alias("code_freight_class"),
        F.trim("FreightClassDescription").alias("name_freight_class_description"),
        F.trim("FreightClass").alias("name_freight_class"),

        # Classification - Collective
        F.trim("CollectiveClassCode").alias("code_collective_class"),
        F.trim("CollectiveClass").alias("name_collective_class"),

        # Office & Origin
        F.trim("ResponsibleOffice").alias("code_responsible_office"),
        F.trim("Import/DomesticCode").alias("code_import_domestic"),
        F.trim("CountryofOrigin").alias("name_country_of_origin"),
        F.trim("CEXCode").alias("code_cex"),

        # Status
        F.trim("AFIItemStatus").alias("code_afi_item_status"),
        F.trim("ManufacturingStatus").alias("code_manufacturing_status"),
        F.trim("CurrentSCPManufacturingStatus").alias("code_current_scp_manufacturing_status"),
        F.trim("MarketingItemStatus").alias("code_marketing_item_status"),
        F.trim("MarketingStatusDescription").alias("name_marketing_status"),
        F.trim("CurrentStatus").alias("code_current_status"),
        F.col("ManufacturingStatusChangeDate").cast("date").alias("dt_manufacturing_status_change"),

        # Flags
        F.when(F.lower(F.trim("MainPieceItem")) == "true", True).otherwise(False).alias("is_main_piece"),
        F.col("CommodityItem").cast("int").alias("num_commodity_item"),
        F.trim("SellableItemFlag").alias("code_sellable_item"),  # ← FIX: trim instead of cast int
        F.col("F123ProductFlag").cast("int").alias("is_f123_product"),
        F.col("HSCoreProductFlag").cast("int").alias("is_hs_core_product"),
        F.col("HSProprietaryProductFlag").cast("int").alias("is_hs_proprietary_product"),
        F.col("HSExclusiveFlag").cast("int").alias("is_hs_exclusive"),
        F.col("BerklineProductFlag").cast("int").alias("is_berkline_product"),
        F.col("BenchcraftProductFlag").cast("int").alias("is_benchcraft_product"),
        F.col("NewMillenniumProductFlag").cast("int").alias("is_new_millennium_product"),
        F.col("BardiniProductFlag").cast("int").alias("is_bardini_product"),
        F.col("ShanghaiStore").cast("int").alias("is_shanghai_store"),
        F.col("DefaultGroup").cast("int").alias("num_default_group"),

        # Market
        F.trim("MarketIntroducedAt").alias("name_market_introduced_at"),
        F.col("MarketBeginDate").cast("date").alias("dt_market_begin"),
        F.col("MarketEndDate").cast("date").alias("dt_market_end"),

        # Pricing
        F.col("FOBPrice").cast("decimal(14,3)").alias("amt_fob_price"),
        F.trim("GoodBetterBestForPricePoint").alias("code_good_better_best"),  # ← FIX: trim instead of decimal
        F.col("GBBSortId").cast("int").alias("num_gbb_sort"),  # ← FIX: int instead of decimal

        # Vendor
        F.trim("PrimaryVendor").alias("code_primary_vendor"),
        F.trim("PrimaryVendorName").alias("name_primary_vendor"),  # ← FIX: added comma

        # Invoice & Forecast
        F.trim("InitialInvoicePeriod").alias("code_initial_invoice_period"),
        F.col("InitialInvoiceQty").cast("int").alias("qty_initial_invoice"),  # ← FIX: cast int + added comma
        F.trim("ItemForecastPlannerID").alias("id_item_forecast_planner"),  # ← FIX: added comma

        # Package / Main Piece
        F.trim("MainPiece").alias("code_main_piece")

    ).filter(
        (F.col("id_item_sku").isNotNull()) &
        (F.col("id_item_sku") != "N/A")
    )

    # ------------------------------------------------------------------
    # REPARTITION (performance for large tables)
    # ------------------------------------------------------------------
    print(f"Repartitioning into {NUM_PARTITIONS} partitions...")
    df_final = df_clean.repartition(NUM_PARTITIONS)

    # ------------------------------------------------------------------
    # WRITE TO BRONZE (overwrite existing table)
    # ------------------------------------------------------------------
    print("Writing data to Bronze table...")
    df_final.write \
        .format("delta") \
        .mode("overwrite") \
        .option("overwriteSchema", "true") \
        .saveAsTable(full_target_path)

    execution_time = round((time.time() - start_time) / 60, 2)
    print(f"Completed successfully in {execution_time} minutes.")

except Exception as e:
    print(f"Migration failed: {str(e)}")
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
