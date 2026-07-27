# World Cup Team Performance and Position-Specific Player Report

## Executive summary

This report consolidates **32 national teams**, **142 tournament-role player profiles**, **64 matches**, and **11,016 analyzed possessions** into one coaching reference. It combines observed possession outcomes with the regularized empirical hurdle-pipeline scenario audit. The strongest use is opponent preparation, video-review prioritization, and formation of testable tactical hypotheses.

**Important boundary:** observed goals, xG, shots, box entries, and transition exposure describe this tournament sample. Expected net xG, EvA gaps, optimal styles, and substitution gains are model-generated scenarios. They are not causal claims, guarantees, transfer valuations, or replacements for scouting, medical, training, and match-context evidence.

## How to read the metrics

- **xG:** summed shot quality created during the team's possessions.
- **Shot rate:** percentage of possessions containing at least one shot.
- **Box-entry rate:** percentage of possessions entering the penalty area.
- **Transition xG conceded:** opponent xG generated immediately after the team's possessions; lower is better and it is not total defensive xG conceded.
- **Mean EvA gap:** average difference between the best modeled tactic and the observed tactic. It identifies review candidates, not proven coaching errors.
- **Wasted net xG:** cumulative modeled EvA gap across possessions. It scales with possession volume, so compare it alongside the mean gap.
- **Physical matchup deltas:** lineup-minus-opponent aerial, pressing, and recovery proxies. Positive values indicate a modeled lineup edge.
- **V4 evaluation score:** a role-relative tournament score centered at 50; 10 points equal one within-role population standard deviation. It is not an absolute or cross-role quality measure.

## V4 validation and final metrics

**Validation status: PASS.** The leakage-safe OOF audit covers **64 matches**, **32 teams**, and **9,685 possessions**.

| Team/model validation metric | V4 final value |
| --- | --- |
| OOF positives | 13 |
| OOF Brier score | 0.001339 |
| OOF PR-AUC | 0.005958 |
| OOF ROC-AUC | 0.689341 |
| OOF unique probabilities | 8739 |
| Locked holdout Brier score | 0.001478 |
| Locked holdout PR-AUC | 0.016655 |
| Locked holdout ROC-AUC | 0.742019 |

| Player/report validation metric | V4 final value |
| --- | --- |
| Players before cutoff | 680 |
| Eligible players (300+ minutes) | 142 |
| Players excluded | 538 |
| Successful action endpoints | 81,231 |
| Linked SB360 actor snapshots | 72,016 |
| Events with SB360 context | 203,454 |
| Player heatmaps | 142 |
| Team reports | 32 |
| Compiled report files | 64 |
| Eligible substitutions | 0 |
| Suppressed substitutions | 3608 |

All V4 acceptance gates passed, including missing-value-free output, complete OOF team coverage, held-out-match exclusion, the 300-minute cutoff, fullback spatial-role safeguards, exact pressure discounting, within-role normalization, SB360 coverage, counterfactual safety, compiled-report completeness, and locked-classifier replay.
**Spatial boundary:** StatsBomb 360 contains event-time freeze-frame snapshots, not continuous optical tracking. Heatmaps show observed successful endpoints and visible actor snapshots; they do not interpolate unobserved runs.

### V4 top role-relative player evaluations

| Rank | Player | Functional role | Minutes | OBV/90 | Final third | Role z |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Hernández Cascante | Holding Anchor | 414 | +0.6666 | 6.9% | +2.61 |
| 2 | Young-Gwon Kim | Deep Playmaker | 373 | +0.4447 | 3.8% | +2.55 |
| 3 | Wojciech Szczęsny | Goalkeeper | 390 | +0.5992 | 2.6% | +2.30 |
| 4 | Borna Sosa | Box-to-Box Runner | 440 | +0.0706 | 31.1% | +2.19 |
| 5 | Éder Gabriel Militão | Ball-Winner | 364 | +0.2005 | 19.9% | +1.70 |
| 6 | Woo-Young Jung | Ball-Winner | 318 | +0.2307 | 17.3% | +1.67 |
| 7 | Sergino Dest | Wide Creator | 308 | +0.0997 | 31.7% | +1.63 |
| 8 | Kalidou Koulibaly | Deep Playmaker | 387 | +0.3210 | 3.3% | +1.44 |
| 9 | João Félix Sequeira | Target Forward | 340 | -0.2163 | 47.7% | +1.41 |
| 10 | Jin-Su Kim | Attacking Wingback | 341 | +0.0005 | 46.0% | +1.38 |

## Tournament overview

| Team | Matches | Poss. | Goals | xG | Shot % | Box entry % | Transition xG conceded | Mean EvA gap | Modeled style |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Argentina | 7 | 639 | 14 | 13.48 | 13.9 | 28.5 | 0.00 | 0.0053 | No meaningful change |
| France | 7 | 616 | 16 | 11.75 | 14.1 | 30.8 | 0.02 | 0.0031 | No meaningful change |
| Brazil | 5 | 470 | 8 | 10.50 | 18.1 | 37.7 | 0.01 | 0.0042 | No meaningful change |
| England | 5 | 403 | 13 | 8.74 | 14.6 | 36.2 | 0.00 | 0.0029 | No meaningful change |
| Germany | 3 | 277 | 6 | 8.23 | 20.6 | 45.1 | 0.00 | 0.0057 | No meaningful change |
| Portugal | 5 | 456 | 12 | 7.31 | 14.0 | 34.9 | 0.42 | 0.0018 | No meaningful change |
| Croatia | 7 | 696 | 8 | 6.84 | 9.5 | 31.2 | 0.00 | 0.0016 | No meaningful change |
| Switzerland | 4 | 339 | 5 | 6.09 | 9.4 | 26.0 | 0.00 | 0.0004 | No meaningful change |
| Morocco | 7 | 552 | 5 | 5.13 | 9.6 | 21.9 | 0.04 | 0.0031 | No meaningful change |
| Netherlands | 5 | 427 | 10 | 4.99 | 8.7 | 31.1 | 0.02 | 0.0025 | No meaningful change |
| Spain | 4 | 372 | 9 | 4.75 | 12.1 | 32.5 | 0.00 | 0.0024 | No meaningful change |
| Senegal | 4 | 333 | 5 | 4.27 | 13.8 | 30.0 | 0.00 | 0.0043 | No meaningful change |
| Japan | 4 | 326 | 5 | 4.25 | 10.4 | 28.2 | 0.03 | 0.0054 | No meaningful change |
| Poland | 4 | 313 | 2 | 4.18 | 8.6 | 23.6 | 0.26 | 0.0041 | Patient Build-up |
| United States | 4 | 333 | 3 | 3.94 | 12.6 | 34.8 | 0.00 | 0.0011 | No meaningful change |
| Canada | 3 | 272 | 2 | 3.93 | 11.8 | 30.1 | 0.04 | 0.0013 | No meaningful change |
| Iran | 3 | 234 | 4 | 3.83 | 11.1 | 29.5 | 0.00 | 0.0036 | No meaningful change |
| Ecuador | 3 | 253 | 4 | 3.81 | 9.9 | 31.6 | 0.00 | 0.0025 | No meaningful change |
| Belgium | 3 | 242 | 1 | 3.68 | 12.8 | 33.9 | 0.00 | 0.0037 | No meaningful change |
| South Korea | 4 | 314 | 5 | 3.58 | 13.4 | 30.6 | 0.00 | 0.0013 | No meaningful change |
| Ghana | 3 | 260 | 5 | 3.35 | 9.2 | 26.2 | 0.00 | 0.0054 | Patient Build-up |
| Uruguay | 3 | 248 | 2 | 3.27 | 12.9 | 32.3 | 0.00 | 0.0055 | No meaningful change |
| Saudi Arabia | 3 | 255 | 3 | 3.20 | 9.8 | 30.2 | 0.48 | 0.0015 | No meaningful change |
| Denmark | 3 | 270 | 1 | 3.19 | 11.1 | 36.7 | 0.00 | 0.0028 | No meaningful change |
| Serbia | 3 | 264 | 5 | 3.08 | 11.0 | 29.9 | 0.14 | 0.0035 | No meaningful change |
| Mexico | 3 | 263 | 2 | 3.06 | 13.7 | 34.6 | 0.00 | 0.0009 | No meaningful change |
| Cameroon | 3 | 247 | 4 | 2.93 | 9.7 | 30.0 | 0.00 | 0.0002 | No meaningful change |
| Tunisia | 3 | 283 | 1 | 2.41 | 10.2 | 30.4 | 0.00 | 0.0006 | No meaningful change |
| Wales | 3 | 259 | 1 | 2.22 | 8.1 | 23.9 | 0.00 | 0.0018 | No meaningful change |
| Australia | 4 | 311 | 4 | 1.56 | 8.0 | 26.0 | 0.28 | 0.0032 | Patient Build-up |
| Qatar | 3 | 255 | 1 | 1.39 | 7.5 | 20.8 | 0.00 | 0.0021 | No meaningful change |
| Costa Rica | 3 | 234 | 3 | 1.23 | 3.8 | 14.5 | 0.00 | 0.0032 | No meaningful change |

