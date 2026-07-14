# Amazon POS Sales and Forecast — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | SCP Team (`29ff4afb-7e3c-4218-9cc9-cd4e14e09551`) |
| **Report Name** | Amazon POS Sales and Forecast |
| **Backing Model** | Amazon POS Sales and Forecast (`c7bb4952-f773-4f39-8906-127a47755d0d`) |
| **Model Size** | 12 tables (7 user + 1 hidden + 4 auto-date), 7 measures, 12 relationships, 0 RLS roles |
| **Analyzed** | 2026-07-07 |

---

## §1 — Supply-chain question & chain link

**Question:** What is the Amazon channel's actual POS sell-through, on-hand inventory, open purchase orders, and Amazon's own demand forecast — and how does Ashley's wholesale sell-in to Amazon compare against Amazon's POS consumption?

| Link | How served |
|---|---|
| **Demand** (primary) | Amazon's actual POS (Point-of-Sale) units and revenue from `AmazonCustomerPOS` — what consumers are actually buying through Amazon |
| **Demand — Amazon Forecast** | Amazon's own demand forecast from `AmazonCustomerForecast` — what Amazon projects it will need (drives Amazon's PO to Ashley) |
| **Inventory** | Amazon's on-hand inventory snapshot (`Sellable On-Hand QTY`, `90+ Day Inv`, `Open PO QTY`) from `AmazonCustomerInventory` — what stock Amazon currently holds and has on order |
| **Demand — Ashley Wholesale** | Ashley's actual sell-in to Amazon (`AFI Order Qty` vs `AFI Order Amt`) from `ActualsCustItemWH_AFI` filtered to Amazon customer accounts `3352200` and `3559000` — what Ashley shipped to Amazon |

> ⚠️ **Critical structural observation:** The model compares Amazon POS (sell-through) with Ashley wholesale sell-in (ship-to-Amazon), but there is **no cross-reference against Ashley's internal demand forecast**. The model answers "Amazon POS vs Amazon Forecast vs Amazon Inventory vs Ashley Wholesale" — not "Are Ashley's planners forecasting Amazon correctly."

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Is Amazon's POS running ahead of or behind its own forecast? Identify items where Amazon will need more stock | Analyst / Demand Planner | Weekly | **Operational** |
| Is Amazon's on-hand inventory + open PO sufficient to cover forecasted demand? Identify stockout risk at Amazon | Analyst / Supply Planner | Weekly | **Operational** |
| Is Ashley wholesale sell-in aligned with Amazon's consumption? Stop over-shipping or escalate if under-shipping | Demand Planner | Weekly | **Operational** |
| Which items have >90-day inventory aging at Amazon? Trigger markdown, return, or inventory rotation | Inventory Analyst | Monthly | **Operational** |
| What is the ratio of Amazon's POS to Ashley's wholesale sell-in? Inform replenishment cadence | Planner / Manager | Monthly | **Performance / Governance** |
| Are Amazon's forecasts for specific SKUs consistently off from actual POS? Flag for Amazon vendor account team to renegotiate forecast data sharing | Supply Chain Manager | Quarterly | **Financial-Justification** |

---

## §3 — Key metrics / measures

