# Raw Semantic Model Exports (.bim)

Raw Power BI semantic-model definitions (Tabular Model BIM/JSON) exported from the
Supply Chain Analytics-Premium workspace. These are the **verification layer** for
the analyses in the parent directory: every claim in an `*_Analysis.md` file about
a measure, column, relationship, or source query can be independently checked
against the corresponding `.bim` here.

Conventions:
- Files are UTF-8 with BOM — parse with `encoding='utf-8-sig'` in Python.
- `*_extracted.txt` files are plain-text extractions kept alongside particularly
  large models for convenience.
- `GF_FC_Tool_clean.bim` is a cleaned re-export of `GF_FC_Tool.bim`.
- Not every analyzed model has a `.bim` yet (earlier analyses predate this
  practice). Findings verified against a `.bim` are marked ✅ in
  `../_catalog/Bug_Findings_Log.md`; unverified ones are marked 🔶.

| BIM file | Analysis document |
|---|---|
| demand_review_model.bim | Demand_Review_Analysis.md |
| fcst_accy_cust_itwh_model.bim | Forecast_Accuracy_CustItWh_Analysis.md |
| fcst_accy_itwh_model.bim | Forecast_Accuracy_ItWh_Analysis.md |
| inv_txn_balance_model.bim | Inventory_Transactions_ItemBalance_Analysis.md |
| on_time_pct_model.bim | On_Time_Pct_By_Customer_Analysis.md |
| safety_stock_model.bim | Safety_Stock_Analysis.md |
| weekly_trend_model.bim | Weekly_Trend_Analysis.md |
| Product_Review.bim (+ _extracted.txt) | Product_Review_Analysis.md |
| Complete_Series_In_Stock.bim | Complete_Series_In_Stock_Analysis.md |
| Consumption_Report.bim | Consumption_Report_Analysis.md |
| Demand_Fulfillment.bim | Demand_Fulfillment_Analysis.md |
| Demand_Sensing_Report.bim | Demand_Sensing_Report_Analysis.md |
| Demo_Inventory_Health.bim | Demo_Inventory_Health_Analysis.md |
| FCA_Services_Fee_Audit.bim | FCA_Services_Fee_Audit_Analysis.md |
| Forecast_Change_WoW.bim | Forecast_Change_WoW_Analysis.md |
| GF_FC_Tool.bim / GF_FC_Tool_clean.bim | GF_FC_Tool_Analysis.md |
| Planner_Assignment.bim (+ _extracted.txt) | Planner_Assignment_Analysis.md |
| Usage Metrics Report.bim | Usage_Metrics_Report_Analysis.md |
