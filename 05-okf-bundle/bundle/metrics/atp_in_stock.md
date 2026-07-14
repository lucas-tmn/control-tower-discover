---
type: Metric
title: ATP In Stock
description: Percentage of ATP stock observations where available-to-promise quantity is greater than zero for selected item-warehouse-week combinations.
tags: [atp, in-stock, inventory, availability, fulfillment, customer-service, kpi]
timestamp: 2026-07-07
status: draft
---

## Definition

ATP In Stock measures how often a selected item-warehouse-week had positive available-to-promise quantity in the ATP source. It is an event-rate metric: each ATP observation contributes one stock event, and observations where `ATPQty > 0` contribute one in-stock event.

Use this metric to understand whether customers are likely seeing available ATP for active, forecasted items at customer-invoicing warehouses.

## Calculation

```text
ATPInStockRate = SUM(InStockEvent) / SUM(StockEvent)
```

Expressed as a percentage:

```text
ATPInStockRate (%) = (SUM(InStockEvent) / SUM(StockEvent)) x 100
```

Where:

- `InStockEvent` = count of underlying ATP observations where `ATPQty > 0`
- `StockEvent` = count of underlying ATP observations in scope

Both fields are produced by [ATP In Stock Query](/datasets/queries/atp_in_stock_query.md).

Do not compute this metric when `SUM(StockEvent) = 0`; there are no ATP observations in scope for the selected grain.

## Recommended Grain

The query output is grouped by:

- `ItemSKU`
- `WarehouseID`
- `WeekEnding`
- `RecentLaunchFlag`
- `InitialInvoiceDate`

For reporting, aggregate to the level being reviewed before calculating the percentage. Examples:

- Item x warehouse x week
- Warehouse x week
- `RecentLaunchFlag` x week
- Total selected portfolio x week

Use a ratio of sums, not an average of row-level percentages, when rolling up across items, warehouses, or weeks.

## Scope Rules

The supporting query intentionally limits the metric to rows that are meaningful for ATP availability analysis:

- `ATPWeek = 'Week2'`, matching a typical customer-request lead time of roughly seven days
- prior completed fiscal weeks only, using `FiscalWeekIndicator BETWEEN -8 AND -1`
- customer-invoicing warehouses `1`, `15`, `17`, `28`, `5`, `335`, and `ECR`
- item-warehouse combinations with positive resultant forecast in the last 13 months
- Logility item statuses excluding `D`, `I`, `R`, `T`, and `N`

Changing these filters changes the business meaning of the metric and should be called out when comparing reports.

## Interpretation

| Rate | Signal |
| --- | --- |
| 100% | Every ATP observation in scope had positive ATP quantity. |
| 0% < rate < 100% | Intermittent availability; customers may see ATP on some days but not consistently across the reviewed week. |
| 0% | No ATP observation in scope had positive ATP quantity; this is a strong availability risk for the selected item, warehouse, and week. |

Use `AvgATPQty` from [ATP In Stock Query](/datasets/queries/atp_in_stock_query.md) as supporting context. A high in-stock rate with low average ATP quantity can still indicate shallow availability, while a low in-stock rate with high average ATP quantity can indicate uneven ATP timing during the week.

## Relationship to Stockout Analysis

ATP In Stock is customer-facing availability evidence. It complements, but does not replace, supply-plan metrics such as [Shippable Inventory](/metrics/shippable_inventory.md), [Safety Stock Gap](/metrics/safety_stock_gap.md), and [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md).

- ATP In Stock answers whether ATP showed positive available quantity during recent completed weeks.
- Shippable Inventory and related supply-plan metrics answer whether the planning model projects enough future inventory to cover demand and safety stock.

When ATP In Stock is low for active items with recent forecast demand, use [Stockout Escalation](/playbooks/stockout_escalation.md) or [Supply Plan Review](/playbooks/supply_plan_review.md) to investigate whether the issue is current inventory, inbound supply timing, forecast demand, or item status.

## Related

- [ATP In Stock Query](/datasets/queries/atp_in_stock_query.md)
- [Stockout](/glossary/stockout.md)
- [Shippable Inventory](/metrics/shippable_inventory.md)
- [Safety Stock Gap](/metrics/safety_stock_gap.md)
- [Projected Fulfillment Rate](/metrics/projected_fulfillment_rate.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
