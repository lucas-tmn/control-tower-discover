---
title: FactCurrentForecast table documentation
domain: Supply Chain Planning
warehouse: SupplyChain_Gold
schema: <schema>
table_name: FactCurrentForecast
last_updated: 2026-06-19
owner: Supply Chain Planning

---

## 1. Purpose & Business Context

This table captures the latest forecast snapshot that is published to supply planning, at the weekly item-warehouse grain. It stores three forecast quantities — resultant (model-driven), promotional lift, and total — normalized to weekly granularity from monthly source data. This is the operationally current forecast consumed by supply planning workflows and reports.

- **Implementing as Weekly Forecast value in anticipation of transition in weekly forecast in Q3**

---

## 2. Physical Table Definition

```sql
CREATE TABLE <schema>.FactCurrentForecast (
    ItemSKU VARCHAR(20) NOT NULL,
    WarehouseID VARCHAR(10) NOT NULL,
    WeekEnding DATE NOT NULL,
    ResultantForecast INT NOT NULL,
    PromoLift INT NOT NULL,
    TotalForecast INT NOT NULL,
    SnapshotDate DATE NOT NULL
);
```

---

## 3. Column Definitions

| Column | Data Type | Notes |
| --- | --- | --- |
| ItemSKU | VARCHAR(20) | Product identifier. Source: `SupplyForecast.FCST_1_ID` (RTRIM applied). Foreign key to `DimProduct[ItemSKU]`. |
| WarehouseID | VARCHAR(10) | Warehouse location identifier. Source: `SupplyForecast.FCST_2_ID` (RTRIM applied). Foreign key to `DimWarehouse[WarehouseID]`. |
| WeekEnding | DATE | Fiscal week ending date. Derived from `DimDate.FiscalWeekLastDate` matched on `SupplyForecast.FCST_YR_PRD = DimDate.FiscalMonthYear`. Foreign key to `DimDate[FiscalWeekLastDate]`. |
| ResultantForecast | INT | Resultant forecast quantity (model-driven). Source: `SupplyForecast.FCST_RSLT_QTY` normalized to weekly by dividing by weeks-in-month and rounding. |
| PromoLift | INT | Promotional lift quantity. Source: `SupplyForecast.PROMO_LIFT_QTY` normalized to weekly by dividing by weeks-in-month and rounding. |
| TotalForecast | INT | Total forecast quantity (resultant + promo). Computed as `(FCST_RSLT_QTY + PROMO_LIFT_QTY) / WeeksinMonth`, rounded and cast to INT. |
| SnapshotDate | DATE | Point-in-time snapshot date when this forecast was captured. Source: `SupplyForecast.dtea` (CONVERT to DATE). Indicates the load/run date of the published forecast. |

---

## 4. Semantic Model Layer

**Model Type:** Star schema / Direct Lake Query

**Fact Table:** `FactCurrentForecast`

### Relationships

| From | To | Type | Direction |
| --- | --- | --- | --- |
| `FactCurrentForecast[ItemSKU]` | `DimProduct[ItemSKU]` | Many-to-One | Single |
| `FactCurrentForecast[WarehouseID]` | `DimWarehouse[WarehouseID]` | Many-to-One | Single |
| `FactCurrentForecast[WeekEnding]` | `DimDate[FiscalWeekLastDate]` | Many-to-One | Single |

---

## 5. Measures (TMDL)

### Current Forecast

```tmdl
measure 'Resultant Forecast Qty' =
    CALCULATE(SUM(FactCurrentForecast[ResultantForecast]))
    formatString: #,0
    displayFolder: "Current Forecast"
    description: "Sum of resultant (model-driven) forecast quantities by selected dimensions."

measure 'Promo Lift Qty' =
    CALCULATE(SUM(FactCurrentForecast[PromoLift]))
    formatString: #,0
    displayFolder: "Current Forecast"
    description: "Sum of promotional lift forecast quantities by selected dimensions."

measure 'Total Forecast Qty' =
    CALCULATE(SUM(FactCurrentForecast[TotalForecast]))
    formatString: #,0
    displayFolder: "Current Forecast"
    description: "Sum of total forecast (resultant + promo) quantities by selected dimensions."
```

---

## 6. Source Data & ETL Logic

### Purpose & Business Context

Latest published forecast input for supply planning operations. Loaded from the weekly-grain forecast snapshot table at the item-warehouse level. Forecast quantities are normalized from monthly source values to weekly grain to align with operational planning cycles.

### Physical Table Definition

See Section 2.

### Semantic Model Layer

See Section 4.

### Measures

See Section 5.

### Source Data & ETL Logic

```sql
SELECT RTRIM([SFC].[FCST_1_ID]          ) AS [ItemSKU]
      ,RTRIM([SFC].[FCST_2_ID]    ) AS [WarehouseID]
      ,[DD].[FiscalWeekLastDate] AS [WeekEnding]
      ,CAST(ROUND([SFC].[FCST_RSLT_QTY]/[W].[WeeksinMonth],0) AS INT) AS [ResultantForecast]
      ,CAST(ROUND([SFC].[PROMO_LIFT_QTY]/[W].[WeeksinMonth],0) AS INT) AS [PromoLift]
      ,CAST(ROUND(([SFC].[FCST_RSLT_QTY] + [SFC].[PROMO_LIFT_QTY])/[W].[WeeksinMonth],0) AS INT) AS [TotalForecast]
      ,CONVERT(DATE, [SFC].[dtea]) AS [SnapshotDate]
  FROM [Enterprise_Lakehouse].[Wholesale_DemandPlanning_AFI].[SupplyForecast] AS SFC
  LEFT JOIN ( 
SELECT DISTINCT [FiscalMonthYear]
      ,[FiscalWeekLastDate]
  FROM [Enterprise_Lakehouse].[MasterData_DW].[DimDate]
  ) AS DD 
  ON [SFC].[FCST_YR_PRD] = [DD].[FiscalMonthYear]
  	LEFT JOIN ( 
SELECT [FiscalMonthYear]
      ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [WeeksinMonth]
  FROM [Enterprise_Lakehouse].[MasterData_DW].[DimDate]
  GROUP BY [FiscalMonthYear]
	) AS W
	ON [SFC].[FCST_YR_PRD] = [W].[FiscalMonthYear]
  WHERE [DD].[FiscalWeekLastDate] IS NOT NULL  -- Fiscal Calendar ends at start of 2029
```

**ETL Notes:**

- **Data source:** `[Enterprise_Lakehouse].[Wholesale_DemandPlanning_AFI].[SupplyForecast]` — published forecast snapshot table
- **Refresh frequency:** Nightly or transactional (based on SupplyForecast publication cycle)
- **Key transformation logic:**
  - **Grain normalization:** Monthly forecast quantities (FCST_RSLT_QTY, PROMO_LIFT_QTY) divided by actual weeks-in-month (calculated from DimDate) and rounded to INT for weekly-level consumption
  - **Fiscal week mapping:** SupplyForecast.FCST_YR_PRD matched to DimDate.FiscalMonthYear to retrieve FiscalWeekLastDate and week count
  - **Snapshot filtering:** WHERE clause excludes records where fiscal week does not map to calendar (edge case handling for fiscal calendar boundaries)
- **Snapshot strategy:** Latest only — this table contains only the most recent snapshot. Full snapshot history (e.g., for Plan Drop horizon analysis) will be managed in a Phase 5 specialized model.

---

## 7. Change Log

| Date | Change | Author |
| --- | --- | --- |
| 2026-06-19 | Initial draft | Robert Font Perez |
