[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "InvTransWeeklySummary_DataDestination", IsNewTarget = false], Settings = [Kind = "Manual", AllowCreation = false, ColumnSettings = [Mappings = {[SourceColumnName = "ItemSKU", DestinationColumnName = "ItemSKU"], [SourceColumnName = "Warehouse", DestinationColumnName = "Warehouse"], [SourceColumnName = "ItemFlag", DestinationColumnName = "ItemFlag"], [SourceColumnName = "FiscalWeekLastDate", DestinationColumnName = "FiscalWeekLastDate"], [SourceColumnName = "TransactionCode", DestinationColumnName = "TransactionCode"], [SourceColumnName = "TransactionCodeDesc", DestinationColumnName = "TransactionCodeDesc"], [SourceColumnName = "TransactionType", DestinationColumnName = "TransactionType"], [SourceColumnName = "TransactionQty", DestinationColumnName = "TransactionQty"], [SourceColumnName = "NetChangeQty", DestinationColumnName = "NetChangeQty"]}], DynamicSchema = false, UpdateMethod = [Kind = "Append"], TypeSettings = [Kind = "Table"]]]}]
shared InvTransWeeklySummary = // SQL Query Template

let
    Source = Sql.Database("ashley-edw.database.windows.net", "ashley_edw",
                [CommandTimeout=#duration(0, 1, 0, 0), Query="

SELECT [inv].[ItemSKU]
      ,[inv].[Warehouse]
      ,[inv].[ItemFlag]
      ,[inv].[FiscalWeekLastDate]
      ,[inv].[TransactionCode]
      ,[inv].[TransactionCodeDesc]
      ,[inv].[TransactionType]
      ,SUM([inv].[TransactionQty]) AS [TransactionQty]
      ,SUM([inv].[NetChange]) AS [NetChangeQty]
  FROM (

SELECT RTRIM([IH].[ITNBR]) AS [ItemSKU]
      ,RTRIM([IH].[HOUSE]) AS [Warehouse]
      ,CASE 
           WHEN [RW].[UUCB] BETWEEN 13000 AND 14999 THEN 'Raw Materials' 
           WHEN [RW].[UUCB] BETWEEN 15800 AND 15899 THEN 'WIP Items' 
           WHEN [FG].[UUCB] BETWEEN 15900 AND 15999 THEN 'Finished Goods' 
           ELSE 'N/A'
       END AS [ItemFlag]
      ,[DD].[FiscalWeekLastDate]
      ,RTRIM([IH].[TCODE]) AS [TransactionCode]
      ,CASE RTRIM([IH].[TCODE]) 
           WHEN 'RP' THEN 'Receipt from purchase order'
           WHEN 'RM' THEN 'Receipt from manufacturing order'
           WHEN 'RC' THEN 'Receipt w/o open order'
           WHEN 'RW' THEN 'Transfer: receiving warehouse'
           WHEN 'IP' THEN 'Component consumption by manufacturing'
           WHEN 'IS' THEN 'Miscellaneous: Not charged to vendor or customer'
           WHEN 'IW' THEN 'Transfer: Issuing Warehouse'
           WHEN 'IX' THEN 'Uncontrolled floor stock reduction'
           WHEN 'SM' THEN 'Scrap from Manufacturing Order'
           WHEN 'SS' THEN 'Scrap from stock'
           WHEN 'IA' THEN 'Inventory Adjustment'
           WHEN 'RS' THEN 'Return to stock'
           WHEN 'SA' THEN 'Sales Shipments'
           WHEN 'VR' THEN 'Vendor Return'
           WHEN 'SC' THEN 'Component scrap from Manufacturing Order'
           ELSE 'N/A'
       END AS [TransactionCodeDesc]
      ,CASE
           WHEN RTRIM([IH].[TCODE])  IN ( 'RP', 'RM', 'RC', 'RW', 'LA', 'PH', 'RS', 'RW', 'VA' ) THEN
               'Receipts'
           WHEN RTRIM([IH].[TCODE])  = 'IA' THEN
               'Inv Adjustments'
           ELSE
               'Usage'
       END AS [TransactionType]
      ,CASE
           WHEN RTRIM([IH].[TCODE])  IN ( 'RP', 'RM', 'RC', 'RW', 'IA', 'LA', 'PH', 'RS', 'RW', 'VA' ) THEN
               [IH].[TRQTY]
           ELSE
               [IH].[TRQTY] * -1
       END AS [NetChange]
       ,[IH].[TRQTY] AS [TransactionQty]
  FROM [Manufacturing_Inventory_AFI].[IMHIST] AS IH

  LEFT JOIN [Enterprise_DW].[DimDate] AS DD 
    ON [IH].[TRNDT] = [DD].[MapicsDate]
  
  LEFT JOIN [MasterData_ItemMaster_AFI].[ITMEXT] AS EXT 
    ON [IH].[ITNBR] = [EXT].[ITNBR]

  LEFT JOIN (
SELECT ia.STID
      ,ia.ITNBR
      ,b.UUCB
  FROM MasterData_ItemMaster_AFI.ITMRVA           ia --Enterprise_DB2_ODS.dbo.ITMRVA ia  
      INNER JOIN MasterData_ItemMaster_AFI.ITMRVB b --Enterprise_DB2_ODS.dbo.ITMRVB b  
          ON ia.STID = b.STID
         AND ia.ITNBR = b.ITNBR
         AND ia.ITRV = b.ITRV
 WHERE b.UUCB BETWEEN 15900 AND 15999
   AND '1' = ia.UUCA
  ) AS FG
  ON [EXT].[CEX] = [FG].[STID]
  AND [IH].[ITNBR] = [FG].[ITNBR]


  LEFT JOIN ( 
SELECT wm.WHID
      ,ia.STID
      ,ia.ITNBR
      ,b.UUCB
  FROM Wholesale_Purchasing_AFI.WHSMST            wm --Enterprise_DB2_ODS.dbo.whsmst wm  
      INNER JOIN MasterData_ItemMaster_AFI.ITMRVA ia --Enterprise_DB2_ODS.dbo.ITMRVA ia  
          ON wm.STID = ia.STID

      INNER JOIN MasterData_ItemMaster_AFI.ITMRVB b --Enterprise_DB2_ODS.dbo.ITMRVB b  
          ON ia.STID = b.STID
         AND ia.ITNBR = b.ITNBR
         AND ia.ITRV = b.ITRV
 WHERE b.UUCB BETWEEN 13000 AND 15899
   AND '1' = ia.UUCA
  ) AS RW
  ON [IH].[HOUSE] = [RW].[WHID]
    AND [IH].[ITNBR] = [RW].[ITNBR]

  WHERE [DD].[FiscalWeekIndicator] = -1

    --Exclude transaction adjusting costs, Physical Inventory, 'Transfer Warehouse' duplication, and other obscure transactions
    AND[IH].[TCODE] NOT IN ( 'CA', 'CU', 'PH', 'TW', 'LA' )

    --Exclude transfer warehouses logic
    AND [IH].[HOUSE] NOT IN ( 'A', 'M', 'L', 'N', 'U', 'S', 'D', 'K', 'T', 'W', 'G', 'B', 'F', 'E' )

    -- Exclude High Jump location movement within warehouse transactions
    AND [IH].[REASN] <> 'HJ-MOV'
    AND ([FG].[UUCB] IS NOT NULL OR [RW].[UUCB] IS NOT NULL)

    ) AS inv

    GROUP BY [inv].[ItemSKU]
            ,[inv].[Warehouse]
            ,[inv].[ItemFlag]
            ,[inv].[FiscalWeekLastDate]
            ,[inv].[TransactionCode]
            ,[inv].[TransactionCodeDesc]
            ,[inv].[TransactionType]

                      ", CreateNavigationProperties=false]),
  #"Changed column type" = Table.TransformColumnTypes(Source, {{"FiscalWeekLastDate", type date}})
in
    #"Changed column type";
shared InvTransWeeklySummary_DataDestination = let
  Pattern = Fabric.Warehouse([CreateNavigationProperties = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[warehouseId = "e146ffe2-d907-46a7-9b7e-3e739a31b24e"]}[Data],
  TableNavigation = Navigation_2{[Schema = "SCP_Core", Item = "FactInvTransactionsWeekly"]}[Data]
in
  TableNavigation;
