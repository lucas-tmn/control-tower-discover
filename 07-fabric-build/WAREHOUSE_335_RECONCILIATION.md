# Warehouse 335 — Reconciliation Note

| Field | Value |
|---|---|
| Status | **Provisionally resolved — pending Robert's confirmation** |
| Created | 2026-07-10 |
| Affects | `Systemic_Patterns_Registry.md` (PAT-08), `Artifact_First_Extraction_Pass.md` (§3), `DEC-004.md` (F4), `README.md` (open risk section) |

## The conflict

Two of our own documents reached different conclusions about what warehouse `335` is:

| Source | Conclusion | Basis |
|---|---|---|
| Inv Management live-workspace re-run (2026-07-07) | "335 is Ashley's **main distribution center**" | Inference from model behavior: the entire core Inv Management model (`Inventory`, `W2 SS Change`, `Inv Age`) is scoped to warehouse 335, with the 7-warehouse `SI at US Warehouse` table feeding *into* it |
| `07-fabric-build/docs/model-definitions/dimension-tables/DimWarehouse.md` (dated 2026-06-18, authored by Robert Font Perez) | 335 belongs to **`WarehouseGroup = 'ASH'` (Ashton)** — a group *separate from* `AFI` (which contains the core warehouses 1, 15, 16, 17, 28, 42, 5, 70, ECR) | Concrete ETL SQL: `CASE WHEN '335' THEN 'ASH'`, `PlanningWarehouse = '335-ASH'`, distinct from every `AFI`-grouped code |

These are not obviously the same claim. "Main DC for the network" and "a distinct
facility called Ashton, grouped separately from the core AFI warehouses" could both
be true (Ashton could be the primary hub *and* be organizationally/physically
distinct from the AFI group) — or the original "main DC" framing could simply have
been an overreach from limited evidence (Inv Management's core model being scoped to
335 doesn't necessarily mean 335 is "the" main DC network-wide; it may just mean
Inv Management's excess/consolidation process happens to center on Ashton
specifically, for reasons the model itself doesn't state).

## Which has stronger evidence

The DimWarehouse.md conclusion is better supported for now:
- It has **concrete, executable ETL SQL** with an explicit warehouse-to-group mapping
  for all ~50 known warehouse codes, not just an inference from one model's scope.
- It has an **owner and date** (Robert Font Perez, 2026-06-18) — a named, attributable
  source rather than a pattern inferred from DAX/SQL behavior.
- It is **part of a governed table definition** intended to become the single
  conformed `DimWarehouse` for the whole estate, which is a stronger claim to
  authority than any one legacy report's internal scoping choice.

The Inv Management conclusion is not wrong, but it was an **inference about intent**
("why would this model be scoped to 335 unless 335 is the main hub") rather than a
direct statement of fact. That inference may still be correct — Ashton could well be
the primary hub *within* the ASH group, or even network-wide — but the DimWarehouse
doc doesn't confirm or deny that; it only confirms 335's *group membership*, not its
*relative importance*.

## Provisional resolution

Going forward, until Robert confirms otherwise, this repo will describe warehouse
`335` as: **"Ashton — a distinct warehouse/facility, grouped separately from the
core AFI warehouses (`WarehouseGroup = 'ASH'`). Inv Management's core model happens
to be scoped to it, but this repo does not yet have confirmed evidence that 335 is
'the' primary distribution center for the network as a whole."** The stronger,
unqualified "main DC" framing from the 2026-07-07 update is retracted as overreach
and replaced with this more precise, appropriately hedged version.

This does **not** change the underlying comparability risk already flagged in PAT-08 —
if anything it sharpens it: 335/Ashton is confirmed to be a real, distinct warehouse
(not a data artifact or staging code), so any report that inconsistently includes or
excludes it from "total" figures is inconsistently scoping a real facility, which is
exactly the kind of drift a conformed `DimWarehouse` is meant to eliminate.

## Question to send Robert (reusable, short)

> "Confirming on warehouse 335 (Ashton) — is it meant to be understood as Ashley's
> primary/main distribution center, or as one facility among several under its own
> `ASH` group? Two of our documents currently frame it differently and we want to
> use your definition as the source of truth."

## Where this propagates

- `01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md` — PAT-08 note updated
- `01-evidence/track-a-reports/_catalog/Artifact_First_Extraction_Pass.md` — §3 updated
- `02-decision-registry/decisions/DEC-004.md` — F4 open questions updated
- `README.md` — open-risk section updated
