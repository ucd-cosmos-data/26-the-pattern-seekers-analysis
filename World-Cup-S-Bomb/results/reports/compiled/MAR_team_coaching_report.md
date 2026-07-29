# Morocco — Team Coaching Report

## Model-grounded summary

Morocco: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Sofyan Amrabat + Yassine Bounou (0.877). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 1.4814
- Mean possession EvA gap: 0.003112
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Hakim Ziyech (Attacking Midfield/Wing)
2. Achraf Hakimi Mouh (Fullback/Wingback)
3. Azzedine Ounahi (Central/Wide Midfield)
4. Youssef En-Nesyri (Forward)
5. Sofiane Boufal (Central/Wide Midfield)
6. Sofyan Amrabat (Defensive Midfield)
7. Selim Amallah (Central/Wide Midfield)
8. Romain Saïss (Center Back)
9. Yassine Bounou (Goalkeeper)
10. Yahia Attiyat allah (Fullback/Wingback)
11. Nayef Aguerd (Center Back)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.018 |
| Pressing | 4.404 |
| Recovery | -0.129 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 128, GAIN_BELOW_THRESHOLD: 22, INSUFFICIENT_MINUTES: 4.

## V5 role-aware player leaders

1. Yassine Bounou — Goalkeeper; rating 0.5696, VAEP/90 -0.127, xT/90 +0.003, role-adjusted 0.216
2. Yahia Attiyat allah — Attacking Wingback; rating 0.5451, VAEP/90 +0.156, xT/90 +0.033, role-adjusted 0.086
3. Munir Mohand Mohamedi — Goalkeeper; rating 0.5428, VAEP/90 -0.160, xT/90 +0.003, role-adjusted 0.263
4. Abdessamad Ezzalzouli — Wide Creator; rating 0.5340, VAEP/90 +0.139, xT/90 +0.069, role-adjusted 0.248
5. Noussair Mazraoui — Wide Creator; rating 0.5107, VAEP/90 +0.052, xT/90 +0.018, role-adjusted 0.056

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Short Under Pressure to Patient Build-up (0.3750 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.3232 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.2357 cumulative Net xG)

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
