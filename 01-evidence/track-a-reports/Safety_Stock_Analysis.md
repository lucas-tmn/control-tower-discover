# Safety Stock Analysis — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `e68d696f-3e03-4295-95ea-027c51c13ebf`  
**Report ID:** `e913ccfe-58fd-4e83-a532-2a46c1980a01`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~2.04 MB (BIM); 23 tables, 73 measures in `_Measures` + 7 in `_MeasuresIO`

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "For every item × warehouse, is on-hand inventory within its safety stock target band — and how does that band compare to what Logility's Global Forecasting (GF) optimization engine is suggesting as the mathematically optimal safety stock?"

**Primary chain links served:** **Inventory** + **Supply** (Make/Buy planning)  
This is the most complex model in the family. It combines four distinct views:

1. **InvHist** — weekly inventory position (actual on-hand) vs. safety stock target band (Min SS, SS Target, Max SS) for the past 6 weeks and next 9 weeks (using supply plan projected inventory)
2. **GFIO** — Logility Global Forecasting IO optimization output: suggested SS qty and days-of-supply (DOS), constrained upper/lower limits
3. **InvTurns** — rolling 36-month inventory turns calculation at standard cost
4. **InvGoal** — forward 12-month goal inventory investment = SS × standard cost × forward forecast

Secondary links: **Production** (MOQ, Production Resource), **Receipts** (build quantity), **Forecast** (forecast as input to SS calculation)

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Accept / reject Logility GF SS recommendation** — compare `Suggested Qty` (GF engine) vs `Target Qty` (current Logility SS) vs `OH Qty (TW)` — decide whether to apply the suggested change | Inventory Planner | Monthly (SS review cycle) | Performance/Governance |
| **Identify Over/Under items and action** — `% Over (TW)`, `% Under (TW)`, `Overage Qty (TW)`, `OH Qty (TW)` by item × WH; planners decide to expedite (Under) or defer receipts (Over) | Inventory Planner | Weekly | Operational |
| **Calculate excess inventory dollar impact** — `$ Overage (Cost)`, `$ Overage (FOB)`, `$ Inv Investment` show financial cost of inventory outside the SS band | WBR-Leadership / Finance | Weekly / monthly | Financial-Justification |
| **Set MOQ-adjusted SS for Make items** — `Max SS` recalculated when MOQ > Max SS for 'M' (Make) items; planner reviews MOQ-driven SS override | Supply Planner | Monthly | Operational |
| **Review inventory turns by item / warehouse** — `InvTurns` provides 36-month rolling turns (COGS ÷ avg inventory at cost) | Inventory Analyst / Finance | Monthly / quarterly | Performance/Governance |
| **Assess goal inventory investment for next 12 months** — `InvGoal` shows target SS × cost × forward COGS; feeds budget / capital planning | Finance / Supply Chain VP | Monthly | Financial-Justification |
| **Identify items with short lifecycle approaching drop** — `Count Of PD w/i 12Mo`, `Count Of PD w/i 24Mo`, `z_LifeCycle`, `z_LifeCycleCat` flag items close to end-of-life for de-stocking | Category Analyst / Planner | Monthly | Operational |
| **Review J-flag (slow-moving) item SS adjustment** — `J Flag`, `JAltMax`, `JAltChange` on GFIO identify ABC=J items where DOS > 28 days; cap their SS to 28-day equivalent | Inventory Planner / Analyst | Monthly | Performance/Governance |
| **Weekly SS change tracking** — `SS Qty This Week` vs `SS Qty Last Week` (`SS Qty Change`) detects system-driven SS changes for planner awareness | Planner | Weekly | Performance/Governance |

---

## 3. Key Metrics / Measures

