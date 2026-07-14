# Report Analysis: Supplier On-Time Performance

**Workspace:** SCP Global Team  
**Model ID:** `232eb1db-c667-47ee-9b12-8d259814ed2b`  
**Source:** Azure SQL `ashley-edw.database.windows.net` / `ASHLEY_EDW` + SharePoint Excel  
**Analysis Date:** 2026-07-13  
**Analyst:** Claude Code (automated model inspection)

---

## 1. Supply-Chain Question & Chain Link

**Core question this report answers:**  
*"Are our import suppliers shipping their firmed purchase order quantities on time, and what is the volume and financial penalty exposure from delayed shipments, broken down by 1-, 2-, and 3-week delay buckets?"*

**Chain link served:** **On-Time / Receipts** — inbound ocean freight supplier execution.  
Bridges the **Purchase Schedule Worksheet (PSW)** firmed demand (what was committed by suppliers at a snapshot date 3–4 weeks prior to ETD) against actual shipped quantities from those suppliers. This is a **supplier accountability** report, not a demand or inventory report.

Two distinct sub-domains coexist in the same model:
- **Non-Ashton AFI/AFT suppliers** (majority of model): tracked via `PSWHistoricalSnapshots` → `OnTime` using Sunday PSW snapshots
- **Ashton (Warehouse 335 / CVRO office)**: separate pipeline via `Ashton_PSW` using Wednesday PSW snapshots with different logic

---

## 2. Decisions Supported

| Decision | Persona | Frequency | Type |
|---|---|---|---|
| Which suppliers have on-time % below threshold this week — expedite or escalate? | Supply Planner / SCP Analyst | Weekly | **Operational** — contact supplier, request pull-up |
| Which delayed suppliers carry the largest container exposure (container count late)? | Supply Manager | Weekly | **Operational** — prioritize expedite, flag DC receiving |
| What is the dollar-value penalty owed by suppliers for 2-week and 3-week delayed shipments? | Supply Manager / Procurement | Weekly | **Financial-Justification** — ⚠️ penalty formula uses `vdpprice` × hardcoded rates × delayed qty |
| Which suppliers are A/B/C class by forward demand volume — where to focus SCP effort? | SCP Analyst / Supply Manager | Monthly | **Performance/Governance** — ABC stratification for supplier management |
| Is FYTD on-time performance tracking to goal by supplier/product class? | S&OP Leader / WBR | Monthly / WBR | **Performance/Governance** — supplier scorecard, quarterly reviews |
| How much of the delay was absorbed within 1/2/3 subsequent weeks (recovery profile)? | Supply Manager | Weekly | **Operational** — assess supply recovery, adjust safety stock |
| Are Ashton (CVRO) suppliers performing on time vs. FQTY on ETD basis? | Ashton Planner | Weekly | **Operational** — Ashton-specific escalation |

---

## 3. Key Metrics / Measures

All measures reside across two tables: **`OnTime`** (50 measures) and **`Ashton_Ontime By Vendor`** (1 measure). A `TableSelection` parameter switches between 3-week and 4-week measurement buckets throughout.

### 3.1 Core On-Time % Measures

| Measure | Business Meaning | Grain | Source Logic | Flags |
|---|---|---|---|---|
| **MeasureW3OnTime%** | % of firmed qty shipped on-time in 3-week window | Vendor+Item+ETD Week | `DIVIDE(SUM(Shipped follow demand W3), SUM(FirmedW3))` — returns "No Firmed Qty" string when firmQty=0 | ⚠️ Returns a string in some rows — mixed type in numeric column |
| **MeasureW4OnTime%** | Same but 4-week window | Same | `DIVIDE(SUM(Shipped follow demand W4), SUM(FirmedW4))` | Same mixed-type issue |
| **Combined_OnTime%** | Switchable W3/W4 on-time % | Vendor+Item+ETD Week | `SWITCH(SelectedValue, "3-week bucket", [MeasureW3OnTime%], ...)` | ⚠️ Returns blank or "No Firmed Qty" string — may break chart visuals |
| **Combined_OnTime% FYTD** | FYTD on-time across all visible ETD weeks | Vendor aggregate | `DIVIDE(FYTD ShipQty No Excess, FYTD FirmedQty)` within current fiscal year up to last data date | Complex LASTNONBLANK logic — context-sensitive |
| **ShowHideCombined_OnTime%** | Helper to show/hide visual | — | `IF(ISNUMBER([Combined_OnTime%]), "SHOW", "HIDE")` | Workaround for mixed numeric/string issue above |

