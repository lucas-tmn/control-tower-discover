# Manufacturing & Production Capacity

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | [Act_Fcst_by_WNK_MILL_Prod_Resource_Analysis.md](../01-evidence/track-a-reports/Act_Fcst_by_WNK_MILL_Prod_Resource_Analysis.md) (full analysis); [RollingReport_WanekMillen_Analysis.md](../01-evidence/track-a-reports/RollingReport_WanekMillen_Analysis.md) (full analysis); schema-level technical docs for [Act+Fcst vs Manufacturing](../01-evidence/source-model-docs/Act_Fcst_vs_Manufacturing.md), [Production Capacity Vs Forecast](../01-evidence/source-model-docs/Production_Capacity_Vs_Forecast.md), and [DvC - WanekMillenium](../01-evidence/source-model-docs/DvC_WanekMillenium.md); Decision Registry [DEC-006](../02-decision-registry/decisions/DEC-006.md) |
| **Important caveat** | **2 of the 5 reports in this domain have a full Prompt #1 business analysis; 3 remain schema-level only** (tables/DAX/relationships, no bug or decision analysis). What follows for those 3 is lighter depth — everything else in this chapter has full analysis behind it. This chapter also does not yet cover `Supply Plan Detail` itself, the backbone report 13 of 26 estate models depend on — see the caveat in [Supply_Planning_and_Capacity.md](Supply_Planning_and_Capacity.md). |

---

## 1. What this is, and why it exists

Supply planning (see [Supply Planning & Capacity](Supply_Planning_and_Capacity.md))
asks whether the plan can be executed. Manufacturing asks the layer beneath
that: **can the physical plants — Ashley's own domestic finished-goods lines,
plus the Wanek and Millennium vendor facilities that feed them — actually
produce enough, fast enough, to keep that plan real?**

Two vendor facilities sit at the center of nearly every report in this
domain: **Wanek** (vendor codes `600039` / `900639`) and **Millenium**
(vendor codes `624556` / `900515`). They manufacture kits and components that
domestic plants convert into finished goods — which is why a domestic
capacity question (Act+Fcst vs Manufacturing) and a vendor capacity question
(the other four reports) are really the same question asked one supply-chain
tier apart.

## 2. How this runs today

**Production capacity vs. combined demand — Act+Fcst by WNK & MILL Prod
Resource (fully analyzed).** Asks whether production capacity at each
Wanek/Millennium resource covers combined actual + forecast demand over a
16-week horizon
([DEC-006](../02-decision-registry/decisions/DEC-006.md)).

**PO firmness and rollover — Rolling Report - Wanek Millen (fully
analyzed).** A different, narrower question: of the purchase-order quantity
Wanek/Millennium has *confirmed as firm*, how much is actually rolling to a
later delivery week, how has that roll rate trended over ~10 snapshot weeks,
and does safety-stock coverage still hold when it rolls? This is a supplier
**reliability** lens — Act+Fcst by WNK & MILL Prod Resource asks "is there
enough capacity"; this report asks "is the capacity we were promised actually
showing up on time."

**One level up — domestic finished-goods capacity (schema-level only).**
**Act+Fcst vs Manufacturing** asks whether domestic U.S. finished-goods
capacity can absorb blended actual + forecast demand, then steps back down to
check whether Wanek/Millennium's own capacity and output (`ProdCapacity`,
`VendorShipped`) can support it — using a **56-day ETD offset** to represent
the lead time between Wanek/Millennium shipping components and domestic
plants converting them to finished goods.

**Forecast vs. actual manufacturing/procurement orders (schema-level
only).** **Production Capacity Vs Forecast** compares forecast against actual
manufacturing orders, POs, and receipts by item/warehouse/resource, scoped to
"Z"-class products — used to spot production bottlenecks and capacity
utilization by location.

**Demand vs. capacity, 30-week rolling (schema-level only).** **DvC -
WanekMillenium** checks whether each facility can absorb the planned, firm,
and shipped volumes from the Production Schedule Workbench (PSW) over a
rolling 30-week horizon, comparing PSW snapshots and the unconstrained plan
(from EDW) against actual production scans read directly from iSeries factory
systems (FG Output, RP Scan).