### On-Hand vs. Safety Stock Band

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `OH Qty` | On-hand qty in control band (capped at Max SS for Over items) | Item × WH × fiscal week | `SUM(InvHist[CntrlQty])` — calc col: `IF(Inv Qty<0,0, SWITCH(Inv Status, "In Control"→Inv Qty, "Under"→Inv Qty, "Over"→Max SS))` |
| `Overage Qty` | Units above Max SS | Item × WH × fiscal week | `SUM(InvHist[OverQty])` — calc col: `IF("Over", Inv Qty - Max SS, 0)` |
| `OH/SI Qty` | All positive inventory (on-hand + projected SI) | Item × WH × fiscal week | `SUM(InvHist[SIPosQty])` = `MAX(0, Inv Qty)` — includes negative-zeroed values |
| `Opt Qty` | SS Target (the center of the band) | Item × WH × fiscal week | `SUM(InvHist[SS Target])` = `dinSafetyStock` from Logility |
| `Opt Min Qty` | Lower bound of SS band | Item × WH | `SUM(InvHist[Min SS])` = `SS Target × 0.5` — **hardcoded 50% factor** |
| `Opt Max Qty` | Upper bound of SS band | Item × WH | `SUM(InvHist[Max SS])` = `SS Target × 1.5` with MOQ override for Make items |
| `Over SS Qty` | Units above SS Target (not Max SS) | Item × WH | `SUM(InvHist[OverSS])` = `MAX(0, Inv Qty - SS Target)` — different from Overage Qty |
| `Qty Over SS` | Measure-level version of same | Item × WH | `MAX(0, SUM(Inv Qty) - SUM(SS Target))` |
| `Build Qty` | Planned build/production quantity | Item × WH | `SUM(InvHist[Build Qty])` = `dinBuildQuantity` |
| `Build+SS Qty` | SS + Build combined target | Item × WH | `SUM(InvHist[SS + Build])` |
| `% In Control / Over / Under` | % of item-WH combinations in each status | Item × WH | `COUNT(InvHist[Item SKU]) where Inv Status = X / COUNT(all)` |
| `% In Control (TW)` | Current-week % in control | Current week only | Same, filtered `FiscalWeekIndicator = 0` |

### Dollar Measures

| Measure | Business meaning | Source / Logic |
|---|---|---|
| `$ Inventory` / `FOB $` | Total inventory at FOB price | `SUM(InvHist[$ Inv])` = `Inv Qty × CPD.FOB Price` (from SQL) |
| `$ OH` | In-control inventory at FOB | `SUM(InvHist[Cntrl$])` = `CntrlQty × RELATED(z_ProductDetails[FOB Price])` |
| `$ Overage (Cost)` | Overage at standard cost | `SUM(InvHist[Over$(Cost)])` = `OverQty × RELATED(z_CostDefault[CostDefault])` |
| `$ Overage (FOB)` | Overage at FOB price | `SUM(InvHist[Over$(FOB)])` = `OverQty × RELATED(z_ProductDetails[FOB Price])` |
| `$ Inv Investment` | All inventory at standard cost | `SUM(InvHist[InvInvestment$])` = `Inv Qty × z_CostDefault[CostDefault]` |
| `OH $` | On-hand at FOB | `PRODUCTX(z_ProductDetails, FOB Price × [OH Qty])` — **uses PRODUCTX not SUMX; equivalent here but unusual** |

**Note:** `$ Overage` is available at both cost (standard cost from `z_CostDefault`) and FOB — allowing comparison of economic vs. transfer-price excess.

### GF IO Optimization Measures

| Measure | Business meaning | Grain | Source |
|---|---|---|---|
| `Target Qty` | Current Logility SS (from DemandInventorySnapshot) | Item × WH × current month | `SUM(GFIO[dinSafetyStock])` filtered to `FiscalMonthIndicator=0` |
| `Suggested Qty` | GF engine's statistically optimal SS | Item × WH × current month | `SUM(GFIO[SS Qty Suggested])` = `SafetyStockLevelCalculated` (ceiling) |
| `Target DOS` | Current SS in days-of-supply | Item × WH | `Target Qty / DailyAvg` |
| `Suggested DOS` | Suggested SS in days-of-supply | Item × WH | `Suggested Qty / DailyAvg` |
| `Total DOS (TW)` | Current week total inventory in DOS | Item × WH | `(OH Qty(TW) + Overage Qty(TW)) / DailyAvg` |
| `Total DOS (W9)` | Week 9 forward inventory in DOS | Item × WH | Same formula, `FiscalWeekIndicator=9` |
| `Daily Avg` | Implied daily demand from GF settings | Item × WH | `SUM(GFIO[DailyAvg])` = `SS Qty Selected / SS DOS Constrained` — **derived demand rate, not actual demand** |
| `GF SS Qty Suggested` | Raw GF suggested qty (in _MeasuresIO) | Item × WH | `SUM(GFIO[SS Qty Suggested])` — same as `Suggested Qty` but from separate measure table |
| `GF SS Qty Constrained` | Selected/applied SS from GF | Item × WH | `SUM(GFIO[SS Qty Selected])` = `SafetyStockLevel` (ceiling) |
| `GF SS DOS` | Constrained SS in DOS from GF | Item × WH | `SUM(SS Qty Selected) / SUM(DailyAvg)` |
| `DP SS Qty Suggested` / `DP SS Qty Constrained` / `DP WOS` / `DP SS DOS` | **BROKEN — reference `DPIO` table** | N/A | `DPIO` table does not exist in model |