**7 measures total** — all in `_Measures` table. Every measure is a simple `CALCULATE(SUM(...))` with a single filter or a measure-to-measure sum.

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| **POS Qty** | Amazon Point-of-Sale units sold (consumer purchases out of Amazon inventory) | Item × Week | `CALCULATE(SUM(AMZNPOS[POS QTY]))` — source column: `OrderedUnits` |
| **FC Qty** | Amazon's own forward-looking demand forecast (units) | Item × Week | `CALCULATE(SUM(AMZNFC[FC QTY]))` — latest snapshot only, `MAX(SourceFoldersDate)` |
| **POS + FC Qty** | Combined actual POS + Amazon forecast (used for total demand view) | Item × Week | `[POS Qty] + [FC Qty]` |
| **Sellable On-Hand Inv** | Amazon's current sellable on-hand inventory (units) | Item × Week | `CALCULATE(SUM(AMZNInv[Sellable On-Hand QTY]))` |
| **Open PO Qty** | Amazon's open purchase orders (units), i.e. what Amazon has on order from vendors | Item × Week | `CALCULATE(SUM(AMZNInv[Open PO QTY]))` |
| **90+ Day Inventory** | Amazon inventory aged 90+ days (units) — slow-moving / at-risk stock | Item × Week | `CALCULATE(SUM(AMZNInv[90+ Day Inv]))` |
| **AFI Order Qty** | Ashley's wholesale sell-in quantity to Amazon (units shipped) | Item × WH × Week × Status × SalesType | `CALCULATE(SUM(AMZNWholesale[Wholesale Qty]))` — sourced from `ActualsCustItemWH_AFI`, filtered to Amazon accounts `3352200`, `3559000` |

### No complex or suspicious measures found

> ✅ **No hardcoded per-warehouse measures.** No per-marketplace duplicates. All 7 measures are architecturally clean — simple aggregates with transparent naming.

> ✅ **All measures compute correctly.** Basic `SUM` and `+` — no risk of wrong constants, no disguised hardcoded values, no overly complex DAX.

> ⚠️ **No inventory coverage measure exists.** There is no measure combining `Sellable On-Hand Inv + Open PO Qty - POS Qty` to show weeks of supply at Amazon. This calculation must be done manually by the user.

> ⚠️ **No "gap to forecast" measure.** `FC Qty` and `POS Qty` can be compared side-by-side, but no DAX computes `ABS(FC - POS)`, `(FC - POS)/FC`, or any accuracy metric. Accuracy assessment is left to the visual-level analysis.

---

## §4 — Data sources & lineage

| Source | Type | Flag |
|---|---|---|
| **SupplyChain_Enh.AmazonCustomerPOS** | Azure SQL (`ashley-edw / ashley_edw`) | ✅ Governed |
| **SupplyChain_Enh.AmazonCustomerInventory** | Azure SQL | ✅ Governed |
| **SupplyChain_Enh.AmazonCustomerForecast** | Azure SQL | ✅ Governed |
| **SupplyChain_Enh.ActualsCustItemWH_AFI** | Azure SQL | ✅ Governed |
| **Enterprise_DW.DimDate** | Azure SQL (used in AMZNWholesale SQL join) | ✅ Governed |
| **AFISales_DW.DimCustomers** | Azure SQL (used to filter Amazon accounts) | ✅ Governed |
| **z_ProductMaster** (via PBI Dataflow `CurrentProductDetails`) | Dataflow | ✅ Governed (from EDW upstream) |
| **z_DimDate** (via PBI Dataflow `AshleyFiscalCalendarV2`) | Dataflow | ✅ Governed |

> ✅ **No Amazon API connector.** All Amazon data is ingested into Azure SQL (`SupplyChain_Enh` schema) by a separate ETL process upstream — the model never calls Amazon directly.

> ✅ **No SharePoint, no Excel, no manual CSV files.**

### Dataflow references
All dataflow-sourced tables from same source:
- Workspace: `a47e4573-c455-40af-a9ad-e22c81a07926`
- Dataflow: `346f2aa1-dd50-4c11-9630-b17f75854663`
- Entities: `AshleyFiscalCalendarV2`, `CurrentProductDetails`

### Key Sourcing Notes

**Amazon Forecast:** Only the latest `SourceFoldersDate` snapshot is loaded (`WHERE SourceFoldersDate = (SELECT MAX(SourceFoldersDate) FROM AmazonCustomerForecast)`). No historical forecast snapshots.

**Amazon Wholesale:** Filtered to Ashley customer accounts `3352200` and `3559000` (hardcoded in SQL WHERE clause). `FiscalMonthIndicator >= -18` = only the last 18 fiscal months of wholesale data.

**Amazon Inventory:** All available snapshots loaded (no `MAX` filter). Multiple week-endings may contain overlapping snapshots.

