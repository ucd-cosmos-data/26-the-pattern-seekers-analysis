# Qatar 2022 Outfield Tournament Impact v4 — Release Audit

- Active model: `outfield-tournament-impact-v4+goalkeeper-event-profile-v3`
- Release status: **passed**
- Players: 593
- Eligible outfielders: 553
- Main goalkeepers: 32
- Unified publication rows: 585
- 300+ minute outfielders: 126
- 300+ minute unified rows: 142

## Coupled defensive pipeline

The release records and validates this exact order:

1. opposition_adjusted
2. prevention_augmented
3. reliability_shrunk
4. variance_rescaled
5. mixture_weighted

Raw defense cannot be published through this writer as a rescaled v4 component.

## Selected configuration

```json
{
  "attack_reliability_constant": 80.0,
  "bootstrap_se_shrinkage_constant": 0.5,
  "bootstrap_top50_jaccard_median": 0.4492753623188406,
  "bootstrap_top50_jaccard_p10": 0.3333333333333333,
  "config_id": 165,
  "defense_reliability_constant": 300.0,
  "defensive_variance_scale_factor": 6.791590615772471,
  "eligible_for_release": true,
  "leave_one_match_out_median_top50_jaccard": 0.9607843137254902,
  "leave_one_match_out_p95_absolute_rank_shift": 11.339999999999979,
  "mixture_bounds": [
    0.25,
    0.75
  ],
  "opposition_adjustment_variant": "fifa_log_rank",
  "opposition_exposure_scale": 1.0,
  "prevention_weight": 0.75,
  "realized_defensive_variance_share": 0.34999999999999987,
  "single_attribution_count": 3387,
  "single_attribution_granularity": "player-match channel contribution",
  "single_attribution_max_absolute_rank_shift": 262.0,
  "single_attribution_p95_absolute_rank_shift": 113.69999999999982,
  "variance_share_target": 0.35
}
```

## Realized defensive variance share

Not separately recorded.

## Full structured audit

See `ranking_audit_v4.json`. Named validation players are post-score fixtures only and never scoring features.
