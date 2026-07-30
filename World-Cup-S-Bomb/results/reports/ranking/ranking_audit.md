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
| impact_minutes_spearman | 0.7634 | 0.4598 | -0.3036 | 0.3908 | 0.5272 | descriptive |
| impact_goals_spearman | 0.3692 | 0.5391 | 0.1699 | 0.4795 | 0.5888 | descriptive |

## Generalized football-validity checks

```json
{
  "below_180_minute_high_impact": [
    {
      "global_rank_v3": 23,
      "minutes_played": 92.58333333333334,
      "player_name": "Niclas Füllkrug",
      "role_quality_v3": 0.909452202077863,
      "team": "Germany",
      "tournament_impact_raw_v3": 2.175273006321479,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 24,
      "minutes_played": 171.88333333333333,
      "player_name": "Gonçalo Matias Ramos",
      "role_quality_v3": 0.8245050613308864,
      "team": "Portugal",
      "tournament_impact_raw_v3": 2.1550738127301137,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 43,
      "minutes_played": 63.51666666666666,
      "player_name": "Romelu Lukaku Menama",
      "role_quality_v3": 0.8949353926888545,
      "team": "Belgium",
      "tournament_impact_raw_v3": 1.755174647937125,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 51,
      "minutes_played": 112.41666666666669,
      "player_name": "Kai Havertz",
      "role_quality_v3": 0.8259352999209535,
      "team": "Germany",
      "tournament_impact_raw_v3": 1.6209526219594803,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 53,
      "minutes_played": 104.83333333333331,
      "player_name": "Andreas Evald Cornelius",
      "role_quality_v3": 0.8340145105187666,
      "team": "Denmark",
      "tournament_impact_raw_v3": 1.6079540477308794,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 55,
      "minutes_played": 170.41666666666666,
      "player_name": "Marcus Rashford",
      "role_quality_v3": 0.4886657424294259,
      "team": "England",
      "tournament_impact_raw_v3": 1.5823135840476654,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 57,
      "minutes_played": 146.76666666666665,
      "player_name": "Henry Josué Martín Mex",
      "role_quality_v3": 0.7850577378694981,
      "team": "Mexico",
      "tournament_impact_raw_v3": 1.5275265994589926,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 65,
      "minutes_played": 126.81666666666663,
      "player_name": "Leroy Sané",
      "role_quality_v3": 0.44063087057365113,
      "team": "Germany",
      "tournament_impact_raw_v3": 1.3424351972499742,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 72,
      "minutes_played": 132.53333333333333,
      "player_name": "Gabriel Teodoro Martinelli Silva",
      "role_quality_v3": 0.5691636740614071,
      "team": "Brazil",
      "tournament_impact_raw_v3": 1.2859693712577263,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 74,
      "minutes_played": 162.46666666666667,
      "player_name": "Joshua Sargent",
      "role_quality_v3": 0.5498896707378645,
      "team": "United States",
      "tournament_impact_raw_v3": 1.272216582212315,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 75,
      "minutes_played": 176.06666666666666,
      "player_name": "Youssef Msakni",
      "role_quality_v3": 0.3970049244437385,
      "team": "Tunisia",
      "tournament_impact_raw_v3": 1.267479136789363,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 79,
      "minutes_played": 118.1,
      "player_name": "Giorgian Daniel De Arrascaeta Benedetti",
      "role_quality_v3": 0.373264660488552,
      "team": "Uruguay",
      "tournament_impact_raw_v3": 1.2251775315297968,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 81,
      "minutes_played": 125.56666666666668,
      "player_name": "Hee-Chan Hwang",
      "role_quality_v3": 0.559118525409741,
      "team": "South Korea",
      "tournament_impact_raw_v3": 1.215387454224661,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 82,
      "minutes_played": 151.71666666666667,
      "player_name": "Lovro Majer",
      "role_quality_v3": 0.4075503292185322,
      "team": "Croatia",
      "tournament_impact_raw_v3": 1.1900854086562516,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 84,
      "minutes_played": 151.9,
      "player_name": "Michy Batshuayi Tunga",
      "role_quality_v3": 0.5494585205729549,
      "team": "Belgium",
      "tournament_impact_raw_v3": 1.1720748037043274,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 92,
      "minutes_played": 111.5,
      "player_name": "Jack Grealish",
      "role_quality_v3": 0.5522952492043369,
      "team": "England",
      "tournament_impact_raw_v3": 1.1124621046342422,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 98,
      "minutes_played": 155.9666666666667,
      "player_name": "Luis Alberto Suárez Díaz",
      "role_quality_v3": 0.693857998285949,
      "team": "Uruguay",
      "tournament_impact_raw_v3": 1.080336078151308,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 105,
      "minutes_played": 133.4,
      "player_name": "Andreas Skov Olsen",
      "role_quality_v3": 0.47726376803448517,
      "team": "Denmark",
      "tournament_impact_raw_v3": 1.0294284321185685,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 108,
      "minutes_played": 161.88333333333335,
      "player_name": "Haji Wright",
      "role_quality_v3": 0.5249926520057207,
      "team": "United States",
      "tournament_impact_raw_v3": 1.0167239975031495,
      "uncertainty_status_v3": "wide"
    },
    {
      "global_rank_v3": 109,
      "minutes_played": 138.68333333333334,
      "player_name": "Sardar Azmoun",
      "role_quality_v3": 0.6697690165225761,
      "team": "Iran",
      "tournament_impact_raw_v3": 1.0056288767703188,
      "uncertainty_status_v3": "wide"
    }
  ],
  "named_eye_test_audit_only": [
    {
      "assists": 3,
      "audit_only_no_scoring_effect": true,
      "global_rank_v3": 16,
      "goals": 2,
      "player": "Harry Kane",
      "team_rank_v3": 1,
      "tournament_impact_v3": 2.764001456685635
    },
    {
      "assists": 1,
      "audit_only_no_scoring_effect": true,
      "global_rank_v3": 6,
      "goals": 2,
      "player": "Robert Lewandowski",
      "team_rank_v3": 1,
      "tournament_impact_v3": 3.3782270155057272
    }
  ],
  "productive_pairwise_ordering_success_rate": 0.8587301587301587,
  "productive_vs_zero_output_similar_minutes_pair_count": 630,
  "team_leading_scorer_gate_passed": false,
  "team_leading_scorers_outside_team_top_eight": [
    {
      "goals": 1,
      "player": "Andreas Christensen",
      "team": "Denmark",
      "team_rank_v3": 9
    },
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
      "Attacking Midfield/Wing": 34,
      "Central/Wide Midfield": 14,
      "Defensive Midfield": 4,
      "Forward": 34,
      "Fullback/Wingback": 14
    },
    "20": {
      "Attacking Midfield/Wing": 10,
      "Central/Wide Midfield": 1,
      "Forward": 9
    },
    "50": {
      "Attacking Midfield/Wing": 20,
      "Central/Wide Midfield": 7,
      "Defensive Midfield": 1,
      "Forward": 21,
      "Fullback/Wingback": 1
    }
  }
}
```

## Interpretation boundary

Named players appear only in post-score audit rows. No named example can promote a component or change a coefficient, weight, prior, or threshold.
