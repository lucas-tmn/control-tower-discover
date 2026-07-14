---
type: Map
title: Concept Map — OKF Concepts ↔ Reporting Estate
description: For each governed OKF concept (metric, entity, glossary term, dataset, process), the current-state implementations found in the Power BI estate, with confidence levels and known contradictions.
tags: [bridge, concept-map, metrics, entities, glossary, as-is, to-be]
timestamp: 2026-07-09
status: draft
---

# Concept Map — OKF ↔ Estate

Confidence legend: **Direct** = same concept explicitly · **Probable** = strong
match, naming/scope differs · **Candidate** = plausible, needs SME confirmation.

## Metrics

| OKF concept (TO-BE) | AS-IS implementations found | Confidence | Contradictions / notes |
|---|---|---|---|
| [Forecast Accuracy](../05-okf-bundle/bundle/metrics/forecast_accuracy.md) — governed family (MAPE, wMAPE, wMPE, RMSE, PVA), Lag-0…4, consensus-snapshot-aligned, error = `Forecast − Actual` | **3 sibling models**: [SCP Forecast Accuracy](../01-evidence/track-a-reports/Forecast_Accuracy_Analysis.md), [CustItWh](../01-evidence/track-a-reports/Forecast_Accuracy_CustItWh_Analysis.md), [ItWh](../01-evidence/track-a-reports/Forecast_Accuracy_ItWh_Analysis.md); plus accuracy blocks in [Demand Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md), [GF FC Tool](../01-evidence/track-a-reports/GF_FC_Tool_Analysis.md), [Weekly Trend](../01-evidence/track-a-reports/Weekly_Trend_Analysis.md) (broken — BUG-003) | **Direct** | OKF's legacy-label table (`2Week→Lag-0` … `120 Day→Lag-4`) maps exactly onto the `ForecastPeriod` values in the AS-IS models. OKF names the target fact `FcstAccuracy_CustItemWh`; AS-IS `Fcst_Accuracy_Cust_It_Wh` exists but with a March-2025 grain break (PAT-07). OKF warns against exactly the "wrong snapshot date" failure that BUG-001 (year-typo `01/25/2025`) instantiates. OKF's naive forecast (prior period, 4-4-5 normalized) is the governed answer to the AS-IS naive-lag 2M/3M mismatch. Bias tolerance: AS-IS uses 0.08 (ItWh) vs 0.10 (CustItWh) (PAT-03); OKF leaves neutral threshold as `[FILL IN]` → see gap-fill map. |
| [Shippable Inventory](../05-okf-bundle/bundle/metrics/shippable_inventory.md) | `SI` in [Demand Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md), [Demand Fulfillment](../01-evidence/track-a-reports/Demand_Fulfillment_Analysis.md), [AFT_SI-SS_PSW](../01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md); per-warehouse `WH## SI` / `Whse ## - SI` measures in Supply Plan Detail & [Inv Management](../01-evidence/track-a-reports/Inv_Management_Analysis.md) (PAT-08) | **Direct** | AS-IS implements SI as dozens of hardcoded per-warehouse measures; OKF implies one measure over [DimWarehouse](../05-okf-bundle/bundle/datasets/tables/DimWarehouse.md). PAT-08 is the migration case. |
| [Safety Stock Gap](../05-okf-bundle/bundle/metrics/safety_stock_gap.md) | `SS Gap` calc column (Demand Review), `SI-SS` family ([AFT_SI-SS_PSW](../01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md) — DEC-005), [Safety Stock Analysis](../01-evidence/track-a-reports/Safety_Stock_Analysis.md) | **Direct** | AS-IS also has the *inverse* concept `SI Overage = SI > SS × 1.4` (undocumented 1.4×) — closest OKF concept is Overstock Exposure below. |
| [Overstock Exposure](../05-okf-bundle/bundle/metrics/overstock_exposure.md) + [Overstock](../05-okf-bundle/bundle/glossary/overstock.md) glossary | `True Excess` / `True Excess Type` waterfall in [Inv Management](../01-evidence/track-a-reports/Inv_Management_Analysis.md) (DEC-004); `SI Overage` (Demand Review); `Excess FG $`; excess buckets in Inventory Health models | **Probable** | OKF threshold is `[FILL IN: X weeks of forward demand above SS]`; AS-IS operates two competing rules: `SS × 1.4` (Demand Review) and the Inv Management excess waterfall. Reconciliation needed — see gap-fill map. |
| [Days of Supply](../05-okf-bundle/bundle/metrics/days_of_supply.md) / [Coverage Days](../05-okf-bundle/bundle/metrics/coverage_days.md) | `MOS Case 1/2/111/6-x` months-of-supply in [Inv Management](../01-evidence/track-a-reports/Inv_Management_Analysis.md); DOS logic in [When to Disco v2](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md) | **Probable** | AS-IS MOS uses `AVERAGEX` over per-item ratios (BUG-010 distortion); OKF definition is the natural governed replacement. Months vs days unit difference. |
| [ATP In Stock](../05-okf-bundle/bundle/metrics/atp_in_stock.md) | `In Stock` from `Week_2_ATP` (Demand Review); [Complete Series In Stock](../01-evidence/track-a-reports/Complete_Series_In_Stock_Analysis.md) | **Direct** | |
| [Projected Fulfillment Rate](../05-okf-bundle/bundle/metrics/projected_fulfillment_rate.md) | `DF rate` in [Demand Fulfillment](../01-evidence/track-a-reports/Demand_Fulfillment_Analysis.md), [Product Review](../01-evidence/track-a-reports/Product_Review_Analysis.md) and [Product Review (NEW)](../01-evidence/track-a-reports/Product_Review_NEW_Analysis.md) | **Probable** | ⚠️ AS-IS has **two different DF-rate formulas under the same name**: old Product Review `(FD + SI_neg)/FD` vs NEW `(FD + NF + SI_neg)/(FD + NF)` (BUG-018 / PAT-03). OKF definition should arbitrate which becomes governed. |

