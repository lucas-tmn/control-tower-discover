---
type: Metric
title: Safety Stock Gap
description: Quantity by which projected Shippable Inventory falls short of the safety stock target for a given item-warehouse-week; zero when SI meets or exceeds the target.
tags: [supply-plan, safety-stock, inventory, risk, kpi]
timestamp: 2026-06-29
status: agent draft
---

## Definition

Safety Stock Gap (SS Gap) is the quantity an item-warehouse position would need to receive in order to reach its safety stock target in a given planning week. It is an exception signal: a non-zero SSGap means the current supply plan leaves the item below its safety stock buffer for that week.

## Calculation

```text
SSGap = MAX(0, SSQty − SIQty)
```

Equivalently:

- When `SIQty ≥ SSQty`: `SSGap = 0` (at or above target; no gap)
- When `SIQty < SSQty`: `SSGap = SSQty − SIQty` (below target; gap equals the shortfall)

Note that `SSGap` is always non-negative. A position above safety stock target produces a gap of zero, not a surplus value. To measure surplus above target, use `SI-SS` from [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) directly.

Both `SSGap` and `SSQty` are sourced from [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md).

## Interpretation

| SSGap | Signal |
| --- | --- |
| `0` | Position meets or exceeds safety stock target; no action needed for SS |
| `> 0` and SI is positive | Below safety stock target; monitor and consider whether planned supply will close the gap in future weeks |
| `> 0` and SI is negative | Supply gap exists; demand cannot be fully met; safety stock shortfall is secondary concern — address SI < 0 first |

SSGap is most actionable when `SIQty > 0` but `SIQty < SSQty`. In this condition the item can still ship, but the buffer is eroded. If the gap persists across multiple weeks without planned supply closing it, the planner should investigate whether the safety stock target is achievable in the current plan.

## Prioritizing Exceptions

When reviewing SSGap exceptions across many items:

1. **Prioritize near-term weeks first** — a gap in week 1–4 that is inside item lead time cannot be recovered through standard replenishment.
2. **Rank by gap magnitude** — larger `SSGap` values represent a greater buffer erosion.
3. **Filter to active items** — join to [Product Master](/datasets/tables/DimProduct.md) and exclude `LifecycleStage = 'End of Life'` and `PartFlag = 'PART'` to avoid noise from inactive or component items.

## Related

- [Shippable Inventory](/metrics/shippable_inventory.md)
- [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
- [Stockout](/glossary/stockout.md)
