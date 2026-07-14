# Change Log

Entries are newest-first. Each entry records what changed and why.

## 2026-07-07

- Renamed the ATP In Stock query document to `/datasets/queries/atp_in_stock_query.md` to distinguish it from the metric document, and updated related metric and query index links.

- Added ATP In Stock documentation from the external SCP data dictionary source: created `/datasets/queries/atp_in_stock_query.md` for the EDW ATP availability SQL and `/metrics/atp_in_stock.md` defining the event-rate KPI as `SUM(InStockEvent) / SUM(StockEvent)`, with `AvgATPQty` documented as supporting context.

- Clarified `/metrics/forecast_accuracy.md` so the core KPI is customer-level and uses the Working Forecast captured at Demand Consensus, when the approved forecast is pushed to SupplyPlanning and synchronized to the supply-facing current forecast at item-warehouse totals. Added the planned KPI table contract for consensus cycle dates, lag snapshot mapping, and customer-level forecast accuracy calculations. Updated `/glossary/demand_consensus.md`, `/datasets/tables/FactWorkingForecast.md`, and `/datasets/tables/FactCurrentForecast.md` to align with this source-of-truth distinction.

- Rewrote `/metrics/forecast_accuracy.md` from the Forecast Accuracy Reporting BRD as the authoritative source. The metric now documents Demand Consensus snapshot alignment, Lag-0 through Lag-4 evaluation, BRD-defined actual demand, row-level error fields, semantic-model calculations for MAPE, wMAPE, wMPE / forecast bias, RMSE, and Process Value Add, plus embedded forecast-accuracy-specific terms and current bundle gaps.

- Updated index generation to preserve directory `index.md` frontmatter as hand-maintained metadata while regenerating only the markdown body. Added directory-level index descriptions so parent indexes summarize subdirectories from explicit metadata rather than the first child document description.

## 2026-07-06

- Added interim current forecast assets while the gold current forecast table is unavailable: created `/datasets/queries/weekly_current_forecast.md` with the Logility SupplyForecast-to-weekly SQL, and created `/datasets/tables/CurFcstSnapshotDaily.md` documenting the latest-snapshot monthly current forecast source table and its base query.

- Updated dataset cross-links for the `datasets/tables/` subdirectory structure: rewrote bundle-relative dataset references to include the `tables/` segment wherever the target file now lives under the tables directory, and rebuilt `bundle/viz.html` from the corrected markdown.

- Added interim EDW query documents under `/datasets/queries/` for gold table shapes that are not yet available in Fabric. These query documents hold the temporary EDW SQL while the corresponding `/datasets/tables/` documents continue to describe the intended Fabric gold tables.

- Added Supply Plan Today query (`/datasets/queries/supply_plan_today.md`): Documents the EDW SQL needed to produce the current-day Supply Plan Detail shape from `[Wholesale_DemandPlanning_AFI].[SupplyPlanDetail]`, including the current-snapshot filter on max `dtea`, the `DimCurrentProductDetails` item join, and derived inventory/demand/supply fields such as `SI-SS`, `SINegative`, `SIPositive`, `SSGap`, `TotalDemand`, `TotalOut`, `TotalTO`, `TotalProd`, `TotalPOs`, `TotalTI`, and `NetInventoryChange`.

- Added Vendor Master query (`/datasets/queries/vendor_master.md`): Documents the EDW SQL needed to produce the Vendor Master shape from `[Wholesale_Purchasing_AFI].[Vennam]`, including the vendor office filter and office-to-location CASE mapping, the `EXTVNDR` join for lead time and active status, and the import/domestic classification from `ProductOrigin`.

- Added Fiscal Calendar query (`/datasets/queries/fiscal_calendar.md`): Documents the EDW SQL needed to produce the Fiscal Calendar shape from `[Enterprise_DW].[DimDate_NonRetail]`, including derived fiscal week, month, quarter, half, and year labels; fiscal period boundary date conversions; holiday and weekday/weekend attributes; and a rolling fiscal-year filter using `FiscalYearIndicator BETWEEN -5 AND 5`.

