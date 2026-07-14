# Architectural Hypothesis Backlog

## Lifecycle
Proposed → Under Investigation → Evidence Collected → Validated → Canonical

## Backlog

| # | Hypothesis | Status | Grounding evidence | Open question |
|---|---|---|---|---|
| H1 | Decision Context is the primary discovery object | **Under Investigation** | 26 models, 879 measures reviewed | Where is the boundary between a Decision Context and its component atoms (metric, rule, action, persona)? Is Decision Context a container for these atoms, or a peer to them? See `Worked_Examples.md` — this is the exact question the worked examples are built to test. |
| H2 | Metrics are reusable knowledge objects | **Evidence Collected** | 879 measures collapse to 253 distinct signatures; 64 signatures already shared across models | Validates the *reuse* half. Does not yet prove a metric is meaningful without its decision context attached — untested until H1 resolves. |
| H3 | Reports and interviews should answer the same discovery questions | **Proposed** | No interviews conducted yet (Track B not started) | What is the actual question set? Draft and pilot against 1–2 interviewees before Track B scales. |
| H4 | The 26-model sprawl is quantifiable, not anecdotal | **Validated** | 26 models → 6 conformed dimensions + 9 fact grains; 879 → 253 measure signatures; 10 exact-duplicate queries; 10 measure archetypes | This is the strongest evidence Discovery has produced so far — should anchor the Sprint 0/1 conversation with Devon, not be left out of the review pack. |

## Note on Sprint 4 overlap
Some registry-shaping work (Decision Registry Schema v0.2) is already
underway ahead of its formal Sprint 4 slot. This is acceptable as
preparatory drafting but should not be read as Sprint 4 having started —
it remains gated on H1 resolving and Sprint 2/3 validation.
