# Analysis: Usage Metrics Report (Power BI Built-in)

**Workspace:** Supply Chain Analytics-Premium
**Report name:** Usage Metrics
**Semantic model name:** Usage Metrics Report (`ed85ced5-...`)
**Secondary report:** Report Usage Metrics Report (`b602b206-...` — v2 template, same pattern)
**Date analyzed:** 2026-07-09
**Status:** This is a **Power BI system-level admin report**, not a supply chain operational report.

---

## 1. Supply-Chain Question & Link in the Chain

**This report does not answer any supply-chain question.**

It is Microsoft Power BI's built-in **Usage Metrics** template — the same report that Power BI auto-generates for any workspace to show who viewed which reports, when, from which device/platform, and how fast they loaded. It tracks Power BI adoption and performance, not supply chain operations.

- **Domain:** Power BI Governance / BI Platform Operations
- **Chain link:** None. This report is metadata *about* the supply-chain reporting layer; it observes the readers of supply-chain reports, not the supply chain itself.
- The report filters data to workspace `f0e1bc90-...` ("Supply Chain Analytics-Premium") only, so it shows who in the organization is consuming the supply chain dashboards.

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Decision Type |
|---|---|---|---|
| Which reports are unused → archive or deprecate them | Power BI Admin / Governance Lead | Monthly/Quarterly | Performance/Governance |
| Is report load time acceptable → optimize slow reports | BI Developer / Admin | Ad-hoc (when complaints arise) | Performance/Governance |
| Which users are most active → training/champion identification | BI Admin / Enablement Lead | Monthly | Performance/Governance |
| Is the workspace being adopted → report to leadership | BI Admin / IT Director | Quarterly | Performance/Governance |
| Which distribution method is used (app vs. direct) → adjust sharing strategy | BI Admin | Monthly | Performance/Governance |
| Which pages within a report get used → redesign layout | Report Author / Developer | Ad-hoc | Performance/Governance |

**No operational supply-chain decisions** (expedite, safety stock, transfer, procurement) are made from this report. It is purely about governing the BI tool itself.

---

## 3. Key Metrics / Measures

All 46 measures live in the **Model measures** table. None reference warehouse data — all count rows in the usage audit tables.

### View-Count Measures

| Measure | Business Meaning | Grain | Source Logic |
|---|---|---|---|
| `Report views` | Total report opens (page views, not unique) | Per-event (click) | `COUNTROWS('Report views') + 0` |
| `Report viewers` | Unique users who opened the report | User | `DISTINCTCOUNT('Report views'[UserKey]) + 0` |
| `Report view share` | This report's % of all report views in workspace | Report (ratio) | `DIVIDE(COUNTROWS('Report views'), CALCULATE(COUNTROWS('Report views'), ALL('Report views')), 0)` |
| `Page views` | Total page-section views (drill-down) | Per-event | `COUNTROWS('Report page views') + 0` |
| `Total page views` | Same as Page views (duplicate measure) | Per-event | `COUNTROWS('Report page views')` |
| `Total page users` | Unique users per page section | User | `DISTINCTCOUNT('Report page views'[UserKey])` |
| `Page view share` | This page's % share | Page (ratio) | `DIVIDE(COUNTROWS('Report page views'), CALCULATE(COUNTROWS('Report page views'), ALL('Report pages'[SectionName])), 0)` |
| `Weekly Views` | View count for current (incomplete) week | Week | DATESBETWEEN using Dates[fDoW]..[lDoW] |
| `Weekly Viewers` | Unique viewer count for current week | User-Week | Same logic as Weekly Views |

### Performance Measures (P-xx family)

All load-time percentiles read from `'Report load times'[loadTime]` (int64 seconds).

| Measure | Logic |
|---|---|
| `P-10`, `P-25`, `P-50`, `P-75`, `P-90` | `PERCENTILE.INC('Report load times'[loadTime], N)` |
| `P-10 7d` thru `P-90 7d` | As above but `DATESINPERIOD(..., -7, DAY)` with `ALL(Dates)` filter |
| `P-10 trend` thru `P-90 trend` | Split period: first half vs second half, `DIVIDE(second - first, first)` |
| `Performance trend` | Same as `P-50 trend` but `+ 0 * -1` at end (no-op, result same as P-50 trend) |
| `Typical report opening time` | `[P-50] & " sec"` |
| `Typical report opening interval` | Text: "opens within X and Y seconds" |

### Workspace-Level Measures

