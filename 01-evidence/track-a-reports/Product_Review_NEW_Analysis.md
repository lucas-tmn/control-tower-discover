# Product Review (NEW) — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `445df8fa-a5d6-42a9-97c8-d8467f16ea2b`  
**Report ID:** `75a6f209-2fc5-4797-b245-b79aba4b917e`  
**Analysis Date:** 2026-07-08  
**Model Size:** 40 tables (15 data + 5 dim + local date tables); 127 DAX measures total (111 in `_Measures` + 16 across 4 other tables)

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For a given item/series, what is demand trajectory vs. forecast vs. supply coverage — and is the item meeting its lifecycle expectations?

**Primary purpose:** Weekly/monthly product lifecycle review — "is this item healthy, growing, at-risk, or ready to exit?" — spanning new items (<9 months invoiced), current SKUs, and items entering discontinuation.

**Chain links served (all active):**

| Link | How served |
|---|---|
| **Demand** | `OrdHist` req orders (3-year history), `Actuals` (invoiced/written/current req, 26 weeks), `PlacementsOverTime` at wholesale |
| **Forecast** | `FC by Customer Group` (resultant FC, future), `WeeklyForecast`, `Hist Weekly FC`, `AnnualWrkFcst_Snapshots`, `AnnualCurFcst` |
| **Inventory / Supply** | `SupplyPlanDetail` (SI, SS, PO-Firm/Plan, TI, Prod), `DemandFulfillment`, `Week_2_ATP` (in-stock events) |
| **On-time / In-stock** | `In Stock` % via `Week_2_ATP`; `Demand Fulfillment` rate |
| **Forecast accuracy** | `CustItAccy` bias at 2-week / 30d / 60d / 90d horizons |

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Adjust working annual forecast** vs. current forecast snapshot | Demand Planner / Life Cycle Planner | Weekly (cycle meeting) | **Performance/Governance** — coaching planners, aligning plan |
| **Flag item for discontinuation or accelerate exit** based on lifecycle status + demand trend | Life Cycle Planner / Category Analyst | Monthly (PLR) | **Operational** — disposition of inventory, supply halt |
| **Expedite or cancel supply** (PO/TI/Production) when SI vs. forecast coverage gap is negative | Supply Planner | Weekly | **Operational** — handle goods |
| **Intervene on wholesale placements** — address at-risk or declining placements by customer group | Customer Demand Planner | Weekly | **Operational** — handle goods |
| **Assess new product ramp** — is the new item invoicing on schedule? Is 90-day FC accurate? | Life Cycle Planner + Category Analyst | Monthly (first 9 months) | **Performance/Governance** — validate market intro thesis |
| **Build excess inventory business case** (`Excess FG $`) | Planning Manager / Finance | Ad hoc / quarterly | **Financial-Justification** — $ impact of overstock |
| **Approve or escalate safety stock changes** | Planning Manager | Monthly | **Performance/Governance** |

---

## 3. Key Metrics / Measures

