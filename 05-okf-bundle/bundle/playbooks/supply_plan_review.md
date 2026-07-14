---
type: Playbook
title: Supply Plan Review
description: Exception-based reasoning playbook for interpreting the Logility supply plan to identify SI negatives, safety stock gaps, and fulfillment shortfalls, and to prioritize recommended actions.
tags: [supply-plan, inventory, exceptions, logility, playbook, shippable-inventory, safety-stock]
timestamp: 2026-06-29
status: agent draft
---

## Purpose

This playbook defines how to analyze [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) to surface supply constraints, prioritize exceptions, and determine recommended actions. It is the primary reasoning workflow for agents and planners interpreting the current Logility supply plan.

The supply plan is a forward-looking projection — always a snapshot of today's plan as of `SnapshotDate`. Conclusions drawn here reflect the plan's expectations, not physical warehouse reality.

---

## Step 1 — Establish Scope

Before querying [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md), define the scope of the review:

- **Item scope** — a specific SKU, a product line, a planner's portfolio, or all active items
- **Warehouse scope** — a specific warehouse, a warehouse group (from [Warehouse Master](/datasets/tables/DimWarehouse.md)), or all warehouses
- **Time scope** — typically the near-term horizon (weeks 1–13), but full 39-week horizon for longer-range reviews

Filter out noise before analysis:

- Exclude items with `LifecycleStage = 'End of Life'` from [Product Master](/datasets/tables/DimProduct.md)
- Exclude component parts (`PartFlag = 'PART'`) unless the analysis is specifically about components
- Exclude warehouse records not relevant to the planning scope

---

## Step 2 — Identify SI Negative Exceptions

SI negatives are the highest-priority exception in the supply plan. A negative [Shippable Inventory](/metrics/shippable_inventory.md) means the plan cannot fulfill all projected demand for that week.

Filter for: `SIQty < 0` (equivalently, `SINegative < 0`)

For each exception, assess:

1. **Which week?** — How soon is the gap? Weeks inside item lead time have no standard replenishment remedy.
2. **How deep is the gap?** — `SINegative` shows the magnitude; `DemandFulfillmentQty` vs. `TotalDemand` shows the projected fulfillment shortfall.
3. **What is the supply pipeline?** — Are firm orders (`POsFirm`, `ProdFirm`, `TInOnOrder`, `TInInTransit`) arriving before or after the constraint week?
4. **Is the gap isolated to one week or persistent?** — A single negative week that self-corrects in the following week may reflect a timing issue; a run of negative weeks signals a structural supply shortage.

---

## Step 3 — Identify Safety Stock Gap Exceptions

After addressing SI negatives, review items where SI is positive but below the safety stock target. These items can still ship, but their buffer has been eroded.

Filter for: `SSGap > 0` and `SIQty >= 0`

For each exception, assess:

1. **How large is the gap?** — `SSGap` = quantity below target. Larger gaps represent greater exposure to unplanned demand spikes.
2. **Is the gap closing?** — Review the trajectory of `SI-SS` across the 39-week horizon. If it trends toward zero or positive, planned supply is expected to recover the position. If it remains negative or widens, investigate whether Logility has generated sufficient planned orders.
3. **What is driving the shortfall?** — High demand weeks, a missing planned PO, or a transfer delay can all produce a safety stock gap. Understanding the cause determines the right action.

---

## Step 4 — Assess Fulfillment Shortfalls

For any week with `SIQty < 0`, calculate the [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md):

```text
ProjectedFulfillmentRate = DemandFulfillmentQty / TotalDemand
```

- A rate below 100% means some demand will go unmet in that week.
- The unfulfilled quantity = `TotalDemand − DemandFulfillmentQty`.
- Assess whether the unfulfilled demand is Firm (`FirmDemand` is the committed portion) — customer orders at risk must be escalated.

When firm demand is at risk, cross-reference [Sales Orders](/datasets/tables/sales_orders.md) to identify affected customer orders.

---

## Step 5 — Distinguish Firm vs. Planned Supply

When evaluating whether supply will materialize, always separate firm supply from planned supply:

| Supply Type | Reliability | Action if Missing |
| --- | --- | --- |
| Firm (POs, Production, Transfers In — on order or in transit) | High — orders are placed | Confirm receipt date with supplier or DC; expedite if slipping |
| Planned (Logility-projected orders not yet placed) | Lower — plan recommendation only | Verify whether the planner has actioned the planned order; if not, it may not arrive as planned |

Weeks where the only supply covering a gap is **planned** supply carry higher risk than weeks covered by firm supply.

---

## Step 6 — Prioritize and Recommend

Prioritize exceptions in this order:

1. **SI negative, inside item lead time, with firm demand at risk** — Highest urgency; escalate to planner and buyer immediately
2. **SI negative, outside lead time, persistent across multiple weeks** — Structural shortage; review planned order generation and supplier capacity
3. **SI negative, single week, self-correcting** — May be a timing gap; confirm firm receipts arriving immediately after the constraint week
4. **Safety stock gap, near-term (weeks 1–8)** — Monitor; determine if planned supply closes the gap before the horizon
5. **Safety stock gap, outer weeks (weeks 9–39)** — Flag for review; Logility should generate planned orders to recover the position

For each prioritized exception, state:

- Item SKU and warehouse
- Which weeks are affected
- Severity (SI negative vs. SS gap)
- Magnitude (`SINegative`, `SSGap`, or fulfillment shortfall units)
- Whether firm supply is in the pipeline to recover
- Recommended action

---

## Data Notes

- All weeks in [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) end on **Saturday**, aligned to the fiscal week in [Fiscal Calendar](/datasets/tables/DimDate.md).
- The table reflects only the **current day's plan**. There is no historical snapshot comparison available in this table. To compare against a prior plan, a separate snapshot store is required.
- `SnapshotDate` is constant across all rows — filter or ignore it in aggregations.

---

## Related

- [Shippable Inventory (glossary)](/glossary/shippable_inventory.md)
- [Shippable Inventory (metric)](/metrics/shippable_inventory.md)
- [Safety Stock Gap](/metrics/safety_stock_gap.md)
- [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md)
- [Net Forecast](/glossary/net_forecast.md)
- [Firm Demand](/glossary/firm_demand.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Sales Orders](/datasets/tables/sales_orders.md)
- [Stockout Escalation](/playbooks/stockout_escalation.md)
