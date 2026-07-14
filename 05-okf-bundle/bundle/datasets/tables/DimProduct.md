---
type: Dataset
title: Product Master
description: Central product dimensions consolidating item master attributes, ETL-computed lifecycle classification, and planning fields at the item SKU grain.
tags: [entities, product, lifecycle, item-master, planning]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimProduct]"
source_system: ERP
refresh_cadence: daily
data_source: fabric
status: draft
---

## Purpose

Central product dimension for supply chain planning. Consolidates item master attributes from the ERP product master as the primary source, unified with planning details from `DimCurrentProductDetails`, vendor data, invoice history, and product knowledge extensions. Resolves divergent calculated columns across legacy semantic models into a governed set of source attributes and ETL-computed classification columns.

All gold fact tables join to `DimProduct`. Used in:

- Demand and inventory planning
- Lifecycle-stage filtering for forecast and planning reports
- Product hierarchy and classification roll-ups
- New product assessment and end-of-life tracking

---

## Grain

Each row represents a unique **item SKU** (`ItemSKU`). Direct-ship-only supplier items are excluded from this table.

---

## Schema

### Identity

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemSKU` | VARCHAR(15) | Primary key; item-level grain identifier used as FK in all gold fact tables |
| `ItemDescription` | VARCHAR(30) | Full item name from product master |
| `ItemSKUDesc` | VARCHAR(48) | ETL-computed: `ItemSKU + ' - ' + ItemDescription`; convenience label for visuals and slicers |
| `ItemCode` | VARCHAR(25) | Secondary item code from source master; distinct from `ItemSKU` |

### Series

| Column | Type | Meaning |
| --- | --- | --- |
| `SeriesNumber` | VARCHAR(5) | Series identifier for grouping related SKUs |
| `SeriesName` | VARCHAR(100) | Human-readable series name |
| `SeriesColor` | VARCHAR(60) | Color attribute at the series level |
| `FrameNumber` | VARCHAR(16) | Frame number attribute |
| `PlanningSeries` | VARCHAR(16) | ETL-computed: alias of `ItemExtSeriesNumber` using Logility naming convention |
| `ItemExtSeriesNumber` | VARCHAR(16) | Extended/external series number from `DimCurrentProductDetails`; supplemental series identifier |
| `ExtSeriesNumber` | VARCHAR(16) | Extended series number from item master |
| `ExtSeriesDescription` | VARCHAR(119) | Description for the extended series number |
| `SeriesDesc` | VARCHAR(108) | ETL-computed: `PlanningSeries + ' - ' + SeriesName`; replaces model-local Series Desc calculated columns |

### Classification

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemClassCode` | CHAR(4) | Item classification code |
| `ItemClassName` | VARCHAR(25) | Item classification description |
| `CollectiveClass` | VARCHAR(100) | Collective class description |
| `CollectiveClassGroup` | VARCHAR(100) | ETL-computed: custom grouping consolidating collective classes and item classes; applies special rules for components and kits |
| `ProductLine` | VARCHAR(25) | Product line grouping |
| `GeneralDescription` | VARCHAR(10) | General description label from GENDESC table |
| `ItemGrouping` | VARCHAR(35) | Planning-level item grouping |
| `MerchandisingCategory` | SMALLINT | Merchandising category for retail/display purposes |
| `BusinessUnit` | VARCHAR(100) | Business unit from `DimCurrentProductDetails`; may be NULL for items not in that source |
| `Colors` | VARCHAR(23) | Color attribute at the item level |
| `PricePoint` | INT | Price point tier code |
| `ItemPricePointRating` | VARCHAR(6) | Rating within price point tier |

### Finance / Sales Hierarchy

| Column | Type | Meaning |
| --- | --- | --- |
| `AFIFinanceDivision` | VARCHAR(30) | Finance division |
| `AFISalesDivision` | VARCHAR(25) | Sales division description |
| `AFISalesCategory` | VARCHAR(25) | Sales category description |
| `AlternateDivision` | VARCHAR(25) | ETL-computed: strips the `"Signature "` prefix from `AFISalesDivision` for Signature-branded divisions; used where the prefix creates grouping noise |

### Geography / Sourcing

| Column | Type | Meaning |
| --- | --- | --- |
| `ImportDomesticCode` | CHAR(1) | Import (I) or Domestic (D) sourcing indicator |
| `CountryOfOrigin` | VARCHAR(30) | Country of manufacture |
| `ResponsibleOffice` | VARCHAR(10) | Office responsible for sourcing and planning the item |
| `ResponsibleOfficeName` | VARCHAR(10) | Description of the responsible office |
| `CEXCode` | CHAR(3) | Default warehouse that the item balance record is created at |
| `MakeBuyCode` | VARCHAR(10) | Make (manufactured internally) or Buy (purchased); pending ETL implementation |

### Pricing / Physical Attributes

| Column | Type | Meaning |
| --- | --- | --- |
| `FOBArcPrice` | DECIMAL(15,3) | FOB unit price in USD indexed to Arcadia |
| `Cubes` | DECIMAL(5,2) | Item cube in cubic feet |
| `QtyInBox` | DECIMAL(4,0) | Units per carton; used in `MarketableConversionFactor` |
| `UOM` | CHAR(2) | Unit of measure |
| `ContainerVolume` | DECIMAL(10,7) | ETL-computed: `Cubes / 2400`; normalized container volume for purchase order estimation. Used in capacity planning: For a set of PO line items, sum of [Units] *[ContainerVolume] helps answer, "How many containers is the vendor shipping this week? How many containers is the warehouse receiving this week?" |
| `CurrentUnitCost` | DECIMAL(19,3) | Average/list unit cost |

