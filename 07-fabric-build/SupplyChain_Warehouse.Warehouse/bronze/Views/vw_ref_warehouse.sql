-- Auto Generated (Do not modify) EEC817E434050D81CD65594795249060C28F79F52AD1C572B7B0B75B0FF062AE

CREATE   VIEW bronze.vw_ref_warehouse AS
SELECT
    CAST(AFIWarehousesKey AS INT)            AS sk_warehouse,
    TRIM(WarehouseCode)                      AS code_warehouse,
    TRIM(IntransitWarehouse)                 AS code_intransit_warehouse,
    TRIM(ContainerDirectWarehouse)           AS code_container_direct,
    CAST(ControlledWarehouse AS INT)         AS is_controlled_warehouse,
    TRIM(WarehouseLocation)                  AS name_warehouse_location,
    TRIM(WarehouseOrderGroup)                AS name_warehouse_order_group,
    CAST(FinanceInventoryReportFlag AS INT)  AS is_finance_inventory_report
FROM Enterprise_Lakehouse.SupplyChain_DW.DimAFIWarehouses
WHERE AFIWarehousesKey IS NOT NULL