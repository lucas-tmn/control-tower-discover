---
type: Dataset
title: Current Forecast
description: Latest forecast snapshot published to supply planning at the weekly item-warehouse grain, capturing resultant (model-driven, post-override), promotional lift, and total forecast quantities normalized from monthly source data.
tags: [forecast, supply-planning, demand-planning, weekly-grain, snapshot, promotional-lift, logility]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[FactCurrentForecast]"
source_system: Logility
refresh_cadence: daily
data_source: fabric
status: draft
---

## Purpose

Operationally current demand forecast used in the supply planning database for generating the Supply Plan in Logility. This table holds the most recent published forecast at the **item × warehouse × fiscal week** grain — three forecast quantities per row: the resultant (statistical, post-override) forecast, the promotional lift overlay, and their combined total. All quantities are in **units**.

Forecast quantities originate as monthly values in Logility and are normalized to weekly granularity by dividing each monthly quantity by the number of fiscal weeks in that month. This is a basic conversion for trend analysis and not the exact weekly allocation that the Supply Plan would try to solve for.

Used in:

- Supply plan inputs (weekly demand signal for each item-warehouse)
- Item-warehouse reconciliation for [Forecast Accuracy](/metrics/forecast_accuracy.md) after Demand Consensus; customer-level forecast accuracy uses the [Working Forecast](/datasets/tables/FactWorkingForecast.md) captured at consensus because the customer dimension is collapsed in this table
- Promotional lift visibility alongside the statistical model forecast

---

## Grain

Each row represents one **item × warehouse × fiscal week-ending** combination in the latest forecast snapshot.

`ItemSKU` × `WarehouseID` × `WeekEnding` is unique within the table. `SnapshotDate` is a metadata column recording when the forecast was published; it is constant across all rows (the table is fully replaced on each daily load) and is not part of the grain.

---

## Schema

All forecast quantities are in **units**.

### Grain / Keys

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemSKU` | VARCHAR(20) | FK to [Product Master](/datasets/tables/DimProduct.md) (`DimProduct[ItemSKU]`) |
| `WarehouseID` | VARCHAR(10) | FK to [Warehouse Master](/datasets/tables/DimWarehouse.md) (`DimWarehouse[WarehouseID]`) |
| `WeekEnding` | DATE | FK to [Fiscal Calendar](/datasets/tables/DimDate.md) (`DimDate[TransactionDate]`); Saturday, the last day of the fiscal planning week; derived by mapping the monthly forecast period to fiscal week boundaries |

### Forecast Quantities

| Column | Type | Meaning |
| --- | --- | --- |
| `ResultantForecast` | INT | Final forecast quantity (units) after all planner overrides have been applied on top of the statistical model; see [Resultant Forecast](/glossary/resultant_forecast.md) |
| `PromoLift` | INT | Promotional lift quantity (units); incremental demand from planned promotions; distributed evenly across all fiscal weeks in the month — see [Promo Lift](/glossary/promo_lift.md) for the week-distribution caveat |
| `TotalForecast` | INT | Combined demand signal (units): `ResultantForecast + PromoLift`; the total quantity the supply plan should cover for this item-warehouse-week |

### Metadata

| Column | Type | Meaning |
| --- | --- | --- |
| `SnapshotDate` | DATE | Date the forecast was published and loaded from Logility; constant across all rows; the full table is replaced on each daily load |

---

## Snapshot Strategy

This table stores only the most recent published forecast snapshot. The full table is replaced on each daily load; no prior snapshots are retained.

Full snapshot history (required for plan drop horizon analysis or forecast drift tracking) is planned for a future release (Phase 5).

---

## Grain Normalization

Logility publishes forecast quantities at a monthly grain. `FactCurrentForecast` normalizes these to weekly values by dividing each monthly quantity by the number of fiscal weeks in that month (derived from the fiscal calendar). Values are rounded to the nearest integer.

This produces an even distribution across weeks within a month — a 4-week month yields `monthly_qty ÷ 4` per week; a 5-week month yields `monthly_qty ÷ 5`. Promotional lift entered for a specific week in Logility will appear flat across the entire month in this table. Use [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) for week-precise promo distribution.

This normalization logic will no longer apply after the Q3 2026 transition to a native weekly-grain forecast source. The table structure is expected to remain unchanged; only the ETL source will be updated.

---

## Temporal Notes

- `WeekEnding` is sourced from `DimDate[TransactionDate]`, aligned to the fiscal calendar.
- Joins to [Fiscal Calendar](/datasets/tables/DimDate.md) should use the `TransactionDate` column (primary key).
- The fiscal calendar boundary is currently set through early 2029; records beyond that boundary are excluded by the load logic.

---

## Related

- [Resultant Forecast](/glossary/resultant_forecast.md)
- [Promo Lift](/glossary/promo_lift.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Forecast Accuracy](/metrics/forecast_accuracy.md)
