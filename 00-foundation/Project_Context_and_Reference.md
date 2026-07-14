# Project Context & Reference

> **PROJECT:** EAGLE EYE – AI-Powered Supply Chain Control Tower
> **DOCUMENT TYPE:** Project Context & Reference
> **VERSION:** 0.2 (Living Document)
> **CREATED:** 2026-06-28
> **LAST UPDATED:** 2026-06-28
> **STATUS:** In Progress / Collecting Requirements

NOTE: This document consolidates context from multiple source documents as
the project is in its early stages. Requirements and scope will continue to
evolve. All source documents are listed in Section 11.

**Changelog:**
  v0.2 (2026-06-28) – Added baseline & target metrics, technology dependency
                       chain, OKR framework, expanded systems landscape,
                       agentic planning vision, and 3 new source documents.
  v0.1 (2026-06-28) – Initial draft from meeting notes and strategy docs.

RELATED DOCUMENTS
  - MTG-001 : Ashley Eagle Eye Discussion - 22Jun.txt  (Meeting Notes)

## 1. Project Overview

Project Name  : Eagle Eye
Project Type  : AI-Powered Supply Chain Control Tower
Initiative    : Phase 2 of the Supply Chain Control Tower roadmap
Status        : Pre-Discovery / Requirements Collection

VISION (from MTG-001):
  Shift from reporting to decision intelligence. Eagle Eye is the AI-driven
  control tower layer that replaces the current Power BI–centric reporting
  approach with a proactive, self-service decision system.

**Problem It Solves:**
  Control tower adoption is currently near zero, despite a strong data
  foundation. The team must shift from building dashboards to delivering
  decision intelligence with measurable business value.

**North Star:**
  An intelligent, real-time Supply Chain Control Tower powered by AI that
  enables planners, managers, and executives to act on prioritized exceptions
  — before problems become costly.

## 2. Strategic Context

Eagle Eye sits within the broader "One Ashley" Supply Chain Product Strategy,
which aims to move from fragmented planning and supplier systems to a unified,
modular product suite.

  From (Current State) → To (Eagle Eye Target)
  ─────────────────────────────────────────────────────────────────────────────
  Power BI dashboards          → AI-driven decision intelligence
  Passive reporting            → Proactive exception management
  Siloed tools per domain      → Shared KPI layer + control tower views
  Manual data reconciliation   → Standardized outputs, single source of truth
  Reactive decision-making     → Copilot-first, self-service insights
  ─────────────────────────────────────────────────────────────────────────────

BROADER PROGRAM CONTEXT (from Ashley SC Product Strategy WIP):
  Eagle Eye maps to the "Analytics & Control Tower" domain in the broader
  supply chain product portfolio:
    - Drill-down dashboards
    - KPI governance and shared semantics
    - Anomaly detection
    - What-if modeling
    - Value tracking and adoption telemetry
    - Observability services across all SC domains

ONE ASHLEY FRAMEWORK (from Technology Roadmap):
  All supply chain KPIs, dashboards, and AI agent interactions will
  ultimately be surfaced through the One Ashley unified UI. Eagle Eye
  should be designed with this as the target delivery surface — not as a
  standalone tool. The long-term vision is a closed-loop, AI-driven supply
  chain where network design, demand planning, order management, and
  fulfillment operate as a unified, autonomous ecosystem.

**Technology Dependency Chain:**
  The data and system architecture that feeds Eagle Eye follows this sequence:

    Golden Tables (Medallion) → AI Models → Streamline → DOM/EPIC/OPRO
                                                    ↓
                                             One Ashley (Eagle Eye UI)

  Eagle Eye sits at the END of this chain — it consumes clean, trusted data
  from Golden Tables and surfaces it as decision intelligence. This means
  Eagle Eye's quality is directly dependent on upstream data foundation work.

