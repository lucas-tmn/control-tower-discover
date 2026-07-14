[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "SupplyChain_DW DimCurrentProductDetails_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"SupplyChain_DW DimCurrentProductDetails" = let
    // 1. Kết nối nguồn dữ liệu
    Source = Sql.Database("ashley-edw.database.windows.net", "ASHLEY_EDW"),

    // 2. Native SQL — toàn bộ SELECT, TRIM, CAST, FLAG logic chạy trên SQL Server
    RawQuery = Value.NativeQuery(Source, "
        SELECT
            /* ── Surrogate Key ── */
            CAST(CurrentProductDetailsKey AS BIGINT)  AS sk_product,

            /* ── Business Keys / IDs ── */
            RTRIM(LTRIM([Item SKU]))                  AS id_item_sku,
            RTRIM(LTRIM([Item]))                      AS id_item,
            RTRIM(LTRIM([SCP Item]))                  AS id_scp_item,

            /* ── Item Descriptions ── */
            RTRIM(LTRIM([Item Description]))           AS name_item_description,
            RTRIM(LTRIM([Colors]))                     AS name_color,
            CAST([Qty In Box] AS BIGINT)               AS num_qty_in_box,
            RTRIM(LTRIM([UOM]))                        AS code_uom,

            /* ── Series ── */
            RTRIM(LTRIM([Series Number]))              AS code_series,
            RTRIM(LTRIM([Ext Series Number]))          AS code_ext_series,
            RTRIM(LTRIM([Item Ext Series Number]))     AS code_item_ext_series,
            RTRIM(LTRIM([Series Name]))                AS name_series,
            RTRIM(LTRIM([Series Color]))               AS name_series_color,
            RTRIM(LTRIM([Series Description]))         AS name_series_description,

            /* ── Composite Descriptions ── */
            RTRIM(LTRIM([Item-Description-Series]))                AS name_item_desc_series,
            RTRIM(LTRIM([SH-Item-Description-Series]))             AS name_sh_item_desc_series,
            RTRIM(LTRIM([SH-Series-Description]))                  AS name_sh_series_description,
            RTRIM(LTRIM([Item-Description-Series-Item Color]))     AS name_item_desc_series_color,

            /* ── Item Classification ── */
            RTRIM(LTRIM([Item Class Code]))            AS code_item_class,
            RTRIM(LTRIM([Item Class Name]))            AS name_item_class,
            RTRIM(LTRIM([Item Class]))                 AS name_item_class_full,
            RTRIM(LTRIM([Item Code]))                  AS code_item,
            RTRIM(LTRIM([Item Grouping]))              AS name_item_grouping,
            RTRIM(LTRIM([Item Style Code]))            AS code_item_style,
            RTRIM(LTRIM([Item Style Group]))           AS name_item_style_group,
            RTRIM(LTRIM([Item Style]))                 AS name_item_style,

            /* ── Retail & Merchandising ── */
            RTRIM(LTRIM([Product Line]))               AS name_product_line,
            RTRIM(LTRIM([Retail Category Code]))           AS code_retail_category,
            RTRIM(LTRIM([Retail Category Description]))    AS name_retail_category,
            RTRIM(LTRIM([Merchandising Category]))         AS name_merchandising_category,
            RTRIM(LTRIM([Child Style Description]))        AS name_child_style,
            RTRIM(LTRIM([Parent Style Description]))       AS name_parent_style,
            RTRIM(LTRIM([Price Point]))                    AS name_price_point,
            RTRIM(LTRIM([Association Code]))                AS code_association,

            /* ── Sales Class ── */
            RTRIM(LTRIM([Sales Class Code]))               AS code_sales_class,
            RTRIM(LTRIM([Sales Class Description]))        AS name_sales_class_description,
            RTRIM(LTRIM([Sales Class]))                    AS name_sales_class,

            /* ── AFI Sales & Finance ── */
            RTRIM(LTRIM([AFI Sales Category Code]))        AS code_afi_sales_category,
            RTRIM(LTRIM([AFI Sales Category]))             AS name_afi_sales_category,
            RTRIM(LTRIM([AFI Sales Division Code]))        AS code_afi_sales_division,
            RTRIM(LTRIM([AFI Sales Division]))             AS name_afi_sales_division,
            RTRIM(LTRIM([AFI Finance Division]))           AS name_afi_finance_division,

            /* ── Discount / Commission / Freight Class ── */
            RTRIM(LTRIM([Discount Class Code]))            AS code_discount_class,
            RTRIM(LTRIM([Discount Class Description]))     AS name_discount_class_description,
            RTRIM(LTRIM([Discount Class]))                 AS name_discount_class,
            RTRIM(LTRIM([Commission Class Code]))          AS code_commission_class,
            RTRIM(LTRIM([Commission Class Description]))   AS name_commission_class_description,
            RTRIM(LTRIM([Commission Class]))               AS name_commission_class,
            RTRIM(LTRIM([Freight Class Code]))             AS code_freight_class,
            RTRIM(LTRIM([Freight Class Description]))      AS name_freight_class_description,
            RTRIM(LTRIM([Freight Class]))                  AS name_freight_class,
            RTRIM(LTRIM([Collective Class Code]))          AS code_collective_class,
            RTRIM(LTRIM([Collective Class]))               AS name_collective_class,

            /* ── Origin & Office ── */
            RTRIM(LTRIM([Responsible Office]))             AS code_responsible_office,
            RTRIM(LTRIM([Import/Domestic Code]))           AS code_import_domestic,
            RTRIM(LTRIM([Country of Origin]))              AS name_country_of_origin,
            RTRIM(LTRIM([CEX Code]))                       AS code_cex,

            /* ── Status ── */
            RTRIM(LTRIM([AFI Item Status]))                        AS code_afi_item_status,
            RTRIM(LTRIM([Manufacturing Status]))                   AS code_manufacturing_status,
            RTRIM(LTRIM([Current SCP Manufacturing Status]))       AS code_current_scp_manufacturing_status,
            RTRIM(LTRIM([Marketing Item Status]))                  AS code_marketing_item_status,
            RTRIM(LTRIM([Marketing Status Description]))           AS name_marketing_status,
            RTRIM(LTRIM([Current Status]))                         AS code_current_status,
            CAST([Manufacturing Status Change Date] AS DATE)       AS dt_manufacturing_status_change,

            /* ── Flags (BIT / INT) ── */
            CASE WHEN LOWER(RTRIM(LTRIM([Main Piece Item]))) = 'true'
              THEN 1 ELSE 0
            END                                            AS is_main_piece,
            CAST([Commodity Item]              AS BIGINT)  AS num_commodity_item,
            RTRIM(LTRIM([Sellable Item Flag]))             AS code_sellable_item,
            CAST([F123 Product Flag]           AS BIGINT)  AS is_f123_product,
            CAST([HS Core Product Flag]        AS BIGINT)  AS is_hs_core_product,
            CAST([HS Proprietary Product Flag] AS BIGINT)  AS is_hs_proprietary_product,
            CAST([HS Exclusive Flag]           AS BIGINT)  AS is_hs_exclusive,
            CAST([Berkline Product Flag]       AS BIGINT)  AS is_berkline_product,
            CAST([Benchcraft Product Flag]     AS BIGINT)  AS is_benchcraft_product,
            CAST([New Millennium Product Flag] AS BIGINT)  AS is_new_millennium_product,
            CAST([Bardini Product Flag]        AS BIGINT)  AS is_bardini_product,
            CAST([Shanghai Store]              AS BIGINT)  AS is_shanghai_store,
            CAST([Default Group]     AS BIGINT)            AS num_default_group,

            /* ── Market ── */
            RTRIM(LTRIM([Market Introduced At]))           AS name_market_introduced_at,
            CAST([Market Begin Date] AS DATE)              AS dt_market_begin,
            CAST([Market End Date]   AS DATE)              AS dt_market_end,

            /* ── Pricing ── */
            CAST([GBBSortId]         AS BIGINT)            AS num_gbb_sort,
            RTRIM(LTRIM([Good Better Best For Price Point]))  AS code_good_better_best,
            CAST([FOB Price] AS DECIMAL(14,3))    AS amt_fob_price,

            /* ── Vendor ── */
            RTRIM(LTRIM([Primary Vendor]))                    AS code_primary_vendor,
            RTRIM(LTRIM([Primary Vendor Name]))               AS name_primary_vendor,

            /* ── Invoice & Forecast ── */
            CAST([Initial Invoice Qty] AS BIGINT)          AS qty_initial_invoice,
            RTRIM(LTRIM([Initial Invoice Period]))            AS code_initial_invoice_period,
            RTRIM(LTRIM([Item Forecast Planner ID]))          AS id_item_forecast_planner,

            /* ── Package / Main Piece ── */
            RTRIM(LTRIM([Main Piece]))                        AS code_main_piece

        FROM SupplyChain_DW.DimCurrentProductDetails
        WHERE [Item SKU] IS NOT NULL
          AND [Item SKU] <> 'N/A'
    "),
  #"Changed column type" = Table.TransformColumnTypes(RawQuery, {{"dt_manufacturing_status_change", type date}, {"is_main_piece", type logical}, {"dt_market_begin", type date}, {"dt_market_end", type date}})
in
    #"Changed column type";
shared #"SupplyChain_DW DimCurrentProductDetails_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "ref_product_ver2", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
