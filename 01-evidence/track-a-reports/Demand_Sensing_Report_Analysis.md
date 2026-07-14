# Demand Sensing Report — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `67f6a6f2-fcfd-40b4-84cf-832abc412c67`  
**Report ID:** `870185c9-21d8-42a8-8193-c48197d3dd4a`  
**Analysis Date:** 2026-07-08  
**Model Size:** 39 tables (2 analytical fact + 1 FC + 1 order history + 3 dim + 9 slicer/group tables + local date tables); **17 DAX measures** (15 in `Measures (2)`, 1 in `Percentage Filter`, 1 in `Qty Diff`); Compatibility Level 1567  
**BIM File:** [bim/Demand_Sensing_Report.bim](bim/Demand_Sensing_Report.bim)

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> Is the current week's written order rate for a given item-warehouse-customer group **abnormally high or low** compared to the item's historical demand trend — and if so, by how much?

This is a **statistical demand signal / anomaly detection** report. Unlike other reports that measure demand vs. forecast, this one uses a **statistical control chart approach**: it computes a short-term trend average and a long-term baseline, then calculates whether current written orders fall **outside the expected range** (Min ± N standard deviations). The result is a flag (`Trend +/-`) indicating if demand is signaling a shift up (+1), shift down (−1), or normal (0).

**Primary chain links served:**

| Link | How served |
|---|---|
| **Demand (sensing)** | `Trend Data` — pre-computed statistical trend (short-term avg, long-term baseline, Min/Max bounds, Expected Value) at Item × WH Group × Account Group | 
| **Demand (current)** | `Weekly Writ Qties` — this week's written order quantities at same grain |
| **Demand (history)** | Both tables draw from `ActualsCustItemWH_AFI`/`OrderHistory` covering 26+ weeks |
| **Forecast** | `FC` — current resultant forecast (6 months back + 12 months forward) for comparison; `Avg Wkly FC` measure normalizes to weekly rate |

**Not served:** Supply, inventory, on-time, forecast accuracy, receipts.

**Key distinction from other reports:** This report is **not** about whether we are meeting forecast — it's about whether customer order behavior is changing relative to its own historical pattern. A spike or drop in written orders this week signals a potential demand shift that should prompt a forecast revision.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Flag items with abnormal demand signal this week** — `Trend +/-` = +1 or −1 triggers review | Demand Planner / Forecast Analyst | **Weekly** (Monday after week close) | **Operational** — trigger forecast revision investigation |
| **Quantify the magnitude of the demand signal** — `Abs Qty Change` and `Diff%` show how far current orders deviate from trend | Demand Planner | Weekly | **Operational** — size the forecast adjustment |
| **Compare current orders vs. weekly forecast rate** — `Trend % of wklyFC` flags items where demand trend diverges significantly from the plan | Demand Planner / Planning Manager | Weekly | **Performance/Governance** — validate forecast health |
| **Identify whether the signal is positive (above) or negative (below)** trend — differentiate demand surges from demand collapses | Demand Planner | Weekly | **Operational** — expedite supply vs. reduce supply |
| **Filter by significance threshold** — user-configurable `Percentage Filter` (default 15%) and `Qty Diff` (default 20 units) to suppress noise | Demand Planner | Weekly | **Operational** — reduce false positives |
| **Track order entry timing** — `Future Flag` identifies if current orders are for future vs. current fiscal month | Demand Planner | Weekly | **Performance/Governance** — distinguish early booking from genuine demand shift |

> **No Financial-Justification decisions.** No dollar-value impact calculation in this model.

---

## 3. Key Metrics / Measures

