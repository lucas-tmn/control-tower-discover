---
model_name: Act+Fcst vs Manufacturing
server: ashley-edw.database.windows.net
database: ashley_edw
table_count: 10
measure_count: 14
non_warehouse_sources: yes
non_warehouse_source_types: PowerBI Dataflow
---

# Business Context

This report serves domestic manufacturing capacity planning at two levels of the supply chain. The primary question is whether domestic U.S. finished goods production capacity can absorb the blended demand signal — actual orders for past fiscal months plus resultant and promotional forecast for future months. It then steps one level up the supply chain to ask the same question of Wanek and Millennium: because those plants produce the kits and components that feed domestic finished goods production, their capacity (tracked via `ProdCapacity`) and actual output (tracked via `VendorShipped`) must also be sufficient to support the projected demand. The 56-day ETD offset used throughout the model reflects the lead time between when Wanek/Millennium ship kits and components and when domestic plants convert them into finished goods for customer delivery. Dimension data (product details, warehouse master, fiscal calendar) is sourced from shared PowerBI Dataflows rather than direct warehouse queries.

## Relationships

| From | To |
| --- | --- |
| ActDemand.It_WhKey | z_ItemWHProdResource.It_WhKey |
| ActDemand.CurReqWkEnding | z_FiscalCal.'Transaction Date' |
| Fcast.It_WhKey | z_ItemWHProdResource.It_WhKey |
| Fcast.FiscalWeekLastDate | z_FiscalCal.'Transaction Date' |
| Fcast.ETDWkLastDate | z_FiscalCal.'Transaction Date' *(inactive)* |
| ProdCapacity.ResourceID | z_ProdResourceMaster.ResourceID |
| ProdCapacity.FiscalWeekLastDate | z_FiscalCal.'Transaction Date' |
| VendorShipped.'Item SKU' | z_ProductDetails.'Item SKU' |
| VendorShipped.ProdResourceId | z_ProdResourceMaster.ResourceID |
| VendorShipped.FiscalWeekLastDate | z_FiscalCal.'Transaction Date' |
| VendorShipped.ETAWkLastDate | z_FiscalCal.'Transaction Date' *(inactive)* |
| z_ItemWHProdResource.'Item SKU' | z_ProductDetails.'Item SKU' |
| z_ItemWHProdResource.Warehouse | z_WarehouseMaster.Warehouse |
| z_ItemWHProdResource.'Prod Resource' | z_ProdResourceMaster.ResourceID *(inactive)* |

*Only non-date-table relationships listed.*

## Measures

### Act - Invoiced

- Sum of order quantity for invoiced (shipped) demand lines  
`CALCULATE(SUM(ActDemand[Order Qty]), ActDemand[Status]="Invoiced")`

### Act - Open Ord

- Sum of order quantity for open (unfulfilled) demand lines  
`CALCULATE(SUM(ActDemand[Order Qty]),ActDemand[Status]="Open Order")`

### Fcast - Result

- Resultant forecast quantity (base demand forecast, datatype RSLF)  
`CALCULATE(SUM(Fcast[Qty]),Fcast[Datatype] = "RSLF")`

### Fcast - Promo

- Promotional lift component of the forecast (datatype PROL)  
`CALCULATE(SUM(Fcast[Qty]),Fcast[Datatype]="PROL")`

### Fcast - Total

- Total forecast = resultant + promotional lift  
`[Fcast - Result] + [Fcast - Promo]`

### Act+Fcast

- Blended demand: actual orders for past fiscal months plus total forecast for future months  
`CALCULATE(SUM(ActDemand[Order Qty]),z_FiscalCal[Fiscal Month Indicator]<0) + ([Fcast - Result]+[Fcast - Promo])`

### Act+Fcast Weekly Qty

- Blended demand spread evenly across fiscal weeks in the month  
`DIVIDE([Act+Fcast],[FiscalWeeksinMonth])`

### FiscalWeeksinMonth

- Average number of fiscal weeks in the current month context (calculated column on z_FiscalCal handles 4/5/4 calendar)  
`CALCULATE(AVERAGE(z_FiscalCal[FiscalWeeksinMonth]))`

### Prod Capacity

- Total available production hours (max of firm+planned hours vs. stated capacity)  
`CALCULATE(SUM(ProdCapacity[TotalAvailHours]))`

### ETD Fcast

- Total forecast (result + promo) keyed to the ETD week (56 days before customer delivery), using inactive relationship

```dax
CALCULATE(SUM(Fcast[Qty]),Fcast[Datatype] = "RSLF",USERELATIONSHIP(z_FiscalCal[Transaction Date],Fcast[ETDWkLastDate]))
+CALCULATE(SUM(Fcast[Qty]),Fcast[Datatype] = "PROL",USERELATIONSHIP(z_FiscalCal[Transaction Date],Fcast[ETDWkLastDate]))
```

