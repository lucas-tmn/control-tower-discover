[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "DimAshleyWarehouseMaster(AFISales_DW)_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared #"DimAshleyWarehouseMaster(AFISales_DW)" = let
  Source = Sql.Database("ashley-edw.database.windows.net", "ASHLEY_EDW", [Query = "select *#(lf)from AFISales_DW.DimAshleyWarehouseMaster"])
in
  Source;
shared #"DimAshleyWarehouseMaster(AFISales_DW)_DataDestination" = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "brz2_AFISales_DW__DimAshleyWarehouseMaster", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
