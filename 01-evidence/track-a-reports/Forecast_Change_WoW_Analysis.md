# Forecast Change (WoW) — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `d2f91f0f-5735-449b-8147-2be5ea5c0214`  
**Report IDs:** `847c9339` (Forecast Change), `416ffa3e` (Forecast Change - WoW)  
**Analysis Date:** 2026-07-09  
**Model Size:** 57 tables (10 facts + 5 dims + 6 archive + 10 SharePoint + 3 Excel + 3 merge/join + many local date tables); **34 DAX measures** (7+3+1+23 across 4 measure tables); Compatibility Level 1600  
**BIM File:** [bim/Forecast_Change_WoW.bim](bim/Forecast_Change_WoW.bim) — 7.3 MB TMSL (largest model in workspace)  
**Model ID Note:** Semantic model name is "Forecast Change - WoW" (hyphen, "WoW"); API references use this name, not "Forecast Change".

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For each item/collective class and forecast month, how does the current week's forecast snapshot differ from the previous week's snapshot — does the change exceed pre-defined thresholds, and has it been reviewed, approved, and pushed to supply?

This is a **forecast change management and approval workflow** report. It tracks forecast changes week-over-week at the **Item Ext Series Number** level, surfaces changes that exceed collective-class-specific thresholds, and integrates with an **ad-hoc push approval workflow** for manual forecast adjustments.

**Three layers of analysis:**
1. **Current vs. previous snapshot** — PRSLF (resultant forecast + promo lift) changes between this week and last
2. **Threshold-based flagging** — does the % change AND absolute quantity change exceed thresholds set per collective class? Y/N for Over Both / Over Any
3. **Approval workflow integration** — has the change been reviewed ("Weekly Review Status"), approved ("Approved to Push"), and pushed to SP?

Plus **alert/issue dashboards** from SharePoint lists tracking 8 alert types: Check Demand, Check FM, Forecast Error, Inhibited, L2 Issue, Promo to 0, Check FUTO, Large FC Change, Imbalance.

**Primary chain links served:**

| Link | How served |
|---|---|
| **Forecast (change management)** | Core function — `FACT_Series_WorkingForecast` vs. `FACT_Series_CurrentForecast` (current month snapshot vs. previous month snapshot); `Merge1` joins them with approval data |
| **Forecast (approval workflow)** | `FACT _ Adhoc Explanation` / `ExplanantionwithDate` — manual push tracker; `Weekly Review Status` gate |
| **Forecast thresholds** | `FACT_Threshold Review` — per-Collective-Class ABS % change and ABS quantity change thresholds |
| **Forecast alerts/issues** | 8 SharePoint list tables + hidden archive copies — operational issues flagged for planner action |
| **Product lifecycle context** | `Dim Series Status` — series-level attributes (current status, future status, vendor, exclusive comments) |

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Review changes that exceed both thresholds** — "Over Both Thresholds" flag | Life Cycle Planner / Demand Planner | **Weekly** (WoW forecast review) | **Performance/Governance** — determine if adjustment is needed |
| **Approve or reject forecast push to Supply** — `Push to Supply 2` flag: "Large FC, need to push" / "Review to push if needed" / "Ad-hoc pushed" | Life Cycle Planner → Manager | Weekly | **Operational** — formal gate for forecast push |
| **Document ad-hoc pushes** — `FACT _ Adhoc Explanation` captures reason code, explanation, category validation | Demand Planner | Weekly (ad hoc) | **Operational** — audit trail |
| **Triage forecast alerts** — Check Demand, Check FM, Forecast Error, Inhibited, Imbalance, L2 Issue, Promo to 0, Check FUTO, Large FC Change | Demand Planner / Forecast Analyst | Weekly | **Operational** — identify and prioritize issues |
| **Monitor collective class threshold compliance** — are alerts being reviewed/closed (`Action Status`)? | Planning Manager | Monthly | **Performance/Governance** — planner accountability |
| **Aggregate alert history** via `_Record` table — consolidated view of all alert types; archive/non-archive combined | Forecast Analyst | Weekly | **Performance/Governance** — trend of alert volume by type |
| **View UC (Unified Product Journals) context** — planner journal entries cross-linked to series for decision support | Life Cycle Planner | Weekly | **Performance/Governance** — context for forecast change decisions |
| **Threshold configuration** — `FACT_Threshold Review` sets per-CC % and qty thresholds; configurable by Collective Class | Planning Manager / Admin | Monthly (as needed) | **Performance/Governance** — rule parameterization |

---

## 3. Key Metrics / Measures

### From `FACT_Series_WorkingForecast` (7 measures)

