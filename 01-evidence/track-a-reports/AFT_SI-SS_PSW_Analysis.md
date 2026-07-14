# AFT_SI-SS_PSW — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | SCP Global Team (`fb03479c-f98b-414f-bf8f-ab2dfa744ff4`) |
| **Report Name** | AFT_SI-SS_PSW |
| **Backing Model** | AFT_SI-SS_PSW (`766ae87c-0e6a-4c89-9288-b384fca6d7cf`) |
| **Model Size** | 17 tables (11 user + 6 helper), 12 measures, 8 relationships, 0 RLS roles |
| **Analyzed** | 2026-07-07 |

> **Report name key:** AFT = Available For Trade, SI = Shippable Inventory, SS = Safety Stock, PSW = Planned Supply Weeks (or PSW source table). The report tracks whether planned supply covers safety stock requirements at each warehouse over a forward horizon of up to 21 weeks.

---

## §1 — Supply-chain question & chain link

**Question:** For each item-warehouse combination, is the planned supply pipeline (orders in transit + firm production + planned receipts) sufficient to cover the safety stock target over the coming weeks — and where are the gaps that require expediting, transfer, or re-planning?

| Link | How served |
|---|---|
| **Supply** (primary) | Tracks ORDER DUE (by receipt date) and ORDER ETD (by estimated time of departure + lead time) for each DATA TYPE: SAFETY STK (what the safety stock target requires), SHIPPABLE INV (what is physically available/received), SI-SS (gap = Shippable Inventory minus Safety Stock), plus 10+ other supply types (FIRMED, PLANNED, PROD, TFR IN/OUT, etc.) |
| **Inventory** | Shippable Inventory quantity vs Safety Stock target drives the core SS% measure |
| **Receipts** | Combines PO details (open firm orders), supply plan detail (planned receipts), PSW snapshot (firmed + shipped), and vendor pricing/delivery times |

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Which item-warehouses are below safety stock (SS% < target)? Trigger expedite POs or transfers | Planner | Weekly | **Operational** |
| Is a supplier's lead time causing chronic SS gaps? Re-evaluate delivery promise or order earlier | Planner / Analyst | Weekly | **Operational** |
| Is inventory building too far above safety stock (SS% > target)? Delay orders, free up working capital | Planner | Weekly | **Operational** |
| Which items have SI-SS negative (SI below SS) with no planned POs? Escalate to production/ procurement | Planner / Buyer | Weekly | **Operational** |
| Where are container utilization issues? (order qty / 2350) Tie-in to container load efficiency | Supply Planner | Weekly | **Operational** |
| Is my vendor split and lead time data correct in the system? | Planner / Data Steward | Monthly | **Performance / Governance** |
| Which warehous- es × vendor combinations have critical color-coded gaps? Weekly WBR review | Manager / WBR-Leadership | Weekly | **Performance / Governance** |

---

## §3 — Key metrics / measures

**12 measures total** — 8 in `PO` table, 1 in `LastRefresh_Local`, 3 in `Demand Fulfillment`.

### A. Core SS% measures (Table: PO)

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| **SS% DUE** | Ratio of Shippable Inventory to Safety Stock target, by receipt due date | Item × WH × Due Date × Data Type | `CALCULATE(SUM(ORDER DUE), DATA TYPE = "SHIPPABLE INV") / CALCULATE(SUM(ORDER DUE), DATA TYPE = "SAFETY STK")` |
| **SS% ETD** | Same ratio but by ETD (departure + lead time adjusted) | Item × WH × ETD × Data Type | `CALCULATE(SUM(ORDER ETD), DATA TYPE = "SHIPPABLE INV") / CALCULATE(SUM(ORDER ETD), DATA TYPE = "SAFETY STK")` |
| **SS% Test** | **Duplicate of SS% DUE** — same expression, different format string (`0%` vs `0.0%`) | Same | Same as SS% DUE |
| **Due Color** | Binary RED/GREEN indicator relative to a threshold selected from the `Percent` slicer | Item × WH × Due Date | `IF(SS% DUE > SELECTEDVALUE('Percent'[Percentage]), "RED", "GREEN")` |

