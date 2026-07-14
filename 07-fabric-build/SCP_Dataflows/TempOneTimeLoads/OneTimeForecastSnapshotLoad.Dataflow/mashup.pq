[DefaultOutputDestinationSettings = [DestinationDefinition = [Kind = "Reference", QueryName = "DefaultDestination", IsNewTarget = true], UpdateMethod = [Kind = "Replace"], DestinationTypeSettings = [Kind = "Table"]], StagingDefinition = [Kind = "FastCopy"]]
section Section1;
shared DefaultDestination = Lakehouse.Contents([EnableFolding = false]){[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data]{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data];
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "brz_OneTimeForecastHistoryLoad_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared brz_OneTimeForecastHistoryLoad = // SQL Query Template

let
    Source = Sql.Database("ashley-edw.database.windows.net", "ashley_edw",
                [CommandTimeout=#duration(0, 1, 0, 0), Query="

SELECT [DFC].[dfcCustomergroups] 
      ,[DFC].[dfcItem]
      ,[DFC].[dfcWarehouse]
      ,[DFC].[dfcFiscalMonth]
      ,[DFC].[dfcResultantForecast]
      ,[DFC].[dfcPromotionalLift]
      ,[DFC].[dfcSnapshot]
  FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC
  LEFT JOIN (
SELECT DISTINCT [FiscalMonthYear]
      ,[FiscalMonthLastDate]
  FROM [Enterprise_DW].[DimDate]
  ) AS DD
    ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]
  WHERE CONVERT(DATE, [DFC].[dfcSnapshot]) IN
(
N'2023-01-16',
N'2023-02-13',
N'2023-03-13',
N'2023-04-17',
N'2023-05-15',
N'2023-06-12',
N'2023-07-17',
N'2023-08-14',
N'2023-09-11',
N'2023-10-16',
N'2023-11-13',
N'2023-12-11',
N'2024-01-15',
N'2024-02-12',
N'2024-03-11',
N'2024-04-15',
N'2024-05-13',
N'2024-06-10',
N'2024-07-15',
N'2024-08-12',
N'2024-09-09',
N'2024-10-14',
N'2024-11-11',
N'2024-12-09',
N'2025-01-13',
N'2025-02-10',
N'2025-03-29',
N'2025-04-14',
N'2025-05-12',
N'2025-06-09',
N'2025-07-14',
N'2025-08-18',
N'2025-09-08',
N'2025-10-13',
N'2025-11-12',
N'2025-12-16',
N'2026-01-15',
N'2026-02-16',
N'2026-03-14',
N'2026-04-18',
N'2026-05-16'
)
  AND [DD].[FiscalMonthLastDate] < DATEADD(MONTH, 6, [DFC].[dfcSnapshot])

                      ", CreateNavigationProperties=false]),
  #"Changed column type" = Table.TransformColumnTypes(Source, {{"dfcFiscalMonth", Int64.Type}, {"dfcResultantForecast", Int64.Type}, {"dfcPromotionalLift", Int64.Type}, {"dfcSnapshot", type date}})
in
    #"Changed column type";
shared brz_OneTimeForecastHistoryLoad_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "brz_OneTimeForecastHistoryLoad", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
