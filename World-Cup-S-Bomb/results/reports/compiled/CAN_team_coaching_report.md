# Canada — Team Coaching Report

## Model-grounded summary

Canada: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -1.282. Strongest positive squad synergy: Steven de Sousa Vitoria + Kamal Miller (0.647). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.3081
- Mean possession EvA gap: 0.001284
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Alphonso Davies (Central/Wide Midfield)
2. Alistair Johnston (Fullback/Wingback)
3. Jonathan David (Forward)
4. Tajon Buchanan (Central/Wide Midfield)
5. David Junior Hoilett (Central/Wide Midfield)
6. Steven de Sousa Vitoria (Center Back)
7. Kamal Miller (Center Back)
8. Milan Borjan (Goalkeeper)
9. Richie Laryea (Fullback/Wingback)
10. Cyle Larin (Forward)
11. Atiba Hutchinson (Defensive Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.027 |
| Pressing | -1.282 |
| Recovery | 0.782 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 74, INSUFFICIENT_MINUTES: 8, GAIN_BELOW_THRESHOLD: 6.

## V5 role-aware player leaders

1. Alistair Johnston — Attacking Wingback; rating 0.5570, VAEP/90 +0.216, xT/90 +0.067, role-adjusted 0.101
2. Jonathan David — Target Forward; rating 0.5556, VAEP/90 +0.982, xT/90 +0.010, role-adjusted 0.484
3. Alphonso Davies — Box-to-Box / Engine Midfielder; rating 0.5511, VAEP/90 +0.418, xT/90 +0.069, role-adjusted 0.367
4. Richie Laryea — Attacking Wingback; rating 0.5464, VAEP/90 +0.231, xT/90 +0.092, role-adjusted 0.392
5. Tajon Buchanan — Progressive Winger; rating 0.5341, VAEP/90 +0.299, xT/90 +0.097, role-adjusted 0.503

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.0855 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.0599 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.0513 cumulative Net xG)

_Counterfactual values are predictive scenario estimates, not causal treatment effects. Substitutions below the gain floor or with confidence intervals crossing zero are suppressed._

<!-- PLAYER_ROLE_VALIDATION_START -->
## V5 probabilistic role validation

The production role model selected **K=16 with `tied` covariance by BIC with AIC tie-breaking. K-Means functional roles remain the published baseline; GMM probabilities and entropy are additive descriptors.

- Bootstrap ARI median: 0.6260
- Bootstrap ARI fifth percentile: 0.5113
- PCA explained variance: 0.7367

Roles do not award points directly. Continuous role dimensions only modulate the weights applied to observed contributions.
<!-- PLAYER_ROLE_VALIDATION_END -->

<!-- ROLE_AWARE_VALUATION_START -->
## V5 role-aware valuation and attention gate

**Production decision: `ROLE_AWARE_FALLBACK`.** The role-aware layer is active.
The optional attention experiment was disabled for this canonical run, so the interpretable role-aware fallback remains active without publishing unevaluated attention metrics.

New-versus-legacy ranking Spearman correlation: 0.7057.
<!-- ROLE_AWARE_VALUATION_END -->

<!-- CONTINUOUS_ROLE_REFINEMENT_START -->
## Functional-role compatibility

The accepted functional-role refinements remain available beside the original K-Means label. V5 adds continuous seven-dimensional role vectors and probabilistic roles; neither system contains player-name rules or discrete role bonuses.
<!-- CONTINUOUS_ROLE_REFINEMENT_END -->
