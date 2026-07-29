# Croatia — Team Coaching Report

## Model-grounded summary

Croatia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.690. Strongest positive squad synergy: Dominik Livaković + Joško Gvardiol (0.925). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.9757
- Mean possession EvA gap: 0.001566
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Ivan Perišić (Attacking Midfield/Wing)
2. Mateo Kovačić (Central/Wide Midfield)
3. Luka Modrić (Central/Wide Midfield)
4. Joško Gvardiol (Center Back)
5. Andrej Kramarić (Attacking Midfield/Wing)
6. Dominik Livaković (Goalkeeper)
7. Bruno Petković (Forward)
8. Josip Juranović (Fullback/Wingback)
9. Dejan Lovren (Center Back)
10. Marcelo Brozović (Defensive Midfield)
11. Borna Sosa (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.041 |
| Pressing | -2.690 |
| Recovery | 0.290 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, GAIN_BELOW_THRESHOLD: 15.

## V5 role-aware player leaders

1. Ivan Perišić — Wide Creator; rating 0.6035, VAEP/90 +0.432, xT/90 +0.065, role-adjusted 0.413
2. Borna Sosa — Attacking Wingback; rating 0.5514, VAEP/90 +0.129, xT/90 +0.068, role-adjusted 0.068
3. Mislav Oršić — Progressive Winger; rating 0.5462, VAEP/90 +0.086, xT/90 +0.122, role-adjusted 0.963
4. Dominik Livaković — Goalkeeper; rating 0.5458, VAEP/90 -0.130, xT/90 +0.003, role-adjusted 0.053
5. Lovro Majer — Progressive Winger; rating 0.5347, VAEP/90 +0.156, xT/90 +0.076, role-adjusted 0.692

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2061 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2056 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.1470 cumulative Net xG)

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
