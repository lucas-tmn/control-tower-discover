---
type: Metric
title: Projected Fulfillment Rate
description: Percentage of total planned demand in a given item-warehouse-week that the supply plan projects can be fulfilled; below 100% signals a supply constraint in that week.
tags: [supply-plan, fulfillment, demand, inventory, kpi]
timestamp: 2026-06-29
status: agent draft
---

## Definition

Projected Fulfillment Rate measures whether the supply plan can cover all planned demand for a given item-warehouse-week. A rate of 100% means the plan expects to fulfill every unit of demand; below 100% means a supply constraint exists and some demand will go unfulfilled in that week.

## Calculation

```text
ProjectedFulfillmentRate = DemandFulfillmentQty / TotalDemand
```

Expressed as a percentage:

```text
ProjectedFulfillmentRate (%) = (DemandFulfillmentQty / TotalDemand) × 100
```

Where:

- `DemandFulfillmentQty` = quantity of total demand the plan projects can be fulfilled
- `TotalDemand` = `FirmDemand + Promo Lift + NetForecast`

Both values are sourced from [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md).

**Do not compute this metric when `TotalDemand = 0`** — a week with zero planned demand produces a divide-by-zero condition and the ratio is not meaningful.

## Interpretation

| Rate | Signal |
| --- | --- |
| 100% | Full fulfillment projected; no supply constraint this week |
| < 100% | Supply constraint — the plan cannot cover all demand; `TotalDemand − DemandFulfillmentQty` units will be unfulfilled |
| Near 0% | Severe supply gap; nearly all demand for this week will be unmet |

A fulfillment rate below 100% in a near-term week (inside item lead time) is a high-priority exception. There is not enough time to bring in additional supply through normal replenishment, and customer orders will likely be impacted.

## Relationship to Shippable Inventory

Projected Fulfillment Rate and [Shippable Inventory](/metrics/shippable_inventory.md) are complementary views of the same supply constraint:

- A **negative SI** causes a fulfillment shortfall — if `SIQty < 0`, the plan cannot fulfill all demand.
- **Projected Fulfillment Rate** quantifies how much of that demand is projected to be met, making it useful for customer-impact assessment.

When SI is positive, Projected Fulfillment Rate is 100% by definition. Check this metric only when SI indicates a constraint (`SIQty ≤ 0`).

## Related

- [Shippable Inventory](/metrics/shippable_inventory.md)
- [Safety Stock Gap](/metrics/safety_stock_gap.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
- [Firm Demand](/glossary/firm_demand.md)
- [Net Forecast](/glossary/net_forecast.md)
