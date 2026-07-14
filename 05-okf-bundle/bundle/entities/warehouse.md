---
type: Entity
title: Warehouse
description: A physical or virtual warehouse location used in supply chain planning, classified by operational group and mapped to a canonical planning facility code.
tags: [warehouse, logistics, planning, master-data]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimWarehouse]"
status: draft
---

## Definition

A **Warehouse** is a physical distribution center or virtual inventory location used in supply chain planning. Warehouses are the fulfillment nodes for customer orders and the primary dimension for inventory planning and supply allocation reporting.

Virtual warehouse codes (A-suffixed, e.g., `1A`, `15A`, `ECA`) exist in the source system as distinct identifiers but represent the same physical facility as their base code counterpart. For planning purposes they are collapsed onto their physical facility via the `PlanningWarehouse` field in [Warehouse Master](/datasets/tables/DimWarehouse.md).

---

## Warehouse Types

- **Manufacturing and Distribution Warehouse** - physical warehouse locations that meet at least some of their supply through manufacturing. Supply will also come through transfers in from other warehouse sources or purchase orders from third party vendors. Invoices to either wholesale customers receiving full truckload (FTL) or less than truckload shipments (LTL), or direct to consumer "express" shipments through parcel services (unless otherwise noted).
- **Distribution Warehouse** - physical warehouse locations that meet their demand through external supply sources. Either through transfers in from manufacturing sites or purchase orders from third party vendors. Invoices to either wholesale customers receiving full truckload (FTL) or less than truckload shipments (LTL), or direct to consumer "express" shipments through parcel (fedEx) services.
- **Manufacturing Satellite Warehouse** - physical warehouse locations that only manufacturing and do not directly invoice to customers. They transfer out their production to our warehouses that have distribution as well.
- **Container Direct Warehouse** - This is a type of virtual warehouse used for the facilitation of the container direct program, where a customer's order is passed to and directly fulfilled by third party vendors. No inventory is ever taken into our possession. Note: this is a wholesale program, full ocean container loads to furniture dealers, and should not be confused with direct to consumer ecommerce by parcel service
- **Intransit Warehouse** - another type of virtual warehouse used to track inventory that is being transferred between warehouses. When a physical warehouse loads a transfer out to another warehouse, an inventory transaction debits the physical warehouse and credits the intransit warehouse assigned to the destination. When the transfer arrives at the destination, an inventory transaction debits the intransit warehouse and credits the physical warehouse that the load arrived at.
- **Virtual Warehouse** - An entity in our ERP system that is tied to a physical location. This was used as a way to allocate separate inventory for a specific customer that would purchase against the virtual warehouse. The program has been discontinued, although invoice and inventory history still have records from these locations

---

## Warehouse Details

### Manufacturing and Distribution Warehouses

#### 1 - Arcadia

- Located in Arcadia, Wisconsin
- Manufactures Domestic Casegoods and Stationary Upholstery pieces and distrbutes all other finished goods products
- Site ID: 001
- Intransit Warehouse: A
- Virtual Warehouse: 1A

#### 15 - Leesport

- Located in Leesport, Pennsylvania
- Manufactures Stationary Upholstery pieces and distrbutes all other finished goods products
- Site ID: 015
- Intransit Warehouse: L
- Virtual Warehouse: 15A

#### 17 - Advance

- Located in Advance, North Carolina
- Manufactures Stationary Upholstery and distrbutes all other finished goods products
- Site ID: 017
- Intransit Warehouse: N
- Virtual Warehouse: 17A

#### ECR - Ecru

- Located in Ecru, Mississippi
- Manufactures Stationary Upholstery and distrbutes all other finished goods products
- Site ID: 013
- Intransit Warehouse: E
- Virtual Warehouse: ECA

#### 19 - Saltillo

- Located in Saltillo, Mississippi
- Manufactures Hybrid Mattress. Primarily transfers out to other distribution warehouses, but can invoice its products directly to wholesale customers that buy full truckloads. Currently not set up for LTL or Express shipment capability due to it's limited finshed goods storage space.
- Site ID: 019
- Intransit Warehouse: S
- Virtual Warehouse: 19A

### Distribution Warehouses

#### 28 - Mesquite

- Located in Mequite, Texas
- Distributes all finished goods products
- Site ID: 028
- Intransit Warehouse: T
- Virtual Warehouse: 28A

#### 5 - Redlands

- Located in Redlands, California
- Distributes all finished goods products
- Site ID: 005
- Intransit Warehouse: B
- Virtual Warehouse: 5A

#### 335 - Ashton

- Located in Ho Chi Minh City, Vietnam
- Bonded warehouse program benefitting from certain import duties.
- Warehouses and distrbutes all products produced in Vietnam. Select items from other countries may also be opened at this location.
- Acts as a consolidation location for consolidating inventory from multiple vendors
- Primary service point for international customers in Asia, Australia, Africa, Europe
- Serves US customers who don't want to buy full containers direct from vendors
- Also consolidates and transfers to our USA based distribution warehouses where needed supply may not fill containers direct from vendors regularly
- Intransit Warehouse: G

#### 42 - Spanaway

