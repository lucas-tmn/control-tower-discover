# Decision Registry — Index

One row per decision. This is the entry point — click into a decision file for full
Schema v0.2 detail.

| ID | Name | Domain | Type | Status | Source report | Owner |
|---|---|---|---|---|---|---|
| [DEC-001](decisions/DEC-001.md) | Quantify $-value of forecast-accuracy improvement | Forecast | Financial-Justification | Model-only | Forecast Accuracy | Discovery Lead |
| [DEC-002](decisions/DEC-002.md) | Coach planners / rebalance portfolio by forecast accuracy | Forecast | Performance/Governance | Model-only | Forecast Accuracy | Discovery Lead |
| [DEC-003](decisions/DEC-003.md) | Weekly inventory health check + AI narrative for WBR | Inventory | Mixed | Draft — not production | InventoryHealth_AI | Discovery Lead |
| [DEC-004](decisions/DEC-004.md) | Consolidate or liquidate excess inventory at warehouse 335 | Inventory | Operational | Model-only | Inv Management | Discovery Lead |
| [DEC-005](decisions/DEC-005.md) | Expedite POs or transfer stock to close safety-stock gaps | Supply & Inventory | Operational | Model-only | AFT_SI-SS_PSW | Discovery Lead |
| [DEC-006](decisions/DEC-006.md) | Confirm Wanek/Millennium production capacity covers demand | Manufacturing & Capacity | Operational | Model-only | Act+Fcst by WNK & MILL Prod Resource | Discovery Lead |
| [DEC-007](decisions/DEC-007.md) | Size Ashley's wholesale sell-in to Amazon | Demand/Forecast (eCommerce) | Operational | Model-only | Amazon POS Sales and Forecast | Discovery Lead |
| [DEC-008](decisions/DEC-008.md) | Approve or push back the working forecast vs prior plan | Demand/Forecast | Performance/Governance | Model-only | Demand Review | Discovery Lead |
| [DEC-009](decisions/DEC-009.md) | Flag chronic forecast bias for exception review / planner coaching | Demand/Forecast | Performance/Governance | Model-only | Demand Review | Discovery Lead |
| [DEC-010](decisions/DEC-010.md) | Act on in-month consumption pace vs target (incl. $-at-risk) | Demand/Forecast | Operational + Financial | Model-only | Demand Review | Discovery Lead |
| [DEC-011](decisions/DEC-011.md) | Sign off the RH Bedding channel forecast (manual Excel path) | Demand/Forecast (RH channel) | Operational | Model-only | Demand Review | Discovery Lead |

## What this proves, right now

- **DEC-001 and DEC-002 share one source report** (Forecast Accuracy) but are
  genuinely different decisions with different owners, cadences, and risk profiles —
  the first real, evidence-based confirmation of Schema v0.2's "many decisions per
  report" principle.
- **DEC-003 shows the registry can honestly represent "not ready"** — a decision
  entry doesn't have to pretend a report is production-grade; it can document
  exactly what's missing (D1/D5) so the gap is visible instead of hidden.
- **11 entries now span 9 different reports.** DEC-008–011 all come from Demand
  Review — the densest decision surface found so far (its analysis identifies ~10
  distinct decisions; 4 are registered, the rest are candidates: safety-stock
  adjustment via SI Overage, container expedite/defer, placement at-risk actions,
  lifecycle/drop visibility, YoY growth attribution).
- **DEC-009 is the registry's first people-performance decision** (planner
  coaching driven by automated thresholds) — flagged for extra care before any
  Eagle Eye layer amplifies it.
- **DEC-011 is the first "fix the pipe, not the intelligence" verdict** — its
  gap is data governance (manual Excel path), not analytics.
- **None of the 11 entries are above Model-only/Draft status** — this is expected.
  They move to Interview-confirmed once Track B runs, and Validated once Sprint 3's
  workshop confirms them with the actual decision owners.

## Next entries planned
Track A has grown past the original 26-report catalog: as of 2026-07-13 there
are **30 analysis files** in `01-evidence/track-a-reports/`, including Rolling
Report - Wanek Millen (now fully analyzed — Manufacturing sits at 2 of 5
reports full-depth), two Purchasing-domain reports (Supplier ABC Analysis,
Supplier On-Time Performance — neither was in the original 26), and Plan
Detail Timeline (a distinct report discovered while looking for Supply Plan
Detail — not a replacement for it; see its own analysis for why). Remaining
priority: **Supply Plan Detail** itself — the report the majority of the
estate is structurally anchored to (13 of 26 models use its source), identity
and access still unresolved, oldest open item in this program — plus **Plan
Drop 1** from the original 6 cluster representatives. Several Demand Review
decision candidates remain unregistered (list above) and could be added
without further model analysis, as could the 5 decision candidates surfaced
in the new Rolling Report analysis (§2 of that file). The recalibrated
direction — cross-report synthesis, the `06-bridge/` AS-IS↔TO-BE map, the
vendored `07-fabric-build/` engineering layer, and the `08-business-handbook/`
domain narrative (now 7 chapters, a Purchasing chapter next) — continues to
take priority over registering every remaining candidate decision
individually; new DEC entries should be added when a decision is needed for a
handbook chapter or a Track B conversation, not as a separate backlog to
clear.

