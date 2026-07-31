# Implementation prompt — outfield positional balance and opposition context

## Repository and starting point

Work in:

`World-Cup-S-Bomb` (branch `world-cup-sbomb`)

Start from the release state that contains the FIFA-style 55-99 publication
scale and the goalkeeper Tournament Impact v4 diagnostics (Martinez gate
recorded as failed; Event Profile v3 active for goalkeepers). Pin the exact
starting commit as `BALANCE_BASE_COMMIT` once that tree is committed, verify a
clean working tree, and confirm the full release suite passes (116 passed,
1 skipped at time of writing) before changing anything.

This prompt was preceded by a hypothetical validation pass that changed no code. Its findings are embedded below and are binding context: any
implementation must reproduce these diagnostics from the released artifacts
before altering the model.

---

## Objective

Replace the effectively offense-only outfield ordering with a
positionally-balanced, opposition-aware **Tournament Impact v4 (outfield)**
that:

- values defending on the same effective scale as attacking;
- treats player roles as continuous mixtures, not discrete buckets, while
  still evaluating players against their predominant position and the
  offensive/defensive/hybrid sub-roles within it;
- normalizes defensive value for the quality of opponents actually faced, so
  defenders who faced Messi and Mbappe are not punished relative to defenders
  who faced group-stage minnows;
- rewards sustained high-minute contribution on deep runs through evidence
  accumulation and reliability, never through team-advancement bonuses;
- keeps every anti-overfitting rule from the goalkeeper v4 prompt: no
  identity, nationality, award, team-name, or target-rank features, and no
  post-hoc tuning of named players.

Named validation players (fixtures, never inputs): **Jude Bellingham,
Virgil van Dijk, Cristian Romero, Nicolas Otamendi**, plus **Achraf Hakimi**
(attacking-defender fixture) and **Sofyan Amrabat** (screening-midfielder
fixture). **Josip Juranovic** is a watch fixture (see gates).

---

## Diagnosed defects in the active v3 outfield score

The active composite (verified against `run_ranking_repair_v3.py` and
`tournament_rankings_v3.py`) is:

```
impact = vaep_process_without_shot_creation
       + 0.70 * (npxG + 0.76 * penalty_xG)
       + 0.35 * xA
       + 1.0  * defensive_ridge_value        # signed_ridge, alpha=50
```

1. **Variance imbalance.** Across the 553 eligible outfielders:
   `std(attack_component_v3) = 0.798`, range [-0.05, +7.98];
   `std(defensive_component_v3) = 0.075`, range [-0.25, +0.51];
   `corr(defense, impact) = 0.017` vs `corr(attack, impact) = 0.996`.
   Nominal weights are 1:1; realized influence is ~94:6. The ranking is an
   attacking table with a defensive rounding error.