LONGER-TERM AGENTIC VISION (Q4 2027+):
  The broader technology roadmap targets an E2E Agentic Supply Planning
  system where routine decisions are automated and the team shifts to
  data enrichment and exception management. Eagle Eye should be designed
  with this agentic future in mind — starting with assisted intelligence
  and progressively enabling touchless execution where appropriate.

## 3. Roadmap Sequencing

Eagle Eye is Phase 2. Prerequisites must be complete first.

  ┌──────────────────────────────────────────────────────────────────────────┐
  │ PHASE 1 – Complete Current Foundation (PREREQUISITE FOR EAGLE EYE)       │
  │   1. Forecast (Back-End)  – Resolve tech debt                            │
  │   2. Inventory            – Finalize dataset and front-end output         │
  ├──────────────────────────────────────────────────────────────────────────┤
  │ PHASE 2 – Eagle Eye (AI-Powered Control Tower)                           │
  │   1. S&OE – Sales & Operations Execution Layer  ← EAGLE EYE STARTS HERE  │
  ├──────────────────────────────────────────────────────────────────────────┤
  │ PHASE 3 – Expand Scope (Future)                                          │
  │   - Manufacturing & Supply Planning                                      │
  │   - Supplier Performance                                                 │
  │   - Flow Analysis                                                        │
  │   - Supply Chain Financials                                              │
  │   - Plan-to-Production                                                   │
  │   - Customer Fulfillment / Allocation                                    │
  │   - First-Time Inventory Placement Success                               │
  └──────────────────────────────────────────────────────────────────────────┘

NOTE: Phase 3 scope items are not yet prioritized. They will be sequenced
after Eagle Eye Phase 2 is underway.

4. BASELINE METRICS — CURRENT STATE (from Technology Roadmap v1)

These are the CURRENT baseline numbers Eagle Eye must help improve.
They represent the "before" state that defines Eagle Eye's business case.

  DEMAND / FORECASTING
  ┌──────────────────────────────┬─────────────────┬──────────────┬──────────┐
  │ Metric                       │ Current         │ Target       │ By       │
  ├──────────────────────────────┼─────────────────┼──────────────┼──────────┤
  │ wMAPE (Forecast Accuracy)    │ 47%             │ 30–38%       │ Q4 2027  │
  │ Weighted Bias                │ 9.5%            │ 1–3%         │ Q4 2026  │
  └──────────────────────────────┴─────────────────┴──────────────┴──────────┘

  INVENTORY
  ┌──────────────────────────────┬─────────────────┬──────────────┬──────────┐
  │ Metric                       │ Current         │ Target       │ By       │
  ├──────────────────────────────┼─────────────────┼──────────────┼──────────┤
  │ In-Stock %                   │ 79–87%          │ 95%          │ Q4 2027  │
  │ Excess Stock                 │ 13–34%          │ 5–10%        │ Q4 2027  │
  └──────────────────────────────┴─────────────────┴──────────────┴──────────┘

  MANUFACTURING (for Phase 3 context)
  ┌──────────────────────────────┬─────────────────┬──────────────┬──────────┐
  │ Metric                       │ Current         │ Target       │ By       │
  ├──────────────────────────────┼─────────────────┼──────────────┼──────────┤
  │ Schedule Compliance          │ 94%             │ 98%          │ Q4 2027  │
  │ Production Lead Time         │ 3 weeks         │ 2 weeks      │ Q4 2026  │
  └──────────────────────────────┴─────────────────┴──────────────┴──────────┘

  KEY PAIN POINTS (current state driving Eagle Eye need):
    - No "golden data layer" — reporting built on inconsistent data sources
    - Multiple Logility instances (Wholesale vs Retail) with no unified view
    - Manual forecasting with heavy Excel dependency
    - Siloed DC inventory — no cross-network visibility
    - AS400/CODIS dependency for order management (single point of failure)
    - wMAPE at 47% with bias drift to 9.5% — too high for reliable decisions

5. PRODUCT DESIGN: METRIC STRUCTURE

