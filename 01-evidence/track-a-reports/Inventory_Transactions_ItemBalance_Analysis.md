# Inventory Transactions and Item Balance Detail — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `cd43ccd1-8dd6-4622-ba5c-4267bbeca9a7`  
**Report ID:** `d1812b83-c29d-477e-bbcf-1711870dff79`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~1.28 MB (BIM); 19 tables, 11 DAX measures in `a_Measures`

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "For each item × warehouse combination, what is the current on-hand inventory balance (in units and cubes), and how did it move over the past 18 months via receipts, shipments, and warehouse transfers?"

**Primary chain links served:** **Inventory** + **Receipts**  
This is an operational inventory visibility report combining two views:
- **Item Balance** — weekly on-hand snapshot (quantity + cube volume + FOB $) at Item × WH level
- **Inventory Transaction History** — weekly aggregated movements (sales shipments, PO receipts, manufacturing receipts, and warehouse transfers) by transaction code

Secondary links touched:
- **Production/Receipts** — manufacturing receipts (RM) and purchase order receipts (RP) are tracked
- **Supply** — issuing/receiving warehouse transfers (IW/RW) visible for inter-warehouse movements

This report does **not** cover demand forecast, forecast accuracy, or planning signals — it is a pure stock-movement audit tool.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Investigate unexpected on-hand balance** — drill into weekly balance history to find when a spike/drop occurred and which transaction code caused it | Inventory Analyst / Planner | Ad-hoc | Operational |
| **Verify warehouse transfer was received** — confirm IW (issuing) has a matching RW (receiving) entry in the same week for the same item | Inventory Analyst / Logistics | Ad-hoc | Operational |
| **Audit cube utilization by storage type** — `On Hand Cubes`, `Storage Type`, `Storage Type L2` and `L2 Cubes % of Storage Type` show space usage across CSG/UPH/BED categories | Warehouse Operations / DC Manager | Weekly / monthly | Operational |
| **Identify items with zero movement** — cross-referencing on-hand balance against transaction history reveals items with stock but no recent shipments or receipts | Inventory Analyst | Monthly | Operational |
| **Validate manufacturing receipt vs. PO receipt split** — `Manufacturing Receipt` vs. `Purchase Order` and `Receipts in to WH` let planners verify which supply source delivered | Supply Planner / Analyst | Weekly | Operational |
| **Track net inventory change over a period** — `Net Inv Change` = transfers + receipts − shipments gives a net movement audit for reconciliation | Inventory Analyst / Finance | Monthly | Operational / Financial-Justification |
| **Classify item type (FG / KIT / CMP / Part)** — `Item Type` on each item determines which inventory pool it belongs to, enabling separate analysis of finished goods vs. components | Warehouse Operations | Ad-hoc | Operational |

**No Performance/Governance decisions are visible** — this is entirely an operational and audit-oriented report.

---

## 3. Key Metrics / Measures

### On-Hand Balance Measures

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `On Hand Qty` | Weekly on-hand quantity snapshot | Item × WH × fiscal week | `SUM('Item Balance'[On Hand Quantity])` — from `Inventory_Enh_History.ItemBalance` EDW table |
| `On Hand Cubes` | On-hand volume in cubic feet | Item × WH × fiscal week | `SUMX(z_ProductDetails, z_ProductDetails[Cubes] * [On Hand Qty])` — multiplies `Cubes` from product master by on-hand qty |
| `L2 Cubes % of Storage Type` | Share of on-hand cubes within current product filter | Aggregated | `DIVIDE([On Hand Cubes], CALCULATE([On Hand Cubes], ALLSELECTED(z_ProductDetails)))` — denominator is all selected products; varies by active slicer context |
| `L2 Unit % of Storage Type` | Share of on-hand units within current product filter | Aggregated | `DIVIDE([On Hand Qty], CALCULATE([On Hand Qty], ALLSELECTED(z_ProductDetails)))` |

