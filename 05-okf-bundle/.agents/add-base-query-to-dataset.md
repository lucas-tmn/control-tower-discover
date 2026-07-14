# Add Base Query To Dataset

Use this prompt when a gold/Fabric table is not yet available and an OKF dataset page needs a temporary base query documented from pasted SQL.

## Prompt

You are editing the OKF Supply Chain Knowledge Bundle in this repo. I will provide:

- The target dataset Markdown file, such as `bundle/datasets/tables/DimWarehouse.md`
- The base source table that should become the dataset `resource`
- The SQL query that produces the intended dataset shape

Update the target dataset documentation so an agent can query the base source while the gold table is unavailable.

## Required Changes

1. Read `AGENT.md`, the target dataset file, `bundle/log.md`, and the pasted SQL.
2. In the target dataset frontmatter:
   - Update `timestamp` to today's date.
   - Change `resource` to the provided base source table exactly.
   - Leave `data_source`, `source_system`, `refresh_cadence`, and `status` unchanged unless I explicitly ask otherwise.
3. Add a `## Base Query` section near the bottom of the dataset page, after `## Related` if that section exists.
4. Add a one-sentence note above the query explaining that it produces the dataset shape while the gold table is unavailable.
5. Paste the SQL in a fenced `sql` code block. Preserve aliases, joins, filters, CASE logic, comments, ordering, and source table names exactly unless there is an obvious Markdown escaping issue.
6. Append a newest-first entry to `bundle/log.md` under today's date describing:
   - The dataset updated
   - The temporary pivot from gold table assumption to base-query documentation
   - The base source table used
   - Any important join or derived-field logic from the SQL
7. Do not regenerate `bundle/viz.html`, update helper-generated indexes, or run tests during this per-table update.
8. At the end of the response, remind the user to run the helper scripts and tests once all table documents in the batch have been updated.

## Validation

Run these checks before finishing:

```powershell
python -c "from pathlib import Path; import sys; sys.path.insert(0, 'tools'); from document import OKFDocument; p=Path('<TARGET_FILE>'); doc=OKFDocument.parse(p.read_text(encoding='utf-8')); doc.validate(); print(doc.frontmatter['timestamp']); print(doc.frontmatter['resource']); print('Base Query' in doc.body); print(doc.body.count(chr(96)*3 + 'sql'), doc.body.count(chr(96)*3))"
rg -n "<OLD_GOLD_RESOURCE>|<NEW_BASE_RESOURCE>" <TARGET_FILE>
git diff --stat
```

Do not run `python -m pytest tools/tests` for each individual table update. Save tests for the end of the batch.

## Guardrails

- Keep the scope to the target dataset file and `bundle/log.md` unless I explicitly ask for related entity, generated viewer, or index updates.
- Do not regenerate `bundle/viz.html`.
- Do not run `tools/build_index.py` or make helper-generated index updates.
- Do not run tests during per-table updates.
- Do not move SQL mapping logic into entity pages. Dataset pages own schema and query mechanics; entity pages own business meaning.
- Do not change unrelated gold-table references in entity pages unless I explicitly ask for that broader migration.
- Preserve unrelated local changes and untracked files.

## Batch Completion Reminder

After completing a table update, remind the user to run these once all table documents in the batch are finished:

```powershell
python tools/build_index.py
python tools/build_viewer.py --root .\bundle --out .\bundle\viz.html
python -m pytest tools/tests
```

## Input Template

Target dataset file:

```text
bundle/datasets/tables/<TableName>.md
```

New base resource:

```text
[database].[schema].[BaseTable]
```

SQL:

```sql
<paste SQL here>
```
