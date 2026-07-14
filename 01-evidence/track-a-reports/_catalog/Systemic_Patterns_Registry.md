# Systemic Patterns Registry

| Field | Value |
|---|---|
| **Purpose** | Cross-report synthesis of estate-wide patterns found across full Prompt #1 analyses. Single-report findings live in each report's analysis file; **this document only records patterns confirmed in ≥2 independent models.** These patterns are the "skeleton" of what must be standardized before an Eagle Eye / control-tower layer can be built on top of this estate. |
| **Evidence base** | 25 fully-analyzed models (as of 2026-07-09) — all analyses in `01-evidence/track-a-reports/`, raw `.bim` exports for 19 of them in `track-a-reports/bim/` — plus catalog-level scan of all 25 archived model summaries. **Since 2026-07-10, cross-checked against `07-fabric-build/docs/report-migration-docs/02-group-analysis/`** — a tool-parsed (direct TMDL/SQL parsing, not human read) quantitative catalog of the same 26-model estate, produced independently by the data-engineering team. Entries below marked **"Quantitative confirmation"** cite exact figures from that catalog. |
| **Verification** | Where noted ✅, the finding was independently re-verified against the raw `.bim` semantic model file, not just the analysis document |
| **Status** | Living document — update as each new analysis lands |

---

## PAT-01 — Broken/dead measures running in production

**Confirmed in: 4 models.** Measures that structurally cannot return a correct value
exist in live, published models with no warning to users:

| Model | Broken artifact | Failure mode |
|---|---|---|
| Weekly Trend Analysis | `ACTD (accy)`, `90Day Error`, `90Day Error %` | Reference column `Actual Qty` that doesn't exist in `FcstAccuracy` (✅ verified against .bim — the table has no actuals column at all). Always BLANK / −1. |
| Forecast Accuracy CustItWh | All six `(B)` baseline-benchmark measures + `wMAPE Value Add_CIW`, `Error Value Add_CIW` | Reference column `(B)Error` that doesn't exist anywhere in model or SQL. "Value add vs baseline" always equals the raw value. |
| Safety Stock Analysis | `DP SS Qty Suggested/Constrained`, `DP WOS`, `DP SS DOS` | Reference table `DPIO` that doesn't exist in the model. |
| Inv Management | `Measure 2` | Completely empty expression. |

**Implication:** no semantic-model testing or monitoring process exists. A visual
bound to any of these measures shows blank/wrong numbers indefinitely. Any Eagle Eye
layer consuming these models must validate measure health programmatically, not
assume published = working.

**Interview leverage:** "Did you know the 90-day error % on this page has been
returning −1 for every row?" is a trust-building opener, not an accusation.

**Quantitative confirmation:** none available. `07-fabric-build/docs/report-migration-docs/02-group-analysis/`
catalogs consolidation *opportunities* (duplication, drift), not defects — it does
not independently check whether referenced columns/tables actually exist. PAT-01
remains evidence from direct `.bim` inspection only.

---

## PAT-02 — Copy-paste propagation between sibling models (proven, not inferred)

**Confirmed in: 2 model pairs + 1 authoring fingerprint.**

- The **same year-typo `'01/25/2025'`** (intended as a Feb-**2026** cycle-deviation
  trigger) appears in the source SQL of **both** Forecast Accuracy CustItWh and
  Forecast Accuracy ItWh (✅ verified in both .bim files). Identical bug in two
  models is direct proof the models are cloned from one another — and that a bug in
  the "parent" silently propagates.
- Inv Management's `sELECTEDVALUE` casing artifact and `MOS Case 1`/`Case 11` exact
  duplicate show the same copy-edit authoring habit inside a single model.
- On Time % by Customer contains an identical 16-account `DSG` SWITCH block
  copy-pasted into two tables — a change to DSG's account list must be made twice.

**Implication:** the estate has no shared measure library; logic is duplicated by
copy-paste and diverges over time (see PAT-03). Fixing a bug in one model does not
fix its siblings.