### From `Measures (2)` (15 measures)

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `ST Average` | Short-term demand average (13 weeks prior to trend window) | Item × WH Group × Account Group | `SUM(Trend Data[Short Term Average])` — pre-calculated in SQL | |
| `Trend Average` | Average demand over the most recent 6-week trend window | Item × WH Group × Account Group | `SUM(Trend Data[Trend Avg])` — pre-calculated in SQL | |
| `Diff` | Gap: Trend Average − ST Average | — | `[Trend Average] − [ST Average]` | |
| `Diff%` | % difference between trend and short-term | — | `[Diff] / [ST Average]` | ⚠️ divide-by-zero if ST Average = 0 (no historical demand) |
| `Abs Diff %` | Absolute value of Diff% | — | `ABS([Diff%])` | |
| `Abs Qty Change` | Absolute unit difference between trend and short-term | — | `ABS([ST Average] − [Trend Average])` | |
| `Expected` | Statistical expected value from long-term baseline | — | `SUM(Trend Data[Expected Value])` | |
| `Writ Qty` | This week's written order qty | Item × WH Group × Account Group | `COALESCE(SUM(Weekly Writ Qties[Qty Ordered]), 0)` | |
| `Writ Acct +/-` | Flag: is this week's written qty outside the statistical control band? | — | `IF(Qty < Min, −1, IF(Qty > Max, 1, 0))` | ⚠️ Min can be negative — see §9 |
| `Writ Acct +/- (2)` | Flag: same but only triggers downward if Min > 0 | — | `IF(Qty < Min AND Min > 0, −1, IF(Qty > Max, 1, 0))` | ⚠️ **two versions** of same flag — see §7 |
| `Trend +/-` | Primary signal flag: is the recent 6-week trend outside the baseline control band? | — | `IF(ABS(Trend−ST) < QtyDiffValue, 0, IF(Trend < MAX(Min,0), −1, IF(Trend > Max, 1, 0)))` | ⚠️ absolute qty threshold `Qty Diff Value` applied first |
| `Trend Highlight` | Identical to `Trend +/-` | — | **Exact duplicate** of `Trend +/- ` expression | ⚠️ dead duplicate |
| `Avg Wkly FC` | Average weekly forecast rate for the item | Item × WH Group | `SUM(FC[FC]) / (DISTINCTCOUNTNOBLANK(FC[Month Indicator]) × 4.33)` | ⚠️ hardcoded 4.33 — see §9 |
| `Trend % of wklyFC` | Trend average as % of average weekly forecast | — | `[Trend Average] / [Avg Wkly FC]` | |
| `Future Flag` | Is the max current request date in the future (1), current month (0), or past (−1)? | — | `IF(MAX(Orders[Cur Req Fiscal Month]) > TODAY(), 1, IF(...< EDATE(TODAY(),-1), −1, 0))` | ⚠️ `TODAY()` in Import mode |

### From slicer tables

| Measure | Table | Business meaning |
|---|---|---|
| `Percentage Filter Value` | `Percentage Filter` | Selected % threshold for filtering low-significance signals; default 15% if no selection |
| `Qty Diff Value` | `Qty Diff` | Selected absolute unit threshold; default 20 units if no selection |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`Trend Data`** | `ashley-edw.database.windows.net / ashley_edw` — heavy multi-temp-table SQL: computes long-term (26wk) baseline mean/stdev, short-term (13wk) average, and 6-week trend average per Item × WH Group × Account Group | Direct Azure SQL EDW | ⚠️ **High** — all statistical computations (mean, stdev, control bounds) happen in SQL at refresh; no audit trail in Power BI |
| **`Weekly Writ Qties`** | Same EDW — same variable block but different date range; 13 weeks of written orders by week + current trend window | Direct Azure SQL EDW | Medium |
| **`Orders by Request Month`** | Same EDW — `ActualsCustItemWH_AFI` on Current Request date, aggregated by fiscal month; 12+ months range | Direct Azure SQL EDW | Medium |
| **`FC`** | Same EDW — `SupplyChain_Enh.ForecastCommonContainer_Logility` + `DemandForecastLevels_Logility`; 6 months back + 12 forward; uses `Result_Fc_0`–`Result_Fc_11` columns | Direct Azure SQL EDW | Medium |
| **`Dates`** | Same EDW — full `Enterprise_DW.DimDate` query (all date columns) | Direct Azure SQL EDW | Low — standard date table |
| **`Customers`** | Same EDW — `PowerBI_SupplyChain.CustomerAcctMaster_AFI` + 8 synthetic UNION rows (AFICONS, ECOMM, HSENT, HSLIC, INT, MASSRENT, NFM, RHCUST) | Direct Azure SQL EDW | Medium — same synthetic customer pattern as GF Act+Fcst |
| **`Warehouses`** | Same EDW — `SupplyChain_DW.DimAFIWarehouses`; `TOP 1000` limit applied | Direct Azure SQL EDW | ⚠️ `TOP 1000` cap on warehouse list — see §9 |
| **`ProductDetails`** | PowerBI Dataflow `346f2aa1...` → `CurrentProductDetails` (with `Item Ext Series Number` renamed to `Planning Series`) | Governed Dataflow | Low |

