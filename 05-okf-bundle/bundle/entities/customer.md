---
type: Entity
title: Customer
description: A customer entity representing accounts and locations in the supply chain, with canonical attributes used for demand forecasting, order fulfillment, and customer segmentation.
tags: [entities, customer, account, ship-to, demand-planning, hierarchy]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimCustomer]"
source_system: ERP
status: agent draft
---

## Definition

A **Customer** is a buying entity in the supply chain, identified at two levels: the account level (consolidated organization) and the ship-to level (individual receiving location). Customers are the primary demand source and the target of fulfillment operations.

Customer master data originates from the ERP and is exposed through the governed [Customer Master](/datasets/tables/DimCustomer.md) dimension. That dataset is the authoritative source for all customer attributes used in supply chain analysis.

---

## Grain and Uniqueness

The [Customer Master](/datasets/tables/DimCustomer.md) table is keyed on **`AccountAndShipToNumber`**, representing a unique account-ship-to location combination. This grain allows tracking of:

- **Account-level aggregates:** Total customer demand, customer segment reporting, regional analysis
- **Ship-to level detail:** Location-specific demand patterns, multi-location customer dynamics, delivery-specific attributes (address, region, district)

An account may have multiple ship-to locations (e.g., a retailer with regional distribution centers); a single row represents demand and fulfillment flows to one specific location.

---

## Account vs. Ship-To Distinction

| Dimension | Identifier | Meaning | Usage |
| --- | --- | --- | --- |
| **Account** | `AccountNumber` | Parent organization or buying entity | Consolidate demand across all locations; apply business-level rules and customer contracts |
| **Ship-To** | `ShipToNumber` | Individual receiving location | Analyze location-specific demand patterns; forecast and plan at the location level; identify regional demand drivers |

When analyzing demand or planning inventory, use the ship-to grain to capture location-specific dynamics, but reference `AccountNumber` when applying account-level rules or hierarchies.

---

## Key Attributes

| Concept | DimCustomer Column | Description |
| --- | --- | --- |
| Account identifier | `AccountNumber` | Primary account-level identifier; used as FK in fact tables |
| Account name | `AccountName` | Account name for display and filtering |
| Ship-to identifier | `ShipToNumber` | Location-specific identifier; combined with AccountNumber to form the unique key |
| Ship-to name | `ShipToName` | Location name or label (e.g., distribution center name, regional office) |
| Account-ship-to key | `AccountAndShipToNumber` | Composite key for unique row identification |
| Customer group | `CustomerGroup` | Customer grouping classification (e.g., AFICONS, distributor class); critical for demand segmentation |
| Customer segment | `CustomerSegment` | Market or channel segment (e.g., wholesale, retail, direct); used for hierarchical reporting |
| Business type | `ReportingBusinessType` / `BusinessTypeCode` | Standardized business type for regulatory and revenue reporting |
| Address | `Address1`–`Address5` | Shipping address detail (line by line) |
| City | `City` | City name for the ship-to location |
| State | `State` | State abbreviation (US standard) |
| Zip code | `ZipCode` | Postal code |
| Country | `Country` | Country name or code for international locations |
| Region | `Region` | Regional grouping for consolidation and analysis (e.g., North, South, East, West) |
| District | `District` | District or sales territory assignment for alignment with sales organization |

---

## Customer Segmentation

Customers are segmented along multiple dimensions for demand analysis and planning:

- **Customer Group** (`CustomerGroup`) — Primary grouping for demand pattern recognition and forecast model selection (e.g., AFICONS vs. regional distributors have distinctly different demand patterns)
- **Customer Segment** (`CustomerSegment`) — Channel or market segment that governs fulfillment and supply chain strategy (e.g., wholesale orders follow predictable patterns; retail orders may be more volatile)
- **Business Type** (`ReportingBusinessType`) — Regulatory classification for revenue and compliance reporting

Apply these dimensions consistently when segmenting forecast models, setting safety stock policy, or analyzing demand volatility.

---

## Regional and Territorial Organization

The `Region` and `District` fields align customer locations with the sales organization structure:

- **Region** — Broad geographic grouping for consolidated reporting and regional demand analysis
- **District** — Sales territory assignment; use to align supply planning with sales management hierarchy

When analyzing demand or planning supply, respect the sales territory boundaries encoded in `District` unless a specific cross-territory analysis is required by the process.

---

## Related

- [Customer Master](/datasets/tables/DimCustomer.md) — Authoritative dataset for all customer attributes and hierarchies
- [Demand Forecast](/datasets/tables/demand_forecast.md) — Demand signals by customer group and planning period
- [Sales Orders](/datasets/tables/sales_orders.md) — Actual customer orders and fulfillment history
- [New Product Performance Review](/playbooks/new_product_review.md) — Customer segmentation used in product performance analysis