### Inventory Turns (InvTurns)

| Source column | Meaning |
|---|---|
| `Avg Std Cost` | Weighted average standard cost per month |
| `COGS - STD Cost` | Monthly COGS at standard cost |
| `12mo COGS - STD Cost` | Rolling 12-month COGS (window function) |
| `Adj Roll COGS` | `12mo COGS / (PeriodCount / 12)` — annualised COGS adjusted for periods with data |
| `Avg OH Qty` / `Avg Inv Dollars` | Average on-hand qty and $ for the month |
| `PeriodCount` | Number of months with data in the rolling 12-month window |

No DAX measures directly reference `InvTurns` columns — it appears to be used in visuals directly or via implicit aggregation.

### z_ProductDetails Lifecycle / Classification Columns

| Column | Logic | Notes |
|---|---|---|
| `z_LifeCycle` | Maps to: `Disco`, `Scrap`, `PlanDrop`, `Recent Launch` (Qtr4 2024–Qtr4 2025 hardcoded), `Current`, `n/a` | **⚠️ "Recent Launch" quarters hardcoded to 5 specific quarters** |
| `z_LifeCycleCat` | Broader: `PLANNED/DROPS`, `RECENT LAUNCH` (QTR4 2024–QTR4 2025 + ItemStatus=N), `CURRENT`, `n/a` | Same hardcoding issue; uses `Market Introduced At` (string field) |
| `DropIn12Mo` | `(PlanDropDecisionDate - Market Begin Date) <= 365` | **⚠️ Logic error: measures total lifecycle length, not "drops within 12 months of today"** |
| `DropIn18Mo` | `(PlanDropDecisionDate - Market Begin Date) <= 547` | Same logic flaw |
| `DropIn24Mo` | `(PlanDropDecisionDate - Market Begin Date) <= 730` | Same logic flaw |
| `z_OvStock` | Hardcoded list of 10 series numbers → `'Y'` | **⚠️ Hardcoded overstock flag for specific series** |
| `z_KitFlag` | Classifies kits: `Bedding Kit`, `UPH Kit`, `Swatch`, `HIDES`, `VINYL`, `CARD`, `""` | Based on item suffix and class code |
| `z_LeatherFlag` | 12 leather item class codes → `LTHR FG` or `LTHR UN` | |
| `PartFlag` | 32 item class codes → `'PART'`; also `General Description Code = 240` | Broader part definition than inventory txn model |
| `Coll Class` / `Finance Division` | Local re-mappings of item class codes to component/kit categories | Near-identical twin columns with different label styles |
| `Storage Type` / `Storage Type L2` | Same as Inventory Transactions model | Consistent definition across models |
| `Company OH` / `Company SS` / `Company MIN` / `Company Max` | Current-week totals aggregated to product level | Calculated columns calling measures — performance risk |
| `Company Inv Status` | `IF(OH < MIN, "Under", IF(OH > Max, "Over", "In Control"))` | Company-wide status (all warehouses combined) |
| `Company Inv Status Wk20` | Same logic but at `FiscalWeekIndicator = 20` | **Hardcoded week 20 — why?** |
| `SCP Bus Unit` | 60+ item class codes mapped to SCP business units | Very long SWITCH; any new class code will fall through to `CONCATENATE("D-", Collective Class)` |
| `Bed Pieces` | Classifies bedroom items by description substring search (HEADBOARD/FOOTBOARD/RAIL etc.) | `FIND()` on description string — brittle; typo in description can mismatch |

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `InvHist` | `SupplyChain_Enh.DemandInventorySnapshot` (DIN), `Wholesale_DemandPlanning_AFI.SupplyPlanDetail` (SPD), `Wholesale_DemandPlanning_AFI.PlannedRequirementsLogility` (PRQ), `SupplyChain_Enh.ProductionResourcePlan` (PRP), `SupplyChain_DW.DimCurrentProductDetails` (CPD), `MasterData_ItemMaster_AFI.ITBEXT` | **Most complex query** — UNION of past (DIN actual OH, past 6 fiscal weeks) and future (SPD projected inventory, weeks 0–9 forward). Declares `@SSFactor = 0.5`. 1-hour timeout. |
| Same EDW | `GFIO` | `SupplyChain_Enh.IOExportedItemOutputsSnapshot` (OPT) joined to DIN | Logility GF optimization output — latest snapshot; next 6 months only; **16 warehouses allowlisted** |
| Same EDW | `InvTurns` | `Inventory_Enh_History.MonthEndItemRevision` (std cost), `AFISales_DW.FactShippedHistory` (sales), `AFISales_DW.FactQualityCosts` (quality credits), `Inventory_Enh_History.ItemBalance` (on-hand), `PowerBI_SupplyChain.WarehouseMaster` | Complex multi-temp-table SQL with 4 `#temp` tables and explicit `DROP TABLE`; 36-month lookback. Unique to this model. |
| Same EDW | `InvGoal` | `SupplyChain_Enh.DemandForecastSnapshot`, `SupplyChain_Enh.DemandInventorySnapshot`, `MasterData_ItemMaster_AFI.ITMRVB` (standard cost) | Forward 12-month SS × cost × forecast |
| Same EDW | `z_ItemWHMaster` | `SupplyChain_Enh.DemandInventorySnapshot`, `MasterData_ItemMaster_AFI.ITBEXT`, `SupplyChain_Enh.ForecastCommonContainer_Logility` | Item × WH master with avg weekly forecast (13-week rolling) |
| Same EDW | `z_MattKitType` | `Manufacturing_DW.DimBOMDetails`, `SupplyChain_DW.DimCurrentProductDetails` | Mattress kit BOM lookup — classifies mattress kit components |
| Same EDW | `z_KitMkt` | `SupplyChain_DW.DimCurrentProductDetails` | Kit market-introduction dates from parent series |
| Same EDW | `z_CostDefault` | `MasterData_ItemMaster_AFI.ITEMASA` (standard cost), `SupplyChain_Enh.DemandFulfillmentCommonContainer_Logility` (plan drop date) | Item-level standard cost + planned drop decision date |

