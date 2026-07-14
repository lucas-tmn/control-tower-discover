---
type: Metric
title: Shippable Inventory
description: Projected available inventory at the end of a planning week, net of all planned demand and supply events; the primary output of the Logility supply plan.
tags: [supply-plan, inventory, logility, shippable-inventory, kpi]
timestamp: 2026-06-29
status: agent draft
---

## Definition

Shippable Inventory (SI) is the quantity of an item projected to be available at a warehouse at the close of each planning week, after all planned outbound demand and inbound supply have been applied. It is the central planning output in [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) and the primary signal used to identify supply constraints across the 39-week horizon.

See [Shippable Inventory (glossary)](/glossary/shippable_inventory.md) for the conceptual definition and what "shippable" means in this organization.

## Calculation

At the business level, Shippable Inventory is a weekly roll-forward of inventory:

```text
Beginning on hand
  + Purchase order quantity
  + Production quantity
  + Transfers in
  - Transfers out
  - Firm customer orders
  - Net forecast
= Shippable Inventory
```

Where:

- `BeginningBalance` = actual inventory on hand as of `SnapshotDate`
- `TotalPOs` = firm and planned purchase order quantity expected in the week
- `TotalProd` = firm and planned production quantity expected in the week
- `TotalTI` = in-transit, on-order, and planned transfers into the warehouse
- `TotalTO` = firm and planned transfers out of the warehouse
- `FirmDemand` = confirmed customer orders expected to ship in the week
- `NetForecast` = forecast demand remaining after firm customer orders are applied; in business terms, total forecast less firm customer orders, floored at zero

In the Supply Plan Detail fields, the compact calculation is:

```text
SIQty = BeginningBalance + TotalReceipts - TotalOut
TotalReceipts = TotalPOs + TotalProd + TotalTI
TotalOut = FirmDemand + Promo Lift + NetForecast + TotalTO
```

`Promo Lift` is tracked separately from `NetForecast` in [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md), so it is included explicitly in `TotalOut`.

All values are sourced directly from [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md).

## Timing and Roll-Forward

The first projected week starts from today's on-hand inventory, recorded as `BeginningBalance` on the daily `SnapshotDate`. All other elements in the calculation are the receipts, transfers, orders, and forecast demand expected to occur between today and the week-ending Saturday. The result is the projected Shippable Inventory for that week-ending date.

For future weeks, the plan does not restart from today's on-hand balance. It rolls forward from the preceding week-ending Shippable Inventory, then applies that next week's expected receipts, shipments, transfers, and forecast demand to calculate the next week-ending Shippable Inventory.

## Interpretation

| SIQty | Signal |
| --- | --- |
| Positive | Surplus inventory projected; review against safety stock target (`SSQty`) |
| Zero | Plan is exactly balanced; no surplus, no gap |
| Negative | Supply gap — planned outbound exceeds projected receipts; a constraint exists this week |

When `SIQty < 0`:

- The plan cannot fulfill all projected demand for this week.
- If the week is within item lead time, there is no time to bring in additional supply through normal replenishment — escalate immediately.
- If the week is outside lead time, evaluate whether Logility has already generated a planned order to recover the position in a future week.

## Relationship to Safety Stock

SI alone does not indicate whether inventory is "healthy" — it must be compared to the safety stock target (`SSQty`):

- `SI > SS` → position is above target; monitor for overstock risk in extended horizon
- `0 < SI < SS` → position is below target; a safety stock gap exists; see [Safety Stock Gap](/metrics/safety_stock_gap.md)
- `SI < 0` → supply gap; the plan cannot fulfill demand regardless of SS target

## Aggregation Notes

SI quantities should **not** be summed across weeks for a single item-warehouse, as they represent projected ending balances at discrete points in time, not flows. Summing would overstate inventory. Compare week-over-week SI values to understand inventory trajectory.

## Related

- [Shippable Inventory (glossary)](/glossary/shippable_inventory.md)
- [Safety Stock Gap](/metrics/safety_stock_gap.md)
- [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