> ⚠️ **Suspicious — `SS% Test` is a dead duplicate of `SS% DUE`.** Same calculation, format string is the only difference (`0%` vs `0.0%`). Likely an abandoned test measure. Increases model noise.

> ⚠️ **Suspicious — `Due Color` logic:** RED when `SS% DUE > threshold`, GREEN when `≤ threshold`. Semantically, RED should indicate *below* safety stock (SS% < target), not above. If the threshold is the minimum acceptable SS%, SS% above target should be GREEN. This may be intentional (RED = "over target = excess = bad") but the inverse convention is unusual.

### B. Background color measures (Table: PO — 4 measures)

| Measure | Logic |
|---|---|
| **Background color DUE** | 11-category ordinal color mapping for ORDER DUE (COLOR DUE = 1→11) |
| **Background color DUE WHSE** | Same mapping for COLOR DUE WHSE |
| **Background color ETD** | Same mapping for COLOR ETD |
| **Background color ETD WHSE** | Same mapping for COLOR ETD WHSE |

All four are identical `IF(MAX([COLOR n]) = k, hexColor, ...)` cascading 12-level IF statements mapping values 1–11 to hardcoded hex colors (#003366, #B800F6, #F60000, #F69C00, #78C0E0, #004010, #5A90A8, #FD00CA, #5B5959). **Values 8 and 9 share the same color (#FD00CA). Values 10 and 11 share the same color (#5B5959).** No documentation of what each color represents.

> ⚠️ **Suspicious — Colors are hardcoded hex, not theme-referenced.** If the report is rebranded or dark mode is introduced, all four measures must be manually updated. Values 8=9 and 10=11 collapse — suggestion the ordinal could be simplified from 11 to 9 categories.

### C. Demand Fulfillment measures (Table: Demand Fulfillment — 3 measures)

| Measure | Meaning | Logic |
|---|---|---|
| **Demand Fulfill CO** | % of customer orders that can be supplied | `MIN(SUM(sold_orders_can_supply)/SUM(runningsoldorders), 1)` — capped at 100% |
| **Demand Fulfill SI** | % of demand covered by Shippable Inventory | `SUM(runningDF)/SUM(runningdemand)` |
| **Demand Fulfill SS** | % of safety stock covered | `(SUM(ss_can_supply) + SUM(runningdemand)) / (SUM(runningdemand) + SUM(spdSafetyStock))` |

> ⚠️ **Suspicious — `Demand Fulfill SS` formula:** The numerator adds `ss_can_supply + runningdemand`, the denominator adds `runningdemand + spdSafetyStock`. This is not a standard SS fulfillment ratio. If `runningdemand` is always equal in both places, the formula simplifies to `ss_can_supply / spdSafetyStock` only when `runningdemand` cancels out — but it doesn't cancel algebraically in DAX (it's additive). The formula appears to be an attempt to handle a divide-by-zero case that introduces bias when `runningdemand ≠ spdSafetyStock`. This warrants a logic review.

### D. Refresh metadata (Table: LastRefresh_Local)

**Last Refreshed (Local):** `FORMAT(LASTDATE(LastRefresh_Local[LastRefresh]), "MM/dd/YYYY hh:mm:ss AM/PM")`

**Calculated column `Column 4`:** Uses hardcoded `-3 hours` offset.
**Calculated column `Last Refresh new`:** Uses hardcoded `-5 hours` offset.

> ⚠️ **Suspicious — Two different hour offsets in the same table:** `Column 4` uses CST via `-3` (which suggests EDT, not CST), while `Last Refresh new` uses `-5` (CST/EST depending on DST). Contradictory offsets. If both are shown in the report they will disagree.

---

## §4 — Data sources & lineage

