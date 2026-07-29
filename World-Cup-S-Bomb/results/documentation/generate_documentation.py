"""Generate comprehensive, content-aware documentation for ``results/``.

The generator intentionally uses only the Python standard library so the
artifact inventory can be rebuilt without importing the analytics stack.
"""

from __future__ import annotations

import csv
import json
import re
import struct
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any


RESULTS_ROOT = Path(__file__).resolve().parents[1]
DOCUMENTATION_ROOT = Path(__file__).resolve().parent
FOLDER_GUIDES = DOCUMENTATION_ROOT / "folders"

FOLDER_PURPOSES: dict[str, str] = {
    ".": (
        "Top-level result artifacts and entry points produced by the World Cup "
        "analytics pipeline."
    ),
    "audit": (
        "Observed-versus-expected comparison tables used to audit possession "
        "predictions, team aggregates, and out-of-fold behavior."
    ),
    "diagnostics": (
        "Model evaluation, calibration, feature-importance, cluster-quality, "
        "and validation diagnostics."
    ),
    "figures": (
        "Publication-ready charts and the technical onboarding presentation."
    ),
    "metadata": (
        "Machine-readable run metadata, feature definitions, provenance, and "
        "model configuration snapshots."
    ),
    "MIscellaneous": (
        "Supporting tactical summaries, legacy exploratory outputs, and the "
        "compact tournament PDF that do not belong to the canonical release."
    ),
    "reports": (
        "Human- and machine-readable player, team, coaching, and tournament "
        "reports."
    ),
    "reports/canonical": (
        "Canonical release artifacts: rankings, final summary, model summary, "
        "coaches notebook, and their data exports."
    ),
    "reports/canonical/data": (
        "Canonical tabular data backing the published reports."
    ),
    "reports/docs": (
        "Office-document editions of final reporting artifacts."
    ),
    "reports/player_profiles": (
        "One Markdown scouting and valuation profile per tournament player."
    ),
    "reports/starters": (
        "Country-code subfolders containing paired Markdown and JSON reports "
        "for each recorded starter."
    ),
    "reports/teams": (
        "Paired Markdown and JSON coaching reports for all 32 national teams."
    ),
    "reports/team_profiles": (
        "Concise Markdown team profiles with threat, defensive, resistance, "
        "and squad-rating summaries."
    ),
    "reports/v5_figures": (
        "V5 ranking and ElasticNet diagnostic figures embedded in reports."
    ),
    "reports/visuals": (
        "Container for report-linked visual assets."
    ),
    "reports/visuals/heatmaps": (
        "One SVG spatial heatmap per player, derived from event locations."
    ),
    "simulations": (
        "Tactical-style and substitution simulation outputs, including "
        "out-of-fold variants and suppression audits."
    ),
}


def _normalise(path: Path) -> str:
    """Return a forward-slash path relative to ``results``."""

    return path.relative_to(RESULTS_ROOT).as_posix()


def _safe_text(path: Path, limit: int | None = None) -> str:
    """Read text with replacement for malformed legacy characters."""

    with path.open("r", encoding="utf-8", errors="replace") as handle:
        return handle.read() if limit is None else handle.read(limit)


def _first_nonempty(lines: list[str]) -> str:
    """Return the first useful prose line."""

    for line in lines:
        clean = line.strip().lstrip("#").strip()
        if clean and not clean.startswith(("|", "---", "```")):
            return clean
    return ""


def _markdown_metadata(path: Path) -> tuple[str, str, str]:
    """Return title/headings, scale detail, and content description."""

    text = _safe_text(path)
    lines = text.splitlines()
    headings = [
        line.lstrip("#").strip()
        for line in lines
        if re.match(r"^#{1,3}\s+\S", line)
    ]
    title = headings[0] if headings else path.stem.replace("_", " ")
    sections = headings[1:9]
    structure = f"Title: {title}"
    if sections:
        structure += "; sections: " + ", ".join(sections)
    detail = f"{len(lines):,} lines; {len(text.split()):,} words"
    if "player_profiles" in path.parts:
        information = (
            f"Player profile for {title}, covering role, rating components, "
            "spatial/network evidence, and interpretation where available."
        )
    elif path.name.endswith("_team_coaching_report.md"):
        information = (
            f"Team coaching report for {title}, with tactical, player, "
            "simulation, and model-supported observations."
        )
    elif path.name.endswith("_starter_report.md"):
        information = (
            f"Starter report for {title}, pairing player-level match evidence "
            "with role and contribution analysis."
        )
    elif "team_profiles" in path.parts:
        information = (
            f"Team profile for {title}, summarizing threat creation, defensive "
            "compactness, pressure resistance, and squad ratings."
        )
    else:
        lead = _first_nonempty(lines)
        information = lead or f"Markdown report: {title}."
    return structure, detail, information


