---
type: Glossary Term
title: Demand Consensus
description: The demand planning process by which the working forecast is finalized and synchronized from Logility's DemandPlanning database to the SupplyPlanning database, making it the official demand signal consumed by supply planning.
tags: [forecast, demand-planning, supply-planning, logility, process, glossary]
timestamp: 2026-06-29
status: agent draft
---

## Definition

**Demand Consensus** is the collaborative demand planning process in which the demand team reviews, adjusts, and approves the in-progress working forecast in Logility. Once consensus is reached, the approved forecast is synchronized from Logility's DemandPlanning database to the SupplyPlanning database, where it becomes the [Current Forecast](/datasets/tables/FactCurrentForecast.md).

## What Changes at Consensus

Two things happen when a forecast moves through Demand Consensus:

- **Database**: The forecast moves from Logility DemandPlanning → SupplyPlanning.
- **CustomerGroup dimension is collapsed**: The [Working Forecast](/datasets/tables/FactWorkingForecast.md) carries demand at the customer group level. The post-consensus [Current Forecast](/datasets/tables/FactCurrentForecast.md) aggregates these into a single item-warehouse-week row; the customer group breakdown is not retained in the supply planning view.

| | Before Consensus | After Consensus |
| --- | --- | --- |
| **Table** | [Working Forecast](/datasets/tables/FactWorkingForecast.md) | [Current Forecast](/datasets/tables/FactCurrentForecast.md) |
| **Logility database** | DemandPlanning | SupplyPlanning |
| **Grain** | Item × Warehouse × CustomerGroup × Week | Item × Warehouse × Week |
| **Status** | In-progress; subject to change | Approved; consumed by supply planning |

## Implications for Analysis

- Demand visible in [Working Forecast](/datasets/tables/FactWorkingForecast.md) is **not yet committed** — planners may still revise quantities before consensus.
- The [Current Forecast](/datasets/tables/FactCurrentForecast.md) is the authoritative signal for supply plan inputs and item-warehouse reconciliation after consensus.
- Customer-level [Forecast Accuracy](/metrics/forecast_accuracy.md) uses the [Working Forecast](/datasets/tables/FactWorkingForecast.md) captured at the time of consensus, because that is when the approved demand signal is pushed to SupplyPlanning and the working and current forecasts are in sync at the shared item-warehouse total.
- The cadence and approval steps of the Demand Consensus process are [FILL IN: cadence and stakeholders for the Demand Consensus review cycle].

## Related

- [Working Forecast](/datasets/tables/FactWorkingForecast.md)
- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Customer Group](/glossary/customer_group.md)
- [Forecast Accuracy](/metrics/forecast_accuracy.md)
