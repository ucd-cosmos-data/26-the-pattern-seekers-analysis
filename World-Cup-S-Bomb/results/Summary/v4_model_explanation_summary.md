# V4 Model Explanations

## V4 Model Explanations

### Player-ranking metrics

- Players below 300 tournament minutes are excluded before ranking.
- `obv_per_90` is the primary attacking-role signal. Source for this run: `open_event_value_fallback`. The supplied open event export has no licensed StatsBomb OBV column. This build therefore uses the documented open-event pitch-value fallback and does not represent it as proprietary OBV.
- Successful pass/carry endpoints and other completed on-ball actions are mapped on the StatsBomb 120x80 coordinate system.
- `final_third_share` is the proportion of successful event endpoints plus matching SB360 actor snapshots with X > 80.
- Turnovers receive a location-sensitive penalty. The multiplier is exactly 0.5 when the event is flagged under pressure or the SB360 frame shows close/high-density defensive pressure.
- Attacking composites weight role-relative OBV 65%, final-third presence 20%, and pressure-adjusted turnover resilience 15%.
- The final composite is standardized with `groupby('Functional role')`; score 50 is role average and each 10 points represents one within-role population standard deviation.

### Model structure

The V3 leakage-safe 64-match leave-one-match-out transition classifier, Platt calibration, abstention threshold policy, and counterfactual confidence gates remain intact. V4 changes the player-evaluation layer and uses the role-relative score when ranking eligible lineup candidates.

OOF evaluation: 64 matches, 32 teams, Brier 0.001339, PR-AUC 0.005958, ROC-AUC 0.689341.

### StatsBomb source distinctions and heatmap mapping

1. **Standard match events:** event UUID, player identity, action type/outcome, `location`, `pass_end_location`, `carry_end_location`, shot xG, and `under_pressure` define the on-ball action path and value.
2. **Player metadata and tournament components:** player/team identity, position group, squad context, and aggregated minutes define eligibility and the initial functional-role cohort.
3. **StatsBomb 360:** the matching event UUID links actor freeze-frame coordinates and defender density/distance to the event. These snapshots refine pressure and spatial density.

**Important spatial boundary:** StatsBomb 360 contains event-time freeze-frame snapshots, not continuous optical tracking. V4 heatmaps therefore visualize observed successful endpoints and visible actor snapshots; they do not interpolate unobserved runs.

### Spatial and role safeguards

- Fullbacks above 35% combined final-third spatial share are reclassified as `Attacking Wingback`.
- No fullback/wingback may retain the `Holding Anchor` label; below-threshold cases are protected as `Two-Way Fullback`.
- Eligible players: 142 of 680 (538 removed by the cutoff).
- Spatial inputs: 81,231 successful action endpoints and 72,016 linked SB360 actor snapshots.
- Reports: 64 unversioned compiled files, including 142 player sections.

### Top role-relative evaluations

| Rank | Player | Functional role | Minutes | OBV/90 | Final third | Role z |
|---:|---|---|---:|---:|---:|---:|
| 1 | Rodrigo Hernández Cascante | Holding Anchor | 414 | +0.6666 | 6.9% | +2.61 |
| 2 | Young-Gwon Kim | Deep Playmaker | 373 | +0.4447 | 3.8% | +2.55 |
| 3 | Wojciech Szczęsny | Goalkeeper | 390 | +0.5992 | 2.6% | +2.30 |
| 4 | Borna Sosa | Box-to-Box Runner | 440 | +0.0706 | 31.1% | +2.19 |
| 5 | Éder Gabriel Militão | Ball-Winner | 364 | +0.2005 | 19.9% | +1.70 |
| 6 | Woo-Young Jung | Ball-Winner | 318 | +0.2307 | 17.3% | +1.67 |
| 7 | Sergino Dest | Wide Creator | 308 | +0.0997 | 31.7% | +1.63 |
| 8 | Kalidou Koulibaly | Deep Playmaker | 387 | +0.3210 | 3.3% | +1.44 |
| 9 | João Félix Sequeira | Target Forward | 340 | -0.2163 | 47.7% | +1.41 |
| 10 | Jin-Su Kim | Attacking Wingback | 341 | +0.0005 | 46.0% | +1.38 |

These rankings support scouting and video prioritization. They are not causal estimates, transfer values, or direct comparisons across roles.
