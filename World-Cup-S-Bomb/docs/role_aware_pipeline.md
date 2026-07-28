# Role-Aware Player Analytics Pipeline

## Architecture

The extended pipeline treats the existing VAEP/xT and K-Means outputs as a
preserved foundation. Continuous role vectors, 120-by-80 occupancy grids,
StatsBomb 360 geometry, and team-match passing graph features are joined at
player level. A probabilistic GMM supplies role probabilities and entropy, but
roles never add value directly: they continuously modulate the relative
importance of observed contribution metrics.

The raw composite uses the configured weights:

| Component | Weight |
|---|---:|
| VAEP per 90 | 0.40 |
| VAEP per touch | 0.15 |
| xT per 90 | 0.15 |
| Role-adjusted value | 0.15 |
| Completeness | 0.10 |
| Off-ball score | 0.05 |

The final score applies reliability
`minutes / (minutes + 300)` and shrinks to the broad position-group mean.
Probabilistic or K-Means role clusters are not shrinkage targets.

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
python .\scripts\run_pipeline.py --skip-legacy-foundation --enable-attention
```
