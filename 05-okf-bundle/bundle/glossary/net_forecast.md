---
type: Glossary Term
title: Net Forecast
description: The portion of the statistical demand forecast not yet covered by firm customer orders for a given planning week; floored at zero to prevent negative demand in the supply plan.
tags: [supply-plan, demand, forecast, logility, glossary, net-forecast]
timestamp: 2026-06-29
status: agent draft
---

## Definition

**Net Forecast** is the week's statistical demand forecast quantity after subtracting the firm open customer orders already placed for that week. It represents only the "unmet" portion of the forecast — demand that is expected but not yet committed.

```text
NetForecast = MAX(0, StatisticalForecast − FirmDemand)
```

NetForecast has a **lower bound of zero**. When firm customer orders meet or exceed the week's statistical forecast, NetForecast equals zero rather than going negative.

## Why Net Forecast Exists

Without netting, a supply plan that includes both firm orders and a full statistical forecast would double-count demand — planning for the same customer need twice. Logility uses Net Forecast to ensure that only the uncovered portion of the forecast is planned for, keeping total projected demand accurate.

In practice:

- In **near-term weeks** (inside the order horizon), firm orders typically dominate and Net Forecast is often zero.
- In **outer weeks** (beyond the order horizon), firm orders are sparse and Net Forecast approaches the full statistical forecast.

## Relationship to Total Demand

Net Forecast is one of three components of total planned demand in the supply plan:

```text
TotalDemand = FirmDemand + Promo Lift + NetForecast
```

See [Firm Demand](/glossary/firm_demand.md) and [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) for the other components.

## What Net Forecast Is Not

Net Forecast is **not** the statistical forecast itself. When comparing the supply plan's demand signal to the Logility forecast output, use the statistical forecast from the appropriate forecast dataset — not `NetForecast` from `FactSupplyPlanDetail`, which has already been reduced by firm orders.

## Related

- [Firm Demand](/glossary/firm_demand.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Demand Forecast](/datasets/tables/demand_forecast.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
