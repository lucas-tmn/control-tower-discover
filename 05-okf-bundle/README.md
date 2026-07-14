# OKF Supply Chain Knowledge Bundle

This repository creates and maintains an Open Knowledge Format (OKF) bundle for
supply chain reasoning agents. The bundle is a structured, cross-linked markdown
knowledge base covering datasets, metrics, business entities, glossary terms,
processes, and decision playbooks.

The main artifact is the content under `bundle/`. The Python code under `tools/`
exists to maintain that bundle: parsing OKF frontmatter, regenerating directory
indexes, building an interactive HTML graph viewer, and testing those behaviors.

## Context

The current bundle focuses on the Demand/Supply Planning vertical, including
forecasting, inventory, procurement, fulfillment, supplier performance, and
warehouse operations. It is intended to give agents enough shared business
context to reason consistently about supply chain questions without inventing
definitions, calculations, or decision rules.

OKF documents are markdown files with YAML frontmatter. The frontmatter records
the concept type, title, description, tags, timestamp, status, and dataset-specific
metadata where applicable. Links between documents are meaningful relationships;
they are used both by readers and by the visualization tooling.

## Repository Layout

```text
bundle/
  index.md                 Root OKF bundle index
  log.md                   Changelog for bundle edits
  viz.html                 Generated interactive bundle viewer
  datasets/                Warehouse tables, grain, source systems, key fields
  entities/                Canonical business object definitions
  glossary/                Organization-specific term definitions
  metrics/                 KPI definitions and calculation logic
  playbooks/               Step-by-step reasoning workflows
  processes/               Recurring business workflows and decision gates

tools/
  document.py              OKF markdown frontmatter parser and serializer
  build_index.py           Regenerates bundle directory index.md files
  build_viewer.py          Builds bundle/viz.html from concept links
  templates/viz.html       HTML shell for the viewer
  static/viz.css           Viewer styles
  static/viz.js            Viewer behavior
  tests/                   Pytest coverage for parser, index, and viewer tools

AGENT.md                  Working instructions for agents editing this repo
CLAUDE.md                 Parallel agent-facing repository guidance
```

## Bundle Domains

- `bundle/playbooks/`: action-oriented analysis flows, such as forecast revision,
  stockout escalation, new product review, and supply plan review.
- `bundle/processes/`: recurring business processes and decision timing.
- `bundle/datasets/`: data asset references, especially warehouse table docs.
- `bundle/metrics/`: KPI definitions with business meaning and calculation logic.
- `bundle/entities/`: core business objects such as product, customer, vendor,
  warehouse, and transaction date.
- `bundle/glossary/`: company-specific language such as shippable inventory,
  resultant forecast, demand consensus, overstock, and stockout.

## Tooling

### `tools/document.py`

Parses and serializes markdown documents with YAML frontmatter. This is the
shared helper used by the other tools. Required frontmatter keys are:

- `type`
- `title`
- `description`
- `timestamp`

### `tools/build_index.py`

Regenerates `index.md` files for directories inside the OKF bundle. It reads each
concept document's frontmatter and groups index entries by `type`. Use this
script, not manual edits, whenever bundle indexes need to change. The script
preserves existing directory index frontmatter and regenerates the markdown body.
Parent indexes use child `index.md` frontmatter descriptions for subdirectory
summaries.

Common commands:

```powershell
python tools/build_index.py
python tools/build_index.py --dry-run
python tools/build_index.py --root .\bundle
python tools/build_index.py --include-root
```

By default, the root `bundle/index.md` is left alone. Use `--include-root` only
when you intentionally want the helper to regenerate it.

### `tools/build_viewer.py`

Builds a self-contained HTML visualization of the bundle. The viewer walks all
OKF concept documents, extracts frontmatter and markdown links, and writes a
single `viz.html` file with an interactive graph.

Common commands:

```powershell
python tools/build_viewer.py
python tools/build_viewer.py --name "Supply Chain Knowledge Bundle"
python tools/build_viewer.py --root .\bundle --out .\bundle\viz.html
```

Open `bundle/viz.html` in a browser to explore the concept graph. Nodes are
colored by OKF type, and edges come from markdown links between concept files.

### Tests

The test suite covers:

- OKF frontmatter parsing and serialization
- index regeneration behavior
- viewer graph generation, including link edges and skipped missing targets

Run tests from the repository root:

```powershell
python -m pytest tools\tests
```

## Setup

The tools require Python and the packages in `tools/requirements.txt`.

```powershell
python -m venv tools\.venv
.\tools\.venv\Scripts\Activate.ps1
python -m pip install -r tools\requirements.txt
```

After setup, run:

```powershell
python tools/build_index.py --dry-run
python tools/build_viewer.py
python -m pytest tools\tests
```

## Editing the Bundle

When adding a new concept:

1. Create the markdown file in the right `bundle/` subdirectory.
2. Add YAML frontmatter with the required OKF fields.
3. Use bundle-relative links, such as `[Forecast Accuracy](/metrics/forecast_accuracy.md)`.
4. Regenerate indexes with `python tools/build_index.py` when the user is ready
   to refresh generated bundle artifacts.
5. Add a short entry to `bundle/log.md` explaining what changed and why.
6. Rebuild `bundle/viz.html` if links or concept files changed.

When updating an existing concept:

1. Update the document body and frontmatter timestamp.
2. Preserve meaningful cross-links or add new ones where they clarify relationships.
3. Record the change in `bundle/log.md`.
4. Regenerate indexes and the viewer when needed.

## Conventions

- Dataset table files use PascalCase when they mirror warehouse table names, such
  as `DimProduct.md` or `FactSupplyPlanDetail.md`.
- Other concept files generally use lowercase with underscores.
- Dataset documents describe schema, grain, source system, data source, and key
  fields.
- Entity documents describe business meaning, not reporting-specific SQL logic.
- Metric documents define calculations exactly; agents should not substitute
  alternate formulas.
- `[FILL IN: ...]` placeholders mark values that need domain review before a
  document can be treated as complete.
- Broken links should be logged, not silently removed.

## Generated Files

`bundle/viz.html` is generated by `tools/build_viewer.py`. Do not hand-edit it
for durable changes. Update the markdown content, templates, CSS, or JavaScript,
then rebuild the viewer.

Bundle `index.md` files are maintained by `tools/build_index.py`. Do not
hand-edit them for durable changes; update concept files and run the helper.
Use `python tools/build_index.py --include-root` only when the root
`bundle/index.md` should also be regenerated.
