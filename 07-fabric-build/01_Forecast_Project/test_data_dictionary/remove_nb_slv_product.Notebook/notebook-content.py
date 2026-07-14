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
# MAGIC /* SILVER LAYER: PRODUCT MASTER - DIM TABLE
# MAGIC    Target: dbo.slv_product
# MAGIC    Source: dbo.brz_supplychain_dw__dimcurrentproductdetails
# MAGIC    Logic: PRODUCT MASTER - DIM TABLE
# MAGIC */
# MAGIC 
# MAGIC CREATE OR REPLACE TABLE dbo.slv_product AS
# MAGIC SELECT *
# MAGIC     -- Keys & Identifiers
# MAGIC     CAST(CurrentProductDetailsKey AS INT)                 AS sk_product,
# MAGIC     TRIM(ItemSKU)                                        AS id_item_sku,
# MAGIC     TRIM(Item)                                           AS id_item,
# MAGIC     TRIM(SCPItem)                                        AS id_scp_item,
# MAGIC 
# MAGIC     -- Item Descriptions
# MAGIC     TRIM(ItemDescription)                                AS name_item_description,
# MAGIC     TRIM(Colors)                                         AS name_color,
# MAGIC     CAST(QtyInBox AS INT)                                AS num_qty_in_box,
# MAGIC     TRIM(UOM)                                            AS code_uom,
# MAGIC 
# MAGIC     -- Series
# MAGIC     TRIM(SeriesNumber)                                   AS code_series,
# MAGIC     TRIM(ExtSeriesNumber)                                AS code_ext_series,
# MAGIC     TRIM(ItemExtSeriesNumber)                             AS code_item_ext_series,
# MAGIC     TRIM(SeriesName)                                     AS name_series,
# MAGIC     TRIM(SeriesColor)                                    AS name_series_color,
# MAGIC     TRIM(SeriesDescription)                              AS name_series_description,
# MAGIC 
# MAGIC     -- Concatenated Descriptions
# MAGIC     TRIM(`Item-Description-Series`)                      AS name_item_desc_series,
# MAGIC     TRIM(`SH-Item-Description-Series`)                   AS name_sh_item_desc_series,
# MAGIC     TRIM(`SH-Series-Description`)                        AS name_sh_series_description,
# MAGIC     TRIM(`Item-Description-Series-ItemColor`)            AS name_item_desc_series_color,
# MAGIC 
# MAGIC     -- Classification - Item
# MAGIC     TRIM(ItemClassCode)                                  AS code_item_class,
# MAGIC     TRIM(ItemClassName)                                  AS name_item_class,
# MAGIC     TRIM(ItemClass)                                      AS name_item_class_full,
# MAGIC     TRIM(ItemCode)                                       AS code_item,
# MAGIC     TRIM(ItemGrouping)                                   AS name_item_grouping,
# MAGIC     TRIM(ItemStyleCode)                                  AS code_item_style,
# MAGIC     TRIM(ItemStyleGroup)                                 AS name_item_style_group,
# MAGIC     TRIM(ItemStyle)                                      AS name_item_style,
# MAGIC 
# MAGIC     -- Classification - Product Line & Category
# MAGIC     TRIM(ProductLine)                                    AS name_product_line,
# MAGIC     TRIM(RetailCategoryCode)                             AS code_retail_category,
# MAGIC     TRIM(RetailCategoryDescription)                      AS name_retail_category,
# MAGIC     TRIM(MerchandisingCategory)                          AS name_merchandising_category,
# MAGIC     TRIM(ChildStyleDescription)                          AS name_child_style,
# MAGIC     TRIM(ParentStyleDescription)                         AS name_parent_style,
# MAGIC     TRIM(PricePoint)                                     AS name_price_point,
# MAGIC     TRIM(AssociationCode)                                AS code_association,
# MAGIC 
# MAGIC     -- Classification - Sales
# MAGIC     TRIM(SalesClassCode)                                 AS code_sales_class,
# MAGIC     TRIM(SalesClassDescription)                          AS name_sales_class_description,
# MAGIC     TRIM(SalesClass)                                     AS name_sales_class,
# MAGIC     TRIM(AFISalesCategoryCode)                           AS code_afi_sales_category,
# MAGIC     TRIM(AFISalesCategory)                               AS name_afi_sales_category,
# MAGIC     TRIM(AFISalesDivisionCode)                           AS code_afi_sales_division,
# MAGIC     TRIM(AFISalesDivision)                               AS name_afi_sales_division,
# MAGIC     TRIM(AFIFinanceDivision)                             AS name_afi_finance_division,
# MAGIC 
# MAGIC     -- Classification - Discount
# MAGIC     TRIM(DiscountClassCode)                              AS code_discount_class,
# MAGIC     TRIM(DiscountClassDescription)                       AS name_discount_class_description,
# MAGIC     TRIM(DiscountClass)                                  AS name_discount_class,
# MAGIC 
# MAGIC     -- Classification - Commission
# MAGIC     TRIM(CommissionClassCode)                            AS code_commission_class,
# MAGIC     TRIM(CommissionClassDescription)                     AS name_commission_class_description,
# MAGIC     TRIM(CommissionClass)                                AS name_commission_class,
# MAGIC 
# MAGIC     -- Classification - Freight
# MAGIC     TRIM(FreightClassCode)                               AS code_freight_class,
# MAGIC     TRIM(FreightClassDescription)                        AS name_freight_class_description,
# MAGIC     TRIM(FreightClass)                                   AS name_freight_class,
# MAGIC 
# MAGIC     -- Classification - Collective
# MAGIC     TRIM(CollectiveClassCode)                            AS code_collective_class,
# MAGIC     TRIM(CollectiveClass)                                AS name_collective_class,
# MAGIC 
# MAGIC     -- Office & Origin
# MAGIC     TRIM(ResponsibleOffice)                              AS code_responsible_office,
# MAGIC     TRIM(`Import/DomesticCode`)                          AS code_import_domestic,
# MAGIC     TRIM(CountryofOrigin)                                AS name_country_of_origin,
# MAGIC     TRIM(CEXCode)                                        AS code_cex,
# MAGIC 
# MAGIC     -- Status
# MAGIC     TRIM(AFIItemStatus)                                  AS code_afi_item_status,
# MAGIC     TRIM(ManufacturingStatus)                            AS code_manufacturing_status,
# MAGIC     TRIM(CurrentSCPManufacturingStatus)                  AS code_current_scp_manufacturing_status,
# MAGIC     TRIM(MarketingItemStatus)                            AS code_marketing_item_status,
# MAGIC     TRIM(MarketingStatusDescription)                     AS name_marketing_status,
# MAGIC     TRIM(CurrentStatus)                                  AS code_current_status,
# MAGIC     CAST(ManufacturingStatusChangeDate AS DATE)          AS dt_manufacturing_status_change,
# MAGIC 
# MAGIC     -- Flags
# MAGIC     CASE WHEN LOWER(TRIM(MainPieceItem)) = 'true' THEN true ELSE false END   AS is_main_piece,
# MAGIC     CAST(CommodityItem AS INT)                           AS num_commodity_item,
# MAGIC     TRIM(SellableItemFlag)                               AS code_sellable_item,
# MAGIC     CAST(F123ProductFlag AS INT)                         AS is_f123_product,
# MAGIC     CAST(HSCoreProductFlag AS INT)                       AS is_hs_core_product,
# MAGIC     CAST(HSProprietaryProductFlag AS INT)                AS is_hs_proprietary_product,
# MAGIC     CAST(HSExclusiveFlag AS INT)                         AS is_hs_exclusive,
# MAGIC     CAST(BerklineProductFlag AS INT)                     AS is_berkline_product,
# MAGIC     CAST(BenchcraftProductFlag AS INT)                   AS is_benchcraft_product,
# MAGIC     CAST(NewMillenniumProductFlag AS INT)                AS is_new_millennium_product,
# MAGIC     CAST(BardiniProductFlag AS INT)                      AS is_bardini_product,
# MAGIC     CAST(ShanghaiStore AS INT)                           AS is_shanghai_store,
# MAGIC     CAST(DefaultGroup AS INT)                            AS num_default_group,
# MAGIC 
# MAGIC     -- Market
# MAGIC     TRIM(MarketIntroducedAt)                             AS name_market_introduced_at,
# MAGIC     CAST(MarketBeginDate AS DATE)                        AS dt_market_begin,
# MAGIC     CAST(MarketEndDate AS DATE)                          AS dt_market_end,
# MAGIC 
# MAGIC     -- Pricing
# MAGIC     CAST(FOBPrice AS DECIMAL(14,3))                      AS amt_fob_price,
# MAGIC     TRIM(GoodBetterBestForPricePoint)                    AS code_good_better_best,
# MAGIC     CAST(GBBSortId AS INT)                               AS num_gbb_sort,
# MAGIC 
# MAGIC     -- Vendor
# MAGIC     TRIM(PrimaryVendor)                                  AS code_primary_vendor,
# MAGIC     TRIM(PrimaryVendorName)                              AS name_primary_vendor,
# MAGIC 
# MAGIC     -- Invoice & Forecast
# MAGIC     TRIM(InitialInvoicePeriod)                           AS code_initial_invoice_period,
# MAGIC     CAST(InitialInvoiceQty AS INT)                       AS qty_initial_invoice,
# MAGIC     TRIM(ItemForecastPlannerID)                          AS id_item_forecast_planner,
# MAGIC 
# MAGIC     -- Package / Main Piece
# MAGIC     TRIM(MainPiece)                                      AS code_main_piece
# MAGIC 
# MAGIC FROM dbo.brz_supplychain_dw__dimcurrentproductdetails
# MAGIC -- WHERE ItemSKU IS NOT NULL
# MAGIC -- AND ItemSKU <> "N/A"

# METADATA ********************

# META {
# META   "language": "sparksql",
# META   "language_group": "synapse_pyspark"
# META }
