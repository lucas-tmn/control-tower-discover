# Supply Planning & Capacity

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis and governed OKF definitions, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | catalog-level entry for Supply Plan Detail ([`_catalog/Report_Catalog_Comprehensive_View.md`](../01-evidence/track-a-reports/_catalog/Report_Catalog_Comprehensive_View.md)); OKF [`playbooks/supply_plan_review.md`](../05-okf-bundle/bundle/playbooks/supply_plan_review.md). Production-capacity and Wanek/Millennium-specific reports have moved to their own chapter — see [Manufacturing_and_Production_Capacity.md](Manufacturing_and_Production_Capacity.md). |
| **Important caveat** | **`Supply Plan Detail` — the report the majority of the estate is structurally anchored to (13 of 26 models use its underlying source) — has never had a full Prompt #1 analysis.** Access was previously blocked, and it remains one of two outstanding items from the original 6 cluster representatives (alongside Plan Drop 1). This chapter is intentionally scoped to Supply Plan Detail itself; production-capacity questions for Wanek/Millennium now live in [Manufacturing_and_Production_Capacity.md](Manufacturing_and_Production_Capacity.md), which is further along (2 of 5 reports fully analyzed as of 2026-07-13). |

---

## 1. What this is, and why it exists

Once demand is planned (see [Demand Planning & Forecast Consensus](Demand_Planning_and_Forecast_Consensus.md)),
supply planning answers a different question: **can we actually get the
product to the right warehouse in time to meet that demand, and if not, where
exactly does it break?**

The OKF bundle's reasoning playbook for this
([`playbooks/supply_plan_review.md`](../05-okf-bundle/bundle/playbooks/supply_plan_review.md))
frames the supply plan as a forward-looking, point-in-time projection — "always
a snapshot of today's plan as of `SnapshotDate`... conclusions drawn here
reflect the plan's expectations, not physical warehouse reality." That
distinction — plan vs. reality — is the organizing idea for this whole domain.

## 2. How this runs today

**The core weekly supply review — Supply Plan Detail (catalog-level only).**
Per the existing catalog entry
([`_catalog/Report_Catalog_Comprehensive_View.md`](../01-evidence/track-a-reports/_catalog/Report_Catalog_Comprehensive_View.md) §9),
this is the Supply Chain Planning team's weekly review: a daily Logility
snapshot giving the full inventory position per item × warehouse × week —
beginning balance, firm/planned production, POs, transfers, demand, and derived
Shippable Inventory (SI) — across a 35-week capable-to-promise horizon. The
central questions it answers: is each SKU/warehouse above or below safety
stock, where are the negative positions, and what production/POs are already
scheduled. **This catalog entry is lighter than a full Prompt #1 pass** — it
does not yet carry the bug/pattern-level detail the fully-analyzed reports in
this handbook do.

**Production capacity and Wanek/Millennium-specific reports now live in their
own chapter.** See [Manufacturing_and_Production_Capacity.md](Manufacturing_and_Production_Capacity.md)
for Act+Fcst by WNK & MILL Prod Resource, Act+Fcst vs Manufacturing,
Production Capacity Vs Forecast, DvC - WanekMillenium, and Rolling Report -
Wanek Millen — 2 of those 5 now have full Prompt #1 analyses.

**Not yet confirmed — Track B questions:** who reviews Supply Plan Detail and
how often (weekly is inferred from its name and grain, not confirmed by
interview), and what triggers escalation on a negative position.

## 3. Known issues, in business terms

- **Supply Plan Detail's own reliability is unaudited.** Because this report
  has not had a full analysis, none of the verification applied elsewhere in
  this repo (duplicate-measure checks, broken-reference checks, magic-number
  audits) has been applied to the single report most of the estate depends on.
  This is a real gap, not just a documentation one.
- **Production-capacity and Wanek/Millennium-specific known issues** (the
  capacity measure that can't structurally show a shortage, the iSeries direct
  connections, etc.) now live in
  [Manufacturing_and_Production_Capacity.md](Manufacturing_and_Production_Capacity.md) §3.

## 4. Where this is headed (target state)

`FactSupplyPlanDetail` is **built** in the Fabric gold layer with real ETL SQL
([`07-fabric-build/docs/model-definitions/scp-core-model/FactSupplyPlanDetail.md`](../07-fabric-build/docs/model-definitions/scp-core-model/FactSupplyPlanDetail.md)),
as is `DimProductionResource`
([`07-fabric-build/docs/model-definitions/dimension-tables/DimProductionResource.md`](../07-fabric-build/docs/model-definitions/dimension-tables/DimProductionResource.md)) —
this domain has two of the five built conformed dimensions/facts, ahead of most
other domains in this handbook. A candidate `FactProduction` gold fact is
identified in the Fabric team's own analysis but **not yet built**
([`07-fabric-build/docs/report-migration-docs/02-group-analysis/fact-grains.md`](../07-fabric-build/docs/report-migration-docs/02-group-analysis/fact-grains.md)).

The OKF `supply_plan_review.md` playbook already defines a governed
exception-based reasoning process (scope by item/warehouse/time, exclude
end-of-life items and component parts) — this is further along than most
processes in the OKF bundle, most of which remain unfilled placeholders.

## 5. Open questions for Track B

1. Walk me through your weekly supply plan review — what do you look at first,
   and what makes something worth escalating?
2. Has Supply Plan Detail ever shown a negative position that turned out to be
   wrong once someone checked the physical warehouse?

See [Manufacturing_and_Production_Capacity.md](Manufacturing_and_Production_Capacity.md)
§5 for Wanek/Millennium-specific Track B questions.
