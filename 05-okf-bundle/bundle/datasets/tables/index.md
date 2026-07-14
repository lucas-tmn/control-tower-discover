---
type: Index
title: Tables
description: Details about specific Database tables stored in Ashley Enterprise Data
  warehouse (EDW) or the Microsoft Fabric environment
timestamp: 2026-07-07
---

## Tables

### Dataset

- [Current Forecast](FactCurrentForecast.md) - Latest forecast snapshot published to supply planning at the weekly item-warehouse grain, capturing resultant (model-driven, post-override), promotional lift, and total forecast quantities normalized from monthly source data.
- [Current Forecast Snapshot Daily](CurFcstSnapshotDaily.md) - Daily snapshot of the monthly forecast extracted from the SupplyPlanning databases inside Logility.
- [Customer Master](DimCustomer.md) - Customer dimensions at account and ship-to level.
- [Demand Forecast](demand_forecast.md) - Logility-generated demand forecast by item and planning period, loaded into the data warehouse after each planning run.
- [Fiscal Calendar](DimDate.md) - Fiscal calendar dimension providing date, week, month, quarter, half, and year attributes for grouping and indexing supply chain facts.
- [Inventory On Hand](inventory_onhand.md) - Current on-hand inventory quantities by item and warehouse location, sourced from HighJump WMS and synchronized to the ERP and data warehouse.
- [Product Master](DimProduct.md) - Central product dimensions consolidating item master attributes, ETL-computed lifecycle classification, and planning fields at the item SKU grain.
- [Purchase Orders](purchase_orders.md) - Open and historical purchase order lines from the ERP, representing the inbound supply pipeline from suppliers.
- [Sales Orders](sales_orders.md) - Customer sales order lines from the ERP representing actual demand — the primary signal for comparing against the demand forecast.
- [Supply Plan Detail](FactSupplyPlanDetail.md) - Current day's Logility supply plan showing a 39-week forward projection of Shippable Inventory at the item-warehouse-week grain, net of all planned demand, supply receipts, and transfer activity.
- [Vendor Master](DimVendor.md) - Central vendor master dimensions.
- [Warehouse Master](DimWarehouse.md) - Central warehouse master dimensions.
- [Working Forecast](FactWorkingForecast.md) - Latest Working Forecast as extracted from the Logility Demand Planning database at the item-warehouse-customer group-week grain; the pre-consensus demand signal actively being refined before synchronization to supply planning.
