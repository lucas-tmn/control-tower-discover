# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

OKF Supply Chain Knowledge Bundle is a living markdown-based knowledge base documenting datasets, metrics, business definitions, decision playbooks, and business processes for supply chain reasoning agents. It uses Open Knowledge Format conventions to maintain a structured, cross-linked collection of supply chain concepts.

All bundle content lives under `bundle/`. The knowledge base is organized into six logical domains (`type`) accessible via index files:

- **Playbooks** (`bundle/playbooks/index.md`) — Decision playbooks and step-by-step reasoning workflows. Start here for action-oriented analysis.
- **Processes** (`bundle/processes/index.md`) — Recurring business processes, meetings, and orchestration workflows. Start here to understand when major decisions happen.
- **Datasets** (`bundle/datasets/index.md`) — Data asset references with warehouse table details, grain, source system, and key fields.
- **Metrics** (`bundle/metrics/index.md`) — KPI definitions with business meaning and calculation logic.
- **Entities** (`bundle/entities/index.md`) — Canonical business object definitions (products, suppliers, warehouses).
- **Glossary** (`bundle/glossary/index.md`) — Organization-specific term definitions that differ from standard usage.

Current MVP focus is the Demand/Supply Planning vertical: forecasting, inventory, and new product assessment.

## Common Workflows

### Validation, Indexes, and Rebuilds

This repo is used for many small documentation sessions, often with several
content additions in sequence. Do not automatically run validation, index
regeneration, viewer rebuilds, or pytest after routine content edits.

After content edits, ask the user whether they want to run checks now or defer
them for a batch run after the day's content is complete. Treat these as
user-choice steps:

- frontmatter or markdown validation
- `python tools/build_index.py --dry-run`
- `python tools/build_index.py`
- `python tools/build_viewer.py`
- `python -m pytest ...`

It is fine to inspect the changed markdown, compare nearby files, or search for
obvious stale names while editing. Do not hand-edit any `index.md` file under
`bundle/`. Use only `python tools/build_index.py` to update bundle indexes; use
`python tools/build_index.py --include-root` only when the root
`bundle/index.md` should also be regenerated. Do not rewrite `bundle/viz.html`
unless the user asks to run the builder steps for that batch. If validation or
rebuilds are deferred, say which generated artifacts may be temporarily stale.

### Adding a New Concept

All concept files require YAML frontmatter and a changelog entry. Directory
indexes and the viewer should be refreshed when the user is ready to run the
builder steps, but content-only additions may intentionally leave generated
artifacts stale during a batch editing session.

1. Create the file in the appropriate subdirectory (e.g., `bundle/entities/new_concept.md`)
2. Include all frontmatter fields — `type` is required; include all others:
   - `type` (Dataset, Metric, Entity, Process, Glossary Term)
   - `title`, `description` (one sentence), `tags` (YAML array: `[tag1, tag2, tag3]`)
   - `timestamp` (ISO 8601 format)
   - `resource` (warehouse reference `[db].[schema].table` for datasets, system path for others, or omit if not applicable)
   - `status` (`agent draft`, `active`, or `deprecated`)
   - For datasets only: `source_system`, `refresh_cadence`, `data_source`
3. Add cross-links to and from related documents using markdown reference syntax `[title](/path/to/file.md)` — paths are bundle-relative (begin with `/`, interpreted relative to `bundle/`)
4. Append an entry to `bundle/log.md` under today's date describing what was added and why
5. Ask whether to run or defer validation and builder steps. If the user defers, do not edit generated indexes or `bundle/viz.html` in that pass.

### Updating an Existing Concept

1. Update the `timestamp` field in frontmatter
2. Update any cross-links if titles or file paths changed
3. Append an entry to `bundle/log.md` describing what changed and why
4. Ask whether to run or defer validation and builder steps when the change affects generated indexes, the viewer, or link graph output.

### Refreshing a Dataset Schema Section

When warehouse schema changes occur:

1. Compare the current warehouse schema against the `## Schema` section in the dataset file
2. Update added, removed, or renamed columns in the table
3. Update `timestamp` in frontmatter
4. Append a changelog entry to `bundle/log.md` describing the refresh

### Deprecating Content

1. Set `status: deprecated` in frontmatter
2. Add an explanatory note at the top of the document body explaining what replaced it and why
3. Append an entry to `bundle/log.md`

### Flagging Broken or Missing Links

Do not silently remove broken links. Instead:

1. Append an entry to `bundle/log.md` noting the source file and broken target
2. The target may need to be created — flag this as context for future work

## Frontmatter Field Reference

Every concept document has YAML frontmatter. Interpret these fields:

