# GF FC Tool — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `18528d09-0770-4aa3-9f02-fb9acab50101`  
**Report ID:** `063db768-b7e4-4403-b8d6-baf336b1657e`  
**Analysis Date:** 2026-07-09  
**Model Size:** ~40+ tables (6 dim + 6+ core fact + ~30 forecast measure tables); **~190+ DAX measures** (86 in `_Measures`, ~60 in `_CF Measures`, ~30 in individual fact tables); Compatibility Level 1600  
**BIM File:** [bim/GF_FC_Tool.bim](bim/GF_FC_Tool.bim) — 1,177 KB  
**Note on BIM:** Contains ~800KB of linguistic metadata (Q&A / Cortana NLU thesaurus). Model data is ~350KB after stripping.

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> Across the entire GF (Ground Floor / Logility L1) planning hierarchy, how does the current working forecast compare to the current cycle forecast — what is the actual vs. forecast demand gap, the consumption rate, the seasonally-adjusted trend, and the forecast accuracy at every level (L1–L4)?

This is a **multi-line hierarchy forecast review tool** — not a single report but a **suite of analytical views** covering:

1. **Forecast Consumption** — are orders pacing against target consumption rates by Customer Group × Collective Class (CusCC) and Customer Group × Warehouse (CusWH)?
2. **Forecast Change / Gap Analysis** — current vs. working forecast gap; CRD (Current Request Date) change impact; order vs. forecast variance
3. **Forecast Accuracy** — wMAPE at L1 through L4 levels; naive benchmark; forecast value added (FVA)
4. **Seasonal / Trend Analysis** — 3-month rolling average; trend line; seasonally-adjusted projections
5. **Bedroom-Dining Balancing** — item-level supply-demand balancing for bedding components
6. **Imbalance Detection** — which combinations of customer group / collective class / series are imbalanced on forecast and/or safety stock?

**Primary chain links served:** **Demand** (actual orders, forecast at L1–L4, seasonal adjustment, consumption patterns), **Forecast** (multiple versions: working, current, cycle), **Forecast Accuracy** (wMAPE, naive benchmark, FVA), **Supply** (imbalance detection via BedroomDining Balancing).

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Review forecast consumption rate** — is the customer group pacing on target? Are weekly orders consuming at the expected rate? | Demand Planner / Forecast Analyst | **Weekly** | **Performance/Governance** |
| **Approve or override forecast change** — when working FC vs. current FC gap exceeds threshold | Demand Planner / Manager | Weekly | **Performance/Governance** |
| **Adjust CRD-based demand view** — understand how order timing shifts affect demand position | Demand Planner | Weekly | **Operational** |
| **Evaluate forecast accuracy by planning level** — L1–L4 wMAPE, naive fva, FVA by planner/collective class | Planning Manager / WBR Leadership | Monthly | **Performance/Governance** |
| **Seasonal demand interpretation** — 3-month rolling avg vs. trend line vs. seasonally-adjusted projections | Demand Planner | Monthly | **Performance/Governance** |
| **Bedroom-Dining component balancing** — identify and correct supply vs. demand mismatch at CG level | Supply Planner / Demand Planner | Weekly | **Operational** |
| **Imbalance detection** — flag customer group / collective class / series combos where FC% or SS% are misaligned | Planning Manager | Weekly | **Performance/Governance** |
| **Forecast Value Added (FVA)** — measure human overlay vs. statistical forecast improvement | Forecast Analyst | Monthly | **Performance/Governance** |

---

## 3. Key Metrics / Measures

### From `_Measures` (86 measures — key groups)

| Measure Group | Key measures | Purpose |
|---|---|---|
| **Order & FC Variance** | `Total Current Order Qty`, `Total Origin Order Qty`, `Derived Ratios`, `Total Order & FCT`, `FC Qty`, `Derive Ratio Change` | Compare current vs. original request date orders; derive consumption ratios |
| **Forecast Accuracy** | `ABS Forecast Error`, `Forecast Bias`, `L1 PRSLF wMAPE` through `L4 PRSLF wMAPE`, `L1 Naive wMAPE`, `L1 Forecast Value Added` | Accuracy by planning level with naive benchmark |
| **Trend & YoY** | `Total Demand Trend`, `Total Forecast Trend`, `Total Forecast Bias Trend`, `YoY Growth`, `YoY Growth n+1` | Trend analysis, year-over-year changes |
| **Seasonal** | `3M Rolling Avg`, `Total Seas Adj Cur Ord Qty`, `Seas Adj PROL-RSLF Qty`, `Current Trend Line` | Seasonally-adjusted demand patterns |
| **Imbalance** | `Total Imbalanced Series (Overall)`, `Imbalance Ratio (Com)`, `Forecast Gap`, `SS Gap`, `CG Balancing (FC)`, `CG Balancing (SS)` | Bedroom-dining supply-demand imbalance detection |

