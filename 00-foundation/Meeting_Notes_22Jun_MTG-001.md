# Meeting Notes — Eagle Eye Discussion, 22 Jun (MTG-001)

> **PROJECT:** EAGLE EYE
> **DOCUMENT TYPE:** Meeting Notes
> **DOCUMENT ID:** MTG-001
> **DATE:** 2026-06-28
> **STATUS:** Draft

MEETING: Control Tower Strategy, Prioritization & Next Steps

## 1. Meeting Objective
   - Align on future vision and direction of the Supply Chain Control Tower
   - Review current progress (forecasting + inventory)
   - Define priorities, sequencing, and next steps
   - Clarify technology direction and governance approach

## 2. Key Takeaways
   - Control tower adoption is currently near zero, despite strong data foundation
   - Team must shift from: Building dashboards → Delivering decision intelligence
     + measurable value
   - Immediate focus:
       * Finish forecasting + inventory (with usable data)
       * Then transition to AI-powered control tower (Eagle-Eye). Roadmap below.

## 3. Eagle-Eye Strategy & Vision
   - Move away from Power BI–centric reporting
   - Shift From: Reporting → Decision System
   - AI-driven analysis:
       * Standardized outputs
       * Self-service insights
   - Copilot = primary user-interface
   - 3-Tier Metric Structure:
       [Tier 1] Executive Metrics      – Strategic decision-making
       [Tier 2] WBR / Review Metrics   – Weekly business reviews
       [Tier 3] Operational Metrics    – Planner-level execution

## 4. Prioritization & Roadmap

   ┌─────────────────────────────────────────────────────────────────────────┐
   │ PHASE 1 – Complete Current Foundation                                   │
   │   1. Forecast (Back-End)                                                │
   │      - Resolve tech debt                                                │
   │   2. Inventory                                                          │
   │      - Finalize inventory dataset and front-end output                  │
   ├─────────────────────────────────────────────────────────────────────────┤
   │ PHASE 2 – Transition to Eagle-Eye                                       │
   │   1. S&OE (Execution Layer)                                             │
   ├─────────────────────────────────────────────────────────────────────────┤
   │ PHASE 3 – Expand Scope (Later Prioritization)                           │
   │   - Manufacturing & Supply Planning                                     │
   │   - Supplier Performance                                                │
   │   - Flow Analysis                                                       │
   │   - Supply Chain Financials                                             │
   │   - Plan-to-Production                                                  │
   │   - Customer Fulfillment / Allocation                                   │
   │   - First-Time Inventory Placement Success                              │
   └─────────────────────────────────────────────────────────────────────────┘

## 5. Action Items

   [ ] Inventory Data
       Description : Send an extract of the inventory data and the current
                     front-end output in a spreadsheet (CSV or similar
                     readable format) to Ashish
       Owner       : @Font Perez, Robert
       Status      : Open

   [ ] Forecast Accuracy Data
       Description : Send a sample of the forecast accuracy data in CSV format
                     (or Parquet with a sample in spreadsheet format) to Ashish
       Owner       : @Font Perez, Robert
       Status      : Open

   [x] Next Meeting Scheduling
       Description : Schedule a follow-up meeting in two weeks to review
                     progress and touch base on discussed topics
       Owner       : Jenny
       Status      : DONE

   [ ] Fabric vs. Databricks Clarity
       Description : Bring more clarity regarding the Fabric vs. Databricks
                     decision to the next meeting and gather additional
                     information as needed
       Owner       : @Saxena, Ashish | @Rumpel, Devon
       Status      : Open

END OF DOCUMENT – MTG-001
