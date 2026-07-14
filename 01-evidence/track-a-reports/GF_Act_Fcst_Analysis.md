# GF Act+Fcst — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `26c55e74-d007-462d-b85c-b62984039d3b`  
**Report ID:** `1385b8f9-5089-4a2d-a3f4-a964296ae074`  
**Analysis Date:** 2026-07-08  
**Model Size:** 19 tables (3 fact + 5 dim + local date tables); **43 DAX measures** (all in `_Measures`); Compatibility Level 1600

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For a given item/series/warehouse/customer group, how does actual demand (L1 actuals from Logility) compare to the current resultant forecast — and what is the YoY and YTD/YTG trajectory for the current fiscal year?

**This is a "GF" (Ground Floor / L1 Logility) specific report.** It works at the consolidated L1 (company-wide Logility aggregate) grain — **not** at the customer-item-warehouse level used in demand planning review reports. The actuals table (`L1ACTD`) hardcodes `Customer = 'AFICONS'` (the AFI consolidated bucket), making the demand side a single-stream aggregate.

**Primary chain links served:**

| Link | How served |
|---|---|
| **Demand** | `OrderHist` — requested order qty (Original Request date basis), 2-year history, marketable component-adjusted; customer and warehouse breakdown |
| **Forecast** | `L1Fcst` — RSLF (resultant FC) + PROL (promotional lift) + FUTO (future orders) from `DemandForecastSnapshot`, latest snapshot only |
| **Demand vs. Forecast** | `ActFcst` = L1 actuals (past) + RSLF+PROL (future); `OrdFcst` = ordered hist (past) + forecast (future) |

**Secondary links:** None — no supply, inventory, on-time, or receipts data in this model. Pure demand + forecast.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Assess full-year revenue/volume trajectory** — is Act+Fcst Y0 above, at, or below LY? | WBR Leadership / Planning Director | Weekly / Monthly | **Performance/Governance** — measure plan health |
| **Identify collective classes / product lines with negative YoY trends** (`Ord Qty YoY%`, `OrdFcst Y0 %`) | Category Analyst / Planning Manager | Monthly | **Performance/Governance** — coaching, plan adjustment |
| **Compare Disco + P.Drop drag vs. New item contribution** (`P.Drop+Disco Qty`, `New Qty`, `Drop+New`) | Life Cycle Planner / Category Analyst | Monthly (PLR) | **Operational** — lifecycle portfolio decisions |
| **Evaluate warehouse / channel mix shift** (`Ord WH Split`, `ACTD WH Split`, `RSLF WH Split`) | Supply Planner / Network Planning | Monthly | **Performance/Governance** — flag if channel mix drifts from plan |
| **Check forecast consumption rate** (`Fcst Consumption` = FUTO/FCST) — how much of the forecast is backed by future orders | Demand Planner | Weekly | **Operational** — adjust forecast confidence, flag over/under-ordering |
| **Customer % of demand** (`Customer % of Demand`) — which accounts represent largest share of ordered volume | Sales / Account Management | Monthly | **Performance/Governance** — account prioritization |
| **Monitor YTD vs. LY same-period** (`Ord Qty YTD`, `Ord Qty YTD (Y-1)`, `Ord Qty YTD YoY %`) | WBR Leadership / Planning Director | Weekly | **Performance/Governance** |

> **No Financial-Justification decisions identified** — this model has no dollar-value business impact calculation beyond `ActFcst $` and `OrdFcst $` which are simple `SUMX(...FOB Price × Qty)` estimates. No investment case or ROI logic present.

---

## 3. Key Metrics / Measures

