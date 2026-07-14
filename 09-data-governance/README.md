# 09-data-governance

## What this is

A discussion-draft proposal to move Supply Chain from unrestricted, self-service
EDW access to a governed, request-based data model — combining a real,
numbers-based AS-IS audit with Cherry Bui's TO-BE governance framework.

## Files

| File | What it is |
|---|---|
| `Supply_Chain_Data_Governance_Proposal_EN.md` | Full proposal (English) — AS-IS diagnosis, TO-BE framework, phased roadmap with expected outcomes per phase |
| `Supply_Chain_Data_Governance_Proposal_VN.md` | Same proposal, Vietnamese — content identical, system/technical terms (AAD group names, table names, layer names) kept in English in both versions |
| `Semantic_Layer_Draft_Metric_Catalog.md` | Draft starter list of governed metrics (added 2026-07-13) — turns the measure-archetype analysis + Decision Registry into a ranked "which metric to govern first" list, seeding the Data Catalog Cherry's framework calls for |
| `source-evidence/20260210_table_dictionary_cherry_bui_1.xlsx` | Vendored copy of the raw `DW_Developer.TableDictionary` export (6,489 EDW objects, 433 schemas) used as the quantitative basis for the AS-IS section |
| `source-evidence/Cherry-recommend.docx` | Vendored copy of Cherry Bui's original governance recommendation (Data Catalog, Change Proposal Process, Table Registry, AAD Group access model, onboarding checklist) — the proposal's TO-BE section is a direct restatement of this, marked `[Cherry]` throughout |

## Status

**Draft — not yet reviewed with Cherry.** Both proposal documents list open questions
(§7) that need her and the data team's confirmation before this goes to Devon —
notably whether Bronze→Silver→Gold is used consistently today, who currently has
direct EDW access, whether the future semantic model is centralized or per-domain,
and whether a cutover deadline already exists.

## How this connects to the rest of the repo

This section stands somewhat apart from `01-evidence/` through `08-business-handbook/`
(which are about the *reporting* estate specifically) — it's about the *data platform
access model* underneath that estate. The AS-IS diagnosis here independently confirms
findings already in `01-evidence/track-a-reports/_catalog/Systemic_Patterns_Registry.md`
and `06-bridge/source-migration-map.md`: the analyzed reports (31 as of 2026-07-13) that
were found to bypass Bronze/Silver/Gold in the reporting analysis are the concrete
evidence this proposal's AS-IS section cites — including 3 distinct ungoverned-source
patterns now identified (SharePoint/Excel, iSeries ODBC direct, and a single ungoverned
EDW view with no dataflow layer), itemized in §3.2.1 of the English proposal.