### Power BI Dataflows (semi-governed)

| Dataflow | Tables | Notes |
|---|---|---|
| `a47e4573` workspace / `346f2aa1` dataflow | `z_ProductDetails`, `z_FiscalCal`, `z_WarehouseMaster`, `z_VendorMaster` | Same shared conformed layer as all other SC models |

**No SharePoint / Excel sources** — fully EDW + dataflow sourced, like the Inventory Transactions model.

---

## 5. Grain & Snapshot Strategy

**Primary grains:**
- `InvHist`: Item × WH × Fiscal Week — dual-mode: **past 6 fiscal weeks** use actual on-hand (`DIN.dinOnHandQuantity`); **current + forward 9 weeks** use supply plan projected inventory (`SPD.spdShippableInventory`)
- `GFIO`: Item × WH × Fiscal Period (monthly) — latest GF snapshot only; forward 6 months
- `InvTurns`: Item × WH × Fiscal Month — rolling 36-month history
- `InvGoal`: Item × WH — aggregated (no date dimension; single-row per item × WH)

**Snapshot strategy:** Mixed:
- `InvHist` is **dual-mode snapshot**: historical actual + current forward projection (UNION). The past branch uses `DIN.dtea <= most recent snapshot AND FiscalMonthIndicator >= -6 AND FiscalWeekIndicator < 0`; the forward branch uses `latest DIN snapshot + SupplyPlanDetail latest snapshot`.
- `GFIO` is **latest-only** (single max snapshot)
- `InvTurns` is **accumulative history** (36 months, temp tables, window functions)
- `InvGoal` is **forward-looking** (next 12 months) using latest snapshots

The UNION structure in `InvHist` is the critical architectural decision — it allows a single time axis showing both where inventory has been and where it is projected to go.

---

## 6. Dimensions Used

