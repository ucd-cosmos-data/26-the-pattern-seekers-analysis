# Qatar — Team Coaching Report

## Model-grounded summary

Qatar: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Boualem Khoukhi + Abdelkarim Hassan Al Haj Fadlalla (0.649). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.4901
- Mean possession EvA gap: 0.002122
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Akram Hassan Afif (Forward)
2. Boualem Khoukhi (Center Back)
3. Pedro Miguel Correia (Center Back)
4. Abdelkarim Hassan Al Haj Fadlalla (Center Back)
5. Homam Alamin Ahmed (Fullback/Wingback)
6. Almoez Ali Zainalabiddin Abdulla (Forward)
7. Abdulaziz Hatem Mohammed Abdullah (Central/Wide Midfield)
8. Hassan Khalid Al Heidos (Central/Wide Midfield)
9. Karim Boudiaf (Defensive Midfield)
10. Ismaeel Mohammad Mohammad (Fullback/Wingback)
11. Meshaal Aissa Barsham (Goalkeeper)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.005 |
| Pressing | 2.608 |
| Recovery | -0.286 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 81, INSUFFICIENT_MINUTES: 11, GAIN_BELOW_THRESHOLD: 7.

## V5 role-aware player leaders

1. Ismaeel Mohammad Mohammad — Attacking Wingback; rating 0.4975, VAEP/90 +0.069, xT/90 +0.074, role-adjusted 0.084
2. Mohammed Muntari — Target Forward / Penalty-Box Anchor; rating 0.4840, VAEP/90 +0.293, xT/90 -0.001, role-adjusted 0.432
3. Saad Abdullah Al Sheeb — Goalkeeper; rating 0.4812, VAEP/90 -0.155, xT/90 +0.000, role-adjusted 0.000
4. Pedro Miguel Correia — Deep Playmaker; rating 0.4799, VAEP/90 +0.127, xT/90 +0.021, role-adjusted 0.164
5. Homam Alamin Ahmed — Wide Creator; rating 0.4797, VAEP/90 +0.087, xT/90 -0.000, role-adjusted 0.032

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1823 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1006 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.0935 cumulative Net xG)

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
