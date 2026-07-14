# PROVENANCE

| Field | Value |
|---|---|
| **What this is** | A vendored (copied-in) snapshot of the **official Microsoft Fabric workspace repo** for the enterprise supply chain data platform — `data-fabric-enterprise-supply-chain-docs-report-migration-documentation`. This is git-synced infrastructure-as-code (Lakehouses, Warehouses, Dataflows, Notebooks, Data Pipelines, Semantic Models, Reports), not a knowledge document. |
| **Vendored on** | 2026-07-10 |
| **Vendored from** | ZIP export provided by the Discovery Lead (file: `data-fabric-enterprise-supply-chain-docs-report-migration-documentation.zip`) |
| **Repo ownership** | Official / governed — `.github/CODEOWNERS` names `@afi-internal/enterprise-data-warehouse-approvers` as code owner. This is **not** a personal knowledge repo (contrast with `05-okf-bundle/`, which is Robert's personal OKF bundle). |
| **Role in this repo** | The **build/execution layer** — concrete, engineering-ready realization of the TO-BE concepts in `05-okf-bundle/`: real gold-layer table definitions with working ETL SQL, a real `SupplyChain_Gold.SemanticModel`, an early-stage `Forecast Accuracy Gold.Report`, and a next-generation design (`The future/`) including a Control Tower semantic model and alerting (Reflex). |

## What was excluded, and why

`docs/report-migration-docs/01-report-summaries/` was **not** copied into this repo.
Its 25 report-summary files are the same underlying source population already present
in `knowledge-library-archive/` (used throughout `01-evidence/track-a-reports/`) —
copying them again would duplicate content without adding information. Everything
else in the source ZIP was vendored intact, including:

- `docs/report-migration-docs/02-group-analysis/` — the tool-parsed, quantitative
  cross-model catalog (879 measures → 253 signatures, conformed dimensions, fact
  grains, measure archetypes, source governance). This is genuinely new and
  complements (not duplicates) `01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md`.
- `docs/model-definitions/` — concrete dimension/fact table definitions with real
  ETL SQL, ownership, and dates. These resolve many `[FILL IN]` gaps logged in
  `06-bridge/gap-fill-candidates.md`.
- All actual Fabric items: Lakehouses, Warehouses (bronze/silver/gold schemas),
  Dataflows, Notebooks, Data Pipelines, Semantic Models, and the
  `Forecast Accuracy Gold.Report`.

## Ground rules for this directory

1. **Do not edit content here directly.** This is the data-engineering team's
   governed repo, kept intact for diffing against / re-syncing with the upstream
   Fabric workspace. The only file in this directory that is ours is this
   `PROVENANCE.md`.
2. **Corrections, discrepancies, or questions** arising from cross-referencing this
   repo against our own evidence go in `../06-bridge/` — never patched here
   silently. See `WAREHOUSE_335_RECONCILIATION.md` in this directory for a live
   example: a real conflict was found between our own analysis and this repo's
   `DimWarehouse.md`, and it is documented rather than silently resolved.
3. **Re-syncing:** replace this directory's contents wholesale from a fresh
   upstream export, keep this file, update "Vendored on/from" above, and re-check
   `06-bridge/` mappings for drift — same protocol as `05-okf-bundle/`.
4. **This repo requires approval from `@afi-internal/enterprise-data-warehouse-approvers`
   for any real changes** — if anything here needs to change (not just be vendored),
   that has to happen upstream, through that team, not in this discovery repo.

## Relationship to the other 3 layers

| Layer | Nature | This repo's relationship to it |
|---|---|---|
| `01-evidence/` (AS-IS) | Forensic — what the current 25-report estate actually does | This repo's `02-group-analysis/` independently confirms several AS-IS findings (e.g. PAT-08's warehouse-slice measure pattern) with hard numbers |
| `05-okf-bundle/` (TO-BE, conceptual) | Robert's personal governed knowledge bundle — target definitions, glossary, playbooks | This repo is the **concrete engineering realization** of that same target state — real schemas instead of narrative descriptions |
| `06-bridge/` | Maps AS-IS ↔ TO-BE | Several `[FILL IN]` gaps logged there are now answered by files in this directory — see `06-bridge/gap-fill-candidates.md` |
