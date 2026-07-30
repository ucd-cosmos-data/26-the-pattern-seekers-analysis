# Qatar 2022 Player Ranking Methodology — v3

Active model: `ranking-repair-v3.0-qatar-2022`.

## Evidence boundary

All ordinary outfield and continuous goalkeeper evidence is restricted to Qatar 2022 regulation and extra time (StatsBomb periods 1–4). Period 5 is a penalty-shootout channel. Shootout attempts never enter outfield goals, xG, xA, xT, VAEP, finishing, or Tournament Impact.

Player names, team names, reputation, tournament advancement, awards, and external rankings are excluded from scoring. External Qatar 2022 analysis may be used only as a post-score audit.

## Three separate products

1. **Tournament Impact** is a signed total in common action-value units. It determines outfield Global Rank and Team Rank. No within-position z-score, player identity, role bonus, or minutes multiplier creates this value.
2. **Role Quality** is one empirical-Bayes posterior rate. A probabilistic role mixture supplies the prior interpretation; the evidence is shrunk once and is used only for position and role leaderboards.
3. **Uncertainty** is a match-bootstrap interval and rank band. It is reported directly and never becomes another score or minutes penalty.

## Offensive value

The release compares process-only, outcomes-only, process plus a bounded reliability-shrunk realization residual, and process plus full outcomes. Non-penalty goals, regular penalties, assists, xG, xA, expected action value, and realized action value remain explicit. Because VAEP/action value already contains realized shot outcomes, full goals and assists are not added a second time.

Active attack selection: `process_only` (retain_champion).

## Defensive value

The defensive channel targets opportunity-adjusted change in conceding probability and threat prevention. It tests interceptions/blocks, pressure-sequence reductions, retained clearances, location-adjusted aerials, positioning coverage, and errors as signed evidence. Passing progression remains a separate contribution channel and is not a proxy for defending.

Active defense selection: `signed_ridge` (promote_challenger). The legacy one-sided publication lift is not active.

## Goalkeepers

Exactly one main goalkeeper per team is ranked. Continuous shot stopping is calibrated out of fold with match-disjoint development selection between sigmoid and isotonic calibration. Continuous component weights are 40% shot stopping, 15% high-leverage shot stopping, 12% cross/claim control, 10% sweeping, 10% distribution under pressure, and 13% regular-penalty performance. Those weights form 90% of the dedicated score; the separate shootout component is capped at 10%. Missing inputs renormalize the available continuous weights.

Active goalkeeper selection: `goalkeeper_v3` (promote_challenger).

The cross-position goalkeeper fallback is explicitly named `percentile_equivalent_placement`. It is a publication placement, not measured absolute common-unit contribution.

## Compatibility

`player_rankings_v2.csv` and `v5_player_rankings.csv` are byte-identical filename compatibility aliases of the active feature-rich v3 table. Explicit legacy score columns remain available but are preserved, labelled, and not repurposed. `ranking/legacy/` remains the historical archive.