### Vendor

| Column | Type | Meaning |
| --- | --- | --- |
| `PrimaryVendor` | VARCHAR(8) | Primary vendor number |
| `PrimaryVendorName` | VARCHAR(23) | Primary vendor name |

### Structure / Planning

| Column | Type | Meaning |
| --- | --- | --- |
| `MainPieceItem` | VARCHAR(5) | Item number of the main piece in a set maintained by sales teams |
| `ItemForecastPlannerID` | VARCHAR(40) | Forecast planner ID; resolved via COALESCE priority from `Item_ENV` and `NonPkItems` |

### Status / Lifecycle

| Column | Type | Meaning |
| --- | --- | --- |
| `AFIItemStatus` | CHAR(1) | Source lifecycle status code: N = New, D = Discontinued; empty string normalized to C (Current) by ETL; primary input to `LifecycleStage` |
| `CurrentStatus` | CHAR(1) | Current item status from `DimCurrentProductDetails` |
| `FutureStatus` | VARCHAR(40) | Planned future status: F = Phase-out, P = Planned drop; input to `LifecycleStage` and `PlanDropDecisionDate` |
| `ManufacturingStatus` | VARCHAR(25) | Manufacturing status description |
| `ManufacturingStatusChangeDate` | DATE | Date manufacturing status last changed |
| `DiscontinuedDate` | DATE | Date item was discontinued |
| `HoldBuyCode` | VARCHAR(40) | Purchasing hold code; resolved via COALESCE from `Item_ENV` and `NonPkItems` |

### Market / Introduction Dates

| Column | Type | Meaning |
| --- | --- | --- |
| `MarketIntroducedAt` | VARCHAR(30) | Date item was introduced to market; kit item NULLs are corrected to the parent finished-good's date by ETL |
| `MarketBeginDate` | DATE | Market availability begin date |
| `MarketEndDate` | DATE | Market availability end date; NULL while the item is active |
| `InitialInvoiceDate` | DATE | ETL-computed: date of first customer invoice from sales history; drives `Recent Launch` classification in `LifecycleStage` |
| `InitialInvoiceQty` | DECIMAL(38,0) | Quantity on the first invoice |

### Product Flags

| Column | Type | Meaning |
| --- | --- | --- |
| `SellableItemFlag` | CHAR(1) | Indicates item is directly sellable to end customers |
| `ExpressShipFlag` | CHAR(1) | Express shipping eligibility flag |
| `HSExclusiveFlag` | BIT | HomeStore exclusive product flag |
| `HSCoreProductFlag` | BIT | HomeStore core product flag |
| `HSProprietaryProductFlag` | BIT | HomeStore proprietary product flag |
| `ConsumerChoiceFlag` | VARCHAR(5) | Consumer choice program flag |
| `CommodityItem` | BIT | Commodity item classification |
| `Showroom` | VARCHAR(87) | Showroom display attribute |

### Image

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemImage` | VARCHAR(50) | Item image identifier |
| `ImageURL` | VARCHAR(87) | ETL-computed: full image URL; NULL when `ItemImage` is NULL or empty |

### ETL-Computed — Lifecycle & Planning

| Column | Type | Meaning |
| --- | --- | --- |
| `LifecycleStage` | VARCHAR(20) | ETL-computed: `Pre-Invoicing` \| `Recent Launch` \| `Current` \| `End of Life`; single canonical lifecycle stage replacing divergent model-local calculated columns |
| `LifecycleStageSortOrder` | INT | ETL-computed: numeric sort order for `LifecycleStage` (1–4); enables non-alphabetic sort in visuals |
| `DiscontinuationHorizon` | VARCHAR(5) | ETL-computed: `12M` \| `18M` \| `24M` \| NULL; buckets end-of-life items by expected drop timeline; pending implementation |
| `PlanDropDecisionDate` | DATE | ETL-computed: date `FutureStatus` first changed to F or P; pending implementation |
| `PartFlag` | VARCHAR(4) | ETL-computed: `PART` \| `ITEM`; identifies component parts for filtering from customer-facing demand and inventory reports |
| `KitFlag` | VARCHAR(3) | ETL-computed: kit/material type — `Bedding Kit` \| `UPH Kit` \| `Swatch` \| `HIDES` \| `VINYL`; replaces model-local kit-type variants; pending implementation |
| `MarketableConversionFactor` | DECIMAL(10,6) | ETL-computed: `1.0` for standard marketable SKUs; `1/QtyInBox` for GDC-700 component items; enables demand aggregation at the parent SKU level; pending implementation |
| `MarketableItemSKU` | VARCHAR(15) | ETL-computed: self for marketable items; parent finished-good `ItemSKU` for GDC-700 components; used in GROUPBY clauses to roll component demand up to the sellable SKU; pending implementation |

---

## Related

- [FILL IN: Link to NewProductReview process]
- [FILL IN: Link to ForecastRevision process]
- [FILL IN: Link to Supplier entity]
- [FILL IN: Link to LifecycleStage glossary term]
