# Ghana — Team Coaching Report

## Model-grounded summary

Ghana: Patient Build-up led the observed baseline by 0.0054 mean EvA. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Thomas Teye Partey + Mohamed Salisu (0.663). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.2133
- Mean possession EvA gap: 0.005369
- Most common optimal style: Patient Build-up

## Optimized starting 11

1. Mohammed Kudus (Attacking Midfield/Wing)
2. Iñaki Williams Arthuer (Forward)
3. Mohamed Salisu (Center Back)
4. Thomas Teye Partey (Defensive Midfield)
5. Daniel Amartey (Center Back)
6. Salis Abdul Samed (Defensive Midfield)
7. Abdul Rahman Baba (Fullback/Wingback)
8. André Ayew Pelé (Attacking Midfield/Wing)
9. Lawrence Ati-Zigi (Goalkeeper)
10. Jordan Ayew (Attacking Midfield/Wing)
11. Alidu Seidu (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.156 |
| Pressing | 1.137 |
| Recovery | 0.026 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 6.

## V5 role-aware player leaders

1. Mohammed Kudus — Progressive Winger; rating 0.5841, VAEP/90 +0.552, xT/90 +0.031, role-adjusted 0.515
2. Osman Bukari — Ball-Winner; rating 0.5622, VAEP/90 +0.498, xT/90 +0.031, role-adjusted 0.536
3. Kamaldeen Sulemana — Target Forward; rating 0.5417, VAEP/90 +0.429, xT/90 +0.067, role-adjusted 0.270
4. Abdul Rahman Baba — Attacking Wingback; rating 0.5272, VAEP/90 +0.100, xT/90 +0.047, role-adjusted 0.071
5. Jordan Ayew — Progressive Winger; rating 0.5028, VAEP/90 +0.061, xT/90 +0.039, role-adjusted 0.268

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.3480 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.3099 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1862 cumulative Net xG)

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