**Not yet confirmed — Track B questions:** which of these five reports
planners actually open week to week vs. which have fallen out of use; whether
the 56-day ETD offset in Act+Fcst vs Manufacturing is still accurate; and
whether Rolling Report's roll-rate trend has ever driven a real escalation to
Wanek or Millenium.

## 3. Known issues, in business terms

- **The Wanek/Millennium capacity figure may be structurally unable to show a
  shortage.** `Prod Capacity` is defined as `MAX(Firm+Planned Hours,
  TotalAvailHours)` — by construction this can never come out lower than what
  was already scheduled, so it reflects what was *planned*, not what was
  *physically available* ([DEC-006](../02-decision-registry/decisions/DEC-006.md),
  field D5, ✅ verified against the raw model).
- **A date-formatting bug in Rolling Report likely mislabels every chart that
  uses it as a time axis.** The `ETD` calculated column uses
  `FORMAT([ETD Date], "mm/dd")` — in DAX, `mm` means *minutes*, not month.
  Any visual using this column as an axis label shows the month as `00`
  (RollingReport_WanekMillen_Analysis.md §10.6, ✅ verified against the raw
  DAX).
- **A possible data-quality question sits unresolved in Rolling Report's own
  source query.** The SQL filter is `WeekNum = 2`, but the query's own code
  comment reads `"Firm W3"`. If the comment is right, the report may be
  showing the wrong firm horizon — this hasn't been confirmed either way
  (§8, open question 1).
- **Two of the five reports read directly from manufacturing floor systems,
  bypassing the data warehouse.** DvC - WanekMillenium and Rolling Report -
  Wanek Millen both connect via direct ODBC to iSeries production systems
  (`WFVNPROD`, `MILPROD`, `AFIPROD`) rather than governed EDW tables
  ([`_catalog/Systemic_Patterns_Registry.md`](../01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md),
  PAT-04). Production reporting depends on those operational systems staying
  available and stable — a different kind of fragility than the
  SharePoint/Excel risk seen elsewhere in the estate.
- **Three item-type classification paths exist in Rolling Report, and they
  don't agree with each other.** A SQL-computed classification is discarded
  at load; two separate DAX columns (`Item Check`, `Item Type`) produce
  different bucket counts and different class-code sets. No reconciliation
  exists (§7, §10.4).
- **The 3 schema-level reports in this chapter carry the same unverified-risk
  profile Supply Plan Detail does** — no bug/pattern-level analysis has yet
  been applied to Act+Fcst vs Manufacturing, Production Capacity Vs Forecast,
  or DvC - WanekMillenium. Treat any measure from these three as unverified
  until a full Prompt #1 pass is run.

## 4. Where this is headed (target state)

`DimProductionResource` is **built** in the Fabric gold layer
([`07-fabric-build/docs/model-definitions/dimension-tables/DimProductionResource.md`](../07-fabric-build/docs/model-definitions/dimension-tables/DimProductionResource.md)),
shared with the Supply Planning & Capacity domain. A candidate `FactProduction`
gold fact is identified in the Fabric team's own analysis but **not yet
built** — this domain has no dedicated gold fact of its own yet, unlike
Supply Planning.

## 5. Open questions for Track B

1. Of the five Manufacturing reports (Act+Fcst by WNK & MILL Prod Resource,
   Act+Fcst vs Manufacturing, Production Capacity Vs Forecast, DvC -
   WanekMillenium, Rolling Report), which do you actually open week to week?
2. When Rolling Report shows a rising roll rate for a Wanek or Millenium item,
   what's the threshold that triggers escalation, and what's the first
   concrete step?
3. Is the firm horizon in Rolling Report 2 weeks out or 3 weeks out — does
   `WeekNum = 2` in the underlying query match what you understand the report
   to show?
4. Is the 56-day ETD offset in Act+Fcst vs Manufacturing still the right
   lead-time assumption between Wanek/Millennium shipment and domestic
   finished-goods conversion?
5. Has the iSeries connection for production data ever gone down or shown
   stale numbers in a way that affected a real decision?
