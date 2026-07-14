# Plan Detail Timeline — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | SCP Team (`29ff4afb-7e3c-4218-9cc9-cd4e14e09551`) |
| **Report Name** | Plan Detail Timeline |
| **Backing Model** | Plan Detail Timeline (`16c0571b-2d6e-45e4-943f-1869220bf795`) |
| **Compatibility Level** | 1520 (Power BI Desktop ~Dec 2020) |
| **Description** | DRP/MPS weekly planning timeline viewer — projects item × warehouse supply, demand, and inventory position across 22 relative weeks from each planning run date, sourced from Logility via EDW view `SchedulingPlannedDetailTimeline` |
| **Analyzed** | 2026-07-13 |

---

## §1 — Supply-chain question & chain link

**Question:** For each item × warehouse combination, what does the planning system currently project — across demand, supply, and inventory — week-by-week over the next 22 weeks, as of a specific run date?

**Chain links served:** **Forecast + Supply + Inventory** (all simultaneously). The column `PTLDATATYPE` is the row-type discriminator that separates demand forecast rows, supply order rows, projected inventory rows, etc., within a single denormalized fact table. This report is a **DRP/MPS planning timeline viewer** — it spans the full demand-supply balancing link of the chain rather than a single link.

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Is a specific item/warehouse short or long in weeks 1–4? Expedite, cancel, or reschedule receipts accordingly. | DRP Planner / Fcst. Planner | Weekly (tied to planning run) | **Operational** |
| Which items have a planning hold (`Hold/Buy`)? Should the hold be released or maintained? | DRP Planner | Weekly | **Operational** |
| Are key items (`Key Item` flag) adequately covered across the 22-week horizon? Escalate if not. | WBR-leadership / Supply chain manager | Weekly | **Performance/Governance** |
| Is the make-vs-buy split (`MakeBuy Code`) consistent with plan? Alert if a make item is being planned as buy. | Planner / Analyst | Weekly | **Performance/Governance** |
| What is the projected dollar exposure for items where `Current Status` ≠ `Future Status`? Justify investment to fix. | Executive / WBR-leadership | Monthly | **Financial-Justification** (potential — see §9) |
| Which vendor is driving supply risk for a given item over the 22-week horizon? | Planner | Weekly | **Operational** |
| Is `Derived Fcst. Factor` applied consistently across items of the same `Fcst. Type`? | Analyst | Weekly | **Performance/Governance** |

---

## §3 — Key metrics / measures

> **No explicit DAX measures exist in this model.** All numeric fields carry `summarizeBy: sum` (implicit default) or `summarizeBy: none` (dimensions). Every calculation lives in the visual/report layer or doesn't exist.

### Dimension / descriptor columns (PDT table)

| Column | Type | Plain-English Meaning | Flags |
|---|---|---|---|
| `PTLITNBR` | string | Item number — primary product key | No join to product master |
| `PTLWHSE` | string | Warehouse / DC code | No join to location master |
| `PTLDATATYPE` | string | Row-type discriminator — identifies whether row is Demand Forecast, Supply Order, Projected Inventory, etc. | ⚠️ Values unknown from model alone — see §8. Critical for correct interpretation of all PTLWEEK columns |
| `Item Class` | string | Item classification code from ERP | |
| `Collective Class` | string | Grouping above Item Class | |
| `Series` | string | Product series / line | |
| `Divison` | string | Division | ⚠️ **Typo — "Divison" not "Division"** in both source and model. Any join or cross-report lookup on this column will fail silently |
| `Current Status` | string | Current item lifecycle/planning status | Values undocumented in model |
| `Future Status` | string | Planned or projected lifecycle status | Values undocumented |
| `Hold/Buy` | string | Procurement disposition flag | Values undocumented |
| `ABC` | string | ABC classification (velocity/value) | |
| `Key Item` | string | Flag marking strategically important items | Values undocumented — likely Y/N |
| `Fcst. Type` | string | Forecast methodology type | |
| `Source Key` | string | Surrogate or natural key linking back to source system | |
| `MakeBuy Code` | string | Make vs. buy designation | |
| `Vendor` | string | Vendor name or code | Denormalized; no join to vendor master |
| `Fcst. Planner` | string | Forecast planner responsible | |
| `DRP Planner` | string | DRP planner responsible | |
| `Currency Code` | string | Currency of Price column | ⚠️ Implies multi-currency data; no FX rate table present |
| `Run Date` | dateTime | Snapshot date of the planning run — identifies which planning cycle this row belongs to | Drives multi-snapshot comparison capability |
| `Description` | string | Item description | |
| `Price` | double | Unit price | ⚠️ `summarizeBy: sum` — summing prices across items is meaningless. Format string "General" (no currency symbol). Currency not normalized. |

