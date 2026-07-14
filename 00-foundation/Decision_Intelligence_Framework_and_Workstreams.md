# Eagle Eye — Decision Intelligence Framework & Workstreams

**Execution framework for building the capability**
Ashley Furniture · Supply Chain Systems · Global Capability Center
*Working framework · v0.1 · 28 Jun 2026 · Senior Product Manager, SC Systems*

---

## 0. How to read this document

This is the **execution framework** that sits under the Eagle Eye strategy. The
strategy answered *why* and *what*. This answers *how we actually do it* — the
workstreams, the central asset we build, and the model for scaling across the
whole Ashley supply chain over time.

One idea anchors everything below:

> **A dashboard is a fossilized decision.** Every one of the ~3,000 dashboards
> exists because, at some point, someone needed to make a decision and built a
> view to support it. Auditing them is not cleanup — it is *archaeology* to
> recover the decision map of Ashley's supply chain, which has never been
> written down anywhere.

We keep what the fossil represents (the decision) and discard the fossil (the
dashboard).

---

## 1. The central asset — the Decision Knowledge Pool

Everything Eagle Eye does, now and at scale, is organized around one durable
artifact: a **Decision Registry** (the "decision knowledge pool").

### 1.1 What it is

A structured registry whose **unit is a decision** — not a dashboard, not a
report, not a metric. It is the system of record for *how Ashley's supply chain
makes decisions.*

### 1.2 Why it is the spine of the whole capability

- **Tool-agnostic.** It survives any component change — Copilot, platform,
  warehouse, UI. This is the "capability, not tool" principle made concrete.
- **Dual-purpose.** It organizes the work *now* and becomes the knowledge base
  that grounds the AI layer *later*. The decisions, their logic, their data
  lineage, and their success criteria are exactly what a trustworthy Copilot /
  decision agent needs to reason over. We extract tribal knowledge once and it
  becomes fuel for the capability.
- **Reusable across domains.** The same schema works for demand, inventory,
  transport, finance — so scaling is repeatable, not bespoke.
- **The demand signal for the backlog.** It tells us what to build, in what
  order, by value — instead of guessing.

### 1.3 The Decision Registry schema (per entry)

| Field | What it captures |
|---|---|
| **Decision ID & name** | A single, named recurring decision (e.g. "Expedite vs. wait on at-risk SKU") |
| **Domain** | Demand / Inventory / Supply / Procurement / Manufacturing / Warehouse / Transport / Finance / Sales / Customer Service |
| **Decision owner / role** | Who actually makes the call (planner, buyer, inventory controller…) |
| **Frequency & cadence** | Daily / weekly / event-triggered / ad hoc |
| **Trigger** | What prompts the decision (an exception, a date, a threshold breach) |
| **Inputs / data required** | The data and signals the decision depends on |
| **Current tooling** | Which of the ~3,000 dashboards / Excel files support it today |
| **Current decision logic** | The heuristics used today — often tribal, in someone's head or a spreadsheet |
| **What "good" looks like** | Success criteria / the metric this decision moves |
| **Business impact / value at stake** | Why this decision matters (revenue, cost, service, risk) |
| **Exceptions & failure modes** | What happens when it goes wrong |
| **Downstream effects** | What other decisions / domains this one affects |
| **Cross-domain?** | Whether the decision spans boundaries (high-value flag — see §6) |
| **Maturity target** | Assisted → Recommended → Touchless |

### 1.4 The mindset shift it forces

We stop asking *"what dashboard do you need?"* and start asking
*"what decision are you trying to make, and how do you make it today?"*
The first question made 3,000 dashboards. The second one ends them.

---

## 2. The two axes of the capability

The long-term ambition (extending beyond forecast & inventory into transport,
manufacturing, procurement, finance, etc.) only works if we keep two axes
distinct and never confuse them.

```
        DEPTH (maturity within a domain)
        ▲
        │   TOUCHLESS      ░ ░ ░ ░ ░ ░ ░ ░ ░
        │   RECOMMENDED    ▓ ▓ ▓ ░ ░ ░ ░ ░ ░
        │   ASSISTED       █ █ █ ▓ ▓ ░ ░ ░ ░
        │                  └──┴──┴──┴──┴──┴──┴──┴──▶  BREADTH (domains)
              Forecast  Inventory  Demand  Procure  Mfg  Whse  Transport  Finance  CS
```

