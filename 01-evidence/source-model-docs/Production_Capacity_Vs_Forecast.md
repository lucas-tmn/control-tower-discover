---
model_name: Production Capacity Vs Forecast
server: ashley-edw.database.windows.net
database: ashley_edw
table_count: 10
measure_count: 10
non_warehouse_sources: yes
non_warehouse_source_types: PowerBI Dataflows
---

# Business Context

This model tracks demand forecasts against production and procurement capacity across Ashley's supply chain. It compares forecasted quantities (by item, warehouse, and production resource) with actual manufacturing orders (MOs), purchase orders (POs), and receipts to help planners identify where supply exceeds or falls short of demand. The model focuses on "Z" class products and includes planned supply from both internal manufacturing and external vendors, enabling analysis of production bottlenecks and capacity utilization by location and timeframe.

## Relationships

| From | To |
| --- | --- |
| z_ItLocPr.Location | z_LocMaster.Location |
| Forecast.Key | z_ItLocPr.Key |
| MOrds.Key | z_ItLocPr.Key |
| z_ItLocPr.Item | z_ProductDetails.'Item SKU' |
| Receipts.Key | z_ItLocPr.Key |
| Forecast.FiscalWeekLastDate | z_FiscalCal.'Transaction Date' |
| Receipts.FiscalWeekLastDate | z_FiscalCal.'Transaction Date' |
| PlandSupply.Key | z_ItLocPr.Key |
| PlandSupply.DueDate | z_FiscalCal.'Transaction Date' |
| MOrds.DueDate | z_FiscalCal.'Transaction Date' |
| POrds.Key | z_ItLocPr.Key |
| POrds.DueDateWeekEnding | z_FiscalCal.'Transaction Date' |

*Only non-date-table relationships listed.*

## Measures

### Receipts

- Total received quantity across all receipt types.  
`CALCULATE(SUM(Receipts[Trans Qty]))`

### PO Receipts

- Purchased order receipts (Rec Code RP).  
`CALCULATE(SUM(Receipts[Trans Qty]),Receipts[Rec Code]="RP")`

### MO Receipts

- Manufacturing order receipts (Rec Code RM).  
`CALCULATE(SUM(Receipts[Trans Qty]),Receipts[Rec Code]="RM")`

### Firm MO

- Total quantity of active manufacturing orders.  
`CALCULATE(SUM(MOrds[Qty MO]))`

### Firm PO

- Total quantity of active purchase orders.  
`CALCULATE(SUM(POrds[Qty PO]))`

### Plan MO

- Planned quantity for manufacturing.  
`CALCULATE(SUM(PlandSupply[PlnQty]), PlandSupply[OrdType]="Makes")`

### Plan PO

- Planned quantity for purchases.  
`CALCULATE(SUM(PlandSupply[PlnQty]), PlandSupply[OrdType]="Buys")`

### Fcst

- Total forecasted quantity.  
`CALCULATE(SUM(Forecast[Tot Qty]))`

### MO Total

- Combined manufacturing receipts, orders, and planned.  
`[MO Receipts]+[Firm MO]+[Plan MO]`

### Total PO Qty

- Combined purchase receipts, orders, and planned.  
`[PO Receipts]+[Firm PO]+[Plan PO]`

## Tables

### Forecast

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item SKU | string | Source column |
| Warehouse | string | Source column |
| MBX | string | Make/Buy code indicator |
| FiscalWeekLastDate | dateTime | Source column |
| Ind Qty | int64 | Independent demand forecast quantity |
| Dep Qty | int64 | Dependent demand forecast quantity |
| Tot Qty | int64 | Total forecast quantity |
| SnapshotDate | dateTime | Date of forecast snapshot |
| ProdSource | string | Production source identifier |
| ProductionResource | string | Specific production resource or location |
| Key | string | Calculated: `TRIM(Forecast[Item SKU])&"_"&TRIM(Forecast[ProdSource])` |

**Source Query:**