2. **Positional prevention is invisible.** The defensive target only counts
   threat prevented through recorded events. Elite positional defenders
   produce few events precisely because their positioning prevents chances
   from forming. Observed: Van Dijk global #287 (att +0.21, def +0.20),
   Romero #296 (att +0.13, def +0.26), Amrabat #497 (att +0.05, def +0.01),
   while attacking defenders rank via the attack channel alone
   (Juranovic #80, Hakimi #84, Theo Hernandez #85).
3. **No opposition context.** Threat-exposure features charge defenders for
   the quality of attack they faced. Otamendi carries
   `defensive_component_v3 = -0.249` (bottom of the league) after defending
   Mbappe twice, Croatia, and the Netherlands across 734 champion minutes,
   global #478 of 585. A defender's schedule must condition expectation.
4. **Discrete role buckets.** `position_group` cliffs (Fullback vs Wing,
   CB vs DM) flip which implicit expectations apply. Hybrid players are
   scored against the wrong baseline in both directions.
5. **Sub-role blindness.** Within one position, offensive specialists,
   defensive specialists, and hybrids are ranked on one implicit
   (attack-dominated) scale. Hakimi is currently only Morocco's 4th-ranked
   outfielder behind three pure attackers despite carrying 99th-percentile
   defensive value plus near-elite attacking value.

## Hypothetical validation already performed (no code was changed)

- **Variance equalization alone is insufficient and partially harmful.**
  Rescaling defense by the SD ratio (~8-10x) lifts Van Dijk (+~1.6
  attack-equivalents, est. band #60-110) and Romero (+~2.1, est. #50-90) but
  **sinks Otamendi further** (-0.249 becomes ~-2.2) and inflates Juranovic
  (def +0.375 is the highest measured). Conclusion: opposition-context
  adjustment of the defensive target must be applied **before** any variance
  rescaling.
- **Opposition adjustment is the Otamendi fix.** His negative value is an
  artifact of facing the tournament's hardest attacking schedule; prevention
  measured against opponent-conditional expected concession should move his
  channel positive. The implementation must verify this empirically and
  report the before/after decomposition.
- **Continuous role mixtures validate on Hakimi.** With channel weights
  driven by a continuous attacking/defending orientation (constant weight
  sum), Hakimi's combined value exceeds En-Nesyri's attack-only total,
  making him Morocco's top-rated outfielder, matching analyst consensus.
- **Minutes reward is already structurally present (totals), but nullified
  for defenders by the variance imbalance.** Restoring defensive scale plus
  per-channel reliability restores the accumulation reward for Otamendi
  (734 min) and Romero (576 min). No explicit round-reached bonus is needed
  or permitted.
- **Risk identified:** the defensive ridge has OOF Spearman 0.52. Amplifying
  it ~8-10x amplifies its noise equally. Mitigation is mandatory:
  bootstrap-SE shrinkage of per-player defensive value toward the
  opposition-adjusted mean before rescaling, and a hard cap keeping the
  defensive channel's realized variance share at or below parity (50%).

---

## Required model architecture

### 1. Preserve v3

Do not mutate any `*_v3` column, artifact, or test. Publish v4 as new
columns/files exactly as the goalkeeper v4 prompt did:
`tournament_impact_score_outfield_v4`, `tournament_impact_rank_outfield_v4`,
component columns, reliability, and interval fields.

### 2. Opposition-conditional defensive value (order matters: first)

Recompute the defensive target as prevention relative to expected concession
given the opponent's attacking strength, using only pre-match information
(pre-tournament ratings or cumulative pre-match tournament xG; document the
source and prove no post-event leakage). Publish per-player
`defensive_value_raw_v4`, `opponent_attack_strength_faced_v4`, and
`defensive_value_opposition_adjusted_v4`. Add fixtures asserting the
adjustment direction for the hardest and easiest schedules and the
Otamendi before/after decomposition.

### 3. Off-ball prevention term

Add at least one validated positional-prevention feature family that does not
require recorded defensive events: opponent threat suppressed in the
defender's zone of responsibility relative to expectation, and/or
possession-adjusted entry-denial rates, built from the existing 360 frames.
Gate its inclusion on out-of-fold validation, not on fixture movement.

### 4. Continuous role-mixture channel weighting

Compute each player's attacking/defending orientation as a continuous mixture
from existing role vectors and action shares (no new discrete buckets).
Channel weights per player: `w_att + w_def = 1`, bounded away from 0/1
(suggest [0.25, 0.75]) so no player is scored on one channel alone.
Predominant position remains the reporting frame: publish within-position and
within-sub-role ranks (offensive / defensive / hybrid thirds of the mixture
distribution per position) alongside the global rank. Guard against the
known percentile-saturation failure mode: mixtures must be continuous
weights, never within-pool min-max scores.

### 5. Variance-balanced composite with channel reliability — MANDATORY COUPLING

Variance rescaling is only valid **in combination** and **in this order**;
the hypothetical validation proved the uncoupled variant is harmful
(rescaling raw defensive values sinks Otamendi from #478 toward the floor
and inflates the noisiest defensive samples):

```
defensive_value_raw_v4
  -> (2) opposition-conditional adjustment      # required first
  -> (3) off-ball prevention augmentation       # required before scaling
  -> reliability shrinkage (per-channel counts) # required before scaling
  -> variance rescaling to the preregistered share band
  -> (4) role-mixture channel weighting
  -> composite
```

Enforce the coupling structurally, not by convention:

- The composite function must accept **only**
  `defensive_value_opposition_adjusted_v4` (post-shrinkage); passing raw
  defensive values must raise a `ValueError`. There must be no public code
  path that rescales unadjusted defensive values.
- The release audit must record the executed stage order, e.g.
  `defensive_pipeline_stages = ["opposition_adjusted", "prevention_augmented", "reliability_shrunk", "variance_rescaled", "mixture_weighted"]`, and the
  release must abort if any stage is missing or out of order.
- Add a **coupling regression test**: compute the uncoupled variant
  (raw defense, rescaled) in the test only, and assert the released pipeline
  does NOT reproduce it — specifically that Otamendi's v4 rank is above his
  v3 rank (#478), which the uncoupled variant provably violates.

Rescale the (adjusted, shrunk) defensive channel so its realized variance
share across the eligible cohort lands in a preregistered band (suggest
35-50%; grid at minimum {0.35, 0.42, 0.50}). Preregister the full candidate
grid (variance share, mixture bounds, shrinkage constants,
opposition-adjustment variants) and the selection criteria (OOF calibration
unchanged, bootstrap rank stability, single-event sensitivity,
leave-one-match-out) to the audit **before** computing any final ranking,
exactly as the goalkeeper v4 preregistration did.

### 6. Minutes and durability

Keep tournament totals (accumulation is the durability reward). Per-channel
reliability must scale with evidence so that 700-minute defenders' adjusted
defensive value carries more weight than 300-minute samples. Explicit
team-advancement points, round bonuses, or winner bonuses are prohibited —
deep runs must express themselves only through accumulated minutes, harder
opposition faced, and the evidence they generate.

---

## External validation (targets, never inputs)

Collect and cite analyst consensus before finalizing: FIFA Technical Study
Group selections, major-outlet Teams of the Tournament (ESPN, Guardian, BBC,
The Athletic), and statistical tables (WhoScored, SofaScore, FBref) for the
2022 World Cup. Use them only to evaluate the finished ranking.

Face-validity gates (publication blockers):

1. Van Dijk, Romero, and Otamendi all improve by at least 100 global ranks
   versus v3 (from #287 / #296 / #478), with movement traceable to the
   opposition adjustment, prevention term, and variance rebalancing — not to
   any player-specific handling. This should be rasonably mcuh mor and it wouldn't be suprising if Romero and Otamendi broke top 100 and Van Dijk should rasonable brak top 50 and would be fine if in top 30. Don't just go by name value actually adjust the methodology of the modl.
2. Bellingham enters the top 50 with a documented two-way decomposition.
3. Hakimi is the top-ranked Morocco outfielder, consistent with consensus.
4. Amrabat improves materially (from #497) via the off-ball prevention term.
5. Messi remains #1; the attacking top ten is not restructured beyond
   defensible movement (report any attacker falling more than 15 ranks).
6. Juranovic watch fixture: report his movement and its channel attribution;
   if he rises further, the opposition-context section must explain why on
   the evidence, or the weighting region must be reexamined.
7. Identity-shuffle invariance and v3 byte-preservation, as in goalkeeper v4.

If a principled implementation cannot satisfy a gate, report the failed gate
and diagnose the measurement limitation. Do not tune named players.

---

## Propagation, artifacts, tests

Follow the goalkeeper v4 prompt's propagation contract: regenerate every
ranking surface that contains outfielders from one run (unified 585, 300-plus
142, by-team files, profiles, starters, team reports, canonical summaries,
DOCX, figures, manifests); no mixed v3/v4 active copies; explicit
model-version fields; the FIFA-style 55-99 one-decimal publication scale is
retained. Add tests mirroring the existing patterns: preregistration
present-before-results, channel variance-share contract, **the coupling
regression test and stage-order audit assertion from section 5** (raw-input
rejection, recorded stage sequence, Otamendi-above-v3 negative fixture),
opposition adjustment direction fixtures, mixture-bound guards, no identity
leakage, determinism, cohort counts (585/553/142/126), outfield v3
preservation, and every face-validity gate above. Run the complete suite; every test must pass
without weakening any existing test.

## Final handoff

Provide: the new commit id; test counts; the final v4 outfield top 50 and
full four-fixture movement table (v3 rank -> v4 rank with channel
decomposition); selected configuration and full rejected grid; calibration,
stability, and sensitivity results; external-consensus comparison table with
citations; regenerated artifact list with hashes; remaining limitations.
