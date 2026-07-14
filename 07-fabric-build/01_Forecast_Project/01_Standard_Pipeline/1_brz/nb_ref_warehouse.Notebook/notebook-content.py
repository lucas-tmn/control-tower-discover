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

TARGET_TABLE  = "ref_warehouse"
SOURCE_TABLE  = "SupplyChain_DW/DimAFIWarehouses"

COLUMN_SQL = """
    SELECT
        CAST(AFIWarehousesKey AS INT)            AS sk_warehouse,
        TRIM(WarehouseCode)                      AS code_warehouse,
        TRIM(IntransitWarehouse)                 AS code_intransit_warehouse,
        TRIM(ContainerDirectWarehouse)           AS code_container_direct,
        CAST(ControlledWarehouse AS INT)         AS is_controlled_warehouse,
        TRIM(WarehouseLocation)                  AS name_warehouse_location,
        TRIM(WarehouseOrderGroup)                AS name_warehouse_order_group,
        CAST(FinanceInventoryReportFlag AS INT)  AS is_finance_inventory_report
    FROM raw_source
    WHERE AFIWarehousesKey IS NOT NULL
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