- Located in Spanaway, Washington
- Distrbuted all finished goods products
- Discontinued invoicing in spring of 2025, although inventory records may still persist until full closure in spring 2026
- Site ID: 042
- Intransit Warehouse: F
- Virtual Warehouse: 42A

### Manufacturing Satellite Warehouses

#### 12 - Ripley

- Located in Ripley, Mississippi
- Manufactures Motion Upholstery and transfers out to distribution warehouses

#### 101 - Chippewa Falls

- Located in Chippewa Falls, Wisconsin
- Manufactures Stationary Upholstery and transfers out to warehouse 1 - Arcadia

#### 201 - Verona Plant 4

- Located in Verona, Mississippi
- Manufactures Foam Mattresses and transfers out to distribution warehouses

#### 20 - Verona Foam Plant

- Located in Verona, Mississippi
- Manufactures Foam to be used as a raw material in downstream Finished Good production.
  - Transfers foam next door to 201 - Verona for foam mattress production
  - Transfers processed foam to 19 - Saltillo to be used in the foam layers of hybrid mattress production
  - Transfers Foam Buns to ECR - Ecru to be used in the foam cushions for FG upholstery production

#### 3 - Whitehall

- Located in Whitehall, Wisconsin
- Manufactures fiber and webbing to be used as a raw material downstream upholstery production

#### 151 Pottsville

- Located in Pottsville, Pennsylvania
- Closed location. Used to manufacture stationairy upholstery and transfer out to warehouse 15 - Leesport

### Container Direct Warehouses

#### C - Container Direct

#### CNW - Container Direct

#### AF - Container Direct

#### IOR - Container Direct

#### C35 - Ashton Container Direct

#### C99 - Container Direct

### Cross Dock Warehouses

#### 49 - Colton XD

- Located in Redlands, California
- Used as a temporary virtual warehouse to support the cross docking of inbound containers. Example of use use may be when ocean carrier constraints prevent shipments to Central and Eastern USA warehouse locations, and we were only able to get a booking to the West Coast. Unloads the receipt from purchase order and directly loads back onto an outboud trailer, transfering out to the destination warehouse

---

## Warehouse Groups

Each warehouse is assigned to an operational group (`WarehouseGroup`) that governs how it aggregates in planning and reporting. The grouping is ETL-computed from `WarehouseID`.

| Group | Description | Warehouse Codes |
| --- | --- | --- |
| `AFI` | Core AFI distribution centers, including virtual A-suffix counterparts | 1, 15, 17, 28, 42, 5, ECR, 19A, 1A, 15A, 17A, 28A, 42A, 5A, ECA |
| `ASH` | Ashton distribution facility | 335 |
| `C.DIR` | Container Direct — all direct-import receiving variants | C, CNW, C35, AF, C99, IOR |
| `PROD` | Production-only, non-invoicing facilities | 12, 101, 151, 19, 201, 20, 3 |
| `CXD` | Cross-dock only | 49 |
| `SDS` | Supplier Direct Ship | 55 |
| NULL | Warehouse codes with no group assignment | All other codes |

Note: `19` (Saltillo) is classified as `PROD`; its virtual counterpart `19A` is classified as `AFI`. This distinction is intentional in the source ETL.

---

## Planning Warehouse

The `PlanningWarehouse` field provides a single canonical planning facility code per warehouse, replacing three divergent calculated columns (`Physical WH`, `WH Site`, `WHSE`) used across legacy reports. All warehouse-level filtering and aggregation in current reports should use `PlanningWarehouse`.

Key rules:

- Physical warehouse codes map directly to a facility code (e.g., `1 → 1-RKD`, `ECR → ECR-ECR`).
- Virtual A-suffixed codes collapse onto their physical facility code (e.g., `1A → 1-RKD`, `ECA → ECR-ECR`).
- Codes with no explicit mapping pass through as-is.

| `WarehouseID` | `PlanningWarehouse` | Facility Name |
| --- | --- | --- |
| 1, 1A | 1-RKD | Arcadia |
| 15, 15A | 15-LEE | Leesport |
| 17, 17A | 17-ADV | Advance |
| 19, 19A | 19-SLT | Saltillo |
| 28, 28A | 28-MES | Mesquite |
| 42, 42A | 42-SPW | Spanaway |
| 5, 5A | 5-RED | Redlands |
| ECR, ECA | ECR-ECR | Ecru |
| 335 | 335-ASH | Ashton |
| C | C-ENT | Container Direct Enterprise Contract |
| CNW | CNW-CUS | Container Direct Customer Contract |
| C35 | C35-ASH | Container Direct through Ashton |
| AF | AF-CND | Container Direct AF |
| C99 | C99-CND | Container Direct 99 |
| IOR | IOR-CND | Container Direct Importer of Record |
| 12 | 12-RIP | Ripley |
| 101 | 101-CHP | Chippewa Falls |
| 151 | 151-POT | Pottsville |
| 201 | 201-VRM | Verona Mattress |
| 20 | 20-VRF | Verona Foam |
| 3 | 3-WHT | Whitehall |
| 49 | 49-COL | Colton Crossdock |
| 55 | 55-SDS | Supplier Direct Ship |

---

## Related

- [Warehouse Master](/datasets/tables/DimWarehouse.md) — Source dataset for all warehouse attributes and ETL-computed fields