| Measure | Logic |
|---|---|
| `Workspace views` | `SUM('Workspace views'[Views]) + 0` |
| `Workspace reports` | `DISTINCTCOUNT('Report views'[ReportId])` |
| `Workspace active reports` | `DISTINCTCOUNT('Workspace views'[ReportId]) + 0` |
| `Workspace inactive reports` | Reports with 0 days usage |
| `Workspace report view %` | This report's share of all workspace views |
| `Workspace active days per report` | Days with at least one view via `DISTINCTCOUNT('Report views'[Date])` |
| `Workspace view trend` | Same split-half logic as View trend but uses Dates table for range |

### Measures That Look Wrong or Suspicious

- **`Performance trend`** has `+ 0 * -1` at the end — mathematically a no-op (multiplying 0 by -1 still equals 0). It produces the exact same value as `P-50 trend`. Likely a copy-paste artifact where someone intended to negate a value but added `0 * -1` instead of wrapping the whole expression in `-1 * (...)`. In practice this measure is **identical** to `P-50 trend`.
- **`Performance trend` vs `P-50 trend`** — they use the exact same calculation (split-half comparison of P-50). They are literal duplicates in logic despite different names. One should be removed.
- **`View trend`** — the `+ 0` at the end is a DAX idiom to force numeric format, but here it's appended outside the `DIVIDE`, which already handles zero. Harmless but unnecessary.
- **`Page views` and `Total page views`** — Two measures in the same table that compute `COUNTROWS('Report page views')`. Identical. One is redundant.
- **`Weekly Views` / `Weekly Viewers`** — Use `BLANK()` outside the current week range. This means this measure returns *blank* for historical weeks, not 0. Visuals will show gaps, which may be mistaken for null or no data.

### Measures Using Hardcoded Constants

- **`Last refresh time display string`** has a hardcoded magic date: `DATE(2019,11,20)` — if the refresh timestamp is before November 20, 2019, it claims "data not imported." This is a relic of the initial Power BI Usage Metrics release and is now meaningless.
- **`Covered time display string`** and **`Covered perf time display string`** are purely cosmetic text measures.

---

## 4. Data Sources & Lineage

| Table | M Expression / Source | Type |
|---|---|---|
| `Report views` | `UsageMetricsDataConnector.GetMetricsData(BaseUrl & "/.../reportviews")` | Built-in Power BI connector |
| `Report rank` | `UsageMetricsDataConnector.GetMetricsData(BaseUrl & "/.../reportrank")` | Built-in Power BI connector |
| `Report page views` | `UsageMetricsDataConnector.GetMetricsData(BaseUrl & "/.../reportpagesectionviews")` | Built-in Power BI connector |
| `Report load times` | `UsageMetricsDataConnector.GetMetricsData(BaseUrl & "/.../reportloads")` | Built-in Power BI connector |
| `Report pages` | `UsageMetricsDataConnector.GetMetricsData(BaseUrl & "/.../reportpagesectionmetadata")` | Built-in Power BI connector |
| `Reports` | `UsageMetricsDataConnector.GetMetricsData(BaseUrl & "/.../reportmetadata")` | Built-in Power BI connector |
| `Refresh Stats` | `DateTime.LocalNow()` (current timestamp at refresh time) | In-session calculation |
| `Dates` | DAX `CALENDAR(TODAY()-31, ...)` | In-model calculation |
| `Users` / `Users_ReportPageView` | DAX `SUMMARIZE('Report views', ...)` | In-model calculation |
| `Workspace views` | DAX `SUMMARIZE('Report views', ..., "Views", [Report views])` | In-model calculation |
| `Workspace reports` | DAX `ADDCOLUMNS(DISTINCT(Reports[ReportGuid]), ...)` | In-model calculation |

**All source data** comes from Microsoft's internal `UsageMetricsDataConnector` — a Power BI system connector that pulls from the Power BI service's internal audit pipeline. It is accessed via implicit `DirectQuery` / default authentication (the workspace context).

**Data-readiness risk:** None of the usual kind — the connector is fully governed by Microsoft. However:
- The data is available only as far back as the Power BI service retains usage logs (typically 30 days for the free tier, though the `Dates` table hardcodes a 31-day window).
- **The Dates table is limited to `TODAY() - 31` days**, meaning this report explicitly does NOT show history beyond 31 days. Any trend analysis stops at 32 days ago.
- There is **no CSV/Excel/SharePoint/ODBC ungoverned source** in this model.

### Second Model ("Report Usage Metrics Model")

