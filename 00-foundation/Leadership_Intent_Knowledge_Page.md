# Eagle Eye / Control Tower — Reading Leadership's Intent

**A Senior Product Owner's synthesis**
Ashley Furniture · Global Capability Center · Supply Chain Analytics
*Working knowledge page · v1.0 · 28 Jun 2026*

---

## Why this page exists

I was handed a short, blunt brief:

> *"Lucas will be joining us out of the Vietnam office, focused primarily on helping the Supply Chain Analytics team to eventually replace all 3000 of the Supply Chain dashboards! Side note, we will not have 3000 dashboards going forward. That's insane."*

The "3000" is almost certainly not a literal inventory count. It's a rhetorical number — leadership's way of saying *the current model is broken and won't scale*. My job here isn't to restate the strategy decks. It's to read across them and write down **what the managers are actually trying to do, why, and what they're afraid of** — so that whoever picks up Eagle Eye knows the intent, not just the requirements.

Everything below is my interpretation, grounded in the documents we've collected. Where I'm inferring rather than quoting, I say so.

---

## The one-sentence version

> Leadership wants to stop *shipping reports* and start *shipping decisions* — by collapsing thousands of passive dashboards into a single AI-driven decision layer (Eagle Eye) where a planner asks a question in plain language and gets a prioritized, explained, actionable answer.

The dashboard count is the symptom. The disease is that **Ashley has a strong data foundation and near-zero decision adoption.** That gap is the whole reason this project exists.

---

## What the "3000 dashboards" problem really tells me

When a leader reacts that viscerally to a number, they're signalling more than clutter. Reading the strategy and technology roadmaps together, here's what I believe the 3000 actually represents to them:

**1. A cost and maintenance black hole.** Every dashboard is a thing someone has to build, fix, explain, and reconcile. The Technology Roadmap repeatedly flags "no golden data layer" and "reporting built on inconsistent data sources." 3000 dashboards on inconsistent data isn't 3000 answers — it's 3000 *arguments* about whose number is right.

**2. A symptom of dashboards-as-a-crutch.** The meeting notes are explicit: the team must shift *from building dashboards → to delivering decision intelligence + measurable value.* Dashboards proliferate when nobody owns the decision. Every time a question came up, someone built a view instead of solving the workflow. 3000 is what that looks like after a few years.

**3. Proof that visibility ≠ adoption.** "Control tower adoption is currently near zero, despite strong data foundation." This is the line that should keep us up at night. We don't have a *data* problem. We have an *adoption and decision* problem. More dashboards have demonstrably not moved the needle.

**4. A scaling impossibility.** "We will not have 3000 dashboards going forward." If every new SKU, channel, planner, or region spawns more dashboards, the model collapses under its own weight. Leadership has decided the unit of scale can't be "a dashboard" anymore. It has to be something that scales without linear human build effort — i.e. an **AI/Copilot layer** sitting on a **governed data foundation**.

---

## What the managers are actually reaching for

If I strip away the slideware and ask "what does each layer of leadership want out of this," here's what I see:

### Executive level (Ashish, Axel, Julie)
They want **decision intelligence with a measurable P&L story.** Notice the framing everywhere: *measurable value, business value, ROI, value scoreboard.* The PHI model and the OKR "red flag" rule (if an initiative doesn't map to a Key Result, kill it) tell me executives are tired of technology that can't prove it moved a number. Eagle Eye will be judged on whether wMAPE drops, in-stock rises, and excess stock falls — **not** on how slick it looks.

### Strategy / planning leadership (Jenny, Matt, Seth, Josh, Ike)
They want **one source of truth and one KPI language.** The recurring pain across docs is "leaders lack one KPI language, users spend too much time reconciling numbers." Their ambition is a world where a WBR isn't a fight about whose spreadsheet is correct — it's a conversation about what to *do*. The 3-tier metric structure (Executive / WBR / Operational) is their fingerprint: they want the *same underlying truth* rolling up cleanly from planner to boardroom.

### Product / IT leadership (Devon, Amanda, Cyrissa, Simon)
They want **a product, not a project portfolio.** The strategy is emphatic: *don't treat Streamline, One Ashley, AI forecasting, RCCP, optimization as separate projects — treat them as products in one portfolio with shared contracts for data, workflow, and KPIs.* Their ambition is architectural discipline: one canonical data model, one workflow language, one KPI framework. Eagle Eye is the visible tip of that discipline.

### Data / AI leadership (Steven, Zach, Cherry)
They want **AI embedded in the daily workflow, not sidecar analytics.** The repeated warning — "optimization will underdeliver if it stays outside daily user workflows" — is their thesis. Their ambition runs all the way to agentic planning (Forecasting Agent, E2E Supply Planning Agent by ~Q4 2027). Eagle Eye is the on-ramp to that: assisted intelligence first, touchless execution later.

---

## The model they're converging on

Across every document, the same shape keeps appearing. This is the mental model I think leadership shares, whether or not they've drawn it the same way:

```
   OLD WORLD                          NEW WORLD (Eagle Eye)
   ─────────────                      ──────────────────────
   3000 dashboards          →         1 Copilot / decision layer
   "Here's the data"        →         "Here's what's wrong, why,
                                        and what to do about it"
   Pull (user hunts)        →         Push (system surfaces exceptions)
   Reporting                →         Decision system
   Reconcile numbers        →         Trust one number
   Per-domain silos         →         One KPI language, all domains
   Human builds the view    →         AI generates the insight
```

The **Copilot is the headline UX decision.** Leadership has explicitly chosen a conversational, AI-first interface over dashboard-first. That's a strong, opinionated bet. It means the product's primary surface isn't a screen full of charts — it's an interface a planner can *talk to* and get a standardized, explained answer from.

---

## How far the ambition actually reaches

Here's the part the brief hints at but the documents make concrete: **this does not stop at Supply Chain Analytics.**

The "3000 dashboards" the brief mentions are the *starting* battlefield — forecast, inventory, planners. But the strategy and technology roadmaps make the wider ambition unmistakable. The same decision-layer model is meant to extend across the entire Ashley operating ecosystem:

- **Supply Chain core** — demand, supply, inventory (the beachhead)
- **Warehouse & Distribution** — 7 MDCs, 30+ RFCs, network fulfillment via DOM
- **Transportation** — TMS modernization, route optimization, predictive ETA
- **Manufacturing** — the "Dark Factory," MES, digital twin, Reflection AI
- **ERP / Finance** — automated close, One Ashley finance views
- **Order Management** — EPIC / OPRO / DOM capacity-aware promising

Every one of these domains in the Technology Roadmap ends with the same phrase: *"surfaced through the One Ashley Framework."* That's the tell. **Eagle Eye is the proving ground for a pattern leadership intends to replicate enterprise-wide.** If we get the decision-layer model right in Supply Chain Analytics, it becomes the template for how every Ashley function eventually consumes its data and makes its calls.

So when we build Eagle Eye, we are not building a Supply Chain reporting replacement. We are building **the reference implementation of "how Ashley makes operational decisions" going forward.** That's the real weight on this project, and I think it's why leadership cares so much about getting the foundations (data model, KPI semantics, workflow patterns) right rather than rushing to ship screens.

---

## What "good" looks like to them (the success picture)

If I imagine the demo that would make this leadership group genuinely happy, it's not a dashboard tour. It's something like:

> A planner opens the Copilot. It has *already* surfaced the three exceptions that matter most this morning — ranked by business impact, not alert volume. For the top one, it shows *what* is happening (a service risk on a key SKU), *why* (a supplier commit slipped + a demand spike), *how long* they have to act, and *two ranked recommended actions* with the trade-offs visible. The planner picks one, it routes for approval through a shared workflow, and the decision — who, why, expected impact — is captured automatically. No dashboard was opened. No number was reconciled. A decision was made and measured.

That's the north star in human terms. Everything in the capability list (exception prioritization, root-cause, recommendations, confidence scoring, decision traceability) is in service of that single moment.

---

## The fears underneath the ambition (risks leadership keeps naming)

A good read of intent includes reading what they're *afraid of*. The same risks recur across the strategy docs, and they tell me what we'll be measured against:

| What they fear | What it means for Eagle Eye |
|---|---|
| **"Optimization becomes a sidecar"** | If Eagle Eye's AI lives outside the daily workflow, it fails. It must be *where the work happens.* |
| **"Weak trust in AI outputs"** | Every recommendation needs explainability, drivers, backtest, and human override from day one. Trust is the product. |
| **"Transitional platforms become permanent"** | Don't let Eagle Eye calcify into "Power BI with a chat box." It must evolve toward genuine decision automation. |
| **"Unclear master-data ownership"** | Eagle Eye is only as good as Golden Tables. Garbage in, confident-garbage out — which is worse. |
| **"Change saturation in business teams"** | Adoption is the whole game (remember: today it's near zero). Pilot, prove, then scale. |

That last one is the quiet killer. **The previous model's failure mode was building things nobody adopted.** If Eagle Eye is technically brilliant and planners don't use it, we've just built dashboard #3001.

---

## My read on what this means for how we work

A few principles I'd carry into the backlog, derived from the intent above rather than from any single requirement:

1. **Decisions are the unit of value, not dashboards or even insights.** Every backlog item should answer: *what decision does this help someone make, and how will we know it improved?*

2. **Adoption is a first-class metric, not an afterthought.** Given that near-zero adoption is the founding problem, planner touch-rate and workflow-completion matter as much as forecast accuracy.

3. **Earn trust before automating.** The path is assisted → recommended → touchless. Skipping straight to automation, against a backdrop of low AI trust, would repeat the adoption failure.

4. **Build the pattern, not just the product.** Because leadership intends to replicate this across warehouse, transport, manufacturing, ERP — the reusable parts (KPI semantics, exception framework, workflow, Copilot patterns) are arguably more valuable than any one screen.

5. **Tie every release to one or two outcome metrics.** This is leadership's explicit instruction and the OKR "red flag" rule. It's also our defense when someone asks for dashboard #3001 — we can point to the decision and the metric it moves.

---

## Open questions I'd want leadership to answer

Reading intent only gets us so far. These are the gaps where I'd push for an explicit decision rather than guess:

- **Scope of "replace."** Does Eagle Eye *retire* the 3000 dashboards, or *absorb* their function? What's the migration/sunset plan, and who owns telling 3000 dashboards' worth of users their view is going away?
- **Copilot reality check.** What can the Copilot credibly do at MVP vs. what's the 2027 agentic vision? We need to manage the gap between the ambition and what's shippable, or we'll over-promise.
- **Data readiness gate.** Eagle Eye depends on Golden Tables. What's the honest readiness state, and what does Eagle Eye consume in the interim (EDW) without baking in tech debt?
- **The platform decision.** Fabric vs. Databricks is still open and it shapes our architecture. We can't fully commit Eagle Eye's data layer until that lands.
- **Definition of adoption success.** If near-zero adoption is the problem, what number counts as "solved"? We need that target named early.

---

## Bottom line for whoever reads this next

Leadership isn't asking for a better dashboard. They're asking us to **change how Ashley's supply chain makes decisions** — replacing a sprawling, low-adoption reporting estate with a single, trusted, AI-driven decision layer that planners actually *talk to and act on* — and to do it in a way that becomes the **enterprise-wide template** for every other function.

The "3000 dashboards" line is the easy-to-repeat version. The real ambition is bigger and quieter: *one source of truth, one decision layer, one way of working — proven first in Supply Chain Analytics, then everywhere.*

That's the intent. The requirements will follow from it.

---

*Sources synthesized: Eagle Eye discussion notes (22 Jun) · Ashley Supply Chain Product Strategy (WIP) · Supply Chain Product Strategy (capability spec) · 2026 Product Org Roadmap + PHI/OKR model · Technology Roadmap v1 · PO Onboarding Guide. This is an interpretive working document — intent and inference, not signed-off strategy.*
