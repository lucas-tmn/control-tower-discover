# Complete Series In Stock — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `5aa663ad-cd8b-4672-a5ea-0922b6b22db0`  
**Report ID:** `e733c956-cb30-4c33-9f12-4113939b1279`  
**Analysis Date:** 2026-07-08  
**Model Size:** 31 tables (5 data + 3 calculated + 3 dim + local date tables); **66 DAX measures** across 4 tables; Compatibility Level 1600  
**Data Architecture:** Dataflow-backed (converted 03/31/2020) — original SQL preserved in partition comments  
**BIM File:** [bim/Complete_Series_In_Stock.bim](bim/Complete_Series_In_Stock.bim)

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For each item series and warehouse, what percentage of SKUs in the series are **in stock right now** — and how many weeks forward will they remain in stock based on available-to-promise ATP quantities?

**This report operates at the series level, not the item level.** A series (e.g., "Signature Design - Ashley T944 Ashley Manor") is only considered "in stock" when **all** SKUs in that series are in stock. A single missing SKU breaks the series. This "complete series" concept is the defining feature of this report and drives all key metrics.

**Primary chain links served:**

| Link | How served |
|---|---|
| **Inventory** | `InventoryHistory` — 13-week rolling weekly on-hand qty + 26-week avg demand; `CurrentOnHand` — point-in-time snapshot derived from latest InventoryHistory week |
| **Supply / ATP** | `AvailToPromise` — 6-week forward ATP quantities (Week1–Week6) per item-warehouse; determines whether the series will remain in stock through each future week |
| **In-stock performance** | `SeriesInvHist` — calculated series-level % in stock and % on hand, week by week; historical trend enabled |
| **Safety Stock** | `SafetyStock` — current SS targets vs. on-hand gap and vs. average weekly demand |
| **Demand classification** | `ABCXYZ` — ABC (volume) + XYZ (volatility) segmentation per item; used for prioritization |

**Not served:** Forecast, order history, on-time delivery, forecast accuracy.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Identify series with incomplete in-stock position** — which series are missing one or more SKUs right now or in the next 6 weeks? | Supply Planner / Customer Service | Weekly | **Operational** — handle goods: expedite, transfer, or notify |
| **Prioritize series by forward ATP coverage** — is the series in stock for Week1 only, or through Week6? | Supply Planner | Weekly | **Operational** — handle goods: prioritize PO expedites |
| **Identify individual SKUs breaking a series** — drill to item-location level to find the one or two items causing the series to be incomplete | Supply Planner | Weekly | **Operational** — expedite specific item-warehouse |
| **Review Safety Stock adequacy** — is SS set above or below average weekly demand? Which items have on-hand below SS? | Inventory Planner | Monthly | **Performance/Governance** — validate SS parameters |
| **ABC/XYZ prioritization** — focus attention on A-items (high volume) with X classification (stable demand) that are at risk | Supply Planner / Planning Manager | Weekly | **Performance/Governance** — resource allocation |
| **Trend series in-stock % over prior 13 weeks** — is performance improving or deteriorating? | Planning Manager / WBR Leadership | Weekly | **Performance/Governance** — scorecard, accountability |
| **Identify overstock and understock positions** (`OverStockQty`, `UnderStockQty` in `CurrentOnHand`) | Supply Planner | Weekly | **Operational** — transfer or cancel supply |

> **No Financial-Justification decisions.** No dollar-value calculation exists. No cost or revenue impact measures.

---

## 3. Key Metrics / Measures