### From `_CF Measures` (~60 measures — key groups)

| Measure Group | Key measures | Purpose |
|---|---|---|
| **Consumption** | `Goal Consumption CusCC`, `Goal Consumption CusWH`, `Consumption Gap`, `Absolute Consumption Gap`, `Forecast Consumption` | Target vs. actual consumption rates by customer-channel and customer-warehouse |
| **Forecast Gap** | `Working_Total_Forecast`, `CurFC Gap`, `WrkFC Gap`, `Projected CurFC`, `Projected WrkFC` | Working vs. current total forecast comparison |
| **Order Tracking** | `Total Written Order Qty`, `FUTO`, `CRD Open Order`, `Posted Open Order` | Written orders, FUTO, and open order tracking |
| **YTD/YTG** | `Current YTD`, `Current YTD n-1`, `Current YTD YoY`, `Origin YTD`, `Origin YTD YoY`, `FCST YTG`, `Ord + FCST Y0` | Year-to-date and yet-to-go demand analysis |
| **Invoicing/New Items** | `Invoiced`, `Open Order`, `Total Invoiced Less 6m Item Forecast`, `Total Not Invoiced Item Forecast` | New product demand classification |
| **Seasonal Factor** | Multiple seasonality-related measures | Seasonal adjustment logic |

**Key flag: `Derive Flag Color`** in `_CF Measures` — likely a stoplight color indicator for consumption performance.

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`Fact Actuals`** | `ashley-edw.database.windows.net / ashley_edw` — `SupplyChain_Enh.ActualsCustItemWH_AFI` (orig req, cur req, ship week ending; order qty, amount, sales type, status, allocated flag, week diff) | Direct Azure SQL EDW | Medium |
| **`Fact L1 Forecast`** | Same EDW — Logility L1 forecast with `RSLF`, `Promo Lift`, `Forced Forecast`, `Actual Demand`, `Adjusted Demand`, `Valid demands`, `Permanent Component`, `Forecast Model`, `Demand Management Indicator` | Direct Azure SQL EDW | Medium |
| **`Fact FC Accuracy`** | Same EDW — accuracy computation table | Direct Azure SQL EDW | Medium |
| **`Fact CRD Change`** | Same EDW — CRD (Current Request Date) change tracking | Direct Azure SQL EDW | Medium |
| **`Fact Goal Consumption CusCC`** | Same EDW — target consumption rates by Customer Group × Collective Class | Direct Azure SQL EDW | Medium |
| **`Fact Goal Consumption CusWH`** | Same EDW — target consumption rates by Customer Group × Warehouse | Direct Azure SQL EDW | Medium |
| **`Fact Annualize FC`** | Same EDW — annualized forecast computation | Direct Azure SQL EDW | Medium |
| **`Fact Current Forecast`** | Same EDW — current cycle forecast | Direct Azure SQL EDW | Medium |
| **`Fact Seasonal Factor`** | Same EDW — seasonal adjustment factors | Direct Azure SQL EDW | Medium |
| **`Fact L3 Forecast Model`** | Same EDW — L3 forecast model data | Direct Azure SQL EDW | Medium |
| **`Fact BedroomDining Balancing`** | Same EDW — component balancing data | Direct Azure SQL EDW | Medium |
| **`Fact. ABC XYZ`** | Same EDW — ABC/XYZ classification per item | Direct Azure SQL EDW | Medium |
| **~30 FACT_ / L1–L4 tables** | Same EDW — forecast accuracy tree tables | Direct Azure SQL EDW | Medium |
| `Dim Date` | Same EDW — `DimDate` (DateID, FiscalMonthLastDate, FiscalWeekIndicator, etc.) | Direct Azure SQL EDW | Low |
| `Dim Product Detail` | PowerBI Dataflow `346f2aa1...` → `CurrentProductDetails` (with `Product Category`, `Helper Col`, `Exclusive Status`, `Kit Flag`, `Primary Vendor Name - Number` added in PQ) | Governed Dataflow | Low |
| `Dim Customer` | Same EDW — `PowerBI_SupplyChain.CustomerAcctMaster_AFI` | Direct Azure SQL EDW | Low |
| `Dim Warehouse` | Same EDW — warehouse dimension | Direct Azure SQL EDW | Low |
| `Dim Series` | Same EDW — series-level dimension | Direct Azure SQL EDW | Low |
| `Dim Fiscal Month` | Same EDW — fiscal month dimension | Direct Azure SQL EDW | Low |
| `Dim Collective Class` | Same EDW — collective class reference | Direct Azure SQL EDW | Low |

