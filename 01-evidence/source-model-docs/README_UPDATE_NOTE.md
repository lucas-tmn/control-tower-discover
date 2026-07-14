# Update — 2026-07-13 (second pass)

`Rolling_Report_Wanek_Millen.md` in this folder is now **superseded** by a full
Prompt #1 business analysis:

→ `01-evidence/track-a-reports/RollingReport_WanekMillen_Analysis.md`
→ `01-evidence/track-a-reports/bim/RollingReport_WanekMillen.bim`

Keep the schema doc here as raw reference (it's still accurate on tables/DAX),
but treat the track-a-reports version as the primary, current source for this
report going forward.

## Manufacturing & Capacity (Group 4) — coverage tracker

| # | Report | Status |
|---|---|---|
| 1 | Act+Fcst by WNK & MILL Prod Resource | ✅ Full business analysis |
| 2 | Act+Fcst vs Manufacturing | 🟡 Schema-level only |
| 3 | Production Capacity Vs Forecast | 🟡 Schema-level only |
| 4 | DvC - WanekMillenium | 🟡 Schema-level only (🔴 reads iSeries ODBC directly) |
| 5 | Rolling Report - Wanek Millen | ✅ Full business analysis (added 2026-07-13) |

**2 of 5 now at full business-analysis depth.** 3 remain schema-only:
Act+Fcst vs Manufacturing, Production Capacity Vs Forecast, and DvC-WanekMillenium
— the last of which shares the same iSeries-direct-connection risk profile as
Rolling Report (worth prioritizing next if/when analysis resumes, since it's
now the only Group-4 report still fully undocumented at the business level
*and* on an ungoverned source path).
