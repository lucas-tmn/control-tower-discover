---
type: Glossary Term
title: Firm Demand
description: Confirmed open customer order quantity for a given item-warehouse-week; committed demand placed in the ERP system, as distinct from statistical forecast.
tags: [supply-plan, demand, orders, glossary, firm-demand]
timestamp: 2026-06-29
status: agent draft
---

## Definition

**Firm Demand** is the total confirmed open customer order quantity for a given item-warehouse-week combination. These are orders that have been placed by customers and are open in the ERP system — committed demand the business is obligated to fulfill.

Firm Demand is distinct from statistical forecast (which is probabilistic) and from [Net Forecast](/glossary/net_forecast.md) (which is the uncovered residual after firm orders are applied).

## Role in the Supply Plan

In Logility, Firm Demand takes priority over forecast when computing planned demand:

1. **Firm Demand** is applied first — it represents known, committed orders.
2. **Net Forecast** covers only the portion of the statistical forecast not yet covered by firm orders.
3. **Promo Lift** is added separately as a manual marketing input.

This sequencing prevents double-counting: the supply plan does not simultaneously plan for both a customer order and the forecast that originally predicted that order.

## Near-Term vs. Outer Weeks

- In **near-term weeks**, most of the week's expected demand already appears as Firm Demand. Net Forecast will be small or zero.
- In **outer weeks** beyond the order horizon, Firm Demand is sparse and the plan relies primarily on Net Forecast.

Agents should expect high Firm Demand / low Net Forecast in the near term, and low Firm Demand / high Net Forecast further out. A week with unexpectedly high Net Forecast in the near term may signal late-ordering customers or an overstated statistical forecast.

## Related

- [Net Forecast](/glossary/net_forecast.md)
- [Supply Plan Detail](/datasets/tables/FactSupplyPlanDetail.md)
- [Sales Orders](/datasets/tables/sales_orders.md)
- [Supply Plan Review](/playbooks/supply_plan_review.md)
