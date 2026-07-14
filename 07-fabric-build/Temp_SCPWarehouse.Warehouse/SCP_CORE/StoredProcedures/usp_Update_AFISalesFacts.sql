CREATE   PROCEDURE [SCP_Core].[usp_Update_AFISalesFacts]
AS

BEGIN 

EXEC [ETL_Framework].[DW_Developer].[usp_RefreshCuratedTableFromView] 'Temp_SCPWarehouse', 'SCP_Core', 'FactOpenOrders'

END;