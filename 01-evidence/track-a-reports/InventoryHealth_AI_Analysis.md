# InventoryHealth_AI — Structured Report Analysis

| Field | Value |
|---|---|
| **Workspace** | Supply Chain Analytics-Premium |
| **Report Name** | InventoryHealth_AI |
| **Backing Model** | InventoryHealth_AI (`d975771b-c955-43de-9210-e4dc87b9a782`) |
| **Model Size** | 7 tables (5 user + 2 auto-date), 19 measures |
| **Analyzed** | 2026-07-07 |

> **🚨 Critical finding:** All inventory source data is hardcoded inline (#table literals in Power Query). No live EDW, SQL, SharePoint, or dataflow connections exist. The Groq API key is a placeholder — the LLM is never called in the current published state. This is likely a prototype or demo, not a production report.

---

## §1 — Supply-chain question & chain link

**Question:** What is the current weekly state of inventory health — service availability, stock risk, excess/obsolete positions, warehouse capacity — and what does an AI-generated narrative say a leadership team should focus on?

| Link | How served |
|---|---|
| **Inventory** (primary) | KPIs: Turns, WoS, Excess, Obsolete, Damaged, Expired, Warehouse Utilization, Weeks To Full, Overstock Capacity, In Control Rate |
| Demand / Service | ATP In-Stock Rate, Shippable Invoice Rate, Revenue At Risk |
| AI Narrative | Groq LLM (`llama-3.3-70b-versatile`) generates 4 executive narrative cards from the latest two weeks of snapshot data — **disabled in current state, returns static fallback text** |

---

## §2 — Decisions supported

| Decision | Persona | Cadence | Type |
|---|---|---|---|
| Are inventory KPIs on-track this week? (ATP, WoS, Turns) | Manager / WBR-Leadership | Weekly | Performance / Governance |
| Where is revenue at risk from low service availability? Prioritise replenishment | Planner / Analyst | Weekly | Operational |
| Which DCs have overstock or approaching capacity? Trigger transfers or liquidation | DC Manager / Planner | Weekly | Operational |
| Is excess/obsolete/damaged stock growing? Decide write-off or liquidation actions | Finance / Manager | Weekly | Operational |
| What does the AI narrative say to open the WBR with? | Executive | Weekly | Performance / Governance |

---

## §3 — Key metrics / measures

**19 measures total.** All are `MAX([column])` over a static 10-row table — they return a single point value for the latest selected week.

### A. KPI snapshot measures (Table: InventorySnapshot)

| Measure | Meaning | Grain | Logic |
|---|---|---|---|
| Current Total Inventory Commitment | Total $ inventory on-hand ($M) | Weekly | `MAX([Total Inventory Commitment])` |
| Total Inventory Commitment WoW | % change vs prior week | Week-over-week | `DIVIDE(cur - prev, prev)` via `TOPN(1, FILTER(ALL, date < curDate))` |
| Current ATP In-Stock Rate | % SKU-DCs with stock available to promise | Weekly | `MAX([ATP In-Stock Rate])` |
| ATP In-Stock Rate WoW pp | Change in ATP rate (percentage points) | Week-over-week | `(cur - prev) × 100` |
| Current Shippable Invoice Rate | % of demand that can physically ship | Weekly | `MAX([Shippable Invoice Rate])` |
| Current Revenue At Risk | $ demand exposed by stockout risk ($M) | Weekly | `MAX([Revenue At Risk])` |
| Current Inventory Turns | Annualised turn rate | Weekly | `MAX([Inventory Turns])` |
| Current Weeks Of Supply | Forward coverage in weeks | Weekly | `MAX([Weeks Of Supply])` |
| Current Safety Stock Multiple | Safety stock buffer vs. target | Weekly | `MAX([Safety Stock Multiple])` |
| In Control Rate | % inventory positions in statistical process control | Weekly | `MAX([In Control])` |
| Revenue Risk Story Payload | Formatted KPI string for narrative context | — | Concatenated string measure |

### B. Risk story measures (Table: KPI Measures — hidden)

| Measure | Logic |
|---|---|
| Risk Story - Excess Inventory | `MAX([Excess Inventory])` |
| Risk Story - Obsolete Stock | `MAX([Obsolete Stock])` |
| Risk Story - Damaged Stock | `MAX([Damaged Stock])` |
| Risk Story - Expired Inventory | `MAX([Expired Inventory])` |
| Risk Story - Warehouse Utilization | `MAX([Warehouse Utilization])` |
| Risk Story - Weeks To Full | `MAX([Weeks To Full])` |
| Risk Story - Overstock Capacity | `MAX([Overstock Capacity])` |
| Risk Story - Picking Efficiency Risk | `MAX([Picking Efficiency Risk])` |
| **Bottom Line** | **Hardcoded string:** `"Service pressure in low WOS. Capital trapped in high WOS. Inventory not converting to service."` — never changes |
| Updated At GMT +7 | `"Updated at GMT +7" & UNICHAR(10) & FORMAT(UTCNOW() + TIME(7,0,0), "m/d/yyyy h:mm AM/PM")` |

> ⚠️ **`Bottom Line` is a hardcoded string literal.** Always reads the same sentence regardless of current data values. If shown as an executive insight card, it will display this text even when inventory is healthy.

> ⚠️ **`Updated At GMT +7` uses `UTCNOW()` (report-open time, not refresh time).** A user opening a stale report will see today's timestamp against data that may be months old.

> ⚠️ **WoW measures are fragile at the first row.** For the earliest date in the table, `FILTER(ALL, date < curDate)` returns empty → `prev = BLANK()` → WoW shows `BLANK()` silently, no warning.

---

## §4 — Data sources & lineage

| Source | Type | Flag |
|---|---|---|
| `InventorySnapshot` | **Inline `#table()` hardcoded in M** — 10 rows, 2025-02-28 to 2025-05-02 | 🚨 No live connection |
| `WarehouseInventoryClassification` | **Inline `#table()` hardcoded in M** — 6 DC rows | 🚨 No live connection |
| `WeeklyClassificationMix` | **Inline `#table()` hardcoded in M** — 12 week rows | 🚨 No live connection |
| `AIInsights` (live path) | **Groq API** `https://api.groq.com/openai/v1/chat/completions`, model `llama-3.3-70b-versatile` | ⚠️ External cloud LLM call at refresh — **disabled, key is placeholder** |
| `AIInsights` (fallback path) | **Inline `#table()` hardcoded in M** — 4 static narrative rows | 🚨 Always active in current state |

**No EDW, no SQL, no SharePoint, no dataflow connections exist in this model.**

The API key (`GroqApiKey`) = `"PUT_GROQ_API_KEY_HERE"`. The M code guard: `if GroqApiKey = "PUT_GROQ_API_KEY_HERE" or Text.Length(GroqApiKey) < 20 then Fallback`. In current published state, the LLM is never called.

**AIInsights M query pattern (when key is valid):**
```m
Payload = Json.FromValue([
    current_week = Date.ToText(Current[Week Ending], "yyyy-MM-dd"),
    total_inventory_m = Current[Total Inventory Commitment],
    total_inventory_wow = Current[Total Inventory Commitment] - Prior[Total Inventory Commitment],
    atp_rate = Current[ATP In-Stock Rate],
    ...
]),
Prompt = "You are generating concise executive Power BI inventory health insights. Return strict JSON array with four objects: {section,text,sort}. Sections must be WHAT WE NOTICED, WHERE THE RISK IS, WHAT THIS MEANS, FOCUS FOR NEXT STEPS. ...",
Body = Json.FromValue([model = GroqModel, messages = {...}, temperature = 0.2])
```

---

## §5 — Grain & snapshot strategy

**Primary grain:** Weekly (one row = one `Week Ending` date)
**Data range:** 2025-02-28 → 2025-05-02 (10 weeks, hardcoded inline — frozen)
**Snapshot strategy:** Not applicable — no live snapshots. Data is fixed at model publish time.

`AIInsights` takes the last 2 rows of `InventorySnapshot` (sorted ascending) to compute WoW deltas for the LLM prompt. Since the data never refreshes, "last 2 rows" always refers to the same two hardcoded rows (2025-04-25 and 2025-05-02).

---

## §6 — Dimensions used

| Dimension | Source | Notes |
|---|---|---|
| Date / Week | `InventorySnapshot[Week Ending]` + auto-generated `LocalDateTable` | Calendar-year auto date table only; no fiscal calendar |
| DC Warehouse | `WarehouseInventoryClassification[DC Warehouse]` — 6 rows (SAILLO, ADVANCE NC, LEESPORT PA, REDLANDS, MESQUITE, ARCADIA) | **Not related to `InventorySnapshot`** — no join, standalone visual only |
| Week label | `WeeklyClassificationMix[Week]` text "W1"–"W12" | **Not related to `InventorySnapshot` or any date** — no join, no mapping to actual dates |

**No conformed dimensions exist in this model** — no Product, no Vendor, no Customer, no Warehouse dimension with attributes, no fiscal calendar. The only relationship is `InventorySnapshot[Week Ending]` → auto-generated `LocalDateTable`.

---

## §7 — Duplication / consolidation signals

| Signal | Detail |
|---|---|
| `WarehouseInventoryClassification` has no relationship to `InventorySnapshot` | DC-level classification percentages cannot cross-filter with weekly KPIs. Isolated table — standalone bar chart only |
| `WeeklyClassificationMix` has no relationship to any date | "W1"–"W12" text labels have no mapping to actual `Week Ending` dates. "W1" ≠ first week in `InventorySnapshot` |
| `AIInsights` fallback duplicates `InventorySnapshot` last row | Hardcoded fallback text (`$482.6M`, `-5.3 pp`, `$18.4M`) exactly echoes the values from the last row of the inline data. Two independent copies of the same numbers |
| `Revenue Risk Story Payload` (DAX) and `AIInsights` (M) both assemble the same KPI values | Two separate representations of the same KPI summary — one in DAX string, one in M JSON payload |
| `KPI Measures` table is a hidden dummy-row container | `#table(type table [Dummy = Int64.Type], {{1}})` — valid pattern, but hidden table makes measures hard to discover for new developers |
| `Bottom Line` is a static string measure | Could be dynamic DAX based on thresholds; currently a hardcoded assertion |

---

## §8 — Open questions

1. **Prototype or production?** All data is hardcoded (10 weeks, 6 DCs). `PBI_ProTooling = ["DevMode"]` and placeholder API key both signal this was never deployed against live data.
2. **Is the Groq API key configured anywhere?** Published model has `"PUT_GROQ_API_KEY_HERE"`. The AI narrative is entirely disabled in current state.
3. **Where is the real inventory health data?** The workspace has `Demo_Inventory Health` and `InventoryHealth_CurrentDashboard`. Is `InventoryHealth_AI` meant to be an AI layer on top of a production model?
4. **Are the 10 hardcoded rows real historical data or synthetic demo data?** Values look plausible but are unverified. If real, the report is frozen at 2025-05-02 (>2 months stale as of analysis date).
5. **What is `Process Value Add` and `In Control`?** Supply-chain SPC terms not common in standard inventory reports. No business definition in the model.
6. **What should trigger a WBR alert?** No threshold logic, no conditional formatting rules, no alert definitions exist. The AI narrative is the only "signal" — and it's static text.

---

## §9 — Business assumptions / magic numbers

### 9.1 — All KPI values are hardcoded constants

Every number in this report — inventory commitment, ATP rate, revenue at risk, turns, WoS, excess percentages — is a literal value in an `#table()` constructor. No formula, no derivation, no source query.

Example (last data row, 2025-05-02):
```m
{#date(2025,5,2), 482.6, 0.918, 0.668, 18.4, 5.9, 7.8, 5.3, 0.186, 0.053, 0.012, 0.024, 0.784, 6.8, 0.852, 0.124, 0.668, 0.017}
```

No documentation of origin. Could be real data extracted manually from EDW; could be synthetic demo data.

### 9.2 — LLM temperature = 0.2 (hardcoded)

`temperature = 0.2` in the Groq call body. Deliberate choice for deterministic output. Not documented. If temperature is changed, the structured JSON response format may break — there is no retry or validation logic.

### 9.3 — LLM response parsing has no error handling

```m
Rows = Json.Document(Content),
T = Table.FromRecords(Rows),
Renamed = Table.RenameColumns(T, {{"section","Insight Section"},{"text","Insight Text"},{"sort","Sort Order"}}, MissingField.Ignore)
```

If the LLM returns markdown-wrapped JSON, extra text, or unexpected field names, the entire `AIInsights` table errors and the report page goes blank. No `try...otherwise` wrapper. `MissingField.Ignore` only protects column renaming, not JSON parse failures.

### 9.4 — `Updated At GMT +7` reports open-time, not refresh-time

`UTCNOW()` in DAX evaluates at query time (visual render), not at dataset refresh time. A user opening a stale report sees today's time against data that is months old — falsely implying freshness.

### 9.5 — `Bottom Line` is a hardcoded executive statement

```dax
"Service pressure in low WOS. Capital trapped in high WOS. Inventory not converting to service."
```

Always displayed, never computed. If this appears on an executive WBR card it will show this sentence even when all KPIs are green.

### 9.6 — `Current Revenue At Risk` = hardcoded number with no derivation formula

The report shows `$18.4M` revenue at risk (week ending 2025-05-02). This is a literal value typed into the `#table()` constructor — not calculated from demand × stockout probability × margin or any other formula. Its derivation is entirely unknown. If used in executive reporting, it is an assertion, not an analysis.

### 9.7 — Does this report calculate dollar-value business impact?

Yes — `Current Revenue At Risk` ($M) is the financial exposure metric. But it is **not calculated** — it is a hardcoded constant. There is no formula linking it to demand, service levels, margin, or any other modeled quantity. Every assumption behind the number is invisible.

---

## §10 — Comparability / consistency

### 10.1 — `WeeklyClassificationMix` weeks not aligned to `InventorySnapshot` dates

`WeeklyClassificationMix` uses text labels "W1"–"W12". `InventorySnapshot` uses actual dates. No relationship or mapping between them. Any visual showing both implies a time alignment that does not exist in the model.

### 10.2 — `WarehouseInventoryClassification` is temporally disconnected

6 DC rows have no `Week Ending` column and no relationship to `InventorySnapshot`. DC classification percentages (Sweet Spot, Excess, etc.) are for an unknown point in time — cannot be compared to weekly KPI trends except by assumption.

### 10.3 — WoW delta logic is silently broken at the first row

For the first date (2025-02-28), `FILTER(ALL(InventorySnapshot), date < curDate)` returns an empty table. `TOPN(1, empty)` = empty. `prev = BLANK()`. Both `Total Inventory Commitment WoW` and `ATP In-Stock Rate WoW pp` show `BLANK()` with no label or warning. Users see nothing and don't know why.

### 10.4 — AI narrative and static KPI card can diverge after a data update

The hardcoded fallback narrative contains literal values (`$482.6M`, `-5.3 pp`, `$18.4M`) that exactly match the last row of `InventorySnapshot`. If a developer updates the `#table` data but forgets to update the fallback narrative strings, two visuals on the same page will show different numbers for the same metric.

### 10.5 — `AIInsights` prompt assumes 4-section fixed structure

The system prompt demands: `"Sections must be WHAT WE NOTICED, WHERE THE RISK IS, WHAT THIS MEANS, FOCUS FOR NEXT STEPS"`. If the LLM omits a section or adds one, the `Table.FromRecords(Rows)` step produces a table with wrong row count. Report visuals expecting exactly 4 rows will render incorrectly. No structural validation exists.

---

## Closing — Interview seeds

**1. On production vs. prototype:**
> "The data in this report is hardcoded — 10 weeks ending May 2, 2025. Is this a demo you built to show what the AI narrative concept looks like, or is it actually connected to live inventory data somewhere that I'm not seeing?"

**2. On the AI narrative capability:**
> "The Groq API key in the model is still the placeholder `PUT_GROQ_API_KEY_HERE`, so the AI narrative never actually runs — it always shows static text. Has the live LLM version ever worked in production, and if so, where does the real API key live?"

**3. On Revenue At Risk:**
> "The report shows $18.4M revenue at risk. Where does that number come from — is it pulled from a system, calculated from stockout exposure, or was it typed in manually for the demo?"

**4. On the gap to a production version:**
> "There are two other Inventory Health reports in this workspace — `Demo_Inventory Health` and `InventoryHealth_CurrentDashboard`. What's the relationship between those and this one — is the plan to eventually replace one of them with a live version of this AI report?"
