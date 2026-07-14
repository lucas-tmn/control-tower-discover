# Sprint 3 — Knowledge Validation Workshop Format

## Objective
Turn Interview-confirmed Decision Knowledge into Validated, business-agreed
knowledge — resolving conflicts and assigning ownership along the way.

## Who attends
- The **Decision Owner / Persona** named in the registry row (B3) — the
  actual person who makes this decision, not their manager, unless they are
  the same.
- One **SME** if the decision spans a domain the owner doesn't fully cover
  (e.g. a data/BI person for metric definitions).
- The **Discovery Lead**, facilitating — not presenting conclusions, asking
  for confirmation.

## Format (30–45 min per decision, batch related decisions in one session
where possible — e.g. all Inventory Health decisions together)

### 1. Present the draft (5 min)
Walk through the registry row as it stands: trigger, rule, action, metric,
data source — including its current Status and any Open Questions.
Frame explicitly as draft: *"here's our best understanding — tell us what's
wrong."*

### 2. Confirm or correct field by field (15–20 min)
Go through Group A–D fields relevant to this decision. For each, ask
directly: *"is this right?"* — don't accept silence as agreement; ask each
person present to respond.

### 3. Resolve open questions and conflicts (10–15 min)
For each Open Question (F4) or Track A/B/C conflict logged in Sprint 2:
present both versions neutrally and ask the owner which is correct, or
whether both are true in different circumstances. Log the resolution and
who confirmed it.

### 4. Confirm ownership and cadence (5 min)
Explicitly confirm B3 (Owner/Persona) and B4 (Cadence) — these determine who
maintains this knowledge going forward (F3, Registry entry owner).

## Conflict resolution protocol
When Track A (model), Track B (interview), and Track C (SOP/shadow process)
disagree, resolve in this order of authority — mirroring the Knowledge
Library's own authority ordering:

1. **Direct confirmation from the decision owner in this workshop** — wins
   over any prior inference.
2. **Interview-confirmed, if the owner isn't present** — wins over model-only
   hypothesis.
3. **Model-only hypothesis** — lowest confidence; treated as a starting
   point only, never as final.

If the owner's live answer contradicts a written SOP, log both: the
decision, and the fact that practice has drifted from documentation — this
is itself a finding worth surfacing to leadership, not something to quietly
overwrite.

## Duplicate detection
Before validating a new decision, check it against already-validated
decisions and candidate Decision Patterns from Sprint 2. If two decisions
share the same trigger/rule/action shape across different reports, consider
merging them into one Decision Pattern with multiple source reports (A5),
rather than keeping duplicates — the same logic that collapsed 879 measures
into 253 signatures applies at the decision level.

## Exit criteria for a decision to become "Validated" (F1)
- Owner has directly confirmed Group B fields in a workshop.
- All Open Questions for this decision are either resolved or explicitly
  accepted as ongoing unknowns (not silently dropped).
- Ownership (F3) and Confidence source (F2) are recorded.

## Output of Sprint 3
Decision Registry rows at Status = Validated, ready to become canonical in
Sprint 4 — plus an explicit list of any decisions that remain contested and
need escalation beyond this workshop format (e.g. cross-team disagreement
on the same decision).
