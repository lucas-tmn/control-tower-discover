---
model_name: Rolling Report - Wanek Millen
server: Ashley-edw.database.windows.net
database: ASHLEY_EDW
table_count: 5
measure_count: 5
non_warehouse_sources: yes
non_warehouse_source_types: iSeries ODBC
---

# Business Context

This report tracks purchase order rolling activity and firm commitments across warehouses for specific vendors (600039, 900515, 900639, 624556), focusing on finished goods and repair parts (RP). The model compares firm quantities (FQty) against rolled quantities to measure compliance, calculates safety stock percentages (SS%), and monitors late ASN (Advanced Ship Notices) arriving on Monday–Tuesday. The report appears to support supply chain visibility and demand planning by measuring the percentage of orders held firm versus those that were rolled to later ETDs, with a secondary lens on late shipment arrivals relative to planned ETDs.

## Relationships

| From | To |
| --- | --- |
| Firm and Roll.Key | Late ASN.Key |

## Measures

### %Rolled

- Average percentage of firm orders rolled across items and warehouses.

```dax
AVERAGEX(SUMMARIZE('Firm and Roll','Firm and Roll'[Item],'Firm and Roll'[Whse],"RolledQty", SUM('Firm and Roll'[Roll Quantity]),"TotalFQty", SUM('Firm and Roll'[FQty])),If( [RolledQty] = 0,0,IF([RolledQty] > [TotalFQty], 1, DIVIDE([RolledQty], [TotalFQty]))))
```

### RollafterLateASN

- Rolled quantity after accounting for late ASN shipments (Mon+Tue).

```dax
VAR SummarizedTable = SUMMARIZE('Firm and Roll','Firm and Roll'[Item],'Firm and Roll'[ETD Date],"RolledQty", SUM('Firm and Roll'[Roll Quantity]),"Monship", SUM('Late ASN'[MonASN]),"TueShip", SUM('Late ASN'[TueASN])) RETURN SUMX(SummarizedTable,[RolledQty] - [Monship] - [TueShip])
```

### %Roll Average

- Average percentage rolled by item and ETD date.

```dax
AVERAGEX(SUMMARIZE('Firm and Roll','Firm and Roll'[Item],'Firm and Roll'[ETD Date],"RolledQty", SUM('Firm and Roll'[Roll Quantity]),"TotalFQty", SUM('Firm and Roll'[FQty]),If( [RolledQty] = 0,0,IF([RolledQty] > [TotalFQty], 1, DIVIDE([RolledQty], [TotalFQty])))))
```

### %RolledASN

- Average rolled percentage after late ASN by item and ETD.

```dax
AVERAGEX(SUMMARIZE('Firm and Roll','Firm and Roll'[Item],'Firm and Roll'[ETD Date],"RolledQty", [RollafterLateASN],"TotalFQty", SUM('Firm and Roll'[FQty]),IF([RolledQty] = 0, 0, IF([RolledQty] > [TotalFQty], 1, DIVIDE([RolledQty], [TotalFQty])))))
```

### SS% Average

- Average safety stock percentage across items, warehouses, and ETD dates.

```dax
AVERAGEX(SUMMARIZE('Firm and Roll','Firm and Roll'[Item],'Firm and Roll'[Whse],'Firm and Roll'[ETD Date],"%SS%Average", SUM('Firm and Roll'[SS%])),[%SS%Average]/100)
```

## Tables

