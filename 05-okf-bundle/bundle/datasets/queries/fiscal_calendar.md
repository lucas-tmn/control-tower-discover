---
type: Query
title: Fiscal Calendar Query
description: EDW SQL query that produces the fiscal calendar shape.
tags: [date, fiscal-calendar, calendar, time, dimension, query]
timestamp: 2026-07-06
resource: "[Enterprise_DW].[DimDate_NonRetail]"
source_system: ERP
refresh_cadence: yearly
data_source: ashley_edw
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

---

## Base Query

Use this query to produce the Fiscal Calendar shape while the gold `DimDate` table is unavailable.

```sql
SELECT [DateID] AS [TransactionDate]
      ,[DateKey] AS [IntegerDate]
      ,[MapicsDate] AS [MapicsDate]
	  ,[CalendarDayOfWeekName] AS [DayOfWeek]
	  ,[FiscalWeek] AS [FiscalWeekNum]
	  ,CONCAT('FW ', RIGHT(CONCAT('00',[FiscalWeek]),2)) AS [FWDesc]
	  ,[FiscalWeekYear] AS [FiscalYearWeekNum]
	  ,[FiscalMonth] AS [FiscalMonthNum]
	  ,CONCAT('FM ', RIGHT(CONCAT('00',[FiscalMonth]),2)) AS [FMDesc]
	  ,FORMAT(CONVERT(DATE,CONCAT([FiscalMonthYear],'01')), 'MMM') AS [FiscalMonthName]
	  ,[FiscalMonthYear] AS [FiscalYearMonthNum]
	  ,FORMAT(CONVERT(DATE,CONCAT([FiscalMonthYear],'01')), 'MMM yyyy') AS [FiscalMonthYearDesc]
	  --,CONVERT(DATE,CONCAT([FiscalMonthYear],'01')) AS [Fiscal Month (calendar start)]
	  ,[FiscalQuarter] AS [FiscalQuarterNum]
	  ,CONCAT('FQ ', RIGHT(CONCAT('00',[FiscalQuarter]),2)) AS [FQDesc]
	  ,[FiscalSemesterYear] AS [FiscalYearHalfNum]
	  ,[FiscalSemester] AS [FiscalHalfNum]  
	  ,CONCAT('FH ', RIGHT(CONCAT('00',[FiscalSemester]),2)) AS [FHDesc]
	  ,[FiscalYear] AS [FiscalYear]
	  ,CONCAT('FY ', [FiscalYear]) AS [FYDesc]
	  ,CONVERT(DATE,[FiscalWeekFirstDate]) AS [FiscalWeekStart]
	  ,CONVERT(DATE, [FiscalWeekLastDate]) AS [FiscalWeekEnd]
	  ,CONVERT(DATE,[FiscalMonthFirstDate]) AS [FiscalMonthStart]
	  ,CONVERT(DATE,[FiscalMonthLastDate]) AS [FiscalMonthEnd]
	  ,CONVERT(DATE,[FiscalYearFirstDate]) AS [FiscalYearStart]
	  ,CONVERT(DATE,[FiscalYearLastDate]) AS [FiscalYearEnd]
	  ,[HolidayIndicator] AS [HolidayIndicator]
	  ,[HolidayName] AS [HolidayName]
	  ,[WeekdayWeekend]
	  ,[FiscalDateIndicator] AS [FiscalDayIndicator]
      ,[FiscalWeekIndicator] AS [FiscalWeekIndicator]
      ,[FiscalMonthIndicator] AS [FiscalMonthIndicator]
      ,[FiscalQuarterIndicator] AS [FiscalQuarterIndicator]
      ,[FiscalYearIndicator] AS [FiscalYearIndicator]
  FROM [Enterprise_DW].[DimDate_NonRetail]
  WHERE [FiscalYearIndicator] BETWEEN -5 AND 5
```

