# S&OE Playbook Readiness Plan

This plan tracks the work needed to make the OKF bundle ready for an agent to execute a weekly Sales and Operational Execution (S&OE) playbook.

The immediate goal is not to document the business process as a standing meeting. The immediate goal is to create an agent-facing playbook under `bundle/playbooks/` that can reason through the S&OE MVP topics and generate the files needed to run the proposed meeting.

Source reference: `C:\Users\roperez\OneDrive - Ashley Furniture Industries, Inc\Documents\Ad-hoc Analysis\S&OE KPI Framework_0701.xlsx`, tab `MVP`.

## Target Outcome

The bundle is ready when an agent can be pointed at `bundle/playbooks/` and can:

- Identify the S&OE MVP playbook as the right workflow.
- Load the required dataset, metric, glossary, and entity context from the bundle.
- Generate the required meeting package from current data.
- Explain each KPI section using documented definitions, grains, time windows, breakdowns, and ranking logic.
- Flag data gaps explicitly instead of inventing unavailable measures.

## MVP Topics From The Source Workbook

These are the S&OE MVP sections the bundle must support.

| Category | MVP topic | Time window | Required views |
| --- | --- | --- | --- |
| Inventory | In-Stock / Fill Rate by Make and Buy | Prior 4 weeks to next 12 weeks | Make/Buy, Collective Class, Warehouse |
| Inventory | Units Out of Stock / negative Shippable Inventory | Prior 4 weeks to next 12 weeks | Collective Class, Series, Warehouse, top 25 SKU, stockout and recovery dates |
| Inventory | Top 25 Backorders | Next 1 week plus 8-week recovery view | Customer, order, SKU, warehouse, stockout date, recovery date |
| Demand | Top 25 Demand Misses | Prior 1 week | Series, Warehouse, SKU |
| Supply | Top 25 Supply Misses | Prior 1 week | Series, Warehouse, SKU |
| Supply | Actual Production vs Firm Planned Production vs Capacity | Prior 1 week, YTD trend, next 12-week recovery plan | Warehouse |

## Phase 1 - Create The Executable Playbook

- [ ] Create `bundle/playbooks/s_and_oe_mvp_review.md`.
- [ ] Add frontmatter using the existing playbook conventions.
- [ ] Define the playbook purpose as preparing the proposed S&OE meeting package.
- [ ] Document the required input datasets:
  - [ ] `FactSupplyPlanDetail`
  - [ ] `FactCurrentForecast`
  - [ ] `FactWorkingForecast`, if working forecast context is needed
  - [ ] `sales_orders`
  - [ ] `inventory_onhand`
  - [ ] `purchase_orders`
  - [ ] `DimProduct`
  - [ ] `DimWarehouse`
  - [ ] `DimCustomer`
  - [ ] `DimDate`
- [ ] Define the output contract:
  - [ ] Meeting-ready workbook or tabular output package.
  - [ ] Executive summary of the top exceptions.
  - [ ] KPI detail tables by section.
  - [ ] Data-gap and assumption log.
  - [ ] Recommended discussion prompts or actions for each KPI section.
- [ ] Define the playbook execution sequence:
  - [ ] Establish reporting date and time windows.
  - [ ] Validate source freshness and row counts.
  - [ ] Build inventory availability views.
  - [ ] Build backorder risk views.
  - [ ] Build demand miss views.
  - [ ] Build supply miss views.
  - [ ] Build production adherence views.
  - [ ] Summarize cross-functional actions and unresolved blockers.
- [ ] Add related links from the playbook to every metric and source dataset it depends on.
- [x] Add the playbook to `bundle/playbooks/index.md`. (dont by python helper)
- [ ] Add a changelog entry in `bundle/log.md`.

## Phase 2 - Add Supporting Metric Documents

Each metric document should be written for agent execution, not just business definition. It must include grain, source fields, time window, filters, ranking logic, breakdowns, and output columns.

### Fill Rate

