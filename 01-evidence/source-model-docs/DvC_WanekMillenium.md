---
model_name: DvC  - WanekMillenium
server: ashley-edw.database.windows.net
database: ASHLEY_EDW
table_count: 11
measure_count: 14
non_warehouse_sources: yes
non_warehouse_source_types: SharePoint (Excel), ODBC (iSeries — WFVNPROD/Wanek, MILPROD/Millenium, AFIPROD)
---

# Business Context

This report tracks **Demand vs. Capacity (DvC)** for two furniture manufacturing vendors — **Wanek** (vendor codes 600039 / 900639) and **Millenium** (vendor code 624556 / 900515) — serving Ashley Furniture's supply chain planning team. It answers whether manufacturing capacity at each facility can absorb the planned, firm, and shipped unit volumes from the Production Schedule Workbench (PSW) over a rolling 30-week horizon. Key questions include: How do actual and promised capacity commitments compare to the constrained and unconstrained supply plan? Are actual production scans (FG Output and RP Scan from iSeries factory systems) tracking in line with PSW projections? Structurally, the model pulls PSW weekly snapshots and unconstrained plan from the Ashley EDW warehouse, enriches them with item classification from iSeries (item category, ITCLAD), and overlays capacity override/promise data from a manually-maintained SharePoint Excel workbook. A linear trendline layer across ETD weeks enables visual capacity trend analysis.

## Relationships

| From | To |
| --- | --- |
| PSW.ReKey | Capacity Actual.ReKey |
| PSW.Timeline Key | SISS Timeline.PSW Key |
| PSW.ReKey | Capacity Promise.ReKey |
| PSW.ITEMETDVEndor Key | Item Master.Key |
| RP Scan.Key | Item Master.Key |
| FG Output.Key | Item Master.Key |
| Item Master.PSW_Item | Production Resource Master.ItemID |

*All DateTable relationships excluded. PSW ↔ Capacity Actual and PSW ↔ Capacity Promise use bidirectional cross-filtering. Item Master → Production Resource Master is many-to-many (toCardinality: many).*

## Measures

### Overide Cap - No filter Group

- Sums override capacity for future-dated weeks; suppressed when Series or Status slicers are active, visible only when Type=FG or a Prod Resource filter is applied.  
`IF(AND(NOT ISFILTERED('Item Master'[Series]), NOT ISFILTERED('Item Master'[Status])), IF((ISFILTERED('Item Master'[Type]) && SELECTEDVALUE('Item Master'[Type]) = "FG") || ISFILTERED('Item Master'[Prod Resource]), SUMX(FILTER('Capacity Actual', 'Capacity Actual'[Attribute] > TODAY()), 'Capacity Actual'[Override Cap]), BLANK()), BLANK())`

### Promise Cap- No filter Group

- Same filter guard as Overide Cap; sums promised capacity values for future-dated weeks from the Capacity Promise table.  
`IF(AND(NOT ISFILTERED('Item Master'[Series]), NOT ISFILTERED('Item Master'[Status])), IF((ISFILTERED('Item Master'[Type]) && SELECTEDVALUE('Item Master'[Type]) = "FG") || ISFILTERED('Item Master'[Prod Resource]), SUMX(FILTER('Capacity Promise', 'Capacity Promise'[Attribute] > TODAY()), 'Capacity Promise'[Value]), BLANK()), BLANK())`

### Output

- Actual production output (FG + RP scan quantities for past ETDs); only renders when FG/RP type or specific dimension filters are active.  
`IF(((ISFILTERED('Item Master'[Type]) && (CONTAINSSTRING(..., "FG") || CONTAINSSTRING(..., "RP"))) || ISFILTERED('Item Master'[Prod Resource]) || ...), SUMX(SUMMARIZE(FILTER('FG Output', ETD < TODAY()), ...), [Qty]) + SUMX(SUMMARIZE(FILTER('RP Scan', ETD < TODAY()), ...), [Qty]), BLANK())`

### Firm&Ship

- Total committed supply units — firm orders plus shipped quantities from the PSW snapshot.  
`SUM('PSW'[Firm_Qty]) + SUM('PSW'[Ship_Qty])`

### Firm&Ship Cont

- Total container volume for firm and shipped orders, derived from unit quantities via the PSW calculated container columns.  
`SUM(PSW[Firm_cont]) + SUM(PSW[Ship_cont])`

### Total PSW

- Total planned supply across all order statuses (shipped, firm, and planned).  
`CALCULATE(SUM('PSW'[Firm_Qty]) + SUM('PSW'[Ship_Qty]) + SUM(PSW[Plan_Qty]))`

### Total PSW C&CNW

- Total PSW restricted to items with ETD within the next 8 weeks (C&CNW window), used for near-term capacity planning.  
`CALCULATE(SUM('PSW'[Firm_Qty]) + SUM('PSW'[Ship_Qty]) + SUM('PSW'[Plan_Qty]), FILTER('Item Master', 'Item Master'[PSW_ETD] <= TODAY() + (6 - WEEKDAY(TODAY(),2)) + 8 * 7))`

### Total PSW Cont

- Total container volume across all plan statuses (shipped, firm, and planned).  
`SUM('PSW'[Firm_cont]) + SUM('PSW'[Ship_cont]) + SUM(PSW[Plan_cont])`

### Total PSW Unconstraint

- Total supply including unconstrained planned quantities, enabling constrained vs. unconstrained scenario comparison.  
`SUM('PSW'[Firm_Qty]) + SUM('PSW'[Ship_Qty]) + SUM(PSW[Plan Unconstraint Qty])`

### Trendline