---

## §5 — Grain & snapshot strategy

**Primary grain:** Item SKU × Week Ending (all three Amazon tables)

**Amazon POS & Inventory:** All historical weekly snapshots available in source — trend analysis possible.

**Amazon Forecast:** Latest snapshot only (`MAX(SourceFoldersDate)`) — **no trend/accuracy analysis possible against prior forecasts**. The forecast is a point-in-time view.

**Amazon Wholesale (AFI):** `FiscalMonthIndicator >= -18` — 18 months of history retained.

**Snapshot strategy:**
- **Amazon POS/Inv** = historical snapshot series (weekly). Multiple weeks available for trend comparison.
- **Amazon FC** = latest snapshot only. If forecast accuracy tracking is needed over time, this model cannot support it.
- **Ashley Wholesale** = transactional history, grouped to weekly grain.

### Date alignment
All four fact tables link to `z_DimDate` via `WeekEnding` / `CurReqWkEnding` — Ashley fiscal calendar (dataflow). Amazon's week-ending dates are assumed to align with Ashley fiscal weeks. Any misalignment (Amazon weeks ending on different days) causes date drift that is invisible in the model.

---

## §6 — Dimensions used

| Dimension | Source | Notes |
|---|---|---|
| **Product (Item)** | `z_ProductMaster` — Dataflow `CurrentProductDetails` (91+ columns) | `z_ItemFilter` calculated column marks items that have POS data (`ISNUMBER(SUM(AMZNPOS[POS QTY]))`) — used to filter the product list to Amazon-active items |
| **Date (Fiscal)** | `z_DimDate` — Dataflow `AshleyFiscalCalendarV2` (43+ columns) | Standard Ashley fiscal calendar. `z_DataRange` calculated column returns TRUE for dates within [earliest wholesale date, latest Amazon FC date] — used as a visual-level date filter |
| **Warehouse** | Embedded in `AMZNWholesale[Warehouse]` | **No standalone Warehouse dimension.** Amazon inventory is at the Amazon FC level, not Ashley warehouses |
| **Customer** | Embedded in `AMZNWholesale` SQL filter only | Customers filtered to `3352200` and `3559000` in SQL. No customer dimension in the model — if Amazon has sub-accounts, they are not visible |
| **Sales Type / Status** | Embedded in `AMZNWholesale` fact | Dimension attributes on the wholesale fact, no standalone dimension tables |

### Notable re-derived attributes

| Attribute | Source | Drift risk |
|---|---|---|
| **`z_ItemFilter`** | Calculated column: `ISNUMBER(CALCULATE(SUM(AMZNPOS[POS QTY])))` | Returns TRUE if an item has any POS data. But this is a static column computed at model refresh. If a new item receives POS data mid-cycle, `z_ItemFilter` is correct only after the next refresh. |
| **`z_DataRange`** | Calculated column: `FiscalWeekEnd >= MIN(Wholesale[CurReqWkEnding]) AND FiscalWeekEnd <= MAX(FC[WeekEnding])` | Sets the date window from earliest wholesale record to latest forecast record. Since `MIN/MAX` are computed table-wide (not per-item), the window is global — may include/exclude dates incorrectly for items with different date ranges. |

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| **4 auto-generated LocalDateTables** | One per date-valued column on Product Master. All identical structure (Year → Month → Quarter → Day). Could be replaced by a single shared date table with role-playing relationships |
| **`z_ItemFilter` and `z_DataRange` are table-wide calculated columns** | Both use `MIN/MAX/SUM` without per-item filter context. They are global flags applied to entire tables, which may be inaccurate if item date ranges vary |
| **AMI (Amazon) data is in 3 separate tables (POS, Inv, FC)** | Could be consolidated into a single "Amazon Data" table with a Data Type dimension (POS / Inv / FC), reducing relationships from 12 to ~6 |
| **Amazon Wholesale vs Amazon POS are separate tables with no shared relationship** beyond Product Master and Date. No view collapses "Amazon total demand = POS + wholesale" despite `POS + FC Qty` measure existing |