> **No SharePoint. No Excel. No Fabric sources.** Cleanest all-EDW sourcing of any model in the workspace. The 30+ fact tables all come from `ashley-edw` SQL.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Multidimensional — varies by table:

| Table | Grain |
|---|---|
| `Fact Actuals` | Item SKU × Warehouse × FiscalWeekEnding (order header detail) |
| `Fact L1 Forecast` | Item SKU × Warehouse × Forecast Month (Logility L1 monthly forecast) |
| `Fact FC Accuracy` | — likely Item × WH or aggregated (wMAPE calculations reference L1–L4 levels) |
| `Fact Goal Consumption CusCC` | Customer Group × Collective Class (consumption rate targets) |
| `Fact Goal Consumption CusWH` | Customer Group × Warehouse (consumption rate targets) |
| `Fact CRD Change` | Item SKU × — measures impact of Current Request Date changes |
| `FACT_` forecast accuracy tables (L1–L4) | Various planning hierarchy levels |

**Snapshot strategy:** Current-snapshot only with some trend tables. The forecast accuracy hierarchy (L1–L4 with wMAPE, naive, FVA) suggest periodic accuracy computations at defined snapshot dates — the `Fact FC Accuracy` and L1/L2/L3/L4 tables feed the accuracy reporting.

---

## 6. Dimensions Used

| Dimension | Table | Notes |
|---|---|---|
| **Product** | `Dim Product Detail` (91+ cols) | Conformed dataflow; adds `Product Category`, `Helper Col`, `Exclusive Status`, `Kit Flag`, `Primary Vendor Name - Number` via Power Query |
| **Date** | `Dim Date` (DateID, fiscal columns) | Standard `Enterprise_DW.DimDate` |
| **Customer** | `Dim Customer` (`Customer Name`, `Customer Group`, `Customer`, `Customer Desc`, `z_AcctFilter`, `Account Number`, `Account Name`, `Country`) | Local SQL query |
| **Warehouse** | `Dim Warehouse` (WH code, group, location) | Conformed |
| **Series** | `Dim Series` (Item Ext Series Number) | Series-level reference |
| **Fiscal Month** | `Dim Fiscal Month` | Separate fiscal month dimension |
| **Collective Class** | `Dim Collective Class` | CC reference |
| **ABC/XYZ** | `Fact. ABC XYZ` | Item-level classification |

---

## 7. Duplication / Consolidation Signals

1. **~30 "FACT_" forecast accuracy tables** — L1–L4 wMAPE, naive, FVA, forecast components. Each is a separate table (e.g., `FACT:L1 PRSLF wMAPE`, `FACT:L1 Naive wMAPE`, `FACT:L1 Forecast Value Added`, `FACT:L1 RSLF wMAPE`, etc.). These are likely computed in SQL and loaded as pre-aggregated tables. If the logic is the same across levels, a single table with a `Level` dimension would reduce table count from 30+ to 1.

2. **`_Measures` (86 measures) and `_CF Measures` (~60 measures)** overlap conceptually — both have consumption, gap, and order-tracking measures. The separation between "current forecast" and "working forecast" measures across two measure tables suggests an organic split during development.

