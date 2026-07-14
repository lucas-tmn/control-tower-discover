EXEC [ETL_Framework].[DW_Developer].[usp_RefreshCuratedTableFromView] 'SupplyChain_Warehouse', 'SCP_Core', 'DimFiscalCalendar'


EXECUTE SCP_Core.usp_Update_AFISalesFacts
EXECUTE SCP_Core.usp_Update_Dimensions
EXECUTE SCP_Core.usp_Update_LogilityData