- **Depth** = how mature a domain's decisions are: assisted → recommended →
  touchless. Each domain climbs at its own pace, gated by data readiness.
- **Breadth** = how many domains the capability covers.

**Rule:** never trade one axis for the other carelessly. We do *not* need
touchless everywhere before expanding, and we do *not* spread thinly across all
domains at "assisted" before deepening any of them. Beachhead domains earn
depth; the playbook (§5) earns breadth.

---

## 3. The architecture: one shared spine, many domain rollouts

Scaling fails if every domain is a separate project. So the framework splits
into a **spine built once** and a **per-domain motion repeated many times.**

### 3.1 The shared spine (build once, reuse everywhere)

1. **Decision Registry** — the knowledge pool (§1)
2. **KPI semantic layer** — one governed definition per metric, all domains
3. **Trust framework** — transparency, calibration, consistency, correctability
4. **Decision services** — exception, recommendation, workflow, traceability
   engines that any domain plugs into
5. **Copilot UX patterns** — the interaction patterns reused per domain
6. **Governance & operating model** — ownership, councils, release cadence

### 3.2 The per-domain work (repeatable — see the playbook in §5)

Each domain reuses the spine and runs the same 8-step motion. Domain #2 should
be cheaper than #1; domain #5 should be close to assembly.

---

## 4. The workstreams

Eight workstreams. The first four are *foundational and largely build the spine*;
the last four *recur per domain and per phase.*

### WS1 — Dashboard Discovery & Inventory  *(the archaeology)*
Inventory the ~3,000 dashboards: owner, usage telemetry, data source, refresh,
overlap. Find the ~20% carrying ~80% of real use. Flag zombies and duplicates.
**Output:** a complete, usage-ranked dashboard inventory.

### WS2 — Decision Mapping  *(reverse-engineer the decisions)*
For the dashboards that matter, work backwards to the decision each one serves.
Pair this with planner shadowing and stakeholder interviews to capture the
decisions that have *no* dashboard (the Excel and tribal-knowledge gaps).
**Output:** the raw decision map per domain.

### WS3 — Decision Registry / Knowledge Pool  *(the synthesis — the durable asset)*
Consolidate WS1+WS2 into the structured Decision Registry (§1.3). This is the
asset that outlives every component and later grounds the AI.
**Output:** a populated, prioritized decision registry.

### WS4 — Data & KPI Foundation
Per domain, assess Golden Tables vs. EDW readiness; resolve conflicting KPI
definitions into one governed semantic layer; define the data-readiness gate
(what may / may not be built on interim data).
**Output:** KPI semantic layer + per-domain data-readiness scores.

### WS5 — Dashboard Rationalization
Apply the verdict model to every dashboard: **Keep / Merge / Migrate / Retire.**
Default verdict is *not* "keep" — a view survives only if it earns its place
against a decision. Sunset with a change-management plan.
**Output:** a rationalization plan and a shrinking dashboard count.

### WS6 — Platform & Decision Services
Lock the platform direction (Fabric vs. Databricks) and stand up the reusable
decision services — exception prioritization, recommendation, workflow,
decision traceability — that all domains consume.
**Output:** the technical spine.

### WS7 — Trust & Adoption
Build the trust mechanics into every output (show-the-work, confidence
calibration, drill-to-source, override, correctability) and run the
change-management motion. Adoption is a first-class metric.
**Output:** trusted, adopted decision experiences.

### WS8 — Governance & Operating Model
Named owners for canonical data; an enterprise planning council for definitions
and cross-domain trade-offs; release cadence; maturity governance
(assisted→recommended→touchless gates).
**Output:** a durable operating model for the capability.

---

## 5. The per-domain playbook (the repeatable motion for breadth)

This is how each new domain is onboarded — the same eight steps every time, so
expansion is a *motion*, not a series of one-off projects.