- [ ] Create `bundle/metrics/fill_rate.md`.
- [ ] Define actual fill rate as actual shipped quantity divided by actual requested quantity at item-warehouse grain.
- [ ] Clarify how the forward-looking availability view differs from historical shipped/requested fill rate.
- [ ] Document Make/Buy breakdown using `DimProduct[MakeBuyCode]`.
- [ ] Document Collective Class breakdown using `DimProduct[CollectiveClass]` or `DimProduct[CollectiveClassGroup]`.
- [ ] Document Warehouse breakdown using `DimWarehouse`.
- [ ] Identify whether the current bundle has the right shipped quantity and requested quantity fields.
- [ ] Add to `bundle/metrics/index.md`.

### Stockout Exposure

- [ ] Create `bundle/metrics/stockout_exposure.md`.
- [ ] Define units out of stock from negative Shippable Inventory / SI gap logic.
- [ ] Use `FactSupplyPlanDetail[SIQty]`, `SINegative`, `DemandFulfillmentQty`, and `TotalDemand` where appropriate.
- [ ] Define dollar exposure and percent of total exposure.
- [ ] Define stockout date as the first week where available projected inventory cannot cover demand.
- [ ] Define recovery date as the first following week where the projected position returns to non-negative or target-safe status.
- [ ] Document required rollups: Collective Class, Series, Warehouse, SKU.
- [ ] Add to `bundle/metrics/index.md`.

### Backorder Risk

- [ ] Create `bundle/metrics/backorder_risk.md`.
- [ ] Define what qualifies as a backorder for this bundle.
- [ ] Identify source table and fields for open backordered customer demand.
- [ ] Define top 25 ranking by at-risk units, dollars, and percent of total.
- [ ] Include customer, order, SKU, warehouse, original promise date, stockout date, and recovery date in the output contract.
- [ ] Document how backorder risk links to Stockout Exposure and Supply Plan Detail.
- [ ] Add to `bundle/metrics/index.md`.

### Demand Miss

- [ ] Create `bundle/metrics/demand_miss.md`.
- [ ] Define demand miss as actual sales or intake minus expected demand forecast.
- [ ] Confirm whether actual demand should use shipped quantity, ordered quantity, or sales intake for the S&OE view.
- [ ] Confirm whether expected demand should use `FactCurrentForecast`, `FactWorkingForecast`, or another forecast snapshot.
- [ ] Define units, dollars, and percent variance.
- [ ] Define top 25 ranking by absolute miss.
- [ ] Document rollups by Series, Warehouse, and SKU.
- [ ] Add to `bundle/metrics/index.md`.

### Supply Miss

- [ ] Create `bundle/metrics/supply_miss.md`.
- [ ] Define supply miss as firm supply minus actual produced or received supply.
- [ ] Confirm whether the metric includes production only, purchase orders only, transfers, or all supply.
- [ ] Identify current documented fields in `FactSupplyPlanDetail` that support firm or planned supply.
- [ ] Identify missing actual supply source fields.
- [ ] Define units, dollars, and percent variance.
- [ ] Define top 25 ranking by absolute miss.
- [ ] Document rollups by Series, Warehouse, and SKU.
- [ ] Add to `bundle/metrics/index.md`.

### Production Plan Adherence

- [ ] Create `bundle/metrics/production_plan_adherence.md`.
- [ ] Define adherence as `1 - (sum(abs(actual item-level production - item-level plan)) / total production)`.
- [ ] Confirm the source for actual production.
- [ ] Confirm the source for firm planned production.
- [ ] Confirm the source for capacity by warehouse or production site.
- [ ] Define prior-week, YTD trend, and 12-week recovery-plan views.
- [ ] Document warehouse-level output requirements.
- [ ] Add to `bundle/metrics/index.md`.

## Phase 3 - Close Dataset Gaps

The current bundle already has core planning datasets, but the MVP playbook needs several data contracts confirmed before it can be reliably executed.

- [ ] Confirm whether `sales_orders` has the fields needed for fill rate:
  - [ ] Requested quantity.
  - [ ] Shipped quantity.
  - [ ] Current request date.
  - [ ] Promise date.
  - [ ] Customer and order identifiers.