| Dimension | Source | Local re-derivations / drift risks |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow) | **Most locally enriched of any model** — 25+ calculated columns. Key local ones: `z_LifeCycle`, `z_LifeCycleCat`, `PartFlag`, `z_KitFlag`, `z_LeatherFlag`, `Coll Class`, `Finance Division`, `SCP Bus Unit`, `Company OH/SS/MIN/Max`, `Company Inv Status`, `Company Inv Status Wk20`, `Bed Pieces`, `z_OvStock`, `z_MakeItem`, `z_BuyItem`, `z_Make&Buy`, `z_MattKitType`, `KitMarket`, `PlanDropDecisionDate`, `DropIn12Mo/18Mo/24Mo`. None of these are in the shared dataflow. |
| **Date** | `z_FiscalCal` (dataflow) | `FiscalWeekIndicator` is the key for TW/W9/LW filters. `FiscalMonthIndicator = 0` used to filter GFIO current-month measures. |
| **Warehouse** | `z_WarehouseMaster` (dataflow) | Standard conformed dimension |
| **Vendor** | `z_VendorMaster` (dataflow) | Present; likely used for Make/Buy source display |
| **Item × WH bridge** | `z_ItemWHMaster` (EDW) | Acts as a conformed bridge entity connecting `InvHist` and `GFIO` to `z_ProductDetails` via `Item_WH` composite key. Carries `MBX` (Make/Buy), `IP ABC`, `PickPut`, `Avg Wkly Fcast`. |
| **Cost** | `z_CostDefault` (EDW) | Item-level standard cost + plan drop date. Used for cost-basis dollar measures (`$ Overage (Cost)`, `InvInvestment$`, `ExcessBuild$`). Two relationships to `z_CostDefault`: from `InvTurns`, `InvGoal`, `InvHist`, and one inactive from `z_KitMkt`. |
| **Mattress Kit Type** | `z_MattKitType` (EDW BOM) | Classifies mattress kit components (Spring/Foam); linked to `z_ProductDetails` via `LOOKUPVALUE`. |
| **Kit Market** | `z_KitMkt` (EDW) | Kit market-introduction dates; linked to `z_ProductDetails`; used in `z_LifeCycle` "Recent Launch" logic. |

---

## 7. Duplication / Consolidation Signals

1. **`Count Of PD w/i 12Mo` and `Count Of PD w/i 18Mo` are identical — both sum `DropIn12Mo`:**  
   ```dax
   Count Of PD w/i 12Mo = CALCULATE(SUM(z_ProductDetails[DropIn12Mo]))
   Count Of PD w/i 18Mo = CALCULATE(SUM(z_ProductDetails[DropIn12Mo]))  -- should be DropIn18Mo
   ```
   `Count Of PD w/i 18Mo` references the 12-month column by mistake. The 18-month count equals the 12-month count, making both measures indistinguishable.

2. **`Coll Class` and `Finance Division` columns — twin SWITCH tables:**  
   Both map the same 14 item class codes (WVBC, WVHC, ZARP, USKE, etc.) and then fall through to a nested SWITCH for kit classification. `Coll Class` uses uppercase labels (`"BEDDING COMPONENTS"`); `Finance Division` uses mixed case (`"Bedding Components"`). Same logic, two names, minor label divergence — should be one column.

3. **`Over SS Qty` and `Qty Over SS` measure the same thing differently:**  
   - `Over SS Qty = SUM(InvHist[OverSS])` where `OverSS = MAX(0, Inv Qty - SS Target)` (row-level)  
   - `Qty Over SS = MAX(0, SUM(Inv Qty) - SUM(SS Target))` (aggregate-level)  
   These will differ when aggregating across multiple items — row-level summing vs. aggregate subtraction. Neither is documented as the "correct" one.

4. **`$ Inventory` and `FOB $` are identical measures:**  
   Both return `CALCULATE(SUM(InvHist[$ Inv]))`. Two names for the same value.

5. **`OH $` uses `PRODUCTX` instead of `SUMX`:**  
   `PRODUCTX(z_ProductDetails, FOB Price × [OH Qty])` — `PRODUCTX` is the _product_ (multiplication) iterator, not sum. In this case it multiplies `(FOB Price × [OH Qty])` across rows of `z_ProductDetails` and sums the results — equivalent to `SUMX` for a product calculation. However, `PRODUCTX` semantics are unusual here and if the expression ever changes to include more than one term, the behaviour would differ from `SUMX`. Should be `SUMX`.

