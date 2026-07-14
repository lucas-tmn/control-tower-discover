# When to Disco v2 — Model Analysis
**Workspace:** SCP Team  
**Semantic Model ID:** `fe13baa6-7a0d-4fb3-8ba4-9d98e029efd8`  
**Report ID:** `cd6307bc-0322-4069-855d-2b06247a13fc`  
**Analysis Date:** 2026-07-08  
**Model Size:** 12 tables (1 fact + 4 dim + local date tables); **12 DAX measures** (all in `_Measures`); Compatibility Level 1567

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> For items that are discontinuation candidates (Future Status = F, P, or similar), how many months of supply remain — and should we send the disco notice now or wait?

**This is an operational worklist report, not a trend/analytics report.** It answers a single, time-sensitive question for each item planner:
> *"Given today's on-hand inventory, in-transit supply, firm production, and current customer orders — how many months of demand can this item cover, and does that exceed the threshold to hold off a discontinuation notice?"*

**Primary chain link served:** **Inventory** (current coverage position) + **Supply** (POs in transit, firm production) + **Demand** (customer allocated orders, 3-month average demand rate)

Secondary link: **Operational lifecycle decision** — specifically the "when to send discontinuation template" workflow, which is a documented recurring business process in this workspace (see "When to send disco template" report also in SCP Team).

**Not served:** Forecast, On-time delivery, receipts trend, historical accuracy.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Send or hold discontinuation notice** to customers for a specific item — is MOS < threshold so customers need to be notified now? | Life Cycle Planner / FC Planner | Weekly (triggered by `Check F Status = 1`) | **Operational** — handle goods: initiate disco communication |
| **Prioritize which items to disco first** — rank items by `Months of Supply` (lowest = most urgent) | Life Cycle Planner | Weekly | **Operational** — handle goods |
| **Review combined AFI + Ashton (335) MOS** (`MOS ALL`) — items may be viable at AFI warehouses but out of stock at Ashton, or vice versa | Supply Planner / Life Cycle Planner | Weekly | **Operational** — transfer vs. disco decision |
| **Identify items with HoldBuy + Future F status + MOS < 6** — the `Check F Status` flag surfaces highest-urgency items automatically | Life Cycle Planner | Weekly | **Operational** — escalate or act immediately |
| **Filter by planner** using `Select Planner Type` slicer (Primary vs. Secondary planner) — each planner sees their own item worklist | Individual FC Planner | Weekly | **Operational** — personal worklist management |

> **No Financial-Justification decisions.** No dollar-value calculation exists in this model. No Performance/Governance layer (no trend, no benchmarking against targets). Purely operational triage.

---

## 3. Key Metrics / Measures

All 12 measures reside in `_Measures`. **This is the smallest model in the workspace family** — most "calculations" are pre-aggregated in the SQL query itself and imported as columns.

