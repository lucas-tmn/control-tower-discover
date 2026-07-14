[StagingDefinition = [Kind = "FastCopy"]]
section Section1;
[DataDestinations = {[Definition = [Kind = "Reference", QueryName = "brz_supplychain_enh_1__demandforecastsnapshotdaily_DataDestination", IsNewTarget = true], Settings = [Kind = "Automatic", TypeSettings = [Kind = "Table"]]]}]
shared brz_supplychain_enh_1__demandforecastsnapshotdaily = let
    Source = Sql.Database("ashley-edw.database.windows.net", "ashley_edw", [CommandTimeout = #duration(0, 1, 0, 0), Query = "#(lf)            SELECT #(lf)                -- Keys & Identifiers#(lf)                TRIM(dfcItem) AS id_item_sku,#(lf)                TRIM(dfcWarehouse) AS code_warehouse,#(lf)                CAST(dfcFiscalMonth AS INT) AS num_fiscal_month,#(lf)                TRIM(dfcCustomerGroups) AS code_customer_group,#(lf)#(lf)                -- Forecast Values#(lf)                CAST(dfcResultantForecast AS DECIMAL(14,3)) AS qty_resultant_forecast,#(lf)                CAST(dfcPromotionalLift AS DECIMAL(14,3)) AS qty_promotional_lift,#(lf)                CAST(dfcForcedForecast AS DECIMAL(14,3)) AS qty_forced_forecast,#(lf)                CAST(dfcOrderFutureQty AS INT) AS qty_order_future,#(lf)                CAST(dfcPermComptQty AS DECIMAL(14,2)) AS qty_perm_component,#(lf)#(lf)                -- Snapshot & Dates#(lf)                CAST(dfcSnapshot AS DATETIME) AS ts_snapshot,#(lf)#(lf)                -- Classification#(lf)                TRIM(dfcMainPiece) AS code_main_piece,#(lf)                TRIM(dfcCollectiveClass) AS name_collective_class,#(lf)                TRIM(dfcUsr32Text) AS name_product_category,#(lf)                TRIM(dfcFCSTTypeCode) AS code_forecast_type,#(lf)                TRIM(dfcMgmtCode) AS code_management,#(lf)#(lf)                -- Derived Forecast#(lf)                TRIM(dfcDerivedFCSTID) AS id_derived_forecast,#(lf)                CAST(dfcDerivedFCSTfctr AS DECIMAL(10,3)) AS val_derived_forecast_factor,#(lf)#(lf)                -- Demand#(lf)                CAST(dfcValidDemandMonths AS INT) AS num_valid_demand_months,#(lf)#(lf)                -- Other#(lf)                TRIM(dfcUsr25Text) AS name_usr25,#(lf)#(lf)                -- Source Audit#(lf)                TRIM(usra) AS name_created_by,#(lf)                CAST(dtea AS DATETIME) AS ts_created,#(lf)                TRIM(usrc) AS name_modified_by,#(lf)                CAST(dtec AS DATETIME) AS ts_modified,#(lf)#(lf)                -- From DimDate Join#(lf)                DD.FiscalMonthLastDate#(lf)#(lf)            FROM [SupplyChain_Enh].[DemandForecastSnapshot] AS DFC#(lf)            LEFT JOIN (#(lf)                SELECT DISTINCT [FiscalMonthYear], [FiscalMonthLastDate]#(lf)                FROM [Enterprise_DW].[DimDate]#(lf)            ) AS DD ON [DFC].[dfcFiscalMonth] = [DD].[FiscalMonthYear]#(lf)            WHERE CONVERT(DATE, [DFC].[dfcSnapshot]) IN (#(lf)                N'2023-01-16', N'2023-02-13', N'2023-03-13', N'2023-04-17', N'2023-05-15', N'2023-06-12', #(lf)                N'2023-07-17', N'2023-08-14', N'2023-09-11', N'2023-10-16', N'2023-11-13', N'2023-12-11', #(lf)                N'2024-01-15', N'2024-02-12', N'2024-03-11', N'2024-04-15', N'2024-05-13', N'2024-06-10', #(lf)                N'2024-07-15', N'2024-08-12', N'2024-09-09', N'2024-10-14', N'2024-11-11', N'2024-12-09', #(lf)                N'2025-01-13', N'2025-02-10', N'2025-03-29', N'2025-04-14', N'2025-05-12', N'2025-06-09', #(lf)                N'2025-07-14', N'2025-08-18', N'2025-09-08', N'2025-10-13', N'2025-11-12', N'2025-12-16', #(lf)                N'2026-01-15', N'2026-02-16', N'2026-03-16', N'2026-04-20', N'2026-05-16'#(lf)            )#(lf)            AND [DD].[FiscalMonthLastDate] < DATEADD(MONTH, 6, [DFC].[dfcSnapshot])#(lf)        ", CreateNavigationProperties = false]),

    // Bước ép kiểu dữ liệu trong Power Query để đảm bảo định dạng icon trong Report chuẩn
    #"Changed Type" = Table.TransformColumnTypes(Source, {
        {"num_fiscal_month", Int64.Type},
        {"qty_resultant_forecast", type number},
        {"qty_promotional_lift", type number},
        {"qty_forced_forecast", type number},
        {"qty_order_future", Int64.Type},
        {"qty_perm_component", type number},
        {"val_derived_forecast_factor", type number},
        {"num_valid_demand_months", Int64.Type},
        {"ts_snapshot", type datetime},
        {"ts_created", type datetime},
        {"ts_modified", type datetime},
        {"FiscalMonthLastDate", type date}
    }),
  #"Renamed columns" = Table.RenameColumns(#"Changed Type", {{"FiscalMonthLastDate", "fiscal_month_last_date"}})
in
    #"Renamed columns";
shared brz_supplychain_enh_1__demandforecastsnapshotdaily_DataDestination = let
  Pattern = Lakehouse.Contents([CreateNavigationProperties = false, EnableFolding = false, HierarchicalNavigation = null]),
  Navigation_1 = Pattern{[workspaceId = "c8d9fc83-18b6-4e1d-8264-0b49eed36fe0"]}[Data],
  Navigation_2 = Navigation_1{[lakehouseId = "62a3081e-4093-4f46-856c-f50aa58732fa"]}[Data],
  TableNavigation = Navigation_2{[Id = "brz_supplychain_enh_1__demandforecastsnapshotdaily_ver2", ItemKind = "Table"]}?[Data]?
in
  TableNavigation;
