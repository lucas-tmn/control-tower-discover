---
type: Dataset
title: Customer Master
description: Customer dimensions at account and ship-to level.
tags: [entities, customer, demand-planning, ship-to, hierarchy]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimCustomer]"
source_system: ERP
refresh_cadence: daily
data_source: fabric
status: draft
---

## Purpose

Central customer dimension for supply chain planning and demand analysis. Consolidates customer account and ship-to location attributes to enable demand forecasting, order fulfillment analysis, and forecast accuracy reporting. Provides ship-to level detail for multi-location customers to capture location-specific subscription and demand patterns.

Used as the customer entity in:

- Demand forecasting models
- Order fulfillment analysis
- Forecast accuracy reporting
- Demand pattern segmentation

---

## Grain

Each row represents a unique **account and ship-to location combination** (`AccountAndShipToNumber`).

---

## Schema

| Column | Type | Meaning |
| --- | --- | --- |
| `AccountAndShipToNumber` | VARCHAR(20) | Composite key identifying the unique account-ship-to combination for multi-location demand tracking |
| `AccountNumber` | VARCHAR(10) | Account-level identifier; used as foreign key in fact tables |
| `AccountName` | VARCHAR(200) | Customer name / account name for display and filtering |
| `ShipToNumber` | VARCHAR(10) | Ship-to location code identifying the receiving location |
| `ShipToName` | VARCHAR(200) | Ship-to location name or address label |
| `CustomerGroup` | VARCHAR(100) | Customer grouping classification for demand segmentation (e.g., AFICONS, regional distributor class) |
| `CustomerSegment` | VARCHAR(100) | Market or channel segment (e.g., wholesale, retail, direct) for hierarchical reporting |
| `ReportingBusinessType` | VARCHAR(100) | Standardized business type for regulatory and revenue reporting |
| `BusinessTypeCode` | VARCHAR(20) | Code / abbreviation for business type |
| `Address1` | VARCHAR(200) | Primary address line |
| `Address2` | VARCHAR(200) | Secondary address line |
| `Address3` | VARCHAR(200) | Tertiary address line (suite, building) |
| `Address4` | VARCHAR(200) | Quaternary address line |
| `Address5` | VARCHAR(200) | Quinary address line |
| `City` | VARCHAR(100) | City name |
| `State` | VARCHAR(2) | State abbreviation (US standard) |
| `ZipCode` | VARCHAR(10) | Postal code |
| `Country` | VARCHAR(100) | Country name or code |
| `Region` | VARCHAR(100) | Regional grouping for consolidation and analysis |
| `District` | VARCHAR(100) | District or sales territory assignment |

---

## Related

- [Customer](/entities/customer.md) — Canonical customer business object definition
- [Demand Forecast](/datasets/demand_forecast.md) — Demand signals indexed by customer
- [Sales Orders](/datasets/sales_orders.md) — Actual customer order transactions
- [FILL IN: Link to forecast accuracy metric]