### 3.2 Quantity Measures

| Measure | Business Meaning | Grain | Source Logic | Flags |
|---|---|---|---|---|
| **Combined_FirmedQty** | Firmed PO qty at snapshot 3 or 4 weeks before ETD | Vendor+Item+ETD Week | `SUM(FirmedW3)` or `SUM(FirmedW4)` via Switch | — |
| **Combined_ShippedQty** | Total qty shipped (including excess) | Same | `SUM(ShippedW3)` or `SUM(ShippedW4)` | Includes overshipment |
| **Combined_ShipQty No Excess** | Shipped qty capped at firmed qty | Same | `SUM(Shipped follow demand W3)` or `W4` = `MIN(FirmedWX, ShippedWX)` | — |
| **Combined_DelayedQTY** | Units late (firmed minus shipped-follow-demand) | Same | `SUM(DelayedW3)` or `SUM(DelayedW4)` | — |
| **Combined_Excess Ship** | Units shipped above firmed qty | Same | `SUM(W3ExcessShipped)` or `SUM(W4ExcessShipped)` | — |
| **Combined_Delayed_1Week (pcs)** | Delayed units recovered 1 week late | Same | `SUM(Delayed_1Week_W3/W4)` via Switch | — |
| **Combined_Delayed_2Week (pcs)** | Delayed units recovered 2 weeks late | Same | `SUM(Delayed_2Week_W3/W4)` | — |
| **Combined_Delayed_3Week (pcs)** | Delayed units still late after 3 weeks | Same | `SUM(Delayed_3Week_W3/W4)` | — |

### 3.3 Container Measures

| Measure | Business Meaning | Grain | Source Logic | Flags |
|---|---|---|---|---|
| **Combined_ShippedQty_Container** | Shipped qty in containers | Vendor+Item+ETD Week | `SUMX(OnTime, (Cubes × Shipped follow demand WX) / 2400)` | ⚠️ **2400 hardcoded** = CBF/container; no parameter |
| **Combined_DelayedContainer** | Delayed units in containers | Same | `SUM(DelayW3/W4_Container)` = `DelayedWX × Cubes / 2400` | ⚠️ **2400 hardcoded** |
| **Combined_Delayed_1/2/3Week_Container** | Delay recovery in containers | Same | `SUM(Delayed_NWeek_WX_Container)` | ⚠️ **2400 hardcoded** |
| **Delay_Ratio_1Week** | 1-week delayed containers as % of shipped | Vendor aggregate | `DIVIDE([Combined_Delayed_1Week_Container], [Combined_ShippedQty_Container])` | — |
| **Delay_Ratio_2Week** | 2-week delay container ratio | Same | Same pattern | — |
| **Delay_Ratio_3Week** | 3-week delay container ratio | Same | Same pattern | — |

### 3.4 Financial Penalty Measures ⚠️ HIGH RISK

