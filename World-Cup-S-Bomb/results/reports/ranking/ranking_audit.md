# Qatar 2022 Ranking Repair Audit

- Active model: `ranking-repair-v3.0-qatar-2022`
- Generated from player/team identity-free scoring: **PASS**
- Ordinary event scope: `qatar-2022-periods-1-4-v1`

## Eight-pass gates

| Pass | Decision | Active selection or fallback |
|---|---|---|
| 1 | PASS | immutable champion snapshot |
| 2 | PASS | qatar-2022-periods-1-4-v1 |
| 3 | PASS | defensive_challenger:signed_ridge |
| 4 | PASS | Tournament Impact / Role Quality / Uncertainty |
| 5 | PASS | process_only |
| 6 | PASS | opportunity-adjusted signed_ridge; legacy lift retired |
| 7 | PASS | goalkeeper_v3 |
| 8 | PASS | active v3 generators and complete artifact family |

## Component decisions

| Component | Champion | Challenger | Decision | Active |
|---|---|---|---|---|
| attack | process_only | process_plus_shrunk_residual | retain_champion | process_only |
| defense | positive_elastic_net | signed_ridge | promote_challenger | signed_ridge |
| outfield_ranking | unified_v2_publication | ranking_repair_v3 | promote_challenger | ranking_repair_v3 |
| goalkeeper | goalkeeper_v2 | goalkeeper_v3 | promote_challenger | goalkeeper_v3 |
| cross_position_goalkeeper | Blom bridge described ambiguously | percentile_equivalent_placement | promote_explicit_fallback | percentile_equivalent_placement |

## Champion versus challenger

| Metric | Champion | Challenger | Difference | Ci Low | Ci High | Gate |
|---|---|---|---|---|---|---|
| defense_oof_rmse | 0.0477 | 0.0450 | -0.0027 | -0.0039 | -0.0014 | PASS |
| defense_oof_spearman | 0.4472 | 0.5226 | 0.0755 | 0.0428 | 0.1068 | PASS |
| goalkeeper_brier_score | 0.1972 | 0.1754 | -0.0217 | — | — | PASS |
| goalkeeper_ece | 0.1473 | 0.0699 | -0.0774 | — | — | PASS |
| impact_minutes_spearman | 0.7634 | 0.4698 | -0.2936 | 0.4011 | 0.5371 | descriptive |
| impact_goals_spearman | 0.3692 | 0.5465 | 0.1773 | 0.4879 | 0.5959 | descriptive |

## Generalized football-validity checks

