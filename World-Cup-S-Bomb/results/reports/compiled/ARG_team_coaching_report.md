# Argentina — Team Coaching Report

## Model-grounded summary

Argentina: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.135. Strongest positive squad synergy: Nicolás Hernán Otamendi + Damián Emiliano Martínez (0.927). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 2.9806
- Mean possession EvA gap: 0.005266
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Lionel Andrés Messi Cuccittini (Attacking Midfield/Wing)
2. Damián Emiliano Martínez (Goalkeeper)
3. Rodrigo Javier De Paul (Defensive Midfield)
4. Alexis Mac Allister (Central/Wide Midfield)
5. Enzo Fernandez (Defensive Midfield)
6. Julián Álvarez (Forward)
7. Nicolás Hernán Otamendi (Center Back)
8. Nahuel Molina Lucero (Fullback/Wingback)
9. Marcos Javier Acuña (Fullback/Wingback)
10. Ángel Fabián Di María Hernández (Central/Wide Midfield)
11. Cristian Gabriel Romero (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.043 |
| Pressing | -2.135 |
| Recovery | 0.730 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, GAIN_BELOW_THRESHOLD: 15, INSUFFICIENT_MINUTES: 6.

## V5 role-aware player leaders

1. Lionel Andrés Messi Cuccittini — Progressive Winger; rating 0.7739, VAEP/90 +0.632, xT/90 +0.158, role-adjusted 0.951
2. Ángel Fabián Di María Hernández — Progressive Winger; rating 0.6357, VAEP/90 +0.733, xT/90 +0.200, role-adjusted 0.777
3. Marcos Javier Acuña — Attacking Wingback; rating 0.6148, VAEP/90 +0.422, xT/90 +0.068, role-adjusted 0.096
4. Rodrigo Javier De Paul — Deep Playmaker; rating 0.6104, VAEP/90 +0.244, xT/90 +0.052, role-adjusted 0.289
5. Nicolás Alejandro Tagliafico — Wide Creator; rating 0.5764, VAEP/90 +0.264, xT/90 +0.021, role-adjusted 0.056

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.9990 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.7842 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.4272 cumulative Net xG)

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
