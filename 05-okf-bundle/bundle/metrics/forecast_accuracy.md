---
type: Metric
title: Forecast Accuracy
description: Governed customer-level forecast accuracy metric family using the Working Forecast captured at Demand Consensus, including MAPE, wMAPE, wMPE forecast bias, RMSE, and Process Value Add.
tags: [forecast, demand-planning, demand-consensus, logility, accuracy, bias, pva, kpi]
timestamp: 2026-07-07
status: draft
---

## Definition

Forecast Accuracy is the governed framework for measuring how well the approved Demand Consensus forecast predicted actual demand. The core KPI is tracked at the customer level using the [Working Forecast](/datasets/tables/FactWorkingForecast.md) as it existed at the time of Demand Consensus, when that forecast is pushed to SupplyPlanning and is in sync with the supply-facing current forecast at the shared item-warehouse total.

Forecast accuracy is evaluated against official consensus snapshot dates, across lag periods from **Lag-0 through Lag-4**, so Demand Planning can measure forecast improvement as the actual demand period gets closer.

This metric family replaces ad hoc or legacy snapshot-selection logic with consensus-cycle alignment. The primary governed outputs are:

- MAPE - Mean Absolute Percentage Error
- wMAPE - Weighted Mean Absolute Percentage Error
- wMPE - Weighted Mean Percent Error / Forecast Bias
- RMSE - Root Mean Squared Error
- PVA - Process Value Add

Use this page as the semantic-model definition for forecast accuracy calculations. The BRD is authoritative over earlier agent-draft guidance on this metric.

## Business Purpose

Forecast accuracy reporting is used to:

- Provide one governed source of truth for forecast accuracy metrics.
- Measure Demand Planning performance across consistent lag periods.
- Identify whether forecast accuracy improves as consensus cycles approach the actuals period.
- Support structured root cause analysis for forecast misses.
- Measure whether the demand planning process adds value beyond a simple naive forecast.

## KPI Source and Grain

The core KPI is measured from the Working Forecast captured at the consensus snapshot. That source preserves the customer-level planning dimension needed for forecast accuracy. The supply-facing [Current Forecast](/datasets/tables/FactCurrentForecast.md) remains useful for item-warehouse reconciliation after consensus, but it does not retain the customer-level forecast breakdown.

The target forecast accuracy fact is measured at:

```text
CustomerGroup x ItemSKU x WarehouseID x FiscalPeriod x ForecastSnapshotDate x LagIndicator
```

The BRD names the forecast accuracy fact as `FcstAccuracy_CustItemWh` and defines the business grain as **Customer-Item-Warehouse-Fiscal Period**. In the current Working Forecast contract, the customer-level planning dimension is `CustomerGroup`. If the final KPI tables carry a lower-level customer key in addition to `CustomerGroup`, document that field in the table docs and update this grain.

Current-state time period is **Fiscal Month**. A future transition to weekly evaluation is still TBD.

Required rollups include:

- Customer / Item / Warehouse
- Item / Warehouse
- Customer Group
- Item
- Warehouse
- Brand
- Total Business

Reporting views may aggregate across 1-week, 4-week, and 12-week windows, but the governed source period remains the fiscal period tied to the selected lag snapshot.

## Consensus Snapshot Alignment

Forecast accuracy must align to official Demand Consensus snapshot dates, not simply the latest available forecast snapshot.

At the consensus moment, the finalized Working Forecast is pushed from Logility DemandPlanning to SupplyPlanning. The customer-level KPI should use the Working Forecast snapshot from that consensus moment. The Current Forecast can be used to reconcile the synchronized item-warehouse totals after the push, but it should not be treated as the primary customer-level KPI source because the customer dimension is collapsed in the supply-facing table.

The BRD defines two supporting structures:

| Structure | Purpose |
| --- | --- |
| `DimFcstConsensusCycleDates` | SharePoint-maintained list of locked forecast dates for each consensus period. |
| `FcstAccuracySnapshotDates` | Derived mapping from consensus cycle dates to Lag-0 through Lag-4 snapshot dates and actuals month-end dates. |