1. **Decision discovery** — dashboard archaeology + shadowing for the domain (WS1–WS2)
2. **Populate the registry** — add the domain's decisions to the pool (WS3)
3. **Data & KPI readiness** — score the domain; define what's buildable now (WS4)
4. **Pick the beachhead decision(s)** — highest value × readiness × adoptability
5. **Build the decision service** — exception → recommendation → workflow, on the spine
6. **Earn trust & drive adoption** — land first answers where users can verify (WS7)
7. **Measure & deepen** — climb the maturity curve within the domain
8. **Connect cross-domain decisions** — wire this domain's decisions to adjacent ones (§6)

---

## 6. Horizontal scaling — the supply chain *is* a decision chain

The long-term reach (Demand Planning, Inventory Management, Transportation,
Manufacturing, Procurement, Finance, Sales, Warehouse, Customer Service) has a
natural logic: **Eagle Eye expands by following the decision flow of the
business itself.**

```
  DEMAND ─▶ SUPPLY ─▶ INVENTORY ─▶ PROCUREMENT ─▶ MANUFACTURING
                                                        │
   FINANCE  (cuts across every domain)                  ▼
        ▲                                          WAREHOUSE
        │                                              │
  CUSTOMER SERVICE ◀──── TRANSPORTATION ◀──────────────┘
```

### 6.1 Domain sequencing criteria

Sequence domains by a weighted blend of:

- **Data readiness** — is there a trustworthy foundation? (Golden Tables maturity)
- **Decision density & value** — how many high-value daily decisions live here?
- **Adoptability** — are the users and a champion ready?
- **Strategic pull** — does leadership care now?
- **Dependency** — does this domain feed many others downstream?

**Why forecast + inventory go first:** data foundation furthest along
(Streamline, Golden Tables 1.0), already the chosen beachhead, and they feed
*everything* downstream. Get the upstream decisions right and the whole chain
benefits.

### 6.2 Cross-domain decisions — the highest-value frontier

The decisions worth the most are exactly the ones **no single dashboard serves
today** because they span boundaries. "Should we expedite this shipment?" touches
inventory, transport, procurement *and* customer service at once — today a
planner opens five dashboards and stitches it by hand.

This is the strategic punchline: **the value of Eagle Eye compounds as it spans
domains.** A single-domain decision layer is useful; a cross-domain one is
something no dashboard estate could ever be. The Decision Registry must capture
cross-boundary decisions deliberately (the `Cross-domain?` flag in §1.3), because
they are where the capability stops being "better reporting" and becomes
genuinely new.

---

## 7. How this maps to the phased plan

This framework operates *inside* the five-phase strategy already presented:

| Strategy phase | Framework focus | Lead workstreams |
|---|---|---|
| **P1 Discover & Assess** | Archaeology + decision mapping for beachhead | WS1, WS2, WS3 (start), WS4 (assess) |
| **P2 Foundation & Rationalize** | Build the spine; triage dashboards | WS3, WS4, WS5, WS6, WS8 |
| **P3 Beachhead MVP** | First domain's decision service, proven | WS6, WS7 + playbook steps 4–7 |
| **P4 Expand** | Apply the playbook to adjacent domains | Per-domain playbook (§5) |
| **P5 Scale & Automate** | Cross-domain decisions; climb to touchless | §6.2 + maturity governance (WS8) |

---

## 8. What to do first (concrete)

1. **Stand up the Decision Registry schema** — agree the fields (§1.3) before any
   audit, so discovery captures the right things the first time.
2. **Run WS1 + WS2 on the beachhead only** — don't archaeology all 3,000 at once;
   start where we'll build first (forecast / inventory).
3. **Populate the registry for that domain** and use it to pick the beachhead
   decision by value × readiness × adoptability.
4. **Score data readiness** and lock the data-readiness gate before building.
5. **Prove the per-domain playbook once** — the goal of the first domain is not
   just value; it's a *repeatable motion* we can point at the next domain.

---

## 9. The one-line summary

> Eagle Eye is built by recovering Ashley's decision map from its 3,000
> dashboards into a single Decision Registry, building one shared spine of
> trust + data + decision services beneath it, and applying a repeatable
> per-domain playbook that follows the supply chain's own decision flow — from
> forecast and inventory outward to every domain, deepening from assisted to
> touchless as trust and data allow.

---

*Companion to: Eagle Eye — Strategic Plan, Project Context & Reference, and the
Leadership Intent knowledge page. Working framework — to be pressure-tested and
costed before commitment.*
