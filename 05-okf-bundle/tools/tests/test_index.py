from __future__ import annotations

from pathlib import Path

from document import OKFDocument
from build_index import regenerate_indexes


def _write_doc(path: Path, type_: str, title: str, description: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = OKFDocument(
        frontmatter={
            "type": type_,
            "title": title,
            "description": description,
            "timestamp": "2026-05-27T00:00:00+00:00",
        },
        body=f"# {title}\n\n{description}\n",
    )
    path.write_text(doc.serialize(), encoding="utf-8")


def _write_index(path: Path, title: str, description: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    doc = OKFDocument(
        frontmatter={
            "type": "Index",
            "title": title,
            "description": description,
            "timestamp": "2026-05-27",
            "owner": "manual",
        },
        body=f"# {title}\n\nOld generated body.\n",
    )
    path.write_text(doc.serialize(), encoding="utf-8")


def test_regenerate_groups_by_type_and_links_relative(tmp_path: Path):
    root = tmp_path / "bundle"
    _write_doc(
        root / "datasets" / "actuals.md",
        "Dataset",
        "Actuals Dataset",
        "Shipment actuals from ERP.",
    )
    _write_doc(
        root / "tables" / "fact_sales.md",
        "Dataset",
        "Fact Sales",
        "Daily-sharded sales fact table.",
    )
    _write_doc(
        root / "tables" / "dim_product.md",
        "Dataset",
        "Dim Product",
        "Product dimension.",
    )

    # include_root=True so we can assert on the root index; written_names covers all three dirs.
    written = regenerate_indexes(root, include_root=True)
    written_names = {p.parent.name for p in written}
    assert {"bundle", "datasets", "tables"} <= written_names | {root.name}

    tables_index = (root / "tables" / "index.md").read_text(encoding="utf-8")
    tables_doc = OKFDocument.parse(tables_index)
    # Heading derived from directory name, not concept type.
    assert tables_doc.body.startswith("## Tables")
    assert "### Dataset" in tables_doc.body
    assert "# Tables" not in tables_doc.body.splitlines()
    assert "[Fact Sales](fact_sales.md)" in tables_doc.body
    assert "[Dim Product](dim_product.md)" in tables_doc.body
    assert "Daily-sharded sales fact table." in tables_doc.body
    assert tables_doc.frontmatter["type"] == "Index"

    root_index = (root / "index.md").read_text(encoding="utf-8")
    root_doc = OKFDocument.parse(root_index)
    assert "Subdirectories" in root_index
    assert "(datasets/index.md) - Shipment actuals from ERP." in root_doc.body
    assert "(tables/index.md) - Contains 2 entries: Dim Product, Fact Sales." in root_doc.body
    assert "Product dimension." not in root_doc.body


def test_regenerate_skips_empty_directories(tmp_path: Path):
    root = tmp_path / "bundle"
    root.mkdir()
    (root / "empty_dir").mkdir()

    written = regenerate_indexes(root)
    assert written == []
    assert not (root / "empty_dir" / "index.md").exists()


def test_regenerate_single_child_reuses_description(tmp_path: Path):
    root = tmp_path / "bundle"
    _write_doc(
        root / "datasets" / "only.md",
        "Dataset",
        "Only Dataset",
        "The only dataset in this bundle.",
    )

    regenerate_indexes(root, include_root=True)

    root_index = (root / "index.md").read_text(encoding="utf-8")
    root_doc = OKFDocument.parse(root_index)
    # When a subdirectory has one concept, its description propagates to the root index
    # without needing a manually authored index description.
    assert "(datasets/index.md) - The only dataset in this bundle." in root_doc.body


def test_regenerate_preserves_index_frontmatter_and_uses_it_for_parent(tmp_path: Path):
    root = tmp_path / "bundle"
    _write_doc(
        root / "queries" / "customer.md",
        "Query",
        "Customer Query",
        "Customer-specific query description.",
    )
    _write_doc(
        root / "queries" / "item.md",
        "Query",
        "Item Query",
        "Item-specific query description.",
    )
    _write_index(
        root / "queries" / "index.md",
        "Queries",
        "General query directory description.",
    )

    regenerate_indexes(root, include_root=True)

    queries_doc = OKFDocument.parse(
        (root / "queries" / "index.md").read_text(encoding="utf-8")
    )
    assert queries_doc.frontmatter == {
        "type": "Index",
        "title": "Queries",
        "description": "General query directory description.",
        "timestamp": "2026-05-27",
        "owner": "manual",
    }
    assert "Old generated body." not in queries_doc.body
    assert "[Customer Query](customer.md)" in queries_doc.body

    root_doc = OKFDocument.parse(
        (root / "index.md").read_text(encoding="utf-8")
    )
    assert "(queries/index.md) - General query directory description." in root_doc.body
    assert "Customer-specific query description." not in root_doc.body