### From `_Measures` table (111 measures — selected key ones)

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `Req Order` | Total requested demand (orders placed, not shipped) | Item × Warehouse × Month | `SUM(OrdHist[Order Quantity])` — 3Y window | |
| `Fut FC` | Future resultant forecast (RSLF + PROL types) | Item × CustGrp × Warehouse × Month | `SUM('FC by Customer Group'[Qty])` — latest snapshot | |
| `Act + FC` | Blended actuals (hist) + future forecast | Item × Month | Hist (FiscalMonthInd<0) + `Fut FC` | |
| `Act + FC Y0` | Current fiscal year blended | Item × Year | Yr0 actuals + Yr0 forecast | |
| `FC TY` | Total forecast this fiscal year | Item × Year | `CALCULATE([Fut FC], FiscalYearIndicator=0)` | |
| `FC Y+1` | Next fiscal year forecast | Item × Year | `FiscalYearIndicator=1` | |
| `SI` | Shippable Inventory (current week+) | Item × Warehouse × Week | `SUM(SupplyPlanDetail[SI])` where `FiscalWeekInd≥0` | |
| `On Hand` | On-hand qty (prior weeks) | Item × Warehouse | `DemandFulfillment[On Hand Qty]` `FiscalWeekInd<0` | |
| `OH + SI` | On-hand plus committed supply | Item × Warehouse | `[On Hand] + [SI]` | |
| `Demand Fulfillment` (rate) | % of demand (firm+forecast) that SI covers, clamped [0,1] | Item × Warehouse × Week | `(FirmDemand+NetForecast+SINeg)/(FirmDemand+NetForecast)` | ⚠️ see §9 |
| `In Stock` | % of weeks item was in-stock at warehouse (ATP>0) | Item × Warehouse × Month | `SUM(InStockEvent)/SUM(StockEvent)` — excludes `AFI_Item_Status="N"` | |
| `Demand Fulfillment - last 3 Mo` | DF rate restricted to last 3 fiscal months | — | `FiscalMonthInd > -3` | |
| `FC Bias - 90d` | Bias at 90-day horizon: (FC−Act)/Act | Item × CustGrp × Wh × Month | `CustItAccy[ForecastPeriod]="90Days"` | |
| `FC Bias - 30d` | Bias at 30-day horizon | — | `"30Days"` | |
| `FC Bias - 90d - last 3 Mo` | 90d bias trailing 3 months | — | `FiscalMonthInd≥-3` | |
| `FC Bias - 90d - last 12 Mo` | 90d bias trailing 12 months | — | `FiscalMonthInd≥-12` | ⚠️ spans pre/post March 2025 grain split (see §10) |
| `avg Wrk Fcst` | Monthly avg of current working 12M forecast | Item × Wh × Customer | `SUM(AnnualWrkFcst_Snapshots[Annual...])/12` | ⚠️ hardcoded `/12` |
| `avg Cur Fcst` | Monthly avg of last cycle promoted forecast | — | `SUM(AnnualCurFcst[...])/12` | ⚠️ hardcoded `/12` |
| `Seas Annualized 3 M Hist` | Seasonally-adjusted actuals × 4 → annualized | Item | 3M hist seas-adj × **4** | ⚠️ magic number `*4` — see §9 |
| `Annl C/CNW Demand` | Annualized wholesale demand | Item | `[Avg WHC Demand]*12` | ⚠️ hardcoded `*12` |
| `Excess FG $` | Dollar value of FG inventory exceeding 1.4× safety stock | Item | `[Excess Qty FG] * AVERAGE(z_ProductDetails[FOB Price])` | ⚠️ **AVERAGE bug — see §9** |
| `YTD ACT` / `YTD-1 ACT` | Year-to-date actual demand, current vs. prior year | Item × Year | `FiscalYearInd=0, FiscalMonthInd<0` | ⚠️ see §10 comparability |
| `YTD Growth` | YTD qty growth rate YoY | Item | `([YTD ACT]-[YTD-1 ACT])/[YTD-1 ACT]` | |
| `Snapshot` | Max snapshot date in FC by Customer Group | — | `MAX(SnapshotDate)` — data freshness proxy | |
| `UTC Refresh Time` | Model refresh timestamp | — | `UTCNOW()` | |
| `Projected Demand Coverage %` | Rolling cumulative supply coverage vs. demand | Item × Wh × Week | `[Projected Demand Coverage]/[RollingCumDemand]` | |
| `At Risk Placements` | Wholesale placements at risk, current week | Item × Customer | `PlacementsOverTime[At Risk Placements]`, `FiscalWeekInd=0` | |

### From other tables

