# Eight-Pass Ranking Repair Execution Prompt

Use the following prompt to implement the complete ranking repair. It is
intentionally staged: every pass must be independently testable, and no
challenger may replace the current champion merely because selected player
examples look better.

---

## Role and objective

You are the lead football-analytics and ML engineer working in:

`C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb`

Implement an eight-pass repair of the Qatar 2022 player-ranking system. The
final result must correct the known offensive, defensive, goalkeeper, exposure,
and cross-position problems without degrading validated parts of the model.

This is a full implementation task, not an advisory review. Change all
necessary source code, tests, generators, ranking files, audits, documentation,
Markdown reports, JSON reports, figures, aliases, and the final DOCX.

Complete all eight passes in order. Do not stop after producing a plan or after
fixing only the CSVs.

## Current defects that the implementation must address

1. Period-five penalty-shootout kicks enter ordinary outfield goals and related
   performance features. The current feature table reports Messi and Mbappé
   with 9 goals, Paredes and Montiel with 2, and several other false match-goal
   totals.
2. The learned defensive head is degenerate:
   - OOF offense correlation is approximately `0.562`.
   - OOF defense correlation is approximately `0.347`.
   - Interceptions, pressures, duel win rate, and aerial wins receive zero
     learned defensive coefficients.
   - All current CB rows have `role_def_scaled = 0`, as do nearly all FB and DM
     rows.
3. Tournament-v2 initially overconcentrates the top ranks in FW and AM.
4. The unified publication transform then overcorrects toward CB/FB/DM:
   - 155 defenders receive a one-sided lift.
   - Mean positive lift is approximately `0.585` z-score.
   - No within-position recentering follows that lift.
   - Thirteen of the unified top 20 are CB/FB/DM.
5. Minutes dominate the final publication score:
   - Tournament-v2 score/minutes Spearman is approximately `0.332`.
   - Unified score/minutes Spearman is approximately `0.763`.
6. Goal sensitivity falls after publication:
   - Tournament-v2 score/goals Spearman is approximately `0.519`.
   - Unified score/goals Spearman is approximately `0.369`.
7. Multiple reliability and exposure transformations suppress impactful
   short-minute players instead of representing their uncertainty.
8. Goalkeeper order is heavily dominated by an additive `0.20` for every
   shootout save. Four saves can add `0.80` to a base score that is otherwise
   roughly 0–1.
9. The Blom goalkeeper bridge is a percentile-equivalent publication mapping,
   not measured absolute cross-position value, but current reports can imply
   otherwise.
10. The reports, summaries, aliases, player profiles, audits, and DOCX must be
    regenerated from the repaired model. Stale narrative or stale ranking
    values are not acceptable.

## Non-negotiable rules

- Use only Qatar 2022 tournament evidence in scoring.
- Player names, reputations, teams, advancement stage, awards, and external
  rankings must never be scoring features.
- Named players may appear only in generalized post-score audits and
  explanations.
- External 2022 analyses are audit-only. Do not train on them or hand-tune
  weights until individual names occupy preferred places.
- Preserve unrelated working-tree changes.
- Do not create a git commit unless explicitly asked.
- Keep the current model and artifacts as the champion until a challenger
  passes declared gates.
- Corrected data is allowed to change ranks. “No degradation” means no
  statistically meaningful deterioration in held-out prediction,
  calibration, generalized ranking validity, or stability—not preserving
  known-bad ordering.
- Update generators first. Do not manually patch generated CSV, JSON,
  Markdown, profile, figure, or DOCX values.
- Every generated artifact must be reproducible from source code.
- Maintain compatibility aliases where the repository currently promises
  them. Canonical and mirrored summaries must agree byte-for-byte where that is
  the current contract.
- Every pass must add or update tests before promotion.
- If a challenger fails a gate, retain the champion for that component,
  document the failed challenger in the audit, and continue safely. Never hide
  a failed gate.

## Required working method

At the beginning:

1. Inspect `git status` without modifying anything.
2. Trace the current artifact-generation graph.
3. Record the current schemas and hashes.
4. Create a pass checklist and update it as work completes.
5. Run focused tests after each pass.
6. Run the full relevant test suite and artifact validation after Pass 8.

For every pass, report:

- files changed
- formulas or data contracts changed
- tests added
- champion metrics
- challenger metrics
- gate decision
- artifacts regenerated
- remaining risks