### Past Due Qty

- Open order quantity for fiscal weeks already in the past  
`CALCULATE([Act - Open Ord],z_FiscalCal[Fiscal Week Indicator]<0)`

### FcstAverageWeekly

- Average weekly ETD forecast over the next 16 fiscal weeks  
`DIVIDE(CALCULATE([ETD Fcast],AND(z_FiscalCal[Fiscal Week Indicator]>0,z_FiscalCal[Fiscal Week Indicator]<=16)),17)`

### Vendor Shipped

- Quantity shipped from Wanek/Millennium plants keyed to the manufacturing ship week  
`CALCULATE(SUM(VendorShipped[Shipped Qty]))`

### ETA Vendor Shipped

- Vendor-shipped quantity keyed to the estimated arrival week (ship week + 56 days), using inactive relationship  
`CALCULATE(SUM(VendorShipped[Shipped Qty]), USERELATIONSHIP(z_FiscalCal[Transaction Date],VendorShipped[ETAWkLastDate]))`

## Tables

### ActDemand

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| It_WhKey | string | Source column — composite key (Item SKU + '_' + Warehouse) |
| Item SKU | string | Source column |
| Warehouse | string | Source column |
| Order Qty | int64 | Source column |
| Status | string | Source column — "Invoiced" or "Open Order" |
| InsertedDate | dateTime | Source column |
| ETDWkEnding | dateTime | Calculated: `DATEADD(ActDemand[CurReqWkEnding],-56,DAY)` — customer required date shifted 56 days earlier for ETD |
| CurReqWkEnding | dateTime | Source column — customer required week ending date |

**Source Query:**

```sql
SELECT [ACT].[Item SKU]+'_'+[ACT].[Warehouse] AS [It_WhKey]
      ,[ACT].[Item SKU]
      ,[ACT].[Warehouse]
      ,SUM([ACT].[Order Quantity]) AS [Order Qty]
      --,SUM([ACT].[Order Amount]) AS [Order Amount]
      ,[ACT].[CurReqWkEnding]
      --,[ACT].[Sales Type]
      ,[ACT].[Status]
      ,[ACT].[InsertedDate]
  FROM [SupplyChain_Enh].[ActualsCustItemWH_AFI] AS ACT
  LEFT JOIN [Enterprise_DW].[DimDate] AS DD
    ON  [ACT].[CurReqWkEnding] = [DD].[DateID]

  INNER JOIN ( 
SELECT DISTINCT [DIN].[dinItem]
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
    AND ([DIN].[dinWarehouse] IN ('1','15','17','28','ECR','101','12','19','201')  AND [DIN].[dinMakeBuyCode] = 'M')

  ) AS item
    ON [ACT].[Item SKU] = [item].[dinItem]

  WHERE [DD].[FiscalYearIndicator] >= -1

  GROUP BY [ACT].[Item SKU]
          ,[ACT].[Warehouse]
          ,[ACT].[CurReqWkEnding]
          --,[ACT].[Sales Type]
          ,[ACT].[Status]
          ,[ACT].[InsertedDate]
```

---

### Fcast

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| It_WhKey | string | Source column — composite key (Item + '_' + Warehouse) |
| Item | string | Source column |
| Warehouse | string | Source column |
| Datatype | string | Source column — "RSLF" (resultant), "PROL" (promo lift), "FUTO" (future orders) |
| Qty | int64 | Source column — weekly quantity (monthly total divided by NumWeeks) |
| SnapshotDate | dateTime | Source column — date the forecast snapshot was taken |
| FiscalWeekLastDate | dateTime | Source column — last date of the fiscal week |
| NumWeeks | int64 | Source column — number of fiscal weeks in the source month |
| ETDWkLastDate | dateTime | Source column — FiscalWeekLastDate minus 56 days (ETD week) |

**Source Query:**

