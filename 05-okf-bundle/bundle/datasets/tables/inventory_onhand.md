---
type: Dataset
title: Inventory On Hand
description: Current on-hand inventory quantities by item and warehouse location, sourced from HighJump WMS and synchronized to the ERP and data warehouse.
resource: "[database].[schema].inventory_onhand"
tags: [inventory, warehouse, highjump, erp, on-hand]
timestamp: 2026-06-26T00:00:00Z
source_system: HighJump
refresh_cadence: daily
data_source: azure-sql
status: agent draft
---

## Overview

This dataset reflects the current physical inventory position. It is the primary source for calculating [coverage_days](/metrics/coverage_days.md) and [days_of_supply](/metrics/days_of_supply.md) and for detecting stockout risk.

HighJump (WMS) is the system of record for inventory. Data flows from HighJump to the ERP and from the ERP to the data warehouse on a [FILL IN: daily/real-time] basis.

## Grain

One row per **item × warehouse × location** (or item × warehouse if location-level detail is not available in the DW).

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `item_id` | VARCHAR | Foreign key to [Product Master](/datasets/tables/DimProduct.md) (`ItemSKU`) |
| `warehouse_id` | VARCHAR | Warehouse identifier |
| `location_id` | VARCHAR | Location within the warehouse (may be null if aggregated) |
| `qty_on_hand` | DECIMAL | Physical quantity currently on hand |
| `qty_allocated` | DECIMAL | Quantity reserved/allocated to open orders |
| `qty_available` | DECIMAL | qty_on_hand minus qty_allocated |
| `as_of_date` | DATE | Snapshot date of this record |
| `uom` | VARCHAR | Unit of measure |

> **Note**: Column names above are illustrative. Confirm against the actual warehouse schema and update this document before setting `status: active`.

## Key Joins

- Join to [Product Master](/datasets/tables/DimProduct.md) on `item_id` = `ItemSKU` for product attributes ([FILL IN: lead time and safety stock columns not yet in DimProduct]).
- Join to [purchase_orders](/datasets/tables/purchase_orders.md) on `item_id` to compute total supply pipeline for [days_of_supply](/metrics/days_of_supply.md).

## Known Considerations

- Use `qty_available` (not `qty_on_hand`) for stockout risk calculations — allocated inventory is not available to fill new demand.
- Inventory snapshot timing: records reflect the warehouse state as of `as_of_date`. Intraday movements are not captured.
- [FILL IN: handling of multi-warehouse scenarios, transit inventory, consignment, etc.]
