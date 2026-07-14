# Inventory Health & Excess Management

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis and governed OKF definitions, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | [Inv_Management_Analysis.md](../01-evidence/track-a-reports/Inv_Management_Analysis.md), [Safety_Stock_Analysis.md](../01-evidence/track-a-reports/Safety_Stock_Analysis.md), [AFT_SI-SS_PSW_Analysis.md](../01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md), [When_to_Disco_v2_Analysis.md](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md); OKF [`glossary/overstock.md`](../05-okf-bundle/bundle/glossary/overstock.md), [`metrics/overstock_exposure.md`](../05-okf-bundle/bundle/metrics/overstock_exposure.md), [`metrics/safety_stock_gap.md`](../05-okf-bundle/bundle/metrics/safety_stock_gap.md); Decision Registry [DEC-004](../02-decision-registry/decisions/DEC-004.md), [DEC-005](../02-decision-registry/decisions/DEC-005.md) |
| **Important caveat** | This chapter does **not** cover the archive-described 5-bucket "Inventory Health" production report. **Update:** that report is currently being actively built by the data analyst team and does not yet exist in finished form — this is not an unresolved-identity question anymore, it's a report still in progress. Prompt #1 analysis is planned once it's ready. What follows covers the two inventory-adjacent reports that **have** been fully analyzed today: Inv Management (excess/disposal) and Safety Stock Analysis (coverage/replenishment), plus AFT_SI-SS_PSW (safety-stock gaps). Treat any assumption that these reports are "the" inventory health picture as unconfirmed and temporary. |

---

## 1. What this is, and why it exists

Two related but distinct questions sit under "inventory health" at Ashley:

- **Is there too little inventory somewhere** (a safety-stock gap, risking a
  stockout)?
- **Is there too much inventory somewhere** (excess/overstock, tying up capital
  and risking markdown or write-off)?

The OKF bundle treats these as mirror-image concepts:
[Safety Stock Gap](../05-okf-bundle/bundle/metrics/safety_stock_gap.md) is the
shortfall below target; [Overstock](../05-okf-bundle/bundle/glossary/overstock.md)
is the excess above what demand justifies over a planning horizon. Both concepts
exist in the AS-IS estate, implemented independently in different reports, using
different rules.

## 2. How this runs today

**Excess and disposal — Inv Management.** This report's core model is scoped to
warehouse `335`
([Inv_Management_Analysis.md](../01-evidence/track-a-reports/Inv_Management_Analysis.md) §1).
That warehouse is confirmed, via the governed gold `DimWarehouse` definition, to
be **Ashton** — a real, distinct facility grouped separately from the core AFI
warehouses. An earlier version of this analysis described 335 as "Ashley's main
distribution center"; that framing was **overreach and has been corrected** —
see [`07-fabric-build/WAREHOUSE_335_RECONCILIATION.md`](../07-fabric-build/WAREHOUSE_335_RECONCILIATION.md)
for the full comparison and a question queued for Robert. Whatever 335/Ashton's
network-wide role turns out to be, the report classifies excess inventory there
into four disposal paths — Oversea Vendor (returnable), Consolidate, Drop, and
Unexpected — and this classification is the seed for
[DEC-004](../02-decision-registry/decisions/DEC-004.md).

**Safety-stock gaps and expedite/transfer decisions — AFT_SI-SS_PSW.** This
report tracks the reverse condition: item-warehouses below their safety-stock
target with no purchase order covering the gap, using a 21-week horizon across
two lenses (goods due to arrive vs. goods that have departed origin)
([AFT_SI-SS_PSW_Analysis.md](../01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md),
[DEC-005](../02-decision-registry/decisions/DEC-005.md)).

**Lifecycle-driven disposal — When to Disco v2.** Separately from excess-by-
inventory-position, items also get flagged for disposal based on lifecycle
timing — approaching or past their planned discontinuation date — with warehouse-335-specific
measures of its own
([When_to_Disco_v2_Analysis.md](../01-evidence/track-a-reports/When_to_Disco_v2_Analysis.md)).