| Measure | Business meaning | Logic | Flag |
|---|---|---|---|
| `Current Forecast` | Sum of this week's forecast (working snapshot) | `SUM(FACT_Series_WorkingForecast[Forecast])` | |
| `Current PRSLF` | Sum of this week's PRSLF (resultant + promo) | `SUM(FACT_Series_WorkingForecast[PRSLF])` | |
| `Current Promo` | Sum of this week's promo lift | `SUM(FACT_Series_WorkingForecast[Promo])` | |
| `Forecast Variance` | Absolute change: current − previous forecast | `[Current Forecast] − [Previous Forecast]` | |
| `Alert Count` | Count of item series exceeding BOTH thresholds | `COUNTROWS(FILTER(VALUES(z_ProductDetails[Item Ext Series Number]), [Over Both Thresholds]="Yes"))` | |
| `ABS % Change` | Absolute % change in PRSLF | `ABS(DIVIDE(Current − Previous, Previous))` | ⚠️ 0/0 returns BLANK; denominator=0 returns 1 |
| `Alert Count (ANY)` | Count of item series exceeding ANY threshold | Same as Alert Count but uses `Over Any Threshold` | |

### From `FACT_Series_CurrentForecast` (3 measures)

| Measure | Business meaning |
|---|---|
| `Previous Forecast` | Sum of prior snapshot's forecast |
| `Previous PRSLF` | Prior snapshot's PRSLF (BLANK treated as 0) |
| `Previous Promo` | Prior snapshot's promo lift |

### From `Merge1` (23 measures — core analytical engine)

| Measure | Business meaning | Flag |
|---|---|---|
| `Working Fcst`, `Working_PRSLF`, `Working_Promo` | This week's values from Merge1 | |
| `PRSLF Variance`, `RSLF Variance`, `Promo Variance` | Absolute change vs. previous week | |
| `%Change RSLF` | `Working Fcst / Previous Forecast − 1` | |
| `% Change PRSLF` | `DIVIDE(Current−Previous, Previous)` with 0-handling | |
| `ABS PRSLF Qty Change` | SUMMARIZECOLUMNS by Collective Class → SUMX(ABS(Delta)) — absolute qty change | ⚠️ complex VAR/TABLE/SUMX pattern |
| `Over Percent Threshold` | `IF %Change > Threshold% (from FACT_Threshold Review), "Yes", "No"` | |
| `Over Quantity Threshold` | Same for absolute qty change | |
| `Over Both Thresholds` | "Yes" only if BOTH percent and qty thresholds exceeded | 🚨 **drives `Alert Count` and `Push to Supply`** |
| `Over Any Threshold` | "Yes" if EITHER threshold exceeded | |
| `Threshold - ABS %` / `Threshold - ABS Quantity` | Selected collective class's threshold values | |
| `Push to Supply 2` | **Three-state workflow flag**: "Ad-hoc pushed" (if already approved), "Large FC, need to push" (if Over Both), "Review to push if needed" (if Over Any but not Both) | 🚨 **core workflow decision** |
| `Review Ad-hoc pushed` | Count of series with Push to Supply = "Ad-hoc pushed" | |
| `Review Large FC, need to push` | Count flagged as "Large FC, need to push" | |
| `Review to push if needed` | Count flagged as "Review to push if needed" | |

### From `FACT_Threshold Review` (1 measure)

