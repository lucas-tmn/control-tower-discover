# Devon's Project Summary (REF-002) — Authoritative

> **PROJECT:** EAGLE EYE
> **DOCUMENT TYPE:** Official Project Summary — received from Devon
> **DOCUMENT ID:** REF-002
> **SOURCE:** Devon Rumpel — Sr. Product Director
> **DATE RECEIVED:** 2026-06-28
> **STATUS:** Authoritative reference (leadership-confirmed)

NOTE: This is Devon's own summary of recent Eagle Eye meetings, received
directly from her. Unlike earlier project documents (which were synthesized by
Lucas from roadmaps, strategy decks, and forwarded notes), this is a
LEADERSHIP-CONFIRMED source and should be treated as authoritative where it
differs from prior synthesis.

KEY NEAR-TERM SIGNAL (from Devon's cover note):
  "The near-term direction is to verify if Copilot can work for now and later
  identify a platform. Robert is also working on some different angles using
  Python to develop an HTML to share to users."


---


## 1. Objective
   Eagle Eye is being repositioned as an AI-powered Supply Chain Control Tower /
   Decision Intelligence capability. The goal is to move beyond traditional
   reporting and dashboards to:
     - Deliver standardized, governed metrics
     - Provide AI-generated insights (not just data)
     - Enable faster, more consistent decision-making
     - Reduce reliance on manual/offline analysis

## 2. Core Shift In Approach
   Current State                              → Target State (Eagle Eye)
   - Power BI dashboards, user-driven explore → AI-driven insights, guided outputs
   - Heavy reliance on manual analysis        → Automated, explainable insights
   - Inconsistent metric definitions          → Centrally governed metrics
   - Broad, uncontrolled self-service         → Controlled, persona-based access
   - Reporting-first mindset                  → Decision intelligence-first mindset

## 3. Guiding Principles
   - Business-first focus: business outcomes, not technical experimentation.
   - Standardization before self-service: most users receive predefined
     scorecards and insights; advanced users may access deeper capabilities in
     a controlled way.
   - Metric governance is foundational: central ownership of metric definitions,
     calculation logic, source transparency.
   - Persona-based experience: distinct outputs for Executive / WBR-leadership
     review / Operational planners / Advanced analysts.
   - Architecture flexibility (short-term): backend platform (Fabric vs.
     Databricks) not finalized; focus on portable logic and context, not
     platform-specific builds.
   - Foundation work must continue: current Forecast Accuracy and Inventory
     Health delivery remains priority #1.

## 4. Scope & Roadmap
   Phase 1 — Complete Current Foundation (In Progress)
     - Finalize: Forecast Accuracy, Inventory Health
     - Resolve: data issues / technical debt
     - Deliver: production-ready datasets and outputs
   Phase 2 — Transition to Eagle Eye (Next)
     - Bring Forecast + Inventory into Eagle Eye framework
     - Introduce AI-generated insights, standardized outputs
     - Begin S&OE / execution-level visibility
   Phase 3 — Expand Across Supply Chain
     - Supply Planning, Manufacturing, Supplier Performance, Flow/network
       analytics, Supply chain financials, Allocation/fulfillment, Inventory
       placement effectiveness

## 5. Key Design Elements
   1. Semantic / KPI Layer — standard definitions (Forecast Accuracy, Inventory,
      Operational KPIs); single source of truth.
   2. AI Insight Layer — "what happened" and "why"; drill into Product /
      Location / Time; move descriptive → diagnostic.
   3. User Experience (Copilot-first) — preferred front-end is Copilot-based
      interaction; balance standardized output with targeted, guided exploration.
   4. Controlled Self-Service — not open-ended querying for all; based on role,
      need, data governance.

## 6. Current Assets & Inputs
   - Existing Power BI reporting: Supply Chain Analytics workspace (core
     reporting); SCP Team Workspace / SCP Global Team (more self-service).
   - Early AI prototypes: forecast insight models on a large-scale dataset
     (~8M records).
   - Initial Control Tower foundation: data engineering and backend validation
     already underway.
   - Low adoption of current dashboard-based experience.
   - Strategic direction documented: dashboards → AI-driven decision intelligence.

## 7. Key Challenges / Risks
   - Architecture uncertainty: Fabric vs. Databricks unresolved; risk of
     non-portable solutions too early.
   - Metric inconsistency risk: without governance, multiple versions of "truth."
   - Actionability gap: current outputs perceived as statistical, not specific
     enough, not directive.
   - Context engineering complexity: provide enough data for AI insight while
     avoiding excessive token usage / inefficiency.
   - Adoption risk: prior Control Tower efforts saw minimal business usage; must
     shift toward clear, actionable outputs.

## 8. Roles & Responsibilities
   (Executive / Strategy / Alignment)
     - Drive alignment on architecture direction (Fabric vs. Databricks)
     - Establish guardrails: standardized vs. self-service access
     - Ensure alignment across Product / Data-analytics / Architecture
     - Define escalation points and decision owners
   Amanda / Lucas (Product)
     - Define core business problems Eagle Eye must solve; priority use cases and
       user journeys
     - Ensure outputs are actionable, business-relevant
     - Partner with data teams on architecture readiness and sequencing
     - Balance Eagle Eye work with existing backlog priorities
   Lucas (PO — VN Analytics / Discovery Lead)
     - Inventory current reporting ecosystem: reports, datasets, dashboards;
       owners, lineage, usage, refresh
     - Define key user personas; top business questions Eagle Eye must answer
     - Build metric catalog (definitions, gaps, inconsistencies); context
       engineering foundation
     - Convert discovery into a structured backlog (when ready)

9. NEAR-TERM FOCUS (NEXT 4–6 WEEKS)
   - Complete Forecast & Inventory foundation; stabilize datasets; deliver
     production outputs
   - Inventory and assess current reporting landscape; identify duplication and
     inconsistencies; clarify ownership and usage
   - Define business questions and personas — what decisions must Eagle Eye
     support?
   - Establish metric governance approach: ownership, definitions, reuse model
   - Clarify architecture direction (or decision path); avoid premature
     platform-specific builds; focus on reusable logic and context

10. SUCCESS CRITERIA (INITIAL)
    - Consistency: same answer regardless of team or user
    - Actionability: clear next steps, not just insight
    - Adoption: used in real decision-making forums (not just explored)
    - Efficiency: reduced manual analysis effort
    - Scalability: extendable across supply chain domains

END OF REF-002 — Devon's Official Eagle Eye Summary