6. **`GF SS Qty Suggested` (in `_MeasuresIO`) duplicates `Suggested Qty` (in `_Measures`):**  
   Both return `SUM(GFIO[SS Qty Suggested])`. Two measures in two measure tables with the same expression.

7. **`_Measures` and `_MeasuresIO` — two measure tables:**  
   The IO-specific measures are separated into `_MeasuresIO` but their content partially duplicates `_Measures`. The DP (Demand Planning) measures in `_MeasuresIO` reference `DPIO` which doesn't exist — the split creates dead code in one table.

8. **`z_LifeCycle` vs `z_LifeCycleCat` — two lifecycle columns with overlapping purpose:**  
   Both classify items into lifecycle categories. `z_LifeCycle` is granular (Disco/Scrap/PlanDrop/Recent Launch/Current); `z_LifeCycleCat` is coarser (PLANNED/DROPS/RECENT LAUNCH/CURRENT). They use different source fields for "Recent Launch" (`KitMarket` vs `Market Introduced At`), so the same item can have different lifecycle labels in the two columns.

---

## 8. Open Questions

1. **What are `z_CoVRanges`, `ChinaPRoduct`, and `DPIO` tables?** All three are referenced in the model (measures or calculated columns) but **do not exist** as tables. Any visual or measure using `BucketsVariability`, `zChinaSKUs`, or the four DP IO measures returns an error or BLANK.

2. **What does `Inv Status2` represent?** The column exists in `InvHist` (referenced 3 times) but its expression is not visible from source — it appears to be another status column not used in any visible measure. Is it a legacy field?

3. **Why is `Company Inv Status Wk20` hardcoded to week 20?** Week 20 (~5 months forward) seems like a specific planning horizon. Is this tied to a seasonal peak? Container lead-time? It is not documented and will produce misleading results for users who don't know the reference week.

4. **Is `DATEADD(DAY, 15, OPT.DtuDate)` in GFIO the right snapshot alignment?** The GFIO table shifts `DtuDate` by 15 days to get `FiscalPeriod`. The join to DIN also uses `DATEADD(DAY, 14, OPT.DtuDate)` (different offset) to match DIN's fiscal month. Two different offsets in the same query for the same purpose — are these intentional?

5. **Why does `InvGoal` use `AVG(dinSafetyStock)` across 12 months?** Averaging SS across the forward 12 months smooths out seasonal SS variation. Is the goal an average SS investment or the peak SS investment? The answer changes the capital requirement estimate significantly.

6. **`InvTurns` uses `@Periods = -36` (36 months) but the final WHERE clause returns only `FiscalMonthIndicator BETWEEN (@Periods+12) AND -1`** = months -24 to -1. The 36 months of history are computed but only the most recent 24 months are returned. Was 36 chosen as a lookback to have enough data for the 12-month rolling window at the start of the 24-month output range, or is 36 months the intended output?