| Table | Measure | Key logic |
|---|---|---|
| `SupplyPlanDetail` | `Excess Qty FG` | `SI_Overage` where `SellableItemFlag="Y"` — SI overage = `SI − (SS×1.4)`, rounded |
| `SupplyPlanDetail` | `Excess Qty Kit` | Same but `SellableItemFlag="N"`, excludes VINYL/HIDES/Swatch |
| `SupplyPlanDetail` | `Excess FG $` | `[Excess Qty FG] * AVERAGE(z_ProductDetails[FOB Price])` ⚠️ |
| `SupplyPlanDetail` | `FC Covered Date` | First week where `Item Ext Series FC Covered` = true (SI_Neg ≥ −50% net FC) |
| `SupplyPlanDetail` | `Orders Covered Date` | First week where `Item Ext Series Firm Demand Covered` = true |
| `SupplyPlanDetail` | `8wk Avg Receipt` | `SUM(NetRec)` for weeks 0–7 / 8 — hardcoded `8` |
| `AnnualWrkFcst_Snapshots` | `Plan Change` | Working FC − prior cycle snapshot FC |
| `AnnualWrkFcst_Snapshots` | `YoY%` | `(Working FC − Act Y-1) / Act Y-1` |
| `DemandFulfillment` | `Demand Fulfilment` | `(FirmDemand+NetForecast+SINeg)/(FirmDemand+NetForecast)` clamped [0,1] via IFERROR |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| `z_ProductDetails` | PowerBI Dataflow `346f2aa1...` workspace `a47e4573...` → entity `CurrentProductDetails` | Governed Dataflow | Low |
| `z_FiscalCal` | Same dataflow → `AshleyFiscalCalendarV2` | Governed Dataflow | Low |
| `z_WarehouseMaster` | Same dataflow → `WarehouseMaster` | Governed Dataflow | Low |
| `z_VendorMaster` | Same dataflow → `VendorMaster` | Governed Dataflow | Low |
| `z_CustomerMaster` | Same dataflow → `CustomerMaster_AFI` (+ hardcoded row additions in Power Query) | Governed Dataflow + inline M transform | Medium |
| `SupplyPlanDetail` | `ashley-edw.database.windows.net / ashley_edw` — `SupplyChain_Enh` supply plan table | Direct Azure SQL EDW | Medium |
| `Week_2_ATP` | Same EDW — ATP in-stock event table | Direct Azure SQL EDW | Medium |
| `FC by Customer Group` | Same EDW — `SupplyChain_Enh.DemandForecastSnapshot` | Direct Azure SQL EDW | Medium |
| `OrdHist` | Same EDW — `SupplyChain_Enh.ActualsCustItemWH_AFI` | Direct Azure SQL EDW | Medium |
| `DemandFulfillment` | PowerBI Dataflow `ccbb84a2...` (different dataflow) → entity `Demand Fulfillment` | Governed Dataflow | Low |
| `PlacementsOverTime` | Same EDW — `PowerBI_Wholesale.WeeklyPlacements` | Direct Azure SQL EDW | Medium |
| `Actuals` | Same EDW — `Wholesale_SalesHistory_AFI.InvoiceDetail` + `AFISales_DW.FactOpenOrders` | Direct Azure SQL EDW | Medium |
| `WeeklyForecast` | Same EDW — `Wholesale_DemandPlanning_AFI.DemandForecast` (latest snapshot only via `MAX(dtea)`) | Direct Azure SQL EDW | Medium |
| `Hist Weekly FC` | Same EDW — `SupplyChain_Enh.DemandForecastSnapshot` (13-week lag snapshots) | Direct Azure SQL EDW | Medium |
| `CustItAccy` | Same EDW — `DemandForecastSnapshot` + `ItemActualDemand_Logility` (UNION, split at 3/15/2025) | Direct Azure SQL EDW | Medium |
| `AnnualWrkFcst_Snapshots` | Same EDW — `fcl` table summing `Result_Fc_0` through `Result_Fc_11` + PROL columns | Direct Azure SQL EDW | Medium |
| `AnnualCurFcst` | Same EDW — `SupplyChain_Enh.CurFcstSnapshotWeekly` | Direct Azure SQL EDW | Medium |
| **`Default Planner Assignment Rules`** | **SharePoint list** — `masterashley.sharepoint.com/sites/supplychain-DemandPlanning` | **SharePoint** | ⚠️ **HIGH — ungoverned, manually maintained list** |
| **`User Information List`** | **Same SharePoint site** | **SharePoint** | ⚠️ **HIGH** |
| **`Product Journal`** | **SharePoint-hosted Excel file** — `_Product_Journal_UNIFIED_MASTER.xlsx` (path has embedded "DO NOT OPEN" warning in folder names) | **SharePoint Excel** | ⚠️ **HIGHEST — single shared Excel, manual entries, no schema enforcement** |
| `Placements ABC` | Same EDW — `PowerBI_Wholesale.WeeklyPlacements` (last-week snapshot) | Direct Azure SQL EDW | Medium |
| `Join` | Same EDW — cross-join `CustomerGroup × CC × ItemSKU` | Direct Azure SQL EDW | Low |
| **`Cycle Dates`** | **SharePoint list** — `masterashley.sharepoint.com/sites/SCPGlobalTeam/` | **SharePoint** | ⚠️ **HIGH — controls snapshot filtering for AnnualWrkFcst** |

