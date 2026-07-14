# Demand Planning & Forecast Consensus

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis and governed OKF definitions, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | [Demand_Review_Analysis.md](../01-evidence/track-a-reports/Demand_Review_Analysis.md), [Forecast_Accuracy_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_Analysis.md), [Forecast_Accuracy_ItWh_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_ItWh_Analysis.md), [Forecast_Accuracy_CustItWh_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_CustItWh_Analysis.md), [Weekly_Trend_Analysis.md](../01-evidence/track-a-reports/Weekly_Trend_Analysis.md); OKF [`glossary/demand_consensus.md`](../05-okf-bundle/bundle/glossary/demand_consensus.md), [`glossary/firm_demand.md`](../05-okf-bundle/bundle/glossary/firm_demand.md), [`glossary/net_forecast.md`](../05-okf-bundle/bundle/glossary/net_forecast.md), [`metrics/forecast_accuracy.md`](../05-okf-bundle/bundle/metrics/forecast_accuracy.md); Decision Registry [DEC-001](../02-decision-registry/decisions/DEC-001.md), [DEC-002](../02-decision-registry/decisions/DEC-002.md), [DEC-008](../02-decision-registry/decisions/DEC-008.md), [DEC-009](../02-decision-registry/decisions/DEC-009.md), [DEC-010](../02-decision-registry/decisions/DEC-010.md), [DEC-011](../02-decision-registry/decisions/DEC-011.md) |

---

## 1. What this is, and why it exists

Ashley plans demand in Logility. Planners maintain a **working forecast** —
an in-progress, still-editable view of expected demand broken out by item,
warehouse, and customer group. Periodically, that working forecast goes through
**Demand Consensus**: the demand team reviews it, adjusts it, and approves it,
at which point it is pushed from Logility's planning database into the
supply-planning database and becomes the **current forecast** — the number
supply planning actually builds against
([OKF: Demand Consensus](../05-okf-bundle/bundle/glossary/demand_consensus.md)).

The reason this distinction matters: the working forecast is not yet a
commitment, and its customer-level detail is lost once it becomes the current
forecast (which only retains item-warehouse-week, not the customer group
breakdown). Any question about "what did we plan for this specific customer"
has to be answered from the working forecast, not the current one.

Three components make up total planned demand for a given item-warehouse-week
([OKF: Firm Demand](../05-okf-bundle/bundle/glossary/firm_demand.md), [OKF: Net Forecast](../05-okf-bundle/bundle/glossary/net_forecast.md)):

- **Firm Demand** — confirmed open customer orders. Takes priority over
  forecast, since it's already committed.
- **Net Forecast** — the part of the statistical forecast not yet covered by
  firm orders, floored at zero so nothing is double-counted.
- **Promo Lift** — a manually-entered marketing input layered on top.

In near-term weeks, Firm Demand dominates and Net Forecast is small; in outer
weeks beyond the order horizon, the reverse is true. This is the reason forecast
review conversations look different depending on how far out you're looking.

## 2. How this runs today

The **Demand Review** report is the instrument for this process
([Demand_Review_Analysis.md](../01-evidence/track-a-reports/Demand_Review_Analysis.md)
§2). What we can confirm from the model itself:

- A **monthly cycle**, anchored by a SharePoint list (`Cycle_Dates`) that every
  snapshot-relative measure in the model depends on.
- The report compares the **working plan** against the **prior plan** and a
  **90-day plan**, and computes an `Exception Flag` when the change between
  plans crosses a threshold.
- A separate `Chronic Bias Flag` fires when 90-day bias exceeds 25%, 30-day
  bias exceeds 20%, and consumption-gap rate exceeds 15%, all at once — this is
  the first mechanism in the estate that produces an automated judgment about
  forecast quality, not just a data point ([DEC-009](../02-decision-registry/decisions/DEC-009.md)).
- **In-month consumption pace** is tracked against a historical same-day-of-month
  target, and a $-value "revenue at risk" figure (`consumption_gap_FOB$_cur`)
  is calculated from the gap ([DEC-010](../02-decision-registry/decisions/DEC-010.md)).
- The **RH (Rustic Home/Bedding) channel** forecast is swapped in from a
  separately submitted Excel file, replacing the Logility-generated component
  for that customer group ([DEC-011](../02-decision-registry/decisions/DEC-011.md)).

Forecast accuracy itself is measured by **three sibling models** — the original
SCP Forecast Accuracy model plus ItWh and CustItWh variants
([Forecast_Accuracy_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_Analysis.md),
[Forecast_Accuracy_ItWh_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_ItWh_Analysis.md),
[Forecast_Accuracy_CustItWh_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_CustItWh_Analysis.md)) —
using legacy lag labels (2-week / 30-day / 90-day) that the governed OKF
framework maps onto a cleaner Lag-0 through Lag-4 scale
([OKF: Forecast Accuracy](../05-okf-bundle/bundle/metrics/forecast_accuracy.md)).

