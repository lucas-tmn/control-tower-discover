# Report Analysis: Supplier ABC Analysis

**Workspace:** SCP Global Team  
**Model ID:** `aa3993c2-95e8-4b07-9cf3-a67e4a61d5a6`  
**Source:** Azure SQL `Ashley-edw.database.windows.net` / `ASHLEY_EDW` + SharePoint Excel  
**Analysis Date:** 2026-07-13  
**Analyst:** Claude Code (automated model inspection)

---

## 1. Supply-Chain Question & Chain Link

**Core question this report answers:**  
*"Which import suppliers are A, B, or C class by forward demand volume over the next 17 weeks, and does their ABC classification match the manually assigned Vendor Complexity tier?"*

**Chain link served:** **Demand / Supply (Supplier Stratification)**  
This is a **supplier portfolio management** report, not a transactional execution report. It stratifies the supplier base by forward PSW demand volume (PSWContainersCurrentDay, WeekNum 0–17) and compares that data-driven ABC ranking against a manually maintained complexity tier from an Excel file. It exists to answer: *"Are we allocating SCP analyst attention to the right suppliers?"*

Secondary outputs surfaced by the wide `AFI Vendor List` table: per-warehouse minimum buy (`MB WH##`) and days-to-delivery (`DD WH##`) columns — these are reference attributes, not calculated metrics.

No on-time, inventory, or financial data is present.

---

## 2. Decisions Supported

| Decision | Persona | Frequency | Type |
|---|---|---|---|
| Which suppliers deserve the most SCP analyst attention this period? | SCP Manager / Supply Manager | Monthly / Quarterly | **Performance/Governance** — resource allocation |
| Does the current Vendor Complexity tier in the vendor master match actual forward demand volume — who needs re-tiering? | SCP Analyst / GSCP | Quarterly | **Performance/Governance** — vendor master maintenance |
| Which vendors are mismatched (ABC ≠ Vendor Complexity) — investigate root cause? | SCP Analyst | Ad hoc | **Operational** — flag for vendor master update |
| What is the forward demand concentration — top-N suppliers drive what % of volume? | S&OP Leader / Supply Manager | Monthly | **Performance/Governance** — portfolio concentration risk |
| What are the lead times, container sizes, and minimum buy requirements for each supplier by warehouse? | Supply Planner | Ad hoc reference | **Operational** — planning parameters lookup |

**No Financial-Justification decisions.** No dollar values in the model — purely unit demand volume.

---

## 3. Key Metrics / Measures

Only **3 measures** and **3 calculated columns** in the model. This is an intentionally lean stratification tool.

### 3.1 Calculated Columns (on `PSW (Future 4 months)`)

| Column | Business Meaning | Grain | DAX Logic | Flags |
|---|---|---|---|---|
| **Total By Product Class** | Total demand for all vendors in the same product class | Vendor (within class) | `CALCULATE(SUM([Total Demand]), ALLEXCEPT(table, [Primary Product Class]))` | ⚠️ `ALLEXCEPT` removes ALL filters except class — denominator is always the full class total, even when page filters are active. Inconsistent with `RunningTotal` in `ABC Classification by BU volume` which uses `ALLSELECTED`. |
| **ABC Classification by BU volume** | A/B/C tier based on cumulative demand rank within product class | Vendor | `RunningTotal` (ALLSELECTED, per-class) / `ClassTotal` (ALLEXCEPT) → SWITCH: DemandPerc ≥ 0.80 → "A"; RunningPerc ≤ 0.80 → "A"; ≤ 0.95 → "B"; else "C" | ⚠️ Denominator (`Total By Product Class`) uses `ALLEXCEPT` (unfiltered); numerator uses `ALLSELECTED` (filter-aware). **Mixed context bug**: when a filter removes vendors, ClassTotal stays fixed but RunningTotal shrinks → ABC boundaries shift unpredictably. ⚠️ Two "A" conditions with no priority comment — a single-vendor class where that vendor = 100% demand always gets "A" via DemandPerc branch; redundant overlap with RunningPerc branch undocumented. |
| **Match Status** | Does data-driven ABC agree with manually assigned Vendor Complexity? | Vendor | `IF(ISBLANK(both), "Yes", IF(ABC = VendorComplexity, "Yes", "No"))` | ⚠️ `ISBLANK(both)` → "Yes" — a vendor with no demand AND no complexity assignment is counted as "matched". This understates mismatches. |

### 3.2 Measures

