# Belgium — Team Coaching Report

## Model-grounded summary

Belgium: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Jan Vertonghen + Thibaut Courtois (0.645). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.8230
- Mean possession EvA gap: 0.003707
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Kevin De Bruyne (Attacking Midfield/Wing)
2. Timothy Castagne (Fullback/Wingback)
3. Axel Witsel (Defensive Midfield)
4. Michy Batshuayi Tunga (Forward)
5. Thomas Meunier (Fullback/Wingback)
6. Toby Alderweireld (Center Back)
7. Thibaut Courtois (Goalkeeper)
8. Jan Vertonghen (Center Back)
9. Eden Hazard (Attacking Midfield/Wing)
10. Yannick Ferreira Carrasco (Attacking Midfield/Wing)
11. Leandro Trossard (Forward)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.008 |
| Pressing | 0.226 |
| Recovery | -0.856 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, GAIN_BELOW_THRESHOLD: 10, INSUFFICIENT_MINUTES: 7.

## V5 role-aware player leaders

1. Dries Mertens — Target Forward; rating 0.5674, VAEP/90 +0.610, xT/90 +0.088, role-adjusted 0.845
2. Thibaut Courtois — Goalkeeper; rating 0.5655, VAEP/90 -0.167, xT/90 +0.003, role-adjusted 0.028
3. Kevin De Bruyne — Progressive Winger; rating 0.5610, VAEP/90 +0.263, xT/90 +0.160, role-adjusted 0.631
4. Thorgan Hazard — Progressive Winger; rating 0.5287, VAEP/90 +0.164, xT/90 +0.127, role-adjusted 0.120
5. Michy Batshuayi Tunga — Target Forward; rating 0.5200, VAEP/90 +0.680, xT/90 +0.031, role-adjusted 0.506

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1955 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.1896 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1443 cumulative Net xG)

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
