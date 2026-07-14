---
title: Reusable Transformation Patterns Catalog
source: output/analysis/_inventory/transform_patterns.csv
reusable_patterns: 6
---

## How to read this

Each section is a recurring transformation that appears in many models' source queries or
calculated columns. Today each model re-implements it independently — sometimes identically (safe
to lift once), sometimes inconsistently (a reconciliation risk). These are the building blocks for
the **silver** layer: implement each once, correctly, and have every gold fact/dimension consume it.
Full pattern-to-model map: [_inventory/transform_patterns.csv](_inventory/transform_patterns.csv).

| Pattern | Models | Layer | Reconciliation risk |
| --- | --- | --- | --- |
| fiscal-indicator-window | 18 | DimDate / silver | Low — mostly identical, but anchored to "today" |
| latest-snapshot | 16 | silver | Medium — snapshot key differs per source |
| rslf-prol-futo-unpivot | 11 | silver (forecast) | Medium — column sets drift |
| marketable-sku-conversion | 4 | silver / DimProduct | Low — identical formula, centralize |
| item-wh-composite-key | 4 | silver keys | Low — standardize separator |
| warehouse-normalization | 3 | DimWarehouse | High — divergent mappings |

---

### fiscal-indicator-window

**What it does:** Computes relative-period indicator columns on the fiscal calendar — "this fiscal
month = 0, last month = -1", week/month/quarter/year offsets from today — so measures can filter
`col = 0`, `col >= -3`, etc., instead of hardcoding dates. Drives the vast `calculate(meas, col=
-num)` / `col>=-num` measure family.

**Where it appears (18 models):** Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing, Amazon POS,
Demand Review, Forecast Accuracy (Cust_ItWh), Forecast Accuracy (ItWh), GF Act+Fcst, Inventory
Health, Inventory Transactions and Item Balance Detail, On Time % by Customer, Product Review
(NEW), Production Capacity Vs Forecast, Rolling Report - Wanek Millen, Safety Stock Analysis,
Supply Plan Detail Accuracy, Top Negatives, Weekly Trend Analysis, When to Disco v2.

**Inconsistencies to reconcile:** the offsets are recomputed relative to `TODAY()` in each model's
`z_FiscalCal`, and `Act+Fcst*` carries a **hardcoded** `FiscalWeeksinMonth` SWITCH with a baked-in
`202212 → 6` exception. Centralize the relative-period indicators as governed DimDate columns
(refreshed daily) and drop the hardcoded exception.

---

### latest-snapshot

**What it does:** Filters a snapshot table to its most recent snapshot — `WHERE SnapshotDate =
(SELECT MAX(SnapshotDate) …)` or the DAX equivalent — so operational reports show "current" while
the underlying table retains history.

**Where it appears (16 models):** Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing, AFT_SI-SS_PSW,
Amazon POS, Demand Review, DvC - WanekMillenium, GF Act+Fcst, Inv Management, Plan Drop 1, Product
Review (NEW), Production Capacity Vs Forecast, Rolling Report - Wanek Millen, Safety Stock Analysis,
Supply Plan Detail, Weekly Trend Analysis, When to Disco v2.

**Inconsistencies to reconcile:** the snapshot key differs per source — `SnapshotDate`,
`SPRunDate`, `FileDate`, `InsertedDate`, `dfcSnapshot`, `InitialDate`. Implement one silver
"latest-snapshot" helper parameterized by the snapshot column, and expose both a current view and
the full-history fact (forecast-accuracy and supply-plan-accuracy need history — see
[fact-grains.md](fact-grains.md)).

---

### rslf-prol-futo-unpivot

**What it does:** Unpivots the Logility forecast columns — RSLF (released forecast), PROL (planned
orders), FUTO (future orders), plus working/published variants — from a wide snapshot into a long
forecast-type × value shape so a single measure can sum any forecast type.

**Where it appears (11 models):** Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing, Demand Review,
Forecast Accuracy (Cust_ItWh), Forecast Accuracy (ItWh), GF Act+Fcst, Inventory Health, Product
Review (NEW), Production Capacity Vs Forecast, Safety Stock Analysis, Weekly Trend Analysis.

**Inconsistencies to reconcile:** the exact column set unpivoted drifts (some models include FUTO,
some split working vs 90d-lag, some carry promo separately). Define one canonical forecast-type
enumeration in silver feeding `fact_forecast_snapshot`; measures like `RSLF Qty`, `PROL Qty`,
`FUTO Qty` become one measure sliced by forecast type.

---

### marketable-sku-conversion

**What it does:** Converts component/non-marketable SKUs to their marketable parent and scales
quantity — `DIVIDE(1, SWITCH(General Description Code, 700, LOOKUPVALUE(Qty In Box, parent SKU
= LEFT(Item SKU, LEN-1)), 1))` — so demand rolls up to the sellable unit.

**Where it appears (4 models):** Demand Review, GF Act+Fcst, Product Review (NEW), Weekly Trend
Analysis (the `marketable-sku-conversion` measure pattern; the `z_MarketableConversion` calc column
in GF Act+Fcst and Weekly Trend Analysis).

**Inconsistencies to reconcile:** the formula is identical where it appears as a calc column — low
risk. Centralize as a silver conversion factor exposed on `DimProduct`, so OrdHist/Actuals roll up
consistently across all four reports.

---

### item-wh-composite-key

**What it does:** Builds the Item-SKU × Warehouse composite key used to join demand, supply, and
inventory facts at the item-warehouse grain.

**Where it appears (4 models):** Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing, Production
Capacity Vs Forecast, Safety Stock Analysis.

**Inconsistencies to reconcile:** separator/format varies (concatenation vs surrogate). Standardize
one `Item_WH` key generation in silver and use it as the join key for `fact_actuals`,
`fact_supply_plan`, and `fact_inventory_position`.

---

### warehouse-normalization

**What it does:** Re-maps raw warehouse codes to a physical-warehouse / site grouping (collapsing
logical warehouses onto the physical DC that fulfills them).

**Where it appears (3 models):** GF Act+Fcst (`Physical WH`), Safety Stock Analysis (`WH Site`),
Weekly Trend Analysis (`WHSE`).

**Inconsistencies to reconcile:** **highest risk** — three different column names with potentially
different mappings, and several measures (`z_ACTD(excWH)`, `Ord WH Split`, `WHC Demand`) depend on
`removefilters`/`all` over the warehouse table. Agree one canonical physical-warehouse mapping in
`DimWarehouse` (see [conformed-dimensions.md](conformed-dimensions.md)); this is also what enables
collapsing the hardcoded `WH## SI` measure family.
