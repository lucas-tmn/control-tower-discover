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

# spark.sql("""
#     CREATE TABLE IF NOT EXISTS SupplyChain_Lakehouse.dbo.utl_pipeline_metadata (
#         table_name            STRING,
#         last_watermark_value  STRING,
#         last_load_date        TIMESTAMP,
#         rows_loaded           LONG,
#         rows_rejected         LONG,
#         status                STRING,
#         error_message         STRING,
#         pipeline_notes        STRING
#     )
#     USING DELTA
# """)

# print("Done! utl_pipeline_metadata created.")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

df = spark.sql("""
    SELECT MAX(dfcSnapshot) AS max_wm
    FROM SupplyChain_Lakehouse.dbo.brz_SupplyChain_Enh_1__DemandForecastSnapshotDaily
""")

display(df)

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }

# CELL ********************

# Lấy max watermark từ bảng đã load sẵn
result = spark.sql("""
    SELECT MAX(dfcSnapshot) AS max_wm
    FROM SupplyChain_Lakehouse.dbo.brz_SupplyChain_Enh_1__DemandForecastSnapshotDaily
""").collect()

max_wm = result[0]["max_wm"]
print(f"Max watermark hiện tại: {max_wm}")

# Insert record vào metadata
spark.sql(f"""
    INSERT INTO SupplyChain_Lakehouse.dbo.utl_pipeline_metadata
    VALUES (
        'brz_SupplyChain_Enh_1__DemandForecastSnapshotDaily',
        '{max_wm}',
        current_timestamp(),
        NULL,
        0,
        'success',
        NULL,
        'Seeded manually - full load done before pipeline setup'
    )
""")

print(f"Done! Watermark seeded: {max_wm}")

# METADATA ********************

# META {
# META   "language": "python",
# META   "language_group": "synapse_pyspark"
# META }
