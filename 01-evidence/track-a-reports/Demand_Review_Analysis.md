# Demand Review — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `57f08670-6adb-4352-a64c-4bed8163a042`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~4.9 MB (BIM); 70 tables, 197 DAX measures in `_Measures`

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "For every item × warehouse × customer segment, are we forecasting the right demand, and are we on track to sell it — this month, this quarter, and the next 12 months?"

**Primary chain link served:** **Demand / Forecast**  
The report sits squarely at the demand-sensing and demand-review step of the S&OP/IBP cycle. It surfaces working forecast vs. prior plan vs. 90-day plan, forecast accuracy (bias + error at 2-week / 30-day / 90-day lag), in-stock ATP, actual order consumption vs. target, safety-stock gap, and placement health — all feeding into a monthly demand review meeting.

Secondary links touched:
- **Inventory** — SI (scheduled inventory), on-hand, SS gap, SI overage, excess FG
- **Receipts** — SupplyPlanDetail net receipts, 8-week average receipt
- **On-time** — In-Stock % from `Week_2_ATP`

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Approve / reject working forecast vs. prior plan** — accept planner's R12 logility number or push back | WBR-Leadership / VP Demand | Monthly (cycle) | Performance/Governance |
| **Flag chronic over/under-forecasting items for planner coaching** — `Chronic Bias Flag` drives the exception list | Supply Chain Manager | Monthly | Performance/Governance |
| **Exception-driven forecast review** — `Exception Flag` fires on: (a) ≥ threshold % R12 change vs. prior plan, or (b) combined high-bias + high-error. Planner reviews and justifies or corrects | Planner | Weekly / monthly | Performance/Governance |
| **Adjust safety stock target** — SI vs SS gap and SI Overage (SI > SS × 1.4) highlight over/under-stocked items | Inventory Planner | Monthly | Operational |
| **Expedite or defer container orders** — `fcst_qty_container` and SI signal for the 0–3 month container pipeline | Supply Planner / Logistics | Monthly | Operational |
| **In-month consumption pace decision** — `consumption_performance_indicator_rate_wrk/cur` shows whether current-month orders are tracking behind/ahead of the historical consumption target; triggers account-team outreach or forecast cut | Demand Planner / Sales | Weekly (in-month) | Operational |
| **RH Bedding forecast sign-off** — `fcst_qty_wrk_rh_adjusted` separates RH drop-ship from core Logility plan; RH team must confirm their submitted Excel file is current | Bedding Category / RH Channel Planner | Monthly | Operational |
| **Placement health & at-risk actions** — `placements_at_risk_cur` vs. `placements_cur` drives re-placement or drop decision | Account Planner | Weekly | Operational |
| **Product lifecycle / drop decision** — `z_drop_dates`, `Current/Future Status` column, and `Product_Journal` feed lifecycle visibility | Category Analyst | Monthly | Performance/Governance |
| **YoY growth attribution** — YTD ACT vs. YTD-1 ACT with lifecycle status grouping used in executive growth narrative | Executive / Finance | Monthly | Financial-Justification |

---

## 3. Key Metrics / Measures

### Forecast Volume

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `fcst_qty_wrk_logility` | Working forecast qty (current cycle Logility snapshot) | Item × WH × Customer Group × fiscal month | `Fcst_Snapshots[Total_Fcst]` filtered where `Forecast_Snapshot = working_forecast_date` |
| `fcst_qty_wrk_r12_logility` | Rolling 12-month working forecast | Item × WH × CG | Above, restricted to `Rolling 12 Month Year = 0` |
| `fcst_qty_prior_logility` | Prior-cycle plan for comparison | Item × WH × CG | `Fcst_Snapshots` filtered to `prior_cycle` snapshot date; **⚠️ contains a hardcoded patch for date 2026-02-16 (see §9)** |
| `fcst_qty_90d_logility` | Plan as of 90 days out | Item × WH × CG | `Fcst_Snapshots` filtered to `90d_plan_date` |
| `fcst_qty_wrk_rh_adjusted` | Working forecast with RH Bedding channel swapped in | Item × WH | Logility (ex-RHCUST) + `RH_FC[Qty]` from SharePoint Excel |
| `fcst_qty_add_promo` | Incremental promotional forecast (months 5–11) | Series/CC × fiscal month | `MAX(Fcst_Average_Promo[Avg_Promo] - fcst_qty_wrk_promo, 0)` — **⚠️ month 5–11 hardcode (see §9)** |
| `fcst_qty_container` | Container pipeline (months 0–3 from EDW; 4–12 from container calc) | CC × fiscal month | Mixed: live orders WH `C/CNW` for months 0–3; `Fcst_Container` seasonality-calc for months 4–12 |
| `fcst_qty_wrk_all` | Total working plan = Logility + container + additive promo + RH DS | Item × WH | Sum of four component measures |