3. **Multiple YoY measures with different n-1/n+1 suffixes** (`YoY Growth`, `YoY Growth n+1`, `YoY Growth n-1`, `YoY Bottom Up Growth`, `YoY Bottom Up Growth n+1`) — same pattern repeated for regular forecast and "bottom-up" forecast.

4. **`Derive Flag Color`** in `_CF Measures` — likely a color-coding measure for consumption; similar logic exists in `_Measures` for forecast change.

5. **Imbalance measures** — 13 separate imbalance-related measures (`Total Imbalanced Series (Overall)`, `Imbalanced Series (FC Only)`, `Imbalanced Series (SS Only)`, `Imbalance Ratio (Com)`, `Imbalance Ratio (FC)`, `Imbalance Ratio (SS)`, etc.) that could collapse to a parameterized pattern.

---

## 8. Open Questions

1. **What distinguishes "Current" from "Working" forecast in this model?** Two different forecast tables (`Fact Current Forecast` vs. WorkingForecast via `_CF Measures`). Is "Working" the actively-managed planner forecast and "Current" the latest Logility stastical output?

2. **What are the L1–L4 planning levels?** L1 = Company? L2 = Division? L3 = Category? L4 = SKU? The measure names reference all four but no dimension table defines them.

3. **`Derive Flag Color`** — what colors and what thresholds? Green/Yellow/Red based on what metric?

4. **BedroomDining Balancing** — is this specifically for bedding kits/component items? The column list includes "CG" (Customer Group) balancing for both FC and SS.

5. **Seasonal Factors** — the model has a separate `Fact Seasonal Factor` table. Are these Logility-generated factors or manually maintained?

---

## 9. Business Assumptions

- All forecast "versions" assume a consistent snapshot anchor (no visible date-series tracking across multiple forecast versions in the measure definitions)
- ABC/XYZ classification is snapshot-based from `Fact. ABC XYZ`
- The model assumes wMAPE as the primary accuracy metric across all 4 levels
- No hardcoded magic number constants were identifiable from metadata alone (most thresholds appear to be in EDW SQL)

---

## 10. Comparability

- All forecast accuracy metrics across L1–L4 use wMAPE as the base — should be cross-comparable
- `_Measures` and `_CF Measures` may produce different "forecast gap" numbers because they reference different source tables — careful cross-visual comparison needed
- The model uses `CurReqWkEnding` and `OrigReqWkEnding` as two date dim relationships — same split seen in other models (e.g., GF Act+Fcst)

---

## Key Highlights

**Largest measure set in workspace** — ~190+ DAX measures across 86 + 60 + 30+ distributed across `_Measures`, `_CF Measures`, and individual fact tables.

**All-EDW sourcing — cleanest architecture.** Unlike Forecast Change (WoW) which has 16 SharePoint lists, or FCA Audit which has 2 SharePoint Excels, GF FC Tool sources **everything** from `ashley-edw` via SQL. No SharePoint, no Excel, no dataflows.

**Multi-hierarchy forecast analysis:** L1–L4 planning levels, wMAPE accuracy, forecast value added (FVA), naive benchmark — the most complete forecast analytics suite in the workspace.

**~30 forecast accuracy tables** — one per metric per planning level (L1 PRSLF wMAPE, L2 PRSLF wMAPE, L1 Naive wMAPE, L2 Naive wMAPE, ...). Massive consolidation opportunity if a `Level` dimension were introduced.

**Two separate measure tables (`_Measures` and `_CF Measures`)** — 146 measures total spanning order tracking, consumption, YTD/YTG, seasonal, YoY, and imbalance detection. Some overlap suggests organic growth rather than intentional design.

**Unique features in workspace:**
- Forecast Value Added (FVA) measurement — only model tracking human-vs-statistical forecast improvement
- BedroomDining Balancing — only operational supply-demand balancing logic in workspace
- Imbalance detection by FC% and SS% — unique dual-dimension imbalance flag

**Clean dim model:** 6 dimension tables + ABC/XYZ classification table. All conformed from dataflow or EDW. No orphaned dimensions.

---

*Analysis based on BIM definition extracted 2026-07-09. BIM saved to [bim/GF_FC_Tool.bim](bim/GF_FC_Tool.bim).  
Note: BIM contains ~800KB of linguistic/Q&A metadata. Model structure extracted from cleaned 350KB subset.  
No bundle indexes were modified.*
