# Results documentation

This directory is the comprehensive map of every artifact under `results/`. Generated documentation files are excluded from the inventory to avoid self-referential counts.

## Coverage

- Documented artifacts: **2,579**
- Documented folders: **50**
- File formats: `.csv` (42), `.docx` (1), `.json` (643), `.md` (1,274), `.parquet` (6), `.pdf` (1), `.png` (16), `.pptx` (1), `.svg` (593), `[none]` (2)
- Every artifact has its path, format, byte size, scale, internal structure or schema, and an explanation of the information it contains.

## How to navigate

- Start with the folder table below for a human-readable explanation.
- Use [`file_catalog.csv`](file_catalog.csv) for filtering in a spreadsheet or dataframe.
- Use [`file_catalog.json`](file_catalog.json) for programmatic lookup.
- Rebuild these documents with `python results/documentation/generate_documentation.py` after outputs change.

## Folder catalog

| Results folder | Direct files | Purpose | Detailed guide |
|---|---:|---|---|
| `results/` | 0 | Top-level result artifacts and entry points produced by the World Cup analytics pipeline. | [Open guide](folders/results-root.md) |
| `results/audit/` | 6 | Observed-versus-expected comparison tables used to audit possession predictions, team aggregates, and out-of-fold behavior. | [Open guide](folders/audit.md) |
| `results/diagnostics/` | 17 | Model evaluation, calibration, feature-importance, cluster-quality, and validation diagnostics. | [Open guide](folders/diagnostics.md) |
| `results/figures/` | 14 | Publication-ready charts and the technical onboarding presentation. | [Open guide](folders/figures.md) |
| `results/metadata/` | 5 | Machine-readable run metadata, feature definitions, provenance, and model configuration snapshots. | [Open guide](folders/metadata.md) |
| `results/MIscellaneous/` | 49 | Supporting tactical summaries, legacy exploratory outputs, and the compact tournament PDF that do not belong to the canonical release. | [Open guide](folders/miscellaneous.md) |
| `results/reports/` | 1 | Human- and machine-readable player, team, coaching, and tournament reports. | [Open guide](folders/reports.md) |
| `results/simulations/` | 6 | Tactical-style and substitution simulation outputs, including out-of-fold variants and suppression audits. | [Open guide](folders/simulations.md) |
| `results/reports/canonical/` | 6 | Canonical release artifacts: rankings, final summary, model summary, coaches notebook, and their data exports. | [Open guide](folders/reports-canonical.md) |
| `results/reports/docs/` | 1 | Office-document editions of final reporting artifacts. | [Open guide](folders/reports-docs.md) |
| `results/reports/player_profiles/` | 593 | One Markdown scouting and valuation profile per tournament player. | [Open guide](folders/reports-player-profiles.md) |
| `results/reports/starters/` | 0 | Country-code subfolders containing paired Markdown and JSON reports for each recorded starter. | [Open guide](folders/reports-starters.md) |
| `results/reports/team_profiles/` | 32 | Concise Markdown team profiles with threat, defensive, resistance, and squad-rating summaries. | [Open guide](folders/reports-team-profiles.md) |
| `results/reports/teams/` | 64 | Paired Markdown and JSON coaching reports for all 32 national teams. | [Open guide](folders/reports-teams.md) |
| `results/reports/v5_figures/` | 4 | V5 ranking and ElasticNet diagnostic figures embedded in reports. | [Open guide](folders/reports-v5-figures.md) |
| `results/reports/visuals/` | 0 | Container for report-linked visual assets. | [Open guide](folders/reports-visuals.md) |
| `results/reports/canonical/data/` | 2 | Canonical tabular data backing the published reports. | [Open guide](folders/reports-canonical-data.md) |
| `results/reports/starters/ARG/` | 40 | Paired Markdown and JSON starter reports for team code ARG. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-arg.md) |
| `results/reports/starters/AUS/` | 34 | Paired Markdown and JSON starter reports for team code AUS. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-aus.md) |
| `results/reports/starters/BEL/` | 34 | Paired Markdown and JSON starter reports for team code BEL. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-bel.md) |
| `results/reports/starters/BRA/` | 50 | Paired Markdown and JSON starter reports for team code BRA. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-bra.md) |
| `results/reports/starters/CAN/` | 32 | Paired Markdown and JSON starter reports for team code CAN. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-can.md) |
| `results/reports/starters/CMR/` | 36 | Paired Markdown and JSON starter reports for team code CMR. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-cmr.md) |
| `results/reports/starters/CRC/` | 34 | Paired Markdown and JSON starter reports for team code CRC. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-crc.md) |
| `results/reports/starters/CRO/` | 40 | Paired Markdown and JSON starter reports for team code CRO. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-cro.md) |
| `results/reports/starters/DEN/` | 36 | Paired Markdown and JSON starter reports for team code DEN. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-den.md) |
| `results/reports/starters/ECU/` | 32 | Paired Markdown and JSON starter reports for team code ECU. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-ecu.md) |
| `results/reports/starters/ENG/` | 38 | Paired Markdown and JSON starter reports for team code ENG. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-eng.md) |
| `results/reports/starters/ESP/` | 40 | Paired Markdown and JSON starter reports for team code ESP. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-esp.md) |
| `results/reports/starters/FRA/` | 44 | Paired Markdown and JSON starter reports for team code FRA. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-fra.md) |
| `results/reports/starters/GER/` | 34 | Paired Markdown and JSON starter reports for team code GER. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-ger.md) |
| `results/reports/starters/GHA/` | 34 | Paired Markdown and JSON starter reports for team code GHA. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-gha.md) |
| `results/reports/starters/IRN/` | 40 | Paired Markdown and JSON starter reports for team code IRN. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-irn.md) |
| `results/reports/starters/JPN/` | 44 | Paired Markdown and JSON starter reports for team code JPN. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-jpn.md) |
| `results/reports/starters/KOR/` | 38 | Paired Markdown and JSON starter reports for team code KOR. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-kor.md) |
| `results/reports/starters/KSA/` | 40 | Paired Markdown and JSON starter reports for team code KSA. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-ksa.md) |
| `results/reports/starters/MAR/` | 46 | Paired Markdown and JSON starter reports for team code MAR. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-mar.md) |
| `results/reports/starters/MEX/` | 36 | Paired Markdown and JSON starter reports for team code MEX. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-mex.md) |
| `results/reports/starters/NED/` | 36 | Paired Markdown and JSON starter reports for team code NED. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-ned.md) |
| `results/reports/starters/POL/` | 32 | Paired Markdown and JSON starter reports for team code POL. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-pol.md) |
| `results/reports/starters/POR/` | 44 | Paired Markdown and JSON starter reports for team code POR. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-por.md) |
| `results/reports/starters/QAT/` | 30 | Paired Markdown and JSON starter reports for team code QAT. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-qat.md) |
| `results/reports/starters/SEN/` | 36 | Paired Markdown and JSON starter reports for team code SEN. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-sen.md) |
| `results/reports/starters/SRB/` | 32 | Paired Markdown and JSON starter reports for team code SRB. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-srb.md) |
| `results/reports/starters/SUI/` | 38 | Paired Markdown and JSON starter reports for team code SUI. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-sui.md) |
| `results/reports/starters/TUN/` | 36 | Paired Markdown and JSON starter reports for team code TUN. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-tun.md) |
| `results/reports/starters/URU/` | 34 | Paired Markdown and JSON starter reports for team code URU. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-uru.md) |
| `results/reports/starters/USA/` | 36 | Paired Markdown and JSON starter reports for team code USA. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-usa.md) |
| `results/reports/starters/WAL/` | 30 | Paired Markdown and JSON starter reports for team code WAL. Each player normally has one human-readable and one structured file. | [Open guide](folders/reports-starters-wal.md) |
| `results/reports/visuals/heatmaps/` | 593 | One SVG spatial heatmap per player, derived from event locations. | [Open guide](folders/reports-visuals-heatmaps.md) |

## Canonical publication set

The active release is under `results/reports/canonical/`. It contains the final and model summaries, player rankings, coaches notebook, artifact manifest, and canonical data exports. Player and team profile collections remain under their dedicated report folders.

## Important interpretation notes

- `canonical/` is the preferred source for current published values.
- `diagnostics/` and `audit/` contain evaluation evidence, not leaderboards.
- `MIscellaneous/` contains supporting or legacy exploratory outputs and should not override canonical conclusions.
- `starters/`, `player_profiles/`, and `visuals/heatmaps/` are large one-file-per-entity collections; their folder guides enumerate every artifact.
- Out-of-fold (`oof`) artifacts are the appropriate source for leakage-safe validation comparisons.
