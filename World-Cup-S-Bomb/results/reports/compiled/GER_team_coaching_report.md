# Germany — Team Coaching Report

## Model-grounded summary

Germany: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Antonio Rüdiger + Manuel Neuer (0.657). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.4111
- Mean possession EvA gap: 0.005736
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Joshua Kimmich (Fullback/Wingback)
2. Jamal Musiala (Attacking Midfield/Wing)
3. Serge Gnabry (Attacking Midfield/Wing)
4. Niklas Süle (Fullback/Wingback)
5. Antonio Rüdiger (Center Back)
6. Thomas Müller (Forward)
7. David Raum (Fullback/Wingback)
8. Manuel Neuer (Goalkeeper)
9. Leon Goretzka (Defensive Midfield)
10. Mario Götze (Central/Wide Midfield)
11. Nico Schlotterbeck (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.032 |
| Pressing | 0.154 |
| Recovery | -0.075 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, GAIN_BELOW_THRESHOLD: 9, INSUFFICIENT_MINUTES: 6.

## V5 role-aware player leaders

1. Jamal Musiala — Hybrid Playmaker / Roaming Creator; rating 0.6694, VAEP/90 +0.918, xT/90 +0.158, role-adjusted 0.869
2. Serge Gnabry — Progressive Winger; rating 0.6336, VAEP/90 +0.628, xT/90 +0.076, role-adjusted 0.830
3. Joshua Kimmich — Attacking Wingback; rating 0.5769, VAEP/90 +0.124, xT/90 +0.126, role-adjusted 0.877
4. Leroy Sané — Progressive Winger; rating 0.5759, VAEP/90 +0.592, xT/90 +0.149, role-adjusted 0.578
5. David Raum — Attacking Wingback; rating 0.5730, VAEP/90 +0.294, xT/90 +0.112, role-adjusted 0.143

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.4256 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.2683 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.2539 cumulative Net xG)

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
