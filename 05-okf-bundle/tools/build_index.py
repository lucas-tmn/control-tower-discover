"""Regenerate index.md files for every directory in the OKF bundle.

Adapted from the Google OKF reference-agent bundle/index.py.
LLM synthesis removed — descriptions are pulled directly from each concept's
frontmatter `description` field.

Usage:
    python tools/build_index.py
    python tools/build_index.py --root /path/to/bundle
    python tools/build_index.py --dry-run
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

# Allow running directly from the repo root without installing the package.
sys.path.insert(0, str(Path(__file__).parent))
from document import OKFDocument

_INDEX_FILE = "index.md"

# Files that are never OKF concept docs and should not appear in indexes.
_SKIP_NAMES = {_INDEX_FILE, "log.md", "CLAUDE.md", "AGENT.md"}

# Top-level directories to exclude entirely (tooling, hidden dirs, venv).
_SKIP_DIRS = {"tools", ".venv", "venv", ".git", ".agents", ".codex", "node_modules"}


def _load_doc(path: Path) -> OKFDocument | None:
    try:
        doc = OKFDocument.parse(path.read_text(encoding="utf-8"))
        # Skip files with no frontmatter (non-concept docs).
        return doc if doc.frontmatter else None
    except Exception:
        return None


def _describe_dir(entries: list[tuple[str, str, str, str]]) -> str:
    """Derive a deterministic fallback description for a subdirectory."""
    n = len(entries)
    if n == 1 and entries[0][3]:
        return entries[0][3]

    titles = ", ".join(title for _, title, _, _ in entries if title)
    if titles:
        return f"Contains {n} entries: {titles}."
    return f"Contains {n} entr{'y' if n == 1 else 'ies'}."


def _default_index_frontmatter(
    dir_path: Path,
    entries: list[tuple[str, str, str, str]],
) -> dict[str, Any]:
    """Build default metadata for an index without existing frontmatter."""
    return {
        "type": "Index",
        "title": dir_path.name.replace("_", " ").title(),
        "description": _describe_dir(entries),
        "timestamp": date.today().isoformat(),
    }


def _load_index_frontmatter(index_path: Path) -> dict[str, Any]:
    """Load hand-maintained index frontmatter, if present."""
    if not index_path.exists():
        return {}
    doc = OKFDocument.parse(index_path.read_text(encoding="utf-8"))
    return dict(doc.frontmatter)


def _index_description(index_path: Path) -> str:
    """Return the description from an index.md frontmatter block."""
    return str(_load_index_frontmatter(index_path).get("description") or "")


def _build_index_body(
    dir_path: Path,
    entries: list[tuple[str, str, str, str]],
    *,
    heading_level: int = 1,
) -> str:
    """Build index.md body from (type, title, relative_link, description) entries."""
    grouped: dict[str, list[tuple[str, str, str]]] = defaultdict(list)
    for typ, title, link, desc in entries:
        grouped[typ or "Other"].append((title, link, desc))

    heading = dir_path.name.replace("_", " ").title()
    heading_prefix = "#" * heading_level
    section_prefix = "#" * (heading_level + 1)
    lines: list[str] = [f"{heading_prefix} {heading}", ""]

    for typ in sorted(grouped):
        if typ != "Subdirectories":
            lines += [f"{section_prefix} {typ}", ""]
        else:
            lines += [f"{section_prefix} Subdirectories", ""]
        for title, link, desc in sorted(grouped[typ], key=lambda e: e[0].lower()):
            suffix = f" - {desc}" if desc else ""
            lines.append(f"- [{title}]({link}){suffix}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _build_index_text(
    dir_path: Path,
    entries: list[tuple[str, str, str, str]],
    frontmatter: dict[str, Any],
) -> str:
    """Build complete index.md content, preserving frontmatter."""
    heading_level = 2 if frontmatter.get("title") else 1
    doc = OKFDocument(
        frontmatter=frontmatter,
        body=_build_index_body(dir_path, entries, heading_level=heading_level),
    )
    return doc.serialize()


def _is_excluded(path: Path, bundle_root: Path) -> bool:
    """Return True if path is inside a directory that should be skipped."""
    try:
        rel = path.relative_to(bundle_root)
    except ValueError:
        return True
    # Skip hidden directories and known non-bundle directories.
    for part in rel.parts:
        if part.startswith(".") or part in _SKIP_DIRS:
            return True
    return False


def _directories_to_index(bundle_root: Path) -> list[Path]:
    dirs: set[Path] = set()
    for md in bundle_root.rglob("*.md"):
        if md.name in _SKIP_NAMES:
            continue
        if _is_excluded(md, bundle_root):
            continue
        cur = md.parent
        while cur != bundle_root.parent:
            dirs.add(cur)
            if cur == bundle_root:
                break
            cur = cur.parent
    return sorted(dirs)


def regenerate_indexes(
    bundle_root: Path,
    *,
    dry_run: bool = False,
    include_root: bool = False,
) -> list[Path]:
    """Walk bundle_root and write index.md files for every directory that has concepts.

    Returns the list of index paths written (or that would be written in dry-run mode).
    """
    bundle_root = Path(bundle_root).resolve()
    written: list[Path] = []
    if not bundle_root.exists():
        print(f"Bundle root not found: {bundle_root}", file=sys.stderr)
        return written

    directories = sorted(
        _directories_to_index(bundle_root),
        key=lambda p: (-len(p.relative_to(bundle_root).parts), str(p)),
    )

    dir_descriptions: dict[Path, str] = {}

    for directory in directories:
        entries: list[tuple[str, str, str, str]] = []

        for child in sorted(directory.iterdir()):
            if child.name in _SKIP_NAMES:
                continue
            if child.is_file() and child.suffix == ".md":
                doc = _load_doc(child)
                if doc is None:
                    continue
                fm = doc.frontmatter
                title = str(fm.get("title") or child.stem)
                desc = str(fm.get("description") or "")
                typ = str(fm.get("type") or "")
                entries.append((typ, title, child.name, desc))
            elif child.is_dir():
                if child.name.startswith(".") or child.name in _SKIP_DIRS:
                    continue
                desc = _index_description(child / _INDEX_FILE) or dir_descriptions.get(
                    child, ""
                )
                entries.append(
                    ("Subdirectories", child.name, f"{child.name}/{_INDEX_FILE}", desc)
                )

        if not entries:
            continue

        # Skip the root index.md by default — it is manually maintained.
        if directory == bundle_root and not include_root:
            dir_descriptions[directory] = _describe_dir(entries)
            continue

        index_path = directory / _INDEX_FILE
        frontmatter = _load_index_frontmatter(index_path) or _default_index_frontmatter(
            directory, entries
        )
        content = _build_index_text(directory, entries, frontmatter)

        if dry_run:
            print(f"[dry-run] Would write: {index_path.relative_to(bundle_root)}")
            print(content)
            print("-" * 60)
        else:
            index_path.write_text(content, encoding="utf-8")
            print(f"  wrote  {index_path.relative_to(bundle_root)}")

        written.append(index_path)

        # Store this directory's description for use in its parent's index.
        if directory != bundle_root:
            dir_descriptions[directory] = _describe_dir(entries)

    return written


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Regenerate index.md files for an OKF bundle."
    )
    parser.add_argument(
        "--root",
        default=str(Path(__file__).parent.parent / "bundle"),
        help="Path to the bundle root directory (default: bundle/)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be written without modifying any files",
    )
    parser.add_argument(
        "--include-root",
        action="store_true",
        help="Also regenerate the root index.md (normally skipped as it is hand-crafted)",
    )
    args = parser.parse_args()

    bundle_root = Path(args.root)
    print(f"Bundle root: {bundle_root}")
    written = regenerate_indexes(
        bundle_root, dry_run=args.dry_run, include_root=args.include_root
    )
    verb = "Would write" if args.dry_run else "Wrote"
    print(f"{verb} {len(written)} index file(s).")


if __name__ == "__main__":
    main()
