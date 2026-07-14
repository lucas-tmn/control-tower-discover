---
type: Query
title: Customer Master Query
description: EDW SQL query that produces the customer master shape.
tags: [customer, customer-master, demand, fulfillment, dimension, query]
timestamp: 2026-07-06
resource: "[AFISales_DW].[DimCustomers]"
source_system: ERP
refresh_cadence: daily
data_source: ashley_edw
status: draft
---

## Purpose

Central customer dimension for supply chain planning and demand analysis. Consolidates customer account and ship-to location attributes to enable demand forecasting, order fulfillment analysis, and forecast accuracy reporting. Provides ship-to level detail for multi-location customers to capture location-specific subscription and demand patterns.

Used as the customer entity in:

- Demand forecasting models
- Order fulfillment analysis
- Forecast accuracy reporting
- Demand pattern segmentation

---

## Grain

Each row represents a unique **account and ship-to location combination** (`AccountAndShipToNumber`).

---

## Schema

| Column | Type | Meaning |
| --- | --- | --- |
| `AccountAndShipToNumber` | VARCHAR(20) | Composite key identifying the unique account-ship-to combination for multi-location demand tracking |
| `AccountNumber` | VARCHAR(10) | Account-level identifier; used as foreign key in fact tables |
| `AccountName` | VARCHAR(200) | Customer name / account name for display and filtering |
| `ShipToNumber` | VARCHAR(10) | Ship-to location code identifying the receiving location |
| `ShipToName` | VARCHAR(200) | Ship-to location name or address label |
| `CustomerGroup` | VARCHAR(100) | Customer grouping classification for demand segmentation (e.g., AFICONS, regional distributor class) |
| `CustomerSegment` | VARCHAR(100) | Market or channel segment (e.g., wholesale, retail, direct) for hierarchical reporting |
| `ReportingBusinessType` | VARCHAR(100) | Standardized business type for regulatory and revenue reporting |
| `BusinessType` | VARCHAR(100) | Business type used for customer classification and CustomerGroup derivation |
| `Address1` | VARCHAR(200) | Primary address line |
| `Address2` | VARCHAR(200) | Secondary address line |
| `Address3` | VARCHAR(200) | Tertiary address line (suite, building) |
| `Address4` | VARCHAR(200) | Quaternary address line |
| `Address5` | VARCHAR(200) | Quinary address line |
| `City` | VARCHAR(100) | City name |
| `State` | VARCHAR(2) | State abbreviation (US standard) |
| `ZipCode` | VARCHAR(10) | Postal code |
| `Country` | VARCHAR(100) | Country name or code |
| `CountryCode` | VARCHAR(10) | Country code from the ship-to geographic location |

---

## Related

- [Customer](/entities/customer.md) — Canonical customer business object definition
- [Demand Forecast](/datasets/tables/demand_forecast.md) — Demand signals indexed by customer
- [Sales Orders](/datasets/tables/sales_orders.md) — Actual customer order transactions
- [FILL IN: Link to forecast accuracy metric]

---

## Base Query

Use this query to produce the Customer Master shape while the gold `DimCustomer` table is unavailable.

```sql
SELECT [C].[Account And ShipTo Number] AS [AccountAndShipToNumber]
      ,[C].[Customer Account Number] AS [AccountNumber]
      ,CONCAT(TRIM([C].[Customer Name]), ' - ', TRIM([C].[Customer Account Number])) AS [AccountName] 
      ,[C].[Customer Shipto Number] AS [ShipToNumber]
      ,[C].[ShipTo Details] AS [ShipToName]
      ,CASE 
            WHEN [CG].[CustomerGroup] IS NOT NULL
                THEN [CG].[CustomerGroup]
            WHEN [C].[Customer Account Number] = '6000100' THEN 'AFICONS' --SAMPLE ACCOUNT
            WHEN [C].[Customer Account Number] IN ('1913400','8888000','8888300','8888600','9946600','9955000','9955100','9956600','9966100','9974000','9977400','9983800','9985500','9989200')
                THEN 'HSENT'
            WHEN [C].[Customer Account Number] = '4444400' --ASHCOMM
                THEN 'HSENT' 
            WHEN [C].[Reporting Business Type] = 'Ashley HomeStores'
                    AND [C].[Commission Code] <> '006'
                THEN 'HSLIC'
            WHEN [C].[Business Type] = 'Hybrid - Homestore and Primary'
                THEN 'HSLIC'
            WHEN [C].[Customer Account Number] = '109200'
                THEN 'NFM'
            WHEN [C].[Customer Account Number] = '3061700' --Payless in E-Retail should be AFICONS
                THEN 'AFICONS'
            WHEN [C].[Reporting Business Type] = 'E-Retail'
                THEN 'ECOMM'
            WHEN [C].[Reporting Business Type] = 'Rental'
                THEN 'MASSRENT'
            WHEN [C].[Reporting Business Type] = 'Mass Merchants'
                THEN 'MASSRENT'
            WHEN [C].[Reporting Business Type] = 'International'
                THEN 'INT'
            WHEN [C].[Customer Account Number] = '4031300'
                THEN 'RHCUST'
            WHEN [C].[Customer Account Number] = '3824800'
                THEN 'AFI DIST'
            ELSE 'AFICONS'
        END AS [CustomerGroup]
      ,[C].[Customer Segment] AS [CustomerSegment]
      ,[C].[Reporting Business Type] AS [ReportingBusinessType]
      ,[C].[Business Type] AS [BusinessType]
      ,[G].[Address 1]  AS [Address1]
      ,[G].[Address 2]  AS [Address2]
      ,[G].[Address 3]  AS [Address3]
      ,[G].[Address 4]  AS [Address4]
      ,[G].[Address 5]  AS [Address5]
      ,[G].[City]
      ,[G].[State Code] AS [State]
      ,[G].[ZipCode]
      ,[G].[Country]
      ,[G].[Country Code] AS [CountryCode]
     
  FROM [AFISales_DW].[DimCustomers] AS C
  LEFT JOIN [AFISales_DW].[DimGeographicLocations] AS G
    ON [C].[Shipto AddressID] = [G].[Address ID]
 
  INNER JOIN ( -- Filter out Accounts that haven't ordered in 5 years
SELECT DISTINCT [Account And ShipTo Number]
  FROM [SupplyChain_Enh].[ActualsCustItemWH_AFI]
  ) AS ID
    ON [C].[Account And ShipTo Number] = [ID].[Account And ShipTo Number]
 
    -- Pull in Logility Customer Groupings
  LEFT JOIN [Wholesale_ProductSourcing_AFI].[CustomerGrouping] AS CG
    ON [C].[Customer Account Number] = [CG].[CustomerNumber]
```

