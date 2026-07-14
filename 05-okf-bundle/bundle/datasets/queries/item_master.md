---
type: Query
title: Item Master Query
description: EDW SQL query that produces the item master shape.
tags: [item-master, product, lifecycle, planning, dimension, query]
timestamp: 2026-07-06
resource: "[Enterprise_DW].[DimItemMaster]"
source_system: ERP
refresh_cadence: daily
data_source: ashley_edw
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

## Base Query

This query produces the Product Master dataset shape while the gold table is unavailable.

```sql
SELECT
      RTRIM([IM].[ItemSKU])                                                      AS [ItemSKU]
    , [IM].[ItemDescription]
    , RTRIM([IM].[ItemSKU]) + ' - ' + [IM].[ItemDescription]                    AS [ItemSKUDesc]
    , [IM].[ItemCode]
    , [IM].[SeriesNumber]
    , [IM].[SeriesName]
    , [IM].[SeriesColor]
    , [CPD].[Item Ext Series Number]                                               AS [PlanningSeries]
    , [CPD].[Item Ext Series Number]                                                AS [ItemExtSeriesNumber]
    , [IM].[ExtSeriesNumber]
    , RTRIM([CPD].[Item Ext Series Number]) + ' - ' + [IM].[SeriesDescription]     AS [SeriesDesc]
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
    , [CPD].[Current Status]                                                      AS [CurrentStatus]
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
FROM [Enterprise_DW].[DimItemMaster] AS IM
LEFT JOIN [SupplyChain_DW].[DimCurrentProductDetails] AS CPD
    ON [IM].[ItemSKU] = [CPD].[Item SKU]
LEFT JOIN [Wholesale_Purchasing_AFI].[VENNAM] AS V
    ON [IM].[PrimaryVendor] = [V].[VNDNR]
LEFT JOIN (
    SELECT
          [ID].[ItemNumber]
        , COALESCE(
              MIN(CASE
                      WHEN [ID].[Warehouse] IN ('1', '15', '17', '19', '28', '42', '70', '5', 'ECR')
                      THEN [ID].[InvoiceDate]
                  END),
              MIN([ID].[InvoiceDate])
          )                                                                      AS [InitialInvoiceDate]
    FROM [Wholesale_SalesHistory_AFI].[InvoiceDetail] AS ID
    WHERE [ID].[Warehouse] <> '55'
    GROUP BY [ID].[ItemNumber]
) AS Inv
    ON [IM].[ItemSKU] = [Inv].[ItemNumber]
LEFT JOIN [MasterData_ItemMaster_AFI].[ITMEXT] AS EXT
    ON [IM].[ItemSKU] = [EXT].[ITNBR]
LEFT JOIN [MasterData_ItemMaster_AFI].[GENDESC] AS GDC
    ON [EXT].[GDESCD] = [GDC].[GDCODE]
LEFT JOIN [MasterData_ProductKnowledge].[Item_ENV] AS IPK
    ON [IM].[ItemSKU] = [IPK].[ienItemNumber]
   AND [IPK].[ienEnvironmentCode] = 'AFI'
LEFT JOIN [Wholesale_ProductSourcing].[NonPkItems] AS NPK
    ON [IM].[ItemSKU] = [NPK].[npkItemNumber]
WHERE [IM].[ItemSupplierDirectShipOnly] <> 'True';
```