| Source | Type | Flag |
|---|---|---|
| **Enterprise_DW.DimDate** | Azure SQL (`ashley-edw.database.windows.net` / `ASHLEY_EDW`) | ✅ Governed |
| **SupplyChain_Enh.PSWWeeklyExtractSnapshot** | Azure SQL | ✅ Governed |
| **Wholesale_ProductSourcing_AFI.PoDetail / PoMaster** | Azure SQL | ✅ Governed |
| **Wholesale_ProductSourcing_WVF.PoDetail / PoMaster** | Azure SQL | ✅ Governed (WVF warehouse group) |
| **Wholesale_DemandPlanning_AFI.PlanDetailTimeline** | Azure SQL | ✅ Governed |
| **Wholesale_DemandPlanning_AFI.SupplyPlanDetail** | Azure SQL | ✅ Governed |
| **Wholesale_DemandPlanning_AFI.SCP_FCST_ROOT** | Azure SQL | ✅ Governed |
| **Wholesale_Vendors_AFI.VendorPricing** | Azure SQL | ✅ Governed |
| **Wholesale_Vendors_WNK.VendorPricing** | Azure SQL | ✅ Governed |
| **Wholesale_ProductSourcing_AFI.DeliveryTimes** | Azure SQL | ✅ Governed |
| **Inventory_DW.DimItemMaster** | Azure SQL | ✅ Governed |
| **PowerBI_SupplyChain.AFIItemABCCurrentSnapshot** | Azure SQL | ✅ Governed |
| **SupplyChain_Enh.PlanDetailTimelineSnapshot** | Azure SQL | ✅ Governed (used by Old Snap / Past Week) |
| **PowerBI_SupplyChain.SupplyPlanDetailCurrentDay** | Azure SQL | ✅ Governed (Demand Fulfillment) |
| **Manufacturing_MasterData.FlatBOM** (AFI/WNK/MIL × 6) | Azure SQL | ✅ Governed |
| **VENDOR LIST AFT & 232.xlsx** (SharePoint) | **SharePoint Excel** | ⚠️ **Ungoverned** — manual Excel file at `SCPGlobalTeam-Tools/` |
| **Userfields Master File (CC,EVC,ABCXYZ).xlsx** (SharePoint) | **SharePoint Excel** | ⚠️ **Ungoverned** — manual Excel file |
| **Wanek Item DRP Breakdown.xlsx** (SharePoint) | **SharePoint Excel** | ⚠️ **Ungoverned** — manual Excel file |
| **NFM Item Filter.xlsx** (SharePoint) | **SharePoint Excel** | ⚠️ **Ungoverned** — manual Excel file |

**EDW objects summary:** 16+ SQL tables/views across 5+ databases, plus 4 manual SharePoint Excel files.

> ⚠️ **No RLS defined** — all users see all items, warehouses, and vendors. Sensitive data (vendor pricing, margin information) visible to all model users.

### Warehouse codes in use across the model

Different SQL sub-queries have inconsistent warehouse inclusion lists. The four lists do not match each other:

| Source query | Warehouse list | Missing vs main list |
|---|---|---|
| PSWWeeklyExtractSnapshot (PO main) | 1,15,17,201,28,42,5,70,ECR,335,49,19,12,C,CNW,232 | — (reference) |
| PlanDetailTimeline (PO) | 1,15,17,201,28,42,5,70,ECR,335,49,19,12 | Missing: C, CNW, 232 |
| DeliveryTimes (PO) | 1,15,17,201,28,42,5,70,ECR,335,49,19,12 | Missing: C, CNW, 232 |
| EVC,CC SHAREPOINT | 1,101,12,15,151,17,19,20,201,28,3,335,42,49,5,C,ECR | Includes 101,151,3,20; excludes 70,232,CNW |
| DELIVERY TIME table | 1,15,17,28,42,5,70,ECR,335,49,19,12,201 | Missing: C, CNW, 232 |
| Demand Fulfillment | 180-day horizon, warehouse list from SP supply plan (not independently filtered) | Different mechanism |

This means **an item tracked in one part of the model may not have corresponding data in another part for the same warehouse**, producing gaps or incorrect SS% when cross-referenced.

---

## §5 — Grain & snapshot strategy

**Primary grain:** Item × Warehouse × Due Date / ETD Week Ending × Data Type (20+ supply categories: SAFETY STK, SHIPPABLE INV, SI-SS, FIRM PO, TFR IN, TFR OUT, PLANNED PROD, KIT COMPT USAGE, NET FCST, etc.)

**Horizon:** CalendarWeekIndicator −10 to +21 (32 weeks total: 10 weeks backward, 21 forward from current week)

