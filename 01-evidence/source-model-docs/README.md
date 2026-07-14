# Source Model Documentation — Manufacturing & Capacity (Group 4)

These 4 files are **technical schema documentation** (tables, DAX measures,
relationships, source system) produced by Robert's team as part of the
`data-fabric-enterprise-supply-chain` report-migration work — not business
analysis in the Prompt #1 sense (no bugs, patterns, decisions, or "Open
questions for Track B").

They cover the 4 of 5 Manufacturing & Capacity (Group 4) reports that did not
yet have any documentation in this repo:

| File | Report |
|---|---|
| `Act_Fcst_vs_Manufacturing.md` | Act+Fcst vs Manufacturing |
| `Production_Capacity_Vs_Forecast.md` | Production Capacity Vs Forecast |
| `DvC_WanekMillenium.md` | DvC - WanekMillenium (reads iSeries ODBC directly — 🔴) |
| `Rolling_Report_Wanek_Millen.md` | Rolling Report - Wanek Millen (reads iSeries ODBC directly — 🔴) |

The 5th report in this group, **Act+Fcst by WNK & MILL Prod Resource**, already
has a full Prompt #1 business analysis in `track-a-reports/` — not duplicated here.

**Status:** schema-level only. Treat as reference material for whoever writes
the full business analysis next — it pre-populates the technical fields
(tables, measures, relationships, source) so that analysis can focus on
business context, bugs, and decisions rather than re-deriving the schema.

*Added 2026-07-13, from `Eagle_Eye_Knowledge_Library/02_Source_Truth_Reporting_Estate/01-report-summaries/`.*
