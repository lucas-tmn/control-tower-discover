# Sprint 4 — Decision Intelligence Foundation: Registry Population Process

## Objective
Move Validated Decision Knowledge (Sprint 3 output) into the canonical,
governed Decision Registry — the reusable asset Eagle Eye is built on.

## Prerequisite
Every row entering this process must be at Status (F1) = **Validated**.
Model-only or Interview-confirmed rows do not get promoted — per Repository
Principle "Knowledge is promoted, not created," promotion is a statement
that something has earned trust, not a formatting step.

## Registry structure
Use Decision Registry Schema v0.2 as-is (Groups A–F, 30 fields, ⭐-marked
core set filled first). Do not redesign the schema at this stage — the 6
open design questions logged in Schema v0.2 §8 (persona vocabulary, decision
granularity, Decision Type completeness, AI-suitability scoring, gold-model
referencing, D5 severity) should be resolved with input from real Sprint 2/3
data before schema changes, not before.

## Population steps

### 1. Final field completion
Fill any remaining Extended (non-⭐) fields now that the decision is
validated — particularly C4 (Conformed dimension), C5 (Fact grain), since
Sprint 4 is where the registry should start referencing the *target* gold
model (6 dimensions, 9 fact grains) alongside today's source tables, per
Schema v0.2 open question 5.

### 2. Knowledge relationships
Link each decision to:
- Other decisions sharing a Decision Pattern (from Sprint 2/3)
- The conformed dimension(s) and fact grain(s) it depends on
- Any other decision it feeds or depends on (many-to-many, per Schema
  principle 2.2)

### 3. AI grounding metadata
Attach the fields needed later by Sprint 5 without doing Sprint 5's
assessment yet: E1 (AI suitability inputs), E6 (Financial linkage, where
applicable). This is metadata capture, not an AI-readiness verdict.

### 4. Governance placement
Store the registry in a governed, owned location (per Schema v0.2 §7) —
not a personal file. For the GitHub repo version of this work, that means:
a structured, versioned file (e.g. one table or one file per decision with
consistent front-matter) with a named owner (F3) per row, not prose
scattered across markdown.

### 5. Repository hygiene check
Before adding a new decision file to the repo, confirm it is not an empty
placeholder — every file added at this stage must have all ⭐ core fields
filled and Status = Validated. This is the gate the earlier "No empty
scaffolding" principle exists to enforce at the point it matters most.

## Knowledge Repository structure (for the GitHub repo)
Suggested layout once populating begins:

```
decision-registry/
├── decisions/
│   ├── DEC-001.md   (one file per decision, following Schema v0.2 fields)
│   ├── DEC-002.md
│   └── ...
├── decision-patterns/
│   └── PATTERN-001.md   (cross-report recurring shapes)
├── dimensions/          (6 conformed dimensions — already designed)
├── facts/               (9 fact grains — already designed)
└── registry-index.md    (one row per decision — ID, name, domain, status, owner)
```

## Output of Sprint 4
A searchable, governed Decision Registry — the first version of the
"reusable Decision Knowledge asset" the Roadmap names as Sprint 4's success
criterion — ready for Sprint 5 to assess against.
