# Brazil — Team Coaching Report

## Model-grounded summary

Brazil: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -6.128. Strongest positive squad synergy: Thiago Emiliano da Silva + Marcos Aoás Corrêa (0.778). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.7461
- Mean possession EvA gap: 0.004167
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Richarlison de Andrade (Forward)
2. Éder Gabriel Militão (Fullback/Wingback)
3. Raphael Dias Belloli (Attacking Midfield/Wing)
4. Neymar da Silva Santos Junior (Attacking Midfield/Wing)
5. Marcos Aoás Corrêa (Center Back)
6. Carlos Henrique Casimiro (Defensive Midfield)
7. Thiago Emiliano da Silva (Center Back)
8. Vinícius José Paixão de Oliveira Júnior (Central/Wide Midfield)
9. Danilo Luiz da Silva (Fullback/Wingback)
10. Alisson Ramsés Becker (Goalkeeper)
11. Rodrygo Silva de Goes (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.126 |
| Pressing | -6.128 |
| Recovery | 0.692 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 140, GAIN_BELOW_THRESHOLD: 24, INSUFFICIENT_MINUTES: 1.

## V5 role-aware player leaders

1. Neymar da Silva Santos Junior — Progressive Winger; rating 0.6484, VAEP/90 +0.645, xT/90 +0.150, role-adjusted 0.847
2. Vinícius José Paixão de Oliveira Júnior — Progressive Winger; rating 0.6163, VAEP/90 +0.530, xT/90 +0.124, role-adjusted 0.767
3. Raphael Dias Belloli — Progressive Winger; rating 0.6014, VAEP/90 +0.436, xT/90 +0.170, role-adjusted 0.579
4. Gabriel Teodoro Martinelli Silva — Progressive Winger; rating 0.5943, VAEP/90 +0.821, xT/90 +0.203, role-adjusted 0.633
5. Rodrygo Silva de Goes — Progressive Winger; rating 0.5747, VAEP/90 +0.631, xT/90 +0.091, role-adjusted 0.890

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.4708 cumulative Net xG)
- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.4654 cumulative Net xG)
- Against High-Intensity Press: switch from Short Under Pressure to Patient Build-up (0.3857 cumulative Net xG)

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