```sql
SELECT [FC].[It_WhKey]
      ,[FC].[Item]
      ,[FC].[Warehouse]
      ,[FC].[Datatype]
      ,CAST(ROUND([FC].[Qty]/[FC].[NumWeeks],0) AS INT) AS [Qty]
      ,[WD].[FiscalWeekLastDate]
	  ,DATEADD(DAY, -56,[WD].[FiscalWeekLastDate]) AS [ETDWkLastDate]
      ,[FC].[NumWeeks]
      ,[FC].[SnapshotDate]
  FROM (
SELECT [DFC].[dfcItem]+'_'+[DFC].[dfcWarehouse] AS [It_WhKey]
      ,[DFC].[dfcItem] AS [Item]
	  ,[DFC].[dfcWarehouse] AS [Warehouse]
	  ,[Datatype] = 'RSLF'
	  ,SUM([DFC].[dfcResultantForecast]) AS [Qty]
	  ,[DD].[FiscalMonthLastDate]
	  ,[DD].[NumWeeks]
	  ,CONVERT(DATE,[DFC].[dtea]) AS [SnapshotDate]
  FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC
  LEFT JOIN (
SELECT [FiscalMonthYear]
      ,[FiscalMonthLastDate]
	  ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [NumWeeks]
  FROM [Enterprise_DW].[DimDate]
  GROUP BY [FiscalMonthYear]
          ,[FiscalMonthLastDate]
  ) AS DD 
  ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]

  INNER JOIN ( 
SELECT DISTINCT [DIN].[dinItem]
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
    AND ([DIN].[dinWarehouse] IN ('1','15','17','28','ECR','101','12','19','201')  AND [DIN].[dinMakeBuyCode] = 'M')

  ) AS item
    ON [DFC].[dfcItem] = [item].[dinItem]

  WHERE [DFC].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandForecastSnapshot])
    AND [DD].[FiscalMonthLastDate] IS NOT NULL
    AND [DFC].[dfcResultantForecast] > 0
    
  GROUP BY [DFC].[dfcItem]
          ,[DFC].[dfcWarehouse]
          ,[DD].[FiscalMonthLastDate]
		  ,[DD].[NumWeeks]
          ,[DFC].[dtea]

UNION 

SELECT [DFC].[dfcItem]+'_'+[DFC].[dfcWarehouse] AS [It_WhKey]
      ,[DFC].[dfcItem] AS [Item]
	  ,[DFC].[dfcWarehouse] AS [Warehouse]
	  ,[Datatype] = 'PROL'
	  ,SUM([DFC].[dfcPromotionalLift]) AS [Qty]
	  ,[DD].[FiscalMonthLastDate]
	  ,[DD].[NumWeeks]
	  ,CONVERT(DATE, [DFC].[dtea]) AS [SnapshotDate]
  FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC
  LEFT JOIN (
SELECT [FiscalMonthYear]
      ,[FiscalMonthLastDate]
	  ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [NumWeeks]
  FROM [Enterprise_DW].[DimDate]
  GROUP BY [FiscalMonthYear]
          ,[FiscalMonthLastDate]
  ) AS DD 
  ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]

  INNER JOIN ( 
SELECT DISTINCT [DIN].[dinItem]
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
    AND ([DIN].[dinWarehouse] IN ('1','15','17','28','ECR','101','12','19','201')  AND [DIN].[dinMakeBuyCode] = 'M')

  ) AS item
    ON [DFC].[dfcItem] = [item].[dinItem]

  WHERE [DFC].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandForecastSnapshot])
    AND [DD].[FiscalMonthLastDate] IS NOT NULL
    AND [DFC].[dfcPromotionalLift] > 0

  GROUP BY [DFC].[dfcItem]
          ,[DFC].[dfcWarehouse]
          ,[DD].[FiscalMonthLastDate]
		  ,[DD].[NumWeeks]
          ,[DFC].[dtea]

UNION 

SELECT [DFC].[dfcItem]+'_'+[DFC].[dfcWarehouse] AS [It_WhKey]
      ,[DFC].[dfcItem] AS [Item]
	  ,[DFC].[dfcWarehouse] AS [Warehouse]
	  ,[Datatype] = 'FUTO'
	  ,SUM([DFC].[dfcOrderFutureQty]) AS [Qty]
	  ,[DD].[FiscalMonthLastDate]
	  ,[DD].[NumWeeks]
	  ,CONVERT(DATE, [DFC].[dtea]) AS [SnapshotDate]
  FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC
  LEFT JOIN (
SELECT [FiscalMonthYear]
      ,[FiscalMonthLastDate]
	  ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [NumWeeks]
  FROM [Enterprise_DW].[DimDate]
  GROUP BY [FiscalMonthYear]
          ,[FiscalMonthLastDate]
  ) AS DD 
  ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]

  INNER JOIN ( 
SELECT DISTINCT [DIN].[dinItem]
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
    AND ([DIN].[dinWarehouse] IN ('1','15','17','28','ECR','101','12','19','201')  AND [DIN].[dinMakeBuyCode] = 'M')

  ) AS item
    ON [DFC].[dfcItem] = [item].[dinItem]

  WHERE [DFC].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandForecastSnapshot])
    AND [DD].[FiscalMonthLastDate] IS NOT NULL
    AND [DFC].[dfcOrderFutureQty] > 0

  GROUP BY [DFC].[dfcItem]
          ,[DFC].[dfcWarehouse]
          ,[DD].[FiscalMonthLastDate]
		  ,[DD].[NumWeeks]
          ,[DFC].[dtea]
    ) AS FC

   LEFT JOIN (
SELECT DISTINCT [FiscalMonthLastDate]
	  ,[FiscalWeekLastDate]
  FROM [Enterprise_DW].[DimDate]
   ) AS WD
   ON [FC].[FiscalMonthLastDate] = [WD].[FiscalMonthLastDate]
```