- Linear regression trendline of Total PSW projected over the ETD axis, used for visual capacity trend analysis across the 30-week horizon.  
`VAR temp = LINESTX(ALLSELECTED('Item Master'[PSW_ETD]), [Total PSW], 'Item Master'[PSW_ETD]) ... RETURN x * slope + intercept`

### Trendline C&CNW

- Trendline restricted to the C&CNW 8-week ETD window; returns BLANK beyond the window boundary.  
`VAR temp = LINESTX(FILTER(ALLSELECTED(...), ETD <= 8-week window), [Total PSW C&CNW], ...) ... RETURN IF(x <= window, y)`

### Trendline C&CNW Full ETD

- Trendline computed on all ETDs within 28 days of today, providing a short-horizon linear trend overlay.  
`VAR temp = LINESTX(FILTER(ALLSELECTED(...), ETD < TODAY()+28), [Total PSW], ...) ... RETURN y`

### Trendline Cont

- Linear regression trendline for container volumes over the ETD axis.  
`VAR temp = LINESTX(ALLSELECTED('Item Master'[PSW_ETD]), [Total PSW Cont], ...) ... RETURN y`

### Trendline Unconstraint

- Linear regression trendline for unconstrained supply quantities over the ETD axis.  
`VAR temp = LINESTX(ALLSELECTED('Item Master'[PSW_ETD]), [Total PSW Unconstraint], ...) ... RETURN y`

## Tables

### PSW

**Source type:** Warehouse (ashley-edw.database.windows.net / ASHLEY_EDW), with M-query merges from ODBC iSeries expressions (ItemVAL from AFIPROD/AMFLIBA and ItemMaster from AFIPROD/ADOWNLOAD)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item | string | Source column |
| ProdResourceID | string | Source column |
| Collective Class | string | Source column |
| Product Line | string | Source column |
| Cubes | double | Source column — item cubic volume |
| Item Class Code | string | Source column |
| Sellable Item Flag | string | Source column |
| Series number | string | Source column |
| Warehouse | string | Source column |
| Vendor | string | Source column — vendor code (600039/900639/624556/900515) |
| ETD | dateTime | Source column — estimated time of delivery (week ending) |
| Item Description | string | Source column |
| Ship_Qty | int64 | Source column |
| Firm_Qty | int64 | Source column |
| Plan_Qty | int64 | Source column |
| Unconstraint_Plan_Qty | int64 | Source column |
| UnconstraintKIT_Plan_Qty | int64 | Source column |
| Current SI | double | Source column — current shippable inventory |
| SI at Wk22 | double | Source column — projected shippable inventory at week 22 |
| HB Code | string | Source column — hold buy code |
| Current Status | string | Source column |
| Future Status | string | Source column |
| U Code | string | Source column — MFPUS from ITBEXT |
| SPRunDate | dateTime | Source column — snapshot run date |
| WeekNum | int64 | Source column — relative week offset |
| MB code | string | Source column — MK buy code |
| ITCLAD | string | Source column — item class code from iSeries ITMRVAL0 (merged from ItemVAL expression) |
| CATEGORY | string | Source column — item category from ITEMMASTERL01 (merged from ItemMaster expression) |
| General Vendor | string | Calculated: `IF(ISBLANK(PSW[Vendor]), "Unknown Vendor", IF(PSW[Vendor] = "624556", "MILLE", "WANEK"))` |
| Ship_cont | double | Calculated: `PSW[Ship_Qty] * PSW[Cubes] / 2300` |
| Plan_cont | double | Calculated: `PSW[Plan_Qty] * PSW[Cubes] / 2300` |
| Firm_cont | double | Calculated: `PSW[Firm_Qty] * PSW[Cubes] / 2300` |
| Production Resource | string | Calculated: extracts suffix after "-" in ProdResourceID; falls back to BLANK PROD lookup |
| Type | string | Calculated: classifies item as FG / RP / Kits / Components based on Sellable Flag, CATEGORY, ITCLAD, and Production Resource |
| Plan Unconstraint Qty | int64 | Calculated: `IF(Type = "FG", Unconstraint_Plan_Qty, UnconstraintKIT_Plan_Qty)` |
| Key | string | Calculated: `Type & General Vendor & ETD` |
| ReKey | string | Calculated: `ProdResourceID & ETD` |
| Timeline Key | string | Calculated: `Item & " " & Whse` |
| Whse | string | Calculated: normalizes Warehouse to AFT for non-specific warehouses |
| Status | string | Calculated: `Current Status & ":" & Future Status` |
| All Qty | int64 | Calculated: `Ship_Qty + Firm_Qty + Plan_Qty + Plan Unconstraint Qty` |
| ITEMETDVEndor Key | string | Calculated: `Item & "-" & ETD & "-" & Vendor` |
| Item-Vendor | string | Calculated: `Item & "-" & Vendor` |
| MainProdRe | string | Calculated: LOOKUPVALUE of Correct ProdResourceID from Production Resource Master |
| Main Production Resource | string | Calculated: extracts suffix after "-" in MainProdRe; falls back to BLANK PROD lookup |
| MB code | string | Source column |

**Source Query:**