## Entities & dimensions

| OKF concept | AS-IS reality | Confidence | Notes |
|---|---|---|---|
| [Warehouse](../05-okf-bundle/bundle/entities/warehouse.md) + [DimWarehouse](../05-okf-bundle/bundle/datasets/tables/DimWarehouse.md) — incl. virtual warehouses (`1A`,`ECA`), `PlanningWarehouse` collapse, Intransit & Container Direct types | No conformed warehouse dimension in the estate (PAT-08); warehouse `335` (Ashton — a distinct facility per governed `DimWarehouse`, network-wide primacy not confirmed, see `07-fabric-build/WAREHOUSE_335_RECONCILIATION.md`) hardcoded in 11+ models with inconsistent include/exclude; `C/CNW` container-warehouse string hardcoded in Demand Review filters | **Direct** | OKF's Container Direct Warehouse type explains the AS-IS `C/CNW` exclusions; its Intransit type is a strong candidate explanation for satellite/335 flows. The taxonomy answers several open questions in DEC-004 F4. |
| [Product](../05-okf-bundle/bundle/entities/product.md) | `z_ProductDetails` dataflow + local lifecycle groupings per model (Demand Review §6; Safety Stock hardcoded "Recent Launch" quarters) | **Probable** | AS-IS lifecycle buckets are re-derived locally per model — drift risk the OKF entity would eliminate. |
| [Customer](../05-okf-bundle/bundle/entities/customer.md) + [Customer Group](../05-okf-bundle/bundle/glossary/customer_group.md) | `z_CustomerMaster` dataflow; Weekly Trend appends 8 synthetic customer-group rows in Power Query (structural hack); On Time % has no customer master at all (16-account DSG SWITCH) | **Direct** | The synthetic-row hack and the DSG SWITCH are exactly the local re-derivations the OKF entity governs away. |
| [Vendor](../05-okf-bundle/bundle/entities/vendor.md) | `z_VendorMaster` dataflow + ungoverned SharePoint vendor Excel driving Oversea-Vendor classification (Inv Management, AFT_SI-SS_PSW) | **Direct** | |
| [Transaction Date](../05-okf-bundle/bundle/entities/transaction_date.md) + [DimDate](../05-okf-bundle/bundle/datasets/tables/DimDate.md) | `z_FiscalCal` dataflow; three different date anchors inside Inv Management alone (PAT-07); 4-4-5 fiscal handling implicit and unvalidated (Demand Review YTD-1 double offset) | **Direct** | PAT-07 is the migration case for one conformed calendar. |