| Measure | Business Meaning | Grain | Source Logic | Flags |
|---|---|---|---|---|
| **Penalty_2Week_Delay** | Dollar penalty for 2-week delayed units | Vendor+Item+ETD Week | `SUMX(OnTime, 0.02 × Combined_Delayed_2Week × vdpprice)` | ⚠️ **2% rate hardcoded**, `vdpprice` from `VendorPricing` table — price may be stale |
| **Penalty_3Week_Delay** | Dollar penalty for 3-week delayed units | Same | `SUMX(OnTime, 0.05 × Combined_Delayed_3Week × vdpprice)` | ⚠️ **5% rate hardcoded** |
| **PenaltyAmount** | Total penalty exposure | Vendor aggregate | `[Penalty_2Week_Delay] + [Penalty_3Week_Delay]` | ⚠️ Sum of two hardcoded rate calculations |
| **PenaltyPercent** | Penalty as % of shipped $ | Vendor aggregate | `DIVIDE([PenaltyAmount], [ShippedAmount])` | — |
| **ShippedAmount** | Total $ value shipped | Same | `SUMX(OnTime, Combined_ShippedQty × vdpprice)` | `vdpprice` single price per item-vendor, not date-versioned |

### 3.5 ABC and Ashton Measures

| Measure | Business Meaning | Grain | Source Logic | Flags |
|---|---|---|---|---|
| **Supplier ABC coding** (calc col) | A/B/C by forward demand volume per product class | Vendor | Running cumulative % within class; A ≤ 80%, B ≤ 95%, else C | ⚠️ **80%/95% thresholds hardcoded** |
| **Ontime_Overall** (Ashton) | Ashton vendor on-time % | Vendor+ETD | `COUNT(Ontime="Yes") / COUNT(all)` — pure row count, not qty-weighted | ⚠️ Count-based, not qty-weighted — inflates performance for small orders |

### 3.6 Suspicious / Potentially Wrong Logic

- **`FirmedW4` uses WeekNums `{0, 1, 2, 4}` — skips week 3.** W3 uses `{0, 1, 2}`. No comment. If this is intentional (skip W3 equivalent of 3-week window?) it is undocumented; most likely a copy-paste error.
- **`MeasureW3OnTime%` / `Combined_OnTime%` returns string `"No Firmed Qty"`** when qty=0 — mixed numeric/string type. The `ShowHideCombined_OnTime%` workaround confirms the team is aware but the root cause is not fixed.
- **`MeasureW3Shipment%`** branches on `(_FirmQty = 0 || ISBLANK) && NOT ISBLANK(ShippedQty)` → string. Inconsistent with `W3OnTime%` null-handling.
- **`Combined_OnTime% FYTD`** `LASTNONBLANK` relies on `Combined_FirmedQty + Combined_ShipQty No Excess > 0`. Vendors with zero shipped in recent weeks may be silently excluded from FYTD calculation.
- **`Ashton Ontime_Overall` is count-based, not qty-weighted.** A vendor shipping 1 piece on time and 1,000 pieces late scores 50% — misleading.

---

## 4. Data Sources & Lineage

### Source 1: Azure SQL (`ashley-edw.database.windows.net` / `ASHLEY_EDW`)

| Schema | Object | Model Table | Risk |
|---|---|---|---|
| `SupplyChain_Enh` | `PSWWeeklyExtractSnapshot` | `PSWHistoricalSnapshots`, `Ashton_PSW`, `List Of Vendor from PSW Historical` | Governed EDW ✅ — core PSW source |
| `PowerBI_SupplyChain` | `CurrentProductDetails` | Referenced in SQL JOINs for item/series/class | ✅ Governed |
| `PowerBI_SupplyChain` | `VendorMaster` | `Ashton_PSW` | ✅ Governed |
| `PowerBI_SupplyChain` | `PSWContainersCurrentDay` | `ABC Coding by volume` | ✅ Governed |
| `Wholesale_Purchasing_AFI` | `VENNAM` | `PSWHistoricalSnapshots`, `VendorPricing` | ✅ Governed |
| `Wholesale_ProductSourcing_AFI` | `PoDetail`, `PoMaster` | `Ashton_Shipped_SQL` | ✅ Governed |
| `Wholesale_Vendors_AFI` | `VendorPricing` | `VendorPricing` | ✅ Governed — but ⚠️ price not date-versioned |
| `Wholesale_ProductSourcing_AFI` | `vendor` | `QA Team` | ✅ Governed |
| `Manufacturing_MasterData_WNK` | `PSTBOMD` | Used in BOM exclusion filter (SQL) | ⚠️ Manufacturing schema — separate governance domain |
| `Enterprise_DW` | `DimDate` | `DimDate` | ✅ Conformed dimension |

