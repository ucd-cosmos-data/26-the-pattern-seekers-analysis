# Ecuador — Team Coaching Report

## Model-grounded summary

Ecuador: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Patient Build-up to Short Under Pressure). Strongest positive squad synergy: Felix Eduardo Torres Caicedo + Piero Martín Hincapié Reyna (0.652). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.5571
- Mean possession EvA gap: 0.002544
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Pervis Josué Estupiñán Tenorio (Fullback/Wingback)
2. Gonzalo Jordy Plata Jiménez (Central/Wide Midfield)
3. Felix Eduardo Torres Caicedo (Center Back)
4. Moisés Isaac Caicedo Corozo (Defensive Midfield)
5. Enner Remberto Valencia Lastra (Attacking Midfield/Wing)
6. Piero Martín Hincapié Reyna (Center Back)
7. Angelo Smit Preciado Quiñónez (Fullback/Wingback)
8. Michael Steveen Estrada Martínez (Forward)
9. Hernán Ismael Galíndez (Goalkeeper)
10. Jeremy Leonel Sarmiento Morante (Central/Wide Midfield)
11. Jhegson Sebastián Méndez Carabalí (Defensive Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.004 |
| Pressing | 1.896 |
| Recovery | 0.400 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 68, GAIN_BELOW_THRESHOLD: 7, INSUFFICIENT_MINUTES: 2.

## V5 role-aware player leaders

1. Pervis Josué Estupiñán Tenorio — Attacking Wingback; rating 0.5858, VAEP/90 +0.250, xT/90 +0.088, role-adjusted 0.120
2. Enner Remberto Valencia Lastra — Target Forward; rating 0.5711, VAEP/90 +0.599, xT/90 +0.028, role-adjusted 0.634
3. Angelo Smit Preciado Quiñónez — Deep Playmaker; rating 0.5554, VAEP/90 +0.111, xT/90 +0.069, role-adjusted 0.137
4. Gonzalo Jordy Plata Jiménez — Box-to-Box / Engine Midfielder; rating 0.4994, VAEP/90 +0.245, xT/90 +0.060, role-adjusted 0.182
5. Jeremy Leonel Sarmiento Morante — Progressive Winger; rating 0.4842, VAEP/90 +0.227, xT/90 +0.070, role-adjusted 0.378

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Patient Build-up to Short Under Pressure (0.1544 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Short Under Pressure (0.1356 cumulative Net xG)
- Against Wide Retreating Block: switch from Patient Build-up to Short Under Pressure (0.1334 cumulative Net xG)

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
