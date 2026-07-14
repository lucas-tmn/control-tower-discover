---
type: Dataset
title: Demand Forecast
description: Logility-generated demand forecast by item and planning period, loaded into the data warehouse after each planning run.
resource: "[database].[schema].[demand_forecast]"
tags: [demand-planning, forecast, logility, supply-chain]
timestamp: 2026-06-29
source_system: Logility
refresh_cadence: weekly
data_source: azure-sql
status: deprecated
---

> **Deprecated.** This document was a placeholder for the demand forecast concept. It has been superseded by [Current Forecast](/datasets/tables/FactCurrentForecast.md), which documents the actual Fabric implementation (`FactCurrentForecast`) with confirmed schema, grain, and source system details.

## Overview

This dataset contains the output of Logility's demand planning engine. It represents the planned demand signal used by supply planning, procurement, and inventory management processes.

Logility runs on a [FILL IN: weekly/daily] cadence and produces forecasts for a [FILL IN: N-week/month] planning horizon. When a planned purchase order or manufacturing order is firmed in Logility, it is pushed to the ERP and the forecast is updated accordingly.

## Grain

One row per **item × planning period**.

- Planning period is [FILL IN: weekly / monthly].
- Multiple forecast versions may exist for the same item × period. Always use the most recent `forecast_version` unless explicitly comparing versions.

## Schema

| Column | Type | Description |
| --- | --- | --- |
| `item_id` | VARCHAR | Foreign key to [Product Master](/datasets/tables/DimProduct.md) (`ItemSKU`) |
| `period_start_date` | DATE | First date of the planning period |
| `forecast_qty` | DECIMAL | Forecasted demand quantity in planning UOM |
| `forecast_version` | VARCHAR | Version identifier for the planning run |
| `version_date` | DATE | Date the forecast version was generated |
| `uom` | VARCHAR | Unit of measure for forecast_qty |

> **Note**: Column names above are illustrative. Confirm against the actual warehouse schema and update this document before setting `status: active`.

## Key Joins

- Join to [Product Master](/datasets/tables/DimProduct.md) on `item_id` = `ItemSKU` for product attributes and planning parameters.
- Join to [sales_orders](/datasets/tables/sales_orders.md) on `item_id` + period alignment for forecast vs. actual comparison.

## Known Considerations

- Forecast for new products in early launch may be based on analogous item history or management input, not statistical modeling. Treat accuracy expectations accordingly.
- [FILL IN: any known data quality issues, e.g., lag between Logility run and DW load, handling of discontinued items, etc.]