---

### VendorShipped

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item SKU | string | Source column |
| Transcaction Code | string | Source column — transaction type (value "SA" = shipment/assembly) |
| ProdResourceId | string | Source column — production resource identifier |
| FiscalWeekLastDate | dateTime | Source column — fiscal week of the manufacturing ship event |
| Shipped Qty | double | Source column |
| RefreshDate | dateTime | Source column — data refresh timestamp |
| ETAWkLastDate | dateTime | Source column — FiscalWeekLastDate + 56 days (estimated arrival week) |

**Source Query:**

```sql
SELECT TRIM([IMH].[ITNBR]) AS [Item SKU]
	  ,TRIM([IMH].[TCODE]) AS [Transcaction Code]
	  ,[PC].[ProdResourceId]
	  ,[DD].[FiscalWeekLastDate]
	  ,DATEADD(DAY, 56,[DD].[FiscalWeekLastDate]) AS [ETAWkLastDate]
      ,SUM([IMH].[TRQTY]) AS [Shipped Qty]
      ,DW_Developer.fn_GetCSTDate(GETDATE()) AS [RefreshDate]
  FROM [Manufacturing_Inventory_WNK].[IMHIST] AS IMH

  INNER JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON [PC].[SnapshotDate] = (SELECT MAX([SnapshotDate]) FROM [SupplyChain_Enh].[ProductionConversion])
	  AND [IMH].[ITNBR] = [PC].[ItemId]
	  AND [PC].[LocationId] = '900515'

  INNER JOIN [Enterprise_DW].[DimDate] AS DD
    ON [IMH].[TRNDT] = [DD].[MapicsDate]
	AND [DD].[FiscalWeekIndicator] >= -18

 
  WHERE [IMH].[TCODE] = 'SA'
    AND [IMH].[HOUSE] = '31'

  GROUP BY ([IMH].[ITNBR])
          ,([IMH].[TCODE])
          ,[PC].[ProdResourceId]
          ,[DD].[FiscalWeekLastDate]

UNION 

SELECT TRIM([IMH].[ITNBR]) AS [Item SKU]
	  ,TRIM([IMH].[TCODE]) AS [Transcaction Code]
	  ,[PC].[ProdResourceId]
	  ,[DD].[FiscalWeekLastDate]
	  ,DATEADD(DAY, 56,[DD].[FiscalWeekLastDate]) AS [ETAWkLastDate]
      ,SUM([IMH].[TRQTY]) AS [Shipped Qty]
      ,DW_Developer.fn_GetCSTDate(GETDATE()) AS [RefreshDate]
  FROM [Manufacturing_Inventory_WNK].[IMHIST] AS IMH

  INNER JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON [PC].[SnapshotDate] = (SELECT MAX([SnapshotDate]) FROM [SupplyChain_Enh].[ProductionConversion])
	  AND [IMH].[ITNBR] = [PC].[ItemId]
	  AND [PC].[LocationId] = '600039'

  INNER JOIN [Enterprise_DW].[DimDate] AS DD
    ON [IMH].[TRNDT] = [DD].[MapicsDate]
	AND [DD].[FiscalWeekIndicator] >= -18

 
  WHERE [IMH].[TCODE] = 'SA'
    AND [IMH].[HOUSE] = '35'

  GROUP BY ([IMH].[ITNBR])
          ,([IMH].[TCODE])
          ,[PC].[ProdResourceId]
          ,[DD].[FiscalWeekLastDate]


UNION 

SELECT TRIM([IMH].[ITNBR]) AS [Item SKU]
	  ,TRIM([IMH].[TCODE]) AS [Transcaction Code]
	  ,[PC].[ProdResourceId]
	  ,[DD].[FiscalWeekLastDate]
	  ,DATEADD(DAY, 56,[DD].[FiscalWeekLastDate]) AS [ETAWkLastDate]
      ,SUM([IMH].[TRQTY]) AS [Shipped Qty]
      ,DW_Developer.fn_GetCSTDate(GETDATE()) AS [RefreshDate]
  FROM [Manufacturing_Inventory_WNK].[IMHIST] AS IMH

  INNER JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON [PC].[SnapshotDate] = (SELECT MAX([SnapshotDate]) FROM [SupplyChain_Enh].[ProductionConversion])
	  AND [IMH].[ITNBR] = [PC].[ItemId]
	  AND [PC].[LocationId] = '900639'

  INNER JOIN [Enterprise_DW].[DimDate] AS DD
    ON [IMH].[TRNDT] = [DD].[MapicsDate]
	AND [DD].[FiscalWeekIndicator] >= -18

 
  WHERE [IMH].[TCODE] = 'SA'
    AND [IMH].[HOUSE] = '33'

  GROUP BY ([IMH].[ITNBR])
          ,([IMH].[TCODE])
          ,[PC].[ProdResourceId]
          ,[DD].[FiscalWeekLastDate]


UNION 

SELECT TRIM([IMH].[ITNBR]) AS [Item SKU]
	  ,TRIM([IMH].[TCODE]) AS [Transcaction Code]
	  ,[PC].[ProdResourceId]
	  ,[DD].[FiscalWeekLastDate]
	  ,DATEADD(DAY, 56,[DD].[FiscalWeekLastDate]) AS [ETAWkLastDate]
      ,SUM([IMH].[TRQTY]) AS [Shipped Qty]
      ,DW_Developer.fn_GetCSTDate(GETDATE()) AS [RefreshDate]
  FROM [Manufacturing_Inventory_MIL].[IMHIST] AS IMH

  INNER JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON [PC].[SnapshotDate] = (SELECT MAX([SnapshotDate]) FROM [SupplyChain_Enh].[ProductionConversion])
	  AND [IMH].[ITNBR] = [PC].[ItemId]
	  AND [PC].[LocationId] = '624556'

  INNER JOIN [Enterprise_DW].[DimDate] AS DD
    ON [IMH].[TRNDT] = [DD].[MapicsDate]
	AND [DD].[FiscalWeekIndicator] >= -18
 
  WHERE [IMH].[TCODE] = 'SA'

  GROUP BY ([IMH].[ITNBR])
          ,([IMH].[TCODE])
		  ,[PC].[ProdResourceId]
          ,[DD].[FiscalWeekLastDate]
```