| Measure | Business meaning | Grain | Source / Logic | Flag |
|---|---|---|---|---|
| `On-Hand Qty` | Current on-hand inventory at AFI domestic warehouses | Item (all domestic WHs summed in SQL) | `SUM('When to Disco'[On-Hand Qty])` | ⚠️ pre-aggregated in SQL across specific WH codes — see §4 |
| `In Transit & On Order` | Sum of in-transit POs + on-order POs + firm production + 335 transfer pending | Item | `SUM('When to Disco'[In-Transit & On-Order])` | ⚠️ compound field — see §9 |
| `Balance OH Minus Customer Orders` | Net AFI inventory position after removing allocated customer orders | Item | `SUM([Balance Minus Customer Orders])` = `(OH + InTransit + OnOrder + FirmProd + 335Transfer) − CustomerAllocatedOrders` | |
| `Balance Minus Customer Orders 335` | Net Ashton (WH 335) position after removing 335 customer orders | Item | `SUM([Balance Minus Customer Orders 335])` = `(OH335 + InTransit335 + OnOrder335 − 335Transfer) − CustomerAllocatedOrders335` | |
| `Balance on Hand + In Transit & On Order` | Gross total inventory (no netting of customer orders) | Item | `SUM([On-Hand + In-Transit & On-Order])` | |
| `Customer Allocated Orders` | Open customer orders allocated against AFI domestic inventory | Item | `SUM([Customer Allocated Orders])` — excludes WH 55, CNW, 335, C, AF, IOR; `InventoryAllocatedFlag = 2` only | ⚠️ see §9 |
| `3 MO Avg` | 3-month average monthly demand at AFI domestic warehouses | Item | `SUM('When To Disco'[3 MO Avg])` — pre-calculated in SQL as `SUM(OrderQty) / 3` over `FiscalMonthIndicator BETWEEN -3 AND -1` | ⚠️ see §9 |
| `3 MO Avg ASH` | 3-month average monthly demand at Ashton (WH 335) | Item | `AVERAGE('When to Disco'[3 MO Avg_335])` — **uses AVERAGE not SUM** | ⚠️ **SUM vs AVERAGE inconsistency** — see §7 |
| `Months of Supply` | How many months of AFI demand the net AFI inventory covers | Item | `[Balance OH Minus Customer Orders] / [3 MO Avg]` | ⚠️ see §9 |
| `Months of Supply ASH` | Months of Ashton demand the net Ashton inventory covers | Item | `[Balance Minus Customer Orders 335] / [3 MO Avg ASH]` | |
| `All Inventory Minus Alloc Orders` | Combined net position across AFI + Ashton | Item | `[Balance OH Minus Customer Orders] + [Balance Minus Customer Orders 335]` | |
| `MOS ALL` | Months of supply using combined inventory and combined demand rate | Item | `DIVIDE([All Inventory Minus Alloc Orders], ([3 MO Avg ASH] + [3 MO Avg]))` | ⚠️ denominator adds two AVERAGE/SUM-computed values — see §7 |

**Calculated column in fact table:**

| Column | Logic | Flag |
|---|---|---|
| `Check F Status` | `IF(FutureStatus="F" AND MOS<6 AND HBStatus="HB", 1, 0)` | ⚠️ three-way hardcoded threshold rule — see §9 |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| `z_ProductDetails` | PowerBI Dataflow `346f2aa1...` workspace `a47e4573...` → entity `CurrentProductDetails` | Governed Dataflow | Low |
| `z_FiscalCal` | Same dataflow → `AshleyFiscalCalendarV2` | Governed Dataflow | Low — ⚠️ but **not related to any fact table** (see §7) |
| `z_WarehouseMaster` | Same dataflow → `WarehouseMaster` | Governed Dataflow | Low — ⚠️ **not related to any fact table** |
| `z_VendorMaster` | Same dataflow → `VendorMaster` | Governed Dataflow | Low — ⚠️ **not related to any fact table** |
| `z_CustomerMaster_AFI` | Same dataflow → `CustomerMaster_AFI` | Governed Dataflow | Low — ⚠️ **not related to any fact table** |
| **`When to Disco`** | **`ashley-edw.database.windows.net / ashley_edw`** — single large SQL join across 10+ EDW tables: | Direct Azure SQL EDW | Medium — complex multi-join, latest-only |
| → On-Hand | `MasterData_ItemMaster_AFI.ITEMBL` (WHs: 1,A,5,B,15,L,17,N,ECR,E,28,T,42,F,19,S,49,O) | Direct EDW | |
| → In-Transit / On-Order (AFI) | `Inventory_DW.FactPurchasingPurchaseOrders` (WHs: 1,A,5,B,15,L,17,N,ECR,E,28,T,42,F,19,S,49,O) | Direct EDW | |
| → In-Transit / On-Order (335) | Same `FactPurchasingPurchaseOrders` (WHs: 335, G) | Direct EDW | |
| → Future Status / HB Code / Planner | `MasterData_ProductKnowledge.Item_ENV` (env=AFI only) | Direct EDW | |
| → Customer Allocated Orders (AFI) | `QUALITY_DW.FactOpenOrders` — `InventoryAllocatedFlag=2`, excludes 55,CNW,335,C,AF,IOR | Direct EDW | |
| → Customer Allocated Orders (335) | `AFISales_DW.FactOpenOrders` — `InventoryAllocatedFlag=2`, WH=335, excludes `3824800` | Direct EDW | |
| → 335 Transfer | `SupplyChain_Enh.ActualsCustItemWH_AFI` — account `3824800%`, `FiscalMonthIndicator BETWEEN -1 AND 5` | Direct EDW | ⚠️ see §9 |
| → Firm Production | `Wholesale_DemandPlanning_AFI.SupplyPlanDetail` — latest snapshot only (`MAX(dtea)`) | Direct EDW | |
| → 3 MO Avg (AFI) | `SupplyChain_Enh.ActualsCustItemWH_AFI`, `OrigReqWkEnding`, months -3 to -1, excludes 12,16,213,215,335,50,60,70,C,CNW,AF,IOR | Direct EDW | |
| → 3 MO Avg (335) | Same table, WH=335, excludes account `3824800%` | Direct EDW | |
| → Product Attributes | `PowerBI_SupplyChain.CurrentProductDetails` (joined in SQL, not via dataflow) | Direct EDW | ⚠️ **dual sourcing risk** — same product data loaded via dataflow for `z_ProductDetails` AND via SQL for the fact table join |

