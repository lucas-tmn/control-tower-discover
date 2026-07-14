"""Generate a self-contained HTML visualization of an OKF bundle.

Adapted from the Google OKF reference-agent viewer/generator.py.
Walks all concept .md files, extracts frontmatter and cross-links,
and produces a single viz.html with an interactive Cytoscape.js graph.

Usage:
    python tools/build_viewer.py
    python tools/build_viewer.py --root /path/to/bundle --out viz.html
    python tools/build_viewer.py --name "Supply Chain KB"
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).parent))
from document import OKFDocument, OKFDocumentError

_INDEX_NAME = "index.md"
_SKIP_NAMES = {_INDEX_NAME, "log.md", "CLAUDE.md", "AGENT.md"}
_SKIP_DIRS = {"tools", ".venv", "venv", ".git", ".agents", ".codex", "node_modules"}
_LINK_RE = re.compile(r"\]\(([^)\s]+\.md)(?:#[A-Za-z0-9_\-]*)?\)")

_TYPE_PALETTE: dict[str, str] = {
    "Dataset": "#3b82f6",
    "Metric": "#8b5cf6",
    "Entity": "#10b981",
    "Playbook": "#f59e0b",
    "Process": "#14b8a6",
    "Glossary Term": "#64748b",
}
_DEFAULT_NODE_COLOR = "#94a3b8"


@dataclass
class Concept:
    id: str
    type: str
    title: str
    description: str
    resource: str
    tags: list[str]
    body: str
    links_to: list[str] = field(default_factory=list)

    def to_node(self) -> dict[str, Any]:
        color = _TYPE_PALETTE.get(self.type, _DEFAULT_NODE_COLOR)
        return {
            "data": {
                "id": self.id,
                "label": self.title or self.id,
                "type": self.type,
                "description": self.description,
                "resource": self.resource,
                "tags": self.tags,
                "color": color,
                "size": 30 + min(60, len(self.body) // 200),
            }
        }


def _extract_links(body: str, doc_dir: Path, bundle_root: Path) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    bundle_root_resolved = bundle_root.resolve()
    for m in _LINK_RE.finditer(body):
        target = m.group(1)
        if "://" in target:
            continue
        try:
            if target.startswith("/"):
                # Bundle-root-relative absolute path (e.g. /metrics/forecast_accuracy.md).
                resolved = (bundle_root_resolved / target.lstrip("/")).resolve()
                resolved = resolved.relative_to(bundle_root_resolved)
            else:
                resolved = (doc_dir / target).resolve().relative_to(bundle_root_resolved)
        except ValueError:
            continue
        rel = resolved.as_posix()
        if rel.endswith(".md"):
            rel = rel[:-3]
        if rel and rel not in seen:
            seen.add(rel)
            out.append(rel)
    return out


def _is_excluded(path: Path, bundle_root: Path) -> bool:
    try:
        rel = path.relative_to(bundle_root)
    except ValueError:
        return True
    for part in rel.parts:
        if part.startswith(".") or part in _SKIP_DIRS:
            return True
    return False


def _walk_concepts(bundle_root: Path) -> list[Concept]:
    concepts: list[Concept] = []
    for md_path in sorted(bundle_root.rglob("*.md")):
        if md_path.name in _SKIP_NAMES:
            continue
        if _is_excluded(md_path, bundle_root):
            continue
        try:
            doc = OKFDocument.parse(md_path.read_text(encoding="utf-8"))
        except OKFDocumentError:
            continue
        # Skip files with no frontmatter (non-concept docs).
        if not doc.frontmatter:
            continue
        rel = md_path.relative_to(bundle_root).with_suffix("")
        concept_id = "/".join(rel.parts)
        fm = doc.frontmatter or {}
        tags = fm.get("tags") or []
        if not isinstance(tags, list):
            tags = [str(tags)]
        concept = Concept(
            id=concept_id,
            type=str(fm.get("type") or "Unknown"),
            title=str(fm.get("title") or concept_id),
            description=str(fm.get("description") or ""),
            resource=str(fm.get("resource") or ""),
            tags=[str(t) for t in tags],
            body=doc.body or "",
            links_to=_extract_links(doc.body or "", md_path.parent, bundle_root),
        )
        concepts.append(concept)
    return concepts


def _build_graph(concepts: list[Concept]) -> dict[str, Any]:
    ids = {c.id for c in concepts}
    nodes = [c.to_node() for c in concepts]
    edges: list[dict[str, Any]] = []
    seen_edges: set[tuple[str, str]] = set()
    for c in concepts:
        for target in c.links_to:
            if target == c.id or target not in ids:
                continue
            key = (c.id, target)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append({
                "data": {
                    "id": f"{c.id}__{target}",
                    "source": c.id,
                    "target": target,
                }
            })
    bodies = {c.id: c.body for c in concepts}
    types = sorted({c.type for c in concepts})
    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": bodies,
        "types": types,
        "palette": _TYPE_PALETTE,
    }


def _load_template() -> str:
    template_path = Path(__file__).parent / "templates" / "viz.html"
    return template_path.read_text(encoding="utf-8")


def _load_asset(name: str) -> str:
    asset_path = Path(__file__).parent / "static" / name
    return asset_path.read_text(encoding="utf-8")


def generate_visualization(
    bundle_root: Path,
    out_path: Path,
    *,
    bundle_name: str | None = None,
) -> dict[str, int]:
    """Walk a bundle and write a single self-contained HTML visualization.

    Returns counts: {'concepts': N, 'edges': M, 'bytes': K}.
    """
    bundle_root = Path(bundle_root).resolve()
    out_path = Path(out_path)
    if not bundle_root.is_dir():
        raise FileNotFoundError(f"Bundle directory not found: {bundle_root}")

    concepts = _walk_concepts(bundle_root)
    graph = _build_graph(concepts)
    template = _load_template()
    css = _load_asset("viz.css")
    js = _load_asset("viz.js")
    name = bundle_name or bundle_root.name

    html = (
        template
        .replace("/*__VIZ_CSS__*/", css)
        .replace("/*__VIZ_JS__*/", js)
        .replace("__BUNDLE_NAME__", json.dumps(name))
        .replace("__BUNDLE_DATA__", json.dumps(graph))
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(html, encoding="utf-8")

    return {
        "concepts": len(concepts),
        "edges": len(graph["edges"]),
        "bytes": len(html.encode("utf-8")),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an interactive HTML visualization of an OKF bundle."
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).parent.parent / "bundle"),
        help="Path to the bundle root directory (default: bundle/)",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Output path for viz.html (default: <root>/viz.html)",
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Bundle display name shown in the viewer header",
    )
    args = parser.parse_args()

    bundle_root = Path(args.root)
    out_path = Path(args.out) if args.out else bundle_root / "viz.html"

    print(f"Bundle root : {bundle_root}")
    print(f"Output      : {out_path}")

    counts = generate_visualization(bundle_root, out_path, bundle_name=args.name)
    print(
        f"Done — {counts['concepts']} concepts, "
        f"{counts['edges']} edges, "
        f"{counts['bytes']:,} bytes"
    )


if __name__ == "__main__":
    main()
