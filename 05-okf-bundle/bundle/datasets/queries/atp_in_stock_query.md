---
type: Query
title: ATP In Stock Query
description: EDW SQL query that summarizes recent weekly ATP availability by item, warehouse, and week ending.
tags: [atp, in-stock, inventory, availability, fulfillment, forecast, logility, query]
timestamp: 2026-07-07
resource: "[SupplyChain_Enh].[ATPWeekEnding]"
source_system: Logility
refresh_cadence: weekly
data_source: ashley_edw
status: draft
---

## Purpose

Weekly ATP availability extract for recent planning weeks. The query identifies whether item-warehouse combinations had available-to-promise quantity during each week-ending period, while separating recent launches from active products using first positive shipped invoice history.

Use this query to support [ATP In Stock](/metrics/atp_in_stock.md) reporting and to understand whether customers are likely seeing available ATP for active, recently forecasted items at customer-invoicing warehouses.

---

## Grain

Each row represents one **item x warehouse x week-ending x initial invoice date** grouping after ATP rows are filtered to:

- `ATPWeek = 'Week2'`
- prior completed fiscal weeks (`FiscalWeekIndicator BETWEEN -8 AND -1`)
- selected customer-invoicing warehouses
- item-warehouse combinations with positive recent resultant forecast
- Logility item statuses that are not discontinued, inactive, restricted, terminated, or new-item exclusions

The natural analytic grain is `ItemSKU` x `WarehouseID` x `WeekEnding` x `RecentLaunchFlag`. `InitialInvoiceDate` is included to make the launch classification auditable.

---

## Schema

| Column | Type | Meaning |
| --- | --- | --- |
| `ItemSKU` | VARCHAR | Trimmed item identifier from `[SupplyChain_Enh].[ATPWeekEnding]`; joins to [Product Master](/datasets/tables/DimProduct.md). |
| `WarehouseID` | VARCHAR | Customer-invoicing warehouse from the ATP source, right-trimmed in the outer select; joins to [Warehouse Master](/datasets/tables/DimWarehouse.md). |
| `InitialInvoiceDate` | DATE | Earliest positive shipped invoice date for the item from `[Wholesale_SalesHistory_AFI].[InvoiceDetail]`, excluding supplier direct ship and container-direct virtual warehouses. |
| `RecentLaunchFlag` | VARCHAR | `NewLaunch` when the item has no initial invoice date or is within 90 days of initial invoice as of `WeekEnding`; otherwise `Active`. |
| `WeekEnding` | DATE | ATP week-ending date; aligns to [Fiscal Calendar](/datasets/tables/DimDate.md). |
| `InStockEvent` | INT | Count of underlying ATP observations in the group where `ATPQty > 0`. |
| `StockEvent` | INT | Count of underlying ATP observations contributing to the group. This is the denominator for [ATP In Stock](/metrics/atp_in_stock.md). |
| `AvgATPQty` | DECIMAL | Average ATP quantity observed across the underlying rows for the grouped week. Use as supporting context, not as the in-stock rate itself. |

---

## Source Logic

### ATP window and warehouse scope

The inner ATP subquery reads `[SupplyChain_Enh].[ATPWeekEnding]` and joins `[Enterprise_DW].[DimDate_NonRetail]` on `RunDate` to keep only completed fiscal weeks where `FiscalWeekIndicator BETWEEN -8 AND -1`.

The query filters to:

- `ATPWeek = 'Week2'`
- `InsertedVersion = 1`
- warehouses `1`, `15`, `17`, `28`, `5`, `335`, and `ECR`

`Week2` is used because customer orders commonly have roughly a seven-day lead between order date and requested date, so the second ATP week better reflects the ATP position customers expect to see.

### Recent forecast demand filter

The query inner joins to a `[SupplyChain_Enh].[DemandForecastSnapshot]` aggregate by item and warehouse, limited to snapshots from the last 13 months. The `HAVING SUM(dfcResultantForecast) > 0` filter keeps only item-warehouse combinations with positive recent forecast demand.

This prevents ATP rows for item-warehouse combinations with no recent forecast demand from inflating availability reporting.

### Item status filter

The query left joins `[SupplyChain_Enh].[DemandFulfillmentCommonContainer_Logility]` by item, warehouse, and week ending, then filters out item statuses `D`, `I`, `R`, `T`, and `N`.

Because the item-status condition is in the `WHERE` clause, rows without a matching Logility status record are also excluded.

### Launch classification

The launch-classification subquery reads `[Wholesale_SalesHistory_AFI].[InvoiceDetail]`, keeps positive shipped quantity, and excludes warehouses `55`, `C`, and `CNW`.

- Warehouse `55` is excluded because it is the supplier direct ship warehouse and does not have ATP.
- Warehouses `C` and `CNW` are container-direct virtual warehouses; excluding them keeps the initial invoice date tied to the first physical-warehouse shipment.