## Glossary & processes

| OKF concept | AS-IS counterpart | Confidence | Notes |
|---|---|---|---|
| [Demand Consensus](../05-okf-bundle/bundle/glossary/demand_consensus.md) + [Demand Consensus Meeting](../05-okf-bundle/bundle/processes/demand_consensus_meeting.md) | The monthly demand-review cycle instrumented by [Demand Review](../01-evidence/track-a-reports/Demand_Review_Analysis.md) (DEC-008/009); `Cycle_Dates` SharePoint list ↔ OKF's planned `DimFcstConsensusCycleDates` | **Direct** | Same SharePoint-list object seen from both sides — AS-IS documents its fragility (PAT-04), OKF documents its intended governance. |
| [Firm Demand](../05-okf-bundle/bundle/glossary/firm_demand.md) / [Net Forecast](../05-okf-bundle/bundle/glossary/net_forecast.md) / [Resultant Forecast](../05-okf-bundle/bundle/glossary/resultant_forecast.md) | FD/NF components in [Demand Fulfillment](../01-evidence/track-a-reports/Demand_Fulfillment_Analysis.md) & JadeTeam model; "resultant forecast" language in [GF Act+Fcst](../01-evidence/track-a-reports/GF_Act_Fcst_Analysis.md) | **Direct** | |
| [Promo Lift](../05-okf-bundle/bundle/glossary/promo_lift.md) | `fcst_qty_add_promo` additive promo (months 5–11 hardcode) in Demand Review | **Probable** | Month-window hardcode is the AS-IS deviation to reconcile. |
| [Stockout](../05-okf-bundle/bundle/glossary/stockout.md) / [Recently Introduced](../05-okf-bundle/bundle/glossary/recently_introduced.md) | SI-negative at-risk logic (Demand Fulfillment); "Recent Launch" hardcoded quarters (Safety Stock Analysis) | **Probable** | Safety Stock's frozen quarter list vs OKF's definitional approach. |
| [Lifecycle Planning](../05-okf-bundle/bundle/processes/lifecycle_planning.md) | [When to Disco v2](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md), [Plan Drop] cluster, `z_drop_dates` (Demand Review), [Planner Assignment](../01-evidence/track-a-reports/Planner_Assignment_Analysis.md) | **Probable** | |

## Datasets (see source-migration-map.md for the full table-level view)

| OKF dataset (SupplyChain_Gold) | AS-IS sources in use today | Confidence |
|---|---|---|
| [FactSupplyPlanDetail](../05-okf-bundle/bundle/datasets/tables/FactSupplyPlanDetail.md) | `SupplyChain_Enh.DemandForecastSnapshot` (SPD) across Demand Review, AFT_SI-SS_PSW, Inv Management | **Direct** |
| [FactWorkingForecast](../05-okf-bundle/bundle/datasets/tables/FactWorkingForecast.md) / [FactCurrentForecast](../05-okf-bundle/bundle/datasets/tables/FactCurrentForecast.md) | `Fcst_Snapshots` (Demand Review); `Wholesale_DemandPlanning_AFI.DemandForecast` (Weekly Trend — older schema, PAT-07) | **Direct** |
| [sales_orders](../05-okf-bundle/bundle/datasets/tables/sales_orders.md) | `SupplyChain_Enh.ActualsCustItemWH_AFI` (`OrdHist`) | **Probable** — OKF itself notes its sales_orders draft is superseded by the BRD on the actual-demand basis |

## Known contradictions (raise with Robert)

1. **Actual-demand basis:** OKF forecast_accuracy (BRD-aligned) = ordered qty by
   request date minus load lead time; AS-IS models vary, and OKF's own
   sales_orders draft still says shipped qty. One basis must win.
2. **Overstock threshold:** OKF `[FILL IN]` vs two competing AS-IS rules
   (`SS × 1.4` and the Inv Management waterfall).
3. **DF-rate formula:** two AS-IS formulas under one name (BUG-018); OKF's
   Projected Fulfillment Rate should arbitrate.
4. **Bias neutral threshold:** OKF `[FILL IN]` vs AS-IS 0.08/0.10 split (PAT-03).
