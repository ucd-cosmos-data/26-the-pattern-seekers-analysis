# Goalkeeper ranking rebuild prompt — consolidated single metric (PSxG + clutch v5)

## 0. Read this first — consolidation mandate

This update has one primary product rule:

> **Publish one active goalkeeper ranking, not two.**

Do **not** ship a permanent dual system of “Event Profile / actual” versus
“Tournament Impact” unless consolidation is proven impossible under the gates
below. The historical split confused readers, split website copy, and made it
unclear which list was “the” ranking.

**Required outcome preference (in order):**

1. **Preferred:** one consolidated live score that replaces the active GK
   ranking everywhere (goalkeeper tables, unified/global GK slotting,
   profiles, team reports, website).
2. **Acceptable temporary:** consolidated candidate written to `*_v5` only,
   live aliases unchanged, while gates fail — still one *candidate* metric,
   not two promoted metrics.
3. **Last resort only:** keep two labeled metrics. Allowed only if the audit
   proves that no identity-blind consolidated specification can satisfy the
   face-validity gates in §9 **and** PSxG + clutch integrity. Dual retention
   must be explicitly justified in the audit and must not be the default plan.

Legacy v3 Profile and experimental v4 Impact columns may remain as **frozen
audit baselines**. They are not competing public rankings after a successful
promotion.