Do not declare the task complete while any required artifact contains stale
scores, stale formulas, stale methodology, or references to a retired ranking
layer as the active model.

---

# Pass 1 — Freeze the champion and build the regression harness

## Goal

Create an immutable comparison baseline before changing any ranking behavior.
This pass should not intentionally alter scores.

## Inspect and cover

At minimum:

- `scripts/run_pipeline.py`
- `scripts/refresh_tournament_rankings_v2.py`
- `scripts/unify_tournament_ratings.py`
- `scripts/validate_unified_team_rankings.py`
- `src/models/valuation.py`
- `src/models/tournament_rankings.py`
- `src/models/goalkeeper_valuation.py`
- `src/features/goalkeepers.py`
- `src/features/role_vectors.py`
- `src/reporting/artifacts.py`
- `src/report_generators.py`
- existing ranking and goalkeeper tests

## Implement

1. Add a deterministic champion snapshot/audit utility that captures:
   - source-data hashes
   - configuration
   - ranking schemas
   - artifact hashes
   - model metrics
   - score distributions by position
   - global, team, position, role, and GK ranks
   - correlations with minutes, goals, xG, xA, VAEP, and direct defensive
     evidence
2. Record the current output as `champion` and the repaired version as
   `challenger` or `v3`. Do not overwrite the champion during development.
3. Add bootstrap confidence intervals for metric comparisons.
4. Add leave-one-match-out rank-stability diagnostics.
5. Add leave-one-team-out validation where the target/model structure permits
   it.
6. Add artifact-schema tests for all six-field unified tables and the
   feature-rich rankings.
7. Ensure repeated runs with unchanged inputs produce identical output hashes,
   excluding known nondeterministic document metadata. Normalize DOCX metadata
   if necessary.

## Baseline measurements

Capture, at minimum:

- offense and defense OOF RMSE, MAE, and correlation
- goalkeeper ROC AUC, PR AUC, Brier score, and ECE
- raw-to-final rank Spearman
- score/minutes Spearman
- score/goals Spearman
- position representation in top 20, 50, and 100
- rank changes between base V5, tournament-v2, and unified publication
- number and mean size of defensive lifts
- number of ranked players below 90, 180, and 300 minutes
- bootstrap rank intervals and top-k stability

## Tests

Add regression tests that fail if:

- baseline files are silently overwritten
- schemas drift without an explicit schema-version change
- output becomes nondeterministic
- rank columns disagree with score ordering
- team, position, or role ranks are not internally consistent
- a backup goalkeeper receives a published GK rank

## Exit gate

Pass only when the baseline can be reproduced and compared automatically.
There must be no intentional ranking change in this pass.

---

# Pass 2 — Repair event boundaries and outcome fields

## Goal

Remove penalty-shootout contamination from all ordinary outfield performance
features while preserving shootout evidence separately.

## Primary code targets

- `scripts/build_player_skill_inputs.py`
- `scripts/preprocess_possessions.py`
- `scripts/run_pipeline.py`
- any event/feature aggregation code under `src/features/`
- any code that constructs goals, xG, shots, assists, xT, VAEP, or finishing
  components
- tests for player skill inputs, possessions, tournament rankings, and unified
  rankings

## Implement

1. Create one authoritative event-scope helper, used by every outfield feature
   path:
   - ordinary match performance includes periods 1–4
   - period 5 is shootout-only
2. Do not rely on downstream subtraction. Filter at feature construction.
3. Materialize explicit fields:
   - `open_play_goals`
   - `non_penalty_goals`
   - `regular_penalty_goals`
   - `regulation_extra_time_goals`
   - `assists`
   - `xg_non_shootout`
   - `xa_non_shootout`
   - `shootout_attempts`
   - `shootout_goals`
4. Apply the same boundary to:
   - shots and shots/90
   - xG and xG/90
   - xA and xA/90
   - actual assists
   - xT
   - VAEP and action values
   - finishing and tournament-impact components
5. Preserve the goalkeeper shootout event channel, but keep it completely
   separate from ordinary shot stopping.
6. Add provenance fields documenting the event-period scope.
7. Update data dictionaries and feature definitions.

## Required invariants

- Official tournament match goals reconcile to 172, including own goals under
  the repository’s documented convention.
