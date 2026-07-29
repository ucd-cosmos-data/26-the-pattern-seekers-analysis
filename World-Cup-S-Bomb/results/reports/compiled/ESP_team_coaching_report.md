# Spain — Team Coaching Report

## Model-grounded summary

Spain: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -12.554. Strongest positive squad synergy: Rodrigo Hernández Cascante + Unai Simón Mendibil (0.779). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.8424
- Mean possession EvA gap: 0.002407
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Daniel Olmo Carvajal (Attacking Midfield/Wing)
2. Pedro González López (Central/Wide Midfield)
3. Marco Asensio Willemsen (Forward)
4. Rodrigo Hernández Cascante (Center Back)
5. Pablo Martín Páez Gavira (Central/Wide Midfield)
6. Sergio Busquets i Burgos (Defensive Midfield)
7. Álvaro Borja Morata Martín (Forward)
8. Unai Simón Mendibil (Goalkeeper)
9. Jordi Alba Ramos (Fullback/Wingback)
10. Aymeric Laporte (Center Back)
11. Alejandro Balde Martínez (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.046 |
| Pressing | -12.554 |
| Recovery | 0.142 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 95, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 2.

## V5 role-aware player leaders

1. Daniel Olmo Carvajal — Progressive Winger; rating 0.6259, VAEP/90 +0.558, xT/90 +0.072, role-adjusted 0.562
2. Jordi Alba Ramos — Attacking Wingback; rating 0.5825, VAEP/90 +0.359, xT/90 +0.104, role-adjusted 0.140
3. Ferrán Torres García — Progressive Winger; rating 0.5610, VAEP/90 +0.458, xT/90 +0.053, role-adjusted 0.396
4. Marco Asensio Willemsen — Progressive Winger; rating 0.5574, VAEP/90 +0.799, xT/90 +0.021, role-adjusted 0.593
5. Unai Simón Mendibil — Goalkeeper; rating 0.5530, VAEP/90 -0.050, xT/90 +0.001, role-adjusted 0.000

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.3288 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1965 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1035 cumulative Net xG)

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