---

### ProdCapacity

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ResourceID | string | Source column — production resource identifier |
| LocationID | string | Source column — plant location |
| FiscalWeekLastDate | dateTime | Source column |
| FirmHours | double | Source column — committed production hours |
| PlannedHours | double | Source column — planned production hours |
| TotalAvailHours | double | Source column — MAX(firm+planned, stated capacity) |
| Snapshotdate | dateTime | Source column — most recent Monday snapshot date |

**Source Query:**

```sql
SELECT [PC].[ResourceID]
      ,[PC].[LocationID]
      ,[DD].[FiscalWeekLastDate]
      ,SUM([PC].[FirmHours]) AS [FirmHours]
      ,SUM([PC].[PlannedHours]) AS [PlannedHours]
      ,SUM(GREATEST(([PC].[FirmHours]+[PC].[PlannedHours]),[PC].[TotalAvailHours])) AS [TotalAvailHours]
	  ,[PC].[Snapshotdate]
  FROM [Supplychain_History].[ProductionCapacity]  AS PC
  LEFT JOIN [Enterprise_DW].[DimDate] AS DD
    ON [PC].[SolverDate] = [DD].[DateTimeID]
  WHERE [PC].[Snapshotdate] = (SELECT MAX([SnapshotDate]) FROM [Supplychain_History].[ProductionCapacity] WHERE DATENAME(WEEKDAY,[Snapshotdate]) = 'MONDAY')
    AND [PC].[LocationID] IN (
                              '1','101','12','15','151'
                              ,'17','19','20','28','ECR','201'
                              ,'900515','600039','624556','900639'
                              )

  GROUP BY [PC].[ResourceID]
          ,[PC].[LocationID]
          ,[DD].[FiscalWeekLastDate]
		  ,[PC].[Snapshotdate]
```

---

### z_FiscalCal

**Source type:** PowerBI Dataflow

