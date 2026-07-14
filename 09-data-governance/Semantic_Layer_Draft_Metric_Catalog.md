# Semantic / KPI Layer — Draft Metric Catalog (Starter)

| Field | Value |
|---|---|
| **Purpose** | First draft of the metric side of Cherry's Data Catalog (see `Supply_Chain_Data_Governance_Proposal_EN.md` §4.3) — turns the Decision Registry and the knowledge library's measure-archetype analysis into a starter list of *governed metrics needed*, not just documentation to read. |
| **Status** | Draft — unreviewed. Meant as a seed for Cherry to correct, not a finished catalog. |
| **Sources** | `00-foundation/`'s merged `02-group-analysis/measure-archetypes.md` (879 measures → 253 signatures → 10 archetypes); `02-decision-registry/` (11 DEC entries); `01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md`. |

---

## 1. Why this exists

The Decision Registry answers "what decision does this metric serve." The
measure-archetype analysis answers "how many ways is this metric currently
computed, and where." Neither on its own is a governance artifact — put
together, they say **which metrics need one governed definition first**,
ranked by how many decisions and reports they already touch. That's the
starting point for Cherry's Data Catalog + Business Glossary, and for the
Dashboard Creation Policy / KPI Governance Charter she's flagged as
not-yet-drafted (proposal §4.3).

## 2. Candidate governed metrics, ranked by consolidation value

| # | Archetype | Canonical metric (proposed) | Currently duplicated as | Decisions that depend on it | Priority |
|---|---|---|---|---|---|
| 8 | Hardcoded warehouse slice | `[SI] := SUM(fact_supply_plan[ShippableInventory])`, sliced by `DimWarehouse` | ~40 measures in Supply Plan Detail (`WH1 SI`, `WH5 SI`, ... `WH## SI-SS`, `WH## Wk4 SI`) + repeated in Inv Management as `Whse # - SI` | [DEC-004](../02-decision-registry/decisions/DEC-004.md), [DEC-005](../02-decision-registry/decisions/DEC-005.md) | **Highest** — largest single cleanup (~40 measures → 1), and it's the same warehouse dimension the DimWarehouse cross-check below already touched |
| 7 | Forecast-accuracy family | One `fact_forecast_accuracy`-based set (`Bias %`, `wMAPE`, `Mean ABS Dev`...), parameterized by grain + lag | Near-duplicated across Forecast Accuracy (ItWh), Forecast Accuracy (Cust_ItWh), and embedded again in Demand Review / Product Review (NEW) / Weekly Trend Analysis | [DEC-001](../02-decision-registry/decisions/DEC-001.md), [DEC-002](../02-decision-registry/decisions/DEC-002.md), [DEC-008](../02-decision-registry/decisions/DEC-008.md), [DEC-009](../02-decision-registry/decisions/DEC-009.md) | **High** — second-largest cluster, and it already has a confirmed bug riding on top of it (two "identical" Forecast Accuracy reports use different bias thresholds, 8% vs 10% — see Bug Findings Log) |
| 3 | Ratio / percentage | Generic `DIVIDE(measure, measure)` pattern | 13 models, incl. the two roll-rate measures in Rolling Report (`%Rolled` vs `%Roll Average` — same formula, different grain, not interchangeable, no naming distinction) | (none registered yet — candidate from Rolling Report analysis §2) | Medium — mostly needs a naming/grain convention, not full consolidation |
| 9 | Cost / cube weighting | One `SUMX(DimProduct, DimProduct[factor] * [Qty])` helper | ActFcst $, OrdFcst $, OH $, On Hand Cubes, SS Cubes, Excess FG $ — across GF Act+Fcst, Safety Stock Analysis, Supply Plan Detail, Inventory Transactions | [DEC-010](../02-decision-registry/decisions/DEC-010.md) (the only $-value decision candidate that has real dollar measures behind it) | Medium — fewer members, but this is the archetype tied to the one financial-justification decision currently registered |

## 3. Cross-check finding worth folding in: DimWarehouse has already moved

While comparing the knowledge library's dimension-table designs against the
actual Fabric build (2026-07-13), 5 of 6 conformed dimensions are byte-identical
— but **`DimWarehouse` has already diverged**: the live Fabric build now maps
warehouse codes `16` (Statesville) and `70` (Etna), which the original design
snapshot still excluded. This means the warehouse-normalization work archetype
#8 depends on ("Depends on warehouse-normalization reconciliation," per the
archetype note above) **may already be further along than this catalog
assumes** — worth a direct check with Cherry/Robert on current `DimWarehouse`
coverage before scoping the archetype #8 cleanup.

## 4. Suggested first ask of Cherry

Not "review this whole catalog" — narrower: **confirm or correct the
priority order in §2**, and say which of these 4 candidate metrics she'd
want as the first governed definition built in the semantic model. Archetype
#8 (warehouse SI) is the recommendation, since it's the largest cleanup, ties
directly to 2 registered decisions, and the underlying dimension work may
already be partway done.

## 5. Not covered in this draft (deliberately out of scope for a first pass)

- The other 6 archetypes (additive base, filtered sum, error/variance,
  relative-period shift, period averaging, conditional-format/label) — lower
  duplication value or no registered decision riding on them yet.
- The full 253-signature list — lives in the knowledge library's
  `measure_sigs.csv`, not reproduced here.
- Formal Business Glossary entries (definitions, calculation logic, sample
  values) for each metric — this draft only identifies *which* metrics need
  one; writing the governed definition itself is the next step, and should
  happen with whoever owns the archetype's source report.
