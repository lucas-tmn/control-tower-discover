---
title: DimDate table documentation
domain: Supply Chain Planning 
warehouse: <warehouse>
schema: <schema> 
table_name: DimDate 
last_updated: 2026-06-16  
owner: Supply Chain Planning 

---

## 1. Purpose & Business Context

Fiscal calendar dimension used for grouping facts by various fiscal calendar attributes

- **Note: Schema still needs to be defined**

---

## 2. Physical Table Definition

```sql
CREATE TABLE <warehouse>.<schema>.DimDate (
    [Transaction Date] DATE NOT NULL,
    [Fiscal Year] INT NOT NULL,
    [Integer Date] INT NOT NULL,
    [Mapics Date] INT NOT NULL,
    [Day of Week] VARCHAR(9) NOT NULL,
    [Fiscal Week Num] INT NOT NULL,
    [FW Desc] VARCHAR(5) NOT NULL,
    [Fiscal Year Week Num] INT NOT NULL,
    [Fiscal Month Num] INT NOT NULL,
    [FM Desc] VARCHAR(5) NOT NULL,
    [Fiscal Month Name] VARCHAR(3) NOT NULL,
    [Fiscal Year Month Num] INT NOT NULL,
    [Fiscal Month Year Desc] VARCHAR(8) NOT NULL,
    [Fiscal Quarter Num] INT NOT NULL,
    [FQ Desc] VARCHAR(5) NOT NULL,
    [Fiscal Year Half Num] INT NOT NULL,
    [Fiscal Half Num] INT NOT NULL,
    [FH Desc] VARCHAR(5) NOT NULL,
    [FY Desc] VARCHAR(5) NOT NULL,
    [Fiscal Week Start] DATE NOT NULL,
    [Fiscal Week End] DATE NOT NULL,
    [Fiscal Month Start] DATE NOT NULL,
    [Fiscal Month End] DATE NOT NULL,
    [Fiscal Year Start] DATE NOT NULL,
    [Fiscal Year End] DATE NOT NULL,
    [Holiday Indicator] VARCHAR(12) NOT NULL,
    [Holiday Name] VARCHAR(20) NULL,
    [WeekdayWeekend] VARCHAR(7) NOT NULL,
    [Fiscal Day Indicator] INT NOT NULL,
    [Fiscal Week Indicator] INT NOT NULL,
    [Fiscal Month Indicator] INT NOT NULL,
    [Fiscal Quarter Indicator] INT NOT NULL,
    [Fiscal Year Indicator] INT NOT NULL,
    [FiscalWeeksinMonth] INT NOT NULL
);
```

### Add the primary key

```sql
ALTER TABLE <schema>.DimDate
ADD CONSTRAINT PK_DimDate
PRIMARY KEY NONCLUSTERED ([Transaction Date])
NOT ENFORCED;

```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| Transaction Date | dateTime | primary key - distinct dates |
| Fiscal Year | int64 | YYYY |
| Integer Date | int64 | YYYYMMDD |
| Mapics Date | int64 | MAPICS date used in AS400 tables |
| Day of Week | string | "Sunday" through "Saturday" |
| Fiscal Week Num | int64 | Week number of the fiscal year |
| FW Desc | string | "FW ##" |
| Fiscal Year Week Num | int64 | YYYYWW |
| Fiscal Month Num | int64 | 1-12 |
| FM Desc | string | "FM ##" |
| Fiscal Month Name | string | "Jan, Feb, Mar" |
| Fiscal Year Month Num | int64 | YYYYMM |
| Fiscal Month Year Desc | string | "Oct YYYY" |
| Fiscal Quarter Num | int64 | 1-4 |
| FQ Desc | string | "FQ ##" |
| Fiscal Year Half Num | int64 | YYYYH |
| Fiscal Half Num | int64 | 1-2 |
| FH Desc | string | "FH #" |
| FY Desc | string | "FY YYYY" |
| Fiscal Week Start | dateTime | Sunday date - start of fiscal week |
| Fiscal Week End | dateTime | Saturday date - last day of fiscal week |
| Fiscal Month Start | dateTime | First Sunday date of fiscal month |
| Fiscal Month End | dateTime | Last Saturday date of fiscal month |
| Fiscal Year Start | dateTime | First Sunday date of fiscal year |
| Fiscal Year End | dateTime | Last Saturday date of fiscal year |
| Holiday Indicator | string | "Holiday" or "Non-Holiday" |
| Holiday Name | string | blank or Holiday Name |
| WeekdayWeekend | string | "Weekday" or "Weekend" |
| Fiscal Day Indicator | int64 | index of days, current day is zero, +/-X for days forward or back |
| Fiscal Week Indicator | int64 | index of weeks, current week is zero, +/-X for weeks forward or back |
| Fiscal Month Indicator | int64 | index of months, current month is zero, +/-X for months forward or back |
| Fiscal Quarter Indicator | int64 | index of quarters, current quarter is zero, +/-X for quarters forward or back |
| Fiscal Year Indicator | int64 | index of years, current year is zero, +/-X for years forward or back |
| FiscalWeeksinMonth | int64 | Count of weeks in the month |

---

## 4. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-16 | Initial draft | Robert Font Perez |