Eagle Eye uses a 3-tier metric hierarchy (from MTG-001):

  [Tier 1] EXECUTIVE METRICS
           → Strategic decision-making
           → PHI (Product Health Index) may apply: see Section 6

  [Tier 2] WBR / REVIEW METRICS
           → Weekly Business Reviews
           → Periodic cadence for management-level decisions

  [Tier 3] OPERATIONAL METRICS
           → Planner-level execution
           → Day-to-day exception handling and supply chain actions

**Primary User Interface:**
  Copilot = primary UX for Eagle Eye
  (AI-driven, conversational interface rather than static dashboards)

6. KEY CAPABILITIES EXPECTED (from SC Product Strategy + Tech Roadmap)

Based on the supply chain product strategy, Eagle Eye's control tower layer
is expected to include (not yet confirmed as final scope):

  EXCEPTION MANAGEMENT
    - Prioritized exception queues by planner / supplier / leadership role
    - Alert types: service risk, supply disruption, inventory imbalance,
      demand anomaly, cost/margin impact, plan-adherence, master data
    - Business impact and urgency scoring for each exception

  DECISION INTELLIGENCE
    - Root-cause visibility: demand shift, supply disruption, inventory
      imbalance, supplier delay
    - Recommended actions (expedite, transfer, rebalance, supplier change)
    - Constraint and flexibility indicators
    - Confidence / risk scoring on recommendations

  VISIBILITY LAYER
    - Cross-domain drill paths: KPI → exception → workflow action
    - Role-based views: planner, supplier ops, manager, executive
    - Real-time visibility: demand, inventory, supply, POs, in-transit,
      supplier performance

  WORKFLOW & COLLABORATION
    - Assign, comment, approve, escalate, and resolve decisions
    - Shared workflow semantics across all SC domains
    - Decision traceability: who decided, why, expected impact

  ANALYTICS & REPORTING
    - What-if / scenario modeling
    - Value tracking against baseline metrics (see Section 4)
    - Adoption telemetry
    - KPI governance and shared definitions

  AI / COPILOT FEATURES
    - Standardized AI-driven analysis outputs
    - Self-service insights
    - Statistical + transformer AI models for forecasting assistance
    - Touchless execution where appropriate (with human-in-the-loop override)

  AGENTIC PLANNING (Longer-term, aligned with Q4 2027 roadmap target):
    - Forecasting Agent: Production AI agent handling routine forecast decisions
    - E2E Supply Planning Agent: Orchestrating master agent across all SC domains
    - Routine decisions automated; planner role shifts to data enrichment
      and exception oversight

7. KPI FRAMEWORK (from 2026 Product Roadmap – PHI)

The Product Health Index (PHI) may be used to measure Eagle Eye's product
success alongside operational SC metrics.

  PHI Formula:
    PHI = (BV Score × 0.35) + (Roadmap Alignment Score × 0.20)
          + (On-Time Delivery Score × 0.20) + (NPS Score × 0.25)

  PHI Scoring Thresholds:
  ┌─────────────┬──────────────┬──────────────────────────────────────────┐
  │ PHI Score   │ Health       │ Action                                   │
  ├─────────────┼──────────────┼──────────────────────────────────────────┤
  │ 85 – 100    │ Healthy      │ Scale investment / replicate practices   │
  │ 70 – 84     │ At Risk      │ Targeted intervention required           │
  │ < 70        │ Unhealthy    │ Leadership action / reset needed         │
  └─────────────┴──────────────┴──────────────────────────────────────────┘

  Core KPIs to track (from Product Org Roadmap):
    - % Product initiatives delivering targeted business value
    - % Products with up-to-date, business-aligned roadmaps
    - % Products with on-time delivery
    - NPS (Biz + Eng) for usability, adoption, impact

  SC-specific metrics expected for Eagle Eye:
    - Forecast accuracy and bias (wMAPE, FVA) → baseline in Section 4
    - Service level / OTIF / stockout rate
    - Inventory health (DOS, turns, obsolete %)
    - Supplier responsiveness and PO cycle time
    - Planner adoption rate (workbench usage, override behavior)
    - Exception cycle time and closure rate

