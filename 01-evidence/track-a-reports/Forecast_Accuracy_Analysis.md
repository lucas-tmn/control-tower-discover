# Forecast Accuracy — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | Supply Chain Analytics-Premium |
| **Report Name** | Forecast Accuracy |
| **Backing Model** | SCP Forecast Accuracy (`08f13036-5182-4e09-a4ea-cce6135b4640`) |
| **Model Size** | 29 tables, 80 measures (72 + 4 + 3 + 1) |
| **Analyzed** | 2026-07-07 |

> **Note on model identification:** No semantic model named "Forecast Accuracy" exists in the workspace. The most comprehensive matching model is "SCP Forecast Accuracy" (29 tables). A second candidate "Forecast Accuracy (ItWh)" (23 tables) was not analyzed. Confirm the backing model with the workspace owner.

---

## §1 — Supply-chain question & chain link

**Question:** How accurately are demand forecasts predicting actual sales — by SKU, warehouse, customer group, planner, and forecast horizon (2 Week / 30 Day / 60 Day / 90 Day / 120 Day) — and what is the financial value of improving that accuracy?

| Link | How served |
|---|---|
| **Forecast** (primary) | Measures accuracy of Logility Resultant + Promo Lift vs. actual demand across 5 horizons using wMAPE / MAPE / MASE / RMSE / sMAPE + YTD + YoY variants |
| Demand | Actual demand (`ItemActualDemand_Logility`) is the denominator for all accuracy metrics |
| Supply | Forecast error directly exposes safety stock and service level risk |
| Inventory | Financial impact model connects wMAPE improvement → incremental net sales via service level and gross margin bridge |

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Which planners / teams have best vs worst accuracy? Assign coaching, rebalance portfolios, set targets | WBR-Leadership / Manager | Monthly | Performance / Governance |
| Which SKUs / collective classes have lowest wMAPE? Prioritize manual overrides or model changes in Logility | Planner / Analyst | Monthly | Operational |
| Is the forecast systematically biased over or under? Adjust in Logility | Planner / Analyst | Monthly | Operational |
| Which forecast horizon is most accurate? Set ordering cadence to most reliable horizon | Analyst / S&OP Lead | Quarterly | Performance / Governance |
| Does the statistical forecast add value over a naive model? (Forecast Value Added) Justify Logility investment | Manager / S&OP Lead | Quarterly / Annual | Financial-Justification |
| Is wMAPE improving or degrading YoY? Supply-chain S&OP KPI tracking | Executive / WBR-Leadership | Monthly (WBR) | Performance / Governance |
| What is the financial impact of a X% improvement in accuracy? Build executive business case | Executive / Finance | Quarterly / Annual | Financial-Justification |
| Which ABC/XYZ tier drives most error? Prioritize A-items | Planner / Analyst | Monthly | Operational |
| Are No-Go/new SKUs inflating error metrics? Decide whether to exclude from wMAPE targets | Planner / Analyst | Weekly | Performance / Governance |

---

## §3 — Key metrics / measures

**Total: 80 measures** — 72 in `AFI Forecast Accuracy`, 4 in `AFI Sales & Cost`, 3 in `Impact Measures`, 1 in `Additional Forecast Improvement`.

### A. Primary accuracy measures

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| Total Demand | Actual units sold | Item × WH × CustGrp × FiscalMonth | `SUM([Actual Demand Quantity])` |
| Total Forecast | Promoted Resultant Forecast | Same | `SUM([Promoted Resultant Forecast Quantity])` |
| Total Forecast Error | Forecast − Actual | Same | `SUM([Forecast Error])` |
| Total Forecast Bias | Systematic over/under ratio | Same | `DIVIDE([Forecast Error],[Forecast])` |
| Total Forecast Attainment | Actual ÷ Forecast; 1.0 = perfect | Same | `DIVIDE([Demand],[Forecast])` |
| Total wMAPE ⭐ | Volume-weighted MAE / mean demand (primary KPI) | Aggregated | `DIVIDE([MAD],[Mean Actual Demand])` |
| Total Naive wMAPE | Naive baseline (2-month lookback) | Aggregated | `DIVIDE([Naive MAD],[Mean Actual Demand])` |
| Total Forecast Value Added | wMAPE minus Naive wMAPE | Aggregated | `[wMAPE] - [Naive wMAPE]` |
| Total MASE | MAD ÷ Naive MAD (< 1 = better than naive) | Aggregated | `DIVIDE([MAD],[Mean ABS Scaled Error])` |
| Total RMSE | Root mean squared error | Aggregated | `SQRT([MSE])` |
| Total Tracking Signal | Forecast bias momentum detector | Aggregated | `DIVIDE([Forecast Error YTD],[MAD])` |