The forecast accuracy fact should join to the Working Forecast history by `ForecastSnapshotDate` and should retain the forecast cycle and lag labels used for reporting.

### Lag Labels

| Legacy period label | Governed lag label |
| --- | --- |
| `2Week` | `Lag-0` |
| `30 Day` | `Lag-1` |
| `60 Day` | `Lag-2` |
| `90 Day` | `Lag-3` |
| `120 Day` | `Lag-4` |

## Core Inputs

| Input | Definition |
| --- | --- |
| `ActualDemand` | Ordered quantity by current request date minus load lead time for the defined fiscal period. This supersedes the prior draft instruction to use shipped quantity for forecast accuracy. |
| `ForecastQty` | Working Forecast quantity captured at Demand Consensus for the applicable `ForecastSnapshotDate` and `LagIndicator` at the same customer-item-warehouse-period grain. |
| `NaiveForecastQty` | Forecast baseline derived from prior-period actual demand, adjusted for 4-4-5 fiscal calendar alignment. |
| `ForecastSnapshotDate` | Date of the consensus forecast snapshot used for the lag calculation. |
| `ActualsMonthEndDate` | Fiscal month-end date for the actual demand period being evaluated. |
| `ForecastCycleIdentifier` | Forecast cycle label, such as `FY26-M03`, used to tie the snapshot date to the Demand Consensus cycle. |
| `LagIndicator` | Relative lag bucket from `Lag-0` through `Lag-4`. |

### Naive Forecast

The naive forecast assumes the prior fiscal period's actual demand is the best available predictor for the current period. Because AFI uses a 4-4-5 fiscal calendar, the prior period must be normalized by fiscal weeks before being applied to the current period.

```text
PriorPeriodAverageWeeklyDemand = PriorPeriodActualDemand / PriorPeriodFiscalWeekCount
NaiveForecastQty = PriorPeriodAverageWeeklyDemand * CurrentPeriodFiscalWeekCount
```

## Row-Level Calculations

Calculate these fields at the target forecast accuracy fact grain before reporting-level aggregation.

| Field | Calculation |
| --- | --- |
| `ForecastError` | `ForecastQty - ActualDemand` |
| `AbsoluteForecastError` | `ABS(ForecastQty - ActualDemand)` |
| `NaiveForecastError` | `NaiveForecastQty - ActualDemand` |
| `AbsoluteNaiveForecastError` | `ABS(NaiveForecastQty - ActualDemand)` |
| `SquaredForecastError` | `(ForecastQty - ActualDemand)^2` |

The BRD Section 6.2 text says signed forecast error is `Actual Demand - Forecast Quantity`, but the BRD change log and metric sections define the governed direction as `Forecast - Actual`. Use `ForecastQty - ActualDemand` so positive values indicate over-forecasting and negative values indicate under-forecasting.

## Semantic Model Metrics

### MAPE - Mean Absolute Percentage Error

Average absolute percentage error across valid observations.

```text
MAPE = SUM(ABS(ForecastQty - ActualDemand) / ActualDemand) / CountValidObservations * 100
```

Use only valid observations. Exclude records where `ActualDemand = 0` unless the business defines a separate zero-actual handling rule.

### wMAPE - Weighted Mean Absolute Percentage Error

Absolute forecast error weighted by actual demand volume. This should be the primary scale-insensitive error metric for aggregate reporting.

```text
wMAPE = SUM(ABS(ForecastQty - ActualDemand)) / SUM(ActualDemand) * 100
```

Lower values are better.

### wMPE - Weighted Mean Percent Error / Forecast Bias

Signed forecast error weighted by actual demand volume. This measures directional bias.

```text
wMPE = SUM(ForecastQty - ActualDemand) / SUM(ActualDemand) * 100
```

Interpretation:

| wMPE value | Meaning |
| --- | --- |
| Positive | Over-forecast |
| Negative | Under-forecast |
| Near zero | Directionally neutral, subject to the neutral threshold defined by the business |