- [ ] Confirm whether `sales_orders` can represent backorders directly, or whether a separate backorder dataset is needed.
- [ ] Create or update a dataset doc for the backorder source if separate from `sales_orders`.
- [ ] Confirm actual production source.
- [ ] Create `bundle/datasets/tables/production_actuals.md` if actual production is a separate table.
- [ ] Confirm production or warehouse capacity source.
- [ ] Create `bundle/datasets/tables/capacity_plan.md` if capacity is a separate table.
- [ ] Confirm whether dollar exposure should use item price, cost, FOB, margin, or another valuation field.
- [ ] Document the selected dollar valuation source in the relevant metric docs.

## Phase 4 - Align Existing Documents

- [ ] Review `bundle/datasets/tables/FactSupplyPlanDetail.md` for all fields needed by S&OE stockout, supply miss, and production views.
- [ ] Review `bundle/datasets/tables/DimProduct.md` for Make/Buy, Collective Class, Series, SKU, and dollar valuation attributes.
- [ ] Review `bundle/datasets/tables/DimWarehouse.md` for warehouse rollups needed by S&OE views.
- [ ] Review `bundle/datasets/tables/DimCustomer.md` for customer-level backorder reporting.
- [ ] Review `bundle/datasets/tables/sales_orders.md` and replace placeholders or stale generic names where known.
- [ ] Update existing cross-links so the S&OE playbook can traverse from playbook to metric to dataset without broken paths.
- [ ] Replace outdated references to root-level dataset paths if the actual files live under `bundle/datasets/tables/`.

## Phase 5 - Define The Meeting Package Contract

The playbook should say exactly what the agent must produce.

- [ ] Define required output files.
- [ ] Define required workbook tabs or table sections.
- [ ] Define required columns for each KPI section.
- [ ] Define default sort order for each table.
- [ ] Define required filters and slicers:
  - [ ] Reporting week.
  - [ ] Warehouse.
  - [ ] Make/Buy.
  - [ ] Collective Class.
  - [ ] Series.
  - [ ] SKU.
  - [ ] Customer, where applicable.
- [ ] Define required summary language:
  - [ ] What changed.
  - [ ] What is at risk.
  - [ ] Who owns the follow-up.
  - [ ] What data is missing.
- [ ] Define severity labels for each KPI section.
- [ ] Define how to handle ties in top 25 lists.
- [ ] Define how to handle zero denominators in percent calculations.

## Phase 6 - Validate Agent Readiness

- [ ] Run a link check across `bundle/`.
- [ ] Regenerate bundle indexes if this repo's tooling supports it.
- [ ] Confirm `bundle/playbooks/index.md` includes the S&OE MVP playbook.
- [ ] Confirm `bundle/metrics/index.md` includes all new S&OE metric docs.
- [ ] Confirm every new doc has required frontmatter.
- [ ] Confirm every new doc has a `Related` section.
- [ ] Confirm all known unknowns are explicitly marked with `[FILL IN: ...]`.
- [ ] Confirm an agent can answer:
  - [ ] What data do I need to prepare the S&OE package?
  - [ ] Which KPI sections do I produce?
  - [ ] What time window applies to each section?
  - [ ] What source fields define each metric?
  - [ ] What tables should be ranked top 25?
  - [ ] What gaps block full execution?

## Current Known Blockers

- [ ] Actual production source is not confirmed.
- [ ] Capacity source is not confirmed.
- [ ] Backorder source is not confirmed as either `sales_orders` or a separate dataset.
- [ ] Dollar valuation source for exposure views is not confirmed.
- [ ] Fill rate numerator and denominator fields are not confirmed.
- [ ] Demand miss actuals basis is not confirmed: shipped demand, ordered demand, or sales intake.
- [ ] Forecast source for demand miss is not confirmed: current forecast, working forecast, or another snapshot.

## Working Assumptions

- The S&OE playbook belongs under `bundle/playbooks/`.
- Supporting KPI definitions belong under `bundle/metrics/`.
- Source/schema/mapping details belong under `bundle/datasets/`.
- Business object descriptions remain under `bundle/entities/`.
- Breakdown views such as Collective Class, Series, Warehouse, SKU, and Customer are sections inside metric/playbook docs, not standalone metrics.
- The bundle should flag unavailable sources instead of inventing calculations.
