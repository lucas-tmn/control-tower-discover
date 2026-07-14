# Consumption Report — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `935e1a2f-e655-466d-ac4f-95617dcb5bb7`  
**Report ID:** `b256080a-aa6c-497c-a758-0e7e6ba4fbb0`  
**Analysis Date:** 2026-07-08  
**Model Size:** 24 tables (4 fact + 1 dim product + 1 dim warehouse + 1 dim calendar + local date tables); **7 DAX measures** (all in `Target_Consumption` table + 1 in `CurFcst`); Compatibility Level 1600  
**BIM File:** [bim/Consumption_Report.bim](bim/Consumption_Report.bim)

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> Based on **how orders typically accumulate through the month** (historical consumption pattern), are we on track to hit the forecast this month — and what is the projected gap?

This is a **mid-month forecast attainment / order pacing** report. It answers a very specific intra-month question: given that today is Day N of the fiscal month, historically X% of the month's orders arrive by Day N — so if current orders are at Y% of forecast, are we pacing ahead, on target, or behind?

The SQL is explicitly documented as:
> *"Estimates expected orders for the current month by comparing current orders against historical consumption patterns"*

**Primary chain links served:**

| Link | How served |
|---|---|
| **Demand** | `Orders` — current month actual orders (Current Request date, `FiscalMonthInd=0` only) |
| **Forecast** | `CurFcst` — current month's forecast snapshot (day 1 of fiscal month); `Target_Consumption[Forecast]` — same source embedded in the target calc |
| **Forecast attainment** | `Target_Consumption` — pre-calculated target consumption rate (historical %) applied to current forecast; gap vs. current orders |

**Secondary:** `Logility_FUto` — latest Logility forecast (all months, latest snapshot). Present in model but **not connected to Target_Consumption via DAX measures**. Appears to be a reference/context table for additional slicing.

**Not served:** Supply, inventory, on-time, receipts, forecast accuracy, safety stock.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Are we pacing ahead/behind forecast this month?** — check `indicator_consumption` flag (Behind / On Target / Ahead) by Collective Class and Customer Group | Planning Manager / WBR Leadership | **Daily or Weekly** (intra-month) | **Performance/Governance** — monitor plan health in-flight |
| **Quantify the gap in units** (`gap_consumption`) — how many orders are we behind or ahead of historical pace? | Demand Planner / Category Analyst | Weekly | **Performance/Governance** — calibrate forecast for the month |
| **Identify which Collective Class / Customer Group is driving the gap** — drill to product-category level | Demand Planner | Weekly | **Performance/Governance** — root cause, coaching |
| **Trigger proactive sales or demand management action** — if behind target, signal sales team to investigate; if ahead, consider pulling forward supply | Planning Manager / Sales Management | Weekly | **Operational** — handle demand signal |

> No Financial-Justification decisions — no dollar impact calculation.

---

## 3. Key Metrics / Measures