### From `_GeneralMeasures` (30 measures)

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `Series SKU Count` | Total SKUs in a series | Series × WH × Week | `SUM(SeriesInvHist[SKUs In Series])` | |
| `SKUs In Stock Count` | SKUs with ATP ≥ avg weekly demand | Series × WH × Week | `SUM(SeriesInvHist[SKUs In Stock])` | |
| `SKUs On Hand Count` | SKUs with any on-hand qty > 0 | Series × WH × Week | `SUM(SeriesInvHist[SKUs On Hand])` | |
| `In Stock %` | % of series SKUs in stock | Series × WH × Week | `[SKUs In Stock Count] / [Series SKU Count]` | |
| `On Hand %` | % of series SKUs with any inventory | Series × WH × Week | `[SKUs On Hand Count] / [Series SKU Count]` | |
| `Series In Stock` | Count of series where 100% SKUs are in stock | Series × WH × Week | `MAX(SUM(SeriesInvHist[Series % In Stock]) where =1, 0)` | ⚠️ see §9 |
| `Series In Stock %` | % of series that are fully in stock | WH × Week | `[Series In Stock] / [Series Count]` | |
| `Series On Hand %` | % of series with 100% SKUs on hand | WH × Week | `[Series On Hand] / [Series Count]` | |
| `Item Qty Short` | Total units short across items | Item × WH × Week | `ABS(SUM(InventoryHistory[QtyShort]))` | |
| `On Hand Qty` | Total on-hand qty, current week | Item × WH | `SUM(InventoryHistory[OnHandQty])` filtered to `TODAY()+MOD(7-WEEKDAY(TODAY()),7)` | ⚠️ TODAY() in Import mode |
| `Count of SKUs < 1Wk Supply` | Items where OnHand < AvgQty (less than 1 week of supply) | Series × WH | Same date filter as above | ⚠️ TODAY() in Import mode |
| `Safety Stock` | Sum of SS targets | Item × WH | `SUM(SafetyStock[SafetyStock])` | |
| `SS Gap to Avg Demand` | Items where SS < avg weekly demand (underfunded) | Item × WH | `SUM(SafetyStock[Safety Stock < AvgWklyDemand])` — capped at 0 (negative = gap) | |
| `On Hand Gap to SS` | Items where on-hand < SS (below safety stock) | Item × WH | `SUM(SafetyStock[On Hand Shortage to SS])` — capped at 0 | |
| `SS Excess to Avg Demand` | Items where SS > avg weekly demand (overfunded) | Item × WH | `SUM(SafetyStock[Safety Stock > AvgWklyDemand])` — positive only | |
| `ATPWeek1` – `ATPWeek6` | ATP qty for each forward week (1–6) | Item × WH | `SUM(AvailToPromise[ATPQty])` filtered by `ATPWeek="Week1"` etc. | ⚠️ duplicate of `Wk1 ATP`–`Wk6 ATP` in `_ATPMeasures` |
| `Series in Stock Current Week` | Series in-stock % this week, excluding WH 335 | — | `[Series In Stock %]` with `WeekEnding≥TODAY()`, WH≠"335" | ⚠️ TODAY() + hardcoded WH exclusion |

### From `_ATPMeasures` (24 measures)

| Measure | Business meaning | Flag |
|---|---|---|
| `Wk1 ATP`–`Wk6 ATP` | ATP qty per forward week — **duplicate of `ATPWeek1`–`ATPWeek6`** | ⚠️ duplicate |
| `Wk1 In Stock %`–`Wk6 In Stock %` | % of series SKUs in stock per forward week | |
| `Wk1 Short`–`Wk6 Short` | Shortage qty per forward week | |
| `Avg Wkly Demand` | Average weekly demand (from `AvailToPromise[AvgQty]`, Week1 filter) | ⚠️ pulls AvgQty from ATP table at Week1 only — may differ from InventoryHistory avg |
| `ATP Shortage` | Total shortfall vs. avg weekly demand | |
| `SKUs in Stock %` | % of ATP series SKUs in stock (uses ATPSeriesCount denominator) | |

### From `ATP Summary` table (11 measures)

| Measure | Business meaning | Flag |
|---|---|---|
| `Series in Stock % - Wk1` – `Wk6` | **AVERAGEX** of `SeriesInStock%` per week | ⚠️ AVERAGEX of a binary (0/1) column — effectively mean of 0/1 flags, not a count-based % |
| `Series_in_Stock %` | 0 or 1: is entire series in stock? | Binary flag |
| `Total On Hand Qty` | On-hand qty filtered to current ATP week ending | ⚠️ TODAY() in Import mode |