> ⚠️ **Suspicious — `Total MASE` denominator:** Uses `AVERAGEX([ABS Scaled Error])` where `[ABS Scaled Error]` is a pre-computed SQL column. If this column uses a 3-month naive lag (matching the historical table) while DAX `[Total Naive wMAPE]` uses 2-month lag, MASE and Forecast Value Added reference **different naive benchmarks in the same model**. See §10.

> ⚠️ **Suspicious — `Additional Forecast Improvement Value` default = 1:** `SELECTEDVALUE([Additional Forecast Improvement %], 1)` — fallback when no slicer row is selected is **1 (= 100%)**, making `[Total wMAPE - Improvement] = wMAPE - 1.0` (negative). Any page displaying this measure without the slicer active shows nonsense. Default should be `0`.

> ⚠️ **Suspicious — `Total Service Level %`:** `DIVIDE(SUM([Total Service Level]),[Total Demand])`. If `[Total Service Level]` is a rate column (0–1 per row), summing rates then dividing by demand units is dimensionally incorrect. Used directly in the Forecast Impact formula.

> ⚠️ **Suspicious — `Total Tracking Signal` window mismatch:** Numerator is YTD cumulative; denominator is point-in-time MAD. Standard tracking signal uses running-average MAD. The two windows differ throughout the year, making the signal unstable early in each fiscal year.

> ⚠️ **Duplicate measure — `Total MAD-MEAN Ratio` = `Total wMAPE`:** Identical DAX formula `DIVIDE([MAD],[Mean of Actual Demand])` under two different names.

### B. Time-intelligence variants

- `TOTALYTD` × 7 measures (demand, forecast, ABS error, MAD, wMAPE and YTD variants)
- `PARALLELPERIOD(...,-12,MONTH)` × 6 measures (previous year variants)
- `DATESINPERIOD(...,-6,MONTH)` × 2 measures (6-month trend)

> ⚠️ All YTD measures use `'AFI Forecast Accuracy'[Fiscal Date]` directly → resets at **January 1** (calendar year), not at Ashley fiscal year start. Any "YTD" label against fiscal-year targets is calendar-year, not fiscal-year.

### C. Financial impact measures

| Measure | Full DAX Expression |
|---|---|
| Forecast Impact - Net Sales | `[Total Net Sales]*(1-[Total Service Level %])*[Gross Margin % - Standard Cost]*3*(([Total Historical wMAPE]-[Total wMAPE])/[Total Historical wMAPE])` |
| Forecast Impact - Net Sales (What If) | Same formula, replaces `[Total wMAPE]` with `[Total wMAPE - Improvement]` |
| Forecast Impact - Net Sales (Improvement) | `[What If] - [Current]` |

**`* 3` multiplier is hardcoded and undocumented.** See §9.

### D. What-If slicer

`GENERATESERIES(0, 0.105, 0.005)` — range 0% to 10.5% in 0.5% steps. Max slider value undocumented.

---

## §4 — Data sources & lineage

| Source | Type | Flag |
|---|---|---|
| `ashley-edw.database.windows.net / ashley_edw` + `ASHLEY_EDW` | Azure SQL (EDW) | ⚠️ Casing inconsistency — same server, two database name cases |
| PowerBI Dataflow `CurrentProductDetails` (`workspaceId=a47e4573`, `dataflowId=346f2aa1`) | PBI Dataflow | ✅ Governed |
| SharePoint User List (`95e7d6e4-…`) at `masterashley.sharepoint.com/sites/supplychain-DemandPlanning` | SharePoint Tables | ⚠️ Ungoverned manual list |
| SharePoint Planner Assignment (`531a515e-…`) | SharePoint Tables | ⚠️ Ungoverned manual list |
| `Impact Measures` table | Inline static row (Binary.Decompress base64) | ⚠️ Hardcoded static container |

**EDW objects touched:**

