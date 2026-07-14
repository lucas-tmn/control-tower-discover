# Artifact-First Extraction Pass — Catalog-Level Scan of 24 Remaining Reports

| Field | Value |
|---|---|
| **Scope** | All 25 model-summary files in `knowledge-library-archive/.../01-report-summaries/`, excluding Forecast Accuracy (ItWh) — already deep-dived — and including Inv Management (now deep-dived, see companion analysis) |
| **Depth** | Catalog-level automated scan (front-matter + pattern search across DAX/SQL/comments), **not** full Prompt #1 — this is the "delta-check" tier from the 3-tier depth model |
| **Purpose** | (a) surface cross-report patterns invisible from any single report, (b) prioritize which of the 24 should get full Prompt #1 treatment next, (c) review the 24 summaries as a body of evidence per the open Sprint 1 action item |
| **Run** | 2026-07-07 |

---

## 1 — Inventory at a glance (all 25 model summaries)

| Report | Tables | Measures | Non-warehouse source? |
|---|---:|---:|---|
| Demand Review | 46 | 230 | Yes |
| Product Review (NEW) | 25 | 129 | Yes |
| Safety Stock Analysis | 13 | 91 | Yes |
| Supplier On-Time Performance | 13 | 54 | Yes |
| Supply Plan Detail | 5 | 63 | Yes |
| GF Act+Fcst | 10 | 43 | Yes |
| Forecast Accuracy (Cust_ItWh) | 12 | 27 | Yes |
| JadeTeam Inventory Health | 2 | 30 | No |
| Forecast Accuracy (ItWh) ✅ done | 14 | 25 | Yes |
| Supply Plan Detail Accuracy | 4 | 19 | Yes |
| On Time % by Customer | 6 | 18 | No |
| Inv Management ✅ done | 11 | 16 | Yes |
| Weekly Trend Analysis | 11 | 15 | Yes |
| Act+Fcst vs Manufacturing | 10 | 14 | Yes |
| Act+Fcst by WNK & MILL Prod Resource | 10 | 14 | Yes |
| DvC - WanekMillenium | 11 | 14 | Yes |
| Inventory Health | 9 | 14 | Yes |
| When to Disco v2 | 7 | 13 | Yes |
| AFT_SI-SS_PSW | 17 | 12 | Yes |
| Inventory Transactions and Item Balance Detail | 5 | 11 | Yes |
| Production Capacity Vs Forecast | 10 | 10 | Yes |
| Top Negatives | 8 | 6 | Yes |
| Rolling Report - Wanek Millen | 5 | 5 | Yes |
| Amazon POS Sales and Forecast | 6 | 7 | Yes |
| Receipts | 4 | 1 | No |
| Plan Drop 1 | 1 | 0 (implicit sum only) | No |

---

## 2 — Major finding: the "Inventory Health" identity question is likely resolved

The handoff flagged an open, cross-cutting risk: at least 3 differently-scoped models
share the "Inventory Health" name, none confirmed as the production 5-bucket report
the original catalog describes.

