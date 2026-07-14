# Act+Fcst by WNK & MILL Prod Resource — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | SCP Global Team (`fb03479c-f98b-414f-bf8f-ab2dfa744ff4`) |
| **Report Name** | Act+Fcst by WNK & MILL Prod Resource |
| **Backing Model** | Act+Fcst by WNK & MILL Prod Resource (`5b4974d6-e9da-49a7-86c6-3d7d73e6ea7b`) |
| **Description** | Takes the Item-Warehouse forecast from Demand Optimization and traces back the sourcing strategy to connect the forecast directly to the associated production resource at Wanek and/or Millenium for FG, UN Kits, and Components |
| **Model Size** | 20 tables (10 user + 10 auto-date), 14 measures, 23 relationships, 0 RLS roles |
| **Analyzed** | 2026-07-07 |

---

## §1 — Supply-chain question & chain link

**Question:** For each production resource (physical line/machine) at Wanek 1, Wanek 2, Wanek 3, and Millenium, what is the forecast demand volume (in units), and is available production capacity sufficient to meet it over the forward horizon (16 weeks)?

| Link | How served |
|---|---|
| **Forecast** (primary) | Item-warehouse forecast from Demand Optimization (Logility) split into RSLF (resultant), PROL (promotional lift), FUTO (future orders), traced to production resource |
| **Production** (primary) | Maps forecast to specific production lines (`ProdResourceId`) at each WNK/MILL plant via a 3-branch sourcing logic (Buy → vendor plant, Transfer → source plant, Make → producing plant) |
| **Supply / Receipts** | `VendorShipped` tracks actual shipped quantities from WNK/MILL IMHIST, with a +56-day ETD offset to align with receipt at destination warehouse |
| **Demand** | `ActDemand` provides invoiced + open order actuals for the historical comparison window (FiscalYearIndicator ≥ −1) |

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Is a specific production line at WNK/MILL over- or under- capacity for the forecasted demand? Reassign production across lines or plants | Production Planner | Weekly | **Operational** |
| Which items have forecast volume exceeding available hours at their assigned resource? Decide to add overtime, shift production, or expedite | Production Planner | Weekly | **Operational** |
| Is the actual shipped quantity from the vendor aligned with what was forecast downstream? Identify chronic variance | Planner / Analyst | Weekly / Monthly | **Performance / Governance** |
| What is the net Act+Fcst position for a resource? (past-due demand + forward forecast) — trigger escalation if past-due is accumulating | Planner / Supply Chain Analyst | Weekly | **Operational** |
| Where are UN Kit component demands vs their make/buy/transfer source? Trace component demand to parent item's production resource | Planner (Components) | Weekly | **Operational** |
| Which planning vendors / production locations are sourcing what volumes? Manage vendor allocation vs plant capacity | Supply Planner | Monthly | **Performance / Governance** |
| Does the 56-day lead time assumption for vendor shipments still match actual transit times? Review ETA accuracy | Analyst | Quarterly | **Performance / Governance** |

---

## §3 — Key metrics / measures

**14 measures total** — all in `_Measures` (dummy) table.

### A. Forecast measures

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| **Fcast - Result** | Baseline resultant forecast quantity (units) | Item × WH × FiscalMonth × Datatype=R | `CALCULATE(SUM(Fcast[Qty]), Fcast[Datatype]="RSLF")` — sourced from `DemandForecastSnapshot.dfcResultantForecast`, summed per fiscal month |
| **Fcast - Promo** | Promotional lift forecast (units) | Same × Datatype=P | `CALCULATE(SUM(Fcast[Qty]), Fcast[Datatype]="PROL")` |
| **Fcast - Total** | Sum of baseline + promo | Same | `[Fcast - Result] + [Fcast - Promo]` |
| **ETD Fcast** | Resultant + promo shifted by 8-week ETD offset via inactive relationship | Same, but anchored to `ETDWkLastDate` | `CALCULATE(SUM(Fcast[Qty]),...USING USERELATIONSHIP(Fcast[ETDWkLastDate] ↔ FiscalCal[Transaction Date]))` for both RSLF and PROL |
| **FcstAverageWeekly** | Average weekly ETD forecast over forward horizon (weeks 1–16) | Resource × Week | `DIVIDE(CALCULATE([ETD Fcast], FiscalWeekIndicator >0 AND <=16), 17)` — **divide by 17 for 16-week span** |

