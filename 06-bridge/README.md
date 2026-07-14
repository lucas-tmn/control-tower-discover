---
type: Guide
title: Bridge Layer — AS-IS ↔ TO-BE Map
description: How the forensic evidence layer (01-evidence, current reporting estate) connects to the governed knowledge bundle (05-okf-bundle, target-state definitions), and how to use the four bridge maps.
tags: [bridge, as-is, to-be, governance, eagle-eye, control-tower]
timestamp: 2026-07-09
status: draft
---

# 06-bridge — the AS-IS ↔ TO-BE map

This repo holds two bodies of knowledge produced independently:

| Layer | Where | Nature | Question it answers |
|---|---|---|---|
| **AS-IS** | `01-evidence/` + `02-decision-registry/` | Forensic, descriptive — what the 25-report Power BI estate *actually does today*, including bugs, magic numbers, duplications, and the decisions it supports | "What is really happening?" |
| **TO-BE** | `05-okf-bundle/` | Normative, governed — Robert's Open Knowledge Format bundle defining target-state metrics, entities, glossary, datasets (SupplyChain_Gold), playbooks, and processes | "What should be happening?" |

Neither layer is complete alone. The AS-IS layer finds problems but doesn't define
the destination; the TO-BE layer defines destinations but has explicit
`[FILL IN: …]` gaps and doesn't know what the estate currently does. **This bridge
directory is where the two meet.** Its four maps:

| Map | What it connects | Primary use |
|---|---|---|
| [concept-map.md](concept-map.md) | OKF metrics/entities/glossary ↔ our reports, measures, and systemic patterns (PAT-xx) | Orientation: for any concept, find both its governed definition and its current implementations |
| [gap-fill-candidates.md](gap-fill-candidates.md) | Robert's `[FILL IN]` placeholders ↔ AS-IS constants we discovered | Feed governance: propose current-state values as starting points for approval |
| [decision-playbook-map.md](decision-playbook-map.md) | Decision Registry (DEC-xxx) ↔ OKF playbooks & processes | Show which real decisions each playbook standardizes, and which decisions have no playbook yet |
| [source-migration-map.md](source-migration-map.md) | Current sources (SupplyChain_Enh / SupplyChain_DW / Wholesale_DemandPlanning_AFI / SharePoint) ↔ SupplyChain_Gold targets | Migration planning: what each report would re-point to in the governed layer |

## Reading rules

- Bridge files follow the OKF frontmatter convention from `05-okf-bundle/` so that
  agents reading Robert's bundle can read this layer the same way.
- Links **into** the OKF bundle use paths like `../05-okf-bundle/bundle/metrics/forecast_accuracy.md`.
  Links **into** evidence use paths like `../01-evidence/track-a-reports/Demand_Review_Analysis.md`.
- Every mapping row carries a confidence: **Direct** (same concept, explicitly),
  **Probable** (strong match, minor naming/scope differences), or **Candidate**
  (plausible, needs SME confirmation — usually Robert's).
- Disagreements between AS-IS and TO-BE are findings, not errors — record them
  here, then raise upstream. Do not patch `05-okf-bundle/` directly (see its
  `PROVENANCE.md`).

## Audiences

- **Data analyst team:** start with `source-migration-map.md` and
  `gap-fill-candidates.md` — they translate discovery findings into build work.
- **Devon / leadership:** `decision-playbook-map.md` shows how field-observed
  decisions roll up into standardized processes — the Eagle Eye story in one page.
- **Robert:** `gap-fill-candidates.md` is effectively a pull-request-in-prose
  against the bundle's `[FILL IN]` gaps; `concept-map.md` flags where the estate
  contradicts the bundle.
- **AI agents:** read this file, then `concept-map.md`, before answering any
  question that mixes "current state" and "should be" — the two layers must never
  be silently blended.
