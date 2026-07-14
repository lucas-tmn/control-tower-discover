# Track B — Business Discovery Interview Guide

## Purpose
Confirm, correct, and fill in the fields Track A (reports) cannot answer on
its own — mainly Group B of the Decision Registry Schema v0.2: Trigger (B2),
Workflow Action(s) (B5), Action when off-track (B6), Escalation path (B7),
Shadow tools (B8) — plus Data Readiness field D3 and AI-suitability input E2.

## Who to interview
Per the roadmap's Track B scope: Planners (Demand, Inventory, Supply),
Buyers, and Leadership. Suggested order — start closest to the two already
worked examples, to test the interview questions against known evidence
before broadening:

1. **Demand Planner** (tests Weekly Trend Analysis worked example)
2. **Inventory Planner / Buyer** (tests Inventory Health worked example)
3. Supply Planning
4. Leadership (WBR / Executive persona — different decision type per A7:
   performance/financial, not operational)

## Pilot before scaling
Run steps 1–2 first as a pilot to validate hypothesis H3 ("reports and
interviews should answer the same discovery questions"). Only proceed to
steps 3–4 once the question set below has been adjusted based on what the
pilot reveals.

## Interview structure (45–60 min)

### 1. Warm-up (5 min)
- What's your role, and what does a typical week look like?
- What report(s) do you look at most often?

### 2. Walk through a known decision (15–20 min)
Use the worked example most relevant to this persona as a **seed
hypothesis**, not a leading assumption:

> "We looked at [Weekly Trend Analysis / Inventory Health] and it seems like
> when [Written/Requested outpaces Forecast / a SKU crosses into the Excess
> bucket], the expected next step is [prepare for demand increase / halt
> replenishment]. Is that how you actually decide? What did we get wrong or
> miss?"

This directly confirms/corrects B2 (Trigger), B5 (Workflow Action), and
tests whether the "rule" atom identified in the worked example matches
reality or was an oversimplification.

### 3. Action when off-track — the key question (10 min)
> "When [key metric] goes bad, what's your actual next concrete step?"
(This is field B6 — the single most important field per Schema v0.2, since
it's the raw material for Eagle Eye's recommendation feature.)

Follow-ups:
- Who else needs to be involved before you act?
- Is there a point where you escalate instead of acting yourself? To whom,
  and how long does that usually take? (B7)

### 4. Shadow tools (5–10 min)
> "Besides Power BI, what do you use to actually make this decision or track
> it — Excel, email, Slack, meetings? Walk me through one."
(Field B8 — also feeds Track C: any file/process named here should be
requested for the Track C evidence collection.)

### 5. Trust check (5 min)
> "Is there a number in [report] you don't fully trust, or that you've had
> to work around?"
(Feeds Data Readiness field D3 — confirms or contradicts what Track A
already flagged, e.g. hardcoded placeholders found in Inventory Health.)

### 6. Close (5 min)
- Anything we should have asked but didn't?
- Who else should we talk to about this decision?

## After each interview
1. Log responses directly against the relevant Decision Registry row's B/D
   fields.
2. Update Status (F1) from "Model-only (hypothesis)" to "Interview-confirmed."
3. Log anything unresolved in Open Questions (F4) rather than guessing.
4. Flag any named document/process for Track C collection.