**Critical product correction vs earlier draft:** do **not** freeze the live
Profile top five. That order overrates short-sample / low-stakes process
excellence (especially Al Owais at #2 and Turner at #3) and underrates
decisive tournament keeping (especially Martínez). Rebuild the gates around
face-valid tournament value, not continuity of a broken leaderboard.

---

## 1. Repository and immutable starting point

Work in:

`C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb`

Relevant existing state:

- Live / “actual” GK ranking today = Event Profile v3  
  (`dedicated_goalkeeper_score_v3` → `goalkeeper_rank_v3`)
- Experimental Impact v4 exists under `goalkeeper_rankings_v4.*` and was **not**
  promoted (`martinez_first: false`, Martínez Impact #26, consensus gate fail)
- Calibrated post-shot probabilities already exist via
  `calibrate_post_shot_xg_v3` (and related prevention proxies)
- Outfield live ranking already uses Tournament Impact as its single active
  score; GKs are the awkward dual-label case this prompt eliminates

Before changing anything:

1. Record `git rev-parse HEAD` and working-tree cleanliness.
2. Confirm live GK order from
   `results/reports/ranking/goalkeeper_rankings.csv` sorted by
   `goalkeeper_rank_v3`.
3. Record the **defective** live Profile top five as a baseline to beat, not
   preserve:

   | Live rank | Keeper | Team | v5 expectation |
   |---:|---|---|---|
   | 1 | Wojciech Szczęsny | Poland | Remain **high** (top ~8) |
   | 2 | Mohammed Khalil Al Owais | Saudi Arabia | **Demote hard** — not elite; not top 10 |
   | 3 | Matthew Charles Turner | United States | **Demote** from top 3; ~8–12 is plausible |
   | 4 | Yassine Bounou | Morocco | Remain **high** |
   | 5 | Dominik Livaković | Croatia | Remain **high** / elite band |

4. Record Martínez’s live Profile rank (expect ~23) and Impact v4 rank
   (expect ~26) as the dual-metric failure exhibit that v5 must correct.
5. Run the existing release suite; record baseline pass count.
6. Hash goalkeeper, unified, profile, report, summary, figure, and manifest
   artifacts that promotion would touch.
7. Inventory every public surface that currently says “Event Profile” vs
   “Tournament Impact” for goalkeepers. That inventory becomes the
   consolidation rewrite checklist.

This is a **new v5 consolidated model**. Do not rewrite eight-pass outfield
history. Do not silently alter outfield Tournament Impact. Do not pretend v4
was promoted. Do not leave the website describing two active GK rankings after
a successful v5 promotion.

---

## 2. Hypothetical design validation (do this reasoning before coding)

Complete this section in the audit **before** implementing scoring code.

### 2.1 What “actual” and “impact” meant historically

| Historical label | Question it answered | Failure mode |
|---|---|---|
| Event Profile v3 (“actual”) | How good was ordinary keeping process? | Inflated short-sample rate keepers (Al Owais, Turner); compressed shootouts; treated the 120' final save as one more high-leverage save |
| Tournament Impact v4 | How much did actions change match/tournament win probability? | Ordinary prevention weight still dominated; Martínez stayed ~#26; never promoted; created a second list |

Having both live was never necessary for outfielders (Impact *is* their
ranking). For GKs it was a labeling patch. Retire the split.

### 2.2 Why a single consolidated metric is preferable

One public question:

> How valuable was this goalkeeper’s tournament performance when shot
> difficulty (PSxG), ordinary prevention, late/match-decisive interventions,
> penalties/shootouts, and support actions are valued coherently — with
> harder opposition and deeper knockout states mattering somewhat, without
> turning team pedigree into a hard rank bonus?

If v5 is specified correctly, “actual” and “impact” become the **same**
published ordering.

### 2.3 Why PSxG is the integrity check-back

Without post-shot difficulty, keepers who face many weak shots look elite on
save counts. With PSxG:

- easy shot (low PSxG): save ≈ little credit; concede ≈ large penalty;
- hard shot (high PSxG): save ≈ large credit; concede ≈ small penalty.

This is mandatory primary shot-stopping math.

### 2.4 Why clutch must be explicit inside the same score

The Kolo Muani 120th-minute World Cup final save must be high PSxG × high
clutch, not “one more save.” Late regulation, ET, and match-preserving saves
need an explicit channel inside the **same** score — not a second ranking.

### 2.5 Face-validity redesign (replaces top-five freeze)

**Do not freeze the live top five.**

Validated expectations for the consolidated ranking:

| Keeper | Live Profile | Required / expected v5 treatment |
|---|---:|---|
| Martínez | ~23 | **Hard:** top **10**. **Target band:** top **3** is desirable and should be achievable without name hacks if PSxG+clutch+shootouts work. Need not be #1. |
| Livaković | 5 | Stay **elite / high** (typically top ~5–6) |
| Bounou | 4 | Stay **high** (typically top ~6–8) |
| Szczęsny | 1 | Stay **high** (typically top ~8); may fall from #1 |
| Lloris / Noppert / Costa / similar deep-run keepers | mid/low | May rise with honest volume + leverage; keep plausible |
| Turner | 3 | **Hard:** not top 3. **Soft band:** around **8–12** is reasonable |
| Al Owais | 2 | **Hard:** not top 10. Group-stage short-sample rate excellence is **not** elite tournament keeping. He should not be in the conversation for podium / top-tier slots |

**Opposition / team-quality prior (soft, not mandatory rank order):**

- Facing stronger attacks and surviving deeper knockout rounds may raise
  value **somewhat** through shot difficulty, leverage, and schedule — not
  through a raw “better team ⇒ +N ranks” feature.
- Weaker-schedule keepers can still outrank stars if PSxG + clutch evidence
  says so.
- Do **not** encode FIFA ranking, market value, or “big team” labels as
  features. If opposition strength is used, it must come from pre-action
  shot/state/opponent-attack strength already estimable in-repo without
  identity leakage.

### 2.6 Martínez top-10 / top-3 validation logic

Why Martínez must be **definitely top 10** in a consolidated tournament rating:

- two decisive shootouts with credited saves;
- 120' World Cup final high-PSxG save;
- full champion minutes / elimination exposure;
- Golden Glove is **validation only**, never a feature.

Why he need **not** be forced to #1:

- v4’s Martínez-first hard gate encouraged overfit and still failed when
  ordinary prevention dominated;
- Livaković / Bounou / Szczęsny can honestly compete for #1–3 on PSxG +
  volume + shootouts.

Why **top 3 is a target, not a vanity pin:**

- If PSxG + clutch + shootout WPA are working, Martínez should land in or
  near the podium band without name checks.
- Hard gate = top 10. Soft/promotion-preferred gate = top 3.
- If he is top 10 but outside top 3, pass hard gates and report whether top 3
  failed because of weight bounds, missing clutch definition, or genuine
  PSxG weakness — do not secretly add points.

### 2.7 Why Al Owais and Turner must be gated downward

**Al Owais (live #2):**

- short sample / group-stage profile;
- elite continuous rates without equivalent knockout / clutch / shootout
  corpus;
- must not occupy elite consideration under a tournament-value estimand;
- **hard gate: outside top 10.**

**Turner (live #3):**

- respectable US run, but not Profile-#3 tournament value;
- **hard gate: outside top 3;**
- **soft: around 8–12 is plausible;** outside 6–15 needs explanation.

### 2.8 When dual metrics would be “absolutely necessary”

Only if:

1. No identity-blind consolidated config satisfies §9 hard gates;
2. Audit shows PSxG+clutch integrity still wants a diagnostic secondary view;
3. Owner explicitly accepts dual retention after reading the diagnosis.

Until then, assume one metric.

Write the pre-code validation conclusion into
`results/diagnostics/ranking_repair/goalkeeper_v5_preregistration.json`
under `consolidation_decision` and `face_validity_gates_preregistered`.

---

## 3. Objective

Build and (if gates pass) **promote** a single active ranking:

**Goalkeeper Consolidated Value v5 = PSxG-checked prevention + clutch +
bounded penalties/shootouts + bounded support (+ optional opposition-adjusted
difficulty already inside PSxG/leverage)**

That one score must:

1. Use **PSxG / Expected Saves** as the primary shot-stopping check-back;
2. Include an explicit **clutch function** for late and match-decisive saves;
3. Absorb useful Impact v4 ideas into the same score;
4. Replace Event Profile v3 as the live public GK ordering after promotion;
5. Place **Martínez definitely in the top 10**, with **top 3 as the preferred
   target band** (not a forced #1);
6. Keep other true elite / deep-run keepers **high** (Livaković, Bounou,
   Szczęsny, and other evidence-backed names);
7. **Demote** Profile-inflated names: Al Owais out of elite consideration;
   Turner out of the podium;
8. Allow stronger opposition / deeper knockout exposure to matter **somewhat**
   via difficulty and state — not via pedigree bonuses;
9. Remain identity-blind in features;
10. Avoid shipping two competing public GK leaderboards.

---

## 4. Non-negotiables

- **One active public GK ranking after successful promotion.**
- No player-name, nationality, award, Golden Glove, or desired-rank features
  inside the scorer.
- No post-hoc swapping of names into slots after scoring.
- No deletion of frozen v3/v4 audit fields/columns.
- No promotion on partial **hard** gates.
- No team-round participation bonus as a raw feature (“reached final ⇒ +points”).
- No “big team ⇒ higher rank” hard rule; opposition may matter only through
  measurable shot difficulty / state / attack strength.
- No double counting the same save in ordinary PSxG and clutch without an
  explicit decomposition.
- Raw save totals are not an acceptable primary shot-stopping score.
- Do **not** freeze live Profile ranks 1–5.
- Do **not** revive a Martínez-must-be-#1 hard gate.
- Prefer fail-closed over cosmetic pins or dual peer leaderboards.

Named keepers may appear in **tests and gates** as acceptance fixtures. They
must never appear as model features.

---

## 5. Estimand definition (single metric)

### 5.1 Public estimand

`goalkeeper_consolidated_value_v5` estimates a keeper’s Qatar 2022 tournament
contribution to preventing goals and preserving match-winning states, where:

- shot difficulty is measured post-shot (PSxG);
- timing and match state scale prevention (clutch / leverage);
- penalties and shootouts are explicit, bounded channels;
- support is secondary;
- facing tougher chances / deeper elimination states can raise value
  somewhat through those channels;
- uncertainty and sample size regularize short-sample rate mirages.

### 5.2 Public label after promotion

One name everywhere, e.g.:

- **Goalkeeper Tournament Rating (v5)**  
  or  
- **Goalkeeper Ranking (PSxG + Clutch)**

Do **not** label the promoted ranking “Impact” beside a second “Actual”
list. Archived Profile v3 may appear only as audit history.

### 5.3 Relationship to old metrics

| Metric | After v5 success | After v5 fail-closed |
|---|---|---|
| Profile v3 | Archived baseline | Remains live |
| Impact v4 | Archived experiment | Archived experiment |
| Consolidated v5 | **Sole live GK ranking** | Candidate-only `*_v5` |

---

## 6. Required model architecture

### 6.1 Preserve baselines

Do not mutate v3 dedicated fields or existing v4 impact fields. Keep frozen
comparison artifacts.

### 6.2 Implement v5 module

Preferred paths:

- `src/models/goalkeeper_consolidated_value_v5.py`
- model version: `goalkeeper_consolidated_value_v5`
- release driver: `scripts/run_goalkeeper_v5_release.py`

### 6.3 Published fields (minimum)

Passthrough / archive:

- `goalkeeper_event_profile_score_v3`
- `goalkeeper_rank_v3`
- `goalkeeper_tournament_impact_score_v4` / `rank_v4` if present

Active consolidated fields:

- `goalkeeper_consolidated_value_raw_v5`
- `goalkeeper_consolidated_value_score_v5`
- `goalkeeper_consolidated_value_rank_v5`
- `psxg_shot_stopping_value_v5`
- `psxg_goals_prevented_v5`
- `psxg_mean_difficulty_faced_v5`
- `psxg_easy_shot_share_faced_v5`
- `psxg_hard_shot_share_faced_v5`
- `opponent_attack_strength_faced_v5` (if used; else document absence)
- `clutch_save_value_v5`
- `late_game_prevention_value_v5`
- `match_winning_save_value_v5`
- `state_leverage_prevention_value_v5`
- `regular_penalty_impact_v5`
- `shootout_win_probability_added_raw_v5`
- `shootout_win_probability_added_v5`
- `cross_claim_value_v5`
- `sweeping_value_v5`
- `distribution_value_v5`
- `support_composite_v5`
- `goalkeeper_reliability_v5`
- score/rank uncertainty intervals
- `v5_selected_config_id`
- `v5_consolidation_status` ∈ {`promoted_single_metric`, `candidate_only`, `dual_metric_fallback`}
- `active_goalkeeper_rank_field`

One main goalkeeper per team (32 ranked). Backups unranked.

---

## 7. Channel specifications

### 7.1 Channel A — PSxG / Expected Saves (primary)

Reuse `calibrate_post_shot_xg_v3` (or current calibrated successor).

Scope: ordinary non-penalty on-target shots, periods 1–4. Exclude off-target,
blocked, regular penalties, period-5 shootouts.

For each shot:

- `p_psxg` = calibrated post-shot goal probability;
- `y` = 1 if goal else 0 under keeper attribution rules;
- `prevention = p_psxg - y`.

Easy save ⇒ little credit; hard save ⇒ large credit; soft goal against ⇒
large penalty.

Aggregate with shot-count reliability shrinkage — this is a main weapon
against Al Owais-style short-sample inflation.

Diagnostics required:

- correlation(raw saves, score) vs correlation(PSxG prevention, score);
- mean PSxG faced;
- easy vs hard save rates;
- goals prevented above/below PSxG.

### 7.2 Channel B — Clutch (explicit, same score)

Pre-action inputs only: minute/period/ET, score diff, group vs knockout,
time remaining, simple match-state threat.

Required:

1. Final ~15 min regulation + all ET uplifted vs early/mid regulation.
2. Match-preserving / match-winning contexts extra uplift.
3. Clutch scales difficulty-checked prevention; low-PSxG soft shots stay
   low-value even late.
4. No team progression points; no identity features.

Mandatory fixture: Kolo Muani 120' save = high clutch × high PSxG; removal
lowers Martínez’s consolidated score.

### 7.3 Channel C — State leverage on non-clutch shots

Retain general pre-action leverage for non-late shots. Document anti-double-
count rule vs clutch with a numeric example.

### 7.4 Optional opposition difficulty (soft “better teams / harder chances”)

If used:

- prefer opponent attack strength, shot quality already in PSxG, or
  pre-action chance quality;
- never use final tournament placement, awards, or team reputation labels;
- effect must be “somewhat higher,” not a hard sort key.

If not used, say so and rely on PSxG + knockout state alone.

### 7.5 Channel D — Regular penalties

Separate, regularized, enter once.

### 7.6 Channel E — Shootouts

Explicit WPA; credited saves only; woodwork/off-target = 0 on main path;
bound influence; report raw + bounded.

Fixtures: Martínez vs Netherlands / France; Livaković vs Japan / Brazil;
Bounou vs Spain.

### 7.7 Channel F — Support

Cross/claim, sweeping, distribution; bounded; missing ≠ silent zero.

---

## 8. Score skeleton and weight search

### 8.1 Skeleton

```text
consolidated_raw_v5 =
    w_psxg   * psxg_shot_stopping_value_v5
  + w_clutch * clutch_save_value_v5
  + w_lev    * state_leverage_prevention_value_v5   # 0 if folded into clutch
  + w_pen    * regular_penalty_impact_v5
  + w_so     * shootout_win_probability_added_v5
  + w_supp   * support_composite_v5
```

### 8.2 Preregistration constraints

Write grid to disk before selection:

- `w_psxg` largest single weight;
- `w_psxg + w_clutch >= 0.55`;
- `w_so <= 0.20` before additional bound;
- `w_supp <= 0.25`;
- `w_pen <= 0.10`;
- no identity / award / round-reached / “big club” features;
- clutch and shootout bounds as grid dimensions.

### 8.3 Selection rule

Among identity-blind configs:

1. Filter to configs that pass **all hard gates in §9**.
2. Among survivors, prefer configs that also pass **soft / preferred gates**
   (Martínez top 3; Turner in 8–12; elite keepers clustered high).
3. Maximize documented integrity (PSxG concordance, clutch monotonicity,
   bootstrap stability, low sensitivity to one easy save).
4. If no config passes hard gates, fail-closed (§14). Do not pin names.

Do **not** choose weights solely by searching until Martínez is #1.
Do **not** choose weights solely by preserving live Profile order.

---

## 9. Face-validity gates (replaces top-five freeze)

Named players below are **acceptance fixtures for tests/gates only**.

### 9.1 Hard gates (must all pass to promote)

| ID | Gate | Pass condition |
|---|---|---|
| H1 | Martínez top 10 | `rank(Martínez) <= 10` |
| H2 | Al Owais not elite | `rank(Al Owais) >= 11` (outside top 10) |
| H3 | Turner not podium | `rank(Turner) >= 4` (outside top 3) |
| H4 | Elite core stays high | At least **3 of** {Martínez, Livaković, Bounou, Szczęsny} in **top 8** |
| H5 | No Profile mirage podium | Neither Al Owais nor Turner in top 3 |
| H6 | Identity-blind | Name/team shuffle leaves scores unchanged |
| H7 | PSxG integrity | Shot-stopping channel is PSxG-based; raw save count is not the sort key |
| H8 | Clutch monotonicity | Removing Kolo Muani final save lowers Martínez |
| H9 | Shootout monotonicity | Removing credited shootout saves lowers affected keepers’ shootout channel |
| H10 | Single-metric consolidation | Promotion sets one active GK rank field; no peer Impact list |
| H11 | No pedigree feature | Team reputation / awards / final placement not in model matrix |
| H12 | Baseline preservation | v3/v4 audit fields remain available and unmodified |

### 9.2 Soft / preferred gates (report; use in config selection among H-survivors)

| ID | Gate | Preferred condition |
|---|---|---|
| S1 | Martínez podium band | `rank(Martínez) <= 3` |
| S2 | Turner reasonable band | `8 <= rank(Turner) <= 12` (or explain if 6–7 / 13–15) |
| S3 | Al Owais far from elite | `rank(Al Owais) >= 15` preferred |
| S4 | Livaković elite | `rank(Livaković) <= 6` |
| S5 | Bounou high | `rank(Bounou) <= 8` |
| S6 | Szczęsny high | `rank(Szczęsny) <= 8` |
| S7 | Deep-run keepers not crushed | median rank among {Lloris, Noppert, Costa, Pickford} better than live Profile median for that set |
| S8 | Opposition/difficulty gradient | mean PSxG faced or opponent-attack faced rises toward the top third of the table **somewhat** (correlation soft-check, not hard sort) |

**Promotion rule:**

- All **H** gates required.
- **S1 (Martínez top 3)** is strongly preferred: if multiple configs pass all H
  gates, choose one that also passes S1 when integrity is comparable.
- Failing S1 alone does **not** fail the release if H1 passes — but the audit
  must diagnose why top 3 was missed.
- Failing H1 (Martínez outside top 10) **does** fail the release.

### 9.3 Explicit non-gates

These are **not** required:

- Martínez #1;
- freezing Szczęsny #1 / Al Owais #2 / Turner #3;
- exact expert consensus ordering for all 32;
- monotonic rank by team strength.

---

## 10. Full validation / engineering gates

In addition to §9:

1. Consolidation decision recorded before selection.
2. No double-count proof for PSxG vs clutch.
3. Reliability / shrinkage prevents one soft save from creating elite ranks
   (unit + diagnostic).
4. Uncertainty intervals + rank stability published.
5. Website/report language presents one live GK ranking after promotion.
6. Release suite green + new v5 unit tests (§16).

---

## 11. Comparison artifacts

`results/diagnostics/ranking_repair/goalkeeper_v5_rank_comparison.csv`

Columns at minimum:

- player, team
- rank_profile_v3
- rank_impact_v4
- rank_consolidated_v5
- delta_v5_minus_v3
- delta_v5_minus_v4
- psxg_shot_stopping_value_v5
- clutch_save_value_v5
- shootout_win_probability_added_v5
- support_composite_v5
- gate_flags (e.g. martinez_top10, al_owais_outside_top10, turner_outside_top3)
- notes

Audit prose must explain:

- why Al Owais and Turner moved down;
- why Martínez entered top 10 (and whether top 3);
- why Livaković / Bounou / Szczęsny stayed high or moved;
- which Profile and Impact ideas were absorbed into the single metric;
- why a second live list is unnecessary.

---

## 12. Artifacts to write

- `results/reports/ranking/goalkeeper_rankings_v5.csv`
- `results/reports/ranking/goalkeeper_rankings_v5.json`
- `results/diagnostics/ranking_repair/goalkeeper_v5_audit.json`
- `results/diagnostics/ranking_repair/goalkeeper_v5_preregistration.json`
- `results/diagnostics/ranking_repair/goalkeeper_v5_event_attribution.csv`
- `results/diagnostics/ranking_repair/goalkeeper_v5_sensitivity.json`
- `results/diagnostics/ranking_repair/goalkeeper_v5_rank_stability.csv`
- `results/diagnostics/ranking_repair/goalkeeper_v5_rank_comparison.csv`
- `results/diagnostics/ranking_repair/goalkeeper_v5_gate_report.json`
- figures under `results/reports/v5_figures/` as needed

`goalkeeper_v5_audit.json` / gate report must include every H/S gate boolean,
selected weights, rejected configs, and promotion recommendation.

---

## 13. Promotion contract (only if all hard gates pass)

Promote consolidated v5 to canonical GK aliases:

- `results/reports/ranking/goalkeeper_rankings.csv`
- `results/reports/ranking/goalkeeper_rankings.json`
- unified / website GK aliases

Set:

- `active_goalkeeper_rank_field = goalkeeper_consolidated_value_rank_v5`
- `v5_consolidation_status = promoted_single_metric`

Regenerate dependents from the same run (unified ranking, 300+ list,
by-team files, profiles, starter pairs, team reports, canonical summaries,
DOCX, figures, manifests).

Rewrite all dual-metric “Profile vs Impact” live language to **one**
goalkeeper ranking.

---

## 14. Fail-closed and dual-metric fallback

### 14.1 Fail-closed (default)

If any hard gate fails:

- write candidate `*_v5` + audit;
- live stays on Profile v3;
- `v5_consolidation_status = candidate_only`;
- diagnose blockers (e.g. Martínez stuck at 12–15; Al Owais still top 8;
  clutch too weak; PSxG channel still volume-like).

### 14.2 Dual-metric fallback (rare)

Only under §2.8. One declared primary, one diagnostic secondary. Never two
peer official GK rankings.

---

## 15. Reporting and website contract

After promotion, public copy must say:

- one Qatar 2022 goalkeeper ranking;
- PSxG difficulty check-back;
- clutch / late match-decisive prevention;
- bounded shootouts + support;
- Martínez ranks top 10 (state exact rank; if also top 3, say so);
- Al Owais is not an elite tournament GK under this estimand;
- Turner is not podium-ranked;
- Livaković / Bounou / Szczęsny remain high if evidence says so;
- stronger opposition matters somewhat via chance quality/state, not pedigree.

Methodology must be rewritten (not footnoted) in canonical model/final/
coaches summaries and website explainers.

Global/unified GK slotting uses this **same** consolidated score.

---

## 16. Tests to add or extend

1. PSxG prevention aggregation on synthetic shots.
2. Easy save worth less than hard save (outcome fixed).
3. Clutch uplift for ET/final-minute vs early minute (PSxG fixed).
4. Kolo Muani event present + score falls on removal.
5. Shootout credited-save WPA; woodwork ≠ full save.
6. Gate helpers: Martínez ≤10; Al Owais ≥11; Turner ≥4; neither Owais nor
   Turner in top 3; ≥3 of elite core in top 8.
7. Identity shuffle invariance.
8. No player-name strings in scoring path.
9. Active field points at consolidated rank after mocked promotion.
10. Soft-gate reporter for Martínez ≤3 (assert report exists; do not hard-fail
    release tests solely on soft gates unless running the promotion suite).

Keep full existing release suite green.

---

## 17. Suggested execution order

1. Write consolidation + face-validity preregistration (§2).
2. Freeze/hash baselines; record defective live top five.
3. Inventory dual-metric language.
4. Implement PSxG + diagnostics.
5. Implement clutch + anti-double-count.
6. Implement penalties, shootouts, support; optional opposition difficulty.
7. Preregister grid; score configs.
8. Select config passing all H gates; prefer S1 (Martínez top 3) among ties.
9. Write artifacts + gate report.
10. Tests.
11. Promote + regenerate + rewrite language only if H gates pass.
12. If fail: candidate-only report with blocker diagnosis.

---

## 18. Done means

**A. Promoted single-metric success**

- One live GK ranking;
- Hard gates all true (Martínez top 10; Al Owais outside top 10; Turner
  outside top 3; elite core mostly high; PSxG+clutch integrity);
- Soft gates reported (Martínez top 3 preferred);
- Dependents regenerated; tests green;
- `promoted_single_metric`.

**B. Candidate-only**

- Full v5 artifacts; live unchanged; clear gate failures;
- `candidate_only`.

**C. Dual-metric fallback (rare)**

- Only with §2.8 justification;
- `dual_metric_fallback`.

Anything that keeps Al Owais/Turner as a frozen podium, or that publishes two
peer official GK rankings, has failed this prompt.
