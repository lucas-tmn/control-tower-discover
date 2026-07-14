[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "Wholesale_SalesHistory_AFI InvoiceHeader_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"Wholesale_SalesHistory_AFI InvoiceHeader" = let
    // 1. Kết nối nguồn dữ liệu
    Source = Sql.Database("ashley-edw.database.windows.net", "ASHLEY_EDW"),

    // 2. Native SQL Query — toàn bộ SELECT, TRIM, CAST, NULL-handling chạy trên SQL Server
    RawQuery = Value.NativeQuery(Source, "
        SELECT
            /* ── Business Keys / IDs ── */
            RTRIM(LTRIM(CAST(InvoiceNumber     AS VARCHAR(50))))  AS id_invoice,
            RTRIM(LTRIM(CAST(CustomerNumber    AS VARCHAR(50))))  AS id_customer,
            RTRIM(LTRIM(CAST(ShiptoNumber      AS VARCHAR(50))))  AS id_ship_to,
            RTRIM(LTRIM(CAST(OrderNumber       AS VARCHAR(50))))  AS id_order,
            RTRIM(LTRIM(CAST(PurchaseOrder     AS VARCHAR(50))))  AS id_purchase_order,
            RTRIM(LTRIM(CAST(Warehouse         AS VARCHAR(50))))  AS id_warehouse,
            RTRIM(LTRIM(CAST(ShiptoSalesman    AS VARCHAR(50))))  AS id_salesman,
            RTRIM(LTRIM(CAST(TripNumber        AS VARCHAR(50))))  AS id_trip,
            RTRIM(LTRIM(CAST(DropNumber        AS VARCHAR(50))))  AS id_drop,
            RTRIM(LTRIM(CAST(PromotionNumber   AS VARCHAR(50))))  AS id_promotion,
            RTRIM(LTRIM(CAST(CreditApprovalNBR AS VARCHAR(50))))  AS id_credit_approval,

            /* ── Dates (CleanDate logic: '0', '0.0', '' → NULL) ── */
            CAST(InvoiceDate AS DATE)  AS dt_invoice,

            CASE 
                WHEN RTRIM(LTRIM(CAST(RequestDate AS VARCHAR(20)))) IN ('0', '0.0', '')
                THEN NULL ELSE TRY_CAST(RequestDate AS DATE)
            END AS dt_request,

            CASE 
                WHEN RTRIM(LTRIM(CAST(OrderDate AS VARCHAR(20)))) IN ('0', '0.0', '')
                THEN NULL ELSE TRY_CAST(OrderDate AS DATE)
            END AS dt_order,

            CASE 
                WHEN RTRIM(LTRIM(CAST(TripCreatedDate AS VARCHAR(20)))) IN ('0', '0.0', '')
                THEN NULL ELSE TRY_CAST(TripCreatedDate AS DATE)
            END AS dt_trip_created,

            /* ── Amounts ── */
            CAST(InvoiceAmount  AS FLOAT)  AS amt_invoice,
            CAST(TaxAmount      AS FLOAT)  AS amt_tax,
            CAST(TermsDiscount  AS FLOAT)  AS amt_terms_discount,

            /* ── Names & Descriptions ── */
            RTRIM(LTRIM(ShiptoName))        AS name_ship_to,
            RTRIM(LTRIM(ShiptoAddress1))    AS name_ship_to_address_1,
            RTRIM(LTRIM(ShiptoAddress2))    AS name_ship_to_address_2,
            RTRIM(LTRIM(ShiptoCity))        AS name_ship_to_city,
            RTRIM(LTRIM(SoldtoName))        AS name_sold_to,
            RTRIM(LTRIM(ShiptoCountryName)) AS name_ship_to_country,
            RTRIM(LTRIM(ShipInstructions))  AS name_ship_instructions,

            /* ── Codes & Flags ── */
            RTRIM(LTRIM(ShiptoState))          AS code_ship_to_state,
            RTRIM(LTRIM(ShiptoZipCode))        AS code_ship_to_zip,
            RTRIM(LTRIM(OrderArrivalCode))     AS code_order_arrival,
            RTRIM(LTRIM(AdvertisingFlag))      AS code_advertising_flag,
            RTRIM(LTRIM(OrderType))            AS code_order_type,
            RTRIM(LTRIM(OrderTypePrimary))     AS code_order_type_primary,
            RTRIM(LTRIM(OrderTypeSecondary))   AS code_order_type_secondary,
            RTRIM(LTRIM(OrderTypeUsrDefine3))  AS code_order_type_usr_3,
            RTRIM(LTRIM(OrderTypeUsrDefine4))  AS code_order_type_usr_4,
            RTRIM(LTRIM(CreditCode))           AS code_credit,
            RTRIM(LTRIM(CurrencyCode))         AS code_currency,

            /* ── Numeric / Quantities ── */
            CAST(PostingMonth AS BIGINT)  AS num_posting_month,
            CAST(LeadTime     AS BIGINT)  AS num_lead_time_days,
            CAST(Sequence     AS BIGINT)  AS num_sequence,
            CAST(ShipWeight   AS FLOAT)   AS val_ship_weight

        FROM Wholesale_SalesHistory_AFI.InvoiceHeader
        WHERE InvoiceDate >= '2023-01-01'
          AND InvoiceNumber IS NOT NULL
    ")
in
    RawQuery;
shared #"Wholesale_SalesHistory_AFI InvoiceHeader_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "brz_saleshistory_afi__invoiceheader_ver2", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
