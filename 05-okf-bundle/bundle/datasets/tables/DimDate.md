---
type: Dataset
title: Fiscal Calendar
description: Fiscal calendar dimension providing date, week, month, quarter, half, and year attributes for grouping and indexing supply chain facts.
tags: [calendar, fiscal, date, dimension, time-intelligence]
timestamp: 2026-06-29
resource: "[SupplyChain_Gold].[dbo].[DimDate]"
source_system: ERP
refresh_cadence: yearly
data_source: fabric
status: draft
---

## Purpose

Fiscal calendar dimension used to group and filter supply chain facts by fiscal period. Provides a full hierarchy from individual dates up through fiscal weeks, months, quarters, halves, and years. Includes period-relative indicators (current period = 0, past = negative, future = positive) that support rolling-window analysis without hardcoded date logic.

Used as the time dimension in:

- Demand forecasting and forecast accuracy reporting
- Inventory coverage and days-of-supply calculations
- Sales and order trend analysis
- Holiday and weekday/weekend segmentation

---

## Grain

Each row represents a unique **calendar date** (`TransactionDate`).

---

## Schema

| Column | Type | Meaning |
| --- | --- | --- |
| `TransactionDate` | DATE | Primary key — distinct calendar dates |
| `FiscalYear` | INT | Fiscal year number (YYYY) |
| `IntegerDate` | INT | Date as integer in YYYYMMDD format |
| `MapicsDate` | INT | Legacy AS400/MAPICS date format used in ERP source tables |
| `DayOfWeek` | VARCHAR | Full weekday name (Sunday through Saturday) |
| `FiscalWeekNum` | INT | Week number within the fiscal year |
| `FWDesc` | VARCHAR | Fiscal week label (e.g., FW 01) |
| `FiscalYearWeekNum` | INT | Composite fiscal week key (YYYYWW) |
| `FiscalMonthNum` | INT | Fiscal month number (1–12) |
| `FMDesc` | VARCHAR | Fiscal month label (e.g., FM 01) |
| `FiscalMonthName` | VARCHAR | Abbreviated month name (Jan, Feb, Mar, …) |
| `FiscalYearMonthNum` | INT | Composite fiscal month key (YYYYMM) |
| `FiscalMonthYearDesc` | VARCHAR | Readable period label (e.g., Oct 2025) |
| `FiscalQuarterNum` | INT | Fiscal quarter number (1–4) |
| `FQDesc` | VARCHAR | Fiscal quarter label (e.g., FQ 2) |
| `FiscalYearHalfNum` | INT | Composite fiscal half key (YYYYH) |
| `FiscalHalfNum` | INT | Fiscal half number (1–2) |
| `FHDesc` | VARCHAR | Fiscal half label (e.g., FH 1) |
| `FYDesc` | VARCHAR | Fiscal year label (e.g., FY 2025) |
| `FiscalWeekStart` | DATE | Sunday date marking the start of the fiscal week |
| `FiscalWeekEnd` | DATE | Saturday date marking the end of the fiscal week |
| `FiscalMonthStart` | DATE | First Sunday of the fiscal month |
| `FiscalMonthEnd` | DATE | Last Saturday of the fiscal month |
| `FiscalYearStart` | DATE | First Sunday of the fiscal year |
| `FiscalYearEnd` | DATE | Last Saturday of the fiscal year |
| `HolidayIndicator` | VARCHAR | "Holiday" or "Non-Holiday" |
| `HolidayName` | VARCHAR | Holiday name, or blank if not a holiday |
| `WeekdayWeekend` | VARCHAR | "Weekday" or "Weekend" |
| `FiscalDayIndicator` | INT | Relative day index; 0 = today, negative = past, positive = future |
| `FiscalWeekIndicator` | INT | Relative week index; 0 = current week |
| `FiscalMonthIndicator` | INT | Relative month index; 0 = current month |
| `FiscalQuarterIndicator` | INT | Relative quarter index; 0 = current quarter |
| `FiscalYearIndicator` | INT | Relative year index; 0 = current year |
| `FiscalWeeksInMonth` | INT | Count of fiscal weeks in the month |

---

## Related

- [FILL IN: Link to Forecast Accuracy metric]
- [FILL IN: Link to Days of Supply metric]
- [FILL IN: Link to Demand Forecast dataset]
