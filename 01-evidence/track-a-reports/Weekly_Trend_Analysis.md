# Weekly Trend Analysis — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `c42edbed-ca3d-4517-be0b-ac1f3129a2cd`  
**Report ID:** `42037442-2ccd-4a97-b2c2-2ea51736c1bc`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~1.46 MB (BIM); 17 tables, 15 DAX measures in `_Measures`

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "On a week-by-week basis, how is actual demand (invoiced, written, requested) trending vs. forecast — and are open orders tracking to consume this month's plan?"

**Primary chain links served:** **Demand** + **Forecast**  
The report stitches together four data streams onto a single weekly time axis:
- **Actuals** — past invoiced shipments, written orders, and current-request dates (last 26 weeks, some extending 13 weeks forward for request dates)
- **Forecast** — working weekly forecast (forward 6 months from latest Logility snapshot)
- **FcstAccuracy** — lagged forecast vs. actual comparison (past 26 weeks, at varying lag horizons)
- **FutOrd** — current-month order consumption vs. total forecast (2-month window)

This is a WBR (Weekly Business Review) demand trend monitor — its purpose is to show whether actual demand is running ahead of, behind, or on-plan with the current working forecast.

Secondary links: no inventory, supply, or production signals present.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Adjust working forecast up/down based on demand trend** — compare `Inv Qty` / `Writ Qty` trend line vs `Working Fcst` to decide if the current month's plan is too high or low | Demand Planner / WBR Lead | Weekly | Operational |
| **Monitor current-month consumption rate** — `dfoConsumption = dfoFUTO / dfoFcst` shows % of this month's forecast already ordered; acts as early warning if consumption is tracking below plan | Demand Planner / Sales | Daily / weekly | Operational |
| **Evaluate 12-week (or transitional lag) forecast accuracy** — `90Day Error %` = lag forecast vs actual; used to assess Logility model performance over rolling 26 weeks | Supply Chain Manager / Analyst | Weekly | Performance/Governance |
| **Compare Written vs Invoiced vs Current Request** — understanding which date type is driving trend; a spike in Written may precede Invoiced by weeks | WBR-Leadership / Demand Planner | Weekly | Operational |
| **Identify items / categories with demand diverging from forecast** — slice by Collective Class, Series, Warehouse, Customer Group | Planner / Category Analyst | Weekly | Operational |

---

## 3. Key Metrics / Measures

### Actuals Measures

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Inv Qty` | Units shipped (invoiced), past weeks only | Item × WH × CustGroup × fiscal week | `SUM(Actuals[Qty]) where Sales Type="Invoiced" AND FiscalWeekIndicator < 1` — includes current week (<=0 means week 0 included) |
| `Inv Qty (CS)` | Units shipped, **strictly past** weeks | Item × WH × fiscal week | Same but `FiscalWeekIndicator < 0` — excludes current week. **⚠️ Near-duplicate of `Inv Qty`; differs by one week boundary (see §7)** |
| `Writ Qty` | Units written (order entry date), past weeks | Item × WH × fiscal week | `SUM(Actuals[Qty]) where Sales Type="Written" AND FiscalWeekIndicator < 1` |
| `Curr Qty` | Units by current request date (past + future) | Item × WH × fiscal week | `SUM(Actuals[Qty]) where Sales Type="Current Request"` — no week filter; includes future open orders |
| `Curr Req Qty` | **Identical to `Curr Qty`** | Same | Same expression — exact duplicate (see §7) |
| `FUTO` | Future open orders by request date (forward-looking) | Item × WH × fiscal week | `SUM(Actuals[Qty]) where Sales Type="Current Request" AND FiscalWeekIndicator >= 0` |

### Forecast Measures

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Working Fcst` | Weekly working forecast qty | Item × WH × CustGroup × fiscal week | `SUM(Forecast[Qty])` — from `Wholesale_DemandPlanning_AFI.DemandForecast` (latest snapshot), distributed evenly across weeks within month: `(ResultantFcst + PromoLift) / NumWeeks` where NumWeeks = 4 or 5 |
| `dfoFUTO` | Actual orders so far this month | Item × WH × CustGroup | `SUM(FutOrd[dfcOrderFutureQty]) where FiscalMonthIndicator=0` |
| `dfoFcst` | Total monthly forecast for current month | Item × WH × CustGroup | `SUM(FutOrd[Total Forecast]) where FiscalMonthIndicator=0` |
| `dfoConsumption` | Orders received as % of total monthly forecast | Item × WH × CustGroup | `DIVIDE([dfoFUTO], [dfoFcst])` — in-month consumption rate |
| `dfoGap` | Orders received minus total monthly forecast | Item × WH × CustGroup | `[dfoFUTO] - [dfoFcst]` — raw gap (negative = behind plan) |