```sql
WITH RankedFCL AS (
    SELECT
        [Item-lvl1],
        [Location],
        [MK_BuyCode],
        [Planning Vendor],
        [FileDate] AS [SnapshotDate],
        ROW_NUMBER() OVER (PARTITION BY [Item-lvl1], [Location], [Planning Vendor] ORDER BY [FileDate] DESC) AS RowNumber
    FROM
        [SupplyChain_Enh].[ForecastCommonContainer_Logility]
),

FCL AS (
    SELECT
        [Item-lvl1],
        [Location],
        [MK_BuyCode],
        [Planning Vendor],
        [SnapshotDate]
    FROM RankedFCL
    WHERE RowNumber = 1
),

LatestProdResource AS (
    SELECT ItemID, LocationID, ProdResourceID, [EndEffectiveDate], SnapshotDate
    FROM SupplyChain_Enh.ProductionConversion
    WHERE [SnapshotDate] = (SELECT MAX([SnapshotDate]) FROM SupplyChain_Enh.ProductionConversion)
    AND EndEffectiveDate BETWEEN GetDate() AND '2098-12-31'
    AND (
        [ProdResourceID] LIKE '600039%'
        OR [ProdResourceID] LIKE '900639%'
        OR [ProdResourceID] LIKE '624556%'
        OR [ProdResourceID] LIKE '900515%'
    )
),

AllProductionResource AS (
    SELECT ItemID, LocationID, ProdResourceID, [EndEffectiveDate], SnapshotDate,
        ROW_NUMBER() OVER (PARTITION BY ItemID, LocationID ORDER BY SnapshotDate DESC, EndEffectiveDate DESC) AS RowNumber
    FROM SupplyChain_Enh.ProductionConversion
    WHERE
        [ProdResourceID] LIKE '600039%'
        OR [ProdResourceID] LIKE '900639%'
        OR [ProdResourceID] LIKE '624556%'
        OR [ProdResourceID] LIKE '900515%'
),

RecentSnapshot AS (
    SELECT * FROM AllProductionResource WHERE RowNumber = 1
),

FinalProdResource AS (
    SELECT
        COALESCE(LatestProdResource.ItemID, RecentSnapshot.ItemID) AS [ItemID],
        COALESCE(LatestProdResource.LocationID, RecentSnapshot.LocationID) AS [LocationID],
        COALESCE(LatestProdResource.ProdResourceID, RecentSnapshot.ProdResourceID) AS [ProdResourceID],
        COALESCE(LatestProdResource.EndEffectiveDate, RecentSnapshot.EndEffectiveDate) AS [EndEffectiveDate],
        COALESCE(LatestProdResource.SnapshotDate, RecentSnapshot.SnapshotDate) AS [SnapshotDate]
    FROM LatestProdResource
    FULL OUTER JOIN RecentSnapshot
        ON LatestProdResource.ItemID = RecentSnapshot.ItemID
        AND LatestProdResource.LocationID = RecentSnapshot.LocationID
),

Unconstraint AS (
    SELECT
        LatestProdResource.ProdResourceID,
        [UPQ].[uprID],
        [UPQ].[uprItem] AS Item,
        [UPQ].[uprItemDescription] AS ItemDSC,
        [UPQ].[uprWarehouse] AS Warehouse,
        [UPQ].[uprVendorNumber] AS Vendor,
        [UPQ].[uprOrderNumber],
        [UPQ].[uprQuantity] AS [Unconstraint Qty],
        [UPQ].[uprDueDate],
        [UPQ].[uprShipDate],
        FCL.[MK_BuyCODE] AS [MB code],
        CONVERT(DATE, CAST([UPQ].[uprShipDate] AS VARCHAR(8)), 112) AS ETD,
        [UPQ].[usra],
        [UPQ].[dtea],
        [UPQ].[usrc],
        [UPQ].[dtec]
    FROM [Wholesale_DemandPlanning_AFI].[UnconstrainedPlannedRequirements] AS UPQ
    LEFT JOIN [Enterprise_DW].[DimDate] DD
        ON CAST(DD.[DateID] AS DATE) = CONVERT(DATE, CAST([UPQ].[uprShipDate] AS VARCHAR(8)), 112)
    LEFT JOIN FCL
        ON [UPQ].[uprItem] = FCL.[Item-lvl1]
        AND [UPQ].[uprWarehouse] = FCL.[Location]
        AND [UPQ].[uprVendorNumber] = FCL.[Planning Vendor]
    LEFT JOIN LatestProdResource
        ON [UPQ].[uprItem] = LatestProdResource.[ItemID]
        AND [UPQ].[uprVendorNumber] = LatestProdResource.[LocationID]
    WHERE
        DD.[CalendarWeekIndicator] BETWEEN 0 AND 30
        AND [UPQ].[dtea] = (SELECT MAX([dtea]) FROM [Wholesale_DemandPlanning_AFI].[UnconstrainedPlannedRequirements])
        AND [UPQ].[uprVendorNumber] IN ('600039','900515','900639','624556')
        AND [UPQ].[uprQuantity] > 0
        AND [UPQ].[uprItem] NOT LIKE '%SW'
        AND [UPQ].[uprItem] NOT LIKE '%CARD%'
        AND [UPQ].[uprItem] NOT LIKE '%VINYL%'
        AND [UPQ].[uprItem] NOT LIKE '%HIDES%'
),

Uncons AS (
    SELECT
        CASE WHEN Unconstraint.ProdResourceID IS NULL THEN LatestProdResource.ProdResourceID
             ELSE Unconstraint.ProdResourceID END AS ProdResource,
        Unconstraint.*
    FROM Unconstraint
    LEFT JOIN LatestProdResource ON Unconstraint.[Item] = LatestProdResource.[ItemID]
),

Cons AS (
    SELECT
        FinalProdResource.[ProdResourceID],
        PSW.[Item],
        PSW.[Whse],
        PSW.[Whse] AS [Warehouse],
        PSW.[Vendor],
        PSW.[WeekNum],
        CAST(DATEADD(DAY, 7 - DATEPART(WEEKDAY, PSW.[SPRunDate]), PSW.[SPRunDate]) + PSW.[WeekNum] * 7 AS DATE) AS ETD,
        PSW.[ITDESC],
        PSW.[VNAME],
        CAST(PSW.[SQty] AS INT) AS Ship_Qty,
        CAST(PSW.[FQty] AS INT) AS Firm_Qty,
        CAST(PSW.[PQty] AS INT) AS Plan_Qty,
        PSW.[SPRunDate]
    FROM [SupplyChain_Enh].[PSWWeeklyExtractSnapshot] PSW
    LEFT JOIN FinalProdResource
        ON PSW.Item = FinalProdResource.[ItemID]
        AND PSW.[Vendor] = FinalProdResource.[LocationID]
    WHERE
        PSW.[Vendor] IN ('600039','900515','900639','624556')
        AND PSW.[WeekNum] BETWEEN -8 AND 30
        AND (PSW.[SQty] + PSW.[FQty] + PSW.[PQty]) > 0
        AND PSW.[Item] NOT LIKE '%SW'
        AND PSW.[Item] NOT LIKE '%CARD%'
        AND PSW.[Item] NOT LIKE '%VINYL%'
        AND PSW.[Item] NOT LIKE '%HIDES%'
        AND CAST(PSW.[SPRunDate] AS DATE) = (SELECT CAST(MAX([SPRunDate]) AS DATE) FROM [SupplyChain_Enh].[PSWWeeklyExtractSnapshot])
),

PSW AS (
    SELECT
        COALESCE(CONS.[Item], UnCONS.[Item]) AS [Item],
        COALESCE(CONS.[ITDESC], UnCONS.[ItemDSC]) AS [Item Description],
        COALESCE(CONS.[Vendor], LEFT(UnCONS.[ProdResource],6)) AS [Vendor],
        COALESCE(CONS.[Warehouse], UnCONS.[Warehouse]) AS [Warehouse],
        COALESCE(CONS.[ProdResourceID], UnCONS.[ProdResource]) AS [ProdResourceID],
        COALESCE(CONS.[ETD], UnCONS.[ETD]) AS [ETD],
        COALESCE(CONS.Ship_Qty,0) AS Ship_Qty,
        COALESCE(CONS.Firm_Qty,0) AS Firm_Qty,
        COALESCE(CONS.Plan_Qty,0) AS Plan_Qty,
        COALESCE(UNCONS.[Unconstraint Qty],0) AS Unconstraint_Plan_Qty,
        UNCONS.[MB Code],
        Cons.SPRunDate,
        Cons.WeekNum
    FROM Cons
    FULL OUTER JOIN Uncons
        ON CONS.[Item] = Uncons.Item
        AND CONS.[ProdResourceID] = Uncons.ProdResource
        AND CONS.[Warehouse] = Uncons.Warehouse
        AND CONS.ETD = Uncons.ETD
),

PDTL AS (
    SELECT
        PTLITNBR AS [Item],
        PTLWHSE AS [Whse],
        PTLWEEK1 AS [Current SI],
        PTLWEEK22 AS [SI at Wk22]
    FROM [Wholesale_DemandPlanning_AFI].[PlanDetailTimeline]
    WHERE PTLDATATYPE = 'SHIPPABLE INV'
    AND dtea = (SELECT MAX(dtea) FROM [Wholesale_DemandPlanning_AFI].[PlanDetailTimeline])
)

SELECT
    PSW.[Item],
    PSW.[ProdResourceID],
    CPD.[Collective Class],
    CPD.[Product Line],
    CPD.[Cubes],
    CPD.[Item Class Code],
    CPD.[Sellable Item Flag],
    CPD.[Series number],
    PSW.[Warehouse],
    PSW.[Vendor],
    PSW.ETD,
    PSW.[Item Description],
    PSW.Ship_Qty,
    PSW.Firm_Qty,
    PSW.Plan_Qty,
    CASE WHEN PSW.[MB Code] = 'B' THEN CAST(PSW.Unconstraint_Plan_Qty AS INT) ELSE 0 END AS Unconstraint_Plan_Qty,
    CAST(PSW.Unconstraint_Plan_Qty AS INT) AS UnconstraintKIT_Plan_Qty,
    PDTL.[Current SI],
    PDTL.[SI at Wk22],
    FCL.[MK_BuyCODE] AS [MB code],
    CPD.[HOLD BUY CODE],
    CPD.[Current Status],
    CPD.[Future Status],
    ITBEXT.MFPUS AS [U Code],
    PSW.SPRunDate,
    PSW.WeekNum
FROM PSW
LEFT JOIN [PowerBI_SupplyChain].[CurrentProductDetails] CPD ON PSW.[Item] = CPD.[Item SKU]
LEFT JOIN PDTL ON (PSW.[Item] = PDTL.[Item] AND PSW.[Warehouse] = PDTL.[Whse])
LEFT JOIN [MasterData_ItemMaster_AFI].[ITBEXT] ON (PSW.[Item] = ITBEXT.[ITNBR] AND PSW.[Warehouse] = ITBEXT.[HOUSE])
LEFT JOIN FCL
    ON [PSW].[Item] = FCL.[Item-lvl1]
    AND [PSW].[Warehouse] = FCL.[Location]
    AND PSW.[Vendor] = FCL.[Planning Vendor]
```