> ⚠️ **Suspicious — `FcstAverageWeekly` divides by 17 not 16:** The filter is `FiscalWeekIndicator > 0 AND <= 16` = 16 weeks. But `DIVIDE(... , 17)`. If the goal is average per week, the denominator should be 16 (or 15 for "next 15 complete weeks + current partial week"). The +1 is either a fencepost adjustment for the current partial week or a bug. No documentation.

### B. Actual / Demand measures

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| **Act - Invoiced** | Historical invoiced demand (units) | Item × WH × Week × Status | `CALCULATE(SUM(ActDemand[Order Qty]), ActDemand[Status]="Invoiced")` |
| **Act - Open Ord** | Open customer orders not yet invoiced | Same × Open | `CALCULATE(SUM(ActDemand[Order Qty]), ActDemand[Status]="Open Order")` |
| **Past Due Qty** | Open orders whose fiscal week is in the past | Item × WH × Past Week × Open | `CALCULATE([Act - Open Ord], FiscalWeekIndicator < 0)` |

### C. Composite measures

| Measure | Meaning | Logic |
|---|---|---|
| **Act+Fcast** | Historical actuals (past months) + forward forecast | `CALCULATE(SUM(ActDemand[Order Qty]), FiscalMonthIndicator < 0) + [Fcast - Result] + [Fcast - Promo]` |
| **Act+Fcast Weekly Qty** | Act+Fcast divided by weeks in month | `DIVIDE([Act+Fcast], [FiscalWeeksinMonth])` |
| **FiscalWeeksinMonth** | Number of weeks in the current fiscal month context | `CALCULATE(AVERAGE(z_FiscalCal[FiscalWeeksinMonth]))` — backed by hardcoded SWITCH column |

> ⚠️ **Suspicious — `Act+Fcast` fiscal boundary:** `CALCULATE(SUM(ActDemand[Order Qty]), FiscalMonthIndicator < 0)` — the `< 0` boundary uses the actDemand dimension's fiscal context. If FiscalMonthIndicator = 0 represents "current month," the boundary is correct. But ActDemand and Fcast may have different FiscalMonthIndicator assignments for the same month (e.g. one at −1 one at 0) — creating a gap or double-count at the transition boundary.

### D. Production & Vendor measures

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| **Prod Capacity** | Total available production hours (firm + planned, bounded) | Resource × Week | `CALCULATE(SUM(ProdCapacity[TotalAvailHours]))` — source uses `GREATEST((FirmHours+PlannedHours), TotalAvailHours)`, so if planned > capacity it takes planned as the "available" value |
| **Vendor Shipped** | Quantity shipped by vendor, by production week | Item × Resource × Week | `CALCULATE(SUM(VendorShipped[Shipped Qty]))` — source: IMHIST TRQTY, JOIN ProdResourceId |
| **ETA Vendor Shipped** | Same as Vendor Shipped, shifted by 56 days via inactive relationship | Same, anchored to receipt week | `CALCULATE(SUM(VendorShipped[Shipped Qty]), USERELATIONSHIP(FiscalCal[Date] ↔ VendorShipped[ETAWkLastDate]))` |

> ⚠️ **Suspicious — `Prod Capacity` takes `MAX(Firm+Planned, TotalAvailHours)`:** The SQL uses `GREATEST(FirmHours+PlannedHours, TotalAvailHours)`. If planned hours exceed available capacity, the measure uses planned as the capacity — meaning **capacity is never below the planned load by construction**. The measure shows what was scheduled, not what was actually available. To see true under/over-capacity, a user must mentally compare Prod Capacity with Utilized Hours (if such a visual exists).

