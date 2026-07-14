---
title: DimProduct table documentation
domain: Supply Chain Planning
warehouse: SupplyChain_Gold
schema: <schema>
table_name: DimProduct
last_updated: 2026-06-19
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

Central product dimension for supply chain planning, consolidating item master attributes from `Enterprise_Lakehouse.MasterData_DW.DimItemMaster` (primary source) unified with `SupplyChain_DW.DimCurrentProductDetails`, supplemented by `ItemMaster_AFI.ITMEXT`/`GENDESC` and `MasterData_ProductKnowledge.Item_ENV`/`Wholesale_ProductSourcing.NonPkItems` extensions at the same Item SKU grain. This table resolves 110 drifted calculated columns across 16 legacy semantic models into a governed set of source attributes plus seven ETL-computed classification columns (`LifecycleStage`, `KitFlag`, `DiscontinuationHorizon`, `PlanDropDecisionDate`, `LifecycleSortOrder`, `MarketableConversionFactor`, `MarketableItemSKU`). All 9 gold fact tables join to DimProduct, making it the priority-1 dimension build.

---

## 2. Physical Table Definition

````sql
CREATE TABLE <warehouse>.<schema>.DimProduct (
    -- Identity
    [ItemSKU] VARCHAR(15) NOT NULL,
    [ItemDescription] VARCHAR(30) NOT NULL,
    [ItemSKUDesc] VARCHAR(48) NOT NULL,                   -- ETL-computed
    [ItemCode] VARCHAR(25) NULL,

    -- Series
    [SeriesNumber] VARCHAR(5) NULL,
    [SeriesName] VARCHAR(100) NULL,
    [SeriesColor] VARCHAR(60) NULL,
    [PlanningSeries] VARCHAR(16) NULL,                    -- ETL-computed
    [ItemExtSeriesNumber] VARCHAR(16) NULL,
    [ExtSeriesNumber] VARCHAR(16) NULL,
    [SeriesDesc] VARCHAR(108) NULL,                       -- ETL-computed
    [FrameNumber] VARCHAR(16) NULL,

    -- Classification
    [ItemClassCode] CHAR(4) NULL,
    [ItemClassName] VARCHAR(25) NULL,
    [CollectiveClass] VARCHAR(100) NULL,
    [CollectiveClassGroup] VARCHAR(100) NULL,             -- ETL-computed
    [ProductLine] VARCHAR(25) NULL,
    [GeneralDescription] VARCHAR(10) NULL,
    [ItemGrouping] VARCHAR(35) NULL,
    [Colors] VARCHAR(23) NULL,

    -- Style
    [PricePoint] INT NULL,
    [ItemPricePointRating] VARCHAR(6) NULL,

    -- Finance / Sales Hierarchy
    [AFIFinanceDivision] VARCHAR(30) NULL,
    [AFISalesDivision] VARCHAR(25) NULL,
    [AFISalesCategory] VARCHAR(25) NULL,
    [AlternateDivision] VARCHAR(25) NULL,                 -- ETL-computed

    -- Geography / Sourcing
    [ImportDomesticCode] CHAR(1) NULL,
    [CountryOfOrigin] VARCHAR(30) NULL,
    [ResponsibleOffice] VARCHAR(10) NULL,
    [ResponsibleOfficeName] VARCHAR(25) NULL,
    [CEXCode] CHAR(3) NULL,
    [MakeBuyCode] VARCHAR(10) NULL,                       -- ETL-computed (pending implementation)

    -- Pricing / Physical Attributes
    [FOBArcPrice] DECIMAL(15,3) NULL,
    [Cubes] DECIMAL(5,2) NULL,
    [QtyInBox] DECIMAL(4,0) NULL,
    [UOM] CHAR(2) NULL,
    [ContainerVolume] DECIMAL(10,7) NULL,                -- ETL-computed
    [CurrentUnitCost] DECIMAL(19,3) NULL,

    -- Vendor
    [PrimaryVendor] CHAR(8) NULL,
    [PrimaryVendorName] VARCHAR(23) NULL,

    -- Structure / Planning
    [MainPieceItem] VARCHAR(5) NULL,
    [ItemForecastPlannerID] VARCHAR(40) NULL,

    -- Status / Lifecycle (source attributes)
    [AFIItemStatus] CHAR(1) NULL,
    [CurrentStatus] CHAR(1) NULL,
    [FutureStatus] VARCHAR(40) NULL,
    [ManufacturingStatus] VARCHAR(25) NULL,
    [ManufacturingStatusChangeDate] DATE NULL,
    [DiscontinuedDate] DATE NULL,
    [HoldBuyCode] VARCHAR(40) NULL,

    -- Market / Introduction Dates
    [MarketIntroducedAt] VARCHAR(30) NULL,
    [MarketBeginDate] DATE NULL,
    [MarketEndDate] DATE NULL,
    [InitialInvoiceDate] DATE NULL,                       -- ETL-computed
    [InitialInvoiceQty] DECIMAL(38,0) NULL,

    -- Product Flags
    [SellableItemFlag] CHAR(1) NULL,
    [ExpressShipFlag] CHAR(1) NULL,
    [HSExclusiveFlag] BIT NULL,
    [HSCoreProductFlag] BIT NULL,
    [HSProprietaryProductFlag] BIT NULL,
    [ConsumerChoiceFlag] VARCHAR(5) NULL,
    [CommodityItem] BIT NULL,
    [Showroom] VARCHAR(87) NULL,

    -- Image
    [ItemImage] VARCHAR(50) NULL,
    [ImageURL] VARCHAR(87) NULL,

    -- ETL-Computed (Governed)
    [LifecycleStage] VARCHAR(20) NOT NULL,               -- ETL-computed
    [LifecycleSortOrder] INT NOT NULL,                   -- ETL-computed
    [DiscontinuationHorizon] VARCHAR(5) NULL,            -- ETL-computed (pending implementation)
    [PlanDropDecisionDate] DATE NULL,                    -- ETL-computed (pending implementation)
    [PartFlag] VARCHAR(4) NOT NULL,                      -- ETL-computed
    [KitFlag] VARCHAR(3) NOT NULL,                       -- ETL-computed (pending implementation)
    [MarketableConversionFactor] DECIMAL(10,6) NOT NULL, -- ETL-computed (pending implementation)
    [MarketableItemSKU] VARCHAR(15) NOT NULL             -- ETL-computed (pending implementation)
);
````