*After loading, the M query merges ItemVAL (ODBC: AFIPROD/AMFLIBA.ITMRVAL0 — item class codes) and ItemMaster (ODBC: AFIPROD/ADOWNLOAD.ITEMMASTERL01 — item categories) via left join on Item number.*

---

### Capacity Actual

**Source type:** SharePoint (Excel) — `https://masterashley.sharepoint.com/sites/SCPGlobalTeam-Tools/Shared%20Documents/Tools/Capacity%20Master.xlsx`, sheet "Wanek & Millen"

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Production Resource | string | Source column |
| Number | string | Source column |
| Office | string | Source column |
| GSCA | string | Source column — global supply chain analyst |
| GSCP | string | Source column — global supply chain planner |
| Date Updated | string | Source column |
| GSCP/GSCA Note | string | Source column |
| GSCA Approval | string | Source column |
| Attribute | dateTime | Source column — week date (unpivoted from column headers) |
| Override Cap | int64 | Source column — capacity override value (renamed from "Value" after filter for ACT = "ACT PCS" or "Override") |
| ReKey | string | Calculated: `Production Resource & Attribute` |

*(Source filters rows where ACT = "ACT PCS" or "Override" and Attribute > 2024-09-16; unpivots date columns to rows)*

---

### Capacity Promise

