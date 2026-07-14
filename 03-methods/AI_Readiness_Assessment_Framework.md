# Sprint 5 — AI Readiness Assessment Framework

## Objective
Assess the canonical Decision Registry (Sprint 4 output) to identify where
AI/Copilot/agents should begin — and be explicit about what isn't ready yet.

## Prerequisite
Only assess decisions at Status = Validated with complete core (⭐) fields.
Assessing a Model-only decision for AI-readiness is building on an unproven
foundation — exactly the risk the whole program exists to prevent.

## AI Suitability scoring (using Schema v0.2 §4 criteria)
Score each decision Low / Med / High on:
1. **Decision frequency** — how often does it recur? (rare → rarely
   justifies AI investment)
2. **Data availability** — governed, historical data behind it? (pulls
   directly from D1/D2/D5 — a decision resting on an ungoverned source or
   an unexplained assumption like the `×3` multiplier is not ready,
   regardless of how valuable it would be)
3. **Action clarity** — can a specific action be recommended, or is the
   decision purely interpretive/judgment-based?
4. **Business impact** — what does a wrong decision cost?

A strong AI candidate needs most criteria at High. Document the reasoning
per criterion, not just the score — the reasoning is what makes this
defensible to leadership later.

## Bucketing decisions

| Bucket | Criteria | What it means |
|---|---|---|
| **Ready — Copilot grounding candidate** | High data availability + High action clarity | Safe to ground a Q&A/Copilot feature on; low risk of confident-wrong answers |
| **Ready — Agent/automation candidate** | High on all 4 criteria | Frequent, clear, high-impact, trustworthy data — worth exploring touchless automation |
| **Promising — needs data work first** | High frequency/impact, but Low/Med data availability | The decision matters, but per D1/D2/D5, the underlying data needs governance work before AI touches it |
| **Not ready** | Low on frequency or impact, or purely judgment-based with no clear action pattern | Deprioritize for AI; may still be well worth having in the registry for human use |

## AI Opportunity Map
Produce one view grouping decisions by bucket, with:
- Decision ID/name and domain
- Current bucket + one-line reasoning
- If "Promising — needs data work": what specifically needs fixing (link to
  the D2/D5 finding, e.g. a hardcoded placeholder or unexplained multiplier)
- If "Ready": suggested AI pattern (Q&A grounding vs. recommendation
  surfacing vs. automated action)

## Decision Automation Candidates
From the "Ready — Agent/automation" bucket, further filter by: is the
action fully deterministic given the data (safe to automate), or does it
require human judgment even when data is clear (recommend, don't automate)?
Keep this distinction explicit — conflating "AI can calculate this" with
"AI should act on this" is the main risk at this stage.

## Eagle Eye AI Roadmap (output structure)
A simple phased view for leadership:
1. **Now** — Copilot-grounding candidates ready today
2. **Next** — Promising decisions once specific data-governance fixes land
   (name the fixes, e.g. "resolve the `×3` multiplier in Forecast Accuracy
   before using it in any financial-impact AI feature")
3. **Later** — automation candidates, once Now/Next have proven trust in
   practice

## Output of Sprint 5
An AI Readiness Assessment, an AI Opportunity Map, a list of Decision
Automation Candidates, and the Eagle Eye AI Roadmap — the artifact that
lets leadership see exactly where trusted knowledge already supports AI,
and where it deliberately doesn't yet.
