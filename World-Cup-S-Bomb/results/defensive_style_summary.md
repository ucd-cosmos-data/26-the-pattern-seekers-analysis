# Tournament Defensive-Style Clustering

- Eligible possessions: 9,685
- Excluded for insufficient spatial coverage: 1,331
- Selected clusters: 4
- Silhouette score: 0.1897
- Stability ARI: 0.9999

Labels are deterministic interpretations of event-and-360 centroid fingerprints.
Attacking outcomes were excluded from model fitting and are shown only for evaluation.

| Cluster | Defensive style | Possessions | Share | Strongest distinctions | Shot allowed | Mean xG allowed |
|---:|---|---:|---:|---|---:|---:|
| 0 | Compact Pressure Block | 3,121 | 32.23% | Close support (+0.81 SD), Mean ball distance (-0.75 SD), Immediate proximity (+0.67 SD), Defensive width (-0.62 SD) | 22.11% | 0.0281 |
| 1 | Wide Retreating Block | 5,091 | 52.57% | Close support (-0.61 SD), Immediate proximity (-0.60 SD), Behind-ball share (+0.51 SD), Space per defender (+0.44 SD) | 7.23% | 0.0063 |
| 2 | Set-Piece Compact Shape | 727 | 7.51% | Nearest pressure distance (+2.40 SD), Mean ball distance (+1.90 SD), Line variation (+1.74 SD), Space per defender (-1.32 SD) | 18.02% | 0.0160 |
| 3 | High-Intensity Press | 746 | 7.70% | Counterpress rate (+2.35 SD), Pressure-event rate (+2.24 SD), Defensive-action rate (+2.02 SD), Immediate proximity (+0.89 SD) | 2.41% | 0.0029 |

Spatial features are normalized into the attacking team's coordinate direction.
Visible-area and observed-player thresholds reduce camera-coverage artifacts.