All 43 measures reside in `_Measures`.

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `ACTD Qty` | L1 actual demand from Logility history snapshot | Item × Warehouse × Month (AFICONS consolidated) | `SUM(L1ACTD[Qty])` — from `DemandForecastHistorySnapshot`, **latest snapshot only** | ⚠️ see §9 |
| `RSLF Qty` | Resultant forecast (future months only) | Item × CustGrp × Warehouse × Month | `SUM(L1Fcst[Qty])` where `Datatype="RSLF"` and `FiscalMonthInd > -1` | |
| `PROL Qty` | Promotional lift (future months only) | Item × CustGrp × Warehouse × Month | `SUM(L1Fcst[Qty])` where `Datatype="PROL"` and `FiscalMonthInd > -1` | |
| `FCST Qty` | Total future forecast = RSLF + PROL | Item × CustGrp × Warehouse × Month | `[RSLF Qty] + [PROL Qty]` | |
| `FUTO Qty` | Future orders (open orders in forecast system) | Item × CustGrp × Warehouse × Month | `SUM(L1Fcst[Qty])` where `Datatype="FUTO"` | |
| `ActFcst` | L1 actuals (past) + forecast (future) | Item × Month | `[ACTD Qty] + [FCST Qty]` | ⚠️ grain mismatch — see §10 |
| `Ord Qty` | Requested order quantity from OrderHist | Item × Customer × Warehouse × Month | `SUM(OrderHist[Order Qty])` — original request date basis, marketable component-adjusted | |
| `Ord Amt` | Requested order amount | — | `SUM(OrderHist[Order Amount])` | |
| `OrdFcst` | Ordered history (past) + forecast (future) | Item × Month | `[Ord Qty](FiscalMonthInd<0) + [FCST Qty]` | |
| `ActFcstRoll` | Rolling 6-month window: L1 actuals + RSLF | Item × Month | `([ACTD Qty]+[RSLF Qty])` where `FiscalMonthInd > -7` | ⚠️ hardcoded `-7` window |
| `Fcst Consumption` | Ratio of future orders to total forecast | Item × Month | `DIVIDE([FUTO Qty],[FCST Qty])` | ⚠️ see §9 |
| `Fcst Gap` | Gap between future orders and forecast | Item × Month | `[FUTO Qty] - [FCST Qty]` | |
| `Disco Qty` | Act+FC for items with Current Status = "D" | Item | `CALCULATE([ActFcst], CurrentStatus="D")` | |
| `P.Drop Qty` | Act+FC for items with Future Status = "P" or "F" | Item | `CALCULATE([ActFcst], FutureStatus IN {"P","F"})` | |
| `P.Drop+Disco Qty` | Combined lifecycle drag | Item | `[Disco Qty] + [P.Drop Qty]` | |
| `New Qty` | Act+FC for NEW items (no future status) | Item | `CALCULATE([ActFcst], CurrentSCPMfgStatus="NEW", FutureStatus="")` | ⚠️ double-condition; see §9 |
| `Drop+New` | Net of lifecycle exits + new entrants | Item | `[P.Drop+Disco Qty] + [New Qty]` | |
| `Coll Class Total` | Total order qty for collective class (removes item/WH filter) | Collective Class × Month | `SUM(OrderHist[Order Qty])` with `ALLEXCEPT(z_ProductDetails, CollectiveClass)` | |
| `Ord WH Split` | Warehouse's share of total ordered qty | Warehouse | `[Ord Qty] / [z_ACTD(excWH)]` | |
| `ACTD WH Split` | Warehouse's share of total L1 actuals | Warehouse | `[ACTD Qty] / [z_ACTD(excWH)]` | |
| `RSLF WH Split` | Warehouse's share of RSLF forecast | Warehouse | `[RSLF Qty] / [z_Fcst(exc WH)]` | |
| `Customer % of Demand` | Customer's share of total ordered demand | Customer | `[Ord Qty] / [Ord Qty (all Cust)]` | |
| `ActFcst $` | Dollar value of L1 actuals + forecast | Item | `SUMX(z_ProductDetails, FOBPrice × [ActFcst])` | ⚠️ see §9 |
| `OrdFcst $` | Dollar value of ordered hist + forecast | Item | `SUMX(z_ProductDetails, FOBPrice × [OrdFcst])` | ⚠️ same |
| `Ord Qty YoY%` | YoY growth using Fiscal Year Indicator | Item × Year | `([Ord Qty] − prev year) / prev year` using `FiscalYearInd=-1` | ⚠️ see §10 — two YoY measures |
| `Ord Qty YoY% 2` | YoY growth using DATEADD(-1 YEAR) | Item × Year | Same formula but via `DATEADD(TransactionDate,-1,YEAR)` | ⚠️ **duplicate with different calendar logic** |
| `Ord Qty YTD` | YTD ordered qty current year | Item | Uses `TODAY()` → `LOOKUPVALUE(FiscalMonthNum)` → filter `< current month` | ⚠️ `TODAY()` in DAX; see §9 |
| `Ord Qty YTD (Y-1)` | YTD ordered qty prior year, same period | Item | Same month cutoff applied to `FiscalYearInd=-1` | |
| `Ord Qty YTD YoY %` | YTD growth rate | Item | `[Ord Qty YTD]/[Ord Qty YTD (Y-1)] - 1` | |
| `Ord Qty YTD Growth` | YTD absolute qty growth | Item | `[Ord Qty YTD] - [Ord Qty YTD (Y-1)]` | |
| `Ord Qty YTG (Y-1)` | YTG (yet to go) ordered qty prior year | Item | `FiscalMonthNum >= current month`, `FiscalYearInd=-1` | |
| `Fcst Qty YTG` | YTG forecast, current year | Item | `CALCULATE([FCST Qty], FiscalYearInd=0)` | |
| `FCST YTG YOY` | YTG forecast vs. LY YTG actuals | Item | `[Fcst Qty YTG]/[Ord Qty YTG (Y-1)] - 1` | |
| `OrdFcst Y0` | Full-year ordered + forecast, current fiscal year | Item | `CALCULATE([OrdFcst], FiscalYearInd=0)` | |
| `OrdFcst Y0 %` | Full-year growth vs. prior year ordered qty | Item | `[OrdFcst Y0]/[Ord Qty (Y-1)] - 1` | |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| `z_ProductDetails` | PowerBI Dataflow `346f2aa1...` workspace `a47e4573...` → entity `CurrentProductDetails` (column `Item Ext Series Number` renamed to `Planning Series` in PQ) | Governed Dataflow | Low |
| `z_FiscalCal` | Same dataflow → `AshleyFiscalCalendarV2` | Governed Dataflow | Low |
| `z_WarehouseMaster` | Same dataflow → `WarehouseMaster` | Governed Dataflow | Low |
| `z_VendorMaster` | Same dataflow → `VendorMaster` | Governed Dataflow | Low |
| `z_CustomerMaster_AFI` | `ashley-edw.database.windows.net / ashley_edw` — `PowerBI_SupplyChain.CustomerAcctMaster_AFI` with **11 hardcoded account exclusions** + **9 synthetic customer rows** (AFICONS, ECOMM, HSENT, HSLIC, INT, MASSRENT, MFRM, NFM, RHCUST) appended via UNION in SQL | Direct Azure SQL + inline SQL UNION | ⚠️ **Medium-High** — synthetic customer list embedded in SQL, not governed reference table |
| `L1ACTD` | Same EDW — `SupplyChain_Enh.DemandForecastHistorySnapshot` (latest snapshot only: `WHERE dfhSnapshot = MAX(...)`) | Direct Azure SQL EDW | Medium |
| `L1Fcst` | Same EDW — `SupplyChain_Enh.DemandForecastSnapshot` (latest snapshot only: `WHERE dfcSnapshot = MAX(...)`) UNION of RSLF + PROL + FUTO datatypes | Direct Azure SQL EDW | Medium |
| `OrderHist` | Same EDW — `SupplyChain_Enh.ActualsCustItemWH_AFI` **on Original Request date** (`OrigReqWkEnding`), 2-year window (`FiscalYearIndicator >= -2`), marketable component-adjusted | Direct Azure SQL EDW | Medium |
| **`z_LeatherFlag`** | **SharePoint-hosted Excel file** — `Leather FG and Kits.xlsx` in `/Shared Documents/Demand Planning/Power BI Query Data/`, table `LeatherItems` | **SharePoint Excel** | ⚠️ **HIGH — ungoverned manual Excel, no schema enforcement** |

