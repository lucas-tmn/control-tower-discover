---
title: Candidate Fact Grains Catalog
source: output/analysis/_inventory/base_objects.csv, query_fingerprints.csv
candidate_fact_grains: 9
exact_duplicate_queries: 10
---

## How to read this

Each section is one candidate gold fact. Grain is taken from the GROUP BY columns captured per
source query in [_inventory/base_objects.csv](_inventory/base_objects.csv). Snapshot strategy
matters: facts whose source is used in `history` mode anywhere (forecast accuracy, supply-plan
accuracy) must retain all snapshots; facts only ever read `latest` can keep current-snapshot only
but should still carry the snapshot key for future trending.

**Exact-duplicate source queries** (same normalized fingerprint across models) are direct merges —
build the fact once and point both reports at it:

| Fingerprint | Source | Models / report-tables (identical query) |
| --- | --- | --- |
| a36c42f779a8 | Manufacturing_Inventory_WNK.IMHIST | Act+Fcst by WNK & MILL · Act+Fcst vs Manufacturing (VendorShipped) |
| 5b3282a03338 | SupplyChain_Enh.DemandInventorySnapshot | Act+Fcst by WNK & MILL · Act+Fcst vs Manufacturing (z_ItemWHProdResource) |
| 93f24aaf9e55 | Wholesale_DemandPlanning_AFI.SupplyPlanDetail | Demand Review · Product Review (NEW) (SupplyPlanDetail) |
| 25c5a8ae2891 | SupplyChain_Enh.ATPWeekEnding | Demand Review · Product Review (NEW) (Week_2_ATP) |
| be43bacafd37 | PowerBI_Wholesale.WeeklyPlacements | Demand Review · Product Review (NEW) (Placements ABC) |
| 3100a0f27603 | PowerBI_Wholesale.WeeklyPlacements | Demand Review (Placement_History) · Product Review (NEW) (PlacementsOverTime) |
| a5e99276f8ec | Wholesale_SalesHistory_AFI.InvoiceDetail | Product Review (NEW) · Weekly Trend Analysis (Actuals) |
| 0d4ee2be95b8 | Wholesale_DemandPlanning_AFI.DemandForecast | Product Review (NEW) (WeeklyForecast) · Weekly Trend Analysis (Forecast) |
| 941938c73560 | SupplyChain_DW.DimCurrentProductDetails | Inventory Health · Safety Stock Analysis (z_KitMkt) |
| 4c875edcd65d | Enterprise_DW.DimDate | AFT_SI-SS_PSW (DUE · ETD — role-played date) |

---

### FactForecastSnapshot

**Grain:** Item SKU × Warehouse × Customer Group × Fiscal Month × Snapshot date (forecast type:
working/RSLF/PROL/FUTO unpivoted).

**Source base object(s):** `SupplyChain_Enh.DemandForecastSnapshot` (11 models, primary in 15
report-tables — the most-used fact source in the estate); `Wholesale_DemandPlanning_AFI.DemandForecast`
(weekly working forecast, exact-dup `0d4ee2be95b8`); `SupplyChain_Enh.CurFcstSnapshotDaily/Weekly`
(published-forecast snapshots).

**Snapshot strategy:** **history required** — used in `history` mode by Weekly Trend Analysis and
GF Act+Fcst; keep all `SnapshotDate`/`dfcSnapshot` rows. The RSLF/PROL/FUTO measures slice by a
forecast-type column produced by the unpivot pattern.

**Replaces report tables:** Fcast, Fcst_Snapshots, FC by Customer Group, L1Fcst, WeeklyForecast,
Forecast, FutOrd, Hist Weekly FC, Orders_Current_Month_Futo, Fcst_Average_Promo.

**Questions answered:** What is the current/working forecast by item-warehouse-customer? How has
the forecast for a period changed across snapshots? RSLF vs PROL vs FUTO split.

---

### FactActuals

**Grain:** Item SKU × Warehouse × Customer Account × Fiscal Week/Month (sales type:
invoiced/open-order/written).