**All dimension tables sourced directly from EDW SQL except `ProductDetails`** — this is the only model in the workspace family where `Customers`, `Warehouses`, and `Dates` are **not** loaded from the conformed dataflow. They are independently queried from the EDW. This means:
- Warehouse groupings (AFI/ASH/CND/OTH) are **re-derived locally in SQL** — not from the `z_WarehouseMaster` dataflow.
- Customer groupings are **re-derived locally** — not from the `z_CustomerMaster` dataflow.
- The `Dates` table is a **raw DimDate query** — not the `z_FiscalCal` dataflow (which uses `AshleyFiscalCalendarV2`).

> **No Fabric sources. No SharePoint.** All SQL hits `Ashley-edw.database.windows.net`.

---

## 5. Grain & Snapshot Strategy

**Primary grain by table:**

| Table | Grain |
|---|---|
| `Trend Data` | Item SKU × Warehouse Group (AFI/ASH/CND/OTH) × Account Group — **one row per combination** (latest computation) |
| `Weekly Writ Qties` | Item SKU × Warehouse Group × Account Group × **Fiscal Week** (13 weeks + trend window) |
| `Orders by Request Month` | Item SKU × Customer Account × Warehouse × **Fiscal Month** (Current Request date basis) |
| `FC` | Item × Warehouse Group × Customer Group × **Fiscal Month** (6 back + 12 forward) |

**Snapshot strategy:**
- `Trend Data` — **latest-only**: computes statistical averages fresh on each refresh. No history of previous trend computations. Cannot compare "trend this week" vs. "trend last week."
- `Weekly Writ Qties` — 13 weeks of history + current trend window; enables week-by-week written order trend view.
- `Orders by Request Month` — rolling monthly history for seasonal context.
- `FC` — latest Logility forecast snapshot.

**Statistical window design (in SQL):**
```
@TrendEnd    = -1    (last completed week)
@TrendWeeks  = 6     (trend window: weeks -6 to -1)
@ShortTermWeeks = 13 (short-term baseline: weeks -20 to -7)
@LongTermWeeks  = 26 (long-term baseline: weeks -32 to -7)
@Stdevs (Trend Data) = 1.5
@Stdevs (Weekly Writ Qties) = 2   ← DIFFERENT VALUE
```

---

## 6. Dimensions Used

| Dimension | Table | Connected? | Notes |
|---|---|---|---|
| **Product** | `ProductDetails` (91 cols) | ✅ — to all 4 fact tables via `Item SKU` / `Item-Lvl1` | Conformed dataflow; `Item Ext Series Number` renamed `Planning Series` |
| **Date** | `Dates` (41 cols) | ✅ — to `Weekly Writ Qties[FiscalWeekLastDate]`, `Orders by Request Month[Cur Req Fiscal Month]`, `FC[Fiscal Month]` | **Local EDW query**, NOT the z_FiscalCal dataflow; 41 raw DimDate columns |
| **Customer** | `Customers` (6 cols) | ✅ — to `Weekly Writ Qties[Account Group]` (via Account Group), `Orders by Request Month[Customer Account Number]`, `FC[dfcCustomerGroups]`, `Trend Data[Account Group]` | Local SQL + synthetic UNION rows |
| **Warehouse** | `Warehouses` (9 cols) | ✅ — to `Orders by Request Month[Warehouse]`, `Trend Data[Warehouse Group]`, `Weekly Writ Qties[Warehouse Group]`, `FC[WhGrp]` | Local SQL; `TOP 1000` limit |

**Slicer / field parameter tables (no relationships, used as visual controls):**