`RecentLaunchFlag` is assigned as:

```text
NewLaunch when InitialInvoiceDate is null
NewLaunch when InitialInvoiceDate + 90 days > WeekEnding
Active otherwise
```

---

## Metric Logic

[ATP In Stock](/metrics/atp_in_stock.md) is calculated from this query as:

```text
ATPInStockRate = SUM(InStockEvent) / SUM(StockEvent)
```

`AvgATPQty` is a supporting diagnostic that shows the average available-to-promise quantity observed during the week. It helps explain whether an in-stock week had shallow or deep availability, but it is not the in-stock-rate numerator.

---

## Related

- [ATP In Stock](/metrics/atp_in_stock.md)
- [Product Master](/datasets/tables/DimProduct.md)
- [Warehouse Master](/datasets/tables/DimWarehouse.md)
- [Fiscal Calendar](/datasets/tables/DimDate.md)
- [Current Forecast](/datasets/tables/FactCurrentForecast.md)
- [Stockout](/glossary/stockout.md)

## Base Query

```sql
SELECT [ATP].[ItemSKU]
      ,RTRIM([ATP].[Warehouse]) AS [WarehouseID]
      ,[LC].[InitialDate] AS [InitialInvoiceDate]
      ,CASE 
            WHEN [LC].[InitialDate] IS NULL 
                THEN 'NewLaunch'
            WHEN DATEADD(DAY,90,[LC].[InitialDate]) > [ATP].[WeekEnding]
                THEN 'NewLaunch'
            ELSE 'Active'
        END AS [RecentLaunchFlag]
      ,[ATP].[WeekEnding]
      ,SUM(ATP.[In Stock Event]) AS [InStockEvent]
      ,SUM(ATP.[Stock Event])    AS [StockEvent]
      ,AVG(ATP.[ATPQty])         AS [AvgATPQty]
  FROM (
SELECT RTRIM(atp.[ItemSKU]) AS [ItemSKU]
      ,atp.[Warehouse]
      ,atp.[ATPWeek]
      ,atp.[WeekEnding]
  
                 ,atp.[ATPQty]
                 ,dd.FiscalMonthLastDate
                 ,CASE
                      WHEN [atp].[ATPQty] > 0 THEN
                          1
                      ELSE
                          0
                  END AS [In Stock Event]
                 ,1   AS [Stock Event]
             --,atp.[RunDate]
             --,atp.[InsertedVersion]
             --,atp.[VersionDescription]
             --,atp.[APNQ]
             FROM [SupplyChain_Enh].[ATPWeekEnding]                     atp
                 INNER JOIN Enterprise_DW.DimDate_NonRetail AS dd
                     ON atp.[RunDate] = dd.[DateID]
                     AND [dd].[FiscalWeekIndicator] BETWEEN -8 AND -1

                 INNER JOIN (
                                SELECT dfs.dfcItem
                                      ,dfs.dfcWarehouse
                                      ,SUM(dfs.dfcResultantForecast) AS RSLF
                                  FROM SupplyChain_Enh.DemandForecastSnapshot dfs
                                 WHERE dfs.dfcSnapshot > DATEADD(MONTH, -13, GETDATE())
                                 GROUP BY dfs.dfcItem
                                         ,dfs.dfcWarehouse
                                HAVING SUM(dfs.dfcResultantForecast) > 0
                            )                                           dfc
                     ON dfc.dfcItem = RTRIM(atp.[ItemSKU])
                    AND dfc.dfcWarehouse = atp.Warehouse

              LEFT JOIN [SupplyChain_Enh].[DemandFulfillmentCommonContainer_Logility] AS DFL
                ON [atp].[ItemSKU] = [DFL].[Item]
                AND [atp].[Warehouse] = [DFL].[Whse]
                AND [atp].[WeekEnding] = [DFL].[WeekEnding]
            WHERE atp.[ATPWeek] = 'Week2'
              AND atp.[Warehouse] IN ( '1', '15', '17', '28', '5', '335', 'ECR' )
              AND atp.[InsertedVersion] = 1
              AND [DFL].[ItemStatus] NOT IN ( 'D', 'I', 'R', 'T','N') 


       ) ATP
  LEFT JOIN (

        SELECT [ItemNumber]
              ,MIN([InvoiceDate]) AS [InitialDate]
          FROM [Wholesale_SalesHistory_AFI].[InvoiceDetail]
          WHERE [Warehouse] NOT IN ('55','C','CNW') 
            AND [QuantityShipped] > 0

          GROUP BY [ItemNumber]
    ) AS LC 
    ON [ATP].[ItemSKU] = [LC].[ItemNumber]

 GROUP BY [ATP].[ItemSKU]
         ,[ATP].[Warehouse]
         ,[ATP].[WeekEnding]
         ,[LC].[InitialDate]
```
