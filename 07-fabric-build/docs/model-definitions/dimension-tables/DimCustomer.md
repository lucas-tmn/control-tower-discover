---
title: DimCustomer table documentation
domain: Supply Chain Planning
warehouse: SupplyChain_Gold
schema: <schema>
table_name: DimCustomer
last_updated: 2026-06-19
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

Central customer dimension for supply chain planning and demand analysis, consolidating customer attributes from `AFISales_DW.DimCustomers` (SQL master) unified with `PowerBI_SupplyChain.CustomerAcctMaster_AFI` dataflow shadow (retired after parity check). This table serves as the customer entity for demand forecasting, order fulfillment, and forecast accuracy reporting across 5+ models, with ship-to level detail for subscription and demand patterns.

---

## 2. Physical Table Definition

```sql
CREATE TABLE <warehouse>.<schema>.DimCustomer (
    [AccountAndShipToNumber] VARCHAR(20) NULL,
    [AccountNumber] VARCHAR(10) NOT NULL,
    [AccountName] VARCHAR(200) NULL,
    [ShipToNumber] VARCHAR(10) NULL,
    [ShipToName] VARCHAR(200) NULL,
    [CustomerGroup] VARCHAR(100) NULL,
    [CustomerSegment] VARCHAR(100) NULL,
    [ReportingBusinessType] VARCHAR(100) NULL,
    [BusinessTypeCode] VARCHAR(20) NULL,
    [Address1] VARCHAR(200) NULL,
    [Address2] VARCHAR(200) NULL,
    [Address3] VARCHAR(200) NULL,
    [Address4] VARCHAR(200) NULL,
    [Address5] VARCHAR(200) NULL,
    [City] VARCHAR(100) NULL,
    [State] VARCHAR(2) NULL,
    [ZipCode] VARCHAR(10) NULL,
    [Country] VARCHAR(100) NULL,
    [Region] VARCHAR(100) NULL,
    [District] VARCHAR(100) NULL
);
```

### Add the primary key

```sql
ALTER TABLE <schema>.DimCustomer
ADD CONSTRAINT PK_DimCustomer
PRIMARY KEY NONCLUSTERED ([AccountAndShipToNumber])
NOT ENFORCED;
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| `AccountAndShipToNumber` | VARCHAR(20) | Composite key combining AccountNumber and ShipToNumber for multi-location demand tracking |
| `AccountNumber` | VARCHAR(10) | Primary key — account-level grain identifier used as FK in FactActuals, FactWorkingForecast, FactCurrentForecast, FactForecastAccuracy; source accounts from `AFISales_DW.DimCustomers` |
| `AccountName` | VARCHAR(200) | Customer name / account name from master; used in report filtering and display |
| `ShipToNumber` | VARCHAR(10) | Ship-to location code; identifies individual receiving location for multi-location customers |
| `ShipToName` | VARCHAR(200) | Ship-to location name or address label |
| `CustomerGroup` | VARCHAR(100) | Customer grouping classification for demand segmentation (e.g., AFICONS, regional distributor classes); critical grain for FactWorkingForecast and FactCurrentForecast |
| `CustomerSegment` | VARCHAR(100) | Market or channel segment (e.g., wholesale, retail, direct); used for hierarchical reporting and demand patterns |
| `ReportingBusinessType` | VARCHAR(100) | AFI-standardized business type for regulatory and revenue reporting |
| `BusinessTypeCode` | VARCHAR(20) | Code/abbreviation for business type; source mapping varies; standardize on AFI reporting standard |
| `Address1` | VARCHAR(200) | Primary address line |
| `Address2` | VARCHAR(200) | Secondary address line |
| `Address3` | VARCHAR(200) | Tertiary address line (suite, building) |
| `Address4` | VARCHAR(200) | Quaternary address line (additional detail) |
| `Address5` | VARCHAR(200) | Quinary address line (additional detail) |
| `City` | VARCHAR(100) | City for account / ship-to location |
| `State` | VARCHAR(2) | State abbreviation (US standard) |
| `ZipCode` | VARCHAR(10) | Postal code |
| `Country` | VARCHAR(100) | Country name or code for international accounts |
| `Region` | VARCHAR(100) | Regional grouping for account consolidation and analysis |
| `District` | VARCHAR(100) | District or sales territory assignment |

---

## 4. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-19 | Initial draft | Robert Font Perez |
