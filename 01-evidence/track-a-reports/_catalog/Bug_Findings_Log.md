# Bug Findings Log

| Field | Value |
|---|---|
| **Purpose** | Verified, reportable defects found during Track A analysis. Dual use: (1) direct input for the BI/report-owning team, (2) **trust-building openers for Track B** — approaching a report owner with "we found this defect in your report, is it affecting you?" positions Discovery as bringing value, not extracting knowledge, and their answer naturally reveals how the report is actually used. |
| **Verification levels** | ✅ **Verified** = independently confirmed against the raw `.bim` semantic model. 🔶 **Reported** = documented in a Prompt #1 analysis from live model inspection, not yet re-verified against raw BIM. |
| **Severity** | 🔴 produces wrong numbers users likely rely on · 🟠 produces blank/dead output or silently missing data · 🟡 hygiene/consistency defect |
| **As of** | 2026-07-08 |

> Handling note: this log names reports and defects, never people. Consistent with
> registry principle of attaching findings to artifacts, not individuals.

---

## Open defects

| ID | Sev | Model | Defect | Impact | Level |
|---|---|---|---|---|---|
| BUG-001 | 🔴 | Forecast Accuracy **CustItWh** + **ItWh** (both) | Cycle-deviation trigger date written as `'01/25/2025'`; intent (per SQL comment) is the Feb **2026** cycle | The Feb-2026 cycle deviation override silently never fires in either model; affected periods fall through to the day+15 default and may use the wrong forecast snapshot | ✅ Verified in both .bim |
| BUG-002 | 🔴 | Demand Review | Customer-group filter misspelled `RHCHUST` (should be `RHCUST`) in `fcst_change_qty_r12_wrk_v_prior_all` | Filter matches nothing; RH Bedding drop-ship change is silently excluded from the R12 working-vs-prior change measure | ✅ Verified in .bim (typo present alongside 11 correctly-spelled uses) |
| BUG-003 | 🟠 | Weekly Trend Analysis | `ACTD (accy)`, `90Day Error`, `90Day Error %` reference column `Actual Qty` which does not exist in `FcstAccuracy` (source SQL selects no actuals) | All three always return BLANK or −1; any visual bound to them shows meaningless accuracy figures | ✅ Verified in .bim (table has no actuals column) |
| BUG-004 | 🟠 | Forecast Accuracy CustItWh | All `(B)` baseline-benchmark measures reference nonexistent column `(B)Error`; `wMAPE Value Add_CIW` / `Error Value Add_CIW` therefore equal the raw measure | "Value add vs baseline" story the measures were built to tell is structurally impossible; benchmark concept absent from model entirely | 🔶 Reported |
| BUG-005 | 🟠 | Safety Stock Analysis | `DP SS Qty Suggested`, `DP SS Qty Constrained`, `DP WOS`, `DP SS DOS` reference table `DPIO` which does not exist in the model | Four dead measures; any DP-IO comparison page is non-functional | 🔶 Reported |
| BUG-006 | 🟠 | Demand Review | `RH_DropShip_Sales_2024` source file and query hard-filtered to calendar 2024 | All RH drop-ship actuals from 2025-01-01 onward silently absent from `orders_qty_cur_req_date_all` | 🔶 Reported |
| BUG-007 | 🔴 | Demand Review | Hardcoded one-off patch `date(2026,02,16)` inside `fcst_qty_prior_logility` (Bedding RHCUST February correction) | Permanently distorts prior-plan comparisons for the Feb-2026 cycle; wrong for every other cycle if logic is ever reused | ✅ Verified in .bim |
| BUG-008 | 🟡 | Inv Management | `Measure 2` has a completely empty expression | Dead object; noise in the measure list | 🔶 Reported |
| BUG-009 | 🟡 | Inv Management | `MOS Case 11` is an exact DAX duplicate of `MOS Case 1`; `sELECTEDVALUE` casing artifact in `New True Excess` | Duplicate maintenance surface; divergence risk on future edits | 🔶 Reported |
| BUG-010 | 🔴 | Inv Management | `MOS Case 1/111` use `AVERAGEX` over per-item ratios rather than volume-weighted totals | Headline months-of-supply is systematically distorted by low-volume/high-excess items (worked example in analysis: 5.06 shown vs 1.1 true) | 🔶 Reported |
| BUG-011 | 🟠 | AFT_SI-SS_PSW | `SS% Test` is an exact duplicate of `SS% DUE`; two contradictory hardcoded UTC offsets (−3 vs −5) in one table | Dead test measure in production; timestamp semantics ambiguous | 🔶 Reported |
| BUG-012 | 🔴 | AFT_SI-SS_PSW | `Due Color` shows RED when SS% is *above* threshold — inverted-looking convention | If unintentional, users are color-guided to the wrong rows; needs owner confirmation before classification as bug vs convention | 🔶 Reported — **confirm intent first** |
| BUG-013 | 🔴 | Act+Fcst by WNK & MILL | `Prod Capacity = MAX(Firm+Planned, TotalAvailHours)` — capacity can never show below planned load | Structural masking of capacity shortfalls; `FcstAverageWeekly` also divides a 16-week window by 17 | 🔶 Reported |
| BUG-014 | 🟠 | Inventory Transactions & Item Balance | `InventoryDollars` calculated column broken; `Issuing Transfer` sums negative-signed qty into a measure combined with mixed sign conventions in `Net Inv Change` | Net-movement math unreliable without sign audit | 🔶 Reported |
| BUG-015 | 🟡 | On Time % by Customer | `On Time % - Promised` divides promised-basis numerator by the requested-basis total denominator; 16-account DSG SWITCH copy-pasted into two tables; WH335 table uses a different lookback (9 months) than main tables (55 weeks) | Promised OT% subtly mis-based; DSG list dual-maintenance; internal incomparability | 🔶 Reported |
| BUG-016 | 🟡 | Safety Stock Analysis | `DropIn12Mo` computes `(PlanDropDecisionDate − Market Begin Date) ≤ 365` — total lifecycle length, not "drops within 12 months of today" | Lifecycle flag answers a different question than its name implies | 🔶 Reported |
| BUG-017 | 🟠 | Demand Review | `LM Abs It Err %` mixes numerator from `Fcst_Accuracy_Cust_It_Wh` with denominator from `ItWHAccy` (different grain/table) | Ratio combines mismatched populations; fragile to either table changing | 🔶 Reported |
| BUG-018 | 🔴 | Product Review + Product Review (NEW) | Two reports with the same name compute `DF rate` with different formulas: old `(FD + SI_neg)/FD` vs NEW `(FD + NF + SI_neg)/(FD + NF)` | Anyone comparing "the Product Review DF rate" across the two sees different numbers for the same item with no visible reason; also a PAT-03 instance | 🔶 Reported (2026-07-09) |

