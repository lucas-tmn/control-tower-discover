CREATE TABLE [bronze].[ref_forecast_cycle] (

	[code_cycle] varchar(8000) NULL, 
	[name_cycle_description] varchar(8000) NULL, 
	[dt_cycle_month_last] date NULL, 
	[dt_forecast_snapshot] date NULL, 
	[name_exception_note] varchar(8000) NULL, 
	[ts_modified] datetime2(6) NULL, 
	[ts_created] datetime2(6) NULL, 
	[_load_dt] datetime2(6) NULL
);