All 6 business measures live in `Target_Consumption` table; 1 utility measure in `CurFcst`.

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `target_consumption` | Historical % of month's orders expected to have been received by today's day-of-month | CustGrp × CollectiveClass × WH | `SUM(target_order_qty) × SUM(CurFcst[TotalForecast]) / SUM(Forecast) / SUM(CurFcst[TotalForecast])` | ⚠️ formula simplifies to `SUM(target_order_qty)/SUM(Forecast)` — see §9 |
| `current_consumption` | Actual order qty this month as % of current forecast | CustGrp × Item × WH × Month | `SUM(Orders[Order Quantity]) / SUM(CurFcst[TotalForecast])` | ⚠️ grain mismatch between Orders (item-level) and CurFcst (item-level, day-1 snapshot) — see §10 |
| `gap_consumption_rate` | Pacing gap rate: target % − actual % | — | `[target_consumption] − [current_consumption]` | |
| `gap_consumption` | Pacing gap in units: rate × forecast | — | `[gap_consumption_rate] × SUM(CurFcst[TotalForecast])` | |
| `indicator_consumption` | Traffic-light status: Behind / On Target / Ahead | — | `SWITCH(TRUE(), gap_rate > 0.05 → "Behind", < −0.05 → "Ahead", "On Target")` | ⚠️ hardcoded ±5% band — see §9 |
| `consumption_title_cur` | Dynamic report title showing current month, week, and day position | — | Complex DAX string: fiscal month desc + week position + day-of-month position | ⚠️ uses `Fiscal Day Indicator = 0` filter to find today; breaks if today is not in z_FiscalCal |
| `Snapshot` (in CurFcst) | Max snapshot date in Target_Consumption | — | `MAX(Target_Consumption[snapshot_date])` — data freshness indicator | |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`Target_Consumption`** | `ashley-edw.database.windows.net / ashley_Edw` (note mixed case) — massive nested SQL: `DemandForecastSnapshot` × `DimDate` × `DimCurrentProductDetails` × historical consumption pattern subquery using `Wholesale_SalesHistory_AFI.OrderHistory`, 36-month window | Direct Azure SQL EDW | ⚠️ **High** — most complex single query in any model reviewed; 36-month historical cross-join with complete day-spine gap-filling; runs at latest FC snapshot only |
| **`Orders`** | Same EDW — `SupplyChain_Enh.ActualsCustItemWH_AFI`, **current month only** (`FiscalYearInd=0, FiscalMonthInd=0`), Current Request date, seasonality-adjusted via `Wholesale_DemandPlanning_AFI.SeasonalitySnapshot` | Direct Azure SQL EDW | Medium — `SEAS_FCTR` join; hardcoded fallback |
| **`CurFcst`** | Same EDW — `SupplyChain_Enh.CurFcstSnapshotDaily` filtered to **day 1 of current fiscal month** (`dateadd(day,1,FiscalMonthFirstDate) where FiscalMonthIndicator=0`) | Direct Azure SQL EDW | ⚠️ Medium — uses day-1 snapshot specifically; see §9 |
| **`Logility_FUto`** | Same EDW — same `CurFcstSnapshotDaily` table, **latest snapshot** (`MAX(SnapshotDate)`) — not day-1 restricted | Direct Azure SQL EDW | Medium — different snapshot logic from `CurFcst` |
| `CurrentProductDetails` | PowerPlatform Dataflows (note: `PowerPlatform.Dataflows` connector, not `PowerBI.Dataflows`) → workspace `a47e4573...`, dataflow `346f2aa1...` → entity `CurrentProductDetails` | Governed Dataflow | Low — different connector API but same dataflow |
| `WarehouseMaster` | Same PowerPlatform Dataflow → `WarehouseMaster` | Governed Dataflow | Low |
| `z_FiscalCal` | Same PowerPlatform Dataflow → `AshleyFiscalCalendarV2` | Governed Dataflow | Low |

> **Note on connector:** This model uses `PowerPlatform.Dataflows(null)` with `Workspaces` navigation, whereas other models in the workspace use `PowerBI.Dataflows(null)` directly. This is a newer connector API version — functionally equivalent but signals this model was built/updated more recently.

> **No Fabric sources.** All SQL hits `ashley-edw.database.windows.net`.

> **`Target_Consumption` SQL runs at query time** against a live EDW — includes a 36-month window historical aggregation. This is an extremely heavy query; refresh time is likely significant.

---

## 5. Grain & Snapshot Strategy

**Primary grain:**

| Table | Grain |
|---|---|
| `Target_Consumption` | Customer Group × Collective Class × Item SKU × Warehouse × **current fiscal month** (one row per combination, latest FC snapshot) |
| `Orders` | Customer Account × Item SKU × Warehouse × **current fiscal month** (FiscalMonthInd=0 only) |
| `CurFcst` | Item SKU × Warehouse × **current fiscal month** (day-1 snapshot, FiscalMonthInd=0) |
| `Logility_FUto` | Item SKU × Warehouse × **all future months** (latest snapshot) |

**Snapshot strategy: Point-in-time current month only.**