> **Note:** No Fabric sources. All SQL queries hit `ashley-edw.database.windows.net` (Azure SQL Server) — this model has not migrated to Fabric.

---

## 5. Grain & Snapshot Strategy

**Primary grain by table:**

| Table | Grain |
|---|---|
| `OrdHist`, `FC by Customer Group`, `CustItAccy`, `AnnualWrkFcst_Snapshots` | Item SKU × Warehouse × Fiscal Month |
| `SupplyPlanDetail` | Item SKU × Warehouse × Fiscal Week |
| `Actuals`, `WeeklyForecast`, `Hist Weekly FC` | Item SKU × Warehouse × Customer Group × Fiscal Week |
| `DemandFulfillment` | Item SKU × Warehouse × Fiscal Week |
| `Week_2_ATP` | Item SKU × Warehouse × Fiscal Month |

**Snapshot strategy:** Mixed.

- `AnnualWrkFcst_Snapshots` — **explicit historical snapshots** keyed on `SnapshotDate` linked to `Cycle Dates` SharePoint list. Enables plan-vs-plan change tracking across planning cycles. **Requires** historical snapshots.
- `FC by Customer Group` — single latest-snapshot resultant FC (`MAX(dtea)` in WeeklyForecast; `DemandForecastSnapshot` for monthly).
- `Hist Weekly FC` — historical 90-day-lag forecast snapshots (13-week lookback join). Enables accuracy vs. what was actually forecast at the time.
- `CustItAccy` — pre-built accuracy snapshot in EDW at specific lag dates (day+15 of prior month per horizon).
- `SupplyPlanDetail` has a `Snapshot Date` column but no DAX measures filter on it — unclear if EDW returns latest-only or multiple runs.

---

## 6. Dimensions Used

| Dimension | Table | Notes |
|---|---|---|
| **Product** | `z_ProductDetails` (109 cols) | Item SKU, series, collective class, lifecycle status, kit flag, sellable flag, brand flags (F123, HS, Berkline, Benchcraft, New Millennium, Bardini, Shanghai Store flags), FOB Price, Market Begin/End Date |
| **Date / Fiscal Calendar** | `z_FiscalCal` (43 cols) | Conformed — fiscal week/month/quarter/year indicators (relative: 0=current, −1=last, +1=next), rolling 12-month year calc, holiday indicators |
| **Warehouse** | `z_WarehouseMaster` (11 cols) | Warehouse group (C/CNW = wholesale), controlled flag, sort order |
| **Vendor** | `z_VendorMaster` (11 cols) | Reference — linked via `z_ProductDetails[Primary Vendor]` |
| **Customer** | `z_CustomerMaster` (40 cols) | Account, ship-to, customer group, planner filter |
| **Production Resource** | Not present | `SupplyPlanDetail` has Prod-Firm/Plan columns but no production resource dimension table |

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `Life Cycle Status` | `z_ProductDetails` calc column | `FutureStatus` in {F,P,L,E} → "Drop"; `InvoicingMonths` ≤ 9 → "New (inv < 9 M)"; else "Current" | **High** — 9-month threshold hardcoded; silent misclassification if business definition changes |
| `Invoicing Months` | `z_ProductDetails` calc column | `DATEDIFF(MAX(FC SnapshotDate), InitialInvoiceMonth, MONTH)` — relative to FC snapshot date, not today | **High** — value shifts depending on visual filter context |
| `Kit Flag` | `z_ProductDetails` calc column | SKU suffix: `M*UN` → Bedding Kit; `*UN` → UPH Kit; `*SW` → Swatch; `*HIDES`/`*VINYL` | Medium — SKU suffix conventions could change |
| `z_LeatherFlag` | `z_ProductDetails` calc column | `SWITCH` against 13 hardcoded Item Class Codes | Medium |
| `Storage Type` | `z_ProductDetails` calc column | Collective Class SWITCH; OUTDOOR + Cubes > **13** → UPH, else CSG | Medium — cube threshold **13** undocumented |
| `Status (groups)` | `z_ProductDetails` calc column | Concatenated `Current+Future Status` two-char codes → 5 groups (CURRENT / DISCO / DROPPED / LIQUIDATED / NEW) | Medium — breaks silently if status codes change |
| `Avg Sales Price` | `z_ProductDetails` calc column | `Actuals[Amt]/Actuals[Qty]` with `REMOVEFILTERS(z_FiscalCal)` (all-time avg); falls back to FOB Price if 0 | Medium — no recency weighting; used in `$ Fut FC` via `Est Amt` |
| `Rolling 12 Month Year` | `z_FiscalCal` calc column | `FLOOR((FiscalMonthInd+7)/12, 1)` — offset of 7 | Medium — offset undocumented; effectively starts rolling year 7 months prior |

