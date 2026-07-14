---
title: Conformed Dimensions Catalog
source: output/analysis/_inventory/dim_columns.csv
conformed_dimensions: 6
---

## How to read this

Each section is one proposed gold dimension. "Shared source columns" are the attributes pulled
straight from the EDW master (present consistently across models). "Drifted calculated columns"
are **model-local DAX calculated columns** that re-derive business attributes on top of the
master — these have diverged across models and are the reconciliation work: each must become one
governed gold column with one canonical rule. Full column matrix:
[_inventory/dim_columns.csv](_inventory/dim_columns.csv).

| Gold dimension | Role-playing name today | Models | Calc cols | Two-source? |
| --- | --- | --- | --- | --- |
| DimProduct | z_ProductDetails | 16 | 110 | Yes |
| DimDate | z_FiscalCal | 16 (21 incl. base) | 20 | Yes (retail / non-retail) |
| DimWarehouse | z_WarehouseMaster | 14 | 3 | No |
| DimVendor | z_VendorMaster | 9 | 2 | No |
| DimCustomer | z_CustomerMaster_AFI | 5 | 7 | Yes |
| DimProductionResource | z_ProdResourceMaster | 2 | 4 | No |

---

### z_ProductDetails → gold dim `DimProduct`

**Reached via:** dataflow `PowerBI_SupplyChain.CurrentProductDetails` (14 models) **and** SQL
`SupplyChain_DW.DimCurrentProductDetails` (10 models) — same product master, unify. Item-master
extensions (`MasterData_ItemMaster_AFI.ITMEXT`/`ITBEXT`, `Enterprise_DW.DimItemMaster`) hang off
the same Item SKU grain and should fold in as attributes.

**Shared source columns:** Item SKU, Item Description, Series Number, Series Name, Collective
Class, Product Line, FOB Price, Qty In Box, General Description Code, Current Status, Future
Status, AFI Item Status, Import/Domestic Code, Responsible Office, AFI Finance Division, Make/Buy
Code, Item Ext Series Number (see `dim_columns.csv` for the full ~70-column source list).

**This is the largest reconciliation surface in the estate: 110 model-local calculated columns.**
The display-helper columns are harmless duplicates; the classification columns are genuine drift.

**Harmless display helpers (standardize, low risk):**

| Concern | Models | Note |
| --- | --- | --- |
| `ItemSKU Desc` (`Item SKU & " - " & Item Description`) | 14 | Identical CONCATENATE — one gold column |
| `Series Desc` (`Series Number & " - " & Series Name`) | 13 | Identical CONCATENATE — one gold column |

**Drifted classification columns to reconcile (pick one canonical rule each):**

| Concern | Models | Note |
| --- | --- | --- |
| Lifecycle classification (`z_LifeCycle`, `z_LifeCycleCat`) | Inventory Health, Safety Stock Analysis | SWITCH on Future Status / AFI Item Status / KitMarket → Disco/Scrap/Recent Launch/… — same intent, verify thresholds match |
| `Life Cycle Status` + `Market + Life Cycle` | Demand Review, Product Review (NEW) | Separate multi-line SWITCH (different column name, overlapping intent with z_LifeCycle) — converge all four into one canonical lifecycle attribute |
| `Status` / `Stat` | Demand Review, Product Review (NEW) | Status-grouping SWITCH — reconcile with lifecycle |
| Disco/drop horizon (`DropIn12Mo/18Mo/24Mo`, `PlanDropDecisionDate`, `z_Dropped at Horizon`, `z_SortLifecycle`) | Safety Stock Analysis, Supply Plan Detail | Disco-timing logic implemented several ways — one governed set of horizon flags |
| `KitMarket` (LOOKUPVALUE to z_KitMkt) | Inventory Health, Safety Stock Analysis | Depends on a separate kit-market table (exact-dup query `941938c73560`) — fold the kit-market intro date into DimProduct |
| `KitMarket` / `Kit Flag` / kit-type | Inventory Health, Safety Stock Analysis, + matt-kit in Safety Stock | Kit identification logic — one canonical kit flag |
| `z_MarketableConversion` | GF Act+Fcst, Weekly Trend Analysis | `DIVIDE(1, SWITCH(General Description Code,700,LOOKUPVALUE(Qty In Box, parent SKU),1))` — identical here, but this is the **marketable-SKU conversion** business rule (see [transformation-patterns.md](transformation-patterns.md)); belongs in silver, exposed as a gold column |
| `Coll Class` re-derivation | Inventory Health, Safety Stock Analysis, Supply Plan Detail Accuracy | Collective-class grouping computed locally — standardize |
| `z_ItemFilter` (report-visibility flag) | 7 models | `ISNUMBER([model-specific measure])` — model-specific by design; **not** a gold column, it is a report-layer visibility helper. Document and drop from the dimension |

**Recommendation:** DimProduct is the priority-1 gold artifact. Lift the source attributes from
the unified master, then replace the lifecycle/status/kit/marketable family with a small set of
governed columns whose rules are agreed once. Leave `z_ItemFilter`-style visibility flags in the
report layer.

