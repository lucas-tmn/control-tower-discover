# PROVENANCE

| Field | Value |
|---|---|
| **What this is** | A vendored (copied-in) snapshot of Robert's **OKF Supply Chain Knowledge Bundle** repository (`scp-okf-bundle`, master branch). |
| **Vendored on** | 2026-07-09 |
| **Vendored from** | ZIP export of the GitHub repository provided by the Discovery Lead (file: `scp-okf-bundle-master.zip`; upstream file timestamps 2026-07-08) |
| **Original author / owner** | Robert (supply-chain business, data analysis & AI SME) |
| **Role in this repo** | The **TO-BE layer**: governed target-state definitions of metrics, entities, glossary terms, datasets (SupplyChain_Gold), playbooks, and processes. Contrast with `01-evidence/` (the AS-IS layer) and `06-bridge/` (the mapping between them). |

## Ground rules for this directory

1. **Do not edit content here directly.** This is Robert's knowledge, kept intact
   so it can be diffed against / re-synced with his upstream repo. Everything
   inside (including `AGENT.md`, `CLAUDE.md`, `README.md`, `SOE_PLAN.md`,
   `tools/`, `.agents/`, and the nested `.gitignore`) is exactly as vendored,
   except this `PROVENANCE.md` file, which is ours.
2. **Corrections, gap-fills, and disagreements** with the bundle's content go in
   `../06-bridge/` (especially `gap-fill-candidates.md`), then get proposed to
   Robert upstream — not patched here silently.
3. **Re-syncing:** to update, replace this directory's contents wholesale from a
   fresh upstream export, keep this file, and update the "Vendored on/from"
   fields above. Then re-check `../06-bridge/` mappings for drift.
4. The bundle's own agent instructions (`AGENT.md`/`CLAUDE.md`) apply **within
   this directory only** — e.g., its rule "do not hand-edit index.md, use
   `tools/build_index.py`" governs `05-okf-bundle/bundle/`, not the rest of the
   control-tower-discover repo.