> ⚠️ **Suspicious — `Vendor Shipped` and `ETA Vendor Shipped` are the same base value on different dates:** The same `SUM([Shipped Qty])` is used. `Vendor Shipped` anchors to `FiscalWeekLastDate` (production ship week), while `ETA Vendor Shipped` shifts 56 days forward to `ETAWkLastDate` (expected receipt week). No measure captures the *delta* between planned ETA and actual arrival — so transit-time variance is invisible.

---

## §4 — Data sources & lineage

| Source | Type | Flag |
|---|---|---|
| **SupplyChain_Enh.DemandForecastSnapshot** | Azure SQL (`ashley-edw / ashley_edw`) | ✅ Governed |
| **SupplyChain_Enh.DemandInventorySnapshot** | Azure SQL | ✅ Governed |
| **SupplyChain_Enh.ActualsCustItemWH_AFI** | Azure SQL | ✅ Governed |
| **SupplyChain_Enh.ProductionConversion** | Azure SQL | ✅ Governed |
| **Supplychain_History.ProductionCapacity** | Azure SQL | ✅ Governed |
| **Enterprise_DW.DimDate** | Azure SQL | ✅ Governed |
| **Manufacturing_Inventory_WNK.IMHIST** | Azure SQL (Wanek) | ✅ Governed |
| **Manufacturing_Inventory_MIL.IMHIST** | Azure SQL (Millenium) | ✅ Governed |
| **Manufacturing_MasterData.BOMView** (implied via SQL) | Azure SQL | ✅ Governed |
| **z_ProductDetails** (via PBI Dataflow) | Dataflow `CurrentProductDetails` | ✅ Governed (from EDW upstream) |
| **z_FiscalCal** (via PBI Dataflow) | Dataflow `AshleyFiscalCalendarV2` | ✅ Governed |
| **z_WarehouseMaster** (via PBI Dataflow) | Dataflow `WarehouseMaster` | ✅ Governed |

> ✅ **No SharePoint, Excel, CSV, or ODBC sources found.** All 20 tables are sourced from governed Azure SQL or governed PBI Dataflows (which themselves source from EDW).

### EDW objects summary: 10+ SQL tables/views across `ashley_edw`, `Manufacturing_Inventory_WNK`, `Manufacturing_Inventory_MIL`, `Manufacturing_MasterData`, `SupplyChain_Enh`, `Supplychain_History`, `Enterprise_DW`, `Wholesale_DemandPlanning_AFI`, `PowerBI_SupplyChain`, `Inventory_DW` databases.

- CommandTimeout = 1 hour on all SQL partitions
- `DemandForecastSnapshot` filtered to latest snapshot (`MAX(dtea)`) — point-in-time extract
- `DemandInventorySnapshot` filtered to latest snapshot
- `ProductionCapacity` filtered to latest Monday snapshot

---

## §5 — Grain & snapshot strategy

**Primary grain:** Item × Warehouse × Fiscal Month (spread to Fiscal Week) × DataType (RSLF / PROL / FUTO)

**Production-aligned grain:** Item × ProdResourceId × LocationId × Fiscal Week (`VendorShipped` and `ProdCapacity` tables)

**Horizon:**
- **Forecast:** Latest snapshot only (`dtea = MAX(dtea)`) — no historical snapshots preserved, **no trend analysis possible**
- **Actual Demand:** `FiscalYearIndicator ≥ -1` (current + 1 prior year)
- **Vendor Shipped:** `FiscalWeekIndicator ≥ -18` (18 weeks back)
- **Production Capacity:** Latest Monday snapshot only — no historical

**Snapshot strategy:** **All tables are point-in-time (latest snapshot only).** No historical snapshot dimension exists. This means:
- Forecast accuracy trends cannot be calculated
- Capacity utilization trends cannot be calculated
- The model answers "what is the current outlook" not "how has our outlook changed over time"

The 56-day offset (`ETDWkLastDate`, `ETDWkEnding`, `ETAWkLastDate`) aligns forecast and actuals to an estimated time of departure (ETD) week rather than fiscal week — effectively shifting demand visibility 8 weeks earlier for production planning purposes.

