---
type: Metric
title: Coverage Days
description: The number of days current on-hand available inventory can satisfy demand at the current demand rate, without accounting for any inbound supply.
tags: [inventory, coverage, stockout-risk, kpi]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Definition

Coverage Days is a snapshot metric: how long will current on-hand inventory last if no new supply arrives? It is a leading indicator of stockout risk and the fastest signal to compute when assessing immediate exposure.

Unlike [Days of Supply](/metrics/days_of_supply.md), Coverage Days does **not** include open purchase orders. Use Coverage Days to assess immediate risk; use Days of Supply for forward-looking planning decisions.

## Calculation

```text
Coverage Days = qty_available / avg_daily_demand
```

Where:

- `qty_available` = `qty_on_hand` minus `qty_allocated` from [inventory_onhand](/datasets/tables/inventory_onhand.md)
- `avg_daily_demand` = rolling N-day average of `shipped_qty` from [sales_orders](/datasets/tables/sales_orders.md)
- N = [FILL IN: 30, 60, or 90 days — confirm with planning team]

## Interpretation

Compare Coverage Days against the item's `lead_time_days` from [Product Master](/datasets/tables/DimProduct.md) ([FILL IN: confirm lead time column — not currently in DimProduct]):

- **Coverage Days < lead_time_days** → Stockout risk: a replenishment order placed today cannot arrive before current stock is depleted.
- **Coverage Days ≥ lead_time_days** → Stock will last until the next receipt assuming normal demand continues.

Specific escalation thresholds are defined in [stockout_escalation](/playbooks/stockout_escalation.md).

## Related

- [Days of Supply](/metrics/days_of_supply.md) — the forward-looking companion metric that includes open POs
- [Inventory On Hand](/datasets/tables/inventory_onhand.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Stockout](/glossary/stockout.md)
- [Stockout Escalation](/playbooks/stockout_escalation.md)