**Snapshot strategy:** Two-tier:
1. **Current (live):** Direct from `PlanDetailTimeline` for real-time SS position
2. **Historical (snapshot):** `Old Snap` and `Past Week` use `PlanDetailTimelineSnapshot` at `@maxdateplan - 7 days` for trend/comparison against prior week

**Delivery time shaping:** ETD = Due Date + (delivery lead time from `DeliveryTimes` table + 7 hardcoded days)

---

## §6 — Dimensions used

| Dimension | Source | Notes |
|---|---|---|
| **Date (Week)** | `Enterprise_DW.DimDate` — two identical tables: `DUE` and `ETD` | CalendarWeekIndicator (−10 to +21). No fiscal calendar attributes used |
| **Product** | `Item Desc` — 5-way join across `DimItemMaster`, `SCP_FCST_ROOT`, `AFIItemABCCurrentSnapshot` | Includes `Hold/Buy` (Usr_04_TEXT), `item_status` / `future_status` (Usr_01/Usr_22), `Derived_FCST_FTR`, `CubicFeet`, `ABC`, `Current Status` |
| **Warehouse** | Embedded string in PO fact + `EVC,CC SHAREPOINT` | **No standalone Warehouse dimension** — only an `EVC,CC SHAREPOINT` table that filters to 17 warehouses. No warehouse name, region, type, or capacity attributes |
| **Vendor** | `Vendor Split` — UNION of AFI+WNK VendorPricing + VENNAM join | Includes VendorPricing split data. Calculated columns enrich with SharePoint personnel data (SCP Analyst, SCP Manager, Asia SCP, GSCP Mentor, etc.) |
| **Customer** | Not present | No customer dimension |
| **Product Class** | `Product Filter` — 6x UNION of FlatBOM | Hardcoded CASE classifications: ZipperCover, RP, UnKits, Pillow, UPH, CG, Bedding, Plastics, Foundation, Panel, RawMaterial, Check |
| **Planner org** | SharePoint VENDOR LIST + `Item Desc` (Fcst_Planner from SCP_FCST_ROOT) | SharePoint list maps vendor numbers to SCP teams. Wanek section parsed from separate Wanek DRP Excel |

### Notable re-derived attributes

| Attribute | Source | Drift risk |
|---|---|---|
| `STATUS` = `item_status & ":" & future_status` | SCP_FCST_ROOT (Usr_01 + Usr_22) | If Logility changes these fields or their delimiter, all status-based filters break silently |
| `max status` = `CALCULATE(MAX(STATUS), ALLEXCEPT(item_number))` | DAX on fact table | Items with multiple warehouse rows inherit the max status across all warehouses — incorrect when status differs by warehouse |
| `FORECAST PLANNER` on Vendor Split = IF(Wanek, Wanek DRP Planner, SCP FCST Planner) | Hybrid: SharePoint + Wanek Excel + Logility | Three sources for one attribute. If Wanek Excel is updated late, FCST Planner is stale |
| `M/B` (Make/Buy) on Vendor Split | Wanek Excel `MBUY CD` | Only populated for Wanek items; blank for all AFI/WVF-sourced items |

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| **`SS% Test` = `SS% DUE`** | Identical DAX expression — abandoned test measure |
| **DUE and ETD tables** | Both query `Enterprise_DW.DimDate` with identical M code and SQL. Only difference: ETD is used for departure-based date, DUE for receipt-based. Could share one date table filtered by context |
| **Current and Past Week** | Identical SQL structure — only difference: Past Week uses `PlanDetailTimelineSnapshot` at `@maxdateplan - 7` instead of live `PlanDetailTimeline`. Collapses to one parameterized query |
| **4 Background Color measures** | Same 12-level IF cascade. Switch only the input column (COLOR DUE / COLOR DUE WHSE / COLOR ETD / COLOR ETD WHSE). Could be a single calculation group |
| **SS% DUE and SS% ETD** | Same SAFETY STK/SHIPPABLE INV ratio on different date dimensions. Same extraction pattern replicated |
| **Warehouse lists (3+ variants)** | Hardcoded IN clauses in 3+ SQL sub-queries within PO alone, plus separate lists in EVC and DELIVERY TIME. One governed reference list would eliminate drifts |
| **Item Desc sourced from 5-way SQL join** with vendor/cross-workspace duplicates | `DimItemMaster` left-joined three times (Inventory_DW, Enterprise_DW, SCP_FCST_ROOT, ABC snapshot). Could consolidate into a governed Product dimension from EDW |
| **Delivery time logic** = `DeliveryTimes.delivery final + 7` | The `+7` days appears in the M query but not in the DeliveryTimes source table. Hardcoded offset should be a column in the source or a parameter |
| **Missing WHSE column in Current/Past Week** | SQL comment `--new.WHSE` shows the warehouse column was intentionally removed. Current.SS% is computed without warehouse grouping, then LOOKUPVALUE'd back to PO. This means an item with multiple warehouses sharing the same ETD week gets the first-matching SS% — data corruption risk |
| **Vendor Split** has 16+ calculated columns populated via LOOKUPVALUE from SharePoint columns — each a separate DAX expression for one attribute. Could collapse into a single EVALUATE pattern or a VIEW in EDW |

