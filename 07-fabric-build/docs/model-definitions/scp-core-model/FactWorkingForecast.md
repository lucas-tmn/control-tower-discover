---
title: FactWorkingForecast table documentation
domain: Supply Chain Planning
fabric_warehouse_name: SupplyChain_Gold
table_name: FactWorkingForecast
schema: <schema>
last_updated: 2026-06-19
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

Latest snapshot of the nightly in-progress working forecast from the demand team. Provides current-state demand signal at the item-warehouse-customer level broken down by forecast type (Resultant, Promotional Lift, Total). Operational reports consume this table for daily demand planning and visibility.

-**Implementing as Weekly Forecast value in anticipation of transition in Q3**

---

## 2. Physical Table Definition

```sql
CREATE TABLE <schema>.FactWorkingForecast (
    [CustomerGroup] VARCHAR(50) NOT NULL,      -- Foreign key to DimCustomer; AFICONS if unknown
    [ItemSKU] VARCHAR(20) NOT NULL,            -- Foreign key to DimProduct
    [WarehouseID] VARCHAR(10) NOT NULL,        -- Foreign key to DimWarehouse
    [WeekEnding] DATE NOT NULL,                -- Fiscal week ending date; foreign key to DimDate
    [ResultantForecast] INT NOT NULL,          -- Model resultant forecast quantity (RSLF)
    [PromoLift] INT NOT NULL,                  -- Promotional lift quantity (PROL)
    [TotalForecast] INT NOT NULL,              -- Total forecast = ResultantForecast + PromoLift
    [SnapshotDate] DATE NOT NULL               -- Date when this forecast was generated; latest snapshot only
);
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| CustomerGroup | VARCHAR(50) | Demand planning customer group; NULL values normalized to 'AFICONS' by ETL. Foreign key to DimCustomer. |
| ItemSKU | VARCHAR(20) | Item SKU identifier. Foreign key to DimProduct. Source: `DFC.dfcItem` (RTRIM applied). |
| WarehouseID | VARCHAR(10) | Warehouse identifier. Foreign key to DimWarehouse. Source: `DFC.dfcWarehouse` (RTRIM applied). |
| WeekEnding | DATE | Fiscal week ending date. Joined from DimDate based on source `DFC.dfcFiscalMonth`. Foreign key to DimDate[FiscalWeekLastDate]. |
| ResultantForecast | INT | Model resultant forecast quantity weekly equivalent. Source: `DFC.dfcResultantForecast / WeeksinMonth` (rounded to INT). |
| PromoLift | INT | Promotional lift quantity weekly equivalent. Source: `DFC.dfcPromotionalLift / WeeksinMonth` (rounded to INT). |
| TotalForecast | INT | Total forecast quantity (ResultantForecast + PromoLift) weekly equivalent. Computed during load. |
| SnapshotDate | DATE | Snapshot creation date. ETL filters to latest snapshot only: `WHERE SnapshotDate = MAX(SnapshotDate)`. Source: `CONVERT(DATE, DFC.dfcSnapshot)`. |

---

## 4. Semantic Model Layer

- **Model Type** - Star Schema
- **Fact Table** - FactWorkingForecast

---

### Relationships

| From | To | Type | Direction |
| --- | --- | --- | --- |
| `FactWorkingForecast[ItemSKU]` | `DimProduct[ItemSKU]` | Many-to-One | Single |
| `FactWorkingForecast[WarehouseID]` | `DimWarehouse[WarehouseID]` | Many-to-One | Single |
| `FactWorkingForecast[CustomerGroup]` | `DimCustomer[AccountAndShipToNumber]` | Many-to-One | Single |
| `FactWorkingForecast[WeekEnding]` | `DimDate[TransactionDate]` | Many-to-One | Single |

---

## 5. Measures (TMDL)

### `displayFolder: Working Forecast`

#### Resultant Forecast Qty

```tmdl
	measure 'Resultant Forecast Qty' = CALCULATE(SUM(FactWorkingForecast[ResultantForecast]))
		formatString: #,0
		displayFolder: "Working Forecast"
		description: "Model resultant forecast quantity — the statistical demand model output."