**Source type:** SharePoint (Excel) — `https://masterashley.sharepoint.com/sites/SCPGlobalTeam-Tools/Shared%20Documents/Tools/Capacity%20Master.xlsx`, sheet "Wanek & Millen"

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Production Resource | string | Source column |
| Number | string | Source column |
| Office | string | Source column |
| GSCA | string | Source column |
| GSCP | string | Source column |
| ACT | string | Source column |
| Date Updated | string | Source column |
| GSCP/GSCA Note | string | Source column |
| GSCA Approval | string | Source column |
| Attribute | dateTime | Source column — week date (unpivoted) |
| Value | int64 | Source column — promised capacity value |
| ReKey | string | Calculated: `Production Resource & Attribute` |

*(Same source and shape as Capacity Actual but filters for ACT = "Promised")*

---

### Item Master

**Source type:** Calculated DAX table (UNION of distinct Item/ETD/Vendor rows from PSW, RP Scan, and FG Output)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| PSW_Item | string | Source: PSW[Item] |
| PSW_ETD | dateTime | Source: PSW[ETD] |
| PSW_Vendor | string | Source: PSW[Vendor] |
| Key | string | Calculated: `PSW_Item & "-" & PSW_ETD & "-" & PSW_Vendor` |
| Type | string | Calculated: LOOKUPVALUE from PSW[Type] |
| Prod Resource Key | string | Calculated: `PSW_Item & "-" & PSW_Vendor` |
| ProdResource | string | Calculated: LOOKUPVALUE from Production Resource Master or BLANK PROD fallback |
| Status | string | Calculated: LOOKUPVALUE from PSW[Status] |
| Series | string | Calculated: LOOKUPVALUE from PSW[Series number] |
| Prod Resource | string | Calculated: extracts suffix after "-" from ProdResource |
| General Vendor | string | Calculated: `IF(PSW_Vendor = "624556", "Mille", "Wanek")` |
| MainProdResource | string | Calculated: LOOKUPVALUE of Correct ProdResourceID from Production Resource Master or BLANK PROD fallback |
| Main Prod Resource | string | Calculated: extracts suffix after "-" from MainProdResource |
| Switch Key | string | Calculated: alternate vendor key for cross-vendor production resource lookup |

*(RP Scan rows included only where New Item is not blank and ETD >= MIN(PSW[ETD]); same filter for FG Output)*

---

### FG Output

**Source type:** ODBC iSeries — combines Wanek (WFVNPROD/AMFLIBW) and Millenium (MILPROD/AMFLIBL) production output scans

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| UDDMOR | string | Source column — manufacture order number |
| UDDITM | string | Source column — item number |
| JOBNO | string | Source column — job number |
| QTY | int64 | Source column — scanned output quantity |
| Jobno Date | dateTime | Calculated: parses date from JOBNO string |
| ETD | dateTime | Calculated: `Jobno Date + 7 - WEEKDAY(Jobno Date)` — rounds up to week ending Saturday |
| New Item | string | Calculated: LOOKUPVALUE of PSW[Item] by UDDITM |
| Key | string | Calculated: `UDDITM & "-" & ETD & "-" & Output Vendor` |
| Output Vendor | string | Calculated: `IF(LEFT(UDDMOR,2) = "MC", "624556", IF(LEFT(UDDMOR,2) = "MX", "600039", "900639"))` |

**Wanek Output Query (ODBC — System: WFVNPROD, Collection: AMFLIBW):**

```sql
With OutputScan as (
    SELECT
        DWUPHSCND.UDDMOR,
        DWUPHSCND.UDDITM,
        DWUPHSCND.UDDSER,
        COALESCE(AMFLIBW.MOHMST.JOBNO, AMFLIBW.MOMAST.JOBNO) as JOBNO
    FROM G20ACF9V.WWUSAF.DWUPHSCND DWUPHSCND
    LEFT JOIN AFILELIBW.DATEFILE ON RIGHT(UDDDAT, 6) = KYDATE
    LEFT JOIN AMFLIBW.MOHMST ON (DWUPHSCND.UDDMOR = AMFLIBW.MOHMST.ORDNO AND DWUPHSCND.UDDITM = AMFLIBW.MOHMST.FITEM)
    LEFT JOIN AMFLIBW.MOMAST ON (DWUPHSCND.UDDMOR = AMFLIBW.MOMAST.ORDNO AND DWUPHSCND.UDDITM = AMFLIBW.MOMAST.FITEM)
    WHERE
        ((WEEK(CURRENT DATE) <= 12 AND FWK# <= WEEK(CURRENT DATE) AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2))
           OR (WEEK(CURRENT DATE) <= 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE) - 1), 2)
                 AND FWK# >= (52 - 12 + WEEK(CURRENT DATE)))
            OR (WEEK(CURRENT DATE) > 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2)
                AND (FWK# BETWEEN (WEEK(CURRENT DATE) - 12) AND WEEK(CURRENT DATE))))
        AND (DWUPHSCND.UDDMOR LIKE 'MX%' OR DWUPHSCND.UDDMOR LIKE 'MY%')
)
Select UDDMOR, UDDITM, JOBNO, Count(UDDSER) as Qty
from OutputScan
group by UDDMOR, UDDITM, JOBNO
```

