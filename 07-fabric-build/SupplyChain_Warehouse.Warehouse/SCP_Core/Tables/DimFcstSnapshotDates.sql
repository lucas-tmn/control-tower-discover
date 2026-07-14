CREATE TABLE [SCP_Core].[DimFcstSnapshotDates] (

	[FcstCycle] varchar(7) NOT NULL, 
	[FcstPeriod] varchar(5) NOT NULL, 
	[FcstSnapshotDate] date NULL, 
	[ActualsMonthEnd] date NULL, 
	[ActualsFiscalPeriod] int NULL, 
	[SortFcstPeriod] int NULL
);