### Add the primary key

```sql
ALTER TABLE <schema>.DimProduct
ADD CONSTRAINT PK_DimProduct
PRIMARY KEY NONCLUSTERED ([ItemSKU])
NOT ENFORCED;
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| `ItemSKU` | VARCHAR(15) | Primary key — item-level grain identifier used as FK in all 9 gold fact tables |
| `ItemDescription` | VARCHAR(30) | Full item name from product master |
| `ItemSKUDesc` | VARCHAR(48) | ETL-computed: `RTRIM(ItemSKU) + ' - ' + ItemDescription`; replaces 14 model-local `ItemSKU Desc` calc columns |
| `ItemCode` | VARCHAR(25) | Secondary item code from source master; distinct from ItemSKU |
| `SeriesNumber` | VARCHAR(5) | Series identifier for grouping related SKUs |
| `SeriesName` | VARCHAR(100) | Human-readable series name |
| `SeriesColor` | VARCHAR(60) | Color attribute at the series level |
| `PlanningSeries` | VARCHAR(16) | ETL-computed: alias of `ItemExtSeriesNumber` from `DimCurrentProductDetails`; uses Logility naming convention |
| `ItemExtSeriesNumber` | VARCHAR(16) | Extended/external series number from `DimCurrentProductDetails`; supplemental series identifier |
| `ExtSeriesNumber` | VARCHAR(16) | Extended series number from `DimItemMaster` |
| `ExtSeriesDescription` | VARCHAR(119) | Description for the extended series number |
| `SeriesDesc` | VARCHAR(108) | ETL-computed: `RTRIM(ItemExtSeriesNumber) + ' - ' + SeriesDescription`; replaces 13 model-local `Series Desc` calc columns |
| `ItemClassCode` | CHAR(4) | Item classification code |
| `ItemClassName` | VARCHAR(25) | Item classification description |
| `CollectiveClassCode` | CHAR(4) | Collective class code; source attribute — model-local recalculations retired per Phase 3 decision |
| `CollectiveClass` | VARCHAR(100) | Collective class description |
| `ProductLine` | VARCHAR(25) | Product line grouping |
| `GeneralDescriptionCode` | DECIMAL(4,0) | General description code; code 700 identifies non-marketable component SKUs for marketable conversion |
| `GeneralDescription` | VARCHAR(10) | General description label sourced from `ItemMaster_AFI.GENDESC` via `ITMEXT.GDESCD` join |
| `ItemGrouping` | VARCHAR(35) | Planning-level item grouping |
| `MerchandisingCategory` | SMALLINT | Merchandising category for retail/display purposes |
| `BusinessUnit` | VARCHAR(100) | Business unit from `DimCurrentProductDetails`; may be NULL for items not in that source |
| `Colors` | VARCHAR(23) | Color attribute at the item level |
| `ItemStyleCode` | CHAR(3) | Style code |
| `ItemStyleGroup` | VARCHAR(20) | Style group for reporting roll-up |
| `ChildStyleDescription` | VARCHAR(65) | Description of the child style |
| `ParentStyleDescription` | VARCHAR(65) | Description of the parent style |
| `PricePoint` | INT | Price point tier code |
| `ItemPricePointRating` | VARCHAR(6) | Rating within price point tier |
| `AFIFinanceDivision` | VARCHAR(30) | Ashley Furniture Industries finance division |
| `AFISalesDivisionCode` | CHAR(3) | AFI sales division code |
| `AFISalesDivision` | VARCHAR(25) | AFI sales division description |
| `AFISalesCategoryCode` | CHAR(3) | AFI sales category code |
| `AFISalesCategory` | VARCHAR(25) | AFI sales category description |
| `AlternateDivision` | VARCHAR(25) | ETL-computed: strips the `"Signature "` prefix from `AFISalesDivision` for Signature-branded divisions; used in reports where the prefix creates grouping noise |
| `SalesClassCode` | CHAR(2) | Sales classification code |
| `SalesClassDescription` | VARCHAR(25) | Sales classification description |
| `DiscountClassCode` | CHAR(2) | Discount class code |
| `DiscountClassDescription` | VARCHAR(25) | Discount class description |
| `CommissionClassCode` | CHAR(2) | Commission class code |
| `CommissionClassDescription` | VARCHAR(25) | Commission class description |
| `FreightClassCode` | CHAR(2) | Freight class code |
| `FreightClassDescription` | VARCHAR(25) | Freight class description |
| `RetailCategoryCode` | CHAR(3) | Retail category code for retail-channel reporting |
| `RetailCategoryDescription` | VARCHAR(30) | Retail category description |
| `ImportDomesticCode` | CHAR(1) | Import (I) or Domestic (D) sourcing indicator |
| `CountryOfOrigin` | VARCHAR(30) | Country where item is manufactured; source column is `CountryofOrigin` (lowercase 'o') in `DimItemMaster` |
| `ResponsibleOffice` | VARCHAR(10) | Office responsible for sourcing/planning the item |
| `CEXCode` | CHAR(3) | Customer exclusivity code |
| `MakeBuyCode` | VARCHAR(10) | Make (manufactured internally) or Buy (purchased); currently a placeholder (`''`) — pending implementation |
| `FOBArcPrice` | DECIMAL(15,3) | FOB unit price in USD; used by Archetype 9 `[$ Value]` measure |
| `Cubes` | DECIMAL(5,2) | Item cube (cubic feet); used by Archetype 9 `[Cubes]` measure |
| `QtyInBox` | DECIMAL(4,0) | Units per carton; used in `MarketableConversionFactor` pattern |
| `UOM` | CHAR(2) | Unit of measure |
| `ContainerVolume` | DECIMAL(10,7) | ETL-computed: `CAST(Cubes AS DEC(9,5)) / 2400`; normalized container volume for PO estimation |
| `CurrentUnitCost` | DECIMAL(19,3) | Average/list unit cost |
| `PrimaryVendor` | CHAR(8) | Primary vendor number |
| `PrimaryVendorName` | VARCHAR(23) | Primary vendor name; sourced from `Wholesale_Purchasing_AFI.VENNAM.VNAME` via `PrimaryVendor` join |
| `MainPiece` | VARCHAR(40) | Main piece flag or code |
| `MainPieceItem` | VARCHAR(5) | Item number of the main piece in a set |
| `ItemForecastPlannerID` | VARCHAR(40) | Forecast planner ID; sourced from `COALESCE(Item_ENV.ienForecastPlannerID, NonPkItems.npkForecastPlannerID)` |
| `SecondaryPlanner` | VARCHAR(50) | Secondary planner identifier |
| `AFIItemStatus` | CHAR(1) | Source lifecycle status code: N = New, D = Discontinued; empty string `''` normalized to `'C'` by ETL; input to `LifecycleStage` logic |
| `CurrentStatus` | CHAR(1) | Current item status from `DimCurrentProductDetails` |
| `FutureStatus` | VARCHAR(40) | Planned future status (F = Phase-out, P = Planned drop); sourced from `COALESCE(Item_ENV.ienFutureStatus, NonPkItems.npkFutureStatus)`; input to `LifecycleStage` and `PlanDropDecisionDate` |
| `ManufacturingStatus` | VARCHAR(25) | Manufacturing status description |
| `ManufacturingStatusChangeDate` | DATE | Date manufacturing status last changed |
| `CurrentSCPManufacturingStatus` | VARCHAR(7) | SCP-specific manufacturing status; may differ from MarketingStatus |
| `MarketingItemStatus` | CHAR(1) | Marketing status code |
| `MarketingStatusDescription` | VARCHAR(25) | Marketing status description |
| `HoldBuyCode` | VARCHAR(40) | Purchasing hold code; sourced from `COALESCE(Item_ENV.ienHoldBuyCode, NonPkItems.npkHoldBuyCode)` |
| `MarketIntroducedAt` | VARCHAR(30) | Date item was introduced to market; ETL corrects kit item NULLs by assigning parent finished good's date |
| `MarketBeginDate` | DATE | Market availability begin date |
| `MarketEndDate` | DATE | Market availability end date; NULL while item is active |
| `InitialInvoicePeriod` | VARCHAR(7) | YYYYMM period of first customer invoice |
| `InitialInvoiceDate` | DATE | Date of first invoice; derived from `SalesHistory_AFI_Enh.InvoiceDetail`; drives `Recent Launch` classification in `LifecycleStage` |
| `InitialInvoiceQty` | DECIMAL(38,0) | Quantity on first invoice |
| `SellableItemFlag` | CHAR(1) | Indicates item is directly sellable to end customers |
| `ExpressShipFlag` | CHAR(1) | Express shipping eligibility flag |
| `F123ProductFlag` | BIT | F123 program product flag |
| `HSExclusiveFlag` | BIT | HomeStore exclusive product flag |
| `HSCoreProductFlag` | BIT | HomeStore core product flag |
| `HSProprietaryProductFlag` | BIT | HomeStore proprietary product flag |
| `ConsumerChoiceFlag` | VARCHAR(5) | Consumer choice program flag |
| `CommodityItem` | BIT | Commodity item classification |
| `Showroom` | VARCHAR(87) | Showroom display attribute |
| `ItemImage` | VARCHAR(50) | Item image identifier or binary reference |
| `ImageURL` | VARCHAR(87) | ETL-computed: `'http://www.ashleydirect.com/graphics/' + ItemImage`; NULL when `ItemImage` is NULL or empty string |
| `LifecycleStage` | VARCHAR(20) | ETL-computed: `Pre-Invoicing` \| `Recent Launch` \| `Current` \| `End of Life`. Priority order: FutureStatus in (F,P,L,E)→End of Life; AFIItemStatus=N→Pre-Invoicing; InitialInvoiceDate within 9 months→Recent Launch; AFIItemStatus in (D,R)→End of Life; else→Current. Replaces 4+ divergent model-local lifecycle calc columns. |
| `LifecycleSortOrder` | INT | ETL-computed: Pre-Invoicing=1, Recent Launch=2, Current=3, End of Life=4; enables non-alphabetic sort in visuals. **Note:** ETL aliases this as `[LifecycleStageSort]` — confirm target column name with data engineering. |
| `DiscontinuationHorizon` | VARCHAR(5) | ETL-computed: `12M` \| `18M` \| `24M` \| NULL; buckets items by expected drop timeline; pending implementation |
| `PlanDropDecisionDate` | DATE | ETL-computed: date FutureStatus first changed to F or P; pending implementation |
| `PartFlag` | VARCHAR(4) | ETL-computed: `PART` \| `ITEM`; identifies component parts for filtering |
| `KitFlag` | VARCHAR(3) | ETL-computed: kit/material type classification; replaces multiple model-local kit-type variants; pending implementation |
| `MarketableConversionFactor` | DECIMAL(10,6) | ETL-computed: 1.0 for marketable SKUs; `1/QtyInBox` for GDC-700 component items; pending implementation |
| `MarketableItemSKU` | VARCHAR(15) | ETL-computed: self for marketable items; parent finished-good SKU for GDC-700 components; pending implementation |

---

## 4. ETL Computed Column Details

### PlanningSeries

**Purpose:** Series planning identifier using Logility naming convention; provides continuity for Logility users while preserving the original `EnterpriseItemMaster` source attribute name.

**Expression:** Direct reference to source attribute: Location-to-description mapping: Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `DimCurrentProductDetails.ItemExtSeriesNumber`

**Output values:** VARCHAR(16) | NULL

---

### ContainerVolume

**Purpose:** Normalized cube measurement for purchase order container estimation; used in downstream systems (e.g., Informer 4) to calculate container counts.

**Expression:** Normalize item cube to container units:  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `DimItemMaster.Cubes`

**Output values:** DECIMAL(10,7) | NULL

**Downstream usage:** Multiply by purchase order quantity to estimate container count: `ContainerVolume × OrderQuantity = EstimatedContainers`

---

### InitialInvoiceDate

**Purpose:** Date of first customer invoice; sourced from invoiced sales history; drives `Recent Launch` classification in `LifecycleStage`.

**Expression:** Aggregation against `SalesHistory_AFI_Enh.InvoiceDetail`; prefers the priority warehouse set, falls back to any non-55 warehouse: Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `SalesHistory_AFI_Enh.InvoiceDetail` — `ItemSKU`, `InvoiceDate`, `Warehouse`

**Output values:** DATE | NULL

---

### ItemSKUDesc

**Purpose:** Convenience label for visuals and slicers; replaces 14 model-local `ItemSKU Desc` calculated columns across legacy semantic models.

**Expression:**  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)
**Inputs:** `ItemSKU`, `ItemDescription`

---

### AlternateDivision

**Purpose:** Strips the `"Signature "` prefix from `AFISalesDivision` values for Signature-branded divisions; used in reports where the prefix creates grouping noise or label truncation.

**Expression:**  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `DimItemMaster.AFISalesDivision`

**Output values:** VARCHAR(25) | NULL

---

### CollectiveClassGroup

**Purpose:** Custom grouping of collective classes and item classes; consolidates related product categories and applies special rules for components and kits.

**Expression:** Priority-ordered mapping of ItemClassCode and CollectiveClass:  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `ItemClassCode`, `CollectiveClass`, `ItemSKU`

**Output values:** VARCHAR(100) | NULL

---

### SeriesDesc

**Purpose:** Convenience label for series slicers; replaces 13 model-local `Series Desc` calculated columns. NULL when `ItemExtSeriesNumber` is NULL.

**Expression:**  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)
**Inputs:** `DimCurrentProductDetails.ItemExtSeriesNumber` (= `PlanningSeries`), `DimItemMaster.SeriesDescription` (= `SeriesName` in DimProduct)

---

### LifecycleStage

**Purpose:** Single canonical lifecycle stage replacing 4+ divergent model-local calculated columns; used as the primary filter axis in lifecycle-based planning reports.

**Expression:** Priority-ordered CASE on status source columns: Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `Item_ENV.ienFutureStatus`, `NonPkItems.npkFutureStatus`, `DimItemMaster.AFIItemStatus`, `InitialInvoiceDate`

**Output values:** `Pre-Invoicing` | `Recent Launch` | `Current` | `End of Life`

---

### LifecycleSortOrder

**Purpose:** Enables non-alphabetic sort order on `LifecycleStage` in Power BI visuals without a separate sort table.

**Expression:** Mirrors `LifecycleStage` conditions:  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** Same as `LifecycleStage`

**Output values:** 1–4

> **Name discrepancy:** The ETL aliases this column as `[LifecycleStageSort]`. The DDL and semantic model use `[LifecycleSortOrder]`. Confirm the target column name with data engineering before finalizing the load script.

---

### DiscontinuationHorizon

**Purpose:** Lets planners filter by near-term vs. medium-term drop horizon without hard-coding date ranges in measures.

**Expression:** Bucket `PlanDropDecisionDate` relative to current date (only applies to items in `End of Life` stage):  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `LifecycleStage`, `PlanDropDecisionDate`

**Output values:** `12M` | `18M` | `24M` | NULL

> **Status:** Pending implementation — not in current ETL.

---

### PlanDropDecisionDate

**Purpose:** Anchors `DiscontinuationHorizon` bucketing and supports time-based drop-decision reporting.

**Expression:** Date `FutureStatus` first changed to `F` or `P`, sourced from status-change history table (exact source TBD with EDW team).

**Inputs:** Status-change audit history keyed on `ItemSKU`

**Output values:** DATE | NULL (NULL if item has never been planned for drop)

> **Status:** Pending implementation — currently inserted as `''` (empty string).

---

### PartFlag

**Purpose:** Allows filtering of component/sub-assembly SKUs from customer-facing demand and inventory reports.

**Expression:** Two-tier check: `ITMEXT.GDESCD` code 240 identifies parts; otherwise check `ItemClassCode` against a curated list of part-component codes:  Defined in [Source Data & ETL Logic](#6-source-data--etl-logic)

**Inputs:** `ItemMaster_AFI.ITMEXT.GDESCD`, `DimItemMaster.ItemClassCode`

**Output values:** `PART` | `ITEM`

---

### KitFlag

**Purpose:** Single canonical kit identifier replacing multiple model-local kit-type variants; classifies items by kit/material type for grouping in unit-count measures.

**Expression:** Pattern-based classification on ItemSKU suffix (priority-ordered):

```sql
CASE
    WHEN LEFT([ItemSKU], 1) = 'M' AND RIGHT(RTRIM([ItemSKU]), 2) = 'UN' THEN 'Bedding Kit'
    WHEN RIGHT(RTRIM([ItemSKU]), 2) = 'UN' THEN 'UPH Kit'
    WHEN RIGHT(RTRIM([ItemSKU]), 2) = 'SW' THEN 'Swatch'
    WHEN RIGHT(RTRIM([ItemSKU]), 5) = 'HIDES' THEN 'HIDES'
    WHEN RIGHT(RTRIM([ItemSKU]), 5) = 'VINYL' THEN 'VINYL'
    ELSE ''