The table is sorted by observed xG rather than a synthetic overall rank. That preserves the distinction between attack volume, transition control, and model-estimated tactical opportunity.

# Team-by-team performance

## Argentina (ARG)

**Dynamic tactical summary:** Argentina: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.135. Strongest positive squad synergy: Nicolás Hernán Otamendi + Damián Emiliano Martínez (0.927). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Argentina's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 7 |
| Attacking possessions | 639 |
| Goals / xG | 14 / 13.48 |
| Shots / possession-to-shot rate | 99 / 13.9% |
| Penalty-area entry rate | 28.5% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 8.46; the OOF scenario ceiling was 11.44. The cumulative review gap was 2.98, averaging 0.0053 per possession.

Average lineup matchup deltas were **-0.043 aerial**, **-2.135 pressing**, and **+0.730 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Nicolás Hernán Otamendi + Damián Emiliano Martínez (0.927).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 80 possessions with 1.00 cumulative modeled gap (0.0125 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, INSUFFICIENT_MINUTES: 18, GAIN_BELOW_THRESHOLD: 3.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Attacking Midfield/Wing | Progressive Winger | 734 | 60.2 | 1.004 |
| 2 | Enzo Fernandez | Defensive Midfield | Ball-Winner | 601 | 56.1 | 0.222 |
| 3 | Ángel Fabián Di María Hernández | Central/Wide Midfield | Progressive Winger | 305 | 53.6 | 0.232 |
| 4 | Julián Álvarez | Forward | Target Forward | 485 | 49.5 | 0.355 |
| 5 | Rodrigo Javier De Paul | Defensive Midfield | Wide Creator | 635 | 46.2 | 0.138 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Australia (AUS)

**Dynamic tactical summary:** Australia: Patient Build-up led the observed baseline by 0.0032 mean EvA. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Harry Souttar + Kye Rowles (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Australia's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 311 |
| Goals / xG | 4 / 1.56 |
| Shots / possession-to-shot rate | 25 / 8.0% |
| Penalty-area entry rate | 26.0% |
| Opponent transition shots / xG | 1 / 0.28 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **Patient Build-up** most often. OOF actual expected Net xG was 1.75; the OOF scenario ceiling was 2.60. The cumulative review gap was 0.85, averaging 0.0032 per possession.

Average lineup matchup deltas were **+0.083 aerial**, **+3.342 pressing**, and **-0.799 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Harry Souttar + Kye Rowles (0.755).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 37 possessions with 0.22 cumulative modeled gap (0.0059 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, INSUFFICIENT_MINUTES: 20.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `SUPPORTED_CHANGE`. The style change cleared the tactical effect floor.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mathew Ryan | Goalkeeper | Goalkeeper | 387 | 61.2 | 0.042 |
| 2 | Aziz Eraltay Behich | Fullback/Wingback | Box-to-Box Runner | 387 | 48.1 | 0.036 |
| 3 | Aaron Mooy | Defensive Midfield | Ball-Winner | 387 | 47.4 | 0.041 |
| 4 | Harry Souttar | Center Back | Deep Playmaker | 387 | 46.2 | 0.070 |
| 5 | Jackson Irvine | Forward | Ball-Winner | 374 | 43.0 | 0.104 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Belgium (BEL)

**Dynamic tactical summary:** Belgium: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Belgium's total xG was near the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 242 |
| Goals / xG | 1 / 3.68 |
| Shots / possession-to-shot rate | 34 / 12.8% |
| Penalty-area entry rate | 33.9% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.69; the OOF scenario ceiling was 3.51. The cumulative review gap was 0.82, averaging 0.0037 per possession.

Average lineup matchup deltas were **-0.008 aerial**, **+0.226 pressing**, and **-0.856 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 15 possessions with 0.20 cumulative modeled gap (0.0130 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, INSUFFICIENT_MINUTES: 17.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Brazil (BRA)

**Dynamic tactical summary:** Brazil: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -6.128. Strongest positive squad synergy: Thiago Emiliano da Silva + Marcos Aoás Corrêa (0.778). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Brazil's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was below the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 5 |
| Attacking possessions | 470 |
| Goals / xG | 8 / 10.50 |
| Shots / possession-to-shot rate | 95 / 18.1% |
| Penalty-area entry rate | 37.7% |
| Opponent transition shots / xG | 1 / 0.01 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 7.02; the OOF scenario ceiling was 8.77. The cumulative review gap was 1.75, averaging 0.0042 per possession.

Average lineup matchup deltas were **-0.126 aerial**, **-6.128 pressing**, and **+0.692 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Thiago Emiliano da Silva + Marcos Aoás Corrêa (0.778).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 43 possessions with 0.47 cumulative modeled gap (0.0109 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 140, INSUFFICIENT_MINUTES: 25.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Éder Gabriel Militão | Fullback/Wingback | Ball-Winner | 364 | 67.0 | 0.140 |
| 2 | Marcos Aoás Corrêa | Center Back | Holding Anchor | 455 | 60.3 | 0.279 |
| 3 | Thiago Emiliano da Silva | Center Back | Holding Anchor | 409 | 60.0 | 0.170 |
| 4 | Carlos Henrique Casimiro | Defensive Midfield | Ball-Winner | 409 | 56.3 | 0.301 |
| 5 | Richarlison de Andrade | Forward | Target Forward | 328 | 53.3 | 0.458 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Cameroon (CMR)

**Dynamic tactical summary:** Cameroon: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Direct Long Play to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Cameroon's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 247 |
| Goals / xG | 4 / 2.93 |
| Shots / possession-to-shot rate | 26 / 9.7% |
| Penalty-area entry rate | 30.0% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 1.93; the OOF scenario ceiling was 1.98. The cumulative review gap was 0.05, averaging 0.0002 per possession.

Average lineup matchup deltas were **+0.078 aerial**, **+4.206 pressing**, and **-0.111 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 5 possessions with 0.04 cumulative modeled gap (0.0073 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 106, INSUFFICIENT_MINUTES: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Canada (CAN)

**Dynamic tactical summary:** Canada: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -1.282. Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Canada's total xG was near the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 272 |
| Goals / xG | 2 / 3.93 |
| Shots / possession-to-shot rate | 35 / 11.8% |
| Penalty-area entry rate | 30.1% |
| Opponent transition shots / xG | 2 / 0.04 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.86; the OOF scenario ceiling was 3.17. The cumulative review gap was 0.31, averaging 0.0013 per possession.

Average lineup matchup deltas were **-0.027 aerial**, **-1.282 pressing**, and **+0.782 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 10 possessions with 0.09 cumulative modeled gap (0.0086 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 74, INSUFFICIENT_MINUTES: 14.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Costa Rica (CRC)

**Dynamic tactical summary:** Costa Rica: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Costa Rica's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 234 |
| Goals / xG | 3 / 1.23 |
| Shots / possession-to-shot rate | 11 / 3.8% |
| Penalty-area entry rate | 14.5% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 1.59; the OOF scenario ceiling was 2.20. The cumulative review gap was 0.61, averaging 0.0032 per possession.

Average lineup matchup deltas were **+0.101 aerial**, **+0.962 pressing**, and **-0.471 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 17 possessions with 0.15 cumulative modeled gap (0.0088 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, INSUFFICIENT_MINUTES: 16.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Croatia (CRO)

**Dynamic tactical summary:** Croatia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.690. Strongest positive squad synergy: Dominik Livaković + Joško Gvardiol (0.925). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Croatia's total xG was among the tournament leaders, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 7 |
| Attacking possessions | 696 |
| Goals / xG | 8 / 6.84 |
| Shots / possession-to-shot rate | 77 / 9.5% |
| Penalty-area entry rate | 31.2% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 6.35; the OOF scenario ceiling was 7.33. The cumulative review gap was 0.98, averaging 0.0016 per possession.

Average lineup matchup deltas were **+0.041 aerial**, **-2.690 pressing**, and **+0.290 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Dominik Livaković + Joško Gvardiol (0.925).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 34 possessions with 0.21 cumulative modeled gap (0.0061 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, INSUFFICIENT_MINUTES: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Borna Sosa | Fullback/Wingback | Box-to-Box Runner | 440 | 71.9 | 0.061 |
| 2 | Luka Modrić | Central/Wide Midfield | Ball-Winner | 673 | 59.9 | 0.241 |
| 3 | Josip Juranović | Fullback/Wingback | Wide Creator | 624 | 59.2 | 0.058 |
| 4 | Dominik Livaković | Goalkeeper | Goalkeeper | 720 | 58.3 | 0.037 |
| 5 | Mateo Kovačić | Central/Wide Midfield | Ball-Winner | 650 | 55.5 | 0.121 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Denmark (DEN)

**Dynamic tactical summary:** Denmark: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.172. Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Denmark's total xG was below the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 270 |
| Goals / xG | 1 / 3.19 |
| Shots / possession-to-shot rate | 35 / 11.1% |
| Penalty-area entry rate | 36.7% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.62; the OOF scenario ceiling was 3.31. The cumulative review gap was 0.69, averaging 0.0028 per possession.

Average lineup matchup deltas were **-0.157 aerial**, **-2.172 pressing**, and **-0.546 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 37 possessions with 0.25 cumulative modeled gap (0.0067 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 87, INSUFFICIENT_MINUTES: 12.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Ecuador (ECU)

**Dynamic tactical summary:** Ecuador: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Patient Build-up to Short Under Pressure). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Ecuador's total xG was near the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 253 |
| Goals / xG | 4 / 3.81 |
| Shots / possession-to-shot rate | 30 / 9.9% |
| Penalty-area entry rate | 31.6% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.51; the OOF scenario ceiling was 3.07. The cumulative review gap was 0.56, averaging 0.0025 per possession.

Average lineup matchup deltas were **-0.004 aerial**, **+1.896 pressing**, and **+0.400 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Patient Build-up were most often improved in the model by Short Under Pressure. This pattern covered 22 possessions with 0.15 cumulative modeled gap (0.0070 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 68, INSUFFICIENT_MINUTES: 9.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## England (ENG)

**Dynamic tactical summary:** England: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -3.654. Strongest positive squad synergy: John Stones + Jordan Pickford (0.815). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, England's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 5 |
| Attacking possessions | 403 |
| Goals / xG | 13 / 8.74 |
| Shots / possession-to-shot rate | 63 / 14.6% |
| Penalty-area entry rate | 36.2% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 4.78; the OOF scenario ceiling was 5.82. The cumulative review gap was 1.04, averaging 0.0029 per possession.

Average lineup matchup deltas were **+0.012 aerial**, **-3.654 pressing**, and **+0.987 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** John Stones + Jordan Pickford (0.815).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 36 possessions with 0.30 cumulative modeled gap (0.0083 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, INSUFFICIENT_MINUTES: 17.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | John Stones | Center Back | Holding Anchor | 465 | 57.6 | 0.252 |
| 2 | Luke Shaw | Fullback/Wingback | Box-to-Box Runner | 457 | 55.3 | 0.088 |
| 3 | Jordan Pickford | Goalkeeper | Goalkeeper | 486 | 52.4 | 0.029 |
| 4 | Harry Kane | Forward | Target Forward | 422 | 52.1 | 0.517 |
| 5 | Harry Maguire | Center Back | Holding Anchor | 454 | 48.3 | 0.207 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## France (FRA)

**Dynamic tactical summary:** France: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Raphaël Varane + Aurélien Djani Tchouaméni (0.842). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, France's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was below the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 7 |
| Attacking possessions | 616 |
| Goals / xG | 16 / 11.75 |
| Shots / possession-to-shot rate | 101 / 14.1% |
| Penalty-area entry rate | 30.8% |
| Opponent transition shots / xG | 1 / 0.02 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 7.61; the OOF scenario ceiling was 9.26. The cumulative review gap was 1.65, averaging 0.0031 per possession.

Average lineup matchup deltas were **+0.105 aerial**, **+1.067 pressing**, and **-0.652 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Raphaël Varane + Aurélien Djani Tchouaméni (0.842).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 53 possessions with 0.36 cumulative modeled gap (0.0068 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, INSUFFICIENT_MINUTES: 19, GAIN_BELOW_THRESHOLD: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ousmane Dembélé | Attacking Midfield/Wing | Progressive Winger | 448 | 61.3 | 0.119 |
| 2 | Olivier Giroud | Forward | Target Forward | 433 | 59.2 | 0.633 |
| 3 | Aurélien Djani Tchouaméni | Defensive Midfield | Ball-Winner | 662 | 58.8 | 0.227 |
| 4 | Jules Koundé | Fullback/Wingback | Wide Creator | 514 | 55.4 | 0.074 |
| 5 | Kylian Mbappé Lottin | Forward | Progressive Winger | 654 | 55.1 | 0.728 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Germany (GER)

**Dynamic tactical summary:** Germany: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Germany's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 277 |
| Goals / xG | 6 / 8.23 |
| Shots / possession-to-shot rate | 68 / 20.6% |
| Penalty-area entry rate | 45.1% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 4.82; the OOF scenario ceiling was 6.23. The cumulative review gap was 1.41, averaging 0.0057 per possession.

Average lineup matchup deltas were **-0.032 aerial**, **+0.154 pressing**, and **-0.075 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 32 possessions with 0.43 cumulative modeled gap (0.0133 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, INSUFFICIENT_MINUTES: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Ghana (GHA)

**Dynamic tactical summary:** Ghana: Patient Build-up led the observed baseline by 0.0054 mean EvA. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Thomas Teye Partey + Mohamed Salisu (0.663). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Ghana's total xG was below the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 260 |
| Goals / xG | 5 / 3.35 |
| Shots / possession-to-shot rate | 25 / 9.2% |
| Penalty-area entry rate | 26.2% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Short Under Pressure |
| Most frequent defensive style | Compact Pressure Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **Patient Build-up** most often. OOF actual expected Net xG was 2.27; the OOF scenario ceiling was 3.48. The cumulative review gap was 1.21, averaging 0.0054 per possession.

Average lineup matchup deltas were **-0.156 aerial**, **+1.137 pressing**, and **+0.026 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Thomas Teye Partey + Mohamed Salisu (0.663).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 36 possessions with 0.35 cumulative modeled gap (0.0097 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, INSUFFICIENT_MINUTES: 20.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `SUPPORTED_CHANGE`. The style change cleared the tactical effect floor.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 301 | 56.1 | 0.126 |
| 2 | Daniel Amartey | Center Back | Deep Playmaker | 301 | 54.2 | 0.076 |
| 3 | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 301 | 47.8 | 0.016 |
| 4 | Mohamed Salisu | Center Back | Deep Playmaker | 301 | 47.4 | 0.169 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Iran (IRN)

**Dynamic tactical summary:** Iran: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Morteza Pouraliganji + Seyed Majid Hosseini (0.669). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Iran's total xG was near the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 234 |
| Goals / xG | 4 / 3.83 |
| Shots / possession-to-shot rate | 33 / 11.1% |
| Penalty-area entry rate | 29.5% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 1.90; the OOF scenario ceiling was 2.60. The cumulative review gap was 0.69, averaging 0.0036 per possession.

Average lineup matchup deltas were **+0.058 aerial**, **+1.725 pressing**, and **-1.059 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Morteza Pouraliganji + Seyed Majid Hosseini (0.669).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 20 possessions with 0.18 cumulative modeled gap (0.0088 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 96, INSUFFICIENT_MINUTES: 14.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mehdi Taremi | Forward | Target Forward | 305 | 60.7 | 0.447 |
| 2 | Morteza Pouraliganji | Center Back | Deep Playmaker | 305 | 46.5 | 0.125 |
| 3 | Seyed Majid Hosseini | Center Back | Deep Playmaker | 305 | 31.4 | 0.027 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Japan (JPN)

**Dynamic tactical summary:** Japan: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Maya Yoshida + Shūichi Gonda (0.773). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Japan's total xG was above the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was below the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 326 |
| Goals / xG | 5 / 4.25 |
| Shots / possession-to-shot rate | 44 / 10.4% |
| Penalty-area entry rate | 28.2% |
| Opponent transition shots / xG | 1 / 0.03 |
| Most frequent attacking style | Short Under Pressure |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 3.12; the OOF scenario ceiling was 4.62. The cumulative review gap was 1.50, averaging 0.0054 per possession.

Average lineup matchup deltas were **-0.029 aerial**, **+10.178 pressing**, and **-0.086 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Maya Yoshida + Shūichi Gonda (0.773).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 38 possessions with 0.42 cumulative modeled gap (0.0111 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, INSUFFICIENT_MINUTES: 16.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Shūichi Gonda | Goalkeeper | Goalkeeper | 413 | 56.8 | 0.015 |
| 2 | Wataru Endo | Defensive Midfield | Ball-Winner | 326 | 55.4 | 0.095 |
| 3 | Maya Yoshida | Center Back | Deep Playmaker | 413 | 46.6 | 0.223 |
| 4 | Junya Ito | Fullback/Wingback | Attacking Wingback | 346 | 44.9 | 0.043 |
| 5 | Daichi Kamada | Attacking Midfield/Wing | Ball-Winner | 337 | 26.7 | 0.131 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Mexico (MEX)

**Dynamic tactical summary:** Mexico: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Direct Long Play to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Mexico's total xG was below the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 263 |
| Goals / xG | 2 / 3.06 |
| Shots / possession-to-shot rate | 41 / 13.7% |
| Penalty-area entry rate | 34.6% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 1.93; the OOF scenario ceiling was 2.14. The cumulative review gap was 0.21, averaging 0.0009 per possession.

Average lineup matchup deltas were **+0.071 aerial**, **+1.266 pressing**, and **-0.714 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 6 possessions with 0.05 cumulative modeled gap (0.0087 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 95, INSUFFICIENT_MINUTES: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Morocco (MAR)

**Dynamic tactical summary:** Morocco: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Sofyan Amrabat + Yassine Bounou (0.877). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Morocco's total xG was above the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 7 |
| Attacking possessions | 552 |
| Goals / xG | 5 / 5.13 |
| Shots / possession-to-shot rate | 60 / 9.6% |
| Penalty-area entry rate | 21.9% |
| Opponent transition shots / xG | 1 / 0.04 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 4.34; the OOF scenario ceiling was 5.82. The cumulative review gap was 1.48, averaging 0.0031 per possession.

Average lineup matchup deltas were **-0.018 aerial**, **+4.404 pressing**, and **-0.129 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Sofyan Amrabat + Yassine Bounou (0.877).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 55 possessions with 0.37 cumulative modeled gap (0.0068 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 128, INSUFFICIENT_MINUTES: 22, GAIN_BELOW_THRESHOLD: 4.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Sofiane Boufal | Central/Wide Midfield | Progressive Winger | 477 | 60.5 | 0.097 |
| 2 | Romain Saïss | Center Back | Deep Playmaker | 486 | 59.6 | 0.148 |
| 3 | Yahia Attiyat allah | Fullback/Wingback | Box-to-Box Runner | 350 | 58.1 | 0.123 |
| 4 | Achraf Hakimi Mouh | Fullback/Wingback | Wide Creator | 661 | 53.7 | 0.171 |
| 5 | Yassine Bounou | Goalkeeper | Goalkeeper | 603 | 52.3 | 0.041 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Netherlands (NED)

**Dynamic tactical summary:** Netherlands: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Virgil van Dijk + Andries Noppert (0.840). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Netherlands's total xG was above the tournament median, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was below the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 5 |
| Attacking possessions | 427 |
| Goals / xG | 10 / 4.99 |
| Shots / possession-to-shot rate | 43 / 8.7% |
| Penalty-area entry rate | 31.1% |
| Opponent transition shots / xG | 1 / 0.02 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 4.46; the OOF scenario ceiling was 5.38. The cumulative review gap was 0.92, averaging 0.0025 per possession.

Average lineup matchup deltas were **+0.024 aerial**, **+0.739 pressing**, and **+0.057 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Virgil van Dijk + Andries Noppert (0.840).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 29 possessions with 0.22 cumulative modeled gap (0.0077 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 92, INSUFFICIENT_MINUTES: 18.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Jurriën David Norman Timber | Center Back | Ball-Winner | 409 | 60.4 | 0.073 |
| 2 | Virgil van Dijk | Center Back | Deep Playmaker | 510 | 58.8 | 0.258 |
| 3 | Frenkie de Jong | Defensive Midfield | Ball-Winner | 499 | 55.5 | 0.194 |
| 4 | Nathan Aké | Center Back | Holding Anchor | 506 | 49.9 | 0.086 |
| 5 | Andries Noppert | Goalkeeper | Goalkeeper | 510 | 41.3 | 0.069 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Poland (POL)

**Dynamic tactical summary:** Poland: Patient Build-up led the observed baseline by 0.0041 mean EvA. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Kamil Glik + Matty Cash (0.756). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Poland's total xG was near the tournament median, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 313 |
| Goals / xG | 2 / 4.18 |
| Shots / possession-to-shot rate | 30 / 8.6% |
| Penalty-area entry rate | 23.6% |
| Opponent transition shots / xG | 2 / 0.26 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **Patient Build-up** most often. OOF actual expected Net xG was 2.57; the OOF scenario ceiling was 3.72. The cumulative review gap was 1.15, averaging 0.0041 per possession.

Average lineup matchup deltas were **+0.054 aerial**, **+1.148 pressing**, and **-0.413 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Kamil Glik + Matty Cash (0.756).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 32 possessions with 0.22 cumulative modeled gap (0.0068 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 90, INSUFFICIENT_MINUTES: 20.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `SUPPORTED_CHANGE`. The style change cleared the tactical effect floor.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Wojciech Szczęsny | Goalkeeper | Goalkeeper | 390 | 73.0 | 0.039 |
| 2 | Piotr Zieliński | Central/Wide Midfield | Wide Creator | 344 | 57.9 | 0.208 |
| 3 | Matty Cash | Fullback/Wingback | Wide Creator | 390 | 57.0 | 0.031 |
| 4 | Grzegorz Krychowiak | Defensive Midfield | Ball-Winner | 348 | 54.6 | 0.029 |
| 5 | Jakub Piotr Kiwior | Center Back | Deep Playmaker | 377 | 45.0 | 0.079 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Portugal (POR)

**Dynamic tactical summary:** Portugal: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -4.222. Strongest positive squad synergy: Kléper Laveran Lima Ferreira + Diogo Meireles Costa (0.754). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Portugal's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 5 |
| Attacking possessions | 456 |
| Goals / xG | 12 / 7.31 |
| Shots / possession-to-shot rate | 66 / 14.0% |
| Penalty-area entry rate | 34.9% |
| Opponent transition shots / xG | 2 / 0.42 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 4.72; the OOF scenario ceiling was 5.47. The cumulative review gap was 0.75, averaging 0.0018 per possession.

Average lineup matchup deltas were **+0.006 aerial**, **-4.222 pressing**, and **-0.010 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Kléper Laveran Lima Ferreira + Diogo Meireles Costa (0.754).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 33 possessions with 0.18 cumulative modeled gap (0.0055 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 123, INSUFFICIENT_MINUTES: 20.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | João Félix Sequeira | Attacking Midfield/Wing | Target Forward | 340 | 64.1 | 0.193 |
| 2 | João Pedro Cavaco Cancelo | Fullback/Wingback | Box-to-Box Runner | 345 | 56.2 | 0.053 |
| 3 | Kléper Laveran Lima Ferreira | Center Back | Deep Playmaker | 389 | 53.4 | 0.142 |
| 4 | Rúben Santos Gato Alves Dias | Center Back | Deep Playmaker | 392 | 51.6 | 0.085 |
| 5 | Diogo Meireles Costa | Goalkeeper | Goalkeeper | 489 | 50.6 | 0.037 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Qatar (QAT)

**Dynamic tactical summary:** Qatar: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Wide Retreating Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Qatar's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 255 |
| Goals / xG | 1 / 1.39 |
| Shots / possession-to-shot rate | 19 / 7.5% |
| Penalty-area entry rate | 20.8% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 1.80; the OOF scenario ceiling was 2.29. The cumulative review gap was 0.49, averaging 0.0021 per possession.

Average lineup matchup deltas were **+0.005 aerial**, **+2.608 pressing**, and **-0.286 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 25 possessions with 0.18 cumulative modeled gap (0.0073 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 81, INSUFFICIENT_MINUTES: 18.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Saudi Arabia (KSA)

**Dynamic tactical summary:** Saudi Arabia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -0.540. Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Saudi Arabia's total xG was below the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 255 |
| Goals / xG | 3 / 3.20 |
| Shots / possession-to-shot rate | 30 / 9.8% |
| Penalty-area entry rate | 30.2% |
| Opponent transition shots / xG | 1 / 0.48 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.09; the OOF scenario ceiling was 2.41. The cumulative review gap was 0.32, averaging 0.0015 per possession.

Average lineup matchup deltas were **-0.117 aerial**, **-0.540 pressing**, and **+0.714 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 18 possessions with 0.11 cumulative modeled gap (0.0063 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 118, INSUFFICIENT_MINUTES: 14.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Senegal (SEN)

**Dynamic tactical summary:** Senegal: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -1.491. Strongest positive squad synergy: Kalidou Koulibaly + Edouard Mendy (0.753). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Senegal's total xG was above the tournament median, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 333 |
| Goals / xG | 5 / 4.27 |
| Shots / possession-to-shot rate | 50 / 13.8% |
| Penalty-area entry rate | 30.0% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.77; the OOF scenario ceiling was 4.00. The cumulative review gap was 1.24, averaging 0.0043 per possession.

Average lineup matchup deltas were **+0.016 aerial**, **-1.491 pressing**, and **-0.488 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Kalidou Koulibaly + Edouard Mendy (0.753).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 35 possessions with 0.33 cumulative modeled gap (0.0093 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, INSUFFICIENT_MINUTES: 20.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Kalidou Koulibaly | Center Back | Deep Playmaker | 387 | 64.4 | 0.112 |
| 2 | Ismaïla Sarr | Attacking Midfield/Wing | Target Forward | 365 | 63.7 | 0.481 |
| 3 | Youssouf Sabaly | Fullback/Wingback | Attacking Wingback | 387 | 62.2 | 0.080 |
| 4 | Abdou Diallo | Center Back | Deep Playmaker | 349 | 60.8 | 0.076 |
| 5 | Boulaye Dia | Attacking Midfield/Wing | Target Forward | 330 | 49.6 | 0.179 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Serbia (SRB)

**Dynamic tactical summary:** Serbia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.400. Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Serbia's total xG was below the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 264 |
| Goals / xG | 5 / 3.08 |
| Shots / possession-to-shot rate | 31 / 11.0% |
| Penalty-area entry rate | 29.9% |
| Opponent transition shots / xG | 2 / 0.14 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.31; the OOF scenario ceiling was 3.12. The cumulative review gap was 0.81, averaging 0.0035 per possession.

Average lineup matchup deltas were **+0.055 aerial**, **-2.400 pressing**, and **-0.287 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 35 possessions with 0.24 cumulative modeled gap (0.0067 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 112, INSUFFICIENT_MINUTES: 20.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## South Korea (KOR)

**Dynamic tactical summary:** South Korea: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Young-Gwon Kim + Seung-Gyu Kim (0.730). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, South Korea's total xG was near the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 314 |
| Goals / xG | 5 / 3.58 |
| Shots / possession-to-shot rate | 47 / 13.4% |
| Penalty-area entry rate | 30.6% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.95; the OOF scenario ceiling was 3.31. The cumulative review gap was 0.36, averaging 0.0013 per possession.

Average lineup matchup deltas were **+0.118 aerial**, **+6.170 pressing**, and **+0.195 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Young-Gwon Kim + Seung-Gyu Kim (0.730).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 14 possessions with 0.11 cumulative modeled gap (0.0077 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 93, INSUFFICIENT_MINUTES: 17.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Young-Gwon Kim | Center Back | Deep Playmaker | 373 | 75.5 | 0.249 |
| 2 | Woo-Young Jung | Defensive Midfield | Ball-Winner | 318 | 66.7 | 0.066 |
| 3 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 341 | 63.8 | 0.107 |
| 4 | Heung-Min Son | Attacking Midfield/Wing | Target Forward | 390 | 55.4 | 0.119 |
| 5 | In-Beom Hwang | Defensive Midfield | Ball-Winner | 360 | 55.3 | 0.101 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Spain (ESP)

**Dynamic tactical summary:** Spain: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -12.554. Strongest positive squad synergy: Rodrigo Hernández Cascante + Unai Simón Mendibil (0.779). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Spain's total xG was above the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 372 |
| Goals / xG | 9 / 4.75 |
| Shots / possession-to-shot rate | 48 / 12.1% |
| Penalty-area entry rate | 32.5% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Compact Pressure Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 4.28; the OOF scenario ceiling was 5.12. The cumulative review gap was 0.84, averaging 0.0024 per possession.

Average lineup matchup deltas were **-0.046 aerial**, **-12.554 pressing**, and **+0.142 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Rodrigo Hernández Cascante + Unai Simón Mendibil (0.779).

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 36 possessions with 0.33 cumulative modeled gap (0.0091 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 95, INSUFFICIENT_MINUTES: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Hernández Cascante | Center Back | Holding Anchor | 414 | 76.1 | 0.199 |
| 2 | Aymeric Laporte | Center Back | Holding Anchor | 317 | 57.9 | 0.167 |
| 3 | Pedro González López | Central/Wide Midfield | Ball-Winner | 372 | 55.0 | 0.109 |
| 4 | Sergio Busquets i Burgos | Defensive Midfield | Ball-Winner | 379 | 51.4 | 0.275 |
| 5 | Unai Simón Mendibil | Goalkeeper | Goalkeeper | 414 | 31.8 | 0.059 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Switzerland (SUI)

**Dynamic tactical summary:** Switzerland: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Compact Pressure Block (Direct Long Play to Short Under Pressure). Strongest positive squad synergy: Granit Xhaka + Manuel Obafemi Akanji (0.755). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Switzerland's total xG was above the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 339 |
| Goals / xG | 5 / 6.09 |
| Shots / possession-to-shot rate | 37 / 9.4% |
| Penalty-area entry rate | 26.0% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.83; the OOF scenario ceiling was 2.94. The cumulative review gap was 0.11, averaging 0.0004 per possession.

Average lineup matchup deltas were **-0.030 aerial**, **+2.987 pressing**, and **-0.646 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Granit Xhaka + Manuel Obafemi Akanji (0.755).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Direct Long Play were most often improved in the model by Short Under Pressure. This pattern covered 8 possessions with 0.05 cumulative modeled gap (0.0061 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 121, INSUFFICIENT_MINUTES: 22.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Box-to-Box Runner | 380 | 56.5 | 0.033 |
| 2 | Breel-Donald Embolo | Forward | Target Forward | 330 | 52.3 | 0.656 |
| 3 | Remo Freuler | Defensive Midfield | Ball-Winner | 346 | 51.5 | 0.158 |
| 4 | Manuel Obafemi Akanji | Center Back | Holding Anchor | 387 | 49.6 | 0.303 |
| 5 | Granit Xhaka | Defensive Midfield | Ball-Winner | 387 | 48.6 | 0.132 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Tunisia (TUN)

**Dynamic tactical summary:** Tunisia: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -2.788. Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Tunisia's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 283 |
| Goals / xG | 1 / 2.41 |
| Shots / possession-to-shot rate | 32 / 10.2% |
| Penalty-area entry rate | 30.4% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Short Under Pressure |
| Most frequent defensive style | Compact Pressure Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.70; the OOF scenario ceiling was 2.85. The cumulative review gap was 0.16, averaging 0.0006 per possession.

Average lineup matchup deltas were **-0.059 aerial**, **-2.788 pressing**, and **+1.194 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 15 possessions with 0.09 cumulative modeled gap (0.0059 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 91, INSUFFICIENT_MINUTES: 19.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## United States (USA)

**Dynamic tactical summary:** United States: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -0.925. Strongest positive squad synergy: Matthew Charles Turner + Tim Ream (0.756). Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, United States's total xG was near the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 4 |
| Attacking possessions | 333 |
| Goals / xG | 3 / 3.94 |
| Shots / possession-to-shot rate | 46 / 12.6% |
| Penalty-area entry rate | 34.8% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 3.58; the OOF scenario ceiling was 3.91. The cumulative review gap was 0.33, averaging 0.0011 per possession.

Average lineup matchup deltas were **-0.068 aerial**, **-0.925 pressing**, and **+0.496 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Matthew Charles Turner + Tim Ream (0.756).

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 10 possessions with 0.08 cumulative modeled gap (0.0084 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, INSUFFICIENT_MINUTES: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Sergino Dest | Fullback/Wingback | Wide Creator | 308 | 66.3 | 0.134 |
| 2 | Tyler Adams | Defensive Midfield | Ball-Winner | 391 | 58.9 | 0.068 |
| 3 | Timothy Weah | Attacking Midfield/Wing | Target Forward | 318 | 49.4 | 0.155 |
| 4 | Matthew Charles Turner | Goalkeeper | Goalkeeper | 391 | 47.9 | 0.039 |
| 5 | Christian Pulisic | Attacking Midfield/Wing | Progressive Winger | 336 | 47.3 | 0.350 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Uruguay (URU)

**Dynamic tactical summary:** Uruguay: no tactical change cleared the modeled effect floor. Primary review signal: pressing deficit -0.252. Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Uruguay's total xG was below the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 248 |
| Goals / xG | 2 / 3.27 |
| Shots / possession-to-shot rate | 33 / 12.9% |
| Penalty-area entry rate | 32.3% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 2.65; the OOF scenario ceiling was 3.85. The cumulative review gap was 1.19, averaging 0.0055 per possession.

Average lineup matchup deltas were **+0.090 aerial**, **-0.252 pressing**, and **-0.035 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 38 possessions with 0.42 cumulative modeled gap (0.0109 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 80, INSUFFICIENT_MINUTES: 8.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

## Wales (WAL)

**Dynamic tactical summary:** Wales: no tactical change cleared the modeled effect floor. Primary review signal: transition review against Set-Piece Compact Shape (Short Under Pressure to Patient Build-up). Strongest positive squad synergy: Insufficient shared-minutes data. Model transition-conceded-v2, target transition_conceded, calibration platt, threshold None (no validated threshold; abstention).

### Tier 1 — Observed Tournament Evidence

Across the analyzed possessions, Wales's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

| Observed tournament indicator | Value |
| --- | --- |
| Matches represented | 3 |
| Attacking possessions | 259 |
| Goals / xG | 1 / 2.22 |
| Shots / possession-to-shot rate | 24 / 8.1% |
| Penalty-area entry rate | 23.9% |
| Opponent transition shots / xG | 0 / 0.00 |
| Most frequent attacking style | Patient Build-up |
| Most frequent defensive style | Wide Retreating Block |

### Tier 2 — Model-Supported Scenario Audits

The 64-match leave-one-match-out audit selected **No meaningful change** most often. OOF actual expected Net xG was 1.95; the OOF scenario ceiling was 2.37. The cumulative review gap was 0.42, averaging 0.0018 per possession.

Average lineup matchup deltas were **-0.031 aerial**, **+1.564 pressing**, and **-0.189 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Top positive player synergy:** Insufficient shared-minutes data.

**Highest-volume review pattern:** against Set-Piece Compact Shape, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 11 possessions with 0.08 cumulative modeled gap (0.0076 per possession).

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 71, INSUFFICIENT_MINUTES: 6.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | V4 role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

# Top tournament-role players by position

These leaderboards contain only players with at least 300 tournament minutes. V4 scores are standardized within functional role: 50 is role average and each 10 points is one population standard deviation. Grouping the display by broad position aids navigation but does not make scores directly comparable across roles.

## V4 role-score construction

- Risk-adjusted OBV per 90: 65%.
- Final-third spatial presence: 20%.
- Pressure-adjusted turnover resilience: 15%.
- Pressured turnover penalties are exactly half the standard location-sensitive penalty.
- Successful event endpoints and SB360 actor snapshots use the StatsBomb 120x80 pitch.
- Fullbacks above 35% combined final-third share are classified as Attacking Wingbacks.


**Goalkeeper warning:** the source features do not provide a complete provider post-shot-xG model. The report uses on-target StatsBomb shot xG as an explicitly labeled proxy, then adds goals prevented, claims, sweeping location, and pressured distribution. It remains unsuitable as a standalone goalkeeper selection model.

## Goalkeeper

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Wojciech Szczęsny | Poland | Goalkeeper | Goalkeeper | 390 | 73.0 | 0.039 | 0.00 | 0.00 | 4.16 |
| 2 | Mathew Ryan | Australia | Goalkeeper | Goalkeeper | 387 | 61.2 | 0.042 | 0.00 | 0.00 | 4.65 |
| 3 | Dominik Livaković | Croatia | Goalkeeper | Goalkeeper | 720 | 58.3 | 0.037 | 0.00 | 0.25 | 4.12 |
| 4 | Shūichi Gonda | Japan | Goalkeeper | Goalkeeper | 413 | 56.8 | 0.015 | 0.00 | 0.22 | 3.05 |
| 5 | Hugo Lloris | France | Goalkeeper | Goalkeeper | 614 | 53.1 | 0.028 | 0.00 | 0.00 | 2.34 |
| 6 | Jordan Pickford | England | Goalkeeper | Goalkeeper | 486 | 52.4 | 0.029 | 0.00 | 0.00 | 2.96 |
| 7 | Yassine Bounou | Morocco | Goalkeeper | Goalkeeper | 603 | 52.3 | 0.041 | 0.00 | 0.15 | 3.73 |
| 8 | Diogo Meireles Costa | Portugal | Goalkeeper | Goalkeeper | 489 | 50.6 | 0.037 | 0.00 | 0.18 | 2.76 |
| 9 | Seung-Gyu Kim | South Korea | Goalkeeper | Goalkeeper | 390 | 49.7 | 0.030 | 0.00 | 0.00 | 3.46 |
| 10 | Edouard Mendy | Senegal | Goalkeeper | Goalkeeper | 387 | 49.0 | 0.030 | 0.00 | 0.00 | 3.72 |

The goalkeeper ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Center Back

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Hernández Cascante | Spain | Right Center Back | Holding Anchor | 414 | 76.1 | 0.199 | 0.75 | 5.00 | 4.35 |
| 2 | Young-Gwon Kim | South Korea | Left Center Back | Deep Playmaker | 373 | 75.5 | 0.249 | 0.78 | 5.06 | 1.93 |
| 3 | Kalidou Koulibaly | Senegal | Right Center Back | Deep Playmaker | 387 | 64.4 | 0.112 | 0.80 | 9.30 | 4.65 |
| 4 | Abdou Diallo | Senegal | Left Center Back | Deep Playmaker | 349 | 60.8 | 0.076 | 0.58 | 6.71 | 0.77 |
| 5 | Jurriën David Norman Timber | Netherlands | Right Center Back | Ball-Winner | 409 | 60.4 | 0.073 | 0.53 | 17.37 | 3.30 |
| 6 | Marcos Aoás Corrêa | Brazil | Left Center Back | Holding Anchor | 455 | 60.3 | 0.279 | 0.53 | 4.75 | 2.57 |
| 7 | Thiago Emiliano da Silva | Brazil | Right Center Back | Holding Anchor | 409 | 60.0 | 0.170 | 0.58 | 6.60 | 2.20 |
| 8 | Romain Saïss | Morocco | Left Center Back | Deep Playmaker | 486 | 59.6 | 0.148 | 0.80 | 7.60 | 2.22 |
| 9 | Virgil van Dijk | Netherlands | Center Back | Deep Playmaker | 510 | 58.8 | 0.258 | 0.64 | 6.01 | 1.41 |
| 10 | Aymeric Laporte | Spain | Left Center Back | Holding Anchor | 317 | 57.9 | 0.167 | 0.67 | 4.26 | 1.14 |

The center back ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Fullback/Wingback

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Borna Sosa | Croatia | Left Back | Box-to-Box Runner | 440 | 71.9 | 0.061 | 0.27 | 10.63 | 2.45 |
| 2 | Éder Gabriel Militão | Brazil | Right Back | Ball-Winner | 364 | 67.0 | 0.140 | 0.40 | 13.86 | 4.95 |
| 3 | Sergino Dest | United States | Right Back | Wide Creator | 308 | 66.3 | 0.134 | 0.29 | 13.46 | 4.39 |
| 4 | Jin-Su Kim | South Korea | Left Back | Attacking Wingback | 341 | 63.8 | 0.107 | 0.56 | 7.66 | 3.17 |
| 5 | Youssouf Sabaly | Senegal | Right Back | Attacking Wingback | 387 | 62.2 | 0.080 | 0.43 | 11.85 | 6.04 |
| 6 | Josip Juranović | Croatia | Right Back | Wide Creator | 624 | 59.2 | 0.058 | 0.40 | 8.51 | 4.47 |
| 7 | Yahia Attiyat allah | Morocco | Left Back | Box-to-Box Runner | 350 | 58.1 | 0.123 | 0.20 | 11.31 | 5.14 |
| 8 | Matty Cash | Poland | Right Back | Wide Creator | 390 | 57.0 | 0.031 | 0.50 | 10.16 | 1.39 |
| 9 | Ricardo Iván Rodríguez Araya | Switzerland | Left Back | Box-to-Box Runner | 380 | 56.5 | 0.033 | 0.83 | 6.39 | 2.60 |
| 10 | João Pedro Cavaco Cancelo | Portugal | Right Back | Box-to-Box Runner | 345 | 56.2 | 0.053 | 0.93 | 6.01 | 5.75 |

The fullback/wingback ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Defensive Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Woo-Young Jung | South Korea | Left Defensive Midfield | Ball-Winner | 318 | 66.7 | 0.066 | 0.82 | 15.00 | 4.25 |
| 2 | Tyler Adams | United States | Center Defensive Midfield | Ball-Winner | 391 | 58.9 | 0.068 | 0.60 | 20.48 | 6.21 |
| 3 | Aurélien Djani Tchouaméni | France | Right Defensive Midfield | Ball-Winner | 662 | 58.8 | 0.227 | 0.75 | 10.74 | 4.89 |
| 4 | Carlos Henrique Casimiro | Brazil | Left Defensive Midfield | Ball-Winner | 409 | 56.3 | 0.301 | 0.50 | 13.20 | 3.30 |
| 5 | Enzo Fernandez | Argentina | Center Defensive Midfield | Ball-Winner | 601 | 56.1 | 0.222 | 0.42 | 17.52 | 3.74 |
| 6 | Thomas Teye Partey | Ghana | Right Defensive Midfield | Ball-Winner | 301 | 56.1 | 0.126 | 0.69 | 12.85 | 3.59 |
| 7 | Frenkie de Jong | Netherlands | Left Defensive Midfield | Ball-Winner | 499 | 55.5 | 0.194 | 0.86 | 14.96 | 3.60 |
| 8 | Wataru Endo | Japan | Right Defensive Midfield | Ball-Winner | 326 | 55.4 | 0.095 | 0.53 | 20.43 | 6.35 |
| 9 | In-Beom Hwang | South Korea | Left Defensive Midfield | Ball-Winner | 360 | 55.3 | 0.101 | 0.44 | 13.50 | 6.50 |
| 10 | Grzegorz Krychowiak | Poland | Center Defensive Midfield | Ball-Winner | 348 | 54.6 | 0.029 | 0.75 | 14.49 | 4.40 |

The defensive midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Central/Wide Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sofiane Boufal | Morocco | Left Midfield | Progressive Winger | 477 | 60.5 | 0.097 | 0.25 | 18.50 | 3.21 |
| 2 | Luka Modrić | Croatia | Right Center Midfield | Ball-Winner | 673 | 59.9 | 0.241 | 0.50 | 17.93 | 4.95 |
| 3 | Piotr Zieliński | Poland | Right Center Midfield | Wide Creator | 344 | 57.9 | 0.208 | 0.50 | 13.33 | 3.92 |
| 4 | Mateo Kovačić | Croatia | Left Center Midfield | Ball-Winner | 650 | 55.5 | 0.121 | 0.75 | 21.19 | 3.88 |
| 5 | Pedro González López | Spain | Left Center Midfield | Ball-Winner | 372 | 55.0 | 0.109 | 0.60 | 14.74 | 6.28 |
| 6 | Ángel Fabián Di María Hernández | Argentina | Right Midfield | Progressive Winger | 305 | 53.6 | 0.232 | 0.00 | 10.92 | 2.95 |
| 7 | Vinícius José Paixão de Oliveira Júnior | Brazil | Left Midfield | Progressive Winger | 307 | 45.6 | 0.280 | 0.00 | 12.04 | 4.40 |
| 8 | Yunus Dimoara Musah | United States | Right Center Midfield | Ball-Winner | 365 | 45.0 | 0.101 | 0.25 | 19.24 | 4.44 |
| 9 | Bernardo Mota Veiga de Carvalho e Silva | Portugal | Right Center Midfield | Ball-Winner | 382 | 41.3 | 0.092 | 0.12 | 14.60 | 4.95 |
| 10 | Azzedine Ounahi | Morocco | Right Center Midfield | Ball-Winner | 589 | 35.9 | 0.073 | 0.29 | 16.04 | 4.73 |

The central/wide midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Attacking Midfield/Wing

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | João Félix Sequeira | Portugal | Left Wing | Target Forward | 340 | 64.1 | 0.193 | 0.50 | 8.99 | 2.38 |
| 2 | Ismaïla Sarr | Senegal | Left Wing | Target Forward | 365 | 63.7 | 0.481 | 0.50 | 13.31 | 3.94 |
| 3 | Ousmane Dembélé | France | Right Wing | Progressive Winger | 448 | 61.3 | 0.119 | 0.50 | 18.88 | 4.22 |
| 4 | Lionel Andrés Messi Cuccittini | Argentina | Right Wing | Progressive Winger | 734 | 60.2 | 1.004 | 0.33 | 10.91 | 3.68 |
| 5 | Heung-Min Son | South Korea | Left Wing | Target Forward | 390 | 55.4 | 0.119 | 0.17 | 8.78 | 3.23 |
| 6 | Raphael Dias Belloli | Brazil | Right Wing | Progressive Winger | 330 | 50.2 | 0.294 | 0.00 | 15.52 | 4.36 |
| 7 | Boulaye Dia | Senegal | Center Attacking Midfield | Target Forward | 330 | 49.6 | 0.179 | 0.36 | 8.73 | 2.18 |
| 8 | Timothy Weah | United States | Right Wing | Target Forward | 318 | 49.4 | 0.155 | 0.20 | 7.36 | 3.68 |
| 9 | Hakim Ziyech | Morocco | Right Wing | Wide Creator | 663 | 47.4 | 0.175 | 0.33 | 20.64 | 3.26 |
| 10 | Christian Pulisic | United States | Left Wing | Progressive Winger | 336 | 47.3 | 0.350 | 0.40 | 11.77 | 4.55 |

The attacking midfield/wing ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Forward

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Mehdi Taremi | Iran | Center Forward | Target Forward | 305 | 60.7 | 0.447 | 0.39 | 19.47 | 3.54 |
| 2 | Olivier Giroud | France | Center Forward | Target Forward | 433 | 59.2 | 0.633 | 0.56 | 12.69 | 0.62 |
| 3 | Kylian Mbappé Lottin | France | Left Center Forward | Progressive Winger | 654 | 55.1 | 0.728 | 0.25 | 5.23 | 3.99 |
| 4 | Richarlison de Andrade | Brazil | Center Forward | Target Forward | 328 | 53.3 | 0.458 | 0.23 | 16.45 | 4.39 |
| 5 | Breel-Donald Embolo | Switzerland | Center Forward | Target Forward | 330 | 52.3 | 0.656 | 0.22 | 13.08 | 1.09 |
| 6 | Harry Kane | England | Center Forward | Target Forward | 422 | 52.1 | 0.517 | 0.48 | 6.62 | 2.56 |
| 7 | Julián Álvarez | Argentina | Center Forward | Target Forward | 485 | 49.5 | 0.355 | 0.25 | 22.26 | 2.60 |
| 8 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Center Forward | Target Forward | 303 | 47.5 | 0.587 | 0.50 | 6.24 | 1.49 |
| 9 | Youssef En-Nesyri | Morocco | Center Forward | Target Forward | 554 | 46.1 | 0.163 | 0.54 | 18.36 | 1.95 |
| 10 | Robert Lewandowski | Poland | Center Forward | Target Forward | 390 | 43.2 | 0.733 | 0.45 | 9.70 | 2.77 |

The forward ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

# Recommended coaching workflow

1. Select the opponent's team section and identify its observed attack style, transition exposure, and physical matchup deltas.
2. Pull video for the stated highest-volume review pattern; confirm that the possession labels match the intended tactical interpretation.
3. Use the position leaderboard only to identify candidate role profiles, then check the player's own team context and tournament minutes.
4. Re-run the substitution or style scenario with the expected match state and available squad before training it.
5. Record the pre-match hypothesis and post-match outcome so future calibration can separate useful signals from tournament-specific noise.

# Limitations and validity

- The analysis is valid as an exploratory and predictive decision-support artifact over the supplied tournament data. It is not a randomized or causal study.
- V4 preserves the schema-checked calibrated transition classifier and 64-match leave-one-match-out audit while replacing the player layer with 300-minute eligibility, SB360 spatial context, and role-relative scoring. Threshold abstention still prevents weak transition warnings.
- Rare transition events create high variance. Aggregate patterns and precision-aware decisions are safer than interpreting individual possessions as certain events.
- Player physicality uses event-derived proxies: ground-duel wins approximate tackle-related success, and recoveries approximate defensive recovery activity.
- Player rankings cover 142 eligible 300+ minute players from 680 observed players; they do not measure performance outside this competition.
- Recommended actions require video confirmation and domain review. Medical status, fatigue, tactical instructions, score state, and opposition substitutions can materially change the correct decision.

---

Generated reproducibly from the processed possession, player-profile, matchup, audit, and simulation artifacts in this repository.