### Numeric week columns (all `int64`, `summarizeBy: sum`)

| Column | Plain-English Meaning | Flags |
|---|---|---|
| `PTLWEEK1` | Planned quantity for relative week offset +1 from Run Date | ⚠️ See below |
| `PTLWEEK2` … `PTLWEEK22` | Planned qty for relative offsets +2 through +22 | ⚠️ See below |
| `Derived Fcst. Factor` | Multiplier applied upstream to derive adjusted forecast quantity | ⚠️ `summarizeBy: sum` — summing a multiplier across rows is semantically wrong. Should likely be `none` or averaged |

⚠️ **PTLWEEK1–PTLWEEK22 — hardcoded pivoted week columns.** 22 columns represent relative week offsets from `Run Date`, NOT absolute calendar dates. No week-start-date column exists in the model. A user viewing "PTLWEEK3" cannot determine which calendar week that refers to without knowing the Run Date of the row.

⚠️ **`summarizeBy: sum` on all PTLWEEK columns is structurally dangerous.** When multiple `PTLDATATYPE` rows exist per item/warehouse (demand + supply + projected inventory all share the same key), summing across them produces numbers that are neither demand nor supply — arithmetically summed row types, which is not a meaningful supply-chain metric. No model-level filter enforces single-type context.

⚠️ **`Derived Fcst. Factor` summed as default.** If multiple rows exist per item/warehouse/run-date (one per PTLDATATYPE), the factor is summed across row types — almost certainly wrong.

---

## §4 — Data sources & lineage

| Layer | Detail |
|---|---|
| **Server** | `ashley-edw.database.windows.net` |
| **Database** | `ashley_edw` |
| **Object** | `[PowerBI_SupplyChain].[SchedulingPlannedDetailTimeline]` |
| **Connection mode** | Import (full extract, no DirectQuery, no incremental refresh) |
| **Query** | Explicit `SELECT` of all 43 columns by name — **no WHERE clause, no date filter, no row-limit predicate** |
| **Timeout** | `CommandTimeout = #duration(0, 1, 0, 0)` = **1 hour** ⚠️ |
| **M transformation** | Single step after source: cast `PTLWEEK1`–`PTLWEEK22` to `Int64` |

> ⚠️ **No WHERE clause / no date filter on the SQL query.** All historical run dates are pulled on every refresh. As the EDW view accumulates planning snapshots over time, the full-refresh import grows unboundedly — the 1-hour timeout will eventually be insufficient with no incremental load strategy in place.

> ⚠️ **No dataflow / certified dataset intermediate layer.** PDT queries the EDW view directly. If `SchedulingPlannedDetailTimeline` is modified upstream, this model breaks with no governance checkpoint.

> ⚠️ **`SchedulingPlannedDetailTimeline` is a single ungoverned SQL view as the sole source.** No documentation of which base tables it joins, how it pivots PTLWEEK1–22, or what PTLDATATYPE values it produces.

---

## §5 — Grain & snapshot strategy

**Primary grain:** one row per (`PTLITNBR`, `PTLWHSE`, `PTLDATATYPE`, `Run Date`)

**Snapshot strategy: multi-snapshot by design.** `Run Date` has a full date hierarchy and is the primary temporal key. The model retains all historical planning run snapshots — users can compare how the plan for a given item/week changed between successive Run Dates.

**Risk:** Single import partition with no incremental refresh. All snapshots load in full on every refresh. For a weekly planning cycle this means data volume grows ~52× per year with no pruning logic. As the model ages, refresh time and premium capacity usage will increase monotonically.

---

## §6 — Dimensions used

**All dimensions are locally denormalized** into the PDT flat table — no separate dimension tables, no star schema, single wide fact.

