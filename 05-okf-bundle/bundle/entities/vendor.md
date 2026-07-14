---
type: Entity
title: Vendor
description: A supplier or vendor from whom the company sources products, characterized by lead time, country of origin, active status, and office designation used across procurement and supply planning.
tags: [vendor, supplier, procurement, supply-planning, master-data]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimVendor]"
status: agent draft
---

## Definition

A **Vendor** is a supplier from whom the company sources products. Vendors are the procurement nodes in the supply chain and appear as a reporting dimension across purchase orders, receipts, on-time delivery, and production planning. The [Vendor Master](/datasets/tables/DimVendor.md) dataset is the single source of truth for all vendor attributes.

Vendor identity is keyed on `VendorNumber`, which serves as the foreign key across all gold fact tables in the supply chain warehouse (`FactPSW`, `FactReceipts`, `FactOnTime`, `FactProduction`).

---

## Active Status

The `VendorActive` flag distinguishes vendors still in active use from those that have been deactivated. Both active and inactive vendors are retained in `DimVendor` to preserve historical fact joins.

| `VendorActive` | Meaning |
| --- | --- |
| `Y` | Vendor is active; eligible for new purchase orders and planning |
| `N` | Vendor is inactive; historical records only — exclude from forward-looking analyses |

When filtering for current procurement or supply planning analyses, always apply `VendorActive = 'Y'` unless the intent is to include historical sourcing data.

---

## Lead Time

`LeadTime` is the standard order lead time in days from purchase order placement to expected receipt. It is sourced from the vendor master and used in supply planning calculations to determine when to place replenishment orders.

Lead time is a vendor-level attribute. If item-level lead time variation is needed, verify whether that granularity is captured in the product or procurement source systems — it is not stored in `DimVendor`.

---

## Country of Origin

`Country` identifies the country of the vendor's primary location or origin, used primarily for import vs. domestic segmentation in sourcing and compliance reporting. This is the vendor's country, not the product's country of origin — the two may differ when a vendor sources from multiple countries.

---

## Vendor Office

Vendors may have multiple offices (`VendorOffice`, `VendorOfficeLocation`). Office-level grouping supports sourcing and supply planning reports that need visibility below the vendor level but above the transaction level.

---

## Related

- [Vendor Master](/datasets/tables/DimVendor.md) — Source dataset for all vendor attributes and active status