---

## 7. Duplication / Consolidation Signals

1. **Two demand fulfilment implementations:** `DemandFulfillment[Demand Fulfilment]` (DAX measure, clamps [0,1] with IFERROR) vs. `SupplyPlanDetail[Demand Fulfillment]` (raw source column from EDW). Same concept, two paths. Note spelling difference: "Fulfilment" (1-l) vs "Fulfillment" (2-l) — easy to confuse in measure references.

2. **Seven FC Bias variants:** `FC Bias`, `FC Bias - 30d`, `FC Bias - 90d`, `FC Bias - 30d - last 3 Mo`, `FC Bias - 90d - last 3 Mo`, `FC Bias - 90d - last 12 Mo`, `FC Bias - 90d - Y0` — all are minor CALCULATE wrappers on the same base formula. Candidate for a calculation group.

3. **YTD/YTG 3-year matrix:** `YTD ACT` / `YTD-1 ACT` / `YTD-2 ACT` / `YTG FC` / `YTG-1 ACT` / `YTG-2 ACT` + matching Growth measures = 12 measures for one pattern. Candidate for a calculation group.

4. **Parallel $ and Qty hierarchies:** `Act + FC`, `Act + FC Y0`, `$ Act + FC`, `$ Act + FC Y0`, `$ Fcst Y1`, `$ Act Y-1` — same temporal logic duplicated for qty and dollar versions.

5. **WHC Demand hardcoded 4×:** `WHC Demand`, `WHC Demand TY`, `WHC Demand LY`, `WHC Demand Hist TY`, `WHC Demand Growth` all hardcode `OR(Warehouse="C", Warehouse="CNW")` inline. If warehouse codes change, all five break independently.

6. **`DemandForecastSnapshot` queried 3×:** `FC by Customer Group`, `Hist Weekly FC`, and `CustItAccy` (post-March 2025) all independently query the same EDW table with different filters and no shared dataflow layer.

7. **`PowerBI_Wholesale.WeeklyPlacements` queried 2×:** `PlacementsOverTime` (12-month window) and `Placements ABC` (last-week only) — independent queries of the same source.

8. **Dead scaffolding:** Two blank measures named `Measure` and `Measure 2` exist in `_Measures` table — empty placeholders.

---

## 8. Open Questions

1. **`SupplyPlanDetail` latest-only or multi-snapshot?** The table has `Snapshot Date` but no DAX measures filter it. If the EDW query returns multiple supply plan runs, SI measures double-count.

2. **`Product Journal` ownership and reliability.** The SharePoint Excel path embeds folders named "DO NOT OPEN / Seriously DO NOT OPEN / GO BACK NOW / Self Destruct If Opened" — humorous but signals this file is fragile. How many planners write to it? Is it versioned? What happens when a row is deleted or incorrectly edited?

3. **`Cycle Dates` SharePoint list maintenance.** This list controls which `AnnualWrkFcst_Snapshots` rows are "working forecast" vs. historical. Who owns it, how often updated, and is it possible to go stale after a planning cycle?

4. **`WeeklyForecast` snapshot lag.** Uses `MAX(dtea)` (latest snapshot only) — mid-week refreshes before a new FC publish will show the previous cycle's forecast. Is this intended behavior? Do users see "forecast not updated yet" during transition periods?

5. **Customer exclusion `<> '3824800'`** silently applied in `Actuals`, `OrdHist` related queries — what customer is this and is the intent to permanently exclude from all demand history?

6. **Warehouse exclusion inconsistency.** `Actuals` excludes `NOT IN ('213','215','55')`; `CustItAccy` NaiveFcst excludes `NOT IN ('C','CNW','C35','55')`. Different exclusion sets for the same demand concept — intentional (different channels) or an oversight?