| Measure | Business meaning |
|---|---|
| `Measure` | Empty placeholder measure (no expression) |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`FACT_Series_WorkingForecast`** | `ashley-edw.database.windows.net / ashley_edw` — `SupplyChain_Enh.DemandForecastSnapshot` latest snapshot, aggregated by Item Ext Series Number, Fiscal Month, Collective Class, Customer Group | Direct Azure SQL EDW | Medium |
| **`FACT_Series_CurrentForecast`** | Same EDW — `SupplyChain_Enh.CurFcstSnapshotDaily` **1 month prior** (`DATEADD(MONTH, -1, max snapshot)`) | Direct Azure SQL EDW | Medium — uses month-old snapshot as "previous" |
| **`FACT_Threshold Review`** | **SharePoint Excel** — `..._Vietnam Files/3. Forecast Change/Company Level/Threshold - by Collective Class.xlsx` | **SharePoint Excel** | ⚠️ **HIGH** — manual file, defines critical threshold values |
| **`FACT _ Adhoc Explanation`** | **SharePoint Excel** — `...Ad Hoc Push to SP Request Tracker.xlsx` | **SharePoint Excel** | ⚠️ **HIGH** — manual push approval log |
| **`Unified Product Journals`** | **SharePoint Excel** — `..._Product_Journal_UNIFIED_MASTER.xlsx` | **SharePoint Excel** | ⚠️ **HIGH** — same file flagged in Product Review (NEW) |
| **`Dim Series Status`** | Same EDW — `PowerBI_SupplyChain.CurrentProductDetails` + `ForecastCommonContainer_Logility` + `VendorMaster` — series-level aggregated SQL | Direct Azure SQL EDW | Medium |
| **`FACT_Input from Category`** | **SharePoint Excel** — `...FC Change Manual Dec2025.xlsx` | **SharePoint Excel** | ⚠️ **HIGH** — manual category input |
| **`Frequency`** | **SharePoint Excel** — `...AlertName-Type.xlsx` | **SharePoint Excel** | Medium |
| **8 alert tables** (Forecast Error, Inhibited, L2_Issue, Promo to 0, Check Demand, Check FM, Large FC Change, Imbalance) + 2 Check FUTO | **SharePoint Lists** — `https://masterashley.sharepoint.com/sites/supplychain-DemandPlanning`, 10 different list IDs | **SharePoint Lists** | ⚠️ **HIGH** — 10 independent SharePoint lists; fragile column removal patterns |
| **6 archive alert tables** | Same SharePoint lists (past-dated versions) | **SharePoint Lists** | Medium — preserved as hidden archive copies |
| `z_DimDate` | Same EDW — full `Enterprise_DW.DimDate` (73 columns, both calendar AND fiscal) | Direct Azure SQL EDW | Low |
| `z_ProductDetails` | PowerBI Dataflow `346f2aa1...` → `CurrentProductDetails` | Governed Dataflow | Low |
| `z_WarehouseMaster` | Same dataflow → `WarehouseMaster` | Governed Dataflow | Low |
| `z_VendorMaster` | Same EDW — `PowerBI_SupplyChain.VendorMaster` | Direct Azure SQL EDW | Low |
| `z_CustomerMaster` | Same EDW — `AFISales_DW.DimCustomers` (local SQL query) | Direct Azure SQL EDW | Low |
| `_Record` | Power Query — `Table.Combine` of all archive + current alert tables (18 source tables) | PQ Combine | Medium — consolidation of all alert tables; fragile if columns change |
| `FACT _ Adhoc Explanation` | **SharePoint Excel** — `...FC Change Manual Dec2025.xlsx`, sheet `Table2` | **SharePoint Excel** | ⚠️ **HIGH** — manual input; filename suggests Dec 2025 data (may be stale) |

---

## 5. Grain & Snapshot Strategy

**Primary grain:** **Item Ext Series Number (Series) × Fiscal Month** — aggregated, no warehouse-level.

| Table | Grain |
|---|---|
| `FACT_Series_WorkingForecast` | Item Ext Series Number × Fiscal Month (summed across warehouses and customer groups) |
| `FACT_Series_CurrentForecast` | Item SKU × Fiscal Month (same source, prior snapshot) |
| `Merge1` | Item Ext Series Number × Fiscal Month × FiscalWeekIndicator — enriched with explanation data |
| `Dim Series Status` | Series Number — one row per series (current attributes) |
| 8 alert tables | Individual alert/issue records per series/warehouse at point-in-time |

**Snapshot strategy:**
- `FACT_Series_WorkingForecast` = **latest** `DemandForecastSnapshot` (`MAX(dfcSnapshot)`)
- `FACT_Series_CurrentForecast` = **previous month** snapshot (`DATEADD(MONTH, -1, max snapshot)`)
- 8 alert tables = **live SharePoint lists** (current state)
- 6 archive alert tables = **historical snapshots** of same lists (hidden)
- `FACT _ Adhoc Explanation` = manual Excel log of push requests

---

## 6. Dimensions Used

| Dimension | Table | Connected? | Notes |
|---|---|---|---|
| **Product** | `z_ProductDetails` (91 cols) | ✅ | Conformed dataflow; linked via `Item SKU` and `Item Ext Series Number` → `Dim Series Status[Series Number]` |
| **Date** | `z_DimDate` (73 cols) | ✅ — 12 relationships | Full EDW DimDate with both calendar AND fiscal columns (unlike most other models which use the `AshleyFiscalCalendarV2` dataflow) |
| **Customer** | `z_CustomerMaster` (1 col visible: `Customer Group`) | ✅ | Minimal; only Customer Group used as a dim |
| **Warehouse** | `z_WarehouseMaster` (11 cols) | ✅ — not directly to fact; likely for warehouse-level alert filtering |
| **Vendor** | `z_VendorMaster` (11 cols) | ✅ — via `z_ProductDetails[Primary Vendor]` |
| **Series Status** | `Dim Series Status` (8 cols) | ✅ | Core dim for this model: `Series Number`, `Current Status`, `Collective Class`, `I/D Code`, `Future Status`, `Exclusive Comment`, `Market Introduced At`, `Vendor Name` |
| **Threshold** | `FACT_Threshold Review` (3 cols) | ✅ — via `dfcCollectiveClass` / `Collective Class` | Per-CC threshold parameters |
| **Product Journal** | `Unified Product Journals` (13 cols) | ✅ — via `Item Series` → `Series Number` and `Channel` → `Customer Group` | Planner context |