### Firm and Roll

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item | string | Source column; item/SKU identifier |
| Whse | string | Source column; warehouse code |
| Vendor | string | Source column; vendor/supplier number |
| Series number | string | Source column |
| Collective Class | string | Source column |
| Division | string | Source column; AFI Finance Division |
| Current Status | string | Source column |
| Future Status | string | Source column |
| ITDESC | string | Source column; item description |
| VNAME | string | Source column; vendor name |
| ETD Date | dateTime | Source column; estimated time of delivery (formatted as short date) |
| FQty | double | Source column; firm quantity (sum aggregatable) |
| Roll Quantity | double | Source column; quantity rolled to later ETD (sum aggregatable) |
| SI | double | Source column; shippable inventory (sum aggregatable) |
| SS | double | Source column; safety stock (sum aggregatable) |
| SS% | double | Source column; safety stock percentage (sum aggregatable) |
| Item Check | string | Calculated: DAX logic to classify items as KIT & COMPONENTS or FG based on collective class, item name patterns (UN, numeric prefix), and vendor |
| SS% Final | double | Calculated: safety stock percentage only for the latest ETD per item/warehouse; otherwise 0 |
| latest SI | double | Calculated: shippable inventory for the latest ETD per item/warehouse; otherwise 0 |
| latest SS | double | Calculated: safety stock for the latest ETD per item/warehouse; otherwise 0 |
| Key | string | Calculated: composite key = Item & ETD Date & Vendor & Whse |
| ETD | string | Calculated: formatted ETD Date as mm/dd |
| New_Roll | double | Calculated: minimum of Roll Quantity and FQty; represents new rolling activity (sum aggregatable) |
| Old_Roll | double | Calculated: Roll Quantity minus New_Roll; represents historical rolling (sum aggregatable) |
| ITEMNO | string | Source column |
| ItemClass | string | Source column |
| Category | string | Calculated: LOOKUPVALUE from ItemMaster by item number |
| ProdResourceID | string | Source column; production resource identifier |
| Sellable Item Flag | string | Source column |
| Item Type | string | Calculated: DAX classification logic that returns FG, RP, Kits, or Components based on sellable flag, category, item name, resource ID, and item class lookups |
| ITEMCLAD | string | Calculated: LOOKUPVALUE from ItemVAL by item number |

**Source Query:**