**Quantitative confirmation:** the Fabric catalog independently found **10 exact-duplicate
source queries** (identical normalized SQL fingerprint reused across two different
models) — e.g. `Wholesale_DemandPlanning_AFI.SupplyPlanDetail` copy-pasted into both
Demand Review and Product Review (NEW); `Wholesale_SalesHistory_AFI.InvoiceDetail`
copy-pasted into both Product Review (NEW) and Weekly Trend Analysis (full list:
`fact-grains.md`, exact-duplicate-queries table). This is a different detection
method (query fingerprinting, not manual bug-spotting) confirming the same
estate-wide copy-paste authoring habit from an independent angle.

---

## PAT-03 — Same name, different logic across sibling models

**Confirmed in: 3 concept groups.** Measures/parameters with identical names or
identical business meaning silently differ across models:

| Concept | Divergence |
|---|---|
| `Bias Threshold` | **0.08** in Forecast Accuracy ItWh (✅ verified) vs **0.10** in CustItWh — same concept, same name family, different tolerance. An item can be "acceptable" in one report and "biased" in its sibling. |
| `Refresh Date` | ItWh: `FiscalDayIndicator = 0` (today). CustItWh: `FiscalDayIndicator = −1 then +2` (yesterday + 2 days). Same measure name, different date semantics. |
| MOS / months-of-supply | Inv Management `MOS Case 1/11` (plan-demand denominator) vs `Case 111` (true-demand denominator with negative-branch) — sequential naming implies versions of one calc; they are different calculations. |
| Demand-fulfillment rate | **Two reports named "Product Review"** compute `DF rate` differently: old = `(FD + SI_neg) / FD`; NEW = `(FD + NF + SI_neg) / (FD + NF)` — same visual label, different denominator populations (BUG-018). Added 2026-07-09. |

Related, previously-logged instances: naive-lag 2M vs 3M mismatch (SCP Forecast
Accuracy), warehouse-335 include/exclude inconsistency (When to Disco v2 vs others).

**Implication:** any cross-report comparison — the core promise of a control tower —
is unsafe until these are reconciled into one governed definition per concept.

