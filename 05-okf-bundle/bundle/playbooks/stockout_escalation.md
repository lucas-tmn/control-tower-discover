---
type: Playbook
title: Stockout Escalation
description: Decision rules for assessing stockout risk severity and determining the appropriate escalation and remediation action.
tags: [inventory, stockout, escalation, procurement, playbook]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Purpose

This playbook defines how to classify stockout risk severity and what action to recommend. It is triggered when [coverage_days](/metrics/coverage_days.md) or [days_of_supply](/metrics/days_of_supply.md) falls below safe thresholds — either in a standalone inventory review or as Step 3 of the [New Product Performance Review](/playbooks/new_product_review.md).

## Severity Classification

Classify stockout risk using the relationship between available supply and the item's `lead_time_days` from [Product Master](/datasets/tables/DimProduct.md) ([FILL IN: confirm lead time column — not currently in DimProduct]):

| Condition | Severity | Description |
| --- | --- | --- |
| `days_of_supply ≥ lead_time_days` | None | Supply pipeline is sufficient; no action needed |
| `coverage_days < lead_time_days` and open PO `expected_receipt_date` is before projected stockout | Warning | On-hand stock will run out, but an inbound receipt is expected to arrive before demand is unmet |
| `coverage_days < lead_time_days` and no open PO, or open PO arriving after projected stockout | Critical | Stockout projected with no current remedy in the supply pipeline |
| `qty_available = 0` | Current Stockout | Item is already out of stock |

## Recommended Actions by Severity

### Warning

- Monitor the open PO `expected_receipt_date` closely each planning cycle.
- Confirm with the supplier that the expected receipt date is still valid — do not assume the system date is current.
- Flag to the buyer or planner in the review summary.

### Critical

- **Expedite options**: Assess whether the open PO can be expedited or whether an emergency PO is feasible within the supplier's minimum lead time.
- **Lead time check**: Confirm actual supplier lead time against `lead_time_days` in [Product Master](/datasets/tables/DimProduct.md) ([FILL IN: confirm lead time column]) — the standard may be stale or the supplier may be experiencing delays.
- **Demand review**: Assess whether any open customer orders can be rescheduled to reduce short-term demand pressure while supply catches up.
- **Escalate to buyer**: Flag immediately with projected stockout date, projected recovery date, and recommended action.

### Current Stockout

- Immediately escalate to buyer and supply chain leadership.
- Identify which customer orders are affected by joining to [sales_orders](/datasets/tables/sales_orders.md) on `item_id` where `open_qty > 0`.
- Communicate expected recovery date based on the next open PO `expected_receipt_date` from [purchase_orders](/datasets/tables/purchase_orders.md).

## Projecting the Recovery Date

The **recovery date** is the `expected_receipt_date` of the next open PO for the item.

If no open PO exists:

- Note that no replenishment is in the pipeline.
- Calculate the earliest possible receipt as: today + `lead_time_days` (the floor, assuming a PO were placed today and the supplier performs at standard lead time).
- Include this earliest-possible recovery date in the escalation alongside the note that no PO has been placed.

## Related

- [Stockout](/glossary/stockout.md)
- [Coverage Days](/metrics/coverage_days.md)
- [Days of Supply](/metrics/days_of_supply.md)
- [Inventory On Hand](/datasets/tables/inventory_onhand.md)
- [Purchase Orders](/datasets/tables/purchase_orders.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [New Product Performance Review](/playbooks/new_product_review.md)
