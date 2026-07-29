# Netherlands — Team Coaching Report

## Model-grounded summary

Netherlands: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Virgil van Dijk + Andries Noppert (0.840). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.9239
- Mean possession EvA gap: 0.002490
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Denzel Dumfries (Fullback/Wingback)
2. Frenkie de Jong (Defensive Midfield)
3. Memphis Depay (Forward)
4. Cody Mathès Gakpo (Attacking Midfield/Wing)
5. Daley Blind (Fullback/Wingback)
6. Nathan Aké (Center Back)
7. Andries Noppert (Goalkeeper)
8. Virgil van Dijk (Center Back)
9. Steven Bergwijn (Forward)
10. Teun Koopmeiners (Defensive Midfield)
11. Noa Lang (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.024 |
| Pressing | 0.739 |
| Recovery | 0.057 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 92, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 4.

## V5 role-aware player leaders

1. Denzel Dumfries — Attacking Wingback; rating 0.5827, VAEP/90 +0.182, xT/90 +0.050, role-adjusted 0.079
2. Andries Noppert — Goalkeeper; rating 0.5529, VAEP/90 +0.022, xT/90 +0.001, role-adjusted 0.087
3. Cody Mathès Gakpo — Progressive Winger; rating 0.5509, VAEP/90 +0.292, xT/90 +0.075, role-adjusted 0.376
4. Daley Blind — Attacking Wingback; rating 0.5282, VAEP/90 +0.104, xT/90 +0.051, role-adjusted 0.087
5. Memphis Depay — Target Forward; rating 0.5245, VAEP/90 +0.494, xT/90 +0.047, role-adjusted 0.459

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2242 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1516 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.1368 cumulative Net xG)

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