---

## §6 — Dimensions used

| Dimension | Source | Notes |
|---|---|---|
| **Product (Item)** | **z_ProductDetails** (Dataflow via `CurrentProductDetails`) | Includes Series Number/Name, Item Class, Manufacturing Status, ABC codes. Re-derived `Series Desc`, `ItemSKU Desc`, `z_LeatherFlag` via DAX SWITCH |
| **Date (Fiscal)** | **z_FiscalCal** (Dataflow via `AshleyFiscalCalendarV2`) | 3+ active relationships to Fcast, ActDemand, ProdCapacity, VendorShipped columns + 6+ inactive relationships for ETD/ETA offsets. **`FiscalWeeksinMonth` is a hardcoded SWITCH column** |
| **Warehouse** | **z_WarehouseMaster** (Dataflow from `VendorMaster`) | Linked via `z_ItemWHProdResource[Warehouse]` |
| **Production Resource** | **z_ProdResourceMaster** (derived from `ProdCapacity`) | Enriched with `Prod Group` (Wanek 1/2/3, Millenium, Domestic) and `Resource Group` (~38 hardcoded ResourceID-to-group mappings) via DAX SWITCH |
| **Vendor / Production Location** | Embedded in SQL filters + `VendorShipped` via LocationID | 4 fixed IDs: 900515 (Wanek 1), 900639 (Wanek 2), 600039 (Wanek 3), 624556 (Millenium) — hardcoded |
| **Planning Vendor** | `DemandInventorySnapshot.dinInvPlanningVendor` | Filtered to same 4 IDs + `dinMakeBuyCode = 'M'` |

### Notable re-derived attributes

| Attribute | Source | Drift risk |
|---|---|---|
| **`z_LeatherFlag`** | SWITCH on Item Class Code — 10 leather classes + 3 UN classes mapped to "LTHR FG", "LTHR UN", "" | If new leather class codes are added, this SWITCH silently returns blank — items disappear from leather filters |
| **`Prod Group`** | SWITCH on LocationID — 5 values | Adding a new WNK plant (e.g. Wanek 4) requires DAX edit |
| **`Resource Group`** | SWITCH with ~38 hardcoded ResourceID → Group mappings | Every new production line requires model edit |
| **`FiscalWeeksinMonth`** | Hardcoded SWITCH on Fiscal Year Month Num | Only special-cases FiscalMonth 202212 (6 weeks) and months 3/6/9/12 (5 weeks). If Ashley changes fiscal calendar, this breaks silently. If a fiscal month outside this pattern has a different week count, the hardcode misses it |

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| **10 auto-generated LocalDateTables** | One per date column. All identical structure (Year, MonthNo, Month, QuarterNo, Quarter, Day). Could collapse to one shared date table with role-playing relationships |
| **56-day offset in 3 places** | `DATEADD(DAY, -56, ...)` appears in Fcast SQL, ActDemand calculated column, and VendorShipped SQL. The offset is the same (8 weeks) but computed independently in three locations — if the lead time assumption changes, all three must be updated |
| **Same 4 vendor IDs hardcoded in 5+ SQL WHERE clauses** | The vendor filter `('900515','600039','624556','900639') OR MakeBuy='M'` appears in Fcast (×3 UNION branches), ActDemand (×1), z_ItemWHProdResource (×1), and ProdCapacity (×1). No shared parameter or lookup table |
| **Fcast table uses 3-branch UNION** (RSLF / PROL / FUTO) — same source table, same joins, same filter, only the aggregated column and datatype change. Could collapse to a PIVOT or UNPIVOT pattern |
| **VendorShipped uses 4-branch UNION** — one per LocationId, each slightly different (different IMHIST database for MIL, different HOUSE filters for WNK). Four near-identical queries parameterized by LocationId/HOUSE |
| **`_Measures` table is a dummy row container** | Single `{{1}}` row — valid pattern but measure discovery requires knowing to look in a table named `_Measures` |
| **`z_ProdResourceMaster` derived from ProdCapacity, then enriched with 2 SWITCH columns** — the base table is a `Table.Distinct(Table.SelectColumns(ProdCapacity, {"ResourceID","LocationID"}))`. SWITCH columns should be in a governed dimension, not DAX-calculated |

