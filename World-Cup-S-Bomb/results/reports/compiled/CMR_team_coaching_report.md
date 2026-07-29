# Cameroon — Team Coaching Report

## Model-grounded summary

Cameroon: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Direct Long Play to Patient Build-up). Strongest positive squad synergy: André-Frank Zambo Anguissa + Nouhou Tolo (0.627). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.0510
- Mean possession EvA gap: 0.000235
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Jean-Eric Maxim Choupo-Moting (Forward)
2. Nouhou Tolo (Fullback/Wingback)
3. Ngoran Suiru Fai Collins (Fullback/Wingback)
4. Bryan Mbeumo (Attacking Midfield/Wing)
5. André-Frank Zambo Anguissa (Defensive Midfield)
6. Karl Brillant Toko Ekambi (Attacking Midfield/Wing)
7. Martin Hongla Yma II (Central/Wide Midfield)
8. Jean-Charles Castelletto (Center Back)
9. Nicolas Alexis Julio N'Koulou Ndoubena (Center Back)
10. Devis Rogers Epassy Mboka (Goalkeeper)
11. Nicolas Moumi Ngamaleu (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.078 |
| Pressing | 4.206 |
| Recovery | -0.111 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 106, GAIN_BELOW_THRESHOLD: 9, INSUFFICIENT_MINUTES: 6.

## V5 role-aware player leaders

1. Karl Brillant Toko Ekambi — Ball-Winner; rating 0.5550, VAEP/90 +0.317, xT/90 +0.039, role-adjusted 0.110
2. Devis Rogers Epassy Mboka — Goalkeeper; rating 0.5452, VAEP/90 -0.188, xT/90 +0.002, role-adjusted 0.420
3. Bryan Mbeumo — Progressive Winger; rating 0.5106, VAEP/90 +0.154, xT/90 +0.051, role-adjusted 0.349
4. André Onana — Goalkeeper; rating 0.5102, VAEP/90 -0.065, xT/90 +0.002, role-adjusted 0.500
5. Vincent Paté Aboubakar — Target Forward; rating 0.4882, VAEP/90 +0.363, xT/90 +0.014, role-adjusted 0.458

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0364 cumulative Net xG)
- Against Set-Piece Compact Shape: switch from Direct Long Play to Patient Build-up (0.0146 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to No meaningful change (0.0000 cumulative Net xG)

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
