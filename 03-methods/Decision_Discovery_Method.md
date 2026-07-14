# Sprint 2 — Decision Discovery Method (v0.1 draft)

**Calibration note:** this method is built from 2 worked examples (Weekly
Trend Analysis, Inventory Health) — both operational decisions. Re-test and
adjust after decomposing 5–10 more reports, especially at least one
performance/governance and one financial-justification decision (per Schema
v0.2 §A7), since those may not fit this method cleanly.

## Objective
Turn Track A/B/C evidence into draft Decision Knowledge entries, using the
Decision Registry Schema v0.2 as the target structure.

## Step-by-step

### Step 1 — Identify a candidate decision from Track A
For each report, ask: what decision does this report's structure imply?
(Not "what does it show" — "what does someone do differently because of
it.") Use the 7-atom decomposition already proven in the Sprint 0 Worked
Examples as the starting shape: trigger, metric(s), rule, action, persona,
owner, data source.

### Step 2 — Draft the registry row at Model-only status
Populate the `[Model]`-sourced fields directly from the report (A3, A5, A6,
C1–C7, D1, D2, D5) and draft hypotheses for the `[Both]` fields (A2, A7, B1,
B3, B4) using the report's structure as inference, not confirmation.
Set Status (F1) = **Model-only (hypothesis)**.

### Step 3 — Cross-check against Track B interview evidence
When an interview covering this decision is available, update every
`[Interview]` field (B2, B5–B8, D3, E2) directly from what the person said —
do not paraphrase toward what the report implied. If the interview
contradicts the model-based hypothesis, log the contradiction rather than
quietly resolving it in favor of one source.
Update Status (F1) = **Interview-confirmed** once B-group fields are filled.

### Step 4 — Cross-check against Track C evidence
If an SOP or shadow-process artifact exists for this decision, compare it
against both the model hypothesis and the interview. Log any conflict as an
Open Question (F4) rather than picking a winner unilaterally — conflicts
get resolved in Sprint 3 (Validation), not invented away here.

### Step 5 — Look for cross-report patterns
As multiple decisions accumulate, check whether the same trigger/rule shape
recurs across reports (the same way 879 measures collapsed to 253
signatures and 10 measure archetypes). A repeating decision shape across
reports is itself a discovery — log it as a candidate **Decision Pattern**
even if the underlying reports differ.

### Step 6 — Escalate what can't be resolved from evidence alone
Anything genuinely unclear — conflicting thresholds, unnamed owners, unclear
escalation paths — goes into Open Questions (F4) and becomes the agenda for
the Sprint 3 validation workshop for that decision. Do not guess to fill a
field; an honest blank is more useful than a confident wrong answer.

## Output of Sprint 2
A set of Decision Registry rows, each at Status = Model-only or
Interview-confirmed (never yet Validated — that's Sprint 3's job), plus a
running list of candidate Decision Patterns and unresolved Open Questions.

## Anti-patterns to avoid
- Filling every field for speed, including ones with no real evidence yet —
  a populated-looking row with invented content is worse than an honest gap.
- Resolving a Track A vs Track B conflict yourself instead of logging it for
  Sprint 3 — validation is a business function, not a Discovery Lead call.
- Treating "Model-only" status as good enough to build on — per Repository
  Principle "Evidence before Architecture," nothing gets built on a
  Model-only row until it's at least Interview-confirmed.