| Dimension | Column(s) | Conformed? | Notes |
|---|---|---|---|
| **Item / Product** | `PTLITNBR`, `Description`, `Item Class`, `Collective Class`, `Series` | ❌ Not conformed | No join to shared Product dim |
| **Warehouse** | `PTLWHSE` | ❌ Not conformed | No join to Location/Warehouse dim |
| **Division** | `Divison` (typo) | ❌ Not conformed | Typo is a governance risk for cross-report comparisons |
| **Vendor** | `Vendor` | ❌ Not conformed | No join to vendor master |
| **Planner** | `Fcst. Planner`, `DRP Planner` | ❌ Not conformed | Two separate planner columns, no shared People dim |
| **Date (Run Date)** | `Run Date` → auto LocalDateTable | ❌ PBI-generated only | No enterprise fiscal calendar; standard Gregorian Year/Quarter/Month/Day hierarchy only |
| **Item attributes** | `ABC`, `Key Item`, `Hold/Buy`, `MakeBuy Code`, `Current Status`, `Future Status`, `Fcst. Type` | ❌ Denormalized | Drift risk from master data; no lookup table |

**No ProductionResource dimension. No Customer dimension.**

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| **PTLWEEK1–PTLWEEK22 (22 identical-pattern columns)** | Same data type, same format string "0", same summarize behavior, same naming pattern. Should be unpivoted in the EDW view or in Power Query to a normalized `(WeekOffset INT, Quantity INT)` structure, enabling a proper time axis and eliminating 22 redundant column definitions |
| **`DateTableTemplate` + `LocalDateTable`** | Two auto-generated PBI date tables with identical hierarchy structure. Template is static dead weight; local table is the active instance. Standard PBI behavior but adds noise to model definition |
| **Vendor, Fcst. Planner, DRP Planner, Item Class, Collective Class, Series, Division** | All denormalized — repeat on every row for the same item. No slowly changing dimension capability; a vendor name change requires full re-extract |
| **`Current Status` and `Future Status`** | Parallel string columns — likely share the same value domain. Could share a single Status lookup with role-playing relationship |
| **`Fcst. Planner` and `DRP Planner`** | Two planner columns with likely overlapping person lists. No shared People/Planner dimension |

---

## §8 — Open questions

1. **What are the valid values of `PTLDATATYPE`?** This is the single most critical unknown. Without knowing which row types exist (e.g. "DEMAND", "SUPPLY", "PROJ_INVT", "MPS RECEIPT") no visual-level filter logic can be verified, and all PTLWEEK summation is uninterpretable.

2. **What does PTLWEEK1 represent exactly?** Is it the calendar week that starts on Run Date, the week immediately after, or is there a fixed offset? Is the offset fiscal-week-based or calendar-week-based? The EDW view definition is required to answer this.

3. **What is `Derived Fcst. Factor` and how is it applied?** Is it pre-applied to the PTLWEEK quantities in the EDW view, or is it a multiplier the report consumer is expected to apply manually?

4. **What are the valid values of `Hold/Buy`, `Current Status`, `Future Status`, `Key Item`?** These coded fields have no data dictionary in the model. Slicer/filter behavior is opaque to new users.

5. **How many distinct `Run Date` values are currently in the EDW view?** This determines whether the no-filter full-load query is manageable today or already at risk of timeout.

6. **Is `Price` standard cost, list price, or transfer price?** And is it already in a normalized currency or does `Currency Code` imply FX conversion is needed before any dollar-impact calculation?

---

## §9 — Business assumptions / magic numbers

| Constant / Setting | Location | Apparent Purpose | Documented? |
|---|---|---|---|
| `#duration(0, 1, 0, 0)` (1 hour) | M query `CommandTimeout` | Maximum allowed SQL query execution time | ⚠️ No. Hardcoded. No explanation of why 1 hour was chosen |
| `PTLWEEK1` … `PTLWEEK22` (22 weeks) | EDW view column names, baked into model | Planning horizon = 22 relative weeks forward | ⚠️ No. If the EDW view is ever extended to PTLWEEK23+, those columns will be silently excluded from this model |
| `Calendar(Date(2015,1,1), ...)` | DateTableTemplate partition | Date table seed — static placeholder | Cosmetic; template is never queried directly |
| `INT(([MonthNo] + 2) / 3)` | Auto date table QuarterNo | Standard Gregorian calendar quarter | ⚠️ Assumes Gregorian calendar — not fiscal year-aware |

