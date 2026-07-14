CREATE     PROCEDURE [SCP_Core].[usp_Update_AFISalesFacts]
AS

BEGIN 

EXEC [ETL_Framework].[DW_Developer].[usp_RefreshCuratedTableFromView] 'SupplyChain_Warehouse', 'SCP_Core', 'FactOpenOrders'
EXEC [ETL_Framework].[DW_Developer].[usp_RefreshCuratedTableFromView] 'SupplyChain_Warehouse', 'SCP_Core', 'FactAFISales_CurReqQty'

END;