**Mille Output Query (ODBC — System: MILPROD, Collection: AMFLIBL):**

```sql
With OutputScan as (
    SELECT
        DWUPHSCND.UDDMOR,
        DWUPHSCND.UDDITM,
        DWUPHSCND.UDDSER,
        COALESCE(AMFLIBL.MOHMST.JOBNO, AMFLIBL.MOMAST.JOBNO) as JOBNO
    FROM LLUSAF.DWUPHSCND DWUPHSCND
    LEFT JOIN AFILELIBL.DATEFILE ON RIGHT(UDDDAT, 6) = KYDATE
    LEFT JOIN AMFLIBL.MOHMST ON (DWUPHSCND.UDDMOR = AMFLIBL.MOHMST.ORDNO AND DWUPHSCND.UDDITM = AMFLIBL.MOHMST.FITEM)
    LEFT JOIN AMFLIBL.MOMAST ON (DWUPHSCND.UDDMOR = AMFLIBL.MOMAST.ORDNO AND DWUPHSCND.UDDITM = AMFLIBL.MOMAST.FITEM)
    WHERE
        ((WEEK(CURRENT DATE) <= 12 AND FWK# <= WEEK(CURRENT DATE) AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2))
           OR (WEEK(CURRENT DATE) <= 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE) - 1), 2)
                 AND FWK# >= (52 - 12 + WEEK(CURRENT DATE)))
            OR (WEEK(CURRENT DATE) > 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2)
                AND (FWK# BETWEEN (WEEK(CURRENT DATE) - 12) AND WEEK(CURRENT DATE))))
        AND DWUPHSCND.UDDMOR LIKE 'MC%'
)
Select UDDMOR, UDDITM, JOBNO, Count(UDDSER) as Qty
from OutputScan
group by UDDMOR, UDDITM, JOBNO
```

---

### RP Scan

**Source type:** ODBC iSeries — combines Wanek (WFVNPROD/AMFLIBW) and Millenium (MILPROD/AMFLIBL) roll-pack/ready-pack scan records

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ORDNO | string | Source column — order number |
| ITNBR | string | Source column — item number |
| JOBNO | string | Source column — job number |
| Vendor | string | Source column — added by M transform (based on HOUSE code or hardcoded for Mille) |
| QTY | double | Source column — scan quantity |
| SCANYEAR | string | Source column |
| TRNDT | double | Source column — transaction date (encoded) |
| Jobno Date | dateTime | Calculated: parses from JOBNO (MX/MY/MC orders) or from SCANYEAR + TRNDT |
| ETD | dateTime | Calculated: `Jobno Date + 7 - WEEKDAY(Jobno Date)` |
| TRNDATE | dateTime | Calculated: decoded from TRNDT numeric |
| New ETD | dateTime | Calculated: `7 + TRNDATE - WEEKDAY(TRNDATE)` |
| First MO | string | Calculated: `LEFT(ORDNO, 2)` — manufacture order prefix |
| New Item | string | Calculated: LOOKUPVALUE from PSW[Item] by ITNBR |
| Key | string | Calculated: `ITNBR & "-" & ETD & "-" & Vendor` |

**Wanek RP Scan Query (ODBC — System: WFVNPROD, Collection: AMFLIBW):**

```sql
WITH ITM AS (
    SELECT DISTINCT Item, Category FROM ADOWNLOADW.ITEMMASTERL01
),
ITV AS (
    SELECT DISTINCT ITNOAD, ITCLAD FROM AMFLIBW.ITMRVAL0
),
RPOutput AS (
    SELECT
        IMHIST.ORDNO, IMHIST.ITNBR, IMHIST.TRQTY, IMHIST.TRNDT, IMHIST.HOUSE,
        SUBSTR(IMHIST.TRNDT, 2, 2) AS ScanYear,
        COALESCE(AMFLIBW.MOHMST.JOBNO, AMFLIBW.MOMAST.JOBNO) AS JOBNO
    FROM AMFLIBW.IMHIST IMHIST
    LEFT JOIN AFILELIBW.DATEFILE ON RIGHT(TRNDT, 6) = KYDATE
    LEFT JOIN ITM ON IMHIST.ITNBR = ITM.ITEM
    LEFT JOIN ITV ON IMHIST.ITNBR = ITV.ITNOAD
    LEFT JOIN AMFLIBW.MOHMST ON (IMHIST.ORDNO = AMFLIBW.MOHMST.ORDNO) AND (IMHIST.ITNBR = AMFLIBW.MOHMST.FITEM)
    LEFT JOIN AMFLIBW.MOMAST ON (IMHIST.ORDNO = AMFLIBW.MOMAST.ORDNO) AND (IMHIST.ITNBR = AMFLIBW.MOMAST.FITEM)
    WHERE
        IMHIST.ORDNO IS NOT NULL
        AND TCODE = 'RM'
        AND TRQTY > 0
        AND (ITM.CATEGORY LIKE '%RP%' OR ITV.ITCLAD IN ('CIRP', 'RPMT', 'RPRT', 'TA', 'UDRP', 'UERF', 'UIRP'))
        AND ((WEEK(CURRENT DATE) <= 12 AND FWK# <= WEEK(CURRENT DATE) AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2))
           OR (WEEK(CURRENT DATE) <= 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE) - 1), 2)
                 AND FWK# >= (52 - 12 + WEEK(CURRENT DATE)))
            OR (WEEK(CURRENT DATE) > 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2)
                AND (FWK# BETWEEN (WEEK(CURRENT DATE) - 12) AND WEEK(CURRENT DATE))))
)
SELECT ORDNO, ITNBR, JOBNO, ScanYear, TRNDT, Sum(TRQTY) AS Qty, HOUSE
FROM RPOutput
GROUP BY ORDNO, ITNBR, JOBNO, ScanYear, TRNDT, HOUSE
```