**⚠️ `InventoryDollars` (calculated column) — BROKEN:**  
`'Item Balance'[On Hand Quantity] * 'Item Balance'[itbStdCost]`  
The column `itbStdCost` does **not exist** in the `Item Balance` table or its SQL query. The EDW query selects only `ItemNumber`, `Warehouse`, `DateWeekEnding`, `OnHandQty`, `ItemStatus`. `itbStdCost` was never added to the SQL. This column always returns BLANK/0.

**`InvFob$` (calculated column):**  
`'Item Balance'[On Hand Quantity] * RELATED(z_ProductDetails[FOB Price])`  
Works correctly — uses FOB Price from `z_ProductDetails` dataflow. This is the only working dollar-value column on the balance table.

### Transaction Movement Measures

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Sales Shipments` | Units shipped to customers | Item × WH × fiscal week | `SUM([Absolute Qty])` filtered to `TransactionCodeDesc = "Sales Shipments"` — **uses Absolute Qty (always positive)** |
| `Receipts in to WH` | Units received from PO + manufacturing | Item × WH × fiscal week | `SUM([Transaction Qty]) where CodeDesc = "Receipt from manufacturing order" + SUM([Transaction Qty]) where CodeDesc = "Receipt from purchase order"` — **uses Transaction Qty (positive receipts)** |
| `Purchase Order` | PO receipt qty | Item × WH × fiscal week | `SUM([Transaction Qty]) where TransactionCode = "RP"` |
| `Manufacturing Receipt` | Manufacturing receipt qty | Item × WH × fiscal week | `SUM([Transaction Qty]) where TransactionCode = "RM"` |
| `Issuing Transfer` | Units leaving warehouse (transfer out) | Item × WH × fiscal week | `SUM([Transaction Qty]) where CodeDesc = "Transfer: Issuing Warehouse"` — **⚠️ sign is negative in source (outbound movement); summing raw Qty means this measure is negative** |
| `Receiving Transfer` | Units arriving at warehouse (transfer in) | Item × WH × fiscal week | `SUM([Transaction Qty]) where CodeDesc = "Transfer: Receiving Warehouse"` — **positive in source** |
| `Net Inv Change` | Net inventory movement for period | Item × WH × fiscal week | `[Issuing Transfer] + [Receipts in to WH] + [Receiving Transfer] - [Sales Shipments]` — **⚠️ sign mechanics inconsistent; see §9** |

**Note on `Receipts in to WH` vs `Purchase Order` + `Manufacturing Receipt`:**  
`Receipts in to WH` filters by `TransactionCodeDesc` (text strings); `Purchase Order` and `Manufacturing Receipt` filter by `TransactionCode` (codes RP and RM). These are measuring the same thing via two different filter fields. They should be equal, but if `TransactionCodeDesc` values change in the EDW (rename/reclassification), `Receipts in to WH` silently breaks while `Purchase Order`/`Manufacturing Receipt` remain correct (and vice versa).

### Row-Level Calculated Columns

**`Inventory Transaction History`:**

| Column | Logic | Notes |
|---|---|---|
| `Error` (= `ItemFlag`) | `CASE: Part-class items → 'Part'; else original ITW.ItemFlag` | First `[ItemFlag]` column from SQL |
| `ItemFlag2` | `CASE: Part-class + suffix 'UN' → 'KIT'; Part-class otherwise → 'CMP'; else → 'FG'` | **Second SQL column also named `[ItemFlag]`** — Power Query auto-resolves the duplicate alias to `ItemFlag2`; this is fragile and undocumented |
| `Transaction Type` (computed) | `CASE: Qty>0 → 'Incoming'; Qty<0 → 'Outbound'; else → 'Incoming'` | Zero-qty transactions mapped to 'Incoming' — silent edge case |
| `TransactionType` | From EDW source column `ITW.TransactionType` | EDW-native type classification; separate from the computed `Transaction Type` column — two columns with nearly identical names |
| `Absolute Qty` | `ABS(ITW.Qty)` | Computed in SQL; always ≥ 0 |

**`z_ProductDetails` (local derived columns unique to this model):**

| Column | Logic | Notes |
|---|---|---|
| `Item Type` | `LOOKUPVALUE('Inventory Transaction History'[ItemFlag2], [Item SKU], z_ProductDetails[Item SKU])` | **Reverse lookup** — dimension table looks up a value from a fact table. Performance risk: scans transaction history for every product row. Also returns the first-found `ItemFlag2` for that item regardless of warehouse or week — if an item appears with different flags across warehouses, result is non-deterministic. |
| `Storage Type` | `SWITCH: STATIONARY UPH/MOTION UPH → 'UPH'; OUTDOOR + Cubes>31 → 'UPH'; else → 'CSG'` | **Magic number: `31` cubic feet** — threshold for OUTDOOR items classified as UPH vs CSG. Undocumented. |
| `Storage Type L2` | `SWITCH: BEDDING → 'BED'; CSG → 'CASE'; else passthrough Storage Type` | Adds a Bedding-specific sub-type; `Storage Type` 'CSG' becomes 'CASE' at L2 |
| `RH Item Flag` | `SWITCH Item Class Code: ZJRI/ZERS/ZJIK/ZJRF/ZERV/ZJLK/ZERF → 'RH'; else → 'AFI'` | 7 hardcoded RH item class codes — no documentation of why these specific codes |

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `Item Balance` | `Inventory_Enh_History.ItemBalance` joined to `MasterData_ItemMaster_AFI.ITMEXT` and `Enterprise_DW.DimDate` | Weekly on-hand snapshot; 18-month rolling window; **no CommandTimeout set** (uses default); filters by freight class (`FRTNAT BETWEEN 15900–15999`) OR 27 item class codes |
| Same EDW | `Inventory Transaction History` | `Inventory_Enh.InventoryTransactionsWeeklySummary` joined to `Enterprise_DW.DimDate` and `SupplyChain_DW.DimCurrentProductDetails` | Weekly aggregated transactions; 18-month rolling; 6 transaction codes; explicit warehouse allowlist (20 warehouses); **no CommandTimeout set** |

### Power BI Dataflows (semi-governed)

| Dataflow | Tables | Notes |
|---|---|---|
| `a47e4573` workspace / `346f2aa1` dataflow | `z_ProductDetails`, `z_WarehouseMaster`, `z_FiscalCal` | Same shared conformed dimension layer as all other SC models. Note: `z_ProductDetails` in this model does **not** rename `Item Ext Series Number` to `Planning Series` (unlike accuracy models) — raw column name used. |

**No SharePoint / Excel / ungoverned sources** — this is the only report in the family with a fully EDW + dataflow sourcing model.

---

## 5. Grain & Snapshot Strategy

**Primary grain:**
- `Item Balance`: Item SKU × Warehouse × Fiscal Week — weekly ending-balance snapshot
- `Inventory Transaction History`: Item SKU × Warehouse × Fiscal Week × Transaction Code — weekly aggregated movements

**Snapshot strategy:** Both tables are **rolling 18-month windows** (`FiscalMonthIndicator BETWEEN -18 AND 0`), including the current period. This is operationally appropriate — users need recent history for audit and reconciliation, not trend analytics requiring years of history.

The `Item Balance` table is a **true snapshot** (weekly point-in-time balance). The `Inventory Transaction History` is a **flow** table (accumulated movements per week). These are two fundamentally different things — balance stock vs. movement flows — that share a common grain key (Item × WH × Week). Users must be careful not to sum the balance across weeks (double-counting) while summing transactions is valid.

**Latest-vs-historical:** Both modes are used:
- On-hand balance: users typically want the latest week only (current stock level)
- Transaction history: users want a range of weeks to audit movements

No DAX measure enforces "latest week only" for `On Hand Qty` — if a user removes the week filter, they will sum all 78+ weeks of on-hand balances, producing a meaningless inflated number.

---

## 6. Dimensions Used

| Dimension | Source | Local re-derivations / drift risks |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow → `CurrentProductDetails`) | Four locally derived columns unique to this model: `Item Type` (LOOKUPVALUE from fact), `Storage Type` (Collective Class mapping), `Storage Type L2` (sub-type), `RH Item Flag` (class code mapping). None of these appear in the shared dataflow — they are model-specific. `Item Type` specifically is problematic (see §9). |
| **Date / Fiscal Calendar** | `z_FiscalCal` (dataflow) | 8 local date tables auto-generated for `z_FiscalCal` date columns (`Fiscal Week Start`, `Fiscal Week End`, `Fiscal Month Start`, etc.) — more auto-date tables than any other model in this family. The relationship between `Item Balance[Week Ending]` and `z_FiscalCal[Transaction Date]` is the primary date filter path. |
| **Warehouse** | `z_WarehouseMaster` (dataflow) | Both fact tables relate to `z_WarehouseMaster[Warehouse]`. However, warehouse filtering in the SQL differs between the two tables (see §10) — the warehouse dimension does not enforce a consistent scope. |

---

## 7. Duplication / Consolidation Signals

1. **27-item-class-code list repeated 3× in `Inventory Transaction History` SQL:**  
   The same list (`MATT`, `UESW`, `USKE`, ..., `ZXMK`) appears in three separate CASE statements within one query. Any class code change must be updated in all three places simultaneously or the ItemFlag, ItemFlag2, and WHERE clause will diverge. This list should be a single CTE or a table-valued parameter.

2. **Same 27-item-class-code list also in `Item Balance` SQL:**  
   Fourth copy of the same list, this time in a separate table. Four independent copies total across the model.

3. **`Receipts in to WH` duplicates `Purchase Order` + `Manufacturing Receipt` by different filter field:**  
   Three measures measuring receipt quantities — one by description string, two by code. Should be one measure family with a shared source filter.

4. **`TransactionType` (EDW source) vs `Transaction Type` (computed CASE):**  
   Two columns with near-identical names, different sources, different values. The computed one (`Transaction Type`) is derived from Qty sign; the source one (`TransactionType`) comes from the EDW. A user slicing by `Transaction Type` vs `TransactionType` will see different results — no labelling distinguishes them.

5. **`ItemFlag` (first) vs `ItemFlag2` (second) — SQL column name collision:**  
   Two columns both aliased as `[ItemFlag]` in the SQL SELECT. Power Query disambiguates by appending `2` to the second. This is an accidental naming convention created by a SQL bug, not a deliberate design. The column `ItemFlag2` is used in `z_ProductDetails[Item Type]` via LOOKUPVALUE, but its existence depends on Power Query's behaviour when handling duplicate column names — a fragile dependency.

6. **`Storage Type` and `Storage Type L2` locally derived here vs not present in other models:**  
   These are useful classification columns that other SC models (Demand Review, Forecast Accuracy) do not have. If needed elsewhere they would need to be redefined, risking divergence.

---

## 8. Open Questions

1. **What was `itbStdCost` supposed to be?** The `InventoryDollars` calculated column references a column that never existed in the SQL. Was a standard cost field planned but never added to the EDW query? Or was this copied from a different model that had a different source table with that column? Is anyone expecting to see inventory at standard cost?

2. **Is `InventoryDollars` actually used in any report visual?** It's defined as a column, but since it's always BLANK, any visual using it would show nothing. Has anyone noticed?

3. **Why does `Item Balance` use an EXCLUSION warehouse list (39 excluded) while `Inventory Transaction History` uses an INCLUSION list (20 included)?** These two strategies are hard to keep in sync. Were they intentionally designed to cover different warehouse populations, or is this an unintentional discrepancy?

4. **What is transaction code `IP`?** It is included in the `WHERE TransactionCode IN (...)` filter but no DAX measure references it. Is it intentionally loaded for raw drill-through access in the report (user can see IP transactions in a table visual without a measure), or is it forgotten dead weight?

5. **What is `FRTNAT BETWEEN 15900 AND 15999` in `Item Balance`?** This is a freight class range filter on `MasterData_ItemMaster_AFI.ITMEXT` joining to Item Balance. The range 15900–15999 is undocumented — presumably a category of items that qualify for the balance snapshot alongside the 27 item class codes. What products does this range cover?

6. **Is `Item Type` (LOOKUPVALUE from transaction fact) producing correct results?** If an item appears with `ItemFlag2 = 'FG'` in one warehouse and `ItemFlag2 = 'KIT'` in another, the LOOKUPVALUE returns the first match found — non-deterministic. Has this been validated?

7. **No measure for current-week-only filter:** Users can accidentally sum `On Hand Qty` across all 78+ weeks and get a meaningless number. Is there a report-level filter enforcing the current week, or must users know to apply it manually?

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `FRTNAT BETWEEN 15900 AND 15999` | `Item Balance` SQL | Selects items with freight class codes in this range from `ITMEXT` for inclusion in the balance snapshot | **No** — meaning of this range unknown from the model; presumably an internal freight classification for a specific product type |
| `31` cubic feet | `Storage Type` calc column | OUTDOOR items with Cubes > 31 are classified 'UPH' (upholstery) instead of 'CSG' (casegoods) | **No** — threshold appears to distinguish large outdoor items (sofas, sectionals) from smaller outdoor pieces; no documentation |
| 7 RH item class codes (`ZJRI`, `ZERS`, `ZJIK`, `ZJRF`, `ZERV`, `ZJLK`, `ZERF`) | `RH Item Flag` calc column | Marks these items as 'RH' (Restoration Hardware channel?) vs 'AFI' | **No** — class codes are raw EDW codes; no business context provided in the model |
| `FiscalMonthIndicator BETWEEN -18 AND 0` | Both fact table SQL queries | 18-month rolling window + current month | **No comment** — why 18 months? Most SC models use 12 months. This is the only model with an 18-month lookback. |
| `RIGHT(TRIM([ITW].[ItemSKU]),2) = 'UN'` | `ItemFlag2` CASE in SQL | Items with part-class codes ending in 'UN' suffix → classified as 'KIT' | **No** — 'UN' = "unit" suffix convention for kit items; not documented in model |
| Transaction code whitelist: `SA, RP, IW, RW, RM, IP` | `Inventory Transaction History` WHERE clause | Only 6 transaction types loaded | **No comment** — `IP` loaded but no measure uses it; `SA`/`RP`/`IW`/`RW`/`RM` all have measures |
| Warehouse inclusion list (20 WHs): `1,12,15,151,16,17,19,20,28,3,335,42,49,5,50,ECR,70,101,60` | `Inventory Transaction History` WHERE | Physical warehouse scope for transactions | **No** — list is hardcoded; warehouse `20` appears twice in the list (not causing harm but indicates copy-paste error) |

**`Net Inv Change` sign mechanics — potential logic error:**  
```
Net Inv Change = [Issuing Transfer] + [Receipts in to WH] + [Receiving Transfer] - [Sales Shipments]
```
- `Receipts in to WH` — positive (inbound)
- `Receiving Transfer` — positive (inbound)  
- `Issuing Transfer` — **negative in source** (outbound transaction Qty is negative); adding a negative number is mathematically correct but semantically confusing
- `Sales Shipments` — uses **Absolute Qty** (always positive), then subtracts; correct

Result: `Net Inv Change` should be positive when more stock arrives than leaves — this is mathematically consistent as written. However, if anyone ever changes `Sales Shipments` to use `Transaction Qty` (which for sales is negative), the subtraction would double-count. The mixed use of `Absolute Qty` for sales vs. signed `Transaction Qty` for everything else is undocumented and fragile.

**Dollar value — `InvFob$` only works; `InventoryDollars` is broken:**  
`InvFob$ = On Hand Qty × FOB Price` — this IS a dollar-value number (inventory at selling price, not cost). It feeds any financial view of on-hand stock. Since standard cost (`itbStdCost`) is missing, there is no cost-based inventory valuation available in this model despite the placeholder column.

---

## 10. Comparability / Consistency Issues

### a. Warehouse scope mismatch between `Item Balance` and `Inventory Transaction History`

| Table | Filter approach | Logic |
|---|---|---|
| `Item Balance` | Excludes 39 named warehouses (blocklist) | Everything NOT in that list is included |
| `Inventory Transaction History` | Includes 20 named warehouses (allowlist) | Only those specific warehouses |

A user comparing on-hand balance to transaction movements for the same item × warehouse may see data in one table but not the other if the warehouse falls in a coverage gap. No DAX measure or visual annotation warns of this. The model's single `z_WarehouseMaster` dimension does not enforce consistent scope.

### b. `TransactionType` (EDW column) vs `Transaction Type` (computed column) — same label, different values

Both columns appear in the model. The EDW column comes from `ITW.TransactionType` — its values depend on EDW coding conventions. The computed column derives direction from Qty sign (`Incoming`/`Outbound`). These will disagree for any transaction where the EDW's `TransactionType` classification doesn't match the sign of Qty. A user filtering by one vs. the other gets different row counts.

### c. `Receipts in to WH` vs `Purchase Order` + `Manufacturing Receipt` — different filter fields

| Measure | Filter field | Risk |
|---|---|---|
| `Receipts in to WH` | `TransactionCodeDesc` (text string) | Breaks silently if EDW renames the description |
| `Purchase Order` | `TransactionCode = "RP"` (code) | Stable unless code is changed |
| `Manufacturing Receipt` | `TransactionCode = "RM"` (code) | Stable unless code is changed |

`Receipts in to WH` should equal `Purchase Order + Manufacturing Receipt` by design, but the two filter paths can diverge. No validation measure exists to confirm they match.

### d. `Item Type` is non-deterministic for multi-warehouse items

`z_ProductDetails[Item Type] = LOOKUPVALUE('Inventory Transaction History'[ItemFlag2], [Item SKU], ...)` returns the first matching row's `ItemFlag2`. If item "ABC123" appears as FG in warehouse 1 and as KIT in warehouse 12 (for example, if it's sold both as a complete unit and as a kit component), the `Item Type` column will return whichever warehouse's row the engine finds first — not necessarily the "main" type. There is no grouping, deduplication, or priority logic.

### e. `On Hand Cubes` uses dataflow `Cubes` column; `Inventory Transaction History` has no cube-based measure

On-hand inventory has both unit and cube measures. Transaction movements only have unit measures. A user cannot compute "how many cubes of receipts arrived this week" — the cube dimension is only on the balance side.

---

## Closing — Interview Seeds

1. **"The `InventoryDollars` column — the one that shows on-hand inventory at standard cost — always shows zero or blank. Were you expecting to see dollar values there, and do you know that the standard cost field was never connected to the data?"**  
   *(Confirms whether a broken column is actively expected to work and whether any reports or analyses depend on it.)*

2. **"When you're looking at the on-hand balance for an item across multiple weeks, are you always comparing the same week's snapshot to a transaction total — or do you sometimes sum the balance over multiple weeks? Because summing the balance across weeks would inflate the number significantly."**  
   *(Surfaces whether users understand the stock vs. flow distinction and whether incorrect aggregation is happening in practice.)*

3. **"The transaction history only covers 20 specific warehouses by name, but the on-hand balance covers a broader set. Has there been a case where you saw an on-hand balance for an item at a warehouse but couldn't find the corresponding receipt transaction — and if so, was the warehouse outside the 20 in scope?"**  
   *(Validates whether the warehouse scope mismatch is causing confusion in practice.)*

4. **"Transaction code `IP` is included in the data pull but doesn't appear in any calculated total — it would only show up if someone drills into the raw transaction rows. What does `IP` represent, and was it meant to have its own measure or is it there purely for reference?"**  
   *(Determines whether `IP` is an intentional raw-data inclusion or forgotten scope creep, and whether a measure is expected.)*