- Added Customer Master query (`/datasets/queries/customer_master.md`): Documents the EDW SQL needed to produce the Customer Master shape from `[AFISales_DW].[DimCustomers]`, including ship-to geography from `[AFISales_DW].[DimGeographicLocations]`, a five-year ordered-account filter from `[SupplyChain_Enh].[ActualsCustItemWH_AFI]`, and Logility customer grouping overrides from `[Wholesale_ProductSourcing_AFI].[CustomerGrouping]`; documents derived `AccountName` and `CustomerGroup` classification logic.

- Added Item Master query (`/datasets/queries/item_master.md`): Documents the EDW SQL needed to produce the Product Master shape from `[Enterprise_DW].[DimItemMaster]`, including joins to current product details, vendor names, invoice history, item extensions, general descriptions, product knowledge, and non-PK items; documents derived logic for `CollectiveClassGroup`, `AlternateDivision`, `AFIItemStatus`, `LifecycleStage`, `LifecycleStageSort`, `PartFlag`, image URL construction, and planner/future-status/hold-buy coalescing.

- Added Warehouse Master query (`/datasets/queries/warehouse_master.md`): Documents the EDW SQL needed to produce the Warehouse Master shape from `[SupplyChain_DW].[DimAFIWarehouses]`, including `WarehouseGroup`, `PlanningWarehouse`, `SortBy`, and the `AshleyWarehouseMaster` join for `SiteID`.

- Restored the affected gold table documents (`DimWarehouse`, `DimProduct`, `DimCustomer`, `DimDate`, `DimVendor`, and `FactSupplyPlanDetail`) to their Fabric table definitions so `/datasets/tables/` remains the home for gold table documentation, not interim EDW query logic.

## 2026-06-29 (Structural refactor: Playbooks vs. Processes)

Restructured the knowledge base to distinguish between **Playbooks** (step-by-step reasoning workflows for specific analyses) and **Processes** (recurring business workflows, meetings, and decision orchestration):

- Created `/playbooks/` folder and moved four existing decision playbooks: `new_product_review.md`, `forecast_revision.md`, `stockout_escalation.md`, `supply_plan_review.md`. Updated their `type` field from "Process" to "Playbook".
- Created `/playbooks/index.md` organizing playbooks by decision domain (New Product Management, Demand Planning, Inventory Risk, Supply Planning).
- Replaced `/processes/` content with new definition for business processes. Created two placeholder business process files: `lifecycle_planning.md` (product lifecycle evaluation) and `demand_consensus_meeting.md` (recurring forecast review). These are marked `agent draft` with [FILL IN] sections for organization-specific details.
- Updated `/processes/index.md` with new definition and placeholder process entries.
- Updated main `/index.md` to reflect both Playbooks and Processes as top-level domains, with appropriate descriptions distinguishing their purpose.
- Updated `/CLAUDE.md` project instructions to document the Playbooks vs. Processes distinction, updated frontmatter type field reference, updated reasoning guidelines, and clarified file naming conventions (playbook files vs. process files).
- Updated all cross-references (17 files across entities, glossary, datasets, and metrics) to point from `/processes/*` to `/playbooks/*` for the four migrated playbooks.

Why: The prior term "Processes" conflated two different concepts: detailed analytical workflows (which are playbooks—step-by-step recipes you follow to analyze a scenario) and recurring business procedures (which are processes—when decisions happen, who participates, and how they orchestrate). This separation will make the knowledge base clearer for both agents and humans consulting it.

## 2026-06-29 (Working Forecast glossary additions)

- Added Demand Consensus glossary term (`/glossary/demand_consensus.md`): Defines the process by which the working forecast is finalized and synchronized from Logility DemandPlanning to SupplyPlanning. Documents the two key effects at consensus: database handoff and CustomerGroup dimension collapse. Includes a comparison table (pre/post-consensus) and a [FILL IN] placeholder for the cadence and stakeholder details of the review cycle.
- Added Customer Group glossary term (`/glossary/customer_group.md`): Defines CustomerGroup as a Logility demand planning segment distinct from individual customer accounts in DimCustomer. Documents that AFICONS is a valid group (not a data quality flag), that CustomerGroup is grain-level in FactWorkingForecast only, and that it is collapsed at Demand Consensus. Includes a [FILL IN] for the DimCustomer source system.

