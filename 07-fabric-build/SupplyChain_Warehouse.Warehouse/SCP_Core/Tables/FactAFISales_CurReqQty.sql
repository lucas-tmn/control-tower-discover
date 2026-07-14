CREATE TABLE [SCP_Core].[FactAFISales_CurReqQty] (

	[AccountAndShipToNumber] varchar(8000) NOT NULL, 
	[ItemSKU] varchar(8000) NOT NULL, 
	[Warehouse] varchar(8000) NOT NULL, 
	[CurReqWkEnd] date NOT NULL, 
	[OrderQty] int NULL, 
	[OrderAmt] decimal(18,2) NULL, 
	[OrderStatus] varchar(10) NOT NULL
);