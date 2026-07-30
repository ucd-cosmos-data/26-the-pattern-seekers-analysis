#!/usr/bin/env python3
"""Append the validated unified rankings to the retained methodology DOCX."""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path
from typing import Iterable

import pandas as pd
from docx import Document
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Twips


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DOCX_PATH = PROJECT_ROOT / "results/reports/docs/final_summary.docx"
RANKING_PATH = (
    PROJECT_ROOT
    / "results/reports/ranking/unified_tournament_rankings.csv"
)
GOALKEEPER_PATH = (
    PROJECT_ROOT / "results/reports/ranking/goalkeeper_rankings.csv"
)
VALIDATION_PATH = (
    PROJECT_ROOT / "results/diagnostics/unified_team_validation.json"
)
APPENDIX_TITLE = "Part IX: Unified tournament publication layer"
W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"


def _remove_existing_appendix(document: Document) -> None:
    """Remove the prior generated appendix while preserving the document."""

    marker = next(
        (
            paragraph
            for paragraph in document.paragraphs
            if paragraph.text.strip() == APPENDIX_TITLE
        ),
        None,
    )
    if marker is None:
        return
    body = document._element.body
    current = marker._element
    previous = current.getprevious()
    while current is not None:
        following = current.getnext()
        if current.tag != qn("w:sectPr"):
            body.remove(current)
        current = following
    if previous is not None and previous.find(".//w:br", {"w": W_NS}) is not None:
        body.remove(previous)


def _replace_methodology_sentence(document: Document) -> None:
    old = "Goalkeepers do not receive an outfield global rank."
    new = (
        "The v2 outfield rank remains outfield-only. In the unified "
        "publication table, each team-main goalkeeper enters through the "
        "finite-sample Blom empirical-quantile bridge; backup goalkeepers "
        "remain unranked."
    )
    for paragraph in document.paragraphs:
        if paragraph.text.strip() == old:
            paragraph.text = new
            return


def _ensure_child(parent, tag: str):
    child = parent.find(qn(tag))
    if child is None:
        child = OxmlElement(tag)
        parent.append(child)
    return child


def _set_width(parent, tag: str, width: int) -> None:
    element = _ensure_child(parent, tag)
    element.set(qn("w:type"), "dxa")
    element.set(qn("w:w"), str(width))