> **No Fabric sources.** All SQL hits `ashley-edw.database.windows.net` (Azure SQL Server).

---

## 5. Grain & Snapshot Strategy

**Primary grain by table:**

| Table | Grain |
|---|---|
| `L1ACTD` | Item × Warehouse × Fiscal Month (AFICONS consolidated — no customer dimension) |
| `L1Fcst` | Item × Customer Group × Warehouse × Fiscal Month |
| `OrderHist` | Item × Customer Account × Warehouse × Fiscal Month (Original Request date) |

**Snapshot strategy: Latest-only for both fact tables.**

- `L1ACTD`: `WHERE dfhSnapshot = (SELECT MAX(dfhSnapshot) FROM DemandForecastHistorySnapshot)` — no historical comparison of actuals snapshots.
- `L1Fcst`: `WHERE dfcSnapshot = (SELECT MAX(dfcSnapshot) FROM DemandForecastSnapshot)` — single latest forecast cycle only.
- `OrderHist`: No snapshot concept — live requested order data filtered to last 2 fiscal years.

**Implication:** No plan-vs-plan change tracking. No accuracy measurement. This model is purely a **current-state demand + forecast view** — it cannot show how the forecast changed between planning cycles. That capability lives in other models (e.g., `AnnualWrkFcst_Snapshots` in Product Review (NEW)).

