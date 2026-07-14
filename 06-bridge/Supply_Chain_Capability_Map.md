# Supply Chain Capability Map

| Field | Value |
|---|---|
| **Confidence level** | Model-only — synthesized from the Decision Registry, the Business Handbook chapters, and the `06-bridge/` AS-IS↔TO-BE maps. Not yet confirmed with the people who run each capability. Every claim below traces to a specific source file in this repo; gaps are stated as gaps, not implied as complete. |
| **Primary sources** | `02-decision-registry/registry-index.md`, `06-bridge/decision-playbook-map.md`, `06-bridge/concept-map.md`, all 7 chapters in this folder, `05-okf-bundle/bundle/playbooks/index.md`, `05-okf-bundle/bundle/processes/index.md` |
| **Purpose** | Give a PO, DA, leader, or AI agent the end-to-end Supply Chain picture in one page, without reading every evidence file first. |

---

## 1. One-page capability overview

Ashley's Supply Chain decision flow, as currently organized in this repo:

```text
Channel-Specific (Amazon & RH Bedding) ─┐
                                         ▼
                              Demand Planning & Forecast Consensus
                                         │
                                         ▼
                              Supply Planning & Capacity
                                    │           │
                                    ▼           ▼
                              Purchasing   Manufacturing & Production Capacity
                                    │           │
                                    └─────┬─────┘
                                          ▼
                              Inventory Health & Excess Management
                                          │
                                          ▼
                              Order Fulfillment & Customer Service

Lifecycle Management intersects at both ends:
new-item introduction → Demand Planning · discontinuation → Inventory Health
```

**8 capabilities** — 7 have a drafted handbook chapter; **Purchasing** is the
8th, evidence-gathering stage only (chapter not yet written).

---

## 2. Capability detail table

| Capability | Business question | Key decisions (registry) | Current evidence | Target-state asset (OKF) | Open gaps |
|---|---|---|---|---|---|
| **Demand Planning & Forecast Consensus** | Is the working forecast converging to something the business trusts, and is forecast accuracy improving? | DEC-001, DEC-002, DEC-008, DEC-009, DEC-010 (5) | Demand Review, Forecast Accuracy (+2 grain variants), Weekly Trend — chapter drafted | [Forecast Revision](../05-okf-bundle/bundle/playbooks/forecast_revision.md) playbook + [Demand Consensus Meeting](../05-okf-bundle/bundle/processes/demand_consensus_meeting.md) process — **Direct fit** for DEC-008 | DEC-001's ×3/+91-day multiplier is an undocumented assumption feeding an executive $-value model (PAT-06); DEC-009's coaching thresholds (25/20/15%) need governance approval before becoming a playbook |
| **Supply Planning & Capacity** | Where are safety-stock gaps, and should we expedite or transfer stock to close them? | DEC-005 (1) | AFT_SI-SS_PSW — chapter explicitly does **not** yet cover Supply Plan Detail itself | [Stockout Escalation](../05-okf-bundle/bundle/playbooks/stockout_escalation.md) playbook — **Direct fit** | **Supply Plan Detail remains unanalyzed** — 13/26 models in the estate depend on its source, access historically blocked. Single biggest structural gap in the repo. A possible inverted color convention (`Due Color`) must be confirmed before trusting severity bands |
| **Purchasing** | What should be bought, when, and from whom? | None registered yet | Supplier ABC Analysis, Supplier On-Time Performance analyzed | None identified in the OKF bundle yet | Chapter not yet written; no OKF playbook exists for sourcing/PO-timing decisions |
| **Manufacturing & Production Capacity** | Can Wanek/Millennium production capacity cover demand? | DEC-006 (1) | 2 of 5 reports full-depth (Act+Fcst by WNK & MILL Prod Resource, Rolling Report – Wanek Millen); 3 remaining at schema-level only | [Supply Plan Review](../05-okf-bundle/bundle/playbooks/supply_plan_review.md) playbook — **Probable fit** | A `MAX()` capacity-masking bug must be fixed before the playbook can trust the capacity signal; 3/5 reports still schema-only |
| **Inventory Health & Excess Management** | Do we have too much or too little inventory, and what should be done about excess? | DEC-003, DEC-004 (2) | Inv Management, InventoryHealth_AI — chapter explicitly does **not** yet cover the still-unbuilt 5-bucket "Inventory Health" production report (in build with the DA team now) | [Overstock](../05-okf-bundle/bundle/glossary/overstock.md) glossary + [Overstock Exposure](../05-okf-bundle/bundle/metrics/overstock_exposure.md) metric — **Probable fit** | No disposal-action playbook exists yet (consolidate vs. liquidate vs. return-to-vendor); the production Inventory Health report itself is still mid-build |
| **Order Fulfillment & Customer Service** | Which orders are at fulfillment risk, and are we delivering on time? | None registered yet | Chapter drafted (fulfillment risk ranking, expedite/transfer, on-time delivery) | None identified in the OKF bundle | No decision has been formally registered yet; no OKF playbook exists for this capability specifically |
| **Channel-Specific: Amazon & RH Bedding** | How should Amazon wholesale sell-in be sized, and how is the manual RH Bedding forecast path handled? | DEC-007, DEC-011 (2) | Amazon POS Sales and Forecast — chapter drafted | None — both DECs are on the bridge layer's explicit **"playbook-authoring queue"** (no OKF counterpart yet) | DEC-011's verdict was "fix the pipe, not the intelligence" — a data-governance problem (manual Excel submission), not an analytics one; DEC-007 is missing weeks-of-supply/gap measures |
| **Lifecycle Management** | When should new items be reviewed, planners reassigned, or old items discontinued? | Candidates identified, **not yet formally registered** | Chapter drafted | [New Product Performance Review](../05-okf-bundle/bundle/playbooks/new_product_review.md) playbook + [Lifecycle Planning](../05-okf-bundle/bundle/processes/lifecycle_planning.md) process **already exist and are waiting** | Rare case where TO-BE is ahead of AS-IS: the governed playbook exists, but the registry decisions haven't been formalized yet to plug into it |

