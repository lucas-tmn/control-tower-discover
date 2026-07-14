# Demand Fulfillment — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `06d8bddb-c259-433e-aef6-62c3cd949a45`  
**Report ID:** `11494f80-bea9-447c-8805-6e84bd1b528f`  
**Analysis Date:** 2026-07-08  
**Model Size:** 20 tables (2 fact + 1 bridge + 3 dim + local date tables); **32 DAX measures** (24 in `Demand Fulfillment`, 8 in `Top Negatives`); Compatibility Level 1567  
**BIM File:** [bim/Demand_Fulfillment.bim](bim/Demand_Fulfillment.bim)  
**Note on BIM:** Source JSON contains case-variant duplicate translation keys (`SI_negative__Last_Week` vs `SI_negative__last_week`). BIM extracted via Node.js (last-value-wins). PowerShell `ConvertFrom-Json` cannot parse the raw file.

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For each item-warehouse by week, how much of the total demand (firm customer orders + net forecast) is covered by shippable inventory — and which series/items are most "at-risk" (highest SI Negative)?

This is a **weekly supply coverage / demand fulfillment rate** report. It answers:
1. What % of demand is the current supply plan able to cover? (`Total % Cust Orders Covered`)
2. How did that change week-over-week?
3. Which items/series have the largest uncovered demand (Top Negatives)?

**Primary chain links served:**

| Link | How served |
|---|---|
| **Inventory / Supply** | `Demand Fulfillment[SI Negative]` — shippable inventory shortfall vs. demand; `[On Hand Qty]`, `[On Hand $]` |
| **Demand** | `Demand Fulfillment[Firm Demand]` — allocated customer orders; `[Net Forecast]` — unfirmed forecast demand |
| **Forecast** | `TblForecastCommonContainer_Logility` — Logility planning details (planner, series, import/domestic); linked via Item-WH concatenate key |
| **Demand Fulfillment rate** | Core KPI: `(Firm Demand + Net Forecast + SI Negative) / (Firm Demand + Net Forecast)`, clamped [0,1] |

**Not served:** On-time delivery, forecast accuracy, order history, receipts.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Assess overall demand fulfillment rate** vs. 90% goal — are we above or below target this week vs. last week? | WBR Leadership / Planning Director | Weekly (WBR) | **Performance/Governance** — scorecard |
| **Identify worst-performing series** by SI Negative — `Top Negatives` worklist ranked by dollar shortfall | Supply Planner / DRP Planner | Weekly | **Operational** — expedite, source alternative, flag customer |
| **Track WoW change** in Firm Demand and SI Negative — is the gap growing or closing? | Supply Planner / Planning Manager | Weekly | **Performance/Governance** — trend accountability |
| **Category-level DF rate comparison** — which Collective Class × Import/Domestic Code is dragging overall DF? | Category Analyst / Planning Manager | Weekly | **Performance/Governance** — prioritization |
| **Monitor DF against category-specific goals** (`DF Goal` column) — Import items have different targets than Domestic | Inventory Planner / Category Analyst | Weekly | **Performance/Governance** — manage to tiered targets |
| **6-month moving average tracking** (`Total % Cust Orders Covered 6MMA`) — smooth weekly noise, see structural trend | Planning Director / Executive | Monthly | **Performance/Governance** — strategic trend |
| **Dollar-value shortfall** (`SI Neg $` in Top Negatives) — which items have largest revenue-at-risk | Planning Manager / Finance | Weekly | **Financial-Justification** — prioritize supply actions by $ impact |

---

## 3. Key Metrics / Measures

