---
type: Dataset
title: Sales Orders
description: Customer sales order lines from the ERP representing actual demand — the primary signal for comparing against the demand forecast.
resource: "[database].[schema].sales_orders"
tags: [sales, demand, fulfillment, customer-orders, erp]
timestamp: 2026-06-26T00:00:00Z
source_system: ERP
refresh_cadence: daily
data_source: azure-sql
status: agent draft
---

## Overview

This dataset contains customer sales order lines from the ERP system. It is the primary source of **actual demand** used to evaluate forecast accuracy, assess product performance, and identify fulfillment gaps.

Use `shipped_qty` (not `ordered_qty`) when measuring realized demand — it reflects what was actually fulfilled and consumed inventory.

## Grain

One row per **order line** (order number + line number).

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `order_id` | VARCHAR | Unique sales order identifier |
| `order_line` | INTEGER | Line number within the order |
| `item_id` | VARCHAR | Foreign key to [Product Master](/datasets/tables/DimProduct.md) (`ItemSKU`) |
| `customer_id` | VARCHAR | Customer identifier |
| `order_date` | DATE | Date the order was placed |
| `requested_ship_date` | DATE | Customer-requested ship date |
| `actual_ship_date` | DATE | Date the order was actually shipped |
| `ordered_qty` | DECIMAL | Quantity ordered by the customer |
| `shipped_qty` | DECIMAL | Quantity actually shipped (fulfilled demand) |
| `open_qty` | DECIMAL | Quantity remaining to be shipped |
| `order_status` | VARCHAR | Status: Open, Shipped, Cancelled, etc. |
| `uom` | VARCHAR | Unit of measure |

> **Note**: Column names above are illustrative. Confirm against the actual warehouse schema and update this document before setting `status: active`.

## Key Joins

- Join to [Product Master](/datasets/tables/DimProduct.md) on `item_id` = `ItemSKU` for product attributes.
- Join to [demand_forecast](/datasets/tables/demand_forecast.md) on `item_id` + period alignment for forecast vs. actual comparison.

## Known Considerations

- Filter by `order_status` correctly: cancelled orders must be excluded from demand actuals.
- `ordered_qty` vs. `shipped_qty` distinction is critical: use `shipped_qty` for demand actuals, `ordered_qty` for backlog and unfulfilled demand analysis.
- [FILL IN: any known data quality issues specific to your ERP, e.g., returns handling, EDI order timing, etc.]