| Field | Meaning | Required? |
| --- | --- | --- |
| `type` | Kind of concept: Dataset, Metric, Entity, Playbook, Process, Glossary Term | Always |
| `title` | Display name | Always |
| `description` | One-sentence summary | Always |
| `tags` | Cross-cutting categories as YAML array: `[tag1, tag2, tag3]` | Always |
| `timestamp` | Last modified (ISO 8601 format) | Always |
| `resource` | Warehouse table `[db].[schema].table` or system path | Datasets only |
| `source_system` | Upstream origin: Logility, HighJump, ERP, Manual | Datasets only |
| `refresh_cadence` | How often data updates: real-time, daily, weekly | Datasets only |
| `data_source` | Where to query: `azure-sql`, `fabric`, or `both` | Datasets only |
| `status` | `agent draft` (needs review) · `active` (reliable) · `deprecated` (do not use) | Always |

## Data Source Migration

The warehouse is migrating from Azure SQL Server to Microsoft Fabric. During this transition:

- `data_source: azure-sql` — query Azure SQL only
- `data_source: fabric` — query Fabric only
- `data_source: both` — prefer Fabric; fall back to Azure SQL if needed

When a document does not specify `data_source`, note the ambiguity in a `log.md` entry rather than assuming.

## Content Conventions

### [FILL IN: ] Placeholders

Documents contain `[FILL IN: ...]` placeholders for organization-specific values that must be completed before marking `status: active`:

- Table names (e.g., `[FILL IN: forecast run cadence]`)
- Threshold values (e.g., `[FILL IN: min consecutive periods for revision]`)
- Time windows and parameters (e.g., `[FILL IN: recently introduced product window]`)

Search for these across all files when onboarding domain expertise. Mark them complete by replacing with actual values and updating `timestamp` and `log.md`.

### Cross-Links

Links between files represent meaningful relationships. Follow them during analysis:

- `[title](/path/to/file.md)` — bundle-relative path; `/` is interpreted relative to `bundle/`, not the repo root
- Always include "Related" sections at the end of process and metric files listing all referenced concepts

### Reasoning Guidelines for Agents

When this bundle is used to analyze supply chain scenarios:

1. **Playbooks** (`bundle/playbooks/`) — Use when you need step-by-step guidance for a specific analysis or decision. Playbooks define the reasoning path, data sources to consult, and decision rules. Examples: assessing new product performance, recommending forecast revisions.
2. **Processes** (`bundle/processes/`) — Use to understand recurring business workflows, meetings, and decision gates. Processes describe *when* decisions happen, *who* participates, and *how* decisions are made. Examples: demand consensus meetings, product lifecycle reviews.
3. Pull **dataset context** from `bundle/datasets/` before drawing conclusions
4. Apply **metric definitions** from `bundle/metrics/` exactly as documented — do not invent alternative calculations
5. Use **glossary definitions** when a term has org-specific meaning that differs from general usage
6. State data source and time window when making any data-backed claim
7. Flag uncertainty when a threshold, rule, or definition is not documented — note that the knowledge base may need to be extended

## File Structure Notes

```text
bundle/          ← all OKF content lives here (bundle root)
  index.md       ← root bundle index
  log.md         ← changelog; newest entries first
  datasets/
  entities/
  glossary/
  metrics/
  playbooks/
  processes/
tools/           ← Python utility scripts (not part of the bundle)
CLAUDE.md        ← project instructions (not part of the bundle)
```

- **bundle/log.md** — Changelog of all additions, updates, and deprecations. Always append when making changes.
- **index.md files** — Bundle indexes linking to concepts. Do not hand-edit
  these files during content work. Update them only by running
  `python tools/build_index.py`; add `--include-root` only when
  `bundle/index.md` should be regenerated too. The helper preserves existing
  directory index frontmatter and regenerates index bodies from concept
  frontmatter.
- Individual concept files — Named clearly to match their title. Subdirectories keep related concepts grouped by domain.

## File Naming Conventions

Dataset files under the tables subdirectory use **PascalCase** to match warehouse table naming standards. All other concept files use **lowercase with underscores** following standard OKF conventions.

- Dataset files: `bundle/datasets/tables/DimCustomer.md`, `bundle/datasets/tables/FactActuals.md`
- Playbook files: `bundle/playbooks/new_product_review.md`, `bundle/playbooks/forecast_revision.md`
- Process files: `bundle/processes/lifecycle_planning.md`, `bundle/processes/demand_consensus_meeting.md`
- Metric files: `bundle/metrics/forecast_accuracy.md`, `bundle/metrics/days_of_supply.md`
- Entity files: `bundle/entities/product.md`, `bundle/entities/supplier.md`
- Glossary files: `bundle/glossary/recently_introduced.md`

## Status Values

- **`agent draft`** — Content requires domain expert review and company-specific values (table names, thresholds, time windows) filled in before marking active
- **`draft`** — Initial human review completed. Secondary opinion required before elevated to `active`
- **`active`** — Reliable for use by agents in analysis and reasoning
- **`deprecated`** — Do not use; has been superseded or is no longer valid

Always change status gradually — a draft becomes active only after review; an active document becomes deprecated by explicit decision, never silently.