**Quantitative confirmation:** the Fabric catalog's measure-signature analysis
(`measure-archetypes.md`) found **879 distinct measures across the 26 models
collapse to only 253 distinct normalized signatures, of which 64 recur in more than
one model** — i.e. roughly a quarter of all "different" measures in the estate are
actually the same calculation wearing a different name, and 64 of those repeated
shapes already show divergence risk. Two concrete illustrations beyond what's above:
- **Forecast-accuracy family (archetype #7, ~60+ members, 6 models):** nearly
  identical measure sets in Forecast Accuracy (ItWh), Forecast Accuracy (CustItWh,
  suffixed `_CIW`), and embedded again in Demand Review, Product Review (NEW), and
  Weekly Trend Analysis — differing only in grain (Item / Item-WH / Cust-Item-WH)
  and lag (2wk/30d/90d), confirming this isn't 3 unrelated models but one
  calculation copy-pasted with cosmetic renaming 5+ times.
- **DimProduct classification drift (110 model-local calculated columns across 16
  models):** lifecycle/status classification alone is reimplemented under **four
  different names** — `z_LifeCycle`/`z_LifeCycleCat` (Inventory Health, Safety Stock
  Analysis), `Life Cycle Status` + `Market + Life Cycle` (Demand Review, Product
  Review (NEW)), plus separate `Status`/`Stat` groupings — same business intent,
  unverified whether thresholds actually match. See
  `07-fabric-build/docs/report-migration-docs/02-group-analysis/conformed-dimensions.md`.
  This is the single largest same-concept-different-logic surface found in the
  entire estate — larger than the forecast-accuracy family above.

---

## PAT-04 — Ungoverned SharePoint/Excel dependencies in decision-critical paths

**Confirmed in: 5+ models.** Manually-maintained Excel files and SharePoint lists sit
directly inside forecast, vendor-classification, and planner-assignment logic:

| Model | Dependency | Sharpest risk |
|---|---|---|
| Demand Review | 8 SharePoint sources, incl. `RH_Fcst.xlsx` (working **and** prior plan from the same file), `Cycle_Dates` list driving every snapshot-relative measure | `RH_DropShip_Sales_2024.xlsx` is hard-filtered to calendar 2024 — **all RH drop-ship actuals from 2025 onward are silently absent** |
| Demand Review | `_Product_Journal_UNIFIED_MASTER.xlsx` — path literally contains "DO NOT OPEN / Self Destruct If Opened" | A live shared workbook read directly by Power BI; refresh-time lock/stale-read risk acknowledged in the path name itself |
| AFT_SI-SS_PSW | 5 SharePoint files (vendor list, Consumer Choice/EVC, Wanek DRP, NFM filter) | Feed disposal/expedite classification |
| Inv Management | `VENDOR LIST AFT & 232.xlsx` | Directly drives the Oversea-Vendor returnability disposal decision |
| Forecast Accuracy (both variants) | SharePoint-fed threshold/parameter tables | Governance thresholds live outside any governed store |

**Implication:** cycle-date lists, planner assignments, and channel forecasts —
inputs that decide what leadership sees — have no schema validation, no version
control, no owner metadata. This is the single most common data-readiness blocker
(field D1) across the Decision Registry so far.

**Quantitative confirmation:** the Fabric catalog's own front-matter is internally
inconsistent on the exact count — `00-overview.md` states "14 models affected" by
governed-external-source needs, while `source-governance.md`'s own front matter
states `models_with_external_sources: 22`. We report both rather than picking one;
the discrepancy itself is a small illustration of PAT-03 (same concept, different
number, even within one team's own catalog). What both agree on: SharePoint/Excel
is the dominant ungoverned pattern, plus a distinct, smaller risk not previously
logged here — **2 models (DvC - WanekMillenium, Rolling Report - Wanek Millen) read
directly from manufacturing iSeries systems via ODBC** (`WFVNPROD`, `MILPROD`,
`AFIPROD`), bypassing the EDW entirely. This is a different governance gap than
SharePoint/Excel — it's operational systems being queried directly by BI, not just
ungoverned reference data.

---

## PAT-05 — Undocumented business constants ("magic numbers") in decision math

**Confirmed in: every model analyzed (12/12).** Consolidated table of the highest-stakes
constants (full lists in each analysis §9):

| Constant | Model | Role |
|---|---|---|
| `× 3` multiplier; `+ 91 days` shift | SCP Forecast Accuracy | Net-sales financial-impact bridge shown to leadership |
| `0.1 / 0.15` alert thresholds; `SS × 1.4` overage line | Demand Review | Drive `Exception Flag` and SI-overage exception lists |
| `25% / 20% / 15%` AND-combined | Demand Review `Chronic Bias Flag` | Labels a planner as chronically over/under-forecasting — a people-performance judgment |
| `1.08 / 0.92` fallback seasonality | Demand Review `OrdHist` SQL | Silently injects ±8% when seasonality data is missing |
| `0.08` vs `0.10` bias tolerance | Fcst Accuracy ItWh vs CustItWh | See PAT-03 |
| `160,000 / 58,000 / 218,000` capacity ceiling | Inv Management | Open-capacity decision, no owner/date |
| Vendor `633312`, `643509`; "all non-Vietnam = returnable" | Inv Management | Disposal-path classification with no contractual check |
| `−55 weeks` vs `−9 months` lookbacks | On Time % (main tables vs WH335 table) | Two different history windows inside one model — OT% not comparable across its own pages |
| 10 hardcoded series → overstock flag; 5 hardcoded "Recent Launch" quarters | Safety Stock Analysis | Lifecycle/overstock classification frozen in time |
| `MAX(Firm+Planned, TotalAvailHours)` | Act+Fcst WNK/MILL `Prod Capacity` | Capacity structurally can never show a shortfall |
| `202212 → 6` hardcoded fiscal-week-count exception | Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing (`FiscalWeeksinMonth`) | One-off correction for a single historical fiscal month, baked permanently into a SWITCH that otherwise computes weeks-per-month generically — new find, added 2026-07-10 |

**Implication:** these constants are **fossilized business decisions** — exactly the
tacit knowledge the discovery program exists to surface. Each one is a ready-made,
low-threat interview question ("where did 1.4 come from?").

**Quantitative confirmation:** the `202212 → 6` row above comes directly from the
Fabric catalog's `transformation-patterns.md` (fiscal-indicator-window pattern,
18 models) — an independent discovery of the same "one-off hardcoded exception
baked into otherwise-generic logic" pattern this section already documented from
Demand Review and Inv Management. Three independent instances of this authoring
habit now confirmed across the estate.

---

## PAT-06 — Financial impact numbers built on unverified assumptions reach executives

**Confirmed in: 2 models.**

- SCP Forecast Accuracy: net-sales impact bridge with undocumented `×3` and
  `+91-day` components.
- Demand Review: `consumption_gap_FOB$_cur` converts an assumed consumption pace
  (historical same-day-of-month average, no seasonality/trend adjustment) into a
  dollar "revenue at risk" figure via rolling-average FOB price — a single point
  estimate presented as fact, likely appearing in monthly WBR decks.

**Implication:** the highest-visibility numbers in the estate are among the least
audited. For Eagle Eye, financial-translation layers need explicit assumption
registers and confidence framing — and these two formulas are the first candidates
for validation with Finance.

**Quantitative confirmation:** none available. The Fabric catalog's cost/cube-weighting
archetype (#9: `SUMX(DimProduct, factor * Qty)`, 8 members across 4 models) covers
*unit-economics* weighting (FOB price, cube, avg sales price) but not the specific
consumption-pace or forecast-value-add formulas flagged here — this pattern is
still evidenced only by direct model inspection.

---

## PAT-07 — Time-alignment inconsistency inside and across models

**Confirmed in: 4+ models.**

- Inv Management uses **three different date anchors** across its own tables
  (next-Saturday / yesterday-with-Monday-adjustment / `GETDATE()`).
- Demand Review's `Fcst_Accuracy_Cust_It_Wh` is a UNION of two grains with an
  unannotated **March-2025 structural break** (pre: Item-WH with Customer hardcoded
  `'AFICONS'`; post: Cust-Item-WH) — customer-level history before the break is an
  artifact, not data.
- Demand Review `YTD-1 ACT` uses a double fiscal offset (`FY=−1 AND month < −12`)
  whose correctness depends on unvalidated fiscal-calendar regularity.
- AFT_SI-SS_PSW carries two contradictory hardcoded UTC offsets in one table.
- Weekly Trend sources its forecast from `DemandForecast` (older schema, latest-only)
  while every sibling model uses `DemandForecastSnapshot` — trend comparisons against
  sibling reports use structurally different forecast bases.

**Implication:** "as of when?" has no single answer even within one report. A control
tower needs one conformed calendar + snapshot convention; this pattern is the
strongest architectural argument gathered so far.

**Quantitative confirmation:** the Fabric catalog independently arrives at the same
conclusion with hard numbers, from three angles:
- **Calendar duplication:** `Enterprise_DW.DimDate` is used by 21 models,
  `Enterprise_DW.DimDate_NonRetail` by 6 more (two calendars where governance
  intends one, differentiated only by a retail/non-retail attribute), and the
  `z_FiscalCal` role-playing copy appears separately in 16 models.
- **The fiscal-indicator-window pattern** (relative "this month = 0" style columns)
  is reimplemented in **18 models**, each recomputed independently relative to
  `TODAY()` in that model's own copy of the calendar — meaning 18 separate places
  where a calendar bug or drift could produce a different "as of when" answer.
- **The latest-snapshot pattern** (filtering to the most recent snapshot) appears in
  **16 models**, using **6 different column names** for the same concept across
  sources: `SnapshotDate`, `SPRunDate`, `FileDate`, `InsertedDate`, `dfcSnapshot`,
  `InitialDate` — no shared convention for what "current" even means at the column
  level. See `07-fabric-build/docs/report-migration-docs/02-group-analysis/transformation-patterns.md`.

---

## PAT-08 — "One measure per warehouse" instead of a warehouse dimension

**Confirmed in: 2 models** (Supply Plan Detail ~40 `WH## SI` measures; Inv Management
7 `Whse ## - SI` measures) — plus the estate-wide warehouse-335 hardcoding (11 of 25
models) documented in `Artifact_First_Extraction_Pass.md` §3. An earlier update to
this pattern (2026-07-07) claimed 335 is confirmed as "the main DC" — **that framing
was overreach and has been corrected (2026-07-10)**: the Fabric build's governed
`DimWarehouse` definition confirms 335 (Ashton) is a real, distinct warehouse grouped
separately from the core AFI warehouses, but does not confirm network-wide primacy.
Provisionally resolved pending Robert's confirmation — see
`../../07-fabric-build/WAREHOUSE_335_RECONCILIATION.md`. On Time % even maintains a
separate `WH335OnTime` table with a *different lookback window* (9 months vs 55
weeks) than its own main tables — this fact stands regardless of how the "main DC"
question resolves.

**Implication:** warehouse is not modeled as a conformed dimension anywhere it
matters. This is a concrete, buildable Eagle Eye foundation item: one `DimWarehouse`,
one SI measure, one OT% definition. The Fabric build's `DimWarehouse.md` (see
`07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md`) is a
ready-made candidate — it already defines the exact `PlanningWarehouse` collapse
this pattern calls for.

**Quantitative confirmation:** the Fabric catalog's archetype #8 ("Hardcoded
warehouse slice") independently itemizes exactly this pattern: `Supply Plan Detail`
has one `CALCULATE(SUM(SI), Warehouse = "##")` measure per warehouse code (1, 5, 15,
16, 17, 28, 42, 50, 70, ECR), repeated again for the SI-SS variant and again for the
"Wk4 SI" variant — **~40 measures total for what should be one measure sliced by a
dimension**. `Inv Management` repeats the identical anti-pattern as `Whse # - SI`.
Separately, `z_WarehouseMaster` is reached via 14 different model paths with 3
drifted local calculated columns (`Physical WH`, `WH Site`, `WHSE` — three different
names for the same physical-warehouse-normalization concept across GF Act+Fcst,
Safety Stock Analysis, and Weekly Trend Analysis), flagged in the Fabric catalog as
the **highest-risk** transformation pattern in the entire estate specifically
because the three mappings may not agree with each other.

---

## How to use this registry

1. **Sprint 2 recalibration input** — the handoff's "recalibrate the method after ≥5
   reports" trigger is met (25 of 26 done). These patterns, not additional single-report
   findings, should drive what Prompt #1 looks for next (e.g., add a standing
   "check for broken measure references" step — it has paid off 4 times).
2. **Interview strategy input** — PAT-01 and PAT-05 findings convert directly into
   low-threat, evidence-anchored interview openers (see `Bug_Findings_Log.md`).
3. **Eagle Eye architecture backlog seed** — PAT-03/-07/-08 define the
   standardization work (governed measure library, conformed calendar/snapshot
   convention, conformed DimWarehouse) that must precede any cross-report
   intelligence layer. Cross-reference `00-foundation/Architectural_Hypothesis_Backlog.md`.
4. **Cross-verification status (as of 2026-07-10)** — 6 of 8 patterns (PAT-02, 03,
   04, 05, 07, 08) now carry independent quantitative confirmation from the
   data-engineering team's own tool-parsed catalog (`07-fabric-build/`), produced
   by a different method (TMDL/SQL parsing) than this document (manual Prompt #1
   analysis). Two patterns (PAT-01, PAT-06) remain evidenced only by direct model
   inspection — the Fabric catalog's scope (consolidation opportunities) doesn't
   cover defect-detection or financial-formula auditing, so this is an expected
   gap, not a weakness to chase down artificially.