*(After load, M adds Vendor based on HOUSE code: 31 → 900515, 33 → 900639, else 600039)*

**Mille RP SCan Query (ODBC — System: MILPROD, Collection: AMFLIBL):**

```sql
WITH ITM AS (
    SELECT DISTINCT Item, Category FROM ADOWNLOADL.ITEMMASTERL01
),
ITV AS (
    SELECT DISTINCT ITNOAD, ITCLAD FROM AMFLIBL.ITMRVAL0
),
RPOutput AS (
    SELECT
        IMHIST.ORDNO, IMHIST.ITNBR, IMHIST.TRQTY, IMHIST.TRNDT,
        SUBSTR(IMHIST.TRNDT, 2, 2) AS ScanYear,
        COALESCE(AMFLIBL.MOHMST.JOBNO, AMFLIBL.MOMAST.JOBNO) AS JOBNO
    FROM AMFLIBL.IMHIST IMHIST
    LEFT JOIN AFILELIBL.DATEFILE ON RIGHT(TRNDT, 6) = KYDATE
    LEFT JOIN ITM ON IMHIST.ITNBR = ITM.ITEM
    LEFT JOIN ITV ON IMHIST.ITNBR = ITV.ITNOAD
    LEFT JOIN AMFLIBL.MOHMST ON (IMHIST.ORDNO = AMFLIBL.MOHMST.ORDNO) AND (IMHIST.ITNBR = AMFLIBL.MOHMST.FITEM)
    LEFT JOIN AMFLIBL.MOMAST ON (IMHIST.ORDNO = AMFLIBL.MOMAST.ORDNO) AND (IMHIST.ITNBR = AMFLIBL.MOMAST.FITEM)
    WHERE
        IMHIST.ORDNO IS NOT NULL
        AND TCODE = 'RM'
        AND TRQTY > 0
        AND (ITM.CATEGORY LIKE '%RP%' OR ITV.ITCLAD IN ('CIRP', 'RPMT', 'RPRT', 'TA', 'UDRP', 'UERF', 'UIRP'))
        AND ((WEEK(CURRENT DATE) <= 12 AND FWK# <= WEEK(CURRENT DATE) AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2))
           OR (WEEK(CURRENT DATE) <= 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE) - 1), 2)
                 AND FWK# >= (52 - 12 + WEEK(CURRENT DATE)))
            OR (WEEK(CURRENT DATE) > 12 AND FYR# = RIGHT(DIGITS(YEAR(CURRENT DATE)), 2)
                AND (FWK# BETWEEN (WEEK(CURRENT DATE) - 12) AND WEEK(CURRENT DATE))))
)
SELECT ORDNO, ITNBR, JOBNO, ScanYear, TRNDT, Sum(TRQTY) AS Qty
FROM RPOutput
GROUP BY ORDNO, ITNBR, JOBNO, ScanYear, TRNDT
```

*(Vendor hardcoded to "624556" for all Mille rows via M transform)*

---

### BLANK PROD

**Source type:** SharePoint (Excel) — `https://masterashley.sharepoint.com/sites/SCPGlobalTeam-Tools/Shared%20Documents/Tools/Inhouse%20Data%20(Do%20not%20move)/Wanek_Blank%20PROD%20SKU.xlsx`, Sheet1

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item # | string | Source column |
| Class RM | string | Source column |
| Type | string | Source column |
| Item_Status | string | Source column |
| Future_status | string | Source column |
| HB | string | Source column — hold buy code |
| Corrected Prod | string | Source column — corrected production resource ID |
| PROD | string | Source column |
| Vendor | string | Calculated: `LEFT(Corrected Prod, 6)` — extracted from production resource prefix |
| Item-Vendor | string | Calculated: `Item # & "-" & Vendor` |

*(Manual override table for items where ProdResourceID is blank in the warehouse data)*

---

### Current Product Detail

**Source type:** Warehouse (ashley-edw.database.windows.net / ASHLEY_EDW)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| Item SKU | string | Source column |
| Item Description | string | Source column |
| Item Class Code | string | Source column |
| Product Line | string | Source column |
| Collective Class | string | Source column |
| Sellable Item Flag | string | Source column |

**Source Query:**

```sql
SELECT
    [Item SKU],
    [Item Description],
    [Item Class Code],
    [Product Line],
    [Collective Class],
    [Sellable Item Flag]
FROM [PowerBI_SupplyChain].[CurrentProductDetails]
```

---

### Latest Update

**Source type:** Warehouse (ashley-edw.database.windows.net / ASHLEY_EDW)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| tpkServerName | string | Source column |
| tpkDatabaseName | string | Source column |
| tpkSchemaName | string | Source column |
| tpkTableName | string | Source column |
| tpkObjectType | string | Source column |
| tpkPrimaryKey | string | Source column |
| tpkStorageType | string | Source column |
| tpkSourceSystem | string | Source column |
| tpkSourceServer | string | Source column |
| tpkSourceDatabase | string | Source column |
| tpkSourceObject | string | Source column |
| tpkETLTool | string | Source column |
| tpkRefreshRate | int64 | Source column |
| tpkRefreshDescription | string | Source column |
| tpkUpdateMethod | string | Source column |
| tpkCreateDate | dateTime | Source column |
| tpkModified | dateTime | Source column |
| tpkLastAudit | dateTime | Source column |
| tpkCreatedDate | dateTime | Source column |
| tpkCreated | dateTime | Source column |
| tpkColumnStatsLastUpdated | dateTime | Source column |
| tpkLastBatchStartDate | dateTime | Source column |
| tpkRowCount | double | Source column |
| tpkInvalidCount | double | Source column |
| tpkColumnStatsCount | int64 | Source column |
| tpkColumnCount | int64 | Source column |
| tpkValidKeyValues | boolean | Source column |
| *(+ additional tpk* metadata columns)* | various | Source columns — ETL/data platform tracking metadata |

