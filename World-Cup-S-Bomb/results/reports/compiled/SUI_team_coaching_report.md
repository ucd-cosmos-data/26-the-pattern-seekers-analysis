# Switzerland — Team Coaching Report

## Model-grounded summary

Switzerland: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Direct Long Play to Short Under Pressure). Strongest positive squad synergy: Granit Xhaka + Manuel Obafemi Akanji (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.1079
- Mean possession EvA gap: 0.000360
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Breel-Donald Embolo (Forward)
2. Granit Xhaka (Defensive Midfield)
3. Ricardo Iván Rodríguez Araya (Fullback/Wingback)
4. Manuel Obafemi Akanji (Center Back)
5. Ruben Vargas (Attacking Midfield/Wing)
6. Remo Freuler (Defensive Midfield)
7. Silvan Widmer (Fullback/Wingback)
8. Xherdan Shaqiri (Central/Wide Midfield)
9. Yann Sommer (Goalkeeper)
10. Nico Elvedi (Center Back)
11. Noah Okafor (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.030 |
| Pressing | 2.987 |
| Recovery | -0.646 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 121, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 9.

## V5 role-aware player leaders

1. Fabian Rieder — Deep Playmaker; rating 0.5372, VAEP/90 +0.241, xT/90 +0.034, role-adjusted 0.078
2. Yann Sommer — Goalkeeper; rating 0.5336, VAEP/90 -0.126, xT/90 +0.000, role-adjusted 0.000
3. Ruben Vargas — Progressive Winger; rating 0.5335, VAEP/90 +0.249, xT/90 +0.079, role-adjusted 0.344
4. Silvan Widmer — Attacking Wingback; rating 0.5248, VAEP/90 +0.154, xT/90 +0.039, role-adjusted 0.086
5. Edimilson Fernandes — Ball-Winner; rating 0.5140, VAEP/90 +0.137, xT/90 +0.029, role-adjusted 0.092

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Direct Long Play to Short Under Pressure (0.0491 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Short Under Pressure (0.0408 cumulative Net xG)
- Against High-Intensity Press: switch from Direct Long Play to Short Under Pressure (0.0120 cumulative Net xG)

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
