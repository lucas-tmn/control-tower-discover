CREATE TABLE [meta].[dq_results] (

	[result_id] int NOT NULL, 
	[pipeline_run_id] varchar(36) NULL, 
	[rule_id] int NOT NULL, 
	[check_time] datetime2(6) NOT NULL, 
	[status] varchar(10) NOT NULL, 
	[actual_value] varchar(500) NULL, 
	[expected_value] varchar(500) NULL, 
	[error_detail] varchar(4000) NULL
);