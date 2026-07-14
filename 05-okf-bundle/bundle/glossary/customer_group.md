---
type: Glossary Term
title: Customer Group
description: A Logility demand planning grouping of customer accounts used to organize and review the working forecast at a segment level; distinct from individual customer records in DimCustomer.
tags: [demand-planning, customer, logility, forecast, glossary, customer-group]
timestamp: 2026-06-29
status: draft
---

## Definition

**Customer Group** is a Logility demand planning construct that groups individual customer accounts into segments for collaborative forecast review. Demand planners work at the customer group level when building and adjusting the [Working Forecast](/datasets/tables/FactWorkingForecast.md) — a single customer group row represents the aggregate demand from all accounts within that group for a given item-warehouse-week.

## Current Customer Groups

| Customer Group | Makeup |
| --- | --- |
| AFICONS | Intended for Primaries and general wholesale customers. But is the default assignment when no other rule exists |
| ECOMM | Ecommerce accounts like Wayfair and Amazon |
| HSENT | Enterprise HomeStore accounts |
| HSLIC | Licensee HomeStore accounts |
| INT | International accounts |
| MASSRENT | Mass Merchants like Walmart and Menards, and Rental stores like Aaron's or Rent-A-Center |
| MFRM | Mattress firm account |
| NFM | Nebraska Furniture Mart account |
| RHCUST | Resident Home account |

## Distinction from DimCustomer

Customer Group is not the same as an individual customer record in [Customer Master](/datasets/tables/DimCustomer.md).

| | Customer Group | Customer (DimCustomer) |
| --- | --- | --- |
| **Level** | Planning segment (group of accounts) | Individual account or ship-to |
| **Where used** | [Working Forecast](/datasets/tables/FactWorkingForecast.md) grain | Order and sales transaction grain |
| **Source** | Logility DemandPlanning | [FILL IN: ERP or MDM source for DimCustomer] |
| **Collapsed at consensus** | Yes — not retained in [Current Forecast](/datasets/tables/FactCurrentForecast.md) | No |

## AFICONS

`AFICONS` is a valid Logility customer group. Rows in the source DemandPlanning database where the customer group is NULL are normalized to `AFICONS` by the ETL load. Treat `AFICONS` as a real planning segment, not a data quality flag.

## Where Customer Group Appears

`CustomerGroup` is part of the grain in [Working Forecast](/datasets/tables/FactWorkingForecast.md) only. It is not carried through to [Current Forecast](/datasets/tables/FactCurrentForecast.md) after the [Demand Consensus](/glossary/demand_consensus.md) process collapses the customer group dimension.

## Related

- [Working Forecast](/datasets/tables/FactWorkingForecast.md)
- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Demand Consensus](/glossary/demand_consensus.md)
- [Customer Master](/datasets/tables/DimCustomer.md)
