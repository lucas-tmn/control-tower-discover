---
title: Measure Archetypes Catalog
source: output/analysis/_inventory/measure_sigs.csv
distinct_measures: 879
distinct_signatures: 253
shared_signatures: 64
measure_archetypes: 10
---

## How to read this

The 879 measures across 26 models collapse to 253 distinct normalized signatures; 64 signatures
recur across more than one model. Rather than re-transcribe every measure (that lives in the Phase 1
summaries), this catalog names the **archetypes**: the parameterized shapes that, with a conformed
dimension to slice by, replace dozens of near-identical measures. Signatures and members:
[_inventory/measure_sigs.csv](_inventory/measure_sigs.csv).

`col`/`meas`/`str`/`num` in signatures are the normalizer's placeholders for column ref, measure
ref, string literal, numeric literal.

| # | Archetype | Signature(s) | Models | ≈Members |
| --- | --- | --- | --- | --- |
| 1 | Additive base measure | `calculate(sum(col))` · `sum(col)` | 18 | 167 |
| 2 | Filtered/typed sum | `calculate(sum(col),col=str)` · `…col=num` | 10 | 76 |
| 3 | Ratio / percentage | `divide(meas,meas)` | 13 | 43 |
| 4 | Error / variance | `meas-meas` · `meas+meas` | 10 | 35 |
| 5 | Relative-period shift | `calculate(meas,col=±num)` · `…>=-num` | 5 | 60+ |
| 6 | Period averaging window | `divide(calculate(meas,…range),num)` | 6 | 20+ |
| 7 | Forecast-accuracy family | `averagex(accy,meas)` · bias/wMAPE | 6 | 60+ |
| 8 | Hardcoded warehouse slice | `WH## SI` = `calculate(sum,col=str)` | 3 | 40+ |
| 9 | Cost/cube weighting | `sumx(z_productdetails,col*meas)` | 4 | 8 |
| 10 | Conditional-format / label | `if(max(col)=str,str,blank())` · switch labels | 8 | 50+ |

---

### 1 — Additive base measure

**Canonical form:** `[Qty] := SUM(fact[value])` (or CALCULATE-wrapped for context transition).

**Members (129 via `calculate(sum(col))`, 38 via `sum(col)`):** Prod Capacity, Vendor Shipped, FC
Qty, POS Qty, Total On Hand Qty, Forecast, Actuals, Total Firm Demand, Net Fcst, On Hand Qty,
Target Prod/PO/TI/TO, the Supply Plan Detail Accuracy `Target *`/`Act *`/`Error *` family,
When-to-Disco balance measures, etc.

**Consolidation:** these are one base sum per fact column. Define base quantities once on each gold
fact; everything else derives from them.

---

### 2 — Filtered / typed sum

**Canonical form:** `[Qty (type)] := CALCULATE([Qty], fact[type] = "X")` — slice the base sum by a
type/status/transaction-code column.

**Members:** Act - Invoiced / Act - Open Ord (sales type), Issuing/Receiving Transfer · Sales
Shipments · Purchase Order · Manufacturing Receipt (transaction code), PO Receipts / MO Receipts,
Plan MO / Plan PO, RSLF/PROL/FUTO Qty, Disco/Liquidate/NewGO/PlanDrop/Scrap Qty.

**Consolidation:** one parameterized measure per fact, sliced by the governed type column. Several
of these (RSLF/PROL/FUTO, transaction codes) depend on the unpivot/normalization patterns in
[transformation-patterns.md](transformation-patterns.md).

---

### 3 — Ratio / percentage

**Canonical form:** `[Rate] := DIVIDE([numer], [denom])`.

**Members (43 across 13 models):** wMAPE, Bias %, In Stock, Demand Fulfillment, Consumption Rate,
ProjFulfillment%, Inv Turns, GoalInvTurns, On-Time %, % Excess/Sold/Net Forecast/Safety Stock,
Months of Supply.

**Consolidation:** keep DIVIDE shape; these stay per-report but reuse the same numerator/denominator
base measures once those are centralized.

---

### 4 — Error / variance & simple combination

**Canonical form:** `[Error] := [Forecast] - [Actual]` / `[Total] := [a] + [b]`.

**Members:** Error Qty, Fcst Gap, 90Day Error, SS Qty Change, Net Inv Change, MO Total, POS + FC
Qty, OH + SI, ActFcst, FCST Qty (= RSLF+PROL), Total PSW family.

**Consolidation:** trivial once the operands are conformed base measures.

---

### 5 — Relative-period shift (YoY / prior / trailing)

**Canonical form:** `[Measure (Y-n)] := CALCULATE([Measure], DimDate[period offset] = -n)` and
trailing-window `… >= -n`.

