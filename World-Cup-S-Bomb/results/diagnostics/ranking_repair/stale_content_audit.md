# Ranking Repair Stale-Content Audit

- Active stale matches: **0**

| Path | Line | Pattern | Classification | Context |
|---|---:|---|---|---|
| `README.md` | 48 | `within-position-absolute` | compatibility-or-legacy | not use within-position z-scores as absolute global value, the former repeated |
| `README.md` | 49 | `one-sided-defensive-lift` | compatibility-or-legacy | exposure cascade, or the former one-sided defensive publication lift. |
| `data/processed/player_evaluation_provenance.json` | 590 | `old-exposure-constants` | compatibility-or-legacy | "ranking_formula": "role-relative minutes shrinkage of (0.50*vaep_total_p90 + 0.30*vaep_per_touch + 0.20*xt_p90), reliability=minutes/(minutes+450)" |
| `docs/ranking-repair-eight-pass-prompt.md` | 434 | `within-position-absolute` | compatibility-or-legacy | - Do not use within-position z-scores as absolute global value. |
| `docs/ranking-repair-eight-pass-prompt.md` | 542 | `one-sided-defensive-lift` | compatibility-or-legacy | Replace the raw, equally averaged, one-sided direct-defensive lift with |
| `docs/ranking-repair-eight-pass-prompt.md` | 633 | `one-sided-defensive-lift` | compatibility-or-legacy | The active one-sided defensive evidence lift should be retired when the |
| `docs/ranking-repair-eight-pass-prompt.md` | 692 | `shootout-save-0.20` | compatibility-or-legacy | 4. Do not let shootout saves add an unbounded `0.20` each to the base score. |
| `docs/ranking-repair-eight-pass-prompt.md` | 832 | `within-position-absolute` | compatibility-or-legacy | - the old within-position z-score is the active absolute global value |
| `docs/ranking-repair-eight-pass-prompt.md` | 833 | `one-sided-defensive-lift` | compatibility-or-legacy | - the old one-sided defensive lift is active when retired |
| `docs/ranking-repair-eight-pass-prompt.md` | 962 | `shootout-save-0.20` | compatibility-or-legacy | - `shootout_save_points: 0.20` |
| `docs/ranking-repair-eight-pass-prompt.md` | 964 | `within-position-absolute` | compatibility-or-legacy | - old within-position z-score descriptions |
| `docs/ranking-repair-eight-pass-prompt.md` | 965 | `one-sided-defensive-lift` | compatibility-or-legacy | - old one-sided defensive-lift descriptions |
| `docs/role_aware_pipeline.md` | 25 | `within-position-absolute` | compatibility-or-legacy | Tournament Impact is not a within-position z-score. The active release also |
| `docs/role_aware_pipeline.md` | 166 | `old-exposure-constants` | compatibility-or-legacy | `minutes / (minutes + 450)` shrinkage, additional exposure adjustments, and a |
| `docs/role_aware_pipeline.md` | 167 | `one-sided-defensive-lift` | compatibility-or-legacy | one-sided defensive evidence lift. The former goalkeeper publication added |
| `docs/role_aware_pipeline.md` | 168 | `shootout-save-0.20` | compatibility-or-legacy | `0.20` per shootout save and described a Blom-derived bridge too broadly. |
| `docs/website-post-eight-pass-update-prompt.md` | 1058 | `one-sided-defensive-lift` | compatibility-or-legacy | - old one-sided defensive lift is active if retired |
| `docs/website-post-eight-pass-update-prompt.md` | 1060 | `within-position-absolute` | compatibility-or-legacy | - old within-position z-score is absolute global value if retired |
| `results/Summary/model_summary.md` | 28 | `one-sided-defensive-lift` | compatibility-or-legacy | Defensive value is based on opportunity-adjusted threat prevention and signed errors. The old one-sided defensive publication lift is retired. |
| `results/diagnostics/ranking_repair/champion/model_summary.json` | 2523 | `old-exposure-constants` | compatibility-or-legacy | "outfield_reliability": "minutes / (minutes + 450)", |
| `results/diagnostics/ranking_repair/champion/model_summary.json` | 2524 | `old-exposure-constants` | compatibility-or-legacy | "goalkeeper_reliability": "feature_coverage * minutes / (minutes + 450)", |
| `results/documentation/generate_documentation.py` | 1030 | `within-position-absolute` | active-and-correct | "within-position z-scoring or a position-dependent publication lift.", |
| `results/documentation/generate_documentation.py` | 1110 | `one-sided-defensive-lift` | compatibility-or-legacy | "exposure penalties, the one-sided defensive publication lift, an " |
| `results/documentation/generate_documentation.py` | 1111 | `shootout-save-0.20` | active-and-correct | "unbounded `0.20` per shootout save, or a Blom bridge described as " |
| `results/documentation/reports-rankings.md` | 7 | `within-position-absolute` | active-and-correct | - **Tournament Impact v3** is signed total contribution in common action-value units. It determines global and team order without within-position z-scoring or a position-dependent publication lift. |
| `results/documentation/reports-rankings.md` | 65 | `shootout-save-0.20` | compatibility-or-legacy | Retired methodology may appear only in that explicitly historical material. The active score does not use the old within-position z-score as absolute global value, repeated 450/180/90-minute exposure penalties, the one-sided defensive publication lift, an unbounded `0.20` per shootout save, or a Blo |
| `results/documentation/reports-rankings.md` | 65 | `within-position-absolute` | compatibility-or-legacy | Retired methodology may appear only in that explicitly historical material. The active score does not use the old within-position z-score as absolute global value, repeated 450/180/90-minute exposure penalties, the one-sided defensive publication lift, an unbounded `0.20` per shootout save, or a Blo |
| `results/documentation/reports-rankings.md` | 65 | `one-sided-defensive-lift` | compatibility-or-legacy | Retired methodology may appear only in that explicitly historical material. The active score does not use the old within-position z-score as absolute global value, repeated 450/180/90-minute exposure penalties, the one-sided defensive publication lift, an unbounded `0.20` per shootout save, or a Blo |
| `results/metadata/feature_definitions.json` | 71 | `within-position-absolute` | compatibility-or-legacy | "within-position z-score as absolute global value", |
| `results/metadata/feature_definitions.json` | 73 | `one-sided-defensive-lift` | compatibility-or-legacy | "one-sided direct-defensive publication lift", |
| `results/metadata/feature_definitions.json` | 74 | `shootout-save-0.20` | compatibility-or-legacy | "0.20 additive points per goalkeeper shootout save", |
| `results/reports/canonical/model_summary.md` | 28 | `one-sided-defensive-lift` | compatibility-or-legacy | Defensive value is based on opportunity-adjusted threat prevention and signed errors. The old one-sided defensive publication lift is retired. |
| `results/reports/model_summary.md` | 28 | `one-sided-defensive-lift` | compatibility-or-legacy | Defensive value is based on opportunity-adjusted threat prevention and signed errors. The old one-sided defensive publication lift is retired. |
| `results/reports/ranking/ranking_methodology.md` | 13 | `within-position-absolute` | active-and-correct | 1. **Tournament Impact** is a signed total in common action-value units. It determines outfield Global Rank and Team Rank. No within-position z-score, player identity, role bonus, or minutes multiplier creates this value. |
| `scripts/generate_final_tournament_report.py` | 863 | `old-exposure-constants` | compatibility-or-legacy | "- Outfield reliability is minutes/(minutes+450).", |
| `scripts/refresh_tournament_rankings_v2.py` | 69 | `shootout-save-0.20` | compatibility-or-legacy | "shootout_save_points": 0.20, |
| `scripts/run_pipeline.py` | 2039 | `shootout-save-0.20` | compatibility-or-legacy | "shootout_save_points": 0.20, |
| `scripts/run_pipeline.py` | 2063 | `old-exposure-constants` | compatibility-or-legacy | "outfield_reliability": "minutes / (minutes + 450)", |
| `scripts/run_pipeline.py` | 2065 | `old-exposure-constants` | compatibility-or-legacy | "feature_coverage * minutes / (minutes + 450)" |
| `scripts/run_ranking_repair_v3.py` | 1723 | `old-exposure-constants` | active-and-correct | r"(EXPOSURE_SATURATION_SHARE\|PUBLICATION_EXPOSURE_SHARE\|" |
| `scripts/run_ranking_repair_v3.py` | 1724 | `old-exposure-constants` | active-and-correct | r"MinutesReliability.{0,20}450\|" |
| `scripts/run_ranking_repair_v3.py` | 1728 | `within-position-absolute` | active-and-correct | "within-position-absolute": re.compile( |
| `scripts/run_ranking_repair_v3.py` | 1729 | `within-position-absolute` | active-and-correct | r"within-position.{0,80}(?:absolute\|global\|publication\|z-score)", |
| `scripts/run_ranking_repair_v3.py` | 1732 | `one-sided-defensive-lift` | active-and-correct | "one-sided-defensive-lift": re.compile( |
| `scripts/run_ranking_repair_v3.py` | 1733 | `one-sided-defensive-lift` | active-and-correct | r"(one-sided.{0,50}defensive\|DEFENSIVE_EVIDENCE_LIFT)", |
| `scripts/run_ranking_repair_v3.py` | 1737 | `stale-docx-appendix` | active-and-correct | r"Part IX: Unified tournament publication layer", |
| `scripts/run_team_simulation_reports.py` | 784 | `old-exposure-constants` | compatibility-or-legacy | "uses `minutes/(minutes+450)` shrinkage; 300 minutes is a reporting " |
| `scripts/unify_tournament_ratings.py` | 40 | `old-exposure-constants` | compatibility-or-legacy | EXPOSURE_SATURATION_SHARE = 0.75 |
| `scripts/unify_tournament_ratings.py` | 41 | `one-sided-defensive-lift` | compatibility-or-legacy | DEFENSIVE_EVIDENCE_LIFT = 1.00 |
| `scripts/unify_tournament_ratings.py` | 42 | `old-exposure-constants` | compatibility-or-legacy | PUBLICATION_EXPOSURE_SHARE = 0.75 |
| `scripts/unify_tournament_ratings.py` | 370 | `old-exposure-constants` | compatibility-or-legacy | (1.0 - EXPOSURE_SATURATION_SHARE) |
| `scripts/unify_tournament_ratings.py` | 371 | `old-exposure-constants` | compatibility-or-legacy | + EXPOSURE_SATURATION_SHARE * reliability |
| `scripts/unify_tournament_ratings.py` | 374 | `old-exposure-constants` | compatibility-or-legacy | "exposure_share": EXPOSURE_SATURATION_SHARE, |
| `scripts/unify_tournament_ratings.py` | 395 | `old-exposure-constants` | compatibility-or-legacy | factor = 1.0 - PUBLICATION_EXPOSURE_SHARE * uncertainty |
| `scripts/unify_tournament_ratings.py` | 397 | `old-exposure-constants` | compatibility-or-legacy | "exposure_share": PUBLICATION_EXPOSURE_SHARE, |
| `scripts/unify_tournament_ratings.py` | 509 | `one-sided-defensive-lift` | compatibility-or-legacy | DEFENSIVE_EVIDENCE_LIFT |
| `scripts/unify_tournament_ratings.py` | 517 | `one-sided-defensive-lift` | compatibility-or-legacy | "lift_fraction": DEFENSIVE_EVIDENCE_LIFT, |
| `scripts/update_unified_final_summary_docx.py` | 573 | `within-position-absolute` | active-and-correct | "within-position z-score, role bonus, team-strength bonus, or repeated " |
| `scripts/update_unified_final_summary_docx.py` | 604 | `one-sided-defensive-lift` | compatibility-or-legacy | "The former one-sided defensive publication lift is retired." |
| `scripts/update_unified_final_summary_docx.py` | 817 | `within-position-absolute` | active-and-correct | "within-position normalization as absolute global value." |
| `scripts/update_unified_final_summary_docx.py` | 1053 | `stale-docx-appendix` | active-and-correct | if "Part IX: Unified tournament publication layer" in text: |
| `src/models/tournament_rankings.py` | 163 | `shootout-save-0.20` | compatibility-or-legacy | GOALKEEPER_TOURNAMENT_IMPACT_PER_SHOOTOUT_SAVE = 0.20 |
| `src/models/tournament_rankings.py` | 1161 | `shootout-save-0.20` | compatibility-or-legacy | "period-five shootout penalty contributes 0.20, the goalkeeper's " |
| `src/rating_uncertainty.py` | 7 | `old-exposure-constants` | compatibility-or-legacy | reliability = minutes / (minutes + 450) |
| `src/reporting/artifacts.py` | 663 | `one-sided-defensive-lift` | compatibility-or-legacy | "normalization, a one-sided direct defensive-evidence " |
| `src/reporting/artifacts.py` | 1619 | `old-exposure-constants` | compatibility-or-legacy | "minutes/(minutes+450) position-prior shrinkage.", |
| `src/reporting/ranking_repair_release.py` | 610 | `within-position-absolute` | active-and-correct | "No within-position z-score, player identity, role bonus, or " |
| `src/reporting/ranking_repair_release.py` | 961 | `one-sided-defensive-lift` | compatibility-or-legacy | "prevention and signed errors. The old one-sided defensive " |
| `src/reporting/ranking_repair_release.py` | 1999 | `within-position-absolute` | compatibility-or-legacy | "within-position z-score as absolute global value", |
| `src/reporting/ranking_repair_release.py` | 2001 | `one-sided-defensive-lift` | compatibility-or-legacy | "one-sided direct-defensive publication lift", |
| `src/reporting/ranking_repair_release.py` | 2002 | `shootout-save-0.20` | compatibility-or-legacy | "0.20 additive points per goalkeeper shootout save", |
| `src/simulation_engine.py` | 762 | `old-exposure-constants` | compatibility-or-legacy | output["rating_minutes_reliability"] = minutes / (minutes + 450.0) |
| `src/simulation_engine.py` | 2094 | `old-exposure-constants` | compatibility-or-legacy | profiles["rating_minutes_reliability"] = minutes / (minutes + 450.0) |
| `src/simulation_engine.py` | 2325 | `old-exposure-constants` | compatibility-or-legacy | "reliability=minutes/(minutes+450)" |
| `tests/test_final_summary_docx_v3.py` | 69 | `stale-docx-appendix` | test-fixture | assert "Part IX: Unified tournament publication layer" not in text |
| `tests/test_ranking_documentation_v3.py` | 96 | `old-exposure-constants` | test-fixture | assert "minutes / (minutes + 450)" not in active |
| `tests/test_ranking_documentation_v3.py` | 97 | `old-exposure-constants` | test-fixture | assert "minutes / (minutes + 450)" in legacy |
| `tests/test_ranking_documentation_v3.py` | 98 | `shootout-save-0.20` | test-fixture | assert "`0.20` per shootout save" in legacy |
| `tests/test_ranking_repair_release_v3.py` | 578 | `old-exposure-constants` | test-fixture | "minutes / (minutes + 450)", |
| `tests/test_ranking_repair_release_v3.py` | 579 | `shootout-save-0.20` | test-fixture | "shootout_save_points: 0.20", |
| `tests/test_ranking_repair_release_v3.py` | 581 | `within-position-absolute` | test-fixture | "within-position z-score is the active absolute global value", |
| `tests/test_ranking_repair_release_v3.py` | 582 | `one-sided-defensive-lift` | test-fixture | "one-sided defensive evidence lift is active", |
| `tests/test_stale_content_scan.py` | 22 | `shootout-save-0.20` | test-fixture | "SHOOTOUT_SAVE_POINTS = 0.20\n" |
| `tests/test_stale_content_scan.py` | 23 | `old-exposure-constants` | test-fixture | "impact = minutes / (minutes + 450)\n", |
| `tests/test_stale_content_scan.py` | 29 | `stale-docx-appendix` | test-fixture | 'APPENDIX_TITLE = "Part IX: Unified tournament publication layer"\n', |
| `tests/test_stale_content_scan.py` | 34 | `stale-docx-appendix` | test-fixture | 'if "Part IX: Unified tournament publication layer" in text:\n' |
| `tests/test_stale_content_scan.py` | 40 | `within-position-absolute` | test-fixture | "The active score does not use within-position z-scores as absolute " |
| `tests/test_stale_content_scan.py` | 47 | `old-exposure-constants` | test-fixture | "The former score used minutes / (minutes + 450).\n", |
| `tests/test_stale_content_scan.py` | 59 | `shootout-save-0.20` | test-fixture | '  "0.20 additive points per goalkeeper shootout save"\n' |
| `tests/test_stale_content_scan.py` | 65 | `shootout-save-0.20` | test-fixture | '"shootout_save_points": 0.20,\n', |
| `tests/test_stale_content_scan.py` | 70 | `shootout-save-0.20` | test-fixture | "shootout save points: 0.20\n", |
| `tests/test_stale_content_scan.py` | 75 | `old-exposure-constants` | test-fixture | 'assert "minutes / (minutes + 450)" in historical_text\n', |
| `tests/test_stale_content_scan.py` | 81 | `old-exposure-constants` | test-fixture | '    pattern = r"EXPOSURE_SATURATION_SHARE"\n' |
| `tests/test_stale_content_scan.py` | 89 | `shootout-save-0.20` | test-fixture | '{"context": "SHOOTOUT_SAVE_POINTS = 0.20"}\n', |
| `tests/test_stale_content_scan.py` | 115 | `within-position-absolute` | test-fixture | ("README.md", "within-position-absolute") |