> **Note:** This model uses `PowerBI_SupplyChain.CurrentProductDetails` directly in the SQL query to get Item Description and Item Ext Series Number — in addition to loading `z_ProductDetails` from the same data via dataflow. If the two sources drift (e.g., a product attribute updated in one but not the other), the model silently shows inconsistent data.

> **No Fabric sources.** All SQL hits `ashley-edw.database.windows.net` (Azure SQL Server).

---

## 5. Grain & Snapshot Strategy

**Primary grain:** **Item SKU** (single row per item, all warehouses pre-aggregated in SQL).

This is a **latest-only, point-in-time snapshot** model:
- On-hand qty: from `ITEMBL` live table — reflects today's balance
- In-transit / on-order: from `FactPurchasingPurchaseOrders` — live open POs only
- Customer orders: from `FactOpenOrders` — live allocated open orders only
- Firm production: latest supply plan snapshot (`MAX(dtea)`)
- 3 MO Avg: trailing 3 fiscal months of order history (FiscalMonthInd -3 to -1)
- 335 Transfer: account `3824800` shipments in months -1 to +5 (past 1 + future 5 months)

**No historical snapshots.** This model cannot answer "how has the MOS for this item changed week-over-week?" It is a **point-in-time triage tool** — every refresh completely replaces prior values.

**Implication for decisions:** Users must act quickly after each refresh, or the numbers are stale. No built-in trend to know if MOS is improving or deteriorating.

---

## 6. Dimensions Used

| Dimension | Table | Connected to fact? | Notes |
|---|---|---|---|
| **Product** | `z_ProductDetails` (93 cols) | ✅ Yes — `When to Disco[Item SKU]` → `z_ProductDetails[Item SKU]` | Conformed; only relationship in the model |
| **Date / Fiscal Calendar** | `z_FiscalCal` (38 cols) | ❌ **No relationship** | Present in model but unused — orphaned dimension |
| **Warehouse** | `z_WarehouseMaster` (11 cols) | ❌ **No relationship** | Present but unused — warehouse aggregation done in SQL |
| **Vendor** | `z_VendorMaster` (11 cols) | ❌ **No relationship** | Present but unused |
| **Customer** | `z_CustomerMaster_AFI` (38 cols) | ❌ **No relationship** | Present but unused — no customer-level breakdown in this model |
| **Planner (slicer)** | `Select Planner Type` (3 cols) | ✅ Referenced via `NAMEOF()` | Calculated table used as slicer: maps to `z_ProductDetails[ItemForecastPlannerID]` or `[Secondary Planner]` |

