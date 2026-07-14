---
type: Dataset
title: Warehouse Master
description: Central warehouse master dimensions.
tags: [warehouse, master-data, planning, logistics, dimension]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimWarehouse]"
source_system: ERP
refresh_cadence: daily
data_source: fabric
status: draft
---

## Purpose

Central warehouse dimension for supply chain planning.

---

## Grain

Each row represents a unique active **warehouse** (`WarehouseID`). Source values include physical codes (e.g., `1`, `15`, `ECR`) and virtual A-suffixed variants (e.g., `1A`, `15A`, `ECA`).

---

## Schema

### Identity

| Column | Type | Meaning |
| --- | --- | --- |
| `WarehouseID` | VARCHAR(10) | Primary key — warehouse-level grain identifier used as FK in gold fact tables; raw warehouse codes from source system |
| `WarehouseName` | VARCHAR(100) | ETL-computed: `WarehouseID + ' - ' + WarehouseLocation`; convenience label for visuals and slicers |
| `WarehouseLocation` | VARCHAR(100) | Physical or logical warehouse location description from master |

### Attributes

| Column | Type | Meaning |
| --- | --- | --- |
| `WarehouseOrderGroup` | VARCHAR(100) | Order grouping attribute for warehouse-level operational segmentation |
| `IntransitWarehouse` | VARCHAR(100) | Intransit or consolidation warehouse designation |
| `ContainerDirectWarehouse` | VARCHAR(100) | Container-direct receiving designation; supports direct-to-warehouse container shipments |
| `ControlledWarehouse` | VARCHAR(100) | Controlled warehouse designation; governed inventory model indicator |
| `AFIWarehousesKey` | VARCHAR(100) | Alternative key from source `DimAFIWarehouses` table |
| `SiteID` | VARCHAR(50) | Site or location ID from `AshleyWarehouseMaster`; used in supply chain systems |

### ETL-Computed

| Column | Type | Meaning |
| --- | --- | --- |
| `WarehouseGroup` | VARCHAR(10) | Operational group assignment — `AFI`, `ASH`, `C.DIR`, `PROD`, `CXD`, or `SDS`; NULL for unmapped codes. Enables warehouse-level aggregation in reports. See [Warehouse](/entities/warehouse.md) for group definitions and member codes. |
| `PlanningWarehouse` | VARCHAR(10) | Preferred attribute to be displayed in reporting. Shorthand for `<ID>-<Name>` (e.g., `1-RKD`, `15-LEE`, `ECR-ECR`). Collapses virtual A-suffixed codes onto their physical facility code. See [Warehouse](/entities/warehouse.md) for full mapping. |
| `SortBy` | INT | Display sort order for consistent warehouse sequencing across all reporting views; no NULLs — unmapped codes receive sequential values above 51 |

---

## Related

- [Warehouse](/entities/warehouse.md) — Business definition, warehouse group classification, and PlanningWarehouse facility mapping
