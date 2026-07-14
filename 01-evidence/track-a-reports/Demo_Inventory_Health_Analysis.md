# Demo_Inventory Health — Model Analysis
**Workspace:** Supply Chain Analytics-Premium  
**Semantic Model ID:** `a30d470d-8e45-465d-a85b-82fd9dec4b5d`  
**Report ID:** `911bdb5f-0653-4d12-98d7-6a599df5474f`  
**Analysis Date:** 2026-07-09  
**Model Size:** 32 tables (5 fact + 4 dim + 1 bridge pair + 1 measure table + local date tables); **24 DAX measures** (all in `_Measure`); Compatibility Level 1567  
**BIM File:** [bim/Demo_Inventory_Health.bim](bim/Demo_Inventory_Health.bim)  
**Critical Flag:** 🚨 **ALL data sourced from local Excel files on a specific user's OneDrive** — this is a demo/prototype, not a production model.

---

## 1. Supply-Chain Question & Chain Link

**Core question:**
> What is the overall health of our inventory portfolio — how much is productive (in-stock), excess, or obsolete — expressed as ratios and dollar values?

**This is a demo/prototype model** (named "Demo_Inventory Health"), not a production-ready report. It demonstrates a star-schema dimensional model for inventory health analytics with:
- ABC/XYZ demand classification
- Safety stock parameters (service level, uncertainty, reorder point)
- Inventory excess and obsolescence calculations
- Quality/defect cost tracking
- Demand forecast integration

**Primary chain links served:**

| Link | How served |
|---|---|
| **Inventory** | `FactInventoryPosition` — current on-hand, in-transit, on-order, ATP, safety stock, WOS, status classification |
| **Demand** | `FactActualDemand` — shipped quantities, invoice amounts, gross margin; `FactInventoryTransactions` — movement history with DaysSinceLastMovement |
| **Forecast** | `FactDemandForecast` — resultant forecast, promo lift, forced forecast; snapshot-enabled |
| **Inventory Health** | Excess Ratio, Obsolete Ratio, In-Stock Ratio (portfolio composition) |
| **Quality** | `FactQualityCosts` — defect credits, returns, short shipments |
| **Safety Stock Parameters** | `BridgeSafetyStock` — service level, demand uncertainty, SS calculated vs. adjusted, reorder point, review period |

---

## 2. Decisions Supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| **Assess inventory portfolio health** — what % of inventory is in-stock vs. excess vs. obsolete? | Inventory Manager / Finance | Monthly | **Performance/Governance** — strategic KPI |
| **Monitor WOS distribution** — how many SKUs are < 5 WOS (shortage risk) vs. > 52 WOS (overstock)? | Inventory Planner | Monthly | **Performance/Governance** — portfolio distribution |
| **Review safety stock adequacy** — using service level targets, demand uncertainty, and SS bounds | Inventory Planner | Monthly | **Performance/Governance** — validate SS parameters |
| **Track quality/return costs** — credit qty, return amount, short-ship amount by customer/product | Quality Manager | Monthly | **Performance/Governance** — defect cost tracking |
| **Monitor inventory obsolescence** — items not moved in > 90 days | Finance / Inventory Manager | Monthly | **Operational** — write-off decisions |
| **Toggle between $ and quantity views** via `Parameter` field parameter | Various | Ad hoc | — |

> **Note:** Most KPI measures use hardcoded literal values (see §9) — the decisions above cannot currently be supported by the actual model calculations.

---

## 3. Key Metrics / Measures

All 24 measures reside in `_Measure`.

### Production-quality measures (with real logic)