- `Target_Consumption` — uses latest FC snapshot for current month demand/forecast; `target_consumption` rate is based on **36-month historical average** (pre-aggregated in SQL, not a live trend).
- `CurFcst` — deliberately anchored to **day 1 of the current fiscal month** (`dateadd(day,1,FiscalMonthFirstDate)`). This means the forecast baseline is locked to the opening forecast, not today's forecast — intentional design to measure attainment against a fixed target.
- `Orders` — current month to-date, live.
- `Logility_FUto` — latest snapshot for all months; purpose unclear from model alone.

**No historical tracking** — this model cannot show last month's consumption pacing. It is a **single-month intra-month view only**.

---

## 6. Dimensions Used

| Dimension | Table | Connected? | Notes |
|---|---|---|---|
| **Product** | `CurrentProductDetails` (93 cols + 2 calc cols) | ✅ — to `Target_Consumption[item_sku]`, `Orders[Item SKU]`, `CurFcst[ItemSku]`, `Logility_FUto[ItemSku]` | Same conformed source; adds `Collective Class (groups)` and double-nested `Collective Class (groups) (groups)` — see §7 |
| **Warehouse** | `WarehouseMaster` (11 cols) | ✅ — to all four fact tables | Conformed |
| **Date / Fiscal Calendar** | `z_FiscalCal` (38 cols) | ✅ — to `Orders[FiscalMonthLastDate]` and `CurFcst[FiscalMonthLastDate]` | Note: `Target_Consumption[fiscal_month_last_date]` and `[snapshot_date]` connect to **local date tables** only, not to `z_FiscalCal` — so z_FiscalCal cannot filter `Target_Consumption` |

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `Collective Class (groups)` | `CurrentProductDetails` calc column | SWITCH grouping — different mapping than Product Review (NEW): includes "BEDROOM" and "RTA & ASHTON YORK" groups not present in other models | ⚠️ **Medium-High** — different grouping logic than same-named column in Product Review (NEW) and GF Act+Fcst; three models, three mappings |
| `Collective Class (groups) (groups)` | `CurrentProductDetails` calc column | Second-level rollup of `Collective Class (groups)` — "OTHER" bucket for less-common classes | Medium — double-nested grouping; unusual pattern |
| `target_consumption` rate | Pre-calculated in `Target_Consumption` SQL | 36-month historical average of `MTD FUTO / Total Month` by CustGrp × CC × WH × FiscalDayOfMonth; gap-filled with 0 for days with no orders | ⚠️ High — business-critical number; entirely in EDW SQL |

---

## 7. Duplication / Consolidation Signals

1. **`Collective Class (groups)` has different mappings across models.** In this model: BEDROOM and "RTA & ASHTON YORK" are separate groups. In Product Review (NEW): "RTA & METAL BEDS" is the group, BEDROOM not mentioned. In GF Act+Fcst: the column doesn't exist. Same column name, different buckets — cross-report comparison of "Collective Class group" breaks.

2. **`Collective Class (groups) (groups)` — double-nested grouping** with an empty name. This column applies SWITCH on the already-grouped column to create a second-level "OTHER" bucket. This pattern is unusual and suggests the first grouping was insufficient but wasn't refactored.

3. **`CurFcst` and `Logility_FUto` both source from `SupplyChain_Enh.CurFcstSnapshotDaily`** with different snapshot filters:
   - `CurFcst`: day-1 of current fiscal month snapshot only
   - `Logility_FUto`: latest snapshot across all months
   Same table, two semantic purposes, no documentation in model. Both are in the model but `Logility_FUto` has no DAX measures and is connected only to dimensions — its role is unclear.

4. **`Target_Consumption[Forecast]` (SQL column) vs. `CurFcst[TotalForecast]` (separate table)** — both represent total forecast for the current month. `target_consumption` measure cross-divides them: `SUM(target_order_qty) × SUM(CurFcst[TotalForecast]) / SUM(Forecast) / SUM(CurFcst[TotalForecast])`. The TotalForecast terms cancel, leaving `SUM(target_order_qty)/SUM(Forecast)`. The presence of `CurFcst[TotalForecast]` in the formula is algebraically redundant — see §9.

5. **`Orders` table connects to `z_FiscalCal` but `Target_Consumption` does not.** User applying a fiscal month filter via z_FiscalCal will filter Orders but not Target_Consumption — the two measures behave differently under the same slicer.