### Source 2: SharePoint Excel ⚠️ UNGOVERNED

| Object | Model Table | Risk |
|---|---|---|
| `https://masterashley.sharepoint.com/.../VENDOR LIST AFT & 232.xlsx` Sheet `AFI` | `Vendor List` | ⚠️ **Manual Excel file** — ungoverned, no refresh guarantee, anyone can edit without version control. Vendor metadata (SCP Analyst, GSCP, Asia SCP assignment) lives here only. |

**No Dataflow, iSeries MAPICS, or other sources.** This model is simpler in lineage than the WNK/MILL model.

**Ungoverned / elevated-risk sources (2):**
1. `SharePoint Excel — Vendor List AFT & 232.xlsx` — manual maintenance, silently stale.
2. `Manufacturing_MasterData_WNK.PSTBOMD` — BOM component exclusion filter; schema changes break the exclusion silently.

---

## 5. Grain & Snapshot Strategy

**Primary grains:**
- **`PSWHistoricalSnapshots`:** `Item + Warehouse + Vendor + SPRunDate (Sunday) + WeekNum` — weekly PSW snapshot
- **`OnTime`:** `Item + Warehouse + Vendor + Capture_date` — deduplicated snapshot header (no qty at this grain)
- Calculated columns on `OnTime` perform row-level CALCULATE lookups back into `PSWHistoricalSnapshots` to produce firmed/shipped qty at each row
- **`Ashton_PSW`:** `Item + Vendor + ETD (Wednesday PSW snapshot)` — latest Wednesday snapshot only

**Snapshot strategy:**
- `PSWHistoricalSnapshots`: **2-year rolling historical snapshots** (all Sundays, `SPRunDate >= DATEADD(year,-2,GETDATE())`)
- `Ashton_PSW`: **Latest Wednesday snapshot only** — no history for Ashton
- `DimDate`: 2-year window for fiscal week/year

**Historical snapshot capability:** ✅ Present for non-Ashton (2 years of Sunday snapshots) — can answer "what was firmed 8 weeks ago vs. what shipped". ❌ Absent for Ashton — no trend analysis possible.

---

## 6. Dimensions Used

| Dimension | Table | Conformed? | Local Re-derivations / Drift Risk |
|---|---|---|---|
| **Vendor** | `Vendor List` (SharePoint Excel) | ❌ Not conformed | SCP Analyst, GSCP, Asia SCP — manual maintenance in Excel. Vendor activeness flag in Excel not verified against ERP. |
| **Product / Item** | `Item Master` (EDW `CurrentProductDetails`) | Partial ✅ | `Collective Class`, `Item Class Code`, `AFI Sales Division`, `AFI Finance Division`, `Cubes` — conformed. Null Cubes → 0 applied in M (reasonable default but hides missing data). |
| **Date / Fiscal** | `DimDate` (EDW `Enterprise_DW`) | Partial ✅ | Only `FiscalWeek` and `FiscalYear` pulled. `DATEFIRST 7` in SQL aligns week start to Sunday for PSW. |
| **Fiscal Week** | `Fiscal_Week` (calculated DAX table) | ❌ Local derived | Filters `VALUES(OnTime[ETD Week 1])` to Saturdays (`WEEKDAY(...,2)=6`). 3-week and 4-week bucket labels computed inline. Not a shared calendar object. |
| **Warehouse** | Derived inline in `OnTime[Warehouse]` calc col | ❌ Not conformed | SWITCH mapping: `"335"→"Ashton"`, `{"1","15","17","28","42","5","ECR"}→"AFT"`, others pass through. Hardcoded — breaks when new warehouse added. |
| **QA Team** | `QA Team` (EDW `Wholesale_ProductSourcing_AFI.vendor`) | Partial ✅ | Maps `vendor_no → qa_office_team`. Simple 2-column extract, minimal drift risk. |
| **Capture Date** | `Capture_date` (calculated DAX table) | ❌ Local derived | `VALUES(OnTime[Capture_date])` — PSW run dates available to filter. No fiscal labeling. |