### From `Demand Fulfillment` table (24 measures)

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `Total Firm Demand` | Sum of allocated customer orders | Item × WH × Week | `SUM(Demand Fulfillment[Firm Demand])` | |
| `Total Net Forecast` | Sum of net (unfirmed) forecast demand | Item × WH × Week | `SUM(Demand Fulfillment[Net Forecast])` | |
| `Total SI Negative` | Sum of SI shortfall (negative shippable inventory) | Item × WH × Week | `SUM(Demand Fulfillment[SI Negative])` | ⚠️ column is raw negative value from EDW; see §9 |
| `Total On Hand Qty` | Sum of on-hand inventory | Item × WH × Week | `SUM(Demand Fulfillment[On Hand Qty])` | |
| `Total % Cust Orders Covered` | Demand fulfillment rate, clamped [0,1] | Item × WH × Week | `(FirmDemand + NetForecast + SINegative) / (FirmDemand + NetForecast)`, IFERROR→0 | ⚠️ **4 versions exist** — see §7 |
| `Total % Cust Orders Covered v2` | Alt DF rate — uses `SI Negative` alone as numerator | — | `SINegative / (FirmDemand + NetForecast)`, clamped [0,1] | ⚠️ **different formula** — see §7 |
| `Total % Cust Orders Covered v2.1` | Alt DF rate — uses `ABS(SI Negative)` as numerator | — | `ABS(SINegative) / (FirmDemand + NetForecast)`, clamped [0,1] | ⚠️ **different formula** — see §7 |
| `Total % Cust Orders Covered v3` | Same as primary measure — exact duplicate | — | Identical to `Total % Cust Orders Covered` | ⚠️ exact duplicate |
| `Total % Cust Orders Covered 6MMA` | 6-month moving average of weekly DF rate | Week | `AVERAGEX(DATESINPERIOD(..., -182, DAY), [Total % Cust Orders Covered])` | ⚠️ hardcoded 182 days — see §9 |
| `Total % Cust Orders Covered YTD` | YTD average DF rate | Week → Year | `CALCULATE([Total % Cust Orders Covered], DATESYTD(Fiscal Date))` | |
| `Demand Fulfillment Goal` | Global DF target | — | **Constant literal `0.90`** | ⚠️ hardcoded scalar — see §9 |
| `Firm Demand - This_Week` | Firm demand for the most recent week only | Item × WH | `SUM(Demand Fulfillment[Firm Demand - This Week])` | ⚠️ column calc uses `MAX(Fiscal Date)` — see §9 |
| `Firm Demand - Last_Week` | Firm demand one week prior | Item × WH | `SUM(Demand Fulfillment[Firm Demand - Last Week])` | ⚠️ same `MAX` pattern |
| `SI Negative - This_Week` | SI shortfall this week | Item × WH | `SUM(Demand Fulfillment[SI Negative - This Week])` | |
| `SI Negative - Last_Week` | SI shortfall last week | Item × WH | `SUM(Demand Fulfillment[SI Negative - Last Week])` | |
| `Net Forecast - This_Week` | Net forecast this week | Item × WH | `SUM(Demand Fulfillment[Net Forecast - This Week])` | |
| `Net Forecast - Last_Week` | Net forecast last week | Item × WH | `SUM(Demand Fulfillment[Net Forecast - Last Week])` | |
| `Firm Demand - This Wk over Last Wk` | WoW absolute change in Firm Demand | Item × WH | `This Week − Last Week` | |
| `Firm Demand - This Wk over Last Wk %` | WoW % change | Item × WH | `This Week / Last Week`, IFERROR→BLANK | |
| `SI Negative - This Wk over Last Wk` | WoW absolute change in SI Negative | Item × WH | `This Week − Last Week` | |
| `SI Negative - This Wk over Last Wk %` | WoW % change | Item × WH | `This Week / Last Week`, IFERROR→BLANK | |
| `% Cust Order Covered - This_Week` | DF rate for this week only | Item × WH | Same clamped formula using This Week columns | |
| `% Cust Order Covered - Last_Week` | DF rate for last week only | Item × WH | Same clamped formula using Last Week columns | |

### From `Top Negatives` table (8 measures)