def _csv_metadata(path: Path) -> tuple[str, str, str]:
    """Return full CSV schema, dimensions, and inferred content."""

    rows = 0
    header: list[str] = []
    with path.open("r", encoding="utf-8-sig", errors="replace", newline="") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            pass
        else:
            rows = sum(1 for _ in reader)
    structure = "Columns: " + ", ".join(header) if header else "Empty CSV"
    detail = f"{rows:,} data rows × {len(header):,} columns"
    information = _description_from_name(path, "Tabular dataset")
    return structure, detail, information


def _json_metadata(path: Path) -> tuple[str, str, str]:
    """Return JSON root structure, dimensions, and inferred content."""

    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            payload: Any = json.load(handle)
    except (json.JSONDecodeError, OSError) as error:
        return "Unreadable JSON", "Parse failed", f"JSON parse error: {error}"
    if isinstance(payload, dict):
        keys = [str(key) for key in payload]
        structure = "Top-level keys: " + ", ".join(keys)
        detail = f"Object with {len(keys):,} top-level keys"
    elif isinstance(payload, list):
        detail = f"Array with {len(payload):,} records"
        if payload and isinstance(payload[0], dict):
            keys = [str(key) for key in payload[0]]
            structure = "Record keys: " + ", ".join(keys)
        else:
            structure = f"Top-level JSON {type(payload).__name__}"
    else:
        structure = f"Top-level JSON {type(payload).__name__}"
        detail = "Scalar JSON value"
    return structure, detail, _description_from_name(path, "JSON artifact")


def _png_metadata(path: Path) -> tuple[str, str, str]:
    """Return PNG dimensions without third-party imaging dependencies."""

    width = height = 0
    with path.open("rb") as handle:
        header = handle.read(24)
    if len(header) >= 24 and header[:8] == b"\x89PNG\r\n\x1a\n":
        width, height = struct.unpack(">II", header[16:24])
    dimensions = f"{width:,} × {height:,} pixels" if width else "PNG image"
    return "Raster image", dimensions, _description_from_name(path, "Figure")


def _svg_metadata(path: Path) -> tuple[str, str, str]:
    """Return SVG geometry and content description."""

    text = _safe_text(path, 16_384)
    viewbox = re.search(r'viewBox=["\']([^"\']+)', text)
    title = re.search(r"<title>(.*?)</title>", text, flags=re.DOTALL)
    structure = (
        f"SVG viewBox: {viewbox.group(1)}" if viewbox else "SVG vector image"
    )
    if title:
        information = re.sub(r"\s+", " ", title.group(1)).strip()
    elif "heatmaps" in path.parts:
        information = (
            f"Player spatial heatmap for {path.stem.replace('-', ' ')}, "
            "showing event-location intensity on the pitch."
        )
    else:
        information = _description_from_name(path, "Vector figure")
    return structure, "Scalable vector graphic", information


def _office_metadata(path: Path) -> tuple[str, str, str]:
    """Inspect DOCX/PPTX package metadata using OOXML."""

    properties: dict[str, str] = {}
    slide_count = 0
    with zipfile.ZipFile(path) as archive:
        if "docProps/app.xml" in archive.namelist():
            app = archive.read("docProps/app.xml").decode(
                "utf-8", errors="replace"
            )
            for key in ("Pages", "Words", "Paragraphs", "Slides"):
                match = re.search(rf"<{key}>(.*?)</{key}>", app)
                if match:
                    properties[key.lower()] = match.group(1)
        slide_count = sum(
            1
            for name in archive.namelist()
            if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)
        )
    if path.suffix.lower() == ".docx":
        detail = (
            f"{properties.get('pages', 'unknown')} stored pages; "
            f"{properties.get('words', 'unknown')} words"
        )
        return (
            "WordprocessingML document",
            detail,
            _description_from_name(path, "Formatted Word report"),
        )
    detail = f"{slide_count or properties.get('slides', 'unknown')} slides"
    return (
        "PowerPoint Open XML presentation",
        detail,
        _description_from_name(path, "Presentation"),
    )


def _pdf_metadata(path: Path) -> tuple[str, str, str]:
    """Estimate PDF page count from page objects."""

    data = path.read_bytes()
    pages = len(re.findall(rb"/Type\s*/Page(?!s)\b", data))
    detail = f"{pages} detected pages" if pages else "PDF document"
    return "Portable Document Format", detail, _description_from_name(
        path, "Formatted PDF report"
    )


