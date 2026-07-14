---
type: Dataset
title: Supply Plan Detail
description: Current day's Logility supply plan showing a 39-week forward projection of Shippable Inventory at the item-warehouse-week grain, net of all planned demand, supply receipts, and transfer activity.
tags: [supply-plan, inventory, logility, shippable-inventory, safety-stock, demand, transfers, production, purchase-orders]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[FactSupplyPlanDetail]"
source_system: Logility
refresh_cadence: daily
data_source: both
status: draft
---

## Purpose

Daily extract of the Logility supply plan for operations. The table is fully overwritten each day with the current plan for semantic model efficiency. There is a similar table that keeps the snapshot history available. The Supply Plan is generate in the Logility application and projects 39 weeks forward from the snapshot date, showing how inventory is expected to evolve week by week at each item-warehouse combination, given current demand signals, open supply orders, planned orders, and safety stock targets.

The central output is [Shippable Inventory](/glossary/shippable_inventory.md) (`SIQty`) — the quantity projected to be available at the close of each planning week. Negative SI values identify supply gaps where planned outbound exceeds projected receipts. The Supply Plan solver's primary goal is to make Shippable Inventory match the Safety Stock Target.

Used in:

- Exception-based supply plan review (SI negatives, safety stock gaps, fulfillment shortfalls)
- Week-by-week visibility into firm vs. planned supply and demand
- Safety stock gap analysis across the 39-week horizon

---

## Grain

Each row represents one **item × warehouse × week-ending Saturday** combination in the current supply plan.

`ItemSKU` × `WarehouseID` × `WeekEnding` is unique within the table. `SnapshotDate` is a metadata column that records when the daily extract was loaded; it does not vary within the table and should not be treated as part of the grain.

---

## Schema

