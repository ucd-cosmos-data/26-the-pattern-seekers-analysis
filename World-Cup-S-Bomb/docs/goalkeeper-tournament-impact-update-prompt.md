# Third implementation prompt — rebuild the Qatar 2022 goalkeeper ranking

## Repository and immutable starting point

Work in:

`C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb`

Start from this verified analytics release:

`PASS8_COMMIT=48b9703797d19931f0ae266d9bfd63d1499a0412`

Before changing anything:

1. Confirm `git rev-parse HEAD` equals `PASS8_COMMIT`.
2. Confirm the working tree is clean.
3. Run the complete existing release suite and confirm all 50 tests pass.
4. Record hashes for the current goalkeeper, unified-ranking, profile, report,
   summary, figure, and manifest artifacts.

This is a new goalkeeper update built on the validated Pass-8 release. Do not
rewrite the eight-pass history or silently alter the outfield model.

---

## Objective

Replace the current public goalkeeper ordering with a transparent
**Qatar 2022 Tournament Goalkeeper Impact** ranking that properly values:

- ordinary non-penalty shot stopping;
- high-leverage and match-saving interventions;
- regular-time and extra-time penalties;
- penalty-shootout impact;
- crosses, sweeping, and distribution;
- the changing value of actions by match state, knockout stage, and time;
- uncertainty and sample size.

The rebuilt ranking must recognize Emiliano Martínez as the tournament's
number-one goalkeeper. This is a release acceptance fixture because his
Golden Glove, two decisive shootouts, and 120th-minute World Cup final save are
material tournament-impact evidence that the current event-profile score
almost discards.

Do **not** achieve this by adding player-name checks, Argentina checks,
award flags, manually assigned player points, or arbitrary post-hoc rank
overrides. Martínez may be named in tests and validation, but identity,
nationality, awards, reputation, and the desired rank must never be model
features.

If a principled tournament-impact model does not place Martínez first, report
the failed gate and diagnose the remaining measurement problem. Do not secretly
tune a single player into first place.

---

## Current baseline and diagnosed defect

The current dedicated v3 ranking is an ordinary event-profile model:

`dedicated_goalkeeper_score_v3 = 0.90 * continuous_goalkeeper_rating_v3 + shootout_component_v3`

Its continuous channel uses:

- 40% continuous non-penalty shot stopping;
- 15% high-leverage shot stopping;
- 13% regular-penalty performance;
- 12% cross/claim control;
- 10% sweeping;
- 10% distribution under pressure.

Although shootouts nominally have a 10% cap, the largest observed shootout
addition is only about `0.0199`. Martínez receives approximately `0.0071` for
three credited shootout saves and ranks 23rd with a score near `0.4038`.

The model is not broadly nonsensical: Szczęsny, Bounou, and Livaković are in its
top five. The central defect is that decisive tournament value is severely
compressed:

- the Kolo Muani save is treated as merely one high-leverage save;
- a 120th-minute save in the World Cup final has no final-specific consequence
  value;
- shootout events receive too little realized influence;
- progression and elimination consequences are absent;
- shootout misses and saves do not have explicit win-probability value;
- the public label can be interpreted as "best goalkeeper" even though the
  current score answers a narrower event-profile question.

Keep the existing v3 score as an auditable baseline. Build a separate active
tournament-impact score rather than disguising a changed estimand as the same
model.

---

## Required model architecture

### 1. Preserve the v3 baseline

Do not delete or mutate these fields:

- `continuous_goalkeeper_rating_v3`
- `shootout_component_v3`
- `dedicated_goalkeeper_score_v3`
- `goalkeeper_rank_v3`
- existing v3 component and uncertainty fields

Retain a frozen v3 artifact for before/after comparison.

### 2. Create an active tournament-impact model

Implement a new versioned model, preferably:

- `src/models/goalkeeper_tournament_impact_v4.py`
- model version: `goalkeeper_tournament_impact_v4`

Publish at minimum:

- `goalkeeper_event_profile_score_v3`
- `goalkeeper_tournament_impact_score_v4`
- `goalkeeper_tournament_impact_rank_v4`
- `ordinary_shot_stopping_value_v4`
- `high_leverage_save_value_v4`
- `regular_penalty_impact_v4`
- `shootout_win_probability_added_v4`
- `cross_claim_value_v4`
- `sweeping_value_v4`
- `distribution_value_v4`
- `goalkeeper_reliability_v4`
- `goalkeeper_score_interval_low_v4`
- `goalkeeper_score_interval_high_v4`
- rank-stability or top-five probability fields