**Three out of five dimension tables have no relationships to the fact table.** They load data into the model but cannot filter the `When to Disco` table. This is likely copy-paste from a parent template model — the dimensions exist but serve no filtering purpose.

**Locally re-derived attributes (drift risk):**

| Attribute | Location | How derived | Risk |
|---|---|---|---|
| `Check F Status` | `When to Disco` calc column | `FutureStatus="F" AND MOS < 6 AND HBStatus="HB"` | **High** — three business rules hardcoded; see §9 |
| `Month's of Supply` | Pre-calculated in SQL | `(OH + InTransit + OnOrder + FirmProd + 335Transfer − CustOrders) / 3MO Avg` | Medium — pre-calculated in SQL, duplicated as DAX measure `Months of Supply` |
| `WH Group` normalization | **Not present** — warehouse codes hardcoded in SQL `WHERE` clauses | N/A | Medium — 19 domestic WH codes and 2 Ashton codes listed explicitly in SQL; if a new WH is added, it is silently excluded |

---

## 7. Duplication / Consolidation Signals

1. **`3 MO Avg` uses `SUM` in DAX measure; `3 MO Avg ASH` uses `AVERAGE`.**
   - `3 MO Avg` → `CALCULATE(SUM('When To Disco'[3 MO Avg]))`
   - `3 MO Avg ASH` → `CALCULATE(AVERAGE('When to Disco'[3 MO Avg_335]))`
   The SQL pre-aggregates each to a single row per item (`SUM(Order Qty)/3` grouped by Item SKU). At item level both `SUM` and `AVERAGE` return the same single value. However, when sliced by `z_ProductDetails` attributes (e.g., Collective Class), the `SUM` of `3 MO Avg` across items will correctly add all items' averages; `AVERAGE` of `3 MO Avg_335` will average the per-item averages (Simpson's paradox territory). This inconsistency affects `MOS ALL` which combines both in the denominator.

2. **`Month's of Supply` pre-calculated in SQL and re-calculated in DAX.**
   The SQL query computes `[Month's of Supply]` as a column in `When to Disco`. The DAX measure `Months of Supply` then recalculates: `DIVIDE([Balance OH Minus Customer Orders],[3 MO Avg])`. These should agree at item grain, but diverge if the visual aggregates across items (DAX measure sums numerator and denominator separately; SQL column is pre-divided). No documentation flags this dual-calculation.

3. **Three orphaned dimension tables** (`z_FiscalCal`, `z_WarehouseMaster`, `z_CustomerMaster_AFI`, `z_VendorMaster`) load but have no relationships and cannot filter anything. These inflate model size and refresh time with no benefit.

4. **`When to Disco` table name inconsistency:** The table is named `"When to Disco"` but DAX measures reference it as `'When To Disco'` (capital T) and `'When to Disco'` (lowercase t) interchangeably. Power BI handles this case-insensitively, but it signals that the model was built/edited by multiple people without a naming convention.

5. **Two separate `FactOpenOrders` sources for customer orders:**
   - AFI: `QUALITY_DW.FactOpenOrders` (excludes 55,CNW,335,C,AF,IOR)
   - 335: `AFISales_DW.FactOpenOrders` (WH=335 only)
   Different schemas, different DB schemas (`QUALITY_DW` vs `AFISales_DW`). Both represent allocated open orders but from different source systems — no documentation explains why two tables are used vs. one unified source.

6. **`z_ProductDetails` loaded twice:** Once via the governed dataflow (for the `z_ProductDetails` dimension table), and once directly via `PowerBI_SupplyChain.CurrentProductDetails` in the `When to Disco` SQL join (for Item Description, Item Ext Series Number). If these sources refresh at different times, the same item may show different descriptions depending on which field is used in a visual.

---

## 8. Open Questions

1. **What is the "disco notice" process exactly?** The `Check F Status` flag (FutureStatus=F + MOS<6 + HB=HB) identifies items to act on — but what happens next? Is there a standard email template? Does the planner log it somewhere, or take action directly in Logility/ERP? The report "When to send disco template" in the same workspace suggests a defined workflow — but the two reports are not linked in the model.

