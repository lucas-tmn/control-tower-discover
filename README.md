# Control Tower Discover — Eagle Eye Discovery Program

**Mission:** Discover Ashley's Business Decision Landscape and externalize
organizational decision knowledge into trusted, reusable Decision
Intelligence assets. See `00-foundation/Discovery_Vision.md`.

## The six layers (read this first)

Since 2026-07-09 this repository unifies independently-produced bodies of
knowledge plus the maps and narrative between them:

| Layer | Where | Nature |
|---|---|---|
| **AS-IS** — what the estate actually does | `00-…04-…` (evidence, decision registry, methods, prompts) | Forensic, descriptive: 31 fully-analyzed Power BI models (as of 2026-07-13; includes 2 Purchasing-domain reports, 1 additional Manufacturing report, and 1 newly-discovered Supply/Inventory report added after the original 26-report catalog — see the catalog's addendum), raw `.bim` exports, verified bug log, systemic patterns (some now cross-quantified against the Fabric build), 11 registered decisions, plus `01-evidence/source-model-docs/` — schema-level technical reference for the 3 Manufacturing reports not yet at full business-analysis depth |
| **STRATEGY** — leadership direction and intent | `00-foundation/` (strategy-layer docs) | Devon's Project Summary (authoritative), Leadership Intent, DI Framework & Workstreams, meeting notes, access request brief — merged in 2026-07-13 from a parallel knowledge library; dated late June/early July, so authoritative on *direction*, not current on *execution status* (see `00-foundation/README_Strategy_Layer_Provenance.md`) |
| **TO-BE (conceptual)** — what it should do | `05-okf-bundle/` | Robert's OKF Supply Chain Knowledge Bundle (vendored, do not edit — see its `PROVENANCE.md`): governed metrics, entities, glossary, SupplyChain_Gold datasets, playbooks, processes. Written in Open Knowledge Format for AI agents |
| **BRIDGE** — the map between AS-IS and TO-BE | `06-bridge/` | Concept map, gap-fill candidates (our findings → Robert's `[FILL IN]`s, many now resolved by the Fabric build), decision↔playbook map, source-migration map |
| **TO-BE (concrete)** — the actual engineering build | `07-fabric-build/` | Official Microsoft Fabric workspace repo (vendored, do not edit — see its `PROVENANCE.md`): real gold-layer table definitions with working ETL SQL, a real semantic model, an early-stage Forecast Accuracy report. Owned by the data-engineering team (`@afi-internal/enterprise-data-warehouse-approvers`), not a personal knowledge bundle |
| **BUSINESS HANDBOOK** — domain narrative across all layers | `08-business-handbook/` | Plain-language chapters, 7 domains drafted (Demand Planning, Inventory Health, Supply Planning & Capacity, Manufacturing & Production Capacity, Order Fulfillment, Channel-Specific, Lifecycle Management) — Purchasing chapter planned next — meant to be read and trusted at face value: every claim traces to a source, gaps are stated as gaps |
| **DATA GOVERNANCE PROPOSAL** — platform access model | `09-data-governance/` | Draft proposal (EN + VN) moving Supply Chain from unrestricted EDW self-service to a governed, request-based model — real AS-IS audit (6,489-table EDW dictionary) + Cherry Bui's TO-BE framework (catalog, registry, AAD groups). Not yet reviewed with Cherry |

**Audience guide:** Data analyst team → start at `06-bridge/source-migration-map.md`
and `01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md`. Leadership (Devon)
→ `08-business-handbook/` + `06-bridge/decision-playbook-map.md` +
`02-decision-registry/registry-index.md` + `00-foundation/Devons_Project_Summary_REF-002_AUTHORITATIVE.md`
(her own summary — read this first if reconciling against anything else here).
Robert → `06-bridge/gap-fill-candidates.md`
(a pull-request-in-prose against the bundle's gaps). Data engineering →
`07-fabric-build/` directly, plus anything in `06-bridge/` that references it.
AI agents → read `06-bridge/README.md` before answering anything that mixes
current-state and target-state; never blend layers silently.

**For AI readers:** every file in this repo is either (a) evidence collected
directly from a source (a semantic model, a report catalog, a raw `.bim`), (b) a
method or template ready to run, (c) a governed synthesis with an explicit source
tag, or (d) vendored external knowledge with provenance. Nothing here is invented
content presented as fact — ambiguity is flagged inline (see
`00-foundation/Repository_Principles.md`, principle 1). For "how does Ashley make
decision X" prefer `02-decision-registry/`; for "what should metric Y mean" prefer
`05-okf-bundle/`; for "how do those two relate" use `06-bridge/`.

## Program status (6 sprints)

| Sprint | Name | Status | Where it lives |
|---|---|---|---|
| 0 | Foundation | **Done** (v1.2) | `00-foundation/` |
| 1 | Evidence Discovery | **In progress** — Track A: 31 full Prompt #1 analyses as of 2026-07-13 (all 6 planned representatives covered or superseded; +2 Purchasing reports, +1 additional Manufacturing report, +1 newly-discovered Supply/Inventory report since the base 26 — catalog addendum has details); 21 raw `.bim` models vendored; 11 decisions in registry (5 more identified in the Rolling Report analysis, not yet registered — by design, see registry-index.md policy); synthesis layer live (Systemic Patterns Registry, Bug Findings Log). Manufacturing & Capacity group now at 2 of 5 reports full-depth (was 1 of 5) — has its own handbook chapter now. Track B strategy upgraded to bug-led "gift" protocol; Track B/C fieldwork not started | `01-evidence/` |
| 2 | Decision Discovery | Method ready; recalibration trigger met — bridge layer (`06-bridge/`) is the recalibrated direction | `03-methods/Decision_Discovery_Method.md` |
| 3 | Knowledge Validation | Method ready, not yet run | `03-methods/Validation_Workshop_Format.md` |
| 4 | Decision Intelligence Foundation | Method ready, not yet run | `03-methods/Registry_Population_Process.md` |
| 5 | AI Readiness | Method ready, not yet run | `03-methods/AI_Readiness_Assessment_Framework.md` |

## Repo structure

```
control-tower-discover/
├── 00-foundation/              Sprint 0 — vision, charter, operating model,
│                                hypothesis backlog, worked examples,
│                                repository principles, sign-off, external
│                                market research (Lessons_From_The_Market.md),
│                                and the strategy layer (Devon's Project
│                                Summary, Leadership Intent, DI Framework,
│                                meeting notes — merged 2026-07-13, see
│                                README_Strategy_Layer_Provenance.md)
├── 01-evidence/                Sprint 1 — Evidence Discovery (AS-IS layer)
│   ├── track-a-reports/        30 per-report Prompt #1 analyses (2026-07-13)
│   │   ├── _catalog/           catalog, cross-report scans, Systemic
│   │   │                        Patterns Registry, Bug Findings Log
│   │   │                        (catalog now has an addendum section for
│   │   │                        reports found after the original 26 —
│   │   │                        Supplier ABC, Supplier On-Time, Rolling
│   │   │                        Report, Plan Detail Timeline)
│   │   └── bim/                21 raw .bim semantic-model exports
│   │                            (verification layer)
│   ├── source-model-docs/      Schema-level technical reference (tables, DAX,
│   │                            relationships) for the 3 Manufacturing
│   │                            reports still below full business-analysis
│   │                            depth — merged 2026-07-13
│   ├── track-b-interviews/     Business Discovery interview guide (template)
│   └── track-c-additional-evidence/   SOP/shadow-process template
├── 02-decision-registry/       Schema v0.2 + 11 registered decisions (DEC-001…011)
├── 03-methods/                 Ready-to-run methods for Sprint 2–5
├── 04-prompts/                 Prompt #1 (Data Discovery), 10 sections
├── 05-okf-bundle/              TO-BE layer, conceptual — Robert's OKF bundle
│                                (vendored; see PROVENANCE.md; do not edit directly)
├── 06-bridge/                  AS-IS ↔ TO-BE maps (concept, gap-fill,
│                                decision↔playbook, source migration)
├── 07-fabric-build/             TO-BE layer, concrete — the actual Microsoft
│                                Fabric build (vendored; see PROVENANCE.md;
│                                do not edit directly)
├── 08-business-handbook/        Domain-organized business narrative
│                                cutting across all layers (7 chapters drafted;
│                                Purchasing planned next)
└── 09-data-governance/          Draft governance proposal (EN+VN): EDW access
                                 audit + Cherry's TO-BE framework, source-evidence/
                                 vendors the raw table dictionary + her recommendation
```

## Current priorities (Track A — Sprint 1)

6 reports chosen as cluster representatives for full Prompt #1 analysis:

| Cluster | Representative | Status |
|---|---|---|
| Forecast Accuracy | Forecast Accuracy (SCP Forecast Accuracy model) | ✅ Done |
| Supply & Inventory | Inv Management | ✅ Done |
| Manufacturing | DvC-WanekMillenium | Pending |
| Demand/Forecast | Demand Review | ✅ Done |
| Demand/Forecast | Weekly Trend Analysis | ✅ Done |
| Lifecycle | Plan Drop 1 | Pending |

Note: `InventoryHealth_AI` was also analyzed, but is a confirmed prototype
(100% hardcoded data, AI narrative disabled, never connected to live data) —
not a decision-relevant production report. Kept as evidence of estate
sprawl, not as a cluster representative. See
`01-evidence/track-a-reports/InventoryHealth_AI_Analysis.md`.

**Update 2026-07-08 — 12 full analyses complete.** The run order deviated from
the representative list (that's fine — the list is a prioritization tool, not a
gate). All analyses in `01-evidence/track-a-reports/`. From 2026-07-08 onward,
analyses are accompanied by the raw `.bim` semantic-model exports, enabling
independent verification of findings (several key findings are ✅
.bim-verified — see `_catalog/Bug_Findings_Log.md`):

| Report | Status |
|---|---|
| Forecast Accuracy (SCP model) | ✅ Done (v2 deep re-run) |
| Forecast Accuracy CustItWh / ItWh | ✅ Done — **3 sibling forecast-accuracy models analyzed**, confirmed threshold/logic divergence (PAT-03) |
| Demand Review | ✅ Done — densest decision surface (~10 decisions; 4 registered as DEC-008–011) |
| Inv Management | ✅ Done (live-workspace re-run) |
| InventoryHealth_AI | ✅ Done — confirmed prototype |
| AFT_SI-SS_PSW · Act+Fcst WNK/MILL · Amazon POS | ✅ Done |
| Safety Stock · Weekly Trend · On Time % | ✅ Done |
| **Batch of 2026-07-09 (13 new):** Product Review (NEW) · GF Act+Fcst · When to Disco v2 · Complete Series In Stock · Consumption Report · Demand Fulfillment · Demand Sensing · Demo_Inventory Health · FCA Services Fee Audit · Forecast Change WoW · GF FC Tool · Planner Assignment · Product Review | ✅ Done |
| Usage Metrics Report | ✅ Analyzed — PBI admin template (31-day window), not a supply-chain report; usage telemetry exists and a data pull from it is the fastest way to confirm which reports are actively used |

Still outstanding, in priority order: **Inventory Health** (identity question —
oldest open item, now further narrowed, see below), **Supply Plan Detail**
(structural anchor for 13/26 models; previously access-blocked),
DvC-WanekMillenium, Plan Drop 1.

**Sprint-2 recalibration trigger met (≥5 reports; now 25).** Marginal value has
shifted from additional single-report depth to synthesis and bridging. Synthesis
documents in `_catalog/`:
- `Systemic_Patterns_Registry.md` — 8 estate-wide patterns (PAT-01…PAT-08),
  each confirmed in ≥2 independent models
- `Bug_Findings_Log.md` — 18 verified/reported defects; doubles as the Track B
  "gift" protocol: approach report owners with a found defect (value-bringing,
  low-threat) instead of an open-ended interview (extraction-framed)

And the recalibrated direction itself: **`06-bridge/`**, mapping this AS-IS
evidence onto the governed TO-BE layer in `05-okf-bundle/`.

All other reports (delta-check tier) are catalogued in
`01-evidence/track-a-reports/_catalog/Report_Catalog_Comprehensive_View.md`,
alongside the cross-report pattern scan in
`01-evidence/track-a-reports/_catalog/Artifact_First_Extraction_Pass.md`
covering all 25 archived model summaries.

## Open, cross-cutting risk

The workspace has at least 3 differently-scoped models sharing "Inventory
Health" in their name (`Demo_Inventory Health`, `InventoryHealth_CurrentDashboard`,
`InventoryHealth_AI`), none confirmed as the production report the original
catalog describes. This is an estate-level discoverability risk, not a
single-report bug — flagged in `00-foundation/Worked_Examples.md`.

**Update 2026-07-07:** the archive's `Inventory_Health.md` model summary (9
tables, 14 measures) describes a **5-bucket classification (Below Max / Over
Target / Excess / High Excess / TIB)** matching the original catalog's
description almost exactly — the strongest candidate found so far for "the
real production report." Not yet confirmed as actually in active use (that
needs usage telemetry, not just artifact matching — see
`Artifact_First_Extraction_Pass.md` §2), but this substantially narrows the
risk. Recommended as the next Prompt #1 target.