| Schema.Object | Table fed |
|---|---|
| `Enterprise_DW.DimDate` | Ashley Fiscal Calendar |
| `SupplyChain_DW.DimForecastDetails` | AFI Forecast Accuracy (fact) |
| `SupplyChain_Enh.ForecastTimePeriods` | AFI Forecast Accuracy |
| `SupplyChain_Enh.DemandForecastSnapshot` | AFI Forecast Accuracy |
| `SupplyChain_Enh.ItemActualDemand_Logility` | AFI Forecast Accuracy + AFI Historical |
| `SupplyChain_DW.DimDateFile` | Naive forecast date alignment |
| `SupplyChain_Enh.ItemForecast_Logility` | AFI Historical Forecast Accuracy |
| `Wholesale_Marketing.ItemMaster` | AFI Historical (Z%K exclusion) |
| `PowerBI_SupplyChain.FCC_LogilityCurrentDay` | AFI Logility (planner/location) |
| `PowerBI_SupplyChain.CurrentProductDetails` | AFI Status + AFI Sales & Cost |
| `PowerBI_SupplyChain.ItemABCCode` (stored proc) | ABC-XYZ hidden table |
| `Wholesale_DemandPlanning.ItemServiceLevel` | AFI Service Level |
| `PowerBI_Wholesale.InvoiceHistory` | AFI Sales & Cost |
| `PowerBI_Wholesale.QualityCosts` | AFI Sales & Cost |
| `MasterData_ItemMaster_AFI.ITMRVB` | AFI Sales & Cost (std cost) |
| `PowerBI_SupplyChain.CustomerAcctMaster_AFI` | Bridge table |

Additional flags:
- SQL `CommandTimeout = #duration(0,3,0,0)` (3 hours) on three large tables
- `AFI Sales & Cost` uses `GETDATE()` at refresh — date window desync risk on failed refresh
- No RLS — all users see all items, warehouses, and customer groups
- No ungoverned Excel/CSV for fact data

---

## §5 — Grain & snapshot strategy

**Primary grain:** SCP Item × AFI Warehouse Code × Fiscal Date (month-end) × Forecast Period (2W / 30D / 60D / 90D / 120D) × CustomerGroupS

**Snapshot strategy:** Required and implemented. SQL UNPIVOT on `ForecastTimePeriods` converts wide 5-horizon columns to tall snapshot format. Historical baseline adds a second time dimension: `Historical Fiscal Date = Fiscal Date + 91 days`.

**Fiscal windows:**
- Ashley Fiscal Calendar: FiscalYearIndicator −5 to +2 (7 years)
- AFI Forecast Accuracy (current): FiscalYearIndicator ≥ −2 (3 years)
- AFI Historical Forecast Accuracy: FiscalYear ≥ start of FY-2
- AFI Sales & Cost: FY-2 to today

---

## §6 — Dimensions used

| Dimension | Source | Drift risk |
|---|---|---|
| Product | PBI Dataflow `CurrentProductDetails` (95 cols) | **Team column** SWITCH hard-codes ~20 planner IDs → silently blank for unlisted planners; **Collective Class Group** SWITCH won't catch new accessory classes; **In-Line/No-Go** hardcodes `"New"` status string |
| Date | `Enterprise_DW.DimDate` (42 cols, FY −5 to +2) | `FiscalMoYr` calc column `LEFT(MonthName,3)+"-"+RIGHT(Year,2)` breaks if month name format changes; YTD/YoY use calendar year, not fiscal year |
| Warehouse | **None** — string embedded in fact only | ⚠️ No name, type, or location attributes; filter-only |
| Customer Group | Embedded string + CustGrp-CC bridge | No customer name, segment, or geography |
| Planner / Team | SharePoint lists + Product dim | Manually maintained; stale on personnel changes |
| ABC-XYZ | Hidden `ABC-XYZ` table via stored proc | Duplicated as RELATED columns on Product dim — two copies of same classification |
| Service Level | `ItemServiceLevel` (ForecastLevel=3 filter only) | One level available; no per-item level variants |