| Table | Type | Purpose |
|---|---|---|
| `Order Group 1/2/3` | Calculated field parameter | Controls grouping dimension in order visuals (9 options each) |
| `Req Group 1/2/3` | Calculated field parameter | Controls grouping dimension in request month visuals (10 options each) |
| `Trend Group 1` | Calculated field parameter | Controls grouping dimension in trend visuals (9 options) |
| `Trend Group 2` | Calculated field parameter (hidden) | Hidden version of Trend Group 1 |
| `Percentage Filter` | Calculated `GENERATESERIES(0, 1, 0.05)` | User-selectable % significance threshold (0–100% in 5% steps) |
| `Qty Diff` | Calculated `GENERATESERIES(0, 100, 10)` | User-selectable absolute unit threshold (0–100 in steps of 10) |

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `Warehouse Group` (AFI/ASH/CND/OTH) | SQL in `Trend Data`, `Weekly Writ Qties`, `Orders by Request Month`, `FC`, `Warehouses` | CASE WHEN on raw WH codes — **replicated 5 times in SQL** | ⚠️ **High** — if a new WH code is added, must update all 5 SQL queries; conformed `z_WarehouseMaster` not used |
| `Account Group` (DSG/Non-A/individual) | SQL in `Weekly Writ Qties`, `Orders by Request Month`, `Customers` | Different bucketing logic in each query — see §7 | ⚠️ **High** — inconsistent across tables |
| `Logility Group` | `Orders by Request Month` SQL | Hardcoded map: 8 named account numbers → individual names; Commission Code 006 → 'HSE'; Ashley HomeStores → 'HSL'; else 'AFICONS' | Medium |

---

## 7. Duplication / Consolidation Signals

1. **`Trend +/-` and `Trend Highlight` are exact duplicates.** Both measures have identical expressions. `Trend Highlight` appears to be a renamed copy for use in a different visual context (e.g., conditional formatting vs. flag column), but functionally identical.

2. **`Writ Acct +/-` and `Writ Acct +/- (2)` differ by one condition.** `+/-` fires the downward flag when `Qty < Min` regardless of Min's sign. `+/- (2)` only fires downward when `Qty < Min AND Min > 0` — suppressing false negatives when the control band's lower bound is negative (no demand possible). Neither is labeled as the preferred version.

3. **Warehouse grouping logic (AFI/ASH/CND/OTH) is hardcoded in 5 separate SQL queries.** The mapping of warehouse codes to groups is duplicated in `Trend Data`, `Weekly Writ Qties`, `Orders by Request Month`, `FC`, and `Warehouses` SQL. If Warehouse 49 should move from "OTH" to "AFI", it must be changed in all 5 places. The conformed `z_WarehouseMaster` dataflow (used by other models) is not used here.

4. **Account Group logic differs between `Weekly Writ Qties` and `Trend Data` SQL:**
   - `Weekly Writ Qties`: Non-A accounts bucketed as `'Non-A Accounts'`; uses `DimCustomers` as source
   - `Trend Data`: Non-A accounts kept as `Customer Group`; uses `CustomerAcctMaster_AFI` as source
   The two tables have different granularities of customer grouping for the "non-A" segment — joins between them via `Account Group` will silently misalign.

5. **`Order Group 1`, `Order Group 2`, `Order Group 3` are identical field parameter tables** with the same 9 options in the same order. Same for `Req Group 1/2/3`. These 6 tables exist to drive 6 different field parameter slicers on different report pages — they are functionally identical and could collapse to one set if the visual bindings were updated.

6. **`Customers` dimension in this model vs. `z_CustomerMaster_AFI` in other models** — independent SQL query vs. conformed dataflow; different columns (this model has 6 cols, the conformed has 38 cols). The synthetic UNION rows differ: this model has 8 (AFICONS, ECOMM, HSENT, HSLIC, INT, MASSRENT, NFM, RHCUST); `z_CustomerMaster_AFI` in GF Act+Fcst has 9 (adds MFRM). Cross-report customer filtering will silently be inconsistent.

7. **`FC` table uses `SupplyChain_Enh.ForecastCommonContainer_Logility`** (via `DemandForecastLevels_Logility` for max file date), while other models use `SupplyChain_Enh.DemandForecastSnapshot`. Same underlying forecast concept; different EDW tables. Reconciliation between this model's forecast and forecast from other models may not balance.

---

## 8. Open Questions

1. **What does "Account Group" mean in `Trend Data` vs. `Weekly Writ Qties`?** The two tables use the term but source it differently (different SQL, different bucketing for non-A accounts). When the Trend signal and the Weekly Writ Qties are compared for the same "Account Group," are they actually at the same grain?

2. **`@Stdevs = 1.5` in `Trend Data` vs. `@Stdevs = 2` in `Weekly Writ Qties`.** Two different standard deviation multipliers for computing the control band width — the trend table uses 1.5 sigma and the weekly written qty table uses 2 sigma. Was this intentional? If the weekly written qty signal uses 2σ bounds but the trend uses 1.5σ bounds, the sensitivity of `Trend +/-` vs. `Writ Acct +/-` is structurally different. Are users aware?