END
```

**Inputs:** `ItemSKU`

**Output values:** `Bedding Kit` | `UPH Kit` | `Swatch` | `HIDES` | `VINYL` | `''` (empty string for non-kit items)

> **Status:** Pending implementation — not in current ETL.

---

### MarketableConversionFactor

**Purpose:** Converts component-item demand quantities to their equivalent finished-good sellable units so that demand measures aggregate correctly at the parent SKU level.

**Expression:** Silver marketable-SKU-conversion pattern:

```sql
CASE
    WHEN [GeneralDescriptionCode] = '700' THEN 1.0 / NULLIF([QtyInBox], 0)
    ELSE 1.0
END
```

**Inputs:** `GeneralDescriptionCode`, `QtyInBox`

**Output values:** `1.0` for standard marketable SKUs; fractional (`1/QtyInBox`) for GDC-700 component items

> **Status:** Pending implementation — currently inserted as `''` (empty string).

---

### MarketableItemSKU

**Purpose:** Substitutes the parent Item SKU for component items in `GROUPBY` clauses, enabling demand measures to aggregate at the sellable finished-good level by rolling GDC-700 component rows up to their parent SKU.

**Expression:** Lookup to parent finished-good SKU for GDC-700 component items; self-reference for all others:

```sql
CASE
    WHEN [GeneralDescriptionCode] = '700' THEN <parent_fg_sku_lookup>
    ELSE [ItemSKU]
