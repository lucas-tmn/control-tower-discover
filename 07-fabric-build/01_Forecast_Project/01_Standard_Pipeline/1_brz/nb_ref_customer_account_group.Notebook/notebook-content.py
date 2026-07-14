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

TARGET_TABLE = "ref_customer_account_group"
SOURCE_TABLE = "Wholesale_ProductSourcing_AFI/CustomerGrouping"

COLUMN_SQL = """
SELECT
    TRIM(CAST(CustomerNumber AS STRING))                 AS id_customer,
    UPPER(TRIM(CustomerGroup))                           AS code_customer_group,
    TRIM(CustomerGroupLevel3)                            AS name_customer_group_level3,
    TRIM(BusinessTypeCode)                               AS name_business_type,
    TRIM(usra)                                           AS name_created_by,
    CAST(dtea AS TIMESTAMP)                              AS ts_created,
    TRIM(usrc)                                           AS name_modified_by,
    CAST(dtec AS TIMESTAMP)                              AS ts_modified

FROM raw_source
WHERE CustomerNumber IS NOT NULL
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
