# Role-Aware Player Analytics Pipeline

## Active Qatar 2022 ranking architecture

The active release is `ranking-repair-v3.0-qatar-2022`. It preserves the
match-cross-fitted VAEP/xT, spatial, network, 360, and probabilistic-role
evidence produced by the player pipeline, but replaces the old publication
transform with three deliberately separate products.

### Tournament Impact v3

Tournament Impact is signed total contribution in common action-value units.
It is the only outfield score used for `global_rank_v3` and `team_rank_v3`.
Reporting position, role label, player identity, team identity, awards,
advancement stage, reputation, and external rankings cannot change it.

The active attack channel separates expected process, non-penalty goals,
regular penalties, actual assists, xG, xA, and a bounded realization residual.
The selected attack ablation is recorded in the release audit so realized
outcomes are credited once rather than duplicated through VAEP and a full
goal/assist bonus. The defensive channel is selected independently by its
match-disjoint champion/challenger gate and uses signed, opportunity-adjusted
threat-prevention evidence when that challenger passes.

Tournament Impact is not a within-position z-score. The active release also
does not apply the retired one-sided defender lift or a cascade of 450-, 180-,
and 90-minute exposure multipliers.

### Role Quality v3

Role Quality is a contribution rate with one empirical-Bayes shrinkage
treatment. Prior strength is selected from held-out match evidence, and
probabilistic role membership changes only the prior interpretation. Roles
never add value directly to Tournament Impact.

`position_rank_v3` and `role_rank_v3` use Role Quality. Adding empty minutes
cannot improve it. Strong short-sample play may remain highly rated, but its
interval will be wider rather than its score receiving repeated exposure
penalties.

### Uncertainty

Uncertainty is estimated by resampling whole Qatar 2022 matches. The release
publishes Tournament Impact bounds, rank-stability bounds, and a
`stable`/`moderate`/`wide` status. These fields describe sample precision and
never become another score penalty.

## Authoritative event boundary

Ordinary outfield performance includes periods 1–4 only. Period 5 is
shootout-only and is filtered at feature construction, not subtracted later.
The shared scope helper materializes:

- open-play goals;
- non-penalty goals;
- regular-penalty goals;
- regulation/extra-time goals;
- actual assists;
- non-shootout xG and xA; and
- separate shootout attempts and conversions.

The same periods 1–4 boundary applies to shots, xT, VAEP, finishing, and every
Tournament Impact component. Period-five evidence cannot alter an outfield
player's ordinary score.

## Defensive model boundary

The positive-ElasticNet defensive head remains the frozen champion unless a
signed linear or calibrated nonlinear challenger passes nested
match-disjoint and leave-one-team-out gates. Challenger evidence covers
threat removed by interceptions and blocks, pressure-sequence value
reduction, retained-value clearances, opportunity-adjusted aerials, errors,
penalties conceded, progression, and coverage-qualified 360 suppression.

If no challenger passes, the audit records that failure and retains the
champion. Publication never compensates for a failed defensive model with a
large position-based lift.

## Goalkeeper branch

Goalkeepers remain on a dedicated branch with exactly one ranked main
goalkeeper per team. Backup keepers do not receive a published GK rank.
Match-disjoint development folds compare logistic and isotonic post-shot
calibration, with ROC AUC, PR AUC, Brier score, and expected calibration error
reported.

The dedicated score publishes continuous shot stopping, high-leverage shot
stopping, cross/claim control, sweeping, distribution under pressure, regular
penalty performance, and shootout performance separately. Continuous shot
stopping uses periods 1–4 and excludes penalties. Regular penalties use their
own periods 1–4 channel. Shootouts use period 5 only and can contribute at most
10% of the dedicated score; there is no additive `0.20` per save.

When common goalkeeper expected-goals/value-added units are unavailable, the
only cross-position fallback is `percentile_equivalent_placement`. It is a
rank-percentile publication bridge, not measured absolute contribution and
not evidence that a goalkeeper and outfielder have equal common-unit value.

## Validation and release boundaries

- Event and learned valuation folds keep complete matches disjoint.
- Imputation, scaling, calibration, and model selection are fitted inside
  development folds.
- Defensive candidates also undergo leave-one-team-out validation.
- Player-name and team-name permutation tests must leave individual scores
  unchanged.
- Champion/challenger decisions are made independently for attack, defense,
  outfield publication, and goalkeeper components.
- External Qatar 2022 analyses and named-player checks are audit-only and
  cannot tune scoring weights.
- Active artifacts, aliases, profiles, figures, manifests, Markdown, and DOCX
  are generated from source and checked for stale methodology.

The active feature-rich tables are `player_rankings.csv` and the explicit
`player_rankings_v3.csv`. `player_rankings_v2.csv`,
`v5_player_rankings.csv`, and `v5_player_rankings.json` are byte-identical
compatibility aliases after v3 promotion; those filenames do not activate the
retired formulas. Original pre-v3 tables remain under
`results/reports/ranking/legacy/`. The sole active ranking-figure family is
`results/reports/v3_figures/`; existing V5 figures are historical comparison
evidence.

## Data limitations

Only StatsBomb Open Data events, lineups, match metadata, player minutes, and
public 360 freeze frames from the 2022 FIFA World Cup enter scoring. No player
identities are inferred for anonymous off-ball freeze-frame actors. Missing
360 observations remain missing and are represented through masks, coverage,
and evidence counts rather than zeros. Off-ball movement and positioning
therefore describe coverage-qualified event-actor evidence, not continuous
optical tracking.

Rankings describe this tournament sample, not permanent player ability or
causal effects. Uncertainty reflects match-to-match sampling within Qatar 2022
and does not establish generalization to another competition.

## Reproducibility

All scikit-learn and PyTorch components use random seed 42. The release
manifest records portable relative paths and SHA-256 hashes. Run the canonical
pipeline from the repository root:

```powershell
python .\scripts\run_pipeline.py --reuse-validated-oof
```

Run `python -m pytest -q` plus the ranking, goalkeeper, documentation, artifact,
and DOCX validators before publication.

## Historical pre-v3 architecture

The preserved V5 foundation used non-negative team-disjoint ElasticNet
calibration and combined VAEP/xT, role-aware, completeness, off-ball, spatial,
and network signals. Its fallback composite weights were:

| Component | Historical fallback weight |
|---|---:|
| VAEP per 90 | 0.40 |
| VAEP per touch | 0.15 |
| xT per 90 | 0.15 |
| Role-adjusted value | 0.15 |
| Completeness | 0.10 |
| Off-ball score | 0.05 |

The pre-v3 publication layer then used within-position normalization,
`minutes / (minutes + 450)` shrinkage, additional exposure adjustments, and a
one-sided defensive evidence lift. The former goalkeeper publication added
`0.20` per shootout save and described a Blom-derived bridge too broadly.
These details are retained only to reproduce and audit the frozen champion;
none is an active v3 scoring rule.
