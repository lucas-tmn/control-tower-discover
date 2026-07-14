---
type: Map
title: Gap-Fill Candidates — OKF [FILL IN] ↔ Discovered AS-IS Values
description: Every [FILL IN] placeholder in the OKF bundle, matched with values, behaviors, or process facts discovered in the reporting estate. Proposed as starting points for governance approval, not as automatically correct answers.
tags: [bridge, gap-fill, governance, thresholds, okf]
timestamp: 2026-07-10
status: draft
---

# Gap-Fill Candidates

**How to read:** the OKF bundle deliberately leaves `[FILL IN]` where a business
decision is needed. Track A discovery found what the estate *currently does* in
many of those spots. A current-state value is not automatically the right governed
value — several are contradictory or suspect — but it is the honest starting point
for the approval conversation. Rows marked ⚔️ have **competing AS-IS values** that
need arbitration, which is itself a finding.

**Update 2026-07-10:** cross-checked against `07-fabric-build/docs/model-definitions/`
— the data-engineering team's concrete, engineering-ready gold table definitions
(real ETL SQL, ownership, dates). Each row now carries a **Status**: 🟢 Resolved
(the gold definition answers this concretely), 🟡 Partially resolved (a governed
attribute/column now exists, but the exact business value/threshold still isn't
set), or ⚪ Still open (neither side has an answer — a genuine two-team gap, not
just a documentation lag).

## Metric thresholds

