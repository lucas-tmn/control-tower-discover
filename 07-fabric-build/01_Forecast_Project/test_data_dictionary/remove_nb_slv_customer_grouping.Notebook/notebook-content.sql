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
-- MAGIC /* SILVER LAYER: CUSTOMER GROUP - DIM TABLE
-- MAGIC    Target: dbo.slv_customer_grouping
-- MAGIC    Logic: CUSTOMER GROUP - DIM TABLE
-- MAGIC */
-- MAGIC 
-- MAGIC CREATE OR REPLACE TABLE dbo.slv_customer_grouping AS
-- MAGIC SELECT *
-- MAGIC     TRIM(CAST(CustomerNumber AS STRING))                 AS id_customer,
-- MAGIC     TRIM(CustomerGroup)                                  AS code_customer_group,
-- MAGIC     TRIM(CustomerGroupLevel3)                            AS name_customer_group_level3,
-- MAGIC     TRIM(BusinessTypeCode)                               AS name_business_type,
-- MAGIC     TRIM(usra)                                           AS name_created_by,
-- MAGIC     CAST(dtea AS TIMESTAMP)                              AS ts_created,
-- MAGIC     TRIM(usrc)                                           AS name_modified_by,
-- MAGIC     CAST(dtec AS TIMESTAMP)                              AS ts_modified
-- MAGIC 
-- MAGIC FROM dbo.brz_wholesale_productsourcing_afi__customergrouping
-- MAGIC -- WHERE CustomerNumber IS NOT NULL

-- METADATA ********************

-- META {
-- META   "language": "sparksql",
-- META   "language_group": "synapse_pyspark"
-- META }
