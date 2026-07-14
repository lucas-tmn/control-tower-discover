# Forecast Accuracy (ItWh) — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `e53895de-d652-4f1e-8a9c-962cca4fece8`  
**Report ID:** `ae8f2774-70eb-464f-9204-5803782f2fe3`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~1.72 MB (BIM); 23 tables, 25 DAX measures in `_Measures` + 1 in `Acceptable Abs Bias`

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "How accurately did Logility forecast demand at the Item SKU × Warehouse grain — across five lag horizons (2-week, 30-day, 60-day, 90-day, **120-day**) — and does the Logility forecast outperform a naïve carry-forward baseline over the trailing 12 months?"

**Primary chain link:** **Forecast**  
A pure forecast-accuracy scorecard at the Item × Warehouse level, one dimension coarser than the sibling "Forecast Accuracy (Cust_ItWh)" report. Unlike that model, this one adds a **120-day lag horizon** and an **inventory-segmentation dimension** (`InvSegGlobalCC`) to slice accuracy by item archetype, forecastability class, lifecycle, and margin cube.

Secondary links touched:
- **Demand** — actual demand from `ItemActualDemand_Logility` is the accuracy denominator
- **Inventory segmentation** — `InvSegGlobalCC` (ABC/XYZ, lifecycle, forecastability) enriches the product dimension; no supply/inventory action measures present

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Identify items with persistent bias** — `90D Sku Bias` + `90D Over/Under` flag items for model override in Logility | Demand Planner / FC Analyst | Monthly (post-cycle) | Performance/Governance |
| **Assess Logility value-add vs. naïve baseline by segment** — `wMAPE Value Add` / `wMAPE vs Naive` (same measure) shows whether Logility beats carry-forward, sliceable by lifecycle, forecastability, ABC/XYZ | Supply Chain Manager / Analyst | Monthly / quarterly | Performance/Governance |
| **Evaluate accuracy at new 120-day horizon** — unique to this model vs. Cust_ItWh; supports long-lead-time sourcing decisions where a 3–4 month forward view is needed | Supply Chain Manager / Logistics Planner | Monthly | Performance/Governance |
| **Segment accuracy by inventory archetype** — `Segmentation Parameter` slicer (ABC/XYZ, Lifecycle, Forecastability, MarginCube, Volume) surfaces which item segments drive forecast error | Analyst / Supply Chain Manager | Monthly / quarterly | Performance/Governance |
| **Coach or reassign Category Analyst** — `Demand Planner Assignment Rules` maps Collective Class → Category Analyst; accuracy can be filtered by analyst to identify accountability gaps | Supply Chain Manager | Quarterly | Performance/Governance |
| **Track accuracy by item lifecycle status** — `Month End Status Snapshots` allows segmenting accuracy for items that were IN LINE, being DROPPED, DISCO, or NEW at the time of forecast | Category Analyst | Monthly | Performance/Governance |
| **Set custom bias alert threshold** — `Acceptable Abs Bias` slicer (0–30%, step 1%) allows user to define the acceptable tolerance for `Over/Under` classification | Demand Planner / Analyst | Per session | Performance/Governance |

**No Operational or Financial-Justification decisions are directly supported.** All decisions manage the planning process quality, not inventory movement or investment cases.

---

## 3. Key Metrics / Measures

