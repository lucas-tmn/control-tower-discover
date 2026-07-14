---
title: DimWarehouse table documentation
domain: Supply Chain Planning
warehouse: SupplyChain_Gold
schema: <schema>
table_name: DimWarehouse
last_updated: 2026-06-18
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

Central warehouse dimension for supply chain planning, consolidating warehouse attributes from `SupplyChain_DW.DimAFIWarehouses` (SQL master) unified with `PowerBI_SupplyChain.WarehouseMaster` (EDW) dataflow shadow (retired after parity check). This table resolves physical warehouse normalization rules across 3 legacy semantic models into a single governed `PlanningWarehouse` column that collapses virtual warehouses onto their physical DC fulfillment points and aligns Logility planning codes with physical warehouse identifiers.

---

## 2. Physical Table Definition

```sql
CREATE TABLE <warehouse>.<schema>.DimWarehouse (
    [WarehouseID] VARCHAR(10) NOT NULL,
    [WarehouseName] VARCHAR(100) NULL,
    [WarehouseLocation] VARCHAR(100) NULL,
    [WarehouseOrderGroup] VARCHAR(100) NULL,
    [IntransitWarehouse] VARCHAR(100) NULL,
    [ContainerDirectWarehouse] VARCHAR(100) NULL,
    [ControlledWarehouse] VARCHAR(100) NULL,
    [AFIWarehousesKey] VARCHAR(100) NULL,
    [SiteID] VARCHAR(50) NULL,
    [WarehouseGroup] VARCHAR(100) NULL,                  --ETL-computed
    [PlanningWarehouse] VARCHAR(10) NOT NULL,            --ETL-computed
    [SortBy] INT NOT NULL                                --ETL-computed
);
```

### Add the primary key

