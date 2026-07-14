---
type: Map
title: Decision–Playbook Map — Decision Registry ↔ OKF Playbooks & Processes
description: Mapping between field-observed decisions (DEC-001…011, evidence-based, as-is) and the OKF bundle's standardized playbooks and processes (to-be), including decisions with no playbook and playbooks with no observed decision.
tags: [bridge, decisions, playbooks, processes, registry]
timestamp: 2026-07-09
status: draft
---

# Decision ↔ Playbook Map

**The relationship:** a Decision Registry entry documents a decision *as it is
actually made today* (evidence from models, later interviews). An OKF playbook
prescribes *how the reasoning should run*. Mature state = every recurring
high-value decision has both: registry evidence + a governed playbook. The gaps
on either side below are the work queue.

## Matched pairs

| DEC (AS-IS evidence) | OKF playbook/process (TO-BE) | Fit | Notes |
|---|---|---|---|
| [DEC-005](../02-decision-registry/decisions/DEC-005.md) — expedite/transfer to close SS gaps | [Stockout Escalation](../05-okf-bundle/bundle/playbooks/stockout_escalation.md) | **Direct** | Playbook's severity classification (days_of_supply vs lead_time, open-PO timing) is the governed version of AFT_SI-SS_PSW's color logic. Playbook's `[FILL IN: lead time column]` gap is mirrored by the estate (see gap-fill map). BUG-012 (possible inverted color) must be resolved before mapping severity bands 1:1 |
| [DEC-008](../02-decision-registry/decisions/DEC-008.md) — approve/push back working forecast | [Forecast Revision](../05-okf-bundle/bundle/playbooks/forecast_revision.md) + [Demand Consensus Meeting](../05-okf-bundle/bundle/processes/demand_consensus_meeting.md) | **Direct** | DEC-008's evidence (exception mechanics, snapshot anchoring, RH swap) fills most of the process doc's placeholders — see gap-fill map |
| [DEC-009](../02-decision-registry/decisions/DEC-009.md) — chronic-bias exception review / planner coaching | [Forecast Revision](../05-okf-bundle/bundle/playbooks/forecast_revision.md) (partially) | **Probable** | The coaching/people-performance aspect has **no OKF playbook** — deliberate? The 25/20/15% thresholds need governance before this becomes a playbook (see gap-fill map) |
| [DEC-004](../02-decision-registry/decisions/DEC-004.md) — consolidate/liquidate excess at WH335 | [Overstock](../05-okf-bundle/bundle/glossary/overstock.md) glossary + [Overstock Exposure](../05-okf-bundle/bundle/metrics/overstock_exposure.md) metric | **Probable** | Concepts exist but **no disposal-action playbook** (consolidate vs liquidate vs return-to-vendor) exists in the bundle — the 4-way `True Excess Type` waterfall in Inv Management is ready-made playbook input |
| [DEC-010](../02-decision-registry/decisions/DEC-010.md) — in-month consumption pace → chase orders / cut forecast | [Forecast Revision](../05-okf-bundle/bundle/playbooks/forecast_revision.md) (the "cut" branch) | **Candidate** | The account-outreach branch and the $-at-risk framing have no OKF counterpart; PAT-06 caveats apply before standardizing |
| DEC-00x candidates from Product Review reports (lifecycle health) | [New Product Performance Review](../05-okf-bundle/bundle/playbooks/new_product_review.md) + [Lifecycle Planning](../05-okf-bundle/bundle/processes/lifecycle_planning.md) | **Direct** (once registered) | Product Review (NEW) analysis + When to Disco v2 supply the evidence to fill lifecycle_planning's 7 placeholders |
| [DEC-006](../02-decision-registry/decisions/DEC-006.md) — Wanek/Millennium capacity coverage | [Supply Plan Review](../05-okf-bundle/bundle/playbooks/supply_plan_review.md) | **Probable** | BUG-013 (`MAX()` capacity masking) is a prerequisite fix before this playbook can trust the capacity signal |

## Decisions with no playbook (playbook-authoring queue for Robert/team)

| DEC | Why it deserves a playbook |
|---|---|
| [DEC-001](../02-decision-registry/decisions/DEC-001.md) — $-value of forecast-accuracy improvement | Executive financial-justification logic (×3, +91d) exists only as undocumented DAX; a governed playbook + assumption register is the fix for PAT-06 |
| [DEC-002](../02-decision-registry/decisions/DEC-002.md) — planner coaching / portfolio rebalance | Pairs with DEC-009; people-performance decisions need explicit, approved rules more than any other class |
| [DEC-007](../02-decision-registry/decisions/DEC-007.md) — Amazon wholesale sizing | Channel-specific replenishment reasoning (POS vs Amazon fcst vs sell-in) is undocumented; the missing weeks-of-supply/gap measures make it a strong Eagle Eye + playbook candidate |
| [DEC-011](../02-decision-registry/decisions/DEC-011.md) — RH Bedding forecast sign-off | Verdict was "fix the pipe": the playbook here is a data-submission SOP, not analytics |
| Forecast Change WoW's `Push to Supply` 3-state workflow (unregistered DEC candidate) | A literal in-model workflow flag ("Large FC, need to push" / "Review to push" / "Ad-hoc pushed") — already half a playbook, in DAX form |

## Playbooks with no registered decision yet (evidence queue for us)

| OKF playbook/process | Where evidence will come from |
|---|---|
| [New Product Performance Review](../05-okf-bundle/bundle/playbooks/new_product_review.md) | Register DECs from [Product_Review_NEW](../01-evidence/track-a-reports/Product_Review_NEW_Analysis.md) + [Complete_Series_In_Stock](../01-evidence/track-a-reports/Complete_Series_In_Stock_Analysis.md) |
| [Lifecycle Planning](../05-okf-bundle/bundle/processes/lifecycle_planning.md) | Register DECs from [When_to_Disco_v2](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md) + [Planner_Assignment](../01-evidence/track-a-reports/Planner_Assignment_Analysis.md) |
| [Supply Plan Review](../05-okf-bundle/bundle/playbooks/supply_plan_review.md) | Supply Plan Detail analysis still outstanding (access previously blocked) — highest-priority remaining Track A target alongside Inventory Health |