**Members (60+):** the whole `YTD/YTG ACT`, `Ord Qty (Y-1)`, `Req Order -1/-2`, `FC Bias - …last 3
Mo`, `R12 *`, `Prior 12M *`, `In Stock - Last Mo`, `Demand Fulfillment LY/TY` family across Demand
Review, Product Review (NEW), GF Act+Fcst, Safety Stock Analysis, Weekly Trend Analysis.

**Consolidation:** these all depend on the **fiscal-indicator-window** columns. With governed
relative-period indicators on `DimDate`, these become one time-intelligence measure per base metric
parameterized by offset, instead of dozens of hardcoded variants.

---

### 6 — Period averaging window

**Canonical form:** `[3M Avg] := DIVIDE(CALCULATE([Measure], DimDate[offset] >= -3 && < 0), 3)`.

**Members:** 3M Average, 6M Average, 8wk Avg Receipt, Avg WHC Demand, Daily Avg, avg Wrk/Cur Fcst,
Seas Annualized 3 M, Trend (3M vs 6M).

**Consolidation:** one windowed-average helper parameterized by window length, on top of the
relative-period indicators.

---

### 7 — Forecast-accuracy family

**Canonical form:** a small set over `fact_forecast_accuracy` — `Total Forecast`, `Total Demand`,
`Error = Fcst-Dmd`, `Bias % = DIVIDE(Error,Demand)`, `Mean ABS Dev = AVERAGEX(accy, |fcst-dmd|)`,
`wMAPE = DIVIDE(AbsDev, Demand)`, plus Naive and Bias-adjusted variants.

**Members (60+):** nearly identical sets appear in **Forecast Accuracy (ItWh)**, **Forecast Accuracy
(Cust_ItWh)** (suffixed `_CIW`), and embedded in **Demand Review** / **Product Review (NEW)** /
**Weekly Trend Analysis**. The only real difference is the grain (Item vs Item-WH vs Cust-Item-WH)
and the lag (2wk/30d/90d).

**Consolidation:** **define this archetype once** over `fact_forecast_accuracy`, parameterized by
grain and lag. This is the single largest measure-duplication cluster after the warehouse family.

---

### 8 — Hardcoded warehouse slice — **flagged exception**

**Today:** `Supply Plan Detail` has `WH1 SI`, `WH5 SI`, `WH15 SI`, `WH16 SI`, `WH17 SI`, `WH28 SI`,
`WH42 SI`, `WH50 SI`, `WH70 SI`, `WHECR SI`, each `CALCULATE(SUM(SI), Warehouse = "##")`, then the
same again for `WH## SI-SS` and `WH## Wk4 SI` — ~40 measures. `Inv Management` repeats it as
`Whse # - SI`.

**Canonical form:** **one** `[SI] := SUM(fact_supply_plan[ShippableInventory])` sliced by
`DimWarehouse[Warehouse]` on the visual. Same for SI-SS and the week-bucket variants.

**Action:** this is the headline measure cleanup — replace ~40+ hardcoded-warehouse measures with
one measure + the conformed `DimWarehouse`. Depends on warehouse-normalization reconciliation.

---

### 9 — Cost / cube weighting

**Canonical form:** `[$ or Cubes] := SUMX(DimProduct, DimProduct[factor] * [Qty])`.

**Members:** ActFcst $, OrdFcst $, OH $, On Hand Cubes, SS Cubes, Excess FG $, Total Cubes — across
GF Act+Fcst, Safety Stock Analysis, Supply Plan Detail, Inventory Transactions.

**Consolidation:** one weighting helper parameterized by the DimProduct factor (FOB price / cube /
avg sales price), reused across facts.

---

### 10 — Conditional-format & label measures

**Canonical form:** presentation-layer `IF(MAX(col)="X", "#hex", BLANK())` color measures and
`SWITCH/SELECTEDVALUE` title/label measures.

**Members (50+):** Top Negatives Background/Font color, AFT_SI-SS_PSW Background color DUE/ETD
(±WHSE), Supplier On-Time `Combined_*` table-selector switches, Demand Review / Product Review title
and `consumption_*` indicator measures.

**Action:** these are **report-local presentation logic**, not analytical measures. Keep them in the
report layer; do **not** lift into the centralized semantic model. They are listed so reviewers know
the ~50 are intentionally excluded from consolidation.

---

## What stays per-report

Beyond archetype 10, a long tail of genuinely bespoke single-model measures (DvC trendline
`LINESTX`, JadeTeam SS adjustment, Supplier On-Time penalty/FYTD logic, MOS case ladders in Inv
Management) are model-specific and remain in their reports. The centralized model should provide the
**base quantities and conformed dimensions** these build on, not the bespoke compositions themselves.
