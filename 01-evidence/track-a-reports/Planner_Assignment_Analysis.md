# Planner Assignment — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `393360eb-a8d3-4ef2-8a53-489e29c8d676`  
**Report ID:** `1b52d60a-1844-4131-b864-63c8a1a168c4`  
**Analysis Date:** 2026-07-09  
**Model Size:** 1 table (`Data`) + LocalDateTables; **1 DAX measure**; Compatibility Level 1567  
**BIM File:** [bim/Planner_Assignment.bim](bim/Planner_Assignment.bim) — 63.5 KB  

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For every item-SKU in the most recent Logility forecast, is the item currently assigned to the correct demand planner based on its product lifecycle status? If not, who should it be reassigned to?

This is a **data quality / planner governance audit** worklist — not an analytical report. It identifies items where the `ienForecastPlannerID` (the planner code stored in the ERP item master environment table) does not match the expected planner for that item's lifecycle stage.

The expected planner assignments encode **organizational knowledge about team structure**: who handles what type of items based on lifecycle, exclusivity, distribution channel, and collective class.

**Chain links served:** **Forecast Governance** — ensuring each item is assigned to the correct demand planner/forecast analyst so that forecast reviews and updates are properly routed.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Reassign Discontinued items to SKUJAK** — items with Current Status = 'D' should be transitioned from the inline planning team to the specialist who manages discontinuation runout | Life Cycle Planner / Planning Manager | **Weekly** (after each FC publish) | **Performance/Governance** — ensure proper planner coverage |
| **Reassign Homestore Exclusive items to TMANGAN** — items flagged as Homestore-only should be handled by the Homestore specialist | Planning Manager | Weekly | **Performance/Governance** |
| **Reassign INT Exclusive items to TRACYHO** — items exclusive to International channel go to the International specialist | Planning Manager | Weekly | **Performance/Governance** |
| **Reassign Drop INT Bedding items to SLYONS** — bedding items with Future Drop status that are International should go to a specific bedding specialist | Life Cycle Planner | Weekly | **Performance/Governance** |
| **Fix "Wrong Planner" inline items** — Inline items assigned to Drop planners (vice versa) are flagged for correction | Planning Manager | Weekly | **Performance/Governance** |
| **Audit planner assignment changes over time** — see which items have shifted between planners (implicit via repeated runs) | Planning Manager | Monthly | **Performance/Governance** |

### Organizational Knowledge Encoded in the Model

This model captures **implicit organizational structure rules**:
- The **inline planning team** consists of exactly 3 planners: **HNGUYEN2, VHA, KHHO**
- **SKUJAK** handles all Discontinued items
- **TMANGAN** handles Homestore Exclusive items
- **TRACYHO** handles International Exclusive items
- **SLYONS** handles Drop International Bedding items
- All non-inline planners listed above are NOT valid for Inline items
- Conversely, inline planners are NOT valid for Drop items — these must be transitioned off

---

## 3. Key Metrics / Measures

### DAX Measure (1 total)

| Measure | Table | Business meaning | Logic |
|---|---|---|---|
| `Issue Count` | `Data` | Total number of items with a Planner Assignment Issue | `COUNTROWS(FILTER(Data, NOT ISBLANK(Data[Planner Assignment Issue])))` |

### Calculated Column: `Status` (in SQL, not DAX)

The `Status` column classifies each item into one of 5 lifecycle-based categories using a SQL CASE expression:

```sql
CASE
    WHEN CPD.[AFI Item Status] = 'D'                              THEN 'Disco'
    WHEN IPK.[ienFutureStatus] IN ('P', 'F', 'E', 'L')             THEN 'Drop'
    WHEN [IM].[ExclusiveComment] = 'Homestore'                     THEN 'Homestore Exclusive'
    WHEN CPD.[Market Introduced At] LIKE 'INT%'                    THEN 'INT Exclusive'
    ELSE 'Inline'
END AS [Status]
```

| Status Value | Condition | Meaning |
|---|---|---|
| `Disco` | `Current Status = 'D'` | Item is discontinued — inventory runout mode |
| `Drop` | `Future Status IN ('P','F','E','L')` | Item is planned for future discontinuation (P=Planned Drop, F=Future Drop, E=Phase-out, L=Liquidate) |
| `Homestore Exclusive` | `ExclusiveComment = 'Homestore'` | Item is exclusive to Ashley HomeStores retail channel |
| `INT Exclusive` | `Market Introduced At LIKE 'INT%'` | Item was introduced for International markets |
| `Inline` | Everything else | Standard item managed by the main planning team |

### Power Query M Business Rule Engine: `Planner Assignment Issue`

The column implements a **6-condition rule engine** in a single `Table.AddColumn` step:

