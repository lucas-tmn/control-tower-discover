# On Time % by Customer — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `91c7052d-6817-4721-958e-b99ec39f19ba`  
**Report ID:** `895229b4-b703-4a8a-9b0e-54f487fc24fb`  
**Analysis Date:** 2026-07-08  
**Model Size:** ~1.10 MB (BIM); 6 tables, 19 DAX measures total

---

## 1. Supply-Chain Question & Chain Link

**Question the report answers:**  
> "For each customer group and item, how reliably do our shipments meet the original request date, original promise date, current request date, and current promise date — measured at both week-level and day-level accuracy?"

**Primary chain links served:** **On-Time** (Delivery performance)  
This is the only report in the family focused purely on on-time delivery (OTD) performance. It tracks whether shipments arrive when promised at two levels of temporal precision (week vs. day) and against four reference dates (original request, original promise, current request, current promise).

Secondary links touched:
- **Inventory** — WH335OnTime provides on-time metrics specifically for warehouse 335 (a specific DC)
- **Demand** — the `Shipped Quantity` denominator doubles as a demand fulfillment metric

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Identify customers / items / warehouses with chronically low OT%** — drill into which account–warehouse combinations consistently miss original promise date | Customer Service Manager / Supply Chain Manager | Weekly | Performance/Governance |
| **Compare week-level vs day-level OT%** — large gap reveals cases where shipments arrive in the promised week but not the promised day; manage customer expectations accordingly | Customer Service / Account Manager | Monthly | Operational |
| **Monitor WH335 (specific DC) performance separately** — `WH335OnTime` table provides Request and Promise OT% for this warehouse only, using a different methodology | Warehouse Ops Manager | Weekly | Operational |
| **Evaluate which on-time definition to apply per customer** — `Total On-Time % - Original Promise Wk` vs `Current Promise Day` etc.; each account agreement references a different promise date definition | Customer Service / Account Manager | Monthly | Performance/Governance |
| **Track OT% by DSG (Dick's Sporting Goods) accounts** — 16 specific account numbers are hardcoded into a `Customer` column as "DSG - All Accounts" — an intentional DSG rollup for this retail customer | Dedicated Account Manager | Weekly | Operational/Performance |

**Primary persona:** Customer Service Manager / Account Manager — the report answers "are we keeping our delivery promises to this customer?"

---

## 3. Key Metrics / Measures

### On-Time % — Week-Level (`On Time (week)` table)

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Total Shipped Quantity` | Total units shipped | Cust × Item × WH × fiscal week × order type | `SUM('On Time (week)'[Shipped Quantity])` — from `AFISales_Enh.OnTimeDeliveryDetail.otdShippedQuantity` |
| `Total On-Time % - Original Promise Wk` | % shipped in or before the week of original promise | Same | `DIVIDE(SUM(Qty On Time - Orig Promise Week), [Total Shipped Quantity])` |
| `Total On-Time % - Current Promise Wk` | % shipped in or before the week of latest promise | Same | `DIVIDE(SUM(Qty On Time - Cur Promise Week), [Total Shipped Quantity])` |
| `Total On-Time % - Original Request Wk` | % shipped in or before the week of original request | Same | `DIVIDE(SUM(Qty On Time - Orig Request Week), [Total Shipped Quantity])` |
| `Total On-Time % - Current Request Wk` | % shipped in or before the week of current request | Same | `DIVIDE(SUM(Qty On Time - Cur Request Week), [Total Shipped Quantity])` |

### On-Time % — Day-Level (`On Time (day)` table)

| Measure | Business meaning | Grain | Source / Logic |
|---|---|---|---|
| `Total Shipped Qty` | Same as week-level | Same | Same source table, different SELECT columns |
| `Total On-Time % - Original Promise Day` | % shipped on or before the exact day of original promise | Same | `DIVIDE(SUM(Qty On Time - Orig Promise Day), [Total Shipped Qty])` |
| `Total On-Time % - Current Promise Day` | % shipped on or before the exact day of current promise | Same | Same pattern |
| `Total On-Time % - Original Request Day` | % shipped on or before the exact day of original request | Same | Same pattern |
| `Total On-Time % - Current Request Day` | % shipped on or before the exact day of current request | Same | Same pattern |
| `Total Avg Days - Original Promise Day` | Average days from original promise to delivery | Same | `DIVIDE(SUM(Orig Promise To Delivery), [Total Shipped Qty])` — delivery time is source hours/24 averaged across shipments |
| `Total Avg Days - Current Promise Day` | Average days from current promise to delivery | Same | Same pattern |
| `Total Avg Days - Original Request Day` | Average days from original request to delivery | Same | Same pattern |
| `Total Avg Days - Current Request Day` | Average days from current request to delivery | Same | Same pattern |

### Warehouse 335 Specific (`WH335OnTime` table)

| Measure | Grain | Source / Logic |
|---|---|---|
| `Total Inv Qty` | Cust × Item × WH335 × fiscal week | `SUM(WH335OnTime[Total Inv Qty (Req)])` |
| `On Time Req` | Same | `SUM(WH335OnTime[On Time Req Qty])` |
| `On Time Prom` | Same | `SUM(WH335OnTime[On Time Prom Qty])` |
| `On Time % - Requested` | Same | `DIVIDE([On Time Req], [Total Inv Qty])` — **uses Total Inv Qty based on Request as denominator** |
| `On Time % - Promised` | Same | `DIVIDE([On Time Prom], [Total Inv Qty])` — **⚠️ See §9: denominator is 'Req' total, not 'Prom' total** |

### Column-Level Calculated Fields

**`Customer` column (both `On Time (week)` and `On Time (day)`):**  
SWITCH mapping 16 hardcoded account numbers to `"DSG - All Accounts"` — Dick's Sporting Goods accounts. All other accounts get `Customer Name - Account Number` concatenation. This is the only customer rollup in the model — there is no systematic customer master join. (**⚠️ Identical SWITCH copy-pasted into both tables.**)

**`AshleyFiscalCalendar` table:**  
Loaded from the same dataflow as `z_FiscalCal` but from an older entity (`AshleyFiscalCalendar` vs `AshleyFiscalCalendarV2`). **Orphaned — no relationships, no measures reference it.** It appears to be dead weight in the model.

---

## 4. Data Sources & Lineage

### EDW / SQL (governed)

| Source | Table | Schema/Object | Notes |
|---|---|---|---|
| `ashley-edw.database.windows.net` / `ashley_edw` | `On Time (week)` | `AFISales_Enh.OnTimeDeliveryDetail` joined to `PowerBI_Wholesale.Customers` and `PowerBI_SupplyChain.CurrentProductDetails` and `Enterprise_DW.DimDate` | **3-hour CommandTimeout** (longest in any model); 55-week history; groups by week, customer, item, WH, order type. OT% computed at **week-level** using `otdQtyOnTimeOrigPromiseWeek` etc. |
| Same EDW | `On Time (day)` | Same sources | Same query structure; OT% computed at **day-level** using `otdQtyOnTimeOrigPromiseDay` etc. Delivery duration columns converted from hours to days (`/24`). |
| Same EDW | `WH335OnTime` | `Wholesale_SalesHistory_AFI.InvoiceDetail` + `Enterprise_DW.DimDate` + `AFISales_DW.DimCustomers` | Own SQL query — **PIVOT** of Request vs Promised status at week level; WH335 only; 9-month history. On-time defined as `InvoiceDate Week ≤ RequestDate Week` (or PromisedDelivery Week) — **not day-level**. |

### Power BI Dataflows (semi-governed)

| Dataflow | Tables | Notes |
|---|---|---|
| `a47e4573` workspace / `346f2aa1` dataflow | `z_ProductDetails`, `z_FiscalCal`, `AshleyFiscalCalendar` | `AshleyFiscalCalendar` from entity `AshleyFiscalCalendar` (older); `z_FiscalCal` from `AshleyFiscalCalendarV2` (newer). Both loaded but only `z_FiscalCal` is connected. |

**No SharePoint / Excel.** Fully EDW + dataflow.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Customer Account × Item SKU × Warehouse × Fiscal Week × Order Type 2

All OT% measures aggregate weekly shipped qty and on-time qty, computing the ratio at whatever dimension level the user filters to.

**Snapshot strategy:** **Latest only** — `On Time (week)` and `On Time (day)` retain a rolling 55 weeks of history (no snapshots, no versioning). `WH335OnTime` has ~9 months (FiscalMonthIndicator >= -9). This is appropriate for a performance tracking report — users compare current OT% to past OT% as a trend, not to multiple versions.

**No historical snapshots are needed** — the one "truth" per week per shipment is sufficient. Bringing multiple snapshot versions would add complexity with no clear value for this metric type.

---

## 6. Dimensions Used

| Dimension | Source | Notes |
|---|---|---|
| **Product / Item** | `z_ProductDetails` (dataflow) | Local modification: blank/space in `AFI Item Status` replaced with `'C'` (Current). This is the only model that modifies the dataflow output in Power Query. All three fact tables join to `z_ProductDetails[Item SKU]`. |
| **Date / Fiscal Calendar** | `z_FiscalCal` (dataflow → `AshleyFiscalCalendarV2`) | Used by all three fact tables. `FiscalWeekIndicator >= -55` for the main OTD tables; `FiscalMonthIndicator >= -9` for WH335. |
| **Warehouse** | Not a separate dimension table | Warehouse codes exist in the fact tables but there is **no `z_WarehouseMaster`** in this model. Any warehouse attribute (name, group, type) must come from the EDW join in the SQL, not from the conformed warehouse dimension. |
| **Customer** | No conformed dimension | `Customer Name`, `ABC Account-Current Year`, `Reporting Business Type` are brought in via SQL join to `PowerBI_Wholesale.Customers` — a different source than the `z_CustomerMaster_AFI` dataflow used in other models. No conformed customer master exists. The `Customer` SWITCH column is the only local classification (for DSG). |
| **AshleyFiscalCalendar** | **Orphaned table** | No relationships; no measures reference it. Loaded but unused. |

---

## 7. Duplication / Consolidation Signals

1. **`On Time (week)` and `On Time (day)` are structured identically:**  
   Both query the same `OnTimeDeliveryDetail` table with the same joins, filters, and grouping — only the OT% columns differ (`otdQtyOnTimeOrigPromiseWeek` vs `otdQtyOnTimeOrigPromiseDay`). The `Customer` SWITCH column is copy-pasted identically in both tables. These could be consolidated into a single table with a `Granularity` dimension (Week/Day).

2. **`Total Shipped Quantity` in `On Time (week)` and `Total Shipped Qty` in `On Time (day)` should be identical** but the DAX is in two separate measure tables. Any change to the shipping quantity definition would need to be updated in both places.

3. **The `Customer` SWITCH column has 16 hardcoded DSG account numbers — duplicated across both tables:**  
   If a DSG account number changes or a new one is added, both `On Time (week)` and `On Time (day)` must be updated. The same SWITCH exists in two copies.

4. **`AshleyFiscalCalendar` vs `z_FiscalCal` — two fiscal calendars loaded from the same dataflow:**  
   One is entity `AshleyFiscalCalendar`, the other is `AshleyFiscalCalendarV2`. `AshleyFiscalCalendar` is orphaned. This suggests a migration from V1 to V2 that left dead weight behind.

5. **`WH335OnTime` replicates OTD logic independently:**  
   Instead of filtering the main `OnTimeDeliveryDetail` table for warehouse 335, a completely separate SQL query (with PIVOT) was built. This query uses a different on-time definition (week-level InvoiceDate vs RequestDate/PromiseDate comparison) and a different source for customer attributes (`AFISales_DW.DimCustomers` vs `PowerBI_Wholesale.Customers`). The same metric from two different data pipelines will inevitably diverge.

6. **No `z_WarehouseMaster` dimension:** Unlike every other model in the SC Analytics workspace, the on-time models have no warehouse dimension table. Warehouse attributes (name, group, region) are unavailable for filtering unless they are joined in SQL sporadically.

---

## 8. Open Questions

1. **Why does `AshleyFiscalCalendar` still exist in the model?** It is loaded from the dataflow, has a full set of date attributes, but sits completely isolated — no relationships, no measures, no visual can reference it (unless used implicitly in a visual filter). Is it a remnant from a model revision that was never removed?

2. **Why is there no `z_WarehouseMaster` dimension?** Every other SC model has it. Without it, users cannot filter OT% by Warehouse Group, Site, or any warehouse attribute. Is this an intentional simplification or an oversight?

3. **What is warehouse 335?** A dedicated WH335OnTime table exists solely for this warehouse. Is 335 a major DC (e.g., a regional distribution center) that requires separate monitoring, or is it a problem child that gets its own report?

4. **How do the 16 DSG account numbers stay in sync?** DSG accounts are hardcoded in a SWITCH column in Power Query. If DSG opens a new account, acquires another chain, or closes a location, the list goes stale. Is there a process to update this?

5. **Which column is the "official" OT% definition?** Four definitions (Original Request, Original Promise, Current Request, Current Promise) at two grains (Week, Day) = 8 OT% variants. Is one definition the KPI reported to leadership? Which one?

6. **The 3-hour CommandTimeout on the OTD queries suggests performance problems.** Is the `OnTimeDeliveryDetail` table indexed for these queries? Are users experiencing long refresh times?

7. **The `On Time % - Promised` measure in `WH335OnTime` uses `Total Inv Qty (Req)` as denominator — not `Total Inv Qty (Prom)`.** This means `On Time % - Promised` actually divides Promise-compliant qty by Request-basis total. If request and promise totals differ, this measure is wrong. See §9.

---

## 9. Business Assumptions / Magic Numbers

| Constant | Where | What it does | Documented? |
|---|---|---|---|
| `FiscalWeekIndicator >= -55` | Both `On Time` table SQL | ~13-month rolling history | **No** — 55 weeks threshold. No explanation of why 55 (calendar trimesters? 1 year + a quarter?). |
| `FiscalMonthIndicator >= -9` | `WH335OnTime` SQL | ~9-month rolling history for WH335 | **No** — different lookback from main tables (55 weeks vs 9 months). Not comparable. |
| `NOT LIKE 'Z__K'`, `<> 'ZARP'`, `<> 'ZAHM'`, `NOT LIKE '%SW'`, `NOT LIKE '%CARD'` | Both On Time table SQL | Excludes kits, bedding accessories, swatches, cards, and ZAHM items from OT% | **No** — item class exclusions hardcoded in both SQL queries. Documented neither in SQL comments nor in the model. `ZAHM` suspicion: cardboard/hangers? |
| `/24` division | On Time (day) delivery time columns | Converts source hours to days | **Partially** — the source column name `otdOrgPromToDelivery` is in hours, so `/24` is logically correct. But no DAX check prevents usage of these columns without the week-grain denominator. |
| `16 hardcoded account numbers → "DSG - All Accounts"` | `Customer` calc column (both tables) | Rolls up 16 specific account numbers under one DSG label | **No** — a copy-pasted SWITCH in two tables. No DSG account master list maintained anywhere else. |
| `Warehouse = '335'` | `WH335OnTime` SQL | Specific warehouse filter | **Partially** — table name says 335, but no business purpose stated. |
| `FiscalYear = '2024' AND FiscalQuarter = '3'` | Commented-out test filter in WH335OnTime SQL | ETL test criteria | **No** — in a comment block, suggests WH335OnTime may be in-development. |
| 3-hour `CommandTimeout` | Both On Time table queries | Exceptionally long timeout | **No** — the 180-second timeout (3 minutes, not 3 hours) is set; 3 hours would be 10800. Actual: `#duration(0, 3, 0, 0)` = 3 minutes. Still long compared to other models (1 minute default). |

**`On Time % - Promised` in WH335OnTime — potential denominator error:**
```dax
// Current definition
On Time % - Promised = DIVIDE(WH335OnTime[On Time Prom], WH335OnTime[Total Inv Qty])
// where Total Inv Qty = SUM(WH335OnTime[Total Inv Qty (Req)])
// NOT: SUM(WH335OnTime[Total Inv Qty (Prom)])
```

`Total Inv Qty (Req)` = `Late Req Qty + On Time Req Qty` (by Request).  
`Total Inv Qty (Prom)` = `Late Prom Qty + On Time Prom Qty` (by Promise).  
The measure uses `Total Inv Qty (Req)` even for the Promise calculation. If any shipment has a different classification for Request vs Promise (e.g., on-time per Request but late per Promise), the denominator doesn't match the numerator's population, and the reported OT% is wrong. The correct denominator for `On Time % - Promised` should be `Total Inv Qty (Prom)`.

**Dollar-value business impact:** This model does **not** calculate any dollar-value impact. No FOB price, cost, or revenue is included in any OTD measure. The metrics are pure service-level percentages with no financial weighting.

---

## 10. Comparability / Consistency Issues

### a. Week-level vs day-level OT% — structurally different definitions, same fact table

| Metric | Freshness of promise | How "on-time" is measured |
|---|---|---|
| `On Time % - Original Promise Wk` | Latest snapshot | Shipped in or before the week of the original promise |
| `On Time % - Original Promise Day` | Latest snapshot | Shipped on or before the exact day of the original promise |
| `On Time % - Original Request Wk` | Latest snapshot | Shipped in or before the week of the original request date |
| `On Time % - Original Request Day` | Latest snapshot | Shipped on or before the exact day of the original request |

A customer with 90% OT at week level could have 70% OT at day level — but there is no mapping between the two. The gap itself is informative, but a user who doesn't understand the distinction could misinterpret large fluctuations.

### b. `On Time % - Promised` in WH335OnTime uses wrong denominator — structurally different from main tables

The main `On Time (week)` and `On Time (day)` tables compute OT% as `(On Time Qty) / (Total Shipped Qty)`. The `WH335OnTime` table computes it as:
- `On Time % - Requested` = `On Time Req Qty / (Late Req Qty + On Time Req Qty)` — correct by Request
- `On Time % - Promised` = `On Time Prom Qty / (Late Req Qty + On Time Req Qty)` — **uses Request total, not Promise total**

This makes `WH335OnTime[On Time % - Promised]` potentially > 100% (if Promise classification differs from Request) or < correct value. Not comparable with `On Time % - Current Promise Wk` from the main table.

### c. Main On-Time tables and WH335OnTime use different customer attribute sources

| Attribute source | On Time (week/day) | WH335OnTime |
|---|---|---|
| Customer Name + ABC + Business Type | `PowerBI_Wholesale.Customers` | `AFISales_DW.DimCustomers` |
| Customer Service Agent | Not available | Available |
| Bill To Country | Not available | Available |

Different customer attribute sources mean the same account may have different `ABC Account-Current Year` or `Reporting Business Type` depending on which table is queried. No conformed customer dimension exists to reconcile the two.

### d. Item class exclusions differ between main tables and WH335OnTime

Main tables: excludes `Z__K`, `ZARP`, `ZAHM`, items ending in `SW`, `CARD`.  
WH335OnTime: **no exclusions at all**.

This means items excluded from OT% calculation in the main dashboard may show up in WH335 performance — making the WH335 "total" not directly comparable to the overall OT%.

### e. `AshleyFiscalCalendar` (V1) vs `z_FiscalCal` (V2) — two fiscal calendars coexist

Both loaded; only `z_FiscalCal` is connected. If a new report visual accidentally uses date fields from `AshleyFiscalCalendar`, there would be no filter propagation to any fact table. The orphaned table is a maintenance risk.

### f. `Customer Name` in On Time tables does not join to any customer dimension

The `Customer Name` column is brought in via SQL join to `PowerBI_Wholesale.Customers`, not through a conformed dimension. Any account with a name change in the EDW but not updated in the wholesaler customer table would display differently than in other SC models that use `z_CustomerMaster_AFI`.

---

## Closing — Interview Seeds

1. **"When you look at the on-time percentage for a customer, are you using the week-level or day-level measure? And when you report OT% up to leadership, which one of the four definitions — Original Promise, Original Request, Current Promise, Current Request — is the KPI?"**  
   *(Determines which of the 8+ OT% variants is the de facto KPI and whether the others are actually reviewed or just noise.)*

2. **"Warehouse 335 has its own separate on-time calculation in this model, and it defines 'on-time' differently from the main dashboard — it compares the invoice week to the request/promise week using the sales invoice table, rather than using the on-time delivery system. Have you noticed 335's OT% looking different from the same warehouse's number in the main view?"**  
   *(Surfaces awareness of the methodological discrepancy between WH335OnTime and the main tables.)*

3. **"The DSG accounts — there are 16 specific account numbers hardcoded into a column to roll them up as 'DSG - All Accounts'. If a new DSG store opens with a new account number, who needs to update this list, and how would they know it's missing?"**  
   *(Establishes whether the DSG rollup is actively managed or a one-time setup that has already drifted.)*

4. **"There's a separate calendar table called `AshleyFiscalCalendar` that's loaded but not connected to anything in the model — it's V1 of the fiscal calendar that was superceded by V2. Do you know if any chart or dashboard tile still references the old table, and is it safe to remove?"**  
   *(Validates whether the orphaned calendar table is live in any visual or can be cleaned up.)*
