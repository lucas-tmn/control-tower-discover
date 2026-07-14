CREATE TABLE [meta].[view_definitions] (

	[schema] varchar(50) NOT NULL, 
	[view_name] varchar(200) NOT NULL, 
	[definition] varchar(4000) NULL, 
	[_load_dt] datetime2(6) NOT NULL
);