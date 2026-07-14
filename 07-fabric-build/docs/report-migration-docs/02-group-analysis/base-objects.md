---
title: Base Objects Catalog
source: output/analysis/_inventory/base_objects.csv
distinct_base_objects: 107
multi_model_base_objects: 45
---

## How to read this

Each EDW base object is the underlying table referenced inside a report-table's source query
(the `FROM`/`JOIN` targets, normalized across the 26 models). `role` distinguishes the primary
`FROM` driver from a joined lookup. `snapshot` records how the object is sliced in time:
`latest` (a "most recent snapshot" filter is applied), `history` (multiple snapshots retained —
required for accuracy trending), or `none` (no snapshot concept). Full rows, including
GROUP BY grain, are in [_inventory/base_objects.csv](_inventory/base_objects.csv).

The high-frequency head below is the **consolidation backbone**: a handful of base objects
account for the majority of the 439 usages.

## Consolidation backbone (used by ≥5 models)

| Base object | Models | Uses | Primary | Snapshot | Gold role |
| --- | --- | --- | --- | --- | --- |
| Enterprise_DW.DimDate | 21 | 60 | 3 | latest/history/none | `DimDate` (conformed) |
| PowerBI_SupplyChain.CurrentProductDetails | 14 | 20 | 3 | latest/none | `DimProduct` (dataflow path) |
| Wholesale_DemandPlanning_AFI.SupplyPlanDetail | 13 | 18 | 10 | latest/history/none | `fact_supply_plan` |
| SupplyChain_Enh.DemandForecastSnapshot | 11 | 22 | 15 | latest/history/none | `fact_forecast_snapshot` / `fact_forecast_accuracy` |
| SupplyChain_DW.DimCurrentProductDetails | 10 | 27 | 3 | latest/none | `DimProduct` (SQL path) |
| SupplyChain_Enh.ActualsCustItemWH_AFI | 9 | 11 | 6 | latest/none | `fact_actuals` |
| Enterprise_DW.DimDate_NonRetail | 6 | 15 | 1 | latest/none | `DimDate` (non-retail variant — reconcile) |
| SupplyChain_Enh.DemandInventorySnapshot | 6 | 13 | 4 | latest/none | `fact_inventory_position` |
| MasterData_ItemMaster_AFI.ITMEXT | 6 | 7 | 0 | none | `DimProduct` extension (item master) |
| PowerBI_SupplyChain.CustomerAcctMaster_AFI | 5 | 15 | 4 | none | `DimCustomer` |
| SupplyChain_Enh.PSWWeeklyExtractSnapshot | 5 | 9 | 7 | latest/none | `fact_psw` |
| SupplyChain_Enh.ProductionConversion | 5 | 8 | 1 | latest/none | `DimProductionResource` / `fact_production` |
| AFISales_DW.DimCustomers | 5 | 7 | 0 | none | `DimCustomer` (sales path — reconcile with CustomerAcctMaster) |
| SupplyChain_Enh.ForecastCommonContainer_Logility | 5 | 5 | 3 | latest/none | `fact_psw` / container plan |

## Secondary objects (used by 3–4 models)

| Base object | Models | Uses | Snapshot | Gold role |
| --- | --- | --- | --- | --- |
| Wholesale_SalesHistory_AFI.InvoiceDetail | 4 | 5 | none | `fact_actuals` (invoiced sales path) |
| SupplyChain_Enh.ItemActualDemand_Logility | 4 | 4 | none | `fact_forecast_accuracy` (actual-demand side) |
| PowerBI_SupplyChain.VendorMaster | 4 | 4 | none | `DimVendor` |
| Wholesale_ProductSourcing_AFI.PoDetail | 3 | 6 | latest/none | `fact_receipts` (purchase orders) |
| Enterprise_DW.DimItemMaster | 3 | 5 | latest/none | `DimProduct` extension |
| MasterData_ItemMaster_AFI.ITBEXT | 3 | 4 | latest/none | `DimProduct` extension (balance ext) |
| PowerBI_SupplyChain.FCC_LogilityCurrentDay | 3 | 4 | none | container current-day (vs snapshot history) |
| DW_Developer.TableDictionary | 3 | 4 | none | refresh-metadata utility (not a fact) |
| PowerBI_SupplyChain.DemandFulfillmentCommonContainer_Logility | 3 | 3 | none | demand-fulfillment container |
| SupplyChain_Enh.ATPWeekEnding | 3 | 3 | latest/none | `fact_inventory_position` (ATP in-stock) |
| Inventory_Enh_History.ItemBalance | 3 | 3 | none | `fact_inventory_position` (on-hand balance) |
| AFISales_DW.FactOpenOrders | 3 | 3 | latest/none | `fact_actuals` (open-order side) |

## Notable two-source masters (reach the same entity two ways)

| Entity | Path A (dataflow / PowerBI_SupplyChain) | Path B (SQL / *_DW) | Action |
| --- | --- | --- | --- |
| Product master | `PowerBI_SupplyChain.CurrentProductDetails` (14) | `SupplyChain_DW.DimCurrentProductDetails` (10) | Unify into one gold `DimProduct` |
| Customer master | `PowerBI_SupplyChain.CustomerAcctMaster_AFI` (5) | `AFISales_DW.DimCustomers` (5) | Unify into one gold `DimCustomer` |
| Container / FCC | `PowerBI_SupplyChain.FCC_LogilityCurrentDay` (current-day) | `SupplyChain_Enh.ForecastCommonContainer_Logility` (snapshot) | Same Logility container, two latencies — one fact + snapshot flag |
| Date | `Enterprise_DW.DimDate` (21) | `Enterprise_DW.DimDate_NonRetail` (6) | One `DimDate` with a retail/non-retail calendar attribute |

## Snapshot-handling note

`DemandForecastSnapshot`, `SupplyPlanDetail`, and `PSWWeeklyExtractSnapshot` are each used in
**both** `latest` and `history` modes across models — the same physical object is snapshot-filtered
to "current" for operational reports and retained in full for accuracy/trend reports. Gold facts
must keep the snapshot key (`SnapshotDate` / `SPRunDate` / `FileDate`) so a single fact can serve
both, sliced by a snapshot-selection measure. See [fact-grains.md](fact-grains.md).

## Long tail

The remaining ~62 base objects are single-model (manufacturing iSeries `IMHIST`/`MOMAST`,
warehouse-management `t_stored_item`/`TranLog`, quality `ARPHEADER`, network `facility`, etc.).
These are documented per-model in the Phase 1 summaries and are **not** consolidation targets
for the first gold release; they are candidate silver passthroughs. Full enumeration:
[_inventory/base_objects.csv](_inventory/base_objects.csv).
