# Poland — Team Coaching Report

## Model-grounded summary

Poland: Patient Build-up led the observed baseline by 0.0041 mean EvA. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Kamil Glik + Matty Cash (0.756). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.1530
- Mean possession EvA gap: 0.004133
- Most common optimal style: Patient Build-up

## Optimized starting 11

1. Robert Lewandowski (Forward)
2. Kamil Glik (Center Back)
3. Matty Cash (Fullback/Wingback)
4. Bartosz Bereszyński (Fullback/Wingback)
5. Piotr Zieliński (Central/Wide Midfield)
6. Jakub Piotr Kiwior (Center Back)
7. Jakub Kamiński (Central/Wide Midfield)
8. Grzegorz Krychowiak (Defensive Midfield)
9. Przemysław Frankowski (Central/Wide Midfield)
10. Wojciech Szczęsny (Goalkeeper)
11. Kamil Grosicki (Attacking Midfield/Wing)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.054 |
| Pressing | 1.148 |
| Recovery | -0.413 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 90, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 7.

## V5 role-aware player leaders

1. Wojciech Szczęsny — Goalkeeper; rating 0.6318, VAEP/90 -0.240, xT/90 +0.005, role-adjusted 0.468
2. Robert Lewandowski — Target Forward / Penalty-Box Anchor; rating 0.5228, VAEP/90 +0.507, xT/90 +0.019, role-adjusted 0.452
3. Bartosz Bereszyński — Wide Creator; rating 0.5146, VAEP/90 +0.078, xT/90 +0.040, role-adjusted 0.014
4. Jakub Kamiński — Progressive Winger; rating 0.4809, VAEP/90 +0.173, xT/90 +0.047, role-adjusted 0.408
5. Karol Świderski — Holding Anchor; rating 0.4700, VAEP/90 +0.005, xT/90 -0.010, role-adjusted 0.002

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2162 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2053 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1831 cumulative Net xG)

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