**No conformed `z_FiscalCal` — uses `z_DimDate` (raw EDW DimDate with 73 columns)** — different calendar structure than most other models.

---

## 7. Duplication / Consolidation Signals

1. **8 alert tables + 6 archive alert tables + 2 check FUTO tables = 16 near-identical tables.** Each follows the same pattern: SharePoint list → remove columns → rename. They differ only by their SharePoint list ID. The `_Record` table combines 18 of them via `Table.Combine`. This pattern suggests the model should have a single unified alert fact table with an `AlertType` dimension rather than 16 near-identical tables.

2. **Archive vs. live distinction is handled by separate tables with no formal archive date logic** — 6 tables are prefixed `Archive_` and hidden, but there's no shared date-based filtering to distinguish archival vs. current data. The `_Record` table combines all 18 sources indiscriminately.

3. **`Merge1` (19 cols, 23 measures) is the de facto central fact table** — it performs the PQ join between `WorkingwithDate` and `ExplanantionwithDate`, then all 23 measures are defined on it. This concentrates all business logic in one table, which is efficient but makes `Merge1` a pivot point where any refresh failure in any upstream table breaks the entire model.

4. **`FACT_Series_WorkingForecast` and `FACT_Series_CurrentForecast` have almost identical schemas** — same columns (Item SKU, Forecast, Promo, PRSLF, Snapshot Date). They differ only by snapshot filter. These could be a single fact table with a `SnapshotType` dimension.

5. **`Push to Supply` (int64) vs. `Push to Supply 2` (calculated DAX text) in `Merge1`** — `Push to Supply` is an empty int64 column (probably development leftovers). `Push to Supply 2` is the actual DAX-calculated three-state flag. The int64 column should be removed.

6. **`Current Forecast` is in both `FACT_Series_WorkingForecast` and `Merge1`** — `Merge1` gets its own `Working Fcst` measure while also having access to the series table's measures via relationship.

---

## 8. Open Questions

1. **"Previous" snapshot = 1 month before current (`DATEADD(MONTH, -1)`)?** The `FACT_Series_CurrentForecast` SQL uses `DATEADD(MONTH, -1, @upper_ss)` as the lower snapshot bound. This means "current" vs. "previous" is 1 calendar month apart, **not** 1 week. The report is titled "Forecast Change - WoW" (Week over Week) but the data snapshots are month apart. Is "WoW" a misnomer, or is there a weekly filter applied elsewhere?

2. **16 SharePoint list tables + 2 SharePoint Excel files managed by who?** The 8 alert types come from SharePoint lists under `supplychain-DemandPlanning`. Who populates these — automated processes from Logility, or manual entry by planners? If they're auto-generated, is there a reason they're SharePoint lists and not EDW tables?

3. **`FACT_Threshold Review` is a SharePoint Excel file** with per-Collective-Class thresholds that drive the entire flagging/alert system. Who updates this file, how often, and is there version control? A wrong value here can cause all Over Both/Over Any flags to misfire.

4. **Filename `FC Change Manual Dec2025.xlsx`** — this was current as of Dec 2025. Has the file been renamed or is this still the active manual input file? If it's Dec 2025 data, it's now 7+ months old.

5. **`_Record` table combines all 18 alert tables** — what is the deduplication strategy? If the same alert appears in both an archive and a current table (possible if the SharePoint list was migrated), `_Record` would double-count it.

6. **`z_DimDate` includes both Calendar and Fiscal date columns** — 73 columns total. This is the largest date dimension in any model. Was this necessary because the SharePoint lists use calendar dates while the EDW forecast uses fiscal dates?

