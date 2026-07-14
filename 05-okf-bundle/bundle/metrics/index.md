---
type: Index
title: Metrics
description: KPI definitions with business meaning, calculation logic, and interpretation.
timestamp: 2026-07-07
---

## Metrics

### Metric

- [ATP In Stock](atp_in_stock.md) - Percentage of ATP stock observations where available-to-promise quantity is greater than zero for selected item-warehouse-week combinations.
- [Coverage Days](coverage_days.md) - The number of days current on-hand available inventory can satisfy demand at the current demand rate, without accounting for any inbound supply.
- [Days of Supply](days_of_supply.md) - Forward-looking supply coverage that includes both current on-hand available inventory and open inbound purchase order receipts projected against the demand forecast.
- [Forecast Accuracy](forecast_accuracy.md) - Governed customer-level forecast accuracy metric family using the Working Forecast captured at Demand Consensus, including MAPE, wMAPE, wMPE forecast bias, RMSE, and Process Value Add.
- [Overstock Exposure](overstock_exposure.md) - The quantity of inventory projected to remain on hand beyond the planning horizon at the current demand rate, indicating excess supply relative to expected demand.
- [Projected Fulfillment Rate](projected_fulfillment_rate.md) - Percentage of total planned demand in a given item-warehouse-week that the supply plan projects can be fulfilled; below 100% signals a supply constraint in that week.
- [Safety Stock Gap](safety_stock_gap.md) - Quantity by which projected Shippable Inventory falls short of the safety stock target for a given item-warehouse-week; zero when SI meets or exceeds the target.
- [Shippable Inventory](shippable_inventory.md) - Projected available inventory at the end of a planning week, net of all planned demand and supply events; the primary output of the Logility supply plan.
