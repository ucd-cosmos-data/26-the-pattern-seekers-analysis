# United States — Team Coaching Report

## Model-grounded summary

United States: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -0.925. Strongest positive squad synergy: Matthew Charles Turner + Tim Ream (0.756). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.3304
- Mean possession EvA gap: 0.001101
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Tyler Adams (Defensive Midfield)
2. Yunus Dimoara Musah (Central/Wide Midfield)
3. Christian Pulisic (Attacking Midfield/Wing)
4. Tim Ream (Center Back)
5. Antonee Robinson (Fullback/Wingback)
6. Timothy Weah (Attacking Midfield/Wing)
7. Joshua Sargent (Forward)
8. Matthew Charles Turner (Goalkeeper)
9. Sergino Dest (Fullback/Wingback)
10. Weston McKennie (Central/Wide Midfield)
11. Walker Zimmerman (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.068 |
| Pressing | -0.925 |
| Recovery | 0.496 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, GAIN_BELOW_THRESHOLD: 11, INSUFFICIENT_MINUTES: 4.

## V5 role-aware player leaders

1. Christian Pulisic — Progressive Winger; rating 0.6370, VAEP/90 +0.529, xT/90 +0.114, role-adjusted 0.741
2. Matthew Charles Turner — Goalkeeper; rating 0.6048, VAEP/90 -0.123, xT/90 +0.003, role-adjusted 0.158
3. Brenden Aaronson — Progressive Winger; rating 0.5695, VAEP/90 +0.662, xT/90 +0.063, role-adjusted 0.294
4. Antonee Robinson — Attacking Wingback; rating 0.5662, VAEP/90 +0.198, xT/90 +0.085, role-adjusted 0.097
5. Giovanni Reyna — Progressive Winger; rating 0.5555, VAEP/90 +0.369, xT/90 +0.148, role-adjusted 0.939

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.0836 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0715 cumulative Net xG)
- Against Set-Piece Compact Shape: switch from Direct Long Play to Patient Build-up (0.0514 cumulative Net xG)

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