### From `CurrentOnHand` (1 measure)
| Measure | Business meaning | Flag |
|---|---|---|
| `Weeks On Hand` | `OnHandQty / AvgQty` at item-location level | |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| `z_ProductDetails` | PowerBI Dataflow `346f2aa1...` workspace `a47e4573...` → `CurrentProductDetails` (+ `Initial Invoice Date` calculated column added in PQ) | Governed Dataflow | Low |
| `z_FiscalCal` | Same dataflow → `AshleyFiscalCalendarV2` | Governed Dataflow | Low |
| `z_WarehouseMaster` | Same dataflow → `WarehouseMaster` | Governed Dataflow | Low |
| **`InventoryHistory`** | PowerBI Dataflow `db1585dc...` workspace `f0e1bc90...` (= **Supply Chain Analytics-Premium** workspace itself) → entity `InventoryHistory` | Governed Dataflow (self-workspace) | Medium — converted from direct SQL on 03/31/2020; original SQL preserved in comment |
| **`AvailToPromise`** | PowerBI Dataflow `b65f2c0b...` workspace `a47e4573...` → entity `AvailableToPromiseLastUpdate` | Governed Dataflow | Medium |
| **`ABCXYZ`** | PowerBI Dataflow `db1585dc...` (same as InventoryHistory) → entity `ABCXYZ` | Governed Dataflow | Medium — sourced from `PowerBI_SupplyChain.AFIItemABCCurrentSnapshot` (latest snapshot only) |
| **`SafetyStock`** | Same dataflow → entity `SafetyStock` | Governed Dataflow | Medium — sourced from `PowerBI_SupplyChain.SupplyPlanDetailCurrentDay`, current week only |
| `SeriesInvHist` | **Calculated table** — `SUMMARIZE(InventoryHistory, ...)` in-model | DAX Calculated | Medium — expensive at scale; recalculates on every model refresh |
| `ATPInvItemLocation` | **Calculated table** — `SUMMARIZE(FILTER(InventoryHistory, WeekEnding=TODAY()+…), …)` | DAX Calculated + TODAY() | ⚠️ **High** — TODAY() baked into calculated table definition; table is stale the moment the day changes |
| `ATP Summary` | **Calculated table** — `SUMMARIZE(AvailToPromise, …)` joining multiple tables | DAX Calculated | Medium |
| `CurrentOnHand` | **Power Query derived** from `InventoryHistory` — filters to `MAX(Week Ending)` row, adds `WeeksOnHand` | PQ derived table | Low |

**Original EDW sources** (from SQL comments in partition expressions):
- `InventoryHistory` → `SupplyChain_Enh.DemandFulfillmentCommonContainer_Logility` (date anchoring), `Enterprise_DW.DimItemMaster`, `AFISales_Enh.OrderHistory`, `SupplyChain_Enh.FactATPInventory` (ATP quantities), `SupplyChain_Enh.FactWeeklyInventoryHistory`
- `ABCXYZ` → `PowerBI_SupplyChain.AFIItemABCCurrentSnapshot`
- `SafetyStock` → `PowerBI_SupplyChain.SupplyPlanDetailCurrentDay` (current week SS only)

> All original sources on `ashley-edw.database.windows.net` (Azure SQL). No Fabric sources.

---

## 5. Grain & Snapshot Strategy

**Primary grains:**

| Table | Grain |
|---|---|
| `InventoryHistory` | Item SKU × Warehouse (Location) × **Fiscal Week** — 13-week rolling history |
| `SeriesInvHist` | Series × Warehouse × **Fiscal Week** — calculated from InventoryHistory via SUMMARIZE |
| `AvailToPromise` | Item SKU × Warehouse × **ATP Week slot** (Week1–Week6 relative labels) × Run Date |
| `ABCXYZ` | Item SKU — latest snapshot only |
| `SafetyStock` | Item SKU × Warehouse — current week only |
| `CurrentOnHand` | Item SKU × Warehouse — latest week from InventoryHistory |

**Snapshot strategy:** Hybrid.

- `InventoryHistory` — **13 weeks of weekly snapshots** preserved → enables trend analysis of series in-stock % over time.
- `AvailToPromise` — **latest run only** (`AvailableToPromiseLastUpdate`); 6-week forward view; no historical ATP snapshots.
- `ABCXYZ` and `SafetyStock` — **latest snapshot only**.
- `ATPInvItemLocation` — calculated table rebuilt at each refresh, filtered to current week via `TODAY()`.