| OKF gap (file → placeholder) | Status | AS-IS discovered value(s) | Evidence | Recommendation |
|---|---|---|---|---|
| `metrics/forecast_accuracy.md` → neutral-bias threshold & accuracy-band boundaries `[FILL IN: business-approved threshold values]` | ⚪ Still open | ⚔️ `Bias Threshold = 0.08` (ItWh model, ✅ .bim-verified) vs `0.10` (CustItWh model). Demand Review separately uses `0.1` bias-alert and `25%/20%/15%` AND-combined chronic thresholds. Accuracy bands `<70/70-80/80-90/>90%` appear in the OKF page itself as examples. Neither `07-fabric-build/docs/model-definitions/` nor the OKF bundle sets a governed number — this is a genuine business decision, not a documentation gap | [Forecast_Accuracy_ItWh](../01-evidence/track-a-reports/Forecast_Accuracy_ItWh_Analysis.md) §9, [CustItWh](../01-evidence/track-a-reports/Forecast_Accuracy_CustItWh_Analysis.md) §9, [Demand Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §9; PAT-03/PAT-05 | Present both values + the sibling-divergence finding to the planning team; pick one governed neutral threshold. The 25/20/15% chronic triple (DEC-009) should be revisited at the same session since it drives people-performance labeling |
| `metrics/overstock_exposure.md` → planning horizon `[FILL IN: planning horizon in days, e.g., 90]` and `glossary/overstock.md` → threshold `[FILL IN: X weeks of forward demand above SS]` | ⚪ Still open | ⚔️ Two competing rules in production: `SI > SS × 1.4` (Demand Review `SI Overage`) and the Inv Management excess waterfall (excess vs weeks 2–5 / 6–9 plan demand, i.e. ~1–2 month horizons, with a parallel 6-month variant). No gold-layer resolution exists yet either | [Demand Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §9, [Inv Management](../01-evidence/track-a-reports/Inv_Management_Analysis.md) §3/§9 | Arbitrate: 1.4×SS is simple but unexplained; the waterfall is richer but distorted at aggregate level (BUG-010). Neither should be adopted as-is without an owner |
| `metrics/coverage_days.md` → standard horizon `[FILL IN: 30, 60, or 90 days]` | ⚪ Still open | AS-IS months-of-supply logic uses weeks 2–5 (≈30d) and weeks 6–9 (≈60d) windows; When to Disco uses month-based DOS | [Inv Management](../01-evidence/track-a-reports/Inv_Management_Analysis.md) §3, [When_to_Disco_v2](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md) | 30/60 split already de-facto standard in excess logic |
| `metrics/coverage_days.md` → lead-time column `[FILL IN: confirm lead time column — not currently in DimProduct]` | 🟡 Partially resolved — **correction, see note** | **Self-correction (2026-07-10):** this row was marked "confirmed absent on both sides" in the 2026-07-10 pass, but that was checked only against `DimProduct.md`. `07-fabric-build/docs/model-definitions/dimension-tables/DimVendor.md` actually defines `LeadTime INT` (plus `AFILeadTime`/`WVFLeadTime`, flagged in the doc itself as "WVF deprecated — need differentiated column"). Lead time lives at the **vendor** level, not the product level the OKF placeholder assumed — arguably the more correct home for it, since transit/order lead time is a vendor/route attribute, not an item attribute. The schema exists; whether it's populated with real per-vendor values (vs. the AS-IS estate's single hardcoded +56-day constant for Wanek/Millennium) is unconfirmed | [Demand_Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §4, [Act_Fcst_by_WNK_MILL](../01-evidence/track-a-reports/Act_Fcst_by_WNK_MILL_Prod_Resource_Analysis.md), `07-fabric-build/docs/model-definitions/dimension-tables/DimVendor.md` | Confirm `DimVendor.LeadTime` is populated with real per-vendor values, not left blank/default. Also resolve the `AFILeadTime`/`WVFLeadTime` deprecation the doc itself flags as unfinished before relying on this column |
| `glossary/recently_introduced.md` → window `[FILL IN: e.g., within the last 12 months]` | 🟡 Partially resolved | Safety Stock Analysis hardcodes "Recent Launch" = Qtr4 2024–Qtr4 2025 (frozen list, ~5 quarters ≈ 15 months). `DimProduct.md` now defines governed ETL-computed columns `LifecycleStage`, `DiscontinuationHorizon`, and `LifecycleSortOrder` — the **schema** for a non-frozen lifecycle window now exists, replacing the old per-model hardcoded quarter lists, but the doc doesn't state what window value populates `DiscontinuationHorizon` — that's still a business decision | [Safety_Stock_Analysis](../01-evidence/track-a-reports/Safety_Stock_Analysis.md) §6, `07-fabric-build/docs/model-definitions/dimension-tables/DimProduct.md` | Confirm the intended value for `DiscontinuationHorizon` with the product/lifecycle owner — the hard part (a governed column to hold it) is already built |
| `glossary/stockout.md` → phase-2 thresholds `[FILL IN]` | ⚪ Still open | Demand Fulfillment's SI-Negative ranking defines de-facto "at-risk" severity; AFT_SI-SS_PSW color logic encodes severity bands (subject to BUG-012 inversion question) | [Demand_Fulfillment](../01-evidence/track-a-reports/Demand_Fulfillment_Analysis.md), [AFT_SI-SS_PSW](../01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md) §9 | Confirm the color convention first (BUG-012), then formalize |

## Process documentation gaps

**Not resolved by the Fabric build** — these are meeting/workflow process docs;
`docs/model-definitions/` documents data schema, not decision-making process. All
remain ⚪ still open, exactly as before, pending Track B interviews.

| OKF gap | AS-IS discovered facts | Evidence |
|---|---|---|
| `processes/demand_consensus_meeting.md` → cadence, participants, inputs, KPIs, decision rules, outputs (7 placeholders) | Monthly cycle anchored by `Cycle_Dates` SharePoint list; inputs = Demand Review report (working vs prior vs 90d plan, exception flag, chronic bias flag, consumption pace, RH channel swap); decision = approve/push-back working forecast (DEC-008); exception mechanics = threshold-driven `Exception Flag`; post-meeting output = push to Logility/supply. Personas hypothesized in DEC-008/009 — **interview-pending** | [Demand_Review_Analysis](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §2, [DEC-008](../02-decision-registry/decisions/DEC-008.md), [DEC-009](../02-decision-registry/decisions/DEC-009.md) |
| `processes/lifecycle_planning.md` → all sections (7 placeholders) | Lifecycle machinery found across: `z_drop_dates` LAG-window status log + `Current/Future Status` (Demand Review), When to Disco v2 (disco-notice timing decision with WH335-specific measures), Plan Drop cluster, Planner Assignment (lifecycle-based planner routing). Schema-side note: `DimProduct.md`'s new `LifecycleStage`/`DiscontinuationHorizon`/`PlanDropDecisionDate` columns (see metric-thresholds table above) will give this process a governed data foundation once built, but the process itself — who decides, when, on what trigger — is still unconfirmed | [When_to_Disco_v2](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md), [Planner_Assignment](../01-evidence/track-a-reports/Planner_Assignment_Analysis.md), [Demand_Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §2 |
| `glossary/demand_consensus.md` → cadence & stakeholders `[FILL IN]` | Same facts as demand_consensus_meeting row above | Same |
| `glossary/customer_group.md` → source `[FILL IN: ERP or MDM source for DimCustomer]` | 🟢 **Resolved.** `07-fabric-build/docs/model-definitions/dimension-tables/DimCustomer.md` confirms the governed source: `AFISales_DW.DimCustomers` (SQL master, ERP-side) unified with `PowerBI_SupplyChain.CustomerAcctMaster_AFI` — the dataflow copy is **already retired** after a parity check. This directly answers the OKF placeholder. AS-IS reads `z_CustomerMaster` from the shared dataflow (workspace `a47e4573…`) → `PowerBI_Supplychain` layer, i.e. the AS-IS estate is still on the path the gold model has already moved off of; Weekly Trend appends 8 synthetic group rows locally (hack to be retired by governed DimCustomer) | [Demand_Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §4/§6, [Weekly_Trend](../01-evidence/track-a-reports/Weekly_Trend_Analysis.md) §6, `07-fabric-build/docs/model-definitions/dimension-tables/DimCustomer.md` |

## Dataset documentation gaps

| OKF gap | Status | AS-IS discovered facts | Evidence |
|---|---|---|---|
| `metrics/forecast_accuracy.md` → ERP source-field mapping `[FILL IN]`; consensus/lag dataset docs `[FILL IN]` | 🟡 Partially resolved | AS-IS equivalents already live: `Cycle_Dates` SharePoint list (ID `94a48657`, SCPGlobalTeam site) ↔ planned `DimFcstConsensusCycleDates`; snapshot CASE logic in both Fcst Accuracy models' SQL ↔ planned `FcstAccuracySnapshotDates` (currently carrying BUG-001). `07-fabric-build/docs/model-definitions/scp-core-model/FactWorkingForecast.md` and `FactCurrentForecast.md` now define the governed forecast-type structure (Resultant/PromoLift/Total, i.e. RSLF/PROL/Total) and snapshot handling concretely — the *structure* side of this gap is resolved; the *ERP source-field mapping* and *cycle-date governance* side is not yet built (both docs note "Implementing... in anticipation of transition in Q3," i.e. still in progress) | [Demand_Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §4; Bug log BUG-001; `07-fabric-build/docs/model-definitions/scp-core-model/FactWorkingForecast.md`, `FactCurrentForecast.md` |
| `datasets/tables/demand_forecast.md` → horizon, cadence, data-quality issues `[FILL IN ×3]` | 🟡 Partially resolved | Weekly Trend reads it forward **6 months, latest snapshot only, weekly grain**; known issue: it's the only model on this older table while siblings use `DemandForecastSnapshot` (PAT-07 comparability). `FactCurrentForecast.md` is the gold successor to this legacy table — it already documents weekly grain and latest-snapshot handling, and explicitly flags itself as "in anticipation of transition in Q3," confirming the data-engineering team knows this table needs replacing. The specific data-quality issue (Weekly Trend's stale legacy source) should be logged in the new doc once migration happens — not yet done | [Weekly_Trend](../01-evidence/track-a-reports/Weekly_Trend_Analysis.md) §4, `07-fabric-build/docs/model-definitions/scp-core-model/FactCurrentForecast.md` |
| `datasets/tables/sales_orders.md` → known data-quality issues `[FILL IN]` | ⚪ Still open | From `OrdHist` SQL: 2-year rolling window (+6 future months), `1.08/0.92` fallback seasonality injection when factor missing, permanent exclusions `Warehouse <> '55'` and `Account <> '3824800'` (reasons unknown), `LVL_NBR = 3` seasonality level undocumented. No `sales_orders`-equivalent gold fact table exists yet in `07-fabric-build/docs/model-definitions/` (only `FactSupplyPlanDetail`, `FactWorkingForecast`, `FactCurrentForecast` are built so far) — this is a genuine gap on both sides, not just missing documentation | [Demand_Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) §9 |

**Resolution summary (2026-07-10, corrected):** of 11 gap rows across all three
tables, **1 fully resolved** (customer source), **4 partially resolved** (schema/
structure now exists, business value or population still pending — including a
same-day self-correction on the lead-time row, see its note), **6 still open**
(genuine two-team gaps or pure business decisions, not documentation lag). No row
was marked resolved by inventing a plausible-sounding answer — every status above
traces to a specific file and line in `07-fabric-build/`.

## Handoff protocol

1. Review this table with Robert; for each row he either adopts a value
   (bundle `status: draft → active`), schedules an arbitration (⚔️ rows), or
   rejects with rationale. 🟢/🟡 rows can move faster since the schema work is
   already done — the ask is confirming a value, not building anything.
2. Adopted values get edited **in his upstream repo**, then re-vendored here
   (see `../05-okf-bundle/PROVENANCE.md`) — never patched locally.
3. Interview-pending facts (personas, meeting mechanics) get confirmed via
   Track B before adoption; the bug-led "gift" protocol
   (`../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md`) applies.
4. ⚪ Still-open rows confirmed absent from `07-fabric-build/` too (lead-time
   column, `sales_orders` fact) should go to the data-engineering team as schema
   gaps, not just to Robert as documentation gaps — they need a build decision,
   not just a governance decision.
