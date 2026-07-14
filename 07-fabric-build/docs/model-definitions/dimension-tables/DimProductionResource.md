---
title: DimProductionResource table documentation
domain: Supply Chain Planning
fabric_warehouse_name: SupplyChain_Gold
schema: <schema>
table_name: DimProductionResource
last_updated: 2026-06-19
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

Production resource dimension consolidating distinct ResourceID × LocationID pairs from `[Enterprise_Lakehouse].[DemandPlanning_AFI].[ProductionCapacity]`, which maps production resources (by vendor or domestic warehouse ) to manufacturing facilities across Ashley's operations and third party suppliers (vendors). Each row represents a unique resource-location pair. Enriched with `LocationDesc` (standardized facility name derived from warehouse code mapping) to provide consistent facility naming for capacity and demand-supply reports. Joined with vendor and warehouse master data to ensure location identifiers are mapped to current facility names.

---

## 2. Physical Table Definition

```sql
CREATE TABLE <warehouse>.<schema>.DimProductionResource (
    [ResourceID] VARCHAR(50) NOT NULL,
    [LocationID] VARCHAR(10) NOT NULL,
    [LocationDesc] VARCHAR(50) NOT NULL,         -- ETL-computed
    [ResourceGroup] VARCHAR(20) NOT NULL         -- ETL-computed
);
```

### Add the primary key

```sql
ALTER TABLE <schema>.DimProductionResource
ADD CONSTRAINT PK_DimProductionResource
PRIMARY KEY NONCLUSTERED ([ResourceID])
NOT ENFORCED;
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| `ResourceID` | VARCHAR(10) | Primary key component — production resource identifier (machine, line, or work center code) from `[ProductionCapacity]` source. Used as FK in FactProduction and FactSupplyPlan. |
| `LocationID` | VARCHAR(10) | Primary key component — production facility code (warehouse or vendor code) from `[ProductionCapacity]` source. Combined with ResourceID to form the grain. |
| `LocationDesc` | VARCHAR(50) | ETL-computed standardized facility name derived from LocationID mapping. Maps warehouse codes (1, 15, 17, etc.) to location descriptions (1-RKD for Arcadia, 15-LEE for Leesport, etc.). Falls back to `LocationID-VNAME` pattern for unmapped or vendor-supplied locations. |
| `ResourceGroup` | VARCHAR(20) | ETL-computed resource facility classification — DOM MFG (domestic manufacturing), WNK/MIL (Wanek/Millennium), or VENDOR (supplier-provided resources). Enables resource-level aggregation for capacity constraint reporting. |

---

## 4. ETL Computed Column Details

### LocationDesc

**Purpose:** Standardized facility name providing human-readable location labels for capacity and demand reporting. Maps warehouse/facility codes to facility identifiers using a hardcoded mapping for AFI Locations. ELse, use the vendor name from vendor master tables.

**Expression:** Location-to-description mapping: Defined in [Source Data & ETL Logic](#5-source-data--etl-logic)

**Inputs:** `[LocationID]` (from `[ProductionCapacity]`), joined with `[VENNAM].[VNAME]` vendor name for fallback.

**Output values:** VARCHAR(50) — facility identifier (e.g., 1-RKD, 15-LEE, or LocationID-VendorName for unmapped locations)

**Notes:** The ELSE clause concatenates unmapped LocationIDs with vendor names from the `[VENNAM]` table. This supports locations that may be added in the future without requiring table re-definition.

### ResourceGroup

**Purpose:** Resource facility classification enabling product-sourcing-level aggregation for capacity and demand reporting. Distinguishes between Ashley's domestic manufacturing facilities (DOM MFG), Wanek/Millennium strategic supplier locations (WNK/MIL), and other vendor-supplied resources (VENDOR).

**Expression:** Facility-type classification: Defined in [Source Data & ETL Logic](#5-source-data--etl-logic)

**Inputs:** `[LocationID]` and `[ResourceID]` (from `[ProductionCapacity]`)

**Output values:** VARCHAR(20) — facility group (DOM MFG, WNK/MIL, or VENDOR)

**Notes:** Classification is location-first (domestic locations → DOM MFG); if not a domestic location but ResourceID matches Wanek/Millennium codes → WNK/MIL; otherwise → VENDOR. This enables filtering and aggregation by facility sourcing strategy.

---

## 5. Source Data & ETL Logic

This section documents the bronze-layer query used to populate `DimProductionResource`.

**Source tables:**

- `[Enterprise_Lakehouse].[DemandPlanning_AFI].[ProductionCapacity]` ([PC]) — base resource-location pairs
- `[Enterprise_Lakehouse].[Wholesale_Purchasing_AFI].[VENNAM]` ([VND]) — vendor master data for fallback location naming

**ETL Query:**

````sql
SELECT DISTINCT
    [PC].[LocationID],
    [PC].[ResourceID],
    CASE RTRIM([PC].[LocationID])
        WHEN '1'   THEN '1-RKD'      -- Arcadia
        WHEN '15'  THEN '15-LEE'     -- Leesport
        WHEN '17'  THEN '17-ADV'     -- Advance
        WHEN '28'  THEN '28-MES'     -- Mesquite
        WHEN '42'  THEN '42-SPW'     -- Spanaway
        WHEN '5'   THEN '5-RED'      -- Redlands
        WHEN 'ECR' THEN 'ECR-ECR'    -- Ecru
        WHEN '335' THEN '335-ASH'    -- Ashton
        WHEN '12'  THEN '12-RIP'     -- Ripley
        WHEN '101' THEN '101-CHP'    -- Chippewa Falls
        WHEN '151' THEN '151-POT'    -- Pottsville
        WHEN '19'  THEN '19-SLT'     -- Saltillo
        WHEN '201' THEN '201-VRM'    -- Verona Mattress
        WHEN '20'  THEN '20-VRF'     -- Verona Foam
        WHEN '3'   THEN '3-WHT'      -- Whitehall
        WHEN '99999' THEN '99999-TEST'
        ELSE
            RTRIM([PC].[LocationID]) + '-' + RTRIM([VND].[VNAME])
    END AS [LocationDesc],
    CASE
        WHEN RTRIM([PC].[LocationID]) IN (
            '1','15','17','28','42','5','ECR','335',
            '12','101','151','19','201','20','3'
        ) THEN 'DOM MFG'

        WHEN [PC].[ResourceID] IN (
            '900515','900639','600039','659852','624556','641068'
        ) THEN 'WNK/MIL'

        ELSE 'VENDOR'
    END AS [ResourceGroup]

FROM [Enterprise_Lakehouse].[DemandPlanning_AFI].[ProductionCapacity] AS [PC]
LEFT JOIN [Enterprise_Lakehouse].[Wholesale_Purchasing_AFI].[VENNAM] AS [VND]
    ON [PC].[LocationID] = [VND].[VNDNR]
````

**Grain:** Distinct ([ResourceID], [LocationID]) pairs with computed [LocationDesc] and [ResourceGroup].

---

## 6. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-19 | Initial draft | Robert Font Perez |