```m
each
    if [Status] = "Disco" and [Planner] <> "SKUJAK" 
        then "Disco - Should be SKUJAK"
    
    else if [Status] = "Homestore Exclusive" and [Planner] <> "TMANGAN" 
        then "Homestore Exclusive - Should be TMANGAN"
    
    else if [Status] = "INT Exclusive" and [Planner] <> "TRACYHO" 
        then "INT Exclusive - Should be TRACYHO"
    
    else if [Status] = "Drop" and [Collective Class] = "BEDDING" 
                and Text.Contains(Text.Upper(Text.From([Market Introduced At])), "INT") 
                and [Planner] <> "SLYONS" 
        then "Drop INT Bedding - Should be SLYONS"
    
    else if [Status] = "Drop" and List.Contains({"HNGUYEN2", "VHA", "KHHO"}, [Planner]) 
        then "Wrong Planner"
    
    else if [Status] = "Inline" and not List.Contains({"HNGUYEN2", "VHA", "KHHO"}, [Planner]) 
        then "Wrong Planner"
    
    else null
```

#### Rule-by-rule analysis:

| # | Condition | Trigger | Correct Planner | Issue Message |
|---|---|---|---|---|
| **1** | Disco item assigned to anyone other than SKUJAK | `Status="Disco" AND Planner<>"SKUJAK"` | SKUJAK | "Disco - Should be SKUJAK" |
| **2** | Homestore Exclusive assigned to anyone other than TMANGAN | `Status="Homestore Exclusive" AND Planner<>"TMANGAN"` | TMANGAN | "Homestore Exclusive - Should be TMANGAN" |
| **3** | INT Exclusive assigned to anyone other than TRACYHO | `Status="INT Exclusive" AND Planner<>"TRACYHO"` | TRACYHO | "INT Exclusive - Should be TRACYHO" |
| **4** | Drop item + Bedding + INT channel — not SLYONS | `Status="Drop" AND CC="BEDDING" AND MarketINT AND Planner<>"SLYONS"` | SLYONS | "Drop INT Bedding - Should be SLYONS" |
| **5** | Drop item assigned to an INLINE planner | `Status="Drop" AND Planner IN {HNGUYEN2,VHA,KHHO}` | *(not specified)* | "Wrong Planner" |
| **6** | Inline item NOT assigned to an INLINE planner | `Status="Inline" AND Planner NOT IN {HNGUYEN2,VHA,KHHO}` | HNGUYEN2, VHA, or KHHO | "Wrong Planner" |

**Critical insight on Rule #4:** The condition `Text.Contains(Text.Upper(Text.From([Market Introduced At])), "INT")` overlaps with Rule #3's Status condition (`Market Introduced At LIKE 'INT%'`). However, Rule #3 runs BEFORE Rule #4 in the `else if` chain. If an item matches "INT Exclusive" status (Rule #3), Rule #4 **never fires for that item**. Rule #4 only fires for items that are NOT already classified as INT Exclusive but still have "INT" in their Market Introduced At and are Drop BEDDING. This suggests Rule #4 was written to catch a specific edge case that Rule #3 missed.

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **`Data`** | `ashley-edw.database.windows.net / Ashley_edw` — 4-table JOIN: | Direct Azure SQL EDW + PQ | Medium |

### Underlying EDW Tables:
| Alias | Full Table | Purpose |
|---|---|---|
| `FCC` | `SupplyChain_Enh.ForecastCommonContainer_Logility` | Master item-list from latest Logility forecast snapshot; excludes warehouses C,12,101,151,16,20,213 |
| `CPD` | `SupplyChain_DW.DimCurrentProductDetails` | Current product attributes: Collective Class, Item Ext Series Number, AFI Item Status, Import/Domestic Code, Market Introduced At |
| `IM` | `Enterprise_DW.DimItemMaster` | `ExclusiveComment` field (e.g., 'Homestore') |
| `IPK` | `MasterData_ProductKnowledge.Item_ENV` | `ienForecastPlannerID` (current planner), `ienFutureStatus`, filtered to `ienEnvironmentCode='AFI'` |

### Data Processing:
- **SQL** performs the SELECT + CASE to classify items into `Status`
- **Power Query M** adds the `Planner Assignment Issue` column using the 6-condition rule engine
- **Result:** A flat table with 11 columns — no relationships, no further transformations

> **No SharePoint, no Excel.** Single-source EDW SQL + Power Query enrichment.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** **Item SKU** (`Item-Lvl1`) — one row per distinct item in the latest Logility forecast snapshot.

**Snapshot strategy:** **Latest-only.** `WHERE FCC.FileDate = (SELECT MAX(FileDate) FROM ForecastCommonContainer_Logility)`. No historical tracking — every refresh completely replaces the dataset. Cannot answer "which items changed planner assignment since last week."

---

## 6. Dimensions Used