END
```

**Inputs:** `GeneralDescriptionCode`, `ItemSKU`, parent-child SKU mapping (source join TBD with EDW team)

**Output values:** `ItemSKU` for marketable items; parent finished-good `ItemSKU` for GDC-700 components

> **Status:** Pending implementation — currently inserted as `''` (empty string).

---

## 5. Column Exclusions

| Column Definition | Exclusion reason |
| --- | --- |
| [CollectiveClassCode] CHAR(4) | Use attribute names, not codes. |
| [GeneralDescriptionCode] DECIMAL(4,0) | Use attribute names, not codes. |
| [ItemStyleCode] CHAR(3) | Use attribute names, not codes. |
| [ItemStyleGroup] VARCHAR(20) | Never Used |
| [ChildStyleDescription] VARCHAR(65) | Never Used |
| [ParentStyleDescription] VARCHAR(65) | Never Used |
| [AFISalesDivisionCode] CHAR(3) | Use attribute names, not codes. |
| [AFISalesCategoryCode] CHAR(3) | Use attribute names, not codes. |
| [SalesClassCode] CHAR(2) | Use attribute names, not codes. |
| [SalesClassDescription] VARCHAR(25) | Never Used |
| [DiscountClassCode] CHAR(2) | Never Used |
| [DiscountClassDescription] VARCHAR(25) | Never Used |
| [CommissionClassCode] CHAR(2) | Never Used |
| [CommissionClassDescription] VARCHAR(25) | Never Used |
| [FreightClassCode] CHAR(2) | Never Used |
| [FreightClassDescription] VARCHAR(25) | Never Used |
| [RetailCategoryCode] CHAR(3) | Never Used |
| [RetailCategoryDescription] VARCHAR(30) | Never Used |
| [MainPiece] VARCHAR(40) | NULL, use `MainPieceItem` |
| [SecondaryPlanner] VARCHAR(50) | Deprecated |
| [CurrentSCPManufacturingStatus] VARCHAR(7) | Inaccurate |
| [MarketingItemStatus] CHAR(1) | Never Used |
| [MarketingStatusDescription] VARCHAR(25) | Never Used |
| [InitialInvoicePeriod] VARCHAR(7) | Prefer Initial Invoice Date |
| [F123ProductFlag] BIT | Never Used |

---

## 6. Source Data & ETL Logic

```sql
SELECT
      RTRIM([IM].[ItemSKU])                                                      AS [ItemSKU]
    , [IM].[ItemDescription]
    , RTRIM([IM].[ItemSKU]) + ' - ' + [IM].[ItemDescription]                    AS [ItemSKUDesc]
    , [IM].[ItemCode]
    , [IM].[SeriesNumber]
    , [IM].[SeriesName]
    , [IM].[SeriesColor]
    , [CPD].[ItemExtSeriesNumber]                                                AS [PlanningSeries]
    , [CPD].[ItemExtSeriesNumber]                                                AS [ItemExtSeriesNumber]
    , [IM].[ExtSeriesNumber]
    , RTRIM([CPD].[ItemExtSeriesNumber]) + ' - ' + [IM].[SeriesDescription]     AS [SeriesDesc]
    , [IM].[FrameNumber]
    , [IM].[ItemClassCode]
    , [IM].[ItemClassName]
    , [IM].[CollectiveClass]
    , CASE
          WHEN [IM].[ItemClassCode] IN ('WVBC', 'WVHC', 'ZARP') THEN 'BEDDING COMPONENTS'
          WHEN [IM].[ItemClassCode] = 'USKE' THEN 'BEDDING KT KITS'
          WHEN [IM].[ItemClassCode] IN ('WVCD', 'WVUP', 'UESW', 'WVWB') THEN 'UPH COMPONENTS'
          WHEN [IM].[ItemClassCode] IN ('WVCS', 'WVHD', 'WVCU') THEN 'CG COMPONENTS'
          WHEN [IM].[ItemClassCode] = 'UTRK' THEN 'UPH KT KITS'
          WHEN [IM].[CollectiveClass] IN ('ACCESSORIES', 'STATIONARY UPH', 'MOTION UPH')
           AND RIGHT(RTRIM([IM].[ItemSKU]), 2) = 'UN' THEN 'UPH KITS'
          WHEN [IM].[CollectiveClass] = 'BEDDING'
           AND LEFT([IM].[ItemClassCode], 1) = 'Z'
           AND RIGHT([IM].[ItemClassCode], 1) = 'K' THEN 'BEDDING KITS'
          WHEN [IM].[ItemClassCode] IN ('WVVG', 'WVBF') THEN 'BEDDING KITS'
          WHEN [IM].[CollectiveClass] IN ('ACCESSORIES', 'LAMPS', 'RUGS', 'THROWS & PILLOWS') THEN 'ACCENTS'
          ELSE [IM].[CollectiveClass]
      END                                                                        AS [CollectiveClassGroup]
    , [IM].[ProductLine]
    , [GDC].[GDICL]                                                             AS [GeneralDescription]
    , [IM].[ItemGrouping]
    , [IM].[Colors]
    , [IM].[PricePoint]
    , [IM].[ItemPricePointRating]
    , [IM].[AFIFinanceDivision]
    , [IM].[AFISalesDivision]
    , [IM].[AFISalesCategory]
    , CASE
          WHEN [IM].[AFISalesDivision] LIKE 'Signature %'
              THEN SUBSTRING([IM].[AFISalesDivision], 11, LEN([IM].[AFISalesDivision]))
          ELSE [IM].[AFISalesDivision]
      END                                                                        AS [AlternateDivision]
    , [IM].[ImportDomesticCode]
    , [IM].[CountryofOrigin]
    , [IM].[ResponsibleOffice]
    , [IM].[ResponsibleOfficeName]
    , [IM].[CEXCode]
    , ''                                                                         AS [MakeBuyCode]
    , [IM].[FOBArcPrice]
    , [IM].[Cubes]
    , [IM].[QtyInBox]
    , [IM].[UOM]
    , CAST([IM].[Cubes] AS DEC(9, 5)) / 2400                                    AS [ContainerVolume]
    , [IM].[CurrentUnitCost]
    , [IM].[PrimaryVendor]
    , [V].[VNAME]                                                                AS [PrimaryVendorName]
    , [IM].[MainPieceItem]
    , TRIM(COALESCE([IPK].[ienForecastPlannerID], [NPK].[npkForecastPlannerID])) AS [ItemForecastPlannerID]
    , CASE WHEN [IM].[AFIItemStatus] = '' THEN 'C' ELSE [IM].[AFIItemStatus] END AS [AFIItemStatus]
    , [CPD].[CurrentStatus]                                                      AS [CurrentStatus]
    , TRIM(COALESCE([IPK].[ienFutureStatus], [NPK].[npkFutureStatus]))           AS [FutureStatus]
    , [IM].[ManufacturingStatus]
    , [IM].[ManufacturingStatusChangeDate]
    , [IM].[DiscontinuedDate]
    , TRIM(COALESCE([IPK].[ienHoldBuyCode], [NPK].[npkHoldBuyCode]))             AS [HoldBuyCode]
    , [IM].[MarketIntroducedAt]
    , [IM].[MarketBeginDate]
    , [IM].[MarketEndDate]
    , [Inv].[InitialInvoiceDate]                                                 AS [InitialInvoiceDate]
    , [IM].[InitialInvoiceQty]
    , [IM].[SellableItemFlag]
    , [IM].[ExpressShipFlag]
    , [IM].[HSExclusiveFlag]
    , [IM].[HSCoreProductFlag]
    , [IM].[HSProprietaryProductFlag]
    , [IM].[ConsumerChoiceFlag]
    , [IM].[CommodityItem]
    , [IM].[Showroom]
    , [IM].[ItemImage]
    , CASE [IM].[ItemImage]
          WHEN '' THEN NULL
          WHEN NULL THEN NULL
          ELSE CONCAT('http://www.ashleydirect.com/graphics/', [IM].[ItemImage])
      END                                                                        AS [ImageURL]
    , CASE
          WHEN RTRIM(COALESCE([IPK].[ienFutureStatus], [NPK].[npkFutureStatus])) IN ('F', 'P', 'L', 'E') THEN 'End of Life'
          WHEN [IM].[AFIItemStatus] = 'N' THEN 'Pre-Invoicing'
          WHEN [Inv].[InitialInvoiceDate] >= DATEADD(MONTH, -9, GETDATE()) THEN 'Recent Launch'
          WHEN [IM].[AFIItemStatus] IN ('D', 'R') THEN 'End of Life'
          ELSE 'Current'
      END                                                                        AS [LifecycleStage]
    , CASE
          WHEN RTRIM(COALESCE([IPK].[ienFutureStatus], [NPK].[npkFutureStatus])) IN ('F', 'P', 'L', 'E') THEN 4
          WHEN [IM].[AFIItemStatus] = 'N' THEN 1
          WHEN [Inv].[InitialInvoiceDate] >= DATEADD(MONTH, -9, GETDATE()) THEN 2
          WHEN [IM].[AFIItemStatus] IN ('D', 'R') THEN 4
          ELSE 3 -- Current
      END                                                                        AS [LifecycleStageSort]
    , ''                                                                         AS [PlanDropDecisionDate]
    , CASE
          WHEN [EXT].[GDESCD] = '240' THEN 'PART'
          WHEN [IM].[ItemClassCode] IN ('MATT', 'UBBC', 'UESW', 'USKE', 'UTRK', 'WVBC', 'WVCD',
                                        'WVCS', 'WVCU', 'WVHC', 'WVHD', 'WVUP', 'WVVF', 'WVVG',
                                        'WVWB', 'ZACK', 'ZAMK', 'ZARP', 'ZAWU', 'ZDCK', 'ZDLK',
                                        'ZDMK', 'ZJBK', 'ZJFK', 'ZKBK', 'ZLSD', 'ZMCK', 'ZMLK',
                                        'ZMMK', 'ZUCK', 'ZUMK', 'ZXCK', 'ZXLK', 'ZXMK') THEN 'PART'
          ELSE 'ITEM'
      END                                                                        AS [PartFlag]
    , ''                                                                         AS [MarketableConversionFactor]
    , ''                                                                         AS [MarketableItemSKU]