| Measure | Business meaning | Source / Logic | Flag |
|---|---|---|---|
| `OH Quantity` | Total on-hand inventory quantity | `SUM(FactInventoryPosition[OnHandQty])` | |
| `SS Target` | Total safety stock target | `SUM(FactInventoryPosition[SafetyStockQty])` | |
| `Qty Trend LM` | Month-over-month on-hand quantity trend text | `FORMAT(DIVIDE([OH Qty], [OH Qty LM]))`, returns "Trend Up +X% with LM" / "Trend Down -X%" / "Not Change" | |
| `OH Quantity LM` | On-hand quantity last month | `CALCULATE([OH Qty], DATEADD(DimDate[FiscalMonthFirstDate], -1, MONTH))` | |
| `Obsolete Ratio` | Ratio of items not moved in 90+ days × $25,600 per unit to inventory value | `(SUM(TransactQty) × 25600 where DaysSinceLastMovement>90) / (OH × Inv_$)` | ⚠️ **magic number 25600** — see §9 |
| `Excess Ratio` | Ratio of items not moved in 90+ days × $40,600 per unit to inventory value | `(SUM(TransactQty) × 40600 where DaysSinceLastMovement>90) / (OH × Inv_$)` | ⚠️ **magic number 40600** — see §9 |
| `In-Stock Ratio` | Complement of excess + obsolete = productive inventory share | `1 − [Excess Ratio] − [Obsolete Ratio]` | ⚠️ depends on both ratios above |
| `Inventory Value` | On-hand qty × hardcoded unit price | `[OH Qty] * [Inv_$]` | ⚠️ **`Inv_$ = 120600` literal** — see §9 |
| `Excess Value` | Excess transaction qty × $40,600 | `SUM(TransactionQty) × 40600` | ⚠️ same 40600 magic number |
| `Excess Quantity` | Raw excess transaction qty | `SUM(TransactionQty)` | |
| `Excess Quantity Ratio` | Excess qty as % of OH, scaled by 0.2 | `DIVIDE(Excess Qty, OH Qty) * 0.2` | ⚠️ **magic number 0.2** — see §9 |
| `Qty Conditional Color Format w Target` | Visual KPI label: OH qty as % of safety stock target | `"~ " + FORMAT(OH/SS Target) + " w Target"` | |

### Hardcoded literal measures (demo placeholders)

| Measure | Value | Should be | Flag |
|---|---|---|---|
| `Inv_$` | `120600` | Actual average inventory unit value per item (calculated from DimProduct) | ⚠️ **literal constant** |
| `Turns` | `12` | `DIVIDE([Inventory Value], COGS)` — commented out formula | ⚠️ **literal; formula truncated** |
| `SKU count` | — | `DISTINCTCOUNT(FactInventoryPosition[ItemSKUKey])` | ⚠️ **uses `InTransitQty` column** — wrong column |
| `Excess SKU count` | — | `DISTINCTCOUNT(FactInventoryPosition[ItemSKUKey]) WHERE Status='Excess'` | ⚠️ **uses `FactActualDemand[GrossMargin]`** — wrong table AND wrong column |
| `Current short Items` | `10` | Actual count of items with WOS < threshold | ⚠️ **literal constant** |
| `Revenue Short` | `100000` | Actual dollar value of lost revenue from stockouts | ⚠️ **literal constant** |
| `Current Quantity` | `1000` | Actual current on-hand at item level | ⚠️ **literal constant** |
| `Next Short Item expected in 60 days` | `8` | Projected shortage count from WOS trajectory | ⚠️ **literal constant** |
| `Avg Forecast Demand` | `100` | `AVG(FactInventoryPosition[AvgWeeklyDemand])` | ⚠️ **literal constant** |
| `WOS` | `10` | `CALCULATE(AVERAGE(FactInventoryPosition[WeeksOfSupply]))` | ⚠️ **literal constant** |
| `Short Qty Trend LM` | — | Same logic as `Qty Trend LM` with different text formatting | ⚠️ duplicate concept |

---

## 4. Data Sources & Lineage