### Core Accuracy Measures

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Forecast` | Sum of Logility forecast qty | Item × WH × fiscal month × lag period | `SUM(ItWHAccy[Total Forecast])` — `dfcResultantForecast + dfcPromotionalLift` |
| `Actuals` | Sum of actual demand | Same grain | `SUM(ItWHAccy[Actual Demand])` — from `ItemActualDemand_Logility` |
| `Error Qty` | Raw forecast error (Fcst − Actual) | Same | `[Forecast] - [Actuals]` |
| `Bias %` | Directional bias % | Same | `DIVIDE([Error Qty], [Actuals])` |
| `Abs Error (It_wh)` | Absolute error at Item × WH grain | Item × WH | `SUM(ItWHAccy[ABS(Error)])` — row-level sum |
| `Abs Error (It)` | Absolute error collapsed to Item grain | Item × fiscal month | `SUM(ItErr[Abs Error])` — from `ItErr` calculated table which first SUMs across warehouses |
| `ABS Percent Error` | Aggregate WAPE (not MAPE) | Aggregated | `DIVIDE(ABS([Actuals]-[Forecast]),[Actuals])` — **⚠️ same ambiguity as CustItWh model: name says "Percent Error" but is aggregate WAPE** |
| `wMAPE` | Weighted MAPE — row-average ABS error / row-average demand | Row-aggregated | `DIVIDE(AVERAGEX(ItWHAccy,[ABS(Error)]), AVERAGEX(ItWHAccy,[Actual Demand]))` |
| `MAPE` | Simple unweighted MAPE | Row-aggregated | `AVERAGEX(ItWHAccy,[ABSPError])` where `ABSPError = ABS(Error)/Actual Demand` per row — **⚠️ inflated by low-volume rows** |
| `RSME` | Root Mean Square Error at item level | Item | `SQRT(AVERAGEX(ItErr, POWER([Error Qty], 2)))` — note: name says "RSME" not "RMSE" (transposed letters); uses `[Error Qty]` measure in `ItErr` context |

### Naïve Benchmark Measures — `(N)` prefix

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `NaiveFcst` / `(N)Forecast` | Naïve carry-forward forecast (v1) | Item × WH × fiscal month | `SUM(ItWHAccy[NaiveFcst])` — prior month actuals ÷ NumWeeks × NumWeeks of target month; joined on `FiscalMonthIndicator+1 = target month` |
| `(N)Error` | Naïve forecast error | Same | `SUM(ItWHAccy[(N)Error])` = `NaiveFcst - Actual Demand` |
| `(N)Error %` | Naïve bias % | Same | `DIVIDE([(N)Error],[Actuals])` |
| `(N)Mean ABS Dev` | Average absolute naïve error | Row-level | `AVERAGEX(ItWHAccy, [(N)ABS(Error)])` |
| `Naive wMAPE` | Naïve wMAPE (benchmark to beat) | Row-aggregated | `DIVIDE([(N)Mean ABS Dev], [Mean Act Dmd])` |
| `wMAPE Value Add` | How much better Logility is vs. naïve | Same | `[wMAPE] - [Naive wMAPE]` — **negative = Logility better** |
| `wMAPE vs Naive` | **Identical to `wMAPE Value Add`** | Same | `[wMAPE] - [Naive wMAPE]` — **exact duplicate measure (see §7)** |
| `Error vs Naive` | Logility bias improvement vs. naïve bias | Same | `ABS([Bias %]) - ABS([(N)Error %])` |

### NaiveFcst_v2 — Second Naïve Variant

`ItWHAccy` contains a second naïve forecast column, `NaiveFcst_v2`, sourced from subquery `NF_2` in SQL. It uses the **same SQL logic** as `NaiveFcst` (same warehouse exclusions, same prior-month calculation) but joined on a **different key**:

| | Join key (month field) |
|---|---|
| `NaiveFcst` (NF) | `FiscalMonthIndicator+1 = target FiscalMonthIndicator` — "what month the naive covers" |
| `NaiveFcst_v2` (NF_2) | `Snapshot Year Month = FiscalMonthYear` — "what month the forecast was issued" |

`NaiveFcst_v2` is loaded as a column in the table but **no DAX measure references it**. It appears to be an in-development alternate naive definition that was never wired into any measure. It is dead weight consuming model memory.

### Threshold & Parameter Measures

| Measure | Value | Notes |
|---|---|---|
| `Bias Threshold` | **`0.08`** (8%) | Hardcoded literal; used in `Over/Under` column and `90D Over/Under`. **⚠️ Different from CustItWh model which uses 0.10 (10%)** — same concept, different thresholds across sibling models |
| `Parameter Value` | `SELECTEDVALUE('Acceptable Abs Bias'[Parameter])` | User slicer 0–30% in steps of 1% |
| `Measure` | **(empty expression)** | Placeholder measure with no logic — dead code |
| `Item Error` | **(empty expression)** | Placeholder measure with no logic — dead code |
| `Refresh Date` | `CALCULATE(MIN(z_FiscalCal[Transaction Date]), REMOVEFILTERS(z_FiscalCal), z_FiscalCal[Fiscal Day Indicator] = 0)` | **⚠️ Different from CustItWh model** which uses `FiscalDayIndicator = -1 then +2`. This model uses `FiscalDayIndicator = 0` with no offset — "today" rather than "yesterday+2". Same measure name, different date logic across models. |

### Row-Level Calculated Columns (ItWHAccy)

| Column | Logic | Notes |
|---|---|---|
| `Error` | `Total Forecast - Actual Demand` | |
| `ABS(Error)` | `ABS(Actual Demand - Total Forecast)` | Subtraction reversed vs. Error — same magnitude |
| `ABSPError` | `DIVIDE(ABS(Error), Actual Demand)` | Per-row MAPE input; BLANK when Actual Demand = 0 |
| `(N)Error` | `NaiveFcst - Actual Demand` | |
| `(N)ABS(Error)` | `ABS((N)Error)` | |
| `Over/Under` | `Error/Actual Demand > 0.08 → "Over"; < -0.08 → "Under"; else "Even"` | Uses hardcoded `[Bias Threshold]` = 0.08 |
| `FcstPeriod` | Sort-prefix version: `"____120Days"`, `"___90Days"`, `"__60Days"`, `"_30Days"`, `"2Week"` | Display sort hack; 120Days now present (not in CustItWh) |
| `It-Whse` | `Item SKU & "_" & Warehouse` | Composite key used for... undetermined; no relationship or measure references it |
| `NaiveFcst_v2` | From SQL `NF_2` subquery | **Dead column — no measure references it** |
| `Snapshot Year Month` | `(YEAR(dfcSnapshot)*100) + MONTH(dfcSnapshot)` | Integer YYYYMM of snapshot date; used only as `NF_2` join key |

### Calculated Columns (z_ProductDetails)

| Column | Logic | vs. CustItWh model |
|---|---|---|
| `PR Categories` | Maps Collective Class → `RTA`, `CASEGOODS`, `MOTION`, `STATIONARY`, `Accents` (lowercase), passthrough for others | Bucket label `"Accents"` (mixed case) vs. `"ACCENTS"` (uppercase) in CustItWh. `"RTA"` here vs. `"RTA & METAL BEDS"` in CustItWh. `METAL BEDS` → `CASEGOODS` here vs. `"RTA & METAL BEDS"` in CustItWh. |
| `Collective Class (groups)` | ACCENTS, CASEGOODS, **HO WALL OCC** (new), OTHER, **RTA & METAL BEDS** | Adds `"HO WALL OCC"` bucket for HOME OFFICE / OCCASIONAL TABLES / WALL & ENTERTAINMENT — this bucket does not exist in CustItWh's version |
| `90D Sku Bias` | `DIVIDE(CALCULATE([Forecast], 90Days, FiscalMonthIndicator>=-6), CALCULATE([Actuals], 90Days, FiscalMonthIndicator>=-6)) - 1` | Identical logic to CustItWh but references `[Forecast]`/`[Actuals]` measures (ItWh names) vs. `[Total Forecast]`/`[Total Demand]` (CustItWh names) |
| `90D Over/Under` | `90D Sku Bias > [Bias Threshold] → "Over"; < -[Bias Threshold] → "Under"; "Even"` | Threshold 0.08 here vs. 0.10 in CustItWh — same concept, different cutoffs |

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `ItWHAccy` | `SupplyChain_Enh.DemandForecastSnapshot` (forecast), `SupplyChain_Enh.ItemActualDemand_Logility` (actuals), `SupplyChain_Enh.ActualsCustItemWH_AFI` (naive), `Enterprise_DW.dimDate_nonRetail`, `Enterprise_DW.DimDate` | Complex multi-join; 1-hour `CommandTimeout`; **no UNION ALL split** — single grain throughout (Item × WH only, no Customer Group) |
| Same EDW | `Month End Status Snapshots` | `PowerBI_SupplyChain.DemandFulfillmentCommonContainer_Logility`, `PowerBI_SupplyChain.CurrentProductDetails`, `Enterprise_DW.DimDate` | Same query as CustItWh model — identical source |

### Power BI Dataflows (semi-governed)

| Dataflow | Tables fed | Notes |
|---|---|---|
| `a47e4573` workspace / `346f2aa1` dataflow | `z_ProductDetails`, `z_FiscalCal`, `z_WarehouseMaster`, `z_VendorMaster` | Same shared conformed dimension dataflow used across all SC models. `z_VendorMaster` added here — not present in CustItWh model |
| `f0e1bc90` workspace (this workspace) / `2de5b43a` dataflow | `InvSegGlobalCC` | Inventory segmentation dataflow unique to this model in the accuracy family; connects via `PowerPlatform.Dataflows` |

### SharePoint (ungoverned) ⚠️

| Source | Table | Content | Risk |
|---|---|---|---|
| `masterashley.sharepoint.com/sites/supplychain-DemandPlanning` | `Users` | List ID `95e7d6e4` — username → PlannerName | **Medium** — same risk as CustItWh |
| Same site | `Demand Planner Assignment Rules` | List ID `531a515e` — same list as CustItWh's `PlannerAssignment`, but this model pulls **only** `CollectiveClass` + `CategoryAnalystId` (deduplicated), discarding LifeCyclePlanner, FCAnalyst, CustDemandPlanner | **Medium** — subset of same list; deduplication by CollectiveClass means one Category Analyst per CC |

**Comparison:** CustItWh model uses all four planner roles; ItWh model uses only Category Analyst. Both read the same SharePoint list but extract different columns.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Item SKU × Warehouse × Fiscal Month × Forecast Horizon (2-week / 30-day / 60-day / 90-day / 120-day)

Coarser than CustItWh (no Customer Group dimension). Five lag horizons vs. four in CustItWh — the 120-day horizon is unique to this model.

**No UNION ALL split** (unlike CustItWh): this model has a single query branch throughout — there is no pre/post March 2025 structural grain change. The Item-WH grain was always available regardless of when Customer Group data became available.

**Snapshot strategy:** Accumulative trailing 12 months (`FiscalMonthIndicator between -12 and -1`). `Snapshot Date` column retained, enabling cycle-over-cycle trend analysis. No "latest only" simplification is appropriate.

---

## 6. Dimensions Used

| Dimension | Source | Local re-derivations / drift risks |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow) | `PR Categories` and `Collective Class (groups)` — two independent groupings with different bucket names/logic vs. CustItWh model (see §7). `90D Sku Bias` and `90D Over/Under` locally derived. `z_ItemFilter = ISNUMBER([Forecast])` filters to items with accuracy data. |
| **Date / Fiscal Calendar** | `z_FiscalCal` (dataflow) | Same conformed dataflow as CustItWh. |
| **Warehouse** | `z_WarehouseMaster` (dataflow) | Same conformed dataflow. Warehouses C, CNW, C35, 55 excluded from naïve forecast SQL but included in accuracy data. |
| **Vendor** | `z_VendorMaster` (dataflow) | Added vs. CustItWh — linked via `z_ProductDetails[Primary Vendor] → z_VendorMaster[VendorNumber]`. `VendorDesc` exposed as grouping option in `Group By 1/2`. |
| **Inventory Segmentation** | `InvSegGlobalCC` (in-workspace dataflow) | ABC/XYZ, Level1/Level2 Archetype, LifecycleParameter, ForecastabilityParameter, VolumeParameter, GlobalMarginCubeParameter, MarginCubeParameter. Linked via `InvSegGlobalCC[ItemSKU] → z_ProductDetails[Item SKU]`. `Segmentation Parameter` calculated table exposes these as a user-selectable slicer. |
| **Category Analyst / Planner** | `Demand Planner Assignment Rules` (SharePoint) | `Collective Class → Category Analyst` only; direct relationship `z_ProductDetails[Collective Class] → DPARule[CollectiveClass]` is active. Simpler than CustItWh's PlannerAssignment which maps on `CustGrp-CC`. |
| **Item Lifecycle Status** | `Month End Status Snapshots` (EDW) | Same query as CustItWh. `Status Snapshot` column locally derived (see §7 for duplicate note). |

---

## 7. Duplication / Consolidation Signals

1. **`wMAPE Value Add` and `wMAPE vs Naive` are identical measures:**  
   Both return `[wMAPE] - [Naive wMAPE]` — exact same expression, different names. One is dead code.

2. **`NaiveFcst` and `(N)Forecast` are identical measures:**  
   Both return `CALCULATE(SUM(ItWHAccy[NaiveFcst]))` — same pattern as CustItWh model's duplicates.

3. **`NaiveFcst_v2` column — loaded but never used:**  
   SQL subquery `NF_2` runs the same naïve calculation as `NF` but joins on `Snapshot Year Month` instead of fiscal month target period. The column is materialized in the model but no DAX measure references it. Wastes query execution time and model memory.

4. **`Measure` and `Item Error` — empty placeholder measures:**  
   Two measures with no expression body. Likely created as stubs and never deleted.

5. **`Month End Status Snapshots` SQL is copy-pasted from CustItWh model verbatim:**  
   Including the typo `FutreDropFlag` (should be `FutureDropFlag`), the same Monday-snapshot logic (`dateadd(day,-5,FiscalMonthLastDate)`), and the same `Status Snapshot` SWITCH expression with duplicated `"DISCO"` branch. A governed shared table would eliminate this.

6. **`PR Categories` vs. CustItWh's `Planning Categories` — same concept, different names and mappings:**  
   Both group `Collective Class` into planning buckets but with divergent outputs (see §10). These should be a single shared defined hierarchy in the conformed `z_ProductDetails` dataflow.

7. **`Collective Class (groups)` — same column name as CustItWh but different bucket content:**  
   Adds `"HO WALL OCC"` bucket absent in CustItWh. An item in HOME OFFICE will classify differently depending on which model is queried.

8. **`Group By 1` and `Group By 2` — near-identical:**  
   Same grouping options with different default sort order, identical to the pattern in CustItWh. Both expose `PR Categories` (vs. `Planning Categories` in CustItWh), confirming the column name divergence.

---

## 8. Open Questions

1. **Is the 120-day horizon actively reviewed?** It exists in `ItWHAccy` (via the `ForecastPeriod = '120Days'` UNION branch) and in `FcstPeriod` sort column, but there are no 120-day-specific DAX measures (analogous to `FC Bias - 90d` measures in Demand Review). Is this horizon used in any report visual?

2. **What does `NaiveFcst_v2` represent?** The join on `Snapshot Year Month` (when the forecast was issued) vs. `NaiveFcst` (what month the forecast covers) suggest an attempt to build a "naïve for the cycle" concept vs. a "naïve for the period" concept. Was this in-development and abandoned?

3. **`It-Whse` composite key column — where is it used?** It concatenates `Item SKU + "_" + Warehouse` but no relationship or measure references it in this model. Tooltip? External tool? Or orphaned development artifact?

4. **Who owns this report vs. CustItWh?** Both are in the same workspace with overlapping scope. Is ItWh the "older" version that CustItWh replaced at customer-group level? If so, are there plans to retire ItWh once customer-group accuracy is fully adopted?

5. **Does `Demand Planner Assignment Rules` intentionally drop LifeCyclePlanner and FC Analyst?** The CustItWh model's equivalent table (`PlannerAssignment`) pulls four planner roles; this model pulls only Category Analyst. Was this deliberate simplification or an oversight?

6. **Is `RSME` (typo for RMSE) actively used?** It's the only RMSE-family measure in any of the three accuracy models — unique to this report. Was it requested by a specific user, and do they know the name is transposed?

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `0.08` (8%) | `Bias Threshold` measure; `Over/Under` column; `90D Over/Under` | Classifies items as Over/Under-forecasting | **No** — hardcoded literal; **different from CustItWh's 0.10 (10%)**. Same concept, different threshold. No business rationale visible for either value. |
| `-6` months | `90D Sku Bias` calculated column | Restricts SKU-level 90-day bias to trailing 6 months | **No** — same as CustItWh; creates a different look-back vs. main measures (12 months). Undocumented. |
| `dateadd(day, 15, FiscalMonthFirstDate)` | Snapshot date derivation (all 5 lag periods) | Default "3rd Monday" snapshot approximation | **Partially** — SQL comment labels it. Not always accurate (corrected by CASE blocks). |
| `'01/25/2025'` (year typo) | CASE block for all 5 lag periods | Intended as Feb 2026 cycle deviation trigger | **Bug** — same year-2025 typo as CustItWh model. Both models share this error, meaning the Feb 2026 cycle deviation override is silently not applied in either. |
| `'3/10/2025' → '3/24/2025'` | 120-day CASE block only | Unique deviation for March 2025 at 120-day lag | **Partially** — no comment explaining why March 2025 specifically needed a 120-day deviation. Not present in other lag periods. |
| `FiscalDayIndicator = 0` | `Refresh Date` measure | Gets "today" from fiscal calendar for data freshness label | **No** — differs from CustItWh's `FiscalDayIndicator = -1 then +2`. No documentation of which is correct. |
| `lag120d.[FiscalMonthIndicator]+4` | 120-day lag join | Joins 4 months back for 120-day horizon | **No comment** — consistent with 90-day (+3), 60-day (+2), 30-day (+1), 2-week (+0) pattern; mathematically expected. |
| `WHERE [ACT].[Warehouse] NOT IN ('C','CNW','C35','55')` | Naïve forecast SQL | Excludes container/special warehouses from naïve baseline | **No comment** — same as CustItWh. Container and WH 55 excluded from naïve but included in accuracy numerator/denominator. |
| `[IAD].[Company] = 'AFI'` | Actuals SQL | Filters to AFI company only | **No comment** — silent constant filter. |

**120-day column alias bug:** The `ForecastPeriod = '120Days'` UNION branch names its snapshot column `[90Days]` (copy-paste error from the 90-day block). The outer join uses `[SnapshotDate]` from `ForecastTimePeriods` CTE, so Power BI picks it up correctly from the CTE alias — the column alias mistake is internal to the CTE UNION and does not propagate to the outer query column name. However it is a maintenance risk: anyone editing this SQL CASE block could be confused by the wrong alias.

**Dollar-value business impact:** This model does **not** calculate any dollar-value impact. `InvSegGlobalCC` carries revenue, COGS, margin, and margin-cube fields but no DAX measure in this model multiplies accuracy error by any $ value. The segmentation is used purely to slice accuracy metrics, not to compute a $ impact of accuracy improvement.

---

## 10. Comparability / Consistency Issues

### a. `Bias Threshold` is 0.08 here vs. 0.10 in CustItWh — same `Over/Under` concept, different cutoffs

An item can be classified "Even" in this model but "Over" in CustItWh for a bias of 9%. A cross-report comparison of Over/Under counts is meaningless without knowing which threshold was applied. Neither model documents the rationale for its threshold.

### b. `PR Categories` vs. `Planning Categories` — same column, different names and different bucket outputs across models

| Collective Class | ItWh `PR Categories` | CustItWh `Planning Categories` |
|---|---|---|
| METAL BEDS | `CASEGOODS` | `RTA & METAL BEDS` |
| Any `*RTA` | `RTA` | `RTA & METAL BEDS` |
| ACCESSORIES | `Accents` (mixed case) | `ACCENTS` (upper case) |
| OCCASIONAL TABLES | passthrough | `CASEGOODS` |

An analyst comparing accuracy for METAL BEDS between the two reports will see it in different categories. No shared governed definition exists.

### c. `Collective Class (groups)` differs between models

| Bucket | ItWh | CustItWh |
|---|---|---|
| `HO WALL OCC` | Exists (HOME OFFICE, OCCASIONAL TABLES, WALL & ENTERTAINMENT) | Does not exist — these pass through as individual classes |
| `CASEGOODS` | BEDROOM + DINING only | BEDROOM + DINING only (same) |

An item in OCCASIONAL TABLES will appear in `HO WALL OCC` in ItWh and as uncategorized in CustItWh.

### d. `wMAPE Value Add` and `wMAPE vs Naive` are identical — one will always shadow the other

If both appear in the same report visual, users see the same number twice. No documentation distinguishes them.

### e. `Refresh Date` measure inconsistency across models

| Model | `Refresh Date` logic | Effective result |
|---|---|---|
| ItWh (this) | `MIN(date) where FiscalDayIndicator = 0` | "Today" in fiscal calendar |
| CustItWh | `MIN(date) where FiscalDayIndicator = -1) + 2` | "Yesterday" + 2 days = tomorrow |

Both label the measure `Refresh Date` but produce different dates. Neither is documented.

### f. Naïve forecast grain differs between naïve v1 and v2 within the same model

- `NaiveFcst` (NF): joined to the **target forecast period** — "what actuals from M-1 predict for M"
- `NaiveFcst_v2` (NF_2): joined to the **snapshot month** — "what actuals from the cycle month predict for the cycle month"

These two naïves answer different questions. Since `NaiveFcst_v2` is never used in any measure, the discrepancy is currently harmless — but if a future developer wires it into a measure, they would likely conflate the two without understanding the difference.

### g. No pre/post date split — unlike CustItWh, this model's 12-month trend is consistent

A key difference vs. CustItWh: ItWH has **no UNION ALL structural break**. The entire 12 months uses a single Item × WH grain with no Customer Group hardcoding. Trend analysis spanning any 12-month window is internally consistent. This is an advantage of this model over CustItWh for longitudinal analysis.

---

## Closing — Interview Seeds

1. **"The 120-day forecast horizon exists in this model but the Demand Review report only tracks out to 90 days. Who actually looks at 120-day accuracy numbers, and has that horizon ever changed a sourcing decision — for example, locking a container order or shifting a vendor?"**  
   *(Determines whether 120-day accuracy has an operational consumer or is theoretical backlog.)*

2. **"This model's Over/Under threshold is 8%, but the customer-level Forecast Accuracy report uses 10% for the same classification. Who set those numbers, and does it matter that an item classified 'Even' here could be classified 'Over' in the other report?"**  
   *(Surfaces whether the inconsistency is known and intentional, or an accidental divergence no one has noticed.)*

3. **"The `wMAPE Value Add` number tells you whether Logility beats a naïve carry-forward. If Logility were consistently losing to naïve on a segment — say, RTA items — what would actually change: would you turn off Logility for that class, manually override, or just note it?"**  
   *(Tests whether the benchmark comparison drives any real planning process change or is purely informational.)*

4. **"There is a field called `NaiveFcst_v2` in the data that was built but never connected to any chart or number in the report. Do you know what it was meant to show, and is there a pending request to use it?"**  
   *(Identifies whether this is in-flight development or an abandoned experiment that should be cleaned up.)*