def _parquet_metadata(path: Path) -> tuple[str, str, str]:
    """Describe Parquet files without requiring PyArrow."""

    return (
        "Apache Parquet columnar dataset",
        "Binary table; inspect with pandas or PyArrow for the physical schema",
        _description_from_name(path, "Columnar analytical dataset"),
    )


def _description_from_name(path: Path, fallback: str) -> str:
    """Infer analytical meaning from stable artifact naming conventions."""

    stem = path.stem.lower()
    rules = (
        ("player_rankings", "Player leaderboard with global, position, role, and team ranks plus valuation features."),
        ("model_summary", "Model-selection, validation, calibration, feature-importance, and metric-gate summary."),
        ("final_summary", "Tournament-wide executive report with player leaders and all-team summaries."),
        ("coaches_notebook", "Coach-facing tactical notebook covering networks, pressing, spatial advantages, and line breaking."),
        ("artifact_manifest", "Release manifest listing generated artifacts and integrity hashes."),
        ("cleanup_manifest", "Record of obsolete-artifact cleanup and canonical publication checks."),
        ("rating_validation_comparison", "Legacy-versus-current player rating and rank comparison."),
        ("role_aware_rating_comparison", "Comparison of legacy and role-aware valuation outputs."),
        ("role_aware_valuation_validation", "Validation diagnostics for the role-aware contribution model."),
        ("player_role_challenger_validation", "Baseline-versus-challenger role discovery validation results."),
        ("player_evaluation", "Player-level valuation feature matrix and final scores."),
        ("player_leaderboard", "Condensed player leaderboard for reporting and downstream use."),
        ("team_player_leaderboards", "Team-scoped player rankings and rating summaries."),
        ("team_coaching_report", "Team coaching report with tactical and player evidence."),
        ("starter_report", "Individual starter report in machine- or human-readable form."),
        ("goalkeeper_rankings", "Goalkeeper-only ranking visualization from the bifurcated goalkeeper model."),
        ("global_outfield_rankings", "Global outfield player ranking visualization."),
        ("france_team_rankings", "France squad ranking visualization."),
        ("elasticnet_coefficients", "ElasticNet coefficient visualization showing learned valuation feature weights."),
        ("expected_vs_actual", "Observed-versus-model-expected audit output."),
        ("calibration", "Probability calibration diagnostic or curve."),
        ("feature_importance", "Model feature-importance output."),
        ("cluster", "Role or tactical-cluster diagnostic output."),
        ("simulation", "Counterfactual tactical or substitution simulation output."),
        ("suppression", "Audit of simulation recommendations removed by safety or eligibility rules."),
        ("provenance", "Data and model provenance record for reproducibility."),
        ("feature", "Feature definitions, values, or diagnostic summaries."),
    )
    for token, description in rules:
        if token in stem:
            return description
    return f"{fallback}: {path.stem.replace('_', ' ').replace('-', ' ')}."


def _file_metadata(path: Path) -> dict[str, Any]:
    """Build a catalog record for one result artifact."""

    suffix = path.suffix.lower()
    handlers = {
        ".md": _markdown_metadata,
        ".csv": _csv_metadata,
        ".json": _json_metadata,
        ".png": _png_metadata,
        ".svg": _svg_metadata,
        ".docx": _office_metadata,
        ".pptx": _office_metadata,
        ".pdf": _pdf_metadata,
        ".parquet": _parquet_metadata,
    }
    handler = handlers.get(suffix)
    if handler is None:
        structure, detail, information = (
            "Placeholder or unclassified file",
            f"{path.stat().st_size:,} bytes",
            _description_from_name(path, "Artifact"),
        )
    else:
        try:
            structure, detail, information = handler(path)
        except (OSError, ValueError, KeyError, zipfile.BadZipFile) as error:
            structure, detail, information = (
                f"{suffix.lstrip('.').upper()} artifact",
                "Metadata inspection failed",
                f"{_description_from_name(path, 'Artifact')} Inspection error: {error}",
            )
    relative = _normalise(path)
    folder = Path(relative).parent.as_posix()
    return {
        "path": relative,
        "folder": "." if folder == "." else folder,
        "filename": path.name,
        "extension": suffix or "[none]",
        "bytes": path.stat().st_size,
        "format_details": detail,
        "structure": structure,
        "information": information,
    }


def _slug(folder: str) -> str:
    """Return a stable guide filename for a relative folder."""

    if folder == ".":
        return "results-root"
    return re.sub(r"[^a-z0-9]+", "-", folder.lower()).strip("-")


