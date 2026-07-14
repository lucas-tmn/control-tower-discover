# Order Fulfillment & Customer Service

| Field | Value |
|---|---|
| **Confidence level** | Model-only — built from report/data-model analysis and governed OKF definitions, **not yet confirmed with the people who run this process**. Every claim below is sourced; unsourced claims are explicitly flagged as Track B questions rather than stated as fact. |
| **Primary sources** | [Demand_Fulfillment_Analysis.md](../01-evidence/track-a-reports/Demand_Fulfillment_Analysis.md), [On_Time_Pct_By_Customer_Analysis.md](../01-evidence/track-a-reports/On_Time_Pct_By_Customer_Analysis.md), [AFT_SI-SS_PSW_Analysis.md](../01-evidence/track-a-reports/AFT_SI-SS_PSW_Analysis.md); OKF [`glossary/stockout.md`](../05-okf-bundle/bundle/glossary/stockout.md), [`metrics/projected_fulfillment_rate.md`](../05-okf-bundle/bundle/metrics/projected_fulfillment_rate.md); Decision Registry [DEC-005](../02-decision-registry/decisions/DEC-005.md) |

---

## 1. What this is, and why it exists

This domain covers two related but distinct questions: **will we be able to
fulfill demand** (a forward-looking, plan-based question), and **did we
actually ship on time** (a backward-looking, measurement question).

The OKF bundle formalizes the forward-looking side as **Projected Fulfillment
Rate** — what percentage of planned demand the supply plan expects to cover in
a given item-warehouse-week, with anything below 100% signaling a real
constraint ([OKF: Projected Fulfillment Rate](../05-okf-bundle/bundle/metrics/projected_fulfillment_rate.md)).
It also formalizes **stockout** as having two forms: a *current* stockout
(zero available inventory right now) and a *projected* stockout (coverage days
less than lead time — the item will run out before the next replenishment
arrives, even if it's not out today) ([OKF: Stockout](../05-okf-bundle/bundle/glossary/stockout.md)).

## 2. How this runs today

**Fulfillment risk ranking — Demand Fulfillment.** This report asks, for each
item-warehouse by week, how much of total demand (firm orders plus net
forecast) is covered by shippable inventory, and ranks items by how negative
their SI position is — i.e., which items are most "at-risk"
([Demand_Fulfillment_Analysis.md](../01-evidence/track-a-reports/Demand_Fulfillment_Analysis.md) §1).

**Safety-stock-gap-driven expedite/transfer — AFT_SI-SS_PSW.** As covered in
more depth in the
[Inventory Health chapter](Inventory_Health_and_Excess_Management.md), this
report identifies item-warehouses below their safety-stock target with no PO
covering the gap, and is the seed for
[DEC-005](../02-decision-registry/decisions/DEC-005.md) — the
expedite-or-transfer decision.

**Actual delivery performance — On Time % by Customer.** This report measures,
for each customer group and item, how reliably shipments met the original
request date, original promise date, current request date, and current
promise date — at both week-level and day-level
([On_Time_Pct_By_Customer_Analysis.md](../01-evidence/track-a-reports/On_Time_Pct_By_Customer_Analysis.md) §1).

**Not yet confirmed — Track B questions:** who owns the response when Demand
Fulfillment flags an item as at-risk — is it the same person who acts on
AFT_SI-SS_PSW's expedite signal, or a different role — and whether On Time %
is reviewed proactively or only pulled up reactively when a customer
complains.

## 3. Known issues, in business terms

- **The "on-time against promise" number may be measuring the wrong thing.**
  `On Time % - Promised` divides a promised-basis numerator by a
  *requested*-basis total, not a promised-basis total — meaning the percentage
  may not actually represent what it claims to
  ([On_Time_Pct_By_Customer_Analysis.md](../01-evidence/track-a-reports/On_Time_Pct_By_Customer_Analysis.md) §9,
  [`_catalog/Bug_Findings_Log.md`](../01-evidence/track-a-reports/_catalog/Bug_Findings_Log.md) BUG-015).
- **On-time performance for warehouse 335/Ashton is measured differently from
  everywhere else in the same report.** The `WH335OnTime` table uses a
  different lookback window (9 months vs. 55 weeks elsewhere), a different
  customer-attribute source, and different item-class exclusions than the
  main On Time tables — three separate ways this one warehouse's numbers
  aren't comparable to the rest of the report
  ([On_Time_Pct_By_Customer_Analysis.md](../01-evidence/track-a-reports/On_Time_Pct_By_Customer_Analysis.md) §10).
- **Two fiscal calendars coexist in the same report** (`AshleyFiscalCalendar`
  V1 and `z_FiscalCal` V2) — which one is "correct" for a given number depends
  on which table it came from, not something visible on the report itself
  ([On_Time_Pct_By_Customer_Analysis.md](../01-evidence/track-a-reports/On_Time_Pct_By_Customer_Analysis.md) §10).
- **Customer names don't join to any governed customer master.** The only
  customer rollup in the model is a hardcoded SWITCH mapping 16 specific
  account numbers to "DSG" (Dick's Sporting Goods), copy-pasted identically
  into two separate tables — a change to that account list has to be made
  twice, and every other customer is just a raw name-and-account-number
  concatenation with no master-data governance
  ([On_Time_Pct_By_Customer_Analysis.md](../01-evidence/track-a-reports/On_Time_Pct_By_Customer_Analysis.md) §3,
  [`_catalog/Systemic_Patterns_Registry.md`](../01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md), PAT-02).
- **A color-coded urgency indicator on the expedite/transfer report may be
  backwards** — see the [Inventory Health chapter](Inventory_Health_and_Excess_Management.md#3-known-issues-in-business-terms)
  for BUG-012; it's listed there rather than repeated here since it belongs to
  AFT_SI-SS_PSW specifically, which that chapter covers in more depth.

## 4. Where this is headed (target state)

The governed `DimCustomer` is **built**
([`07-fabric-build/docs/model-definitions/dimension-tables/DimCustomer.md`](../07-fabric-build/docs/model-definitions/dimension-tables/DimCustomer.md)) —
this directly addresses the "no governed customer master" issue above, once On
Time % migrates to it instead of its hardcoded DSG SWITCH. The governed
`DimWarehouse` (also built) is the mechanism that would let WH335/Ashton stop
needing a separate table with its own rules — one warehouse dimension, sliced
consistently, replaces the current split.

No gold fact table for on-time/shipment performance exists yet on either side
of this repo — the OKF bundle's Projected Fulfillment Rate metric is defined
conceptually, but there is no built `FactOnTime`-equivalent to calculate it
from today.

## 5. Open questions for Track B

1. When Demand Fulfillment flags an item as at-risk, what actually happens
   next — and is that the same process as AFT_SI-SS_PSW's expedite flag, or
   different?
2. Do you trust the "on-time vs promised" percentage as accurate, or has it
   ever surprised you compared to what you remember happening?
3. Is warehouse 335/Ashton's on-time performance something you review
   separately from the rest of the network, or did you expect it to be
   combined?
4. How do you currently identify which account a shipment belongs to when it's
   not one of the DSG accounts — is the raw name-and-number enough in
   practice?
