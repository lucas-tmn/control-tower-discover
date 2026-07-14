# FCA Services Fee Audit — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `703aac84-58c9-4133-af9c-c8bb4facee4a`  
**Report ID:** `f14b994a-ec08-4e7d-9054-9e97cc6350c0`  
**Analysis Date:** 2026-07-09  
**Model Size:** 13 tables (2 SQL + 2 SharePoint Excel + 1 calculated + local date tables); **0 DAX measures**; Compatibility Level 1600  
**BIM File:** [bim/FCA_Services_Fee_Audit.bim](bim/FCA_Services_Fee_Audit.bim)  
**Note:** Zero measures — all logic is implemented as calculated columns. This is a pure worklist/audit table report with no aggregated KPIs.

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For each FCA (Free Carrier Alongside) purchase order with "In-Transit" through "Receiver" status, has the vendor correctly invoiced the FCA service fee? Is the amount as expected, over-billed, under-billed, duplicated, or missing?

This is a **financial audit / invoice verification** report for FCA-based purchase orders. It compares:
1. The **expected FCA service fee** based on the vendor's PIS Adjustment % × PO Amount
2. The **actual invoice adjustment amount** recorded for each PO
3. Computes an **Audit Status** (PASSED / FAILED) and a **Classification** (Duplicate/Missing/Over/Under)

**Primary chain links served:**

| Link | How served |
|---|---|
| **Supply (Purchasing)** | `POAdjusment` — FCA purchase orders in In-Transit to Receiver status (status codes 30–50); ETD, ETA, warehouse, vendor, PO Amount |
| **Finance (Invoice Audit)** | `POAdjusment[AdjustmentAmount]` vs. `[FCA_SERVICE]` (calculated expected fee); `RequireVerification[Classification]` flags discrepancies |
| **Vendor Master** | `VendorList` — vendor details, office, SC planner assignment |
| **PIS Parameters** | `PISAdjustment` — per-vendor PIS (Price Increase Surcharge?) Adjustment % used to compute expected FCA fee |

**Not served:** Demand, forecast, inventory, on-time, forecast accuracy. This is a purely operational financial audit report.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Accept or reject FCA service invoice adjustment** — flag PASSED vs. FAILED based on < 0.5% tolerance | FCA Auditor / Supply Chain Finance | **Weekly** (as PO status changes) | **Financial-Justification** — validate vendor billing, prevent overpayment |
| **Identify duplicate FCA charges** — POs with > 1 FCA-related adjustment note | FCA Auditor | Weekly | **Financial-Justification** — recover overpayment |
| **Identify missing FCA charges** — POs where FCA service fee was not invoiced at all | FCA Auditor | Weekly | **Operational** — follow up with vendor |
| **Flag Ashton (WH 335) shipments from CVRO vendors** — FCA service is ineligible for these routes | FCA Auditor / Supply Planner | Weekly | **Financial-Justification** — reject illegitimate charges |
| **Review over/under billing** — `Classification` = "more than expected" or "less than expected" | FCA Auditor | Weekly | **Financial-Justification** — negotiate or adjust payment |

---

## 3. Key Metrics / Measures

**There are zero DAX measures in this model.** All logic is implemented as **calculated columns** in Power Query or DAX. The model acts as a flat worklist table.

### Key calculated columns

| Column | Table | Business meaning | Logic | Flag |
|---|---|---|---|---|
| `FCA_SERVICE` | POAdjusment | Expected FCA service fee for this PO | `POAmount × PIS% / (1 − PIS%)` | |
| `Status` | POAdjusment | Audit pass/fail | `IF(ABS(AdjAmount − FCA_SERVICE)/FCA_SERVICE < 0.005, "PASSED", "FAILED")`; special case: CVRO+WH335 always FAILED | ⚠️ hardcoded 0.5% tolerance — see §9 |
| `PO Status` | POAdjusment | PO lifecycle stage text label | SWITCH on `POStatusCode` (10=Cfm Required through 99=Canceled) | Low |
| `FCA_Count` | POAdjusment | Count of FCA references in adjustment notes for this PO | `LOOKUPVALUE(RequireVerification[FCA_Count], PO #, PONumber)` | ⚠️ cross-table lookup |
| `FCA_Count` | RequireVerification | Number of adjustment notes containing "FCA" text per PO | `COUNTROWS(FILTER(POAdjusment, PONumber=CurrentPO AND SEARCH("FCA", Note)>0))` | |
| `Classification` | RequireVerification | Audit classification text | Complex `SWITCH(TRUE(), ...)` — 7 possible values: duplicate/missing/over/under/ineligible/blank | ⚠️ maintains business rules — see §9 |