Scanning the archive directly: **`Inventory_Health.md`** (model name "Inventory
Health," 9 tables, 14 measures, sourced from PowerBI Dataflows) describes itself as
classifying inventory into **exactly five health buckets — Below Max, Over Target,
Excess, High Excess, and TIB (Throw in the Bay)** — based on days of supply and
safety-stock multiples, plus ATP in-stock rate by launch window.

This matches the original catalog's "5-bucket classification" description almost
exactly, and is structurally distinct from both:
- `InventoryHealth_AI` (confirmed prototype, 100% hardcoded, already flagged not
  production), and
- `JadeTeam Inventory Health` (2 tables, 30 measures, a **4-bucket** model — firm
  demand / net forecast / safety stock / excess — genuinely different classification
  logic, likely a different team's parallel build, not a naming variant of the same
  thing).

**This is not yet a confirmed answer** — it's an artifact-level match, and the
recommended verification step from earlier in this conversation still applies (usage
telemetry / access logs to confirm which of these is actually in active use). But it
substantially de-risks the open item: **`Inventory_Health.md`'s underlying model is
the strongest candidate for "the real production Inventory Health report" found so
far**, and is a strong next candidate to replace the Supply & Inventory cluster
representative slot if Inv Management's findings suggest a fuller decision picture
lives there instead. Recommend running full Prompt #1 on it soon — see priority list
below.

---

## 3 — Cross-report pattern: warehouse `335` — inconsistent inclusion

Warehouse code `335` appears hardcoded (not as a normal filterable dimension member)
across **11 of the 25** report summaries scanned:

| Report | How 335 is treated |
|---|---|
| When to Disco v2 | 47 mentions — has **dedicated measures** for warehouse 335 separately from "all domestic warehouses" (explicitly *excludes* 335 from one rolling-average measure, then adds it back in a total) |
| On Time % by Customer | 17 mentions |
| Inv Management | Entire core model (`Inventory`, `W2 SS Change`, `Inv Age`) is scoped to warehouse 335 only — see update below |
| Inventory Health, Safety Stock Analysis, Supplier On-Time Performance, AFT_SI-SS_PSW, Amazon POS Sales and Forecast, GF Act+Fcst, Inventory Transactions and Item Balance Detail, Supply Plan Detail Accuracy, Product Review (NEW), Demand Review | 1-3 mentions each — mostly in warehouse-list `IN (...)` filters |

**Update 2026-07-07 — resolved for Inv Management, still open estate-wide.** A live
Prompt #1 re-run against the actual Inv Management workspace (see
`01-evidence/track-a-reports/Inv_Management_Analysis.md` §1/§4/§8) concluded warehouse
`335` is "Ashley's main distribution center" — the entire core model is deliberately
scoped to it, and the separate `SI at US Warehouse` table tracks the other 7 satellite
warehouses (1/5/15/17/28/42/ECR) for inbound shippable inventory feeding into 335.

**Update 2026-07-10 — that conclusion was overreach; corrected.**
`07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md` (governed
ETL SQL, authored by Robert, dated 2026-06-18 — predates our 07-07 update) shows 335
belongs to `WarehouseGroup = 'ASH'` (Ashton), a group distinct from the core `AFI`
warehouses (1, 15, 16, 17, 28, 42, 5, 70, ECR). This confirms 335 is a real, named,
distinct facility — but does **not** confirm it is "the" primary DC network-wide;
that was an inference from Inv Management's internal scoping choice, not a
governed statement of fact. **Provisionally resolved pending Robert's
confirmation** — full comparison, evidence weighing, and the question queued for
him are in `07-fabric-build/WAREHOUSE_335_RECONCILIATION.md`. Until confirmed,
this repo describes 335 as "Ashton — a distinct warehouse grouped separately from
the core AFI warehouses," not as "the main DC."

This does not resolve the cross-report inconsistency below: `When to Disco v2`
still both includes and excludes 335 from "all warehouse" totals depending on the
measure, and it's not yet confirmed whether every other report treats 335
consistently.

**Why this still matters:** `335` is sometimes *included* in "all warehouse" lists
and sometimes explicitly *excluded* (When to Disco v2 does both, in different
measures, in the same model). Now that 335/Ashton is confirmed as a real, distinct
warehouse (not a data artifact or staging code), any *exclusion* of it from a
"total inventory" figure is inconsistently scoping a real facility — a genuine
comparability risk regardless of whether 335 turns out to be "the" main DC or just
one facility among several. Any comparison of "total inventory" or "total demand"
figures across two different reports could still be comparing different physical
scopes without anyone realizing it. This is the same category of risk as the
Forecast Accuracy naive-lag mismatch — a comparability trap, not a single-report
bug. **Recommend a single, explicit interview question on how warehouse 335/Ashton
should be scoped in "total" figures**, asked once and reused across every future
Track B conversation rather than re-derived per report.

---

## 4 — Cross-report pattern: "one measure per warehouse" duplication