### Forecast Accuracy Measures — ⚠️ PARTIALLY BROKEN

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Lag Fcst` | Lagged forecast qty (at snapshot date) | Item × WH × CustGroup × week | `SUM(FcstAccuracy[Fcst Qty])` — weekly qty = monthly forecast ÷ weeks in month (4 or 5) |
| `ACTD (accy)` | Actual demand for accuracy comparison | Same | `SUM(FcstAccuracy[Actual Qty])` — **⚠️ BROKEN: column `Actual Qty` does not exist in `FcstAccuracy` table or its SQL; always returns BLANK** |
| `90Day Error` | Raw forecast error for accuracy | Same | `[Lag Fcst] - [ACTD (accy)]` — **⚠️ BROKEN: `ACTD (accy)` is always BLANK, so this equals `[Lag Fcst]`** |
| `90Day Error %` | Bias % for accuracy | Same | `DIVIDE(SUM(FcstAccuracy[Fcst Qty]), SUM(FcstAccuracy[Actual Qty])) - 1` — **⚠️ BROKEN: denominator is always 0/BLANK, always returns -1 or BLANK** |

**All four accuracy measures are unusable in their current state.** The `FcstAccuracy` table has no `Actual Qty` column — it was never included in the SQL SELECT list.

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `Actuals` | 5-branch UNION from `Wholesale_SalesHistory_AFI.InvoiceDetail` (Invoiced/Written/CurrReq - historical) + `AFISales_DW.FactOpenOrders` (Written/CurrReq - open) | Complex 5-way UNION; marketable component adjustment via GDESCD=700 join; 1-hour timeout; **26 weeks past, 13 weeks forward** |
| Same EDW | `Forecast` | `Wholesale_DemandPlanning_AFI.DemandForecast` | **⚠️ Different source than all other SC models** — uses `DemandForecast` table (older/different schema) not `DemandForecastSnapshot`; latest snapshot only; forward 6 months |
| Same EDW | `FcstAccuracy` | `SupplyChain_Enh.DemandForecastSnapshot` | Lagged forecast at weekly grain; **⚠️ missing Actual Qty column** — SQL query only selects forecast columns, no actuals join |
| Same EDW | `FutOrd` | `SupplyChain_Enh.DemandForecastSnapshot` | Current month consumption tracking; latest snapshot only; current + next month |

### Power BI Dataflows (semi-governed)

| Dataflow | Tables | Notes |
|---|---|---|
| `a47e4573` workspace / `346f2aa1` dataflow | `z_ProductDetails`, `z_FiscalCal`, `z_WarehouseMaster`, `z_VendorMaster`, `z_CustomerMaster_AFI` | Same shared conformed layer. **`z_CustomerMaster_AFI` is locally augmented** with 8 hardcoded rows (see §9). |

**No SharePoint / Excel sources.** Fully EDW + dataflow.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Item SKU × Warehouse × Customer Group × Fiscal Week

All four tables share this grain, but with different time horizons:
- `Actuals`: –26 to +13 fiscal weeks (depending on Sales Type)
- `Forecast`: current fiscal week to +26 (6 months forward, weekly distributed)
- `FcstAccuracy`: –26 weeks of demanded periods
- `FutOrd`: current + next month only

**Snapshot strategy:**
- `Actuals` — **latest only** for open orders; historical for invoiced/written
- `Forecast` — **latest snapshot** (`MAX(dtea)` from `DemandForecast`)
- `FcstAccuracy` — **historical snapshots** retained (each row carries the snapshot date that was used to pull the lagged forecast); enables looking back at what was forecasted N weeks ago for a given demand week
- `FutOrd` — **latest snapshot only**

The model is designed for **current-period operational monitoring**, not long-term trend accumulation — 26-week lookback is consistent across tables, appropriate for a WBR.

---

## 6. Dimensions Used

| Dimension | Source | Notes |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow) | Two local calc columns unique to this model: `z_MarketableConversion` and `z_ItemFilter`. No lifecycle, storage type, or kit classification columns — much lighter than Safety Stock or Inventory Transactions models. |
| **Date / Fiscal Calendar** | `z_FiscalCal` (dataflow) | `FiscalWeekIndicator` is the key filter throughout. `FiscalMonthIndicator` used only for `FutOrd` measures. |
| **Warehouse** | `z_WarehouseMaster` (dataflow) | Standard conformed; excluded WHs 213, 215, 55 hardcoded in Actuals SQL. |
| **Vendor** | `z_VendorMaster` (dataflow) | Present but no measures reference it — likely used for report filtering only. |
| **Customer** | `z_CustomerMaster_AFI` (dataflow + **local augmentation**) | The dataflow entity `CustomerMaster_AFI` is loaded and then **8 rows are appended inline in Power Query** (AFICONS, ECOMM, HSENT, HSLIC, INT, MASSRENT, NFM, RHCUST). These synthetic rows use the Customer Group code as both `Account And ShipTo Number` and `Account Name`. **⚠️ This is a structural hack** — see §9. |

**Note:** `FcstAccuracy[CustGroup]` and `Forecast[CustGroup]` join to `z_CustomerMaster_AFI[Account And ShipTo Number]` — joining a forecast customer group string to an account+shipto key. This only works because of the 8 manually appended rows that place the CustGroup string value in the `Account And ShipTo Number` field. If a new Customer Group is added to the forecast system and not added to this hardcoded list, its data silently drops out of any customer-filtered view.

---

## 7. Duplication / Consolidation Signals

1. **`Curr Qty` and `Curr Req Qty` are identical:**
   ```dax
   Curr Qty     = CALCULATE(SUM(Actuals[Qty]), Actuals[Sales Type]="Current Request")
   Curr Req Qty = CALCULATE(SUM(Actuals[Qty]), Actuals[Sales Type]="Current Request")
   ```
   Exact same expression, two measure names. One is dead code.

2. **`Inv Qty` vs `Inv Qty (CS)` — one-week boundary difference:**
   - `Inv Qty`: `FiscalWeekIndicator < 1` (includes week 0 = current week)
   - `Inv Qty (CS)`: `FiscalWeekIndicator < 0` (excludes current week)  
   The `(CS)` suffix is unexplained — possibly "Current-week Subtracted". The difference is only visible when looking at the current week. Both are kept active but the naming gives no guidance on when to use which.

3. **`dfoFUTO` vs `FUTO` — two "future orders" measures:**
   - `FUTO = SUM(Actuals[Qty]) where Sales Type="Current Request" AND FiscalWeekIndicator >= 0` — from `Actuals`, weekly grain
   - `dfoFUTO = SUM(FutOrd[dfcOrderFutureQty]) where FiscalMonthIndicator=0` — from `FutOrd`, monthly grain, Logility's own FUTO field  
   These measure the same business concept (open forward orders) from different source tables with different grains. A user comparing them will see different numbers; no model documentation explains which to use.

4. **`Lag Fcst` and `90Day Error` and `90Day Error %` — accuracy measures are structurally broken:**  
   Rather than three distinct measures, all three are effectively `Lag Fcst` (since `ACTD (accy)` = BLANK). They should be consolidated once the actual demand column is repaired.

5. **`FcstAccuracy` vs `Forecast` — two weekly forecast tables from different source systems:**  
   `FcstAccuracy` pulls lagged forecast from `SupplyChain_Enh.DemandForecastSnapshot`; `Forecast` pulls working forecast from `Wholesale_DemandPlanning_AFI.DemandForecast`. These are different tables in different schemas. If the working and lagged forecast snapshots diverge in methodology, the comparison becomes unreliable.

6. **`z_ItemFilter` references `[Curr Qty] + [FUTO] + [Writ Qty]`** — a product-dimension filter column that calls three measures. This creates a dependency from the dimension table back into fact-derived measures, similar to the reverse-lookup pattern seen in other models. Performance risk when the model has many items.

---

## 8. Open Questions

1. **Was `Actual Qty` in `FcstAccuracy` ever populated?** The SQL comment says `/* Get Forecasts at Snapshot Dates*/` and only selects forecast columns. Was there originally a second query that joined actuals, or was the `ACTD (accy)` measure always broken?

2. **What does `Forecast` (`DemandForecast` table) represent vs. `FutOrd` (`DemandForecastSnapshot`)?** The two forecast source tables are in different schemas (`Wholesale_DemandPlanning_AFI` vs `SupplyChain_Enh`). Are they the same data at different points in the ETL pipeline, or fundamentally different? Is one more current than the other?

3. **Why is the `FcstAccuracy` lag definition transitional for Apr–Jun 2025?** The SQL comment says `"Delete everything below once we get to July 2025"` but the code remains (now with `202507+` restoring 12-week lag). Was the 12-week lag intentionally suspended for those 3 months, and if so, why? Is the historical accuracy data for Apr–Jun 2025 trustworthy?

4. **What is the `(CS)` in `Inv Qty (CS)`?** Current-week Subtracted? Customer Shipments? The measure is slightly different from `Inv Qty` but without documentation it's impossible to know which is "correct" for which use case.

5. **Who maintains the 8 manually appended customer group rows in `z_CustomerMaster_AFI`?** If a new forecast customer group is introduced in Logility (e.g., a new channel like `ECOM2`), it must be manually added here or it silently falls off all customer-filtered views. Is there a process to keep this list in sync?

6. **Is `Working Fcst` from `DemandForecast` the same as the working forecast used in Demand Review?** Demand Review uses `DemandForecastSnapshot`; this model uses `DemandForecast`. If planners override their forecast in one system and it doesn't flow to both tables, the WTA and Demand Review could show different numbers for the same item.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `FiscalWeekIndicator BETWEEN -26 AND 0` (or +13) | `Actuals` SQL | 26-week past lookback for Invoiced/Written; 13-week forward for Current Request / Open Orders | **No comment** — 26 weeks = half-year; 13 weeks = quarter. Reasonable for a WBR but not documented. |
| `NumWeeks = CASE FiscalMonth IN ('3','6','9','12') THEN 5 ELSE 4` | `Forecast` SQL | Distributes monthly forecast evenly across weeks | **Partially** — reflects fiscal calendar convention. Quarter-end months always 5 weeks. Hardcoded string comparison on month numbers. |
| `FiscalMonthIndicator < 2` | `FutOrd` SQL | Loads current + next month | **No comment** — narrow 2-month scope. Enough for consumption tracking but excludes any forward visibility beyond next month. |
| `WHERE [ID].[CustomerNumber] <> '3824800'` | `Actuals` SQL | Excludes one specific account from all demand data | **No comment** — same exclusion as seen in Demand Review `OrdHist` SQL. Reason unknown — internal, test, or special account. |
| `WHERE [OO].[Inventory Allocated Flag] = '2'` | Open orders branch of `Actuals` SQL | Filters open orders to a specific allocation status | **No comment** — `Flag = '2'` meaning not documented. Presumably "allocated" or "confirmed" orders only. |
| 8 hardcoded Customer Group rows in `z_CustomerMaster_AFI` | Power Query | Appends AFICONS, ECOMM, HSENT, HSLIC, INT, MASSRENT, NFM, RHCUST as synthetic account rows | **No comment** — a structural workaround to join forecast CustGroup strings to an `Account And ShipTo Number` dimension. Each group is its own Account And ShipTo Number = the group name itself. If the dataflow's `CustomerMaster_AFI` entity ever includes these groups natively, there would be duplicate rows. |
| `GDESCD = '700'` | Actuals SQL (MC join) | Selects marketable component items for Qty-in-Box adjustment | **No comment** — same filter seen in other models. General description code 700 = items sold as part of multi-unit packs. |
| Lag windows: `-13`, `-3`, `-5`, `-9` weeks | `FcstAccuracy` SQL | Map to 12-week, 2-week, 4-week, 8-week lag periods for specific fiscal months | **Partially** — SQL comments label each deviation. The `DATEADD(WEEK, -13, ...)` = 12-week + 1 week offset (not 12 weeks exactly) because the lag is computed from the forecast snapshot date to the demanded week. |
| Hardcoded fiscal month range `202503` to `202507` | `FcstAccuracy` SQL | Boundaries for transitional lag period (Apr–Jun 2025 use shorter lags) | **Partially** — comment says "delete below once July 2025" but code now extends to `202507` as the resumption point. The 3-month transitional period (Apr/May/Jun 2025) uses entirely different lag definitions. |

**Dollar-value business impact:** This model does compute `Amt` (FOB dollar amount) in both `Actuals` and `Forecast` tables, but **no DAX measure exposes dollar amounts** — only `Qty` measures are defined. FOB $ is available at the column level for drill-through only. No financial business-case calculation exists.

---

## 10. Comparability / Consistency Issues

### a. `FcstAccuracy` lag definition changes mid-history — `90Day Error %` is not time-comparable

The `FcstAccuracy` SQL contains a structural change to the lag definition:

| Period | Lag used | Forecast period label |
|---|---|---|
| Up to and including 202503 (Mar 2025) | 12-week lag (`DATEADD(WEEK, -13, ...)`) | `'12wk'` |
| 202504 (Apr 2025) | 2-week lag (`DATEADD(WEEK, -3, ...)`) | `'2wk'` |
| 202505 (May 2025) | 4-week lag (`DATEADD(WEEK, -5, ...)`) | `'4wk'` |
| 202506 (Jun 2025) | 8-week lag (`DATEADD(WEEK, -9, ...)`) | `'8wk'` |
| 202507+ (Jul 2025 onward) | 12-week lag restored | `'12wk'` |

A trend line of `90Day Error %` across the last 26 weeks will show values from at least two different lag periods. The Apr–Jun 2025 values use 2–8 week lags (much shorter horizon, usually lower error) while all other months use 12-week lags (longer horizon, typically higher error). **These are not comparable** and a naïve time-series plot will make Apr–Jun 2025 look artificially accurate. The `Forecast Period` column distinguishes them but if filtered out or aggregated together, the distortion is invisible.

### b. `Forecast` table uses `DemandForecast` vs. `DemandForecastSnapshot` used everywhere else

| Metric | Source table | Schema |
|---|---|---|
| `Working Fcst` (this model) | `Wholesale_DemandPlanning_AFI.DemandForecast` | Older schema |
| `fcst_qty_wrk_logility` (Demand Review) | `SupplyChain_Enh.DemandForecastSnapshot` | Newer schema |

If these two tables are kept in sync these numbers should match. If there is any ETL timing difference, transformation difference, or version skew between the two, `Working Fcst` in this report will differ from the working forecast shown in Demand Review — two people looking at "the same forecast" in two different reports will see different numbers.

### c. `FUTO` vs `dfoFUTO` — same business concept, different sources and grains

| Measure | Source | Grain | What it counts |
|---|---|---|---|
| `FUTO` | `Actuals` (FactOpenOrders + InvoiceDetail) | Weekly | Open orders with current request date in current/future weeks |
| `dfoFUTO` | `FutOrd` (DemandForecastSnapshot) | Monthly | `dfcOrderFutureQty` — Logility's own aggregated future order field |

These two will rarely be equal. `FUTO` comes from the transactional order tables; `dfoFUTO` comes from what Logility has ingested into its snapshot. Data timing, order eligibility rules, and aggregation may all differ. Showing both in the same report without explanation creates confusion.

### d. `Actuals` time range differs by Sales Type — inconsistent window

Current Request extends 13 weeks into the future; Invoiced/Written stay at 26 weeks past only. A user filtering by `Sales Type = "Current Request"` sees a fundamentally wider time window than filtering by "Invoiced". The fiscal calendar `FiscalWeekIndicator` filter hides this asymmetry — it's embedded in SQL, not visible as a data column.

### e. `z_CustomerMaster_AFI` join approach — synthetic rows create dual-key ambiguity

The 8 appended rows place Customer Group strings (e.g., `"AFICONS"`) in the `Account And ShipTo Number` field, which normally holds numeric `AccountNumber + ShiptoNumber` concatenated strings. This means:
- Any real account whose number happens to match one of these 8 strings would collide
- Filtering by `Customer Group` works only because `Forecast[CustGroup]` joins to `Account And ShipTo Number`, not to an actual `Customer Group` field
- `Actuals[Account And ShipTo Number]` joins to the same key — so actual transaction accounts (numeric) and forecast customer groups (string) co-exist in the same dimension with no type enforcement

---

## Closing — Interview Seeds

1. **"The `90Day Error %` accuracy number on this report is always showing blank or -100% for some items. Were you aware that the actual demand column is missing from the underlying data, meaning the accuracy metric isn't working at all — and are you currently using a different report to track forecast accuracy?"**  
   *(Surfaces the broken accuracy measure directly and determines whether anyone is relying on it in this report or using the Forecast Accuracy (ItWh/CustItWh) reports instead.)*

2. **"In April, May, and June 2025, the forecast accuracy lag in this report was shortened from 12 weeks to 2–4–8 weeks respectively. If you look at the accuracy trend line over the past 6 months, those three months would look much more accurate than the others just because a shorter lag was used — not because the forecast actually improved. Did anyone communicate that change, and do you know which period's accuracy is 'real' by the standard definition?"**  
   *(Determines whether the lag-period transition is known and whether users are interpreting the accuracy trend correctly.)*

3. **"The `Working Fcst` line in this chart comes from a different database table than the forecast numbers in the Demand Review report. Have you ever noticed the two reports showing different forecast numbers for the same item in the same week — and if so, which one do you trust?"**  
   *(Validates whether the `DemandForecast` vs. `DemandForecastSnapshot` source difference causes visible discrepancies in practice.)*

4. **"When `dfoConsumption` drops below, say, 60% of plan in week 3 of the month — what is the concrete action that follows? Do you call the account, adjust the forecast down immediately, or wait until week 4?"**  
   *(Establishes the operational trigger and response process that the consumption rate metric is designed to support.)*