---

## 8. Open Questions

1. **Who uses this report and at what cadence?** The consumption rate is meaningful only mid-month. Is this checked daily, weekly, or only at the WBR? Does anyone act on the "Behind Target" flag intra-week, or is it a month-end retrospective?

2. **`CurFcst` is anchored to day 1 of the fiscal month.** If the forecast changes significantly mid-month (e.g., a large order is added or dropped), the denominator stays fixed at the opening forecast. Is this intentional — measuring attainment against a frozen target — or should it track the latest forecast?

3. **`Logility_FUto` role.** This table (latest forecast snapshot, all months) has no DAX measures and no relationship to `Target_Consumption`. Is it used in report visuals as a slicer context or reference? Or is it a leftover from development?

4. **`Target_Consumption` SQL runs a full 36-month historical aggregation every refresh.** This is a very heavy query with cross-joins and window functions. What is the current refresh schedule, and has performance been a concern? Would moving the historical consumption rate to a pre-built EDW view or Fabric table help?

5. **`Logility_FUto[FiscalMonthLastDate]` connects to a local date table, not `z_FiscalCal`** — same issue as `Target_Consumption`. If a user applies a fiscal calendar slicer, `Logility_FUto` is unfiltered. Is this intentional?

6. **`SEAS_FCTR` fallback in `Orders` SQL is `0.0833` (1/12).** This is used when no seasonality factor is found for an item. `1/12 ≈ 8.33%` implies equal monthly seasonality. Is this an appropriate fallback, or should items with missing seasonality factors be flagged rather than silently adjusted?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **±5% band** in `indicator_consumption` | DAX measure | `gap_rate > 0.05` → "Behind Target"; `< -0.05` → "Ahead of Target"; else "On Target" | **No** — ±5% tolerance band is undocumented; whether this is a business-agreed threshold or a developer choice is unknown |
| **36 months** in `Target_Consumption` SQL | SQL | Historical window for consumption pattern: `FiscalMonthIndicator BETWEEN -36 AND -1` | **Partially** — SQL comment says "36 months of history"; rationale (enough seasonality cycles = 3 years) not explained |
| **Day 1 of fiscal month** in `CurFcst` SQL | SQL | `WHERE SnapshotDate = dateadd(day,1,FiscalMonthFirstDate)` — locks forecast to opening of month | **No** — critical design choice (frozen vs. rolling baseline) not documented in model |
| **`SEAS_FCTR` fallback = `0.0833`** | `Orders` SQL (`isnull(sf.SEAS_FCTR, 0.0833)`) | Default seasonality factor = 1/12 when no factor found | **No** — implies equal distribution across 12 months; wrong for items with true seasonality and no Logility factor |
| **`CASE WHEN target_consumption = 0 THEN 1`** | `Target_Consumption` SQL | Prevents division by zero; if historical consumption = 0 for this day, use 100% as target | **Partially** — SQL comment explains zero-avoidance; but returning `1` (100%) means an item with no historical orders will show 0% current consumption against 100% target, always "Behind Target" |
| Algebraically redundant `CurFcst[TotalForecast]` in `target_consumption` | DAX measure | `SUM(target_order_qty) × SUM(TotalForecast) / SUM(Forecast) / SUM(TotalForecast)` — TotalForecast cancels | **No** — formula simplifies to `SUM(target_order_qty)/SUM(Forecast)`; the extra division/multiplication adds confusion and may introduce floating-point noise |
| **Pre-month orders assigned to Day 1** | `Target_Consumption` SQL (Order History UNION) | Orders placed before the fiscal month start but requesting delivery in that month are bucketed to `FiscalDayOfMonth = 1` | **Partially** — SQL comment explains this is the "Day 1 baseline"; does the business agree pre-month orders should all land on day 1? |
| Warehouse exclusions `NOT IN ('C','CNW','55','IOR','AF')` | `Target_Consumption` SQL + `Orders` SQL | Wholesale, return, and internal warehouses excluded from both historical and current consumption | **No** — consistent across both queries (good); but IOR and AF exclusion rationale undocumented |
| Account exclusion `<> '3824800'` | `Orders` SQL | Same internal AFI account excluded as in other models | **No** |
| `FiscalDateIndicator = 0` in `consumption_title_cur` | DAX measure | Identifies "today" in the fiscal calendar | **No** — if model is refreshed but z_FiscalCal has no row with `FiscalDateIndicator=0` (e.g., today is a holiday or outside calendar range), title returns error/blank |

