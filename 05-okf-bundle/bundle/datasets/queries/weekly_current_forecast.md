---
type: Query
title: Weekly Current Forecast
description: Query the latest snapshot of the current forecast used in Supply Planning, transformed into a weekly value.
tags: [forecast, current-forecast, weekly-grain, logility, supply-planning, query]
timestamp: 2026-07-06
resource: "[Wholesale_DemandPlanning_AFI].[SupplyForecast]"
source_system: Logility
refresh_cadence: daily
data_source: ashley_edw
status: draft
---

## Purpose

Use this query to produce the [Current Forecast](/datasets/tables/FactCurrentForecast.md) weekly item-warehouse forecast shape while the gold-level `FactCurrentForecast` table is not deployed.

The source forecast quantities are monthly values from Logility SupplyForecast. The query expands each fiscal month to its fiscal week-ending dates through `DimDate_NonRetail`, then evenly distributes monthly forecast quantities across the number of fiscal weeks in the month.

---

## Output Grain

Each row represents one **item x warehouse x fiscal week-ending** combination for a forecast snapshot.

`ItemSKU` x `WarehouseID` x `WeekEnding` should be unique for a single `SnapshotDate`.

---

## Key Transformations

- Trims item and warehouse identifiers from `FCST_1_ID` and `FCST_2_ID`.
- Maps Logility fiscal month period `FCST_YR_PRD` to fiscal week-ending dates through `[Enterprise_DW].[DimDate_NonRetail]`.
- Counts distinct fiscal week-ending dates in each fiscal month to derive `WeeksinMonth`.
- Divides monthly `FCST_RSLT_QTY` and `PROMO_LIFT_QTY` by `WeeksinMonth`, rounds to whole units, and casts to integer.
- Filters out fiscal periods that do not resolve to a fiscal week-ending date.

---

## SQL

```sql
SELECT RTRIM([SFC].[FCST_1_ID]          ) AS [ItemSKU]
      ,RTRIM([SFC].[FCST_2_ID]    ) AS [WarehouseID]
      ,[DD].[FiscalWeekLastDate] AS [WeekEnding]
      ,CAST(ROUND([SFC].[FCST_RSLT_QTY]/[W].[WeeksinMonth],0) AS INT) AS [ResultantForecast]
      ,CAST(ROUND([SFC].[PROMO_LIFT_QTY]/[W].[WeeksinMonth],0) AS INT) AS [PromoLift]
      ,CAST(ROUND(([SFC].[FCST_RSLT_QTY] + [SFC].[PROMO_LIFT_QTY])/[W].[WeeksinMonth],0) AS INT) AS [TotalForecast]
      ,CONVERT(DATE, [SFC].[dtea]) AS [SnapshotDate]
  FROM [Wholesale_DemandPlanning_AFI].[SupplyForecast] AS SFC
  LEFT JOIN (
SELECT DISTINCT [FiscalMonthYear]
      ,[FiscalWeekLastDate]
  FROM [Enterprise_DW].[DimDate_NonRetail]
  ) AS DD
  ON [SFC].[FCST_YR_PRD] = [DD].[FiscalMonthYear]
  	LEFT JOIN (
SELECT [FiscalMonthYear]
      ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [WeeksinMonth]
  FROM [Enterprise_DW].[DimDate_NonRetail]
  GROUP BY [FiscalMonthYear]
	) AS W
	ON [SFC].[FCST_YR_PRD] = [W].[FiscalMonthYear]
  WHERE [DD].[FiscalWeekLastDate] IS NOT NULL
```

---

## Related

- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Current Forecast Snapshot Daily](/datasets/tables/CurFcstSnapshotDaily.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
- [Resultant Forecast](/glossary/resultant_forecast.md)
- [Promo Lift](/glossary/promo_lift.md)