---

## §8 — Open questions

1. **What do the 11 COLOR codes (1–11) mean?** The ordinal mapping (1=blue, 2=purple, 3=red, etc.) is undocumented. Likely maps to exception categories (negative SI, no planned POs, container alignment, etc.). Need business user confirmation.

2. **What is the `Percent` table's single value?** The Percent table is Base64-encoded inline data. `Due Color` measures compare SS% against `SELECTEDVALUE('Percent'[Percentage])`. No documentation of what the default percentage threshold is.

3. **Is the Current/Past Week missing WHSE column a bug?** The `--new.WHSE` comment suggests warehouse was intentionally dropped from the PIVOT, but `Change SS%` and `SS% Alert` on Current then LOOKUPVALUE back to PO by ITNBR only (not ITNBR+WHSE). If an item has multiple warehouses, this could match the wrong warehouse's value.

4. **Who uses this report and how often?** No usage metadata in the model. The ~21-week forward horizon + color exception coding suggests weekly WBR by planners.

5. **Are the 4 SharePoint Excel files actively maintained?** Manual Excel files are the highest data-readiness risk in this model. Personnel data (VENDOR LIST), EVC/ABC codes (Userfields Master), Wanek DRP mapping, and NFM filter all depend on someone remembering to update a SharePoint .xlsx.

6. **Is the NFM filter live?** `NFM FILTER` is a SharePoint Excel with no visible relationship in the model. `PO[NFM]` is a calculated column from it. Not clear whether NFM items are included or excluded from the main report.

7. **Which version of the 3 warehouse inclusion lists is the "source of truth"?** Lists differ across sub-queries — items may appear in one view but not another for the same warehouse.

8. **What does SI-SS as a DATA TYPE represent in the source?** It exists as a data type alongside SAFETY STK and SHIPPABLE INV but is excluded from the main PO filter for orders = 0. Likely represents the "net gap" position.

---

## §9 — Business assumptions / magic numbers

### 9.1 — `DeliveryTimes.delivery final + 7` (M code)

Hardcoded 7-day addition to the vendor's delivery final value to compute `NEW ETD WEEKEND`. No documentation of what the +7 represents — likely buffer for weekend/handling before the next ETD week-end anchor. If vendor lead times are already inclusive of handling, this double-counts and ETD overstates actual supply availability.

### 9.2 — Container divisor `/ 2350` in Demand Fulfillment SQL

```sql
CASE WHEN CONVERT(INT,coalesce(supply.[demand_lv3],0) / 2350) = 0 THEN 1 ELSE supply.[demand_lv3] / 2350 END
```

Hardcoded 2350 as the standard container capacity. No documentation of unit (cubic feet? units?). 40' HC container standard ≈ 2,350–2,400 cubic feet of cargo capacity, suggesting this is a cube-based divisor. If item cube-per-unit changes or mixed-container loading varies, this constant is inaccurate. Used in `onlynegSIcontainers` / `onlynegSI-SScontainers` flags.

### 9.3 — SS% Alert thresholds = 75 and 150 (hardcoded in Current calculated column)

```dax
IF(AND(PastSS% <= 150, SS% >= 150), SS%,
IF(AND(PastSS% >= 75, SS% <= 75), SS%, 0)) / 100
```