---

## §8 — Open questions

1. **Who ingests the Amazon data into `SupplyChain_Enh.AmazonCustomer*`?** The model relies entirely on an upstream process that loads Amazon data into Azure SQL. Is this a daily/weekly batch, an API call, or a manual export? If the pipeline breaks, the report silently shows stale data.

2. **Are Amazon's week-ending dates aligned with Ashley fiscal calendar?** The model joins Amazon `WeekEnding` to Ashley `z_DimDate[Transaction Date]`. If Amazon's week end differs from Ashley's (e.g. Amazon uses Sunday vs Ashley uses Saturday), some data shifts by 1 day.

3. **What is the `SourceFoldersDate` in `AmazonCustomerForecast`?** The forecast table filters to `MAX(SourceFoldersDate)` — is this the date Amazon published the forecast, the date Ashley's ETL downloaded it, or something else?

4. **Who uses this report and how often?** No usage metadata. Amazon account managers reviewing forecast vs sell-through weekly is the most likely use case.

5. **Does this report still answer the right question?** There is no Ashley-internal forecast in the model. If the original intent was "compare Ashley's forecast of Amazon demand vs Amazon's actual POS," this model is incomplete for that purpose.

6. **Are the Amazon account numbers `3352200` and `3559000` still valid?** These are hardcoded in the AMZNWholesale SQL. If Amazon restructures its account setup, wholesale data stops being captured silently.

---

## §9 — Business assumptions / magic numbers

### 9.1 — `FiscalMonthIndicator >= -18` in AMZNWholesale SQL

```sql
AND [DD].[FiscalMonthIndicator] >= -18
```

Hardcoded 18-month lookback window for wholesale (Ashley sell-in) data. No parameterization. If a user needs to review wholesale data older than 18 months, it is not available. No documentation of why 18 months (common standard for fiscal year + 6 prior months, but not stated).

### 9.2 — Customer account numbers hardcoded in SQL

```sql
AND [DC].[Customer Account Number] IN ('3352200','3559000')
```

Two hardcoded Amazon wholesale customer account numbers. If Amazon adds a new buying account or restructures existing ones, this filter must be updated via SQL edit and model republish. No parameter, no lookup table.

### 9.3 — Amazon Forecast: latest snapshot only (no versioning)

```sql
WHERE AFC.[SourceFoldersDate] = (SELECT MAX([SourceFoldersDate]) FROM ...)
```

The forecast is always the most recent available snapshot. All prior forecasts are discarded. This means: if the latest forecast was published while Amazon was mid-month (with incomplete data), the forecast may show lower/higher values than the previous complete forecast. No way to compare "forecast as of last week" vs "forecast as of this week."

### 9.4 — All numeric NULLs defaulted to zero

```sql
ISNULL(POS.[OrderedRevenue], 0) AS [POS Revenue]
-- and 8 more ISNULLs across AMZNPOS, AMZNInv, and AMZNWholesale
```

NULL numeric values are replaced with 0 at the SQL level. This means a week with no POS data and a week with zero POS data are indistinguishable. If the `AmazonCustomerPOS` table has a gap (e.g. missing batch upload for one week), that week shows 0 sales — the same as a genuine zero-selling week.

### 9.5 — `z_DataRange` uses table-wide MIN/MAX

```dax
VAR POSStart = MIN(AMZNWholesale[CurReqWkEnding])
VAR FCEnd = MAX('AMZNFC'[WeekEnding])
```

The date range window is computed once per table refresh — not per item. Items with data starting later or ending earlier than the global extremes still appear within the range, creating visual rows with no data for portions of the timeline.

### 9.6 — `z_ItemFilter` uses `ISNUMBER` not `> 0`

```dax
ISNUMBER(CALCULATE(SUM(AMZNPOS[POS QTY])))
```