| Measure | Business Meaning | Grain | DAX Logic | Flags |
|---|---|---|---|---|
| **Running Total of Demand** | Cumulative demand from highest-volume vendor downward | Vendor | `CALCULATE(SUM([Total Demand]), FILTER(ALLSELECTED(table), [Total Demand] >= CurrentDemand))` — uses `SELECTEDVALUE` to capture single-vendor context | ⚠️ Returns `0` (not `BLANK()`) when RunningTotal is blank — can distort bar charts that distinguish 0 from BLANK. ⚠️ No class grouping: running total is across ALL vendors in ALLSELECTED scope (no `Primary Product Class` filter) — inconsistent with `ABC Classification by BU volume` which is per-class. |
| **Running %** | Cumulative demand % (Pareto curve) | Vendor | `DIVIDE(Running Total of Demand, GrandTotal_ALLSELECTED)` | ⚠️ GrandTotal uses `ALLSELECTED` without class split — same scope inconsistency as above. Pareto % is cross-class, not within-class. Incomparable to `ABC Classification by BU volume` which is within-class. |
| **ABC Classification by filtered volume** | ABC tier using currently filtered scope (measure version) | Vendor | Same logic as calc column but uses `ALLSELECTED` for both RunningPerc and GrandTotal — `DemandPerc >= 0.80` → "A", `RunningPerc <= 0.80` → "A", ≤ 0.95 → "B", else "C" | ⚠️ No class grouping — single Pareto across all visible vendors regardless of product class. Gives different results than the calculated column `ABC Classification by BU volume`. The two ABC classifications **are not the same metric** despite similar names. |

### 3.3 Suspicious / Potentially Wrong Logic

- **`Running %` and `ABC Classification by filtered volume` cross ALL product classes** while `ABC Classification by BU volume` ranks within-class. These metrics answer different questions and are not directly comparable. If a visual shows both, the user sees two inconsistent ABC rankings with no labeling of the difference.
- **`Match Status` returns "Yes" for double-blank** — a newly added vendor with no PSW demand and no complexity assignment in Excel is treated as "matched". False positive.
- **`ABC Classification by BU volume` ALLEXCEPT/ALLSELECTED mismatch** — in an unfiltered view, the results are likely correct. When any page-level filter is applied (e.g., filtering to one Office), ClassTotal is unfiltered but RunningTotal is filtered, producing incorrect per-class cumulative percentages.

---

## 4. Data Sources & Lineage

### Source 1: Azure SQL (`Ashley-edw.database.windows.net` / `ASHLEY_EDW`)

| Schema | Object | Model Table | Risk |
|---|---|---|---|
| `PowerBI_SupplyChain` | `PSWContainersCurrentDay` | `PSW (Future 4 months)` | ✅ Governed — current-day PSW snapshot |

SQL (verbatim):
```sql
SELECT
    Vendor, VNAME, SUM([Value]) AS [Total Demand], SPRundate
FROM PowerBI_SupplyChain.PSWContainersCurrentDay
WHERE ITEMCLASS NOT IN ('TA','TU','CIRP','UIRP','UIF','LA')
    AND WeekNum BETWEEN 0 AND 17
GROUP BY Vendor, VNAME, SPRundate
```

### Source 2: SharePoint Excel ⚠️ UNGOVERNED

| Object | Model Table | Risk |
|---|---|---|
| `https://masterashley.sharepoint.com/sites/SCPGlobalTeam-Tools/Shared%20Documents/Tools/Daily%20Reports/VENDOR LIST AFT & 232.xlsx` Sheet `AFI` | `AFI Vendor List` | ⚠️ **Same file used in Supplier On-Time Performance.** Manual Excel — Vendor Complexity, Primary Product Class, LT, MB/DD per warehouse, analyst assignments all live here. No version control, no refresh guarantee. |

**This model has only 2 data sources total.** The entire analysis rests on one SQL query and one Excel file.

**No relationships defined between `PSW (Future 4 months)` and `AFI Vendor List` in the model.** The join is performed in M (Power Query) at load time: `PSW (Future 4 months)` LEFT OUTER JOINs `AFI Vendor List` on `Vendor = NUMBER`. The joined result is a single flat table — `AFI Vendor List` is exposed separately in the model but only as a passthrough reference table (no active relationships).

---

## 5. Grain & Snapshot Strategy

**Primary grain:** `Vendor + SPRundate` — one row per vendor per PSW run date (daily)

**Snapshot strategy:** **Current day only** — `PSWContainersCurrentDay` is today's PSW snapshot. No historical trend. The `Report Refresh Date` column carries the `SPRundate` from the query, but since it's always the most recent run, no time-series analysis is possible.

**No historical snapshot capability.** Cannot answer "how did vendor ABC tier change vs. last quarter?" The `Report Refresh Date` relationship to a LocalDateTable exists but serves no analytical purpose — there is only ever one date in the data.

---

## 6. Dimensions Used

