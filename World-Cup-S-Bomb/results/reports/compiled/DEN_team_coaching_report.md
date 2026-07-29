# Denmark — Team Coaching Report

## Model-grounded summary

Denmark: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.172. Strongest positive squad synergy: Kasper Schmeichel + Joachim Andersen (0.650). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.6901
- Mean possession EvA gap: 0.002828
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Christian Dannemann Eriksen (Central/Wide Midfield)
2. Pierre-Emile Højbjerg (Central/Wide Midfield)
3. Andreas Christensen (Center Back)
4. Jesper Lindstrøm (Attacking Midfield/Wing)
5. Joakim Mæhle (Fullback/Wingback)
6. Joachim Andersen (Center Back)
7. Kasper Dolberg (Forward)
8. Andreas Skov Olsen (Attacking Midfield/Wing)
9. Rasmus Nissen Kristensen (Fullback/Wingback)
10. Kasper Schmeichel (Goalkeeper)
11. Thomas Delaney (Defensive Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.157 |
| Pressing | -2.172 |
| Recovery | -0.546 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 87, GAIN_BELOW_THRESHOLD: 10, INSUFFICIENT_MINUTES: 2.

## V5 role-aware player leaders

1. Kasper Schmeichel — Goalkeeper; rating 0.5694, VAEP/90 -0.126, xT/90 +0.024, role-adjusted 0.052
2. Andreas Skov Olsen — Progressive Winger; rating 0.5544, VAEP/90 +0.522, xT/90 +0.030, role-adjusted 0.589
3. Rasmus Nissen Kristensen — Attacking Wingback; rating 0.5480, VAEP/90 +0.186, xT/90 +0.074, role-adjusted 0.068
4. Alexander Hartmann Bah — Attacking Wingback; rating 0.5387, VAEP/90 +0.251, xT/90 +0.163, role-adjusted 1.000
5. Joakim Mæhle — Attacking Wingback; rating 0.5344, VAEP/90 +0.203, xT/90 +0.056, role-adjusted 0.075

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2472 cumulative Net xG)
- Against Set-Piece Compact Shape: switch from Short Under Pressure to Patient Build-up (0.1203 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1136 cumulative Net xG)

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
