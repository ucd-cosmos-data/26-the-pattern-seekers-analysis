# South Korea — Team Coaching Report

## Model-grounded summary

South Korea: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Young-Gwon Kim + Seung-Gyu Kim (0.730). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.3593
- Mean possession EvA gap: 0.001341
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Heung-Min Son (Attacking Midfield/Wing)
2. Moon-Hwan Kim (Fullback/Wingback)
3. Gue-Sung Cho (Forward)
4. Young-Gwon Kim (Center Back)
5. In-Beom Hwang (Defensive Midfield)
6. Jin-Su Kim (Fullback/Wingback)
7. Seung-Gyu Kim (Goalkeeper)
8. Jae-Sung Lee (Attacking Midfield/Wing)
9. Kang-In Lee (Central/Wide Midfield)
10. Hee-Chan Hwang (Central/Wide Midfield)
11. Min Jae Kim (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.118 |
| Pressing | 6.170 |
| Recovery | 0.195 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 93, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 3.

## V5 role-aware player leaders

1. Heung-Min Son — Target Forward; rating 0.5729, VAEP/90 +0.368, xT/90 +0.078, role-adjusted 0.475
2. Jin-Su Kim — Attacking Wingback; rating 0.5652, VAEP/90 +0.255, xT/90 +0.041, role-adjusted 0.103
3. Chang-Hoon Kwon — Ball-Winner; rating 0.5399, VAEP/90 +0.515, xT/90 +0.059, role-adjusted 0.068
4. Hee-Chan Hwang — Progressive Winger; rating 0.5366, VAEP/90 +0.526, xT/90 +0.093, role-adjusted 0.982
5. Woo-Yeong Jeong — Ball-Winner; rating 0.5359, VAEP/90 +0.415, xT/90 +0.028, role-adjusted 0.113

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1081 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.0540 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0356 cumulative Net xG)

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