```

#### Promo Lift Qty

```tmdl
	measure 'Promo Lift Qty' = CALCULATE(SUM(FactWorkingForecast[PromoLift]))
		formatString: #,0
		displayFolder: "Working Forecast"
		description: "Promotional lift quantity — incremental demand driven by planned promotions."
```

#### Total Forecast Qty

```tmdl
	measure 'Total Forecast Qty' = CALCULATE(SUM(FactWorkingForecast[TotalForecast]))
		formatString: #,0
		displayFolder: "Working Forecast"
		description: "Total working forecast quantity — resultant forecast plus promotional lift."
```

---

## 6. Source Data & ETL Logic

```sql
-- FactWorkingForecast — Latest Snapshot Only
-- Grain: ItemSKU × WarehouseID × CustomerGroup × WeekEnding × SnapshotDate
-- Loads only the most recent snapshot from the source for operational reporting.
-- Full snapshot history is retained in source EDW; Phase 5 specialized models expose it for trend analysis.
-- Define as weekly forecast by dividing by weeks in month in preparation for transition to weekly forecast

SELECT RTRIM([DFC].[dfcCustomerGroups]) AS [CustomerGroup]
      ,RTRIM([DFC].[dfcItem]          ) AS [ItemSKU]
      ,RTRIM([DFC].[dfcWarehouse]     ) AS [WarehouseID]
      ,[DD].[FiscalWeekLastDate] AS [WeekEnding]
      ,CAST(ROUND([DFC].[dfcResultantForecast]/[W].[WeeksinMonth],0) AS INT) AS [ResultantForecast]
      ,CAST(ROUND([DFC].[dfcPromotionalLift]/[W].[WeeksinMonth],0) AS INT) AS [PromoLift]
      ,CAST(ROUND(([DFC].[dfcResultantForecast] + [DFC].[dfcPromotionalLift])/[W].[WeeksinMonth],0) AS INT) AS [TotalForecast]
      ,CONVERT(DATE, [DFC].[dfcSnapshot]) AS [SnapshotDate]
  FROM [Enterprise_Lakehouse].[SupplyChain_Enh].[DemandForecastSnapshotDaily] AS DFC
  LEFT JOIN ( 
    SELECT DISTINCT [FiscalMonthYear]
          ,[FiscalWeekLastDate]
      FROM [Enterprise_Lakehouse].[MasterData_DW].[DimDate]
  ) AS DD 
    ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]
  LEFT JOIN ( 
    SELECT [FiscalMonthYear]
          ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [WeeksinMonth]
      FROM [Enterprise_Lakehouse].[MasterData_DW].[DimDate]
      GROUP BY [FiscalMonthYear]
  ) AS W
    ON [DFC].[dfcFiscalMonth] = [W].[FiscalMonthYear]
  WHERE [DFC].[dfcSnapshot] = (SELECT MAX([dfcSnapshot]) FROM [Enterprise_Lakehouse].[SupplyChain_Enh].[DemandForecastSnapshotDaily] )
    AND [DD].[FiscalWeekLastDate] IS NOT NULL  -- Fiscal Calendar ends at start of 2029
```

**ETL Notes:**

- **Data source:** `Enterprise_Lakehouse.SupplyChain_Enh.DemandForecastSnapshotDaily`
- **Refresh frequency:** Nightly (latest snapshot only loaded; full history retained in source)
- **Key transformation logic:** Normalizes monthly forecast values to weekly equivalent by dividing by the count of distinct fiscal weeks in the month. Coalesces NULL CustomerGroup to 'AFICONS'. Filters to latest snapshot only for operational reporting.

---

## 7. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-19 | Initial draft | Robert Font Perez |
