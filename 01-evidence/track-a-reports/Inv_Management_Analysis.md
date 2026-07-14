# Inv Management — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | SCP Global Team (`fb03479c-f98b-414f-bf8f-ab2dfa744ff4`) |
| **Report Name** | Inv Management |
| **Backing Model** | Inv Management (`0e8093fc-edc6-4983-ab77-4f01f372286f`) |
| **Model Size** | 33 tables (7 real + 4 calculated + 20 auto-date + 2 template), 16 measures, 163 calculated columns, 28 relationships, 0 RLS |
| **Analyzed** | 2026-07-07 |

> **Correction (2026-07-10):** this analysis refers to warehouse 335 as "Ashley's
> main DC" throughout (§1 and elsewhere). That framing has since been found to be
> overreach — an inference from this model's internal scoping, not a governed fact.
> The Fabric build's governed `DimWarehouse` definition confirms 335 (Ashton) is a
> real, distinct warehouse grouped separately from the core AFI warehouses, but does
> not confirm network-wide primacy. Provisionally corrected pending Robert's
> confirmation — see `07-fabric-build/WAREHOUSE_335_RECONCILIATION.md`. The original
> text below is left as-is (unedited, per source-of-record practice); read
> "Ashley's main DC" wherever it appears as "warehouse 335 (Ashton)" instead.

---

## §1 — Supply-chain question & chain link

