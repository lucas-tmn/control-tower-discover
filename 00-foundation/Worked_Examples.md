# Worked Examples

**Purpose:** validate the operating model — and directly test hypothesis
H1 (is Decision Context a single object, or a container of atoms?) —
against real, traceable evidence rather than in the abstract.

Each example below decomposes one report-driven decision into the same
seven atoms, so H1 can be tested by asking: *is this one Decision Context,
or seven linked objects?*

---

## Example 1 — Weekly Trend Analysis (Demand)

**Situation it surfaces:** three signals — Invoiced (actual fulfillment),
Written (order entry, a leading indicator), and Current Request (forward
customer demand) — tracked against a rolling 26-week forecast.

**Decision it drives:**
- Written or Requested outpaces Forecast → prepare for a demand increase.
- Invoiced lags Written/Requested → a backlog is forming; escalate for
  supply chain intervention.
- Forecast substantially exceeds all three actual signals → reduce the
  forecast to match market reality.

| Atom | Value |
|---|---|
| Trigger | Weekly variance between Invoiced/Written/Requested and Forecast crosses a threshold |
| Metric(s) | `90Day Error`, `90Day Error %`, `dfoGap`, `dfoConsumption` |
| Rule | The 3-way comparison logic above — demand-planner-authored, not documented elsewhere |
| Action | Adjust forecast, or escalate to supply planning |
| Persona | Demand Planner |
| Owner | Demand Planning team |
| Data source | AFI wholesale sales history + demand forecast snapshots (warehouse-sourced) |

---

## Example 2 — Inventory Health

> **⚠ Caveat added 2026-07-07:** This example's decomposition below is based on the
> *business description* in the Report Catalog (the 5-bucket classification), not on
> a model actually opened and confirmed. Two Prompt #1 runs since this example was
> written have each landed on a *different* model under a similar name — `Demo_Inventory
> Health` (32 tables, partly hardcoded) and `InventoryHealth_AI` (7 tables, 100%
> hardcoded/frozen demo data, AI narrative disabled) — neither of which is confirmed to
> be the production report described here. Treat this example as **unverified against
> a real model** until the actual backing model is located and confirmed. `Inv
> Management` has since replaced Inventory Health as the Supply & Inventory cluster's
> Tier 2 representative for that reason.


**Situation it surfaces:** weekly item-warehouse inventory is classified
into five health buckets — Below Max, Over Target, Excess, High Excess, and
TIB ("Throw in the Bay") — based on days of supply relative to safety stock
(SS) multiples (≤1.5x SS, up to 3x SS, 3x–365 days of demand, 365–712 days,
beyond that).

**Decision it drives:**
- Below Max → replenish, possibly expedite.
- Over Target → hold, monitor.
- Excess / High Excess / TIB → halt replenishment; consider liquidation or
  promotional push, in escalating order of urgency.

| Atom | Value |
|---|---|
| Trigger | Weekly bucket classification crosses a safety-stock-multiple or days-of-supply threshold |
| Metric(s) | `Total On Hand Qty/$`, `Total Safety Stock $`, `Total Below Max $`, `Total Excess $`, `Total High Excess $`, ATP in-stock rate |
| Rule | Five-bucket threshold logic above |
| Action | Replenish / hold / liquidate or promote, depending on bucket |
| Persona | Inventory Planner / Buyer |
| Owner | Inventory Management team |
| Data source | Warehouse on-hand inventory + demand forecast + safety stock targets |

---

## What these two examples tell us about H1

Both decisions decompose cleanly into the same seven atoms, and in both
cases the **rule** is planner-authored tribal knowledge that exists nowhere
in written documentation today — this is itself a discovery finding, not
just a modeling exercise: the report shows the *numbers*, but the
*decision rule* that turns those numbers into action lives only in the
report's original author or the planner's head.

This is the concrete test case for H1: is "Weekly Trend Analysis demand
adjustment" one Decision Context holding all seven rows, or is the Decision
Context just trigger+rule+action, with metric/persona/owner as separate
linked objects it references? **Recommend resolving H1 against these two
examples with the team before Sprint 2 begins**, rather than in the
abstract.