| Dimension | Table | Conformed? | Local Re-derivations / Drift Risk |
|---|---|---|---|
| **Vendor** | `AFI Vendor List` (SharePoint Excel) | ❌ Not conformed | `Vendor Complexity` (A/B/C/D?), `Primary Product Class`, analyst assignments — all manually maintained in Excel. No ERP or EDW backing. |
| **Product Class** | `Primary Product Class` from `AFI Vendor List` | ❌ Not conformed | Single manually-assigned product class per vendor. Multi-product-class vendors carry only primary class. |
| **Office / Region** | `Office` from `AFI Vendor List` | Partial | Same Office codes as other models (CVRO, etc.) but sourced from Excel, not a conformed dimension table. |
| **Date** | `Report Refresh Date` (auto date table) | ❌ Not conformed | Single-date column; auto-generated LocalDateTable serves no analytical use. `__PBI_TimeIntelligenceEnabled = 1` is enabled but time intelligence is meaningless on a single-date dataset. |

### Notable: Per-Warehouse MB/DD columns ⚠️

`AFI Vendor List` carries **16 MB (Minimum Buy) columns** and **16 DD (Days-to-Delivery) columns**, one per warehouse code (MB 1, MB 3, MB 5, MB 12, MB 15, MB 151, MB 16, MB 17, MB 19, MB 20, MB 215, MB 242, MB 28, MB 335, MB 42, MB 49, MB 50, MB 60, MB 70, MB ECR, MB 232 + DD equivalents). These are:
- Stored in **wide/pivoted format** (one column per WH) in the Excel file
- Not calculated — they are static lookup values
- Not validated against any EDW table
- **32 columns of manually maintained planning parameters with no governance** — if these feed any planning system, errors are invisible

---

## 7. Duplication / Consolidation Signals

| Signal | Details |
|---|---|
| **ABC Classification defined twice** | `ABC Classification by BU volume` (calculated column, within-class Pareto, ALLEXCEPT denominator) and `ABC Classification by filtered volume` (measure, cross-class Pareto, ALLSELECTED denominator) implement different ABC logic under similar names. One report user sees two ABC numbers that don't match with no explanation. |
| **80%/95% thresholds duplicated** | Hardcoded in the calculated column AND the measure independently. A threshold change requires updating both. |
| **`Running Total of Demand` measure ignores class** | The Pareto measure (`Running Total`, `Running %`) is cross-class; the calc column is within-class. Same visual can display both — they answer different questions. |
| **`AFI Vendor List` Excel shared with Supplier On-Time Performance** | Both models pull from the same `VENDOR LIST AFT & 232.xlsx`. Any column added to the Excel is available in both models but may be interpreted differently. No single point of change management. |
| **Item class exclusions shared pattern** | `ITEMCLASS NOT IN ('TA','TU','CIRP','UIRP','UIF','LA')` appears identically in 3 models (this, Supplier OTP, and ABC Coding in OTP). Not centralized. |
| **WeekNum 0–17 appears in multiple models** | Also in `ABC Coding by volume` table in the Supplier On-Time Performance model. Same 17-week window, defined independently. |

---

## 8. Open Questions

1. **What does Vendor Complexity A/B/C/D actually mean?** The Excel column `Vendor Complexity` stores a value compared to the data-driven ABC. Is Vendor Complexity a distinct scale (not A/B/C but e.g., "High/Medium/Low")? If Vendor Complexity uses different labels than A/B/C, `Match Status` will always return "No" even when conceptually aligned.
2. **Who maintains `Vendor Complexity` in the Excel file?** If it's updated once a year vs. the ABC model refreshes daily, `Match Status` "No" could mean "stale tier" not "wrong tier."
3. **Is `PSWContainersCurrentDay` the right source for strategic ABC?** It reflects today's PSW demand snapshot. If today's PSW is anomalous (e.g., a large promo order), ABC tier could flip for one vendor. Should this use a rolling average?
4. **What do `MB` and `DD` columns mean?** Column names suggest Minimum Buy and Days-to-Delivery, but they're not used in any DAX measure — they're pure reference. Are these the parameters planners actually use, and if so, how (copied into another tool)?
5. **Is there an active `D` tier in Vendor Complexity?** The ABC logic produces only A/B/C. If the Excel has a "D" tier, those vendors always show `Match Status = "No"`.
6. **Who owns the 17-week forward window decision?** `WeekNum BETWEEN 0 AND 17` drives the entire ABC calculation. A shorter or longer horizon would shift tiers. Is 17 the S&OP planning horizon?
7. **Is this model still live / actively used?** The PBI Desktop version is `25.06` (June 2025 build), suggesting recent maintenance. But no refresh schedule or owner is visible in the model metadata.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Location | Apparent Purpose | Documented? |
|---|---|---|---|
| **`WeekNum BETWEEN 0 AND 17`** | SQL: `PSWContainersCurrentDay` | 17-week forward PSW demand window for ABC basis | ❌ No comment |
| **Item classes `'TA','TU','CIRP','UIRP','UIF','LA'`** | SQL | Excluded from demand volume | ❌ No comment — same exclusions as other models |
| **`0.80` (A boundary)** | DAX calc col + measure (2 places) | Top 80% cumulative demand = A tier | ❌ Standard Pareto convention, undocumented |
| **`0.95` (B boundary)** | DAX calc col + measure (2 places) | 80–95% cumulative = B tier; >95% = C | ❌ Undocumented |
| **`DemandPerc >= 0.80` override** | DAX calc col + measure (2 places) | A single vendor comprising ≥80% of class total gets A regardless of cumulative position | ❌ Edge case for single-dominant-vendor classes — logical but undocumented |
| **LT column** | `AFI Vendor List` Excel | Lead time (days?) per vendor — `LT` errors replaced with 0 in M | ❌ Unit (weeks/days?) and source unknown; 0 default for errors hides missing data |