### Grain / Keys

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemSKU` | VARCHAR(20) | FK to [Product Master](/datasets/DimProduct.md) (`DimProduct[ItemSKU]`) |
| `WarehouseID` | VARCHAR(10) | FK to [Warehouse Master](/datasets/DimWarehouse.md) (`DimWarehouse[Warehouse]`) |
| `WeekEnding` | DATE | FK to [Fiscal Calendar](/datasets/DimDate.md) (`DimDate[TransactionDate]`); always a Saturday; the last day of the projected planning week |

### Demand

| Column | Type | Meaning |
| --- | --- | --- |
| `BeginningBalance` | INT | Actual on-hand balance as of [SnapshotDate] — NOT the projected beginning on-hand for each week. This value is identical across all [WeekEnding] dates. For projected inventory at week ending, use [SIQty]. |
| `FirmDemand` | INT | Confirmed open customer order quantity for the week; see [Firm Demand](/glossary/firm_demand.md) |
| `Promo Lift` | INT | Manual promotional lift quantity entered by marketing and fed into Logility; independent of the statistical forecast |
| `NetForecast` | INT | Statistical forecast quantity net of firm customer orders; floored at zero — when firm orders meet or exceed the forecast, this is 0; see [Net Forecast](/glossary/net_forecast.md) |

### Transfers Out

| Column | Type | Meaning |
| --- | --- | --- |
| `TOutFirm` | INT | Quantity on a firm (committed) transfer-out order |
| `TOutPlanned` | INT | Quantity on a transfer-out order Logility has planned but not yet committed (outside lead time) |

### Production

| Column | Type | Meaning |
| --- | --- | --- |
| `ProdFirm` | INT | Quantity on a firm production order |
| `ProdPlanned` | INT | Quantity on a production order Logility has planned but not yet committed (outside production lead time) |

### Purchase Orders

| Column | Type | Meaning |
| --- | --- | --- |
| `POsFirm` | INT | Quantity on a firm purchase order |
| `POsPlanned` | INT | Quantity on a purchase order Logility has planned but not yet committed (outside vendor manufacturing lead time) |

### Transfers In

| Column | Type | Meaning |
| --- | --- | --- |
| `TInInTransit` | INT | Quantity on a transfer-in order currently in transit to this warehouse |
| `TInOnOrder` | INT | Quantity on a firm transfer-in order not yet in transit |
| `TInPlanned` | INT | Quantity on a transfer-in order Logility has planned but not yet committed (outside lead time) |

### Inventory Position

| Column | Type | Meaning |
| --- | --- | --- |
| `SIQty` | INT | [Shippable Inventory](/glossary/shippable_inventory.md): projected available quantity at week-end; the primary supply plan output |
| `SSQty` | INT | Safety stock target quantity for this item-warehouse |
| `SI-SS` | INT | `SIQty − SSQty`; positive = above safety stock target; negative = below target |
| `SINegative` | INT | `SIQty` when `SIQty < 0`; zero otherwise; isolates supply gap weeks |
| `SIPositive` | INT | `SIQty` when `SIQty ≥ 0`; zero otherwise |
| `SSGap` | INT | Quantity needed to reach safety stock target; zero when `SIQty ≥ SSQty`; see [Safety Stock Gap](/metrics/safety_stock_gap.md) |

### Aggregate Demand & Fulfillment

| Column | Type | Meaning |
| --- | --- | --- |
| `TotalDemand` | INT | `FirmDemand + Promo Lift + NetForecast`; total planned outbound demand for the week |
| `DemandFulfillmentQty` | INT | Quantity of `TotalDemand` the plan projects can be fulfilled; see [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md) |
| `TotalOut` | INT | `FirmDemand + Promo Lift + NetForecast + TotalTO`; total quantity leaving this warehouse (demand + transfers out) |

### Aggregate Supply

| Column | Type | Meaning |
| --- | --- | --- |
| `TotalTO` | INT | `TOutFirm + TOutPlanned`; total transfer-out |
| `TotalProd` | INT | `ProdFirm + ProdPlanned`; total production |
| `TotalPOs` | INT | `POsFirm + POsPlanned`; total purchase orders |
| `TotalTI` | INT | `TInInTransit + TInOnOrder + TInPlanned`; total transfer-in |
| `TotalReceipts` | INT | `TotalProd + TotalPOs + TotalTI`; all planned inbound supply |
| `NetInventoryChange` | INT | `TotalReceipts − TotalOut`; net weekly inventory movement |

### Metadata

| Column | Type | Meaning |
| --- | --- | --- |
| `SnapshotDate` | DATE | Date the daily Logility extract was loaded; equals today; constant across all rows in the table since the full plan is replaced each day |

---

## Planning Horizon & Temporal Notes

- The plan covers **39 weeks forward** from `SnapshotDate`.
- `WeekEnding` is always a **Saturday**, aligned to the fiscal week boundary in [Fiscal Calendar](/datasets/DimDate.md).
- All date joins to `DimDate` should use the `TransactionDate` column.
- Because the table is a daily overwrite, there is no history of prior plan snapshots. To compare today's plan to a prior plan, a separate snapshot store would be required.

---

## Firm vs. Planned Supply

Supply quantities appear in paired columns (e.g., `POsFirm` / `POsPlanned`). Understanding the distinction is critical for assessing supply reliability:

- **Firm** — An order exists in the system. The quantity is committed and should be considered reliable for the near-term horizon.
- **Planned** — Logility has computed that an order should be placed but it has not been issued yet. Planned quantities are projections and may not materialize if lead times or constraints change.

When assessing short-term supply risk, weight firm supply more heavily than planned supply.

---

## Related

- [Shippable Inventory](/glossary/shippable_inventory.md)
- [Net Forecast](/glossary/net_forecast.md)
- [Firm Demand](/glossary/firm_demand.md)
- [Safety Stock Gap](/metrics/safety_stock_gap.md)
- [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
- [Product Master](/datasets/DimProduct.md)
- [Warehouse Master](/datasets/DimWarehouse.md)
- [Fiscal Calendar](/datasets/DimDate.md)
