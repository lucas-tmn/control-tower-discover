---
type: Map
title: Source Migration Map — Current Estate Sources ↔ SupplyChain_Gold Targets
description: Table-level mapping from the data sources the 25 analyzed reports use today (SupplyChain_Enh, SupplyChain_DW, Wholesale_DemandPlanning_AFI, dataflows, SharePoint) to the governed SupplyChain_Gold layer, cross-checked against the actual Fabric build.
tags: [bridge, migration, data-sources, supplychain-gold, lineage]
timestamp: 2026-07-10
status: draft
---

# Source Migration Map

**Purpose:** when the estate (or its Eagle Eye successor) re-points to the
governed gold layer, this is the crosswalk. Also doubles as a dependency census:
which reports break if a given legacy source changes.

Confidence legend: **Confirmed/Built** = a real table definition with working ETL
SQL exists in `07-fabric-build/docs/model-definitions/` (not just named in the OKF
bundle's prose) · **Direct** = OKF doc names the same object/lineage, not yet built
· **Probable** = role-equivalent, contract differences to verify, not yet built ·
**Gap** = no gold target documented yet, on either side.

**Update 2026-07-10:** cross-checked against the actual Fabric build
(`07-fabric-build/`). Several targets previously listed as OKF-bundle prose only are
now confirmed built with real SQL; a few surprises came out of checking rather than
assuming — noted inline.

## Governed EDW sources → Gold targets

| AS-IS source (schema.object) | Used by (analyzed reports) | Gold target | Confidence |
|---|---|---|---|
| `SupplyChain_Enh.DemandForecastSnapshot` (as SupplyPlanDetail extract) | Demand Review, AFT_SI-SS_PSW, Inv Management (`SI at US Warehouse`, `W2 SS Change`), Demand Fulfillment | [`FactSupplyPlanDetail`](../07-fabric-build/docs/model-definitions/scp-core-model/FactSupplyPlanDetail.md) (built) — also documented conceptually at [OKF's copy](../05-okf-bundle/bundle/datasets/tables/FactSupplyPlanDetail.md) | **Confirmed/Built** |
| `SupplyChain_Enh.DemandForecastSnapshot` (as Fcst_Snapshots — working/prior/90d) | Demand Review, Forecast Change WoW, GF FC Tool | [`FactWorkingForecast`](../07-fabric-build/docs/model-definitions/scp-core-model/FactWorkingForecast.md) (built) | **Confirmed/Built** — OKF notes historical consensus snapshots must be retained; AS-IS already retains them; the built doc confirms `CustomerGroup` defaults to `'AFICONS'` when unknown — the same hardcode our own Demand Review analysis flagged pre-March-2025 |
| `Wholesale_DemandPlanning_AFI.DemandForecast` (older schema, latest-only) | **Weekly Trend only** (PAT-07 divergence) | [`FactCurrentForecast`](../07-fabric-build/docs/model-definitions/scp-core-model/FactCurrentForecast.md) (built, but the doc itself notes "implementing... in anticipation of transition in Q3" — i.e. still mid-migration) | **Confirmed/Built (transitional)** — migrating Weekly Trend to this table removes the PAT-07 comparability break once the Q3 transition completes |
| `SupplyChain_Enh.ActualsCustItemWH_AFI` (`OrdHist`) | Demand Review, GF Act+Fcst, Demand Sensing, Consumption Report | No equivalent fact built yet in `07-fabric-build/` (only 3 facts exist: SupplyPlanDetail, WorkingForecast, CurrentForecast) — OKF's [`sales_orders`](../05-okf-bundle/bundle/datasets/tables/sales_orders.md) remains conceptual only | **Probable — confirmed not yet built.** Actual-demand basis (ordered-by-request-date-minus-lead-time vs shipped) must be settled per BRD; carry the `OrdHist` data-quality facts into the gold doc once it's built (see gap-fill map) |
| `Fcst_Accuracy_Cust_It_Wh` / `ItWhAccy` views | 3 Forecast Accuracy models, Demand Review | No equivalent fact built yet in `07-fabric-build/` — OKF's planned `FcstAccuracy_CustItemWh` (per [forecast_accuracy.md](../05-okf-bundle/bundle/metrics/forecast_accuracy.md)) remains conceptual only | **Direct — confirmed not yet built** — gold build must resolve the March-2025 grain break and BUG-001 snapshot logic rather than port them |
| `Distribution_Warehouse_Wholesale` transaction log | Inv Management (`Inv Age`), Inventory Transactions & Item Balance | No equivalent fact built yet — OKF's [`inventory_onhand`](../05-okf-bundle/bundle/datasets/tables/inventory_onhand.md) remains conceptual only | **Probable — confirmed not yet built** — transaction-grain vs balance-grain contract to verify; BUG-014 sign conventions must be normalized whenever this is built |
| PO / receipt tables behind Receipts, FCA Fee Audit, Supplier On-Time | FCA_Services_Fee_Audit, Supplier On-Time (catalog tier) | No equivalent fact built yet — OKF's [`purchase_orders`](../05-okf-bundle/bundle/datasets/tables/purchase_orders.md) remains conceptual only | **Probable — confirmed not yet built** |
| `SupplyChain_Enh` ATP (`Week_2_ATP`) | Demand Review (In Stock), Complete Series In Stock | No equivalent built as a gold table — OKF's [`atp_in_stock_query`](../05-okf-bundle/bundle/datasets/queries/atp_in_stock_query.md) is documented as a query pattern, not a table, on both sides | **Direct — confirmed not yet built as a table** |

## Conformed dimensions (dataflow → Gold)

**Notable finding:** 5 of 6 conformed dimensions are confirmed built with real ETL
SQL in `07-fabric-build/`. The 6th — `DimDate` — is **not**: its doc literally
states "Schema still needs to be defined." This is a genuine surprise: `DimDate` is
the dimension PAT-07 most depends on (3 date anchors in Inv Management, fiscal
calendar duplicated across 21+6 models, 6 different snapshot-key column names —
see `Systemic_Patterns_Registry.md` PAT-07), and it's the least-built of the six.

| AS-IS (shared dataflow `a47e4573…` → PowerBI_Supplychain) | Gold target | Confidence | Migration note |
|---|---|---|---|
| `z_ProductDetails` | [`DimProduct`](../07-fabric-build/docs/model-definitions/dimension-tables/DimProduct.md) (built) | **Confirmed/Built** | Source confirmed: `Enterprise_Lakehouse.MasterData_DW.DimItemMaster` (primary) unified with `SupplyChain_DW.DimCurrentProductDetails`. The built doc explicitly states it resolves **110 drifted calculated columns across 16 legacy models** into 7 governed classification columns (`LifecycleStage`, `KitFlag`, `DiscontinuationHorizon`, `PlanDropDecisionDate`, `LifecycleSortOrder`, `MarketableConversionFactor`, `MarketableItemSKU`) — this is the single highest-value dimension in the whole migration |
| `z_FiscalCal` | [`DimDate`](../07-fabric-build/docs/model-definitions/dimension-tables/DimDate.md) — **stub only, "Schema still needs to be defined"** | **Not yet built** | One calendar, one snapshot convention would resolve PAT-07 (3 date anchors in Inv Management, YTD-1 double offset, UTC-offset contradictions) — but the gold table doesn't exist yet. This should be flagged as a priority build gap given how many patterns depend on it |
| `z_WarehouseMaster` | [`DimWarehouse`](../07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md) (built) | **Confirmed/Built** | Source confirmed: `SupplyChain_DW.DimAFIWarehouses` + `Wholesale_Codis_AFI.AshleyWarehouseMaster`. Real `WarehouseGroup`/`PlanningWarehouse` mapping exists (see `07-fabric-build/WAREHOUSE_335_RECONCILIATION.md` for the 335/Ashton finding this produced) — this is the PAT-08 fix: retire ~40 per-warehouse hardcoded measures across Supply Plan Detail + Inv Management once reports point here |
| `z_CustomerMaster` (+ Weekly Trend's 8 synthetic rows; On Time %'s DSG SWITCH) | [`DimCustomer`](../07-fabric-build/docs/model-definitions/dimension-tables/DimCustomer.md) (built) | **Confirmed/Built** | Source confirmed: `AFISales_DW.DimCustomers` (SQL master); the `PowerBI_SupplyChain.CustomerAcctMaster_AFI` dataflow shadow is **already retired** after parity check. Synthetic-row hack and the copy-pasted 16-account DSG rollup become governed customer-group attributes once reports migrate |
| `z_VendorMaster` | [`DimVendor`](../07-fabric-build/docs/model-definitions/dimension-tables/DimVendor.md) (built) | **Confirmed/Built** | Source confirmed: `PowerBI_SupplyChain.VendorMaster` (primary) + `Wholesale_Purchasing_AFI.VENNAM` + `Wholesale_ProductSourcing_AFI.vendor`. **Includes a `LeadTime` column** (plus `AFILeadTime`/`WVFLeadTime`, flagged in the doc as deprecated/needing differentiation) — see the gap-fill map's corrected lead-time row. Country/returnability attributes here replace hardcoded vendor IDs 633312/643509 (Inv Management Oversea-Vendor logic) |
| `z_ProdResourceMaster` | [`DimProductionResource`](../07-fabric-build/docs/model-definitions/dimension-tables/DimProductionResource.md) (built) | **Confirmed/Built** | Source confirmed: `Enterprise_Lakehouse.DemandPlanning_AFI.ProductionCapacity`. Resource-location pairs mapped to standardized facility names — relevant to DEC-006's `Prod Capacity` masking issue (BUG-013), though that issue lives in the measure layer, not this dimension |

## Ungoverned sources with NO gold target yet (governance queue)

| AS-IS source | Feeds | Risk (from PAT-04) | Proposed gold disposition |
|---|---|---|---|
| SharePoint `Cycle_Dates` list (`94a48657`) | Every snapshot-relative measure in Demand Review; Fcst Accuracy snapshot logic | Cycle open depends on manual list update | Becomes `DimFcstConsensusCycleDates` — **still not built** in `07-fabric-build/` either (planned in OKF `forecast_accuracy.md` only) — highest-priority governance item, and now also blocked on the still-unbuilt `DimDate` above |
| `RH_Fcst.xlsx` (working + prior tabs) | RH channel plan (DEC-011) | No versioning; prior plan destructible | Governed submission path with schema validation — per DEC-011 verdict; not built |
| `RHSales_2024.xlsx` | RH drop-ship actuals | Frozen at 2024 (BUG-006) | Replace with EDW-sourced channel actuals; not built |
| `_Product_Journal_UNIFIED_MASTER.xlsx` | Product journal (Demand Review) | Live shared workbook, lock-read risk | EDW journal table or list with API; not built (not a `DimProduct.md` attribute today) |
| `VENDOR LIST AFT & 232.xlsx` | Vendor classification (Inv Management, AFT_SI-SS_PSW) | Manual master data | **`DimVendor` is now built** and ready to receive this — the SharePoint file itself isn't retired yet, but the governed destination exists (unlike the other rows in this table) |
| `Default_Planner` / `Users` SharePoint lists | Planner routing (Demand Review, Planner Assignment) | Assignment drift | Fold into governed planner-assignment table (Planner Assignment report already computes correct-vs-actual — its logic is the seed); not built |
| OneDrive personal Excel (Demo_Inventory Health) | Demo model only | Not production — no migration | Archive/exclude |

## Report-level dependency census (which reports touch which layer)

Legend: E = SupplyChain_Enh · D = SupplyChain_DW · W = Wholesale_DemandPlanning_AFI · F = shared dataflow dims · S = SharePoint/Excel

| Report | E | D | W | F | S |
|---|---|---|---|---|---|
| Demand Review | ● | ● | ● | ● | ● (8 sources) |
| Forecast Accuracy (×3 models) | ● | | ● | ● | ● (params) |
| Inv Management | ● | | ● | ● | ● (vendor) |
| AFT_SI-SS_PSW | ● | | | ● | ● (5 files) |
| Weekly Trend | ● | | ● (older table) | ● | |
| Safety Stock Analysis | ● | ● | | ● | |
| Demand Fulfillment / Product Review (both) / GF family | ● | ● | ● | ● | varies |
| On Time % by Customer | ● | | | | |
| FCA Services Fee Audit / Planner Assignment / Forecast Change WoW / Demand Sensing / Consumption / Complete Series | ● | varies | varies | ● | varies |

(Full per-table detail lives in each report's analysis §4; this census is the
one-glance version for migration sequencing: **Demand Review is the widest
dependency surface and should migrate last; On Time % is the narrowest and could
pilot first.**)

## Build-status headline (2026-07-10)

Of everything mapped in this document: **5 of 6 conformed dimensions are built**
with real ETL SQL (DimProduct, DimWarehouse, DimCustomer, DimVendor,
DimProductionResource) — only **DimDate remains an unbuilt stub**, despite being
the dimension the most patterns (PAT-07 especially) depend on. Of the **9 candidate
gold facts** identified in `07-fabric-build/docs/report-migration-docs/02-group-analysis/fact-grains.md`,
only **3 are actually built** (FactSupplyPlanDetail, FactWorkingForecast,
FactCurrentForecast) — all three on the forecast/supply-plan side, consistent with
Devon's stated Phase 1 priority. Inventory, receipts, production, on-time, and
PSW facts remain conceptual only. This gives a concrete, evidence-based answer to
"how far along is the Fabric build, really" — useful for status reporting
independent of what any dashboard currently shows.
