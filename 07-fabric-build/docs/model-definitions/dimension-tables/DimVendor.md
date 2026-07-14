---
title: DimVendor table documentation
domain: Supply Chain Planning
warehouse: SupplyChain_Gold
table_name: DimVendor
schema: <schema>
last_updated: 2026-06-19
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

Central vendor dimension for supply chain planning, consolidating vendor master attributes from `PowerBI_SupplyChain.VendorMaster` (primary source) and supplemented with vendor-name lookups from `Wholesale_Purchasing_AFI.VENNAM` and `Wholesale_ProductSourcing_AFI.vendor` for PSW and sourcing reports. This table provides a single source of truth for vendor attributes (lead times, location, country of origin, active status) used across procurement, supply planning, and on-time performance reporting. Vendor-level aggregates like open purchase orders and ranking have been moved to the measure layer and are computed at report time.

---

## 2. Physical Table Definition

```sql
CREATE TABLE <warehouse>.<schema>.DimVendor (
    [VendorNumber] VARCHAR(20) NOT NULL,
    [VendorName] VARCHAR(200) NOT NULL,
    [VendorOffice] VARCHAR(100) NULL,
    [VendorOfficeLocation] VARCHAR(100) NULL,
    [VendorDesc] VARCHAR(255) NULL,
    [Country] VARCHAR(50) NULL,
    [LeadTime] INT NULL,
    [AFILeadTime] INT NULL,
    [WVFLeadTime] INT NULL,
    [VendorActive] VARCHAR(1) NULL
);
```

### Add the primary key

```sql
ALTER TABLE <schema>.DimVendor
ADD CONSTRAINT PK_DimVendor
PRIMARY KEY NONCLUSTERED ([VendorNumber])
NOT ENFORCED;
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| `VendorNumber` | VARCHAR(20) | Primary key — vendor identifier used as FK in 4 gold fact tables (FactPSW, FactReceipts, FactOnTime, FactProduction); source from `PowerBI_SupplyChain.VendorMaster` |
| `VendorName` | VARCHAR(200) | Vendor legal name or trading name; consolidated from `PowerBI_SupplyChain.VendorMaster`, `Wholesale_Purchasing_AFI.VENNAM`, and `Wholesale_ProductSourcing_AFI.vendor` lookups for PSW/sourcing models |
| `VendorOffice` | VARCHAR(100) | Vendor office/division designation; used for vendor office-level grouping in supply planning and sourcing reports |
| `VendorOfficeLocation` | VARCHAR(100) | Geographic or functional location of the vendor office (e.g., region, facility code) |
| `VendorDesc` | VARCHAR(255) | `CONCAT(RTRIM([VendorNumber]), ' - ', RTRIM([VendorName]))` |
| `Country` | VARCHAR(50) | Country of origin or country of vendor's primary location; supports import/domestic segmentation |
| `LeadTime` | INT | Standard lead time in days; source lead time for supplier orders |
| `VendorActive` | VARCHAR(1) | Active indicator flag (Y/N or 1/0); filters active vs. inactive vendors in gold fact loads |

---

## 4. Dropped Columns

| Column | Data Type | Notes |
| --- | --- | --- |
| `AFILeadTime` | INT | WVF deprecated. Do need differentiated column |
| `WVFLeadTime` | INT | WVF deprecated. Do need differentiated column |

## 5. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-19 | Initial draft | Robert Font Perez |
