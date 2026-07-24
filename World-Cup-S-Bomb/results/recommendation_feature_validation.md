# Recommendation Feature Validation

- Eligible possessions: 9,685
- Fold-specific feature rows: 48,425
- Matches: 64
- History features: 28
- Player and matchup features: 64
- Shot outcomes: 1,207
- Box-entry outcomes: 3,060
- 15-second opponent box transitions: 259
- Attacking xG: 133.758
- 15-second transition xG conceded: 20.470

Team, opponent, and player performance features use only training-fold matches dated before the match being represented. Exact current-possession defensive shape is excluded.

## Checks

| Check | Result |
|---|---|
| Possession IDs are unique within every feature fold | PASS |
| Every possession appears once in each feature fold | PASS |
| All derived inputs are complete | PASS |
| No current-possession outcome column is in model inputs | PASS |
| All 64 matches are represented | PASS |
| Transition box target has at least 200 positives | PASS |
