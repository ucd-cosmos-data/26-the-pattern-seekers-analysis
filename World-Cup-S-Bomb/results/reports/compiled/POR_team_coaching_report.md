# Portugal — Team Coaching Report

## Model-grounded summary

Portugal: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -4.222. Strongest positive squad synergy: Kléper Laveran Lima Ferreira + Diogo Meireles Costa (0.754). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.7544
- Mean possession EvA gap: 0.001849
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Bruno Miguel Borges Fernandes (Attacking Midfield/Wing)
2. Bernardo Mota Veiga de Carvalho e Silva (Central/Wide Midfield)
3. João Félix Sequeira (Attacking Midfield/Wing)
4. Cristiano Ronaldo dos Santos Aveiro (Forward)
5. João Pedro Cavaco Cancelo (Fullback/Wingback)
6. Kléper Laveran Lima Ferreira (Center Back)
7. Diogo Meireles Costa (Goalkeeper)
8. Rúben Santos Gato Alves Dias (Center Back)
9. Raphaël Adelino José Guerreiro (Fullback/Wingback)
10. Rúben Diogo Da Silva Neves (Defensive Midfield)
11. Otávio Edmilson da Silva Monteiro (Central/Wide Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | 0.006 |
| Pressing | -4.222 |
| Recovery | -0.010 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 123, GAIN_BELOW_THRESHOLD: 16, INSUFFICIENT_MINUTES: 4.

## V5 role-aware player leaders

1. Raphaël Adelino José Guerreiro — Attacking Wingback; rating 0.5849, VAEP/90 +0.263, xT/90 +0.076, role-adjusted 0.113
2. Diogo Meireles Costa — Goalkeeper; rating 0.5730, VAEP/90 -0.122, xT/90 +0.002, role-adjusted 0.278
3. Rafael Alexandre Conceição Leão — Progressive Winger; rating 0.5686, VAEP/90 +0.550, xT/90 +0.059, role-adjusted 0.751
4. Cristiano Ronaldo dos Santos Aveiro — Target Forward; rating 0.5547, VAEP/90 +0.785, xT/90 +0.009, role-adjusted 0.477
5. João Pedro Cavaco Cancelo — Wide Creator; rating 0.5542, VAEP/90 +0.209, xT/90 +0.068, role-adjusted 0.216

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.1823 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.1821 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0995 cumulative Net xG)

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
