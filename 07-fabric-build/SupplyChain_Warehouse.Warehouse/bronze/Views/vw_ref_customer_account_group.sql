-- Auto Generated (Do not modify) 5951EC394AB5208DDD85A5A542B2C648522687B6CA7E0475DC1CDF0DBBDD0F36

CREATE   VIEW bronze.vw_ref_customer_account_group AS
SELECT
    TRIM(CAST(CustomerNumber AS VARCHAR(200)))            AS id_customer,
    UPPER(TRIM(CustomerGroup))                           AS code_customer_group,
    TRIM(CustomerGroupLevel3)                            AS name_customer_group_level3,
    TRIM(BusinessTypeCode)                               AS name_business_type,
    TRIM(usra)                                           AS name_created_by,
    TRY_CAST(dtea AS DATETIME2(6))                       AS ts_created,
    TRIM(usrc)                                           AS name_modified_by,
    TRY_CAST(dtec AS DATETIME2(6))                       AS ts_modified
FROM Enterprise_Lakehouse.Wholesale_ProductSourcing_AFI.CustomerGrouping
WHERE CustomerNumber IS NOT NULL