```sql
SELECT [ITWH].[Item SKU]
      ,[ITWH].[Warehouse]
      ,[ITWH].[MBX]
      ,[ITWH].[Source]
      ,[ITWH].[ProdSource]
      ,[DD].[FiscalMonthLastDate]
      ,[DD].[FiscalMonthYear] 
INTO #MBX
  FROM (

SELECT DISTINCT RTRIM([DIN].[dinItem]) AS [Item SKU]
      ,RTRIM([DIN].[dinWarehouse]) AS [Warehouse]
	  ,RTRIM([DIN].[dinMakeBuyCode]) AS [MBX]
	  ,RTRIM([DIN].[dinSource1]) AS [Source]
	  ,CASE 
		WHEN [DIN].[dinMakeBuyCode] IN ('M','X')
			THEN RTRIM([DIN].[dinSource1])
		WHEN [DIN].[dinMakeBuyCode] = 'B'
			THEN RTRIM([CPD].[Primary Vendor])

		END AS [ProdSource]
  FROM [SupplyChain_Enh].[DemandInventorySnapshot] AS DIN
  INNER JOIN [SupplyChain_DW].[DimCurrentProductDetails] AS CPD
  ON [DIN].[dinItem] = [CPD].[Item SKU]
    AND LEFT([CPD].[Item Class Code], 1) = 'Z'
	AND RIGHT(RTRIM([CPD].[Item Class Code]),1) <> 'K'

  WHERE [DIN].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[DemandInventorySnapshot])
  ) AS ITWH
  CROSS JOIN (
SELECT DISTINCT [FiscalMonthLastDate], [FiscalMonthYear] 
  FROM [Enterprise_DW].[DimDate]
  WHERE [FiscalMonthIndicator] BETWEEN 0 AND 11
  ) AS DD


SELECT [M1].[Item SKU]
      ,[M1].[Warehouse]
      ,[M1].[MBX]
      ,[M1].[Source]
      ,[M1].[ProdSource]
      ,[M1].[FiscalMonthLastDate]
      ,[M1].[FiscalMonthYear]
	  ,ISNULL(SUM([DFC].[dfcResultantForecast]+[DFC].[dfcPromotionalLift]),0) AS [Qty]
      ,CONVERT(DATE, (SELECT MAX([dfcSnapshot]) FROM [SupplyChain_Enh].[DemandForecastSnapshot])) AS [SnapshotDate]
INTO #MBX2
  FROM [#MBX] AS M1
  LEFT JOIN [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC
    ON [M1].[Item SKU] = [DFC].[dfcItem]
	  AND [M1].[Warehouse] = [DFC].[dfcWarehouse]
	  AND [M1].[FiscalMonthYear] = [DFC].[dfcFiscalMonth]
	  AND [DFC].[dfcSnapshot] = (SELECT MAX([dfcSnapshot]) FROM [SupplyChain_Enh].[DemandForecastSnapshot])

GROUP BY [M1].[Item SKU]
        ,[M1].[Warehouse]
        ,[M1].[MBX]
        ,[M1].[Source]
        ,[M1].[ProdSource]
        ,[M1].[FiscalMonthLastDate]
        ,[M1].[FiscalMonthYear]


SELECT [M2].[Item SKU]
      ,[M2].[Warehouse]
      ,[M2].[MBX]
      ,[M2].[Source]
	  ,[M2].[ProdSource]
      ,[M2].[FiscalMonthYear]
	  ,[DD].[FiscalWeekLastDate]
	  ,CONVERT(NUMERIC, [M2].[Qty]/[DD].[WeeksinMonth]) AS [Qty]
      ,[M2].[SnapshotDate] 
INTO #FC
  FROM [#MBX2] AS M2
  LEFT JOIN ( 
SELECT DISTINCT [DD].[FiscalWeekLastDate]
	  ,[DD].[FiscalMonthYear]
	  ,[W].[WeeksinMonth]
  FROM [Enterprise_DW].[DimDate] AS DD
  LEFT JOIN (

SELECT [FiscalMonthYear]
      ,COUNT(DISTINCT [FiscalWeekLastDate]) AS [WeeksinMonth]
  FROM [Enterprise_DW].[DimDate]
  WHERE [FiscalMonthIndicator] BETWEEN 0 AND 11

  GROUP BY [FiscalMonthYear]
  ) AS W
  ON [DD].[FiscalMonthYear] = [W].[FiscalMonthYear]
  WHERE [DD].[FiscalMonthIndicator] BETWEEN 0 AND 11

  ) AS DD 
  ON [M2].[FiscalMonthYear] = [DD].[FiscalMonthYear]


SELECT [IND].[Item SKU]
      ,[IND].[Warehouse]
      ,[IND].[MBX]
	  ,[IND].[ProdSource]
	  ,ISNULL([P].[ProductionResource],RTRIM([IND].[ProdSource])+'-PROD') AS [ProductionResource]
      ,[IND].[FiscalWeekLastDate]
      ,ISNULL([IND].[Qty],0) AS [Ind Qty]
	  ,ISNULL([DEP].[Dep Qty],0) AS [Dep Qty]
	  ,ISNULL([IND].[Qty],0)+ISNULL([DEP].[Dep Qty],0) AS [Tot Qty]
      ,[IND].[SnapshotDate] 
  FROM [#FC] AS IND
  LEFT JOIN ( 
SELECT [Item SKU]
      ,[ProdSource]
      ,[FiscalWeekLastDate]
      ,SUM([Qty]) AS [Dep Qty]
  FROM [#FC]
  WHERE [MBX] = 'X'
  GROUP BY [Item SKU]
          ,[ProdSource]
          ,[FiscalWeekLastDate]
  ) AS DEP
  ON [IND].[Item SKU] = [DEP].[Item SKU]
  AND [IND].[Warehouse] = [DEP].[ProdSource]
  AND [IND].[FiscalWeekLastDate] = [DEP].[FiscalWeekLastDate]

  LEFT JOIN (
SELECT DISTINCT [PRP].[Item]
      ,[PRP].[Location]
      ,[PRP].[ProductionResource]
  FROM [SupplyChain_Enh].[ProductionResourcePlan] AS PRP
  WHERE [PRP].[SnapshotDate]  = (SELECT MAX([SnapshotDate]) FROM [SupplyChain_Enh].[ProductionResourcePlan])
    --AND [PRP].[Item] = '4060438'
  ) AS P
  ON [IND].[Item SKU] = [P].[Item]
  AND [IND].[ProdSource] = [P].[Location]

  WHERE [IND].[MBX] IN ('M','B')
    AND (ISNULL([IND].[Qty],0)+ISNULL([DEP].[Dep Qty],0)) > 0



DROP TABLE [#MBX]
DROP TABLE [#MBX2]
DROP TABLE [#FC]
```