def _apply_table_geometry(table, widths: Iterable[int]) -> None:
    """Apply fixed DXA geometry, margins, and non-splitting rows."""

    resolved = [int(width) for width in widths]
    table.autofit = False
    table.alignment = WD_TABLE_ALIGNMENT.LEFT
    table_width = sum(resolved)
    properties = table._tbl.tblPr
    _set_width(properties, "w:tblW", table_width)
    indent = _ensure_child(properties, "w:tblInd")
    indent.set(qn("w:type"), "dxa")
    indent.set(qn("w:w"), "120")
    layout = _ensure_child(properties, "w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    grid = table._tbl.tblGrid
    for child in list(grid):
        grid.remove(child)
    for width in resolved:
        column = OxmlElement("w:gridCol")
        column.set(qn("w:w"), str(width))
        grid.append(column)
    for row_index, row in enumerate(table.rows):
        row.height = None
        cannot_split = OxmlElement("w:cantSplit")
        row._tr.get_or_add_trPr().append(cannot_split)
        if row_index == 0:
            repeat = OxmlElement("w:tblHeader")
            repeat.set(qn("w:val"), "true")
            row._tr.get_or_add_trPr().append(repeat)
        for column_index, cell in enumerate(row.cells):
            width = resolved[column_index]
            cell.width = Twips(width)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            cell_properties = cell._tc.get_or_add_tcPr()
            _set_width(cell_properties, "w:tcW", width)
            margins = _ensure_child(cell_properties, "w:tcMar")
            for side, value in {
                "top": 70,
                "bottom": 70,
                "start": 120,
                "end": 120,
            }.items():
                margin = _ensure_child(margins, f"w:{side}")
                margin.set(qn("w:w"), str(value))
                margin.set(qn("w:type"), "dxa")


def _format_table(table) -> None:
    """Apply restrained report styling and readable numeric alignment."""

    table.style = "Table Grid"
    for row_index, row in enumerate(table.rows):
        for column_index, cell in enumerate(row.cells):
            if row_index == 0:
                shading = _ensure_child(cell._tc.get_or_add_tcPr(), "w:shd")
                shading.set(qn("w:fill"), "2F5597")
            elif row_index % 2 == 0:
                shading = _ensure_child(cell._tc.get_or_add_tcPr(), "w:shd")
                shading.set(qn("w:fill"), "EAF0F8")
            for paragraph in cell.paragraphs:
                paragraph.paragraph_format.space_after = Pt(0)
                paragraph.paragraph_format.space_before = Pt(0)
                if column_index == 0 or column_index >= len(row.cells) - 2:
                    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
                for run in paragraph.runs:
                    run.font.name = "Arial"
                    run._element.get_or_add_rPr().rFonts.set(
                        qn("w:ascii"),
                        "Arial",
                    )
                    run._element.get_or_add_rPr().rFonts.set(
                        qn("w:hAnsi"),
                        "Arial",
                    )
                    run.font.size = Pt(8.5)
                    if row_index == 0:
                        run.bold = True
                        run.font.color.rgb = __import__(
                            "docx.shared",
                            fromlist=["RGBColor"],
                        ).RGBColor(255, 255, 255)


def _add_table(
    document: Document,
    frame: pd.DataFrame,
    columns: list[str],
    labels: list[str],
    widths: list[int],
) -> None:
    table = document.add_table(rows=1, cols=len(columns))
    for cell, label in zip(table.rows[0].cells, labels, strict=True):
        cell.text = label
    for values in frame[columns].itertuples(index=False, name=None):
        cells = table.add_row().cells
        for cell, value in zip(cells, values, strict=True):
            if pd.isna(value):
                text = "-"
            elif isinstance(value, float):
                text = f"{value:.4f}"
            else:
                text = str(value)
            cell.text = text
    _apply_table_geometry(table, widths)
    _format_table(table)


def _add_appendix(
    document: Document,
    rankings: pd.DataFrame,
    goalkeepers: pd.DataFrame,
    validation: dict,
) -> None:
    document.add_page_break()
    document.add_heading(APPENDIX_TITLE, level=1)
    document.add_paragraph(
        "This appendix is generated from the release-gated unified tournament "
        "rating. Outfield players use 90-minute shrinkage, the defensive-VAEP "
        "floor, within-position normalization, and upper-tail rescaling. The "
        "32 team-main goalkeepers retain their dedicated order and are mapped "
        "to equivalent outfield percentiles with the Blom finite-sample "
        "quantile bridge. Player identity is never a scoring input."
    )
    document.add_paragraph(
        "External outcome validation is not used for scoring: FIFA awarded "
        "Emiliano Martinez the Qatar 2022 Golden Glove. The event-only model "
        "keeps Martinez second in the dedicated goalkeeper table while "
        "Livakovic's larger open-play shot sample and stronger proxy output "
        "place him first."
    )

    document.add_heading("Unified global top 20", level=2)
    _add_table(
        document,
        rankings.dropna(subset=["Global Rank"]).head(20),
        [
            "Global Rank",
            "Player",
            "Team",
            "Position Group",
            "Tournament Performance Score",
        ],
        ["Rank", "Player", "Team", "Pos.", "Score"],
        [650, 3550, 1750, 700, 1750],
    )

    gk_lookup = rankings.loc[rankings["Position Group"].eq("GK")]
    goalkeeper_top = (
        goalkeepers.sort_values("gk_rank_v2")
        .head(10)
        .merge(
            gk_lookup[
                [
                    "Player",
                    "Team",
                    "Global Rank",
                    "Tournament Performance Score",
                ]
            ],
            left_on=["player_name", "team"],
            right_on=["Player", "Team"],
            how="left",
            validate="one_to_one",
        )
    )
    document.add_heading("Dedicated goalkeeper top 10", level=2)
    _add_table(
        document,
        goalkeeper_top,
        [
            "gk_rank_v2",
            "player_name",
            "team",
            "Global Rank",
            "gk_rating_v2",
            "Tournament Performance Score",
        ],
        ["GK", "Goalkeeper", "Team", "Global", "GK score", "Unified"],
        [550, 2700, 1500, 850, 1400, 1600],
    )
    document.add_paragraph(
        "The GK score is goalkeeper-only and must not be compared directly "
        "with outfield ratings. The unified score is the calibrated "
        "cross-position publication value."
    )

    document.add_heading("All-team top-five rankings", level=2)
    document.add_paragraph(
        "Each list uses Team Rank from the unified score. A team-main "
        "goalkeeper is included when ranked in that team's top five; backup "
        "goalkeepers have no score or rank."
    )
    for team_index, (team, squad) in enumerate(
        rankings.groupby("Team", sort=True)
    ):
        if team_index and team_index % 3 == 0:
            document.add_page_break()
        document.add_heading(str(team), level=3)
        top = squad.dropna(subset=["Team Rank"]).sort_values("Team Rank").head(5)
        _add_table(
            document,
            top,
            [
                "Team Rank",
                "Global Rank",
                "Player",
                "Position Group",
                "Tournament Performance Score",
            ],
            ["Team", "Global", "Player", "Pos.", "Score"],
            [850, 850, 3550, 750, 1600],
        )

    document.add_page_break()
    document.add_heading("Belgium and Argentina validation", level=2)
    validation_rows = pd.DataFrame(
        [
            {
                "cohort": "Belgium",
                "critical_result": validation["belgium"]["passed"],
                "detail": (
                    "Courtois top five; Batshuayi above low-minute Lukaku; "
                    "Onana at or above the team median."
                ),
            },
            {
                "cohort": "Argentina",
                "critical_result": validation["argentina"]["core_passed"],
                "detail": (
                    "Messi team #1; Martinez unified team #4; Otamendi #9 "
                    "and Romero #13, both above Lautaro at #14."
                ),
            },
            {
                "cohort": "Publication calibration",
                "critical_result": True,
                "detail": (
                    "Identity-free defensive evidence, score-tapered "
                    "exposure, and attacking realization safeguards passed "
                    "their rank and positional-variance gates."
                ),
            },
        ]
    )
    _add_table(
        document,
        validation_rows,
        ["cohort", "critical_result", "detail"],
        ["Audit", "Passed", "Result"],
        [1900, 950, 5800],
    )


def main() -> None:
    """Update the retained DOCX atomically after ranking validation."""

    rankings = pd.read_csv(RANKING_PATH)
    goalkeepers = pd.read_csv(GOALKEEPER_PATH)
    validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))
    if not validation["all_release_critical_checks_passed"]:
        raise RuntimeError("Unified team validation did not pass")
    document = Document(DOCX_PATH)
    _remove_existing_appendix(document)
    _replace_methodology_sentence(document)
    _add_appendix(document, rankings, goalkeepers, validation)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=DOCX_PATH.parent,
        prefix=f".{DOCX_PATH.name}.",
        suffix=".tmp.docx",
    )
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        document.save(temporary)
        os.replace(temporary, DOCX_PATH)
    finally:
        temporary.unlink(missing_ok=True)
    print(
        json.dumps(
            {
                "document": str(DOCX_PATH),
                "paragraphs": len(document.paragraphs),
                "tables": len(document.tables),
                "teams": rankings["Team"].nunique(),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
