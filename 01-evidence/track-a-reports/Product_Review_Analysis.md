# Product Review — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `a5fead7b-e98a-43f7-ba2d-13476d99066c`  
**Report ID:** `5df27f28-6cd4-4884-89f7-ae5af3c991a5`  
**Analysis Date:** 2026-07-09  
**Model Size:** 48 tables (20+ fact + 10 dim/lookup + local date tables); **218 DAX measures** across 15 measure tables; Compatibility Level 1567  
**BIM File:** [bim/Product_Review.bim](bim/Product_Review.bim) — 3,372 KB  
**Note:** This is the **original** Product Review model — distinct from "Product Review (NEW)" (analysis #11). This model is significantly larger and serves as the comprehensive item-level review across all supply chain domains.

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For a given item, what is its complete health picture across all supply chain dimensions — demand trend, forecast accuracy, supply plan coverage, placements, on-time performance, retail sales, inventory turns, and more?

This is the **original comprehensive item review report** — the predecessor of Product Review (NEW). It integrates data from **Logility, Retail Sales (3 sources), Wholesale Invoicing/Orders, Warehouse Inventory, ATP, Supply Plan, Vendor Master, On-Time Performance, PIM, Nailed (store-level inventory)**, and more — all in a single model.

**Chain links served: ALL — Demand, Forecast, Supply, Inventory, On-Time, Production, Retail, Quality, Vendor.**

### Report Domains (Tabs):

| Tab/Domain | Tables | Purpose |
|---|---|---|
| **Forecast Accuracy** | `Forecast Accuracy` (58 measures) | Multi-period accuracy with wMAPE, naive benchmark, FVA, CV, sMAPE, scaled errors |
| **Demand Data** | `Demand Data` (11 measures) | 3-month rolling avg, YTD, YoY, 2-years-ago demand trend |
| **Logility - Current Mo** | `Logility - Current Mo` (24 measures) | Day-over-day forecast changes for months 0–5 |
| **SupplyPlanDetail** | `SupplyPlanDetail` (22 measures) | SI-SS gap, % COC, DF rate, weeks of supply, fill rate, inventory velocity |
| **Demand Fulfillment** | `Demand Fulfillment` (3 measures) | Firm demand, SI negative, basic DF rate (FirmDemand-only) |
| **Placements** | `Placements` + `Placements - Wk` (11 measures) | Placement volume, 3-month velocity, cube velocity, HS specific |
| **Sales Trend - AFI** | `Sales Trend - AFI` (27 measures) | AFI wholesale sales qty/$, 3-mo avg, YTD/YoY, weekly CoV, WH splits |
| **Sales Trend - Retail** | `Sales Trend - Retail` (20 measures) | Retail written/invoiced sales qty/$ across Homes Corp, Licensee, Storis |
| **Sales Trend - Ashcomm** | `Sales Trend - Ashcomm` (20 measures) | Commissioned channel written/invoiced sales |
| **Inventory Turns** | `Inventory Turns` (3 measures) | 12-month COGS / avg inventory at item-warehouse |
| **Current SS/SI** | `Current SS/SI` (7 measures) | Current safety stock vs. shippable inventory, weeks supply |
| **On Time** | `On Time` (5 measures) | On-time performance by 4 reference date definitions |
| **Nailed** | `Nailed` (0 measures) | Retail store-level inventory (on-hand, reserved, available, damaged) |
| **Future Orders** | `Future Orders - Current Mo` + `- Month End` (1 measure) | Current month order future qty, consumption % |
| **ATP** | `ATP Week Ending` + `ATP (2)` (2 measures) | Morning/afternoon ATP by version |
| **Product Details** | `Product Details` (103 cols) | Full item master with calculated attributes (lifecycle, planner, lead time, ABC/XYZ, PIM, color) |

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Full item health check** — review all KPIs on one screen (demand trend, FC accuracy, DF rate, placements, OT%, turns, inventory velocity) | Supply Planner / Category Analyst | Weekly | **Performance/Governance** |
| **Forecast accuracy review by period** (30d/60d/90d/120d) with vs. naive benchmark and FVA | Forecast Analyst / Planning Manager | Weekly/Monthly | **Performance/Governance** |
| **Day-over-day forecast change monitoring** (months 0–5) — identify rapid forecast shifts between daily Logility runs | Demand Planner | Daily | **Operational** — detect unexpected forecast moves |
| **DF rate monitoring** — % of customer orders covered by SI, with/without net forecast, YTD variants | Supply Planner | Weekly | **Performance/Governance** |
| **Sales trend by channel** — AFI wholesale, retail (3 sub-channels), Ashcomm — are channel trends aligned? | Channel Manager / Planning Director | Monthly | **Performance/Governance** |
| **Placement velocity** — 3-month rolling avg placements as proxy for retail demand pull | Demand Planner | Weekly | **Performance/Governance** |
| **On-time performance** — 4 metrics by original/current request/promise week | Customer Service Manager | Weekly | **Performance/Governance** |
| **Inventory turns** — COGS / avg inventory; 12-month rolling view | Inventory Manager | Monthly | **Performance/Governance** |
| **Safety stock gap** — SI vs. SS, weeks of supply, COC rate | Supply Planner | Weekly | **Performance/Governance** |
| **Nailed (retail store inventory)** — store-level on-hand, reserved, available, damaged | Retail Ops | Weekly | **Operational** |
| **ATP morning vs. afternoon version** — monitor intra-day ATP updates | Supply Planner | Daily | **Operational** |

---

## 3. Key Metrics / Measures

**All 218 measures across 15 tables.** Only key groups documented here.

### Forecast Accuracy (58 measures — largest measure set)

| Measure | Description | Formula Key Points |
|---|---|---|
| `Total Demand` | Sum of actual demand qty | `SUM(ForecastAccuracy[Actual Demand Quantity])` |
| `Total Forecast` | Sum of promoted resultant forecast | `SUM(ForecastAccuracy[Promoted Resultant Forecast Quantity])` |
| `Total Accuracy` | Symmetric accuracy: lower/upper ratio | `IF(Demand>=FC, FC/Demand, Demand/FC)` — simple ratio |
| `Total sABS % Error` | Symmetric absolute % error | `ABS(D-F)/((D+F)/2)` — denominator = average of demand+forecast |
| `Total Forecast Error` | Absolute forecast error | `SUM(ForecastAccuracy[Forecast Error])` |
| `Total Forecast Bias` | Bias as % of demand | `DIVIDE(Total Forecast Error, Total Demand)` |
| `Total wMAPE` | Weighted MAPE | `DIVIDE(Mean ABS Deviation, Mean of Actual Demand)` |
| `Total MAPE` | Mean absolute % error (AVERAGEX) | `AVERAGEX(ForecastAccuracy, ABS(D-F)/D)` |
| `Total sMAPE` | Symmetric MAPE (AVERAGEX) | `AVERAGEX(ForecastAccuracy, sABS%Error)` |
| `Total MAD-MEAN Ratio` | Alternative to wMAPE | — |
| `Total MSE`, `Total RMSE` | Mean squared error, root MSE | — |
| `Total Standard Deviation` | Of actual demand | `STDEVX.P(ForecastAccuracy, Total Demand)` |
| `Total Coefficient of Variation` | Volatility measure | `DIVIDE(StdDev, Mean of Demand)` |
| `Total Forecast Attainment` | Demand/Forecast ratio | `DIVIDE(Total Demand, Total Forecast)` |
| `Total Normalized Forecast Metric` | (F-D)/(F+D) — normalized range | — |
| `Total wsMAPE` | wMAPE on scaled demand | Uses `sDemand` column |
| `Total MASE` | Mean Absolute Scaled Error | `DIVIDE(MAD, Mean ABS Scaled Error)` |
| `Total wMAPE - 30d/60d/90d/120d` | wMAPE by forecast period | `CALCULATE(wMAPE, ForecastPeriod="30 Day")` |
| `Total Forecast Bias - 30d/60d/90d/120d` | Bias by period | — |
| `Total Naive Forecast` | Sum of naive (lag) forecast | `SUM(ForecastAccuracy[Naive Forecast])` |
| `Total Naive wMAPE` | Naive benchmark wMAPE | `DIVIDE(Naive MAD, Mean of Demand)` |
| `Forecast Value Added` | FVA = wMAPE − Naive wMAPE | `[Total wMAPE] - [Total Naive wMAPE]` |
| `FVA - 30d/60d/90d/120d` | FVA by period | — |
| `Weekly Total Dmnd`, `Weekly StDev`, `Weekly CoV` | Weekly volatility stats | AVEGREX + STDEVX.P |

### Demand Fulfillment (3 measures)

| Measure | Description |
|---|---|
| `Total Firm Demand` | `SUM(DemandFulfillment[Firm Demand])` |
| `Total SI Negative` | `SUM(DemandFulfillment[SI Negative])` |
| `Total % Cust Orders Covered` | `(FirmDemand + SI_Neg) / FirmDemand` — **NO NetForecast** |

**⚠️ CRITICAL: DF rate formula differs from Product Review (NEW).** This model uses `(FD + SI_neg) / FD` — denominator is FirmDemand only. The NEW version uses `(FD + NF + SI_neg) / (FD + NF)` — includes NetForecast. Two reports with same name, different numbers.

### Demand Data (11 measures)

| Measure | Description |
|---|---|
| `Total Dmnd` | Demand from Logility `ItemActualDemand` |
| `Total Dmnd - Rolling 3Mo` | 3-month rolling sum |
| `Total Dmnd - 3Mo Avg` | Rolling 3Mo / distinct month count |
| `Dmnd Average` | `(PrevMo + 3MoAgo + PrevYear + 2YrsAgo) / 4` — weighted average |
| `Total Dmnd - YTD Current/Previous Year` | YTD via TOTALYTD |
| `Total Dmnd - Previous Mo / 3Mo Ago / 2Yrs Ago` | Period comparisons via PARALLELPERIOD |

### Logility - Current Mo (24 measures — 6 months × 4 variants)

Pattern for each month 0–5:
- `Pro_Rslt_FC_N` = `Result_Fc_N + Result_PROL_N` (current day forecast)
- `Prev Day Pro_Rslt_FC_N` = yesterday's forecast via `DATEADD(FileDate, GoBack, DAY)`
- `Day over Day - Pro_Rslt_FC_N` = absolute change
- `Day over Day Change - Pro_Rslt_FC_N` = UP/DOWN/FLAT label

**Key assumption:** `Go Back` = −1 normally, = −3 if Monday (skip weekend). Day-over-day compares to the most recent business day.

### SupplyPlanDetail (22 measures)

| Measure | Description | Formula |
|---|---|---|
| `SI-SS` | SI minus safety stock | `SUM(spdShippableInventory) - SUM(spdSafetyStock)` |
| `SI as % of SS` | SI relative to SS target | `DIVIDE(SI, SS)` |
| `*SI Neg` | Negative SI (shortfall) | `SUM(SI Negative)` |
| `*FirmDemands+NetForecast` | Total demand | `SUM(spdFirmDemands) + SUM(spdNetForecast)` |
| `*% COC` | Customer order coverage (FD only) | `(FirmDemands + *SI Neg) / FirmDemands`, clamped [0,1] |
| `*% COC w/ NetForecast` | COC with NF | `(FD+NF+SI_Neg) / (FD+NF)`, clamped [0,1] |
| `*SCP Team DF_2` | DF rate using `spdDemandFulfillment` | `DF / (FD+NF)`, clamped [0,1] |
| `*SCP Team DF_2 w/o NetForecast` | DF rate FD-only | `DF / FD`, clamped [0,1] |
| `*DF YTD / *SI Neg YTD` | YTD versions of DF and SI Neg | TOTALYTD |
| `WeeksOfSupply` | SI / weekly demand rate | `SI / (NetForecast + FirmDemands)` |
| `*% of Out of Stock` | SI Neg / Firm Demands | — |
| `*Fill Rate_2b` | DF / SI Neg, clamped [0,1] | — |
| `*Inventory Velocity` | Beginning OH / Promoted Resultant | — |
| `Promoted Resultant` | RSLF + Promo Lift | — |
| `Production + Purchase Orders` | Total supply | — |

### Sales Trend - AFI (27 measures)

Key qty/$ measures with rolling 3-month avg, YTD current/previous, YTD YoY % change:
- `Total Qty Shipped`, `Total Qty Ordered`
- `Total Net Sales`, `Total Amount Ordered`
- `Total Net Sales - YTD Current Year / Previous Year / % Change YTD YoY`
- `Weekly Avg Qty Ordered`, `Weekly StDev Qty Ordered`, `Weekly CoV` — unique statistical measures
- `Total Qty Shipped - 232` and `- C/CNW` — channel splits
- `Avg $ per Piece` = Amount / Qty

### On Time (5 measures)

| Measure | Formula |
|---|---|
| `Total Shipped Quantity` | `SUM(Shipped Qty)` |
| `Total On-Time % - Original Request Wk` | `QtyOnTime_OrigReq / Total Shipped` |
| `Total On-Time % - Original Promise Wk` | `QtyOnTime_OrigPromise / Total Shipped` |
| `Total On-Time % - Current Promise Wk` | `QtyOnTime_CurPromise / Total Shipped` |
| `Total On-Time % - Current Request Wk` | `QtyOnTime_CurReq / Total Shipped` |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **Product Details** | Dataflow `346f2aa1...` workspace `a47e4573...` | Governed Dataflow | Low |
| **CurrentProductDetails** | Same dataflow, `PowerPlatform.Dataflows` API | Governed Dataflow | Low — separate API connector |
| **Forecast Accuracy** | Dataflow `1d89d8d0...` workspace `f0e1bc90` (original SQL: `SupplyChain_Enh.ItemForecast_Logility` + `ItemActualDemand_Logility`, multiple LEFT JOINs, 30/60/90/120d period classification) | Governed Dataflow | Medium |
| **Demand Data** | Same dataflow → `Demand Data` (original SQL: `ItemActualDemand_Logility` + `DimDate`) | Governed Dataflow | Medium |
| **Logility - Current Mo** | Same dataflow → `Logility - Current Mo` (original SQL: `FCC_Logility90DayHist` current-month, excludes `Z__K`/`ZARP`/`ZAHM` item classes, excludes `%UN`/`%SW`/`%CARD` items) | Governed Dataflow | Medium |
| **SupplyPlanDetail** | Dataflow `bd5ad7a5...` → `SupplyPlanDetail` | Governed Dataflow | Medium |
| **Placements** | Dataflow `e6ade32d...` → `Placements` | Governed Dataflow | Medium |
| **Sales Trend - AFI** | Dataflow `e6afbf37...` → `Sales Trend - AFI` (original SQL: `InvoiceHistory` + `QualityCosts` + `OrderHistory`, 3 LEFT JOINs, 2-year range) | Governed Dataflow | Medium |
| **Sales Trend - Retail** | Dataflow `268f23ba...` → `Sales Trend - Retail` (original SQL: 3 UNION of FactWrittenSales from HomesCorporate, HomesLicensee, Storis + 3 UNION FactInvoicedSales — 6 UNIONs total, `Retail_DW`) | Governed Dataflow | ⚠️ High — complex 6-table UNION, Retail DB |
| **Sales Trend - Ashcomm** | Same dataflow → `Sales Trend - Ashcomm` | Governed Dataflow | Medium — Retail DB |
| **Nailed** | Dataflow `09eddbaa...` → `Nailed` (original SQL: `FactInventory` + `DimLocation`, current-day only, store-level) | Governed Dataflow | Medium — Retail DB |
| **Inventory Turns** | Same dataflow → `Inventory Turns` (original SQL: `Inventory_Enh.TurnsDetail`, 52-week calc type) | Governed Dataflow | Medium |
| **Current SS/SI** | Dataflow `1804c594...` → `Current SS/SI` (original SQL: `ProdRevCurrentSSSI`, excludes Z__K/ZARP/ZAHM, excludes %SW/%CARD/%UN) | Governed Dataflow | Medium |
| **Forecast - Logility** | Dataflow `09eddbaa...` → `Forecast - Logility` (original SQL: `DemandForecastSnapshot`, latest snapshot, 15-month forward) | Governed Dataflow | Medium |
| **ATP Week Ending / ATP (2)** | Dataflow `e770a268...` → `ATP Week Ending`/`ATP(2)` (original SQL: `ATPWeekEnding`, WH in list, 6 weeks / 13 weeks back) | Governed Dataflow | Medium |
| **On Time** | Dataflow `e6ade32d...` → `On Time` | Governed Dataflow | Medium |
| **Future Orders** | Dataflow `1d89d8d0...` / `bd5ad7a5...` | Governed Dataflow | Medium |
| **Vendor** | **Direct SQL** `ashley-edw` — `DemandInventorySnapshot`, max snapshot | Direct SQL | Medium |
| **Vendor/SKU Lead Time** | **PQ Merge** of Vendor + Vendor Master dataflows | PQ Derived | Medium |
| **PIM** | **Direct SQL** `MasterData_PIM.Product` | Direct SQL | Low |
| **Colors** | **Direct SQL** `Wholesale.ProductDetails` + `Retail.ColorMaster` | Direct SQL | Low |
| **Seasonality** | **Direct SQL** `Wholesale_DemandPlanning_AFI.ItemSeasonalFactor` L2 | Direct SQL | Low |
| **PSW** | Dataflow `bd5ad7a5...` → `PSW` | Governed Dataflow | Medium |
| **ABC Codes** | Dataflow `bd5ad7a5...` → `ABC Codes` | Governed Dataflow | Medium |
| **AshleyFiscalCalendar** | Dataflow `346f2aa1...` → `AshleyFiscalCalendar` | Governed Dataflow | Low |
| **DRP Planner** | Dataflow — item-warehouse planner assignment | Governed Dataflow | Low |
| **Make-Buy Code** | Dataflow — X vs. non-X classification | Governed Dataflow | Low |

### Dataflow Workspaces:
- **`f0e1bc90`** (Supply Chain Analytics-Premium) — hosts 15+ dataflows (Forecast Accuracy, Demand Data, Logility Current Mo, SupplyPlanDetail, Placements, Sales Trend AFI/Retail/Ashcomm, Nailed, Inventory Turns, Current SS/SI, ATP, On Time, PSW, ABC Codes, Future Orders)
- **`a47e4573`** (BI Dev) — hosts Product Details, AshleyFiscalCalendar, Warehouse Master, Vendor Master dataflows

> **No SharePoint, no Excel.** 48 tables entirely from dataflows or direct EDW SQL. Second-cleanest architecture after GF FC Tool.

---

## 5. Grain & Snapshot Strategy

| Table | Grain |
|---|---|
| **Forecast Accuracy** | Item × Warehouse × Fiscal Date × Forecast Period (2wk/30d/60d/90d/120d) |
| **Demand Data** | Item × Warehouse × Fiscal Month |
| **Logility - Current Mo** | Item × Location × FileDate (daily, current month only) |
| **SupplyPlanDetail** | Item × Warehouse × Fiscal Week |
| **Placements** | Item × Account × Month |
| **Sales Trend - AFI / Retail / Ashcomm** | Item × Fiscal Date (monthly aggregated) |
| **ATP Week Ending** | Item × Warehouse × ATPWeek |
| **Nailed** | Item × Store × Date (current day only) |
| **Inventory Turns** | Item × Warehouse × Fiscal Week (52-week rolling) |
| **On Time** | Item/Whse × Fiscal Wk End Date |
| **Current SS/SI** | Item × Warehouse × Week (current snapshot) |
| **ATP (2)** | Item × Warehouse × ATPWeek (morning version = InsertedVersion 2, afternoon = 3) |

**Snapshot strategy:** Mixed — mostly current-snapshot with some historical trend. Forecast Accuracy covers 2+ years of history; Sales Trends cover 2+ years. Nailed is latest-day-only. ATP(2) keeps 13 weeks of version history for morning/afternoon comparison.

---

## 6. Dimensions Used

### Conformed dimensions with direct relationships:

| Dimension | Table | Cols | Notes |
|---|---|---|---|
| **Product** | `Product Details` | 103 columns, 11 calc | Central hub — 25+ relationships from fact tables. Calculated: `Finished Goods`, `xFuture Status`, `Current Fcst Planner`, `Number of Months Invoicing`, `Invoice Month`, `Item Desc & Color`, `Average Lead Time`, `Lead Time Forecast Period`, `xUnit Price`, `ABC Code`, `ABC/XYZ Code`, `Lifestyle` (PIM), `Standard Color` |
| **Fiscal Calendar** | `AshleyFiscalCalendar` | 29 cols | 15+ relationships from fact tables |
| **Warehouse** | `Warehouse Master` | 7 cols | 15+ relationships |
| **Status** | `Status` (hidden) | 3 cols | Item status lookup |
| **Planner** | `Planner` (hidden) | 2 cols | FC planner lookup |
| **Unit Price** | `Unit Price` (hidden) | 2 cols | Unit price lookup |
| **DRP Planner** | `DRP Planner` (hidden) | 4 cols | DRP planner by Item-Whse |
| **Make-Buy Code** | `Make-Buy Code` (hidden) | 4 cols | Make-buy classification |
| **ABC Account** | `ABC Account` | 1 col | Account ABC classification |
| **Reporting Business Type** | `Reporting Business Type` | 1 col | Channel classification |

### Key calculated columns:

**Product Details:**
- `Finished Goods` = IF (ItemClassCode LIKE 'Z%K' OR ZARP/ZAHM) → "non-finished good"
- `Number of Months Invoicing` = `DATEDIFF(InvoiceMonth, TODAY(), MONTH)` — uses TODAY()
- `Invoice Month` = parses `Initial Invoice Period` → "MM/15/YYYY"
- `Average Lead Time` = `RELATED(Vendor/SKU Lead Time[AverageVendorLeadTime])`
- `ABC Code` = `RELATED(ABC Codes[ABC Logility])`
- `ABC/XYZ Code` = `RELATED(ABC Codes[ABCXYZ Code])`

**SupplyPlanDetail:**
- `SI Negative` = `IF(spdShippableInventory < 0, spdShippableInventory, 0)`
- `Make-Buy Code` = `RELATED(Make-Buy Code[MK_BuyCODE])`
- `PlannedTransferIn` / `UnplannedTransferIn` = splits by Make-Buy Code
- `SI w/o Net Forecast` = `SI + NetForecast`
- `BeginningOnHandQty` = IF same week as Run Date → beginning balance, else SI-SS
- `Max Run Date Flag` / `Run Date Filter` = latest-run identifcation

**Logility - Current Mo:**
- `Go Back` = `IF(WEEKDAY(FileDate)=2, -3, -1)` — handles weekend gap (Friday→Monday = −3)
- `Date of Forecast` = FileDate − GoBack (previous business day)

**Sales Trend - AFI:**
- `Wks/Mo` = SWITCH mapping fiscal month 1–12 → 4 or 5 weeks
- `Weekly Qty Ordered` = `QtyOrdered / Wks/Mo`
- `Whse Group` = SWITCH: 335→335, 232→232, C/CNW→C/CNW, else AFI

---

## 7. Duplication / Consolidation Signals

1. **Demand Fulfillment DF rate ≠ Product Review (NEW) DF rate.**
   - This model: `(FD + SI_neg) / FD` — **no NetForecast**
   - NEW model: `(FD + NF + SI_neg) / (FD + NF)` — **with NetForecast**
   Cross-report comparison of "Total % Cust Orders Covered" is invalid. Same metric name, different formula.

2. **5 DF rate variants within this model alone:**
   - `Demand Fulfillment[Total % Cust Orders Covered]` — FD only
   - `SupplyPlanDetail[*% COC]` — FD only (different source table)
   - `SupplyPlanDetail[*% COC w/ NetForecast]` — FD+NF
   - `SupplyPlanDetail[*SCP Team DF_2]` — DF/(FD+NF)
   - `SupplyPlanDetail[*SCP Team DF_2 w/o NetForecast]` — DF/FD

3. **3 Sales Trend tables with near-identical patterns** — AFI (27 meas), Retail (20 meas), Ashcomm (20 meas). Same structure: Total Qty, Rolling 3Mo, 3Mo Avg, Previous Year, YTD Current/Previous, YTD YoY % Change. 67 total measures for one pattern.

4. **Logility - Current Mo day-over-day pattern repeated** — 6 months × 4 measures = 24 measures for one formula pattern. Parameterized with month index 0–5.

5. **CurrentProductDetails (PowerPlatform.Dataflows) and Product Details (PowerBI.Dataflows)** — two product detail tables from different dataflow APIs accessing the same underlying entity.

6. **ATP Week Ending and ATP (2)** — same source table (`ATPWeekEnding`) with different date filters: 6 weeks vs 13 weeks. Measures `ATP - Morning Verison` and `ATP - Afternoon Verison` (note typo "Verison") filter by `InsertedVersion` = 2 vs 3.

7. **SupplyPlanDetail has duplicate "Current SS/SI" table** — same SPD data but pre-filtered for current week. 7 dedicated measures.

---

## 8. Open Questions

1. **This model vs. Product Review (NEW) — which is the primary?** Two models serve the same purpose with different DF rate formulas. Which one is the official version? Are planners confused when numbers disagree?

2. **Why are two Product Detail tables loaded?** `CurrentProductDetails` (PowerPlatform API, 90 cols) and `Product Details` (PowerBI API, 103 cols). The latter has 11 calc columns. Is `CurrentProductDetails` a transitional artifact?

3. **Nailed (store inventory) — what decisions does it drive?** Daily-store-level data. Used for replenishment, markdown, or in-store availability scoring?

4. **ATP Morning vs. Afternoon versions** — `InsertedVersion 2` vs `3`. What do these represent? Two official runs per day? Or corrections/updates?

5. **`Go Back = -3` on Monday** — handles weekend gap. But other holidays (Christmas, Thanksgiving) could create longer gaps. Is there manual override?

6. **Retail Sales Union of 6 queries** — 3 written sales sources (Homes Corp, Licensee, Storis) + 3 invoiced sales sources. Are any other channels missing? Ashcomm is a separate table.

7. **`Finished Goods` classification** excludes Z__K, ZARP, ZAHM items. Are these components, raw materials, or non-sellable items? This filter is applied consistently across the model.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Location | What it does |
|---|---|---|
| `Go Back = IF(MONDAY, -3, -1)` | Logility Current Mo calc | Skips weekends for day-over-day comparison; breaks on multi-day holidays |
| `Wks/Mo = SWITCH(...)` | Sales Trend AFI calc | Fiscal month 3/6/9/12 → 5 weeks; others → 4. Based on 4-5-5 fiscal calendar |
| `WHERE ItemClassCode NOT LIKE 'Z__K'` | Multiple SQL sources | Excludes kit/component items from forecast, ATP, and SS views |
| `WHERE spdItem NOT LIKE '%UN'` | Multiple SQL sources | Excludes bedding kits from ATP/SS views |
| `WHERE spdItem NOT LIKE '%SW'` | Multiple SQL sources | Excludes swatch items |
| `WHERE spdItem NOT LIKE '%CARD'` | Multiple SQL sources | Excludes cardboard card items |
| `ItemClassCode <> 'ZARP' / 'ZAHM'` | Multiple SQL sources | Excludes specific class codes |
| `@Startdate = FiscalYear - 2` | Multiple SQL sources | Date anchor = 2 years back from start of current fiscal year (defines history window) |
| `@Enddate = DATEADD(DAY,-1,GETDATE())` | Sales Trend SQL | Excludes today — data ends yesterday |
| `Warehouse IN (1,5,ECR,17,15,232,28,335,16,42)` | ATP SQL | WH list — not documented |
| `[ituCalctype] = '52'` | Inventory Turns SQL | Filters to 52-week calculation type |
| `ForecastPeriod` classification (2wk/30d/60d/90d/120d) | Forecast Accuracy SQL | Based on `Source File Name` LIKE pattern matching |

---

## 10. Comparability / Consistency

1. **DF rate ≠ Product Review (NEW).** Same-named metric, different formula. This is the single most important comparability issue in the Product Review family.

2. **5 DF rate variants within this model** — a user comparing `*% COC` (FD only) vs `*% COC w/ NetForecast` (FD+NF) on different report tabs may see different coverage rates for the same item-week. The NetForecast inclusion always produces higher (more optimistic) COC rates.

3. **Two Product Detail tables** — if a visual uses `Product Details` columns and another uses `CurrentProductDetails`, they may reference the same item via different relationship paths but with different column availability.

4. **Forecast Value Added = wMAPE − Naive wMAPE** — negative FVA means the promoted forecast is worse than a naive (lag) forecast. This is a standard FVA interpretation but important context for interpretation.

5. **CoV of weekly demand** in Sales Trend — unique to this model. Can be compared to ABC XYZ classification's CoV in BridgeItemABC from Demo_Inventory Health, but the time windows and calcuation methods differ.

---

## Key Highlights

**Largest report in workspace** — 48 tables, **218 measures** (highest in any model), 3.4 MB BIM. The original comprehensive product review, serving 15+ analytical domains.

**All-dataflow architecture** — no SharePoint, no Excel. Dataflows from 2 workspaces (15+ in `f0e1bc90`, core dims in `a47e4573`). Second-cleanest architecture after GF FC Tool.

**🔴 DF rate differs from Product Review (NEW).** This model = `(FD + SI_neg) / FD`. NEW = `(FD + NF + SI_neg) / (FD + NF)`. Cross-report comparison invalid despite identical measure name.

**🔴 5 DF rate variants within model.** `*% COC`, `*% COC w/ NetForecast`, `*SCP Team DF_2` (with/without NF). Same concept, 5 implementations.

**Unique data sets:**
- **Nailed** (retail store-level inventory) — only model with this
- **Retail Sales** (3 sub-channels: Homes Corp, Licensee, Storis) — 6-UNION SQL
- **Ashcomm** (commissioned channel) — separate table
- **PIM** (brand name, Ashley Homestore flags) — product enrichment
- **ColorMaster** (warehouse-to-retail color mapping)
- **Seasonality L2 factors**
- **Weekly CoV** (coefficient of variation) — statistical demand variability

**Key calculated column patterns:**
- `Go Back` delta = handles weekend gap in day-over-day comparison
- `Wks/Mo` = hardcoded SWITCH for fiscal month lengths (4 or 5 weeks)
- `SI Negative` = conditional column for shortfall
- `Make-Buy Code` → splits planned transfers into bought/make categories

**Forecast Accuracy is the most comprehensive in workspace:** wMAPE, sMAPE, MASE, MAPE, RMSE, MSE, CoV, FVA, naive benchmark, scaled errors — 58 measures spanning every major forecast error metric.

---

*Analysis based on BIM definition extracted 2026-07-09. BIM saved to [bim/Product_Review.bim](bim/Product_Review.bim). Detailed extraction log at [bim/Product_Review_extracted.txt](bim/Product_Review_extracted.txt). No bundle indexes were modified.*