---

## 6. Dimensions Used

| Dimension | Table | Notes |
|---|---|---|
| **Product** | `z_ProductDetails` (98 cols) | Same conformed source as other models; `Item Ext Series Number` renamed to `Planning Series` here |
| **Date / Fiscal Calendar** | `z_FiscalCal` (39 cols) | Conformed — includes `YTD/YTG Flag` calc column (TODAY()-based, see §9); fewer columns than Product Review (NEW) model — no `Rolling 12 Month Year` etc. |
| **Warehouse** | `z_WarehouseMaster` (13 cols) | Conformed; adds `WH Group` (SWITCH mapping WH codes → Ashton/C/CNW/AFI) and `Physical WH` (normalizes "1A"→"1", "ECA"→"ECR" etc.) locally |
| **Vendor** | `z_VendorMaster` (11 cols) | Reference — present but no relationship to fact tables visible (linked only via z_ProductDetails[Primary Vendor]→z_VendorMaster[VendorNumber] is **absent** from this model's relationship list) |
| **Customer** | `z_CustomerMaster_AFI` (9 cols) | **Local SQL query** (not a dataflow); 9 synthetic customer groups injected; `z_SortRank` calculated via RANKX on 12-month orders |
| **Leather Flag** | `z_LeatherFlag` (3 cols) | Separate lookup table — Item SKU, Leather Flag (boolean), Last Refresh — sourced from SharePoint Excel |
| **Production Resource** | Not present | |

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `WH Group` | `z_WarehouseMaster` calc column | `SWITCH(Warehouse, "335"→"Ashton", "C"→"C/CNW", "CNW"→"C/CNW", "C35"→"C/CNW", else "AFI")` | Medium — hardcoded WH codes; default fallback is "AFI" which may incorrectly bucket unlisted warehouses |
| `Physical WH` | `z_WarehouseMaster` calc column | Maps suffix-A warehouse codes to numeric (1A→1, 15A→15, ECA→ECR, etc.) | Medium — if new warehouse codes are added, they pass through unmapped |
| `z_ItemFilter` | `z_ProductDetails` calc column | `ISNUMBER([FCST Qty]+[Ord Qty])` — hides items with no forecast and no orders in current context | Low |
| `z_PromoFilter` | `z_ProductDetails` calc column | `ISNUMBER(CALCULATE([PROL Qty]))` — filter to items with promo lift | Low |
| `Fcast Last Date` | `z_ProductDetails` calc column | `CALCULATE(MAX(L1Fcst[FiscalMonthLastDate]), L1Fcst[Item]=EARLIER(...))` — last forecast month per item | Medium — EARLIER() pattern; result depends on row context; may be unreliable in some visual configurations |
| `z_MarketableConversion` | `z_ProductDetails` calc column | `DIVIDE(1, IF(GeneralDescCode=700, QtyInBox of parent SKU, 1))` — converts marketable unit to sellable unit | Medium — LOOKUPVALUE for parent SKU via LEFT(SKU, LEN-1) pattern |
| `Mattress Type` | `z_ProductDetails` calc column | SWITCH on AFI Sales Category → Foam / Innerspring / "" | Low |
| `YTD/YTG Flag` | `z_FiscalCal` calc column | `SWITCH(TRUE(), FiscalMonthNum < LOOKUPVALUE(...TODAY()), "YTD", ..., "YTG")` | ⚠️ **High** — TODAY() evaluated at query time, not at model refresh; values drift between refreshes |
| `Customer` (display) | `z_CustomerMaster_AFI` calc column | `LEFT(CustomerName,16) & " - " & CustomerAccountNumber` | Low — truncates long names at 16 chars |
| `Customer Desc` | `z_CustomerMaster_AFI` calc column | SWITCH on 17 hardcoded account numbers → "DSG - All Accounts"; else shows Customer field | Medium — DSG account list hardcoded in DAX |
| `z_AcctFilter` | `z_CustomerMaster_AFI` calc column | TRUE for 9 synthetic groups; else `ISNUMBER(CALCULATE([Ord Qty]))` | Low |
| `z_SortRank` | `z_CustomerMaster_AFI` calc column | `RANKX(ALL(z_CustomerMaster_AFI), Ord Qty last 12M)` — dense rank | Medium — recomputes on every query; expensive on large customer lists |
| `Test` / `Column` | `z_CustomerMaster_AFI` calc columns | `Test` = SUM(OrderHist[Order Qty]) last 12M; `Column` = `RANK.EQ(Test, Test)` | ⚠️ **Dead scaffolding** — development columns left in production model |

---

## 7. Duplication / Consolidation Signals

1. **Two YoY% measures with different calendar logic:**
   - `Ord Qty YoY%` — uses `FiscalYearIndicator = -1` (relative fiscal year indicator)
   - `Ord Qty YoY% 2` — uses `DATEADD(TransactionDate, -1, YEAR)` (calendar year DATEADD)
   These produce different results when the fiscal year doesn't align with calendar year. Neither is labeled as preferred/deprecated. Both exist in production.

2. **`ActFcst` vs. `OrdFcst` — two "blended" measures with different demand sources:**
   - `ActFcst` = `L1ACTD` (Logility actuals, AFICONS consolidated) + `FCST Qty`
   - `OrdFcst` = `OrderHist` (requested orders, customer-level) + `FCST Qty`
   Same forecast numerator, different actuals. A user viewing both may not know they measure demand differently. No visual label distinguishes them.

3. **`ActFcst $` and `OrdFcst $` use `SUMX(z_ProductDetails, FOBPrice × measure)` — same pattern as `Excess FG $` bug in Product Review (NEW).** When the visual context includes multiple items, `FOB Price` is the item's own attribute, so SUMX iterates correctly here (unlike AVERAGE). These are not buggy — but they hardcode FOB Price as the value basis with no fallback for items with zero FOB Price.

4. **`z_ACTD(excWH)` and `z_OrdQty(excWH)` and `z_Fcst(exc WH)` — three denominator measures for WH split calculations**, each independently removing the WH filter. These are helper measures (prefixed `z_`) but could be collapsed.

5. **`Test` and `Column` in `z_CustomerMaster_AFI`** — clearly development artifacts (`Test = 12M order qty`, `Column = RANK.EQ(Test, Test)`). Should be removed.

6. **`L1ACTD` and `OrderHist` both represent historical demand** for the same items/warehouses but from different EDW tables (`DemandForecastHistorySnapshot` vs. `ActualsCustItemWH_AFI`) and on different date bases (`dfhFiscalMonth` aggregated vs. `OrigReqWkEnding`). The two measures `ACTD Qty` and `Ord Qty` will not reconcile for the same item-month — no documentation explains when to use which.

7. **`z_LeatherFlag` as a standalone dimension** — this is only needed to supplement `z_ProductDetails`, which has no leather flag. It is sourced from a SharePoint Excel file that must be manually maintained in sync with the product master. In Product Review (NEW), leather classification was derived from Item Class Codes in DAX directly (`z_LeatherFlag` was a calc column on z_ProductDetails). Here it is an external file-backed table. Two different approaches to the same classification.

---

## 8. Open Questions

1. **What is "GF" and what does it stand for?** The report name implies "Ground Floor" or possibly an internal project code. Is this report specifically for the Logility L1 (company-wide) planning layer and not used for customer-level review? Who is the primary audience?

2. **`L1ACTD` customer is always `'AFICONS'` (hardcoded in SQL).** This means `ACTD Qty` cannot be broken out by customer group. Yet `L1Fcst` and `OrderHist` have real customer groups. Does the `ActFcst` measure produce meaningful results when filtered by customer? (Answer from model: partial — `ACTD Qty` ignores the customer filter; `FCST Qty` applies it — the blended number is inconsistent.)

3. **`OrderHist` uses `OrigReqWkEnding` (Original Request date).** Most other models in this workspace use `CurReqWkEnding` (Current Request date) for order history. Is this intentional? Original Request dates show when orders were first placed, not when they're currently expected — this produces different demand timing.

4. **`z_LeatherFlag` Last Refresh date** — is this file refreshed manually or on a schedule? If a new leather item is introduced but the Excel isn't updated, it silently appears as non-leather.

5. **`Ord Qty YoY%` vs. `Ord Qty YoY% 2` — which is used in reports?** Both exist in production. If visuals use different measures, YoY numbers on different pages may be inconsistent. Business users may not know which one they're reading.

6. **Is `FUTO` (Future Orders) in `L1Fcst` the correct signal for "forecast consumption"?** `Fcst Consumption = FUTO/FCST` assumes `dfcOrderFutureQty` in Logility represents committed future orders. Confirm this is the same concept used in S&OP meetings when discussing "how sold out are we against forecast."

7. **`z_CustomerMaster_AFI` hardcodes 11 excluded account numbers** (in WHERE clause) and 9 synthetic group names (in UNION). Who owns this list? There is also a commented-out exclusion for account `'4031300'` (RHCUST) — was this intentionally re-enabled elsewhere, or is it still excluded via a different path?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| `Customer = 'AFICONS'` (hardcoded) | `L1ACTD` SQL | All L1 actuals assigned to AFICONS consolidated group — no customer breakdown in actuals | SQL comment — intentional design, no model documentation |
| `FiscalYearIndicator >= -2` | `OrderHist` SQL | 2-year history window for ordered demand | **No** — 2Y is undocumented; different from Product Review (NEW) which uses 3Y |
| `FiscalMonthIndicator > -1` | `RSLF Qty`, `PROL Qty` measures | Forecast only includes current month + future (excludes past months even if forecast data exists there) | **No** — creates hard boundary at current month; past months are excluded from `FCST Qty` regardless of context |
| `FiscalMonthInd > -7` | `ActFcstRoll` | Rolling window = last 6 prior months + current = 7 months total | **No** — "rolling 6 months" is hardcoded as `-7`; description in measure name doesn't reflect the window size |
| `TODAY()` in `YTD/YTG Flag` and `Ord Qty YTD` / `Ord Qty YTD (Y-1)` | `z_FiscalCal` calc column, `_Measures` | Uses live TODAY() to determine which months are YTD vs. YTG | ⚠️ **Risk** — TODAY() is evaluated at query time, not at refresh. In DirectQuery mode this is expected; in Import mode (this model is Import), the YTD/YTG boundary shifts through the day but all data is from the last refresh. Values in exports/snapshots will have different YTD boundaries depending on when they were taken |
| `LEFT(CustomerName, 16)` | `z_CustomerMaster_AFI[Customer]` calc column | Display label truncated to 16 characters | **No** — names longer than 16 chars are silently cut off in all visuals using this field |
| `LOOKUPVALUE(... TODAY())` in `Ord Qty YTD` | `_Measures` | Finds fiscal month number for today to determine YTD cutoff | Same TODAY() risk as above; also: if TODAY() falls on a date not in z_FiscalCal, LOOKUPVALUE returns BLANK → YTD = BLANK |
| `GDESCD = '700'` | `OrderHist` SQL (marketable component join) | Code 700 = "Qty in Box" descriptor in item master; used to find marketable unit conversion factor | **No** — opaque item master code hardcoded in SQL |
| `dfcResultantForecast > 0` / `dfcPromotionalLift > 0` / `dfcOrderFutureQty > 0` | `L1Fcst` SQL | Zero values excluded from each datatype's UNION leg | Partially — avoids nulls but means items with zero RSLF (e.g., items being removed from forecast) disappear from the forecast table entirely |
| `SUMX(z_ProductDetails, FOBPrice × [ActFcst])` / `× [OrdFcst]` | `ActFcst $`, `OrdFcst $` | FOB Price × blended qty for dollar estimate | **No** — uses current FOB Price (as of last model refresh) for all historical periods; price changes are not historically adjusted |
| `Fcst Consumption = DIVIDE([FUTO Qty],[FCST Qty])` | `_Measures` | Assumes FUTO = committed future orders; denominator is RSLF+PROL | **No** — if FCST Qty = 0 (no forecast), DIVIDE returns BLANK (correct); but if an item has FUTO without RSLF (unusual), result > 1 with no cap |
| 9 synthetic customer rows | `z_CustomerMaster_AFI` SQL | AFICONS, ECOMM, HSENT, HSLIC, INT, MASSRENT, MFRM, NFM, RHCUST, MFRM added as literal SQL UNION rows | **No** — these represent special customer channels or aggregation buckets; not documented in model |
| 11 excluded accounts | `z_CustomerMaster_AFI` SQL `WHERE ... NOT IN (...)` | Specific accounts excluded from customer master (inactive/internal) | **No** — list is hardcoded; no governance for adding/removing accounts |

---

## 10. Comparability / Consistency

1. **`Ord Qty YoY%` vs. `Ord Qty YoY% 2` — two YoY measures with different calendar engines.**
   - `Ord Qty YoY%` uses `z_FiscalCal[Fiscal Year Indicator] = -1` (relative fiscal year)
   - `Ord Qty YoY% 2` uses `DATEADD('z_FiscalCal'[Transaction Date], -1, YEAR)` (calendar year shift)
   If the fiscal year starts in a different calendar month (as is typical for Ashley's fiscal calendar), these two measures return different numbers for the same item in the same visual. If different report pages use different measures, YoY comparisons are incomparable across pages.

2. **`ACTD Qty` (from `L1ACTD`) vs. `Ord Qty` (from `OrderHist`) — two demand measures, different sources, different dates.**
   - `ACTD Qty`: `DemandForecastHistorySnapshot.dfhActualDemand` aggregated by fiscal month of the snapshot period; no customer breakdown; latest snapshot only
   - `Ord Qty`: `ActualsCustItemWH_AFI.Order Quantity` aggregated on `OrigReqWkEnding` (original request date); customer-level
   These will not match for the same item-month. No documentation clarifies which represents "true" demand. `ActFcst` uses `ACTD Qty` for the past; `OrdFcst` uses `Ord Qty` for the past — mixing them gives two "full-year" demand pictures that are inherently inconsistent.

3. **`ActFcst` grain mismatch: past = AFICONS (consolidated), future = customer-level.**
   `ActFcst = [ACTD Qty] + [FCST Qty]`. Past (`ACTD Qty`) has no customer dimension (always AFICONS). Future (`FCST Qty`) is filtered by customer group. When a user slices `ActFcst` by customer, the historical portion (`FiscalMonthInd < 0`) shows the full consolidated demand regardless of customer filter, while the forecast portion (`FiscalMonthInd ≥ 0`) correctly filters by customer. This produces misleading "total vs. customer" visuals where the past always shows company total.

4. **`FiscalMonthInd > -1` vs. `FiscalMonthInd < 0` — two ways to say "current/future."**
   `RSLF Qty` uses `> -1` (includes indicator 0 = current month). `OrdFcst` uses `FiscalMonthInd < 0` for the history leg. The current month (`Indicator = 0`) falls in forecast for RSLF but in history for OrdFcst's history leg — current month has both actuals (from OrdHist) and forecast (from RSLF) without a clear rule for which to use.

5. **`OrderHist` uses Original Request date; `L1ACTD` uses Logility's actual demand period.** These represent different demand timing concepts. A large order placed in Month 1 but shipped in Month 3 would appear in Month 1 in `Ord Qty` but in Month 3 in `ACTD Qty`. No documentation flags this difference.

---

## Closing — Interview Seeds

> Direct questions for a follow-up interview with the actual business user.

1. **"When you look at the `ActFcst` vs. `OrdFcst` numbers for the same item on the same page — do you know they pull historical demand from two different sources? Which one do you trust more, and why?"**
   *(Targets: user awareness of the dual-demand-source design; which measure drives actual decisions; trust level in the data.)*

2. **"The `Fcst Consumption` metric shows FUTO ÷ FCST. When that number goes above 1.0 or drops below 0.1, what action do you take — and does someone review it every cycle or only when it hits a threshold?"**
   *(Targets: whether this metric is actively used operationally or is just available; escalation path when it signals over/under-booking.)*

3. **"The `Leather FG and Kits.xlsx` file on SharePoint — who updates it when a new leather product launches, and has it ever been wrong or stale when a new collection hit the market?"**
   *(Targets: ungoverned data source risk; frequency of manual updates; any known failures.)*

4. **"There are two YoY% measures in the model that use different calendar logic and can give different percentages. When this report goes into a WBR deck or leadership review, which one is on the slide — and has anyone ever noticed or questioned the discrepancy?"**
   *(Targets: whether the duplicate measure inconsistency is visible to leadership; risk of conflicting numbers in executive communications.)*

---

*Analysis based on BIM definition extracted 2026-07-08. No bundle indexes were modified.*
