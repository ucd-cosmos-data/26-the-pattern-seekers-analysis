# Tournament Attacking-Style Clustering

- Input: `data/processed/world_cup_possessions.csv`
- Assignment output: `data/processed/world_cup_possession_clusters.csv`
- Eligible attacking possessions: 10,741
- Excluded records with no attacking action: 275
- Selected clusters: 3
- Silhouette score: 0.2449
- Stability ARI: 0.9805
- Smallest cluster: 15.24%

The labels below are deterministic interpretations of centroid fingerprints, not preassigned tactical classes.
Shot, goal, xG, final-third entries, and penalty-area entries were excluded from model fitting and appear only as post-clustering effectiveness summaries.

## Discovered styles

| Cluster | Interpreted style | Possessions | Share | Top distinguishing features | Shot rate | Mean xG |
|---:|---|---:|---:|---|---:|---:|
| 0 | Patient Build-up | 5,473 | 50.95% | Possession duration (+0.78 SD), Carry distance (+0.76 SD), Width span (+0.76 SD) | 14.93% | 0.0169 |
| 1 | Direct Long Play | 1,687 | 15.71% | Progression speed (+1.64 SD), Progressive-pass share (+1.50 SD), Pass length (+1.45 SD) | 4.86% | 0.0049 |
| 2 | Short Under Pressure | 3,581 | 33.34% | Total progression (-0.96 SD), Possession duration (-0.79 SD), Width span (-0.74 SD) | 10.70% | 0.0149 |

## Scope

These are attacking styles discovered from event-derived possession features. General StatsBomb 360 freeze frames are not present in `all_events.csv`, so exact defensive shape and compactness are outside this stage.
