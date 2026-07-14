---
title: Governed External Sources Catalog
source: output/summaries/*.md (front matter + source blocks)
models_with_external_sources: 22
---

## How to read this

These are the **non-warehouse** sources — SharePoint lists, Excel workbooks, Power BI / Power
Platform dataflows, and iSeries ODBC pulls. They are **out of scope for gold fact/dimension
modeling** (they don't live in `ashley_edw`), but each one is a real dependency that today sits in
a personal/team file or an undocumented dataflow. Each needs a **governed home and an owner** before
the Fabric migration, or the new model inherits the same fragility. Tagged from the Phase 1 summary
front matter; per-file paths are in the individual summaries.

## SharePoint / Excel files (manually maintained — highest governance priority)

These are hand-maintained spreadsheets feeding production reports. They should move to governed
tables (silver) with documented ownership and refresh cadence.

| Model | Files / lists | Notes |
| --- | --- | --- |
| AFT_SI-SS_PSW | `Userfields Master File (CC,EVC,ABCXYZ).xlsx`, `VENDOR LIST AFT & 232.xlsx`, `Wanek Item DRP Breakdown.xlsx`, `NFM Item Filter.xlsx`, planner `SHAREPOINT` list | All on `masterashley.sharepoint.com/sites/SCPGlobalTeam-Tools`; drive Consumer Choice / EVC / vendor-office / planner-assignment attributes |
| Demand Review | Multiple SharePoint lists + Excel (Bedding, DemandPlanning, SCPGlobalTeam sites) | RH adjustments, seasonality, parameter/threshold tables |
| Top Negatives | SharePoint, Excel | Vendor / negative-SI working files |
| Inv Management | SharePoint | Excess / capacity working file |
| GF Act+Fcst | SharePoint/Excel + dataflow | Customer / account filter inputs |
| Forecast Accuracy (Cust_ItWh) | SharePoint + Power Platform dataflow + DAX | Acceptable-bias parameter, customer master |
| Product Review (NEW) | SharePoint + "Other" | Threshold / parameter inputs |
| Forecast Accuracy (ItWh) | SharePoint + dataflows | Bias parameters |
| Supplier On-Time Performance | Excel + "Other" | Vendor penalty / table-selection inputs |

**Recurring governed-attribute themes** worth a single governed home (they appear in several of the
above): Consumer Choice / EVC product flags, ABC-XYZ segmentation, planner/analyst assignment,
vendor office/mentor mapping, and forecast-bias parameter thresholds.

## iSeries / ODBC direct pulls (operational systems)

Direct ODBC reads from manufacturing iSeries environments — these bypass the warehouse and should
be evaluated for an EDW ingestion path.

| Model | Source |
| --- | --- |
| DvC - WanekMillenium | iSeries ODBC: WFVNPROD (Wanek), MILPROD (Millenium), AFIPROD; plus SharePoint Excel |
| Rolling Report - Wanek Millen | iSeries ODBC |

## Power BI / Power Platform dataflows (semi-governed)

Dataflows are more governed than spreadsheets but still sit outside `ashley_edw` and often shadow a
DW table. The biggest one — `PowerBI_SupplyChain.CurrentProductDetails` — shadows
`SupplyChain_DW.DimCurrentProductDetails` and is the dataflow path of the gold `DimProduct`
(see [conformed-dimensions.md](conformed-dimensions.md)). Models relying on dataflow sources:

| Model | Dataflow source types |
| --- | --- |
| Act+Fcst by WNK & MILL Prod Resource | Power BI Dataflow |
| Act+Fcst vs Manufacturing | Power BI Dataflow |
| Amazon POS Sales and Forecast | Power BI Dataflow |
| Inventory Health | Power BI Dataflows |
| Production Capacity Vs Forecast | Power BI Dataflows |
| Safety Stock Analysis | Power BI Dataflow |
| Supply Plan Detail | Power BI Dataflow |
| Supply Plan Detail Accuracy | Power BI Dataflow |
| Weekly Trend Analysis | Power BI Dataflows |
| Inventory Transactions and Item Balance Detail | Power BI Dataflows |
| When to Disco v2 | Power BI Dataflows |

## Recommendations

1. **Inventory the SharePoint/Excel files into governed silver tables** with named owners and a
   refresh SLA before cut-over — these are the migration's fragility risk. Prioritize the recurring
   themes (Consumer Choice/EVC, ABC-XYZ segmentation, planner assignment, vendor office, bias
   parameters), which serve multiple reports.
2. **Collapse dataflow-vs-DW shadows** by sourcing the gold dimensions from the DW master and
   retiring the `PowerBI_SupplyChain.*` dataflow copies once parity is confirmed.
3. **Evaluate the iSeries ODBC pulls** (DvC, Rolling Report) for a proper EDW ingestion path so
   production reporting no longer reads operational systems directly.
4. **Parameter / threshold tables** (forecast-change thresholds, acceptable bias, SS % adjustment)
   should become a small governed configuration dimension, not per-report SharePoint lists.