**Source base object(s):** `SupplyChain_Enh.ActualsCustItemWH_AFI` (9 models — the demand-actuals
spine); `Wholesale_SalesHistory_AFI.InvoiceDetail` (4 models, invoiced sales, exact-dup
`a5e99276f8ec`); `AFISales_DW.FactOpenOrders` (open orders); `Wholesale_SalesHistory_AFI.OrderHistory`.

**Snapshot strategy:** none (transactional) — additive by date.

**Replaces report tables:** ActDemand, OrdHist, OrderHist, Actuals, AMZNWholesale, ItWhAccy
(actuals side).

**Questions answered:** Invoiced + open-order + written demand by item/warehouse/customer over
time; YoY and R12 sales; consumption vs forecast.

---

### FactSupplyPlan

**Grain:** Item × Location/Warehouse × Week Ending × (Production Resource) — the SI / SI-SS /
production-plan spine.

**Source base object(s):** `Wholesale_DemandPlanning_AFI.SupplyPlanDetail` (13 models, primary in
10 — the second-most-used fact source); `Wholesale_DemandPlanning_AFI.PlanDetailTimeline` /
`SupplyChain_Enh.PlanDetailTimelineSnapshot`; `SupplyChain_Enh.PlannedRequirementsLogility`.

**Snapshot strategy:** used `latest` (operational SI) and `history` (Supply Plan Detail Accuracy
keeps `SnapshotLead`/`SnapshotSort` snapshots). Keep snapshot key.

**Replaces report tables:** SupplyPlanDetail, Inventory, SISS Timeline, InvHist, Current/Past
Week/PO/Old Snap (PSW-joined), PlandSupply.

**Questions answered:** Shippable inventory (SI), SI minus safety stock, projected fulfillment,
weekly SI by warehouse and week bucket. **This fact + DimWarehouse retires the entire `WH## SI`
hardcoded measure family.**

---

### FactInventoryPosition

**Grain:** Item SKU × Warehouse × (Snapshot/Week) — on-hand, ATP, goal/safety-stock inventory.

**Source base object(s):** `SupplyChain_Enh.DemandInventorySnapshot` (6 models, exact-dup
`5b3282a03338`); `SupplyChain_Enh.ATPWeekEnding` (ATP in-stock, exact-dup `25c5a8ae2891`);
`Inventory_Enh_History.ItemBalance` (on-hand balance); `SupplyChain_Enh.IOExportedItemOutputsSnapshot`
(GF/DP safety-stock outputs).

**Snapshot strategy:** mostly `latest`; ItemBalance history for turns. Keep snapshot/week key.

**Replaces report tables:** z_ItemWHProdResource, z_ItemWHMaster, GFIO, InvGoal, ATPInStock,
Item Balance, SI at US Warehouse.

**Questions answered:** On-hand / ATP / goal inventory by item-warehouse; days-of-supply; in-stock
rate; safety-stock suggested vs constrained.

---

### FactForecastAccuracy

**Grain:** Item × Warehouse × (Customer Group) × Fiscal Month × Forecast lag (2wk/30d/90d).

**Source base object(s):** `SupplyChain_Enh.DemandForecastSnapshot` in **history** mode +
`SupplyChain_Enh.ItemActualDemand_Logility` (4 models) + `ActualsCustItemWH_AFI`;
`SupplyChain_Enh.DemandForecastHistorySnapshot`.

**Snapshot strategy:** **history mandatory** — accuracy is defined by comparing each lagged
forecast snapshot to realized demand. This is the fact that most needs full snapshot retention.

**Replaces report tables:** CustItWHAccy, ItWHAccy, CustItAccy, FcstAccuracy, Month End Status
Snapshots, ItWhAccy.

**Questions answered:** Bias %, wMAPE, MAPE, error vs naive, value-add — at item, item-warehouse,
and customer-item-warehouse grains and at 2wk/30d/90d lags (see the forecast-accuracy archetype in
[measure-archetypes.md](measure-archetypes.md)).

---

### FactPSW

