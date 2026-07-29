# `results/metadata/`

Machine-readable run metadata, feature definitions, provenance, and model configuration snapshots.

## Inventory

- Direct files: **5**
- Immediate subfolders: **0**
- Formats: `.json` (5)

## Files

| File | Format and scale | Information contained | Structure |
|---|---|---|---|
| [`artifact_manifest.json`](../../metadata/artifact_manifest.json) | .json; Object with 5 top-level keys; 117,932 bytes | Release manifest listing generated artifacts and integrity hashes. | Top-level keys: output_root, files, hashes, schema_version, metadata |
| [`cleanup_audit_log.json`](../../metadata/cleanup_audit_log.json) | .json; Object with 13 top-level keys; 479,946 bytes | JSON artifact: cleanup audit log. | Top-level keys: audit_schema_version, generated_at_utc, base_directory, scope, target_directories, prechange_canonical_snapshot, prechange_artifact_counts, observations, moves, deletes, missing_move_sources, unplanned_direct_files, expected_counts |
| [`cleanup_verification.json`](../../metadata/cleanup_verification.json) | .json; Object with 11 top-level keys; 3,891 bytes | JSON artifact: cleanup verification. | Top-level keys: verification_schema_version, generated_at_utc, status, checks, counts, canonical_integrity, root_direct_files, report_direct_files_excluding_readme, legacy_directories, target_directories, readme_links |
| [`pipeline_manifest.json`](../../metadata/pipeline_manifest.json) | .json; Object with 17 top-level keys; 35,311 bytes | JSON artifact: pipeline manifest. | Top-level keys: schema_version, status, model_source, model_warning, model_version, target, calibration_method, threshold, threshold_status, locked_v2_holdout_metrics, tournament_oof_metrics, player_evaluation_provenance, vaep_xt_model, fold_assignment_hash, counts, checks, runtime |
| [`v5_cleanup_manifest.json`](../../metadata/v5_cleanup_manifest.json) | .json; Object with 4 top-level keys; 242 bytes | Record of obsolete-artifact cleanup and canonical publication checks. | Top-level keys: schema_version, cleanup_executed_after_v5_artifact_validation, deleted, allowlist |

## Interpretation and use

Use human-readable Markdown, office documents, and figures for review. Use CSV, JSON, and Parquet artifacts for reproducible analysis. Consult the canonical model summary and provenance metadata before comparing metrics across model generations.