```sql
--BẢNG LẤY SỐ FIRM CẢ RP VÀ FG#(lf)WITH FIRM AS (#(lf)  SELECT #(lf)    [Item], #(lf)    [Whse], #(lf)    [Vendor], #(lf)    [Series number], #(lf)    [Collective Class], #(lf)#(tab)[Sellable Item Flag],#(lf)    [AFI Finance Division] AS [Division], #(lf)    [Current Status], #(lf)    [Future Status], #(lf)    [ITDESC], #(lf)    [VNAME], #(lf)    [SPRunDate], #(lf)    Sum([FQty]) AS [FQty],  #(lf)    CAST(#(lf)      ([SPRunDate] + 14) AS DATE#(lf)    ) AS [ETD], #(lf)    DD.[CalendarWeekIndicator] #(lf)  FROM #(lf)    [SupplyChain_Enh].[PSWWeeklyExtractSnapshot] #(lf)    LEFT JOIN [Enterprise_DW].[DimDate] DD ON cast(DD.[DateID] as date) = cast([SPRunDate] as date)#(lf)    LEFT JOIN [PowerBI_SupplyChain].[CurrentProductDetails] ON [PowerBI_SupplyChain].[CurrentProductDetails].[Item Sku] = [Item] #(lf)  WHERE #(lf)    [Vendor] IN ( '600039', '900515', '900639', '624556') #(lf)    AND [WeekNum] = 2 --SỐ FIRM W3#(lf)    AND DD.[CalendarWeekIndicator] between -10 and -2 --LẤY DATA ĐẾN TUẦN HIỆN TẠI NÊN SNAPSHOT GẦN NHẤT LÀ TỪ 2 TUẦN TRC#(lf)    AND DD.[CalendarDayOfWeekName] = 'Saturday' --LẤY SNAPSHOT VÀO T7#(lf)#(tab)AND [SPRunDate] NOT Between '2025-02-28' and '2025-03-16'#(lf)    AND [Whse] NOT IN ('C', 'CNW', 'AF', 'IOR') --KO TÍNH ROLLING CHO C/CNW#(lf)    AND [Item] NOT LIKE '%SW' #(lf)#(tab)AND [Item] NOT LIKE '%CARD%'#(lf)#(tab)AND [Item] NOT LIKE '%VINYL%'#(lf)#(tab)AND [Item] NOT LIKE '%HIDES%' #(lf)#(tab)#(lf)  GROUP BY #(lf)    [Item], #(lf)    [Whse], #(lf)    [Vendor], #(lf)    [Series number], #(lf)    [Collective Class], #(lf)    [AFI Finance Division], #(lf)#(tab)[Sellable Item Flag],#(lf)    [Current Status], #(lf)    [Future Status], #(lf)    [ITDESC], #(lf)    [VNAME], #(lf)    [SPRunDate], #(lf)    CAST(#(lf)      ([SPRunDate] + 14) AS DATE#(lf)    ),#(lf)     DD.[CalendarWeekIndicator] #(lf)),#(lf)#(lf)#(lf)#(lf)#(lf)--LẤY THÔNG TIN ITEM, số lượng BỊ ROLL#(lf)ROLL AS (#(lf)    SELECT #(lf)        a.[poaItemNum],#(lf)        b.[pomvendornum],#(lf)        b.[pomwarehouse],#(lf)#(tab)#(tab)C.[FiscalWeekIndicator],#(lf)        CAST(b.[pometd] AS DATE) AS [ETD],  #(lf)        Sum(CAST(a.[poaPreviousValue] AS DECIMAL) - CAST(a.[poaValue] AS DECIMAL)) AS [Rolled Quantity]#(lf)    FROM #(lf)        [Wholesale_ProductSourcing_AFI].[PoAuditLog] a#(lf)    LEFT JOIN (#(lf)        SELECT DISTINCT #(lf)            [pomvendornum],#(lf)            [pomordernum],#(lf)            [pomwarehouse],#(lf)            [pometd]#(lf)        FROM #(lf)            [Wholesale_ProductSourcing_AFI].[PoMaster]#(lf)    ) b ON a.[poaOrderNum] = b.[pomordernum]#(lf)    INNER JOIN (#(lf)        SELECT * #(lf)        FROM #(lf)            [Enterprise_DW].[DimDate_NonRetail]#(lf)        WHERE #(lf)            [FiscalWeekIndicator] between -7 and 1#(lf)    ) c ON CAST(a.[poaDateTime] AS DATE) = c.DateID#(lf)    WHERE #(lf)        a.[poaApplication] = 'usp_SummaryPORollover'#(lf)        AND a.[poaFieldName] = 'podQtyOrdered'#(lf)        AND a.[poaTransactionType] = 'D'#(lf)#(tab)GROUP BY#(lf)#(tab)#(tab)a.[poaItemNum],#(lf)        b.[pomvendornum],#(lf)        b.[pomwarehouse],#(lf)#(tab)#(tab)C.[FiscalWeekIndicator],#(lf)        CAST(b.[pometd] AS DATE)#(lf)),#(lf)#(lf)#(lf)--BẢNG FINAL GỘP SỐ FIRM VÀ ROLL CỦA FG?#(lf)Final AS (#(lf)    SELECT  #(lf)        FIRM.[Item], #(lf)        FIRM.[Whse], #(lf)        FIRM.[Vendor], #(lf)#(tab)#(tab)FIRM.[Sellable Item Flag],#(lf)        FIRM.[Series number], #(lf)        FIRM.[Collective Class], #(lf)        FIRM.[Division], #(lf)        FIRM.[Current Status], #(lf)        FIRM.[Future Status], #(lf)        FIRM.[ITDESC], #(lf)        FIRM.[VNAME], #(lf)        FIRM.[ETD],#(lf)        FIRM.[FQty],#(lf)        ROLL.[Rolled Quantity], #(lf)#(tab)#(tab)SPD.[spdShippableInventory],#(lf)#(tab)#(tab)SPD.[spdSafetyStock],#(lf)#(tab)#(tab)CASE  when SPD.[spdSafetyStock]= 0 then SPD.[spdShippableInventory]*100/1#(lf)#(tab)#(tab)else SPD.[spdShippableInventory]*100/SPD.[spdSafetyStock] end AS [SS%]#(lf)    FROM #(lf)        FIRM#(lf)#(tab)#(tab)left join#(lf)        ROLL ON ROLL.[poaItemNum] = FIRM.[Item]#(lf)        AND ROLL.[pomvendornum] = FIRM.[Vendor]#(lf)        AND ROLL.[pomwarehouse] = FIRM.[Whse]#(lf)        AND ROLL.[ETD] = FIRM.[ETD]#(lf)    LEFT JOIN #(lf)        [Wholesale_DemandPlanning_AFI].[SupplyPlanDetail] SPD#(lf)#(tab)ON FIRM.[Item]= SPD.[spdItem]#(lf)#(tab)AND FIRM.[Whse]= SPD.[spdWarehouse]#(lf)#(tab)AND CAST(FIRM.[SPRunDate] AS Date) = Cast(SPD.[dtec] as Date)#(lf)#(tab)AND CAST(FIRM.[ETD] AS Date) = Cast(SPD.[spdWeekEnding] as Date)#(lf)#(tab)WHERE  NOT (FIRM.[FQty] = 0 AND ROLL.[Rolled Quantity] IS NULL)#(lf)),#(lf)#(lf)#(lf)--BẢNG LẤY SỐ ROLLING RP#(lf)RP AS (#(lf)    SELECT  distinct#(lf)        DT.[RPKEY], --RP Order number?#(lf)        DT.[ITEMNO], --RP##(lf)        DT.[QTY],  --Qty roll#(lf)        HD.[MODEL], --FG Item (end item)#(lf)        HD.[WHOSE] --WHSE #(lf)    FROM #(lf)        Supplychain_History.ARPDETAIL DT#(lf)    LEFT JOIN #(lf)        Wholesale_Quality_AFI.ARPHEADER HD ON HD.[RPKEY] = DT.[RPKEY]#(lf)),#(lf)#(lf)#(lf)#(lf)Resources as (SELECT ItemID, LocationID, ProdResourceID#(lf)FROM SupplyChain_Enh.ProductionConversion#(lf)WHERE [SnapshotDate] = (SELECT MAX([SnapshotDate]) AS LatestDate#(lf)    FROM SupplyChain_Enh.ProductionConversion)#(lf)AND [EndEffectiveDate] IS NOT NULL#(lf)  AND ([ProdResourceId] LIKE '600039%'#(lf)       OR [ProdResourceId] LIKE '900639%'#(lf)       OR [ProdResourceId] LIKE '624556%'#(lf)       OR [ProdResourceId] LIKE '900515%'))#(lf)#(lf)#(lf)#(lf)SELECT DISTINCT#(lf)    FINAL.*,#(lf)#(tab)RP.[ITEMNO],#(lf)#(tab)ITMBL.ItemClass,#(lf)#(tab)Resources.ProdResourceID,#(lf)#(tab)FINAL.[Sellable Item Flag],#(lf)#(tab)CASE#(lf)        WHEN RP.[ITEMNO] IS NOT NULL THEN 'RP'#(lf)        WHEN ITMBL.ItemClass IN ('CIRP', 'RPMT', 'RPRT', 'TA', 'UDRP', 'UERF', 'UIRP') THEN 'RP'#(lf)        WHEN FINAL.[ITEM] LIKE '%UN%' THEN 'Kit & Components'#(lf)        WHEN FINAL.[Collective Class] IS NULL THEN#(lf)            CASE#(lf)                WHEN FINAL.[ITEM] LIKE 'R%' THEN 'RP'#(lf)                WHEN ISNUMERIC(FINAL.Item) = 1 AND LEN(FINAL.Item) >= 9 THEN 'RP'#(lf)                ELSE 'Kit & Components'#(lf)            END#(lf)        ELSE 'FG'#(lf)    END AS [Item Category]   --Phân loại FG/ RP#(lf)#(lf)FROM #(lf)   FINAL#(lf)#(tab)LEFT JOIN #(lf)    RP ON#(lf)#(tab)FINAL.[Item] = RP.[ITEMNO]#(lf)#(tab)AND FINAL.[Whse] = RP.[WHOSE]#(lf)#(tab)left join [MasterData_ItemMaster_AFI].[ITMBL] ITMBL#(lf)#(tab)on Final.Item = ITMBL.ItemNumber#(lf)#(tab)AND Final.[Whse] = ITMBL.Warehouse#(lf)#(tab)LEFT JOIN Resources#(lf)#(tab)ON FINAL.Item = Resources.ItemID#(lf)#(tab)AND FINAL.Vendor = Resources.LocationID
```