**Grain:** Item × Location × Vendor × ETD week × Data type — the PSW (Planned Supply Weekly) /
Logility container extract.

**Source base object(s):** `SupplyChain_Enh.PSWWeeklyExtractSnapshot` (5 models, primary in 7);
`SupplyChain_Enh.ForecastCommonContainer_Logility` (5 models);
`PowerBI_SupplyChain.FCC_LogilityCurrentDay` (current-day latency of the same container).

**Snapshot strategy:** `latest` for operational PSW, history snapshots retained
(`SPRunDate`/`FileDate`) for rolling/firm analysis. Keep snapshot key.

**Replaces report tables:** Current/Past Week/PO/Old Snap, Firm and Roll, PSW, Ashton_PSW,
PSWHistoricalSnapshots, Query1 (Plan Drop 1), AnnualWrkFcst_Snapshots.

**Questions answered:** Firm vs roll, %rolled, planned supply by ETD week, container timing,
safety-stock vs shippable at the supply-plan/container level.

---

### FactProduction

**Grain:** Production Resource × Item × Location × Fiscal Week — capacity, conversion, planned vs
firm production/manufacturing orders.

**Source base object(s):** `Supplychain_History.ProductionCapacity`; `SupplyChain_Enh.ProductionConversion`
(5 models); `SupplyChain_Enh.ProductionResourcePlan`; `Manufacturing_ProductionPlanning_AFI.MOMAST`
(manufacturing orders); `PowerBI_SupplyChain.SCPPurchaseOrders_AFI` (planned POs).

**Snapshot strategy:** `latest` capacity snapshots; transactional MO/PO.

**Replaces report tables:** ProdCapacity, Forecast (Prod Cap vs Forecast), MOrds, POrds, PlandSupply,
Production Resource Master.

**Questions answered:** Production capacity vs forecast/plan; firm MO + firm PO vs planned; open
capacity by plant/resource.

---

### FactReceipts

**Grain:** Item × Warehouse/House × Vendor × Receipt date — vendor shipments, receipts,
in-transit/on-order.

**Source base object(s):** `Manufacturing_Inventory_*.IMHIST` (IMHIST receipts, exact-dup
`a36c42f779a8`); `Wholesale_ProductSourcing_AFI.PoDetail`/`PoMaster` (PO receipts);
`PowerBI_SupplyChain.Receipts`/`TotalReceipts`/`PurReceipts`; `Inventory_DW.FactPurchasingPurchaseOrders`.

**Snapshot strategy:** transactional / `latest`.

**Replaces report tables:** VendorShipped, Receipts, On-Order/In-Transit, Query1-3 (Receipts model),
z_ItLocPr.

**Questions answered:** Receipts into warehouse (PO vs MO), vendor-shipped vs ETA, on-order /
in-transit balance.

---

### FactOnTime

**Grain:** Shipment / Invoice line × Customer × Item × Promise/Request date — on-time delivery and
supplier on-time performance.

**Source base object(s):** `AFISales_Enh.OnTimeDeliveryDetail` (customer on-time);
`AFISales_DW.FactShippedHistory`; `Wholesale_SalesHistory_AFI.InvoiceDetail`/`InvoiceHeader`;
supplier on-time derived from PSW firm-vs-ship.

**Snapshot strategy:** transactional.

**Replaces report tables:** On Time (day), On Time (week), WH335OnTime, Ashton_Ontime By Vendor,
On Time per-vendor measures.

**Questions answered:** On-time % vs original/current promise and request date (day and week
grain); average days late; supplier on-time % and delay penalties.

---

## Out-of-first-release facts

Single-model operational extracts — warehouse-management inventory aging
(`Distribution_Warehouse_Wholesale.t_stored_item`/`TranLog`), inventory-transaction weekly summary,
Amazon POS/inventory/forecast (`SupplyChain_Enh.AmazonCustomer*`), and the "When to Disco"
composite — are documented in the Phase 1 summaries. They are candidate silver passthroughs, not
first-release conformed facts.
