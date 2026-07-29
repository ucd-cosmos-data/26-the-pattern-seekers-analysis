# Australia — Team Coaching Report

## Model-grounded summary

Australia: Patient Build-up led the observed baseline by 0.0032 mean EvA. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Harry Souttar + Kye Rowles (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.8514
- Mean possession EvA gap: 0.003189
- Most common optimal style: Patient Build-up

## Optimized starting 11

1. Aziz Eraltay Behich (Fullback/Wingback)
2. Jackson Irvine (Forward)
3. Aaron Mooy (Defensive Midfield)
4. Riley McGree (Forward)
5. Mathew Leckie (Central/Wide Midfield)
6. Kye Rowles (Center Back)
7. Mitchell Thomas Duke (Forward)
8. Craig Goodwin (Central/Wide Midfield)
9. Harry Souttar (Center Back)
10. Mathew Ryan (Goalkeeper)
11. Miloš Degenek (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.083 |
| Pressing | 3.342 |
| Recovery | -0.799 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 7.

## V5 role-aware player leaders

1. Mathew Ryan — Goalkeeper; rating 0.5576, VAEP/90 -0.155, xT/90 +0.002, role-adjusted 0.404
2. Fran Karačić — Attacking Wingback; rating 0.5400, VAEP/90 +0.035, xT/90 +0.139, role-adjusted 0.846
3. Aziz Eraltay Behich — Wide Creator; rating 0.5377, VAEP/90 +0.119, xT/90 +0.044, role-adjusted 0.072
4. Craig Goodwin — Wide Creator; rating 0.4954, VAEP/90 +0.268, xT/90 +0.058, role-adjusted 0.127
5. Nathaniel Atkinson — Deep Playmaker; rating 0.4922, VAEP/90 -0.002, xT/90 +0.008, role-adjusted 0.020

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2183 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1707 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1177 cumulative Net xG)

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