**Implication:** Historical in-stock trend is supported (13 weeks) but forward ATP coverage is always current-state — no way to compare this week's ATP profile to last week's ATP profile.

---

## 6. Dimensions Used

| Dimension | Table | Connected? | Notes |
|---|---|---|---|
| **Product** | `z_ProductDetails` (97 cols) | ✅ | Conformed; adds `AltSeries Number` (U-SKU handling), `AltSeries Description`, `Initial Invoice Date` (derived in PQ), `z_SumItems`, `z_SeriesSort` |
| **Date / Fiscal Calendar** | `z_FiscalCal` (38 cols) | ✅ | Connected to `InventoryHistory[Week Ending]`, `AvailToPromise[WeekEnding]`, `SeriesInvHist[Week Ending]` |
| **Warehouse** | `z_WarehouseMaster` (11 cols) | ✅ | Connected to `InventoryHistory[Location]`, `AvailToPromise[Warehouse]`, `SafetyStock[Warehouse]`, `SeriesInvHist[Warehouse]`, `CurrentOnHand[Location]` |

**All dimension tables are properly connected** — no orphaned tables (unlike When to Disco v2).

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `AltSeries Number` | `z_ProductDetails` calc column | `IF(LEFT(ItemSKU,1)="U", LEFT(ItemSKU,6), SeriesNumber)` — UPH items get first 6 chars as series | Medium — SKU prefix convention; duplicated in `AvailToPromise[AltSeries Number]` with identical SWITCH logic |
| `AltSeries Description` | `z_ProductDetails` calc column | Same U-SKU logic → custom description from first 6 chars + SeriesName + SeriesColor | Medium — duplicated in `InventoryHistory[AltSeriesDescription]` (source column) and `SeriesInvHist[Series Description]` |
| `Initial Invoice Date` | `z_ProductDetails` (Power Query) | `Date.FromText("01/01/2000")` fallback if `Initial Invoice Period = ""` else `Date.FromText(concat)` | Medium — 01/01/2000 sentinel same pattern as Product Review (NEW); different fallback date (2000 vs 1900) |
| `z_SumItems` | `z_ProductDetails` calc column | `CALCULATE(AVERAGE(InventoryHistory[OnHandQty]), ...)` — average on-hand qty per item, used for sorting | Low — sort helper |
| `z_SeriesSort` | `z_ProductDetails` calc column | `CALCULATE(AVERAGE(InventoryHistory[OnHandQty]), FILTER(z_ProductDetails, SeriesNumber=EARLIER(...)))` — series-level sort | Low — sort helper |
| `SeriesProp = 0.05` | Original SQL (in dataflow comment) | Items that represent < 5% of series demand are excluded from series "completeness" calculation | ⚠️ **High** — hardcoded threshold in EDW/dataflow SQL; not visible as a model parameter; defines what "complete" means |
| `ATPWeek1–6` in `InventoryHistory` | Calculated columns | `CALCULATE(SUM(AvailToPromise[ATPQty]), FILTER(AvailToPromise, ItemSKU=Item AND WH=Location AND ATPWeek="Week1"))` — row-level cross-table calculation | ⚠️ **High** — expensive row-level CALCULATE inside calculated column; duplicates logic already in `_GeneralMeasures[ATPWeek1–6]`; same ATP columns duplicated in `ATPInvItemLocation` |
| `SKU In Stock` | `InventoryHistory` (source column from dataflow) | Pre-calculated in dataflow SQL — definition depends on original SQL (OnHand ≥ AvgQty?) | Medium — definition is in dataflow, not visible in model |

---

## 7. Duplication / Consolidation Signals

1. **`ATPWeek1`–`ATPWeek6` appear in three places:**
   - As calculated columns on `InventoryHistory` (row-level, expensive)
   - As DAX measures `ATPWeek1`–`ATPWeek6` in `_GeneralMeasures`
   - As DAX measures `Wk1 ATP`–`Wk6 ATP` in `_ATPMeasures`
   - As calculated columns on `ATPInvItemLocation`
   Four parallel implementations of the same ATP-qty-by-week concept. None are labeled as canonical.

