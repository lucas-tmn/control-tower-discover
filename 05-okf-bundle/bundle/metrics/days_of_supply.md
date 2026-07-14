---
type: Metric
title: Days of Supply
description: Forward-looking supply coverage that includes both current on-hand available inventory and open inbound purchase order receipts projected against the demand forecast.
tags: [inventory, supply, coverage, planning, kpi]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Definition

Days of Supply (DOS) is a forward-looking metric that answers: given current inventory plus expected inbound supply, how many days can we satisfy demand before running out?

Unlike [Coverage Days](/metrics/coverage_days.md), DOS incorporates the open supply pipeline from [purchase_orders](/datasets/tables/purchase_orders.md), making it the right metric for planning decisions and stockout recovery projections.

## Calculation

```text
Days of Supply = (qty_available + open_po_qty) / avg_daily_demand
```

Where:

- `qty_available` = from [inventory_onhand](/datasets/tables/inventory_onhand.md)
- `open_po_qty` = sum of `open_qty` for `po_status IN ('Open', 'Partial')` from [purchase_orders](/datasets/tables/purchase_orders.md)
- `avg_daily_demand` = rolling historical average from [sales_orders](/datasets/tables/sales_orders.md), **or** forward forecast rate from [demand_forecast](/datasets/tables/demand_forecast.md) when available

Using the **forward forecast** as the demand rate is preferred for new products, where historical averages may be too short or unrepresentative.

## Interpretation

| Days of Supply | Signal |
| --- | --- |
| < item lead_time_days | Stockout projected before next receipt can arrive — escalate |
| Between lead time and target DOS | Normal operating range — monitor |
| > target DOS | Potential overstock — review supply pipeline |

Specific thresholds for target DOS are defined in [stockout_escalation](/playbooks/stockout_escalation.md) and [overstock_exposure](/metrics/overstock_exposure.md).

## Related

- [Coverage Days](/metrics/coverage_days.md) — on-hand only snapshot (no inbound supply)
- [Overstock Exposure](/metrics/overstock_exposure.md)
- [Inventory On Hand](/datasets/tables/inventory_onhand.md)
- [Purchase Orders](/datasets/tables/purchase_orders.md)
- [Demand Forecast](/datasets/tables/demand_forecast.md)
- [Product Master](/datasets/tables/DimProduct.md)