7. **Is this report replacing `Product Review` (the original)?** Both exist in the workspace. `Product Review (NEW)` appears to be an evolution but the naming "(NEW)" is ambiguous — permanent branding or temporary migration label? Who uses which?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| `SS × 1.4` | `SupplyPlanDetail[SI Overage]` calc column | Excess threshold: SI > 140% of safety stock triggers overstock flag | **No** — 40% buffer above SS is undocumented |
| `× 4` in `Seas Annualized 3 M Hist` | `_Measures` | Seasonally-adjusted 3-month actuals × 4 → annualized; assumes 4 equal quarters | **No** — wrong when the 3 months straddle a 5-week fiscal month (occurs 4×/year) |
| `/12` in `avg Wrk Fcst`, `avg Cur Fcst` | `_Measures` | Converts annual forecast to monthly avg | No — valid only if annual FC spans exactly 12 months; `AnnualWrkFcst_Snapshots` sums `Result_Fc_0..11` + PROL columns that may extend beyond 12 periods |
| `÷ 5` and `× 12` in `Avg WHC Demand` / `Annl C/CNW Demand` | `_Measures` | 5-month average (`FiscalMonthInd >=-3 and <=1`) then annualized ×12 | **No** — both hardcoded; wrong at fiscal year-end when fewer periods exist |
| `date(1900,1,1)` fallback | `z_ProductDetails[Initial Invoice Month]` | Items with no invoice date get 1900-01-01; `Invoicing Months` returns 0 → classified as "New" | Partially — IFERROR wraps date parse; sentinel value undocumented |
| **9 months** in `Life Cycle Status` | `z_ProductDetails[Life Cycle Status]` calc column | `InvoicingMonths ≤ 9` = "New (inv < 9 M)" | **No** — "new product" = first 9 months is hardcoded; business may have a different definition |
| **13 cubes** in `Storage Type` | `z_ProductDetails[Storage Type]` calc column | OUTDOOR items with `Cubes > 13` stored as UPH, else CSG | **No** |
| `DATEADD(day, 15, ...)` in `CustItAccy` snapshot join | SQL | Snapshot date = 15 days after start of prior fiscal month (approximates Week 3 Monday snapshot) | Partially — SQL comment says "Monday Week 3 Snapshots"; not in model |
| `DATEADD(WEEK, -13, ...)` in `Hist Weekly FC` | SQL | 13-week lookback to match 90-day (12wk) forecast snapshot | **No** — 13 weeks = 91 days ≠ 90 days; undocumented approximation |
| `FiscalWeekIndicator BETWEEN -26 AND 0` | `Actuals` SQL (Invoiced leg) | 26-week history window for weekly actuals | **No** |
| `FiscalWeekIndicator BETWEEN -26 AND 13` | `Actuals` SQL (Written / Current Request legs) | Future window extends to +13 weeks for open orders | **No** |
| **`'3/15/2025'`** hard cutover | `CustItAccy` SQL (`WHERE Snapshot Date >= '3/15/2025'` / `< '3/15/2025'`) | Splits accuracy table into pre/post: before = Item×WH grain; after = Customer×Item×WH grain | Partially — SQL comment documents intent; not exposed in model metadata |
| `offset +7` in `Rolling 12 Month Year` | `z_FiscalCal` calc column | `FLOOR((FiscalMonthInd+7)/12)` — shifts rolling year window by 7 months | **No** — undocumented; effectively starts rolling year 7 months prior |
| `AVERAGE(z_ProductDetails[FOB Price])` in `Excess FG $` | `SupplyPlanDetail` table measure | Multiplies excess qty by **average FOB Price across all products in visual context** | ⚠️ **BUG** — `AVERAGE` of a per-item price produces a blended rate when multiple items shown; should be `RELATED()` or a row-level calculated column |

**Dollar-value business impact calculation:**

```
Excess FG $ = [Excess Qty FG] × AVERAGE(z_ProductDetails[FOB Price])

where:
  Excess Qty FG = SUM(SupplyPlanDetail[SI Overage]) where SellableItemFlag = "Y"
  SI Overage    = ROUND(IF(SI > SS × 1.4, SI − (SS × 1.4), 0), 0)
```

**Unverified assumptions this rests on:**
- 1.4× SS is the agreed excess threshold (undocumented)
- FOB Price is a valid proxy for inventory carrying value (no markdown applied)
- Items are expected to sell at full FOB (no liquidation discount)
- `AVERAGE(FOB Price)` across items in context == item's own FOB Price (**false when multiple items shown**)