The second semantic model at `b602b206-...` is the **v2 template** (Usage Metrics Report V2). It connects to the same built-in Power BI audit database via:
```
Application Name=UserReportUsageMetrics;data source=@DS;initial catalog=@DB
```
with `ImpersonationMode = impersonateCurrentUser` — standard Power BI service connection.

It queries views named `Usage_ReportViews_V2`, `Usage_Reports_V2`, `Usage_ReportViewsRanking_V1`, etc. from the `[Viewers]` schema. The SQL filters look like:
```sql
SELECT [Viewers].[Usage_ReportViews_V2].*
FROM [Viewers].[Usage_ReportViews_V2]
WHERE [Viewers].[Usage_ReportViews_V2].[OwnerTenantGuid] = '{tenant-id}'
  AND ([Viewers].[Usage_ReportViews_V2].[OwnerGroupGuid] = '{workspace-id}'
       OR [Viewers].[Usage_ReportViews_V2].[OwnerUserGuid] = '')
```

**Both models serve the same purpose — the V2 is Microsoft's newer version.** Both are in the same workspace, both read Power BI internal audit tables, neither has any custom supply chain content.

---

## 5. Grain & Snapshot Strategy

| Table | Grain | Detail |
|---|---|---|
| `Report views` | One row per user per report view event | Timestamped to CreationTime (datetime) |
| `Report page views` | One row per user per page section view | Timestamped |
| `Report load times` | One row per report load measurement | Timestamped, includes start/end time |
| `Report rank` | One row per report in org | Daily ranking snapshot |
| `Workspace views` | Aggregated by ReportId-UserKey-Day | Summarized from Report views |
| `Workspace reports` | One row per report, includes trend metric | DAX-calculated |

**Snapshot strategy:** The usage data is **event-level** (every view generates a row). The model then summarizes. The built-in connector only retains ~30 days of event history. The `Dates` table explicitly limits to `TODAY() - 31 days`.

**Need for historical snapshots:** For governance, long-term trend (6–12 months) would be valuable but is not available. Only latest 31 days are present.

---

## 6. Dimensions Used

| Dimension | Source Table | Notes |
|---|---|---|
| **Date** | `Dates` (calculated table) | Last 31 days only; includes `DoW`, `fDoW`, `lDoW` for week boundaries |
| **Report** | `Reports` | From `reportmetadata` API; includes ReportGuid, ReportName, WorkspaceId, IsUsageMetricsReport flag |
| **Report Page** | `Report pages` | From `reportpagesectionmetadata` API; SectionId, SectionName, WorkspaceId |
| **User** | `Users`, `Users_ReportPageView` | Derived via `SUMMARIZE` from Report views. Key fields: UserKey, UserId |
| **Platform** | Inferred via `UserAgent` / `Client` columns | Device, browser, OS parsed from user-agent strings |
| **Workspace** | Implicit via WorkspaceId filter in M queries | Not a standalone dimension — filtered at query level |

**No supply-chain dimensions** (Product, Warehouse, Vendor, Customer, etc.) exist in this model. None are expected.

**Locally re-derived attributes:** None applicable — every column is a direct passthrough from the Power BI audit API.

---

## 7. Duplication / Consolidation Signals

1. **Two nearly identical reports** exist in the workspace: "Usage Metrics" (v1 template) and "Report Usage Metrics Report" (v2 template). They serve the same purpose. One should be retired. The fact that both are published in the same workspace suggests either:
   - A V1 → V2 migration was started but not completed (old report not cleaned up)
   - Two different admins each enabled usage metrics independently

2. **Duplicate measures in "Usage Metrics"** (Model measures table):
   - `Page views` = `COUNTROWS('Report page views') + 0` and `Total page views` = `COUNTROWS('Report page views')` — identical
   - `Performance trend` = `P-50 trend` with a harmless `+ 0 * -1` suffix — effectively identical

3. **Multiple LocalDateTable instances** (11 total, 8 with `Calendar(...)` DAX using MIN/MAX) — each is an auto-generated date table linked to a different datetime column. This is standard Power BI behavior when Import tables have datetime columns and auto date/time is enabled. Consolidation into a single shared date dimension is possible but low-value.

---

## 8. Open Questions

