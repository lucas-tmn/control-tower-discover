---
type: Query
title: Vendor Master Query
description: EDW SQL query that produces the vendor master shape.
tags: [vendor, master-data, procurement, supply-planning, dimension, query]
timestamp: 2026-07-06
resource: "[Wholesale_Purchasing_AFI].[Vennam]"
source_system: ERP
refresh_cadence: daily
data_source: ashley_edw
status: draft
---

## Purpose

Central vendor dimension for supply chain planning. Provides a single source of truth for vendor attributes — lead times, location, country of origin, and active status — used across procurement, supply planning, and on-time performance reporting.

Vendor-level aggregates such as open purchase orders and vendor ranking are not stored in this table; they are computed at report time in the measure layer.

---

## Grain

Each row represents a unique **vendor** (`VendorNumber`). Both active and inactive vendors are included; use the `VendorActive` flag to filter to active vendors only when appropriate for the analysis.

---

## Schema

### Identity

| Column | Type | Meaning |
| --- | --- | --- |
| `VendorNumber` | VARCHAR(8) | Primary key — vendor identifier; used as FK in `FactPSW`, `FactReceipts`, `FactOnTime`, and `FactProduction` |
| `VendorName` | VARCHAR(40) | Vendor legal or trading name from `VENNAM` |
| `VendorDesc` | VARCHAR(60) | ETL-computed: `CONCAT(RTRIM(VendorName), ' - ', RTRIM(VendorNumber))`; convenience label for visuals and slicers |

### Attributes

| Column | Type | Meaning |
| --- | --- | --- |
| `VendorOffice` | VARCHAR(20) | Office or division designation; used for vendor office-level grouping in supply planning and sourcing reports |
| `VendorOfficeLocation` | VARCHAR(40) | Country or region derived from the vendor office code |
| `Country` | VARCHAR(50) | Country of origin or country of vendor's primary location; supports import vs. domestic segmentation |
| `LeadTime` | INT | Standard lead time in days; sourced from vendor master for use in supply planning calculations |
| `VendorActive` | VARCHAR(3) | Active status label (`Yes`/`No`); filters active vs. inactive vendors in reporting and gold fact loads |
| `Vendor Import Domestic Flag` | VARCHAR(8) | Import/domestic classification derived from `EXTVNDR.ProductOrigin`; NULL and `I` values are treated as Import |

---

## Related

- [Vendor](/entities/vendor.md) — Business definition, active status, and lead time context for the Vendor entity

## Base Query

Use this query to produce the Vendor Master shape while the gold `DimVendor` table is unavailable.

```sql
SELECT V.VendorNumber
	  ,V.VendorName
	  ,V.[VendorDesc]
	  ,V.[Office] AS [VendorOffice]
      ,[VendorOfficeLocation] = 
			CASE 
				WHEN V.[Office] = 'ACROS' THEN 'CHINA'
				WHEN V.[Office] = 'AMLO' THEN 'MALAYSIA'
				WHEN V.[Office] = 'CINRO' THEN 'INDIA'
				WHEN V.[Office] = 'CVRO' THEN 'VIETNAM'
				WHEN V.[Office] = 'RKD' THEN 'USA'
				WHEN V.[Office] = 'WBOC' THEN 'CHINA'
				WHEN V.[Office] = 'ACLO' THEN 'CAMBODIA'
				WHEN V.[Office] = 'ABLO' THEN 'BANGLADESH'
				WHEN V.[Office] = 'THAI' THEN 'THAILAND'
				WHEN V.[Office] = 'MYAN' THEN 'MAYANMAR'
				WHEN V.[Office] = 'ATLO' THEN 'TAIWAN R.O.C'
				WHEN V.[Office] = 'CIRO' THEN 'INDONESIA'
				WHEN V.[Office] = 'CANA' THEN 'CANADA'
				WHEN V.[Office] = 'MARO' THEN 'MOROCCO'
				WHEN V.[Office] = 'MXCO' THEN 'MEXICO'
				WHEN V.[Office] = 'MILLE' THEN 'VIETNAM'
				WHEN V.[Office] = 'WANEK' THEN 'VIETNAM'
				WHEN V.[Office] = 'LAOS' THEN 'LAOS'
				WHEN V.[Office] = 'SGPR' THEN 'SINGAPORE'
				WHEN V.[Office] = 'SLKA' THEN 'SRI LANKA'
				WHEN V.[Office] = 'TRKY' THEN 'TURKEY'

				ELSE 'N/A'
			END				
	  ,V.Country
	  -- Need for keeping existing name. Defaults to AFI Lead time, takes WVF lead time where unique to WVF
	  ,A.[LEAD_TIME] AS [LeadTime] 
	  ,[VendorActive] = 
			CASE
				WHEN [A].[Active] = '1'
					THEN 'Yes'
				ELSE 'No'
			END
	  ,[Vendor Import Domestic Flag] = 
			CASE 
				WHEN [A].[ProductOrigin] = 'I' OR [A].[ProductOrigin] IS NULL THEN 'Import'
				WHEN [A].[ProductOrigin] = 'D' THEN 'Domestic'
				ELSE 'N/A'
			END
FROM (

SELECT RTRIM(V.[VNDNR]) AS [VendorNumber]
		,RTRIM(V.[VNAME]) AS [VendorName]
		,V.[VNAMA] AS [Office]
		,CONCAT(RTRIM(V.[VNAME]),' - ',RTRIM(V.[VNDNR])) AS [VendorDesc]
		,V.[VCNTR] AS [Country]
	FROM [Wholesale_Purchasing_AFI].[Vennam] AS V
	WHERE [VNAMA] IN ('ACROS','AMLO','CINRO','CVRO','RKD','WBOC','ACLO'
                      ,'ABLO','THAI','MYAN', 'ATLO', 'CANA', 'CIRO','MARO','MXCO'
					  ,'MILLE', 'WANEK','LAOS','SLKA','SGPR','TRKY'
					  )


	) AS V
	LEFT JOIN [Wholesale_Purchasing_AFI].[EXTVNDR] AS A
	 ON V.VendorNumber = A.[VEND_NUM]
```

