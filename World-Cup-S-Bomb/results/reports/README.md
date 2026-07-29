# World-Cup-S-Bomb Output Directory Index

This directory contains the stable report paths for the World-Cup-S-Bomb
analysis. Versioned aliases and historical compiled outputs have been removed;
the paths below are the current source of truth.

## Directory structure

```text
results/
├── reports/
│   ├── canonical/                 # Narrative summaries and supporting data
│   │   └── data/                  # Supporting team-level datasets
│   ├── ranking/                   # Qatar 2022 ranking tables, audit, and methodology
│   │   └── by_team/               # One complete CSV per national team
│   ├── player_profiles/           # 593 player profiles (Markdown)
│   ├── team_profiles/             # 32 statistical team profiles (Markdown)
│   ├── teams/                     # 32 tactical reports (Markdown + JSON)
│   ├── visuals/
│   │   └── heatmaps/              # 593 player heatmaps (SVG)
│   └── docs/                      # Human-readable document exports
├── diagnostics/                   # Validation metrics and audit artifacts
└── metadata/                      # Artifact, pipeline, and cleanup manifests
```

## Ranking deliverables

- [Global outfield rankings](ranking/global_rankings_outfield.csv) and
  [300-minute view](ranking/global_rankings_outfield_300min.csv): formal
  360-position-aware Qatar 2022 rankings.
- [Goalkeeper rankings](ranking/goalkeeper_rankings.csv): separate goalkeeper
  ratings that are not mixed with outfield scores.
- [Complete ranking CSV](ranking/player_rankings.csv) and
  [JSON](ranking/player_rankings.json): all 593 rated players with legacy and
  v2 fields.
- [Per-team rankings](ranking/by_team/): complete CSVs for all 32 nations.
- [Methodology](ranking/ranking_methodology.md) and
  [eyes-test audit](ranking/ranking_audit.md): formula, weights, position/role
  logic, and before/after checks.

## Canonical narrative deliverables

- [Final summary](canonical/final_summary.md): tournament findings and rating
  movements.
- [Model summary](canonical/model_summary.md) and
  [model summary JSON](canonical/model_summary.json): model methodology,
  validation state, and diagnostics.
- [Coaches notebook](canonical/coaches_notebook.md): passing, pressing,
  spatial, and line-breaking leaders.
- [Team metrics](canonical/data/team_metrics_v2.csv) and
  [defense disruption](canonical/data/defense_disruption.csv): supporting
  canonical datasets.
- [Formatted final summary](docs/final_summary.docx): Word export of the final
  report.

## Profiles, tactical reports, and visuals

- [Player profiles](player_profiles/): 593 individual Markdown reports.
- [Team profiles](team_profiles/): 32 statistical Markdown reports.
- [Tactical team reports](teams/): 32 Markdown reports and 32 matching JSON
  records.
- [Player heatmaps](visuals/heatmaps/): 593 SVG files with globally unique
  player identifiers.
- [Supplementary V5 figures](v5_figures/): retained PNG ranking and coefficient
  plots.

## Validation and provenance

- [Diagnostics](../diagnostics/): validation comparisons, uncertainty outputs,
  model audit trails, and retained V2 diagnostic context.
- [Artifact manifest](../metadata/artifact_manifest.json): portable,
  deduplicated paths for retained generated artifacts.
- [Pipeline manifest](../metadata/pipeline_manifest.json): pipeline and model
  provenance.
- [Cleanup audit](../metadata/cleanup_audit_log.json): pre-change hashes and
  the complete move/delete plan used for this reorganization.
