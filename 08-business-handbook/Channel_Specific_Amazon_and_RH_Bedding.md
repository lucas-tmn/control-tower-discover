# Channel-Specific: Amazon & RH Bedding

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis and governed OKF definitions, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | [Amazon_POS_Sales_and_Forecast_Analysis.md](../01-evidence/track-a-reports/Amazon_POS_Sales_and_Forecast_Analysis.md), [Consumption_Report_Analysis.md](../01-evidence/track-a-reports/Consumption_Report_Analysis.md), [Demand_Sensing_Report_Analysis.md](../01-evidence/track-a-reports/Demand_Sensing_Report_Analysis.md); Decision Registry [DEC-007](../02-decision-registry/decisions/DEC-007.md), [DEC-011](../02-decision-registry/decisions/DEC-011.md) |

---

## 1. What this is, and why it exists

Most of this handbook covers Ashley's core wholesale demand/supply process.
Two channels sit apart from that process enough to need their own reasoning:
**Amazon**, where Ashley sells through a marketplace it doesn't control, and
**RH (Rustic Home/Bedding)**, where the forecast itself is generated outside
the normal Logility process. Both channels also connect to two
general-purpose demand-signal reports — Consumption Report and Demand
Sensing — that aren't channel-specific themselves but are especially relevant
here because of how thin the governed tooling is for these two channels
specifically.

## 2. How this runs today

**Amazon.** The Amazon POS Sales and Forecast report consolidates Amazon's
actual point-of-sale sell-through, Amazon's own on-hand inventory, open
purchase orders, and Amazon's own demand forecast — then compares all of that
against Ashley's wholesale sell-in to Amazon
([Amazon_POS_Sales_and_Forecast_Analysis.md](../01-evidence/track-a-reports/Amazon_POS_Sales_and_Forecast_Analysis.md) §1).
The underlying decision this supports is whether Ashley is sizing its
wholesale shipments to Amazon correctly, given what's actually selling versus
what Amazon itself projects it will need
([DEC-007](../02-decision-registry/decisions/DEC-007.md)).

**RH Bedding.** As covered in the
[Demand Planning chapter](Demand_Planning_and_Forecast_Consensus.md), this
channel's forecast is not generated through the normal Logility process — it's
submitted via a separately maintained Excel file and swapped into the Demand
Review working plan in place of the Logility-generated component for that
customer group ([DEC-011](../02-decision-registry/decisions/DEC-011.md)).

**Two general demand-signal reports relevant to both channels.** The
Consumption Report answers a mid-month pacing question — given how orders
historically accumulate through the month, are we on track to hit the
forecast, and what's the projected gap
([Consumption_Report_Analysis.md](../01-evidence/track-a-reports/Consumption_Report_Analysis.md) §1)?
Demand Sensing takes a different, statistical-control-chart approach: is the
current week's written order rate for an item-warehouse-customer group
abnormally high or low compared to its historical trend, flagged as a shift up,
shift down, or normal
([Demand_Sensing_Report_Analysis.md](../01-evidence/track-a-reports/Demand_Sensing_Report_Analysis.md) §1).
Neither report is Amazon- or RH-specific by design, but both channels — being
thinner on governed tooling than core wholesale — are where a pacing or
anomaly signal is least likely to be caught any other way.

**Not yet confirmed — Track B questions:** whether the Amazon and RH
processes are owned by the same team or different teams, and whether
Consumption Report / Demand Sensing are actually used to monitor these two
channels specifically, or whether that's only an inference from what the
reports are capable of.

## 3. Known issues, in business terms

- **The Amazon report can tell you *what* happened but not automatically
  whether it's a problem.** There is no built-in weeks-of-supply calculation
  and no built-in forecast-gap calculation — a user has to manually combine
  on-hand inventory, open POs, and POS sell-through every time to get the
  signal that matters, and manually compare Amazon's forecast against POS to
  judge accuracy
  ([DEC-007](../02-decision-registry/decisions/DEC-007.md), field D5). This
  isn't a bug — the underlying numbers are believed correct — but it's a
  structural gap between "the data is here" and "the answer is here."
- **The Amazon report never checks against Ashley's own internal forecast.**
  It compares Amazon's POS against Amazon's own forecast and against Ashley's
  wholesale shipments — but whether Ashley's internal demand planners are
  forecasting the Amazon channel accurately is a different question this
  report cannot answer on its own
  ([DEC-007](../02-decision-registry/decisions/DEC-007.md), field D5).
- **The RH forecast pipeline has already failed at least once**, and its
  actuals are frozen at the end of 2024 — see the
  [Demand Planning chapter](Demand_Planning_and_Forecast_Consensus.md) for
  detail; it's not repeated here to avoid the estate's own habit of
  duplicating the same fact across models.

## 4. Where this is headed (target state)

No gold fact table specific to either channel exists yet in the Fabric build —
this domain currently has the thinnest engineering foundation of any chapter
in this handbook. The structural gap in the Amazon report (no weeks-of-supply
or forecast-gap measure) is exactly the kind of thing an Eagle Eye layer could
add real, visible value by automating — see
[DEC-007](../02-decision-registry/decisions/DEC-007.md)'s Eagle Eye assessment,
which already flags this as a strong candidate for that reason.

## 5. Open questions for Track B

1. How do you currently figure out weeks-of-supply at Amazon — do you
   calculate it yourself outside this report, or is there another tool?
2. Do you ever compare Amazon's forecast against Ashley's own internal
   forecast for the same items, and if so, where does that comparison happen?
3. Do you use Consumption Report or Demand Sensing specifically to watch the
   Amazon or RH channels, or are those reports part of a different routine
   entirely?
4. If Amazon's POS data was delayed or wrong for a week, how would you find
   out?
