[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "brz_Actuals_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared brz_Actuals = // SQL Query Template

let
    Source = Sql.Database("ashley-edw.database.windows.net", "ashley_edw",
                [CommandTimeout=#duration(0, 1, 0, 0), Query="

  SELECT RTRIM([DC].[Account And ShipTo Number]) AS [AccountAndShipToNumber]
      ,RTRIM([ID].[ItemNumber]) AS [ItemSKU]
      ,RTRIM([ID].[Warehouse]) AS [Warehouse]
      ,[DD].[FiscalWeekLastDate] AS [CurReqWkEnd]
      ,SUM([ID].[QuantityShipped]) AS [OrderQty]
      ,SUM([ID].[NetSales]) AS [OrderAmt]
			,'Invoiced' AS [OrderStatus]
FROM [Wholesale_SalesHistory_AFI].[InvoiceDetail] AS ID 
  INNER JOIN [Wholesale_SalesHistory_AFI].[InvoiceHeader] AS IH
    ON [ID].[InvoiceNumber] = [IH].[InvoiceNumber]
	  AND [ID].[InvoiceDate] = [IH].[InvoiceDate]
	  AND [ID].[OrderDate] = [IH].[OrderDate]
	  AND [ID].[OrderNumber] = [IH].[OrderNumber]
LEFT JOIN [AFISales_DW].[DimCustomers] AS DC
  ON [ID].[CustomerNumber] = [DC].[Customer Account Number]
    AND [ID].[ShiptoNumber] = [DC].[Customer Shipto Number]
INNER JOIN [Enterprise_DW].[DimDate] AS DD
  ON DATEADD(DAY, -[IH].[LeadTime], [ID].[CurrentRequestDate]) = [DD].[DateID]

WHERE [ID].[QuantityShipped] > 0
    AND [DD].[FiscalWeekLastDate] > '2023-12-31'
  --AND RTRIM([ID].[ItemNumber]) = 'M69731'


GROUP BY RTRIM([DC].[Account And ShipTo Number])
        ,RTRIM([ID].[ItemNumber])
        ,RTRIM([ID].[Warehouse])
        ,[DD].[FiscalWeekLastDate]

UNION

SELECT RTRIM([OO].[Account And ShipTo Number]) AS [AccountAndShipToNumber]
      ,RTRIM([OO].[Item Sku]) AS [ItemSKU]
      ,RTRIM([OO].[Warehouse]) AS [Warehouse]
      ,[DD].[FiscalWeekLastDate] AS [CurReqWkEnd]
      ,SUM([OO].[Open Order Quantity]) AS [OrderQty]
      ,SUM([OO].[Open Order Amount]) AS [OrderAmt]
			,'Open' AS [OrderStatus]
FROM [AFISales_DW].[FactOpenOrders] AS OO 

INNER JOIN [Enterprise_DW].[DimDate]AS DD
  ON DATEADD(DAY, -[OO].[Load Lead Time], [OO].[Current Request Date]) = [DD].[DateID]

WHERE [OO].[Inventory Allocated Flag] = '2'

GROUP BY RTRIM([OO].[Account And ShipTo Number])
        ,RTRIM([OO].[Item Sku])
        ,RTRIM([OO].[Warehouse])
        ,[DD].[FiscalWeekLastDate]

                      ", CreateNavigationProperties=false]),
  #"Changed column type" = Table.TransformColumnTypes(Source, {{"CurReqWkEnd", type date}, {"OrderQty", Int64.Type}})
in
    #"Changed column type";
shared brz_Actuals_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "brz_OneTimeLoadActuals", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