---

## 7. Duplication / Consolidation Signals

| Signal | Details |
|---|---|
| **W3/W4 measure pairs (×8 primitive measures)** | Every core quantity measure exists in W3 and W4 variants (`MeasureDelayedW3` / `MeasureDelayedW4`, etc.) then combined via `Combined_*` SWITCH. 16 primitive measures + 11 Combined = 27 measures that could collapse to 11 if the W3/W4 logic moved to the calculated column layer. |
| **Item class exclusion duplicated in 3 SQL queries** | `'TA','TU','LA','UIF','CIRP','UIRP'` appears in `PSWHistoricalSnapshots`, `Ashton_PSW`, and `ABC Coding by volume` independently. A governed EDW view with this filter would eliminate drift risk. |
| **CVRO/Ashton split duplicated across 5 tables** | `Ashton_PSW`, `Ashton_Shipped_SQL`, `Ashton_Shipped_SQL (Over)`, `Ashton_PSW (Check Over)`, `Ashton_Ontime By Vendor` all independently filter `Office = 'CVRO'` and `Whse = '335'`. |
| **2-year lookback in 3 SQL queries** | `DATEADD(year,-2,GETDATE())` appears independently in `PSWHistoricalSnapshots`, `Ashton_Shipped_SQL`, `DimDate`. |
| **`vdpprice` used in 3 measures** | `Penalty_2Week_Delay`, `Penalty_3Week_Delay`, `ShippedAmount` all SUMX with `OnTime[vdpprice]`. Price is joined from `VendorPricing` via the `OnTime` table as a single non-versioned price — any price change affects all historical rows retroactively. |
| **Delay bucket logic (`MIN(delayed, futureShipped)`)** | The W3 and W4 recovery week computation is copy-pasted for 3 weeks × 2 versions = 6 nearly identical calculated columns, then again for container conversions (6 more). Candidate for a single parameterized expression or M-level pivot. |

---

## 8. Open Questions

1. **Are the 2% and 5% penalty rates contractual?** The `Penalty_2Week_Delay` and `Penalty_3Week_Delay` measures use `0.02` and `0.05` respectively. Are these actual supplier contract terms, a negotiation baseline, or an aspirational rate? If contractual, which vendor contracts do they apply to?
2. **Why does `FirmedW4` use WeekNums `{0,1,2,4}` — skipping 3?** This appears to be a copy-paste error. What is the intended W4 definition?
3. **Is `Ashton_PSW` using Wednesday snapshots intentionally?** The non-Ashton pipeline uses Sunday. The Ashton pipeline uses `DATEPART(dw,SPRUNDATE) = 4` (Wednesday). Is this a business requirement or an artifact of when Ashton's PSW runs?
4. **What happens after `'05/01/2025'`?** Two hardcoded dates (`'05/01/2025'` in SQL, `#date(2025, 5, 10)` in M) gate the Ashton overshipment logic. These are already in the past — is the Ashton overshipment correction still active, or permanently on?
5. **Is `Vendor List` maintained actively?** The SharePoint Excel is the only source of analyst assignment (`SCP ANALYST`, `GLOBAL SUPPLY CHAIN PLANNER`). Who owns it and how often is it updated?
6. **Is `vdpprice` the right price for penalty calculation?** `VendorPricing.vdpprice` filters `vdpprice IS NOT NULL AND <> 0` but is not date-versioned. Is this the vendor cost (FOB price)? Is it the price at time of order, or today's price?
7. **Is the `2400` CBF/container still correct?** Mixed container sizes (20' vs 40') have different CBF. Is 2400 an average, a standard 40' CBF, or something else? Who validated this?
8. **Who uses the Ashton section vs. the main On-Time section?** The two sub-domains have different data freshness (latest Wednesday vs. 2-year Sunday history), different grains, and different on-time definitions. Are they consumed by the same team?