| Measure | Business meaning | Flag |
|---|---|---|
| `Total Firm Dmnd` | Firm demand for negatives worklist | Note: different measure name from `Total Firm Demand` in main table |
| `Total SI Neg` | SI negative for worklist | |
| `Total SI Neg $` | `SUM(SI Neg $)` = `SI Negative × Current Unit Price` | ⚠️ `VALUE(Current Unit Price)` — text-to-number cast; see §9 |
| `Total % of Out of Stock` | `ABS(SI Neg) / Firm Demand × 100` — expressed as percentage | ⚠️ no clamping; can exceed 100% |
| `Ranking` | Dense rank by descending `SI Neg $` across Series × CC × Vendor × Office | Expensive RANKX across 4 dimensions |
| `Total SI Neg $ %` | Series' SI Neg $ as % of total across all series | |
| `Total Unit Price` | `Total SI Neg $ / Total SI Neg` — implied average unit price | |
| `Total % Out of Stock` | Text version of `Total % of Out of Stock` — `LEFT(value, 4) & "%"` | ⚠️ text truncation may cut decimal places |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`Demand Fulfillment`** | PowerBI Dataflow `ccbb84a2...` workspace `a47e4573...` → entity `Demand Fulfillment` | Governed Dataflow | Medium — same dataflow used in Product Review (NEW) |
| **`TblForecastCommonContainer_Logility`** | Same dataflow `ccbb84a2...` → entity `TblForecastCommonContainer_Logility` (filtered: `Item-Lvl1 <> null`, adds `Item/Whse` concat key, deduped) | Governed Dataflow | Medium |
| **`Top Negatives`** | Same dataflow `ccbb84a2...` → entity `Top Negatives` | Governed Dataflow | Medium |
| `z_ProductDetails` | Dataflow `346f2aa1...` → `CurrentProductDetails` | Governed Dataflow | Low |
| `z_VendorMaster` | Same dataflow → `VendorMaster` | Governed Dataflow | Low |
| `z_WarehouseMaster` | Same dataflow → `WarehouseMaster` | Governed Dataflow | Low |
| `z_FiscalCal` | Same dataflow → `AshleyFiscalCalendarV2` | Governed Dataflow | Low |

**All sources governed dataflows — no direct SQL, no SharePoint Excel.** Cleanest sourcing lineage of all models analyzed so far.

> `Demand Fulfillment`, `TblForecastCommonContainer_Logility`, and `Top Negatives` all come from the **same dataflow** (`ccbb84a2`) — a separate "Supply Chain Analytics" dataflow in workspace `a47e4573`, distinct from the product/calendar/warehouse dataflow (`346f2aa1`). This dataflow is also used by `DemandFulfillment` table in Product Review (NEW).

> **No Fabric sources. No SharePoint. No direct SQL in Power BI model.**

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Item SKU (`DF Item`) × Warehouse (`AFI Warehouse Code`) × **Fiscal Week** (`Fiscal Date`)

**Snapshot strategy:**
- `Demand Fulfillment` — dataflow entity; likely refreshed weekly (one row per item-WH-week). Contains historical weekly rows — enables WoW comparison and 6MMA trend.
- `Top Negatives` — dataflow entity; appears to be current-week focused (has `Fiscal Date` but grain unclear without dataflow definition access).
- `TblForecastCommonContainer_Logility` — planning attributes table; appears to be current-state (no date column for historical versioning).

**Historical depth:** Visible from relationships — `Demand Fulfillment[Fiscal Date]` links to `z_FiscalCal`, enabling multi-week trend. `Total % Cust Orders Covered 6MMA` uses 182 days (~6 months) of weekly data, confirming at least 6 months of history is expected.

**This/Last Week columns** are calculated within the dataflow table using `MAX(Fiscal Date)` row-level expressions (see §9 for risk).

---

## 6. Dimensions Used