*(Source: workspace a47e4573-c455-40af-a9ad-e22c81a07926, dataflow 346f2aa1-dd50-4c11-9630-b17f75854663, entity AshleyFiscalCalendarV2)*

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Transaction Date | dateTime | Source column — primary key for time relationships |
| Fiscal Year | int64 | Source column |
| Calendar Year | int64 | Source column |
| Integer Date | int64 | Source column |
| Mapics Date | int64 | Source column |
| Day of Week | string | Source column |
| Fiscal Week Num | int64 | Source column |
| FW Desc | string | Source column |
| Fiscal Year Week Num | int64 | Source column |
| Fiscal Month Num | int64 | Source column |
| FM Desc | string | Source column |
| Fiscal Month Name | string | Source column |
| Fiscal Year Month Num | int64 | Source column |
| Fiscal Month Year Desc | string | Source column — sorted by Fiscal Year Month Num |
| Fiscal Month (calendar start) | dateTime | Source column |
| Fiscal Quarter Num | int64 | Source column |
| FQ Desc | string | Source column |
| Fiscal Year Half Num | int64 | Source column |
| Fiscal Half Num | int64 | Source column |
| FH Desc | string | Source column |
| FY Desc | string | Source column |
| Fiscal Week Start | dateTime | Source column |
| Fiscal Week End | dateTime | Source column |
| Fiscal Month Start | dateTime | Source column |
| Fiscal Month End | dateTime | Source column |
| Fiscal Year Start | dateTime | Source column |
| Fiscal Year End | dateTime | Source column |
| Holiday Indicator | string | Source column |
| Holiday Name | string | Source column |
| WeekdayWeekend | string | Source column |
| Calendar Week Num | int64 | Source column |
| Calendar Month Num | int64 | Source column |
| Calendar Quarter Num | int64 | Source column |
| Fiscal Day Indicator | int64 | Source column — relative day offset from today (negative = past) |
| Fiscal Week Indicator | int64 | Source column — relative fiscal week offset from current week |
| Fiscal Month Indicator | int64 | Source column — relative fiscal month offset (negative = past month) |
| Fiscal Quarter Indicator | int64 | Source column |
| Fiscal Year Indicator | int64 | Source column |
| FiscalWeeksinMonth | int64 | Calculated: `SWITCH(z_FiscalCal[Fiscal Year Month Num],202212,6,SWITCH(z_FiscalCal[Fiscal Month Num],3,5,6,5,9,5,12,5,4))` — weeks per fiscal month (4/5/4 pattern, special case for FY2022 Dec) |

---

### z_ItemWHProdResource

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| It_WhKey | string | Source column — composite key (Item SKU + '_' + Warehouse), deduplicated |
| Item SKU | string | Source column |
| Warehouse | string | Source column — distribution warehouse |
| ABC_IP | string | Source column — inventory planning ABC classification |
| MBX | string | Source column — make/buy/transfer code (M/B/X) |
| WH Source | string | Source column — source warehouse |
| Prod Source | string | Source column — production source location |
| Prod Resource | string | Source column — production resource ID |
| L2 Item | string | Source column — level-2 component item (for kit/sub-assembly items) |
| L2 Prod Source | string | Source column — level-2 production source |
| L2 Prod Resource | string | Source column — level-2 production resource ID |
| dtea | dateTime | Source column — snapshot effective date |

**Source Query:**