1. **Why are both V1 and V2 usage reports published?** Was V2 left behind after an upgrade, or are different teams actually using different versions?
2. **Who is the intended consumer?** The workspace is named "Supply Chain Analytics-Premium" — are supply chain report authors/developers the audience (to monitor their own report performance), or is this for a centralized BI team?
3. **Is anyone actually using this report?** The Usage Metrics report shows its own usage. This creates a circular reference problem (to see who views it, you open it, registering yourself as a viewer).
4. **Has the 31-day window limitation been recognized?** If long-term report adoption trends are wanted, the `Dates` table (currently hardcoded to `TODAY()-31`) would need to be extended.
5. **The v2 model ("Report Usage Metrics Model") uses `defaultMode: "directQuery"`** whereas v1 uses import mode. Is the v2 DirectQuery intentional for near-real-time usage tracking, or was it the default?

---

## 9. Business Assumptions / Magic Numbers

| Constant/Shift | Location | What it does | Documented? |
|---|---|---|---|
| `DATE(2019,11,20)` | `Last refresh time display string` measure | If `Last Refresh` < 2019-11-20, claims "data not imported" | No. Clearly stale — this was the launch date of the original Usage Metrics feature |
| `TODAY() - 31` | `Dates` table partition DAX | Limits date range to last 31 days | No. Assumes 31 days of retention is sufficient for all use cases |
| `+ 0` suffix on ~20 measures | Multiple measures in Model measures | Forces numeric format (DAX idiom) | Standard DAX pattern, not a business assumption |
| `+ 0 * -1` | `Performance trend` measure | Mathematically no-op. Appears intended to negate a value but 0*-1=0 | No. Likely a bug or incomplete refactor |
| `DIVIDE(..., 0)` third arg = 0 | `Report view share` | Returns 0 instead of BLANK on division by zero | Standard DAX, no business assumption |
| `INT(numberOfDays/2) - 1` | All `trend` measures (View trend, P-XX trend, Performance trend) | Splits the available date range into before/after halves for trend comparison. If date range has odd days, the middle 1-2 days are excluded | No. The `-1` exclusion of a midpoint day is undocumented. For a 31-day window: `INT(31/2)-1 = 14` — first 14 days vs last 14 days, with days 15-17 excluded |
| `DoW = 1` (Monday start) / `DoW = 7` (Sunday end) | `Weekly Views`, `Weekly Viewers` | Assumes a Mon-Sun week definition | No. If the org uses a different week definition (Sun-Sat, Wed-Tue), these measures are misaligned |

**Key finding: No dollar-value business impact is calculated.** This report does not estimate cost savings, revenue impact, or ROI. It tracks usage counts and load times only.

---

## 10. Comparability / Consistency

- **Date range is non-extensible.** The `Dates` table is hardcoded to 31 days back from `TODAY()`. A report opened on two different days will naturally have a different lookback window. Comparing "last 31 days" today vs. last month will have partial overlap but no gap alignment.
- **Week measures (`Weekly Views`, `Weekly Viewers`) return `BLANK()` outside the current partial week.** This means they are not comparable across time periods — you see a value for the current (incomplete) week and blank for all prior complete weeks. A visual trend line would have gaps.
- **V1 vs V2 coexistence.** The V1 model uses import mode (full data pulled at refresh); the V2 model uses DirectQuery (live queries). If someone compares numbers between the two, they will differ by the refresh latency (V1 is stale until the next refresh; V2 always reflects latest available audit data).
- **No "before/after" structural splits** in the model. The data either exists in the 31-day window or it doesn't. No branching logic changes metric meaning over time.
- **The `View trend` measure uses `ALL('Dates')` but references `'Report views'[Date]` directly for its period boundaries.** This means the trend calculation is defined by the actual data's date range, not the calendar. If no views happened on a weekend, the trend period shifts. Two reports with different view patterns get different "trend" denominators — they are not directly comparable.

---

## Closing — Interview Seeds

1. **"This Usage Metrics report tracks report views and load times in this workspace. Who is the primary audience — do the supply chain planners see this, or is it just the BI team managing the Power BI environment?"** (Confirm whether this is a governance tool or intended as a self-service adoption feed.)

2. **"Both a V1 and a V2 Usage Metrics report are published here. The V1 uses imports (scheduled refresh) and V2 uses DirectQuery (live). Are you actively migrating between them, or is one orphaned?"** (Clarify duplication — if V1 is dead, remove it; if migration is in progress, pick a completion date.)

3. **"The date range is limited to rolling 31 days. Have you ever needed to see quarterly or yearly trends, or do you always look at the last month?"** (Validate whether the `TODAY()-31` hardcode is a genuine constraint or just a default nobody changed.)

4. **"Do you or your team ever compare numbers between this report and any external source — like Power BI admin portal audit logs, or a separate usage dashboard? If so, do they match?"** (Check for internal consistency governance — if the V1 and V2 give different numbers for the same metric, which one is trusted?)
