# Tournament Defensive-Style Clustering

- Eligible possessions: 9,690
- Excluded for insufficient spatial coverage: 1,326
- Selected clusters: 4
- Silhouette score: 0.1907
- Stability ARI: 0.9980

Labels are deterministic interpretations of event-and-360 centroid fingerprints.
Attacking outcomes were excluded from model fitting and are shown only for evaluation.

| Cluster | Defensive style | Possessions | Share | Strongest distinctions | Shot allowed | Mean xG allowed |
|---:|---|---:|---:|---|---:|---:|
| 0 | Wide Retreating Block | 5,089 | 52.52% | Close support (-0.61 SD), Immediate proximity (-0.60 SD), Behind-ball share (+0.51 SD), Defensive width (+0.45 SD) | 7.29% | 0.0063 |
| 1 | High-Intensity Press | 713 | 7.36% | Counterpress rate (+2.42 SD), Pressure-event rate (+2.32 SD), Defensive-action rate (+2.18 SD), Immediate proximity (+0.88 SD) | 0.28% | 0.0002 |
| 2 | Set-Piece Compact Shape | 756 | 7.80% | Nearest pressure distance (+2.37 SD), Mean ball distance (+1.88 SD), Line variation (+1.70 SD), Space per defender (-1.27 SD) | 17.46% | 0.0156 |
| 3 | Compact Pressure Block | 3,132 | 32.32% | Close support (+0.82 SD), Mean ball distance (-0.76 SD), Immediate proximity (+0.68 SD), Defensive width (-0.61 SD) | 22.57% | 0.0292 |

Spatial features are normalized into the attacking team's coordinate direction.
Visible-area and observed-player thresholds reduce camera-coverage artifacts.
