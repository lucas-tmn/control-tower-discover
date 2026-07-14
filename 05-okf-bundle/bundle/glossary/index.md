---
type: Index
title: Glossary
description: Organization-specific term definitions.
timestamp: 2026-07-07
---

## Glossary

### Glossary Term

- [Customer Group](customer_group.md) - A Logility demand planning grouping of customer accounts used to organize and review the working forecast at a segment level; distinct from individual customer records in DimCustomer.
- [Demand Consensus](demand_consensus.md) - The demand planning process by which the working forecast is finalized and synchronized from Logility's DemandPlanning database to the SupplyPlanning database, making it the official demand signal consumed by supply planning.
- [Firm Demand](firm_demand.md) - Confirmed open customer order quantity for a given item-warehouse-week; committed demand placed in the ERP system, as distinct from statistical forecast.
- [Net Forecast](net_forecast.md) - The portion of the statistical demand forecast not yet covered by firm customer orders for a given planning week; floored at zero to prevent negative demand in the supply plan.
- [Overstock](overstock.md) - A condition in which inventory on hand plus open inbound supply exceeds projected demand over the planning horizon, resulting in excess inventory exposure.
- [Promo Lift](promo_lift.md) - Incremental demand quantity from planned promotions, entered in Logility separately from the statistical forecast and overlaid as a distinct demand component.
- [Recently Introduced](recently_introduced.md) - The business definition of a recently introduced product — the time window after intro_date during which a product is treated as new for planning and analysis purposes.
- [Resultant Forecast](resultant_forecast.md) - The final Logility forecast quantity for a planning period after all planner overrides and adjustments have been applied on top of the statistical model output.
- [Stockout](stockout.md) - A condition in which available inventory is insufficient to satisfy demand, either currently or within the replenishment lead time window.
