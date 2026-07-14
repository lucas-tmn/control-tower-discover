# Rolling Report – Wanek Millen — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | SCP Global Team (`fb03479c-f98b-414f-bf8f-ab2dfa744ff4`) |
| **Report Name** | Rolling Report - Wanek Millen |
| **Backing Model** | Rolling Report - Wanek Millen (`4edfa21f-4f8d-4176-8674-7398c128a6bb`) |
| **Compatibility Level** | 1567 (Power BI Premium Gen2) |
| **Description** | Tracks what proportion of confirmed (firm) WNK/MILL purchase-order quantity is rolling to future ETD weeks, how that roll rate has trended across ~10 snapshot weeks, and whether safety-stock coverage remains sufficient at the time of rolling |
| **Analyzed** | 2026-07-13 |

---

## §1 — Supply-chain question & chain link

**Question:** For vendors Wanek and Millenium (4 hardcoded vendor IDs: 600039, 900515, 900639, 624556), what proportion of confirmed (firm) purchase-order quantity is being rolled to future ETD weeks, how has that roll rate trended across the past ~10 snapshot weeks, and how much safety-stock coverage remains at the time of rolling?

**Chain links served:**
- **Supply / Receipts (primary):** firm PO quantities from `PSWWeeklyExtractSnapshot` (W+2 firm horizon) vs. quantity rolled via `PoAuditLog` (audit action `usp_SummaryPORollover`, transaction type `D` = decrease)
- **Late receipts sub-link:** Monday/Tuesday ASN receipts (`PoAuditLog` action `S`, type `A`) that partially absorb rolled quantity before week close
- **Inventory (secondary):** shippable inventory (SI) and safety stock (SS) from `SupplyPlanDetail` at time of snapshot — to assess whether roll-induced shortfalls are covered

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Escalate to Wanek/Millen on specific items where roll rate is above threshold or trending upward over multiple weeks | Planner / Buyer | Weekly (Saturday snapshot) | **Operational** — supplier escalation / expedite |
| Transfer or reallocate inventory from other warehouses when SI drops below SS for rolled items | Planner | Weekly | **Operational** — transfer / adjust |
| Report roll rate trend and SS coverage to leadership as a supplier reliability KPI | WBR-leadership | Weekly business review | **Performance/Governance** |
| Determine whether Monday/Tuesday late-ASN receipts are materially reducing rolling exposure before week closes | Planner / Analyst | Weekly, within-week | **Operational** — receipt reconciliation |
| Distinguish FG vs RP vs Kit/Component roll behaviour by item type to prioritise recovery actions | Planner / Analyst | Weekly | **Performance/Governance** |

> No dollar-value financial-justification decision is supported — **the model contains no cost or revenue measures.**

---

## §3 — Key metrics / measures

All measures reside in table `Firm and Roll`.

### Measures

| Measure | Plain-English Meaning | Grain | DAX / Logic | Flags |
|---|---|---|---|---|
| **`%Rolled`** | Average fraction of firm quantity that was rolled, capped at 100% | Item × Warehouse | `AVERAGEX(SUMMARIZE(..., Item, Whse), IF(Roll=0,0,IF(Roll>FQty,1,DIVIDE(Roll,FQty))))` | ⚠️ Groups by **Whse** — produces different number than `%Roll Average` which groups by ETD Date. Same formula family, different grain, no naming distinction |
| **`%Roll Average`** | Average fraction of firm quantity rolled, capped at 100% | Item × ETD Date | Same AVERAGEX pattern, grouped by **ETD Date** instead of Whse | ⚠️ See `%Rolled` note — the two roll-rate measures are not interchangeable but named similarly |
| **`RollafterLateASN`** | Net rolled quantity after deducting Mon + Tue late ASN receipts for same item × ETD Date | Item × ETD Date | `SUMX(SUMMARIZE(..., Item, ETD Date, RollQty, MonASN, TueASN), Roll - Mon - Tue)` | ⚠️ **Can go negative** — if ASN qty > Roll qty, result is negative. No floor at zero. Whether negative values are meaningful or data artifacts is undocumented |
| **`%RolledASN`** | Roll rate after subtracting Mon/Tue late-ASN receipts | Item × ETD Date | Same AVERAGEX as `%Roll Average` but using `RollafterLateASN` as numerator | ⚠️ When net roll is negative, the IF branch returns 0 — over-receipt state disappears silently rather than surfacing as a "received-more-than-rolled" flag |
| **`SS% Average`** | Average safety-stock coverage ratio (SI ÷ SS) | Item × Warehouse × ETD Date | `AVERAGEX(SUMMARIZE(..., Item, Whse, ETD Date, SUM(SS%)), value/100)` | ⚠️ **Double /100 chain:** SQL stores `SI*100/SS` (integer-percent), DAX divides by 100 again to get decimal, format string `0%` multiplies back by 100 for display — chain is self-consistent only if SQL integer division doesn't lose precision. **SS=0 fallback:** SQL sets `SS% = SI*100/1` when SS=0, producing arbitrarily large coverage numbers for items with no SS target |

