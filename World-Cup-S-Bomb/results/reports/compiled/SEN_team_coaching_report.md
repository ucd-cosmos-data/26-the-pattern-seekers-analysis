# Senegal — Team Coaching Report

## Model-grounded summary

Senegal: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -1.491. Strongest positive squad synergy: Kalidou Koulibaly + Edouard Mendy (0.753). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.2354
- Mean possession EvA gap: 0.004290
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Youssouf Sabaly (Fullback/Wingback)
2. Ismaïla Sarr (Attacking Midfield/Wing)
3. Boulaye Dia (Attacking Midfield/Wing)
4. Kalidou Koulibaly (Center Back)
5. Idrissa Gana Gueye (Attacking Midfield/Wing)
6. Edouard Mendy (Goalkeeper)
7. Ismail Jakobs (Fullback/Wingback)
8. Nampalys Mendy (Defensive Midfield)
9. Krépin Diatta (Attacking Midfield/Wing)
10. Abdou Diallo (Center Back)
11. Cheikh Ahmadou Bamba Mbacke Dieng (Forward)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.016 |
| Pressing | -1.491 |
| Recovery | -0.488 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 6.

## V5 role-aware player leaders

1. Ismaïla Sarr — Progressive Winger; rating 0.6070, VAEP/90 +0.461, xT/90 +0.090, role-adjusted 0.523
2. Youssouf Sabaly — Attacking Wingback; rating 0.5530, VAEP/90 +0.132, xT/90 +0.078, role-adjusted 0.092
3. Pape Matar Sarr — Holding Anchor; rating 0.5461, VAEP/90 +0.073, xT/90 +0.134, role-adjusted 0.869
4. Krépin Diatta — Progressive Winger; rating 0.5405, VAEP/90 +0.244, xT/90 +0.094, role-adjusted 0.383
5. Ismail Jakobs — Attacking Wingback; rating 0.5292, VAEP/90 +0.046, xT/90 +0.089, role-adjusted 0.123

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.3251 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2672 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1931 cumulative Net xG)

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