**Update 2026-07-09 — second candidate eliminated.** Full analysis of
`Demo_Inventory Health` confirms it is a demo: all data sourced from local
Excel files on a personal OneDrive (see
`01-evidence/track-a-reports/Demo_Inventory_Health_Analysis.md`). With
`InventoryHealth_AI` (prototype) and `Demo_Inventory Health` (demo) both
ruled out, the archive's 5-bucket `Inventory_Health` model is now effectively
the only remaining production candidate. Two confirmation paths: (a) run
Prompt #1 on it directly, and/or (b) pull actual view data from the
workspace's Usage Metrics model (analyzed 2026-07-09 — the telemetry exists,
31-day window).

**New pattern found this pass:** warehouse code `335` is hardcoded (not a
normal filterable dimension member) across 11 of 25 reports, and is
*included* in some "all warehouse" totals and *explicitly excluded* in
others (sometimes within the same model) — a comparability risk if any
cross-report total is ever compared. See `Artifact_First_Extraction_Pass.md`
§3.

**Update 2026-07-07:** a live re-run of Inv Management concluded warehouse `335`
is "Ashley's main distribution center," since that report's entire core model is
deliberately scoped to it.

**Update 2026-07-10 — this conclusion was overreach, now corrected.**
`07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md` (governed
ETL SQL, authored by Robert, dated 2026-06-18) shows 335 belongs to
`WarehouseGroup = 'ASH'` (Ashton) — a group distinct from the core `AFI` warehouses.
This confirms 335 is a real, named, distinct facility, but does **not** confirm it
is "the" primary DC network-wide — that was an inference from limited evidence, not
a stated fact. **Provisionally resolved pending Robert's confirmation** — see
`07-fabric-build/WAREHOUSE_335_RECONCILIATION.md` for the full comparison and the
question queued for him. The underlying comparability risk is unchanged (if
anything sharper): 335/Ashton is a confirmed real warehouse, so any report
inconsistently including/excluding it from "total" figures is inconsistently
scoping a real facility. See `Artifact_First_Extraction_Pass.md` §3 for the full
update.