### RMSE - Root Mean Squared Error

Measures the standard deviation of forecast errors and penalizes large misses more heavily.

```text
RMSE = SQRT(SUM((ForecastQty - ActualDemand)^2) / CountValidObservations)
```

Calculate squared error at the row grain, aggregate squared error to the reporting level, then apply the square root.

### PVA - Process Value Add

Measures whether the Demand Planning process outperformed the naive baseline forecast.

```text
PVA = wMAPE_Naive - wMAPE_Forecast
```

Where:

```text
wMAPE_Forecast = SUM(ABS(ForecastQty - ActualDemand)) / SUM(ActualDemand) * 100
wMAPE_Naive = SUM(ABS(NaiveForecastQty - ActualDemand)) / SUM(ActualDemand) * 100
```

Interpretation:

| PVA value | Meaning |
| --- | --- |
| Positive | Consensus forecast outperformed the naive forecast; the process added value. |
| Negative | Consensus forecast performed worse than the naive forecast; the process did not add value. |
| Zero | Consensus and naive forecasts performed the same. |

## Optional Accuracy Score

The governed BRD metrics are error and bias metrics. If a dashboard needs a higher-is-better accuracy score or accuracy band, derive it explicitly from the selected error metric:

```text
ForecastAccuracyPct = 100 - wMAPE
```

Do not mix raw MAPE, wMAPE, and derived accuracy percentage in the same visual without labeling the measure clearly.

## Classification Fields

The BRD calls for the following reporting classifications:

| Field | Definition |
| --- | --- |
| `AccuracyBand` | Bucketed accuracy classification, such as `<70%`, `70-80%`, `80-90%`, `>90%`, based on the selected accuracy score. |
| `BiasClassification` | Over-Forecast, Under-Forecast, or Neutral based on wMPE. |
| `FiscalPeriodStatus` | Open or Closed status for the actual demand period. |
| `ForecastVersionIdentifier` | Forecast version label, such as Consensus, Statistical, or Final Approved. |
| `DataQualityFlag` | Exception flag for issues such as missing snapshot, zero actual, invalid fiscal period, or missing source relationship. |

Neutral bias thresholds and final accuracy-band boundaries are [FILL IN: business-approved threshold values].

## Planned KPI Tables

The actual KPI tables that contain the relevant consensus snapshots, lag mappings, actual demand, naive forecast, and error calculations will be added to this bundle as dataset docs when their physical contracts are confirmed.

Expected table documentation:

| Planned table | Expected role |
| --- | --- |
| `DimFcstConsensusCycleDates` | Maintained consensus cycle date source that identifies the approved snapshot date for each cycle. |
| `FcstAccuracySnapshotDates` | Lag mapping table that relates each actuals period to the Lag-0 through Lag-4 Working Forecast snapshots. |
| `FcstAccuracy_CustItemWh` | Customer-level KPI fact containing Working Forecast at consensus, actual demand, naive forecast, row-level errors, and fields needed for MAPE, wMAPE, wMPE, RMSE, and PVA. |

Until those table docs are added, this metric page defines the governing business logic and expected calculation contract.

## Embedded Forecast Accuracy Terms

Keep these terms here until they are reused outside forecast accuracy.