| Dimension | Table | Connected? | Notes |
|---|---|---|---|
| **Product** | `z_ProductDetails` (93 cols) | ✅ — `Demand Fulfillment[DF Item]` → `z_ProductDetails[Item SKU]` | Conformed; no calculated columns added in this model |
| **Warehouse** | `z_WarehouseMaster` (11 cols) | ✅ — `Demand Fulfillment[AFI Warehouse Code]` → `z_WarehouseMaster[Warehouse]` | Conformed |
| **Date / Fiscal Calendar** | `z_FiscalCal` (45 cols) | ✅ — `Demand Fulfillment[Fiscal Date]` and `Top Negatives[Fiscal Date]` | This model's z_FiscalCal has **45 columns** — more than other models (38–43); adds `This Week`, `Last Week`, `2 Weeks Ago`, `3 Weeks Ago`, `Current Week Sort`, `Current Week` calc columns specific to WoW analysis |
| **Vendor** | `z_VendorMaster` (11 cols) | ✅ — via `TblForecastCommonContainer_Logility[Planning Vendor]` → `z_VendorMaster[VendorNumber]` | Indirect relationship through bridge table |
| **Logility Planning Context** | `TblForecastCommonContainer_Logility` (25 cols) | ✅ — bridge key `Concatenate` (Item-WH) links `Demand Fulfillment` to Logility planning attributes | Acts as a bridge/lookup table, not a pure dimension |

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `Firm Demand - This Week` | `Demand Fulfillment` calc column | `IF(Fiscal Date = MAX(Fiscal Date), Firm Demand)` | ⚠️ **High** — `MAX(Fiscal Date)` evaluated in row context of the entire table. If the dataflow contains multiple weeks, MAX returns the latest week across ALL rows, correctly isolating this week. But this pattern fails if the table is filtered before evaluation. |
| `Firm Demand - Last Week` | Same | `IF(Fiscal Date = MAX(Fiscal Date) - 7, Firm Demand)` | ⚠️ **High** — hardcoded `-7` days. If a week is missing from the data (refresh gap), `MAX - 7` doesn't match any row → Last Week = 0 silently |
| `SI Negative - This/Last Week` | Same pattern | Same `MAX(Fiscal Date)` and `MAX - 7` logic | Same risks |
| `Net Forecast - This/Last Week` | Same pattern | Same | Same |
| `DF Goal` | `Demand Fulfillment` calc column | SWITCH on `Collective Class + Imp/Dom Code` concatenation → per-category target values (all 0.95 for listed categories, then fallback) | ⚠️ **Medium** — targets hardcoded; if a new Collective Class is added, it silently gets the fallback value. See §9 |
| `Collective Class + Imp/Dom Code` | `Demand Fulfillment` calc column | `RELATED(TblForecastCommonContainer_Logility[Collective Class]) & Import/Domestic Code` | Medium — depends on bridge table join; if item not in `TblForecastCommonContainer_Logility`, returns blank concatenation |
| `SI Neg $` | `Top Negatives` calc column | `SI Negative × VALUE(Current Unit Price)` | ⚠️ `VALUE()` text-to-number cast on `Current Unit Price` column — if column contains non-numeric text, returns error silently masked by measure IFERROR |
| `Current Week` labels | `z_FiscalCal` calc columns | `IF(FiscalWeekInd=0,"This Week", IF=-1,"Last Week", =-2,"2 Weeks Ago", =-3,"3 Weeks Ago", BLANK())` | Low — purpose-built for this report's WoW slicer |

---

## 7. Duplication / Consolidation Signals

1. **Four versions of the core Demand Fulfillment rate measure — all nearly identical:**

   | Measure | Formula | Key difference |
   |---|---|---|
   | `Total % Cust Orders Covered` | `(FD + NF + SI_neg) / (FD + NF)`, clamp [0,1] | **Primary** — SI_neg is negative value, so adding it reduces the rate |
   | `Total % Cust Orders Covered v2` | `SI_neg / (FD + NF)`, clamp [0,1] | Drops FD+NF from numerator — fundamentally different denominator |
   | `Total % Cust Orders Covered v2.1` | `ABS(SI_neg) / (FD + NF)`, clamp [0,1] | Adds ABS — produces positive rate even when SI_neg is positive (no shortage) |
   | `Total % Cust Orders Covered v3` | Same as primary — exact copy | **True duplicate**, no difference in code |

   The v2 and v2.1 formulas are **not equivalent** to the primary — they calculate different things. `v3` is a dead copy. None are labeled with a deprecation note or "use this one" flag.

2. **`% Cust Order Covered - This_Week` and `% Cust Order Covered - Last_Week`** — yet two more DF rate variants, recomputed from the This Week / Last Week source columns rather than using the main measure with a date filter.

3. **`Demand Fulfillment Goal = 0.90` (constant measure) vs. `DF Goal` (per-category calculated column)** — two different goal concepts:
   - `Demand Fulfillment Goal`: single literal constant `0.90` — applies to everything
   - `DF Goal`: per item per category (mostly `0.95`, lower for some categories)
   Both exist simultaneously; unclear which drives report visuals.

4. **`Concatenate` key column duplicated in both `Demand Fulfillment` and `TblForecastCommonContainer_Logility`** — both build `Item & "-" & Warehouse` as their join key. This is a synthetic bridge key pattern; neither table has a natural shared key. If warehouse codes differ between sources, joins silently fail.

5. **`Total Firm Dmnd` in `Top Negatives` vs. `Total Firm Demand` in `Demand Fulfillment`** — same concept, different measure names and different source tables. Cross-page comparisons require knowing which measure is used where.

