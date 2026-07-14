---
type: Dataset
title: Current Forecast Snapshot Daily
description: Daily snapshot of the monthly forecast extracted from the SupplyPlanning databases inside Logility. 
tags: [forecast, current-forecast, snapshot, monthly-grain, logility, supply-planning]
timestamp: 2026-07-06
resource: "[SupplyChain_Enh].[CurFcstSnapshotDaily]"
source_system: Logility
refresh_cadence: daily
data_source: ashley_edw
status: draft
---

## Purpose

Daily current forecast snapshot table used as an interim source while the gold-level [Current Forecast](/datasets/tables/FactCurrentForecast.md) table is not deployed.

This table stores the current forecast at the **item x warehouse x fiscal month** grain. It keeps monthly resultant forecast, promotional lift, and total forecast quantities from the latest available snapshot date.

Use [Weekly Current Forecast](/datasets/queries/weekly_current_forecast.md) when analysis needs the weekly item-warehouse forecast shape documented by [Current Forecast](/datasets/tables/FactCurrentForecast.md).

---

## Grain

Each row represents one **item x warehouse x fiscal month** combination for the latest available snapshot date.

`ItemSKU` x `WarehouseID` x `FiscalMonthYear` should be unique for a single `SnapshotDate`.

---

## Schema

All forecast quantities are in **units**.

### Grain / Keys

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemSKU` | VARCHAR(20) | FK to [Product Master](/datasets/tables/DimProduct.md) (`DimProduct[ItemSKU]`) |
| `WarehouseID` | VARCHAR(10) | FK to [Warehouse Master](/datasets/tables/DimWarehouse.md) (`DimWarehouse[WarehouseID]`) |
| `FiscalMonthLastDate` | DATE | Last date of the fiscal month represented by the row |
| `FiscalMonthYear` | VARCHAR | Fiscal month-year period identifier used to align monthly forecast values to the fiscal calendar |

### Forecast Quantities

| Column | Type | Meaning |
| --- | --- | --- |
| `ResultantForecast` | INT | Final monthly forecast quantity after planner overrides have been applied on top of the statistical model; see [Resultant Forecast](/glossary/resultant_forecast.md) |
| `PromoLift` | INT | Monthly promotional lift quantity; incremental demand from planned promotions; see [Promo Lift](/glossary/promo_lift.md) |
| `TotalForecast` | INT | Combined monthly demand signal: `ResultantForecast + PromoLift` |

### Metadata

| Column | Type | Meaning |
| --- | --- | --- |
| `SnapshotDate` | DATE | Date the forecast snapshot was captured; the base query filters to the latest available snapshot date |

---

## Snapshot Strategy

The base query filters `CurFcstSnapshotDaily` to the maximum available `SnapshotDate`, so the documented extract returns only the latest current forecast snapshot.

Historical daily snapshots may exist in the source table, but the default current-forecast usage should select the latest snapshot unless the analysis explicitly requires forecast drift or plan-drop history.

---

## Monthly vs. Weekly Forecast

`CurFcstSnapshotDaily` is monthly. It does not contain one row per fiscal week.

The weekly current forecast shape is produced by [Weekly Current Forecast](/datasets/queries/weekly_current_forecast.md), which maps monthly forecast periods to fiscal week-ending dates and divides monthly quantities by the number of fiscal weeks in each month. This matches the normalization caveat documented in [Current Forecast](/datasets/tables/FactCurrentForecast.md).

---

## Base Query

This query returns the latest available current forecast snapshot from `CurFcstSnapshotDaily`.

```sql
SELECT RTRIM([CFS].[ItemSku]  ) AS [ItemSKU]
      ,RTRIM([CFS].[Warehouse]) AS [WarehouseID]
      ,[CFS].[FiscalMonthLastDate]
      ,[CFS].[FiscalMonthYear]
      ,[CFS].[ResultantForecast]
      ,[CFS].[PromoLift]
      ,[CFS].[TotalForecast]
      ,CONVERT(DATE,[CFS].[SnapshotDate]) AS [SnapshotDate]
  FROM [SupplyChain_Enh].[CurFcstSnapshotDaily] AS CFS
  WHERE CONVERT(DATE, [CFS].[SnapshotDate]) = (SELECT CONVERT(DATE, MAX([SnapshotDate])) FROM [SupplyChain_Enh].[CurFcstSnapshotDaily])
```

---

## Related

- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Weekly Current Forecast](/datasets/queries/weekly_current_forecast.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Resultant Forecast](/glossary/resultant_forecast.md)
- [Promo Lift](/glossary/promo_lift.md)