### Key calculated columns (table `Firm and Roll`)

| Column | Logic summary | Flags |
|---|---|---|
| **`ETD`** | `FORMAT([ETD Date], "mm/dd")` — display shorthand | ⚠️ **DAX format bug:** `mm` in DAX FORMAT = **minutes**, not months. Month requires `MM`. This column will display `00/dd` (midnight's minute component) instead of the actual month. If used in report visuals as a date label, all months show as `00`. |
| **`Key`** | `Item & ETD Date & Vendor & Whse` string concat | Used for `Firm and Roll → Late ASN` relationship. Format must exactly match `Late ASN[Key]` for join to work correctly |
| **`Item Check`** | Classifies as "KIT & COMPONENTS" or "FG" based on blank Collective Class, "UN" in item number, or numeric+non-numeric suffix pattern | Simpler than `Item Type` — no RP class. Parallel logic — see §7 |
| **`Item Type`** | Multi-branch: FG → RP (by ITMBL ItemClass or Category "RP") → Kits → Components | Most granular classification. Uses both `Category` (iSeries) and `ITEMCLAD` (iSeries). See §7 for inconsistency risk |
| **`New_Roll`** | `MIN(Roll Quantity, FQty)` — roll capped at firm quantity | Correct guard for over-roll scenarios |
| **`Old_Roll`** | `Roll Quantity - New_Roll` — excess roll beyond firm qty | Overflow / residual roll component |
| **`SS% Final`** | For most-recent ETD snapshot per item × whse: `SS%/100`; else 0 | Surfaces only latest-week SS% for item-card use |
| **`latest SI`** | For most-recent ETD per item × whse: SI value; else 0 | Same latest-row extraction pattern |
| **`latest SS`** | For most-recent ETD per item × whse: SS value; else 0 | Same latest-row extraction pattern |
| **`Category`** | `LOOKUPVALUE(ItemMaster[CATEGORY], ItemMaster[ITEM], [Item])` | From iSeries ODBC — no model relationship defined |
| **`ITEMCLAD`** | `LOOKUPVALUE(ItemVAL[ITCLAD], ItemVAL[ITNOAD], [Item])` | From iSeries ODBC — no model relationship defined |

---

## §4 — Data sources & lineage

### Azure SQL EDW — ✅ Governed

Server: `ashley-edw.database.windows.net / ASHLEY_EDW`

| Schema | Object | Purpose |
|---|---|---|
| `SupplyChain_Enh` | `PSWWeeklyExtractSnapshot` | Weekly firm PO snapshots (Saturday only) |
| `Enterprise_DW` | `DimDate` | Calendar dimension (CalendarWeekIndicator, DayOfWeekName) |
| `Enterprise_DW` | `DimDate_NonRetail` | Fiscal calendar (FiscalWeekIndicator) |
| `PowerBI_SupplyChain` | `CurrentProductDetails` | Division, Sellable Item Flag |
| `Wholesale_ProductSourcing_AFI` | `PoAuditLog` | PO quantity changes (rolls) and late ASN receipts |
| `Wholesale_ProductSourcing_AFI` | `PoMaster` | PO header — vendor, warehouse, actual ETD (`pometd`) |
| `Wholesale_ProductSourcing_AFI` | `PoDetail` | PO line — vendor, warehouse for Late ASN |
| `Wholesale_DemandPlanning_AFI` | `SupplyPlanDetail` | Shippable inventory (SI) and safety stock (SS) per item-whse-week |
| `Supplychain_History` | `ARPDETAIL` | RP (Replacement Part) roll detail |
| `Wholesale_Quality_AFI` | `ARPHEADER` | RP roll header (FG model, warehouse) |
| `MasterData_ItemMaster_AFI` | `ITMBL` | Item class codes (CIRP, RPMT, etc.) |
| `SupplyChain_Enh` | `ProductionConversion` | Production resource ID per item × location |
| `DW_Developer` | `TableDictionary` | Data lineage metadata — used for "Latest Update" display |

### iSeries ODBC — ⚠️ Data-readiness risk

Driver: `iSeries Access ODBC Driver`, System: `AFIPROD`, Collection: `AMFLIBA`

| Library | Object | Purpose |
|---|---|---|
| `ADOWNLOAD` | `ITEMMASTERL01` | Item category, material type, style type, production standards (JUMBO_STD, SEW_STD, UPH_STD) |
| `AMFLIBA` | `ITMRVAL0` | Item class validation (ITCLAD code, ITNOAD item number) |

> ⚠️ **Direct connection to live AS/400 production system (AFIPROD).** Bypasses EDW governance. Schema changes, CCSID encoding issues, or iSeries availability will silently break both tables. The `CCSID=65535;Translate=1` ODBC parameter means character data correctness depends on this setting remaining correct — misconfiguration corrupts all string fields silently. `Text.Trim` applied in M queries indicates iSeries fixed-length field padding issues are already known.

---

## §5 — Grain & snapshot strategy

**Primary grain:** Item × Warehouse × Vendor × ETD Date × Snapshot Week (SPRunDate)

**This model is intentionally trend-oriented, not latest-only.** It holds rolling multi-week snapshot history:
- **FIRM data:** Saturday snapshots for `CalendarWeekIndicator between -10 and -2` (up to 9 prior Saturday snapshots, excluding most recent 2 weeks)
- **ROLL audit:** `FiscalWeekIndicator between -7 and 1` (8 fiscal weeks of roll events)
- **Late ASN:** `CalendarWeekIndicator between -8 and 0` (8 calendar weeks)

Users can see how roll rate per item has evolved across snapshot weeks. The `latest SI`, `latest SS`, and `SS% Final` calculated columns extract the most-recent row for operational spot-check use.

**Not possible from this model:** comparing the current week's plan to the prior week's constrained plan (no plan-delta measure). The trend is inferred by visualising roll rate across ETD dates — not across refresh timestamps.

---

## §6 — Dimensions used

| Dimension | Table | Available Attributes | Notes |
|---|---|---|---|
| **Item / SKU** | `Firm and Roll[Item]` | Item code, `Category` (iSeries), `ITEMCLAD` (iSeries), `Division`, `Item Type` (DAX), `Item Check` (DAX), `ProdResourceID` | No standalone item dimension table. Attributes scattered across calculated columns and lookups from two different source systems |
| **Warehouse** | `Firm and Roll[Whse]` | Warehouse code | No warehouse dimension table. Exclusions (C, CNW, AF, IOR) hardcoded in SQL |
| **Vendor / Factory** | `Firm and Roll[Vendor]`, `[VNAME]` | Vendor code, name | Scope locked to 4 hardcoded vendor IDs. No vendor dimension table |
| **ETD Date** | `Firm and Roll[ETD Date]` | Auto-generated LocalDateTable only | No conformed date dimension. `ETD Date` is derived (+14 from SPRunDate — see §9) |
| **Division** | `Firm and Roll[Division]` | AFI Finance Division label | From `PowerBI_SupplyChain.CurrentProductDetails` — not a conformed dim |
| **Item Type / Category** | `[Item Type]` (DAX), `[Item Check]` (DAX), `[Category]` (iSeries), `[ITEMCLAD]` (iSeries) | Classification buckets | ⚠️ Three parallel classification paths — drift risk between iSeries and EDW values |
| **Production Resource** | `Firm and Roll[ProdResourceID]` | Production resource code | Embedded in Firm and Roll fact table, not a separate dimension. Latest snapshot only |

**No RLS defined.** All users see all 4 vendors, all non-excluded warehouses, all item types.

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| **Three item-type classification paths** | SQL `Item Category` CASE (computed, then **explicitly discarded** in M via `Table.RemoveColumns`) + DAX `Item Check` (FG / KIT & COMPONENTS only) + DAX `Item Type` (FG / RP / Kits / Components). Overlapping but non-identical logic. Whether they agree on every row is unverified in the model |
| **`%Rolled` vs `%Roll Average`** | Near-identical AVERAGEX+SUMMARIZE+DIVIDE pattern, different grouping key (Whse vs ETD Date). Could be unified as a single measure with a grouping parameter or report-layer switch |
| **`SS% Final`, `latest SI`, `latest SS`** | Three calculated columns use identical "find latest ETD row per item × whse, return value or 0" logic. Could collapse to one snapshot-flag column plus VALUE lookup |
| **Vendor list duplicated in ≥3 SQL CTEs** | `('600039','900515','900639','624556')` appears in FIRM WHERE, Late ASN WHERE, and Resources CTE filter. A single M parameter would prevent drift |
| **`Key` concatenation in two tables** | Both `Firm and Roll[Key]` and `Late ASN[Key]` build the same composite string for joining. Minor duplication but must stay in sync manually |
| **`Category` and `ITEMCLAD` as LOOKUPVALUE columns** | Both use iSeries ODBC tables with no model relationships. Adding proper relationships or loading these via EDW views would enable filter propagation and eliminate the LOOKUPVALUE dependency |

---

## §8 — Open questions

1. **`WeekNum = 2` vs. comment "SỐ FIRM W3":** The SQL WHERE filter is `WeekNum = 2` but the comment reads `--SỐ FIRM W3` (Firm W3). Is WeekNum 0-indexed (2 = third week = W3)? If the comment is correct and the filter is wrong, the report displays the wrong firm horizon. Needs business confirmation.

2. **RP CTE has no vendor, date, or time filter:** The `RP` CTE pulls all rows from `Supplychain_History.ARPDETAIL` joined to `ARPHEADER` with no vendor/date restriction. Could be very large and produce incorrect item-type classification for historical/inactive items. Is this intentional scope?

3. **`Item Category` computed then discarded:** SQL computes `Item Category` as a CASE expression, but M explicitly removes it. Is `Item Type` (DAX) an exact equivalent or are there edge cases where they disagree?

4. **`RollafterLateASN` can go negative — is this valid?** If MonASN+TueASN > Roll Quantity, the measure returns a negative number. Does a negative value carry business meaning (over-receipt offsetting a prior-week roll), or is it a data artifact?

5. **`[SPRunDate] NOT BETWEEN '2025-02-28' AND '2025-03-16'`:** A permanent 17-day exclusion window is hardcoded in the FIRM query. What caused the data quality issue in that period? Is the exclusion still valid or should those dates be re-enabled?

6. **Is the `+14 days` ETD derivation validated?** `ETD = SPRunDate + 14` is used to join FIRM to ROLL data. If a PO's actual ETD (`pometd`) diverges from `SPRunDate + 14` after amendment, the join misses the roll event. How often are PO ETDs amended after the snapshot run date?

7. **Late ASN Mon/Tue double-deduction:** Can the same units appear in both `MonASN` and `TueASN` for the same item × ETD date? If so, `RollafterLateASN` double-deducts them.

---

## §9 — Business assumptions / magic numbers

**Dollar-value business impact:** **No.** The model contains zero revenue, cost, price, or margin measures. All metrics are unit-quantity based (FQty, Roll Quantity, SI, SS units).

| # | Constant / Offset | Location | Apparent Purpose | Documented? |
|---|---|---|---|---|
| 1 | `+14` days | FIRM CTE: `([SPRunDate] + 14) AS DATE AS [ETD]` | Derives ETD from snapshot run date — assumes snapshot + 2 weeks = expected delivery week | ⚠️ No. Hardcoded lead-time assumption. May not match actual PO ETDs. |
| 2 | `WeekNum = 2` | FIRM CTE WHERE | Selects specific PO firm horizon week from PSWWeeklyExtractSnapshot | ⚠️ Comment says "W3" — 0-indexed or copy-paste error. Ambiguous — see §8 |
| 3 | `CalendarWeekIndicator between -10 and -2` | FIRM CTE WHERE | Rolling 9-week Saturday snapshot window, stopping 2 weeks before current | Comment: "latest snapshot is from 2 weeks ago" — partially documented |
| 4 | `CalendarDayOfWeekName = 'Saturday'` | FIRM CTE WHERE | Selects only Saturday PSW snapshots | Comment: "take snapshot on Saturday" |
| 5 | `FiscalWeekIndicator between -7 and 1` | ROLL CTE inner join | 8 fiscal weeks of roll audit history + 1 forward week | ⚠️ No |
| 6 | `CalendarWeekIndicator BETWEEN -8 AND 0` | Late ASN WHERE | 8 calendar weeks of Mon/Tue ASN data | ⚠️ No |
| 7 | `'2025-02-28'` to `'2025-03-16'` | FIRM CTE WHERE NOT BETWEEN | Excludes specific 17-day data quality window | ⚠️ No comment. Hardcoded. Will remain excluded forever unless manually removed |
| 8 | `Whse NOT IN ('C','CNW','AF','IOR')` | FIRM CTE WHERE | Excludes 4 warehouses from roll calculation | Comment only for C/CNW. AF and IOR exclusion uncommented |
| 9 | `NOT LIKE '%SW'`, `'%CARD%'`, `'%VINYL%'`, `'%HIDES%'` | FIRM CTE WHERE | Excludes fabric/material commodity items | ⚠️ No documentation. New exclusion categories require model edit |
| 10 | `ISNUMERIC(Item)=1 AND LEN(Item)>=9` | FIRM final SELECT item type CASE | Classifies long numeric item numbers as RP | ⚠️ No. Business rule embedded in SQL |
| 11 | `ItemClass IN ('CIRP','RPMT','RPRT','TA','UDRP','UERF','UIRP')` | SQL ITMBL join and DAX `Item Type` | RP item class code set | ⚠️ No documentation. iSeries codes undocumented in model. DAX `Item Type` adds `'TU'` to this list; SQL does not — inconsistency |
| 12 | `EndEffectiveDate IS NOT NULL` | Resources CTE WHERE | Filters to active production resources | Not annotated — standard sentinel convention |
| 13 | `SS=0 → SS% = SI*100/1` | FIRM CTE SS% CASE | When no SS target set, SS% = SI×100 (not bounded) | ⚠️ No. Items with SS=0 appear to have enormous coverage — could be misread as "healthy" when SS target simply hasn't been set |
| 14 | `CCSID=65535;Translate=1` | iSeries ODBC connection string | Character encoding for AS/400 fixed-length fields | ⚠️ Not documented. Misconfiguration silently corrupts all string columns from iSeries |

---

## §10 — Comparability / consistency

### 10.1 — `%Rolled` vs `%Roll Average` — same formula, different grain, no naming distinction
`%Rolled` summarizes by Item × Whse (collapses ETD dates). `%Roll Average` summarizes by Item × ETD Date (collapses warehouses). In a visual with both ETD Date and Whse as slicers, these produce different values. No documentation or tooltip distinguishes intended use.

### 10.2 — Two calendar systems: Calendar vs. Fiscal week
FIRM data uses `DimDate.CalendarWeekIndicator`; ROLL data uses `DimDate_NonRetail.FiscalWeekIndicator`. These are separate dimension tables with potentially non-aligned week boundaries. Roll events and firm snapshots at week boundaries may be attributed to different "week -N" values depending on which system is used, producing a mismatch when comparing FIRM vs. ROLL for the same period.

### 10.3 — ETD derivation mismatch: FIRM (derived) vs. ROLL (actual)
FIRM ETD = `SPRunDate + 14` (approximation). ROLL ETD = actual `pometd` from PoMaster (the real PO field). The join condition is `ROLL.ETD = FIRM.ETD`. If a PO's ETD was amended after the snapshot (a common supply event), `pometd` changes but `SPRunDate + 14` does not — the join misses the roll event, and it disappears from the report silently. This is a structural accuracy risk for all amended POs.

### 10.4 — Item type classification inconsistency across three paths
| Path | Produces | Discrepancy |
|---|---|---|
| SQL `Item Category` (discarded at load) | RP / FG / Kit & Components | Discarded — cannot verify alignment |
| DAX `Item Check` | FG / KIT & COMPONENTS only | No RP class — classifies some RP items as FG |
| DAX `Item Type` | FG / RP / Kits / Components | Adds `'TU'` class code not in SQL RP filter |

A row classified "FG" by `Item Check` can be classified "RP" by `Item Type`. No reconciliation or validation measure exists.

### 10.5 — SS% normalization chain — three representations in one model
- **Source (SQL):** `SS% = SI * 100 / SS` — stored as integer-percent (e.g., 150 = 150%)
- **`SS% Final` calculated column:** `SS%/100` — decimal (1.50)
- **`SS% Average` measure:** AVERAGEX over `SUM(SS%)` then `/100`

A visual using `SUM(SS%)` raw will show values 100× larger than `SS% Average`. No documentation flags this chain.

### 10.6 — `ETD` calculated column format bug affects all date-label visuals
`FORMAT([ETD Date], "mm/dd")` uses `mm` = minutes in DAX. Any visual using `[ETD]` as an axis label will display `00/DD` (month always shown as "00"). This affects the report's primary time axis if this calculated column is used for X-axis labels.

### 10.7 — Hardcoded 2025-02-28/03-16 exclusion creates a permanent data gap
The 17-day exclusion is not time-relative — it permanently removes those dates from all queries. As the rolling window moves forward in time, this gap eventually falls outside the `-10` week lookback and stops being relevant, but it is invisible to users and undocumented.

---

## Closing — Interview Seeds

**Q1 — Decision trigger and escalation:**
> "When you see `%Roll Average` rise above a certain level for a Wanek or Millenium item — what is the threshold that triggers action, and what is the first concrete step you take? Is there a documented escalation path, or does it depend on the individual planner?"

**Q2 — WeekNum = 2 vs. W3 (critical data question):**
> "The underlying query pulls `WeekNum = 2` from the weekly snapshot, but the code comment says 'Firm W3.' Can you confirm which firm horizon this report is meant to show — is it 2 weeks out or 3 weeks out from the run date? And is the `+14 days` ETD assumption tied to that same horizon?"

**Q3 — Late ASN reliability:**
> "The report deducts Monday and Tuesday ASN receipts from the roll quantity to show `RollafterLateASN`. In practice, how reliable are those Monday/Tue ASN figures — are they confirmed receipts or just scheduled arrivals? Have you ever seen the report show a low net roll because of a Monday ASN, only to find the goods hadn't actually arrived?"

**Q4 — Tools outside Power BI:**
> "When you identify an item with high roll rate and SS coverage below 100%, does the recovery action happen entirely in Demand Planning / iSeries, or do you export to Excel and work a recovery plan offline? And for the items where SS is set to zero — are those intentionally excluded from SS monitoring, or is that a data gap you need to flag to someone?"
