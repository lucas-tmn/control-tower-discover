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

TARGET_TABLE = "brz_wholesale_codis_afi__comast"
SOURCE_TABLE = "Wholesale_Codis_AFI/COMAST"

COLUMN_SQL = """
    SELECT
        -- Keys & Identifiers
        TRIM(ACREC)                                         AS code_record_type,
        TRIM(ORDNO)                                         AS id_order,
        TRIM(CUSNO)                                         AS id_customer,
        TRIM(CUSPO)                                         AS id_customer_po,

        -- Order Info
        to_date(CAST(ORDTE AS STRING), 'yyyyMMdd')          AS dt_order,
        CAST(ORVAL AS DECIMAL(14,2))                        AS amt_order_value,
        TRIM(HOUSE)                                         AS code_warehouse,
        TRIM(SLSNO)                                         AS code_salesperson,
        TRIM(SHPNO)                                         AS code_ship_to,

        -- Scheduling & Shipping
        to_date(CAST(RQDTE AS STRING), 'yyyyMMdd')          AS dt_requested,
        CAST(SHLTC AS INT)                                  AS num_lead_time_days,
        TRIM(SHINS)                                         AS name_shipping_instructions,
        to_date(CAST(CUSPD AS STRING), 'yyyyMMdd')          AS dt_customer_paid,

        -- Flags
        TRIM(MPROR)                                         AS code_priority,
        TRIM(CMEMO)                                         AS code_memo
    FROM raw_source
    WHERE ORDNO IS NOT NULL
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