**None.** This is a single flat table with no dimension relationships. All descriptive attributes (Collective Class, Current Status, Future Status, etc.) are embedded source columns in the `Data` table. The model is entirely self-contained.

| Column | Source | Purpose |
|---|---|---|
| `Item-Lvl1` | FCC (Logility) | Item SKU identifier |
| `Planner` | IPK (Item_ENV) | Current assigned planner code |
| `Series` | CPD | Item Ext Series Number (product family) |
| `Collective Class` | CPD | Product category |
| `Current Status` | CPD | `AFI Item Status` |
| `Future Status` | IPK | `ienFutureStatus` |
| `I/D Code` | CPD | Import/Domestic indicator |
| `ExclusiveComment` | IM (DimItemMaster) | Channel exclusivity flag ('Homestore') |
| `Market Introduced At` | CPD | Market introduction code |
| `Status` | SQL CASE | Derived classification: Disco/Drop/Homestore Exclusive/INT Exclusive/Inline |
| `Planner Assignment Issue` | PQ M | Business rule result — null if OK, text if issue found |

---

## 7. Duplication / Consolidation Signals

1. **Model is 1 table + 1 measure** — minimal by design. This is a focused audit worklist, not an analytical model. There is nothing to consolidate.

2. **The `Status` classification logic** (Disco/Drop/Homestore/INT/Inline) overlaps with `z_ProductDetails[Life Cycle Status]` in Product Review (NEW) and `Status (groups)` in GF Act+Fcst. However, the logic here is **independently implemented in SQL** and uses different criteria:
   - This model: Status='D' → Disco; FutureStatus IN {P,F,E,L} → Drop
   - Product Review (NEW): FutureStatus {F,P,L,E} → Drop; InvoicingMonths ≤ 9 → "New"; else "Current"
   - GF Act+Fcst: Current+Future 2-char codes bucketed into 5 groups
   Cross-model status comparisons for the same item may produce different classifications.

3. **The 7 planner names hardcoded in M code** — if the team structure changes (new planner added, planner leaves, roles reassigned), the M code must be edited manually. This is a single point of failure for ongoing data quality.

---

## 8. Open Questions

1. **What happens after an issue is identified?** Is there a downstream process — an automated ticket, a weekly email to the planning manager, a mass update script? Or does someone manually change the planner assignment in Logility/ERP one item at a time?

2. **Who are SKUJAK, TMANGAN, TRACYHO, SLYONS, HNGUYEN2, VHA, KHHO?** Are these still current employees? If a planner changes their role or leaves, the model silently produces incorrect flags until someone edits the M code.

3. **What defines "Wrong Planner" for Drop items?** Rules 5–6 flag Drop items assigned to inline planners, but don't specify WHO the correct planner should be. Is the expectation that the planner should have been set to SKUJAK (same as Disco), or is there another Drop specialist not captured in the rules?

4. **Warehouse exclusions `NOT IN ('C','12','101','151','16','20','213')`** — why are items from these warehouse locations excluded from the audit? Do they represent non-forecasted warehouses (C=wholesale, others = specialty DCs)?

5. **Rule #4 edge case overlap with Rule #3** — see §3 analysis. Has the Drop INT Bedding rule ever actually fired? Or is it dead code because all INT items are already caught by Rule #3's `MarketIntroAt LIKE 'INT%'` → "INT Exclusive" status classification?

6. **Why does Rule #1 check for Disco items NOT assigned to SKUJAK, but there's no equivalent "Disco should be SKUJAK — Done" counterpart?** If SKUJAK is the correct planner for all Disco items, what planner do Disco items HAVE if they're correctly assigned? The rule only flags exceptions, never confirms correct assignments.

7. **Could a single item trigger multiple rules?** The `else if` chain ensures the first matching rule wins. But what if an item is both "Disco" AND "Drop"? The SQL CASE puts 'D' first → Disco wins. What if an item has `Status = D` AND `ExclusiveComment = 'Homestore'`? The SQL CASE checks D first, so it becomes "Disco" (Homestore status never applied). Are these overlaps intentional or data quality issues themselves?

---

## 9. Business Assumptions / Magic Numbers