6. **`Top Negatives` entity is a separate dataflow table** with its own set of columns (`DRP Planner`, `AFI Finance Division`, `AFI Sales Division`, `Current Unit Price`, `Import Domestic Code`) that overlap with — but are not the same as — columns in `Demand Fulfillment`. These appear to be pre-aggregated or filtered views of similar data, not the same grain.

---

## 8. Open Questions

1. **Which DF rate measure is shown in the WBR?** Four versions exist (primary, v2, v2.1, v3). v3 is identical to primary so presumably one of the others is being used somewhere. If different report pages use different versions, the rate shown to leadership may differ from the one planners track.

2. **`Top Negatives` entity — what is its grain and time horizon?** The dataflow entity name is "Top Negatives" — it has a `Fiscal Date` column (linked to z_FiscalCal), suggesting weekly data, but it also has a `DRP Planner` column not in `Demand Fulfillment`. Is it a filtered subset of `Demand Fulfillment` (e.g., items with SI Negative below a threshold) or a separately computed worklist?

3. **`DF Goal` column defaults to what value for unrecognized Collective Classes?** The SWITCH expression covers ~20 specific class-import/domestic combinations at 0.95. The fallback (no match) is not visible in the truncated output — what is it? 0.90? 0, which would break comparisons?

4. **`MAX(Fiscal Date) - 7` for Last Week** — what happens if the dataflow skips a refresh for one week? The prior week's data would be at `-14` days, not `-7`, and `Firm Demand - Last Week` would return blank (= 0) for all items. Has this ever occurred?

5. **`Demand Fulfillment` vs. `SupplyPlanDetail[Demand Fulfillment]` in Product Review (NEW)** — both are sourced from the same dataflow entity (`Demand Fulfillment` / `ccbb84a2`) but the Product Review (NEW) model loads it as `DemandFulfillment` and re-implements the DF rate in DAX. Do they produce identical numbers?

6. **`TblForecastCommonContainer_Logility` bridge — is the `Concatenate` key reliable?** If an item exists in `Demand Fulfillment` but not in `TblForecastCommonContainer_Logility` (e.g., new item not yet in Logility), the RELATED lookups return blank, and `DF Goal` is blank or wrong. How often does this happen for new products?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`0.90`** in `Demand Fulfillment Goal` | DAX measure | Global DF target — 90% demand coverage | **No** — literal scalar; not linked to any category or time-based target-setting process |
| **`0.95`** in `DF Goal` column | DAX calc column | Per-category DF target for ~20 Import and Domestic product categories | **No** — hardcoded; all listed categories = 0.95; rationale for 95% not documented |
| **`-7`** in `Firm Demand - Last Week` | DAX calc column | "Last week" = exactly 7 calendar days before latest date | **No** — silently wrong if data has gaps; no tolerance for missing weeks |
| **`182`** in `Total % Cust Orders Covered 6MMA` | DAX measure | `DATESINPERIOD(..., -182, DAY)` ≈ 6 months = 182 days | **No** — 182 days = 26 weeks = 6×4+2; approximates 6 months but not exactly aligned to fiscal months |
| `IFERROR(..., 0)` in `Total % Cust Orders Covered` | DAX measure | Returns 0 (not BLANK) on divide-by-zero | **No** — items with zero demand AND zero forecast show 0% DF rate, which visually looks like a 0% coverage item even though they are genuinely zero-demand |
| `VALUE(Current Unit Price)` | `Top Negatives[SI Neg $]` calc column | Text-to-number cast; implies `Current Unit Price` column is stored as text in the dataflow entity | ⚠️ — if any value is non-numeric (e.g., blank or formatted text), VALUE() returns error; downstream `Total SI Neg $` would be wrong for those items |
| `LEFT(..., 4) & "%"` in `Total % Out of Stock` | `Top Negatives` measure | Truncates the percentage to 4 characters before appending "%" | **No** — `LEFT("100.5%", 4)` = "100." → displays as "100.%" for items at exactly 100%; `LEFT("9.87%", 4)` = "9.87" → correct. Edge case at 100% is cosmetic but misleading |
| Bridge key `Item & "-" & Warehouse` | `Demand Fulfillment[Concatenate]` and `TblForecastCommonContainer_Logility[Concatenate]` | Synthetic join key built by concatenation | **No** — fragile if either side has trailing spaces or different warehouse code formats; no deduplication check on the Demand Fulfillment side |
| `Demand Fulfillment Goal = .90` | DAX measure literal | Scalar constant without leading zero | Cosmetic — `.90` vs `0.90` is functionally equivalent but inconsistent with standard DAX formatting |