## 2026-06-29 (Working Forecast)

- Added Working Forecast dataset (`/datasets/tables/FactWorkingForecast.md`): Adapted from data engineering table definition (`FactWorkingForecast`). Documents the nightly Logility DemandPlanning database snapshot at item-warehouse-customer group-week grain. Key distinction from `FactCurrentForecast`: this is the pre-consensus view actively being refined by demand planners; `FactCurrentForecast` is the post-consensus version pushed to Logility SupplyPlanning. `CustomerGroup` is part of the grain here but collapsed at consensus. `AFICONS` is a valid customer group (NULL source values normalized to AFICONS by ETL). Grain normalization (monthly → weekly) will be replaced by native weekly source in Q3 2026; table structure expected to remain unchanged. DDL and TMDL measure definitions omitted. Status: `agent draft`.

## 2026-06-29 (Current Forecast batch)

- Added Current Forecast dataset (`/datasets/tables/FactCurrentForecast.md`): Adapted from data engineering table definition (`FactCurrentForecast`). Documents the latest Logility forecast snapshot at item-warehouse-week grain. All quantities in units. `ResultantForecast` is post-override (planner adjustments included); `PromoLift` is distributed evenly across fiscal weeks in the month (divide by weeks in month) — not week-accurate. Full table replaced daily; `SnapshotDate` is metadata. Grain normalization (monthly → weekly) will be replaced by a native weekly source in Q3 2026; table structure expected to remain unchanged. DDL and ETL SQL omitted. Status: `agent draft`.
- Added Resultant Forecast glossary term (`/glossary/resultant_forecast.md`): Defines "Resultant Forecast" as the Logility forecast value after all planner overrides have been applied. Distinguishes from the raw statistical model output (pre-override) and from Net Forecast (which is further netted against firm orders). Clarifies that promo lift is excluded and tracked separately.
- Added Promo Lift glossary term (`/glossary/promo_lift.md`): Defines Promo Lift and documents the key week-distribution difference between `FactCurrentForecast` (flat distribution across all weeks in the month) and `FactSupplyPlanDetail` (week-accurate, reflects the actual week promo was entered). Includes a use-case table to guide dataset selection.
- Deprecated Demand Forecast dataset (`/datasets/tables/demand_forecast.md`): Was a placeholder document with illustrative column names and no confirmed schema. Superseded by `FactCurrentForecast`, which is the concrete Fabric implementation of the same concept.

## 2026-06-29 (Supply Plan Detail batch)