Missing conformed dimensions: no standalone Warehouse, no Vendor, no Production Resource.

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| `AFI Status` (hidden) duplicates `AFI Product Details` | Both pull from `PowerBI_SupplyChain.CurrentProductDetails`. One-to-one bothDirections relationship — leftover workaround never cleaned up |
| ABC/XYZ in two places | Hidden `ABC-XYZ` table + RELATED calculated columns on Product dim. `ForecastPriority` / `CoefVar` only on hidden table |
| Warehouse exclusion vs. inclusion inconsistency | Current fact uses `NOT IN` exclusion list; historical and sales tables use `IN` inclusion list. Different warehouse populations between current and historical periods |
| `CurrentStatus` on fact via RELATED | SCD issue: historical rows reflect today's status, not status at time of forecast |
| `Concatenate` / `Concatenate2` naming collision | Same column names across tables, different semantics |
| Naive lag inconsistency | 2-month in current fact vs 3-month in historical fact |
| `Total MAD-MEAN Ratio` = `Total wMAPE` | Identical formula, two names |
| YTD/PY pattern × 5 metrics | 15+ measures follow identical TOTALYTD/PARALLELPERIOD pattern — candidate for calculation group |
| Team mapping via SWITCH | ~20 hardcoded employee IDs — personnel data in semantic model |

---

## §8 — Open questions

1. Which semantic model backs the plain "Forecast Accuracy" report? (Three candidates; no exact name match)
2. Is the 91-day date shift on Historical Fiscal Date documented and validated?
3. What does the `* 3` multiplier in Forecast Impact represent?
4. Why is there no standalone Warehouse dimension?
5. Is the Team SWITCH column actively maintained?
6. Are the SharePoint planner lists current?
7. Is the naive-lag difference (2M vs 3M) intentional?
8. Does the financial impact model account for item/warehouse margin mix?
9. Who uses which pages in WBR vs monthly vs S&OP?
10. Is `AFI Logility` (FCC_LogilityCurrentDay) actually used in any visual?

---

## §9 — Business assumptions / magic numbers

### 9.1 — `* 3` multiplier in Forecast Impact formula

**Full formula:**
```
Forecast Impact - Net Sales =
  [Total Net Sales]
  × (1 - [Total Service Level %])
  × [Gross Margin % - Standard Cost]
  × 3
  × ([Total Historical wMAPE] - [Total wMAPE]) / [Total Historical wMAPE]
```

`* 3` appears in both `Forecast Impact - Net Sales` and `Forecast Impact - Net Sales (What If)`. No comment, no named variable, no documentation. Most likely candidates: 3-month inventory carrying period, a demand amplification factor, or a "rule of three" heuristic. **This scalar multiplies the entire executive business case result. If wrong by 50%, the dollar projection is wrong by 50%.**

### 9.2 — `+91 days` date shift on Historical Fiscal Date

```m
Table.AddColumn(..., "Historical Fiscal Date", each Date.AddDays([Fiscal Date], 91))
```

Forward-shifts all historical forecast rows by 91 days to align them with the "current" reporting period. Business rationale not documented. If the assumption is wrong, all `[Total Historical wMAPE]` baseline values are misaligned, invalidating the Forecast Impact formula entirely.

### 9.3 — Naive forecast lag inconsistency

| Table | SQL offset |
|---|---|
| `AFI Forecast Accuracy` | `DATEADD(MM,-2,[Year Period])` |
| `AFI Historical Forecast Accuracy` | `DATEADD(MM,-3,[Year Period])` |

Not documented. `[Total MASE]` uses the pre-computed SQL `[ABS Scaled Error]` column (likely 3-month lag), while `[Total Forecast Value Added]` uses DAX `[Total Naive wMAPE]` (2-month lag). **MASE and Forecast Value Added use different naive benchmarks.**

### 9.4 — `GENERATESERIES(0, 0.105, 0.005)` — max 10.5% slider cap

The What-If slicer caps at 10.5% wMAPE improvement. No documented reason. If a business case needs to model >10.5% improvement, the slider cannot represent it.

### 9.5 — `SELECTEDVALUE([Additional Forecast Improvement %], 1)` — default = 1 (likely bug)

When no slicer value selected, fallback is `1` (100%), making `[Total wMAPE - Improvement]` negative. Any page displaying this measure without the slicer active shows garbage. Default should be `0`.

### 9.6 — `Total Service Level %` formula potentially dimensionally incorrect

`DIVIDE(SUM([Total Service Level]),[Total Demand])` — if `[Total Service Level]` is a per-row rate (0–1), summing rates and dividing by demand units is dimensionally meaningless. Used directly in Forecast Impact formula.

