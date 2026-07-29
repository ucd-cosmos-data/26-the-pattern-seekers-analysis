# Serbia — Team Coaching Report

## Model-grounded summary

Serbia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.400. Strongest positive squad synergy: Nikola Milenković + Saša Lukić (0.615). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.8066
- Mean possession EvA gap: 0.003522
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Aleksandar Mitrović (Forward)
2. Dušan Tadić (Attacking Midfield/Wing)
3. Saša Lukić (Defensive Midfield)
4. Sergej Milinković-Savić (Attacking Midfield/Wing)
5. Nikola Milenković (Center Back)
6. Andrija Živković (Fullback/Wingback)
7. Filip Kostić (Fullback/Wingback)
8. Vanja Milinković Savić (Goalkeeper)
9. Strahinja Pavlović (Center Back)
10. Dušan Vlahović (Forward)
11. Marko Grujić (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.055 |
| Pressing | -2.400 |
| Recovery | -0.287 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 112, INSUFFICIENT_MINUTES: 12, GAIN_BELOW_THRESHOLD: 8.

## V5 role-aware player leaders

1. Filip Kostić — Attacking Wingback; rating 0.5778, VAEP/90 +0.451, xT/90 +0.122, role-adjusted 0.125
2. Dušan Tadić — Progressive Winger; rating 0.5699, VAEP/90 +0.405, xT/90 +0.092, role-adjusted 0.371
3. Vanja Milinković Savić — Goalkeeper; rating 0.5504, VAEP/90 -0.144, xT/90 +0.013, role-adjusted 0.330
4. Andrija Živković — Attacking Wingback; rating 0.5422, VAEP/90 +0.185, xT/90 +0.066, role-adjusted 0.104
5. Nemanja Radonjić — Attacking Wingback; rating 0.5221, VAEP/90 +0.068, xT/90 +0.166, role-adjusted 0.700

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2356 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1686 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1482 cumulative Net xG)

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