This number likely feeds executive overstock business cases. The AVERAGE aggregation bug makes it unreliable at any view above single-item level.

---

## 10. Comparability / Consistency

1. **`CustItAccy` structural break at 3/15/2025.** Pre-cutover rows are `Item × Warehouse` grain with `Customer Group = 'AFICONS'` (synthetic placeholder). Post-cutover rows are `Item × Warehouse × CustomerGroup` grain with real customer groups. Any metric filtered by Customer Group (e.g., `FC Bias - 90d` by customer) shows **no data before March 2025** for non-AFICONS customers and **all demand under AFICONS** for historic periods. `FC Bias - 90d - last 12 Mo` spans both sides — its 12-month trailing view mixes two structurally different grains, making the trend line incomparable end-to-end.

2. **`YTD-1 ACT` comparability at start of fiscal year.** `YTD-1 ACT = CALCULATE([Req Order], FiscalYearInd=-1, FiscalMonthInd < -12)`. At the start of the fiscal year, both `YTD ACT` and `YTD-1 ACT` are near-zero → `YTD Growth` and `YTD-1 Growth` produce extreme or undefined values until meaningful months accumulate.

3. **`Fut FC` vs. `FC TY` vs. `PROL Y0` mixing forecast types.** `Fut FC` = all Datatypes; `PROL Y0` = only `Datatype="PROL"`; `Fut RSLF` = only `"RSLF"`. Neither PROL nor RSLF is labeled in the model — unclear whether "PROL" = promotional lift or a separate planning scenario. Any comparison mixing these measures is inconsistent without that definition.

4. **`Actuals` (week-grain, `InvoiceDetail`) vs. `OrdHist` (month-grain, `ActualsCustItemWH_AFI`) both representing demand.** At month level they may not reconcile — different source tables, different warehouse and customer exclusions. A user comparing `Req Order` trend to `Weekly Inv Qty` trend may see different numbers for the same period with no warning.

5. **`Seas Annualized 3 M Hist` (×4) vs. `Seas Annualized 3 M FC` (months 0–3).** Different seasonal adjustment sources (historic seas-adj order qty vs. seas-adj forecast qty) and different annualization assumptions. Presented together as comparable annualized trend measures but methodologically different.

6. **`Life Cycle Status` age clock based on FC snapshot date, not today.** `Invoicing Months = DATEDIFF(MAX(FC SnapshotDate), InitialInvoiceMonth, MONTH)`. If the FC snapshot is from last week, a product's "age" reflects last week's snapshot — not actual elapsed time. This means filtering on different snapshot dates (e.g., via `Cycle Dates` slicer) produces different lifecycle classifications for the same item.

---

## Closing — Interview Seeds

> Direct questions for a follow-up interview with the actual business user. Targeting what the model cannot confirm alone.

1. **"When you see an item with a negative Demand Fulfillment rate or an 'FC Covered Date' more than 4 weeks out, what is the first physical action you take — and do you do it in Power BI, in Logility, via email, or in a Teams chat?"**
   *(Targets: trigger-to-action gap, tool handoff outside Power BI, whether the report drives decisions or confirms them.)*

2. **"The Product Journal Excel file — has it ever had a wrong entry, a deleted row, or a version conflict? And when that happens, does anyone know the report pulled bad data?"**
   *(Targets: data trust in the ungoverned SharePoint Excel source; escalation path when the file breaks.)*

3. **"The `Excess FG $` number — has it ever been presented to a VP or used in a budget or business case? If so, was the FOB Price figure challenged or validated against actual landed cost or expected sell-through price?"**
   *(Targets: whether the financially-material measure with the AVERAGE aggregation bug has fed executive decisions; surfaces the risk if confirmed.)*

4. **"Before March 2025, Forecast Accuracy was tracked at Item×Warehouse level. Since then it's at Customer×Item×Warehouse. If someone asks 'how has our 90-day bias trended over the past 12 months by customer' — do you trust that trend line, and do you know it's mixing two different measurement grains in the same chart?"**
   *(Targets: user awareness of the pre/post-March 2025 structural break; whether planning decisions are being made on an incomparable trend series.)*

---

*Analysis based on BIM definition extracted 2026-07-08. No bundle indexes were modified.*
