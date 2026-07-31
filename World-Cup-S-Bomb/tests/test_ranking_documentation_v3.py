"""Focused tests for the active ranking-repair v3 documentation contract."""

from __future__ import annotations

import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR_PATH = (
    PROJECT_ROOT / "results" / "documentation" / "generate_documentation.py"
)


def _load_generator():
    spec = importlib.util.spec_from_file_location(
        "ranking_documentation_generator",
        GENERATOR_PATH,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_rankings_dictionary_uses_active_v3_contract(
    tmp_path: Path,
) -> None:
    generator = _load_generator()
    generator.DOCUMENTATION_ROOT = tmp_path
    records = [
        {
            "path": "reports/ranking/player_rankings.csv",
            "folder": "reports/ranking",
            "format_details": "593 data rows × 450 columns",
        }
    ]

    generator._write_rankings_dictionary(records)
    generator._write_results_dictionary(records)
    generator.RESULTS_ROOT = tmp_path / "results"
    generator._write_profiles_dictionary(records)
    text = (tmp_path / "reports-rankings.md").read_text(encoding="utf-8")

    required = (
        "ranking-repair-v3.0-qatar-2022",
        "Tournament Impact v3",
        "Role Quality v3",
        "Uncertainty",
        "periods 1–4",
        "global_rankings_outfield.csv",
        "player_rankings_300plus.csv",
        "goalkeeper_rankings.md",
        "global_rank_v3",
        "uncertainty_status_v3",
        "goalkeeper_consolidated_value_rank_v5",
        "PSxG-style",
        "reports/v3_figures/",
        "Canonical-file rule",
    )
    for phrase in required:
        assert phrase in text

    assert "ordered by `global_rank_v2`" not in text
    assert "Separate non-comparable rating" not in text
    assert "Versioned duplicates" in text
    assert "Goalkeepers do not appear in either" in text

    results_dictionary = (
        tmp_path / "results-dictionary.md"
    ).read_text(encoding="utf-8")
    assert "Active Qatar 2022 v3 Tournament Impact" in results_dictionary
    assert "Current outfield ranking figures" in results_dictionary
    assert "Current consolidated goalkeeper" in results_dictionary
    profiles_dictionary = (
        tmp_path / "reports-profiles.md"
    ).read_text(encoding="utf-8")
    assert "Tournament Impact v3 and global/team ranks" in profiles_dictionary
    assert "periods 1–4" in profiles_dictionary


def test_role_pipeline_and_readme_separate_active_and_historical_methods() -> None:
    role_pipeline = (
        PROJECT_ROOT / "docs" / "role_aware_pipeline.md"
    ).read_text(encoding="utf-8")
    readme = (PROJECT_ROOT / "README.md").read_text(encoding="utf-8")

    for text in (role_pipeline, readme):
        assert "Tournament Impact" in text
        assert "Role Quality" in text
        assert "Uncertainty" in text
        assert "periods 1–4" in text
        assert "goalkeeper_rankings" in text
        assert "v3_figures" in text

    historical = role_pipeline.split("## Historical pre-v3 architecture", 1)
    assert len(historical) == 2
    active, legacy = historical
    assert "minutes / (minutes + 450)" not in active
    assert "minutes / (minutes + 450)" in legacy
    assert "`0.20` per shootout save" in legacy
    assert "none is an active v3 scoring rule" in legacy
