-- Auto Generated (Do not modify) 37AF0298EC01E61086D26CF7B54B5140E15BE05822E3014C0454F320902CA778

CREATE         VIEW [SCP_Core_Wrk].[v_FactWorkingForecastCurrent] AS (

SELECT RTRIM([DFC].[DfcCustomerGroups] ) AS [CustomerGroup]
      ,RTRIM([DFC].[dfcItem]     ) AS [ItemSKU]
      ,RTRIM([DFC].[dfcWarehouse]) AS [Warehouse]
      ,ISNULL([DD].[FiscalMonthLastDate],CONVERT(DATE, LEFT([DFC].[dfcFiscalMonth],4)+'-'+RIGHT([DFC].[dfcFiscalMonth],2)+'-15')) AS [FiscalMonthLastDate]
      ,[DFC].[dfcResultantForecast] AS [ResultantForecastQty]
      ,[DFC].[dfcPromotionalLift] AS [PromoLiftQty]
      ,[DFC].[dfcOrderFutureQty] AS [FutureOrderQty]
      ,CONVERT(DATE, [DFC].[dtea]) AS [SnapshotDate]
  FROM [Enterprise_Lakehouse].[Wholesale_DemandPlanning_AFI].[DemandForecast]  AS DFC
  LEFT JOIN (
SELECT DISTINCT [FiscalMonthYear], [FiscalMonthLastDate]
  FROM [Enterprise_Lakehouse].[MasterData_DW].[DimDate]
  ) AS DD
  ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]

);