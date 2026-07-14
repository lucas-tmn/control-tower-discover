---
type: Glossary Term
title: Promo Lift
description: Incremental demand quantity from planned promotions, entered in Logility separately from the statistical forecast and overlaid as a distinct demand component.
tags: [forecast, demand-planning, promotional, logility, glossary, promo]
timestamp: 2026-06-29
status: agent draft
---

## Definition

**Promo Lift** is the incremental demand quantity expected from a planned promotion. It is entered by the demand planning or marketing team in Logility, separate from the statistical forecast, to augment the base demand signal when a promotion is expected to drive demand above the model's baseline.

Promo Lift is always a separate component — it is never embedded in the [Resultant Forecast](/glossary/resultant_forecast.md). Total demand is:

```text
TotalForecast = ResultantForecast + PromoLift
```

## Weekly Distribution Caveat

Demand planning in Logility operates at a **monthly grain**. When promo lift flows downstream, the week-level distribution differs between datasets:

**[Current Forecast](/datasets/tables/FactCurrentForecast.md)** — Promo Lift is extracted at the monthly level and then distributed evenly across all fiscal weeks in that month (÷ weeks in month). A promotion entered for week 1 of a 4-week month appears as `promo_qty ÷ 4` in each of the four weeks — not concentrated in the actual promo week.

**[Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)** — The supply planning module reflects the actual week the promo lift was entered. The full promo quantity appears in the correct planning week; distribution is accurate at the week level.

| Use case | Recommended source |
| --- | --- |
| Monthly aggregate promo demand | Either table |
| Weekly promo timing accuracy | [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md) |
| Forecast input vs. actuals comparison | [Current Forecast](/datasets/tables/FactCurrentForecast.md) |

## Related

- [Resultant Forecast](/glossary/resultant_forecast.md)
- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Net Forecast](/glossary/net_forecast.md)
