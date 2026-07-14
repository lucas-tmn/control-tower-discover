-- Fabric notebook source

-- METADATA ********************

-- META {
-- META   "kernel_info": {
-- META     "name": "synapse_pyspark"
-- META   },
-- META   "dependencies": {
-- META     "lakehouse": {
-- META       "default_lakehouse": "62a3081e-4093-4f46-856c-f50aa58732fa",
-- META       "default_lakehouse_name": "SupplyChain_Lakehouse",
-- META       "default_lakehouse_workspace_id": "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0",
-- META       "known_lakehouses": [
-- META         {
-- META           "id": "62a3081e-4093-4f46-856c-f50aa58732fa"
-- META         }
-- META       ]
-- META     }
-- META   }
-- META }

-- CELL ********************

-- MAGIC %%sql
-- MAGIC /* SILVER LAYER: WAREHOUSE - DIM TABLE
-- MAGIC    Target: dbo.brz_supplychain_dw__dimafiwarehouses
-- MAGIC    Logic: WAREHOUSE - DIM TABLE
-- MAGIC */
-- MAGIC 
-- MAGIC CREATE OR REPLACE TABLE dbo.slv_warehouse AS
-- MAGIC SELECT 
-- MAGIC     CAST(AFIWarehousesKey AS INT)                        AS sk_warehouse,
-- MAGIC     TRIM(WarehouseCode)                                  AS code_warehouse,
-- MAGIC     TRIM(IntransitWarehouse)                             AS code_intransit_warehouse,
-- MAGIC     TRIM(ContainerDirectWarehouse)                       AS code_container_direct,
-- MAGIC     CAST(ControlledWarehouse AS INT)                     AS is_controlled_warehouse,
-- MAGIC     TRIM(WarehouseLocation)                              AS name_warehouse_location,
-- MAGIC     TRIM(WarehouseOrderGroup)                            AS name_warehouse_order_group,
-- MAGIC     CAST(FinanceInventoryReportFlag AS INT)              AS is_finance_inventory_report
-- MAGIC 
-- MAGIC FROM dbo.brz_supplychain_dw__dimafiwarehouses
-- MAGIC -- WHERE AFIWarehousesKey IS NOT NULL

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
