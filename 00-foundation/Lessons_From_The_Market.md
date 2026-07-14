# Lessons from the Market

## Why this document exists

Everything else in this repository comes from inside Ashley — reading our own
reports, our own semantic models, our own decisions. This document is the one
place we look outward: what does the broader market know about supply chain
control towers and decision intelligence programs, and does it change anything
about our approach?

**How to read this document:** every claim below is attributed to a specific
external source with a link. Claims about *our own* estate (Ashley's reports,
bugs, patterns) are clearly marked as such and link back into this repo. The two
should never be blended — a finding from Gartner about the market in general is
not evidence about Ashley specifically, and vice versa.

---

## 1. Where Ashley sits on the market's maturity curve

Gartner's December 2025 report on the visibility-to-orchestration journey
describes four stages of supply chain technology maturity: **Business
Intelligence** (structured data warehouses, descriptive/diagnostic analytics,
retrospective only), **Control Towers** (2010s-era, IoT-driven, real-time but
siloed by function), **Command Centers** (cross-functional data plus a digital
twin, decisions still human-driven), and **Orchestration Platforms** (AI
prescribes and executes decisions directly)
([Incorta, summarizing the Gartner report](https://www.incorta.com/blog/gartner-charts-the-path-from-supply-chain-visibility-to-autonomous-orchestration)).

Ashley's 25-report Power BI estate — as documented across
[`01-evidence/track-a-reports/`](../01-evidence/track-a-reports/) — sits at the
end of stage 1, beginning of stage 2: descriptive dashboards, siloed by report,
not yet cross-functional. Eagle Eye's roadmap targets stage 2→3.

## 2. Most companies get stuck exactly where the actionability gap already worries us

A separate analysis of control-tower maturity makes a specific claim: most
enterprise deployments stall at "the dashboard is populated, the data is
aggregating, but KPIs are unchanged because the system surfaces problems
without resolving them" — and a common next-stage failure mode is **notification
fatigue**, where planners receiving frequent alerts calibrate to ignore them
([Locus.sh, "Control Towers in Supply Chain Decision-Making"](https://locus.sh/blogs/control-towers-supply-chain-decision-making/)).

This maps directly onto the "actionability gap" Devon's own Eagle Eye summary
already names as a risk (see `Devon_summary.txt` context from earlier in this
program) — external research treats it as the single most common place programs
like this one plateau, not a hypothetical risk.

## 3. Why control towers historically under-deliver — and how many of these we'd already found ourselves

Several sources converge on a consistent set of root causes:

- **Data "black holes" destroy trust.** Incomplete or contradictory data across
  systems means no single version of truth, which makes the tower "largely
  ineffective" regardless of its analytics
  ([Logistics Management, "The Supply Chain Control Tower: Myth and Reality"](https://www.logisticsmgmt.com/article/the_supply_chain_control_tower_myth_and_reality)).
- **Multiple ungoverned information sources compound the problem**, and
  organizations often avoid fixing this because of "fear of change management
  and the trauma of past upgrades"
  ([SupplyChainBrain, "How to Avoid Supply Chain Control Tower Failures"](https://www.supplychainbrain.com/articles/28114-how-to-avoid-supply-chain-control-tower-failures)).
- **Visibility and transparency are the single most influential driver of
  successful adoption**, ranked above other factors in a structural-modeling
  study of control tower success factors
  ([Nadar, Gunasekaran & Narwane, ScienceDirect, 2026](https://www.sciencedirect.com/science/article/pii/S2949863525000780)).
- **A typical disruption still requires ~34 manual system updates across 6
  platforms**, per Gartner survey data, and MIT research found a single
  disruption generates ~25 emails needing input from 8 roles — the "war room"
  fallback of Excel, email, and phone calls that control towers are meant to
  replace
  ([FourKites, "Why Supply Chain Control Towers Didn't Deliver on Their Promise"](https://www.fourkites.com/blogs/supply-chain-control-towers-whats-changing/)).
- **Misalignment between software capability and actual business need**, plus
  insufficient top-management engagement, are named as recurring implementation
  failure modes in a socio-technical case study of an intelligent control tower
  rollout
  ([ResearchGate, "Implementation of an intelligent supply chain control tower: a socio-technical systems case study"](https://www.researchgate.net/publication/357000619_Implementation_of_an_intelligent_supply_chain_control_tower_a_socio-technical_systems_case_study)).

**Cross-check against our own findings:** four of these five external causes
already have a direct, independently-discovered counterpart inside Ashley's
estate, documented elsewhere in this repo:

| External cause | Ashley counterpart (our own finding) |
|---|---|
| Data "black holes" / no single truth | 18 verified defects + ungoverned SharePoint/Excel dependencies — see [`Bug_Findings_Log.md`](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md), PAT-04 in [`Systemic_Patterns_Registry.md`](../01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md) |
| Multiple sources, no single version of truth | PAT-03 (same concept, different logic across sibling reports) |
| Fear of change from past failed upgrades | Explicitly named by Devon: "Prior Control Tower efforts saw minimal business usage" |
| Misalignment between capability and business need | The entire premise of this discovery program — reading reports and interviewing users specifically to close this gap before building |

We were not aware of this research when these findings were made — the
convergence is independent, which is a reasonable signal that the discovery
method itself is sound, not just lucky.

**The one external cause without a clear Ashley counterpart yet:** insufficient
top-management engagement. We don't have evidence either way on this — it's a
genuine open question, not a confirmed finding, and not something Track A
artifact analysis can answer.

## 4. The market's own numbers on what "success" looks like

Legacy control towers historically took years to show value. AI-powered ones,
by contrast, are reported to reach payback in **4-8 months** when they focus on
a narrow, measurable use case rather than a full platform build first
([FourKites, same source as above](https://www.fourkites.com/blogs/supply-chain-control-towers-whats-changing/)).

This is the evidentiary basis (not just intuition) for recommending a small,
shippable "quick win" early in the Eagle Eye roadmap — building one narrow,
demonstrable capability and getting a real user to depend on it, rather than
waiting until the full platform is ready before anyone outside the program sees
value.

## 5. A closer domain parallel: Wayfair's explainable-AI requirement

Wayfair — the closest same-domain (furniture/home goods) comparison available —
built its demand-forecasting AI to be explicitly **explainable**, specifically
because most of its inventory is supplier-owned rather than owned by Wayfair
itself: suppliers need to understand *why* the model recommends a given
inventory commitment before they will act on it, not just receive a number
([Chain Store Age, "Exclusive Q&A: Wayfair applies AI to supply chain disruption"](https://chainstoreage.com/exclusive-qa-wayfair-applies-ai-supply-chain-disruption)).

**Why this matters for Ashley specifically:** the same trust problem applies to
Ashley's planners, just with a different reason — they won't act on an AI
recommendation they don't understand, especially where our own discovery has
already found the underlying numbers can be wrong or distorted (e.g. BUG-010's
AVERAGEX distortion of the months-of-supply figure in Inv Management). The Bug
Findings Log and Systemic Patterns Registry effectively double as an
explainability layer already — when a future AI insight says "excess at
warehouse 335/Ashton looks high," the discovery repo already has the context to
say why that number might be less reliable than it looks, rather than
presenting it as unqualified fact.

## 6. What Gartner separately flags as the most likely reason AI supply-chain
   projects fail going forward

Gartner predicts 60% of supply chain digital adoption efforts will fail to
deliver promised value by 2028, and attributes this specifically to
**insufficient investment in learning and development** — teams given new
tools without the skills training to use them effectively
([Gartner press release, May 2025](https://www.gartner.com/en/newsroom/press-releases/2025-05-07-gartner-predicts-60-percent-of-supply-chain-digital-adoption-efforts-will-fail-to-deliver-promised-value-by-2028)).

This is a genuine blind spot for this program: nothing in our discovery work so
far assesses whether the data/analytics team has the skills the Eagle Eye
roadmap will eventually require (semantic modeling at scale, AI-assisted
analytics, governance operations). This isn't a finding — it's a flagged gap,
consistent with "Nhóm 1 — Con người & tổ chức" raised earlier in this program's
brainstorming.

---

## Summary — what changes, what doesn't

**Doesn't change:** the artifact-first discovery method. Four of five external
failure causes were already found independently inside Ashley before this
document existed, which is evidence the current approach is on the right track,
not a reason to redirect it.

**Does change / sharpen:**
1. Elevate the "quick win" recommendation from a nice-to-have to a
   evidence-backed priority (4-8 month payback data point above).
2. Add a standing Track B interview question about alert/notification fatigue —
   not currently in the interview guide, and specifically named by external
   research as a common failure point.
3. Explicitly track team-capability/L&D readiness as an open risk, even though
   no artifact-based finding currently exists for it.
4. Frame the Bug Findings Log / Systemic Patterns Registry, going forward, as
   part of the *explainability layer* for future AI insights (per the Wayfair
   parallel), not only as a defect log.
