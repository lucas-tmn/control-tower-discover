# Prompt #1 — Data Discovery (Read the Model) — Updated

*Original 8 questions kept almost word-for-word. Additions marked NEW.*

1. What supply-chain question does this report exist to answer, and which link in the
   chain (demand / forecast / supply / inventory / production / receipts / on-time)
   does it serve?

2. Decisions supported: List the concrete operational decisions a user would make from
   this report (e.g. "expedite vs wait", "adjust safety stock"). For each: who likely
   makes it (persona: executive / WBR-leadership / planner / analyst), how often, and
   **[NEW] what type of decision it is — Operational (handle goods: expedite/transfer),
   Performance/Governance (manage the planning process: coach planners, pick horizon),
   or Financial-Justification (investment case, $-impact)**.

3. Key metrics / measures. List the important DAX measures with, for each: what it
   means in plain business terms, its grain (item / item-warehouse /
   customer-item-warehouse; day / week / month), and the exact source column/logic.
   Flag any measure whose **name** suggests it's hardcoded or duplicated (e.g.
   per-warehouse "WH## SI" style), **and separately, [NEW] flag any measure whose
   underlying value or logic looks wrong or suspicious even if its name looks normal**
   (e.g. a constant that should be a calculation, a value that doesn't move when the
   underlying data does).

4. Data sources & lineage. List the source tables/objects (EDW, dataflows, SQL,
   SharePoint/Excel/iSeries). Flag any ungoverned sources (manual Excel, SharePoint,
   direct ODBC) as a data-readiness risk.

5. Grain & snapshot strategy. State the primary grain, and whether it needs historical
   snapshots (accuracy/trend) or only latest (operational).

6. Dimensions used. Which conformed dimensions does it slice by (Product, Date,
   Warehouse, Vendor, Customer, ProductionResource), and note any locally re-derived
   attributes (lifecycle, kit flag, fiscal indicators, warehouse normalization) that
   look like they drift from a standard.

7. Duplication / consolidation signals. Anything here that looks identical or
   near-identical to a common pattern — repeated measures, copy-pasted queries,
   re-derived columns — that could collapse into a governed shared definition.

8. Open questions. What you can't determine from the model alone and would need to
   confirm with a business user (e.g. "who actually uses this", "is this still live").

9. **[NEW] Business assumptions / magic numbers.** List every unexplained constant,
   multiplier, date-shift, or offset in the model's DAX or Power Query logic —
   regardless of whether the surrounding calculation otherwise looks correct. For each:
   where it appears, what it seems to do, and whether anything in the model documents
   or explains it. Include explicitly: does this report calculate a dollar-value
   business impact (e.g. accuracy improvement → net sales)? If so, state the formula
   and flag every unverified assumption it rests on — these numbers are high-risk
   because they tend to feed executive business cases.

10. **[NEW] Comparability / consistency.** Note any case where the same-named metric is
    calculated differently across tables, time periods, or grains within this same
    model (e.g. a naive-lag benchmark using 2 months in one place and 3 months in
    another, making the two not actually comparable). Note any structural split in the
    model itself (e.g. "before/after a given date" logic branches) that changes what a
    metric means depending on the filter applied.

**[NEW] Closing — Interview seeds:** Based on everything above, draft 2–4 direct
questions for a follow-up interview with the actual business user, targeting exactly
what this analysis could not confirm from the model alone (the trigger for a decision,
the concrete next action taken, escalation path, tools used outside Power BI, and
whether the person trusts the numbers above). Phrase each as a question ready to ask,
not a restatement of an open question.

Keep it factual and grounded in what's actually in the model — do not invent measures
or sources. Where something is ambiguous, say so rather than guessing.
