# Saudi Arabia — Team Coaching Report

## Model-grounded summary

Saudi Arabia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -0.540. Strongest positive squad synergy: Mohammed Khalil Al Owais + Saud Abdullah Abdul Hamid (0.594). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.3206
- Mean possession EvA gap: 0.001534
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Salem Mohammed Al Dawsari (Central/Wide Midfield)
2. Mohammed Kanoo (Central/Wide Midfield)
3. Saud Abdullah Abdul Hamid (Fullback/Wingback)
4. Firas Tariq Nasser Al Albirakan (Central/Wide Midfield)
5. Saleh Khalid Al Shehri (Forward)
6. Nawaf Shaker Al Abid (Attacking Midfield/Wing)
7. Mohammed Khalil Al Owais (Goalkeeper)
8. Sultan Abdullah Salim Al Ghannam (Fullback/Wingback)
9. Ali Albulayhi (Center Back)
10. Abdulelah Al Amri (Center Back)
11. Abdulelah Saad Hameed Al-Malki (Defensive Midfield)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.117 |
| Pressing | -0.540 |
| Recovery | 0.714 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 118, GAIN_BELOW_THRESHOLD: 12, INSUFFICIENT_MINUTES: 2.

## V5 role-aware player leaders

1. Mohammed Khalil Al Owais — Goalkeeper; rating 0.6055, VAEP/90 -0.205, xT/90 +0.001, role-adjusted 0.442
2. Salem Mohammed Al Dawsari — Progressive Winger; rating 0.5861, VAEP/90 +0.469, xT/90 +0.088, role-adjusted 0.624
3. Mohammed Al Burayk — Attacking Wingback; rating 0.5530, VAEP/90 +0.573, xT/90 +0.068, role-adjusted 0.847
4. Abdulrahman Al-Obood — Progressive Winger; rating 0.5383, VAEP/90 +0.586, xT/90 -0.000, role-adjusted 0.501
5. Sami Khalil Al Naji — Progressive Winger; rating 0.5381, VAEP/90 +0.146, xT/90 +0.129, role-adjusted 0.275

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.1140 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.0558 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0500 cumulative Net xG)

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
