---
type: Dataset
title: Purchase Orders
description: Open and historical purchase order lines from the ERP, representing the inbound supply pipeline from suppliers.
resource: "[database].[schema].purchase_orders"
tags: [procurement, purchase-orders, erp, supply, inbound]
timestamp: 2026-06-26T00:00:00Z
source_system: ERP
refresh_cadence: daily
data_source: azure-sql
status: agent draft
---

## Overview

This dataset contains purchase order lines created in the ERP. It is the primary source for the open supply pipeline — what inventory is coming in and when.

Open POs feed the [days_of_supply](/metrics/days_of_supply.md) calculation and are critical for projecting stockout recovery dates.

Planned POs from Logility become firm ERP purchase orders when released by a planner. The `source` field (or equivalent) distinguishes Logility-originated POs from manually created ones.

## Grain

One row per **PO line** (PO number + line number).

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `po_number` | VARCHAR | Purchase order number |
| `po_line` | INTEGER | Line number within the PO |
| `vendor_id` | VARCHAR | Supplier identifier |
| `item_id` | VARCHAR | Foreign key to [Product Master](/datasets/tables/DimProduct.md) (`ItemSKU`) |
| `ordered_qty` | DECIMAL | Quantity ordered from the supplier |
| `received_qty` | DECIMAL | Quantity received to date |
| `open_qty` | DECIMAL | ordered_qty minus received_qty |
| `expected_receipt_date` | DATE | Supplier-committed or system-calculated receipt date |
| `actual_receipt_date` | DATE | Actual date received (null if not yet received) |
| `po_status` | VARCHAR | Status: Open, Partial, Closed, Cancelled |
| `uom` | VARCHAR | Unit of measure |

> **Note**: Column names above are illustrative. Confirm against the actual warehouse schema and update this document before setting `status: active`.

## Key Joins

- Join to [Product Master](/datasets/tables/DimProduct.md) on `item_id` = `ItemSKU` for planning context.
- Join to [inventory_onhand](/datasets/tables/inventory_onhand.md) on `item_id` to compute [days_of_supply](/metrics/days_of_supply.md).

## Known Considerations

- Filter to `po_status IN ('Open', 'Partial')` when calculating the open supply pipeline. Closed and cancelled POs must be excluded.
- `expected_receipt_date` may not reflect current supplier lead times if the PO was created long ago. Use with awareness of supplier performance history.
- [FILL IN: any nuances around partial receipts, PO amendments, drop-ship orders, etc.]
