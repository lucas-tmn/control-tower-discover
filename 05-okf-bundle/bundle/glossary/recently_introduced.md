---
type: Glossary Term
title: Recently Introduced
description: The business definition of a recently introduced product — the time window after intro_date during which a product is treated as new for planning and analysis purposes.
tags: [new-product, product-lifecycle, glossary, planning]
timestamp: 2026-06-26T00:00:00Z
status: agent draft
---

## Definition

A product is considered **recently introduced** if its `InitialInvoiceDate` from [Product Master](/datasets/tables/DimProduct.md) falls within the following window:

> **[FILL IN: e.g., "within the last 12 months" or "within the first N weeks/months after intro_date"]**

This classification gates which items are included in new product performance reviews and applies appropriate planning adjustments.

## Why This Definition Matters

The boundary between "new" and "established" is a business decision, not a universal supply chain standard. A consistent definition ensures:

- Agents apply the same filter across all analyses involving new products.
- Performance expectations are calibrated appropriately — a 60% forecast accuracy for a new product is evaluated differently than the same accuracy for an established item.
- Planning parameters (safety stock, review frequency) are applied to the right items at the right time.

## Data Source

| Field | Dataset | Notes |
| --- | --- | --- |
| `InitialInvoiceDate` | [Product Master](/datasets/tables/DimProduct.md) | Date of first customer invoice; drives Recent Launch lifecycle stage classification |
| `LifecycleStage` | [Product Master](/datasets/tables/DimProduct.md) | Exclude items where `LifecycleStage = 'End of Life'` from scope |

## Action Required

> This definition requires confirmation from the planning or product management team. Update the time window above and change `status` to `active` once agreed.

## Related

- [Product](/entities/product.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [New Product Performance Review](/playbooks/new_product_review.md)
