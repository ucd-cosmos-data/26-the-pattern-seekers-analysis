# Role-Aware Player Analytics Pipeline

## Architecture

The extended pipeline treats the existing VAEP/xT and K-Means outputs as a
preserved foundation. Continuous role vectors, 120-by-80 occupancy grids,
StatsBomb 360 geometry, and team-match passing graph features are joined at
player level. A probabilistic GMM supplies role probabilities and entropy, but
roles never add value directly: they continuously modulate the relative
importance of observed contribution metrics.

The raw composite uses non-negative weights learned by a team-disjoint
ElasticNet calibration against a transparent team-importance proxy. If the
learned weights fail the non-inferiority gate, the prior weights below remain
the fallback:

| Component | Weight |
|---|---:|
| VAEP per 90 | 0.40 |
| VAEP per touch | 0.15 |
| xT per 90 | 0.15 |
| Role-adjusted value | 0.15 |
| Completeness | 0.10 |
| Off-ball score | 0.05 |

Offensive and defensive VAEP and ElasticNet heads are combined with explicit
role weights rather than `max(Off, Def)`. A contextual VAEP challenger adds
pre-action score differential, match minute, the opponent's 6 October 2022
FIFA ranking strength, and group-stage/knockout phase. It is accepted only by
a development-OOF non-inferiority gate; the canonical run rejected it and
retained the baseline feature set before opening the untouched test. The
defensive vector also includes a 6-by-8-zone xD-style disruption percentile.

The final score applies reliability
`minutes / (minutes + 450)` and shrinks to the broad position-group mean.
Probabilistic or K-Means role clusters are not shrinkage targets.

Ratings are computed for outfield players with 45+ minutes and goalkeepers
with 90+ minutes. The 300-minute outfield threshold and 270-minute goalkeeper
threshold are reporting labels, not computational exclusions.

## Validation boundaries

- Every learned event model uses match-disjoint `GroupKFold`.
- Role-feature scaling is fitted, never calculated from held-out rows.
- The temporal attention mask blocks all future events.
- The attention challenger must satisfy both retrospective and prospective
  ROC-AUC and calibration gates.
- K-Means remains the functional-role baseline; GMM probabilities and entropy
  are additive diagnostics.
- The comparison artifact contains old rating, new rating, difference, and
  the preserved functional role for every ranked player.

## Data limitations

Only StatsBomb Open Data events, lineups, match metadata, player minutes, and
public 360 freeze frames are used. No player identities are inferred for
anonymous off-ball freeze-frame actors. Missing 360 observations remain
missing and are represented through explicit masks, coverage, and evidence
counts. Reported off-ball movement and positioning therefore describe
coverage-qualified event-actor evidence and should not be interpreted as
continuous optical tracking.

## Reproducibility

All scikit-learn and PyTorch components use random seed 42. The artifact
manifest records SHA-256 hashes so a complete run can be audited. Run
`python -m pytest -q` before publishing artifacts. Run the canonical pipeline
from the repository root with:

```powershell
python .\scripts\run_pipeline.py --reuse-validated-oof
```