---

### z_FiscalCal → gold dim `DimDate`

**Reached via:** `Enterprise_DW.DimDate` (21 models) and `Enterprise_DW.DimDate_NonRetail`
(6 models) — reconcile to one calendar with a retail/non-retail attribute rather than two tables.
The `z_FiscalCal` role-playing copy appears in 16 models.

**Shared source columns:** Transaction Date, Fiscal Year, Fiscal Week Num, Fiscal Year Week Num,
Fiscal Month Num, Fiscal Month Year Num, Fiscal Month/Year Desc, Fiscal Quarter/Half Num, Fiscal
Week/Month/Year Start & End, plus the **Fiscal Day/Week/Month/Quarter/Year Indicator** relative
columns (≈40 source columns — see `dim_columns.csv`).

**Drifted calculated columns to reconcile:**

| Concern | Models | Note |
| --- | --- | --- |
| `FiscalWeeksinMonth` | Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing | Hardcoded `SWITCH(... 202212,6, month→5/4 ...)` weeks-in-month — replace with a governed weeks-per-fiscal-month column, drop the hardcoded 2022 exception |
| ~20 fiscal-window relative columns (e.g. "this month = 0", offsets) | 16 models | The **fiscal-indicator-window** pattern (18 models). Centralize relative-period indicators on DimDate so measures stop re-deriving them |

**Recommendation:** Centralizing DimDate + the relative-period indicators is the broadest single
reduction. See the fiscal-indicator-window block in [transformation-patterns.md](transformation-patterns.md).

---

### z_WarehouseMaster → gold dim `DimWarehouse`

**Reached via:** model-local warehouse lists / `PowerBI_SupplyChain.WarehouseMaster` /
`SupplyChain_DW.DimAFIWarehouses` (14 models).

**Shared source columns:** Warehouse (number), Warehouse name, region/site groupings.

**Drifted calculated columns to reconcile:**

| Concern | Models | Note |
| --- | --- | --- |
| Physical-warehouse normalization (`Physical WH`, `WH Site`, `WHSE`) | GF Act+Fcst, Safety Stock Analysis, Weekly Trend Analysis | Three different column names re-mapping raw warehouse codes to a physical-site grouping — this is the **warehouse-normalization** pattern (3 models). One canonical physical-warehouse attribute |

**Critical downstream impact:** a governed `DimWarehouse` is what lets the hardcoded `WH## SI`
measure family (see [measure-archetypes.md](measure-archetypes.md)) collapse to a single measure
sliced by warehouse.

---

### z_CustomerMaster_AFI → gold dim `DimCustomer`

**Reached via:** `PowerBI_SupplyChain.CustomerAcctMaster_AFI` (5 models) **and**
`AFISales_DW.DimCustomers` (5 models) — same customer entity, two paths, unify.

**Shared source columns:** Account Number, Account And ShipTo Number, Customer Group, Reporting
Business Type, customer hierarchy attributes.

**Drifted calculated columns to reconcile:**

| Concern | Models | Note |
| --- | --- | --- |
| Account-filter / sort helpers (`z_AcctFilter`, `z_SortRank`, `CustGroup`, `Customer`, `Test`, `Column`) | GF Act+Fcst, Weekly Trend Analysis | Mostly report-local filter/label helpers; keep `z_AcctFilter` logic only if a governed customer-eligibility flag is wanted, otherwise leave in report layer |

---

### z_VendorMaster → gold dim `DimVendor`

**Reached via:** `PowerBI_SupplyChain.VendorMaster` (4 models) plus
`Wholesale_Purchasing_*.VENNAM` and `Wholesale_ProductSourcing_AFI.vendor` (vendor-name sources
in the PSW/sourcing reports), 9 models total touch a vendor dimension.

**Shared source columns:** Vendor Number, Vendor Name, vendor office/region.

**Drifted calculated columns to reconcile:**

| Concern | Models | Note |
| --- | --- | --- |
| `OpenPOs`, `rank` | Supply Plan Detail | Vendor-level open-PO aggregate + ranking computed on the dimension — these are really measures; move to fact/measure layer, keep DimVendor attribute-only |

---

### z_ProdResourceMaster → gold dim `DimProductionResource`

**Reached via:** `SupplyChain_Enh.ProductionConversion` (5 models feed production-resource
mapping; 2 models materialize the role-playing dimension).

**Shared source columns:** ResourceID, LocationID, resource description.

**Drifted calculated columns to reconcile:**

| Concern | Models | Note |
| --- | --- | --- |
| `Prod Group` | Act+Fcst by WNK & MILL, Act+Fcst vs Manufacturing | `SWITCH(LocationID, 900515→Wanek 1, 900639→Wanek 2, 600039→Wanek 3, 624556→Millenium, Domestic)` — identical hardcoded plant mapping; promote to a governed plant/group attribute |
| `Resource Group` | same 2 models | Multi-line resource grouping SWITCH — standardize alongside Prod Group |