---

## 9. Business Assumptions / Magic Numbers

| Constant | Location | Apparent Purpose | Documented? |
|---|---|---|---|
| **`WeekNum BETWEEN -4 AND 4`** | SQL: `PSWHistoricalSnapshots` | PSW window: 4 weeks before/after ETD | ❌ No comment |
| **`DATEPART(weekday, SPRunDate) = 1`** (Sunday) | SQL | PSW runs on Sundays for non-Ashton | ❌ No comment |
| **`DATEPART(dw, SPRUNDATE) = 4`** (Wednesday) | SQL: Ashton | PSW runs on Wednesdays for Ashton | ❌ No comment |
| **`WHSE = '335'`** | SQL/M (5 places) | Ashton warehouse code | ❌ Hardcoded — no warehouse reference table |
| **`Office = 'CVRO'`** | SQL/M (5 places) | CVRO = Ashton vendor office code | ❌ Hardcoded |
| **`'05/01/2025'` and `#date(2025,5,10)`** | SQL: Ashton, M: Ashton_Shipped_SQL (Over) | Ashton overshipment correction start dates | ❌ **Already in the past** — 2 separate dates, 9-day gap unexplained |
| **`Office NOT IN ('RKD','WANEK','MILLE')`** | SQL: `PSWHistoricalSnapshots` | Excludes internal/plant offices | ❌ No comment on what these are |
| **`Whse NOT IN ('19','201')`** | SQL: `PSWHistoricalSnapshots` | Excludes these warehouses from OTP | ❌ No comment |
| **Item classes: `'TA','TU','LA','UIF','CIRP','UIRP'`** | SQL (3 queries) | Excluded from OTP calculation | ❌ No comment — TA/TU likely "trade/transfers"; others unknown |
| **PO status codes `'10','20','99'` excluded** | SQL: `Ashton_Shipped_SQL` | Not "shipped" statuses | ❌ No comment on code meanings |
| **`WeekNums {0,1,2}` for FirmedW3** | DAX calc col | Weeks 0,1,2 relative to ETD = "firmed window" | ❌ No comment |
| **`WeekNums {0,1,2,4}` for FirmedW4** | DAX calc col | Weeks 0,1,2 and **4** — skips 3 | ❌ **Likely bug** |
| **`2400`** (CBF/container) | DAX calc cols + measures (8+ places) | Cubic feet per container for unit→container conversion | ❌ No comment — single size assumption |
| **`0.02` (2%)** | DAX: `Penalty_2Week_Delay` | Supplier penalty rate for 2-week delay | ❌ No reference to contract or policy document |
| **`0.05` (5%)** | DAX: `Penalty_3Week_Delay` | Supplier penalty rate for 3-week delay | ❌ No reference to contract or policy document |
| **`0.80` / `0.95`** | DAX calc col: `Supplier ABC coding` | ABC A/B boundary thresholds | ❌ Standard Pareto, but undocumented |
| **`DATEADD(year,-2,GETDATE())`** | SQL (3 queries) | 2-year rolling lookback | ❌ No comment on why 2 years |
| **`WeekNum BETWEEN 0 AND 17`** | SQL: `ABC Coding by volume` | 17-week forward window for ABC demand | ❌ No comment |
| **`Capture_date + 21 days`** (`Delay_compare_date`) | M: `OnTime` | 3 future weeks after capture date for recovery tracking | ❌ No comment |
| **`Capture_date - 21 days`** (`Compare_dateW3`) | M: `OnTime` | 3-week lookback for W3 firmed snapshot | ❌ No comment |
| **`Capture_date - 28 days`** (`Compare_dateW4`) | M: `OnTime` | 4-week lookback for W4 firmed snapshot | ❌ No comment |
| **`PSW.SPRunDate > '05/01/2025'`** | SQL: `Ashton_PSW` | Ashton data cutoff — start of Ashton OTP tracking | ❌ **Hardcoded — will not auto-advance** |