---

## 3. Dependency map

```text
Channel-Specific (Amazon & RH Bedding) feeds Demand Planning as a specialized input.

Demand Planning & Forecast Consensus  →  Supply Planning & Capacity
Supply Planning & Capacity            →  Purchasing  AND  Manufacturing & Production Capacity
Purchasing + Manufacturing            →  Inventory Health & Excess Management
Inventory Health & Excess Management  →  Order Fulfillment & Customer Service

Lifecycle Management intersects at both ends:
  new-item introduction  →  Demand Planning
  discontinuation        →  Inventory Health & Excess Management
```

A gap upstream compounds downstream — the clearest example in the current
evidence: **Supply Plan Detail** (Supply Planning & Capacity) is unanalyzed,
which is also why 13/26 models across other capabilities can't be fully
verified against a governed source.

---

## 4. Capability maturity view

Status ladder (same ladder the Decision Registry and Business Handbook already
use): **Evidence collected → Business narrative drafted → Decision registry
linked → Target-state mapped → Ready for backlog.**

| Capability | Maturity stage reached | Why it's stuck there |
|---|---|---|
| Demand Planning & Forecast Consensus | Target-state mapped | Direct playbook fit exists for the core decision (DEC-008); blocked from "ready for backlog" by the DEC-001 undocumented-assumption risk and DEC-009's ungoverned coaching thresholds |
| Supply Planning & Capacity | Target-state mapped (partial) | Direct playbook fit exists, but the domain's central report (Supply Plan Detail) is still unanalyzed — the map is drawn on incomplete evidence |
| Manufacturing & Production Capacity | Target-state mapped (partial) | Probable playbook fit exists, blocked by an unresolved capacity-masking bug and 3 still-schema-only reports |
| Inventory Health & Excess Management | Target-state mapped (partial) | Probable fit exists at the concept level, but no disposal-action playbook yet, and the production report itself is still being built |
| Channel-Specific: Amazon & RH Bedding | Decision registry linked | Decisions are registered, but no OKF playbook exists to map them to yet |
| Lifecycle Management | Business narrative drafted | Unusual case — the OKF playbook is ready and waiting, but decisions haven't been formally registered to connect to it |
| Order Fulfillment & Customer Service | Business narrative drafted | No decision has been registered yet; no OKF playbook exists for this capability |
| Purchasing | Evidence collected | Chapter not yet written; earliest-stage capability in the map |

**Reading this table honestly:** no capability has reached "Ready for backlog"
yet. That is expected at this point in discovery — the map's job is to make
each capability's actual blocker visible (a bug, a missing playbook, an
unregistered decision, or an unwritten chapter), so the next unit of work is
obvious rather than assumed.

---

## 5. How to use this map

- **New joiners:** read this before the individual handbook chapters — it
  tells you which domain to start with based on your role, and what "done"
  looks like for each.
- **Prioritization:** the maturity view is the fastest way to see which
  capability is closest to backlog-ready (Demand Planning) versus earliest-stage
  (Purchasing).
- **Track B interviews:** the "Open gaps" column doubles as a starting
  question list for each domain's interview.