```json
{
  "below_180_minute_high_impact": [
    {
      "global_rank_v3": 21,
      "minutes_played": 171.88333333333333,
      "player_name": "Gonçalo Matias Ramos",
      "role_quality_v3": 0.8697829293988747,
      "team": "Portugal",
      "tournament_impact_raw_v3": 2.299316300885328,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 23,
      "minutes_played": 92.58333333333334,
      "player_name": "Niclas Füllkrug",
      "role_quality_v3": 0.9436371320186367,
      "team": "Germany",
      "tournament_impact_raw_v3": 2.1774286399647487,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 25,
      "minutes_played": 112.41666666666669,
      "player_name": "Kai Havertz",
      "role_quality_v3": 0.9180315601051292,
      "team": "Germany",
      "tournament_impact_raw_v3": 2.1680472813445184,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 53,
      "minutes_played": 104.83333333333331,
      "player_name": "Andreas Evald Cornelius",
      "role_quality_v3": 0.8764830531845313,
      "team": "Denmark",
      "tournament_impact_raw_v3": 1.6907072202971787,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 54,
      "minutes_played": 63.51666666666666,
      "player_name": "Romelu Lukaku Menama",
      "role_quality_v3": 0.9212476645534788,
      "team": "Belgium",
      "tournament_impact_raw_v3": 1.677752555268413,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 55,
      "minutes_played": 170.41666666666666,
      "player_name": "Marcus Rashford",
      "role_quality_v3": 0.5016556437086837,
      "team": "England",
      "tournament_impact_raw_v3": 1.6332584017003002,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 61,
      "minutes_played": 146.76666666666665,
      "player_name": "Henry Josué Martín Mex",
      "role_quality_v3": 0.8127114945799276,
      "team": "Mexico",
      "tournament_impact_raw_v3": 1.4876380439839476,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 64,
      "minutes_played": 155.9666666666667,
      "player_name": "Luis Alberto Suárez Díaz",
      "role_quality_v3": 0.7575695241438137,
      "team": "Uruguay",
      "tournament_impact_raw_v3": 1.430401457161938,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 68,
      "minutes_played": 176.06666666666666,
      "player_name": "Youssef Msakni",
      "role_quality_v3": 0.41388132871329386,
      "team": "Tunisia",
      "tournament_impact_raw_v3": 1.3978702960952358,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 77,
      "minutes_played": 126.81666666666663,
      "player_name": "Leroy Sané",
      "role_quality_v3": 0.43854363284388637,
      "team": "Germany",
      "tournament_impact_raw_v3": 1.257465006099769,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 82,
      "minutes_played": 132.53333333333333,
      "player_name": "Gabriel Teodoro Martinelli Silva",
      "role_quality_v3": 0.5591400028693108,
      "team": "Brazil",
      "tournament_impact_raw_v3": 1.2099862447845788,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 83,
      "minutes_played": 125.56666666666668,
      "player_name": "Hee-Chan Hwang",
      "role_quality_v3": 0.5564011113409506,
      "team": "South Korea",
      "tournament_impact_raw_v3": 1.204829910942031,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 87,
      "minutes_played": 118.1,
      "player_name": "Giorgian Daniel De Arrascaeta Benedetti",
      "role_quality_v3": 0.3724792995103983,
      "team": "Uruguay",
      "tournament_impact_raw_v3": 1.1743695396570806,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 89,
      "minutes_played": 162.46666666666667,
      "player_name": "Joshua Sargent",
      "role_quality_v3": 0.5499006303069451,
      "team": "United States",
      "tournament_impact_raw_v3": 1.1582219656919568,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 90,
      "minutes_played": 151.9,
      "player_name": "Michy Batshuayi Tunga",
      "role_quality_v3": 0.559786972555895,
      "team": "Belgium",
      "tournament_impact_raw_v3": 1.1549643783948165,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 95,
      "minutes_played": 151.71666666666667,
      "player_name": "Lovro Majer",
      "role_quality_v3": 0.40188831851290097,
      "team": "Croatia",
      "tournament_impact_raw_v3": 1.0715846231833905,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 101,
      "minutes_played": 138.68333333333334,
      "player_name": "Sardar Azmoun",
      "role_quality_v3": 0.6992106818127127,
      "team": "Iran",
      "tournament_impact_raw_v3": 1.0454565006405425,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 104,
      "minutes_played": 133.4,
      "player_name": "Andreas Skov Olsen",
      "role_quality_v3": 0.47075188209879143,
      "team": "Denmark",
      "tournament_impact_raw_v3": 1.0261501372347837,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 107,
      "minutes_played": 126.5,
      "player_name": "Kasper Dolberg",
      "role_quality_v3": 0.7822899062312574,
      "team": "Denmark",
      "tournament_impact_raw_v3": 1.0183224394621104,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 109,
      "minutes_played": 111.5,
      "player_name": "Jack Grealish",
      "role_quality_v3": 0.5378140479460877,
      "team": "England",
      "tournament_impact_raw_v3": 0.9958378297392397,
      "uncertainty_status_v3": "wide"
    }
  ],
  "named_eye_test_audit_only": [
    {
      "assists": 3,
      "audit_only_no_scoring_effect": true,
      "global_rank_v3": 11,
      "goals": 2,
      "player": "Harry Kane",
      "team_rank_v3": 1,
      "tournament_impact_v3": 2.939336086659439
    },
    {
      "assists": 1,
      "audit_only_no_scoring_effect": true,
      "global_rank_v3": 4,
      "goals": 2,
      "player": "Robert Lewandowski",
      "team_rank_v3": 1,
      "tournament_impact_v3": 3.6366917241244305
    }
  ],
  "productive_pairwise_ordering_success_rate": 0.8507936507936508,
  "productive_vs_zero_output_similar_minutes_pair_count": 630,
  "team_leading_scorer_gate_passed": false,
  "team_leading_scorers_outside_team_top_eight": [
    {
      "goals": 1,
      "player": "Mohammed Muntari",
      "team": "Qatar",
      "team_rank_v3": 9
    },
    {
      "goals": 1,
      "player": "Kalidou Koulibaly",
      "team": "Senegal",
      "team_rank_v3": 10
    }
  ],
  "top_position_composition": {
    "100": {
      "Attacking Midfield/Wing": 32,
      "Central/Wide Midfield": 15,
      "Defensive Midfield": 6,
      "Forward": 33,
      "Fullback/Wingback": 14
    },
    "20": {
      "Attacking Midfield/Wing": 10,
      "Central/Wide Midfield": 1,
      "Forward": 9
    },
    "50": {
      "Attacking Midfield/Wing": 19,
      "Central/Wide Midfield": 6,
      "Defensive Midfield": 2,
      "Forward": 22,
      "Fullback/Wingback": 1
    }
  }
}
```

## Interpretation boundary

Named players appear only in post-score audit rows. No named example can promote a component or change a coefficient, weight, prior, or threshold.