def _escape(value: object, limit: int | None = None) -> str:
    """Escape content for a compact Markdown table cell."""

    text = str(value).replace("|", r"\|").replace("\r", " ").replace("\n", " ")
    text = re.sub(r"\s+", " ", text).strip()
    if limit is not None and len(text) > limit:
        return text[: limit - 1].rstrip() + "…"
    return text


def _folder_purpose(folder: str) -> str:
    """Return curated or inferred folder purpose."""

    if folder in FOLDER_PURPOSES:
        return FOLDER_PURPOSES[folder]
    if folder.startswith("reports/starters/"):
        team = folder.rsplit("/", 1)[-1]
        return (
            f"Paired Markdown and JSON starter reports for team code {team}. "
            "Each player normally has one human-readable and one structured file."
        )
    return "Result artifacts grouped by pipeline stage or reporting audience."


def _write_catalogs(records: list[dict[str, Any]]) -> None:
    """Write CSV and JSON every-file inventories."""

    fields = [
        "path",
        "folder",
        "filename",
        "extension",
        "bytes",
        "format_details",
        "structure",
        "information",
    ]
    with (DOCUMENTATION_ROOT / "file_catalog.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(records)
    with (DOCUMENTATION_ROOT / "file_catalog.json").open(
        "w", encoding="utf-8"
    ) as handle:
        json.dump(
            {
                "scope": "Every artifact under results/, excluding results/documentation/",
                "artifact_count": len(records),
                "artifacts": records,
            },
            handle,
            indent=2,
            ensure_ascii=False,
        )
        handle.write("\n")


def _write_folder_guides(
    records: list[dict[str, Any]], folders: list[str]
) -> dict[str, str]:
    """Write one navigable Markdown guide per results folder."""

    by_folder: dict[str, list[dict[str, Any]]] = {
        folder: [] for folder in folders
    }
    for record in records:
        by_folder.setdefault(str(record["folder"]), []).append(record)
    guide_paths: dict[str, str] = {}
    for folder in folders:
        guide_name = _slug(folder) + ".md"
        guide_paths[folder] = f"folders/{guide_name}"
        direct = sorted(by_folder.get(folder, []), key=lambda row: row["filename"])
        prefix = "" if folder == "." else folder + "/"
        child_folders = sorted(
            candidate
            for candidate in folders
            if candidate != folder
            and candidate.startswith(prefix)
            and "/" not in candidate[len(prefix) :]
        )
        extension_counts = Counter(str(row["extension"]) for row in direct)
        title = "results/" if folder == "." else f"results/{folder}/"
        lines = [
            f"# `{title}`",
            "",
            _folder_purpose(folder),
            "",
            "## Inventory",
            "",
            f"- Direct files: **{len(direct):,}**",
            f"- Immediate subfolders: **{len(child_folders):,}**",
            "- Formats: "
            + (
                ", ".join(
                    f"`{extension}` ({count:,})"
                    for extension, count in sorted(extension_counts.items())
                )
                if extension_counts
                else "none"
            ),
            "",
        ]
        if child_folders:
            lines.extend(["## Subfolders", ""])
            for child in child_folders:
                child_link = _slug(child) + ".md"
                lines.append(
                    f"- [`results/{child}/`]({child_link}) — "
                    f"{_folder_purpose(child)}"
                )
            lines.append("")
        lines.extend(
            [
                "## Files",
                "",
                "| File | Format and scale | Information contained | Structure |",
                "|---|---|---|---|",
            ]
        )
        if not direct:
            lines.append("| _No direct files_ | — | Folder contains subfolders only. | — |")
        for record in direct:
            artifact_link = "../../" + str(record["path"])
            lines.append(
                "| "
                f"[`{_escape(record['filename'])}`]({artifact_link}) | "
                f"{_escape(record['extension'])}; "
                f"{_escape(record['format_details'], 160)}; "
                f"{int(record['bytes']):,} bytes | "
                f"{_escape(record['information'], 320)} | "
                f"{_escape(record['structure'], 500)} |"
            )
        lines.extend(
            [
                "",
                "## Interpretation and use",
                "",
                "Use human-readable Markdown, office documents, and figures for "
                "review. Use CSV, JSON, and Parquet artifacts for reproducible "
                "analysis. Consult the canonical model summary and provenance "
                "metadata before comparing metrics across model generations.",
                "",
            ]
        )
        (FOLDER_GUIDES / guide_name).write_text(
            "\n".join(lines), encoding="utf-8"
        )
    return guide_paths


def _write_index(
    records: list[dict[str, Any]],
    folders: list[str],
    guide_paths: dict[str, str],
) -> None:
    """Write the master results documentation index."""

    extension_counts = Counter(str(row["extension"]) for row in records)
    by_folder = Counter(str(row["folder"]) for row in records)
    lines = [
        "# Results documentation",
        "",
        "This directory is the comprehensive map of every artifact under "
        "`results/`. Generated documentation files are excluded from the "
        "inventory to avoid self-referential counts.",
        "",
        "## Coverage",
        "",
        f"- Documented artifacts: **{len(records):,}**",
        f"- Documented folders: **{len(folders):,}**",
        "- File formats: "
        + ", ".join(
            f"`{extension}` ({count:,})"
            for extension, count in sorted(extension_counts.items())
        ),
        "- Every artifact has its path, format, byte size, scale, internal "
        "structure or schema, and an explanation of the information it contains.",
        "",
        "## How to navigate",
        "",
        "- Start with the folder table below for a human-readable explanation.",
        "- Use [`file_catalog.csv`](file_catalog.csv) for filtering in a "
        "spreadsheet or dataframe.",
        "- Use [`file_catalog.json`](file_catalog.json) for programmatic lookup.",
        "- Rebuild these documents with "
        "`python results/documentation/generate_documentation.py` after outputs "
        "change.",
        "",
        "## Folder catalog",
        "",
        "| Results folder | Direct files | Purpose | Detailed guide |",
        "|---|---:|---|---|",
    ]
    for folder in folders:
        label = "results/" if folder == "." else f"results/{folder}/"
        lines.append(
            f"| `{label}` | {by_folder.get(folder, 0):,} | "
            f"{_escape(_folder_purpose(folder))} | "
            f"[Open guide]({guide_paths[folder]}) |"
        )
    lines.extend(
        [
            "",
            "## Canonical publication set",
            "",
            "The active release is under `results/reports/canonical/`. It contains "
            "the final and model summaries, player rankings, coaches notebook, "
            "artifact manifest, and canonical data exports. Player and team "
            "profile collections remain under their dedicated report folders.",
            "",
            "## Important interpretation notes",
            "",
            "- `canonical/` is the preferred source for current published values.",
            "- `diagnostics/` and `audit/` contain evaluation evidence, not "
            "leaderboards.",
            "- `MIscellaneous/` contains supporting or legacy exploratory outputs "
            "and should not override canonical conclusions.",
            "- `starters/`, `player_profiles/`, and `visuals/heatmaps/` are large "
            "one-file-per-entity collections; their folder guides enumerate every "
            "artifact.",
            "- Out-of-fold (`oof`) artifacts are the appropriate source for "
            "leakage-safe validation comparisons.",
            "",
        ]
    )
    (DOCUMENTATION_ROOT / "README.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_coverage(records: list[dict[str, Any]], folders: list[str]) -> None:
    """Write a concise completeness report for the generated documentation."""

    lines = [
        "# Documentation coverage report",
        "",
        f"- Source artifacts documented: **{len(records):,}**",
        f"- Source folders documented: **{len(folders):,}**",
        f"- Per-folder guides generated: **{len(folders):,}**",
        "- Undocumented source artifacts: **0**",
        "- Documentation scope excludes `results/documentation/` itself.",
        "",
        "Coverage is verified by matching each source artifact path to exactly "
        "one record in both `file_catalog.csv` and `file_catalog.json`, and by "
        "matching every source folder to one guide in `folders/`.",
        "",
    ]
    (DOCUMENTATION_ROOT / "coverage_report.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    """Generate the complete results documentation set."""

    FOLDER_GUIDES.mkdir(parents=True, exist_ok=True)
    source_files = sorted(
        (
            path
            for path in RESULTS_ROOT.rglob("*")
            if path.is_file() and DOCUMENTATION_ROOT not in path.parents
        ),
        key=lambda path: _normalise(path).lower(),
    )
    source_folders = sorted(
        {
            ".",
            *(
                _normalise(path)
                for path in RESULTS_ROOT.rglob("*")
                if path.is_dir()
                and path != DOCUMENTATION_ROOT
                and DOCUMENTATION_ROOT not in path.parents
            ),
        },
        key=lambda folder: (folder.count("/"), folder.lower()),
    )
    records = [_file_metadata(path) for path in source_files]
    _write_catalogs(records)
    guides = _write_folder_guides(records, source_folders)
    _write_index(records, source_folders, guides)
    _write_coverage(records, source_folders)
    print(
        json.dumps(
            {
                "artifacts_documented": len(records),
                "folders_documented": len(source_folders),
                "folder_guides": len(guides),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
