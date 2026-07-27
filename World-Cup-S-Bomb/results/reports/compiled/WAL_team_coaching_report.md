# Wales — Team Coaching Report

## Model-grounded summary

Wales: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Set-Piece Compact Shape (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: not available. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

- Total wasted Net xG: 0.4194
- Mean possession EvA gap: 0.001831
- Most common optimal style: No meaningful change

## Optimized starting 11

1. Joe Rodon (Center Back)
2. Chris Mepham (Center Back)
3. Aaron Ramsey (Central/Wide Midfield)
4. Ethan Ampadu (Defensive Midfield)
5. Ben Davies (Center Back)
6. Connor Roberts (Fullback/Wingback)
7. Neco Williams (Fullback/Wingback)
8. Kieffer Roberto Francisco Moore (Forward)
9. Wayne Hennessey (Goalkeeper)
10. Harry Wilson (Central/Wide Midfield)
11. Daniel James (Attacking Midfield/Wing)

## Physical matchup deltas

| Matchup | Mean delta |
|---|---:|
| Aerial | -0.031 |
| Pressing | 1.564 |
| Recovery | -0.189 |

## Best bench intervention

> **No validated intervention:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 71, INSUFFICIENT_MINUTES: 6.

## Unified 360-VAEP + xT player leaders

No player cleared the 300-minute V4 evaluation cutoff.

_Only players with at least 300 tournament minutes are ranked. Every player
uses the same cross-role formula: 50% VAEP total per 90, 30% VAEP per touch,
and 20% spatial xT per 90._

## Recurrent tactical mistakes

- Against Set-Piece Compact Shape: switch from Short Under Pressure to Patient Build-up (0.0831 cumulative Net xG)
- Against Compact Pressure Block: switch from Short Under Pressure to Patient Build-up (0.0680 cumulative Net xG)
- Against Wide Retreating Block: switch from Direct Long Play to Patient Build-up (0.0645 cumulative Net xG)

_Counterfactual values are predictive scenario estimates, not causal treatment effects. Substitutions below the gain floor or with confidence intervals crossing zero are suppressed._

<!-- PROSPECTIVE_VALIDATION_START -->
## Prospective possession-model validation

**Overall status: `PARTIAL_PASS_ROLLBACK`.** Box-entry prediction passed every discrimination, calibration, and paired match-bootstrap gate. The shot challenger improved numerically but its confidence interval crossed zero, so it was rejected. The combined prospective artifact was not deployed and the stable production state was preserved.

| Target | Status | Baseline ROC-AUC | Challenger ROC-AUC | PR-AUC | Brier | ECE | Paired ROC gain (90% interval) |
|---|---|---:|---:|---:|---:|---:|---:|
| Box entry | **PASSED** | 0.6888 | 0.7268 | 0.6131 | 0.1722 | 0.0309 | +0.0155 [+0.0106, +0.0205] |
| Shot | **REJECTED** | 0.6642 | 0.6841 | 0.2686 | 0.0960 | 0.0118 | +0.0038 [-0.0030, +0.0120] |

_This challenger is isolated from 360-VAEP/xT player ratings, transition risk, retrospective possession models, and tactical clustering. Player and team descriptive metrics therefore remain unchanged._
<!-- PROSPECTIVE_VALIDATION_END -->

<!-- PLAYER_ROLE_VALIDATION_START -->
## Player-role and valuation validation status

**Production state retained.** The probabilistic role matrix and learned valuation were evaluated as challengers but were not promoted because they missed their predeclared statistical gates.

| Component | Decision | Validation evidence |
|---|---|---|
| Probabilistic GMM roles | **REJECTED** | K=9; silhouette 0.3159; median 500-bootstrap ARI 0.6961 vs required 0.70 |
| Learned Ridge valuation | **REJECTED** | OOF Spearman 0.7095 → 0.7150; gain 95% CI [-0.0053, +0.0165] crosses zero |

The active calibrated 360-VAEP model therefore remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123. Messi remains Argentina rank #1 and Mbappé remains France rank #1; no player-name override was used.
<!-- PLAYER_ROLE_VALIDATION_END -->

<!-- ROLE_AWARE_VALUATION_START -->
## Continuous role-aware valuation A/B test

**Decision: `REJECTED_RETAIN_INCUMBENT`.** The challenger was not promoted. Its Spearman correlation with the incumbent ranking was 0.9854, above the predeclared 0.90 ceiling, so it did not change the overall ordering enough to qualify as the intended systemic correction.

| Benchmark | Incumbent | Challenger diagnostic |
|---|---:|---:|
| Messi global rank | 1 | 1 |
| Mbappé global rank | 2 | 2 |
| Griezmann global rank | 21 | 6 |

The diagnostic Griezmann movement came from creation (0.799), pressing (0.711), and completeness (0.862), with no player-name rule. Nevertheless, all published player/team rankings retain the incumbent 360-VAEP+xT rating.

Foundational model performance remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123, ECE 0.000336.
<!-- ROLE_AWARE_VALUATION_END -->