Confirmed independently in **two** models scanned so far:

| Report | Instances |
|---|---:|
| Supply Plan Detail | ~24 detected in this pass (catalog previously flagged ~40 total `WH## SI`-style measures) |
| Inv Management | 7 (`Whse ECR/1/5/15/17/28/42 - SI`) |

Same shape both times: identical DAX, only the hardcoded warehouse-code filter
differs. No other scanned report shows this pattern at meaningful scale — it appears
specific to models built directly on `SI at US Warehouse` / `SupplyPlanDetail`-style
sources. Strengthens the case (already noted in Inv Management's analysis) for a
single governed "Shippable Inventory" measure sliced by a real `DimWarehouse`,
reusable across both reports rather than authored twice.

---

## 5 — Cross-report pattern: undocumented business constants

| Constant | Report | What it does |
|---|---|---|
| `× 3` | Forecast Accuracy (ItWh) | Multiplier in the net-sales financial-impact formula (previously found) |
| `+ 91 days` | Forecast Accuracy (ItWh) | Historical baseline date shift (previously found) |
| `0.1` (10%) | Demand Review | Default bias-alert threshold (`Bias Threshold Value`) |
| `0.15` (15%) | Demand Review | Default forecast-change alert threshold (`FC Change Value`) |
| `1.4 ×` Safety Stock | Demand Review | Threshold defining "excess" finished-goods inventory (`SI > 1.4 × SS`) |
| `160,000 / 58,000 / 218,000` | Inv Management | Network-wide warehouse capacity ceiling by product type |
| Vendor `633312`, `643509` | Inv Management | Hardcoded "overseas vendor" classification |

Unlike Forecast Accuracy's `×3`/`+91-day`, the Demand Review thresholds (0.1, 0.15,
1.4×) at least have plain-language labels attached ("Bias Threshold," "FC Change
Value") — better documented in intent, but still no visible record of *why* those
specific values were chosen or who owns changing them. Given `Demand Review` is
flagged elsewhere in this repo as arguably the single most strategically important
report in the estate (feeds the S&OP consensus process), **its threshold constants
deserve a dedicated interview question**, distinct from the general "what are the
magic numbers" seed already in Prompt #1's closing block.

---

## 6 — Recommendation: priority order for the next full Prompt #1 runs

Given the roadmap's remaining representatives (Demand Review, DvC-WanekMillenium,
Weekly Trend Analysis, Plan Drop 1) plus this pass's findings, suggested order:

1. **Inventory Health** (`Inventory_Health.md`) — not on the original representative
   list, but the identity-resolution finding above makes this high-value and
   time-sensitive to confirm while it's fresh.
2. **Demand Review** — already a planned representative; largest and most
   strategically important model in the estate (46 tables / 230 measures); the
   0.1/0.15/1.4× thresholds found here warrant full treatment, not just a catalog
   note.
3. **Weekly Trend Analysis** — planned representative; smaller (11 tables/15
   measures), a fast, contained win before tackling Demand Review's size.
4. **DvC-WanekMillenium** — planned representative, Manufacturing cluster.
5. **Plan Drop 1** — planned representative, but genuinely thin (1 table, 0 explicit
   measures) — full Prompt #1 here will be quick; low risk to defer to last.

**Not recommended yet:** Product Review (NEW) and Safety Stock Analysis are large
(129 and 91 measures) and not on the current representative list — hold until the
5 planned representatives plus Inventory Health are done, per the "recalibrate after
≥5 reports" open item from the handoff.

---

## 7 — What this pass does *not* do

This is a pattern-matching scan over existing model-summary text, not a live model
pull — it inherits every limitation already noted in the Inv Management analysis
(summaries may be stale, may not capture every measure/comment, and were written by
a prior team for a different purpose than Eagle Eye discovery). It also does not
touch the 24 summaries' full "Decisions supported" narrative depth — that level of
read is what full Prompt #1 is for, and remains the plan for the priority list above.