2. **`In Stock` concept calculated in 4 different places:**
   - `InventoryHistory[SKU In Stock]` — source column from dataflow (definition opaque)
   - `SeriesInvHist[SKUs In Stock]` — SUMMARIZE of InventoryHistory[SKU In Stock]
   - `AvailToPromise[ATP In Stock]` — `IF(SkuFilter=0, BLANK, IF(AvgQty<=ATPQty, 1, 0))`
   - `AvailToPromise[ATP In Stock_2]` — `IF(SkuFilter=0, BLANK, IF(1<=ATPQty, 1, 0))` (threshold is **1 unit**, not AvgQty)
   The "in stock" definition differs between the historical view (SkuInStock from dataflow) and ATP view (AvgQty ≤ ATPQty vs. 1 ≤ ATPQty). Three different thresholds for "in stock."

3. **`Series In Stock %` calculated in three tables:**
   - `SeriesInvHist[Series % In Stock]` (weekly historical)
   - `_GeneralMeasures[Series In Stock %]` (using SeriesInvHist)
   - `ATP Summary[SeriesInStock%]` + `[SeriesInStock%2]` (using AvailToPromise, two variants)
   - `ATP Summary` measures `Series in Stock % - Wk1` through `Wk6` (AVERAGEX)
   All represent "what % of a series is in stock" but with different source tables, time frames, and aggregation methods.

4. **`Avg Wkly Demand` in two measure tables with different sources:**
   - `_ATPMeasures[Avg Wkly Demand]` → `SUM(AvailToPromise[AvgQty])` filtered to Week1
   - `ATP Summary[Avg Wkly Dmnd]` → `SUM(ATP Summary[AvgQty])` filtered to Week1
   Same concept, different table sources — may not reconcile.

5. **`AltSeries Number` / `AltSeries Description` duplicated across `z_ProductDetails`, `AvailToPromise`, `InventoryHistory`, `SeriesInvHist`, and `ATP Summary`** — each table carries its own copy of this U-SKU normalization. If the U-SKU logic changes, it must be updated in 5+ places.

6. **`_GeneralMeasures` and `_ATPMeasures` overlap:**
   `_GeneralMeasures` has `ATPWeek1`–`ATPWeek6` (measure set);
   `_ATPMeasures` has `Wk1 ATP`–`Wk6 ATP` (same content, different name prefix).
   Two separate measure tables for what is fundamentally one topic (ATP by week).

7. **`Series_in_Stock %` in `ATP Summary` vs. `Series In Stock %` in `_GeneralMeasures`** — same name, different calculation: ATP Summary version returns 0/1 per series; _GeneralMeasures version returns a rate across all series. Easily confused in reports.

---

## 8. Open Questions

1. **`SeriesProp = 0.05` (5%) threshold.** The original SQL in the dataflow comment sets `@SeriesProp = .05` — items representing < 5% of a series' demand are excluded from the series completeness count. This is the most business-critical parameter in the model: it defines what "complete series" means. Is this threshold documented anywhere? Has it ever been changed? Who owns it?

2. **`SKU In Stock` column source definition.** This is a pre-calculated column in the `InventoryHistory` dataflow — its definition is in the dataflow SQL, not visible in the Power BI model. Does "in stock" mean `OnHandQty > 0` or `OnHandQty ≥ AvgQty`? The two thresholds produce materially different "series in stock" numbers. The ATP view uses `AvgQty ≤ ATPQty`; the historical view definition is opaque from here.

3. **`AvailToPromise[ATP In Stock]` vs. `[ATP In Stock_2]`** — two in-stock definitions: one uses `AvgQty` as threshold, one uses `1` (any ATP > 0). Which drives the `Series in Stock % - Wk1` measures visible to users? `SeriesInStock%` and `SeriesInStock%2` in `ATP Summary` map to each version respectively — are both displayed in the report, and do users know they're different?