---

### Late ASN

**Source type:** Warehouse

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| poaItemNum | string | Source column; item number from PO audit log |
| podvendornum | string | Source column; vendor number |
| podwarehouse | string | Source column; warehouse code |
| ETD | dateTime | Source column; estimated time of delivery (formatted as long date) |
| MonASN | double | Source column; ASN (Advanced Ship Notice) quantity arriving on Monday (sum aggregatable) |
| TueASN | double | Source column; ASN quantity arriving on Tuesday (sum aggregatable) |
| Key | string | Calculated: composite key = poaItemNum & ETD & podvendornum & podwarehouse |

**Source Query:**

```sql
WITH LATEASN AS (SELECT #(lf)        a.[poaItemNum],#(lf)#(tab)#(tab)a.[poaordernum],#(lf)        POD.[podvendornum],#(lf)        POD.[podwarehouse],#(lf)        CAST(DATEADD(DAY, - DATEPART(WEEKDAY,a.[poaDateTime] ),a.[poaDateTime] )as Date) AS [ETD], #(lf)#(tab)#(tab)DD.[CalendarDayOfWeekName],#(lf)#(tab)#(tab)CAST(a.[poaValue] AS DECIMAL) [Qty]#(lf)    FROM #(lf)        [Wholesale_ProductSourcing_AFI].[PoAuditLog] a#(lf)    LEFT JOIN #(lf)            [Wholesale_ProductSourcing_AFI].[PoDetail] POD ON (a.[poaOrderNum] = POD.[podordernum] AND a.[poaItemnum] = POD.[poditemnum])#(lf)    LEFT JOIN [Enterprise_DW].[DimDate] DD#(lf)#(tab)#(tab)ON cast(a.[poaDateTime]as Date) = CAST(DD.[DateID] as Date)#(lf)WHERE #(lf)        [poaaction] = 'S'#(lf)#(tab)#(tab)and [poaFieldName] ='podQtyOrdered'#(lf)#(tab)#(tab)and [poatransactiontype] = 'A'#(lf)#(tab)#(tab)AND DD.[CalendarWeekIndicator] BETWEEN -8 AND 0#(lf)#(tab)#(tab)AND DD.[CalendarDayOfWeekName] IN ('Monday','Tuesday')),#(lf)#(lf)Final as (SELECT #(lf)poaItemNum,#(lf)podvendornum,#(lf)podwarehouse,#(lf)ETD,#(lf)CalendarDayOfWeekName,#(lf)Sum(Qty) as LateQty#(lf)FROM LateASN#(lf)WHERE podvendornum in ('600039', '900515', '900639', '624556')#(lf)GROUP BY #(lf)poaItemNum,  #(lf)podvendornum,#(lf)podwarehouse,#(lf)ETD,#(lf)CalendarDayOfWeekName)#(lf)#(lf)SELECT #(lf)poaItemNum,#(lf)podvendornum,#(lf)podwarehouse,#(lf)ETD,#(lf)Max(CASE WHEN CalendarDayOfWeekName ='Monday' THEN LateQty ELSE 0 END) AS 'MonASN',#(lf)max(CASE WHEN CalendarDayOfWeekName ='Tuesday' THEN LateQty ELSE 0 END) AS 'TueASN'#(lf)FROM Final#(lf)group by #(lf)poaItemNum,#(lf)podvendornum,#(lf)podwarehouse,#(lf)ETD
```