Hardcoded SS% thresholds: 75% = minimum acceptable, 150% = maximum acceptable. Items crossing from "acceptable" to "outside band" between weeks are flagged. Not documented, not parameterized. If policy changes (e.g. maximum raised to 200%), the calculated column must be edited and the model republished.

### 9.4 — CalendarWeekIndicator ranges differ by table

| Table | Range |
|---|---|
| DUE / ETD date tables | −10 to +21 |
| PO (main queries) | −10 to +21 |
| Old Snap | −10 to **16** |
| Current / Past Week | −10 to **16** |

`Old Snap`, `Current`, and `Past Week` have a shorter forward horizon (−10 to +16 = 26 weeks vs 32). Items only visible in weeks +17 to +21 in the PO table will have no matching SS data in Current/Past Week, and `Change SS%` / `SS% Alert` will return BLANK for those weeks.

### 9.5 — Current/Past Week lack warehouse grouping

The SQL `--new.WHSE` comment shows warehouse was intentionally removed from the PIVOT GROUP BY. `SS%` computed by Current is at **item × ETD week** grain only. When PO has multiple warehouses for the same item and ETD week, `LOOKUPVALUE('Current'[SS%], ITEM, PO[ITNBR], ETD, PO[ETD])` returns the first match — potentially a different warehouse's SS%.

### 9.6 — Demand Fulfillment 180-day fixed horizon

```sql
spdWeekEnding <= DATEADD(dd, 180, CAST(GETDATE() AS DATE))
```

Hardcoded 180-day (6-month) look-ahead for Demand Fulfillment. Not parameterized. If the planning horizon changes, the SQL must be edited.

### 9.7 — Priority Flag hardcoded by item prefix (Demand Fulfillment SQL)

```sql
CASE
  WHEN CHARINDEX('102',spdItem)=1 THEN 'HIGH'
  WHEN CHARINDEX('110',spdItem)=1 THEN 'HIGH'
  ...
  ELSE 'LOW'
END AS PRIORITY_FLAG
```

Item prefixes (102, 110, 153, 196, 520, 523, 598, 807, 144, 29841) hardcoded as "HIGH" priority. No lookup table, no parameter. Adding a new high-priority series requires a SQL edit and model republish.

### 9.8 — Item exclusion list hardcoded in Demand Fulfillment SQL

```sql
AND spdItem NOT LIKE '%HIDES' AND spdItem NOT LIKE '%VINYL' AND spdItem NOT LIKE '%KT'
AND spdItem NOT LIKE '%SW' AND spdItem NOT LIKE '%CARD' AND spdItem NOT LIKE '%OTTBULK'
AND spdItem NOT LIKE '%CARD2' AND spdItem NOT LIKE '%SPLIT' AND spdItem NOT LIKE '%SW2'
AND inv_item.SellableItemFlag = 'Y'
```

9 suffix-based exclusions + sellable flag. If new non-sellable suffix patterns are added, must remember to update this list in every SQL partition that references items.

### 9.9 — Custom status code mapping

The `Item Desc` SQL uses `Lvl_Nbr IN ('2', '3')` to filter SCP_FCST_ROOT items. `Lvl_Nbr` is a Logility item hierarchy level. Level 2 = SKU level, Level 3 = warehouse-specific. This means some items appear twice (once at level 2 with blank warehouse, once at level 3 with a warehouse). The relationship to PO uses `Merged = item_number + ':' + warehouse`, so level 2 rows (no warehouse) produce `key:` with trailing colon — these will not match any PO items.

### 9.10 — Does this report calculate dollar-value business impact?

**No explicit dollar-value formula exists in this model.** However, the report implicitly highlights inventory dollar risk through:
- Color-coded SS% gaps that flag items below 75% (risk of stockout and lost sales)
- Over-target items above 150% (excess working capital tied up)
- SI-SS negative items with no planned POs (supply gap that will materialize as shortage)

These are not quantified into dollar terms within the model. If users compute dollar impact externally (e.g. "SS% gap × item cost × margin"), that logic lives outside Power BI in manual analysis.

---

## §10 — Comparability / consistency

### 10.1 — `Due Color` direction is semantically ambiguous