**Does this report calculate a dollar-value business impact?**

**Partially — the ingredients exist but no formula is implemented in this model.**

Both `Price` (double, per-row unit price) and `PTLWEEK1`–`PTLWEEK22` (integer quantities) are present. The formula would be:

```
Dollar Impact = Price × Σ(PTLWEEKn)   [filtered to a specific PTLDATATYPE and week selection]
```

**However, no DAX measure implements this multiplication.** The model has zero explicit measures. Any dollar calculation currently lives in a report visual's implicit aggregation or is entirely absent. Additionally:

- ⚠️ `Price` currency is not normalized — `Currency Code` implies multi-currency data; no FX rate table exists in the model
- ⚠️ `Price` format string is "General" (no currency symbol) — increases misinterpretation risk
- ⚠️ `Derived Fcst. Factor` may modify the effective quantity, but its relationship to the PTLWEEK values is undefined in the model

---

## §10 — Comparability / consistency

### 10.1 — Cross-PTLDATATYPE summation (highest severity structural issue)
No explicit measures exist. Any visual that sums PTLWEEK columns without filtering `PTLDATATYPE` aggregates demand + supply + projected inventory rows together. The result is arithmetically summed row types — not a meaningful supply-chain metric. No model-level filter, RLS rule, or measure enforces single-type context.

### 10.2 — Run Date cross-period comparison is structurally ambiguous
`PTLWEEK1` for `Run Date = 2025-01-06` refers to calendar week of Jan 13. `PTLWEEK1` for `Run Date = 2025-01-13` refers to calendar week of Jan 20. Cross-run-date comparison of the same PTLWEEK-N column compares different absolute calendar weeks. The model cannot anchor week offsets to absolute calendar dates because no week-start-date column exists.

### 10.3 — `Price` summed by default across warehouses
An item with two warehouse rows (PTLWHSE = "AFT" and "335") will have prices summed in any visual that doesn't filter to a single warehouse — producing a doubled or otherwise meaningless price figure.

### 10.4 — `Derived Fcst. Factor` summed across PTLDATATYPE rows
If the same item/warehouse/run-date has multiple rows (one per PTLDATATYPE), the factor is summed across row types by default — semantically wrong for a multiplier.

### 10.5 — `Divison` typo creates permanent column name inconsistency
Any report, composite model, or data flow that joins on a "Division" column will fail to match this model's "Divison" field. The mismatch is invisible in slicers but breaks downstream integrations.

### 10.6 — QuarterNo formula uses Gregorian calendar
`INT(([MonthNo] + 2) / 3)` produces standard Q1/Q2/Q3/Q4 calendar quarters. If Ashley operates on a fiscal calendar (e.g. fiscal year starting in July), the quarter labels in the Run Date hierarchy will be wrong for fiscal reporting purposes.

---

## Closing — Interview Seeds

**Q1 — PTLDATATYPE values (critical):**
> "What are the actual values `PTLDATATYPE` takes in the planning system — for example, is it 'DEMAND', 'SUPPLY', 'PROJ_INVT', or something else? And when a planner opens this report to check supply/demand balance, which PTLDATATYPE row do they look at for the projected inventory position?"

**Q2 — Week offset anchor:**
> "Does PTLWEEK1 always represent the calendar week that starts immediately after the Run Date — or is there a fixed offset between Run Date and the week PTLWEEK1 refers to? Have you ever pulled two different Run Dates side by side and found the PTLWEEK columns didn't line up to the same calendar weeks the way you expected?"

**Q3 — Dollar-value usage:**
> "This model has both `Price` and weekly quantities (`PTLWEEK1`–`PTLWEEK22`). Are planners actually multiplying price × quantity to get a dollar exposure number — or is this report used purely in units? If dollar impact is calculated, where does that happen — in the report visual, in Excel, or somewhere else?"

**Q4 — Snapshot volume and refresh:**
> "How many weeks of planning snapshots does this model currently hold, and has anyone noticed the daily/weekly refresh slowing down over time? Is there a plan to drop old Run Date snapshots, or should the model always retain full history for trend analysis?"