---

### MOrds

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ItemSKU | string | Source column |
| Warehouse | string | Manufacturing location |
| DueDate | dateTime | Order due date |
| Qty MO | int64 | Manufacturing order quantity |
| Key | string | Calculated: `TRIM(MOrds[ItemSKU])&"_"&TRIM(MOrds[Warehouse])` |

**Source Query:**

```sql
SELECT RTRIM([MOM].[FITEM]) AS [ItemSKU]
      ,RTRIM([MOM].[FITWH]) AS [Warehouse]
      ,[DD].[DateID] AS [DueDate]
      ,SUM([MOM].[ORQTY]) AS [Qty MO]
  FROM [Manufacturing_ProductionPlanning_AFI].[MOMAST] AS MOM
  LEFT JOIN [Enterprise_DW].[DimDate] AS DD 
    ON [MOM].[ODUDT] = [DD].[MapicsDate]
  WHERE LEFT([MOM].[ITCL],1) = 'Z'
    AND RIGHT(RTRIM([MOM].[ITCL]),1) <> 'K'
	AND [MOM].[OSTAT] < 40
 GROUP BY RTRIM([MOM].[FITEM])
         ,RTRIM([MOM].[FITWH])
         ,[DD].[DateID]
```

---

### POrds

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ItemSKU | string | Source column |
| VendorNumber | string | Vendor/supplier identifier |
| DueDateWeekEnding | dateTime | Purchase order due date (week ending) |
| Qty PO | int64 | Purchase order quantity |
| Key | string | Calculated: `TRIM(POrds[ItemSKU])&"_"&TRIM(POrds[VendorNumber])` |

**Source Query:**

```sql
SELECT [PO].[ItemSKU]
      ,[PO].[VendorNumber]
	  ,[PO].[DueDateWeekEnding]
	  ,SUM([PO].[QtyOrdered]) AS [Qty PO]
  FROM [PowerBI_SupplyChain].[SCPPurchaseOrders_AFI] AS PO
 
  WHERE LEFT([PO].[ItemClass],1) = 'Z'
    AND RIGHT(RTRIM([PO].[ItemClass]),1) <> 'K'
	AND [PO].[PODetailStatusCode] < 40
	AND [PO].[Warehouse] <> '55'

	GROUP BY [PO].[ItemSKU]
            ,[PO].[VendorNumber]
            ,[PO].[DueDateWeekEnding]
```

---