---

## §8 — Open questions

1. **Who uses this report and how often?** No usage metadata. The 16-week forward horizon + capacity alignment suggests weekly production planning WBR.

2. **What does `FcstAverageWeekly / 17` actually represent?** The 17 denominator for a 16-week window is either a fencepost fix or a bug. Need business confirmation.

3. **Is the 56-day (8-week) lead time offset validated?** This constant drives the ETD alignment for all three major tables. If actual lead times vary by item or supplier, the uniform 56-day assumption introduces systematic bias.

4. **Does the ProdCapacity `GREATEST` formula overstate available capacity?** Taking `MAX(Firm+Planned, TotalAvailHours)` means capacity is never below planned usage — could this mask chronic over-scheduling? Do planners have a separate view of raw available hours?

5. **Is the UN Kit traceback (the `KS` BOMView subquery) still accurate?** The UN Kit logic traces through BOMView where `RIGHT(components, 2) = 'UN'`. If BOM structures change or new kit types (e.g. 'KT') are introduced, this filter misses them.

6. **Are the 38 ResourceGroup mappings maintained?** Every new line added to a WNK/MILL plant requires editing a SWITCH calculated column. Who does this and how often?

7. **Is the `z_LeatherFlag` still current?** 10 leather class codes hardcoded. If Ashley adds a new leather classification this filter silently drops those items from any leather-specific visual.

8. **What is the `FUTO` (future order) datatype used for vs `RSLF`?** FUTO loads from `dfcOrderFutureQty`. Is this a Logility-specific future-order bucket or does it overlap with the Resultant forecast? The report has no measure explicitly filtering FUTO.

---

## §9 — Business assumptions / magic numbers

### 9.1 — 56-day (8-week) lead time offset

```
Fcast:      DATEADD(DAY, -56, FiscalWeekLastDate) → ETDWkLastDate
ActDemand:  DATEADD(DAY, -56, CurReqWkEnding)    → ETDWkEnding
VendorShp:  DATEADD(DAY, +56, FiscalWeekLastDate) → ETAWkLastDate
```

The same 56-day offset appears in three places, forward and backward. No documentation of where 8 weeks comes from — likely the average ocean transit + inland lead time from Asia (WNK/MILL factories) to US warehouses. If actual lead time varies by item (e.g. expedited air vs standard ocean vs vessel schedule changes), the constant uniform offset adds noise to all ETD-aligned metrics.

### 9.2 — FcstAverageWeekly divided by 17

```
DIVIDE(CALCULATE([ETD Fcast], FiscalWeekIndicator > 0 AND <= 16), 17)
```

16 weeks of data, divide by 17. No documentation. If the intended function is "average over the next N weeks starting from next week," the denominator should be 16 (or 15 if the current partial week is excluded). The +1 suggests either:
- A fencepost issue (weeks 1 inclusive through 16 inclusive = 16 values, but developer counted 1→16 = 17)
- An attempt to include week 0 in an unrolled context
- A bug

### 9.3 — FiscalWeeksinMonth hardcoded SWITCH (DAX calculated column)

```
SWITCH(z_FiscalCal[Fiscal Year Month Num],
  202212, 6,
  SWITCH(z_FiscalCal[Fiscal Month Num],
    3, 5, 6, 5, 9, 5, 12, 5, 4
  )
)
```

Only special-cases FYM 202212 (6 weeks) and months 3,6,9,12 (5 weeks). All others default to 4. If Ashley changes fiscal calendar structure, this breaks. Used in `Act+Fcast Weekly Qty` = `DIVIDE([Act+Fcast], [FiscalWeeksinMonth])` — so if the week count for a given month is wrong, the per-week quantity is systemically biased.

### 9.4 — ProdCapacity `GREATEST(Firm+Planned, TotalAvailHours)`