7. **`Alert Count` uses `FILTER(VALUES(z_ProductDetails[Item Ext Series Number]), ...)`** — this filters by item series, not by individual SKU or warehouse. If the alert tables have warehouse-level alerts, the count might not reconcile with the threshold-flagged series count.

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`DATEADD(MONTH, -1, upper_ss)`** | `FACT_Series_CurrentForecast` SQL | Defines "previous" snapshot as 1 month before latest | **No** — "Week over Week" suggests 1 week; model uses 1 month |
| **`DATEADD(MONTH, -1, @upper_ss)`** (implicit range) | Same SQL | `SET @lower_ss = DATEADD(MONTH, -1, @upper_ss)` then query uses `BETWEEN @lower_ss AND @upper_ss` — imports 1 month of prior snapshot data | **No** — month range assumption |
| **Threshold % and ABS qty** per CC | `FACT_Threshold Review` Excel | User-configurable per-collective-class parameters | **Partially** — thresholds are visible in the Excel file; no version control |
| **Aggregation to Series level** (no warehouse) | Both FACT SQLs | Forecast summed across all warehouses and customer groups for each Item Ext Series Number | **No** — if warehouse mix changes, series-level aggregate can mask composition shifts |
| SharePoint list columns removed hardcoded | All Power Query queries | 20+ columns removed by name from each SP list (`"Modified"`, `"Modified By"`, `"Color Tag"`, `"Compliance Asset Id"`, `"ID"`, etc.) | **No** — if a SharePoint column is renamed, the query silently includes it or errors |

---

## 10. Comparability / Consistency

1. **"Current" vs. "Previous" snapshot gap is ~1 month, not 1 week.** Despite the report being called "Forecast Change - WoW," the snapshots are compared one calendar month apart. If a user expects "this week vs. last week," the actual change measured is month-to-month, missing interim changes.

2. **`FACT_Series_WorkingForecast` uses `DemandForecastSnapshot` while `FACT_Series_CurrentForecast` uses `CurFcstSnapshotDaily`.** Two different EDW tables for current and previous. These are not the same underlying view — `CurFcstSnapshotDaily` may have different aggregation logic than `DemandForecastSnapshot`. Any difference in the "previous" vs. "current" numbers could be partially due to source table differences, not real forecast changes.

3. **Alert tables have slightly different schemas.** `Large FC Change` has `Original Quantity`, `Current Quantity`, `Change Quantity` columns. `Forecast Error` has `FUTO`, `This Level ABS`, `Upper Level ABS Error`. `Imbalance` has `Imbalance FC%`, `Bed Size`, `Component Type`. `_Record` handles the schema differences by keeping all columns (many become blank for incompatible alert types). This makes cross-alert-type comparisons in `_Record` unreliable.

4. **`z_DimDate` (calendar + fiscal) sits alongside LocalDateTables for various date relationships** — this is the same pattern as `Dates` + LocalDateTables in Demand Sensing Report. The multiple date table architecture (one main `z_DimDate` + 11 LocalDateTables) reflects the mixed calendar/fiscal date needs of the diverse source data.

---

## Key Highlights

**Largest model in the workspace** — 57 tables, 34 DAX measures, 7.3 MB TMSL BIM. Complex mix of EDW SQL, SharePoint lists, SharePoint Excel, and Power Query transformations.

**Core business process: WoW Forecast Change Review with approval workflow**
- Threshold-based flagging (per-collective-class % and qty thresholds)
- Manual push approval workflow (ad hoc + formal review)
- 8 alert types from SharePoint lists, cross-referenced to forecast changes

**⚠️ Key concern: WoW vs. actual month-apart snapshot comparison.** Despite the "Week over Week" report name, the data compares snapshots 1 calendar month apart. This may mislead users who expect a true week-over-week view.

**⚠️ `FACT_Series_WorkingForecast` (DemandForecastSnapshot) vs. `FACT_Series_CurrentForecast` (CurFcstSnapshotDaily)** — two different EDW tables for current vs. previous. Structural source mismatch means part of the "variance" could be from table logic differences, not actual forecast changes.

**⚠️ 16 SharePoint list tables + 3 SharePoint Excel files** — heavy reliance on ungoverned manual sources. One file named `FC Change Manual Dec2025.xlsx` may be 7+ months stale.

**⚠️ `FACT_Threshold Review` Excel drives the entire flagging system** — thresholds for all Collective Classes. No version control, no audit trail. If this file breaks, the Over Both/Over Any flags break silently.

**Architecture strengths:**
- Central `Merge1` table with 23 measures keeps analytical logic in one place
- `_Record` table consolidates 18 alert source tables
- `Push to Supply 2` measure formalizes a 3-state workflow decision
- Threshold parameters are user-configurable (if maintained) rather than hardcoded

---

*Analysis based on BIM definition extracted 2026-07-09. BIM saved to [bim/Forecast_Change_WoW.bim](bim/Forecast_Change_WoW.bim). No bundle indexes were modified.*