### Forecast Change

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Baseline Plan Change` | R12 Logility non-promo shift vs. prior plan | Item | `fcst_qty_wrk_r12_logility_nonPromo - fcst_qty_prior_r12_logility_nonPromo` |
| `fcst_change_%_r12_wrk_v_prior_logility` | % R12 change vs. prior Logility plan | Item | `DIVIDE(change_qty, fcst_qty_prior_r12_logility)` |
| `fcst_change_%_r12_wrk_v_90d_logility` | % change vs. 90-day plan | Item | Same pattern against 90d snapshot |

### Forecast Accuracy (lagged)

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `FC Bias - 90d` | Over/under bias at 90-day lag (rolling) | Item × WH × CG | `DIVIDE(Total Forecast - Actual Demand, Actual Demand)` from `Fcst_Accuracy_Cust_It_Wh` where `ForecastPeriod = "90Days"` |
| `FC Bias - 30d` | Same at 30-day lag | Item × WH × CG | Same source, `ForecastPeriod = "30Days"` |
| `FC Bias - 2wk` | 2-week lag bias | Item × WH × CG | `ForecastPeriod = "2Week"` |
| `FC Error - 30d` | Raw absolute error (Fcst − Act) at 30 days | Item × WH × CG | Not %-normalised — raw qty difference |
| `Chronic Bias Flag` | Automated label: Pre-Launch / Chronic Over / Under / blank | Item × CG | 90d bias > 25% **AND** 30d bias > 20% **AND** consumption gap rate > 15% simultaneously — **⚠️ three thresholds, none documented (see §9)** |
| `Exception Flag` | 1/0 exception trigger used to surface items for review | Item | `abs(R12 % change) > threshold OR (bias + error both > thresholds)` — driven by `Parameter_Fcst_Change_Threshold`, `Bias Threshold`, and `Parameter` slicer tables |
| `LM 90d Abs It Error` | Item-level absolute error, last month, 90d lag | Item | `SUMX(SUMMARIZE(...),...ABS(ItemFcst-ItemDemand)...)` — rolled up item, not cust-item |
| `LM Abs It Err %` | % version | Item | `LM 90d Abs It Error / ItWHAccy[Actual Demand]` — **⚠️ denominator references `ItWHAccy`, numerator uses `Fcst_Accuracy_Cust_It_Wh`; mixed table sources** |

### Orders / Consumption

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `orders_qty_cur_req_date_mdc` | Orders excluding C/CNW warehouse group (main DC-only) | Item × WH × Account | `OrdHist[Order Quantity]` filtered `WH Group <> "C/CNW"` |
| `orders_qty_cur_req_date_all` | All orders incl. RH drop-ship and RH Sales | Item × WH | `OrdHist + RH_DropShip_Sales_2024 + RH_Sales` — **⚠️ RH_DropShip is capped at 2024 only (see §9)** |
| `YTD ACT` | Fiscal YTD actuals (prior months only) | Item × WH | `orders_qty_cur_req_date_mdc` where FY=0, FiscalMonthIndicator<0 |
| `YTD-1 ACT` | Prior FY YTD matched months | Item × WH | **⚠️ double offset: `FY=-1 AND FiscalMonthIndicator < -12`** — means prior-year months before month −12 of current FY; this may not correctly align to "same elapsed point last year" when fiscal year offsets are non-integer (see §10) |
| `consumption_futo` | Orders received so far this month (future-to-ship) | Item × WH | `OrdHist` where `FiscalMonthIndicator = 0`, MDC only; commented-out alternative `Orders_Current_Month_Futo` table exists but is NOT used |
| `consumption_rate_wrk` | Fraction of working forecast consumed so far this month | Item × WH × CG | `consumption_futo / fcst_qty_wrk_logility` |
| `consumption_target_rate` | Historical average consumption rate for same day-of-month | CC × CG × WH | From `TargetConsumption` SQL — ratio of MTD orders to full-month orders, averaged over historical months at same fiscal day |
| `consumption_gap_FOB$_cur` | $ revenue at-risk vs. consumption target | Item | `(target_qty_cur - orders_mdc) * (FOB$ / qty)` — **⚠️ financial impact number, see §9** |

### Inventory / Supply

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `SI` | Scheduled inventory (projected end-of-week balance) | Item × WH × week | `SupplyPlanDetail[SI]` where `FiscalWeekIndicator >= 0` |
| `SS` | Safety stock target | Item × WH × week | `SupplyPlanDetail[SS]` — source column, not independently calculated in DAX |
| `SI Overage` (calc col) | Inventory above SS × 1.4 threshold | Item × WH × week | `ROUND(IF(SI > SS*1.4, SI - SS*1.4, 0), 0)` — **⚠️ 1.4 multiplier is unexplained (see §9)** |
| `SS Gap` (calc col) | Shortfall below SS | Item × WH × week | `IF(SI < SS, SI - SS, 0)` — negative values only |
| `Excess FG $` | Dollar value of excess finished goods | Item | `Excess Qty FG * AVERAGE(z_ProductDetails[FOB Price])` |
| `In Stock` | ATP in-stock % (week 2 bucket) | Item × WH × fiscal month | `DIVIDE(In Stock Event, Stock Event)` from `Week_2_ATP`, excluding discontinued items |
| `8wk Avg Receipt` | 8-week average net receipts | Item × WH | `SUM(SupplyPlanDetail[NetRec]) / 8` where `FiscalWeekIndicator < 8` |

### Dimension / Labelling Measures

| Measure | Notes |
|---|---|
| `consumption_title_cur` | Dynamic title showing fiscal month + week number — calculated entirely in DAX from z_FiscalCal; no external dependency |
| `label_prior_plan_date` / `label_90d_plan_date` | String labels derived from `Fcst_Snapshots` max dates |
| `Snapshot` | Max `SnapshotDate` from `FC by Customer Group` table — this is the soon-to-retire table |

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table in model | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `SupplyPlanDetail` | `SupplyChain_Enh.DemandForecastSnapshot` (SPD) | Direct SQL; weekly supply plan rows |
| Same EDW | `OrdHist` | `SupplyChain_Enh.ActualsCustItemWH_AFI` | ~2-year rolling; seasonality factor from `Wholesale_DemandPlanning_AFI.SeasonalitySnapshot` (LVL_NBR=3) |
| Same EDW | `Fcst_Snapshots` | `SupplyChain_Enh.DemandForecastSnapshot` | Working + prior + 90d snapshots |
| Same EDW | `Fcst_Accuracy_Cust_It_Wh` | Same snapshot table | Post-March 2025: Cust-Item-WH grain; Pre-March 2025: Item-WH grain (UNION ALL) |
| Same EDW | `ItWhAccy` | Same, IT-WH accuracy view | Parallel to `Fcst_Accuracy_Cust_It_Wh` but different grain |
| Same EDW | `Week_2_ATP` | `SupplyChain_Enh` ATP table | In-stock events at item-WH-fiscal month |
| Same EDW | `Placements_ABC`, `Placement_History`, `Join` | `SupplyChain_Enh.ActualsCustItemWH_AFI` + ABC tables | Placement counts |
| Same EDW | `Fcst_Average_Promo` | `Wholesale_DemandPlanning_AFI.SeasonalitySnapshot` | Promo lift avg |
| Same EDW | `Sub-Categories` | `SupplyChain_DW.DimCurrentProductDetails` | Category hierarchy incl. Bedding sub-cat |
| Same EDW | `TargetConsumption` | `SupplyChain_Enh` consumption tables | Historical consumption pattern calc |
| Same EDW | `Fcst_Container` | `SupplyChain_DW` + inventory tables | Container seasonality forecast |
| Same EDW | `Fcst_Current_Published`, `Fcst_Published_CurMonth_30d` | Published forecast table | Currently published plan for WvC comparison |
| Same EDW | `Orders_Current_Month_Futo` | `SupplyChain_Enh.DemandForecastSnapshot` | Current-month future orders — **loaded but NOT actively used in consumption measures (commented out)** |
| Same EDW | `Bedroom_Additional_Detail` | `ashley_edw` item master | Headboard/footboard/rail type flags |
| Same EDW | `z_drop_dates` | Status change log | Drop date history via LAG window function |

### Power BI Dataflows (semi-governed)

| Dataflow workspace | Tables fed | Notes |
|---|---|---|
| `a47e4573-c455-40af-a9ad-e22c81a07926` (another workspace) | `z_ProductDetails`, `z_FiscalCal`, `z_WarehouseMaster`, `z_VendorMaster`, `z_CustomerMaster`, `DemandFulfillment` | Governed shared dataflow; conformed dimension layer |
| `f0e1bc90-35c4-4e31-bc00-ff4a225152b7` (this workspace) | `InvSegGlobalCC` | Inventory segmentation dataflow within same workspace |

### SharePoint / Excel (**⚠️ ungoverned / manual**)

| Source | Table | File | Risk |
|---|---|---|---|
| SharePoint: `supplychain-DemandPlanning` site | `RH_FC` | `RH_Fcst.xlsx` → sheet `Active_Fcst` | **High** — sorted by creation date descending, takes latest; no version control, no schema validation |
| Same site | `RH_FC (Prior_Plan)` | Same `RH_Fcst.xlsx`, different tab/path | **High** — prior plan is a manual Excel snapshot; if file is renamed or moved, query silently fails or picks wrong version |
| Same site | `RH_DropShip_Sales_2024` | `RHSales_2024.xlsx` | **High** — **filename is hardcoded to 2024**; filtered explicitly to dates 2024-01-01–2024-12-31. Will not pick up 2025+ data unless file is renamed and query is changed. |
| Same site | `Default_Planner` | SharePoint list (ID `531a515e`) | Medium — planner assignments live in a SharePoint list; list ID is hardcoded |
| Same site | `Users` | SharePoint list (ID `95e7d6e4`) | Medium |
| Same site | `Product_Journal` | `_Product_Journal_UNIFIED_MASTER.xlsx` → sheet `Unified Product Journals` | **High** — path comment says "DO NOT OPEN / Seriously DO NOT OPEN / GO BACK NOW / Self Destruct If Opened" — indicates a shared live Excel workbook; Power BI reads it directly while users may have it open, risking stale/locked reads |
| `SCPGlobalTeam` site | `Cycle_Dates` | SharePoint list (ID `94a48657`) | Medium — cycle snapshot dates managed via SharePoint list; list ID hardcoded |
| `SCPGlobalTeam-Bedding1` site | `RH_Sales` | `RH S_OP File Sales Data.xlsx` → sheet `POS Sales` | **High** — Bedding POS sales; manual Excel file, no refresh SLA visible |

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Item SKU × Warehouse × Customer Group × Fiscal Month (for forecast accuracy and consumption measures); collapses to Item × WH × Fiscal Week for supply plan (`SupplyPlanDetail`).

**Snapshot strategy:** Mixed — and this is meaningful:
- `Fcst_Snapshots` retains **all historical snapshots** (working + prior + 90-day per cycle), enabling WoW and cycle-over-cycle comparison. This is appropriate for a demand review that needs to show plan volatility.
- `Fcst_Current_Published` and `Fcst_Published_CurMonth_30d` are point-in-time published plan snapshots — current only.
- `SupplyPlanDetail` includes a `Snapshot Date` column suggesting it also holds multiple supply plan snapshots (not just latest), consistent with a weekly refresh.
- `OrdHist` is **rolling 2 years** (`@startyear = -2`, `@endmonth = 6`) — suitable for trend analysis; not a true snapshot pattern.
- `Fcst_Accuracy_Cust_It_Wh` accumulates lagged accuracy data (12 trailing months) — snapshot-like by design.

**Verdict:** Model needs historical snapshots (it has them). No latest-only simplification would be appropriate here.

---

## 6. Dimensions Used

| Dimension | Source | Local re-derivations / drift risks |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow → `PowerBI_Supplychain.CurrentProductDetails`) | `AFI Item Status`, `Life Cycle Status (groups)`, `Collective Class (groups)`, `Item Grouping`, `Current/Future Status` concat — all derived locally. `Sellable Item Flag`, `Bardini/Benchcraft/Berkline/F123 Product Flag` are local boolean columns. **Risk:** lifecycle grouping buckets are not visible in a shared catalogue. |
| **Date / Fiscal Calendar** | `z_FiscalCal` (dataflow) | `Rolling 12 Month Year`, `Rolling 12 Month Month`, `Fiscal Month Indicator` (integer offset from today) — all derived inside the dataflow or as calculated columns. Fiscal calendar is non-standard (conformed but private to this workspace). |
| **Warehouse** | `z_WarehouseMaster` (dataflow) | `Warehouse Group`, `Warehouse Order Group`, `Controlled Warehouse` — local groupings. `"C/CNW"` is hardcoded in multiple measure filters as the container warehouse exclusion string. |
| **Vendor** | `z_VendorMaster` (dataflow) | `VendorActive`, `VendorOfficeLocation` — local. |
| **Customer** | `z_CustomerMaster` (dataflow) | `Customer Group`, `Account Group`, `Customer Segment`, `Shipto Sales Territory` — from shared dataflow but `dfcCustomerGroups` strings in `Fcst_Snapshots` must align exactly; `Default_Planner` uses a separate CG→CC mapping from SharePoint. |
| **Planning Cycle** | `Cycle_Dates` (SharePoint list) | `fcst_snapshot`, `prior_cycle`, `CycleName` — entirely governed by a SharePoint list; no EDW backup. `Fcst_Snapshots` carries its own `working_forecast_date` and `prior_cycle` columns derived from `Cycle_Dates` in the SQL. |
| **Product Category** | `Sub-Categories`, `MerchandisingCategories` | Category hierarchy for Bedding derived locally from `DimCurrentProductDetails` + RH CategoryMaster join. Not from a shared product hierarchy dimension. |
| **Planner Assignment** | `Default_Planner` (SharePoint list) | `Collective Class × CustomerGroup → Planner` — managed entirely in SharePoint; no EDW anchor. |

---

## 7. Duplication / Consolidation Signals

1. **Two forecast accuracy tables at different grains:**  
   `Fcst_Accuracy_Cust_It_Wh` (Customer-Item-WH, post-March 2025) and `ItWhAccy` (Item-WH, separate EDW query). `LM Abs It Err %` mixes them — numerator from `Fcst_Accuracy_Cust_It_Wh`, denominator from `ItWHAccy`. This is structurally fragile and likely unintentional.

2. **`FC by Customer Group (in progress of discontinuing)` table:**  
   Marked in the table name and `PBI_QueryOrder` annotation as being phased out. Several measures still reference it (`Snapshot`, `6M Avg Forecast`, `Promo $`, `fcst_qty_wrk_rh_adjusted`). The deprecation is incomplete.

3. **Duplicate YTD/YTG pattern:**  
   `YTD ACT`, `YTD-1 ACT`, `YTD-2 ACT`, `YTG-1 ACT`, `YTG-2 ACT`, `YTG FC` — six nearly identical CALCULATE wrappers varying only the `Fiscal Year Indicator` and `Fiscal Month Indicator` bounds. Could collapse to a single parameterised measure.

4. **`orders_qty_cur_req_date_last_year (2)` and `orders_qty_cur_req_date_this_year (2)`:**  
   Measures with `(2)` suffix exist alongside their originals. The `(2)` versions differ in which fiscal year / month filter is applied; the naming gives no indication of the distinction. One or both may be dead code.

5. **`orders_qty_cur_req_date_mdc` vs. `orders_qty_cur_req_date_logility`:**  
   Both filter `OrdHist` with `WH Group <> "C/CNW"` — expressions are identical. They appear in different measure chains but represent the same population.

6. **`consumption_target_qty_wrk` and `consumption_target_qty_wrk_min` both sum `TargetConsumption[min_target_order_qty]`:**  
   Same expression, different measure names. `consumption_target_qty_wrk_max` sums `max_target_order_qty`. The min/max pairs suggest a band was intended, but the active measures (`consumption_gap_qty_wrk`, `consumption_gap_qty_cur`) use only the min value with commented-out alternative logic visible in the expression.

7. **`Group By 1`, `Group By 2`, `Group By 3`, `Group By 4`:**  
   Four calculated tables with the same enumeration of grouping options (Collective Class, Series Name, WH Group, etc.) — identical content, different names. Likely a workaround for a dynamic grouping feature needing separate slicers.

8. **`RH_FC` and `RH_FC (Prior_Plan)`:**  
   Both read the same `RH_Fcst.xlsx` file on SharePoint — one takes the latest-sorted file, the other takes a specific path version. Pattern is error-prone: if the file is moved, both break differently.

---

## 8. Open Questions

1. **Who actively uses this report?** The `Users` SharePoint list exists in the model but it's unclear if it gates row-level security or is informational. No RLS roles were visible in the BIM annotations examined.
2. **Is `FC by Customer Group (in progress of discontinuing)` actually retired?** Multiple live measures still reference it. Has it been superseded by `Fcst_Snapshots[Customer_Group]` grain? When is the cutover complete?
3. **What is the actual refresh schedule?** `SupplyPlanDetail` queries the EDW live but `Cycle_Dates` is a SharePoint list — if the SharePoint list isn't updated at cycle open, every snapshot-relative measure (`working_forecast_date`, `prior_cycle`) points to wrong dates.
4. **Does the `Product_Journal` read fail when the Excel is open?** The path name explicitly warns users not to open it; this suggests prior failures. Is there a refresh-time lock issue?
5. **Is `RH_DropShip_Sales_2024` still the correct source for RH drop-ship actuals?** The table is hard-filtered to calendar 2024 only. Any 2025 or 2026 RH drop-ship actual is absent.
6. **Are the `Parameter_Fcst_Change_Threshold`, `Bias Threshold`, and `Parameter` slicer values saved per-user or global?** `Exception Flag` depends on all three; if they reset at session open, different users see different exception lists.
7. **Who maintains `Default_Planner` in SharePoint?** If planner assignments change and the list isn't updated, `Category Analyst Filter` and `Cust Demand Planner` filters break.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `SS × 1.4` | `SupplyPlanDetail[SI Overage]` calc column | Defines "SI Overage" as any SI more than 40% above safety stock | **No** — 1.4 multiplier is unexplained. Is this a company-wide policy? A buffer factor? |
| Hardcoded date `date(2026,02,16)` | `fcst_qty_prior_logility` measure | When prior_cycle = Feb 16 2026, adds a special patch for Bedding RHCUST February forecast | **No** — one-off correction embedded in DAX. Will be wrong for every other cycle. If not removed, it permanently distorts prior-plan comparisons for Feb 2026. |
| `1.08` / `0.92` fallback seasonality factors | `OrdHist` SQL | When no seasonality factor exists in `SeasonalitySnapshot`, quarter-ending months (3,6,9,12) get 1.08, all others get 0.92 | **Partially** — SQL comment identifies it as a fallback; no business rationale. Implies ~8% adjustment either direction when data is missing. |
| `Fiscal Month Indicator > 4` and `< 12` | `fcst_qty_add_promo`, `fcst_fob$_addd_promo` | Additive promo forecast and $ adjustment are only applied to months 5–11 | **No** — why not months 1–4? Likely a planning cycle assumption (promo season starts month 5). |
| Bias thresholds: `> 0.25` (90d), `> 0.2` (30d), `> 0.15` (consumption gap) | `Chronic Bias Flag` | Define when a planner is "chronically" over/under forecasting | **No** — three independent thresholds combined with AND logic. Source of thresholds unknown. |
| `* 4` annualisation of 3-month history | `Seas Annualized 3 M Hist` | Multiplies 3-month seas-adjusted actuals by 4 to get annualised run rate | **No** — assumes linear seasonal profile, which contradicts the seasonality adjustment applied upstream. |
| `@startyear = -2`, `@endmonth = 6` | `OrdHist` SQL | Limits order history to 2 years back, ending at month +6 future | **Commented** — purpose noted in SQL header; the +6 future months are for forward orders. |
| `LVL_NBR = 3` | `OrdHist` SQL (SeasonalitySnapshot join) | Selects a specific level of seasonality hierarchy | **No** — level meaning not documented in model. |
| `Warehouse <> '55'` and `Account Number <> '3824800'` | `OrdHist` SQL WHERE clause | Permanently excludes one warehouse and one account | **No** — exclusion reason unknown. Are these inter-company, test accounts, or special channels? |
| `RHCHUST` (note: misspelled) | `fcst_change_qty_r12_wrk_v_prior_all` | Filter intended for `RHCUST` customer group — misspelled as `RHCHUST` | **Bug** — the filter will never match any record; the Bedding RH drop-ship change is silently dropped from this measure. |

**Dollar-value business impact:** `consumption_gap_FOB$_cur` calculates:  
```
(consumption_target_qty_cur - orders_qty_cur_req_date_mdc) × (FOB$ / qty)
```  
This converts the consumption shortfall (or surplus) to an estimated FOB dollar impact for the current month.  
**Unverified assumptions it rests on:**
- The `consumption_target_rate` (historical average at same day-of-month) is a reliable predictor for the current month — no adjustment for seasonality or trend.
- FOB price used is the rolling average of actual invoiced FOB, not a standard cost — will vary with mix.
- `orders_qty_cur_req_date_mdc` (MDC, excludes container WH) is the right denominator — RH channels excluded.
- No confidence interval — a single point estimate is shown as fact.

This number likely appears in monthly WBR/executive decks. **It is high-risk** because it converts an uncertain consumption pace assumption directly into revenue language.

---

## 10. Comparability / Consistency Issues

### a. Pre/Post March 2025 structural split in forecast accuracy
`Fcst_Accuracy_Cust_It_Wh` is a UNION ALL of two incompatible grains:
- **Post-March 2025:** Customer-Item-Warehouse (3 dimensions)
- **Pre-March 2025:** Item-Warehouse only, with `Customer Group` hardcoded as `'AFICONS'`

Any measure filtered by `Customer Group` (e.g., per-customer bias analysis) will show **zero history before March 2025** for all groups except `AFICONS`. Trend comparisons that span this date will be structurally misleading. No visual annotation warns of this boundary.

### b. YTD-1 ACT double-offset anomaly
`YTD-1 ACT`:
```dax
FiscalYearIndicator = -1 AND FiscalMonthIndicator < -12
```
`YTD ACT`:
```dax
FiscalYearIndicator = 0 AND FiscalMonthIndicator < 0
```
The prior-year measure filters to `FY=-1` AND months before −12. This means it compares this year's YTD (months 0 to -N) against last year's YTD (months -12 to -12-N). This is mathematically correct only if the fiscal year is exactly 12 months and `FiscalMonthIndicator` offsets are continuous — any fiscal year boundary irregularity breaks the alignment. Not validated.

### c. 3M vs 6M averaging inconsistency
`Seas Annualized 3 M Hist` multiplies 3-month sum by **4** (→ 12 months implied).  
`Trend (3M vs 6M)` and `Seas Adj Trend (3M vs 6M)` divide each period by its own count (3 or 6) to get a monthly average, then compute relative change.  
These measures are presented side-by-side but use different annualisation logic — comparing `Seas Annualized` to `Trend` values is not valid.

### d. `fcst_qty_add_promo` month range vs. `fcst_fob$_addd_promo`
Both use `Fiscal Month Indicator > 4 AND < 12` (months 5–11). But `fcst_qty_prior_r12_all` adds `fcst_qty_add_promo` without the same month restriction, using `Rolling 12 Month Year = 0` instead. Prior-plan and working-plan promo add-backs cover different month ranges, making the plan-vs-prior comparison inconsistent for promo-heavy items.

### e. Two RH forecast sources for prior vs. working
- Working: `RH_FC` (latest SharePoint Excel, live tab)
- Prior: `RH_FC (Prior_Plan)` (a different named path/tab from the same file)

If the file is saved in a way that overwrites the prior-plan tab, the prior plan disappears and `R12 CP vs PP` for Bedding becomes meaningless. No version-control mechanism is visible.

---

## Closing — Interview Seeds

1. **"When the Exception Flag fires on an item, what do you physically do next — do you open Logility directly, call the account, or update a spreadsheet? And does that action happen before or after the monthly demand review meeting?"**  
   *(Establishes the actual operational loop the report feeds; determines whether the exception logic is reviewed or bypassed.)*

2. **"The consumption pace gauge shows 'Behind Target' mid-month — has there been a case where that signal triggered a concrete action like pulling forward orders or adjusting the forecast, and if so, who made that call and how long did it take?"**  
   *(Validates whether `consumption_gap_FOB$_cur` influences real decisions, or whether it is a post-hoc metric.)*

3. **"The RH Bedding forecast comes in as a manual Excel file — who owns that file, how often does it get updated during the month, and have there been times when Power BI showed stale RH numbers because the file wasn't refreshed in time for the review?"**  
   *(Assesses the actual reliability risk of the SharePoint Excel data path, and whether the `date(2026,02,16)` patch in `fcst_qty_prior_logility` is a symptom of a recurring data quality problem.)*

4. **"The Chronic Bias Flag thresholds — 25% at 90 days, 20% at 30 days, 15% consumption gap — where did those numbers come from, and does hitting the flag automatically trigger a planner coaching conversation, or does it just appear on a chart that people may or may not look at?"**  
   *(Determines whether governance thresholds are calibrated and enforced, or were set once and never revisited.)*