### Receipts `table`

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item SKU | string | Source column |
| Location | string | Receiving location (warehouse or vendor) |
| Rec Code | string | Receipt code (RM for manufacturing, RP for purchase) |
| FiscalWeekLastDate | dateTime | Fiscal week ending date of receipt |
| Trans Qty | int64 | Transaction/receipt quantity |
| Key | string | Calculated: `TRIM(Receipts[Item SKU])&"_"&TRIM(Receipts[Location])` |

**Source Query:**

```sql
SELECT RTRIM([IM].[ITNBR]) AS [Item SKU]
      ,RTRIM([IM].[HOUSE]) AS [Location]
	  ,RTRIM([IM].[TCODE]) AS [Rec Code]
	  ,[DD].[FiscalWeekLastDate]
      ,SUM([IM].[TRQTY]) AS [Trans Qty]
      
  FROM [Manufacturing_Inventory_AFI].[IMHIST] AS IM
  INNER JOIN [Enterprise_DW].[DimDate] AS DD 
    ON [IM].[TRNDT] = [DD].[MapicsDate]
	AND [DD].[FiscalWeekIndicator] > -14 
	AND [DD].[FiscalDateIndicator] < 0 
  INNER JOIN [MasterData_ItemMaster_AFI].[ITMEXT] AS EXT
    ON [IM].[ITNBR] = [EXT].[ITNBR]
	AND LEFT([EXT].[ITMITCLS],1) = 'Z'
    AND RIGHT(RTRIM([EXT].[ITMITCLS]),1) <> 'K'
  WHERE [IM].[TCODE] = 'RM' 

	GROUP BY RTRIM([IM].[ITNBR])
            ,RTRIM([IM].[HOUSE])
		,RTRIM([IM].[TCODE])
            ,[DD].[FiscalWeekLastDate]

UNION 

SELECT RTRIM([IM].[ITNBR]) AS [Item SKU]
      ,RTRIM([IM].[VNDNR]) AS [Location]
	  ,RTRIM([IM].[TCODE]) AS [Trans Code]
	  ,[DD].[FiscalWeekLastDate]
      ,SUM([IM].[TRQTY]) AS [Rec Qty]
      
  FROM [Manufacturing_Inventory_AFI].[IMHIST] AS IM
  INNER JOIN [Enterprise_DW].[DimDate] AS DD 
    ON [IM].[TRNDT] = [DD].[MapicsDate]
	AND [DD].[FiscalWeekIndicator] > -14 
	AND [DD].[FiscalDateIndicator] < 0 
  INNER JOIN [MasterData_ItemMaster_AFI].[ITMEXT] AS EXT
    ON [IM].[ITNBR] = [EXT].[ITNBR]
	AND LEFT([EXT].[ITMITCLS],1) = 'Z'
    AND RIGHT(RTRIM([EXT].[ITMITCLS]),1) <> 'K'
  WHERE [IM].[TCODE] = 'RP' --IN ('IA','IP','IS','IW','IX','RC','RM','RP','RW','SA','SM','SS','VR')
    AND [IM].[HOUSE] <> '55'

	GROUP BY RTRIM([IM].[ITNBR])
            ,RTRIM([IM].[VNDNR]) 
		,RTRIM([IM].[TCODE])
            ,[DD].[FiscalWeekLastDate]
```

---

### PlandSupply

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Key | string | Composite key: Item SKU + Location |
| Item SKU | string | Source column |
| Location | string | Vendor number (for buys) or warehouse (for makes) |
| DueDate | dateTime | Due/week ending date |
| PlnQty | int64 | Planned quantity |
| OrdType | string | Order type (Makes or Buys) |
| SnapshotDate | dateTime | Date of planning snapshot |

**Source Query:**