| Term | Meaning |
| --- | --- |
| Consensus Forecast Snapshot Date | The approved Working Forecast snapshot date selected from the Demand Consensus cycle date source for accuracy measurement. |
| Forecast Cycle | The fiscal consensus cycle being evaluated, such as a fiscal year/month cycle. |
| Forecast Cycle Identifier | Label tying records to the governed forecast cycle, such as `FY26-M03`. |
| Lag Indicator | Lag bucket showing how far ahead of the actual period the forecast snapshot was taken. |
| Lag-0 | Forecast snapshot closest to the actuals period, replacing the legacy `2Week` label. |
| Lag-1 | Forecast snapshot replacing the legacy `30 Day` label. |
| Lag-2 | Forecast snapshot replacing the legacy `60 Day` label. |
| Lag-3 | Forecast snapshot replacing the legacy `90 Day` label. |
| Lag-4 | Forecast snapshot replacing the legacy `120 Day` label. |
| Actual Demand | Ordered quantity by current request date minus load lead time for the defined fiscal period. |
| Load Lead Time | Lead-time offset applied to current request date when assigning ordered quantity to the actual demand period. |
| Naive Forecast | Prior-period actual demand baseline adjusted for 4-4-5 fiscal calendar differences. |
| Valid Observation | Observation included in metric calculations after excluding invalid rows such as zero actual demand for MAPE. |
| Zero Actual | A record where actual demand is zero; exclude from MAPE and flag for defined handling in weighted metrics. |
| Forecast Bias | Directional forecast error measured by wMPE. |
| Process Value Add | Difference between naive forecast wMAPE and consensus forecast wMAPE. |
| Actuals Month End Date | Fiscal month-end date for the actual demand period. |

## Data Quality and Audit Requirements

Forecast accuracy outputs should retain:

- Snapshot date used for calculation.
- Actuals month-end date.
- Forecast cycle identifier.
- Lag indicator.
- Source system identifier, such as Logility or ERP.
- Record created timestamp.
- Record updated timestamp.
- Data quality flag.

Minimum validation checks:

- Validate that consensus snapshot dates are maintained in the SharePoint source.
- Confirm every lag record has a valid `ForecastSnapshotDate`.
- Flag missing forecast snapshots.
- Flag zero-actual records.
- Confirm fiscal 4-4-5 calendar alignment for actual, forecast, and naive forecast periods.

## Current Bundle Gaps

- The current [Working Forecast](/datasets/tables/FactWorkingForecast.md) documentation describes the latest working forecast only. Customer-level forecast accuracy requires historical Working Forecast snapshots captured at the official consensus dates.
- The actual KPI table docs for consensus cycle dates, lag snapshot mapping, and customer-level forecast accuracy calculations still need to be added to the bundle after their physical contracts are confirmed.
- The current [Sales Orders](/datasets/tables/sales_orders.md) draft says forecast accuracy should use shipped quantity. The BRD supersedes that with ordered quantity by current request date minus load lead time.
- The exact ERP fields for current request date, ordered quantity, and load lead time are [FILL IN: source field mapping].
- The SharePoint-backed `DimFcstConsensusCycleDates` and derived `FcstAccuracySnapshotDates` dataset docs are [FILL IN: create dataset docs when sources are confirmed].
- The BRD uses the spelling `FcstAccurary` in some table names. Confirm final physical names before creating dataset docs.

## Common Failure Modes

- **Wrong snapshot date**: Using the latest forecast instead of the consensus-cycle snapshot causes look-ahead bias.
- **Wrong forecast source**: Using the supply-facing Current Forecast as the customer-level KPI source loses the customer-level planning dimension; use the Working Forecast captured at consensus.
- **Wrong actual demand basis**: Using shipped quantity instead of BRD-defined ordered quantity by request date minus load lead time changes the meaning of accuracy.
- **Missing consensus history**: The latest Working Forecast alone is not enough; lag-based KPI reporting requires retained snapshots for each official consensus cycle.
- **Zero actuals**: MAPE is unstable or undefined when actual demand is zero.
- **4-4-5 mismatch**: Naive forecast and lag comparisons are distorted if fiscal week counts are not aligned correctly.
- **Aggregation order**: Absolute error, squared error, and naive error must be calculated at the fact grain before reporting-level aggregation.

## Related

- [Demand Consensus](/glossary/demand_consensus.md)
- [Customer Group](/glossary/customer_group.md)
- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Working Forecast](/datasets/tables/FactWorkingForecast.md)
- [Current Forecast Snapshot Daily](/datasets/tables/CurFcstSnapshotDaily.md)
- [Sales Orders](/datasets/tables/sales_orders.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Forecast Revision](/playbooks/forecast_revision.md)