## Confirmed-intent / resolved

| ID | Model | Item | Resolution |
|---|---|---|---|
| — | Inv Management | Warehouse `335` hardcoding originally logged as ambiguous | **Update 2026-07-07:** concluded 335 is Ashley's main DC. **Correction 2026-07-10:** that was overreach — governed `DimWarehouse` confirms 335 (Ashton) is a distinct warehouse grouped apart from the core AFI warehouses, but not confirmed as network-wide primary. Provisionally resolved pending Robert's confirmation, see `07-fabric-build/WAREHOUSE_335_RECONCILIATION.md`. Cross-report include/exclude inconsistency remains open (see `Systemic_Patterns_Registry.md` PAT-08). |

---

## Using this log in Track B (the "gift" protocol)

1. **Match bug → report owner.** Open the conversation with the defect, not with
   questions about their workflow.
2. **Ask impact, not process:** "does this affect anything you use?" Their answer
   reveals which pages/measures they actually rely on — the workflow information
   arrives as a side effect, without an extraction-framed interview.
3. **Log the confirmation** back into this file (move to a "confirmed with owner"
   state) and into the relevant DEC entry's D-group fields.
4. **Escalate 🔴 items** (esp. BUG-001, BUG-007, BUG-010, BUG-013) to the BI team
   regardless of interview progress — they affect numbers likely in active use.
