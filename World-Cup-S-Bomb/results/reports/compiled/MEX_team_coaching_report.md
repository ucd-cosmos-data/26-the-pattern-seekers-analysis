# Mexico — Team Coaching Report

## Model-grounded summary

Mexico: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Direct Long Play to Patient Build-up). Strongest positive squad synergy: Héctor Alfredo Moreno Herrera + César Jasib Montes Castro (0.656). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.2085
- Mean possession EvA gap: 0.000876
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Hirving Rodrigo Lozano Bahena (Attacking Midfield/Wing)
2. Jesús Daniel Gallardo Vasconcelos (Fullback/Wingback)
3. Luis Gerardo Chávez Magallón (Defensive Midfield)
4. Héctor Alfredo Moreno Herrera (Center Back)
5. César Jasib Montes Castro (Center Back)
6. Ernesto Alexis Vega Rojas (Attacking Midfield/Wing)
7. Henry Josué Martín Mex (Forward)
8. Jorge Eduardo Sánchez Ramos (Fullback/Wingback)
9. Francisco Guillermo Ochoa Magaña (Goalkeeper)
10. Carlos Alberto Rodríguez Gómez (Central/Wide Midfield)
11. José Andrés Guardado Hernández (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.071 |
| Pressing | 1.266 |
| Recovery | -0.714 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 95, GAIN_BELOW_THRESHOLD: 12, INSUFFICIENT_MINUTES: 3.

## V5 role-aware player leaders

1. Hirving Rodrigo Lozano Bahena — Progressive Winger; rating 0.5758, VAEP/90 +0.321, xT/90 +0.170, role-adjusted 0.651
2. Orbelín Pineda Alvarado — Holding Anchor; rating 0.5422, VAEP/90 +0.239, xT/90 +0.015, role-adjusted 0.959
3. Ernesto Alexis Vega Rojas — Progressive Winger; rating 0.5399, VAEP/90 +0.310, xT/90 +0.012, role-adjusted 0.774
4. Carlos Uriel Antuna Romero — Progressive Winger; rating 0.5356, VAEP/90 +0.288, xT/90 +0.033, role-adjusted 0.404
5. Luis Gerardo Chávez Magallón — Progressive Winger; rating 0.5214, VAEP/90 +0.109, xT/90 +0.075, role-adjusted 0.943

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0523 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.0464 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.0398 cumulative Net xG)

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
