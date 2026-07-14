---
type: Glossary Term
title: Overstock
description: A condition in which inventory on hand plus open inbound supply exceeds projected demand over the planning horizon, resulting in excess inventory exposure.
tags: [inventory, overstock, excess, planning, glossary]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Definition

**Overstock** is the condition where total supply (on-hand + inbound POs) materially exceeds projected demand over the planning horizon.

It is the mirror of [stockout](/glossary/stockout.md): instead of running out, the organization carries more inventory than it can sell within a reasonable timeframe — incurring holding costs, tying up working capital, and risking obsolescence.

## Threshold

An item is flagged as overstock when [Overstock Exposure](/metrics/overstock_exposure.md) exceeds:

> **[FILL IN: e.g., X weeks of forward demand above the safety stock target]**
>
> This threshold requires confirmation from the planning team. Update and change `status` to `active` once agreed.

## Common Root Causes

- Demand came in below forecast — the most common cause for new products during the launch period.
- Supply was built or procured based on an inflated demand signal before the miss was visible.
- A forecast was revised downward too late to stop inbound POs already in transit.
- Promotional or seasonal demand did not materialize as planned.

## Business Impact

- **Holding costs**: warehouse space, handling, and insurance on inventory that is not moving.
- **Obsolescence risk**: particularly acute for new products if demand fails to ramp as expected or the product does not gain traction.
- **Cash flow**: excess inventory ties up working capital that could be deployed elsewhere.

# Related

- [Overstock Exposure](/metrics/overstock_exposure.md)
- [Days of Supply](/metrics/days_of_supply.md)
- [Stockout](/glossary/stockout.md)
- [Forecast Revision](/playbooks/forecast_revision.md)
- [New Product Performance Review](/playbooks/new_product_review.md)