7. **Who maintains `z_OvStock`?** Ten series numbers are hardcoded as "overstock" items. Is this a one-time flag from an S&OP meeting that was never removed? If those series have been discontinued, the flag persists indefinitely.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `@SSFactor = 0.5` | `InvHist` SQL | Defines SS band width: Min SS = SS × 0.5, Max SS = SS × 1.5 (±50% around target) | **Partially** — variable declared at top of SQL with no business rationale. No explanation of why 50%. |
| `28` days DOS cap | `GFIO[JAltMax]` calc column | J-class (slow-moving) items: if GF recommends DOS > 28, cap at 28 days | **No** — magic number. Presumably a policy that slow-moving items should not hold more than ~1 month of supply. |
| `DATEADD(DAY, 15, DtuDate)` | GFIO SQL | Shifts GF output date by 15 days to align to fiscal period | **No** — same `day+15` convention used in accuracy models for cycle snapshot. Inconsistently, a `day+14` offset is also used in the DIN join within the same query. |
| `FiscalMonthIndicator BETWEEN 0 AND 11` | `InvGoal` SQL | Forward 12 months for goal inventory | **No comment** |
| `FiscalMonthIndicator >= -6 AND FiscalWeekIndicator < 0` | Past branch of `InvHist` | Past 6 fiscal months of actual on-hand | **No comment** — why 6 months? Other models use 12 or 18. |
| `FiscalMonthIndicator < 9 AND FiscalWeekIndicator >= 0` | Forward branch of `InvHist` | Forward 9 fiscal months using supply plan | **No comment** — 9-month forward horizon. Why not 12? |
| Hardcoded quarters `"QTR 4 2024"` through `"QTR 4 2025"` | `z_LifeCycle`, `z_LifeCycleCat` | Defines "Recent Launch" window | **No** — as of July 2026, QTR 4 2024–QTR 4 2025 is 6–18 months ago. QTR 1 2026 onwards is NOT in scope, so items launching in 2026 are classified as "Current" or "n/a" rather than "Recent Launch". This is stale. |
| Hardcoded series list (`90703`, `59301`, etc.) | `z_OvStock` | Marks 10 specific series as overstock | **No** — no date, no owner, no expiry. |
| `/ 13` in `Avg Wkly Fcast` | `z_ItemWHMaster` SQL | Divides 6 forecast columns by 13 | **No** — presumably 13 weeks (~quarter). Mixes 6 result columns (3 promo + 3 base) and divides by a time horizon. Unclear if this is a 13-week average or something else. |
| `@Periods = -36` | `InvTurns` SQL | Sets 36-month history lookback | **Commented** as "Inventory Turns" but no rationale for 36 months |
| `LEFT([MEIR].[ChargeNature], 3) = '159'` | `InvTurns` SQL | Filters standard cost to charge nature starting with 159 | **No** — freight class 159xx filter for standard cost records. Same pattern as Item Balance model (`FRTNAT BETWEEN 15900–15999`). |
| `[CPD].[ItemClassCode] NOT LIKE 'Z__K'` and multiple exclusions | `InvTurns` SQL | Excludes kit items, SW, CARD, HIDES, VINYL, UN suffix items from turns | **No comment** — permanent exclusions hardcoded in SQL; if new kit class codes are created, they pass through unless the pattern is updated |
| `STID = '000'` | `InvGoal` SQL (ITMRVB join) | Standard cost site identifier | **No comment** — site '000' = corporate standard cost. |

**Dollar-value business impact — multiple paths:**  

This is the most financially loaded model in the family:

1. **`$ Overage (Cost)`** = `OverQty × Standard Cost` — monthly/weekly excess inventory at cost. This IS used in executive reporting (over-inventory $ at cost is a direct cash metric).
2. **`$ Inv Investment`** = `Inv Qty × Standard Cost` — total inventory value at cost. High-risk if `z_CostDefault[CostDefault]` is stale or missing for any item.
3. **`InvGoal[Goal Inv Cost]`** = `avg SS × standard cost` — used to set forward 12-month inventory investment target. Feeds capital budget.
4. **`InvTurns[Adj Roll COGS]`** = `12mo COGS / (PeriodCount/12)` — annualised COGS. Used in turns formula `Adj Roll COGS / Avg Inv Dollars`. This is a sophisticated calculation; the `PeriodCount` adjustment is important for new items (denominator < 1 year of data would otherwise inflate turns).

All four paths rest on `z_CostDefault[CostDefault]` = `ITEMASA.UCDEF` (cost default from iSeries item master). If this field is zero, NULL, or outdated for any item, every cost-based dollar measure for that item is wrong.

---

## 10. Comparability / Consistency Issues

### a. `DropIn12Mo`, `DropIn18Mo`, `DropIn24Mo` — wrong formula

All three columns compute `PlanDropDecisionDate - Market Begin Date` (total lifecycle length) and compare to a duration threshold. The intended meaning is "this item is planned to drop within N months **from today**". The correct formula would be `PlanDropDecisionDate - TODAY() <= N_days`.

As written:
- An item that launched Jan 2020 and dropped Mar 2020 (73-day lifecycle) → `DropIn12Mo = TRUE` forever, even though it dropped 6 years ago
- An item launching today and planned to drop in 18 months → `DropIn18Mo = FALSE` (547 days lifecycle > 365 threshold for 12Mo, > 547 for 18Mo...)

Wait — for a new item with 18-month lifecycle: `PlanDropDate - MarketBeginDate = 547 days`. `DropIn18Mo = (547 <= 547) = TRUE`. So it would be TRUE. But the semantics are wrong: the "18Mo" label implies "dropping in the next 18 months" which is a time-from-now concept. The formula doesn't use today's date at all.