4. **`ATPInvItemLocation` calculated table uses `TODAY()`** — recalculated at query time, not at refresh. If the model refreshed on Tuesday, `TODAY()` on Thursday returns Thursday's date, which may or may not exist in `InventoryHistory[Week Ending]` (which contains weekly end dates). If no matching week-ending date exists, the entire `ATPInvItemLocation` table returns empty.

5. **Two dataflow workspaces:** `InventoryHistory`, `ABCXYZ`, `SafetyStock` come from dataflow `db1585dc` in workspace `f0e1bc90` (Supply Chain Analytics-Premium itself); `AvailToPromise` comes from dataflow `b65f2c0b` in workspace `a47e4573` (a different workspace). If the two dataflows refresh at different times, ATP and inventory data may be from different points in time — misaligning ATP coverage with on-hand position.

6. **13-week history window for `InventoryHistory` vs. 26-week average window.** The original SQL uses `@StartDate = DATEADD(WEEK, -13, @EndDateAvg)` for the history dataset but `@StartDateAvg = DATEADD(WEEK, -26, @EndDateAvg)` for the demand average calculation. So the report shows 13 weeks of in-stock history but the AvgQty denominator uses 26 weeks of order history. Are users aware the "average demand" baseline covers a longer period than the history trend view?

7. **`ABCXYZ` is latest-snapshot only** — no historical ABC classification is available. If an item moved from A to B, the model always shows it as B. How often does classification change, and does the team want trend visibility here?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`SeriesProp = 0.05`** | Original dataflow SQL (comment) | Items < 5% of series demand excluded from series completeness — defines "complete series" | **No** — in SQL comment only; not surfaced in model or report |
| **`DATEADD(WEEK, -13, @EndDateAvg)`** | Original dataflow SQL | 13-week history window for `InventoryHistory` rolling view | **No** |
| **`DATEADD(WEEK, -26, @EndDateAvg)`** | Original dataflow SQL | 26-week window for average weekly demand calculation | **No** — different window than the 13-week display horizon |
| **`TODAY()+MOD(7-WEEKDAY(TODAY()),7)`** | Multiple DAX measures and calculated tables | "Next Sunday" date — used to anchor to the most recent/upcoming fiscal week end | **No** — assumes fiscal weeks end on Sunday; breaks if fiscal week-end day ever changes |
| `AvgQty ≤ ATPQty` | `AvailToPromise[ATP In Stock]` | In-stock threshold for ATP view: if ATP ≥ average weekly demand, item is "in stock" | **No** |
| `1 ≤ ATPQty` | `AvailToPromise[ATP In Stock_2]` | Alternative in-stock threshold: any ATP > 0 = in stock | **No** — no label distinguishing this from ATP In Stock |
| **`(ATPWeek1 + ATPWeek2 + In Stock Week3) / 3`** | `ATPInvItemLocation[AvgAvail3Wks]` | **BUG** — numerator mixes ATPQty (Week1, Week2) with a binary flag `In Stock Week3` (0 or 1), then divides by 3 | ⚠️ **Confirmed bug** — `In Stock Week3` is 0 or 1, not a qty; averaging it with ATPQty produces nonsense |
| WH `"335"` excluded from `Series in Stock Current Week` | `_GeneralMeasures` | Ashton warehouse excluded from current-week series in-stock KPI | **No** — silently excluded; report headline may differ from what 335 planner sees |
| Warehouse exclusions in original SQL: `NOT IN ('55','CNW','C','232')` | Original dataflow SQL | Demand history excludes wholesale + specific warehouses from AvgQty | **No** |
| `MIN(spdWeekEnding) FROM SupplyPlanDetailCurrentDay` | Original SafetyStock SQL | Safety stock pulled for the earliest week in the current supply plan run | **No** — could differ from "current week" if the plan run spans multiple weeks |
| `AVERAGEX('ATP Summary', 'ATP Summary'[SeriesInStock%])` | `ATP Summary` measures `Series in Stock % - Wk1` etc. | Average of binary (0/1) series-in-stock flags = fraction of series in stock — effectively correct but using AVERAGEX of binary column | Medium risk — at large scale, same result as COUNT-based %; but numerically fragile if nulls exist |

---