- Added Supply Plan Detail dataset (`/datasets/tables/FactSupplyPlanDetail.md`): Adapted from data engineering table definition (`FactSupplyPlanDetail`). Documents the current-day Logility supply plan extract at item-warehouse-week grain, 39-week forward horizon, with WeekEnding always on Saturday. Table is a daily full overwrite; SnapshotDate is metadata, not part of grain. Schema organized into Grain/Keys, Demand, Transfers Out, Production, Purchase Orders, Transfers In, Inventory Position, Aggregate Demand & Fulfillment, Aggregate Supply, and Metadata sections. Includes firm vs. planned supply distinction and planning horizon notes. `data_source: both` (Azure SQL and Fabric). Schema placeholder `[FILL IN: schema]` left in `resource` field — not yet finalized for production. DDL and DAX/TMDL measure definitions omitted. Status: `agent draft`.
- Added Supply Plan Review process (`/processes/supply_plan_review.md`): Six-step exception-based playbook for agents and planners interpreting `FactSupplyPlanDetail`. Covers scope filtering (active items, warehouse scope), SI negative identification and triage, safety stock gap assessment, fulfillment shortfall quantification, firm vs. planned supply distinction, and prioritized exception ranking with recommended actions. Status: `agent draft`.
- Added Shippable Inventory glossary term (`/glossary/shippable_inventory.md`): Defines "Shippable Inventory" as an org-specific Logility concept — projected ending inventory net of planned demand and supply, not physical on-hand or staged inventory. Includes interpretation table for positive/zero/negative SI values. Status: `agent draft`.
- Added Net Forecast glossary term (`/glossary/net_forecast.md`): Defines Net Forecast as the statistical forecast net of firm orders, floored at zero. Explains the netting logic, why the floor exists, and the near-term vs. outer-week demand composition pattern. Status: `agent draft`.
- Added Firm Demand glossary term (`/glossary/firm_demand.md`): Defines Firm Demand as confirmed open customer order quantity, distinct from statistical forecast. Explains its priority role in the Logility supply plan and the near-term vs. outer-week order horizon pattern. Status: `agent draft`.
- Added Shippable Inventory metric (`/metrics/shippable_inventory.md`): Defines SI calculation (`BeginningBalance + TotalReceipts − TotalOut`), interpretation table, relationship to safety stock, and aggregation caveat (SI values should not be summed across weeks). Status: `agent draft`.
- Added Safety Stock Gap metric (`/metrics/safety_stock_gap.md`): Defines SSGap (`MAX(0, SSQty − SIQty)`), interpretation by gap/SI condition, and exception prioritization guidance (near-term first, filter inactive items). Status: `agent draft`.
- Added Projected Fulfillment Rate metric (`/metrics/projected_fulfillment_rate.md`): Defines rate as `DemandFulfillmentQty / TotalDemand`, notes divide-by-zero guard when TotalDemand = 0, and explains relationship to SI (rate is always 100% when SI ≥ 0). Status: `agent draft`.
- Renamed files to follow naming conventions: Glossary, Metrics, and Processes files converted from PascalCase to lowercase_with_underscores (`ShippableInventory.md` → `shippable_inventory.md`, `NetForecast.md` → `net_forecast.md`, `FirmDemand.md` → `firm_demand.md`, `SafetyStockGap.md` → `safety_stock_gap.md`, `ProjectedFulfillmentRate.md` → `projected_fulfillment_rate.md`, `SupplyPlanReview.md` → `supply_plan_review.md`). Updated all cross-references and index links.

## 2026-06-29

- Added Vendor Master dataset (`/datasets/tables/DimVendor.md`): Adapted from data engineering table definition (`DimVendor`); central vendor dimension consolidating attributes from `PowerBI_SupplyChain.VendorMaster` (primary source) and PSW/sourcing lookups. DDL, primary key constraint, and dropped columns (`AFILeadTime`, `WVFLeadTime`) omitted — column definitions and business context retained. Schema grouped into Identity and Attributes sections. Notes that vendor-level aggregates (open POs, ranking) live in the measure layer, not this table. Schema placeholder `[FILL IN: schema]` left in `resource` field. Status: `agent draft`.
- Added Vendor entity (`/entities/vendor.md`): Documents the Vendor business object covering active status interpretation (`VendorActive` Y/N), lead time usage in supply planning, country-of-origin vs. product-origin distinction, and vendor office grouping. Linked to `DimVendor` as authoritative dataset. Status: `agent draft`.

- Added Warehouse Master dataset (`/datasets/tables/DimWarehouse.md`): Adapted from data engineering table definition (`DimWarehouse`); central warehouse dimension consolidating physical warehouse attributes with ETL-computed `WarehouseGroup`, `PlanningWarehouse`, and `SortBy` columns. DDL, primary key constraint, and ETL SQL omitted; column definitions and business context retained. Schema placeholder `[FILL IN: schema]` left in `resource` field. Status: `agent draft`.
- Added Warehouse entity (`/entities/warehouse.md`): Documents the Warehouse business object using `WarehouseGroup` and `PlanningWarehouse` classification logic derived from the ETL. Includes full group-to-warehouse-code mapping (AFI, ASH, C.DIR, PROD, CXD, SDS) and the complete virtual-to-physical facility collapse table (e.g., `1A → 1-RKD`, `ECA → ECR-ECR`). Notes the intentional distinction between warehouse 19 (PROD) and 19A (AFI). Status: `agent draft`.