- Messi ordinary total is 7.
- Mbappé ordinary total is 8.
- Paredes ordinary total is 0.
- Montiel ordinary total is 0.
- Period-five conversions affect only shootout fields.
- Removing a shootout kick does not alter an outfield player’s ordinary
  performance score.
- Non-shootout action counts are unchanged from the champion except where they
  previously included period 5.

Named totals are audit fixtures derived from the event boundary, not
player-specific scoring rules.

## Exit gate

Pass when all goal/event reconciliation tests pass and the challenger can be
regenerated without period-five leakage.

---

# Pass 3 — Repair the learned defensive model

## Goal

Replace or rehabilitate the degenerate learned defensive channel before
changing the final publication transform.

## Primary code targets

- `src/simulation_engine.py`
- `scripts/run_pipeline.py`
- `src/models/valuation.py`
- `src/features/defense_disruption.py`
- `src/features/off_ball.py`
- `src/features/role_vectors.py`
- defensive model tests and grouped-validation tests

## Target redesign

The current defense target is too dependent on an action-type whitelist.
Construct a defensive contribution target based on change in conceding
probability for relevant actions and sequences, regardless of whether the
event type was pre-labelled “defensive.”

Candidate targets should include:

- defensive VAEP / change in conceding probability
- threat removed by interceptions and blocks
- opponent possession-value reduction after pressure
- retained-value clearances
- location- and opportunity-adjusted aerial value
- errors and penalties conceded as negative value
- valid 360-based progression/box-entry suppression where coverage exists

## Feature redesign

Create opportunity-adjusted features, not only per-90 action counts:

- per 100 opponent possessions
- per opponent final-third possession
- per eligible aerial contest
- per pressure opportunity
- action location and pre-action threat
- post-action possession retention
- opponent strength and game state only if they pass the repository’s
  match-disjoint contextual-feature gate

Keep ball progression and possession security as separate CB/FB contribution
channels. Do not treat passing quality as a proxy for defending.

## Challenger models

Evaluate at least:

1. the current positive ElasticNet champion
2. signed Ridge/ElasticNet with regularization
3. a calibrated nonlinear challenger suitable for the sample size

Use nested match-disjoint GroupKFold. Add leave-one-team-out evaluation. Fit
imputation and scaling inside folds.

## Required diagnostics

- coefficient stability across folds
- permutation importance
- prediction distribution by CB/FB/DM
- share of zero or constant predictions
- correlation with direct threat-prevention evidence
- calibration by position and minutes band
- ablations for pressures, interceptions, clearances, aerials, positioning,
  errors, and progression

## Promotion gate

Promote the defensive challenger only if:

- held-out performance is non-inferior by bootstrap confidence interval
- defense correlation improves materially over approximately `0.347`, or the
  alternative target’s predeclared metric improves
- CB/FB/DM predictions do not collapse to zero
- performance is not driven primarily by shots, goals, or key passes acting as
  spurious defensive predictors
- improvements survive leave-one-team-out validation

If no challenger passes, retain the champion defensive model and expose the
failure clearly. Do not compensate with a large publication heuristic.

---

# Pass 4 — Replace the ranking architecture and repeated exposure penalties

## Goal

Separate tournament impact, role quality, and uncertainty. Remove the cascade
of position z-scoring and repeated minutes penalties from the global/team
ranking.

## Primary code targets

- `src/models/valuation.py`
- `src/models/tournament_rankings.py`
- `scripts/unify_tournament_ratings.py`
- `src/models/composite_calibration.py`
- ranking tests and unified ranking tests

## New score contract

Publish three distinct products:

### A. Tournament Impact

A common-unit total contribution score in goals-equivalent or calibrated
action-value units.

Use for:

- `Global Rank`
- `Team Rank`
- global outfield tables
- unified team tables

### B. Role Quality

A single empirical-Bayes posterior rate evaluated through a probabilistic role
mixture.

Use for:

- position rank
- role rank
- role/position leaderboards

### C. Uncertainty

A posterior or bootstrap interval driven by sample size, action opportunities,
and match-to-match variation.

Use for:

- confidence labels
- report explanation
- rank-stability bands

Do not turn uncertainty into additional repeated score penalties.

## Reliability redesign

Replace the current stack of 450-, 180-, and 90-minute shrinkage plus two
exposure multipliers with one fitted empirical-Bayes reliability treatment.

