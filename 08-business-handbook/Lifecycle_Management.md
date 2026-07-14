# Lifecycle Management

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis and governed OKF definitions, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | [When_to_Disco_v2_Analysis.md](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md), [Planner_Assignment_Analysis.md](../01-evidence/track-a-reports/Planner_Assignment_Analysis.md), [Product_Review_Analysis.md](../01-evidence/track-a-reports/Product_Review_Analysis.md), [Product_Review_NEW_Analysis.md](../01-evidence/track-a-reports/Product_Review_NEW_Analysis.md), [Complete_Series_In_Stock_Analysis.md](../01-evidence/track-a-reports/Complete_Series_In_Stock_Analysis.md); OKF [`processes/lifecycle_planning.md`](../05-okf-bundle/bundle/processes/lifecycle_planning.md), [`playbooks/new_product_review.md`](../05-okf-bundle/bundle/playbooks/new_product_review.md), [`glossary/recently_introduced.md`](../05-okf-bundle/bundle/glossary/recently_introduced.md) |
| **Important caveat** | The decisions in this domain are **not yet formally registered** in the Decision Registry — `06-bridge/decision-playbook-map.md` explicitly lists "DEC-00x candidates from Product Review reports" as still pending registration. This chapter describes what the reports do; treat any implied decision here as a candidate for a future DEC entry, not yet a confirmed, named decision the way DEC-001 through DEC-011 are. |

---

## 1. What this is, and why it exists

Every item at Ashley moves through a lifecycle: introduced as new, established
as a current seller, and eventually discontinued. Three different questions
map onto three different stages: **is this new item performing as expected**,
**is this current item being managed by the right planner**, and **is this
item ready to be discontinued**. The OKF bundle's lifecycle-planning process
doc groups all three under one process, but — per the caveat above and echoed
in the gap-fill map — that process document
([`processes/lifecycle_planning.md`](../05-okf-bundle/bundle/processes/lifecycle_planning.md))
is entirely unfilled placeholders on cadence, ownership, and decision rules.
What we know instead comes from the reports themselves.

## 2. How this runs today

**New-item performance — Product Review (NEW).** This report's core question is
whether an item/series' demand trajectory, forecast, and supply coverage are
meeting lifecycle expectations — spanning new items (under 9 months invoiced),
current SKUs, and items entering discontinuation
([Product_Review_NEW_Analysis.md](../01-evidence/track-a-reports/Product_Review_NEW_Analysis.md) §1).
Its predecessor, **Product Review** (the original, non-"NEW" report), asks a
broader version of the same question across more data sources — demand trend,
forecast accuracy, supply plan coverage, placements, on-time performance,
retail sales, and inventory turns all in one model
([Product_Review_Analysis.md](../01-evidence/track-a-reports/Product_Review_Analysis.md) §1).

**Series-level stock completeness — Complete Series In Stock.** A narrower,
more specific lens: for each item series and warehouse, what percentage of
SKUs in that series are in stock right now, and how many weeks forward will
they remain in stock. A series counts as "in stock" only when *every* SKU in
it is — one missing SKU breaks the whole series
([Complete_Series_In_Stock_Analysis.md](../01-evidence/track-a-reports/Complete_Series_In_Stock_Analysis.md) §1).

**Planner governance — Planner Assignment.** This is a data-quality worklist,
not an analytics report: for every item in the most recent forecast, is it
assigned to the correct demand planner based on its lifecycle stage, and if
not, who should it be reassigned to
([Planner_Assignment_Analysis.md](../01-evidence/track-a-reports/Planner_Assignment_Analysis.md) §1).

**Discontinuation timing — When to Disco v2.** For items that are
discontinuation candidates, how many months of supply remain, and should the
disco notice be sent now or held — a time-sensitive, per-item operational
worklist rather than a trend report
([When_to_Disco_v2_Analysis.md](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md) §1).

**Not yet confirmed — Track B questions:** whether Product Review (the
original) is still actively used alongside Product Review (NEW), or whether
it's a legacy report kept alive out of habit; who acts on a Planner Assignment
mismatch and how quickly; and what "send the disco notice" actually triggers
downstream once When to Disco v2 recommends it.

## 3. Known issues, in business terms

- **Two reports with the same core purpose calculate the headline number
  differently.** Product Review and Product Review (NEW) both compute a
  demand-fulfillment rate, but with different formulas — the original divides
  by firm demand alone, the NEW version divides by firm demand plus net
  forecast. The same item can show a different fulfillment rate depending on
  which "Product Review" someone happens to open, with no visible reason why
  ([`_catalog/Bug_Findings_Log.md`](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md) BUG-018,
  [`_catalog/Systemic_Patterns_Registry.md`](../01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md) PAT-03).
- **The governed lifecycle process doesn't exist yet on the TO-BE side
  either.** As the caveat above notes, this isn't a case of our discovery
  lagging documentation that already exists — the OKF bundle's own lifecycle
  process document is unfilled. Whatever governance exists today is entirely
  implicit in how these four reports are used, not written down anywhere.
- **"Recently introduced" has no single agreed definition yet.** Safety Stock
  Analysis (see the [Inventory Health chapter](Inventory_Health_and_Excess_Management.md))
  hardcodes a frozen quarter-based window for "Recent Launch," while Product
  Review (NEW) uses a 9-months-invoiced threshold — two different operational
  definitions of a concept the OKF glossary
  ([`glossary/recently_introduced.md`](../05-okf-bundle/bundle/glossary/recently_introduced.md))
  also leaves as `[FILL IN]`.

## 4. Where this is headed (target state)

The governed `DimProduct` is **built** and already defines the schema for a
non-frozen lifecycle window — `LifecycleStage`, `DiscontinuationHorizon`,
`PlanDropDecisionDate`, and `LifecycleSortOrder` columns exist
([`07-fabric-build/docs/model-definitions/dimension-tables/DimProduct.md`](../07-fabric-build/docs/model-definitions/dimension-tables/DimProduct.md)),
consolidating what today are four different per-model lifecycle
classifications (across Inventory Health, Safety Stock Analysis, Demand
Review, and Product Review (NEW)) into one governed attribute set. The values
that should populate these columns are not yet decided — see
[`06-bridge/gap-fill-candidates.md`](../06-bridge/gap-fill-candidates.md).

The OKF bundle's **New Product Performance Review** playbook
([`playbooks/new_product_review.md`](../05-okf-bundle/bundle/playbooks/new_product_review.md))
is further along than the lifecycle *process* document — it defines a
structured reasoning workflow (sales vs. forecast, stockout/overstock risk,
recovery timelines, recommended actions) ready to apply once the underlying
data questions in this chapter are resolved.

## 5. Open questions for Track B

1. Is the original Product Review report still something you open regularly,
   or has Product Review (NEW) effectively replaced it?
2. When Planner Assignment shows a mismatch, what actually happens — is it
   corrected right away, or does it sit for a while?
3. What does "recently introduced" mean to you in practice — is it closer to
   the 9-month window, the quarter-based window, or something else entirely?
4. When When to Disco v2 says "send the notice now," who receives that notice
   and what do they do with it?
