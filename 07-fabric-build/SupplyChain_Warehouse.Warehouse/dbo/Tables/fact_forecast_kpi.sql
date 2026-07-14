CREATE TABLE [dbo].[fact_forecast_kpi] (

	[id_item_sku] varchar(8000) NULL, 
	[code_warehouse] varchar(8000) NULL, 
	[dt_fsc_month_first] date NULL, 
	[dt_fsc_month_last] date NULL, 
	[code_horizon] varchar(8000) NULL, 
	[dt_snapshot] date NULL, 
	[qty_forecast] float NULL, 
	[qty_actual] float NULL, 
	[qty_naive_forecast] float NULL, 
	[qty_fcst_error] float NULL, 
	[qty_abs_fcst_error] float NULL, 
	[qty_naive_fcst_error] float NULL, 
	[qty_abs_naive_fcst_error] float NULL, 
	[qty_squared_fcst_error] float NULL, 
	[qty_squared_naive_fcst_error] float NULL, 
	[valid_obs_flag] int NULL, 
	[valid_actual_nonzero_flag] int NULL, 
	[abs_pct_error] float NULL
);