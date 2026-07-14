---
title: Phase 2 Cross-Model Analysis — Executive Overview
models_analyzed: 26
distinct_base_objects: 107
base_object_usages: 439
conformed_dimensions: 6
candidate_fact_grains: 9
measure_archetypes: 10
distinct_measures: 879
distinct_measure_signatures: 253
shared_measure_signatures: 64
exact_duplicate_queries: 10
reusable_transform_patterns: 6
governed_external_sources: 14
---

## Purpose

This catalog set tells the data-engineering team how to structure the new Fabric gold/silver
tables and the centralized semantic model. It is **not** a clone of today's 26 reports. It
identifies the small set of **conformed dimensions**, **fact grains**, **reusable silver
transformations**, and **measure archetypes** that can answer the same business questions with
far less duplication.

All structural facts come from the inventory intermediates in
[output/analysis/_inventory/](_inventory/), parsed directly from the source TMDL. Business
meaning was confirmed from the human-curated Phase 1 summaries only where a cluster was ambiguous.

## Headline counts

| Metric | Value |
| --- | --- |
| Semantic models analyzed | 26 |
| Distinct EDW base objects referenced | 107 |
| Total base-object usages (model × report-table) | 439 |
| Proposed conformed dimensions | 6 |
| Candidate gold fact grains | 9 |
| Measure archetypes | 10 |
| Distinct measures across all models | 879 |
| Distinct normalized measure signatures | 253 |
| Signatures shared across >1 model | 64 |
| Exact-duplicate source queries (by fingerprint) | 10 |
| Reusable silver transformation patterns | 6 |
| Governed external sources (SharePoint/Excel/iSeries) | 14 models affected |

## Catalog files

| File | Contents |
| --- | --- |
| [base-objects.md](base-objects.md) | EDW base objects → models/report-tables, role, grain, snapshot handling |
| [conformed-dimensions.md](conformed-dimensions.md) | 6 gold dimension candidates + per-model drifted-calculated-column reconciliation |
| [fact-grains.md](fact-grains.md) | 9 candidate gold facts: grain, sources, snapshot strategy, questions answered |
| [transformation-patterns.md](transformation-patterns.md) | 6 reusable silver building blocks + inconsistencies to reconcile |
| [measure-archetypes.md](measure-archetypes.md) | 10 archetypes with canonical parameterized forms + flagged exceptions |
| [source-governance.md](source-governance.md) | SharePoint/Excel/iSeries sources needing a governed home |

## Top consolidation opportunities (by # models affected)

1. **One conformed `DimProduct`** — replaces `z_ProductDetails` (16 models, **110 model-local
   calculated columns**) reached two ways: dataflow `PowerBI_SupplyChain.CurrentProductDetails`
   (14 models) **and** SQL `SupplyChain_DW.DimCurrentProductDetails` (10 models). This is the
   single highest-impact item: lifecycle/status SWITCHes, marketable-SKU conversion, and
   kit-market lookups have all drifted across models and must be reconciled into governed gold
   columns. See [conformed-dimensions.md](conformed-dimensions.md).

2. **One conformed `DimDate` + a fiscal-calendar service** — `Enterprise_DW.DimDate` is used by
   21 of 26 models and the `z_FiscalCal` role-playing table appears in 16, carrying ~20 repeated
   fiscal-window calculated columns. The **fiscal-indicator-window** pattern appears in 18 models.
   Centralizing the fiscal calendar (with relative-period indicator columns) removes the most
   widespread duplication in the estate.

3. **One `fact_supply_plan` from `SupplyPlanDetail` + one `fact_forecast_snapshot` from
   `DemandForecastSnapshot`** — these two base objects anchor 13 and 11 models respectively, with
   10 exact-duplicate source queries clustering around them and the product/placement helper
   tables. The hardcoded **`WH## SI`** measure family (≈30 near-identical measures in
   `Supply Plan Detail` alone) should collapse to **one measure sliced by `DimWarehouse`**.

## Human review gate

Please review this catalog set and confirm before Phase 3 (gold table design). Phase 3 will turn
these conformed dimensions, fact grains, and measure archetypes into proposed gold table names,
canonical column definitions, source SQL logic, and a centralized DAX measure list.