```sql
SELECT RTRIM([PRQ].[prqItemSKU])+'_'+RTRIM([PRQ].[prqVendorNum]) AS [Key]
      ,RTRIM([PRQ].[prqItemSKU]) AS [Item SKU]
      ,RTRIM([PRQ].[prqVendorNum]) AS [Location]
      ,[PRQ].[prqDueDate] AS [DueDate]
      ,SUM([PRQ].[prqQuantity]) AS [PlnQty]
	  ,'Buys' AS [OrdType]
	  ,CONVERT(DATE,[PRQ].[dtea]) AS [SnapshotDate]
  FROM [SupplyChain_Enh].[PlannedRequirementsLogility] AS PRQ
  INNER JOIN [SupplyChain_DW].[DimCurrentProductDetails] AS CPD
  ON [PRQ].[prqItemSKU] = [CPD].[Item SKU]
    AND LEFT([CPD].[Item Class Code], 1) = 'Z'
	AND RIGHT(RTRIM([CPD].[Item Class Code]),1) <> 'K'
  WHERE [PRQ].[dtea] = (SELECT MAX([dtea]) FROM [SupplyChain_Enh].[PlannedRequirementsLogility])
    --AND [PRQ].[prqItemSKU] = '1964077'

	GROUP BY RTRIM([PRQ].[prqItemSKU])
            ,RTRIM([PRQ].[prqVendorNum])
            ,[PRQ].[prqDueDate]
		,[PRQ].[dtea]

UNION

SELECT RTRIM([SPD].[spdItem])+'_'+RTRIM([SPD].[spdWarehouse]) AS [Key]
      ,[SPD].[spdItem] AS [Item SKU]
      ,[SPD].[spdWarehouse] AS [Location]
      ,[SPD].[spdWeekEnding] AS [DueDate]
	  ,SUM([SPD].[spdPlannedProduction]) AS [PlnQty]
	  ,'Makes' AS [OrdType]
      
	  ,CONVERT(DATE, [SPD].[dtea]) AS [SnapshotDate]
  FROM [Wholesale_DemandPlanning_AFI].[SupplyPlanDetail] AS SPD
  INNER JOIN [SupplyChain_DW].[DimCurrentProductDetails] AS CPD
    ON [SPD].[spdItem] = [CPD].[Item SKU]
    AND LEFT([CPD].[Item Class Code], 1) = 'Z'
	AND RIGHT(RTRIM([CPD].[Item Class Code]),1) <> 'K'
    WHERE CONVERT(date,[SPD].[dtea]) = (SELECT MAX(CONVERT(date,[dtea])) FROM [Wholesale_DemandPlanning_AFI].[SupplyPlanDetail])
    
	GROUP BY CONVERT(DATE, [SPD].[dtea])
            ,[SPD].[spdItem]
            ,[SPD].[spdWarehouse]
            ,[SPD].[spdWeekEnding]
```

---

### z_ItLocPr

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item | string | Source column |
| Location | string | Location identifier |
| ProductionResource | string | Production resource or location-based default |
| Key | string | Calculated: `TRIM(z_ItLocPr[Item])&"_"&TRIM(z_ItLocPr[Location])` |
| z_Filter | boolean | Calculated filter: `([Fcst]+[Receipts]+[Plan MO]+[Plan PO])>0` |

**Source Query:**

```sql
SELECT [PO].[Item]
      ,[PO].[Location]
	  ,COALESCE([P].[ProductionResource],RTRIM([PO].[Location])+'-PROD') AS [ProductionResource]
  FROM (

SELECT DISTINCT [poditemnum] AS [Item]
      ,[podvendornum] AS [Location]
  FROM [Wholesale_ProductSourcing_AFI].[PoDetail]
  WHERE LEFT([poditemclass], 1) = 'Z'
	AND RIGHT(RTRIM([poditemclass]),1) <> 'K'
	AND [podduedate] > DATEADD(MONTH, -18, GETDATE())
	AND [podwarehouse] <> '55'

UNION 

SELECT DISTINCT [PRP].[Item]
      ,[PRP].[Location]
	  --,MAX([PRP].[SnapshotDate]) AS [MaxDate]
  FROM [SupplyChain_Enh].[ProductionResourcePlan] AS PRP
  WHERE [PRP].[SnapshotDate] > DATEADD(MONTH, -18, GETDATE())
	) AS PO

  LEFT JOIN (
SELECT DISTINCT [PRP].[Item]
      ,[PRP].[Location]
      ,[PRP].[ProductionResource] 
--INTO #PRP
  FROM [SupplyChain_Enh].[ProductionResourcePlan] AS PRP
  INNER JOIN (
SELECT [PRP].[Item]
      ,[PRP].[Location]
	  ,MAX([PRP].[SnapshotDate]) AS [MaxDate]
  FROM [SupplyChain_Enh].[ProductionResourcePlan] AS PRP
  WHERE [PRP].[SnapshotDate] > DATEADD(MONTH, -18, GETDATE())
  
  GROUP BY [PRP].[Item]
          ,[PRP].[Location]
		) AS PM
  ON [PRP].[Item] = [PM].[Item]
    AND [PRP].[Location] = [PM].[Location]
	AND [PRP].[SnapshotDate] = [PM].[MaxDate]
  ) AS P
  ON [PO].[Item] = [P].[Item]
  AND [PO].[Location]= [P].[Location]

  --WHERE [P].[ProductionResource] IS NULL
```

