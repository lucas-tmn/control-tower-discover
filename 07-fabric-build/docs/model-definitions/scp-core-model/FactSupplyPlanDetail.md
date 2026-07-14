---
title: FactSupplyPlanDetail table documentation
domain: Supply Chain Planning 
fabric_warehouse_name: SupplyChain_Gold
table_name: FactSupplyPlanDetail 
schema: <schema> 
last_updated: 2026-06-16  
owner: Supply Chain Planning  

---

## 1. Purpose & Business Context

Current day's extract of the Logility Supply Plan for operations. Shows the weekending inventory projections (Shippable Inventory) net of customer demand, forecast, production, purchase orders, and transfer activity.  

---

## 2. Physical Table Definition

```sql
CREATE TABLE <schema>.FactSupplyPlanDetail (
    [ItemSKU] VARCHAR(20) NOT NULL,        -- Foreign key to DimProduct
    [WarehouseID] VARCHAR(10) NOT NULL,      -- Foreign key to DimWarehouse
    [WeekEnding] DATE NOT NULL,            -- Foreign key to DimDate (Transaction Date)
    [BeginningBalance] INT NOT NULL,       -- Beginning inventory balance
    [FirmDemand] INT NOT NULL,             -- Firm demand quantity
    [Promo Lift] INT NOT NULL,             -- Weekly promotional lift quantity
    [NetForecast] INT NOT NULL,            -- Net forecast quantity
    [TOutFirm] INT NOT NULL,               -- Firm transfer-out quantity
    [TOutPlanned] INT NOT NULL,            -- Planned transfer-out quantity
    [ProdFirm] INT NOT NULL,               -- Firm production quantity
    [ProdPlanned] INT NOT NULL,            -- Planned production quantity
    [POsFirm] INT NOT NULL,                -- Firm purchase order quantity
    [POsPlanned] INT NOT NULL,             -- Planned purchase order quantity
    [TInInTransit] INT NOT NULL,           -- In-transit transfer-in quantity
    [TInOnOrder] INT NOT NULL,             -- On-order transfer-in quantity
    [TInPlanned] INT NOT NULL,             -- Planned transfer-in quantity
    [SIQty] INT NOT NULL,                  -- Shippable inventory quantity
    [SSQty] INT NOT NULL,                  -- Safety stock quantity
    [SI-SS] INT NOT NULL,                  -- SI difference to SS target
    [DemandFulfillmentQty] INT NOT NULL,   -- Demand fulfillment quantity projected
    [TotalDemand] INT NOT NULL,            -- Total planned demand (firm + promo + forecast)
    [TotalTO] INT NOT NULL,                -- Total transfer-out (firm + planned)
    [TotalProd] INT NOT NULL,              -- Total production (firm + planned)
    [TotalPOs] INT NOT NULL,               -- Total purchase orders (firm + planned)
    [TotalTI] INT NOT NULL,                -- Total transfer-in (in-transit + on-order + planned)
    [TotalOut] INT NOT NULL,               -- Total outgoing (FirmDemand+Promo+Netforecast+TOs)
    [TotalReceipts] INT NOT NULL,          -- Total planned receipts
    [SINegative] INT NOT NULL,             -- Shippable Inventory Negative
    [SIPositive] INT NOT NULL,             -- Shippable Inventory Positive
    [NetInventoryChange] INT NOT NULL,     -- Net of Receipts minus Shipments
    [SSGap] INT NOT NULL,                  -- Qty needed to get to target (zero if SI>SS)
    [SnapshotDate] DATE NOT NULL           -- Date of snapshot creation
);
```

---

## 3. Semantic Model Layer

- **Model Type** - Star Schema
- **Fact Table** - FactSupplyPlanDetail

---

### Relationships

| From | To | Type | Direction |
| --- | --- | --- | --- |
| `FactSupplyPlanDetail[ItemSKU]` | `DimProduct[ItemSKU]` | Many-to-One | Single |
| `FactSupplyPlanDetail[Warehouse]` | `DimWarehouse[Warehouse]` | Many-to-One | Single |
| `FactSupplyPlanDetail[WeekEnding]` | `DimDate[Transaction Date]` | Many-to-One | Single |

---

## 4. Measures (DAX or TMDL)

### `displayFolder: Current Supply Plan`

#### Beginning OH Qty

```tmdl
	measure 'Beginning OH Qty' =
		VAR MinWeekEnding = MIN(FactSupplyPlanDetail[WeekEnding])
		RETURN
			CALCULATE(
				SUM(FactSupplyPlanDetail[BeginningBalance]),
				FactSupplyPlanDetail[WeekEnding] = MinWeekEnding
			)
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Beginning on hand inventory balance at SnapshotDate"
```

#### Firm Demand Qty

```tmdl
	measure 'Firm Demand Qty' = CALCULATE(SUM(FactSupplyPlanDetail[FirmDemand]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity requested on firm customer orders"
```

#### Promo Lift Qty

