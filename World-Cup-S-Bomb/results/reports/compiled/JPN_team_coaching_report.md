# Japan — Team Coaching Report

## Model-grounded summary

Japan: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Maya Yoshida + Shūichi Gonda (0.773). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.5031
- Mean possession EvA gap: 0.005446
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Daichi Kamada (Attacking Midfield/Wing)
2. Junya Ito (Fullback/Wingback)
3. Ritsu Doan (Attacking Midfield/Wing)
4. Maya Yoshida (Center Back)
5. Wataru Endo (Defensive Midfield)
6. Shūichi Gonda (Goalkeeper)
7. Hidemasa Morita (Defensive Midfield)
8. Takuma Asano (Forward)
9. Ko Itakura (Center Back)
10. Yuto Nagatomo (Fullback/Wingback)
11. Yuki Soma (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.029 |
| Pressing | 10.178 |
| Recovery | -0.086 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, GAIN_BELOW_THRESHOLD: 16.

## V5 role-aware player leaders

1. Hiroki Sakai — Attacking Wingback; rating 0.5393, VAEP/90 +0.197, xT/90 +0.070, role-adjusted 0.101
2. Junya Ito — Attacking Wingback; rating 0.5356, VAEP/90 +0.131, xT/90 +0.054, role-adjusted 0.094
3. Shūichi Gonda — Goalkeeper; rating 0.5231, VAEP/90 -0.093, xT/90 +0.007, role-adjusted 0.291
4. Ritsu Doan — Progressive Winger; rating 0.5226, VAEP/90 +0.185, xT/90 +0.057, role-adjusted 0.323
5. Takumi Minamino — Target Forward; rating 0.5161, VAEP/90 -0.230, xT/90 +0.050, role-adjusted 0.675

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.4231 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.4056 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1832 cumulative Net xG)

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
