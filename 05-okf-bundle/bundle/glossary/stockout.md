---
type: Glossary Term
title: Stockout
description: A condition in which available inventory is insufficient to satisfy demand, either currently or within the replenishment lead time window.
tags: [inventory, stockout, risk, fulfillment, glossary]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Definition

A **stockout** is the condition where available inventory cannot satisfy current or near-term demand.

There are two types of stockout conditions:

## Current Stockout

`qty_available = 0` for an active, demand-bearing item.

The item has no available inventory and cannot fill open orders without a receipt from a supplier.

## Projected Stockout

`coverage_days < lead_time_days` — the item will exhaust its inventory before the next replenishment can arrive, even if inventory is currently positive.

Projected stockout is the more actionable signal because it identifies risk before it becomes a live outage, allowing time for intervention.

## What Counts as "Available"

Always use `qty_available` from [inventory_onhand](/datasets/tables/inventory_onhand.md), **not** `qty_on_hand`. Allocated inventory is committed to open orders and cannot be redirected to fill new demand.

## Severity Levels

| Condition | Severity | Recommended Action |
| --- | --- | --- |
| `days_of_supply ≥ lead_time_days` | None | No action needed |
| `coverage_days < lead_time_days` and open PO arriving in time | Warning | Monitor PO closely; confirm receipt date with supplier |
| `coverage_days < lead_time_days` and no open PO or PO arriving late | Critical | Expedite or place emergency PO; escalate to buyer |
| `qty_available = 0` | Current Stockout | Immediate escalation; communicate to affected customers |

> **Note**: Specific day thresholds for each severity level are not yet defined. See [FILL IN: phase 2 threshold documentation]. Follow [stockout_escalation](/playbooks/stockout_escalation.md) for the current decision process.

## Related

- [Coverage Days](/metrics/coverage_days.md)
- [Days of Supply](/metrics/days_of_supply.md)
- [Inventory On Hand](/datasets/tables/inventory_onhand.md)
- [Stockout Escalation](/playbooks/stockout_escalation.md)