```tmdl
	measure 'Promo Lift Qty' = CALCULATE(SUM(FactSupplyPlanDetail[Promo Lift]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Weekly promotional lift quantity"
```

#### Net Fcast Qty

```tmdl
	measure 'Net Fcast Qty' = CALCULATE(SUM(FactSupplyPlanDetail[NetForecast]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Net of quantity forecasted minus the firm customer orders already placed"
```

#### TO Firm Qty

```tmdl
	measure 'TO Firm Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TOutFirm]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity on a firm Transfer Out order"
```

#### TO Planned Qty

```tmdl
	measure 'TO Planned Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TOutPlanned]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: ""Quantity outside lead time planned to be placed on a Transfer Out order"
```

#### Prod Firm Qty

```tmdl
	measure 'Prod Firm Qty' = CALCULATE(SUM(FactSupplyPlanDetail[ProdFirm]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity on a firm production order"
```

#### Prod Planned Qty

```tmdl
	measure 'Prod Planned Qty' = CALCULATE(SUM(FactSupplyPlanDetail[ProdPlanned]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity outside lead time planned to be placed on a production order"
```

#### PO Firm Qty

```tmdl
	measure 'PO Firm Qty' = CALCULATE(SUM(FactSupplyPlanDetail[POsFirm]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity on a firm purchase order"
```

#### PO Planned Qty

```tmdl
	measure 'PO Planned Qty' = CALCULATE(SUM(FactSupplyPlanDetail[POsPlanned]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity outside lead time planned to be placed on a purchase order"
```

#### TI InTransit Qty

```tmdl
	measure 'TI InTransit Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TInInTransit]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity on a transfer order that's currently In-transit to the destination"
```

#### TI On Order Qty

```tmdl
	measure 'TI On Order Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TInOnOrder]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity on a firm transfer in order"
```

#### TI Planned Qty

```tmdl
	measure 'TI Planned Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TInPlanned]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: ""Quantity outside lead time planned to be placed on a transfer-in order"
```

#### SI Qty

```tmdl
	measure 'SI Qty' = CALCULATE(SUM(FactSupplyPlanDetail[SIQty]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity projected to be available at week ending, net of all receipts and outbound shipments"
```

#### SS Qty

```tmdl
	measure 'SS Qty' = CALCULATE(SUM(FactSupplyPlanDetail[SSQty]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Safety stock target quantity"
```

#### SI - SS

```tmdl
	measure 'SI - SS' = CALCULATE(SUM(FactSupplyPlanDetail[SI-SS]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Shippable Inventory difference to Safety Stock target"
```

#### Projected Fulfillment Qty

```tmdl
	measure 'Projected Fulfillment Qty' = CALCULATE(SUM(FactSupplyPlanDetail[DemandFulfillmentQty]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity of demand projected to be able to fulfill"
```

#### Total Demand Qty

```tmdl
	measure 'Total Demand Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalDemand]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total planned demand (firm customer orders + promo + net forecast)"
```

#### Total TO Qty

```tmdl
	measure 'Total TO Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalTO]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total transfer-out (firm + planned)"
```

#### Total Prod Qty

```tmdl
	measure 'Total Prod Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalProd]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total production (firm + planned)"
```

#### Total PO Qty

```tmdl
	measure 'Total PO Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalPOs]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total purchase orders (firm + planned)"
```

#### Total TI Qty

```tmdl
	measure 'Total TI Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalTI]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total transfer-in (in-transit + on-order + planned)"
```

#### Total Outbound Qty

```tmdl
	measure 'Total Outbound Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalOut]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total outbound shipment quantity (FirmDemand+Netforecast+TransfersOut)"
```

#### Total Receipts Qty

```tmdl
	measure 'Total Receipts Qty' = CALCULATE(SUM(FactSupplyPlanDetail[TotalReceipts]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Total receipt quantity (Production+Purchases+TransfersIn)"
```

#### SI Neg Qty

```tmdl
	measure 'SI Neg Qty' = CALCULATE(SUM(FactSupplyPlanDetail[SINegative]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity where Shippable Inventory is negative"
```

#### SI Pos Qty

```tmdl
	measure 'SI Pos Qty' = CALCULATE(SUM(FactSupplyPlanDetail[SIPositive]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Quantity where Shippable Inventory is positive"
```

#### Net Inventory Change Qty

```tmdl
	measure 'Net Inventory Change Qty' = CALCULATE(SUM(FactSupplyPlanDetail[NetInventoryChange]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Net of Receipts and outbound shipments"
```

#### Gap to SS Qty

```tmdl
	measure 'Safety Stock Gap Qty' = CALCULATE(SUM(FactSupplyPlanDetail[SSGap]))
		formatString: #,0
		displayFolder: "Current Supply Plan"
        description: "Qty needed to get to safety stock target (zero if SI>SS)"
```

---

## 5. Change Log

| Date | Change | Author |
| --- | --- | --- |
| `2026-06-16` | Initial draft | `Robert Font Perez` |
