# Coaching Input Contract

The recommendation engine uses a canonical internal representation, but external
player and lineup data may arrive in different formats. Import adapters convert
supported sources into this contract before feature engineering.

## Minimum required input

- Team name or stable team identifier
- Opponent name or stable team identifier
- Starting lineup for both teams
- Player name or stable player identifier
- Player position or role

## Preferred input

- Starting lineups and expected formation
- Previous-match event data for every player
- Substitution options
- Match date and competition
- Expected tactical roles or sides

## Supported adapter families

1. StatsBomb-style event CSV or JSON
2. Canonical lineup JSON
3. Player-summary CSV with one row per player
4. Provider-specific event or stat exports through a column-mapping adapter

The engine must never use a player's name as a predictive feature. Names and IDs
are used only to join supplied records. Offensive and defensive skill values are
recomputed from the supplied data.

## Canonical lineup JSON

```json
{
  "schema_version": 1,
  "team": "Example FC",
  "opponent": "Opponent FC",
  "match_date": "2026-08-01",
  "lineup": [
    {
      "player_id": "optional-stable-id",
      "player_name": "Player Name",
      "position": "Right Wing",
      "side": "right",
      "data_source": "statsbomb_events",
      "data_reference": "player-or-team-events.csv"
    }
  ],
  "opponent_lineup": []
}
```

## Flexible-source behavior

- Unknown columns are retained as metadata but are not automatically modeled.
- Recognized columns are mapped to canonical event or player-skill components.
- Missing metrics are estimated from position priors and marked with uncertainty.
- Small samples receive stronger empirical-Bayes shrinkage.
- Unsupported formats produce a mapping report listing required user decisions;
  they do not silently guess column meanings.
