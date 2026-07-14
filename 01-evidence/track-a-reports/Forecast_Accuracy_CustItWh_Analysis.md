# Forecast Accuracy (Cust_ItWh) — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `78f0b20f-98aa-4f9d-bf7b-cdf5e80d425e`  
**Report ID:** `9a59a99b-cb78-4f09-8ad5-0d75ab85c7f7`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~1.36 MB (BIM); 17 tables, 26 DAX measures in `_Measures` + 1 in `Acceptable Abs Bias`

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "How accurately did Logility forecast demand at the Customer × Item SKU × Warehouse grain — across four lag horizons (2-week, 30-day, 60-day, 90-day) — and does the Logility forecast outperform a naive baseline over the trailing 12 months?"

**Primary chain link:** **Forecast**  
This is a pure forecast-accuracy scorecard. It measures forecast error and bias after the fact (lagged) to evaluate Logility planning performance. It does not drive replenishment or supply actions directly; it governs the quality of the forecast process itself.

Secondary links touched:
- **Demand** — actual demand from `SupplyChain_Enh.ItemActualDemand_Logility` is the denominator for all accuracy metrics
- No supply, inventory, production, receipts, or on-time signals are present

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Identify which customer × item × warehouse combinations have persistent 90-day forecast bias** — `90D Sku Bias` + `90D Over/Under` labels flag items for planner attention | Demand Planner / FC Analyst | Monthly (post-cycle review) | Performance/Governance |
| **Assess Logility model value-add vs. naive baseline** — `wMAPE Value Add` (vs. Naive) and `wMAPE Value Add_CIW` (vs. Baseline) measure whether Logility beats a 1-month naïve carry-forward | Supply Chain Manager / Analyst | Monthly / quarterly | Performance/Governance |
| **Set exception thresholds for bias reviews** — `Acceptable Abs Bias` slicer (0–30%, step 1%) lets user define what constitutes an acceptable bias level; items exceeding it surface in the `Over/Under` column | Demand Planner / Analyst | Monthly | Performance/Governance |
| **Coach or reassign planners** — `PlannerAssignment` links Collective Class × Customer Group to FC Analyst, Category Analyst, and Cust Demand Planner; users can filter accuracy by planner to identify skill gaps | Supply Chain Manager | Quarterly / per review cycle | Performance/Governance |
| **Track status of items being phased out vs. in-line** — `Month End Status Snapshots` + `Status Snapshot` column (`_DROP`, `DISCO`, `___NEW`, `__IN LINE`) shows whether items with poor accuracy were being dropped anyway | Category Analyst | Monthly | Performance/Governance |
| **Identify horizon where forecast degrades** — comparing 2-week, 30-day, 60-day, 90-day bias/wMAPE side-by-side shows at what planning horizon accuracy deteriorates most | Demand Planner / Analyst | Monthly | Performance/Governance |

**No Operational or Financial-Justification decisions are directly supported.** All decisions are Performance/Governance: evaluating and improving the planning process, not moving inventory or building investment cases.

---

## 3. Key Metrics / Measures

