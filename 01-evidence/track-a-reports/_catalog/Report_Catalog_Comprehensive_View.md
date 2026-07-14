# Eagle Eye — Report Catalog: Comprehensive Business View

**A detailed, decision-oriented reference of the 26 current Supply Chain reports**
Source: `02-group-analysis/report-catalog.md` (Robert's team) · enriched for Eagle Eye discovery
*Compiled: 2026-07-03 · For: Decision Registry pre-population*

---

## How to read this

Each report below is presented with: **Purpose** (what business question it answers),
**Decisions** (what a user does with it), **Key metrics**, **Grain**, **Data source**
(governed status), and **Notes / hidden business rules** worth flagging.

Icons: 🟢 governed EDW source · 🟡 partially governed (dataflow) · 🔴 ungoverned
(SharePoint/Excel/iSeries). ⚠ = a business rule or assumption to confirm.

Where the catalog left a gap that matters for Eagle Eye, it's marked **[+ Eagle Eye note]**.

---

## 🔮 GROUP 1 — DEMAND & FORECAST (what will we sell?)

### 1. Demand Review  🔴
- **Purpose:** The engine room of the **demand consensus process** — reconciles actual orders
  vs forecast (Logility + internal), tracks inventory position (SPD, ATP, on-hand), measures
  performance vs consumption targets.
- **Decisions:** Reach agreement on the forecast in **S&OP / SIOP consensus meetings** — the
  critical first step of Integrated Business Planning. Identify forecast bias, inventory-health
  risk, demand-fulfillment gaps.
- **Users:** Demand planners, forecast analysts, supply chain leadership.
- **Notes:** ⚠ Special RH (Restoration Hardware) adjustments, seasonal analysis, embedded
  exception-detection (flags chronic forecast issues, bedroom-set component imbalance).
- **[+ Eagle Eye note]** This is arguably the **single most strategically important report** —
  it feeds the S&OP process. A strong candidate for early Eagle Eye focus because the "consensus"
  it supports is a recurring, high-value, multi-persona decision.

### 2. Product Review (NEW)  🔴🟡
- **Purpose:** Supports demand consensus for the **Integrated Business Planning (IBP)** initiative.
  Forecast accuracy & bias across 30/90-day horizons; inventory positioning; supply-plan execution.
- **Decisions:** Cross-functional review of forecast performance; build consensus on demand signals
  that feed supply, financial, and operational planning.
- **Users:** Demand planners, category analysts, supply chain managers.
- **Notes:** Customer-item level accuracy, seasonal adjustment, YoY growth, real-time inventory.
  Consolidates EDW + dataflows + SharePoint planning lists.

### 3. GF Act+Fcst  🟡🔴
- **Purpose:** Global Furniture (GF) act+forecast — combines historical actual demand (L1ACTD),
  current forecast snapshots (L1Fcst: RSLF/PROL/FUTO), and order history (OrderHist).
- **Decisions:** How does actual demand compare to rolling forecast? Consumption by
  customer/product/warehouse? YoY trend? Lifecycle analysis (new/disco/phase-drop).
- **Notes:** ⚠ `Fiscal Month Indicator` is the central past/current/future filter. Dimensions from
  a shared dataflow; `z_LeatherFlag` from a SharePoint Excel file.

### 4. Weekly Trend Analysis  🟡
- **Purpose:** Track AFI wholesale sales through **three temporal lenses**: invoiced (actual),
  written (order entry — leading indicator), current request (forward demand signal), vs rolling
  forecast over a 26-week window.
- **Decisions (explicit closed loop):** ⭐ When written/requested outpaces forecast → **prepare for
  demand increase**. When invoiced lags written/requested → **growing backlog, intervene**. When
  forecast far exceeds all three actuals → **reduce forecast to match reality**.
- **[+ Eagle Eye note]** One of the clearest **"action when off-track" reports** in the estate —
  the catalog literally spells out the workflow actions. Excellent raw material for Cherry's
  B6 field and for AI recommendations.

### 5. Amazon POS Sales and Forecast  🟡
- **Purpose:** eCommerce channel — consolidates 4 Amazon streams: consumer POS, Amazon FC
  inventory, Amazon's forward forecast, Ashley's wholesale shipments to Amazon.
- **Decisions:** How are items selling on Amazon vs what we shipped? Current inventory position
  (on-hand, open POs, aged)? Does Amazon's forecast align with POS? Are we sizing wholesale orders right?
- **Notes:** ⚠ Scoped to Amazon accounts 3352200 & 3559000. `z_DataRange` bounds visible dates.
- **[+ Eagle Eye note]** Full Prompt #1 analysis now available —
  `01-evidence/track-a-reports/Amazon_POS_Sales_and_Forecast_Analysis.md`. Key finding: the model
  compares Amazon POS vs Amazon's own forecast vs Ashley wholesale sell-in, but has **no measure
  cross-referencing Ashley's internal demand forecast** and **no inventory-coverage or
  forecast-gap measure** — those comparisons are left entirely to manual visual inspection.

---

## 🎯 GROUP 2 — FORECAST ACCURACY (how good is our forecast?) — *Devon priority #1*

### 6. Forecast Accuracy (ItWh)  🔴
- **Purpose:** Item-warehouse forecast accuracy across **5 horizons** (2-week, 30/60/90/120-day).
  Fact `ItWHAccy` joins Logility forecast vs actual demand vs a **naive benchmark**.
- **Metrics:** Bias %, wMAPE, MAPE, naive wMAPE — sliced by category, warehouse, vendor, ABC/XYZ.
- **Decisions:** How good is the model vs a simple baseline? Which planners are accountable
  (planner-assignment tables from SharePoint)? Item-status context (new/in-line/dropping/disco).
- **[+ Eagle Eye note]** You analyzed this one — production-grade, but ⚠ carries the undocumented
  `×3` financial multiplier, `+91-day` shift, and 2M-vs-3M naive-lag comparability trap.

### 7. Forecast Accuracy (Cust_ItWh)  🔴🟡
- **Purpose:** Same, at **customer-item-warehouse** grain, 4 horizons. Compares snapshots vs actual
  vs **two baselines** (naive + unspecified benchmark "B"), with value-add measures.
- **Notes:** ⚠ Structural split — pre-March 2025 (item-WH grain, customer hardcoded `AFICONS`) vs
  post-March 2025 (full cust-item-WH). Snapshot = 3rd Monday of fiscal month, with hardcoded cycle
  deviations. Planner accountability from SharePoint.

### 8. Supply Plan Detail Accuracy  🟡
- **Purpose:** Measures **supply-plan execution accuracy** — planned supply (production, PO,
  transfers) vs actual receipts. *Note: forecast accuracy is NOT measured here — this is about
  whether operations matched the plan.*
- **Grain / horizons:** snapshots at 2/5/9/13-week lead times.
- **[+ Eagle Eye note]** Easy to confuse with reports 6–7. Distinct decision: "did we execute the
  supply plan?" not "was the forecast right?" Worth a clear label to avoid metric confusion.

---

## 📦 GROUP 3 — SUPPLY & INVENTORY (do we have the right stock?) — *Devon priority #1*

### 9. Supply Plan Detail  🟡
- **Purpose:** The SC Planning team's **weekly supply review**. `SupplyPlanDetail` = daily snapshot
  from Logility. Full inventory position per item × warehouse × week-ending: beginning balance,
  firm/planned production, POs, transfers, demand, and derived **Shippable Inventory (SI)**.
- **Decisions:** Is each SKU/WH above or below safety stock (SI-SS)? Where are negative positions?
  What production/POs are scheduled ahead? Capable-to-promise (35-week horizon, `Fiscal Week Indicator` 0=current).
- **Notes:** ⚠ This is the report with **~40 hardcoded `WH## SI` measures** — the headline measure
  cleanup (→ one SI measure sliced by DimWarehouse).

### 10. AFT_SI-SS_PSW  🔴
- **Purpose:** SI-SS health for AFI wholesale, weekly PSW plan. Monitors POs from two lenses: DUE
  (warehouse receipt week) and ETD (departure).
- **Metrics:** SI-SS; demand fulfillment vs sold orders (CO) / SI / SS; week-over-week (current vs
  prior snapshot). Color-coded by order type & SS% status.
- **Notes:** 🔴 Enriched by 5 SharePoint files (Consumer Choice/EVC, vendor list, Wanek DRP, NFM filter).
- **[+ Eagle Eye note]** Full Prompt #1 analysis now available —
  `01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md`. Key findings: a dead duplicate measure
  (`SS% Test` = `SS% DUE`), an inverted-looking RED/GREEN color convention on `Due Color` worth
  confirming isn't a display bug, a non-standard `Demand Fulfill SS` fulfillment-ratio formula that
  may introduce bias, and two contradictory hardcoded UTC-offset columns in the same table.

### 11. Inventory Health  🟡
- **Purpose:** Inventory health + ATP across the warehouse network. Integrates working & current
  supply forecasts, historical shipments, safety-stock targets, dependent demand → weekly item-WH
  on-hand status.
- **Metrics:** 5 health buckets (**Below Max / Over Target / Excess / High Excess / TIB "Throw in
  the Bay"**) by days-of-supply & SS multiples; ATP in-stock rate by recent-launch window.
- **[+ Eagle Eye note]** You analyzed this — the model found was a **demo** (8/24 measures hardcoded,
  WOS=10, logic errors). The *design* is ambitious (5 fact domains, SCD2, ABC bridge) — likely a
  future-state target, not live. Confirm production status.

### 12. JadeTeam Inventory Health  🟡
- **Purpose:** Inventory in **qty / cubic feet / dollars**, allocated across 4 buckets (firm demand,
  net forecast, safety stock, excess). 16 rolling weeks of SPD from **8 regional warehouses**.
- **Decisions:** Identify excess by item-WH-week; supply-chain optimization; drill by division /
  category / collective class. ⚠ Configurable **safety-stock adjustment parameter** for scenario modeling.
- **[+ Eagle Eye note]** Third "inventory health" variant — evidence of estate sprawl (see #11, #17).
  A merge candidate.

### 13. Inv Management  🔴
- **Purpose:** Warehouse ops — **inventory aging** (6/12/18/18+ months), safety-stock changes,
  excess identification across US DCs.
- **Decisions:** Excess by product type / responsible office / vendor → **consolidation or
  liquidation** decisions. Warehouse-specific SI levels.
- **Notes:** 🔴 Central Inventory fact from planning system + vendor master from SharePoint.

### 14. Inventory Transactions and Item Balance Detail  🟡
- **Purpose:** Weekly inventory **movements** (receipts from MO/PO, inter-WH transfers, sales
  shipments) + point-in-time on-hand qty & dollar value.
- **Decisions:** Analyze inventory flow, warehouse utilization by category/storage type, net change.
- **Notes:** FG + specific item classes only; last 18 months. Sources: `InventoryTransactionsWeeklySummary`,
  `ItemBalance` from EDW.

### 15. Safety Stock Analysis  🔴🟡
- **Purpose:** Safety-stock optimization — inventory levels/status/cost vs SS targets.
- **Decisions:** Which items over/understocked? Does inventory match demand variance? Do SS
  quantities hit turnover & cost goals? Full lifecycle (current/plan-drop/new/disco).
- **Notes:** Weekly & month-end reviews, variance analysis.

### 16. Top Negatives  🔴
- **Purpose:** Identify **critical inventory shortfalls** ("top negatives"). Fact `SPD2` tracks SI,
  SS, and customer-order gaps by item/WH/vendor, by product group & import/domestic.
- **Decisions:** Prioritize & resolve inventory gaps threatening customer fulfillment (8-week
  forward SI, Wanek item planning).
- **Users:** Supply chain analysts & planners.

---

## 🏭 GROUP 4 — MANUFACTURING & CAPACITY (can we make/source enough?)

### 17. Act+Fcst by WNK & MILL Prod Resource  🟡
- **Purpose:** Does **Wanek/Millennium** production capacity cover combined demand (actual open
  orders + forecast) at item-WH-production-resource level, weekly?
- **Notes:** ⚠ Filtered to Wanek (900515/600039/900639) & Millennium (624556) codes. ⚠ **56-day
  offset** converts customer-request-week → estimated-delivery-week. Vendor-shipped from MAPICS.
- **[+ Eagle Eye note]** Full Prompt #1 analysis now available —
  `01-evidence/track-a-reports/Act_Fcst_by_WNK_MILL_Prod_Resource_Analysis.md`. Key finding:
  `Prod Capacity` is defined as `MAX(Firm+Planned, TotalAvailHours)` — by construction, capacity
  can never show as below the planned load, meaning the measure reflects what was *scheduled*,
  not what was actually *available*. Also flags a fencepost inconsistency (16-week filter divided
  by 17) and no measure capturing planned-vs-actual transit-time variance.

### 18. Act+Fcst vs Manufacturing  🟡
- **Purpose:** Domestic US finished-goods capacity vs blended demand (actual orders + resultant/
  promotional forecast) — **then steps up a level**: Wanek/Millennium make the kits/components that
  feed domestic FG, so their capacity (`ProdCapacity`) and output (`VendorShipped`) must also suffice.
- **Notes:** ⚠ 56-day ETD offset = lead time from WNK/MILL kit shipment to domestic FG conversion.

### 19. Production Capacity Vs Forecast  🟡
- **Purpose:** Forecast vs production & procurement capacity — forecasted qty vs actual MOs, POs,
  receipts, by item/WH/production-resource.
- **Decisions:** Where does supply exceed or fall short of demand? Bottlenecks & capacity
  utilization by location/timeframe.
- **Notes:** ⚠ Focused on **"Z" class** products; internal manufacturing + external vendor supply.

### 20. DvC - WanekMillenium  🔴
- **Purpose:** **Demand vs Capacity** for Wanek & Millennium over a rolling **30-week** horizon —
  can each facility absorb planned/firm/shipped volumes from the PSW?
- **Decisions:** Actual/promised capacity vs constrained & unconstrained supply plan? Do factory
  scans (FG Output, RP Scan) track PSW projections?
- **Notes:** 🔴 Reads **iSeries ODBC directly** (WFVNPROD, MILPROD, AFIPROD) + SharePoint Excel
  capacity overrides. Linear trendline across ETD weeks.

### 21. Rolling Report - Wanek Millen  🔴
- **Purpose:** PO **rolling activity & firm commitments** for vendors 600039/900515/900639/624556
  (finished goods + repair parts).
- **Decisions:** % orders held firm vs rolled to later ETDs (compliance); SS%; monitor **late ASNs**
  (Advanced Ship Notices) arriving Mon–Tue.
- **Notes:** 🔴 iSeries ODBC.

---

## 🚚 GROUP 5 — RECEIPTS & FULFILLMENT (is it arriving / shipping on time?)

### 22. Receipts  🟢
- **Purpose:** Receipt & in-transit visibility — 3 streams: received inventory by WH/week
  (`TotalReceipts`), open PO receipts w/ vendor & due-date (`PurReceipts`), on-order/in-transit
  w/ ETA & cost (`Receipts`).
- **Decisions:** Unified view of goods movement through the pipeline for planning & operational monitoring.

### 23. On Time % by Customer  🟢
- **Purpose:** On-time shipment performance by customer — shipment dates vs **original and current**
  request/promise dates. Daily & weekly. Special view for **Warehouse 335** wholesale.
- **Decisions:** Fulfillment SLA visibility; performance trends by customer/product/time.

### 24. Supplier On-Time Performance  🔴
- **Purpose:** **Supplier** on-time delivery — international vendor shipping compliance vs firmed PO
  demand, two windows (W3 3-week / W4 4-week, toggled by slicer).
- **Metrics:** Delayed shipments by pieces & container volume; **penalty amounts** (2%/5% of VDP
  price for 2/3 weeks late); fiscal YTD on-time %.
- **Notes:** 🔴 PSW on-time fact + Ashton-specific vendor table; Vendor List (SharePoint Excel) for
  analyst assignments; ABC coding to prioritize high-impact suppliers.

---

## ♻️ GROUP 6 — LIFECYCLE (when to launch / retire?)

### 25. Plan Drop 1  🟡
- **Purpose:** End-of-life projection — combines historical demand (ACT_DEMD_0..11) + forward
  forecasts (Current..Month+11 FC) to **estimate stockout dates** for items nearing EOL.
- **Decisions (explicit closed loop):** ⭐ Project when on-hand will be exhausted. Flags significant
  deviation between avg historical monthly sales & forward forecast → **planner updates forecast →
  stockout date auto-recalculates**.
- **[+ Eagle Eye note]** Another clean closed-loop example (like #4). The catalog spells out the
  action-and-feedback cycle — ideal for Cherry's B6 and AI recommendations.

### 26. When to Disco v2  🟡
- **Purpose:** "When to Discontinue" — monitors on-hand/in-transit/on-order + months-of-supply to
  find items below the **2-week supply threshold** — the trigger to change status Current →
  Discontinued and notify sales.
- **Decisions:** Manage orderly product exits; coordinate discontinuation notices with sales.
- **Notes:** ⚠ Separate tracking for WH 335; customer-allocated orders; planner assignments.

---

## Cross-cutting observations (the "extra ideas" worth flagging)

**A. Estate sprawl is visible at the business level.** Three inventory-health reports (#11, #12, #13)
answer overlapping questions from different teams; two forecast-accuracy reports (#6, #7) differ only
by grain; five capacity reports (#17–21) all ask "can we make/source enough." This is the sprawl
story *in business terms* — stronger than a raw dashboard count.

**B. Two reports already document the full "closed decision loop"** — Weekly Trend Analysis (#4) and
Plan Drop 1 (#25) explicitly state the action taken when the number moves. These are your best
templates for what a *complete* Decision Registry row looks like, and prime AI-recommendation targets.

**C. Hidden business rules recur and need a governed home** (feeds Decision Registry D5):
- **56-day ETD offset** (#17, #18) — request-week → delivery-week conversion.
- **3rd-Monday-of-fiscal-month snapshot** + hardcoded cycle deviations (#7).
- **2-week supply threshold** as the disco trigger (#26).
- **Pre/post March-2025 grain split**, `AFICONS` hardcode (#7).
- **Penalty tiers** 2%/5% of VDP (#24).
Each is a business decision embedded in code — Eagle Eye must treat these as governed parameters,
not per-report constants.

**D. The S&OP / IBP thread is the strategic backbone.** Demand Review (#1) and Product Review (#2)
both exist to drive **demand consensus** — the first step of Integrated Business Planning. These are
not just reports; they support a recurring, cross-functional, high-value *decision forum*. If Eagle
Eye wants an early high-impact win with executive visibility, the S&OP consensus decision is it.

**E. Governance risk concentrates in Groups 3–4.** Most 🔴 (ungoverned) reports are in Supply/
Inventory and Manufacturing — exactly Devon's priority areas. The manufacturing reports (#20, #21)
reading iSeries directly are the deepest data-readiness risk.

---

## How to use this for the Decision Registry

This catalog lets you **pre-populate the `[Model]` fields for all 26 reports** without opening a
single semantic model — Robert already documented domain (A3), question (B1), metrics (C1), grain
(C3), source (C6), and several assumptions (D5). What remains is the `[Interview]` half — persona
(B3), workflow actions (B5–B6), shadow tools (B8), and user trust (D3) — which only business-user
conversations can fill.

**Suggested priority order for deep discovery** (by Devon's focus × decision value × readiness):
1. Demand Review (#1) — S&OP backbone, high value
2. Forecast Accuracy ItWh (#6) — priority #1, already analyzed
3. Supply Plan Detail (#9) — supply backbone, headline measure cleanup
4. Inventory Health (#11) — priority #1, but confirm demo vs production first
5. Weekly Trend Analysis (#4) & Plan Drop 1 (#25) — clean closed-loop templates

---

*Companion to: Decision Registry Schema v0.2, Decision Intelligence Framework. Enriched from
`report-catalog.md`; the [+ Eagle Eye note] items are additions beyond the source.*

---

## Addendum — reports found after this catalog was compiled (added 2026-07-13)

This catalog was compiled around the original 26-report estate. Discovery has
since surfaced 2 reports that were never part of that 26, plus status updates
on 3 that were:

| Report | Group (nearest fit) | Status | Note |
|---|---|---|---|
| **Supplier ABC Analysis** | Purchasing (new domain) | 🟡 Full Prompt #1 analysis | Not in the original 26 — found via a workspace scan for Manufacturing-adjacent reports. Classifies suppliers into A/B/C tiers against forward 17-week demand. |
| **Supplier On-Time Performance** | Group 5 — Receipts & Fulfillment (#24 in this catalog) | ✅ Full Prompt #1 analysis | Was catalog-level only when this document was written; now fully analyzed. |
| **Rolling Report - Wanek Millen** | Group 4 — Manufacturing & Capacity (#21) | ✅ Full Prompt #1 analysis | Was catalog-level only when this document was written; now fully analyzed — see [Manufacturing_and_Production_Capacity.md](../../../08-business-handbook/Manufacturing_and_Production_Capacity.md). |
| **Plan Detail Timeline** | Group 3 — Supply & Inventory (adjacent to #9, Supply Plan Detail) | 🟡 Full Prompt #1 analysis | **Not a renamed or replacement version of Supply Plan Detail** — different EDW source (`PowerBI_SupplyChain.SchedulingPlannedDetailTimeline`, a single ungoverned view, vs. Supply Plan Detail's `SupplyChain_Enh.DemandForecastSnapshot`), different workspace, different compatibility level (2020-era). Overlapping business purpose (item × warehouse supply/demand/inventory position over time) is why the two are easy to confuse. Supply Plan Detail itself **remains unanalyzed** — this report does not close that gap. |

This brings the total analyzed-report count to **30** (26 original + these 2
net-new, with 2 of the original 26 upgraded from catalog-level to full
analysis in the same period). The 26-report framing above (groups, counts,
priority order) reflects the original catalog date and has not been
renumbered — treat the table above as the current delta on top of it.
