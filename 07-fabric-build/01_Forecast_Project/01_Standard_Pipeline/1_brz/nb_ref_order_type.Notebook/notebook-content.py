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

TARGET_TABLE = "ref_order_type"
SOURCE_TABLE = "Wholesale_Codis_AFI/AAORDTYP"

COLUMN_SQL = """
    SELECT
        TRIM(OTCODE)                                    AS code_order_type,
        TRIM(OTDES1)                                    AS name_order_type,
        TRIM(OTDES2)                                    AS name_order_type_short,
        TRIM(OORDCL)                                    AS code_order_class,
        CAST(OOTCAT AS INT)                             AS num_order_category,
        CASE WHEN TRIM(OROUTE) = 'Y' THEN true ELSE false END    AS is_route_eligible,
        CASE WHEN TRIM(OADCHG) = 'Y' THEN true ELSE false END    AS is_additional_charge,
        CASE WHEN TRIM(OARFLG) = 'Y' THEN true ELSE false END    AS is_auto_replenish,
        CASE WHEN TRIM(OWNEXP) = 'Y' THEN true ELSE false END    AS is_will_notify_expedite,
        CASE WHEN TRIM(OMINEXC) = 'Y' THEN true ELSE false END   AS is_minimum_exception,
        TRIM(OREQMNT)                                  AS code_requirement_type,
        CASE WHEN TRIM(OFDESCH) = 'Y' THEN true ELSE false END   AS is_force_delivery_schedule,
        CASE WHEN TRIM(OFDRIMS) = 'Y' THEN true ELSE false END   AS is_force_delivery_rims,
        TRIM(OTRPTYP)                                   AS code_transport_type,
        CAST(OZNLTIM AS INT)                            AS num_zone_lead_time_days,
        CASE WHEN TRIM(OSPECHND) = 'Y' THEN true ELSE false END  AS is_special_handling,
        CASE WHEN TRIM(OAUTORSCH) = 'Y' THEN true ELSE false END AS is_auto_reschedule,
        CASE WHEN TRIM(OUSRDFN) = 'Y' THEN true ELSE false END   AS is_user_defined,
        TRIM(OTUSER)                                    AS name_modified_by,
        to_date(CAST(OTDATE AS STRING), 'yyyyMMdd')     AS dt_modified
    FROM raw_source
    WHERE OTCODE IS NOT NULL
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
