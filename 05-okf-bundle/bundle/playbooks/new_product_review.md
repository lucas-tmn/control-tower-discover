---
type: Playbook
title: New Product Performance Review
description: A structured reasoning process for assessing recently introduced product sales performance against forecast and surfacing inventory risk recommendations.
tags: [new-product, demand-planning, inventory, forecast, review, playbook]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Purpose

Use this playbook when asked to assess how recently introduced products are performing and what risks need to be discussed. This is a self-directed reasoning workflow — follow the steps in order, gather the relevant data, and produce a structured recommendation.

This playbook covers:

- Sales performance vs. demand forecast
- Inventory risk assessment (stockout or overstock)
- Stockout and overstock projections with recovery timelines
- Recommended actions including forecast revision and escalation

## Step 1 — Scope the Products

Query [Product Master](/datasets/tables/DimProduct.md) for items meeting both criteria:

- `InitialInvoiceDate` falls within the recently introduced window — see [recently_introduced](/glossary/recently_introduced.md) for the exact definition
- `LifecycleStage NOT IN ('End of Life')` — exclude items planned for or already discontinued

Record the item count and the `InitialInvoiceDate` range included so you can cite it in your output.

## Step 2 — Compare Actuals vs. Forecast

For each scoped item, compare actual sales against the planned demand forecast.

**Data sources:**

- Actuals: `shipped_qty` from [sales_orders](/datasets/tables/sales_orders.md) — use shipped quantity, not ordered quantity, to reflect real fulfilled demand
- Forecast: most recent firm forecast version from [demand_forecast](/datasets/tables/demand_forecast.md) for the same item and period
- Align both on the same time period and unit of measure before comparing

Calculate [forecast_accuracy](/metrics/forecast_accuracy.md) per item for the period under review.

**Decision signals:**

| Condition | Signal | Next Step |
| --- | --- | --- |
| Actuals consistently above forecast across multiple periods | Demand stronger than planned | Recommend forecast increase → [forecast_revision](/playbooks/forecast_revision.md) |
| Actuals consistently below forecast across multiple periods | Demand weaker than planned | Recommend forecast decrease → [forecast_revision](/playbooks/forecast_revision.md) |
| Actuals tracking forecast closely | Forecast is healthy | Note as on-track; no revision needed |
| High period-over-period volatility with no clear trend | Unstable demand pattern | Flag for planner review; do not recommend revision based on single-period swings |

A single period of deviation is not sufficient to recommend a revision. Require at least [FILL IN: 2–3 consecutive periods] of consistent directional bias.

## Step 3 — Assess Inventory Risk

For each item, calculate the following metrics using current data:

| Metric | Purpose | Document |
| --- | --- | --- |
| Coverage Days | How long current on-hand inventory lasts with no inbound supply | [coverage_days](/metrics/coverage_days.md) |
| Days of Supply | How long inventory lasts including open PO receipts | [days_of_supply](/metrics/days_of_supply.md) |
| Overstock Exposure | Whether total supply exceeds projected demand over the horizon | [overstock_exposure](/metrics/overstock_exposure.md) |

**Stockout risk signal**: If `days_of_supply < lead_time_days` from [Product Master](/datasets/tables/DimProduct.md) ([FILL IN: confirm lead time column]), a stockout is projected before the next replenishment can arrive. Proceed to [stockout_escalation](/playbooks/stockout_escalation.md) for the action path.

**Overstock risk signal**: If overstock exposure is above threshold, the item has more supply than the forecast can absorb within the planning horizon. See [overstock](/glossary/overstock.md) for severity levels.

## Step 4 — Project Stockout or Recovery Date

**If stockout risk exists:**

1. Using current [inventory_onhand](/datasets/tables/inventory_onhand.md) and open [purchase_orders](/datasets/tables/purchase_orders.md), project the date when `qty_available` will reach zero at the current demand rate.
2. Using the `expected_receipt_date` of the next open PO, project when inventory will return to a positive level.
3. If no open POs exist, note that no replenishment has been initiated — this is a critical escalation signal requiring immediate attention.

**If overstock risk exists:**

1. Calculate weeks of supply above target using [overstock_exposure](/metrics/overstock_exposure.md).
2. Determine root cause: demand miss (actuals below forecast) or supply overbuild (POs placed on inflated forecast before the miss was visible).
3. Identify whether any in-transit POs can still be cancelled or deferred before adding to on-hand inventory.

## Step 5 — Produce Recommendations

Structure the output with the following four sections:

### Section 1: Items On Track

List items where actuals are tracking forecast and inventory is within a healthy range. Brief confirmation — no action needed.

### Section 2: Items at Stockout Risk

For each at-risk item:

- Severity (based on [stockout_escalation](/playbooks/stockout_escalation.md))
- Projected stockout date
- Projected recovery date (based on next open PO receipt, or earliest possible if no PO exists)
- Recommended action (expedite open PO, place emergency PO, escalate to buyer)

### Section 3: Items at Overstock Risk

For each overstock item:

- Weeks of excess supply above target
- Root cause: demand miss vs. supply overbuild
- Recommended action (forecast decrease in Logility, PO cancellation/deferral, demand pull-forward)

### Section 4: Forecast Revision Candidates

List items with consistent forecast deviation (per Step 2 signals) and recommend direction of revision. Reference [forecast_revision](/playbooks/forecast_revision.md) for the full revision process.

Always cite the dataset and time window your analysis covers. Flag any items where data was missing or ambiguous.

## Related

- [Forecast Revision](/playbooks/forecast_revision.md)
- [Stockout Escalation](/playbooks/stockout_escalation.md)
- [Demand Forecast](/datasets/tables/demand_forecast.md)
- [Sales Orders](/datasets/tables/sales_orders.md)
- [Inventory On Hand](/datasets/tables/inventory_onhand.md)
- [Purchase Orders](/datasets/tables/purchase_orders.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Recently Introduced](/glossary/recently_introduced.md)
- [Forecast Accuracy](/metrics/forecast_accuracy.md)
- [Coverage Days](/metrics/coverage_days.md)
- [Days of Supply](/metrics/days_of_supply.md)
- [Overstock Exposure](/metrics/overstock_exposure.md)