**Dollar-value business impact:** ✅ **YES — financial-justification risk.**  
`PenaltyAmount = SUMX(OnTime, 0.02 × Delayed_2Week × vdpprice) + SUMX(OnTime, 0.05 × Delayed_3Week × vdpprice)`  
Every assumption in this formula is unverified:
- `0.02` and `0.05` — are these actual contract rates or aspirational?
- `vdpprice` — is this the correct price basis (FOB cost vs. retail vs. landed)?
- `2400` — is the container conversion denominator valid for all SKUs?
- `Delayed_Nweek` — uses W3 or W4 depending on `TableSelection`; W4 has a likely bug (skips week 3).

If `PenaltyAmount` feeds an executive business case, all four of these constants need external validation.

---

## 10. Comparability / Consistency

| Issue | Details |
|---|---|
| **W3 vs. W4 on-time definition differs fundamentally** | W3 = "what was firmed 3 weeks before ETD shipped within ETD window"; W4 = "what was firmed 4 weeks before ETD shipped within ETD window." The `TableSelection` slicer silently changes the definition. A user switching buckets mid-session gets different numbers for the same vendor — not clearly labeled in visuals. |
| **W4 FirmedQty uses WeekNums {0,1,2,4} — skips 3** | W3 uses {0,1,2}. The W4 firmed denominator is inconsistent with the W3 logic. OTP% for W4 is not directly comparable to W3 even for the same vendor/week. |
| **Ashton on-time = count of rows; non-Ashton on-time = qty-weighted** | `Ontime_Overall` (Ashton) counts Yes/No rows. `MeasureW3OnTime%` sums qty. One small late PO at Ashton equals one large late PO — structurally incomparable. |
| **Ashton uses latest Wednesday snapshot only; non-Ashton uses 2-year Sunday history** | Trend analysis available for non-Ashton (2 years); unavailable for Ashton (single snapshot). FYTD measures work for non-Ashton, not for Ashton. |
| **`Penalty_2Week_Delay` and `Penalty_3Week_Delay` use `Combined_Delayed_NWeek`** | `Combined_Delayed_*` depends on `TableSelection` (W3 or W4). The penalty number changes when the user switches the W3/W4 slicer — same week, different penalty. Not flagged in visuals. |
| **`ABC Coding by volume` uses `PSWContainersCurrentDay`; `OnTime` uses `PSWWeeklyExtractSnapshot`** | Two different PSW source tables. `ABC Coding` reflects today's current PSW snapshot; `OnTime` uses historical Sunday snapshots. Vendor demand ranking (ABC) and on-time performance are on different temporal bases. |
| **`vdpprice` is a single non-versioned price** | Used in `Penalty*`, `ShippedAmount`. If a vendor's price changes, ALL historical penalty calculations retroactively change. No point-in-time price mechanism. |

---

## Closing — Interview Seeds

> **Ready-to-ask questions for the supply planner or supply manager who uses this report:**

1. **"When Combined_OnTime% drops below threshold for a vendor — say below 80% — what specifically do you do next? Do you call the vendor directly, escalate to the GSCP, or log it somewhere? And is that threshold 80% or something else?"**  
   *(Target: confirm the actual decision trigger, escalation path, and whether there is a documented OTP threshold.)*