Requirements:

- fit prior strength from held-out likelihood/error or a hierarchical model
- shrink rate quality once
- derive total impact from posterior rate and observed exposure
- publish the interval
- adding empty minutes cannot improve rate quality
- small-sample excellence may remain highly rated with a wide interval

## Cross-position rule

- Do not use within-position z-scores as absolute global value.
- Reporting position changes must not change common-unit Tournament Impact.
- Probabilistic roles may change the Role Quality interpretation but cannot
  manufacture global value.
- If a percentile-equivalent view is retained, label it explicitly and never
  use it for the primary global/team rank.

## Compatibility fields

Keep legacy fields where required for compatibility, but:

- mark them as legacy
- add clear v3 fields
- document active versus retired fields
- do not silently repurpose old columns with different semantics

## Required tests

- same events and contribution values produce the same Tournament Impact
  regardless of reporting position
- adding a positive-value action cannot lower Tournament Impact
- adding an error with negative value cannot raise Tournament Impact
- adding empty minutes cannot improve Role Quality
- score and rank order agree
- player-name permutation leaves all scores unchanged
- team-name permutation leaves individual scores unchanged unless an explicitly
  validated contextual model uses opponent/team features out of fold

## Exit gate

Generate versioned v3 shadow rankings. Do not yet replace active aliases.

---

# Pass 5 — Rebuild offensive outcomes without double counting

## Goal

Reward realized tournament production reliably while preserving expected
process metrics and avoiding duplicate goal credit.

## Primary code targets

- `src/models/tournament_rankings.py`
- `src/models/valuation.py`
- `src/features/events.py`
- `scripts/run_pipeline.py`
- attack and ranking tests

## Implement

1. Separate:
   - non-penalty goals
   - regular penalty goals
   - actual assists
   - xG
   - xA
   - expected action value
   - realized action value
   - shootout outcomes
2. Determine whether the active VAEP/action-value formulation already includes
   shot outcomes.
3. If outcomes are already included:
   - do not add full goals or assists again
   - add only a bounded, reliability-shrunk realization residual such as
     goals-minus-xG and assists-minus-xA
4. If using expected action value:
   - add realized outcomes exactly once through an explicit bounded channel
5. Separate regular penalties from non-penalty output.
6. Keep shootout conversions outside ordinary outfield impact.
7. Remove the current one-sided attacking-realization penalty if its purpose is
   replaced by the explicit process/outcome decomposition.

## Required ablations

Compare:

- process-only
- outcomes-only
- process plus shrunk residual
- process plus full outcomes
- with and without penalties
- with and without xT/VAEP overlap

Report held-out metrics, rank stability, goals sensitivity, and minutes
sensitivity for every candidate.

## Generalized football-validity audits

- Identify every team-leading regulation scorer outside the team top eight.
- Compare productive attackers with zero-output teammates in similar minutes
  bands.
- Report high-impact substitutes separately by rate, total impact, and
  uncertainty.
- Do not force every scorer above every defender or creator.

## Exit gate

Promote only the offensive component whose held-out and stability gates pass.
Named examples should improve only because the generalized scoring logic
improves.

---

# Pass 6 — Rebuild defensive context and remove the publication overcorrection

## Goal

Replace the raw, equally averaged, one-sided direct-defensive lift with
validated threat-prevention evidence.

## Primary code targets

- `scripts/unify_tournament_ratings.py`
- `src/models/tournament_rankings.py`
- `src/features/defense_disruption.py`
- `src/features/off_ball.py`
- 360/spatial feature code
- ranking and defensive-feature tests

## Required defensive evidence

### Interceptions and blocks

Value by:

- pre-action threat
- field zone
- prevented progression
- retained possession
- resulting possession value

### Pressures

Credit a pressure when the sequence:

- reduces opponent possession value
- forces a rushed/failed action
- produces a recovery within a documented time/action window

Do not reward raw pressure volume alone.

### Clearances

Value:

- danger before clearance
- destination
- possession retained or conceded
- opponent threat immediately afterward

### Aerial defense

Use:

- contest opportunities
- expected win probability
- actual win result
- pitch location
- threat value

Do not use a raw aerial-win count as a complete aerial-quality measure.

### Space and line protection

Where StatsBomb 360 coverage is valid, evaluate:

- box-entry prevention
- line-break suppression
- defensive positioning
- receiver pressure
- protected dangerous zones

Missing 360 evidence must remain missing and be reliability-weighted, not
treated as zero.

### On-pitch outcomes

If included, use a hierarchical teammate/opponent-adjusted xG-conceded model
with strong shrinkage. Do not use raw clean sheets or team advancement as
individual evidence.

## Role design

Use probabilistic role mixtures for:

- stopper CB
- covering/sweeper CB
- ball-playing CB
- defensive fullback
- attacking wingback
- holding midfielder
- ball-winning midfielder
- deep playmaker

Avoid one hard role assignment when tournament minutes span multiple roles.

## Remove or constrain the incumbent heuristic

The active one-sided defensive evidence lift should be retired when the
challenger passes.

If temporarily retained:

- cap it tightly
- recenter it
- expose it as a separate diagnostic
- require opportunity adjustment
- prohibit a mean adjustment remotely close to the current `0.585` z-score

## Required audits

- starter defenders below team median
- high-minute defenders with low threat-prevention evidence
- defenders whose rank is driven by progression rather than defense
- defenders whose rank is driven by raw clearances/pressures
- top-20/50/100 position composition
- CB/FB/DM score distributions
- role-specific calibration and stability

## Exit gate

The new defensive component and publication score must pass predictive,
stability, invariance, and cross-position gates. Do not promote solely because
Romero, Otamendi, Molina, Varane, or Amrabat move upward.

---

# Pass 7 — Recalibrate goalkeepers and separate shootout value

## Goal

Preserve the useful dedicated GK branch while preventing shootouts and the
cross-position bridge from dominating interpretation.

## Primary code targets

- `src/features/goalkeepers.py`
- `src/models/goalkeeper_valuation.py`
- goalkeeper sections in `src/models/tournament_rankings.py`
- goalkeeper publication logic in `scripts/unify_tournament_ratings.py`
- goalkeeper tests

## Implement

1. Preserve a dedicated one-main-GK-per-team ranking.
2. Recalibrate the post-shot xG proxy using match-disjoint calibration:
   - compare logistic and isotonic calibration
   - select only on development folds
   - report ROC AUC, PR AUC, Brier score, and ECE
3. Publish separate components:
   - continuous shot stopping
   - high-leverage shot stopping
   - cross/claim control
   - sweeping
   - distribution under pressure
   - regular penalty performance
   - shootout performance
4. Do not let shootout saves add an unbounded `0.20` each to the base score.
5. Choose one of:
   - a bounded shootout contribution capped at 10–15% of the dedicated GK score
   - separate shootout win-probability-added reported outside the continuous GK
     rating
6. Preserve missing-input weight renormalization and reliability shrinkage.
7. Publish score intervals or bootstrap rank stability for keepers.

## Cross-position publication

Preferred:

- convert GK actions to common expected-goals/value-added units for a truly
  comparable team/global impact score

Fallback:

- retain the Blom bridge only as a field named and documented as
  `percentile_equivalent_placement`
- do not describe it as measured absolute performance value

## Required tests

- backup GKs remain unranked
- one main GK per team
- shootout events never enter ordinary shot-stopping features
- adding a shootout save cannot change the continuous shot-stopping component
- bounded shootout contribution cannot exceed its declared cap
- GK order and global mapping preserve monotonicity
- calibration is fitted out of fold

## Exit gate

Promote the GK challenger only on its dedicated gates. It may remain on the
champion model while the outfield v3 ranking is promoted.

---

# Pass 8 — Shadow release, complete artifact regeneration, and promotion

## Goal

Run the repaired system end to end, decide champion versus challenger per
component, promote only passing components, and regenerate every ranking-
dependent artifact and report.

## Release sequence

1. Run the complete pipeline from validated source data.
2. Generate champion and challenger comparison artifacts.
3. Run every pass gate.
4. Select active offense, defense, outfield score, and GK components
   independently.
5. Record all retained champion fallbacks explicitly.
6. Promote the passing configuration.
7. Regenerate every artifact listed below from generators.
8. Run stale-content searches.
9. Run full tests and validation.
10. Refresh manifests, dictionaries, hashes, and documentation.

## Mandatory ranking artifacts

Regenerate and validate:

- `results/reports/ranking/player_rankings.csv`
- `results/reports/ranking/player_rankings_v2.csv`
- `results/reports/ranking/v5_player_rankings.csv`
- `results/reports/ranking/player_rankings.json`
- `results/reports/ranking/v5_player_rankings.json`
- `results/reports/ranking/player_rankings_300plus.csv`
- `results/reports/ranking/global_rankings_outfield.csv`
  - must include all eligible outfield players, including below 300 minutes
- `results/reports/ranking/global_rankings_outfield_300min.csv`
  - must contain only `minutes >= 300`
- `results/reports/ranking/unified_tournament_rankings.csv`
- `results/reports/ranking/goalkeeper_rankings.csv`
- `results/reports/ranking/goalkeeper_rankings_unified.csv`
- all 32 files in `results/reports/ranking/by_team/`
- all 32 files in `results/reports/ranking/by_team_unified/`

If names containing `v2` or `v5` remain compatibility aliases after v3
promotion, document that fact and verify they mirror the active table. Prefer
new versioned v3 files plus deliberate compatibility aliases over silently
changing historical semantics.

Do not delete `results/reports/ranking/legacy/`. Preserve provenance.

## Mandatory ranking methodology and audits

Regenerate:

- `results/reports/ranking/ranking_methodology.md`
- `results/reports/ranking/ranking_audit.md`
- `results/reports/ranking/ranking_audit.json`
- `results/reports/ranking/refresh_manifest.json`
- `results/diagnostics/unified_team_validation.json`
- `results/diagnostics/v2_validation_summary.json` or a versioned v3
  replacement plus documented alias
- all new champion/challenger, bootstrap, invariance, and stability audits
- any model-validation JSON consumed by the summaries

The audit must contain:

- data-integrity results
- champion/challenger metrics with confidence intervals
- pass/fail decision for every gate
- rank stability
- position composition
- minutes and goals sensitivity
- scorer and defender generalized checks
- GK calibration and shootout-cap checks
- retained fallbacks
- zero player-identity/team-identity scoring confirmation

## Mandatory model summaries and Summary aliases

Update the generator, then regenerate:

- `results/reports/canonical/model_summary.json`
- `results/reports/canonical/model_summary.md`
- `results/reports/model_summary.json`
- `results/reports/model_summary.md`
- `results/Summary/model_summary.md`

All model-summary variants must describe:

- active model version
- active champion/challenger selections by component
- corrected event scope
- new score contract
- reliability method
- attack realization treatment
- defensive target and features
- goalkeeper calibration and shootout treatment
- cross-position comparability boundary
- validation metrics and confidence intervals
- every failed or retained fallback

Remove stale claims that:

- the old within-position z-score is the active absolute global value
- the old one-sided defensive lift is active when retired
- each shootout save receives `0.20` when retired
- the Blom bridge is absolute performance value
- the old exposure cascade is active

Canonical JSON must be the structured source for Markdown generation wherever
possible. Mirrors must be synchronized.

## Mandatory final summaries

Update the final-summary generator, then regenerate:

- `results/reports/canonical/final_summary.md`
- `results/reports/final_summary.md`
- `results/reports/final/world_cup_team_performance_and_top_players.md`

The final summaries must include:

- active ranking methodology in plain language
- global leaders
- 300+ minute leaders
- below-300-minute high-impact players with uncertainty
- position and role leaders
- team leaders
- dedicated goalkeeper leaders
- distinction among Tournament Impact, Role Quality, and Uncertainty
- regulation/extra-time outcomes separated from shootouts
- model limitations
- release-gate outcome

Verify mirrored summaries agree where intended. Do not leave old top-player
tables or old ranking explanations in any alias.

## Mandatory DOCX

Update the DOCX generator and produce:

- `results/reports/docs/final_summary.docx`

The repository currently may not contain this file. The generator must be able
to create a complete DOCX from canonical generated inputs when it is missing;
it must not require an old retained document as a template.

Update:

- `scripts/update_unified_final_summary_docx.py`
- `scripts/update_v2_final_summary_docx.py` if it remains active
- any canonical DOCX generation path

The DOCX must contain the same active methodology, ranking tables, goalkeeper
boundary, uncertainty explanation, validation result, and limitations as the
Markdown final summary. It must not merely append a new appendix to stale old
methodology.

Add an automated DOCX text/table validation test that opens the document and
checks:

- required section titles
- active model version
- expected ranking-table headers
- no retired-formula language
- top rows agree with active CSVs
- GK rows agree with the dedicated GK CSV
- document is readable by `python-docx`

Normalize nondeterministic metadata if DOCX hashing is part of the manifest.

## Ranking-dependent reports and profiles

Search for every consumer of ranking fields and regenerate it. This includes,
where ranking values or methodology appear:

- all files in `results/reports/player_profiles/`
- all files in `results/reports/starters/`
- all files in `results/reports/teams/`
- all files in `results/reports/team_profiles/`
- `results/reports/canonical/coaches_notebook.md`
- compatibility copies of the coaches notebook
- ranking figures in `results/reports/v5_figures/` or versioned v3 figures
- any final-report figures or tables

Update `src/reporting/artifacts.py`, `src/report_generators.py`, and report
scripts so these are regenerated rather than manually edited.

Player profiles should show:

- Tournament Impact and rank
- Role Quality and rank
- uncertainty interval/status
- decisive outcomes
- active contribution components
- legacy scores only in a clearly labelled compatibility section, if retained

## Documentation and inventories

Regenerate:

- `results/documentation/reports-rankings.md`
- `results/documentation/reports-profiles.md` if profile schema changes
- `results/documentation/results-dictionary.md`
- `results/documentation/file_dictionary.csv`
- `results/documentation/file_dictionary.json`
- `results/metadata/artifact_manifest.json`
- `results/metadata/feature_definitions.json` if present
- `results/reports/README.md`
- any top-level README sections describing active rankings

Update schema versions and field dictionaries. Document which files are active,
versioned, aliases, or legacy.

## Figures

Regenerate ranking figures from active scores:

- global outfield ranking
- 300+ minute ranking if published
- goalkeeper ranking
- representative team ranking
- model coefficients/importance
- champion-versus-challenger movement
- position composition and rank-stability diagnostics

Do not reuse a stale figure under a current filename.

## Stale-content audit

Search the entire repository for:

- old score formulas
- `shootout_save_points: 0.20`
- old exposure constants
- old within-position z-score descriptions
- old one-sided defensive-lift descriptions
- old top-player values
- old rank values
- stale `v2`/`v5` claims presented as active
- stale DOCX appendix title/methodology

Classify every remaining match as:

- active and correct
- compatibility/legacy and clearly labelled
- test fixture
- stale and requiring correction

## Final validation commands

Run, at minimum:

- focused feature and ranking tests after each pass
- full ranking tests
- goalkeeper tests
- report/artifact-generation tests
- unified team validation
- documentation generation checks
- DOCX validation
- full project test suite where feasible

If a full test cannot run, report the exact reason and run the largest relevant
subset. Do not silently omit failures.

## Final release criteria

The repair is complete only when:

1. All event-boundary tests pass.
2. Every active component has a recorded champion/challenger decision.
3. No promoted component fails predictive non-inferiority.
4. Defensive predictions are nondegenerate.
5. The exposure cascade is removed from the active score.
6. Global/team impact is not created by reporting-position z-scores.
7. Attack outcomes are counted once.
8. Shootouts are separated for outfield players and bounded/separate for GKs.
9. Full and 300+ global rankings are internally consistent.
10. Dedicated and unified GK files agree on GK order.
11. All 32 `by_team` and `by_team_unified` files match the active global source.
12. Audits, methodology, model summaries, final summaries, Summary aliases,
    profiles, figures, manifests, and documentation are regenerated.
13. `results/reports/docs/final_summary.docx` exists and passes content
    validation.
14. No active report contains stale formulas or stale ranks.
15. The final response lists every changed source file, generated artifact
    family, test result, gate decision, retained fallback, and remaining
    limitation.

## Final response format

Return:

1. **Outcome**
   - active model version
   - promoted and retained components
2. **Eight-pass results**
   - one concise subsection per pass
3. **Metric comparison**
   - champion versus challenger with confidence intervals
4. **Ranking behavior**
   - attack, defense, exposure, cross-position, and GK findings
5. **Artifacts**
   - every regenerated artifact family, including Markdown and DOCX
6. **Tests**
   - commands and results
7. **Remaining limitations**
   - unresolved data or model constraints

Do not claim success based only on improved examples. Success requires passing
the generalized gates and complete artifact consistency.

