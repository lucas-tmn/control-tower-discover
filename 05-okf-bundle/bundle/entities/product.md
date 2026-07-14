---
type: Entity
title: Product
description: A product or SKU in the supply chain, with canonical attributes, ETL-governed lifecycle classification, and planning fields used consistently across all supply chain analyses.
tags: [entities, product, sku, item-master, lifecycle]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimProduct]"
source_system: ERP
status: agent draft
---

## Definition

A **Product** (also referred to as an Item or SKU) is the fundamental planning unit in the supply chain. Each product has a unique `ItemSKU` and carries attributes that govern how it is planned, procured, stored, and sold.

Product master data originates from the ERP and is exposed through the governed [Product Master](/datasets/tables/DimProduct.md) dimension. That dataset is the authoritative source for all product attributes used in supply chain analysis.

---

## Key Attributes

| Concept | DimProduct Column | Description |
| --- | --- | --- |
| Identifier | `ItemSKU` | Primary key; unique item-level grain identifier used as FK across all gold fact tables |
| Display label | `ItemSKUDesc` | ETL-computed: `ItemSKU + ' - ' + ItemDescription`; use in visuals and slicers |
| Item description | `ItemDescription` | Full item name from product master |
| Lifecycle stage | `LifecycleStage` | ETL-computed canonical stage: Pre-Invoicing, Recent Launch, Current, End of Life |
| Item class | `ItemClassCode` / `ItemClassName` | Product classification code and description |
| Collective class | `CollectiveClass` / `CollectiveClassGroup` | Category grouping; `CollectiveClassGroup` is the ETL-governed version for reporting |
| Product line | `ProductLine` | Product line grouping |
| Planning series | `PlanningSeries` | Series identifier using Logility naming convention |
| Planner | `ItemForecastPlannerID` | Assigned forecast planner |
| Primary vendor | `PrimaryVendor` / `PrimaryVendorName` | Default procurement source |
| Sourcing origin | `ImportDomesticCode` / `CountryOfOrigin` | Import vs. domestic indicator and country of manufacture |
| Unit cost | `CurrentUnitCost` | Average/list unit cost |
| Market begin | `MarketBeginDate` | Market availability start date |
| Market end | `MarketEndDate` | Market availability end date; NULL while item is active |
| First invoice date | `InitialInvoiceDate` | Date of first customer invoice; drives Recent Launch classification |
| Discontinued date | `DiscontinuedDate` | Date item was discontinued |
| Part or item | `PartFlag` | ETL-computed: PART or ITEM; use to exclude component SKUs from customer-facing reports |
| Kit type | `KitFlag` | ETL-computed: Bedding Kit, UPH Kit, Swatch, HIDES, VINYL, or empty for non-kit items |

---

## Product Lifecycle Stages

Lifecycle stage is governed by the ETL-computed `LifecycleStage` column in [DimProduct](/datasets/tables/DimProduct.md). Do not derive it independently — use this column as the single canonical source.

| Stage | Meaning | Primary Conditions |
| --- | --- | --- |
| Pre-Invoicing | Item created, not yet invoiced to any customer | `AFIItemStatus = 'N'` |
| Recent Launch | First customer invoice within the past 9 months | `InitialInvoiceDate >= today − 9 months` |
| Current | Actively sold item with established history | Default (none of the above or below conditions met) |
| End of Life | Planned for drop or already discontinued | `FutureStatus IN (F, P, L, E)` OR `AFIItemStatus IN (D, R)` |

> Priority order: End of Life (via FutureStatus) → Pre-Invoicing → Recent Launch → End of Life (via AFIItemStatus) → Current. FutureStatus takes precedence over AFIItemStatus.

`LifecycleStageSortOrder` (1–4) provides a numeric sort order for visuals where alphabetic ordering would be misleading.

---

## New Product Classification

A product enters the **Recent Launch** stage when its `InitialInvoiceDate` falls within the past 9 months. This is the organization's defined window for newly introduced products.

New products require special handling in planning and analysis:

- Forecast accuracy is expected to be lower due to limited demand history.
- Safety stock targets may be elevated to buffer against launch-period demand uncertainty.
- Performance should be reviewed more frequently than established products.

See [New Product Performance Review](/playbooks/new_product_review.md) for the full analysis process.

---

## Component and Kit Classification

Not all SKUs represent sellable finished goods. Two ETL-computed flags identify special item types:

- **`PartFlag = 'PART'`** — Component or sub-assembly SKU; exclude from customer-facing demand and inventory reports unless explicitly analyzing component-level demand.
- **`KitFlag`** — Classifies kit and material type (Bedding Kit, UPH Kit, Swatch, etc.); use when unit-count measures must distinguish kit items from standard items.

For demand measures that must aggregate component demand to the parent finished-good level, use `MarketableItemSKU` and `MarketableConversionFactor` (pending ETL implementation).

---

## Related

- [Product Master](/datasets/tables/DimProduct.md) — Authoritative dataset for all product attributes and lifecycle classification
- [Recently Introduced](/glossary/recently_introduced.md) — New product window definition
- [New Product Performance Review](/playbooks/new_product_review.md) — Analysis playbook for new products
