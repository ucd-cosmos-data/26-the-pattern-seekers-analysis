# Tournament Attacking-Style Clustering

- Input: `data/processed/world_cup_possessions.csv`
- Assignment output: `data/processed/world_cup_possession_clusters.csv`
- Eligible attacking possessions: 10,680
- Excluded records with no attacking action: 336
- Selected clusters: 3
- Silhouette score: 0.2470
- Stability ARI: 0.9974
- Smallest cluster: 15.22%

The labels below are deterministic interpretations of centroid fingerprints, not preassigned tactical classes.
Shot, goal, xG, final-third entries, and penalty-area entries were excluded from model fitting and appear only as post-clustering effectiveness summaries.

## Discovered styles

| Cluster | Interpreted style | Possessions | Share | Top distinguishing features | Shot rate | Mean xG |
|---:|---|---:|---:|---|---:|---:|
| 0 | Direct Long Play | 1,626 | 15.22% | Progression speed (+1.67 SD), Progressive-pass share (+1.53 SD), Pass length (+1.50 SD) | 4.61% | 0.0045 |
| 1 | Patient Build-up | 5,363 | 50.22% | Possession duration (+0.79 SD), Width span (+0.77 SD), Carry volume (+0.77 SD) | 14.86% | 0.0168 |
| 2 | Short Under Pressure | 3,691 | 34.56% | Total progression (-0.92 SD), Possession duration (-0.76 SD), Width span (-0.72 SD) | 9.46% | 0.0100 |

## Scope

These are attacking styles discovered from event-derived possession features. General StatsBomb 360 freeze frames are not present in `all_events.csv`, so exact defensive shape and compactness are outside this stage.
