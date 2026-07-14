---
type: Entity
title: Transaction Date
description: Time dimension entity representing individual calendar dates mapped to fiscal calendar attributes for period-based supply chain analysis.
tags: [entities, calendar, fiscal, date, time-intelligence, dimension]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimDate]"
source_system: ERP
status: agent draft
---

## Definition

A **Transaction Date** is a calendar date mapped to the organization's fiscal calendar. It is the primary time axis for supply chain analysis, providing the full fiscal hierarchy — week, month, quarter, half, and year — along with relative period indicators that enable rolling-window queries without hardcoded date ranges.

Transaction date attributes originate from the governed [Fiscal Calendar](/datasets/tables/DimDate.md) dimension. That dataset is the authoritative source for all date and fiscal period attributes used in supply chain analysis.

---

## Grain and Uniqueness

The [Fiscal Calendar](/datasets/tables/DimDate.md) table is keyed on **`TransactionDate`**, one row per distinct calendar date. This means:

- Every date in the supported planning horizon has exactly one row
- Fiscal period attributes (week, month, quarter) are properties of the date, not computed at query time
- Rolling-window filters use the `*Indicator` columns rather than date arithmetic

---

## Fiscal Calendar Hierarchy

The organization uses a fiscal calendar that does not necessarily align with the Gregorian calendar. Weeks run Sunday–Saturday. Months, quarters, and halves are composed of whole fiscal weeks.

| Level | Columns | Format |
| --- | --- | --- |
| Day | `TransactionDate`, `DayOfWeek` | DATE, full weekday name |
| Week | `FiscalWeekNum`, `FWDesc`, `FiscalYearWeekNum` | Within-year number, label, YYYYWW |
| Month | `FiscalMonthNum`, `FMDesc`, `FiscalMonthName`, `FiscalYearMonthNum` | 1–12, label, abbreviation, YYYYMM |
| Quarter | `FiscalQuarterNum`, `FQDesc` | 1–4, label |
| Half | `FiscalHalfNum`, `FHDesc`, `FiscalYearHalfNum` | 1–2, label, YYYYH |
| Year | `FiscalYear`, `FYDesc` | YYYY, label |

Period boundary columns (`FiscalWeekStart`, `FiscalWeekEnd`, `FiscalMonthStart`, `FiscalMonthEnd`, `FiscalYearStart`, `FiscalYearEnd`) provide the DATE values for the start and end of each period enclosing a given date.

---

## Period Indicators

Relative period indicator columns index time relative to today, eliminating hardcoded date thresholds in analysis logic.

| Column | Meaning |
| --- | --- |
| `FiscalDayIndicator` | 0 = today; −N = N days ago; +N = N days ahead |
| `FiscalWeekIndicator` | 0 = current week; −N = N weeks ago; +N = N weeks ahead |
| `FiscalMonthIndicator` | 0 = current month; −N = N months ago; +N = N months ahead |
| `FiscalQuarterIndicator` | 0 = current quarter; −N = N quarters ago; +N = N quarters ahead |
| `FiscalYearIndicator` | 0 = current year; −N = N years ago; +N = N years ahead |

When defining rolling windows (e.g., last 13 weeks, next 3 months), always filter on these indicator columns rather than computing date ranges at query time.

---

## Holiday and Day-Type Classification

The `HolidayIndicator` and `WeekdayWeekend` columns provide day-type attributes for demand pattern segmentation:

- `HolidayIndicator` — "Holiday" or "Non-Holiday"; use with `HolidayName` to identify named holidays
- `WeekdayWeekend` — "Weekday" or "Weekend"; use when demand patterns differ by day type

---

## Related

- [Fiscal Calendar](/datasets/tables/DimDate.md) — Authoritative dataset for all fiscal date and period attributes
- [FILL IN: Link to Forecast Accuracy metric]
- [FILL IN: Link to Days of Supply metric]
- [FILL IN: Link to Demand Forecast dataset]
