---
type: Dataset
title: Working Forecast
description: Latest Working Forecast as extracted from the Logility Demand Planning database at the item-warehouse-customer group-week grain; the pre-consensus demand signal actively being refined before synchronization to supply planning.
tags: [forecast, demand-planning, working-forecast, customer-group, weekly-grain, snapshot, logility, promotional-lift]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[FactWorkingForecast]"
source_system: Logility
refresh_cadence: daily
data_source: fabric
status: agent draft
---

## Purpose

Nightly snapshot of the in-progress working demand forecast sourced from Logility's DemandPlanning database. Provides the current-state demand signal at the **item × warehouse × customer group × fiscal week** grain across three forecast quantities: resultant (statistical, post-override), promotional lift, and total. All quantities are in **units**.

Unlike [Current Forecast](/datasets/tables/FactCurrentForecast.md), which reflects the demand signal after the Demand Consensus process has been finalized and pushed to Logility's SupplyPlanning database, this table captures the **pre-consensus** state — the working view that demand planners are actively refining. The addition of the `CustomerGroup` dimension makes it the primary source for customer-segment-level demand analysis.

Used in:

- Demand planning review at the customer group level
- Pre-consensus demand signal visibility for daily operational reporting
- Customer-level [Forecast Accuracy](/metrics/forecast_accuracy.md) when captured at the official Demand Consensus snapshot
- Comparison against [Current Forecast](/datasets/tables/FactCurrentForecast.md) to monitor demand consensus-stage adjustments

---

## Grain

Each row represents one **item × warehouse × customer group × fiscal week-ending** combination in the latest forecast snapshot.

`ItemSKU` × `WarehouseID` × `CustomerGroup` × `WeekEnding` is unique within the table. `SnapshotDate` is a metadata column recording when the nightly load ran; it is constant across all rows (the table is fully replaced on each daily load) and is not part of the grain.

---

## Schema

All forecast quantities are in **units**.

### Grain / Keys

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemSKU` | VARCHAR(20) | FK to [Product Master](/datasets/tables/DimProduct.md) (`DimProduct[ItemSKU]`) |
| `WarehouseID` | VARCHAR(10) | FK to [Warehouse Master](/datasets/tables/DimWarehouse.md) (`DimWarehouse[WarehouseID]`) |
| `CustomerGroup` | VARCHAR(50) | Demand planning customer group; FK to [Customer Master](/datasets/tables/DimCustomer.md) (`DimCustomer[AccountAndShipToNumber]`); NULL values in the Logility source are normalized to `AFICONS` by ETL — `AFICONS` is a valid customer group, not a data quality indicator |
| `WeekEnding` | DATE | FK to [Fiscal Calendar](/datasets/tables/DimDate.md) (`DimDate[TransactionDate]`); the last day of the fiscal planning week; derived by mapping the monthly source forecast period to fiscal week boundaries |

### Forecast Quantities

| Column | Type | Meaning |
| --- | --- | --- |
| `ResultantForecast` | INT | Forecast quantity (units) after all planner overrides have been applied on top of the statistical model; see [Resultant Forecast](/glossary/resultant_forecast.md) |
| `PromoLift` | INT | Promotional lift quantity (units); incremental demand from planned promotions, distributed evenly across fiscal weeks in the month; see [Promo Lift](/glossary/promo_lift.md) |
| `TotalForecast` | INT | Combined demand signal (units): `ResultantForecast + PromoLift`; the total quantity to be covered for this item-warehouse-customer group-week |

### Metadata

| Column | Type | Meaning |
| --- | --- | --- |
| `SnapshotDate` | DATE | Date the nightly forecast snapshot was generated; constant across all rows; the full table is replaced on each daily load |

---

## Working vs. Current Forecast

This table and [Current Forecast](/datasets/tables/FactCurrentForecast.md) both originate in Logility but represent different stages of the demand planning workflow.

| | Working Forecast | Current Forecast |
| --- | --- | --- |
| **Logility database** | DemandPlanning | SupplyPlanning |
| **Stage** | Pre-consensus — actively being refined | Post-consensus — approved and published, used to plan purchase orders, manufacturing orders, etc |
| **CustomerGroup** | Yes — part of grain | No — summed to Item-Warehouse (Inventory Plann Location) at Post-consensus sync |
| **Grain** | Item × Warehouse × CustomerGroup × Week | Item × Warehouse × Week |
| **Primary use** | Demand planning by customer segment, forecast accuracy | Supply planning inputs |

The Demand Consensus process synchronizes the finalized working forecast from DemandPlanning to SupplyPlanning, creating the official [Current Forecast](/datasets/tables/FactCurrentForecast.md). Since Supply Planning operates only at the ItemSKU-Warehouse level, demand is aggregated by ItemSKU-Warehouse-FiscalPeriod for synchronization, dropping the customer group dimension.

---

## Snapshot Strategy

This table stores only the most recent nightly working forecast snapshot. The full table is replaced on each daily load; no prior snapshots are retained. Full snapshot history is retained in the upstream source.

---

## Grain Normalization

Logility publishes forecast quantities at a monthly grain in the source database. `FactWorkingForecast` normalizes these to weekly values by dividing each monthly quantity by the number of fiscal weeks in that month (derived from the fiscal calendar). Values are rounded to the nearest integer.

This produces an even distribution across weeks within a month — a 4-week month yields `monthly_qty ÷ 4` per week; a 5-week month yields `monthly_qty ÷ 5`.

This normalization will no longer apply after the Q3 2026 transition to a native weekly-grain forecast source. The table structure and grain are expected to remain unchanged; only the ETL source logic will be updated.

---

## Temporal Notes

- `WeekEnding` is sourced from `DimDate[TransactionDate]`, aligned to the fiscal calendar.
- Joins to [Fiscal Calendar](/datasets/tables/DimDate.md) should use the `TransactionDate` column (primary key).
- The fiscal calendar boundary is currently set through early 2029; records beyond that boundary are excluded by the load logic.

---

## Related

- [Resultant Forecast](/glossary/resultant_forecast.md)
- [Promo Lift](/glossary/promo_lift.md)
- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
- [Customer Master](/datasets/tables/DimCustomer.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Forecast Accuracy](/metrics/forecast_accuracy.md)
