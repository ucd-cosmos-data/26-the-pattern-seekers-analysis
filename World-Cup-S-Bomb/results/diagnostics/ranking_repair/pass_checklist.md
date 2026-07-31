# Ranking Repair Eight-Pass Checklist

- Active model: `ranking-repair-v3.0-qatar-2022`
- Release: **PASS — promoted all passing v3 components**

| Pass | Decision | Selection/fallback | Tests |
|---|---|---|---|
| 1 | PASS | immutable champion snapshot | tests/test_ranking_repair_champion.py |
| 2 | PASS | qatar-2022-periods-1-4-v1 | tests/test_event_scope.py |
| 3 | PASS | defensive_challenger:signed_ridge | tests/test_defensive_challenger.py |
| 4 | PASS | Tournament Impact / Role Quality / Uncertainty | tests/test_tournament_rankings_v3.py |
| 5 | PASS | process_only | tests/test_tournament_rankings_v3.py |
| 6 | PASS | opportunity-adjusted signed_ridge; legacy lift retired | tests/test_defensive_challenger.py and tests/test_tournament_rankings_v3.py |
| 7 | PASS | goalkeeper_v3 | tests/test_goalkeeper_valuation_v3.py |
| 8 | PASS | active v3 generators and complete artifact family | tests/test_ranking_repair_release_v3.py and DOCX validation |