```sql
/* MBX Prod Resource */

SELECT [PRS].[Item SKU]+'_'+[PRS].[Warehouse] AS [It_WhKey]
      ,[PRS].[Item SKU]
      ,[PRS].[Warehouse]
	  ,[PRS].[ABC_IP]
      ,[PRS].[MBX]
      ,[PRS].[WH Source]
      ,[PRS].[Prod Source]
      ,[PRS].[Prod Resource]
	  ,COALESCE([KS].[L2 Item],[PRS].[Item SKU]) AS [L2 Item]
	  ,COALESCE([KS].[L2 Source], [PRS].[Prod Source]) AS [L2 Prod Source]
	  ,COALESCE([PC3].[ProdResourceId], [PRS].[Prod Resource]) AS [L2 Prod Resource]
	  ,[PRS].[dtea]
FROM (

-- Buy Items
SELECT DISTINCT [DIN].[dinItem] AS [Item SKU]
      ,[DIN].[dinWarehouse] AS [Warehouse]
	  ,[DIN].[dinMakeBuyCode] AS [MBX]
	  ,[DIN].[dinSource1] AS [WH Source]
	  ,[DINK].[dinInvPlanningVendor] AS [Prod Source]
	  ,[PC].[ProdResourceId] AS [Prod Resource]
	  ,[DIN].[dinInventoryPlanningABCCode] AS [ABC_IP]
	  ,[DIN].[dtea]
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  LEFT JOIN [SupplyChain_Enh].[DemandInventorySnapshot] AS DINK
    ON [DIN].[dinItem] = [DINK].[dinItem]
	  AND [DIN].[dinSource1] = [DINK].[dinWarehouse]
	  AND [DIN].[dtea] = [DINK].[dtea]
  LEFT JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON CONVERT(DATE, [DIN].[dtea]) = CONVERT(DATE, PC.[SnapshotDate])
	  AND [DIN].[dinItem] = PC.[ItemId] 
	  AND [DINK].[dinInvPlanningVendor] = PC.[LocationId]
    WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
	  AND [DIN].[dinMakeBuyCode] IN ('X','B')
	  AND [DINK].[dinMakeBuyCode] = 'B'

UNION 

-- Transfer Items
SELECT DISTINCT [DIN].[dinItem] AS [Item SKU]
      ,[DIN].[dinWarehouse] AS [Warehouse]
	  ,[DIN].[dinMakeBuyCode] AS [MBX]
	  ,[DIN].[dinSource1] AS [WH Source]
	  ,[DINK].[dinSource1] AS [Prod Source]
	  ,[PC].[ProdResourceId] AS [Prod Resource]
	  ,[DIN].[dinInventoryPlanningABCCode] AS [ABC_IP]
	  ,[DIN].[dtea]   
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  LEFT JOIN [SupplyChain_Enh].[DemandInventorySnapshot] AS DINK
    ON [DIN].[dinItem] = [DINK].[dinItem]
	  AND [DIN].[dinSource1] = [DINK].[dinWarehouse]
	  AND [DIN].[dtea] = [DINK].[dtea]
  LEFT JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON CONVERT(DATE, [DIN].[dtea]) = CONVERT(DATE, PC.[SnapshotDate])
	  AND [DIN].[dinItem] = PC.[ItemId] 
	  AND [DIN].[dinSource1] = PC.[LocationId]
    WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
	  AND [DIN].[dinMakeBuyCode] = 'X'
	  AND [DINK].[dinMakeBuyCode] = 'M'

UNION 

-- Make Items
SELECT DISTINCT [DIN].[dinItem] AS [Item SKU]
      ,[DIN].[dinWarehouse] AS [Warehouse]
	  ,[DIN].[dinMakeBuyCode] AS [MBX]
	  ,[DIN].[dinSource1] AS [WH Source]
	  ,[DIN].[dinSource1] AS [Prod Source]
	  ,[PC].[ProdResourceId] AS [Prod Resource]
	  ,[DIN].[dinInventoryPlanningABCCode] AS [ABC_IP]
	  ,[DIN].[dtea]    
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  LEFT JOIN [SupplyChain_Enh].[ProductionConversion] AS PC
    ON CONVERT(DATE, [DIN].[dtea]) = CONVERT(DATE, PC.[SnapshotDate])
	  AND [DIN].[dinItem] = PC.[ItemId] 
	  AND [DIN].[dinSource1] = PC.[LocationId]
    WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
	AND [DIN].[dinMakeBuyCode] = 'M'

  ) AS PRS

LEFT JOIN ( 
  -- Kit/sub-assembly L2 lookup (items ending in 'UN')
  ...
) AS KS
  ON [PRS].[Item SKU] = [KS].[Parent Item]
   AND [PRS].[Prod Source] = [KS].[Make WH]

WHERE [PRS].[Item SKU] IN (
  SELECT DISTINCT [DFC].[dfcItem]
  FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC
  WHERE [DFC].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandForecastSnapshot])
)
AND (
  [PRS].[Prod Source] IN ('900515','600039','624556','900639')
  OR [KS].[L2 Source] IN ('900515','600039','624556','900639')
)
-- Result deduplicated on It_WhKey
```

---

### z_ProdResourceMaster

**Source type:** Computed (derived from ProdCapacity via M query — no direct external source)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ResourceID | string | Source column — from ProdCapacity |
| LocationID | string | Source column — from ProdCapacity |
| Prod Group | string | Calculated: `SWITCH(z_ProdResourceMaster[LocationID],"900515","Wanek 1","900639","Wanek 2","600039","Wanek 3","624556","Millenium","Domestic")` |
| Resource Group | string | Calculated DAX SWITCH mapping ResourceID → category (Components, UPH FG, LTHR FG, CSG, Bedding FG, etc.) |

*(Distinct ResourceID + LocationID combinations extracted from ProdCapacity; no SQL query)*

---

### z_ProductDetails

**Source type:** PowerBI Dataflow

