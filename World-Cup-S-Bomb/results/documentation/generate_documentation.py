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
        "compact tournament PDF that do not belong to the active release."
    ),
    "miscellaneous": (
        "Supporting tactical summaries, legacy exploratory outputs, and the "
        "compact tournament PDF that do not belong to the active release."
    ),
    "reports": (
        "Human- and machine-readable player, team, coaching, and tournament "
        "reports."
    ),
    "reports/canonical": (
        "Canonical release narrative: final summary, model summary, coaches "
        "notebook, and their data exports."
    ),
    "reports/canonical/data": (
        "Canonical tabular data backing the published reports."
    ),
    "reports/ranking": (
        "Active Qatar 2022 player and goalkeeper rankings, methodology, and "
        "validation audit."
    ),
    "reports/ranking/by_team": (
        "Complete player ranking CSVs for each national team."
    ),
    "reports/ranking/legacy": (
        "Archived pre-v2 ranking tables retained for reproducible comparison."
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
    with (DOCUMENTATION_ROOT / "file_dictionary.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=fields,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(records)
    with (DOCUMENTATION_ROOT / "file_dictionary.json").open(
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


def _family_count(
    records: list[dict[str, Any]],
    folder: str,
    *,
    recursive: bool = False,
) -> int:
    """Count catalog records in one artifact family."""

    if recursive:
        prefix = folder + "/"
        return sum(
            1
            for record in records
            if record["folder"] == folder
            or str(record["folder"]).startswith(prefix)
        )
    return sum(1 for record in records if record["folder"] == folder)


def _write_results_dictionary(records: list[dict[str, Any]]) -> None:
    """Write a compact path-pattern dictionary covering every result file."""

    families = [
        (
            "Audit tables",
            "audit/*",
            _family_count(records, "audit"),
            "Observed-versus-expected and out-of-fold audit tables.",
        ),
        (
            "Model diagnostics",
            "diagnostics/*",
            _family_count(records, "diagnostics"),
            "Validation metrics, calibration, importance, and cluster diagnostics.",
        ),
        (
            "Publication figures",
            "figures/*",
            _family_count(records, "figures"),
            "Charts and the technical onboarding presentation.",
        ),
        (
            "Run metadata",
            "metadata/*",
            _family_count(records, "metadata"),
            "Configuration, provenance, and feature-definition records.",
        ),
        (
            "Supporting/legacy outputs",
            "miscellaneous/*",
            (
                _family_count(records, "miscellaneous")
                + _family_count(records, "MIscellaneous")
            ),
            "Exploratory summaries and noncanonical model leaderboards.",
        ),
        (
            "Reports directory guide",
            "reports/README.md",
            _family_count(records, "reports"),
            "Short guide to the report tree.",
        ),
        (
            "Canonical reports",
            "reports/canonical/*",
            _family_count(records, "reports/canonical"),
            "Current final summary, model summary, and coaches notebook.",
        ),
        (
            "Tournament rankings",
            "reports/ranking/*",
            _family_count(records, "reports/ranking"),
            "Qatar 2022 outfield, 300-minute, goalkeeper, audit, and methodology artifacts.",
        ),
        (
            "Per-team tournament rankings",
            "reports/ranking/by_team/<TEAM>.csv",
            _family_count(records, "reports/ranking/by_team"),
            "Complete player ranking table for each of the 32 national teams.",
        ),
        (
            "Archived legacy rankings",
            "reports/ranking/legacy/*",
            _family_count(records, "reports/ranking/legacy"),
            "Pre-v2 tables retained for before/after reproducibility.",
        ),
        (
            "Canonical report data",
            "reports/canonical/data/*",
            _family_count(records, "reports/canonical/data"),
            "Team metrics and defensive-disruption tables supporting reports.",
        ),
        (
            "Formatted final report",
            "reports/docs/final_summary.docx",
            _family_count(records, "reports/docs"),
            "Word edition of the final tournament report.",
        ),
        (
            "Player profiles",
            "reports/player_profiles/<player-slug>-<player-id>.md",
            _family_count(records, "reports/player_profiles"),
            "One human-readable role and valuation profile per player.",
        ),
        (
            "Starter report pairs",
            "reports/starters/<TEAM>/<player-id>_starter_report.{md,json}",
            _family_count(records, "reports/starters", recursive=True),
            "Markdown and JSON player reports organized by national-team code.",
        ),
        (
            "Team coaching report pairs",
            "reports/teams/<TEAM>_team_coaching_report.{md,json}",
            _family_count(records, "reports/teams"),
            "Human-readable and structured coaching reports for 32 teams.",
        ),
        (
            "Team profiles",
            "reports/team_profiles/<team-name>.md",
            _family_count(records, "reports/team_profiles"),
            "Concise threat, defensive, resistance, and squad-rating profiles.",
        ),
        (
            "Report figures",
            "reports/v5_figures/*",
            _family_count(records, "reports/v5_figures"),
            "Current ranking and ElasticNet coefficient figures.",
        ),
        (
            "Player heatmaps",
            "reports/visuals/heatmaps/<player-slug>-<player-id>.svg",
            _family_count(records, "reports/visuals/heatmaps"),
            "One scalable spatial-event heatmap per player.",
        ),
        (
            "Simulation outputs",
            "simulations/*",
            _family_count(records, "simulations"),
            "Tactical-style, substitution, suppression, and out-of-fold simulations.",
        ),
    ]
    covered = sum(row[2] for row in families)
    if covered != len(records):
        raise RuntimeError(
            f"Dictionary families cover {covered} of {len(records)} artifacts"
        )
    lines = [
        "# Results dictionary",
        "",
        "A compact directory of every result artifact family. Repeated player and "
        "team files are represented once by their filename pattern.",
        "",
        "## Fast lookup",
        "",
        "| If you need… | Go to |",
        "|---|---|",
        "| Primary 300+-minute rankings | [`reports/ranking/global_rankings_outfield_300min.csv`](../reports/ranking/global_rankings_outfield_300min.csv) |",
        "| Full-cohort player table | [`reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) |",
        "| Searchable JSON rankings | [`reports/ranking/player_rankings.json`](../reports/ranking/player_rankings.json) |",
        "| One player’s profile | [`reports/player_profiles/`](../reports/player_profiles/) |",
        "| One player’s heatmap | [`reports/visuals/heatmaps/`](../reports/visuals/heatmaps/) |",
        "| One team’s profile | [`reports/team_profiles/`](../reports/team_profiles/) |",
        "| Full team coaching report | [`reports/teams/`](../reports/teams/) |",
        "| Tournament final summary | [`reports/canonical/final_summary.md`](../reports/canonical/final_summary.md) |",
        "| Model metrics and gate result | [`reports/canonical/model_summary.md`](../reports/canonical/model_summary.md) |",
        "| Coach-facing tactical notes | [`reports/canonical/coaches_notebook.md`](../reports/canonical/coaches_notebook.md) |",
        "| Validation evidence | [`diagnostics/`](../diagnostics/) and [`audit/`](../audit/) |",
        "| Run provenance/configuration | [`metadata/`](../metadata/) |",
        "| Tactical simulations | [`simulations/`](../simulations/) |",
        "| Exact filename search | [`file_dictionary.csv`](file_dictionary.csv) |",
        "",
        "## Complete artifact-family dictionary",
        "",
        "| Artifact family | Path or filename pattern | Files | Information contained |",
        "|---|---|---:|---|",
    ]
    for name, pattern, count, information in families:
        lines.append(
            f"| {name} | `results/{pattern}` | {count:,} | {information} |"
        )
    lines.extend(
        [
            "",
            f"**Coverage:** {covered:,} of {len(records):,} result artifacts.",
            "",
            "## Which version wins?",
            "",
            "Use `results/reports/ranking/` for active player rankings and "
            "`results/reports/canonical/` for active narrative summaries. "
            "`MIscellaneous/` may contain older or exploratory leaderboards and "
            "must not override canonical rankings or validation conclusions.",
            "",
            "For a literal one-row-per-file lookup, filter `file_dictionary.csv` "
            "by `path`, `filename`, `folder`, or `information`. The JSON edition "
            "contains the same dictionary for programmatic use.",
            "",
        ]
    )
    (DOCUMENTATION_ROOT / "results-dictionary.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_profiles_dictionary(records: list[dict[str, Any]]) -> None:
    """Write the profile/report location dictionary."""

    starters_root = RESULTS_ROOT / "reports" / "starters"
    team_codes = (
        sorted(path.name for path in starters_root.iterdir() if path.is_dir())
        if starters_root.is_dir()
        else sorted(
            {
                path.name.split("_", maxsplit=1)[0]
                for path in (RESULTS_ROOT / "reports" / "teams").glob(
                    "*_team_coaching_report.md"
                )
            }
        )
    )
    player_profiles = _family_count(records, "reports/player_profiles")
    starter_files = _family_count(records, "reports/starters", recursive=True)
    heatmaps = _family_count(records, "reports/visuals/heatmaps")
    team_profiles = _family_count(records, "reports/team_profiles")
    team_reports = _family_count(records, "reports/teams")
    lines = [
        "# Reports - Profiles",
        "",
        "Dictionary for locating player profiles, starter reports, heatmaps, and "
        "team reports. Collections are described by pattern rather than by one "
        "summary per file.",
        "",
        "## Profile locations",
        "",
        "| What you want | Location/pattern | Count | Format | What it contains |",
        "|---|---|---:|---|---|",
        f"| Player profile | `results/reports/player_profiles/<player-slug>-<player-id>.md` | {player_profiles:,} | Markdown | Identity, team, position, functional/probabilistic role, rating components, evidence coverage, and interpretation. |",
        f"| Player heatmap | `results/reports/visuals/heatmaps/<player-slug>-<player-id>.svg` | {heatmaps:,} | SVG | Spatial density of the player’s recorded event locations. |",
        f"| Starter report | `results/reports/starters/<TEAM>/<player-id>_starter_report.md` | {starter_files // 2:,} | Markdown | Human-readable player match/role report organized by team. |",
        f"| Starter data | `results/reports/starters/<TEAM>/<player-id>_starter_report.json` | {starter_files // 2:,} | JSON | Structured version of the same starter report. |",
        f"| Team profile | `results/reports/team_profiles/<team-name>.md` | {team_profiles:,} | Markdown | Threat creation, compactness, pressure resistance, and squad ratings. |",
        f"| Team coaching report | `results/reports/teams/<TEAM>_team_coaching_report.md` | {team_reports // 2:,} | Markdown | Full coach-facing tactical and player report. |",
        f"| Team coaching data | `results/reports/teams/<TEAM>_team_coaching_report.json` | {team_reports // 2:,} | JSON | Structured coaching-report content for downstream use. |",
        "| Tournament player/team summary | `results/reports/canonical/final_summary.md` | 1 | Markdown | General player summary, all-team overview, and each team’s top five players. |",
        "| Formatted final report | `results/reports/docs/final_summary.docx` | 1 | Word | Office-document edition of the final report. |",
        "",
        "## Team-code dictionary",
        "",
        "`<TEAM>` is one of: " + ", ".join(f"`{code}`" for code in team_codes) + ".",
        "",
        "## Finding a person",
        "",
        "1. Search `results/reports/player_profiles/` by surname or StatsBomb player ID.",
        "2. Use the same slug/ID in `results/reports/visuals/heatmaps/` for the spatial view.",
        "3. For JSON, locate the player ID under `results/reports/starters/<TEAM>/`.",
        "4. If the filename is uncertain, search [`file_dictionary.csv`](file_dictionary.csv) by `filename` or `path`.",
        "",
        "Example: Christian Pulisic’s profile is "
        "[`reports/player_profiles/christian-pulisic-8246.md`](../reports/player_profiles/christian-pulisic-8246.md).",
        "",
    ]
    (DOCUMENTATION_ROOT / "reports-profiles.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_rankings_dictionary(records: list[dict[str, Any]]) -> None:
    """Write the rankings location and field dictionary."""

    ranking_csv = next(
        record
        for record in records
        if record["path"] == "reports/ranking/player_rankings.csv"
    )
    lines = [
        "# Reports - Rankings",
        "",
        "Dictionary for locating and interpreting the active player, goalkeeper, "
        "position, role, and team rankings.",
        "",
        "## Active ranking files",
        "",
        "| Ranking resource | Location | Use |",
        "|---|---|---|",
        f"| Complete ranking table | [`results/reports/ranking/player_rankings.csv`](../reports/ranking/player_rankings.csv) | Spreadsheet/dataframe source; {ranking_csv['format_details']}. |",
        "| Global outfield ranking | [`results/reports/ranking/global_rankings_outfield.csv`](../reports/ranking/global_rankings_outfield.csv) | All eligible outfield players ordered by `global_rank_v2`. |",
        "| Primary 300+-minute ranking | [`results/reports/ranking/global_rankings_outfield_300min.csv`](../reports/ranking/global_rankings_outfield_300min.csv) | Filters exclusively on Qatar 2022 `minutes_played >= 300`. |",
        "| Goalkeeper ranking | [`results/reports/ranking/goalkeeper_rankings.csv`](../reports/ranking/goalkeeper_rankings.csv) | Separate non-comparable rating for exactly one team-main goalkeeper per nation. |",
        "| Complete ranking JSON | [`results/reports/ranking/player_rankings.json`](../reports/ranking/player_rankings.json) | Same records for applications and APIs. |",
        "| Ranking methodology | [`results/reports/ranking/ranking_methodology.md`](../reports/ranking/ranking_methodology.md) | Position-aware weights, normalization, sample treatment, and role logic. |",
        "| Ranking audit | [`results/reports/ranking/ranking_audit.md`](../reports/ranking/ranking_audit.md) | Before/after comparisons and eyes-test results. |",
        "| Human-readable leaders | [`results/reports/canonical/final_summary.md`](../reports/canonical/final_summary.md) | Overall, position-group, movement, team, and top-five summaries. |",
        "| Coach-facing leaders | [`results/reports/canonical/coaches_notebook.md`](../reports/canonical/coaches_notebook.md) | Pressing, networks, line breaking, spatial advantages, and goalkeeper leaders. |",
        "",
        "## Ranking-field dictionary",
        "",
        "| Field | Meaning |",
        "|---|---|",
        "| `position_group_360` | Formal tournament-usage group: GK, CB, FB, DM, CM, AM, or FW. |",
        "| `global_rank_v2` | Position-aware global outfield rank; goalkeepers are blank. |",
        "| `gk_rank_v2` | Rank among the 32 team-main goalkeepers; backups are blank. |",
        "| `is_main_goalkeeper` | `true` only for the goalkeeper with the most Qatar 2022 minutes on that team. |",
        "| `position_rank_v2` | Rank within `position_group_360`. |",
        "| `role_rank_v2` | Rank within the coherent functional role. |",
        "| `team_rank_v2` | Outfield rank within the 2022 national team. |",
        "| `final_player_rating_v2` / `gk_rating_v2` | Separate 0–1 outfield and goalkeeper tournament scores. |",
        "| `global_rank` | Global outfield rank. In the 300+ file this is recalculated only among eligible outfield players; goalkeepers are blank. |",
        "| `goalkeeper_rank` / `primary_goalkeeper_rank` | Separate goalkeeper-only rank. |",
        "| `position_rank` | Rank within the broad position group. |",
        "| `role_rank` | Rank among players sharing the functional role. |",
        "| `team_rank` | Rank within the player’s national team. |",
        "| `final_player_rating` | Reliability-adjusted final score used for ordering. |",
        "| `RankingStatus` | Outfield ranking eligibility/status explanation. |",
        "| `GKRankingStatus` | Goalkeeper ranking eligibility/status explanation. |",
        "",
        "## Ranking figures",
        "",
        "| Figure | Location |",
        "|---|---|",
        "| Global outfield ranking | [`v5_global_outfield_rankings.png`](../reports/v5_figures/v5_global_outfield_rankings.png) |",
        "| Goalkeeper-only ranking | [`v5_goalkeeper_rankings.png`](../reports/v5_figures/v5_goalkeeper_rankings.png) |",
        "| France squad ranking | [`v5_france_team_rankings.png`](../reports/v5_figures/v5_france_team_rankings.png) |",
        "| Learned valuation coefficients | [`v5_elasticnet_coefficients.png`](../reports/v5_figures/v5_elasticnet_coefficients.png) |",
        "",
        "## Other leaderboards",
        "",
        "`results/MIscellaneous/` contains coaching, recommendation, transition, "
        "and xG model leaderboards. These evaluate auxiliary models and are not "
        "the active player ranking. Use the active CSV above for player "
        "ordering.",
        "",
        "To find any ranking-related filename, filter "
        "[`file_dictionary.csv`](file_dictionary.csv) for `rank` or `leaderboard`.",
        "",
    ]
    (DOCUMENTATION_ROOT / "reports-rankings.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def _write_compact_index(records: list[dict[str, Any]]) -> None:
    """Write the condensed documentation landing page."""

    lines = [
        "# Results documentation dictionary",
        "",
        "Use these three compact dictionaries instead of individual folder summaries:",
        "",
        "- [`Results Dictionary`](results-dictionary.md) — where every artifact family lives.",
        "- [`Reports - Profiles`](reports-profiles.md) — player profiles, heatmaps, starter reports, team profiles, and coaching reports.",
        "- [`Reports - Rankings`](reports-rankings.md) — global, goalkeeper, position, role, and team rankings.",
        "",
        "## Exact-file search",
        "",
        f"The results tree currently contains **{len(records):,} files**. Use "
        "[`file_dictionary.csv`](file_dictionary.csv) for spreadsheet search or "
        "[`file_dictionary.json`](file_dictionary.json) for programmatic search. "
        "These are indexes only; the three Markdown documents above are the "
        "human-readable dictionary.",
        "",
        "## Canonical rule",
        "",
        "Use `results/reports/ranking/` for active player ordering and "
        "`results/reports/canonical/` for narrative summaries. A validation "
        "task may explicitly call for an out-of-fold artifact from `audit/` "
        "or `diagnostics/`.",
        "",
        "Rebuild after result changes with "
        "`python results/documentation/generate_documentation.py`.",
        "",
    ]
    (DOCUMENTATION_ROOT / "README.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def main() -> None:
    """Generate the condensed results dictionaries."""

    source_files = sorted(
        (
            path
            for path in RESULTS_ROOT.rglob("*")
            if path.is_file() and DOCUMENTATION_ROOT not in path.parents
        ),
        key=lambda path: _normalise(path).lower(),
    )
    records = [_file_metadata(path) for path in source_files]
    _write_catalogs(records)
    _write_results_dictionary(records)
    _write_profiles_dictionary(records)
    _write_rankings_dictionary(records)
    _write_compact_index(records)
    print(
        json.dumps(
            {
                "artifacts_documented": len(records),
                "dictionary_reports": 3,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
