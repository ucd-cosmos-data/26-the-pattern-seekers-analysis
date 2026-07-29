# Costa Rica — Team Coaching Report

## Model-grounded summary

Costa Rica: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Keylor Navas Gamboa + Óscar Esau Duarte Gaitán (0.649). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.6111
- Mean possession EvA gap: 0.003150
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Joel Nathaniel Campbell Samuels (Forward)
2. Yeltsin Ignacio Tejeda Valverde (Central/Wide Midfield)
3. Anthony Daniel Contreras Enríquez (Forward)
4. Bryan Oviedo (Fullback/Wingback)
5. Keysher Fuller Spence (Fullback/Wingback)
6. Óscar Esau Duarte Gaitán (Center Back)
7. Celso Borges Mora (Defensive Midfield)
8. Jewison Bennette (Attacking Midfield/Wing)
9. Keylor Navas Gamboa (Goalkeeper)
10. Johan Alberto Venegas Ulloa (Forward)
11. Kendall Jamaal Waston Manley (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.101 |
| Pressing | 0.962 |
| Recovery | -0.471 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, GAIN_BELOW_THRESHOLD: 11, INSUFFICIENT_MINUTES: 5.

## V5 role-aware player leaders

1. Jewison Bennette — Ball-Winner; rating 0.5157, VAEP/90 +0.084, xT/90 +0.038, role-adjusted 0.066
2. Gerson Torres Barrantes — Ball-Winner; rating 0.5101, VAEP/90 -0.016, xT/90 +0.001, role-adjusted 0.063
3. Carlos Manuel Martínez Castro — Deep Playmaker; rating 0.4993, VAEP/90 -0.006, xT/90 -0.001, role-adjusted 0.019
4. Youstin Delfin Salas Gómez — Two-Way Fullback; rating 0.4938, VAEP/90 -0.142, xT/90 +0.030, role-adjusted 0.001
5. Brandon Aguilera Zamora — Holding Anchor; rating 0.4881, VAEP/90 -0.015, xT/90 +0.001, role-adjusted 0.060

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1492 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1456 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1276 cumulative Net xG)

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