| Constant | Location | What it does | Documented? |
|---|---|---|---|
| **Planner alias "SKUJAK"** | M rule #1 | Discontinued items → SKUJAK | **No** — planner name hardcoded |
| **Planner alias "TMANGAN"** | M rule #2 | Homestore Exclusive → TMANGAN | **No** |
| **Planner alias "TRACYHO"** | M rule #3 | INT Exclusive → TRACYHO | **No** |
| **Planner alias "SLYONS"** | M rule #4 | Drop INT Bedding → SLYONS | **No** |
| **Planner aliases {"HNGUYEN2","VHA","KHHO"}** | M rules #5–6 | Inline planning team — exactly these 3 | **No** — hardcoded list |
| `FutureStatus IN ('P','F','E','L')` | SQL CASE | Defines which future status codes = "Drop" | **Partially** — codes visible in SQL; meanings not documented |
| `Market Introduced At LIKE 'INT%'` | SQL CASE | Identifies INT (International) exclusive items by market prefix | **No** — assumes all INT items start with "INT" |
| `ExclusiveComment = 'Homestore'` | SQL CASE | Identifies Homestore exclusive items | **No** |
| `FCC.[Location] NOT IN ('C','12','101','151','16','20','213')` | SQL WHERE | Excluded warehouses — not documented why these are excluded from planner assignment audit | **No** |
| `ienEnvironmentCode = 'AFI'` | SQL WHERE | Only checks planner assignments for the AFI environment (not e.g., import, HS, etc.) | **Partially** — visible in SQL |
| `MAX(FileDate)` | SQL WHERE | Only evaluates latest Logility forecast snapshot; ignores older snapshots | **No** |

---

## 10. Comparability / Consistency

1. **Cross-model lifecycle status disagreement.** The `Status` column's classification logic (Disco/Drop/Homestore/INT/Inline) uses different rules than every other model's lifecycle classification. For example:
   - Items with `Future Status IN ('P','F','E','L')` are "Drop" here, but in Product Review (NEW) they could also be "Drop" but through different logic (DAX SWITCH with additional conditions about Months Invoicing)
   - Items with Current Status = 'D' are "Disco" here; other models may classify them as "DROPPED" or "LIQUIDATED"
   
2. **`Status` in SQL vs. `Life Cycle Status` in DAX.** This model computes the classification in SQL before Power Query. Other models compute it in DAX as calculated columns. The two implementations can diverge over time as item master data changes.

3. **Zero relationships.** This model has no date dimension and no product dimension. If it were ever used in a composite model scenario, date or product filters from other tables would have no effect on the `Data` table. Users could incorrectly think a date filter is being applied.

4. **7 planner names hardcoded.** If the actual ERP system (`Item_ENV`) is the source of truth for planner assignments, the model's "expected" planners should ideally come from a reference table rather than being hardcoded. Currently, if a planner is reassigned in the ERP but not also updated in this model, the model's expected values are stale.

---

## Key Highlights

**Smallest model in workspace** — 1 table, 1 measure, 63 KB BIM. Zero DAX complexity — all logic is in SQL CASE + Power Query M.

**Business rule engine — the "brain" of this report:**
```
Status Classification (SQL CASE):
    AFI Status = 'D'                        → "Disco"
    FutureStatus IN {P,F,E,L}               → "Drop"  
    ExclusiveComment = 'Homestore'          → "Homestore Exclusive"
    MarketIntroAt LIKE 'INT%'               → "INT Exclusive"
    Everything else                         → "Inline"

Planner Check (Power Query M — 6 conditions, sequential):
    [1] Disco NOT SKUJAK                     → "Disco - Should be SKUJAK"
    [2] Homestore Exclusive NOT TMANGAN      → "Homestore Exclusive - Should be TMANGAN"
    [3] INT Exclusive NOT TRACYHO            → "INT Exclusive - Should be TRACYHO"
    [4] Drop + BEDDING + INT NOT SLYONS      → "Drop INT Bedding - Should be SLYONS"
    [5] Drop assigned to {HNGUYEN2,VHA,KHHO} → "Wrong Planner"
    [6] Inline NOT {HNGUYEN2,VHA,KHHO}       → "Wrong Planner"
```

**🔴 7 planner names hardcoded** — the single most fragile aspect. SKUJAK, TMANGAN, TRACYHO, SLYONS, HNGUYEN2, VHA, KHHO are written as string literals in M code. If the planning team structure changes, this model breaks silently until someone edits M.

**🔴 Rule #4 likely dead code.** The `Drop INT Bedding → SLYONS` condition requires `MarketIntroAt` to contain "INT" — but items with `MarketIntroAt LIKE 'INT%'` are already classified as "INT Exclusive" by Rule #3's SQL CASE, before Rule #4 in the M else-if chain ever evaluates. This rule likely never fires for any item.

**Organizational knowledge captured in the model:**
- The **inline team** is exactly 3 people: HNGUYEN2, VHA, KHHO
- **Discontinued items** must be transferred to SKUJAK
- **Homestore Exclusive items** → TMANGAN
- **International Exclusive items** → TRACYHO
- **Drop items** must be moved OFF the inline team (no longer their responsibility)
- A special case exists for **International Bedding drops** → SLYONS

**The model is a snapshot of organizational structure at a point in time** — it encodes implicit team structure that is not documented anywhere else in the data ecosystem.

---

*Analysis based on BIM definition extracted 2026-07-09. BIM saved to [bim/Planner_Assignment.bim](bim/Planner_Assignment.bim). No bundle indexes were modified.*
