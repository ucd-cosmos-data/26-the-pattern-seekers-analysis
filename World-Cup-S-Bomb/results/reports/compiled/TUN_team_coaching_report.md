# Tunisia — Team Coaching Report

## Model-grounded summary

Tunisia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.788. Strongest positive squad synergy: Yassine Meriah + Montassar Omar Talbi (0.659). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.1552
- Mean possession EvA gap: 0.000626
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Montassar Omar Talbi (Center Back)
2. Ellyes Joris Skhiri (Defensive Midfield)
3. Youssef Msakni (Attacking Midfield/Wing)
4. Issam Jebali (Forward)
5. Ali Abdi (Fullback/Wingback)
6. Aïssa Bilal Laïdouni (Defensive Midfield)
7. Anis Ben Slimane (Attacking Midfield/Wing)
8. Yassine Meriah (Center Back)
9. Aymen Dahmen (Goalkeeper)
10. Naïm Sliti (Attacking Midfield/Wing)
11. Mohamed Dräger (Fullback/Wingback)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.059 |
| Pressing | -2.788 |
| Recovery | 1.194 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 91, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 5.

## V5 role-aware player leaders

1. Youssef Msakni — Progressive Winger; rating 0.6009, VAEP/90 +0.583, xT/90 +0.084, role-adjusted 0.969
2. Naïm Sliti — Progressive Winger; rating 0.5549, VAEP/90 +0.390, xT/90 +0.093, role-adjusted 0.377
3. Aymen Dahmen — Goalkeeper; rating 0.5405, VAEP/90 -0.112, xT/90 +0.001, role-adjusted 0.247
4. Mohamed Dräger — Deep Playmaker; rating 0.5383, VAEP/90 +0.191, xT/90 +0.037, role-adjusted 0.477
5. Mohamed Ali Ben Romdhane — Wide Creator; rating 0.5311, VAEP/90 +0.209, xT/90 +0.058, role-adjusted 0.110

_Ratings include eligible outfield players from 45 minutes and goalkeepers from 90 minutes. The 300-minute threshold is a high-reliability label. V2 evaluates contextual VAEP behind a development-OOF non-inferiority gate, then uses the accepted feature set with role-weighted offense/defense channels, calibrated composite weights, xD-style disruption, and 450-minute shrinkage._

## Recurrent tactical mistakes

- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0891 cumulative Net xG)
- Against Compact Pressure Block: switch from Direct Long Play to Patient Build-up (0.0468 cumulative Net xG)
- Against Set-Piece Compact Shape: switch from Direct Long Play to Patient Build-up (0.0193 cumulative Net xG)

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