OKR FRAMEWORK (from 2026 Product Roadmap w/ Artifacts):
  Eagle Eye initiatives must map to the OKR hierarchy:

    Business Goals → Objectives → Key Results (KRs) → Technology Initiatives
    ─────────────────────────────────────────────────────────────────────────
    Rule: If an initiative doesn't map to a measurable KR, it's a red flag.

  Example relevant OKR for Eagle Eye:
    Objective : Improve delivery promise to customers and reduce friction
    KR        : Improve OTIF from 65% → 80%
    Initiative: Connected Supply Planning & Visibility (Eagle Eye feeds this)

## 8. Team & Stakeholders

  PRODUCT OWNER
    Lucas Trinh         – Vietnam-based PO, Supply Chain Analytics
                          (Onboarded June 2026 per onboarding guide)
                          Reports to: Devon Rumpel

  PRODUCT / IT LEADERSHIP
    Devon Rumpel        – Product Leader, Supply Chain
    Amanda Dalesandry   – Product Manager, Demand / Supply / Inventory
    Cyrissa Quarne      – Product Owner, DSI
    Simon Qin           – Product Owner, Supply Chain AI (Shenzhen)
    Julie Boston        – Head of Product (All AFI)

  SUPPLY CHAIN LEADERSHIP (Key Decision Makers)
    Ashish Saxena       – SVP, Supply Chain, CS/CX, Home Delivery
    Axel Barbara        – VP, Supply Chain Strategy
    Jenny Benedict      – Sr Director, SC Strategy and Execution
    Robert Font Perez   – Sr Manager, Global SC Center of Excellence
    Isaac (Ike) Hoehn   – Sr Director, Supply Planning & Ops (HCMC, VN)
    Matt Jeffries       – Sr Director, Inventory Management & Health
    Seth Riegel         – Sr Director, Demand Planning (Wholesale)
    Josh Mosely         – Sr Director, Demand Planning (Retail)

  AI / DATA PARTNERS
    Steven King         – Sr Director, Data Science & AI
    Zach Zhang          – Director of AI (Shenzhen)
    Cherry Bui          – Team Leader, Global SC Data Analytics (HCMC)

  SC ANALYTICS DELIVERY TEAM (from Technology Roadmap):
    1 Scrum Team | 5 Engineers | 0 PO/PM currently assigned
    Note: 1 open PO req in Asia for SC Analytics → this is Lucas's role
    Team reports engineering to SC (not centrally to product org)

## 9. Open Decisions & Dependencies

  [OPEN] Technology Platform Decision
    Fabric vs. Databricks: Devon Rumpel to bring clarity to the next meeting.
    This decision impacts the Eagle Eye architecture and data layer.
    → Owner: @Rumpel, Devon | @Saxena, Ashish
    → Due: Next meeting (~2 weeks from 22Jun)

  [OPEN] Inventory Data Readiness (Phase 1 Dependency)
    Extract of inventory data + front-end output needed by Ashish for review.
    → Owner: @Font Perez, Robert
    → Status: Pending

  [OPEN] Forecast Accuracy Data (Phase 1 Dependency)
    Sample of forecast accuracy data in CSV or Parquet format needed.
    → Owner: @Font Perez, Robert
    → Status: Pending

  [OPEN] Eagle Eye Scope Finalization
    Full scope, MVP boundaries, and acceptance criteria for Eagle Eye Phase 2
    have not yet been defined. This is an active collection phase.

  [DEPENDENCY] Phase 1 (Forecast + Inventory) must be complete or sufficiently
    stable before Eagle Eye Phase 2 begins.

  [DEPENDENCY] Golden Tables (Medallion Architecture)
    Eagle Eye's data quality is tied to the Golden Tables initiative.
    Golden Tables 1.0 is in progress. Golden Tables 2.0 (AGR) and 3.0
    (Financials) are planned later. Eagle Eye should not be built on top
    of EDW (current) — it should consume from Golden Tables once ready.

  [DEPENDENCY] Streamline Full Wholesale Deploy (Q4 2026)
    Eagle Eye's supply/demand visibility layer depends on Streamline being
    live and stable. Logility full sunset is targeted Q2 2027.

