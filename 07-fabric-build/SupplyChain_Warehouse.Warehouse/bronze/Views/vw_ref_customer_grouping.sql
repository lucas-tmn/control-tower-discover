-- Auto Generated (Do not modify) 7EF1BC69D6D11CE00A4369AD48DF7A110196F149AF5D5F9B013471527E00FF0A

CREATE   VIEW bronze.vw_ref_customer_grouping AS
SELECT DISTINCT
    UPPER(TRIM(CAST(CustomerGroup AS VARCHAR(50)))) AS code_customer_group
FROM Enterprise_Lakehouse.Wholesale_ProductSourcing_AFI.CustomerGrouping
WHERE CustomerGroup IS NOT NULL