```sql
SUM(GREATEST(([PC].[FirmHours] + [PC].[PlannedHours]), [PC].[TotalAvailHours])) AS [TotalAvailHours]
```

By construction, `Prod Capacity` is **never less than Firm+Planned hours**. This means capacity utilization can never exceed 100% in this model, because capacity is defined as `MAX(scheduled, actual_capacity)`. To see true utilization, a user would need a separate measure using the raw `TotalAvailHours` without GREATEST — which does not exist.

### 9.5 — 4 fixed vendor/production location IDs

Hardcoded in 5+ SQL WHERE clauses and the `Prod Group` SWITCH:
- `'900515'` = Wanek 1
- `'900639'` = Wanek 2
- `'600039'` = Wanek 3
- `'624556'` = Millenium

Adding a new WNK plant or replacing a vendor requires editing every SQL partition and the DAX SWITCH. No lookup table.

### 9.6 — VendorShipped HOUSE filter codes hardcoded

```sql
-- Wanek 1: IMHIST.HOUSE = '31'
-- Wanek 2: IMHIST.HOUSE = '33'
-- Wanek 3: IMHIST.HOUSE = '35'
-- Millenium: no HOUSE filter (different table Manufacturing_Inventory_MIL.IMHIST)
```

These are Ashley's internal WNK inventory structure codes (HOUSE 31/33/35). If WNK restructures inventory organization, shipped quantities disappear from the model silently.

### 9.7 — z_ProdResourceMaster `Resource Group` SWITCH with ~38 hardcoded mappings

Each line in the DAX maps a ResourceID string to a group label (e.g. "900515-1010", "Frame Cell"). Adding a new line requires editing the SWITCH. No lookup table, no governed source. The fallback is the raw ResourceID string — so unmapped resources still appear but ungrouped.

### 9.8 — z_ProductDetails `z_LeatherFlag` SWITCH with 10 hardcoded class codes

```
"ZMLH","ZMLM","ZMLR","ZMMS","ZMMU","ZXLH","ZXLM","ZXLR","ZXMS","ZXMU" → "LTHR FG"
"ZMLK","ZXLK","ZXMK" → "LTHR UN"
```

If Ashley adds a new leather class code (e.g. "ZMLN"), items with that code are silently excluded from leather FG/UN classification.

### 9.9 — ActDemand time window: FiscalYearIndicator ≥ −1

This means only current fiscal year + 1 prior year are loaded into the model. Older actuals are excluded. If a user filters to a date older than FY-1, `Act - Invoiced` and `Act - Open Ord` return blank.

### 9.10 — VendorShipped lookback: FiscalWeekIndicator ≥ −18

Only 18 weeks of IMHIST shipped data are loaded. A user comparing vendor shipped quantities against forecast for periods older than ~4.5 months will see blank.

### 9.11 — Does this report calculate dollar-value business impact?

**No explicit dollar-value formula exists.** The report operates entirely at the volume (unit) and capacity (hours) level. No margin, cost, or revenue multipliers are applied. Financial impact (e.g. "cost of under-capacity = lost sales × margin") would need to be calculated externally.

---

## §10 — Comparability / consistency

### 10.1 — Same 56-day offset applied as both forward and backward shift (inconsistent semantics)

- `Fcast[ETDWkLastDate]` = `FiscalWeekLastDate - 56 days` — moves the forecast backwards in time to represent "when the order needed to be in production"
- `VendorShipped[ETAWkLastDate]` = `FiscalWeekLastDate + 56 days` — moves the shipped quantity forward in time to represent "when the goods are expected to arrive"

Both use the same 56 constant but in opposite directions. Conceptually sound (one aligns to production schedule, one to receipt) but internally inconsistent for cross-referencing. If you compare Fcast ETD vs VendorShipped ETA without careful context, the 112-day gap between them (56 back + 56 forward) could be misinterpreted.

### 10.2 — ActDemand uses `FiscalYearIndicator ≥ −1`; VendorShipped uses `FiscalWeekIndicator ≥ −18`