Use one main goalkeeper per team for the 32-player ranking. Backup goalkeepers
remain profile-only and explicitly unranked.

### 3. Replace arbitrary stage bonuses with action-level consequence value

Do not award points merely because a goalkeeper's team reached a later round.
That would mix team achievement into individual performance.

Instead, value each relevant goalkeeper action by the change in the team's
probability of:

- winning the current match;
- surviving an elimination match;
- winning a shootout;
- winning the tournament, when a defensible state model is available.

The leverage calculation must use only information available immediately before
the action:

- score differential;
- match minute and period;
- group versus knockout stage;
- elimination state;
- remaining time;
- shootout sequence state;
- team strength only if estimated without post-event leakage.

Document the state model, assumptions, calibration, and fallback behavior.

### 4. Ordinary shot stopping

Continue to exclude:

- off-target attempts;
- blocked shots;
- regular penalties;
- period-five shootout kicks.

Use the calibrated out-of-fold goal probability for qualifying shots on target.
For each shot, compute:

- expected goal probability;
- actual goal outcome;
- ordinary goal-prevention value;
- pre-action match-state leverage;
- leverage-weighted goal-prevention value.

Do not count the same save in both an unbounded ordinary channel and an
unbounded clutch channel. Publish the decomposition and prove that aggregation
does not double count.

### 5. High-leverage interventions

Replace the coarse high-leverage percentile with action-level consequence
weighting.

The 120th-minute Martínez save against Randal Kolo Muani must be represented by
its actual event record and match state. Do not add a named-player bonus.

Add an audit fixture proving that:

- the event is present;
- it belongs to periods 1–4, not period 5;
- it is classified as a non-penalty shot on target;
- its timestamp and final-match elimination state are correct;
- its leverage value exceeds an otherwise equivalent low-consequence save;
- removing the event lowers Martínez's tournament-impact score.

### 6. Regular penalties

Keep ordinary-match penalties separate from open-play shot stopping.

Use a Bayesian or otherwise regularized estimate and action-level consequence
value. A saved regular penalty may affect both goal prevention and match
probability, but its value must enter exactly once in the final score.

### 7. Penalty shootouts

Replace the compressed shootout bonus with explicit shootout
win-probability-added.

For every period-five kick:

1. Reconstruct score, kick order, kicks remaining, sudden-death state, and
   pre-kick win probability.
2. Calculate post-kick win probability.
3. Attribute goalkeeper impact only when supported by the event outcome.
4. Give full save credit to goalkeeper-credited saves.
5. Do not automatically give full save credit for off-target or woodwork misses.
6. Document any partial-attribution rule for pressure-induced misses.
7. Regularize conversion/save expectations without shrinking realized
   tournament consequence to near zero.

Shootout value must be bounded, but the bound must allow decisive shootout
performance to materially affect a short tournament ranking. Report both raw
and bounded win-probability-added.

Add event-level fixtures for:

- Martínez versus the Netherlands;
- Martínez versus France;
- Livaković versus Japan and Brazil;
- Bounou versus Spain.

### 8. Non-shot goalkeeper work

Retain crosses, claims, sweeping, and distribution as supporting channels.
Re-estimate or retain their weights using a documented method.

These channels must not overwhelm demonstrated goal prevention and decisive
match impact. Missing 360 or event coverage remains missing—not zero—and
available-weight renormalization must remain explicit.

### 9. Reliability and uncertainty

The tournament-impact score must not use one generic minutes shrinkage factor
for every channel.

Use channel-appropriate uncertainty:

- shot-count uncertainty for shot stopping;
- attempt-count uncertainty for regular penalties;
- kick-count and state uncertainty for shootouts;
- opportunity counts for crosses, sweeping, and distribution.

Publish score intervals and bootstrap rank stability. Do not present close
point estimates as certain ordering.

---

## Weight selection and anti-overfitting rules

Do not choose weights solely by searching until Martínez becomes number one.

Use a preregistered candidate set or constrained optimization with documented
criteria:

- predictive calibration for shot outcomes;
- action-level win-probability calibration;
- stability under bootstrap resampling;
- plausible dominance of shot prevention and decisive match impact;
- low sensitivity to a single non-decisive event;
- no identity, team-name, award, or final-rank features;
- leave-one-match-out and leave-one-team-out sensitivity checks.

Before viewing the final ranking, write the candidate grids, bounds, and
selection rule to the audit.

The final report must show:

- selected weights;
- all rejected candidates;
- the selection criterion;
- ranking sensitivity over reasonable alternatives;
- Martínez's rank across the candidate region;
- whether the number-one result is robust or knife-edge.

