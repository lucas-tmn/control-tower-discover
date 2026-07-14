[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "DemandForecastSnapshot(SupplyChain_Enh)_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"DemandForecastSnapshot(SupplyChain_Enh)" = let
  Source = Sql.Database("ashley-edw.database.windows.net", "ASHLEY_EDW", [Query = "/* SOURCE SQL FOR DATAFLOW #(lf)   Lọc theo Phiên bản Snapshot và Cửa sổ thời gian 3 năm #(lf)*/#(lf)SELECT * FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC#(lf)WHERE#(lf)    -- 1. Lọc Snapshot Dates (Chỉ lấy các phiên bản chốt S&OP hàng tháng)#(lf)    CONVERT(DATE, [DFC].[dfcSnapshot]) IN (#(lf)        '2023-01-16','2023-02-13','2023-03-13','2023-04-17','2023-05-15',#(lf)        '2023-06-12','2023-07-17','2023-08-14','2023-09-11','2023-10-16',#(lf)        '2023-11-13','2023-12-11','2024-01-15','2024-02-12','2024-03-11',#(lf)        '2024-04-15','2024-05-13','2024-06-10','2024-07-15','2024-08-12',#(lf)        '2024-09-09','2024-10-14','2024-11-11','2024-12-09','2025-01-13',#(lf)        '2025-02-10','2025-03-29','2025-04-14','2025-05-12','2025-06-09',#(lf)        '2025-07-14','2025-08-18','2025-09-08','2025-10-13','2025-11-12',#(lf)        '2025-12-16','2026-01-15','2026-02-16','2026-03-14','2026-04-18',#(lf)        '2026-05-16'#(lf)    )#(lf)    -- 2. Lọc Period: 2 năm quá khứ + 1 năm tương lai#(lf)    AND DATEFROMPARTS([DFC].[dfcFiscalMonth] / 100, [DFC].[dfcFiscalMonth] % 100, 1) #(lf)        BETWEEN DATEADD(YEAR, -2, GETDATE()) AND DATEADD(YEAR, 1, GETDATE())"])
in
  Source;
shared #"DemandForecastSnapshot(SupplyChain_Enh)_DataDestination" = let
  Pattern = Lakehouse.Contents([HierarchicalNavigation = null, CreateNavigationProperties = false, EnableFolding = false]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "brz2_SupplyChain_Enh__DemandForecastSnapshot", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