### Audit classification values

| Value | Meaning |
|---|---|
| (blank) | No adjustment and no FCA expected — no action needed |
| `"FCA Serivce is ineligible for Ashton shipment from CVRO suppliers"` | Special case: CVRO vendors shipping to WH 335 should NOT charge FCA service (typo in column: "Serivce") |
| `"Duplicate FCA Service"` | More than one FCA-related adjustment note found for this PO |
| `"Missing FCA Service"` | No FCA adjustment found but one was expected |
| `"FCA Service Adjustment is more than expected"` | Invoice adjustment > expected FCA service fee |
| `"FCA Service Adjustment is less than expected"` | Invoice adjustment < expected FCA service fee |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`POAdjusment`** | `ashley-edw.database.windows.net / ASHLEY_EDW` — `Wholesale_ProductSourcing_AFI.PoMaster` LEFT JOIN `Wholesale_Purchasing_AFI.VENNAM` LEFT JOIN `Wholesale_ProductSourcing.POAdjustments` (subquery). Filtered: `POIncoterm='FCA'`, `POStatusCode BETWEEN 20 AND 50`, `POCreatedDate >= '2025-09-01'` | Direct Azure SQL EDW | Medium — clear SQL, but `POAdjustments` subquery has `WHERE 1=1` and commented-out filters suggesting development |
| **`PISAdjustment`** | **SharePoint Excel** — `https://masterashley.sharepoint.com/.../FCA Tracking.xlsx` (Summary sheet, columns: Vendor #, PIS Adjustment %) | **SharePoint Excel** | ⚠️ **HIGH** — manual spreadsheet, ungoverned |
| **`VendorList`** | **SharePoint Excel** — `https://masterashley.sharepoint.com/.../VENDOR LIST AFT & 232.xlsx` (AFI sheet) | **SharePoint Excel** | ⚠️ **HIGH** — manual spreadsheet, 7 columns with column positions hardcoded (`Column3`, `Column4`, etc.) |
| `RequireVerification` | **Calculated table** — `DISTINCT(SELECTCOLUMNS(POAdjusment, ...))` | DAX Calculated | Medium — derived from POAdjusment with same cardinality |
| `Refreshed date` | Power Query — `DateTimeZone.UtcNow() + 7 hours` (Vietnam time) | PQ | Low — display use only |

> **No Fabric sources.** SQL hits `ashley-edw.database.windows.net`.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** **Purchase Order** (one row per FCA PO)

| Table | Grain |
|---|---|
| `POAdjusment` | PO Number — filtered to FCA incoterm, status 20–50, created >= Sept 2025 |
| `RequireVerification` | PO Number — derived from POAdjusment (same grain, enriched with Classification) |
| `PISAdjustment` | Vendor Number — per-vendor PIS adjustment % (one row per vendor) |
| `VendorList` | Vendor Number — vendor attributes |

**Snapshot strategy: Live data (no snapshots).**
- `POAdjusment` queries live EDW — returns latest PO data on each refresh
- `PISAdjustment` and `VendorList` — latest state of SharePoint Excel files
- No historical tracking of PO status changes or audit outcomes

---

## 6. Dimensions Used

| Dimension | Table | Connected? | Notes |
|---|---|---|---|
| **Vendor** | `VendorList` (7 cols) | ✅ — `POAdjusment[VendorNumber]`, `RequireVerification[Vendor #]` | `NUMBER`, `NAME`, `OFFICE`, `ACTIVE`, `SCP ANALYST`, `GLOBAL SUPPLY CHAIN PLANNER`, `ASIA SCP` |
| **PIS Parameters** | `PISAdjustment` (2 cols) | ✅ — `POAdjusment[VendorNumber]` via `RELATED()` | Vendor-specific % used to compute expected FCA fee |
| **Date** | LocalDateTables only | — | No fiscal calendar dimension; dates used for date-slicing via LocalDateTable connections |

**Notable:** No `DimProduct`, no `DimWarehouse`, no `DimCustomer` — this model only needs vendor and PO-level data. Warehouse appears as `POWarehouse` string (not connected to `z_WarehouseMaster`).

---

## 7. Duplication / Consolidation Signals

1. **`POAdjusment` and `RequireVerification` contain the same rows at the same grain** — `RequireVerification` is a `SELECTCOLUMNS(...)` of `POAdjusment` with added `FCA_Count` and `Classification` columns. The two tables exist because calculated columns in `POAdjusment` use `RELATED(PISAdjustment[...])` which requires a physical relationship, while `RequireVerification` uses `LOOKUPVALUE` and `FILTER` that work without direct joins. This duplication of grain is architecturally justified but creates a data quality risk — if the two tables drift (e.g., one refreshes before the other), the FCA_Count lookup returns stale values.

2. **`FCA_Count` column exists in both `POAdjusment` and `RequireVerification`** with different implementations:
   - POAdjusment: `LOOKUPVALUE(RequireVerification[FCA_Count], PO #, PONumber)`
   - RequireVerification: `COUNTROWS(FILTER(POAdjusment, Note CONTAINS "FCA"))`
   Circular dependency: POAdjusment looks up RequireVerification's count; RequireVerification counts POAdjusment's notes. This works because RequireVerification is built from POAdjusment data, but the logic is fragile and circular.

3. **`Status` in `POAdjusment` (Audit PASSED/FAILED) vs. `Classification` in `RequireVerification` (textual reason)** — two columns representing the same audit concept at different detail levels. `Status` is a binary pass/fail; `Classification` explains why. Both should be in the same table for filtering consistency.

---

## 8. Open Questions

1. **Is this report actively used for financial decisions (approving/rejecting vendor payments)?** The "FAILED" status identifies invoices that should not be paid as-is. Is there a downstream process — a case in an ERP, a ticket, a notification to AP — or is it a manual review?

2. **Who maintains the `FCA Tracking.xlsx` spreadsheet** and how often are PIS Adjustment % values updated? If a PIS % changes mid-contract, is there a historical record of what % applied to POs from different periods?

3. **Why `'2025-09-01'` as the PO creation date filter?** Is this when the FCA program started? If so, POs before this date may have undocumented FCA charges that the report cannot see.

4. **`VENDOR LIST AFT & 232.xlsx` columns are selected by position** (`Column3`, `Column4`, etc.) rather than by header name. If the spreadsheet structure changes (e.g., a column is inserted), the column mapping breaks silently. Has this happened before?

5. **The `Refreshed date` table uses Vietnam time (+7).** Is the report user/team based in Vietnam? Are other stakeholders in different time zones seeing mismatched refresh timestamps?

6. **`POAdjustments` subquery in SQL has commented-out filter `adjcategory = 6`.** What is category 6? Why was it commented out? Are other adjustment categories now included in the audit?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`0.005` (0.5%)** | `POAdjusment[Status]` calc column | Tolerance threshold: if `ABS(Actual − Expected)/Expected < 0.005`, mark PASSED; else FAILED | **No** — ±0.5% tolerance is undocumented; basis for selecting 0.5% (materiality threshold? accounting policy?) not explained |
| **`FCA_SERVICE = POAmount × PIS% / (1 − PIS%)`** | `POAdjusment[FCA_SERVICE]` calc column | Expected FCA fee derived from PIS Adjustment % | **Partially** — the formula is visible in the column but the derivation logic `PIS%/(1−PIS%)` is not explained; the denominator is `(1−PIS%)` which means `FCA_SERVICE` is larger than `POAmount × PIS%` would suggest |
| **`'2025-09-01'`** | `POAdjusment` SQL | Date filter: only POs created on/after Sept 1, 2025 are included | **No** — appears to be program start date; no comment in SQL |
| `POStatusCode BETWEEN 20 AND 50` | `POAdjusment` SQL | Filters to "On-Order" through "Receiver" status; excludes "Cfm Required" (10), "Closed" (60), "Canceled" (99) | **Partially** — SQL comment explains; excludes unconfirmed and completed POs |
| `CVRO + WH 335 = ineligible` | `POAdjusment[Status]` and `RequireVerification[Classification]` | CVRO vendors shipping to WH 335 (Ashton) should not charge FCA service | **Partially** — business rule embedded in two calculated columns; motivation (logistics route not qualifying for FCA) undocumented |
| `SEARCH("FCA", AdjustmentNote, 1, 0) > 0` | `RequireVerification[FCA_Count]` | Counts adjustments where the word "FCA" appears in the note text | **No** — substring search on free-text notes is fragile (typos like "FCA Serivce" in the model itself suggest data entry quality issues) |
| `DateTimeZone.UtcNow() + 7` | `Refreshed date` PQ | Vietnam time display | **No** — UTC+7 offset; timezone rationale undocumented |

---

## 10. Comparability / Consistency

1. **`PISAdjustment` is a percentage value but its derivation is opaque.** It comes from a SharePoint Excel file with no documentation on how the PIS % is calculated. If this percentage changes inconsistently across vendors, the FCA_SERVICE calculation cannot be validated externally.

2. **`VendorList` uses column position mapping (`Column3`, `Column4`, etc.).** This is fragile — if the Excel sheet header row changes or a column is added, the wrong data will populate `NUMBER`, `NAME`, etc. The `POAdjusment` SQL joins on `VendorNumber` but uses a different vendor table (`Wholesale_Purchasing_AFI.VENNAM`) for vendor attributes (`VNAME`, `VNAMA`). Vendor attributes may differ between the SQL-sourced dimension and the SharePoint Excel version.

3. **The `FCA_Count` circular dependency** — `POAdjusment[FCA_Count] = LOOKUPVALUE(RequireVerification[FCA_Count], ...)` and `RequireVerification[FCA_Count] = COUNTROWS(FILTER(POAdjusment, ...))`. If the two tables are not refreshed in the correct order, counts may be off by one refresh cycle.

4. **`RequireVerification[Audit Status]` is a source column from `SELECTCOLUMNS`** — it copies `POAdjusment[Status]` into the calculated table. But `RequireVerification[Status]` is defined as a separate column that is blank (no expression assigned). The `Audit Status` column is the one that actually passes through the POAdjusment status. Two similarly named columns (`Status` and `Audit Status`) exist in `RequireVerification` with different content — potential user confusion.

---

## Key Highlights

**Zero DAX measures — wszystkie logic là calculated columns.** Model này không có KPI, không có aggregation — là một **worklist/audit table** thuần túy. Mỗi PO được gán một `Status` (PASSED/FAILED) và `Classification` (lý do) dựa trên so sánh invoice adjustment thực tế vs. expected FCA service fee.

**Unique audit rule engine trong calculated columns:**
- `FCA_SERVICE = POAmount × PIS% / (1−PIS%)`
- `Status = PASSED` nếu error < 0.5%; special case CVRO+WH335 luôn FAILED
- `Classification` với 7 output states: blank, ineligible, duplicate, missing, over, under
- Đây là business rule engine chạy hoàn toàn trong DAX calc columns

**🔴 Two ungoverned SharePoint Excel sources:**
- `FCA Tracking.xlsx` — per-vendor PIS Adjustment % (critical input cho expected fee calculation)
- `VENDOR LIST AFT & 232.xlsx` — vendor attributes mapped by column position (siêu fragile)

**🔴 Circular dependency** giữa `POAdjusment[FCA_Count]` và `RequireVerification[FCA_Count]` — mỗi cái LOOKUP/FILTER từ cái kia. Nếu refresh order sai, counts bị lệch.

**🔴 `0.5%` tolerance threshold hardcoded** — không phải parameter, không có tài liệu giải thích tại sao là 0.5%

**🔴 `SEARCH("FCA", Note)` trên free-text** — fragile substring matching. Typo "FCA Serivce" (chính trong model classification label) cho thấy data entry quality issues.

**Architecture notes:** 
- Đây là model duy nhất dùng `ASHLEY_EDW` database (viết hoa) thay vì `ashley_edw`
- `Refreshed date` tính theo giờ Vietnam (+7)
- `POStatusCode` mapping (10→Cfm Required through 99→Canceled) được hardcode trong calc column
- Date filter `'2025-09-01'` — program start date, không document

---

*Analysis based on BIM definition extracted 2026-07-09. BIM saved to [bim/FCA_Services_Fee_Audit.bim](bim/FCA_Services_Fee_Audit.bim). No bundle indexes were modified.*