---

### z_LocMaster

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Location | string | Source column |
| Name | string | Vendor name or warehouse location name |
| Loc Desc | string | Location description (concatenated code and name) |
| Source Type | string | Classification: Domestic, WNK/MILL, or Int Vendor |
| z_LocFilter | boolean | Calculated filter: `([Fcst]+[Receipts]+[Plan MO]+[Plan PO])>0` |
| Test | int64 | Calculated sum: `([Fcst]+[Receipts]+[Plan MO]+[Plan PO])` |

**Source Query:**

```sql
SELECT [VendorNumber] AS [Location]
      ,[VendorName] AS [Name]
	  ,CONCAT(RTRIM([VendorNumber]),' - ',RTRIM([VendorName])) AS [Loc Desc]
	  ,CASE
		WHEN [VendorNumber] IN ('900515','900639','600039','624556')
			THEN 'WNK/MILL'
		ELSE 'Int Vendor'
		END AS [Source Type]

  FROM [PowerBI_SupplyChain].[VendorMaster]

UNION 

SELECT S.[Warehouse Code] AS [Location]
	  ,S.[Warehouse Location] AS [Name]
	  ,CONCAT(RTRIM(S.[Warehouse Code]),' - ', RTRIM(S.[Warehouse Location])) AS [Loc Desc]
	  ,'Domestic' AS [Source Type]

  FROM [SupplyChain_DW].[DimAFIWarehouses] AS S
  WHERE S.[Warehouse Code] IN ('1','15','17','28','ECR','101','12','19','201')
```

---

### z_ProductDetails

**Source type:** PowerBI Dataflows (CurrentProductDetails)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item SKU | string | Source column |
| Item Description | string | Source column |
| Colors | string | Source column |
| Series Number | string | Source column |
| Series Name | string | Source column |
| Series Color | string | Source column |
| Item Grouping | string | Source column |
| Item Class Code | string | Source column |
| Item Class Name | string | Source column |
| Collective Class Code | string | Source column |
| Collective Class | string | Source column |
| Responsible Office | string | Source column |
| Product Line | string | Source column |
| Retail Category Code | string | Source column |
| Retail Category Description | string | Source column |
| AFI Finance Division | string | Source column |
| AFI Sales Division Code | string | Source column |
| AFI Sales Division | string | Source column |
| AFI Sales Category Code | string | Source column |
| AFI Sales Category | string | Source column |
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
| Series Desc | string | Calculated: `CONCATENATE(z_ProductDetails[Series Number],CONCATENATE(" - ", z_ProductDetails[Series Name]))` |
| ItemSKU Desc | string | Calculated: `CONCATENATE(z_ProductDetails[Item SKU],CONCATENATE(" - ",z_ProductDetails[Item Description]))` |
| ItemSKU Description | string | Source column |
| Series Description | string | Source column |
| Ext Series Number | string | Source column |
| Ext Series Description | string | Source column |
| HSExclusiveFlag | boolean | Source column |
| ContainerVolume | double | Source column |
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
| Secondary Planner | string | Source column |
| Showroom | string | Source column |

---

### z_FiscalCal

**Source type:** PowerBI Dataflows (AshleyFiscalCalendarV2)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Transaction Date | dateTime | Key column; fiscal calendar anchor date |
| Fiscal Year | int64 | Source column |
| Calendar Year | int64 | Source column |
| Integer Date | int64 | Source column |
| Mapics Date | int64 | Source column for joining to legacy systems |
| Day of Week | string | Source column |
| Fiscal Week Num | int64 | Source column |
| FW Desc | string | Source column |
| Fiscal Year Week Num | int64 | Source column |
| Fiscal Month Num | int64 | Source column |
| FM Desc | string | Source column |
| Fiscal Month Name | string | Source column |
| Fiscal Year Month Num | int64 | Source column |
| Fiscal Month Year Desc | string | Source column |
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
| Fiscal Day Indicator | int64 | Source column |
| Fiscal Week Indicator | int64 | Source column |
| Fiscal Month Indicator | int64 | Source column |
| Fiscal Quarter Indicator | int64 | Source column |
| Fiscal Year Indicator | int64 | Source column |