---

## 10. Comparability / Consistency

1. **Four DF rate formulas are not interchangeable.** v2 drops `(FD + NF)` from the numerator entirely; v2.1 adds ABS to SI_negative; primary and v3 are identical. These four measures will produce different numbers for every item. If a report page shows `v2.1` (which returns the absolute ratio regardless of sign), it appears as a "coverage %" when SI_negative is actually positive (fully covered) — giving a misleading metric.

2. **`Demand Fulfillment Goal` (0.90) vs. `DF Goal` (0.95 by category)** — if a visual uses `Demand Fulfillment Goal` as the reference line and another uses `DF Goal`, they show different targets for the same item. A 92% DF rate looks "above target" against the 0.90 global goal but "below target" against the 0.95 category goal.

3. **`This Week` / `Last Week` columns use `MAX(Fiscal Date)` evaluated across the ENTIRE table.** If a user applies a date filter to limit the view to a specific historical week (e.g., "show me Week 10"), the `MAX(Fiscal Date)` in a calculated column is computed at model refresh time, not at query time — it always refers to the actual latest week in the data, not the filtered week. A historical drilldown will still show the same "this week" and "last week" values as today's view.

4. **`Total % Cust Orders Covered 6MMA` uses `-182` calendar days**, not 26 fiscal weeks. A fiscal month has 4 or 5 weeks, making 6 fiscal months range from 24 to 26 weeks (168–182 days). At 182 days, the 6MMA always includes 26 calendar weeks but may include 25 or 27 fiscal weeks depending on the fiscal calendar structure. The 6MMA is not strictly comparable across different starting points in the fiscal year.

5. **`z_FiscalCal` in this model has 45 columns vs. 38–43 in other models** — adds 4 custom "current week" categorical columns (`This Week`, `Last Week`, `2 Weeks Ago`, `3 Weeks Ago`, `Current Week Sort`, `Current Week`) specific to this report's WoW display logic. These are model-local derived columns not in the conformed dataflow. If the underlying `z_FiscalCal` dataflow is replaced, these calculated columns survive; but if another model team adds similar columns with different names, cross-model fiscal week semantics diverge.

---

## Closing — Interview Seeds

1. **"There are four versions of the Demand Fulfillment % measure in this model — one is an exact duplicate, and two use different formulas. Which one is on the WBR slide that leadership sees every week? Do you know if it's the same one planners use on their daily pages?"**
   *(Targets: which measure version drives decisions; whether the four-version proliferation has caused inconsistency in reporting to leadership.)*

2. **"The 90% demand fulfillment goal is a fixed constant in the model. But there's also a per-category goal table that says Import items should hit 95%. Is the 90% or the 95% the number your team is held accountable to — and who set those thresholds?"**
   *(Targets: which goal constant is operationally active; whether the dual-goal system creates confusion; governance of targets.)*

3. **"The 'Last Week' numbers in this report assume data is refreshed every single week. If the dataflow skipped a week — say, a holiday or a system outage — the 'Last Week' column would show zero for everything. Has that ever happened, and how would you know if it did?"**
   *(Targets: refresh reliability awareness; whether the MAX-7 pattern failure mode is known; operational resilience.)*

4. **"The Top Negatives list is ranked by dollar shortfall. When an item appears at the top of that list, what is the exact next step — do you open Logility, send an email, create a ticket? And is there a threshold SI Negative amount below which you don't act at all?"**
   *(Targets: operational workflow after seeing the shortfall; whether dollar ranking drives the right prioritization; minimum-action threshold.)*

---

*Analysis based on BIM definition extracted 2026-07-08. BIM saved to [bim/Demand_Fulfillment.bim](bim/Demand_Fulfillment.bim).  
Note: BIM contains case-variant duplicate translation keys — use Node.js or Python to parse; PowerShell ConvertFrom-Json will error.  
No bundle indexes were modified.*