FROM [Enterprise_Lakehouse].[MasterData_DW].[DimItemMaster] AS IM
LEFT JOIN [Enterprise_Lakehouse].[SupplyChain_DW].[DimCurrentProductDetails] AS CPD
    ON [IM].[ItemSKU] = [CPD].[ItemSKU]
LEFT JOIN [Enterprise_Lakehouse].[Wholesale_Purchasing_AFI].[VENNAM] AS V
    ON [IM].[PrimaryVendor] = [V].[VNDNR]
LEFT JOIN (
    SELECT
          [ID].[ItemSKU]
        , COALESCE(
              MIN(CASE
                      WHEN [ID].[Warehouse] IN ('1', '15', '17', '19', '28', '42', '70', '5', 'ECR')
                      THEN [ID].[InvoiceDate]
                  END),
              MIN([ID].[InvoiceDate])
          )                                                                      AS [InitialInvoiceDate]
    FROM [Enterprise_Lakehouse].[SalesHistory_AFI_Enh].[InvoiceDetail] AS ID
    WHERE [ID].[Warehouse] <> '55'
    GROUP BY [ID].[ItemSKU]
) AS Inv
    ON [IM].[ItemSKU] = [Inv].[ItemSKU]
LEFT JOIN [Enterprise_Lakehouse].[ItemMaster_AFI].[ITMEXT] AS EXT
    ON [IM].[ItemSKU] = [EXT].[ITNBR]