An item with exactly 0 total POS passes the filter (0 IS a number). An item with NULL total POS fails the filter (SUM returns BLANK, ISNUMBER(BLANK) = FALSE). This means items with zero aggregate POS are included in the product list — they appear in visuals with zero across all metrics, which may be intended or may be noise.

### 9.7 — Does this report calculate dollar-value business impact?

**No.** There is no dollar-value business impact formula. The model contains `AFI Order Amt` (wholesale order amount) and `POS Revenue` / `Shipped Revenue` columns in their respective tables, but **no DAX measure references any dollar column**. All 7 measures are unit-based only. Financial impact analysis must be done externally.

---

## §10 — Comparability / consistency

### 10.1 — Amazon Forecast (FC Qty) is latest snapshot; Amazon POS is historical series

`FC Qty` returns only the most recent forecast row per item-week. `POS Qty` returns all historical weeks. A chart showing both on the same timeline will show POS values for all months but forecast values only for the latest snapshot window — a user filtering to last year's dates will see POS but blank forecst.

### 10.2 — Amazon Inventory data frequency unknown

`AMZNInv` loads all rows from `AmazonCustomerInventory` without date-filtering. Multiple snapshots per week may exist (e.g. if Amazon refreshes inventory daily). No dedup strategy visible. If multiple rows share the same `WeekEnding` for the same `ItemSKU`, measures like `SUM(Sellable On-Hand QTY)` will double-count inventory.

### 10.3 — `POS + FC Qty` double-counts overlapping periods

```dax
[POS Qty] + [FC Qty]
```

If both `POS Qty` and `FC Qty` have data for the same week (e.g. the current transition week where POS exists through last Friday and the forecast starts from this Monday), the two are summed — creating a single inflated number for that week. There is no logic to handle the transition boundary (e.g. `IF POS exists, use POS + future FC`).

### 10.4 — Amazon Wholesale (AFI) uses CurReqWkEnding, Amazon uses WeekEnding

`AMZNWholesale` joins on `CurReqWkEnding` (Ashley's customer requested ship week). `AMZNPOS`, `AMZNInv`, and `AMZNFC` join on `WeekEnding` (Amazon's own week-ending date). These are **two different week definitions** — Ashley's and Amazon's fiscal calendars may disagree. A visual plotting both `AFI Order Qty` and `POS Qty` on the same x-axis is implicitly comparing two different weekly time scales.

### 10.5 — `90+ Day Inv` is raw cumulative value, not a rate

`90+ Day Inventory` shows absolute units aged 90+ days. No measure divides this by total sellable inventory to show the "aged percentage" — so a large number may be the result of a large total inventory position, not a systematic aging problem.

### 10.6 — No RLS — all users see all Amazon and wholesale data

No Row-Level Security. Any user with access to this report can see POS data, inventory aging, and wholesale unit volumes for all items. Sensitive Amazon account data is not isolated.

---

## Closing — Interview seeds

**1. On the gap to Ashley's internal forecast:**
> "I notice this model doesn't include Ashley's own demand forecast for Amazon — it only uses Amazon's forecast. When you plan what to ship to Amazon, do you use Amazon's forecast numbers directly, or do you compare them against Ashley's internal planning system? And if the two disagree, which one do you trust?"

**2. On the Amazon week alignment:**
> "Amazon's data comes in with its own week-ending dates. We join those to Ashley's fiscal calendar. Have you ever noticed a week where POS numbers look like they shifted by a week — for example around month-end or quarter-end?"

**3. On the aging and overstock risk:**
> "The report shows 90+ day inventory at Amazon in absolute units. When you see an item with high aged inventory, what's the escalation path — does Ashley arrange a return, mark down through Amazon, or just write it off? And do you trust that the 90+ day number from Amazon accurately reflects only slow-moving stock?"

**4. On the Amazon data pipeline:**
> "The Amazon data in this report is loaded into Ashley's EDW from an external pipeline I can't see from here. If you're reviewing the numbers and something looks off, how quickly would you know it's a data pipeline issue versus an actual business trend — and do you have a way to check the raw Amazon data directly?"