2. **Are the 4 orphaned dimension tables (`z_FiscalCal`, `z_WarehouseMaster`, `z_CustomerMaster_AFI`, `z_VendorMaster`) intentionally present?** They increase refresh time and model size. Were they included because slicing by customer or warehouse was planned but never implemented? Or are they a copy-paste artifact from a template?

3. **`335 Transfer` window: months -1 to +5.** The SQL includes transfers from account `3824800%` (AFI internal) over the next 5 fiscal months. Why 5 months? Is this the expected lead time for a 335-to-DC transfer to clear? This affects the net inventory position calculation.

4. **`Inventory Allocated Flag = 2` in both open order queries** — what does flag value `2` mean? Is `1` a different allocation type that should also be included or explicitly excluded?

5. **`Current Status NOT IN ('D','I','R','T')` filter in SQL** — items with these status codes are excluded from the worklist entirely. Does the business intend to never show "D" (discontinued) items, or should discontinued items with remaining inventory still appear to manage runout?

6. **`z_FiscalCal` and time intelligence are loaded but unused.** Is there a plan to add trend analysis (e.g., "how long has this item been below 6 MOS?") to this report in a future version? If so, the date table is ready; otherwise it should be removed.

7. **Model compatibility level 1567 — the lowest across all analyzed models.** This is a relatively old compatibility level (Power BI Desktop ~2019–2020 era). Other models in the workspace are at 1600. Is this model on an older refresh/maintenance cadence?

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`MOS < 6`** in `Check F Status` | `When to Disco` calc column | Items with < 6 months of supply get flagged as urgent to disco | **No** — 6 months is the disco-notice threshold, undocumented in the model |
| **`HB Status = "HB"`** in `Check F Status` | Same | Only items on Hold Buy qualify for urgent disco flag; items not on HB are excluded | **No** — business logic: if not on HB, presumably supply can still be adjusted |
| **`Future Status = "F"`** in `Check F Status` | Same | Only items with hard-future-drop status trigger the flag; "P" (planned drop) does not | **No** — implies there is a distinction between F (confirmed drop) and P (planned, not yet confirmed) |
| **`/ 3`** in 3 MO Avg SQL | SQL query | Sum of 3 months of orders ÷ 3 = monthly average demand rate | **Partially** — the column name says "3 MO Avg" which implies the /3; the SQL comment does not explain the choice of 3 months |
| **`FiscalMonthIndicator BETWEEN -3 AND -1`** | SQL (3 MO Avg calculation) | Uses last 3 full fiscal months; excludes current month (indicator=0) | **No** — 3 months is presumably enough to smooth seasonality but short enough to be responsive; undocumented |
| **`FiscalMonthIndicator BETWEEN -1 AND 5`** | SQL (335 Transfer) | Transfer from account 3824800 in last 1 + next 5 fiscal months included in supply | **No** — 5 months forward = presumably the lead time for 335 transfers to reach customers; undocumented |
| **`InventoryAllocatedFlag = 2`** | SQL (Customer Allocated Orders) | Only inventory-allocated open orders counted; other allocation types excluded | **No** — flag value 2 meaning not documented in model |
| **Warehouse inclusion list (19 codes)** | SQL `WHERE HOUSE IN (...)` | `1,A,5,B,15,L,17,N,ECR,E,28,T,42,F,19,S,49,O` — domestic AFI warehouses | **No** — hardcoded; if a new warehouse is added to the network, it is silently excluded from on-hand and MOS |
| **Warehouse exclusion from 3 MO Avg: `12,16,213,215,335,50,60,70,C,CNW,AF,IOR`** | SQL | These warehouses excluded from demand averaging | **No** — mix of return warehouses (213,215), Ashton (335), wholesale (C,CNW), and others; logic not explained |
| **Account `3824800` exclusions** | SQL (Customer Allocated Orders 335, 335 Transfer) | This account number appears twice — excluded from customer orders at 335, but **included** as the source of 335 Transfer supply | **No** — `3824800` appears to be AFI's internal transfer account; its orders are treated as supply (transfer), not customer demand |
| **`MAX(dtea)` latest supply plan** | SQL (Firm Production) | Only the most recent supply plan snapshot used for firm production | Partially — common pattern; not documented |