### 9.7 — Blended gross margin in impact formula

`[Gross Margin % - Standard Cost]` is a single blended rate across all items and warehouses in context. Filtering to high-margin items inflates impact; low-margin items deflates it. The formula **implicitly assumes homogeneous margins** — never flagged in the report.

### 9.8 — Complete risk matrix for Forecast Impact formula

| Factor | Assumption | Verified? |
|---|---|---|
| `(1 − SL%)` | SL% correctly computed from fill units, not rates | ❌ Uncertain |
| `Gross Margin%` | Blended margin applies uniformly to all items in scope | ❌ Not valid for mixed portfolios |
| `× 3` | Some business multiplier justifying 3× amplification | ❌ Undocumented |
| `HistoricalwMAPE` | +91-day date shift aligns "before" period correctly | ❌ Undocumented |
| Relative improvement ratio | Current vs historical naive lag is consistent | ❌ Not consistent (2M vs 3M) |

---

## §10 — Comparability / consistency

### 10.1 — Naive forecast lag: 2M (current) vs 3M (historical)

`MASE` and `Forecast Value Added` are not comparable across current and historical periods. Any YoY "are we beating naive?" comparison is invalid because the benchmark itself changed.

### 10.2 — Warehouse list: exclusion (current) vs inclusion (historical)

`AFI Forecast Accuracy` uses `NOT IN` on an exclusion list. `AFI Historical` and `AFI Sales & Cost` use `IN` on a different inclusion list. Warehouse '232' appears in the historical inclusion list but also in the current exclusion list. **Current and historical accuracy metrics cover different warehouse populations.** Aggregate comparisons blend different scopes.

### 10.3 — YTD = calendar year, not fiscal year

`TOTALYTD([wMAPE], 'AFI Forecast Accuracy'[Fiscal Date])` resets at January 1. Any "YTD" label on an Ashley fiscal-year dashboard is calendar-year, not fiscal-year. If Ashley's fiscal year starts in a month other than January, all YTD metrics are wrong relative to fiscal targets.

### 10.4 — Two error denominator conventions (MAPE vs sMAPE)

`Total ABS % Error` = `|Demand - Forecast| / Demand` — explodes when demand ≈ 0.
`Total sABS % Error` = `|Demand - Forecast| / ((Demand + Forecast) / 2)` — bounded, symmetric.

Both appear as percentage error metrics with similar names. Not directly comparable.

### 10.5 — `Total MAD-MEAN Ratio` = `Total wMAPE` (identical formula, two names)

Two measures, one formula. Always show the same number. Maintenance trap for any developer who assumes they measure different things.

### 10.6 — Two bias metrics with different denominators

`Total Forecast Bias` = `Forecast Error / Forecast` (over-forecast → +1)
`Total Normalized Forecast Metric` = `(Forecast - Demand) / (Forecast + Demand)` (over-forecast → max +0.5)

Same phenomenon, different scales. If both appear without clear labeling they tell different stories from the same data.

### 10.7 — Service Level % and Sales & Cost time window mismatch

`AFI Forecast Accuracy` and `AFI Sales & Cost` are refreshed independently. `AFI Sales & Cost` uses `GETDATE()` at refresh. If refreshes occur at different times, the `Service Level%` and `Gross Margin%` fed into the same Forecast Impact formula are from different time windows.

---

## Closing — Interview seeds

**1. On the `* 3` multiplier:**
> "The financial impact formula multiplies by a constant 3. Where does that number come from — is it an inventory turns assumption, a lost-sales amplification factor from a specific study, or something else? And when was it last reviewed against actual business performance?"

**2. On trust and usage:**
> "When you look at the Forecast Impact dollar number in this report and present it to leadership, what would need to be true for you to be comfortable committing to that number — and have you ever had leadership push back on it?"

**3. On the historical baseline and the +91-day shift:**
> "The 'historical wMAPE' used as the 'before' baseline shifts dates forward by 91 days. Who set that up and what was the intent — is it aligning a specific prior planning cycle to today's review period, and do you verify it still makes sense each year?"

**4. On the Service Level % source:**
> "The service level percentage feeding into the impact formula comes from a column in the forecast accuracy table. Is that number a pre-calculated service level rate loaded from Logility, or is it computed from fulfilled-vs-ordered quantities — and does it match what your operations team reports as their fill rate?"