**Not yet confirmed — Track B questions:** who actually makes the
consolidate-vs-liquidate-vs-return call day to day, how often this happens, and
whether the four-way disposal classification in Inv Management is actually how
the decision gets made in practice, or whether people use their own judgment
alongside it.

## 3. Known issues, in business terms

- **The headline "months of supply" number may be actively misleading.** The
  MOS calculation averages a ratio across items rather than weighting by
  volume. A worked example from the underlying analysis: two items — one with
  100 units excess against 10 units of demand, another with 10 units excess
  against 90 units of demand — average to roughly 5 months of supply, while the
  true volume-weighted answer is about 1.1 months. **A portfolio with a few
  low-volume, high-excess items can look far more urgent than it actually is**,
  or vice versa ([DEC-004](../02-decision-registry/decisions/DEC-004.md), field D5).
- **The overseas-vendor "returnable" classification has no contractual check.**
  Any vendor outside Vietnam is treated as able to take back excess inventory,
  with two specific Vietnam vendors carved out as exceptions — there's no
  verification this matches actual return-program participation or MOQ terms
  ([DEC-004](../02-decision-registry/decisions/DEC-004.md), field D5).
- **The open-capacity figures may double-count.** Two categories used to
  calculate remaining warehouse capacity (SS Coverage and SS Uncover) may be
  complementary rather than additive, which would mean available capacity is
  understated ([DEC-004](../02-decision-registry/decisions/DEC-004.md), field D2).
- **A color-coded urgency indicator may be inverted.** In AFT_SI-SS_PSW, the
  "Due Color" indicator turns red when the safety-stock percentage is *above*
  threshold, which reads backwards from the usual convention — this needs
  confirmation from a user before anyone assumes it's a display bug
  ([BUG-012](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md)) —
  **do not assume this is wrong until confirmed; it may be an intentional
  convention this document simply doesn't have context for.**
- **The "1.4× safety stock" overage rule and the Inv Management excess
  waterfall are two different definitions of the same idea, and they disagree.**
  Demand Review flags overstock at `SI > SS × 1.4`; Inv Management's excess
  waterfall uses a completely different weeks-of-demand logic. Neither has a
  named owner or documented rationale
  ([`06-bridge/gap-fill-candidates.md`](../06-bridge/gap-fill-candidates.md), metric-thresholds table).

## 4. Where this is headed (target state)

The OKF bundle defines the target metrics —
[Overstock Exposure](../05-okf-bundle/bundle/metrics/overstock_exposure.md) and
[Safety Stock Gap](../05-okf-bundle/bundle/metrics/safety_stock_gap.md) — as
clean, symmetrical formulas, but **both still have unset thresholds**
(`[FILL IN: planning horizon in days]`, `[FILL IN: X weeks of forward demand
above SS]`) — arbitrating between the two competing AS-IS rules is a
prerequisite to filling these in, not something either team can do alone.

On the engineering side, the governed `DimWarehouse` (built, see
[`07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md`](../07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md))
is what will eventually let the ~40 hardcoded per-warehouse measures across
Supply Plan Detail and Inv Management collapse into one governed measure. No
gold fact table for inventory position (`inventory_onhand`) is built yet on
either side of this repo — the excess/safety-stock metrics above have a
governed dimension to slice by, but not yet a governed fact to slice.

## 5. Open questions for Track B

1. Walk me through what actually happens when a SKU shows up as "Unexpected"
   excess — who looks at it next, and how fast?
2. When this report shows red on the Due Color indicator, what does that mean
   to you — too much stock, or too little?
3. Has a vendor outside Vietnam ever refused to take back excess inventory
   that this report assumed they'd accept?
4. Do you use the "months of supply" number as-is, or do you already adjust for
   the fact that a few extreme items can skew it?
5. Is warehouse 335/Ashton the main place these decisions actually get made, or
   one location among several you manage the same way?