**Dollar-value impact:** None. This model contains no dollar calculations — all quantities are in units. No financial-justification logic present.

---

## 10. Comparability / Consistency

1. **`3 MO Avg` (SUM in DAX) vs. `3 MO Avg ASH` (AVERAGE in DAX) at aggregated levels.** At the single-item grain, both return correct per-item values. When a visual rolls up to Collective Class or Planner level, `SUM(3 MO Avg)` correctly totals all items' monthly demand rates, while `AVERAGE(3 MO Avg_335)` returns the mean of item-level averages — biasing toward small items. `MOS ALL = All Inventory / ([3 MO Avg ASH] + [3 MO Avg])` combines these inconsistently aggregated denominators. MOS ALL at any level above single-item is not methodologically valid.

2. **`Month's of Supply` (SQL pre-calculated column) vs. `Months of Supply` (DAX measure) diverge at aggregated levels.** The SQL column is already divided at the row level; summing it across items gives nonsense. The DAX measure divides the summed numerator by the summed denominator (correct for aggregation). If a visual uses the SQL column instead of the DAX measure, aggregated MOS will be wrong. No visual-level audit was possible from model alone.

3. **Two different `FactOpenOrders` tables (`QUALITY_DW` vs. `AFISales_DW`) for the same metric (customer allocated orders)** at different warehouses. If the same open order appears in both tables (possible for orders that are partially allocated across AFI and 335), it could be double-counted in `All Inventory Minus Alloc Orders`. No deduplication logic is visible in the SQL.

4. **`z_FiscalCal` present but unrelated to fact table** — any date-based filtering applied by a user (via slicers using z_FiscalCal) would silently not filter `When to Disco` data. Users may expect time filters to work and not realize they have no effect on this model.

5. **`Current Status NOT IN ('D','I','R','T')` filter (SQL)** vs. `Future Status IS NOT NULL` (SQL) — two different status filters apply. Items passing the Current Status filter but with blank Future Status are excluded. This means items with active current status and no planned future status (i.e., stable current items) are also excluded from the worklist — potentially correct (they're not disco candidates) but not documented.

---

## Closing — Interview Seeds

> Direct questions for a follow-up interview with the actual business user.

1. **"When `Check F Status` flags an item as 1, what is the next physical step — do you send a template notice immediately, or does it go through a review before the customer is contacted? And is that process tracked anywhere outside Power BI?"**
   *(Targets: trigger-to-action gap; whether the flag drives automatic action or requires human judgment; external tool handoff.)*

2. **"The MOS threshold is hardcoded at 6 months. Has that number ever changed — and if the business wanted to tighten it to 4 months, do you know you'd need IT to update the report rather than being able to change it yourself?"**
   *(Targets: awareness that the threshold is hardcoded in DAX, not a configurable parameter; governance and change-management risk.)*

3. **"When you look at MOS ALL for a series or collective class (not a single item), do you trust that number? Or do you always drill down to individual items before making a decision?"**
   *(Targets: whether the SUM vs. AVERAGE aggregation inconsistency in `MOS ALL` has been noticed; user behavior around aggregated vs. item-level reads.)*

4. **"The model shows a snapshot of inventory right now. Has there ever been a situation where an item looked fine on Monday, you didn't send the disco notice, and by Friday it had dropped below threshold — and you'd missed the window? How do you handle the timing between refreshes?"**
   *(Targets: operational pain point from point-in-time-only data; whether users want trend/history; refresh frequency adequacy for the decision cycle.)*

---

*Analysis based on BIM definition extracted 2026-07-08. No bundle indexes were modified.*
