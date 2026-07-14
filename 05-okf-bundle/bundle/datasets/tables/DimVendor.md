---
type: Dataset
title: Vendor Master
description: Central vendor master dimensions.
tags: [vendor, master-data, procurement, supply-planning, dimension]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimVendor]"
source_system: ERP
refresh_cadence: daily
data_source: fabric
status: draft
---

## Purpose

Central vendor dimension for supply chain planning. Provides a single source of truth for vendor attributes — lead times, location, country of origin, and active status — used across procurement, supply planning, and on-time performance reporting.

Vendor-level aggregates such as open purchase orders and vendor ranking are not stored in this table; they are computed at report time in the measure layer.

---

## Grain

Each row represents a unique **vendor** (`VendorNumber`). Both active and inactive vendors are included; use the `VendorActive` flag to filter to active vendors only when appropriate for the analysis.

---

## Schema

### Identity

| Column | Type | Meaning |
| --- | --- | --- |
| `VendorNumber` | VARCHAR(8) | Primary key — vendor identifier; used as FK in `FactPSW`, `FactReceipts`, `FactOnTime`, and `FactProduction` |
| `VendorName` | VARCHAR(40) | Vendor legal or trading name; consolidated from `VendorMaster`, `VENNAM`, and `vendor` source lookups |
| `VendorDesc` | VARCHAR(60) | ETL-computed: `CONCAT(RTRIM(VendorNumber), ' - ', RTRIM(VendorName))`; convenience label for visuals and slicers |

### Attributes

| Column | Type | Meaning |
| --- | --- | --- |
| `VendorOffice` | VARCHAR(20) | Office or division designation; used for vendor office-level grouping in supply planning and sourcing reports |
| `VendorOfficeLocation` | VARCHAR(40) | Geographic or functional location of the vendor office (e.g., region, facility code) |
| `Country` | VARCHAR(50) | Country of origin or country of vendor's primary location; supports import vs. domestic segmentation |
| `LeadTime` | INT | Standard lead time in days; sourced from vendor master for use in supply planning calculations |
| `VendorActive` | CHAR(1) | Active status flag (`Y`/`N`); filters active vs. inactive vendors in reporting and gold fact loads |

---

## Related

- [Vendor](/entities/vendor.md) — Business definition, active status, and lead time context for the Vendor entity