### Core Accuracy Measures

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Total Forecast` | Sum of Logility forecast qty | Cust × Item × WH × fiscal month × lag period | `SUM(CustItWHAccy[Total Forecast])` — from EDW snapshot; includes `ResultantForecast + PromoLift` |
| `Total Demand` | Sum of actual demand (orders received) | Same grain | `SUM(CustItWHAccy[Actual Demand])` — from `ItemActualDemand_Logility` |
| `Error Qty` | Raw forecast error (Fcst − Actual) | Same grain | `[Total Forecast] - [Total Demand]` |
| `Bias %` | Directional bias: how over/under-forecasted | Same grain | `DIVIDE([Error Qty], [Total Demand])` — positive = over-forecast |
| `Abs Error Qty` | Absolute error qty | Same grain | `SUM(CustItWHAccy[ABS(Error)])` |
| `ABS Percent Error_CIW` | Aggregate WAPE (not MAPE) at any selected grain | Aggregated | `DIVIDE(ABS([Total Demand] - [Total Forecast]), [Total Demand])` — **⚠️ this is WAPE, not MAPE; name says "ABS Percent Error" which is ambiguous (see §10)** |
| `wMAPE` | Weighted MAPE — average row-level ABS error / average row-level demand | Row-level aggregated | `DIVIDE(AVERAGEX(CustItWHAccy,[ABS(Error)]), AVERAGEX(CustItWHAccy,[Actual Demand]))` |
| `MAPE_CIW` | Simple (unweighted) MAPE — average of per-row `ABSPError` | Row-level aggregated | `AVERAGEX(CustItWHAccy,[ABSPError])` — where `ABSPError = ABS(Error)/Actual Demand` per row; **⚠️ inflated when Actual Demand is small (see §10)** |
| `Mean ABS Dev_CIW` | Numerator of wMAPE — average absolute error per row | Row-level | `AVERAGEX(CustItWHAccy,[ABS(Error)])` |
| `Mean Act Demand_CIW` | Denominator of wMAPE — average actual demand per row | Row-level | `AVERAGEX(CustItWHAccy,[Actual Demand])` |

### Naive Benchmark Measures — `(N)` prefix

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `NaiveFcst_CIW` / `(N)Forecast_CIW` | Naive 1-month carry-forward forecast | Cust × Item × WH × fiscal month | `SUM(CustItWHAccy[NaiveFcst])` — computed in SQL: prior month's orders ÷ NumWeeks × NumWeeks of target month (= prior month total orders projected forward by week count) |
| `(N)Error_CIW` | Naive forecast error | Same | `SUM(CustItWHAccy[(N)Error])` = `NaiveFcst - Actual Demand` (per row calc column) |
| `(N)Bias %_CIW` | Naive forecast directional bias | Same | `DIVIDE([(N)Error_CIW], [Total Demand])` |
| `(N)Mean ABS Dev_CIW` | Average absolute naive error | Row-level | `AVERAGEX(CustItWHAccy, [(N)ABS(Error)])` |
| `(N)wMAPE` | Naive wMAPE (baseline to beat) | Row-level aggregated | `DIVIDE([(N)Mean ABS Dev_CIW], [Mean Act Demand_CIW])` |
| `wMAPE Value Add` | How much better Logility is vs. naive | Same | `[wMAPE] - [(N)wMAPE]` — **negative = Logility beats naive; positive = naive is better** |
| `Error vs Naive_CIW` | How much better Logility bias is vs. naive bias | Same | `ABS([Bias %]) - ABS([(N)Bias %_CIW])` |

### Baseline Benchmark Measures — `(B)` prefix ⚠️ BROKEN

| Measure | Business meaning | Status |
|---|---|---|
| `(B)Error_CIW` | Baseline forecast error | **BROKEN** — references `CustItWHAccy[(B)Error]`, a column that **does not exist** in the model or source SQL. All `(B)` measures return BLANK at runtime. |
| `(B)Bias %_CIW` | Baseline bias % | **BROKEN** — same root cause |
| `(B)Mean ABS Dev_CIW` | Baseline average absolute error | **BROKEN** |
| `(B)wMAPE_CIW` | Baseline wMAPE | **BROKEN** |
| `wMAPE Value Add_CIW` | Logility wMAPE vs. Baseline wMAPE | **BROKEN** — `[wMAPE] - [(B)wMAPE_CIW]` always equals `[wMAPE]` since `[(B)wMAPE_CIW]` is BLANK |
| `Error Value Add_CIW` | Logility bias vs. Baseline bias | **BROKEN** |

No column `(B)Error` or `(B)ABS(Error)` is defined anywhere in the BIM. The word "Benchmark" does not appear in the model. The `(B)` concept — what it represents, and where the data would come from — is entirely absent.

### Threshold & Parameter Measures

| Measure | Business meaning | Source |
|---|---|---|
| `Bias Threshold_CIW` | **Hardcoded constant: `0.10`** (10%) | Defined as a literal in `_Measures`; used in `Over/Under` column and `90D Over/Under` classification. No slicer; not configurable at runtime. |
| `Parameter Value` | User-selected acceptable abs bias threshold (0–30%) | `SELECTEDVALUE('Acceptable Abs Bias'[Parameter])` from `GENERATESERIES(0, 0.3, 0.01)` |
| `Refresh Date` | Approximate data refresh timestamp | `MIN(z_FiscalCal[Transaction Date]) where FiscalDayIndicator=-1) + 2` — **⚠️ suspicious +2 offset; see §9** |

### Row-Level Calculated Columns (CustItWHAccy)

| Column | Logic | Notes |
|---|---|---|
| `Error` | `Total Forecast - Actual Demand` | Directional error per row |
| `ABS(Error)` | `ABS(Actual Demand - Total Forecast)` | Note: subtraction reversed vs. Error column — same magnitude, harmless |
| `ABSPError` | `DIVIDE(ABS(Error), Actual Demand)` | Used in `MAPE_CIW` — will return BLANK when Actual Demand = 0 |
| `(N)Error` | `NaiveFcst - Actual Demand` | |
| `(N)ABS(Error)` | `ABS((N)Error)` | |
| `Over/Under` | `SWITCH: Error/Actual Demand > 0.10 → "Over"; < -0.10 → "Under"; else "Even"` | Threshold is `[Bias Threshold_CIW]` = hardcoded 0.10 |
| `Cust-CC` | `CustomerGroup + "-" + CollectiveClass` | Bridge key linking to `PlannerAssignment` |
| `FcstPeriod` | Sort-prefix version of ForecastPeriod (`"___90Days"`, `"__60Days"`, etc.) | Display sort hack using leading underscores |

### Calculated Columns (z_ProductDetails)

| Column | Logic |
|---|---|
| `90D Sku Bias` | `DIVIDE(CALCULATE([Total Forecast], 90Days, FiscalMonthIndicator >= -6), CALCULATE([Total Demand], 90Days, FiscalMonthIndicator >= -6)) - 1` — rolling 6-month 90-day bias at SKU level; **⚠️ hardcoded -6 month window** |
| `90D Over/Under` | `SWITCH: 90D Sku Bias > 0.10 → "Over"; < -0.10 → "Under"; else "Even"` — same `Bias Threshold_CIW` constant |
| `Planning Categories` | Local grouping: maps Collective Class → `RTA & METAL BEDS`, `CASEGOODS`, `MOTION`, `STATIONARY`, `ACCENTS`, etc. |
| `Collective Class (groups)` | Similar grouping with slightly different bucket definitions |
| `z_ItemFilter` | `ISNUMBER([Total Forecast])` — used to filter z_ProductDetails to items with accuracy data |

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table in model | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `CustItWHAccy` | `SupplyChain_Enh.DemandForecastSnapshot` (forecast), `SupplyChain_Enh.ItemActualDemand_Logility` (actuals), `SupplyChain_Enh.ActualsCustItemWH_AFI` (naive), `Enterprise_DW.dimDate_nonRetail`, `PowerBI_SupplyChain.CustomerAcctMaster_AFI` | Complex multi-join query; rolling 12 months; 1-hour `CommandTimeout` |
| Same EDW | `Month End Status Snapshots` | `PowerBI_SupplyChain.DemandFulfillmentCommonContainer_Logility`, `PowerBI_SupplyChain.CurrentProductDetails`, `Enterprise_DW.DimDate` | Item lifecycle status at each month-end (last Monday snapshot) |
| Same EDW | `z_CustomerMaster_AFI` | `PowerBI_SupplyChain.CustomerAcctMaster_AFI` | Single-column table — only `Customer Group` |

### Power BI Dataflows (semi-governed)

| Dataflow workspace | Tables fed | Notes |
|---|---|---|
| `a47e4573-c455-40af-a9ad-e22c81a07926` (separate workspace) | `z_ProductDetails`, `z_FiscalCal`, `z_WarehouseMaster` | Shared conformed dimension layer — same dataflow used across multiple Supply Chain models |

### SharePoint (ungoverned) ⚠️

| Source | Table | List/Content | Risk |
|---|---|---|---|
| `masterashley.sharepoint.com/sites/supplychain-DemandPlanning` | `PlannerAssignment` | SharePoint list ID `531a515e` — planner-to-CC/CG mapping | **Medium** — list ID hardcoded; if list is deleted or ID changes, all planner filtering breaks silently |
| Same site | `Users` | SharePoint list ID `95e7d6e4` — username → PlannerName mapping | **Medium** — same risk; PlannerName derived by splitting username before "@" |

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Customer Group × Item SKU × Warehouse × Fiscal Month × Forecast Horizon (2-week / 30-day / 60-day / 90-day)

This is the finest grain in the Supply Chain Analytics workspace for forecast accuracy — more granular than the Item-WH grain used in the Demand Review model's pre-March 2025 history.

**Snapshot strategy:**  
- Accuracy data is **accumulative trailing 12 months** — not "latest only". Each row is a (forecast-snapshot-date, actual-period) pair, enabling trend analysis of accuracy over time.
- The `Snapshot Date` column ties each forecast reading to the specific Logility cycle snapshot, enabling cycle-over-cycle comparison.
- `Month End Status Snapshots` adds item lifecycle status at each month-end, allowing accuracy to be segmented by whether items were in-line, being dropped, new, etc.

**Historical snapshot is essential** — comparing accuracy across cycles and horizons requires the full trailing 12-month set. A latest-only approach would be useless for this report.

---

## 6. Dimensions Used

| Dimension | Source | Local re-derivations / drift risks |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow → `CurrentProductDetails`) | `Planning Categories`, `Collective Class (groups)` — two independent groupings of `Collective Class` with overlapping but not identical bucket logic (see §7). `z_ItemFilter` = ISNUMBER([Total Forecast]) is a local filter flag. `90D Sku Bias` and `90D Over/Under` are locally derived accuracy columns that tie back into the product dimension. |
| **Date / Fiscal Calendar** | `z_FiscalCal` (dataflow → `AshleyFiscalCalendarV2`) | `Fiscal Month Indicator` is the core rolling integer offset used for all time range filters. `Fiscal Day Indicator` is used in the `Refresh Date` measure. Both are dataflow-derived; not re-calculated locally. |
| **Warehouse** | `z_WarehouseMaster` (dataflow) | `Warehouse Group` is the key grouping attribute; no local re-derivation in this model. Container warehouses (C, CNW, C35, 55) excluded from naive forecast SQL but not from accuracy data — any forecast/actual for those warehouses is included in accuracy metrics. |
| **Customer** | `z_CustomerMaster_AFI` (EDW SQL) | **Locally sourced** — not from the shared dataflow. Only contains `Customer Group`. Pre-March 2025 accuracy data hardcodes `'AFICONS'` as Customer Group (see §10). |
| **Planner** | `PlannerAssignment` (SharePoint) | Maps `CustGrp-CC` → planner names. The relationship to `z_CustomerMaster_AFI` and `z_ProductDetails[Collective Class]` is **inactive** (both are marked `active=False`). The active path is via `CustItWHAccy[Cust-CC] → PlannerAssignment[CustGrp-CC]`. Direct CC and CG filters through planner don't propagate unless enabled explicitly in DAX. |
| **Item Lifecycle** | `Month End Status Snapshots` (EDW) | Local derivation of `Status Snapshot` column: maps FutureStatus codes (F/P/L/E) to `_DROP`, ItemStatus D/R to `DISCO`, ItemStatus N to `___NEW`, else `__IN LINE`. Underscore prefixes are sort-order hacks. The column `FutreDropFlag` contains a typo (`Futre` not `Future`) — inherited from the SQL alias. |

---

## 7. Duplication / Consolidation Signals

1. **`wMAPE Value Add` vs. `wMAPE Value Add_CIW` — different baselines, same name pattern:**  
   - `wMAPE Value Add` = `wMAPE - (N)wMAPE` (vs. Naive)  
   - `wMAPE Value Add_CIW` = `wMAPE - (B)wMAPE_CIW` (vs. Baseline — broken)  
   Both measure "how much better than benchmark" but against different benchmarks. A user seeing both measures has no indication that one is always blank. The naming convention (`_CIW` suffix) is inconsistently applied as a suffix across the model.

2. **`NaiveFcst_CIW` and `(N)Forecast_CIW` are identical:**  
   Both return `CALCULATE(SUM(CustItWHAccy[NaiveFcst]))`. Two measures, same expression, different names.

3. **`ABS Percent Error_CIW` and `wMAPE` measure the same concept differently:**  
   - `ABS Percent Error_CIW` = `ABS(Total Demand - Total Forecast) / Total Demand` — aggregate WAPE
   - `wMAPE` = `AvgX(ABS Error) / AvgX(Actual Demand)` — row-level aggregated wMAPE  
   These are not mathematically equivalent and will diverge when mix shifts. Both are presented as "accuracy percentage" but measure different things.

4. **Two category grouping columns in z_ProductDetails — `Planning Categories` vs. `Collective Class (groups)`:**  
   Both group `Collective Class` into buckets but with different rules and different bucket names. The same source column produces two non-interchangeable hierarchies. `Group By 1` and `Group By 2` both reference both columns as filter options with different default ordering, increasing the chance of inconsistent slicing.

5. **`Group By 1` and `Group By 2` are near-identical:**  
   Same list of grouping options (`Customer Group`, `Planning Categories`, `Collective Class`, etc.) with only the default sort order swapped between `Customer Group` (position 0 in Group By 1) and `Planning Categories` (position 0 in Group By 2). Functionally duplicated.

6. **`CustItWHAccy[Cust-CC]` duplicates combination already derivable from relationships:**  
   The `Cust-CC` calculated column concatenates `CustomerGroup + "-" + CollectiveClass`. This bridge key exists only because the `PlannerAssignment` relationship to `z_CustomerMaster_AFI` and `z_ProductDetails` is inactive. If those relationships were activated, `Cust-CC` would be unnecessary.

7. **The SQL for the naive forecast sub-query (`NF`) is copy-pasted between the pre- and post-March 2025 UNION branches**, with one difference: the post-March 2025 branch includes `CustomerAcctMaster_AFI` join to group by Customer Group; the pre-March 2025 branch omits it. The outer join key then mismatches (pre-branch `NF` has no customer group), silently producing a cross-join for naive vs. actual.

---

## 8. Open Questions

1. **What is the `(B)` baseline supposed to be?** No column or data source in the model supplies `CustItWHAccy[(B)Error]` or `CustItWHAccy[(B)ABS(Error)]`. Was a Baseline forecast concept planned (e.g., statistical model output, prior-cycle Logility, or a published plan) and never built? Or was the column removed and the measures left behind?

2. **Who is the primary consumer?** `PlannerAssignment` maps planners to CC × CG, but no row-level security is visible. Does every planner see all data, or is there a separate filter driving personal views?

3. **Is the `z_CustomerMaster_AFI` intentionally a direct EDW SQL query rather than from the shared dataflow?** The shared dataflow has customer master entities; using a direct SQL SELECT DISTINCT Customer Group bypasses any transformations or governance the dataflow applies. Is this intentional (simpler, faster) or a missed consolidation?

4. **Is 60-day accuracy actively used?** The `ForecastPeriod` column includes `60Days` alongside 2-Week, 30-Day, and 90-Day, but the `Demand Review` model (the adjacent report) has no 60-day measures. Is the 60-day horizon tracked anywhere else, or is it dead weight in this model?

5. **Is the `Month End Status Snapshots` table consumed in any report visual?** It enriches lifecycle context but is not referenced by any DAX measure in `_Measures`. Its only role is as a filter dimension in report visuals — which cannot be confirmed from the model alone.

6. **What does "Baseline" mean in this context?** Given that the `(N)` prefix is Naive (prior month actuals), the `(B)` prefix presumably represents a different benchmark — but there is no documentation, comment, or data in the model to confirm this.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `0.10` (10%) | `Bias Threshold_CIW` measure; `Over/Under` column; `90D Over/Under` column | Defines the threshold above/below which an item is classified as "Over" or "Under" forecasting | **No** — hardcoded as a literal `0.10` in a DAX measure; no explanation of why 10% was chosen or who approved it |
| `-6` months | `90D Sku Bias` calculated column in `z_ProductDetails` | Restricts the SKU-level 90-day bias to the trailing 6 months only | **No** — undocumented; creates a different look-back window than the main accuracy metrics (which cover all 12 trailing months). An item can appear "Even" in `90D Over/Under` on the 6M window but be consistently biased over the full 12M. |
| `+2` days | `Refresh Date` measure | `MIN(z_FiscalCal[Transaction Date]) where FiscalDayIndicator=-1) + 2` — adds 2 days to "yesterday" to get an approximate refresh date | **No** — `FiscalDayIndicator = -1` appears to mean "last completed day". Adding 2 days would yield tomorrow, not today. This may be a bug or an attempt to account for ETL lag. The label "Refresh Date" suggests intent to show when data was last updated, but the +2 offset makes the displayed date unreliable. |
| `dateadd(day, 15, FiscalMonthFirstDate)` | Snapshot date derivation for all four lag periods | Default cycle snapshot is "15th day after month start" = nominally the 3rd Monday of the month | **Partially** — SQL comment says "default 3rd Monday as forecast cycle". But day+15 is not always the 3rd Monday; it is an approximation that is corrected for known deviations via CASE statements. |
| Hardcoded cycle deviation dates | `CustItWHAccy` SQL CASE block | 8 specific calendar dates overriding the day+15 default for Nov 2025, Dec 2025, Jan 2026, Feb 2026, Mar 2026 (×2), Apr 2026, May 2026, Jun 2026 | **Partially documented** — each has a SQL comment like `-- add Nov cycle deviation`. However, these must be manually maintained every time a cycle deviates; there is no automated mechanism to detect or update them. |
| `'01/25/2025'` as Feb 2026 trigger | `CustItWHAccy` SQL CASE block for all four periods | Comment says "add Feb cycle deviation" but uses year **2025** — should be **2026** | **Bug** — this trigger date (`01/25/2025`) is in the past and would only match historical data; the Feb 2026 cycle deviation (if any) would fall through to the day+15 default, potentially using the wrong snapshot. |
| `'3/28/2026'` → `'3/16/2026'` | `CustItWHAccy` SQL CASE block | Appears alongside `'3/29/2026'` → `'4/20/2026'`; assigns snapshot 3/16 when month first date is 3/28 | **Suspect** — 3/16/2026 is before 3/28/2026; a snapshot can't precede the month's first date. This override would never fire correctly for a March forecast period. Likely a copy-paste error where `3/28/2026` was meant to be a different month's first date. |
| `WHERE [Snapshot Date] >= '3/15/2025'` / `< '3/15/2025'` | UNION ALL split in `CustItWHAccy` SQL | Separates post/pre March 2025 accuracy data | **Partially** — SQL comment explains the split ("Post March 2025 = Cust Item Warehouse Accuracy"; "Pre March 2025 = Item Warehouse Accuracy"). The exact date 3/15/2025 is not explained — this appears to be when Logility was upgraded to produce customer-group-level forecasts. |
| `Warehouse NOT IN ('C','CNW','C35','55')` | Naive forecast SQL (both branches) | Excludes container and special warehouses from naive baseline | **No** — the comment is absent; the same exclusion exists in `Demand Review`'s `OrdHist` but with warehouse `'55'` only (this model also excludes C, CNW, C35). The exclusion list differs between models. |
| `[IAD].[Company] = 'AFI'` | Actuals SQL (both branches) | Filters actual demand to AFI company only | **No comment** — AFI = Ashley Furniture Industries; presumably this is correct but it's a silent constant filter not visible to users. |

**Dollar-value business impact:** This model does **not** calculate any dollar-value impact. No FOB price, revenue, or cost measure exists. The report is purely about forecast accuracy statistics. However, if `wMAPE Value Add_CIW` (Logility vs. Baseline) were ever repaired, it could be used to calculate an implied $ benefit of using Logility. Currently that calculation does not exist in this model.

---

## 10. Comparability / Consistency Issues

### a. Pre/Post March 2025 structural split — Customer Group grain breaks history

The `CustItWHAccy` table is a **UNION** of:
- **Post-March 2025:** Customer × Item × Warehouse grain; `Customer Group` sourced from `dfcCustomerGroups` field
- **Pre-March 2025:** Item × Warehouse grain only; `Customer Group` hardcoded as `'AFICONS'`

**Impact:** Any filter by Customer Group in the report will return **zero data before March 2025** for all groups except `AFICONS`. A user comparing bias for Customer Group X across a 12-month window that spans March 2025 sees a step-change that is entirely structural, not real. No warning or annotation exists in the model.

Additionally, the naive forecast in the pre-March 2025 branch does not join `CustomerAcctMaster_AFI`, meaning naive is an Item-WH aggregate — when comparing against a Customer-level actual in the post-March 2025 branch, the naive denominator cannot align.

### b. `wMAPE` vs. `ABS Percent Error_CIW` — different accuracy formulas for the same concept

Both claim to measure forecast accuracy percentage:
- `wMAPE = AVERAGEX(rows, ABS(Error)) / AVERAGEX(rows, Actual Demand)` — row-level average of absolute errors, normalised by row-level average of demand
- `ABS Percent Error_CIW = ABS(SUM(Demand) - SUM(Forecast)) / SUM(Demand)` — aggregate WAPE (sum-level)

These diverge when items have heterogeneous demand volumes. The model offers both with no guidance on which to use. A user switching between measures will see different numbers for the same filter without understanding why.

### c. `MAPE_CIW` is not comparable across segments with different demand volumes

`MAPE_CIW = AVERAGEX(CustItWHAccy, ABSPError)` where `ABSPError = ABS(Error)/Actual Demand` per row. When `Actual Demand = 0` for a row, `ABSPError = BLANK` (DAX DIVIDE) and that row is excluded from `AVERAGEX`. When `Actual Demand` is very small (1–2 units), the MAPE can be 500%+ on a single misforecast unit. This makes `MAPE_CIW` incomparable between high-volume and low-volume segments. No adjustment or minimum-demand filter is applied.

### d. `Over/Under` column uses `0.10` hardcode; `Parameter Value` slicer not used in `Over/Under`

The `Acceptable Abs Bias` slicer generates `Parameter Value` (user-configurable 0–30%), but the `Over/Under` calculated column and `90D Over/Under` column both use the hardcoded `0.10` threshold. The slicer appears to be used in visuals via a separate filter logic not visible in the measures — or it may only drive a conditional format, not the column classification. A user who sets the slicer to 20% might expect `Over/Under` to reclassify items, but the column is pre-calculated and won't change.

### e. `90D Sku Bias` uses 6-month window; main `Bias %` uses all available months

- `90D Sku Bias` (in `z_ProductDetails`): `FiscalMonthIndicator >= -6` — trailing 6 months
- `Bias %` (in `_Measures`): no month filter — uses all 12 trailing months in context

A user comparing `90D Sku Bias` to `Bias %` filtered to 90Days will see different numbers even for the same item, because the time windows differ. No label distinguishes these two look-back periods.

### f. Naive forecast grain differs pre/post March 2025

- Post-March 2025: Naive is at Customer × Item × WH grain (includes `CustomerAcctMaster_AFI` join)
- Pre-March 2025: Naive is at Item × WH grain only (no customer join)

When comparing `(N)wMAPE` across the March 2025 boundary, the naive benchmark has a different definition on each side of the cutoff. Pre-March naive is a simpler, less granular baseline that will systematically differ from post-March naive — making cross-period `wMAPE Value Add` (vs. Naive) not comparable.

---

## Closing — Interview Seeds

1. **"The `(B)` baseline measures — `(B)wMAPE_CIW`, `wMAPE Value Add_CIW`, `Error Value Add_CIW` — all return blank in this model because the underlying column doesn't exist. Were these ever working, and if so, what was the Baseline: a statistical model, a prior Logility version, or the published plan? And does anyone realise they're currently always blank?"**  
   *(Determines whether a critical comparison is silently broken and what the intent was.)*

2. **"When you see an item with 90-day bias consistently above 10% for three or more months, what is the concrete next step — do you open Logility directly and override the statistical model, do you leave a comment in a SharePoint/Teams channel, or does something else happen?"**  
   *(Establishes the actual operational loop: does forecast accuracy review translate into a Logility model change, a manual override, or just a coaching note?)*

3. **"The customer-group split in accuracy history means you can't compare Customer Group X's bias trend before and after March 2025 on the same chart — all pre-March data shows as 'AFICONS'. Do users know this, and do they trust any trend line that spans that boundary?"**  
   *(Validates whether the structural break is understood or whether it is generating misleading conclusions in reviews.)*

4. **"The 90-day bias threshold that classifies items as Over/Under is hardcoded at 10%. Who set that number, is it in any written policy, and has there ever been a discussion about whether it should vary by category (e.g., a 10% threshold for a $5 accessory vs. a $2,000 sofa may not make equivalent business sense)?"**  
   *(Confirms whether the governance thresholds have organizational backing or were set once and forgotten.)*