LEFT JOIN [Enterprise_Lakehouse].[ItemMaster_AFI].[GENDESC] AS GDC
    ON [EXT].[GDESCD] = [GDC].[GDCODE]
LEFT JOIN [Enterprise_Lakehouse].[MasterData_ProductKnowledge].[Item_ENV] AS IPK
    ON [CPD].[ItemSKU] = [IPK].[ienItemNumber]
   AND [IPK].[ienEnvironmentCode] = 'AFI'
LEFT JOIN [Enterprise_Lakehouse].[Wholesale_ProductSourcing].[NonPkItems] AS NPK
    ON [CPD].[ItemSKU] = [NPK].[npkItemNumber]
WHERE [IM].[ItemSupplierDirectShipOnly] <> 'True';
```

**ETL Notes:**

- **Primary source:** `Enterprise_Lakehouse.MasterData_DW.DimItemMaster`
- **Secondary sources:** `SupplyChain_DW.DimCurrentProductDetails` (planning series, current status); `Wholesale_Purchasing_AFI.VENNAM` (vendor name); `SalesHistory_AFI_Enh.InvoiceDetail` (initial invoice date); `ItemMaster_AFI.ITMEXT` / `GENDESC` (general description code and label); `MasterData_ProductKnowledge.Item_ENV` (future status, hold buy code, planner ID — AFI environment); `Wholesale_ProductSourcing.NonPkItems` (future status, hold buy code, planner ID — non-PK items)
- **Refresh frequency:** Daily
- **Base filter:** `WHERE [IM].[ItemSupplierDirectShipOnly] <> 'True'` — excludes direct-ship-only supplier items
- **Key transformations:**
  - `AFIItemStatus` empty string `''` normalized to `'C'` (Current)
  - `FutureStatus`, `HoldBuyCode`, `ItemForecastPlannerID` resolved via `COALESCE` priority: `Item_ENV` (AFI environment) then `NonPkItems`
  - `InitialInvoiceDate` prefers priority warehouses `('1','5','15','17','19','28','42','70','ECR')`, falls back to any non-55 warehouse
  - `ImageURL` constructed as `http://www.ashleydirect.com/graphics/ + ItemImage`; NULL when source is NULL or empty
  - Source column `DimItemMaster.CountryofOrigin` (lowercase 'o') maps to `DimProduct.CountryOfOrigin`
- **Pending columns (inserted as `''` placeholder):** `MakeBuyCode`, `PlanDropDecisionDate`, `MarketableConversionFactor`, `MarketableItemSKU`
- **Not yet in ETL:** `KitFlag`, `DiscontinuationHorizon`
- **Name discrepancy:** ETL aliases the sort column as `[LifecycleStageSort]`; DDL and semantic model use `[LifecycleSortOrder]` — confirm target column name with data engineering before finalizing the load script

---

## 7. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-17 | Initial draft | Robert Font Perez |
| 2026-06-19 | Added §6 Source Data & ETL Logic with ETL contract; added §3 Semantic Model Layer note; corrected `DiscontinuedDate` DDL bug (removed table alias); updated `SeriesDesc`, `InitialInvoiceDate`, `LifecycleStage`, and `LifecycleSortOrder` ETL expressions to match ETL contract; added `AlternateDivision` ETL detail; flagged `LifecycleStageSort` vs `LifecycleSortOrder` name discrepancy; marked pending-implementation columns | Robert Font Perez |
