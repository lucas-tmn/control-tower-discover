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
# META         },
# META         {
# META           "id": "584e7d2c-46ca-49dc-bb6c-68df6ef4f424"
# META         }
# META       ]
# META     }
# META   }
# META }

# CELL ********************

TARGET_TABLE = "brz_saleshistory_afi__invoicedetail"
SOURCE_TABLE = "SalesHistory_AFI/InvoiceDetail"  # ← chỉ điền đuôi

COLUMN_SQL = """
    SELECT
        -- Keys & Identifiers
        TRIM(CustomerNumber)                                    AS id_customer,
        TRIM(InvoiceNumber)                                     AS id_invoice,
        TRIM(ExtendedInvoiceNumber)                             AS id_invoice_extended,
        TRIM(ItemSKU)                                           AS id_item_sku,
        CAST(ItemSequence AS INT)                               AS num_item_sequence,
        TRIM(OrderNumber)                                       AS id_order,
        TRIM(ShiptoNumber)                                      AS code_ship_to,
        TRIM(Warehouse)                                         AS code_warehouse,
        TRIM(CurrencyCode)                                      AS code_currency,

        -- Quantities
        CAST(QuantityShipped AS DECIMAL(12,3))                  AS qty_shipped,
        CAST(QuantityOrdered AS DECIMAL(12,3))                  AS qty_ordered,
        CAST(QuantityBackOrdered AS DECIMAL(12,3))              AS qty_backordered,

        -- Pricing & Amounts
        CAST(InvoiceAmount AS DECIMAL(14,2))                    AS amt_invoice,
        CAST(Price AS DECIMAL(14,2))                            AS amt_price,
        CAST(StandardPrice AS DECIMAL(14,2))                    AS amt_standard_price,
        CAST(ContractPrice AS DECIMAL(14,2))                    AS amt_contract_price,
        CAST(NetSales AS DECIMAL(14,3))                         AS amt_net_sales,
        CAST(Discount AS DECIMAL(12,2))                         AS amt_discount,
        CAST(PriceAdjustment AS DECIMAL(12,2))                  AS amt_price_adjustment,
        CAST(Freight AS DECIMAL(12,2))                          AS amt_freight,
        CAST(AdvertisingAccrual AS DECIMAL(12,2))               AS amt_advertising_accrual,
        CAST(DFIDiscount AS DECIMAL(12,2))                      AS amt_dfi_discount,

        -- Dates
        CAST(InvoiceDate AS DATE)                               AS dt_invoice,
        CAST(OrderDate AS DATE)                                 AS dt_order,
        CAST(RequestDate AS DATE)                               AS dt_request,
        CAST(OrderEntry AS DATE)                                AS dt_order_entry,
        CAST(PromisedDelivery AS DATE)                          AS dt_promised_delivery,
        CAST(OriginalRequestDate AS DATE)                       AS dt_original_request,
        CAST(OriginalPromiseDate AS DATE)                       AS dt_original_promise,
        CAST(CurrentRequestDate AS DATE)                        AS dt_current_request,
        CAST(CurrentPromiseDate AS DATE)                        AS dt_current_promise,
        CAST(DeliveryDate AS DATE)                              AS dt_delivery,
        CAST(ActualDelivery AS DATE)                            AS dt_actual_delivery,
        CAST(TripCloseDate AS DATE)                             AS dt_trip_close,
        CAST(FirstScanDate AS DATE)                             AS dt_first_scan,
        CAST(TripCreateDate AS DATE)                            AS dt_trip_create,
        CAST(OriginalInvoiceDate AS DATE)                       AS dt_original_invoice,
        CAST(OriginalOrderDate AS DATE)                         AS dt_original_order,

        -- Delivery Days
        TRIM(CAST(DefaultDeliveryDays AS STRING))               AS code_default_delivery_days,
        TRIM(CAST(DeliveryDays AS STRING))                      AS val_delivery_days,
        TRIM(CAST(DeliveryDaysOriginalPromiseDate AS STRING))   AS val_delivery_days_original_promise,
        TRIM(CAST(DeliveryDaysRaw AS STRING))                   AS val_delivery_days_raw,
        TRIM(CAST(DeliveryDaysOriginalPromiseDateRaw AS STRING)) AS val_delivery_days_original_promise_raw,

        -- Salesperson
        TRIM(CAST(BilltoSalesman AS STRING))                    AS id_salesperson_billto,
        TRIM(CAST(ShiptoSalesman AS STRING))                    AS id_salesperson_shipto,

        -- Trip & Routing
        CAST(TripNumber AS INT)                                 AS num_trip,
        CAST(DropNumber AS INT)                                 AS num_drop,

        -- Item Attributes
        TRIM(ItemClass)                                         AS code_item_class,
        TRIM(CustomerSku)                                       AS name_customer_sku,
        TRIM(PurchaseOrder)                                     AS id_purchase_order,
        TRIM(CAST(PostingMonth AS STRING))                      AS code_posting_month,

        -- Credit & Status
        TRIM(CreditCode)                                        AS code_credit,
        TRIM(CAST(PriorityCode AS STRING))                      AS code_priority,
        TRIM(OrderItemStatus)                                   AS code_order_item_status,
        CAST(OrderPriority AS INT)                              AS num_order_priority,
        TRIM(LineReleaseNumber)                                 AS code_line_release,

        -- Order Type & Codes
        TRIM(OrderType)                                         AS code_order_type,
        TRIM(OrderType3)                                        AS code_order_type_3,
        TRIM(PriceCode)                                         AS code_price,
        TRIM(ItemDiscountCode)                                  AS code_item_discount,
        TRIM(commissioncode)                                    AS code_commission,
        TRIM(FreightCode)                                       AS code_freight,
        TRIM(DiscountSalesClass)                                AS code_discount_sales_class,
        TRIM(FreightSalesClass)                                 AS code_freight_sales_class,
        TRIM(BuyGroupCode)                                      AS code_buy_group,

        -- Exception & Pricing IDs
        CAST(ExceptionID AS INT)                                AS id_exception,
        CAST(GroupPricingExceptionID AS INT)                    AS id_group_pricing_exception,

        -- Percentages
        CAST(WarehouseOperationPercent AS DECIMAL(10,4))        AS pct_warehouse_operation,
        CAST(PriceAdderPercent AS DECIMAL(10,4))                AS pct_price_adder,
        CAST(CalculatedAllowancePercent AS DECIMAL(10,4))       AS pct_calculated_allowance,
        CAST(PackageDiscountAllocationPercent AS DECIMAL(10,4)) AS pct_package_discount_allocation,

        -- Package
        TRIM(PackageDescription)                                AS name_package_description,
        TRIM(PackageID)                                         AS id_package,
        CAST(PackagePrice AS DECIMAL(12,2))                     AS amt_package_price,
        CAST(PackageItemPrice AS DECIMAL(12,2))                 AS amt_package_item_price,
        CAST(PackageItemDiscount AS DECIMAL(12,3))              AS val_package_item_discount,

        -- Original References
        TRIM(CAST(OriginalInvoiceNumber AS STRING))             AS id_original_invoice,
        TRIM(CAST(OriginalOrderNumber AS STRING))               AS id_original_order,
        CAST(OriginalSequenceNumber AS INT)                     AS num_original_sequence,
        TRIM(CAST(OriginalDeliveryMethod AS STRING))            AS code_original_delivery_method

    FROM raw_source
    WHERE InvoiceNumber IS NOT NULL
      AND InvoiceDate >= '2023-01-01'
"""

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

notebookutils.notebook.run(
    "brz_engine",
    7200,
    {
        "TARGET_TABLE": TARGET_TABLE,
        "SOURCE_TABLE": SOURCE_TABLE,
        "COLUMN_SQL":   COLUMN_SQL
    }
)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
