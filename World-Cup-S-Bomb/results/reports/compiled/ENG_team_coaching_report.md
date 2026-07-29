# England — Team Coaching Report

## Model-grounded summary

England: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -3.654. Strongest positive squad synergy: John Stones + Jordan Pickford (0.815). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.0404
- Mean possession EvA gap: 0.002882
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Luke Shaw (Fullback/Wingback)
2. Harry Kane (Forward)
3. John Stones (Center Back)
4. Harry Maguire (Center Back)
5. Declan Rice (Defensive Midfield)
6. Jude Bellingham (Defensive Midfield)
7. Bukayo Saka (Attacking Midfield/Wing)
8. Jordan Pickford (Goalkeeper)
9. Jordan Brian Henderson (Central/Wide Midfield)
10. Phil Foden (Attacking Midfield/Wing)
11. Kyle Walker (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.012 |
| Pressing | -3.654 |
| Recovery | 0.987 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, GAIN_BELOW_THRESHOLD: 15, INSUFFICIENT_MINUTES: 2.

## V5 role-aware player leaders

1. Luke Shaw — Attacking Wingback; rating 0.5996, VAEP/90 +0.273, xT/90 +0.085, role-adjusted 0.118
2. Marcus Rashford — Progressive Winger; rating 0.5925, VAEP/90 +0.574, xT/90 +0.066, role-adjusted 0.988
3. Bukayo Saka — Progressive Winger; rating 0.5858, VAEP/90 +0.467, xT/90 +0.059, role-adjusted 0.490
4. Jude Bellingham — Box-to-Box / Engine Midfielder; rating 0.5771, VAEP/90 +0.278, xT/90 +0.042, role-adjusted 0.222
5. Jack Grealish — Ball-Winner; rating 0.5631, VAEP/90 +0.674, xT/90 +0.093, role-adjusted 0.099

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2988 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2831 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1794 cumulative Net xG)

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
