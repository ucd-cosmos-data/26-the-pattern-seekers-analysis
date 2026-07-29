# `results/`

Top-level result artifacts and entry points produced by the World Cup analytics pipeline.

## Inventory

- Direct files: **0**
- Immediate subfolders: **7**
- Formats: none

## Subfolders

- [`results/MIscellaneous/`](miscellaneous.md) — Supporting tactical summaries, legacy exploratory outputs, and the compact tournament PDF that do not belong to the canonical release.
- [`results/audit/`](audit.md) — Observed-versus-expected comparison tables used to audit possession predictions, team aggregates, and out-of-fold behavior.
- [`results/diagnostics/`](diagnostics.md) — Model evaluation, calibration, feature-importance, cluster-quality, and validation diagnostics.
- [`results/figures/`](figures.md) — Publication-ready charts and the technical onboarding presentation.
- [`results/metadata/`](metadata.md) — Machine-readable run metadata, feature definitions, provenance, and model configuration snapshots.
- [`results/reports/`](reports.md) — Human- and machine-readable player, team, coaching, and tournament reports.
- [`results/simulations/`](simulations.md) — Tactical-style and substitution simulation outputs, including out-of-fold variants and suppression audits.

## Files

| File | Format and scale | Information contained | Structure |
|---|---|---|---|
| _No direct files_ | — | Folder contains subfolders only. | — |

## Interpretation and use

Use human-readable Markdown, office documents, and figures for review. Use CSV, JSON, and Parquet artifacts for reproducible analysis. Consult the canonical model summary and provenance metadata before comparing metrics across model generations.