These two temporal windows do not align. `FiscalYearIndicator` is a year-level boundary (−1 = previous fiscal year); `FiscalWeekIndicator` is a week-level boundary (−18 = 18 weeks back). For a week at week −20: ActDemand includes it (still within prior fiscal year), but VendorShipped excludes it (before week −18). Act+Fcast and Vendor Shipped for the same period may reference different date ranges.

### 10.3 — Three different date alignment strategies across tables

| Table | Date anchor | Offset |
|---|---|---|
| Fcast (forecast) | FiscalMonthLastDate → spread to FiscalWeekLastDate | −56 days → ETDWkLastDate |
| ActDemand (actuals) | CurReqWkEnding | −56 days → ETDWkEnding |
| VendorShipped (vendor ship) | FiscalWeekLastDate (ship week) | +56 days → ETAWkLastDate |

Fcast and ActDemand both use −56, so they align at the ETD level. But VendorShipped uses +56, placing it at the opposite end of the 112-day supply pipeline. A planner comparing `ETD Fcast` with `ETA Vendor Shipped` on the same timeline is comparing forecasts at week T with receipts at week T+16 (8 weeks out × 2).

### 10.4 — `FiscalWeeksinMonth` uses a single fiscal month constant for all years except 202212

Only Fiscal Year Month 202212 (December 2022) has a special 6-week entry. All other years' December uses the default 4 weeks (via the fallback SWITCH that checks month 12 = 5). This means if the December 2023 fiscal month also has 6 weeks, it is incorrectly counted as 5. The `202212` hardcode was not made relative (e.g. month=12 + year=any → check dynamic week count).

### 10.5 — `Prod Capacity` uses the latest Monday snapshot only

```sql
WHERE [PC].[Snapshotdate] = (SELECT MAX([SnapshotDate]) FROM ProductionCapacity WHERE DATENAME(WEEKDAY, [Snapshotdate]) = 'MONDAY')
```

Only the most recent Monday snapshot is loaded. If production capacity was adjusted mid-week or the latest Monday snapshot failed to generate, the capacity data reflects a stale or missing snapshot until the next Monday.

### 10.6 — `Act+Fcast` fiscal boundary may double-count or gap at month 0

`CALCULATE(SUM(ActDemand[Order Qty]), FiscalMonthIndicator < 0)` selects all actuals from fiscal months with indicator < 0 (past months). Then adds `Fcast - Result + Fcast - Promo` (all months, including month 0 and future). If any demand exists for fiscal month indicator = 0 (current month), it exists in Fcast but NOT in ActDemand. If the report is viewed mid-month, current month shows forecast-only numbers — correct. But if month 0 actuals exist and are not backfilled before the forecast loads, the user sees forecast numbers that may exceed reality.

### 10.7 — No RLS means all planners see all production resources

A Wanek 1 production planner can see Millenium's forecast loads and vice versa. While this may be intentional for cross-plant coverage, it means no data isolation between manufacturing locations.

---

## Closing — Interview seeds

**1. On the /17 denominator and the 56-day offset:**
> "The average weekly forecast divides by 17 for a 16-week window — is that intentional so the average includes the current partial week, or should it be 16? And the 56-day lead time offset — is that from a specific study of ocean transit to your warehouses, or is it a rule of thumb that gets adjusted periodically?"

**2. On production capacity:**
> "The capacity measure takes the higher of 'firm+planned hours' and 'available hours' — which means capacity can never show less than what's been scheduled. When you look at a production line and see it 'at capacity,' are you confident that's actual available hours, or could it be masking over-scheduling?"

**3. On the sourcing traceback:**
> "The model traces each item to a production resource through a three-way make/buy/transfer logic. Have you ever found an item that shows up under the wrong plant or resource in this report, and if so, where did the data disconnect?"

**4. On trust and decision-making:**
> "This report gives you a forward-looking view of production load vs capacity at each WNK/MILL line. When you see a line projected over capacity in week 12 — what concrete action do you take, and has the report's projection ever been wrong enough that you over-ordered or under-prepared?"
