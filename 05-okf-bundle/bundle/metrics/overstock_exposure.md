---
type: Metric
title: Overstock Exposure
description: The quantity of inventory projected to remain on hand beyond the planning horizon at the current demand rate, indicating excess supply relative to expected demand.
tags: [inventory, overstock, excess, planning, kpi]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Definition

Overstock Exposure quantifies how much inventory is expected to remain unsold after a defined planning horizon. It flags items where supply significantly exceeds projected demand — a risk of elevated carrying costs, obsolescence, or markdown pressure.

## Calculation

```text
Projected Ending Inventory = qty_available + open_po_qty - (forecast_daily_rate × horizon_days)
Overstock Exposure = MAX(0, Projected Ending Inventory)
Overstock Weeks = Overstock Exposure / avg_weekly_demand
```

Where:

- `qty_available` = from [inventory_onhand](/datasets/tables/inventory_onhand.md)
- `open_po_qty` = sum of open PO qty from [purchase_orders](/datasets/tables/purchase_orders.md)
- `forecast_daily_rate` = from [demand_forecast](/datasets/tables/demand_forecast.md), converted to a daily rate
- `horizon_days` = [FILL IN: planning horizon in days, e.g., 90]

## Interpretation

An item has overstock exposure when `Overstock Weeks` exceeds the target threshold.

| Overstock Weeks Above Target | Signal | Action |
| --- | --- | --- |
| 1–2 weeks | Low — monitor | No immediate action; watch next cycle |
| 2–4 weeks | Moderate | Flag for planner review; consider demand pull-forward |
| > 4 weeks | High | Escalate; consider PO cancellation, deferral, or demand promotion |

> **Note**: Thresholds above are illustrative. Confirm organization-specific targets with the planning team and update this document before setting `status: active`.

## Root Cause Signals

When overstock is detected, identify the underlying driver:

- **Demand miss**: actuals consistently below forecast → recommend forecast downward revision via [forecast_revision](/playbooks/forecast_revision.md).
- **Supply overbuild**: POs were placed based on an inflated forecast before the miss was visible → flag for procurement review of open POs.
- **Both**: common for new products experiencing a demand shortfall during launch ramp.

## Related

- [Days of Supply](/metrics/days_of_supply.md)
- [Forecast Accuracy](/metrics/forecast_accuracy.md)
- [Overstock](/glossary/overstock.md)
- [Forecast Revision](/playbooks/forecast_revision.md)
- [New Product Performance Review](/playbooks/new_product_review.md)