3. **`FC` table reads from `SupplyChain_Enh.ForecastCommonContainer_Logility` (Logility file-based snapshot) not `DemandForecastSnapshot` (the standard EDW source).** Is this intentional — does this report specifically want the Logility-native forecast rather than the promoted snapshot? What is the timing difference between the two?

4. **`Warehouses` table has `TOP 1000` limit.** This is an unexplained SQL cap. How many warehouses exist in `DimAFIWarehouses`? If > 1,000, some are silently excluded. Even if < 1,000 today, new warehouses added in future could be dropped.

5. **`Trend Data` produces one row per item-WH group-account combination.** When a planner looks at a series (multiple items), the DAX SUM of `Trend Avg` across items gives a portfolio-level signal. Is this the intended use, or should each item be evaluated independently? Summing statistical means across items is not the same as a portfolio-level statistical test.

6. **`Today()` in `Future Flag`** — same Import mode freshness issue as other models. If the model last refreshed on Monday and a planner views it on Friday, `TODAY()` returns Friday but all order data is from Monday's refresh.

7. **Who are the 8 named accounts in `Orders by Request Month[Logility Group]` SQL** (`109200`, `193300`, `1494100`, `1256500`, `1907700`, `4444400`, `9987300`, `3352200`)? These appear individually rather than being bucketed. They are not documented in the model.

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`@TrendWeeks = 6`** | Both `Trend Data` and `Weekly Writ Qties` SQL | 6-week trend window (most recent completed weeks) | **Partially** — SQL variable declared; rationale undocumented |
| **`@ShortTermWeeks = 13`** | Both SQL | 13-week short-term baseline (1 quarter) | **Partially** — SQL variable; no rationale |
| **`@LongTermWeeks = 26`** | Both SQL | 26-week long-term baseline (6 months) | **Partially** — SQL variable; no rationale |
| **`@TrendEnd = -1`** | Both SQL | Trend ends at last completed week (not current week in progress) | **Partially** — SQL variable |
| **`@Stdevs = 1.5`** | `Trend Data` SQL | Control band width = 1.5 standard deviations above/below long-term mean | **No** — 1.5σ = ~87% of observations within bounds; ~13% would naturally signal "anomalous" even with no real change |
| **`@Stdevs = 2`** | `Weekly Writ Qties` SQL | Control band width = 2σ for weekly written qty comparison | **No** — **different from `Trend Data`'s 1.5σ**; two different sensitivity levels for the same concept |
| **`4.33`** in `Avg Wkly FC` | DAX measure | Converts monthly forecast to weekly: `monthly / (months × 4.33)` | **No** — 4.33 ≈ 52/12 weeks per month on average; but fiscal months are 4 or 5 weeks, making this an approximation. The `FC` table has a `Weeks` column (actual week count per month) that is not used in this measure |
| **`0.15`** default in `Percentage Filter Value` | DAX measure `SELECTEDVALUE(..., 0.15)` | Default significance filter: only show items where `Abs Diff%` > 15% | **No** — 15% is the "significance" threshold chosen by whoever built this; no documented business rationale |
| **`20`** default in `Qty Diff Value` | DAX measure `SELECTEDVALUE(..., 20)` | Default absolute unit filter: ignore signals < 20 units | **No** — 20 units suppresses noise for low-volume items; why 20 and not 10 or 50 is undocumented |
| **`MIN > 0`** condition in `Writ Acct +/- (2)` | DAX measure | Prevents false "below trend" signal when lower control bound is negative | **Partially** — the existence of v2 implies someone noticed the negative-bound problem in v1 |
| **`EDATE(TODAY(), -1)`** in `Future Flag` | DAX measure | "Past" = before the prior calendar month start | **No** — uses calendar months, not fiscal months |
| DSG account number list (13 accounts) | Multiple SQL queries | These accounts are bucketed as "DSG" across all queries | **No** — hardcoded in SQL; if DSG adds/removes accounts, all SQL queries must be updated independently |
| Non-A account bucketing | `Weekly Writ Qties` SQL | ABC <> 'A' → "Non-A Accounts - Various" | **No** — "A" is the ABC classification threshold; definition of what qualifies as an A-account is in `CustomerAcctMaster_AFI` |
| `TOP 1000` in `Warehouses` SQL | SQL | Limits warehouse dimension to 1,000 rows | **No** — unexplained cap; risk if WH count grows |
| `Current Status IN ('N','C')` in item filters | Both SQL `#itemlist` temp tables | Only New and Current status items included in trend/signal analysis | **No** — Discontinued and other status items are silently excluded from the worklist |

