# Qatar 2022 Ranking Model Summary

- Active model: `ranking-repair-v3.0-qatar-2022`
- Release status: **PASS — promoted all passing v3 components**
- Ordinary performance scope: periods 1–4
- Shootout-only scope: period 5
- Global/team product: Tournament Impact
- Position/role product: Role Quality
- Confidence product: Uncertainty
- Player/team identity scoring features: none

## Component selections

| Component | Active | Decision |
|---|---|---|
| attack | process_only | retain_champion |
| defense | signed_ridge | promote_challenger |
| outfield_ranking | ranking_repair_v3 | promote_challenger |
| goalkeeper | goalkeeper_v3 | promote_challenger |
| cross_position_goalkeeper | percentile_equivalent_placement | promote_explicit_fallback |

## Active architecture

Tournament Impact is a signed common-unit event-value total. It has no within-position normalization and no repeated minutes/exposure multiplier. Role Quality uses one fitted empirical-Bayes shrinkage step. Uncertainty is a match-bootstrap interval, not a score penalty.

Offensive outcomes are separated into non-penalty goals, regular penalties, assists, xG, xA, expected action value, and realized value. Period-five conversions are excluded. A bounded shrunk realization residual is used only when its generalized held-out gate passes.

Defensive value is based on opportunity-adjusted threat prevention and signed errors. The old one-sided defensive publication lift is retired.

The dedicated goalkeeper score assigns 90% to continuous evidence and at most 10% to the separate shootout component. The cross-position fallback is a percentile-equivalent placement, not absolute common-unit performance.

## Validation and limitations

See `ranking/ranking_audit.json` for confidence intervals, grouped validation, all eight pass gates, retained fallbacks, and generalized post-score checks.