**Additionally:** `Count Of PD w/i 18Mo` uses `DropIn12Mo` not `DropIn18Mo` — so the 18-month count equals the 12-month count regardless.

### b. `Over SS Qty` vs `Overage Qty` — different SS reference levels

- `OverQty` / `Overage Qty` = inventory above **Max SS** (SS × 1.5)
- `OverSS` / `Over SS Qty` = inventory above **SS Target** (the center)

Both are shown in the report. An item can be "Over SS" but still "In Control" if inventory is between SS Target and Max SS. A user comparing these two numbers will see dramatically different values without understanding the threshold difference.

### c. `DailyAvg` is derived demand (from SS settings), not actual demand

`GFIO[DailyAvg] = SS Qty Selected / SS DOS Constrained`

This is an **implied** daily demand rate calculated backward from GF SS settings, not measured from actual order history. When used as denominator in `Total DOS (TW)`, the result is "how many days of GF-implied demand does current inventory cover" — not "how many days of actual historical demand". If GF has a stale service level or demand estimate, `DailyAvg` is wrong and all DOS measures are wrong. This is not flagged anywhere in the model.

### d. Past vs. forward `InvHist` use different inventory definitions

- **Past branch** (FiscalWeekIndicator < 0): `Inv Qty = dinOnHandQuantity` — actual Logility on-hand
- **Forward branch** (FiscalWeekIndicator ≥ 0): `Inv Qty = spdShippableInventory` — supply plan projected shippable inventory

These are different inventory definitions. On-hand includes items physically in the warehouse; shippable inventory is a planning calculation that may include receipts not yet arrived. A trend line spanning the current-week boundary (Week -1 to Week 0) crosses from one inventory definition to the other, producing a non-comparable step change that looks like a movement but is a definition shift.

### e. Two lifecycle columns use different source fields for "Recent Launch"

| Column | "Recent Launch" source |
|---|---|
| `z_LifeCycle` | `KitMarket` (from `z_KitMkt` — kit items only; based on parent series market intro) |
| `z_LifeCycleCat` | `Market Introduced At` (from `z_ProductDetails` dataflow — all items) |

A kit item might be "Recent Launch" in `z_LifeCycle` (via `KitMarket`) but not in `z_LifeCycleCat` (if its own `Market Introduced At` doesn't match), or vice versa. Filtering by one vs. the other produces different item populations.

### f. `z_LifeCycle` "Recent Launch" quarters are stale as of July 2026

The last hardcoded quarter is `"Qtr 4 2025"` (Oct–Dec 2025). Any item introduced in Q1 2026 or later is classified as `"Current"` instead of `"Recent Launch"`, even if it is only 1–6 months old. The classification has been stale since January 2026.

---

## Closing — Interview Seeds

1. **"The `% Under (TW)` and `% Over (TW)` percentages use the item-count of items outside the SS band. When you see, say, 25% of items Under — do you work from that percentage directly, or do you filter down to specific items and decide per-item? And what makes you prioritize one Under item over another?"**  
   *(Establishes whether the % metric drives action or is just a headline, and what the real operational triage logic is.)*

2. **"The Logility GF system is suggesting a specific safety stock quantity for each item. When the `Suggested Qty` differs from your `Target Qty` — say Logility wants 50 but you're currently holding to 80 — what happens next? Do you just click 'accept' in Logility, or is there a review step, and who approves large changes?"**  
   *(Determines how the GF suggestion flows from this report into Logility — is the report the decision interface or just informational?)*

3. **"There's a column called `DropIn12Mo` that's supposed to count items dropping within the next 12 months. But the formula actually measures total lifecycle length, not time-from-today. So an item that already dropped 3 years ago with a short lifecycle still shows up as TRUE. Is this giving you the right list, or have you noticed mismatches?"**  
   *(Surfaces the logic bug directly — determines whether users trust the output and what they'd expect the correct formula to be.)*

4. **"The inventory dollar measures — `$ Overage (Cost)`, `$ Inv Investment` — rely on the standard cost from the item master (`UCDEF`). How often is that cost updated, and have you ever seen a case where the on-hand dollar value looked obviously wrong because the cost was stale or zero?"**  
   *(Validates the reliability of the cost-based dollar measures that feed executive capital planning.)*