If Martínez is first only under an extreme or isolated weight combination,
the release gate fails.

---

## External and face-validity validation

External rankings and awards are validation targets, never scoring inputs.

Validate against:

- the official FIFA 2022 Golden Glove result;
- contemporary expert assessments;
- a documented consensus set featuring Martínez, Livaković, Bounou, and
  Szczęsny;
- independent event-statistical goalkeeper assessments where licensing permits.

Required face-validity gates:

1. Emiliano Martínez ranks first in Tournament Goalkeeper Impact v4.
2. At least three of Martínez, Livaković, Bounou, and Szczęsny rank in the top
   five.
3. Martínez's first place is caused by traceable shot, leverage, penalty, and
   shootout events—not identity or advancement points.
4. Removing his final high-leverage save or shootout events lowers his score in
   the expected direction.
5. Shuffling player and team identity labels leaves scores unchanged.
6. Ordinary event-profile v3 values remain byte-for-byte reproducible.

These are publication gates, not permission to alter individual scores after
calculation.

### Prospective reasonable ordering

Use the following full ordering as the preregistered face-validity benchmark for
the consequence-aware model:

1. Emiliano Martínez — Argentina
2. Dominik Livaković — Croatia
3. Yassine Bounou — Morocco
4. Wojciech Szczęsny — Poland
5. Matthew Charles Turner — United States
6. Andries Noppert — Netherlands
7. Mohammed Khalil Al Owais — Saudi Arabia
8. Hugo Lloris — France
9. Jordan Pickford — England
10. Shūichi Gonda — Japan
11. Devis Rogers Epassy Mboka — Cameroon
12. Aymen Dahmen — Tunisia
13. Diogo Meireles Costa — Portugal
14. Alisson Ramsés Becker — Brazil
15. Unai Simón Mendibil — Spain
16. Kasper Schmeichel — Denmark
17. Thibaut Courtois — Belgium
18. Sergio Rochet Álvarez — Uruguay
19. Vanja Milinković Savić — Serbia
20. Mathew Ryan — Australia
21. Seung-Gyu Kim — South Korea
22. Yann Sommer — Switzerland
23. Manuel Neuer — Germany
24. Lawrence Ati-Zigi — Ghana
25. Hernán Ismael Galíndez — Ecuador
26. Milan Borjan — Canada
27. Edouard Mendy — Senegal
28. Seyed Hossein Hosseini — Iran
29. Francisco Guillermo Ochoa Magaña — Mexico
30. Wayne Hennessey — Wales
31. Meshaal Aissa Barsham — Qatar
32. Keylor Navas Gamboa — Costa Rica

Martínez at number one is the strict publication gate. Positions 2–32 are an
expected reasonableness benchmark, not permission to hardcode an exact
permutation. Compare the calculated result against this list using rank
correlation, absolute rank movement, top-five overlap, and documented
event-level explanations for material differences. A defensible evidence-based
deviation is acceptable; unexplained extreme deviations are not.

---

## Required code and test updates

Inspect and update the complete dependency closure, including:

- `src/models/goalkeeper_valuation_v3.py`
- new `src/models/goalkeeper_tournament_impact_v4.py`
- `src/features/goalkeepers.py`
- `scripts/run_ranking_repair_v3.py` or a new versioned release runner
- `src/models/tournament_rankings.py`
- `src/reporting/ranking_repair_release.py`
- unified ranking and publication bridges
- profile, starter, team, canonical summary, and figure generators
- manifests and release audits

Add or update tests covering:

- period boundaries;
- no ordinary/shootout contamination;
- event-level leverage reconstruction;
- no action double counting;
- shootout sequence reconstruction;
- goalkeeper attribution for saves versus misses;
- no identity leakage;
- deterministic output;
- one main goalkeeper per team;
- backup goalkeepers unranked;
- score/rank monotonicity;
- interval and bootstrap reproducibility;
- v3 baseline preservation;
- Martínez number-one acceptance fixture;
- consensus top-five sanity gate;
- all artifact aliases and manifests.

Do not weaken, delete, skip, or xfail existing tests to obtain a green suite.

---

## Ranking propagation and cohort contract

The goalkeeper update is incomplete unless the same v4 truth is propagated to
every ranking surface that contains goalkeepers. Recalculate ranks after the
new goalkeeper placements are merged; never copy old rank numbers into a new
table.

### Dedicated goalkeeper ranking

Update all 32 main goalkeepers in:

- `goalkeeper_rankings_v4.csv` and `.json`;
- canonical `goalkeeper_rankings.csv` and `.json`;
- `goalkeeper_rankings_unified_v4.csv` and `.json`;
- canonical `goalkeeper_rankings_unified.csv` and `.json`.

### Unified global tournament ranking

Regenerate:

- `results/reports/ranking/unified_tournament_rankings.csv`;
- its JSON alias or website payload;
- every file under `results/reports/ranking/by_team_unified/`.

The unified table must still contain 585 ranked players: 553 eligible outfield
players plus 32 main goalkeepers. Replace the old goalkeeper publication bridge
with the v4 bridge, then recompute the complete unified ordering and all global,
team, position, and role rank columns affected by that change.

The bridge must remain explicitly labelled as a cross-position publication
mapping. Do not claim the outfield and goalkeeper raw scores are measured in an
identical absolute unit.

### 300-plus-minute ranking

Regenerate:

- `results/reports/ranking/player_rankings_300plus.csv`;
- its JSON alias or website payload.

This is the all-position 300-plus-minute table. It must remain at 142 rows under
the current eligibility contract: 126 outfield players plus the 16 main
goalkeepers who satisfy `minutes >= 300`. Merge the new v4 goalkeeper placement
for every eligible goalkeeper and recompute the complete 142-player order.

Do not insert goalkeepers into the explicitly outfield-only artifacts:

- `global_rankings_outfield.csv` — 553 outfield players;
- `global_rankings_outfield_300min.csv` — 126 outfield players.

Those two files must remain numerically unchanged except for refreshed
provenance or manifest metadata. Add regression tests proving that the
goalkeeper update changes goalkeeper-containing rankings but does not alter
outfield model scores or outfield-only ordering.

### Rich player table and aliases

Update v4 goalkeeper fields in:

- `player_rankings_v3.csv` and `.json`;
- the canonical `player_rankings.csv` and `.json` aliases;
- any active rich-table successor created by this prompt.

Preserve all valid outfield v3 fields. Add explicit model-version and source
fields so consumers can identify outfield v3 values and goalkeeper Tournament
Impact v4 values without ambiguity.

### Website ranking tabs

The post–Pass-8 website importer must receive consistent data for both player
tabs:

- **Unified tournament ranking:** the regenerated 585-player unified table;
- **300+ minutes:** the regenerated 142-player all-position table.

Both tabs must show the same v4 relative ordering for goalkeepers after applying
the cohort filter. Goalkeeper profiles opened from either tab must use the same
v4 score, components, methodology, and uncertainty fields. No tab may retain
Martínez at v3 rank 23.

Add cross-file tests for every eligible goalkeeper proving agreement among the
dedicated, unified, 300-plus, team, profile, and website-payload artifacts.

---

## Required output artifacts

Create versioned active artifacts:

- `results/reports/ranking/goalkeeper_rankings_v4.csv`
- `results/reports/ranking/goalkeeper_rankings_v4.json`
- `results/reports/ranking/goalkeeper_rankings_unified_v4.csv`
- `results/reports/ranking/goalkeeper_rankings_unified_v4.json`
- `results/diagnostics/ranking_repair/goalkeeper_v4_audit.json`
- `results/diagnostics/ranking_repair/goalkeeper_v4_event_attribution.csv`
- `results/diagnostics/ranking_repair/goalkeeper_v4_sensitivity.json`
- `results/diagnostics/ranking_repair/goalkeeper_v4_rank_stability.csv`
- goalkeeper v4 figures under `results/reports/v4_figures/`

After every gate passes, promote the v4 Tournament Impact ranking to the
canonical goalkeeper aliases consumed by the website:

- `results/reports/ranking/goalkeeper_rankings.csv`
- `results/reports/ranking/goalkeeper_rankings.json`
- `results/reports/ranking/goalkeeper_rankings_unified.csv`
- `results/reports/ranking/goalkeeper_rankings_unified.json`

Keep explicit v3 baseline files and columns available for audit.

Regenerate every dependent artifact from the same run:

- unified tournament ranking with all 585 rows re-ranked;
- 142-player all-position 300-plus-minute ranking;
- all `by_team_unified` ranking files;
- affected player profiles;
- all 593 starter Markdown/JSON pairs;
- all 32 team coaching Markdown/JSON pairs;
- all team profiles;
- canonical model summary;
- canonical final summary;
- coaches notebook;
- DOCX summary;
- figures;
- refresh and master artifact manifests.

No mixed v3/v4 goalkeeper copy may remain in active reports.

---

## Reporting and website contract

Every public report and website payload must clearly distinguish:

- **Event Profile v3** — ordinary multidimensional event performance;
- **Tournament Goalkeeper Impact v4** — consequence-aware Qatar 2022 ranking;
- **Uncertainty** — score interval and rank stability.

The website's primary goalkeeper ordering must use
`goalkeeper_tournament_impact_rank_v4`. Do not relabel the old v3 score as the
new result.

Each goalkeeper profile must explain the reasons for movement. Martínez's
profile must trace his ranking to real event contributions, including ordinary
shot stopping, the final high-leverage intervention, regular penalties, and
both shootouts. Do not use award status as causal evidence in the score.

### Methodology and canonical narrative dependency closure

Fully replace stale goalkeeper-methodology text in:

- `results/reports/canonical/model_summary.md`;
- `results/reports/canonical/model_summary.json`;
- `results/reports/canonical/final_summary.md`;
- `results/reports/canonical/coaches_notebook.md`;
- `docs/final_summary.docx`;
- any active ultimate-model summary, coaches-notebook alias, or generated
  website methodology payload.

Do not append a v4 note beneath obsolete v3 language. Rewrite the active
goalkeeper sections so they consistently explain:

- the distinction between Event Profile v3 and Tournament Impact v4;
- ordinary non-penalty shot scope;
- action-level match and elimination leverage;
- regular-penalty treatment;
- shootout sequence reconstruction and win-probability-added;
- attribution rules for saves, off-target kicks, and woodwork;
- cross, sweeping, and distribution support channels;
- channel-specific reliability and uncertainty;
- the selected formula and weights;
- calibration and validation results;
- cross-position bridge limitations;
- the prospective ordering benchmark and actual result;
- why Martínez moves from v3 rank 23 to v4 rank 1;
- why external awards and consensus were validation evidence rather than
  scoring features.

The final summary must report the final 32-goalkeeper ranking, v3-to-v4 movement,
the top-five stability result, and every release gate. The coaches notebook must
translate the components into practical coaching interpretation without
claiming that the score is a career-strength forecast.

The canonical Markdown, JSON, DOCX, figures, player profiles, team reports, and
website methodology copy must agree on model version, formula, ranks, counts,
and limitations.

Generate at minimum:

- v3 versus v4 rank movement;
- goalkeeper component decomposition;
- shootout win-probability-added;
- high-leverage action contributions;
- score intervals and rank-stability plot;
- top-ten Tournament Goalkeeper Impact ranking.

Use metric-specific scales and label every figure with model version, units,
scope, and source.

---

## Mandatory validation sequence

Run:

1. focused goalkeeper feature tests;
2. goalkeeper v3 regression tests;
3. new goalkeeper v4 tests;
4. ranking and publication-bridge tests;
5. report/artifact-generation tests;
6. the complete existing 50-test Pass-8 release suite;
7. every newly added test;
8. a fresh-clone or clean-tree artifact verification.

The final suite must contain more than the original 50 tests, and every test
must pass.

Verify explicitly:

- 32 ranked main goalkeepers;
- all backup goalkeepers unranked;
- Martínez rank equals 1;
- score order equals rank order;
- no duplicate goalkeeper/team rows;
- no identity scoring features;
- unified tournament ranking contains 585 rows, including all 32 main GKs;
- all-position 300-plus ranking contains 142 rows, including exactly the 16
  main GKs with `minutes >= 300`;
- outfield-only global rankings remain at 553 and 126 rows and retain their
  pre-update score and rank ordering;
- every goalkeeper-containing ranking uses v4 and agrees on cohort eligibility;
- 593 starter Markdown/JSON pairs;
- 32 team coaching Markdown/JSON pairs;
- all selected inputs and generated outputs match refreshed manifests;
- required v4 figures exist and are non-empty;
- canonical summaries and website-facing aliases describe v4 consistently.

---

## Final handoff

Do not call `48b9703797d19931f0ae266d9bfd63d1499a0412` the final goalkeeper-update
commit. It is only the immutable starting point.

After implementation and validation, provide:

1. the new `GK_UPDATE_COMMIT`;
2. the complete test count and passing result;
3. the final 32-goalkeeper v4 ranking;
4. v3-to-v4 rank movement;
5. the selected formula and weights;
6. event-level attribution for Martínez's number-one result;
7. calibration, uncertainty, and sensitivity results;
8. hashes for canonical website inputs;
9. a list of every regenerated dependent artifact;
10. any limitation that remains.

Do not commit or push unless explicitly authorized. Do not edit the website
repository in this task; produce committed analytics inputs that the separate
website-update prompt can consume after `GK_UPDATE_COMMIT` is supplied.
