CREATE TABLE [dbo].[WarehouseMaster] (

	[Warehouse] varchar(8000) NULL, 
	[Warehouse Location] varchar(8000) NULL, 
	[Site ID] varchar(8000) NULL, 
	[Warehouse Name] varchar(8000) NULL, 
	[Warehouse Order Group] varchar(8000) NULL, 
	[Intransit Warehouse] varchar(8000) NULL, 
	[Container Direct Warehouse] varchar(8000) NULL, 
	[Controlled Warehouse] bit NULL, 
	[AFIWarehousesKey] int NULL, 
	[Warehouse Group] varchar(8000) NULL, 
	[Sort By] bigint NULL
);