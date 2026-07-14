CREATE TABLE [SCP_Core].[DimFcstConsensusCycleDates] (

	[CycleName] varchar(8000) NULL, 
	[CycleDescription] varchar(8000) NULL, 
	[CycleMonthLastDate] date NULL, 
	[FcstSnapshot] date NULL, 
	[ExceptionNote] varchar(8000) NULL, 
	[Modified] datetime2(6) NULL, 
	[Created] datetime2(6) NULL
);