**Source Query:**

```sql
SELECT TOP(10) * FROM [DW_Developer].[TableDictionary]
WHERE tpkTableName LIKE '%PSWWeeklyExtractSnapshot%'
```

*(Metadata table — surfaces last-refresh timestamps for the PSW source table; used to display data freshness in the report)*

---

### Production Resource Master

**Source type:** Warehouse (ashley-edw.database.windows.net / ASHLEY_EDW)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| ItemID | string | Source column |
| LocationID | string | Source column — vendor code |
| ProdResourceID | string | Source column |
| EndEffectiveDate | string | Source column |
| SnapshotDate | string | Source column |
| Correct ProdResourceID | string | Source column — corrected value (prefers latest effective record) |
| Item-Location Key | string | Source column — composite key from M query |
| Row Count by Key | string | Source column — count of records per key |
| Sequence Number | string | Source column — 1 = selected record per key |
| Key | string | Calculated: `ItemID & "-" & LocationID` |
| count | int64 | Calculated: `COUNTROWS` per Key (ALLEXCEPT) |

**Source Query:**

```sql
WITH Latest AS (
    SELECT ItemID, LocationID, ProdResourceID, [EndEffectiveDate], SnapshotDate
    FROM SupplyChain_Enh.ProductionConversion
    WHERE [SnapshotDate] = (SELECT MAX([SnapshotDate]) FROM SupplyChain_Enh.ProductionConversion)
    AND [EndEffectiveDate] IS NOT NULL AND [EndEffectiveDate] >= GETDATE()
    AND (
        [ProdResourceID] LIKE '600039%'
        OR [ProdResourceID] LIKE '900639%'
        OR [ProdResourceID] LIKE '624556%'
        OR [ProdResourceID] LIKE '900515%'
    )
),
AllProductionResource AS (
    SELECT ItemID, LocationID, ProdResourceID, [EndEffectiveDate], SnapshotDate,
        ROW_NUMBER() OVER (PARTITION BY ItemID, LocationID ORDER BY SnapshotDate DESC) AS RowNumber
    FROM SupplyChain_Enh.ProductionConversion
    WHERE [EndEffectiveDate] IS NOT NULL
    AND (
        [ProdResourceID] LIKE '600039%'
        OR [ProdResourceID] LIKE '900639%'
        OR [ProdResourceID] LIKE '624556%'
        OR [ProdResourceID] LIKE '900515%'
    )
),
RecentSnapshot AS (
    SELECT * FROM AllProductionResource WHERE RowNumber = 1
),
AllProd AS (
    SELECT
        COALESCE(Latest.ItemID, RecentSnapshot.ItemID) AS [ItemID],
        COALESCE(Latest.LocationID, RecentSnapshot.LocationID) AS [LocationID],
        COALESCE(Latest.ProdResourceID, RecentSnapshot.ProdResourceID) AS [ProdResourceID],
        COALESCE(Latest.EndEffectiveDate, RecentSnapshot.EndEffectiveDate) AS [EndEffectiveDate],
        COALESCE(Latest.SnapshotDate, RecentSnapshot.SnapshotDate) AS [SnapshotDate]
    FROM Latest
    FULL OUTER JOIN RecentSnapshot
        ON Latest.ItemID = RecentSnapshot.ItemID
        AND Latest.LocationID = RecentSnapshot.LocationID
)
SELECT AllProd.*,
    CASE
        WHEN Latest.ProdResourceID IS NULL THEN AllProd.[ProdResourceID]
        ELSE Latest.ProdResourceID
    END AS [Correct ProdResourceID]
FROM AllProd
LEFT JOIN Latest ON Latest.ItemID = AllProd.ItemID
```

*(M post-processing: deduplicated to Sequence Number = 1 per Item-Location Key; BLANK PROD is left-joined to fill in Corrected Prod and Vendor for items with null ProdResourceID)*

---

### SISS Timeline

**Source type:** Warehouse (ashley-edw.database.windows.net / ASHLEY_EDW)

**Columns:**

| Column | Data Type | Notes |
| --- | --- | --- |
| SPDItem | string | Source column — item number |
| spdWarehouse | string | Source column |
| spdWeekEnding | dateTime | Source column — week ending date |
| spdShippableInventory | double | Source column |
| spdSafetyStock | double | Source column |
| PSW Key | string | Calculated: `SPDItem & " " & spdWarehouse` |

**Source Query:**

```sql
SELECT
    SPDItem,
    spdWarehouse,
    spdWeekEnding,
    spdShippableInventory,
    spdSafetyStock
FROM [Wholesale_DemandPlanning_AFI].[SupplyPlanDetail]
WHERE dtec = (SELECT MAX(dtec) FROM [Wholesale_DemandPlanning_AFI].[SupplyPlanDetail])
AND spdWeekEnding = (SELECT MAX(spdWeekEnding) FROM [Wholesale_DemandPlanning_AFI].[SupplyPlanDetail])
```

*(Latest snapshot only; most recent week ending only — provides current shippable inventory and safety stock for the SISS timeline visual)*
