---
type: Query
title: Warehouse Master Query
description: EDW SQL query that produces the warehouse master.
tags: [warehouse, master-data, planning, logistics, dimension, query]
timestamp: 2026-07-06
resource: "[SupplyChain_DW].[DimAFIWarehouses]"
source_system: ERP
refresh_cadence: daily
data_source: ashley_edw
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

---

## Base Query

Use this query to produce the Warehouse Master shape while the gold `DimWarehouse` table is unavailable.

```sql
WITH UnmappedWarehouseCodes AS ( -- Use CTE to avoid SortBY errors
    SELECT DISTINCT RTRIM([Warehouse Code]) AS WarehouseCode,
           ROW_NUMBER() OVER (ORDER BY RTRIM([Warehouse Code])) + 55 AS SortBy
    FROM [SupplyChain_DW].[DimAFIWarehouses]
    WHERE RTRIM([Warehouse Code]) NOT IN ('1','15','16','17','19','28','42','5','70','ECR','335','C35','C','C99','CNW','AF','IOR','12','101','151','20','201','3','60','1A','15A','17A','19A','28A','42A','5A','ECA','55','213','215','242','49','50','52','10','109','14','18','2','21','232','6','7','8','9','P','R','W','','N/A')
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
           WHEN 'AF' THEN 16
           WHEN 'IOR' THEN 17
           WHEN '12' THEN 18
           WHEN '101' THEN 19
           WHEN '151' THEN 20
           WHEN '20' THEN 21
           WHEN '201' THEN 22
           WHEN '3' THEN 23
           WHEN '60' THEN 24
           WHEN '1A' THEN 25
           WHEN '15A' THEN 26
           WHEN '17A' THEN 27
           WHEN '19A' THEN 28
           WHEN '28A' THEN 29
           WHEN '42A' THEN 30
           WHEN '5A' THEN 31
           WHEN 'ECA' THEN 32
           WHEN '55' THEN 33
           WHEN '213' THEN 34
           WHEN '215' THEN 35
           WHEN '242' THEN 36
           WHEN '49' THEN 37
           WHEN '50' THEN 38
           WHEN '52' THEN 39
           WHEN '10' THEN 40
           WHEN '109' THEN 41
           WHEN '14' THEN 42
           WHEN '18' THEN 43
           WHEN '2' THEN 44
           WHEN '21' THEN 45
           WHEN '232' THEN 46
           WHEN '6' THEN 47
           WHEN '7' THEN 48
           WHEN '8' THEN 49
           WHEN '9' THEN 50
           WHEN 'P' THEN 51
           WHEN 'R' THEN 52
           WHEN 'W' THEN 53
           WHEN '' THEN 54
           WHEN 'N/A' THEN 55
           ELSE COALESCE(U.SortBy, 9999)
      END AS [SortBy]
FROM [SupplyChain_DW].[DimAFIWarehouses] AS S
LEFT JOIN [Wholesale_Codis].[AshleyWarehouseMaster] AS M
      ON S.[Warehouse Code] = M.[wmaWarehouse]
LEFT JOIN UnmappedWarehouseCodes AS U
      ON RTRIM(S.[Warehouse Code]) = U.WarehouseCode
WHERE S.[Warehouse Code] NOT IN ('', '10','109','14','18','2','21','213','215','232','242','50','52','55','6','60','7','8','9','N/A','P','R','W')
  Order BY [SortBy] ASC;
```

