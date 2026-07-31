#!/usr/bin/env python3
"""Compile detailed reports into exactly 64 team-level Markdown packets."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TEAM_REPORTS = PROJECT_ROOT / "results/reports/teams"
DEFAULT_PLAYER_REPORTS = PROJECT_ROOT / "results/reports/starters"
DEFAULT_OUTPUT = PROJECT_ROOT / "results/reports/compiled"
TEAM_REPORT_PATTERN = re.compile(r"^([A-Z]{3})_team_coaching_report\.md$")


def compile_report_packets(
    team_reports: Path,
    player_reports: Path,
    output: Path,
) -> dict[str, int]:
    """Copy 32 team reports and concatenate every player report by team."""

    team_sources = sorted(team_reports.glob("*_team_coaching_report.md"))
    if len(team_sources) != 32:
        raise ValueError(f"Expected 32 team reports, found {len(team_sources)}")

    output.mkdir(parents=True, exist_ok=True)
    for existing in output.glob("*.md"):
        existing.unlink()

    compiled_player_count = 0
    player_packet_count = 0
    use_boundary = """## Coaching-use boundary

Use this report to prioritize video review, frame tactical questions, and compare
scenario sensitivities. Do not use it as a standalone selection mandate or a
causal estimate. The stored coaching bundle was corrupted, so simulations use a
regularized empirical hurdle fallback; tracking-derived tackles and recovery
runs are represented by documented event-data proxies. Confirm recommendations
against video, training data, medical context, and opponent-specific scouting.
"""
    for team_source in team_sources:
        match = TEAM_REPORT_PATTERN.match(team_source.name)
        if match is None:
            raise ValueError(f"Unexpected team report filename: {team_source.name}")
        team_code = match.group(1)
        team_text = team_source.read_text(encoding="utf-8").rstrip()
        (output / team_source.name).write_text(
            team_text + "\n\n" + use_boundary.rstrip() + "\n",
            encoding="utf-8",
        )

        player_sources = sorted(
            (player_reports / team_code).glob("*_starter_report.md"),
            key=lambda path: int(path.name.split("_", maxsplit=1)[0]),
        )
        if not player_sources:
            raise ValueError(f"No player reports found for {team_code}")
        sections = [
            f"# {team_code} — Complete Player Report Collection",
            "",
            f"- Included player reports: {len(player_sources)}",
            "- Compilation policy: complete source reports, no omitted sections.",
            "",
            use_boundary.rstrip(),
            "",
        ]
        for position, player_source in enumerate(player_sources, start=1):
            source_text = player_source.read_text(encoding="utf-8").strip()
            sections.extend(
                [
                    "---",
                    "",
                    f"<!-- PLAYER_REPORT {position}: {player_source.name} -->",
                    "",
                    source_text,
                    "",
                ]
            )
        packet = output / f"{team_code}_compiled_player_reports.md"
        packet.write_text("\n".join(sections).rstrip() + "\n", encoding="utf-8")
        compiled_player_count += len(player_sources)
        player_packet_count += 1

    markdown_files = list(output.glob("*.md"))
    team_outputs = list(output.glob("*_team_coaching_report.md"))
    player_outputs = list(output.glob("*_compiled_player_reports.md"))
    checks = {
        "markdown_files": len(markdown_files),
        "team_reports": len(team_outputs),
        "compiled_player_reports": len(player_outputs),
        "compiled_player_sections": compiled_player_count,
    }
    if checks != {
        "markdown_files": 64,
        "team_reports": 32,
        "compiled_player_reports": 32,
        "compiled_player_sections": 342,
    }:
        raise RuntimeError(f"Compiled report validation failed: {checks}")
    return checks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--team-reports", type=Path, default=DEFAULT_TEAM_REPORTS)
    parser.add_argument(
        "--player-reports", type=Path, default=DEFAULT_PLAYER_REPORTS
    )
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    checks = compile_report_packets(
        args.team_reports,
        args.player_reports,
        args.output,
    )
    print(
        f"Wrote {checks['markdown_files']} compiled delivery files to "
        f"{args.output}"
    )
    print(
        f"Included all {checks['compiled_player_sections']} player reports "
        "without truncation"
    )


if __name__ == "__main__":
    main()