*(Source: workspace a47e4573-c455-40af-a9ad-e22c81a07926, dataflow 346f2aa1-dd50-4c11-9630-b17f75854663, entity CurrentProductDetails)*

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item SKU | string | Source column |
| Item Description | string | Source column |
| ItemSKU Description | string | Source column |
| Colors | string | Source column |
| Series Number | string | Source column |
| Series Name | string | Source column |
| Series Description | string | Source column |
| Ext Series Number | string | Source column |
| Ext Series Description | string | Source column |
| Series Color | string | Source column |
| Item Grouping | string | Source column |
| Item Class Code | string | Source column |
| Item Class Name | string | Source column |
| Collective Class Code | string | Source column |
| Collective Class | string | Source column |
| Responsible Office | string | Source column |
| Product Line | string | Source column |
| AFI Finance Division | string | Source column |
| AFI Sales Division Code | string | Source column |
| AFI Sales Division | string | Source column |
| AFI Sales Category Code | string | Source column |
| AFI Sales Category | string | Source column |
| Retail Category Code | string | Source column |
| Retail Category Description | string | Source column |
| HSExclusiveFlag | boolean | Source column |
| FOB Price | double | Source column |
| Import/Domestic Code | string | Source column |
| Qty In Box | double | Source column |
| UOM | string | Source column |
| Main Piece Item | string | Source column |
| Primary Vendor | string | Source column |
| Primary Vendor Name | string | Source column |
| Item Style Code | string | Source column |
| Item Style Group | string | Source column |
| AFI Item Status | string | Source column |
| Manufacturing Status | string | Source column |
| Manufacturing Status Change Date | dateTime | Source column |
| ItemForecastPlannerID | string | Source column |
| Cubes | double | Source column |
| ContainerVolume | double | Source column |
| Unit Price | double | Source column |
| Current Status | string | Source column |
| Future Status | string | Source column |
| ItemImage | string | Source column |
| Image URL | string | Source column |
| Sales Class Code | string | Source column |
| Sales Class Description | string | Source column |
| Marketing Item Status | string | Source column |
| Marketing Status Description | string | Source column |
| Discount Class Code | string | Source column |
| Discount Class Description | string | Source column |
| Commission Class Code | string | Source column |
| Commission Class Description | string | Source column |
| Freight Class Code | string | Source column |
| Freight Class Description | string | Source column |
| Country of Origin | string | Source column |
| CEX Code | string | Source column |
| Commodity Item | boolean | Source column |
| Market Introduced At | string | Source column |
| Market Begin Date | dateTime | Source column |
| Market End Date | dateTime | Source column |
| Initial Invoice Period | string | Source column |
| Initial Invoice Qty | double | Source column |
| Merchandising Category | int64 | Source column |
| Child Style Description | string | Source column |
| Parent Style Description | string | Source column |
| Price Point | int64 | Source column |
| Item Code | string | Source column |
| Association Code | string | Source column |
| Default Group | boolean | Source column |
| Sellable Item Flag | string | Source column |
| ExpressShipFlag | string | Source column |
| F123 Product Flag | boolean | Source column |
| HS Core Product Flag | boolean | Source column |
| HS Proprietary Product Flag | boolean | Source column |
| HS Exclusive Flag | boolean | Source column |
| Berkline Product Flag | boolean | Source column |
| Benchcraft Product Flag | boolean | Source column |
| New Millennium Product Flag | boolean | Source column |
| Bardini Product Flag | boolean | Source column |
| Shanghai Store | boolean | Source column |
| Price Point Rating | string | Source column |
| Main Piece | string | Source column |
| Current SCP Manufacturing Status | string | Source column |
| General Description Code | double | Source column |
| General Description | string | Source column |
| ConsumerChoiceFlag | string | Source column |
| Item Ext Series Number | string | Source column |
| Hold Buy Code | string | Source column |
| Showroom | string | Source column |
| Secondary Planner | string | Source column |
| Series Desc | string | Calculated: `CONCATENATE(z_ProductDetails[Series Number],CONCATENATE(" - ", z_ProductDetails[Series Name]))` |
| ItemSKU Desc | string | Calculated: `CONCATENATE(z_ProductDetails[Item SKU],CONCATENATE(" - ",z_ProductDetails[Item Description]))` |
| z_LeatherFlag | string | Calculated SWITCH on Item Class Code to classify leather FG vs. UN items |

---

### z_WarehouseMaster

**Source type:** PowerBI Dataflow

*(Source: workspace a47e4573-c455-40af-a9ad-e22c81a07926, dataflow 346f2aa1-dd50-4c11-9630-b17f75854663, entity WarehouseMaster)*

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Warehouse | string | Source column — warehouse code (join key) |
| Warehouse Location | string | Source column |
| Warehouse Name | string | Source column |
| Warehouse Order Group | string | Source column |
| Intransit Warehouse | string | Source column |
| Container Direct Warehouse | string | Source column |
| Controlled Warehouse | boolean | Source column |
| AFIWarehousesKey | int64 | Source column |
| Warehouse Group | string | Source column |
| Site ID | string | Source column |
| Sort By | int64 | Source column |

---

### _Measures

**Source type:** In-memory placeholder (no real data — single-row stub table used to host measures)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| z_Measures | string | Source column — placeholder, always empty |

*(All 14 measures are defined on this table)*