## 10. Comparability / Consistency

1. **Three different "in stock" definitions coexist:**
   - Historical (`InventoryHistory[SKU In Stock]`): defined in dataflow SQL (opaque — likely `OnHandQty > 0` or `≥ AvgQty`)
   - ATP current (`AvailToPromise[ATP In Stock]`): `AvgQty ≤ ATPQty`
   - ATP alternative (`AvailToPromise[ATP In Stock_2]`): `1 ≤ ATPQty` (any stock at all)
   Historical in-stock % and forward ATP in-stock % are **not methodologically comparable** unless the dataflow threshold matches the ATP threshold. A series may show 90% in-stock historically but that 90% was computed differently than the Week1 ATP in-stock %.

2. **`Series In Stock %` vs. `Series in Stock % - Wk1` are not the same metric.**
   `Series In Stock %` (from `_GeneralMeasures`) comes from `SeriesInvHist` (InventoryHistory-based, historical).
   `Series in Stock % - Wk1` (from `ATP Summary`) comes from `ATP Summary` (AvailToPromise-based, forward-looking).
   The same visual label could represent two completely different data flows depending on which table's measure is used.

3. **`AvgAvail3Wks` in `ATPInvItemLocation` is numerically wrong.** Expression: `(ATPWeek1 + ATPWeek2 + In Stock Week3) / 3`. `In Stock Week3` is a binary (0 or 1) flag, not a quantity. Adding 0 or 1 to two ATP quantities and dividing by 3 is dimensionally incorrect. The resulting `In Stock AvgAvail3Wks = IF(AvgQty ≤ AvgAvail3Wks, 1, 0)` will produce incorrect in-stock flags for Week 3 items. This is a confirmed data quality bug.

4. **ATP snapshot date vs. InventoryHistory week date may not align.** `AvailToPromise` uses `RunDate` (when the ATP run was executed) and `WeekEnding` (the fiscal week the ATP covers). `InventoryHistory` uses `Week Ending`. If the ATP run date is Tuesday and the inventory history week ends Sunday, comparing the two in `ATPInvItemLocation` (which uses `TODAY()`) may join across mismatched temporal boundaries.

5. **`SafetyStock` is for the current supply plan week; `InventoryHistory` covers 13 historical weeks.** The `SafetyStock[On Hand Qty]` calculated column does a FILTER join back to `InventoryHistory` to find the matching week's on-hand — if `SafetyStock[WeekEnding]` doesn't match any `InventoryHistory[Week Ending]` exactly, the lookup returns BLANK, silently showing 0 on-hand gap.

---

## Closing — Interview Seeds

1. **"When you say a series is 'in stock,' does that mean every single SKU in the series has inventory, or is there a tolerance — like it's okay if one small-volume accessory SKU is missing? And do you know the model currently uses a 5% demand-share threshold to exclude small-volume items from the series count?"**
   *(Targets: user awareness of the SeriesProp=0.05 threshold; whether the business definition of "complete series" matches the model's definition; whether the threshold should be configurable.)*

2. **"The report shows in-stock % for the past 13 weeks and ATP coverage for the next 6 weeks. When a series drops out of stock in Week 3 ATP, what action do you take — and do you have to go to a different system to expedite the specific PO, or can you do that from here?"**
   *(Targets: trigger-to-action gap; tool handoff to Logility or ERP; whether the 6-week ATP horizon is the right window for the decision cadence.)*

3. **"The Week 3 '3-week average availability' column — do you use it? Do you trust it? We found it's mixing a quantity and a binary flag (0/1) in the formula, which means the numbers in that column are likely wrong."**
   *(Targets: surface the AvgAvail3Wks bug; confirm whether users rely on this column for decisions; assess impact.)*

4. **"Is the series in-stock % on the historical trend view (last 13 weeks) using the same definition as the forward ATP in-stock % (Week 1–6)? Or are they measured differently — and does it matter for how you interpret the trend?"**
   *(Targets: user awareness of the three different "in stock" definitions; whether mixed definitions cause misread trends in WBR presentations.)*

---

*Analysis based on BIM definition extracted 2026-07-08. No bundle indexes were modified.*