2. **"The report shows a penalty amount in dollars using a 2% rate for 2-week delays and 5% for 3-week delays. Are these rates actually written into supplier contracts, and have you ever actually billed a supplier using these numbers, or is it more of an internal scorecard pressure tool?"**  
   *(Target: validate the penalty formula's real-world use and whether the 2%/5% constants are contractual or aspirational — this directly affects whether PenaltyAmount feeds an executive business case.)*

3. **"The report has a 3-week bucket and a 4-week bucket selector. Which one do you actually use day-to-day, and do you ever compare them side by side — or does the team just pick one and stick with it?"**  
   *(Target: determine if the W3/W4 switching is actively used or if one bucket is the de facto standard, which informs whether the W4 WeekNum bug matters in practice.)*

4. **"The 2400 cubic feet per container — is that a standard Ashley assumption for all suppliers, or does it vary by origin? For example, do you treat 20-foot containers differently, and is there a table somewhere that maps container type to CBF?"**  
   *(Target: validate the most consequential single constant in the penalty and delay-severity calculations.)*

---

## Appendix: Table Inventory

| Table | Type | Source | Grain | Window |
|---|---|---|---|---|
| `PSWHistoricalSnapshots` | Fact (staging, hidden) | EDW `SupplyChain_Enh.PSWWeeklyExtractSnapshot` | Item+WH+Vendor+Sunday+WeekNum | 2-year rolling |
| `OnTime` | Fact (main) | Derived from `PSWHistoricalSnapshots` | Item+WH+Vendor+Capture_date | 2-year rolling |
| `Ashton_PSW` | Fact (Ashton) | EDW `PSWWeeklyExtractSnapshot` | Item+Vendor+ETD (Wednesday) | Latest snapshot only |
| `Ashton_Shipped_SQL` | Fact (Ashton) | EDW `PoDetail`+`PoMaster` | Item+Vendor+ETD week | 2-year rolling |
| `Ashton_Shipped_SQL (Over)` | Fact (Ashton) | Same as above | Same | YTD only |
| `Ashton_PSW (Check Over)` | Fact (Ashton, hidden) | PSW Wed snapshot | Same | Latest only |
| `Ashton_Ontime Summary` | Aggregated fact (hidden) | Derived from `Ashton_PSW` | Vendor+ETD | Latest only |
| `Ashton_Ontime By Vendor` | Fact | Derived from `Ashton_PSW` | Vendor+ETD | Latest only |
| `Vendor List` | Dimension | **SharePoint Excel (ungoverned)** | Vendor | Current manual |
| `Item Master` | Dimension | EDW `PowerBI_SupplyChain.CurrentProductDetails` | Item SKU | Current only |
| `VendorPricing` | Reference | EDW `Wholesale_Vendors_AFI.VendorPricing` | Vendor+Item | Latest (non-versioned) |
| `QA Team` | Reference | EDW `Wholesale_ProductSourcing_AFI.vendor` | Vendor | Current only |
| `ABC Coding by volume` | Reference | EDW `PowerBI_SupplyChain.PSWContainersCurrentDay` | Vendor | Current day only |
| `List Of Vendor from PSW Historical` | Filter helper | EDW `PSWWeeklyExtractSnapshot` | Vendor | 1-year rolling |
| `DimDate` | Dimension | EDW `Enterprise_DW.DimDate` | Date | 2-year rolling |
| `Fiscal_Week` | Dimension (calculated) | Derived from `OnTime[ETD Week 1]` | ETD Saturday | From `OnTime` |
| `Capture_date` | Dimension (calculated) | Derived from `OnTime[Capture_date]` | Sunday snapshot date | From `OnTime` |
| `TableSelection` | Parameter | Static inline (M) | — | — |
| `Parameter` | Parameter | Calculated DAX table | — | — |
