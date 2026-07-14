CREATE TABLE [SCP_Core].[FactWorkingForecastCurrent] (

	[CustomerGroup] varchar(30) NOT NULL, 
	[ItemSKU] varchar(30) NOT NULL, 
	[Warehouse] varchar(3) NOT NULL, 
	[FiscalMonthLastDate] date NOT NULL, 
	[ResultantForecastQty] int NOT NULL, 
	[PromoLiftQty] int NOT NULL, 
	[FutureOrderQty] int NOT NULL, 
	[SnapshotDate] date NOT NULL
);