```
Due Color = IF(SS% DUE > SELECTEDVALUE('Percent'[Percentage]), "RED", "GREEN")
```

If the percentage threshold represents the minimum acceptable SS% (e.g. 100%), then:
- SS% = 120% (> 100%) → RED (flagged)
- SS% = 80% (≤ 100%) → GREEN (not flagged)

This is **counter-intuitive** — typically RED flags *below* a threshold. If the threshold instead represents the maximum allowed (to flag excess), then the logic is correct but the visual cue is non-standard. Context-dependent, must confirm with business.

### 10.2 — DUE vs ETD can disagree for the same item

An item with SS% DUE = 120% (receipt-date view) may show SS% ETD = 60% (departure + lead time view) if the order has shipped but not yet arrived. The report shows both dimensions side by side — planners must reconcile the two views. No measure explains the delta between them.

### 10.3 — Warehouse populations differ across sub-queries

As documented in §4, the three warehouse inclusion lists in the PO SQL do not match:
- Items in warehouses C, CNW, or 232 are present in PSWWeeklyExtractSnapshot but **absent** from PlanDetailTimeline and DeliveryTimes sub-queries
- An item at WHSE C will have PSW data but no PlanDetailTimeline data → some columns populated, some blank

### 10.4 — Current/Past Week SS% is warehouse-ambiguous

The `--new.WHSE` comment in Current shows the warehouse column was intentionally dropped. `SS%` in Current is aggregated across warehouses for the same item + ETD week. Then `Change SS%` = `(Current[SS%] — PastWeek[SS%])/100` — but if items changed warehouse assignment between weeks, `Past Week` may have matched a different warehouse set.

### 10.5 — `Demand Fulfill SS` formula uses additive safety stock that doesn't algebraically simplify

```
(SUM(ss_can_supply) + SUM(runningdemand)) / (SUM(runningdemand) + SUM(spdSafetyStock))
```

If `runningdemand` varies independently in numerator and denominator (two separate SUM aggregates in DAX, not guaranteed equal), this is not equivalent to a standard SS coverage ratio. The formula is unusual enough to flag for logic review.

### 10.6 — `LastRefresh_Local` hour offsets contradictory

| Column | Offset | Interpretation |
|---|---|---|
| `Column 4` | `-3 hours` | HOUR() - 3 |
| `Last Refresh new` | `-5 hours` | HOUR() - 5 |

If the source `DateTime.LocalNow()` is UTC, CST is UTC-6 (standard) or UTC-5 (daylight). Neither explains the -3. If the server is in a non-US timezone, neither is reliable without checking the actual server location.

### 10.7 — `COLOR DUE` / `COLOR ETD` ordinal scaling

Values 8 and 9 share the same hex color (#FD00CA); values 10 and 11 share #5B5959. This suggests the ordinal originally had 11 categories but adjacent categories are now visually identical — possible consolidation never cleaned up.

---

## Closing — Interview seeds

**1. On the SS% threshold color logic:**
> "When you look at a RED flag next to an item's SS% — does RED mean 'this item is below safety stock and needs attention' or 'this item is above the threshold and has too much inventory'? The current measure colors RED when SS% is *above* the selected percentage value."

**2. On the three inconsistent warehouse lists:**
> "We found three different warehouse inclusion lists used in different parts of this same model — the PSW snapshot covers 17 warehouses, but the PlanDetailTimeline and DeliveryTimes sub-queries cover only 14, missing C, CNW, and 232. When you look at SS% for a C or CNW warehouse item, do you see gaps where a week's data just isn't there, or do you not use this report for those warehouses?"

**3. On the missing warehouse from Current/Past Week:**
> "The Current table that tracks week-over-week SS% change appears to have the warehouse column intentionally removed from its SQL. So when an item lives in multiple warehouses, the 'current SS%' gets averaged together and then looked up back to the PO table by item alone. Is that a known limitation, or is this a bug that nobody has noticed yet?"

**4. On the 4 SharePoint Excel files:**
> "This report enriches its data from four manual SharePoint Excel files — the vendor list, master EVC/ABC codes, the Wanek DRP breakdown, and the NFM filter. How often are those files updated, and what happens to the report if someone forgets to update one of them?"
