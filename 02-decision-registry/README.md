# Decision Registry

**Status: 3 decisions drafted, all at Model-only status.** See `registry-index.md`
for the full list.

`Decision_Registry_Schema_v0.2.md` defines the structure (Groups A–F, 30 fields).
The 3 entries in `decisions/` were populated by applying the Sprint 2 method
(`../03-methods/Decision_Discovery_Method.md`) directly to the evidence in
`../01-evidence/track-a-reports/` — no interview has run yet, so every entry is
honestly marked Model-only, with `[Interview]`-sourced fields marked "pending"
rather than guessed.

## What happens here next
1. Run Track B interviews for the personas named in DEC-001/002/003 (Executive/
   Finance, WBR-Leadership/Manager) and update Status to Interview-confirmed.
2. As the remaining 4 representative reports are analyzed, add their decisions
   here following the same pattern (see `registry-index.md`).
3. Once validated (Sprint 3 workshop), rows become canonical.

## Structure
```
02-decision-registry/
├── Decision_Registry_Schema_v0.2.md
├── registry-index.md      one row per decision — start here
└── decisions/
    ├── DEC-001.md          Forecast Accuracy — financial-justification
    ├── DEC-002.md          Forecast Accuracy — performance/governance
    └── DEC-003.md          InventoryHealth_AI — not yet production
```