| Table | Source | Type | Risk |
|---|---|---|---|
| **ALL tables** | **Local Excel files on user OneDrive:** `C:\Users\HHeidi\OneDrive - Ashley Furniture Industries, Inc\Ashley\Inventory Health\` | **Local Excel via `File.Contents`** | 🚨 **HIGHEST RISK** — completely ungoverned |
| → `Inventory_Health_Sample_Data.xlsx` | BridgeItemABC, BridgeSafetyStock, DimCustomer, DimDate, DimProduct, DimWarehouse, FactActualDemand, FactDemandForecast, FactQualityCosts, FactInventoryTransactions | Local Excel | 🚨 |
| → `FactInventoryPosition_with_Status_StockOutCat.xlsx` | FactInventoryPosition only (different file) | Local Excel | 🚨 |

**Every single table** in this model is loaded from local Excel via `File.Contents("C:\Users\HHeidi\OneDrive\...")`. This means:

1. **Data refresh is entirely dependent on one person** (HHeidi) manually updating these Excel files
2. **No data governance** — anyone with OneDrive access could modify the source files
3. **No audit trail** — Excel changes are not version-controlled or logged
4. **Not portable** — if HHeidi leaves the organization or changes machines, the model breaks
5. **No data source documentation** — where does the data in these Excel files come from? No SQL queries, no ETL pipeline, no dataflow

> **No EDW SQL. No Fabric. No SharePoint. No dataflows.** This is the only model in the workspace with this data architecture.

---

## 5. Grain & Snapshot Strategy

**Primary grain:** Item SKU × Warehouse × Date (surrogate-key based star schema)

**This is the only model in the entire workspace with a proper dimensional star schema:**

| Table | Grain | Key Design |
|---|---|---|
| `FactInventoryPosition` | Item × Warehouse × Date | Surrogate keys (ItemSKUKey, WarehouseKey, DateKey) |
| `FactActualDemand` | Item × Warehouse × Customer × Date | 4-dimensional fact |
| `FactDemandForecast` | Item × Warehouse × FiscalMonth × SnapshotDate | Temporal snapshot enabled |
| `FactInventoryTransactions` | Item × Warehouse × TransactionDate | Transaction grain |
| `FactQualityCosts` | Item × Warehouse × TransactionDate × Customer | Most granular fact |
| `BridgeItemABC` | Item × SnapshotDate | ABC/XYZ classification per snapshot |
| `BridgeSafetyStock` | Item × Warehouse × FiscalPeriod | SS parameters per period |

**DimProduct is SCD Type 2** — has `EffectiveStartDate` and `EffectiveEndDate` columns, enabling historical product dimension tracking.

**Snapshot strategy:** Mixed.
- `FactInventoryPosition[SnapshotDate]` — supports historical inventory position snapshots
- `FactDemandForecast[SnapshotDateKey]` — supports forecast snapshot history
- `BridgeItemABC[SnapshotDateKey]` — ABC classification per snapshot
- `BridgeSafetyStock[SnapshotDate]` and `[FiscalMonthEndDate]` — SS parameters per period
- `FactActualDemand` — transaction history (not snapshot)

---

## 6. Dimensions Used

| Dimension | Table | Keys | Notes |
|---|---|---|---|
| **Product** | `DimProduct` (34 cols) | `ItemSKUKey` (int64) | **SCD Type 2** — `EffectiveStartDate`/`EffectiveEndDate`; includes `LifecycleStage`, `StandardCost`, `CubicFeet`, `UnitWeight`, `ABCCode`, `XYZCode`, `CurrentFlag` |
| **Warehouse** | `DimWarehouse` (11 cols) | `WarehouseKey` (int64) | Adds `WarehouseType`, `ActiveFlag` — richer than conformed `z_WarehouseMaster` |
| **Customer** | `DimCustomer` (19 cols) | `CustomerKey` (int64) | Adds `CreditLimit`, `OutstandingBalance`, `SalesTerritory`, `CustomerServiceRep` — richer than any other customer dimension |
| **Date** | `DimDate` (24 cols) | `DateKey` (int64) | Full fiscal + calendar; `WorkingDayFlag`, `HolidayFlag` |
| **ABC/XYZ** | `BridgeItemABC` (17 cols) | `ItemABCKey`, `ItemSKUKey`, `SnapshotDateKey` | Includes `WarehouseGroup`, `ImportDomestic`, `ForecastPriority` |
| **Safety Stock** | `BridgeSafetyStock` (19 cols) | `SafetyStockKey`, `ItemSKUKey`, `WarehouseKey`, `FiscalPeriodKey` | Includes `ServiceLevel`, `DemandUncertainty`, `SafetyStockCalculated`, `SafetyStockAdjusted`, `ReorderPoint`, `ReviewPeriod`, `EngineType` |
| **Parameter** | `Parameter` (3 cols) | — | Field parameter: "Amount $" ↔ "Quantity" toggle |

**All relationships use integer surrogate keys** — 36 active relationships total. No orphaned dimensions (unlike When to Disco v2). Proper star schema with bridge tables for M:M (ABC, Safety Stock).

**One INACTIVE relationship:** `FactInventoryTransactions[TransactionDateKey] → DimDate[DateKey]` (inactive). Active date relationships exist via `FactInventoryTransactions[WeekEnding]` and `[LastMovementDate]` → LocalDateTables.

---

## 7. Duplication / Consolidation Signals

1. **`Inv_$` (literal constant) is used in multiple measures.** If the actual per-item value differs from 120,600, all dollar-value calculations (`Inventory Value`, `Obsolete Ratio`, `Excess Ratio`) are systematically wrong. The constant should be replaced with `AVERAGE(DimProduct[FOBPrice])` or `[Total Value] / [OH Quantity]`.

2. **`Obsolete Ratio` and `Excess Ratio` share the same underlying logic** (sum transactions where DaysSinceLastMovement > 90) but use **different multipliers** (25600 vs. 40600) and are intended to represent different categories. However, both filter on the same `DaysSinceLastMovement > 90` condition — the two ratios appear to use different cost assumptions for the same pool of slow-moving inventory, or the filter threshold should be different for each.

3. **`Qty Trend LM` and `Short Qty Trend LM`** are near-identical measures with different text formatting (emoji arrows vs. word labels). They compute the same comparison — potential consolidation.

4. **`DimProduct` in this model** has 34 columns including `ABCCode`, `XYZCode`, `StandardCost`, `CubicFeet`, `UnitWeight`, `LifecycleStage` — significantly richer than `z_ProductDetails` in other models (which has 91+ columns but different attributes). The two product dimensions serve different analytical needs but have no shared key or synchronization path.

5. **`BridgeItemABC[ABCCode]` + `BridgeItemABC[ABCLogility]`** — two ABC classifications exist side by side (internal vs. Logility). No documentation explains when to use which.

---

## 8. Open Questions

1. **Is this model a production report or a demo/proof-of-concept?** The name "Demo_Inventory Health", hardcoded literal measures, and local Excel data strongly suggest this is a prototype. Is it being used in production anyway?

2. **Who is "HHeidi" and what happens when this user leaves or changes OneDrive path?** The entire model is tied to one person's local file path. Is there a plan to migrate to EDW/dataflow?

3. **What does `25600` and `40600` represent in the Obsolete/Excess ratio formulas?** Are these per-unit cost assumptions? If so, why are they different for obsolete vs. excess? Neither number is documented.

4. **`SKU count = DISTINCTCOUNT(InTransitQty)` — this is counting distinct in-transit quantities, not distinct items.** Should this be `DISTINCTCOUNT(ItemSKUKey)`? Has anyone used this number for reporting?

5. **`Excess SKU count = DISTINCTCOUNT(FactActualDemand[GrossMargin])` — this counts distinct gross margin values, not distinct items.** This measure appears to be a placeholder with the wrong column selected. Same question.

6. **`Turns = 12` — why is the denominator commented out?** The formula `DIVIDE([Inventory Value], COGS)` is partially written. Was this intentional (showing an annualized constant) or incomplete development?

7. **The `Status` column in `FactInventoryPosition` has values like `"1.Within Target"` and `"Excess"` — who computes this, and where is the logic?** It appears to come from the Excel source file, not from DAX or the dataflow.

8. **`BridgeSafetyStock` has rich parameters (`ServiceLevel`, `DemandUncertainty`, `SafetyStockCalculated`, `SafetyStockAdjusted`, `ReorderPoint`, `EngineType`).** Is this model intended to eventually become a safety stock optimization tool? The parameters are present but no DAX measures reference them.

---

## 9. Business Assumptions / Magic Numbers

| Constant / Logic | Location | What it does | Documented? |
|---|---|---|---|
| **`120600`** in `Inv_$` | DAX measure literal | Average inventory unit value used for ALL dollar calculations | **No** — should be dynamically calculated from data; 120,600 may be outdated or wrong |
| **`12`** in `Turns` | DAX measure literal | Annual inventory turnover rate | **No** — formula `DIVIDE([Inventory Value],...)` is commented out; 12 is a placeholder |
| **`25600`** | `Obsolete Ratio` | Multiplier on `TransactionQty` where `DaysSinceLastMovement > 90` — appears to convert units to dollar value | **No** — if this is a cost assumption, it varies by item; a single constant is incorrect |
| **`40600`** | `Excess Ratio` and `Excess Value` | Same concept as 25600 but different value | **No** — 40600 vs. 25600 implies different cost bases for excess vs. obsolete; undocumented |
| **`0.2`** | `Excess Quantity Ratio` | Scales the ratio: `(Excess Qty / OH Qty) × 0.2` | **No** — if this is a weighting factor, its purpose is not explained |
| **`90`** days threshold | Both ratio measures | `DaysSinceLastMovement > 90` defines slow-moving inventory | **No** — 90-day threshold for obsolescence/excess definition undocumented |
| **`"1.Within Target"`** string | `FactInventoryPosition[Status]` and `Excess or not` calc column | Status value from Excel source; `Excess or not = IF(Status = "1.Within Target", "", "Excess")` | **No** — who populates this status? What are all possible values? |
| **`10`, `100000`, `1000`, `8`, `100`, `10`** | Literal constant measures | `Current short Items`, `Revenue Short`, `Current Quantity`, `Next Short Item expected in 60 days`, `Avg Forecast Demand`, `WOS` | **No** — all clearly demo/placeholder values; none should exist in production |
| `WOS Cat` thresholds: 5/13/25/52 weeks | Calc column in FactInventoryPosition | Buckets Weeks of Supply into 5 ranges | **No** — thresholds may or may not match business classification standards |
| `Local Excel path: "C:\Users\HHeidi\OneDrive..."` | All partition sources | Hard-coded absolute path to user's personal OneDrive | **No** — critically fragile |

---

## 10. Comparability / Consistency

1. **This model's dimensional model uses surrogate integer keys** while every other model in the workspace uses string natural keys (`Item SKU`, `Warehouse`, etc.). If this model were ever to be connected to other models or data sources, the key formats would be incompatible without a mapping layer.

2. **`DimProduct[LifecycleStage]` in this model vs. `z_ProductDetails[Life Cycle Status]` (calculated) in Product Review (NEW)** — both classify items by lifecycle stage, but using completely different logic (one from Excel, one from DAX calculation). Values may not align.

3. **`DimProduct[ABCCode]` vs. `BridgeItemABC[ABCCode]`** — two ABC codes exist in the same model. `DimProduct` has a static ABC; `BridgeItemABC` has a snapshot-dated ABC. They may disagree if ABC classifications change over time.

4. **`FactInventoryPosition[StockOutCat]`** is a source column from the Excel file — its values and logic are not visible in the model. If this categorization differs from other models' stockout logic (e.g., `Week_2_ATP[Stock Event]`), they are not comparable.

5. **Dollar values in this model (`InvoiceAmount`, `TotalQualityCosts`, `ReturnAmount`) vs. dollar values in other models** (`OrdHist[Order Amount]`, `$ Req Order`) — all use different unit price bases. This model may use wholesale invoice prices while others use FOB prices or retail prices. Cross-model dollar comparisons are unreliable.

---

## Key Highlights

**This is a DEMO/PROTOTYPE, not a production report.** The name, data sources, and hardcoded measures all confirm this is a proof-of-concept or reference architecture model.

**🚨 Highest data-risk model in the entire workspace:**
- 100% local Excel data (one person's OneDrive: `C:\Users\HHeidi\...`)
- No data governance, no audit trail, not portable
- If HHeidi leaves, the entire model breaks immediately

**Star schema is the gold standard** — this is the ONLY model with:
- Proper surrogate key joins (integer keys)
- SCD Type 2 product dimension (EffectiveStartDate/EndDate)
- Bridge tables for M:M relationships (ABC, Safety Stock)
- Rich safety stock parameters (ServiceLevel, DemandUncertainty, ReorderPoint, EngineType)
- This architecture would be the target if the other models were ever refactored

**12 out of 24 measures are hardcoded literal values** — `Inv_$=120600`, `Turns=12`, `Current short Items=10`, `Revenue Short=100000`, etc. These are clearly demo placeholders and should never be displayed to business users.

**🐛 Two COUNT measures use wrong columns:**
- `SKU count = DISTINCTCOUNT(InTransitQty)` — counts distinct in-transit quantities, not items
- `Excess SKU count = DISTINCTCOUNT(FactActualDemand[GrossMargin])` — counts distinct gross margins, not items

**Magic numbers 25600 and 40600** are undefined multipliers in the Obsolete/Excess ratio formulas. They appear to be cost assumptions but are undocumented and potentially wrong if inventory values have changed.

**Unused rich data:** `BridgeSafetyStock` contains detailed safety stock parameters (`ServiceLevel`, `DemandUncertainty`, `SafetyStockCalculated`, `SafetyStockAdjusted`, `ReorderPoint`, `EngineType`) that are not referenced by any measure — suggesting planned but unfinished analytics capability.

**Recommendation:** If this model's dimensional architecture is valuable, it should be rebuilt using the same star-schema design but sourced from governed EDW tables (the same SQL tables other models use), not local Excel files.

---

*Analysis based on BIM definition extracted 2026-07-09. BIM saved to [bim/Demo_Inventory_Health.bim](bim/Demo_Inventory_Health.bim). No bundle indexes were modified.*
