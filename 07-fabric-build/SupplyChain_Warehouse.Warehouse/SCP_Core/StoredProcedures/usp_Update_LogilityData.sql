CREATE     PROCEDURE [SCP_Core].[usp_Update_LogilityData]
AS

BEGIN 

EXEC [ETL_Framework].[DW_Developer].[usp_RefreshCuratedTableFromView] 'SupplyChain_Warehouse', 'SCP_Core', 'FactWorkingForecastCurrent'

END;