**Dollar-value business impact:** ❌ None. No financial measures in this model. Purely unit volume.

---

## 10. Comparability / Consistency

| Issue | Details |
|---|---|
| **`ABC Classification by BU volume` vs. `ABC Classification by filtered volume` — two different metrics with near-identical names** | Calc column ranks within product class (ALLEXCEPT); measure ranks across all visible vendors (ALLSELECTED, no class split). If a visual shows both for the same vendor, they can disagree — the labels are too similar to make the difference clear. |
| **`Running %` is cross-class; `ABC Classification by BU volume` is within-class** | A Pareto chart built on `Running %` shows the cross-class curve, not the within-class curve used for ABC assignment. Visually the user may think the Pareto curve drives the tier, but it doesn't — the tier uses a different scope. |
| **`Total By Product Class` uses ALLEXCEPT; `RunningTotal` inside ABC column uses ALLSELECTED** | When a filter is active on the page (e.g., show only Office=CVRO), the denominator (ClassTotal) is unfiltered but the numerator (RunningTotal) is filtered. ABC tiers can shift when slicers are applied — a vendor may appear as "B" unfiltered but "A" filtered, not because of a true tier change but because of the mixed filter context. |
| **`Match Status` treats double-blank as "Yes"** | A vendor with `Total Demand = 0` (no PSW) and null `Vendor Complexity` in Excel shows "Match Status = Yes". This is not a true match — it is a no-data record treated as agreement. It artificially inflates the "matched" count. |
| **`Running Total of Demand` measure returns `0` instead of `BLANK()`** | When no vendor is in context, the measure returns 0. Other measures in this model return BLANK for no-data rows. The 0 can appear in totals, making the grand total of `Running Total` non-blank when it should be. |

---

## Closing — Interview Seeds

> **Ready-to-ask questions for the SCP analyst or supply manager who uses this report:**

1. **"The report shows two ABC classifications — one by product class and one across all vendors. Which one do you actually look at, and when the two disagree for the same vendor, what does that tell you?"**  
   *(Target: determine which ABC metric is operationally trusted and whether the user even knows the two exist with different scopes.)*

2. **"The `Vendor Complexity` column in the Excel file is compared against the data-driven ABC. How often is that Excel updated, and when it shows `Match Status = No`, do you update the Excel to match the data, or investigate why the vendor's demand changed?"**  
   *(Target: find the actual maintenance workflow and whether Match Status drives action or is decorative.)*

3. **"The MB 1, MB 3, MB 335 columns (and the DD columns) in the vendor list — what do MB and DD stand for, and do planners copy those numbers into another system, or are they just for reference in this view?"**  
   *(Target: assess whether the 32 manually-maintained per-warehouse planning parameter columns have an active downstream use or are orphaned reference data.)*

4. **"The ABC is based on the next 17 weeks of PSW demand. Has the team ever discussed whether 17 weeks is the right horizon — for example, whether a seasonal vendor with low demand now but high demand in 12 weeks gets the right tier?"**  
   *(Target: validate the 17-week constant and understand whether the ABC is treated as stable or reassessed seasonally.)*

---

## Appendix: Table Inventory

| Table | Type | Source | Grain | Window |
|---|---|---|---|---|
| `PSW (Future 4 months)` | Fact + Vendor dim (joined) | EDW `PowerBI_SupplyChain.PSWContainersCurrentDay` + `AFI Vendor List` (Excel, left join in M) | Vendor + SPRundate | Current day only (WeekNum 0–17) |
| `AFI Vendor List` | Dimension (reference) | **SharePoint Excel** `VENDOR LIST AFT & 232.xlsx` Sheet `AFI` | Vendor | Current manual maintenance |
| `LocalDateTable_*` | Auto date | Generated from `Report Refresh Date` | Date | Auto-range from data |
| `DateTableTemplate_*` | Auto date template | PBI internal | — | — |