**Question:** For warehouse 335 (Ashley's main DC), what is the current inventory excess position — broken down by Prod Type (CG / UPH / RP), Collective Class, Division, Office — and how many months of supply does that excess represent after accounting for firm demand, transfer out, safety stock changes, and near-term planned demand?

| Link | How served |
|---|---|
| **Inventory** (primary) | Tracks on-hand safety stock, shippable inventory, and derived excess at warehouse 335. Classifies excess into 4 disposal types: Oversea Vendor, Consolidate, Drop, Unexpected |
| **Supply** | Firm demand and transfer-out quantities (3-month and 6-month horizons) are subtracted from inventory to determine net excess |
| **Receipts** | `SI at US Warehouse` table tracks inbound shippable inventory from US warehouses (1, 5, 15, 17, 28, 42, ECR) via lead-time-based ETA for FOB code 301 |

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Which items have true excess at WH 335 that could be liquidated or transferred? | Inventory Planner | Weekly | **Operational** |
| For excess classified as "Oversea Vendor" — should the vendor take back the stock? Coordinate return logistics | Inventory Planner / Vendor Manager | Weekly | **Operational** |
| For excess classified as "Consolidate" (from consolidate-source vendors) — route to consolidated shipments | Supply Planner | Weekly | **Operational** |
| For excess classified as "Drop" (HB items or Discontinued) — mark down, write off, or liquidate | Inventory Analyst / Finance | Weekly | **Operational** |
| Is the current Open Capacity across CG/UPH/RP sufficient for new production? Adjust production allocation | Production Planner / Manager | Weekly | **Performance / Governance** |
| What is the Months of Supply (MOS) for excess inventory? Inform whether to expedite liquidation vs hold | Inventory Manager | Weekly / Monthly | **Performance / Governance** |
| Where is the SS coverage gap (Old SS Uncover)? Trigger replenishment of safety stock | Planner | Weekly | **Operational** |
| How does inventory aging profile look (6/12/18+ months)? Prioritize aging stock for clearance | Inventory Analyst | Monthly | **Operational** |

---

## §3 — Key metrics / measures

**16 measures total** — 9 in `Inventory` table, 7 in `SI at US Warehouse` table.

### A. Core inventory measures (Table: Inventory)

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| **True Excess** (calc column, not measure) | Net excess after subtracting firm demand and transfer out from Old SISS (SI minus SS) | Item × WH 335 | `IF(Excess - Old TRF Stock > 0, Excess - Old TRF Stock, 0)` where Excess = `IF(Firm Demand > Old SISS, 0, Old SISS - Firm Demand)` |
| **MOS Case 1** | Average Months of Supply for excess inventory using weeks 2-5 plan demand as consumption rate | Item × WH 335 | `AVERAGEX(SUMMARIZE(Inventory[Item], "True Excess", SUM(...), "W25 Plan Demand", ..., "W2 SS Change", ..., "W25 True Demand", ...), IF((True Excess-W2 SS Change)<0, 0, IF(W25 Plan Demand=0, True Excess-W2 SS Change, (True Excess-W2 SS Change)/W25 Plan Demand)))` |
| **MOS Case 2** | Average Months of Supply for remaining excess after Case 1, against weeks 6-9 plan demand | Item × WH 335 | `AVERAGEX(SUMMARIZE(... "True Excess 2", SUM(Est Excess Case 1), "W69 Plan Demand", ...), IF(W69=0, True Excess 2, True Excess 2 / W69))` |
| **MOS Case 111** | **Duplicate of MOS Case 1** with additional branch for W25 True Demand < 0 | Item × WH 335 | Same base CASE 1 logic with extra IF for negative demand scenarios |
| **MOS Case6 1** | Same as MOS Case 1 but using 6-month horizon True Excess6 | Item × WH 335 | Parallel structure using Est Excess6 Case 1 |
| **MOS Case6 2** | Same as MOS Case 2 but using 6-month horizon | Item × WH 335 | Parallel structure using Est Excess6 Case 1 |
| **Open Capacity** | Remaining production capacity after subtracting all inventory dispositions (by Prod_Type) | Prod_Type (CG/UPH/RP) | `IF(Prod_Type="CG", 160000 - SUM(Old SS Coverage + SS Uncover + Expedite + TRF Stock + True Excess), IF(Prod_Type="UPH", 58000 - ..., 218000 - ...))` |
| **New True Excess** | Simplified excess after accounting for W2 SS Change only | Item | `IF(W2 SS Change > True Excess, 0, True Excess - W2 SS Change)` |
| **Measure 2** | **Empty — no expression** | — | ` ` (blank measure, likely abandoned) |

> ⚠️ **Suspicious — `MOS Case 11` is a literal duplicate of `MOS Case 1`:** Same DAX expression. Copy-paste residue that was never cleaned up.

> ⚠️ **Suspicious — `Measure 2` is blank:** Zero expression. Should be deleted to reduce model noise.

> ⚠️ **Suspicious — `MOS Case 1` / `MOS Case 111` use `AVERAGEX` not `SUM`/`DIVIDE`:** The MOS measures average the per-item MOS ratio across items. This produces a different number than dividing total excess by total demand. If one item has very high MOS and another has low MOS, the AVERAGEX weights each item equally regardless of volume — a low-volume item with 24 months of excess distorts the aggregate more than intuition expects. See §10.

> ⚠️ **Suspicious — `Open Capacity` subtracts all inventory dispositions from a hardcoded number:** The formula treats True Excess, SS Coverage, SS Uncover, Expedite, and TRF Stock as all reducing available capacity. If the classification overlaps (e.g. SS Coverage and SS Uncover are complementary), they are double-counted as both reducing capacity.

### B. Per-warehouse SI measures (Table: SI at US Warehouse)

| Measure | Meaning | Logic |
|---|---|---|
| **Whse ECR - SI** | Shippable Inventory at warehouse ECR | `SUMX(SUMMARIZE('SI at US Warehouse', [spdItem], "SI", CALCULATE(SUM([spdShippableInventory]), [spdWarehouse]="ECR")), [SI])` |
| **Whse 1 - SI** | Shippable Inventory at warehouse 1 | Same pattern, filter `spdWarehouse="1"` |
| **Whse 5 - SI** | Shippable Inventory at warehouse 5 | Same |
| **Whse 15 - SI** | Shippable Inventory at warehouse 15 | Same |
| **Whse 17 - SI** | Shippable Inventory at warehouse 17 | Same |
| **Whse 28 - SI** | Shippable Inventory at warehouse 28 | Same |
| **Whse 42 - SI** | Shippable Inventory at warehouse 42 | Same |

> ⚠️ **Suspicious — 7 per-warehouse SI measures use identical SUMX+SUMMARIZE+CALCULATE pattern.** Only the warehouse filter string changes. These are an exact duplicate pattern that could collapse into a single measure with a Warehouse dimension. If a new US warehouse is added, a new measure must be created.

### C. Calculated column classification (True Excess Type)

The most important logic lives in calculated columns, not measures:

```
True Excess Type = 
  If(True Excess=0, "No Excess",
    IF(Country<>"VN", "Oversea Vendor",
      IF(Vendor="633312", "Oversea Vendor",
        IF(Vendor="643509", "Oversea Vendor",
          IF(Consolidate Type="Consolidate", "Consolidate",
            IF(HB="HB", "Drop",
              IF(Current Status="D", "Drop", "Unexpected")
  ))))))
```

This cascading SWITCH classifies every excess dollar into a disposal action. Classification priority: Oversea Vendor (non-VN or specific VN vendors) → Consolidate → Drop (HB or Discontinued) → Unexpected.

> ⚠️ **Suspicious — Classification is mutually exclusive by priority, not by business case.** A "Consolidate" item that is also "HB" is classified as "Consolidate" because Consolidate check comes before HB/Drop in the IF chain. The actual disposal action for an HB Consolidate item could differ.

---

## §4 — Data sources & lineage

| Source | Type | Flag |
|---|---|---|
| **Wholesale_DemandPlanning_AFI.SupplyPlanDetail** | Azure SQL (`Ashley-edw / ASHLEY_EDW`) | ✅ Governed |
| **SupplyChain_Enh.PSWWeeklyExtractSnapshot** | Azure SQL | ✅ Governed |
| **Enterprise_DW.DimDate** | Azure SQL | ✅ Governed |
| **PowerBI_SupplyChain.VendorMaster** | Azure SQL | ✅ Governed |
| **Distribution_Warehouse_Wholesale.t_stored_item / t_item_master / TranLog** | Azure SQL | ✅ Governed |
| **Wholesale_ProductSourcing_AFI.DeliveryTimes** | Azure SQL | ✅ Governed |
| **SupplyChain_DW.DimCurrentProductDetails** | Azure SQL | ✅ Governed |
| **MasterData_ItemMaster_AFI.ITBEXT** (MFPUS) | Azure SQL | ✅ Governed |
| **DW_Developer.TableDictionary** | Azure SQL (metadata only) | ✅ Governed |
| **VENDOR LIST AFT & 232.xlsx** (SharePoint) — sheet "AFI" | **SharePoint Excel** | ⚠️ **Ungoverned** — manual file at `SCPGlobalTeam-Tools/Shared Documents/Tools/Daily Reports/` |

> **No dataflows used.** All SQL direct from `Ashley-edw / ASHLEY_EDW`. One SharePoint Excel for vendor MB/DD mappings.

### Key Fact Tables in SQL

| Table | Purpose |
|---|---|
| **Inventory** (M query, monster SQL with 15+ CTEs) | Core table — joins SupplyPlanDetail + PSW + Firm PO + Vendor info + Product details + Date dimension. Warehouse 335 only. Computes all calc columns (True Excess, Oversea Vendor, Consolidate, Drop, Unexpected, MOS components) |
| **W2 SS Change** | Safety stock week-over-week delta (CalendarWeekIndicator 0 → 1) for warehouse 335 |
| **Inv Age** | Inventory aging from TranLog (transaction 151 = receipt). Age buckets: 6m, 12m, 18m, 18m+. Warehouse 335 only |
| **SI at US Warehouse** | Inbound shippable inventory at US warehouses (1,5,15,17,28,42,ECR) via DeliveryTimes lead time (FOB code 301) |

---

## §5 — Grain & snapshot strategy

**Primary grain:** Item × WH 335 (weekly snapshot — current Saturday via `DATEADD(DAY, 14 - DATEPART(WEEKDAY, GETDATE()), GETDATE())`)

**Snapshot strategy:** **Point-in-time only.** The `Inventory` table uses `MAX(dtec)` from `SupplyPlanDetail` with latest detection timestamp. No historical snapshots preserved.

**Horizon:**
- **Current position:** WH 335 safety stock + shippable inventory as of latest Saturday
- **Firm demand:** 3-month and 6-month forward (CalendarMonthIndicator ≤ 3 / ≤ 6 / ≤ 12)
- **Plan demand:** Weeks 2-5 and 6-9 forward
- **PSW supply:** Weeks 0-20 from PSWWeeklyExtractSnapshot
- **Ship history:** `FiscalWeekIndicator` -8 to 0 (8 weeks back)

**Aging:** Based on TranLog receipt date (`tran_type='151'`) compared to `GETDATE()`. This is a running calculation, not a point-in-time snapshot — each refresh recalculates age from the fixed receipt date, so aging drifts forward each week.

---

## §6 — Dimensions used

| Dimension | Source | Notes |
|---|---|---|
| **Product (Item)** | `SupplyChain_DW.DimCurrentProductDetails` (via SQL join in Inventory query) + `MasterData_ItemMaster_AFI.ITBEXT` for MFPUS | Enriched with `Current Status`, `Future Status`, `Collective Class`, `Finance Division`, `Responsible Office`, `Prod_Type` (CG/UPH/RP via hardcoded rules) |
| **Date** | `Enterprise_DW.DimDate` — weekly at Saturday boundaries | CalendarWeekIndicator, CalendarMonthIndicator used for forward demand windows. No fiscal calendar attributes in the core Inventory query |
| **Vendor** | `AFI` (SharePoint Excel) — vendor master with MB/DD columns per warehouse, LT, FOB, Country | **Ungoverned manual file**. `Oversea Vendor` classification depends on Country field and hardcoded vendor IDs 633312/643509 |
| **Prod_Type** | Hardcoded classification in SQL: CG (Accessories, Bedroom, Bedding, Dining, Entertainment, Home Office, Occasional, Outdoor, Other), UPH (Motion, Stationary), RP (everything else) | **Static mapping** — if a new product class is added (e.g. "Mattress"), it falls into RP regardless of business intent |
| **Warehouse** | Not in the core model — WH 335 is hardcoded in every query. `SI at US Warehouse` separately tracks 7 warehouses via a UNION-type pattern | **No Warehouse dimension table exists** |

### Notable re-derived attributes

| Attribute | Source | Drift risk |
|---|---|---|
| **Prod_Type** (CG/UPH/RP) | Hardcoded CASE in SQL based on item class | New product categories default to RP incorrectly |
| **True Excess Type** | DAX SWITCH cascading IF — Country, Vendor, Consolidate Type, HB flag, Current Status | Priority-based classification may assign wrong disposal action when item qualifies for multiple categories |
| **Oversea Vendor** | Calc column: single Country check (VN) + 2 vendor IDs | All non-VN vendors = "Oversea Vendor". No distinction between actual overseas returnability and contractual obligation |
| **Consolidate** | `IF(Consolidate Type = "Consolidate", True Excess - Oversea Vendor, 0)` | Depends on `Consolidate Type` column origin — undocumented |
| **C&F Status** | `Current Status + ":" + Future Status` | Format depends on both columns using consistent delimiters |

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| **MOS Case 11 = MOS Case 1** | Same DAX expression verbatim — copy-paste residue |
| **Measure 2 is blank** | Empty measure with no expression — should be deleted |
| **MOS Case 1 / MOS Case6 1** | Parallel structures for 3-month and 6-month horizons. Same AVERAGEX pattern, different excess column. Could unify with a parameter |
| **MOS Case 2 / MOS Case6 2** | Same parallel pattern with 6-9 week demand |
| **7 per-warehouse SI measures** | `Whse ECR/1/5/15/17/28/42 - SI` — identical SUMX+SUMMARIZE+CALCULATE, only warehouse filter string changes. Single measure + Warehouse dimension would replace all 7 |
| **True Excess / True Excess6** | Two nearly identical calculated column chains (Excess → TRF Stock → True Excess → Oversea Vendor → Consolidate → Drop → Unexpected). Same logic at 3-month and 6-month horizons. Could parameterize horizon |
| **20 auto-generated LocalDateTables** | One per date column in the model. Could consolidate to a single role-playing date table |
| **SummarizedInventory → GeneralTable** | Calculated table SUMMARIZE then unpivoted to row format. This is an ETL step done in DAX (as calculated tables) rather than in Power Query. Works but recalculates on every refresh |
| **US Item / ConsoList / Sort / Counts / Itemtransfer CTEs** | The same "exclusive-item" dedup logic appears in both `Inventory` and `Inv Age` SQL queries. Two independent copies of the same subquery |
| **True Excess Type / True Excess6 Type** | Identical cascading SWITCH logic duplicated for 3-month and 6-month variants |

---

## §8 — Open questions

1. **Why is the core model scoped to warehouse 335 only?** All inventory queries hardcode WH 335. Is this the only DC tracked by this report, or are there parallel reports for other warehouses?

2. **Who maintains the VENDOR LIST AFT & 232.xlsx SharePoint file?** This manual Excel drives vendor classification and Oversea Vendor flagging. If it goes stale, excess classification breaks silently.

3. **What is `Consolidate Type` and where does it come from?** The classification depends on a `Consolidate Type` column on the Inventory table. Its origin in the SQL is not documented.

4. **What does `Prod_Type = "RP"` encompass?** The SQL CASE maps everything not in CG or UPH to "RP" (Rolling/Panel). As Ashley's product lines evolve, new categories default incorrectly.

5. **Is the `MOS Case 1/111` duplicate intentional?** MOS Case 111 has additional logic for negative W25 True Demand but otherwise duplicates Case 1. Are both used in visuals?

6. **Who uses the `SI at US Warehouse` measures and how?** Shippable inventory across 7 US warehouses is tracked but not linked to the core WH 335 inventory position. Is this a separate inventory view for inbound sourcing decisions?

7. **Does the Inv Age table correctly handle returns?** The SQL filters `tran_type='151'` (receipt) and excludes items with `tran_type='347'` (return to vendor). But in/out adjustments may not be fully captured — is the age calculation accurate for items with multiple receipt events?

8. **How often is the model refreshed?** The model uses `GETDATE()` in SQL for date anchoring. If refresh fails for multiple days, the "current Saturday" anchor shifts and the entire inventory position jumps forward.

---

## §9 — Business assumptions / magic numbers

### 9.1 — Open Capacity: 160,000 / 58,000 / 218,000

```dax
Open Capacity =
  IF(Prod_Type = "CG", 160000 - SUM(dispositions...),
    IF(Prod_Type = "UPH", 58000 - SUM(dispositions...),
      218000 - SUM(dispositions...)))
```

Three hardcoded capacity numbers by Prod_Type. No documentation of what these represent (square feet? pallet positions? dollar value?). If warehouse layout changes or WH 335 expands, these numbers must be manually updated in DAX. No parameter, no source table.

### 9.2 — Age thresholds: 182 / 365 / 547 days

```sql
Inv Age Range:
  <= 182  → '6 months'
  183-365 → '12 months'
  366-547 → '18 months'
  > 547   → 'More than 18 months'
```

Hardcoded boundaries. Standard 6/12/18 month aging classes. Reasonable but undocumented — if management changes aging definitions (e.g. "18 months" should be 540 days, not 547), the SQL must be edited.

### 9.3 — Country exclusion: Vietnam only for "Oversea Vendor" classification

```dax
Oversea Vendor = IF(Country <> "VN", True Excess,
  IF(Vendor = "633312", True Excess,
    IF(Vendor = "643509", True Excess, 0)))
```

The classification logic assumes all non-Vietnam vendors can take back excess inventory. No consideration of:
- Contractual returnability clauses
- Vendor location (a Chinese vendor with no US presence is classified same as a US-based vendor)
- MOQ or minimum return thresholds

### 9.4 — Vendor exceptions: 633312 and 643509

Two hardcoded Vietnam vendor IDs that are treated as "Oversea Vendor" despite being VN-located. These are the only VN vendors flagged as returnable. If a new VN vendor is added, it silently falls through to Consolidate/Drop/Unexpected.

### 9.5 — Prod_Type classification (hardcoded SQL CASE)

```sql
CG:  'Accessories','Bedroom','Bedding','Dining','Entertainment','Home Office','Occasional','Outdoor','Other'
UPH: 'Motion','Stationary'
RP:  (everything else)
```

New product classes default to RP. If Ashley adds "Mattress" as a product class, it's classified as RP not CG — biasing capacity open for CG downward and RP upward.

### 9.6 — Current Saturday anchor calculation

```sql
CAST(spdWeekEnding as Date) = DATEADD(DAY, 14 - DATEPART(WEEKDAY, CAST(GetDate() AS DATE)), CAST(GetDate() AS DATE))
```

Anchors the inventory snapshot to the current Saturday. This formula assumes `DATEPART(WEEKDAY)` returns 1 for Sunday, making the next Saturday = GETDATE + (14 - current_dow). If the first day of week setting differs on the SQL server, the anchor lands on a different day. Also, if the model refreshes on Saturday itself, the anchor formula should be correct; if it refreshes on Friday, it references the *next* Saturday (which doesn't exist yet in SPD data).

### 9.7 — FOB code 301 hardcoded in SI at US Warehouse

```sql
WHERE dltfobcode = '301'
```

FOB code 301 is the only delivery time configuration used for US warehouse lead-time calculation. If Ashley changes FOB terms for any of these warehouses, this filter breaks.

### 9.8 — Lead time calculation for SI at US Warehouse

```sql
DATEADD(DAY, 7 - DATEPART(WEEKDAY, GETDATE()), CAST(GETDATE() AS DATE))  -- this Saturday
-- then adds lead time from DeliveryTimes to compute ETA/ETD
```

Hardcoded "current Saturday" anchor + delivery lead time. No weekend/holiday handling. If lead time is 2 days and Friday is a holiday, ETA is calculated as Saturday+2 = Monday, but the formula doesn't account for holidays.

### 9.9 — Week range constants in Inventory SQL

| Range | Purpose |
|---|---|
| Weeks 0-20 | PSWWeeklyExtractSnapshot forward horizon |
| Weeks 1-22 | Firm purchase orders timeline |
| Weeks 2-5 (W25) | Near-term plan demand for MOS Case 1 |
| Weeks 6-9 (W69) | Medium-term plan demand for MOS Case 2 |
| CalendarMonthIndicator ≤ 3 | 3-month firm demand window |
| CalendarMonthIndicator ≤ 6 | 6-month firm demand window |
| CalendarMonthIndicator ≤ 12 | 12-month reference |
| FiscalWeekIndicator -8 to 0 | Shipping history lookback |

All hardcoded. No parameters. If the planning horizon changes (e.g. MOS Case 1 should use weeks 3-6), every reference must be edited.

### 9.10 — Item exclusion suffixes for exclusive-item dedup

`'%W1'`, `'%W9'` — used in SQL to identify exclusive items (likely Wayfair 1 and Wayfair 9 item variants). Hardcoded in both `Inventory` and `Inv Age` queries.

### 9.11 — Does this report calculate dollar-value business impact?

**No.** Zero measures or columns apply dollar multipliers (unit cost, carrying cost rate, margin, revenue). The report operates entirely at the unit/quantity level. All "excess" numbers represent physical inventory quantities, not dollar values. If financial impact is needed (e.g. "carrying cost of excess = $X"), it must be calculated externally.

---

## §10 — Comparability / consistency

### 10.1 — MOS Case 1 / MOS Case 111: AVERAGEX distorts aggregate result

Both measures use `AVERAGEX(SUMMARIZE(Inventory[Item], ...), per-item MOS)`. This averages the per-item MOS ratio regardless of item volume. Consider two items:

| Item | Excess | Plan Demand | Per-Item MOS | Volume-weighted |
|---|---|---|---|---|
| A | 100 | 10 | 10.0 | 100/100 = 1.0 |
| B | 10 | 90 | 0.11 | 10/100 = 0.1 |
| **AVERAGEX MOS = 5.06** | | | **(10+0.11)/2 = 5.06** | **(100+10)/(10+90) = 1.1 |

The AVERAGEX reports 5.06 months while the true excess/demand ratio is 1.1 months. **The MOS number is systemically inflated** by low-volume, high-excess items. This could lead executives to believe excess is less urgent than it actually is.

### 10.2 — True Excess (3-month) vs True Excess6 (6-month) use different horizons

| Chain | Demand horizon | Excess horizon |
|---|---|---|
| True Excess | Firm Demand (3mo) + TRF Out (3mo) | 3-month |
| True Excess6 | Firm Demand6 (6mo) + TRF Out6 (6mo) | 6-month |

Two different excess numbers for the same item. Report visuals showing both side by side may confuse users if labeled without clear horizon distinction. "True Excess" in a monthly WBR may mean 3-month excess to one planner and 6-month to another.

### 10.3 — MOS Case 1 uses weeks 2-5 demand; MOS Case 2 uses weeks 6-9 demand (no overlap)

The two MOS cases are designed to be sequential (Case 1 excess that can't be absorbed by weeks 2-5 flows to Case 2 for weeks 6-9). But they are computed as independent AVERAGEX ratios rather than a true cascading calculation chain. The denominator shifts between cases without a bridge — the same unit of excess is measured against two different time windows.

### 10.4 — Three different date-anchoring strategies across tables

| Table | Date anchor | Method |
|---|---|---|
| **Inventory** | Current Saturday | `DATEADD(DAY, 14-DATEPART(WEEKDAY, GETDATE()), GETDATE())` |
| **W2 SS Change** | Yesterday / Day-before-yesterday | `DATEADD(DAY, CASE WHEN DATEPART(WEEKDAY, GETDATE())=2 THEN -2 ELSE -1 END, GETDATE())` |
| **SI at US Warehouse** | Current Saturday | Same as Inventory |
| **Inv Age** | `GETDATE()` | Age = DateDiff(day, receipt_date, GetDate()) |

`W2 SS Change` uses a different date logic (adjusts for Monday = skip Sunday). If the model refreshes on Monday, W2 SS Change looks back 2 days while Inventory anchors to the next Saturday. These two tables are joined via `LOOKUPVALUE`, and if the refresh time falls between the two anchor calculations, the SS Change value reflects a different window than the main inventory position.

### 10.5 — Oversea Vendor classification uses static Country field (Vendor Master Excel)

The `AFI` SharePoint Excel file supplies Country. If a vendor's Country is updated in the Excel, `Oversea Vendor` classification for that vendor's items changes on next refresh — but all historical data is immediately reclassified. There is no snapshot of "country as of the date the excess was calculated."

### 10.6 — `SummarizedInventory` aggregates after classification, not before

The calculated table `SummarizedInventory` performs `SUMMARIZE(Inventory, Prod_Type, Collective Class, Division, Office, SUM(SS Coverage), SUM(SS Uncover), ...)`. This aggregates the already-classified excess categories. If a classification column changes (e.g. a re-categorization of Prod_Type), the entire historical SUMMARIZE result shifts — no anchor to the date of classification.

### 10.7 — `Inv Age` and `Inventory` use different product dedup logic

Both queries have an "exclusive item" CTE chain (USItem → ConsoList → Sort → Counts → Itemtransfer), but these are independent copies. If one is updated to fix a dedup edge case and the other is not, the item counts between the two tables diverge silently.

---

## Closing — Interview seeds

**1. On the Open Capacity formula:**
> "The report calculates open capacity as 160,000 for CG, 58,000 for UPH, and 218,000 for RP, minus all inventory dispositions. Where did those capacity numbers come from — and when you see a negative open capacity, what decision do you make?"

**2. On the Oversea Vendor classification:**
> "The model flags all non-Vietnam vendors as able to take back excess inventory. Has anyone ever tried to send excess to a vendor that refused it? And how do you determine which Overseas vendors actually participate in return programs?"

**3. On how you actually use the MOS numbers in meetings:**
> "The Months of Supply measure averages across items — so one item with very high excess and low demand makes the aggregate MOS look bigger than the total excess divided by total demand. When you present MOS to leadership, do you reference this number, or do you have a different way of calculating excess coverage that feels more accurate?"

**4. On the single-warehouse scope:**
> "This model only covers warehouse 335. Do you have equivalent reports for the other DCs, or do you use this one as the single source of truth for all inventory management decisions? If a user needs excess visibility at another warehouse, where do they go?"