---

### ItemMaster

**Source type:** iSeries ODBC

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ITEM | string | Source column; item/SKU identifier |
| CATEGORY | string | Source column; item category classification |
| MATERIAL_TYPE | string | Source column; material type |
| STYLE_TYPE | string | Source column; style type classification |
| JUMBO_STD | double | Source column; jumbo standard (sum aggregatable) |
| SEW_STD | double | Source column; sewing standard (sum aggregatable) |
| UPH_STD | double | Source column; units per hour standard (sum aggregatable) |
| ITEM_TYPE | string | Source column; item type classification |

**Source Expression:**

ODBC connection to iSeries system (AFIPROD) accessing `ADOWNLOAD.ITEMMASTERL01` table with column trimming transformation applied.

---

### ItemVAL

**Source type:** iSeries ODBC

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ITNOAD | string | Source column; item number |
| ITCLAD | string | Source column; item class code |

**Source Expression:**

ODBC connection to iSeries system (AFIPROD) accessing `AMFLIBA.ITMRVAL0` table.

---

### Latest Update

**Source type:** Warehouse (metadata table)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| tpkServerName | string | Source column |
| tpkDatabaseName | string | Source column |
| tpkSchemaName | string | Source column |
| tpkTableName | string | Source column |
| tpkObjectType | string | Source column |
| tpkPrimaryKey | string | Source column |
| tpkAlternateKey | string | Source column |
| tpkStorageType | string | Source column |
| tpkRowSToreClusteredKey | string | Source column |
| tpkAdditionalIndexes | string | Source column |
| tpkDistributionKey | string | Source column |
| tpkIndexType | string | Source column |
| tpkSourceSystem | string | Source column |
| tpkSourceServer | string | Source column |
| tpkSourceDatabase | string | Source column |
| tpkSourceObject | string | Source column |
| tpkSourceObjectAlias | string | Source column |
| tpkSourcePlatform | string | Source column |
| tpkReplicatedSource | string | Source column |
| tpkETLTool | string | Source column |
| tpkPackageName | string | Source column |
| tpkTFSPath | string | Source column |
| tpkJobName | string | Source column |
| tpkJobServer | string | Source column |
| tpkRefreshRate | int64 | Source column |
| tpkRefreshDescription | string | Source column |
| tpkUpdateMethod | string | Source column |
| tpkExtractQuery | string | Source column |
| tpkUpdateQuery | string | Source column |
| tpkAdditionaNotes | string | Source column |
| tpkInvalidCount | double | Source column (sum aggregatable) |
| tpkRowCount | double | Source column (sum aggregatable) |
| tpkCreateDate | dateTime | Source column |
| tpkModified | dateTime | Source column |
| tpkCreatedBy | string | Source column |
| tpkModifiedBy | string | Source column |
| tpkLastAudit | dateTime | Source column |
| tpkErrorMsg | string | Source column |
| tpkCreatedDate | dateTime | Source column |
| tpkCreated | dateTime | Source column |
| tpkSourceObjectType | string | Source column |
| tpkPartitionKey | string | Source column |
| tpkColumnStatsCount | int64 | Source column |
| tpkColumnCount | int64 | Source column |
| tpkColumnStatsLastUpdated | dateTime | Source column |
| tpkDeletedRows | double | Source column (sum aggregatable) |
| tpkDataLake | string | Source column |
| tpkDataLakeFolder | string | Source column |
| tpkDataLakeFolderArchive | string | Source column |
| tpkReplicatedSourceExpiryHours | int64 | Source column |
| tpkReplicatedSourceArchiveExpiryHours | int64 | Source column |
| tpkStageDataLakeFolder | string | Source column |
| tpkLastBatchStartDate | dateTime | Source column |
| tpkLibraryList | string | Source column |
| tpkDateKey | string | Source column |
| tpkDateRangeDays | int64 | Source column |
| tpkOperationKey | string | Source column |
| tpkPII | string | Source column |
| tpkValidKeyValues | boolean | Source column |
| tpkselectcolumn | string | Source column |
| tpkDataBricksClusterVersion | string | Source column |
| tpkDataBricksNodeType | string | Source column |
| tpkDataBricksClusterRange | string | Source column |

**Source Query:**

```sql
SELECT * FROM [DW_Developer].[TableDictionary]
WHERE TPKTABLENAME = 'PoAuditLog'
AND TPKsCHEMAnAME = 'Wholesale_ProductSourcing_AFI'
```
