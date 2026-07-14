---
type: Playbook
title: Forecast Revision
description: Decision rules and process for recommending a demand forecast revision in Logility, triggered when actuals consistently deviate from plan in a single direction.
tags: [forecast, demand-planning, logility, revision, playbook]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Purpose

This playbook defines when a Logility forecast revision is warranted and what the recommendation should include. Forecast revisions are not made automatically — this playbook produces a **recommendation for a human planner** to review, adjust, and act on in Logility.

## When to Recommend a Revision

Recommend a forecast revision when [forecast_accuracy](/metrics/forecast_accuracy.md) shows a **consistent directional bias** across multiple planning periods:

| Signal | Direction | Condition |
| --- | --- | --- |
| Actuals persistently above forecast | Upward revision | Demand is stronger than the model is capturing |
| Actuals persistently below forecast | Downward revision | Demand is weaker than the model is projecting |

A single period of deviation is **not** sufficient. Require at least [FILL IN: 2–3 consecutive periods] of consistent bias before recommending a revision. Single-period swings may reflect noise, timing, or a one-time event — not a structural demand shift.

## What to Include in the Recommendation

A complete forecast revision recommendation must specify:

1. **Items affected** — list item_id and description for each
2. **Direction** — upward or downward
3. **Magnitude** — percentage or quantity adjustment suggested, derived from the observed deviation
4. **Time horizon** — which future periods the revision should apply to
5. **Evidence** — the actual vs. forecast comparison supporting the recommendation (periods covered, quantities, accuracy %)
6. **Inventory implication** — what the current forecast miss means for inventory risk (link to [coverage_days](/metrics/coverage_days.md) or [overstock_exposure](/metrics/overstock_exposure.md) as applicable)

## Who Acts on This

Forecast revisions are made by the **demand planner** in Logility. This playbook produces the recommendation; the planner reviews, adjusts, and firms the change in Logility.

After a revision is firmed, planned orders are updated in Logility and pushed to the ERP. Monitor [demand_forecast](/datasets/tables/demand_forecast.md) in subsequent planning cycles to confirm the revision is reflected in the warehouse.

## Cautions

- Do not recommend aggressive revisions based on very short demand history. For a new product with fewer than [FILL IN: 4–6 weeks] of sales data, distinguish between a true demand miss and typical launch-period noise.
- A downward forecast revision for an item with existing open POs may create or worsen overstock — assess the inventory pipeline before recommending.
- A upward forecast revision for a constrained item may trigger planned POs that cannot realistically be sourced within the item's lead time.

## Related

- [Demand Forecast](/datasets/tables/demand_forecast.md)
- [Sales Orders](/datasets/tables/sales_orders.md)
- [Forecast Accuracy](/metrics/forecast_accuracy.md)
- [Overstock Exposure](/metrics/overstock_exposure.md)
- [New Product Performance Review](/playbooks/new_product_review.md)
- [Recently Introduced](/glossary/recently_introduced.md)