```sql
ALTER TABLE <schema>.DimWarehouse
ADD CONSTRAINT PK_DimWarehouse
PRIMARY KEY NONCLUSTERED ([WarehouseID])
NOT ENFORCED;
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| `WarehouseID` | VARCHAR(3) | Primary key — warehouse-level grain identifier used as FK in 8 gold fact tables; source values include raw warehouse codes (1, 15, 1A, 15A, ECA, C35, C, CNW, etc.) |
| `WarehouseName` | VARCHAR(100) | Descriptive warehouse name from master |
| `WarehouseLocation` | VARCHAR(100) | Physical or logical warehouse location grouping |
| `WarehouseOrderGroup` | VARCHAR(100) | Order grouping attribute for warehouse-level operational segmentation |
| `IntransitWarehouse` | VARCHAR(100) | Intransit/consolidation warehouse designation flag |
| `ContainerDirectWarehouse` | VARCHAR(100) | Container-direct receiving warehouse flag; supports direct-to-warehouse container shipments |
| `ControlledWarehouse` | VARCHAR(100) | Controlled warehouse designation; governed inventory model indicator |
| `AFIWarehousesKey` | VARCHAR(100) | Alternative key or reference code from source `DimAFIWarehouses` table |
| `SiteID` | VARCHAR(3) | Site/location ID used in supply chain systems |
| `WarehouseGroup` | VARCHAR(4) | ETL-computed warehouse group assignment mapping each warehouse code to its operational grouping (AFI, ASH, C.DIR, PROD, CXD, SDS). Enables warehouse-level aggregation and slicing in reports. |
| `PlanningWarehouse` | VARCHAR(6) | ETL-computed via warehouse facility mapping logic. Standardized planning warehouse code mapped to facility codes (e.g., 1→1-RKD, 15→15-LEE, ECA→ECR-ECR). Collapses virtual warehouses (A-suffixed variants like 1A, 15A) onto their physical facility codes. |
| `SortBy` | INT | ETL-computed display sort order for warehouse sequencing in reports. Derived from Power BI dataflow WarehouseMaster logic; maps each warehouse code to a sort sequence (1–51). |

### Exclude Inactive Warehouses from Gold Table

-Help maintain a clear experience using warehouse slicers. Hide locations that will never be used.

```sql
WHERE [WarehouseID] NOT IN ('', '10','109','14','18','2','21','213','215','232','242','50','52','55','6','60','7','8','9','N/A','P','R','W') 
```

---

## 4. ETL Computed Column Details

### PlanningWarehouse

**Purpose:** Single canonical warehouse facility mapping column replacing three divergent per-model calculated columns (`Physical WH`, `WH Site`, `WHSE`) and enabling the collapse of 40+ hardcoded warehouse-slice measures into one. Maps each warehouse code (including virtual A-suffixed variants) to its facility code (e.g., 1→1-RKD, ECA→ECR-ECR).

**Expression:** Warehouse facility mapping logic: Location-to-description mapping: Defined in [Source Data & ETL Logic](#5-source-data--etl-logic)

**Inputs:** `WarehouseID`

**Output values:** VARCHAR(10) — normalized planning warehouse identifier

**Reference:** Phase 3 § Silver Layer Design → warehouse-normalization pattern; all mapped warehouses are confirmed in use across GF Act+Fcst (Physical WH), Safety Stock Analysis (WH Site), and Weekly Trend Analysis (WHSE).

---

### WarehouseGroup

**Purpose:** Warehouse operational group assignment enabling warehouse-level aggregation and reporting segmentation across AFI, Ashton, Container Direct, Production, Colton Crossdock, and Supplier Direct Ship groupings.

**Expression:** Warehouse group mapping logic: Location-to-description mapping: Defined in [Source Data & ETL Logic](#5-source-data--etl-logic)

**Inputs:** `WarehouseCode`

**Output values:** VARCHAR(10) — warehouse group code

- `AFI` - Core AFI warehouses
- `ASH` - Ashton warehouse 335 and C35
- `C.DIR` - All container direct warehouses grouped (C, CNW, AFI, IOR)
- `PROD` - Production only, non-invoicing warehouses
- `CXD` - cross dock only warehouses
- `SDS` - Supplier Direct Ship - warehouse 55
- `NULL` for unmapped codes

---

### SortBy

**Purpose:** Display sort order for warehouse sequencing in reports. Derived from Power BI dataflow WarehouseMaster logic; ensures consistent warehouse ordering across all reporting views. No NULLs permitted; unmapped warehouse codes receive distinct sequential assignments (52+) via lookup table.

**Expression:** SortBy mapping logic: Location-to-description mapping: Defined in [Source Data & ETL Logic](#5-source-data--etl-logic)

**Inputs:** `WarehouseCode` (plus UnmappedWarehouseCodes lookup table)

**Output values:** INT — sort sequence (1–51 for known codes, 52+ for unmapped, 9999 as fail-safe)

**Reference:** Power BI WarehouseMaster dataflow logic + error handling for data quality; ensures no NULLs and distinct ordering across all warehouse codes.

---

## 5. Source Data & ETL Logic

This section documents the query from bronze/silver-layer used to populate `DimWarehouse`.

**Source tables:**

- `[Enterprise_Lakehouse].[SupplyChain_DW].[DimAFIWarehouses]` (S) — warehouse master data; provides warehouse code, location, order group, and warehouse attributes
- `[Enterprise_Lakehouse].[Wholesale_Codis_AFI].[AshleyWarehouseMaster]` (M) — warehouse site mapping; provides Site ID for warehouse code lookup
- `UnmappedWarehouseCodes` — CTE dynamic lookup table for sort-order assignment of new/unmapped warehouse codes (created via Prerequisite step below)

### ETL Query

Clean script with no external dependencies. The UnmappedWarehouseCodes logic is computed inline as a CTE, enabling safe execution from stored procedures.

```sql
WITH UnmappedWarehouseCodes AS ( -- Use CTE to avoid SortBY errors
    SELECT DISTINCT RTRIM([Warehouse Code]) AS WarehouseCode,
           ROW_NUMBER() OVER (ORDER BY RTRIM([Warehouse Code])) + 51 AS SortBy
    FROM [Enterprise_Lakehouse].[SupplyChain_DW].[DimAFIWarehouses]
    WHERE RTRIM([Warehouse Code]) NOT IN ('1','15','16','17','19','28','42','5','70','ECR','335','C35','C','C99','CNW','12','101','151','20','201','3','60','1A','15A','17A','19A','28A','42A','5A','ECA','55','213','215','242','49','50','52','10','109','14','18','2','21','232','6','7','8','9','P','R','W')
)
SELECT RTRIM(S.[Warehouse Code]) AS [WarehouseID]
      ,CONCAT(RTRIM(S.[Warehouse Code]),' - ', RTRIM(S.[Warehouse Location])) AS [WarehouseName]
      ,S.[Warehouse Location] AS [WarehouseLocation]
      ,S.[Warehouse Order Group] AS [WarehouseOrderGroup]
      ,S.[Intransit Warehouse] AS [IntransitWarehouse]
      ,S.[Container Direct Warehouse] AS [ContainerDirectWarehouse]
      ,S.[Controlled Warehouse] AS [ControlledWarehouse]
      ,S.[AFIWarehousesKey]
      ,RTRIM([M].[wmaSiteId]) AS [SiteID]
      ,CASE RTRIM(S.[Warehouse Code])
           WHEN '1' THEN 'AFI'
           WHEN '15' THEN 'AFI'
           WHEN '16' THEN 'AFI'
           WHEN '17' THEN 'AFI'
           WHEN '28' THEN 'AFI'
           WHEN '42' THEN 'AFI'
           WHEN '5' THEN 'AFI'
           WHEN '70' THEN 'AFI'
           WHEN 'ECR' THEN 'AFI'
           WHEN '335' THEN 'ASH'
           WHEN 'C' THEN 'C.DIR'
           WHEN 'CNW' THEN 'C.DIR'
           WHEN 'C35' THEN 'C.DIR'
           WHEN 'AF' THEN 'C.DIR'
           WHEN 'C99' THEN 'C.DIR'
           WHEN 'IOR' THEN 'C.DIR'
           WHEN '12' THEN 'PROD'
           WHEN '101' THEN 'PROD'
           WHEN '151' THEN 'PROD'
           WHEN '19' THEN 'PROD'
           WHEN '201' THEN 'PROD'
           WHEN '20' THEN 'PROD'
           WHEN '3' THEN 'PROD'
           WHEN '49' THEN 'CXD'
           WHEN '55' THEN 'SDS'
           WHEN '1A' THEN 'AFI'
           WHEN '15A' THEN 'AFI'
           WHEN '17A' THEN 'AFI'
           WHEN '28A' THEN 'AFI'
           WHEN '42A' THEN 'AFI'
           WHEN '5A' THEN 'AFI'
           WHEN 'ECA' THEN 'AFI'
           WHEN '19A' THEN 'AFI'
           ELSE NULL
      END AS [WarehouseGroup]
      ,CASE RTRIM(S.[Warehouse Code])
           WHEN '1' THEN '1-RKD'      -- Arcadia
           WHEN '15' THEN '15-LEE'    -- Leesport
           WHEN '16' THEN '16-STV'    -- Statesville
           WHEN '17' THEN '17-ADV'    -- Advance
           WHEN '28' THEN '28-MES'    -- Mesquite
           WHEN '42' THEN '42-SPW'    -- Spanaway
           WHEN '5' THEN '5-RED'      -- Redlands
           WHEN '70' THEN '70-ETN'    -- Etna
           WHEN 'ECR' THEN 'ECR-ECR'  -- Ecru
           WHEN '335' THEN '335-ASH'  -- Ashton
           WHEN 'C' THEN 'C-ENT'      -- Container Direct Enterprise Contract
           WHEN 'CNW' THEN 'CNW-CUS'  -- Container Direct Customer Contract
           WHEN 'C35' THEN 'C35-ASH'  -- Container Direct through Ashton
           WHEN 'AF' THEN 'AF-CND'    -- Container Direct AF
           WHEN 'C99' THEN 'C99-CND'  -- Container Direct 99
           WHEN 'IOR' THEN 'IOR-CND'  -- Container Direct Importer of Record
           WHEN '12' THEN '12-RIP'    -- Ripley
           WHEN '101' THEN '101-CHP'  -- Chippewa Falls
           WHEN '151' THEN '151-POT'  -- Pottsville
           WHEN '19' THEN '19-SLT'    -- Saltillo
           WHEN '201' THEN '201-VRM'  -- Verona Mattress
           WHEN '20' THEN '20-VRF'    -- Verona Foam
           WHEN '3' THEN '3-WHT'      -- Whitehall
           WHEN '49' THEN '49-COL'    -- Colton crossdox
           WHEN '55' THEN '55-SDS'    -- Supplier Direct Ship
           WHEN '1A' THEN '1-RKD'     -- Arcadia (Virtual Warehouse)
           WHEN '15A' THEN '15-LEE'   -- Leesport (Virtual Warehouse)
           WHEN '17A' THEN '17-ADV'   -- Advance (Virtual Warehouse)
           WHEN '28A' THEN '28-MES'   -- Mesquite (Virtual Warehouse)
           WHEN '42A' THEN '42-SPW'   -- Spanaway (Virtual Warehouse)
           WHEN '5A' THEN '5-RED'     -- Redlands (Virtual Warehouse)
           WHEN 'ECA' THEN 'ECR-ECR'  -- Ecru (Virtual Warehouse)
           WHEN '19A' THEN '19-SLT'   -- Saltillo (Virtual Warehouse)
           ELSE S.[Warehouse Code]
      END AS [PlanningWarehouse]
      ,CASE RTRIM(S.[Warehouse Code])
           WHEN '1' THEN 1
           WHEN '15' THEN 2
           WHEN '16' THEN 3
           WHEN '17' THEN 4
           WHEN '19' THEN 5
           WHEN '28' THEN 6
           WHEN '42' THEN 7
           WHEN '5' THEN 8
           WHEN '70' THEN 9
           WHEN 'ECR' THEN 10
           WHEN '335' THEN 11
           WHEN 'C35' THEN 12
           WHEN 'C' THEN 13
           WHEN 'C99' THEN 14
           WHEN 'CNW' THEN 15
           WHEN '12' THEN 16
           WHEN '101' THEN 17
           WHEN '151' THEN 18
           WHEN '20' THEN 19
           WHEN '201' THEN 20
           WHEN '3' THEN 21
           WHEN '60' THEN 22
           WHEN '1A' THEN 23
           WHEN '15A' THEN 24
           WHEN '17A' THEN 25
           WHEN '19A' THEN 26
           WHEN '28A' THEN 27
           WHEN '42A' THEN 28
           WHEN '5A' THEN 29
           WHEN 'ECA' THEN 30
           WHEN '55' THEN 31
           WHEN '213' THEN 32
           WHEN '215' THEN 33
           WHEN '242' THEN 34
           WHEN '49' THEN 35
           WHEN '50' THEN 36
           WHEN '52' THEN 37
           WHEN '10' THEN 38
           WHEN '109' THEN 39
           WHEN '14' THEN 40
           WHEN '18' THEN 41
           WHEN '2' THEN 42
           WHEN '21' THEN 43
           WHEN '232' THEN 44
           WHEN '6' THEN 45
           WHEN '7' THEN 46
           WHEN '8' THEN 47
           WHEN '9' THEN 48
           WHEN 'P' THEN 49
           WHEN 'R' THEN 50
           WHEN 'W' THEN 51
           ELSE COALESCE(U.SortBy, 9999)
      END AS [SortBy]
FROM [Enterprise_Lakehouse].[SupplyChain_DW].[DimAFIWarehouses] AS S
LEFT JOIN [Enterprise_Lakehouse].[Wholesale_Codis_AFI].[AshleyWarehouseMaster] AS M
      ON S.[Warehouse Code] = M.[wmaWarehouse]
LEFT JOIN UnmappedWarehouseCodes AS U
      ON RTRIM(S.[Warehouse Code]) = U.WarehouseCode
WHERE S.[Warehouse Code] NOT IN ('', '10','109','14','18','2','21','213','215','232','242','50','52','55','6','60','7','8','9','N/A','P','R','W')
  Order BY [SortBy] ASC;
```

**Grain:** Distinct [WarehouseID] with computed [WarehouseGroup], [SortBy], and [PlanningWarehouse].

---

## 6. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-18 | Initial draft | Robert Font Perez |