---

## 10. Comparability / Consistency

1. **`target_consumption` and `current_consumption` use different denominators at different grains.** `target_consumption` pre-aggregates at CustGrp × CC × WH in SQL, then the DAX measure sums across that. `current_consumption` = `Orders / CurFcst`, where Orders is at item-account-WH grain and CurFcst is at item-WH grain (no customer split). When filtered by Customer Group, `CurFcst[TotalForecast]` does not filter by customer (no customer relationship to CurFcst) — the denominator stays total, making `current_consumption` by customer not comparable to `target_consumption` by customer.

2. **`CurFcst` (day-1 snapshot) vs. `Logility_FUto` (latest snapshot) — two forecast tables for the same month.** If the forecast has changed materially since day 1, the pacing indicator may compare orders against an outdated forecast baseline, making "Behind Target" appear when the forecast itself was revised down.

3. **`z_FiscalCal` filters `Orders` and `CurFcst` but NOT `Target_Consumption`.** If a fiscal calendar slicer is used in a report visual, it will filter the numerator of `current_consumption` but the `target_consumption` denominator (`Target_Consumption[Forecast]`) is unfiltered by calendar. This makes the pacing % incorrect under any fiscal date slicer applied to z_FiscalCal.

4. **`Collective Class (groups)` has different bucket definitions across this model vs. Product Review (NEW) vs. GF Act+Fcst.** A cross-report comparison of "which collective class group is behind target" will silently compare different product rollups. For example, BEDROOM items appear in "BEDROOM" group here but fall under the main Collective Class passthrough in Product Review (NEW), and "OTHER / DISCO" in GF Act+Fcst.

5. **`Orders` uses `CurReqWkEnding` (Current Request date)** for the current month filter — consistent with standard actuals queries. But `Target_Consumption` SQL uses `RequestDate_Date` (original request date) for historical consumption calculation. Different date bases for current vs. historical: today's orders are dated by when customers last moved them; historical patterns are by when customers originally requested. This means the consumption rate and the actuals being measured against it use different demand timing definitions.

---

## Closing — Interview Seeds

1. **"When the indicator shows 'Behind Target' mid-month, what's the first thing you do — and do you ever manually override or ignore it? Are there months where you know the pacing metric is misleading (e.g., big pre-market orders that haven't hit yet)?"**
   *(Targets: whether the ±5% band is the right threshold; known failure modes; whether the report actually drives action or is watched passively.)*

2. **"The consumption rate is based on 36 months of history. If a customer group launched a new ordering behavior in the last 6 months (e.g., moved to EDI or changed ordering cadence), does the historical baseline still make sense — and has that ever caused a false 'Behind Target' alarm?"**
   *(Targets: staleness of the 36-month average; whether structural demand shifts invalidate the historical benchmark.)*

3. **"The forecast used to measure pacing is locked to the forecast from the first day of the month. If the forecast team revised it down on Day 10, this report still measures against the Day-1 target. Is that intentional — are you trying to hold people to the opening plan — or should it track the latest forecast?"**
   *(Targets: confirms whether frozen-baseline is a business design choice or an oversight; drives conversation about accountability vs. accuracy.)*

4. **"The `Logility_FUto` table is in the model but none of the pacing measures use it. Do you know what it's for? Do any of the report pages reference it, or was it added at some point and never removed?"**
   *(Targets: whether the mystery table is actively used in visuals; cleanup opportunity; user awareness of the model's structure.)*

---

*Analysis based on BIM definition extracted 2026-07-08. BIM saved to [bim/Consumption_Report.bim](bim/Consumption_Report.bim). No bundle indexes were modified.*
