# France — Team Coaching Report

## Model-grounded summary

France: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Raphaël Varane + Aurélien Djani Tchouaméni (0.842). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.6468
- Mean possession EvA gap: 0.003107
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Kylian Mbappé Lottin (Forward)
2. Antoine Griezmann (Attacking Midfield/Wing)
3. Aurélien Djani Tchouaméni (Defensive Midfield)
4. Theo Bernard François Hernández (Fullback/Wingback)
5. Adrien Rabiot (Defensive Midfield)
6. Raphaël Varane (Center Back)
7. Jules Koundé (Fullback/Wingback)
8. Hugo Lloris (Goalkeeper)
9. Dayotchanculle Upamecano (Center Back)
10. Marcus Thuram (Central/Wide Midfield)
11. Jordan Veretout (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.105 |
| Pressing | 1.067 |
| Recovery | -0.652 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, GAIN_BELOW_THRESHOLD: 17, INSUFFICIENT_MINUTES: 4.

## V5 role-aware player leaders

1. Kylian Mbappé Lottin — Progressive Winger; rating 0.6558, VAEP/90 +0.625, xT/90 +0.134, role-adjusted 0.694
2. Theo Bernard François Hernández — Attacking Wingback; rating 0.5745, VAEP/90 +0.181, xT/90 +0.047, role-adjusted 0.114
3. Ousmane Dembélé — Progressive Winger; rating 0.5711, VAEP/90 +0.332, xT/90 +0.112, role-adjusted 0.464
4. Antoine Griezmann — Hybrid Playmaker / Roaming Creator; rating 0.5590, VAEP/90 +0.338, xT/90 +0.117, role-adjusted 0.298
5. Eduardo Camavinga — Wide Creator; rating 0.5238, VAEP/90 +0.074, xT/90 +0.072, role-adjusted 0.047

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.3625 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.3060 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.2840 cumulative Net xG)

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
