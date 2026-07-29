# Iran — Team Coaching Report

## Model-grounded summary

Iran: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Morteza Pouraliganji + Seyed Majid Hosseini (0.669). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.6928
- Mean possession EvA gap: 0.003553
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Mehdi Taremi (Forward)
2. Ehsan Hajsafi (Fullback/Wingback)
3. Morteza Pouraliganji (Center Back)
4. Saeid Ezatolahi Afagh (Defensive Midfield)
5. Seyed Majid Hosseini (Center Back)
6. Ali Gholizadeh (Central/Wide Midfield)
7. Ramin Rezaeian (Fullback/Wingback)
8. Sardar Azmoun (Forward)
9. Mehdi Torabi (Central/Wide Midfield)
10. Alireza Jahanbakhsh (Attacking Midfield/Wing)
11. Seyed Hossein Hosseini (Goalkeeper)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.058 |
| Pressing | 1.725 |
| Recovery | -1.059 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 96, GAIN_BELOW_THRESHOLD: 11, INSUFFICIENT_MINUTES: 3.

## V5 role-aware player leaders

1. Alireza Safar Beiranvand — Goalkeeper; rating 0.5512, VAEP/90 -0.164, xT/90 +0.011, role-adjusted 0.219
2. Saman Ghoddos — Target Forward; rating 0.5444, VAEP/90 +0.368, xT/90 +0.064, role-adjusted 0.501
3. Alireza Jahanbakhsh — Ball-Winner; rating 0.5411, VAEP/90 +0.189, xT/90 +0.057, role-adjusted 0.374
4. Karim Ansarifard — Ball-Winner; rating 0.5347, VAEP/90 +0.210, xT/90 +0.030, role-adjusted 0.316
5. Ramin Rezaeian — Attacking Wingback; rating 0.5230, VAEP/90 +0.110, xT/90 +0.085, role-adjusted 0.157

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1768 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.1104 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.1046 cumulative Net xG)

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
