# Eagle Eye — Decision Registry Schema (v0.2)

**The canonical structure for capturing how Ashley's supply chain makes decisions**
Ashley Furniture · Supply Chain Systems · Global Capability Center
*v0.2 · 2026-07-02 · Owner: Lucas Trinh (PO) · For review with: Cherry Bui (Data Lead)*

---

## What's new in v0.2 (for Cherry's review)

v0.2 is shaped by analyzing a third, very different report — **Forecast Accuracy** (a
72-measure production model that quantifies the *dollar value* of forecast quality) —
alongside the two inventory reports. That report exposed three gaps in v0.1:

- **NEW field A7 — Decision Type.** Not every decision is operational. Forecast Accuracy
  drives *performance/governance* decisions (coach planners, choose horizon) and
  *financial-justification* decisions (prove Logility's value). The schema now classifies
  decision type, because each type needs a different kind of Eagle Eye output.
- **NEW field D5 — Undocumented assumptions / magic numbers.** Distinct from D2 (errors).
  A formula can be *correct* yet rest on an *unverified assumption* — e.g. the unexplained
  `× 3` multiplier and the `+91-day` date-shift in the financial-impact model. These are
  high-risk precisely because they feed executive business cases.
- **NEW field E6 — Financial linkage.** Some decisions have a quantified $-value model
  (wMAPE → net sales). This is what executives and Finance care about, and it must record
  the assumptions it rests on.

Also added: a **third worked example** (Forecast Accuracy) proving the schema holds a
performance/financial report, and a note that **Prompt #1 must grow from 8 → 10 sections**.

*(v0.1 is superseded by this file.)*

---

## 1. Purpose

The Decision Registry is the durable, tool-agnostic asset at the centre of Eagle Eye. Its
unit is **one recurring business decision** — not a dashboard, report, or metric. It answers,
for every decision Ashley's supply chain makes: *who makes it, from what data, using which
metrics, what they do next, and whether AI can help.* It organizes discovery now, and later
grounds the Eagle Eye AI/Copilot layer.

---

## 2. Three design principles

**2.1 Every field is tagged by source** — this is what makes the schema drive the prompts:
`[Model]` (read from semantic model, Prompt #1) · `[Interview]` (ask a business user,
Prompt #2) · `[Both]` (model gives a hypothesis, interview confirms) · `[Derived]` (we
compute) · `[System]` (housekeeping).

**2.2 The unit is the decision** — a report may serve many decisions; a decision may draw on
many reports/facts. Many-to-many is expected.

**2.3 Truthfulness is a first-class field** — a metric can *exist* and still be untrustworthy:
a hardcoded placeholder, a logic error, an ungoverned source, an *undocumented assumption*,
or simply distrusted by users. The schema records each explicitly so Eagle Eye never builds
a confident answer on a bad number.

**Core vs Extended** — fields marked ⭐ are the core set (fill for every decision first pass);
the rest deepen over time.

---

## 3. The schema

### Group A — Identity & Classification

> **WHY** — Before we can reason about a decision, we must be able to *name it, find it, and
> classify it*. Without a stable identity and type, decisions blur into each other and we can't
> deduplicate, group, or prioritize them.
> **WHAT** — Give each decision a unique ID and name, locate the report(s)/workspace that support
> it today, and classify its domain and type (operational vs performance vs financial).
> **OUTCOME** — A clean, deduplicated, classifiable *inventory of decisions* — the index the whole
> registry is organized by, and the thing we can count, filter, and rank.

| # | Field | Source | Core | Description / example |
|---|-------|--------|:----:|------------------------|
| A1 | **Decision ID** | [System] | ⭐ | `DEC-014` |
| A2 | **Decision Name** | [Both] | ⭐ | Verb-led. "Prevent stock-out on at-risk SKU" |
| A3 | **Domain** | [Model/Both] | ⭐ | Demand · Forecast · Supply · Inventory · Production · Receipts · On-Time · Quality · Finance |
| A4 | **Sub-process** | [Both] | | e.g. "safety-stock calibration" |
| A5 | **Source report(s)** | [Model] | ⭐ | Report(s) supporting this decision (many-to-many) |
| A6 | **Workspace** | [Model] | | e.g. SCP Team · Supply Chain Analytics-Premium |
| **A7** | **Decision Type** ⟵ *NEW* | [Both] | ⭐ | **Operational** (handle goods: expedite/transfer) · **Performance/Governance** (manage the planning process: coach planners, pick horizon) · **Financial-Justification** (investment case, $-impact) |

### Group B — The Decision (the heart — Cherry's focus)

> **WHY** — This is the whole point of Eagle Eye: not "what does the report show" but "what does a
> human *do*." A dashboard is only the start of a decision; the action taken afterward — and the
> shadow tools used to take it — is what we ultimately want to assist or automate. This group is
> where we capture the *closed decision loop*, which lives in people's heads, not in the model.
> **WHAT** — Capture the real question asked, what triggers it, who decides and how often, the
> concrete action taken (especially when the number goes wrong), the escalation path, and any
> tools used outside Power BI.
> **OUTCOME** — A map of the *actual decision behaviour* — the raw material for Eagle Eye's
> Recommendations feature and the strongest signal of where AI can remove real work.

| # | Field | Source | Core | Description / example |
|---|-------|--------|:----:|------------------------|
| B1 | **Decision Question** | [Both] | ⭐ | User's words. "Which SKUs will stock out in <5 weeks?" |
| B2 | **Trigger** | [Interview] | ⭐ | Threshold breach · fixed cadence · exception alert |
| B3 | **Decision Owner / Persona** | [Both] | ⭐ | Executive · WBR-Leadership · Operational Planner · Advanced Analyst (+ specific role: Manager, S&OP Lead, Quality, Sales, Finance) |
| B4 | **Cadence** | [Both] | ⭐ | Daily · Weekly · Monthly · Quarterly · Ad hoc |
| B5 | **Workflow Action(s)** | [Interview] | ⭐ | Expedite · Transfer · Rebalance · Markdown · Disco · Change supplier · Adjust SS · Override forecast · Coach planner |
| B6 | **Action when off-track** | [Interview] | ⭐ | *Cherry's key question.* "When [metric] goes bad, what's your next concrete step?" |
| B7 | **Escalation path** | [Interview] | | Who they escalate to, wait time, where finalized |
| B8 | **Shadow tools** | [Interview] | ⭐ | Outside Power BI: Excel · email · Slack · meetings — and why |

### Group C — Metrics & Data (semantic-layer / Model side)

> **WHY** — A decision is only as good as the numbers behind it. To govern metrics (one definition
> per KPI) and to let AI answer reliably, we must know exactly what each metric means, at what grain,
> from what source. This group is the foundation of the future KPI/semantic layer, and it's what an
> AI must "know" to answer a question at the right grain without mixing levels.
> **WHAT** — Record the metrics that drive the decision, their plain-business meaning, their grain,
> the dimensions they slice by, the underlying fact/source object, its lineage, and whether it needs
> latest-only or full history.
> **OUTCOME** — A metric-and-data map per decision — the seed of the governed semantic layer and the
> grain/context an AI needs to answer correctly.

| # | Field | Source | Core | Description / example |
|---|-------|--------|:----:|------------------------|
| C1 | **Key Metric(s) / KPI** | [Model] | ⭐ | "Weeks of Supply", "wMAPE", "In-Stock Ratio" |
| C2 | **Metric definition (plain)** | [Model] | ⭐ | Plain-business meaning |
| C3 | **Grain** | [Model] | ⭐ | item · item-WH · cust-item-WH; day/week/month; + forecast horizon where relevant |
| C4 | **Conformed dimension(s)** | [Model] | | Product · Date · Warehouse · Vendor · Customer · ProductionResource |
| C5 | **Fact grain / source object** | [Model] | | e.g. FactInventoryPosition · DemandForecastSnapshot |
| C6 | **Data source & lineage** | [Model] | ⭐ | EDW · dataflow · SharePoint · personal Excel · iSeries |
| C7 | **Snapshot strategy** | [Model] | | latest (operational) · history (accuracy/trend) |

### Group D — Trust & Data Readiness

> **WHY** — This is Eagle Eye's guardrail against its own biggest risk: a confident, wrong answer.
> A metric can *exist* and still be untrustworthy — ungoverned source, hardcoded placeholder, logic
> error, an unverified assumption, or simply distrusted by the people who use it. If AI answers on a
> bad number, it does more harm than the dashboards we're replacing. This group decides what is *safe
> to build on now* versus what must be fixed first.
> **WHAT** — Assess each decision's data readiness, flag known integrity issues and undocumented
> assumptions from the model, and capture whether users actually trust the number (or recompute it
> by hand).
> **OUTCOME** — A per-decision *trust verdict* — the data-readiness gate that tells us which decisions
> Eagle Eye can safely support today, and which are blocked pending governance or a fix.

| # | Field | Source | Core | Description / example |
|---|-------|--------|:----:|------------------------|
| D1 | **Data readiness** | [Model] | ⭐ | Governed · Partially governed · Ungoverned |
| D2 | **Metric integrity / known issues** | [Model] | ⭐ | Hardcoded placeholder · DAX logic error · broken formula *(things that are **wrong**)* |
| D3 | **Metric trust (user)** | [Interview] | ⭐ | Do users trust it? Recompute by hand? Which numbers do they *not* trust? |
| D4 | **Cross-model drift / duplication** | [Model] | | Same concept defined differently *across models* (ABC in two tables; lifecycle drift) |
| **D5** | **Undocumented assumptions / magic numbers** ⟵ *NEW* | [Model/Both] | ⭐ | Constants or logic that may be **correct but unverified** — e.g. `×3` impact multiplier, `+91-day` shift, naive-lag 2M vs 3M. Flag as "confirm with owner". Distinct from D2 (errors) |

### Group E — Eagle Eye Assessment

> **WHY** — Not every decision should be automated, migrated, or even kept. With potentially
> thousands of decisions, we need a consistent way to decide *where Eagle Eye should invest first*
> and *how far to take each one*. This group turns raw discovery into prioritization and a roadmap —
> and enforces "adoption/value first, not build-everything."
> **WHAT** — Score each decision's AI-suitability and business value, assign a rationalization
> verdict (keep/merge/migrate/retire/AI-candidate), set a maturity target (assisted→touchless) and a
> persona access tier, and note any financial linkage.
> **OUTCOME** — A prioritized, roadmap-ready view of the decision estate — the ranked backlog that
> tells us what to build, in what order, and how far.

| # | Field | Source | Core | Description / example |
|---|-------|--------|:----:|------------------------|
| E1 | **AI suitability score** | [Derived] | ⭐ | Cherry's 4 criteria (§4): Frequency · Data availability · Action clarity · Business impact |
| E2 | **Business impact / value at stake** | [Both] | ⭐ | Cost of a wrong call ($, service, capital) |
| E3 | **Rationalization verdict** | [Derived] | ⭐ | Keep · Merge · Migrate · Retire · AI-candidate |
| E4 | **Maturity target** | [Both] | | Assisted → Recommended → Touchless |
| E5 | **Persona access tier** | [Both] | | Standardized scorecard · guided exploration · deep analyst (controlled self-service) |
| **E6** | **Financial linkage** ⟵ *NEW* | [Both] | | Does the decision have a quantified $-value model? What does it rest on? *(e.g. wMAPE → net sales via SL% × GM% × 3 — assumption unverified)* |

### Group F — Governance & Status

> **WHY** — The registry is a *living* asset built from two sources (model + interviews) over time.
> We must know how far each entry has matured, whether it's a model-only hypothesis or user-confirmed
> truth, who owns it, and what's still open. Without this, no one can trust the registry itself — and
> it quietly rots, exactly like the estate it replaces.
> **WHAT** — Track each row's status and confidence (hypothesis vs confirmed), its owner, the open
> questions still to resolve, and the last-updated date.
> **OUTCOME** — A trustworthy, maintainable registry with clear provenance — so anyone reading a row
> knows how solid it is and what remains to confirm.

| # | Field | Source | Core | Description / example |
|---|-------|--------|:----:|------------------------|
| F1 | **Status** | [System] | ⭐ | Draft · Model-only (hypothesis) · Interview-confirmed · Validated |
| F2 | **Confidence / source of truth** | [System] | ⭐ | Confirmed by user, or inferred from model only? |
| F3 | **Registry entry owner** | [System] | | Who maintains this row |
| F4 | **Open questions** | [Both] | | Unknowns to resolve (feeds the interview) |
| F5 | **Last updated** | [System] | ⭐ | Date |

---

## 4. AI Suitability score (E1) — Cherry's four criteria

Scored Low / Med / High; a strong AI candidate needs most at High:
1. **Decision frequency** — recurs often? (rare → rarely justifies AI)
2. **Data availability** — enough *governed, historical* data? (ties to D1/D2/D5)
3. **Action clarity** — a specific action can be recommended, vs purely interpretive?
4. **Business impact** — cost of a wrong decision? (low → deprioritize)

---

## 5. Worked examples (proving the schema holds three contrasting reports)

### Example 1 — *Inventory Health* (ungoverned, operational, action-rich)

| Field | Value |
|-------|-------|
| A2 Name / **A7 Type** | Prevent stock-out on at-risk SKU / **Operational** |
| A3 Domain | Inventory |
| B1 Question | Which SKUs approach stock-out (WOS < 5 weeks)? |
| B3 Persona | Operational Planner |
| B5 Action(s) | Expedite · Substitution · Allocation |
| C1 Metric | Weeks of Supply; StockOutCat flag |
| C6 Source | ⚠ Ungoverned — personal OneDrive Excel |
| D1 Readiness | **Ungoverned** |
| D2 Integrity | ⚠ **WOS hardcoded = 10**, ignores real column |
| D5 Assumptions | — |
| E3 Verdict | Migrate (high value) — **blocked on data** |
| F1 Status | Model-only (hypothesis) |

### Example 2 — *AFI On Hand Values Trend* (governed, operational, simple)

| Field | Value |
|-------|-------|
| A2 Name / **A7 Type** | Rebalance warehouse cube volume / **Operational** |
| A3 Domain | Inventory |
| B1 Question | Which warehouses hold disproportionate cube volume? |
| B3 Persona | Operational Planner / Ops |
| B5 Action(s) | Transfer order · Space rebalancing |
| C1 Metric | L2_OH_Cubes (on-hand cubic volume) |
| C6 Source | Governed EDW (Azure SQL) |
| C7 Snapshot | History (weekly) |
| D1 Readiness | **Governed** |
| D2 Integrity | ⚠ Minor: no ISNULL guard on cubes |
| E3 Verdict | Keep / AI-candidate |

### Example 3 — *Forecast Accuracy* (governed, financial-justification) ⟵ exercises the NEW fields

| Field | Value |
|-------|-------|
| A2 Name / **A7 Type** | Quantify $-value of forecast-accuracy improvement / **Financial-Justification** |
| A3 Domain | Forecast |
| A5 Source report | SCP Forecast Accuracy |
| B1 Question | What is the financial impact of an X% wMAPE improvement? (What-If slider 0–10.5%) |
| B3 Persona | Executive / Finance |
| B4 Cadence | Quarterly / Annual planning |
| B5 Action(s) | Build/justify investment case (e.g. Logility) |
| C1 Metric | Forecast Impact - Net Sales; wMAPE; Forecast Value Added |
| C3 Grain | item × WH × cust-group × fiscal month × 5 horizons (2W/30/60/90/120D) |
| C6 Source | Governed EDW + dataflow; ⚠ **SharePoint planner lists (manual)** |
| C7 Snapshot | History (multi-horizon + 91-day-shifted baseline) |
| D1 Readiness | Partially governed (EDW clean; SharePoint manual) |
| D2 Integrity | Clean — no hardcoded placeholders, no logic errors |
| **D5 Assumptions** | ⚠ **`×3` multiplier unexplained · `+91-day` shift undocumented · naive-lag 2M vs 3M (MASE not comparable)** |
| E1 AI suitability | Freq: Med · Data: High · Action clarity: Med · Impact: High |
| **E6 Financial linkage** | **YES** — wMAPE → Net Sales × (1−SL%) × GM% × 3 × Δ-wMAPE. Rests on unverified `×3` assumption → validate before exec use |
| E3 Verdict | Keep (production) — validate assumptions first |
| F4 Open questions | What is `×3`? Is 91-day shift correct? Are SharePoint planner lists current? |

**Compact Example 4 — *Forecast Accuracy*, performance type:** "Which planners have best/worst
wMAPE → coaching / portfolio rebalance" · **A7 = Performance/Governance** · Persona = WBR-Leadership /
Manager · ⚠ D5: `Team` column hardcodes ~20 planner IDs in a SWITCH — breaks silently when staff
change · Shadow/interview needed: who maintains the SharePoint planner list.

**What the four prove:** the same schema now captures operational, financial-justification, and
performance decisions; governed and ungoverned data; and — crucially — the D5/E6 fields separate
"clean but resting on an unverified assumption" (Forecast Accuracy) from "outright broken"
(Inventory Health) from "safe" (AFI On Hand). Without D5, a *clean-looking* financial model built
on an unexplained `×3` would look fully trustworthy. It isn't — until someone confirms the `×3`.

---

## 6. How this schema drives the prompts (updated for v0.2)

| Prompt | Fills these fields |
|--------|--------------------|
| **Prompt #1 — Data Discovery (read model)** | A5–A7, C1–C7, D1–D2, **D5**, D4, **E6 (partial)** + hypotheses for A2–A3, B1, B3–B4, E1, E3 |
| **Prompt #2 — Business Discovery (interview)** | B2, B5–B8, D3, E2 + confirm all `[Both]` fields |
| **Us (synthesis)** | E1, E3, E4, E5, E6 + reconcile the two sources |

**Prompt #1 must grow 8 → 10 sections** to feed the new fields:
- **New §9 — Business assumptions / magic numbers** → feeds D5 (flag every unexplained
  constant/date-shift, especially in financial or time logic).
- **New §10 — Comparability / consistency** → feeds D5/D4 (same metric defined differently
  across tables or periods that breaks comparison — e.g. the 2M vs 3M naive lag).
- Plus an **"Interview seeds"** closing block → pre-drafts the B5/B6 questions for Prompt #2.

---

## 7. Format & where it lives

**Primary form: a flat, structured table** — one row per decision, columns = fields above.
Best for discovery entry, filtering, and a Fabric/Confluence/SharePoint-list home. Domain (A3)
and Decision Type (A7) give natural grouping *views* without a nested structure.

**Home: a governed location with an owner** (Confluence / SharePoint list / Fabric glossary) —
not a throwaway Excel, or the registry becomes "dashboard #3,001." Matches Cherry's Data Catalog
thinking (owner · definition · lineage · last-updated).

---

## 8. Open design questions (for Cherry)

1. **Persona vocabulary** — lock the list. Devon named four (Executive / WBR / Operational
   Planner / Advanced Analyst); reports surfaced Manager, S&OP Lead, Quality, Sales, Finance.
   Sub-roles under the four, or additional personas?
2. **Decision granularity** — how fine is one "decision"? Suggest: one recurring question +
   one owner + one cadence = one decision.
3. **Decision Type (A7)** — are three types enough (Operational / Performance / Financial), or
   do you see a fourth (e.g. Strategic/Network-design)?
4. **AI suitability scoring** — simple Low/Med/High, or a weighted numeric score?
5. **Today's source vs target gold** — should C4/C5 reference the *future* gold model (6 dims,
   9 facts) as well as today's drifted tables, so the registry is forward-looking? *(Suggest: capture both.)*
6. **D5 severity** — do we need a severity flag on assumptions (blocker vs note), given some
   (like the `×3`) can invalidate an executive business case?

---

*Companion to: Decision Intelligence Framework & Workstreams. v0.2 — to be pressure-tested with
Cherry, then used to upgrade Prompt #1 (8→10 sections) and author Prompt #2.*