10. SYSTEMS & TOOLS CONTEXT (expanded)

  PLANNING SYSTEMS
    Logility (legacy) → being replaced by Streamline (MVP)
    Streamline        – Core DSI planning engine (Q4 2026 full wholesale deploy)
    AS400 / ERP       – System of record for orders, inventory, financials
                        (Strangler Fig API layer being built)

  DATA FOUNDATION (feeds Eagle Eye)
    Golden Tables     – Medallion architecture (single source of truth)
                        v1.0 in progress; v2.0 (AGR), v3.0 (Financials) later
                        NOTE: Eagle Eye should consume from Golden Tables, not EDW
    EDW               – Current data source (interim, to be replaced)

  ORDER MANAGEMENT & FULFILLMENT
    EPIC / OPRO       – Capacity-aware order promising engine (Aug 2026 target)
    DOM (Nextuple)    – Cross-network fulfillment routing
    AshNode           – Network design tool (NLP-driven, scenario planning)

  AI MODELS
    AI Forecast       – Statistical + transformer models; Low Volume AFI & AGR
                        (target live July 2026); wMAPE target 30%
    Forecasting Agent – Production AI agent for routine forecast decisions
    SC Planning Agent – E2E orchestration agent (Q4 2027 target)

  ANALYTICS / REPORTING
    Power BI          – Current reporting platform (to be moved away from)
    Eagle Eye         – AI-driven control tower replacing Power BI approach

  TARGET UI SURFACE
    One Ashley        – Unified framework where ALL SC KPIs, dashboards,
                        and Eagle Eye insights will ultimately be surfaced
                        (RBAC-enabled, role-based, One Ashley Framework)

  COLLABORATION / DELIVERY TOOLS
    Jira              – Backlog, sprints, defects (Jira Product Discovery for SC)
    SharePoint        – Product documentation (SC Teams Channel)

  OPEN: Fabric vs. Databricks (pending decision – see Section 9)

## 11. Source Documents

  [DOC-01] Ashley Eagle Eye Discussion - 22Jun.txt
           Meeting notes from initial strategy discussion (MTG-001)

  [DOC-02] Ashley Supply Chain Product Strategy (WIP).docx
           Full WIP IT product strategy for SC systems (April 2026)
           Covers: One Ashley vision, domain strategies, roadmap, operating model

  [DOC-03] Supply Chain - Product Strategy.docx
           Detailed capability spec for Demand, Inventory, and Supply modules
           Covers: Forecast management, statistical models, dashboard design

  [DOC-04] 2026 Product Roadmap.pdf (Product Org Roadmap)
           7 product initiatives, KPI structure, PHI scoring model

  [DOC-05] Onboarding Guide - PO (Lucas).docx
           Lucas Trinh onboarding guide (June 2026)
           Covers: SC overview, key people, systems, 30/60/90 day plan

  [DOC-06] 2026 Product Roadmap with Artifacts.pptx
           Extended product roadmap deck; includes OKR framework, goal-to-KR
           mapping examples, and Jira alignment templates

  [DOC-07] Technology Roadmap v1.pptx
           Full enterprise technology roadmap across Finance, Supply Chain,
           Manufacturing, Warehousing & Distribution, HR
           SC section: baseline metrics, systems landscape, Golden Tables,
           AI roadmap, Streamline/DOM/EPIC sequencing, investment estimates

  [DOC-08] Product Organization v1.4.pptx
           Product leadership and PMO org structure (visual/chart format;
           limited text extraction — refer to original file for org charts)

END OF DOCUMENT – Eagle Eye - Project Context & Reference v0.2