- Removed Item Master placeholder after supersession by `/datasets/tables/DimProduct.md`: Updated all 14 references across 10 files to point to `DimProduct` instead. Updated field names where mapping is known: `intro_date` → `InitialInvoiceDate`, `item_status` → `LifecycleStage`, FK join text updated to use `ItemSKU`. Added `[FILL IN: confirm lead time column]` markers in `coverage_days.md`, `stockout_escalation.md`, `new_product_review.md`, and `inventory_onhand.md` where `lead_time_days` was referenced but has no equivalent column in DimProduct yet.
- Updated Product entity (`/entities/product.md`): Rewrote from scratch grounded in `DimProduct`. Updated `resource` to point to `DimProduct`. Replaced generic placeholder field names with actual column names (`ItemSKU`, `LifecycleStage`, `PartFlag`, `KitFlag`, etc.). Replaced abstract lifecycle stage table with the four ETL-governed stages (Pre-Invoicing, Recent Launch, Current, End of Life) and their derivation logic. Added Component and Kit Classification section explaining `PartFlag` and `KitFlag` usage rules. Linked `DimProduct` as the authoritative dataset.

---

- Added Transaction Date entity (`/entities/transaction_date.md`): Fiscal calendar date entity documenting the fiscal hierarchy (week, month, quarter, half, year), period boundary columns, relative period indicators, and holiday/day-type classification. Backed by the Fiscal Calendar dataset. Status: `agent draft`.
- Added Product Master dataset (`/datasets/tables/DimProduct.md`): Adapted from data engineering table definition (`DimProduct`); central product dimension consolidating item master attributes, ETL-computed lifecycle classification (`LifecycleStage`, `PartFlag`, `KitFlag`), and planning fields at the item SKU grain. DDL, ETL logic, and source SQL omitted; schema column table filtered by DE exclusion list. Several pending-implementation columns noted (`MakeBuyCode`, `DiscontinuationHorizon`, `PlanDropDecisionDate`, `MarketableConversionFactor`, `MarketableItemSKU`). Schema placeholder `[FILL IN: schema]` left in `resource` field — target schema not specified in source definition. Status: `agent draft`.
- Added Fiscal Calendar dataset (`/datasets/tables/DimDate.md`): Adapted from data engineering table definition (`DimDate`); provides fiscal week, month, quarter, half, and year attributes plus relative period indicators for rolling-window analysis. DDL and PK constraint sections omitted — schema column definitions retained. Resource placeholder left as `[FILL IN]` because warehouse and schema are not yet finalized in the source definition. Status: `agent draft`.
- Added Customer Master dataset (`/datasets/tables/DimCustomer.md`): Adapted from data engineering table definition; consolidated account and ship-to location attributes for demand forecasting, order fulfillment, and forecast accuracy use cases. Status: `agent draft` — pending schema placeholder fill-in and refresh cadence confirmation.
- Added Customer entity (`/entities/customer.md`): Canonical customer business object documenting account vs. ship-to distinction, customer segmentation logic (CustomerGroup, CustomerSegment, BusinessType), and regional/territorial organization (Region, District). Linked to `DimCustomer` as authoritative dataset. Status: `agent draft`.

## 2026-06-26

- Initial bundle scaffold created: AGENT.md, root index.md, all subdirectory index files.
- MVP vertical slice for Demand/Supply Planning domain added: new_product_review process, supporting datasets (demand_forecast, sales_orders, inventory_onhand, purchase_orders, item_master), metrics (forecast_accuracy, coverage_days, days_of_supply, overstock_exposure), entity (product), glossary terms (recently_introduced, stockout, overstock), and supporting processes (forecast_revision, stockout_escalation).
- All documents marked `status: agent draft` — content requires review and company-specific values (table names, thresholds, time windows) filled in before marking active.
