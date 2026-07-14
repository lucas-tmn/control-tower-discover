[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "FcstConsensusCycleDates_DataDestination", IsNewTarget = false], Settings = [Kind = "Manual", AllowCreation = false, ColumnSettings = [Mappings = {[SourceColumnName = "CycleName", DestinationColumnName = "CycleName"], [SourceColumnName = "CycleDescription", DestinationColumnName = "CycleDescription"], [SourceColumnName = "CycleMonthLastDate", DestinationColumnName = "CycleMonthLastDate"], [SourceColumnName = "FcstSnapshot", DestinationColumnName = "FcstSnapshot"], [SourceColumnName = "ExceptionNote", DestinationColumnName = "ExceptionNote"], [SourceColumnName = "Modified", DestinationColumnName = "Modified"], [SourceColumnName = "Created", DestinationColumnName = "Created"]}], DynamicSchema = false, UpdateMethod = [Kind = "Replace"], TypeSettings = [Kind = "Table"]]]}]
shared FcstConsensusCycleDates = let
  Source = SharePoint.Tables("https://masterashley.sharepoint.com/sites/SCPGlobalTeam", [Implementation = "2.0", ViewMode = "All"]),
  #"Navigation 1" = Source{[Id = "94a48657-f48d-4828-a009-a4d635e1657f"]}[Items],
  #"Removed columns" = Table.RemoveColumns(#"Navigation 1", {"Color Tag", "Compliance Asset Id", "ID", "Content Type", "Created By", "Modified By", "Version", "Attachments", "Edit", "Type", "Item Child Count", "Folder Child Count", "Label setting", "Retention label", "Retention label Applied", "Label applied by", "Item is a Record", "App Created By", "App Modified By"}),
  #"Changed column type" = Table.TransformColumnTypes(#"Removed columns", {{"CycleName", type text}, {"CycleMonthLastDate", type date}, {"FcstSnapshot", type date}})
in
  #"Changed column type";
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "BeddingAttributeExt_DataDestination", IsNewTarget = false], Settings = [Kind = "Manual", AllowCreation = false, ColumnSettings = [Mappings = {[SourceColumnName = "ItemSKU", DestinationColumnName = "ItemSKU"], [SourceColumnName = "IsKit", DestinationColumnName = "IsKit"], [SourceColumnName = "CoProduced", DestinationColumnName = "CoProduced"], [SourceColumnName = "IsPurchased", DestinationColumnName = "IsPurchased"], [SourceColumnName = "IsManufactured", DestinationColumnName = "IsManufactured"], [SourceColumnName = "Brand", DestinationColumnName = "Brand"], [SourceColumnName = "Version", DestinationColumnName = "Version"], [SourceColumnName = "BrandVersion", DestinationColumnName = "BrandVersion"], [SourceColumnName = "BrandFamily", DestinationColumnName = "BrandFamily"], [SourceColumnName = "BU_Development", DestinationColumnName = "BU_Development"], [SourceColumnName = "PrimaryBusinessUnit", DestinationColumnName = "PrimaryBusinessUnit"], [SourceColumnName = "PrimaryChannel", DestinationColumnName = "PrimaryChannel"], [SourceColumnName = "CategoryMaster", DestinationColumnName = "CategoryMaster"], [SourceColumnName = "Category", DestinationColumnName = "Category"], [SourceColumnName = "TransitionMap", DestinationColumnName = "TransitionMap"], [SourceColumnName = "TransitionVersion", DestinationColumnName = "TransitionVersion"], [SourceColumnName = "CalendarAssignment", DestinationColumnName = "CalendarAssignment"], [SourceColumnName = "SpecialProgram", DestinationColumnName = "SpecialProgram"], [SourceColumnName = "JBPAtt1", DestinationColumnName = "JBPAtt1"], [SourceColumnName = "JBPAtt2", DestinationColumnName = "JBPAtt2"], [SourceColumnName = "JBPAtt3", DestinationColumnName = "JBPAtt3"], [SourceColumnName = "JBPAtt4", DestinationColumnName = "JBPAtt4"], [SourceColumnName = "JBPAtt5", DestinationColumnName = "JBPAtt5"], [SourceColumnName = "JBPAtt6", DestinationColumnName = "JBPAtt6"], [SourceColumnName = "JBPAtt7", DestinationColumnName = "JBPAtt7"]}], DynamicSchema = false, UpdateMethod = [Kind = "Replace"], TypeSettings = [Kind = "Table"]]]}]
shared BeddingAttributeExt = let
  Source = SharePoint.Files("https://masterashley.sharepoint.com/sites/SCPGlobalTeam-Bedding1/", [ApiVersion = 15]),
  Navigation = Source{[Name = "Products_Revised.xlsx", #"Folder Path" = "https://masterashley.sharepoint.com/sites/SCPGlobalTeam-Bedding1/Shared Documents/Bedding/ReportingInputs/"]}[Content],
  #"Imported Excel workbook" = Excel.Workbook(Navigation, null, true),
  #"Navigation 1" = #"Imported Excel workbook"{[Item = "EDW FEED", Kind = "Sheet"]}[Data],
  #"Promoted headers" = Table.PromoteHeaders(#"Navigation 1", [PromoteAllScalars = true]),
  #"Changed column type" = Table.TransformColumnTypes(#"Promoted headers", {{"IsKit", type text}, {"CoProduced", type text}, {"IsPurchased", type text}, {"IsManufactured", type text}, {"Brand", type text}, {"Version", type text}, {"BrandVersion", type text}, {"BrandFamily", type text}, {"BU_Development", type text}, {"PrimaryBusinessUnit", type text}, {"PrimaryChannel", type text}, {"CategoryMaster", type text}, {"Category", type text}, {"TransitionMap", type text}, {"TransitionVersion", type text}, {"CalendarAssignment", type text}, {"SpecialProgram", type text}, {"JBPAtt2", type text}, {"JBPAtt4", type text}, {"JBPAtt5", type text}, {"JBPAtt6", type text}, {"JBPAtt7", type text}, {"ItemSKU", type text}, {"JBPAtt1", type text}, {"JBPAtt3", type text}}),
  #"Removed other columns" = Table.SelectColumns(#"Changed column type", {"ItemSKU", "IsKit", "CoProduced", "IsPurchased", "IsManufactured", "Brand", "Version", "BrandVersion", "BrandFamily", "BU_Development", "PrimaryBusinessUnit", "PrimaryChannel", "CategoryMaster", "Category", "TransitionMap", "TransitionVersion", "CalendarAssignment", "SpecialProgram", "JBPAtt1", "JBPAtt2", "JBPAtt3", "JBPAtt4", "JBPAtt5", "JBPAtt6", "JBPAtt7"})
in
  #"Removed other columns";
shared BeddingAttributeExt_DataDestination = let
  Pattern = Fabric.Warehouse([HierarchicalNavigation = null, CreateNavigationProperties = false]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[warehouseId = "e146ffe2-d907-46a7-9b7e-3e739a31b24e"]}[Data],
  TableNavigation = Navigation_2{[Schema = "SCP_Core", Item = "DimBeddingAttributeExt"]}[Data]
in
  TableNavigation;
shared FcstConsensusCycleDates_DataDestination = let
  Pattern = Fabric.Warehouse([HierarchicalNavigation = null, CreateNavigationProperties = false]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[warehouseId = "e146ffe2-d907-46a7-9b7e-3e739a31b24e"]}[Data],
  TableNavigation = Navigation_2{[Schema = "SCP_Core", Item = "DimFcstConsensusCycleDates"]}[Data]
in
  TableNavigation;