---

## 10. Comparability / Consistency

1. **`@Stdevs = 1.5` (Trend Data) vs. `@Stdevs = 2` (Weekly Writ Qties) — two signals at different sensitivities.** `Trend +/-` uses the 1.5σ bounds from `Trend Data`; `Writ Acct +/-` uses the 2σ bounds from `Weekly Writ Qties`. A user comparing these two flags on the same row will see different signal sensitivity without any visual indication that they use different thresholds. An item could be flagged as "Trend +" but not "Writ Acct +" for the same week.

2. **`Avg Wkly FC` uses hardcoded `4.33` instead of the `Weeks` column in `FC` table.** The `FC` table has a `Weeks` column that counts the actual number of weeks in each fiscal month (4 or 5). Using 4.33 (the calendar average) produces a weekly rate that is wrong for 5-week fiscal months (underestimates by ~17%) and wrong for 4-week fiscal months (overestimates by ~8%). `Trend % of wklyFC` comparisons will be systematically off in 4-week and 5-week months.

3. **`Account Group` is computed differently in `Trend Data` vs. `Weekly Writ Qties`.** Non-A accounts are bucketed as `Customer Group` in Trend Data but as `'Non-A Accounts'` (a constant string) in Weekly Writ Qties. The relationship `Weekly Writ Qties[Account Group] → Customers[Account Group]` and `Trend Data[Account Group] → Customers[Account And ShipTo Number]` use different join columns. When a visual shows both `Writ Qty` and `Trend Average` filtered by "Account Group," they may be at different grains.

4. **`Dates` table is a raw `DimDate` query vs. `z_FiscalCal` used in other models.** `z_FiscalCal` (from `AshleyFiscalCalendarV2` dataflow) may include corrections, adjustments, or additional derived columns not present in raw `DimDate`. If a fiscal week boundary was adjusted in `AshleyFiscalCalendarV2`, the two calendars would diverge — making week-to-week comparisons between this report and others potentially misaligned.

5. **`FC` uses `ForecastCommonContainer_Logility` (Logility file snapshot) vs. `DemandForecastSnapshot` (standard promoted forecast) used in other models.** The file-based Logility snapshot and the promoted forecast snapshot may differ in timing, coverage, and which levels of the planning hierarchy are included. Comparing `Avg Wkly FC` from this model to forecasts from Forecast Review or Product Review (NEW) may show different numbers for the same item-month.

---

## Closing — Interview Seeds

1. **"When `Trend +/-` shows −1 for an item, what do you do first — open Logility, call the sales rep, look at something else? And is there a minimum number of consecutive weeks at −1 before you actually change the forecast?"**
   *(Targets: the trigger-to-action path; whether a single-week signal drives a decision or multiple weeks are needed; the escalation rule.)*

2. **"The trend bounds in this report use 1.5 standard deviations for the trend flag and 2 standard deviations for the written order flag. Do you know those thresholds are different — and if an item shows 'Trend −' but not 'Writ Acct −', do you act on it differently?"**
   *(Targets: whether planners understand the dual-sensitivity design; whether the inconsistency causes confusion; whether one of the two flags can be retired.)*

3. **"The weekly forecast average is divided by 4.33 to get a per-week rate. Fiscal months are actually 4 or 5 weeks. In a 5-week month, this makes the weekly forecast look about 17% lower than it actually is. Has anyone noticed that `Trend % of wklyFC` fluctuates predictably with 5-week months?"**
   *(Targets: surfaces the 4.33 bug; whether the distortion has been noticed or attributed to demand noise; whether fixing it would change any decisions.)*

4. **"This report compares the last 6 weeks of orders to a 13-week short-term and 26-week long-term baseline. If a product had a major promotion 7 months ago that inflated demand for 8 weeks, that would still be in the 26-week baseline. How do you handle items where the historical baseline is distorted by one-time events?"**
   *(Targets: awareness of the statistical model's assumptions; whether ad-hoc events are excluded from the baseline; whether there's a mechanism to flag distorted baselines.)*

---

*Analysis based on BIM definition extracted 2026-07-08. BIM saved to [bim/Demand_Sensing_Report.bim](bim/Demand_Sensing_Report.bim). No bundle indexes were modified.*
