"""Regression tests for the ranking-repair stale-content classifier."""

from __future__ import annotations

from pathlib import Path

from scripts.run_ranking_repair_v3 import _scan_stale_content


def _write(root: Path, relative: str, text: str) -> None:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_stale_scan_distinguishes_active_rules_from_context(
    tmp_path: Path,
) -> None:
    _write(
        tmp_path,
        "src/active_score.py",
        "SHOOTOUT_SAVE_POINTS = 0.20\n"
        "impact = minutes / (minutes + 450)\n",
    )
    _write(
        tmp_path,
        "scripts/update_unified_final_summary_docx.py",
        "# Historical wording retained temporarily.\n"
        'APPENDIX_TITLE = "Part IX: Unified tournament publication layer"\n',
    )
    _write(
        tmp_path,
        "src/docx_validator.py",
        'if "Part IX: Unified tournament publication layer" in text:\n'
        '    raise ValueError("Stale appendix remains")\n',
    )
    _write(
        tmp_path,
        "README.md",
        "The active score does not use within-position z-scores as absolute "
        "global value.\n",
    )
    _write(
        tmp_path,
        "docs/history.md",
        "# Historical pre-v3 architecture\n\n"
        "The former score used minutes / (minutes + 450).\n",
    )
    _write(
        tmp_path,
        "results/reports/profile.md",
        "- Non-shootout xG: 0.2051\n"
        '- "xg_non_shootout": 0.200274783\n',
    )
    _write(
        tmp_path,
        "results/metadata/feature_definitions.json",
        '{"retired_active_methods": [\n'
        '  "0.20 additive points per goalkeeper shootout save"\n'
        "]}\n",
    )
    _write(
        tmp_path,
        "scripts/run_pipeline.py",
        '"shootout_save_points": 0.20,\n',
    )
    _write(
        tmp_path,
        "results/diagnostics/ranking_repair/champion/model_summary.md",
        "shootout save points: 0.20\n",
    )
    _write(
        tmp_path,
        "tests/test_old_formula.py",
        'assert "minutes / (minutes + 450)" in historical_text\n',
    )
    _write(
        tmp_path,
        "scripts/run_ranking_repair_v3.py",
        "def _scan_stale_content():\n"
        '    pattern = r"EXPOSURE_SATURATION_SHARE"\n'
        "\n"
        "def next_function():\n"
        "    return None\n",
    )
    _write(
        tmp_path,
        "results/diagnostics/ranking_repair/stale_content_audit.json",
        '{"context": "SHOOTOUT_SAVE_POINTS = 0.20"}\n',
    )

    records = _scan_stale_content(tmp_path)
    indexed = {
        (record["path"], record["pattern"]): record
        for record in records
    }

    assert indexed[
        ("src/active_score.py", "shootout-save-0.20")
    ]["classification"] == "stale-requires-correction"
    assert indexed[
        ("src/active_score.py", "old-exposure-constants")
    ]["classification"] == "stale-requires-correction"
    assert indexed[
        (
            "scripts/update_unified_final_summary_docx.py",
            "stale-docx-appendix",
        )
    ]["classification"] == "stale-requires-correction"
    assert indexed[
        ("src/docx_validator.py", "stale-docx-appendix")
    ]["classification"] == "active-and-correct"

    assert indexed[
        ("README.md", "within-position-absolute")
    ]["classification"] == "active-and-correct"
    assert indexed[
        ("docs/history.md", "old-exposure-constants")
    ]["classification"] == "compatibility-or-legacy"
    assert indexed[
        ("scripts/run_pipeline.py", "shootout-save-0.20")
    ]["classification"] == "compatibility-or-legacy"
    assert indexed[
        (
            "results/diagnostics/ranking_repair/champion/model_summary.md",
            "shootout-save-0.20",
        )
    ]["classification"] == "compatibility-or-legacy"
    assert indexed[
        (
            "results/metadata/feature_definitions.json",
            "shootout-save-0.20",
        )
    ]["classification"] == "compatibility-or-legacy"
    assert indexed[
        ("tests/test_old_formula.py", "old-exposure-constants")
    ]["classification"] == "test-fixture"
    assert indexed[
        (
            "scripts/run_ranking_repair_v3.py",
            "old-exposure-constants",
        )
    ]["classification"] == "active-and-correct"

    assert not any(
        record["path"] == "results/reports/profile.md"
        for record in records
    )
    assert not any(
        record["path"].endswith("stale_content_audit.json")
        for record in records
    )
    assert all(record["classification_reason"] for record in records)