**Not yet confirmed — Track B questions:** who specifically sits in the
consensus review, whether it's a single meeting or several, whether the
`Exception Flag` items are reviewed individually or as an aggregate, and
whether the `Chronic Bias Flag` actually leads to a conversation with the
planner it names. The OKF bundle's own process documentation
([`processes/demand_consensus_meeting.md`](../05-okf-bundle/bundle/processes/demand_consensus_meeting.md))
is entirely unfilled placeholders on exactly these points — this is not a gap
unique to our discovery, it's unconfirmed on both sides.

## 3. Known issues, in business terms

- **Two forecast-accuracy reports that look identical use different pass/fail
  bars.** One uses an 8% bias tolerance, the sibling model uses 10% — the same
  item's forecast could be called "acceptable" in one report and "biased" in
  the other, with no visible reason why ([Forecast_Accuracy_ItWh_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_ItWh_Analysis.md) §9,
  [Forecast_Accuracy_CustItWh_Analysis.md](../01-evidence/track-a-reports/Forecast_Accuracy_CustItWh_Analysis.md) §9).
- **A date typo meant a February cycle correction never took effect.** A
  one-time fix intended for the February 2026 cycle was written with the wrong
  year in the underlying code, so the correction silently never applied
  ([BUG-001](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md), ✅ verified against the raw model file).
- **The RH Bedding forecast has already failed once before.** A separate
  hardcoded patch exists specifically to correct a prior RH/Bedding forecast
  problem for one cycle ([BUG-007](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md)),
  and the channel's actuals data is frozen at the end of 2024 — any real
  drop-ship activity from 2025 onward doesn't appear in this report at all
  ([BUG-006](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md)).
- **The Chronic Bias Flag makes a judgment about a planner's work with
  undocumented thresholds.** The 25%/20%/15% combination has no recorded
  rationale or owner, and it's the only mechanism in the estate that produces
  an automated statement about a person's performance rather than about a
  number ([DEC-009](../02-decision-registry/decisions/DEC-009.md)).
- **One sibling report's accuracy numbers are simply broken.** Weekly Trend
  Analysis's accuracy measures reference a column that doesn't exist in the
  underlying table and always return blank or −1
  ([BUG-003](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md), ✅ verified against the raw model file).
- **The "$ at risk" figure has no audited basis.** `consumption_gap_FOB$_cur`
  converts a pace assumption into a dollar figure with no seasonality
  adjustment and no confidence range, and it likely appears in monthly business
  review decks as if it were a precise number ([DEC-010](../02-decision-registry/decisions/DEC-010.md)).

## 4. Where this is headed (target state)

The OKF bundle's governed forecast-accuracy definition
([`metrics/forecast_accuracy.md`](../05-okf-bundle/bundle/metrics/forecast_accuracy.md))
replaces the current three-model, two-threshold situation with one measurement
family (MAPE, wMAPE, wMPE/bias, RMSE, Process Value Add) evaluated consistently
across Lag-0 through Lag-4, anchored to the official consensus snapshot rather
than ad hoc per-model logic.

On the engineering side, the Fabric build has concrete progress specifically on
this domain: `FactWorkingForecast` and `FactCurrentForecast` are **built**, with
real ETL SQL defining the Resultant/Promo Lift/Total forecast structure
([`07-fabric-build/docs/model-definitions/scp-core-model/`](../07-fabric-build/docs/model-definitions/scp-core-model/)) —
though `FactCurrentForecast`'s own documentation notes it is still "in
anticipation of transition in Q3," i.e. not finished. The `Cycle_Dates`
SharePoint list that anchors every snapshot-relative measure today has a
planned governed replacement (`DimFcstConsensusCycleDates`) but **that
replacement is not yet built** on either side of this repo
([`06-bridge/source-migration-map.md`](../06-bridge/source-migration-map.md)).

## 5. Open questions for Track B

1. Walk me through the last consensus cycle — which report was open when a
   number actually changed, and who was in the room?
2. When the Chronic Bias Flag fires on an item, does that lead to an actual
   conversation with the planner, or is it a number nobody follows up on?
3. Has the RH Bedding Excel process ever visibly failed in a way you noticed —
   and if so, how did you find out?
4. Does the "$ at risk" consumption-gap number ever directly change a decision
   (chasing orders, cutting the forecast), or is it read as context only?
5. *(added from external research, see [`00-foundation/Lessons_From_The_Market.md`](../00-foundation/Lessons_From_The_Market.md) §2)*
   — when this report flags an exception, do you actually stop and look at it,
   or has it become something you've learned to scroll past?
