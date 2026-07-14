CREATE   PROCEDURE [SCP_Core].[usp_Update_FcstAccuracy]
AS

BEGIN 

EXEC [ETL_Framework].[DW_Developer].[usp_IncrementalTableLoad] 'SupplyChain_Warehouse', 'SCP_Core', 'FactFcstErrorCalc', 'Append'

END;