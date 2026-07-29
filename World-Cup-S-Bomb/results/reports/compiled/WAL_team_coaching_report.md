# Wales — Team Coaching Report

## Model-grounded summary

Wales: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Set-Piece Compact Shape (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Chris Mepham + Joe Rodon (0.654). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.4194
- Mean possession EvA gap: 0.001831
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Aaron Ramsey (Central/Wide Midfield)
2. Kieffer Roberto Francisco Moore (Forward)
3. Ethan Ampadu (Defensive Midfield)
4. Gareth Frank Bale (Forward)
5. Chris Mepham (Center Back)
6. Joe Rodon (Center Back)
7. Connor Roberts (Fullback/Wingback)
8. Neco Williams (Fullback/Wingback)
9. Daniel James (Attacking Midfield/Wing)
10. Harry Wilson (Central/Wide Midfield)
11. Wayne Hennessey (Goalkeeper)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.031 |
| Pressing | 1.564 |
| Recovery | -0.189 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 71, INSUFFICIENT_MINUTES: 4, GAIN_BELOW_THRESHOLD: 2.

## V5 role-aware player leaders

1. Brennan Johnson — Ball-Winner; rating 0.5596, VAEP/90 +0.433, xT/90 +0.090, role-adjusted 0.135
2. Neco Williams — Wide Creator; rating 0.5312, VAEP/90 +0.132, xT/90 +0.039, role-adjusted 0.112
3. Connor Roberts — Deep Playmaker; rating 0.5062, VAEP/90 +0.066, xT/90 +0.055, role-adjusted 0.046
4. Daniel James — Ball-Winner; rating 0.4923, VAEP/90 +0.045, xT/90 +0.032, role-adjusted 0.038
5. Daniel Ward — Goalkeeper; rating 0.4892, VAEP/90 -0.327, xT/90 +0.010, role-adjusted 0.394

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Set-Piece Compact Shape: switch from Short Under Pressure to Patient Build-up (0.0831 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.0680 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0645 cumulative Net xG)

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
