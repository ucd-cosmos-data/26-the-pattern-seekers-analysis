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
- **Final player rating:** one cross-role score using 50% VAEP total per 90, 30% VAEP per touch, and 20% xT per 90.

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
| Successful action endpoints | 54,286 |
| Linked SB360 actor snapshots | 93,757 |
| Events with SB360 context | 203,454 |
| Player heatmaps | 142 |
| Team reports | 32 |
| Compiled report files | 64 |
| Eligible substitutions | 0 |
| Suppressed substitutions | 3608 |

All V4 acceptance gates passed, including missing-value-free output, complete OOF team coverage, held-out-match exclusion, the 300-minute cutoff, fullback spatial-role safeguards, exact pressure discounting, within-role normalization, SB360 coverage, counterfactual safety, compiled-report completeness, and locked-classifier replay.
**Spatial boundary:** StatsBomb 360 contains event-time freeze-frame snapshots, not continuous optical tracking. Heatmaps show observed successful endpoints and visible actor snapshots; they do not interpolate unobserved runs.

### Unified 360-VAEP + xT player evaluations

| Rank | Player | Team | Minutes | VAEP/90 | VAEP/touch | xT/90 | Rating |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Argentina | 734 | +0.6941 | +0.00416 | +0.1579 | +0.3297 |
| 2 | Kylian Mbappé Lottin | France | 654 | +0.6431 | +0.00462 | +0.1343 | +0.3127 |
| 3 | Richarlison de Andrade | Brazil | 328 | +0.7080 | +0.00993 | +0.0119 | +0.2984 |
| 4 | Julián Álvarez | Argentina | 485 | +0.6361 | +0.00749 | +0.0323 | +0.2905 |
| 5 | Ángel Fabián Di María Hernández | Argentina | 305 | +0.7859 | +0.00447 | +0.1997 | +0.2879 |
| 6 | Cristiano Ronaldo dos Santos Aveiro | Portugal | 303 | +0.6654 | +0.00700 | +0.0091 | +0.2844 |
| 7 | Memphis Depay | Netherlands | 316 | +0.5892 | +0.00421 | +0.0469 | +0.2694 |
| 8 | Daniel Olmo Carvajal | Spain | 388 | +0.5547 | +0.00345 | +0.0722 | +0.2554 |
| 9 | Christian Pulisic | United States | 336 | +0.5271 | +0.00392 | +0.1139 | +0.2496 |
| 10 | Raphael Dias Belloli | Brazil | 330 | +0.4774 | +0.00346 | +0.1698 | +0.2420 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Attacking Midfield/Wing | Progressive Winger | 734 | 0.3297 | 0.694 |
| 2 | Julián Álvarez | Forward | Target Forward | 485 | 0.2905 | 0.636 |
| 3 | Ángel Fabián Di María Hernández | Central/Wide Midfield | Progressive Winger | 305 | 0.2879 | 0.786 |
| 4 | Marcos Javier Acuña | Fullback/Wingback | Attacking Wingback | 397 | 0.1687 | 0.446 |
| 5 | Alexis Mac Allister | Central/Wide Midfield | Ball-Winner | 552 | 0.1423 | 0.284 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mathew Leckie | Central/Wide Midfield | Target Forward | 342 | 0.1368 | 0.259 |
| 2 | Jackson Irvine | Forward | Ball-Winner | 374 | 0.1088 | 0.009 |
| 3 | Aziz Eraltay Behich | Fullback/Wingback | Wide Creator | 387 | 0.0793 | 0.144 |
| 4 | Aaron Mooy | Defensive Midfield | Box-to-Box Runner | 387 | 0.0121 | -0.015 |
| 5 | Kye Rowles | Center Back | Sweeper CB | 387 | -0.0346 | -0.110 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Richarlison de Andrade | Forward | Target Forward | 328 | 0.2984 | 0.708 |
| 2 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 330 | 0.2420 | 0.477 |
| 3 | Vinícius José Paixão de Oliveira Júnior | Central/Wide Midfield | Progressive Winger | 307 | 0.2296 | 0.584 |
| 4 | Lucas Tolentino Coelho de Lima | Defensive Midfield | Ball-Winner | 319 | 0.0589 | 0.155 |
| 5 | Éder Gabriel Militão | Fullback/Wingback | Box-to-Box Runner | 364 | 0.0570 | 0.068 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ivan Perišić | Attacking Midfield/Wing | Wide Creator | 687 | 0.2144 | 0.407 |
| 2 | Andrej Kramarić | Attacking Midfield/Wing | Target Forward | 478 | 0.1937 | 0.365 |
| 3 | Mateo Kovačić | Central/Wide Midfield | Ball-Winner | 650 | 0.1302 | 0.225 |
| 4 | Luka Modrić | Central/Wide Midfield | Ball-Winner | 673 | 0.0858 | 0.087 |
| 5 | Borna Sosa | Fullback/Wingback | Wide Creator | 440 | 0.0781 | 0.130 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Harry Kane | Forward | Target Forward | 422 | 0.1828 | 0.275 |
| 2 | Luke Shaw | Fullback/Wingback | Wide Creator | 457 | 0.1223 | 0.269 |
| 3 | Jude Bellingham | Defensive Midfield | Ball-Winner | 442 | 0.1069 | 0.300 |
| 4 | Harry Maguire | Center Back | Deep Playmaker | 454 | 0.0462 | 0.150 |
| 5 | Declan Rice | Defensive Midfield | Ball-Winner | 450 | 0.0276 | 0.043 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Kylian Mbappé Lottin | Forward | Progressive Winger | 654 | 0.3127 | 0.643 |
| 2 | Olivier Giroud | Forward | Target Forward | 433 | 0.2377 | 0.476 |
| 3 | Ousmane Dembélé | Attacking Midfield/Wing | Progressive Winger | 448 | 0.2020 | 0.351 |
| 4 | Antoine Griezmann | Attacking Midfield/Wing | Ball-Winner | 586 | 0.1995 | 0.343 |
| 5 | Adrien Rabiot | Defensive Midfield | Ball-Winner | 529 | 0.0915 | 0.246 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mohamed Salisu | Center Back | Sweeper CB | 301 | 0.0010 | 0.013 |
| 2 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 301 | -0.0002 | -0.078 |
| 3 | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 301 | -0.0554 | -0.119 |
| 4 | Daniel Amartey | Center Back | Sweeper CB | 301 | -0.0630 | -0.238 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mehdi Taremi | Forward | Target Forward | 305 | 0.2247 | 0.412 |
| 2 | Morteza Pouraliganji | Center Back | Sweeper CB | 305 | 0.0105 | 0.054 |
| 3 | Seyed Majid Hosseini | Center Back | Sweeper CB | 305 | -0.0246 | -0.084 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Daichi Kamada | Attacking Midfield/Wing | Target Forward | 337 | 0.1462 | 0.174 |
| 2 | Junya Ito | Fullback/Wingback | Attacking Wingback | 346 | 0.0744 | 0.121 |
| 3 | Wataru Endo | Defensive Midfield | Ball-Winner | 326 | 0.0148 | -0.014 |
| 4 | Maya Yoshida | Center Back | Sweeper CB | 413 | -0.0403 | -0.129 |
| 5 | Shūichi Gonda | Goalkeeper | Goalkeeper | 413 | -0.0686 | -0.162 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Youssef En-Nesyri | Forward | Target Forward | 554 | 0.1563 | 0.228 |
| 2 | Sofiane Boufal | Central/Wide Midfield | Progressive Winger | 477 | 0.1268 | 0.205 |
| 3 | Hakim Ziyech | Attacking Midfield/Wing | Box-to-Box Runner | 663 | 0.1034 | 0.084 |
| 4 | Azzedine Ounahi | Central/Wide Midfield | Ball-Winner | 589 | 0.0974 | 0.137 |
| 5 | Yahia Attiyat allah | Fullback/Wingback | Wide Creator | 350 | 0.0839 | 0.165 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Memphis Depay | Forward | Target Forward | 316 | 0.2694 | 0.589 |
| 2 | Cody Mathès Gakpo | Attacking Midfield/Wing | Progressive Winger | 460 | 0.1895 | 0.324 |
| 3 | Daley Blind | Fullback/Wingback | Wide Creator | 452 | 0.0791 | 0.140 |
| 4 | Denzel Dumfries | Fullback/Wingback | Attacking Wingback | 510 | 0.0780 | 0.136 |
| 5 | Frenkie de Jong | Defensive Midfield | Ball-Winner | 499 | 0.0336 | 0.060 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Robert Lewandowski | Forward | Target Forward | 390 | 0.2195 | 0.410 |
| 2 | Piotr Zieliński | Central/Wide Midfield | Ball-Winner | 344 | 0.0952 | 0.089 |
| 3 | Bartosz Bereszyński | Fullback/Wingback | Wide Creator | 366 | 0.0608 | 0.078 |
| 4 | Grzegorz Krychowiak | Defensive Midfield | Ball-Winner | 348 | 0.0197 | 0.012 |
| 5 | Matty Cash | Fullback/Wingback | Box-to-Box Runner | 390 | 0.0124 | -0.090 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 303 | 0.2844 | 0.665 |
| 2 | João Félix Sequeira | Attacking Midfield/Wing | Target Forward | 340 | 0.2101 | 0.405 |
| 3 | Bruno Miguel Borges Fernandes | Attacking Midfield/Wing | Progressive Winger | 385 | 0.1671 | 0.220 |
| 4 | Bernardo Mota Veiga de Carvalho e Silva | Central/Wide Midfield | Ball-Winner | 382 | 0.1382 | 0.251 |
| 5 | Raphaël Adelino José Guerreiro | Fullback/Wingback | Wide Creator | 304 | 0.1134 | 0.267 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ismaïla Sarr | Attacking Midfield/Wing | Target Forward | 365 | 0.2237 | 0.436 |
| 2 | Boulaye Dia | Attacking Midfield/Wing | Target Forward | 330 | 0.1654 | 0.256 |
| 3 | Youssouf Sabaly | Fullback/Wingback | Box-to-Box Runner | 387 | 0.0749 | 0.115 |
| 4 | Kalidou Koulibaly | Center Back | Sweeper CB | 387 | 0.0102 | 0.044 |
| 5 | Abdou Diallo | Center Back | Sweeper CB | 349 | -0.0118 | -0.044 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Heung-Min Son | Attacking Midfield/Wing | Target Forward | 390 | 0.2082 | 0.385 |
| 2 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 341 | 0.0983 | 0.216 |
| 3 | Moon-Hwan Kim | Fullback/Wingback | Attacking Wingback | 390 | 0.0784 | 0.140 |
| 4 | In-Beom Hwang | Defensive Midfield | Box-to-Box Runner | 360 | 0.0494 | 0.106 |
| 5 | Woo-Young Jung | Defensive Midfield | Ball-Winner | 318 | 0.0200 | 0.001 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Daniel Olmo Carvajal | Attacking Midfield/Wing | Progressive Winger | 388 | 0.2554 | 0.555 |
| 2 | Pedro González López | Central/Wide Midfield | Ball-Winner | 372 | 0.1236 | 0.180 |
| 3 | Rodrigo Hernández Cascante | Center Back | Deep Playmaker | 414 | 0.0147 | 0.043 |
| 4 | Aymeric Laporte | Center Back | Deep Playmaker | 317 | 0.0089 | 0.040 |
| 5 | Sergio Busquets i Burgos | Defensive Midfield | Ball-Winner | 379 | 0.0032 | -0.055 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Breel-Donald Embolo | Forward | Target Forward | 330 | 0.1938 | 0.312 |
| 2 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Wide Creator | 380 | 0.0457 | 0.024 |
| 3 | Granit Xhaka | Defensive Midfield | Ball-Winner | 387 | 0.0345 | 0.056 |
| 4 | Remo Freuler | Defensive Midfield | Ball-Winner | 346 | 0.0287 | 0.047 |
| 5 | Manuel Obafemi Akanji | Center Back | Deep Playmaker | 387 | 0.0063 | 0.031 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Christian Pulisic | Attacking Midfield/Wing | Progressive Winger | 336 | 0.2496 | 0.527 |
| 2 | Timothy Weah | Attacking Midfield/Wing | Progressive Winger | 318 | 0.2230 | 0.466 |
| 3 | Yunus Dimoara Musah | Central/Wide Midfield | Ball-Winner | 365 | 0.1005 | 0.118 |
| 4 | Antonee Robinson | Fullback/Wingback | Wide Creator | 386 | 0.0958 | 0.186 |
| 5 | Sergino Dest | Fullback/Wingback | Box-to-Box Runner | 308 | 0.0741 | 0.103 |

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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
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

| Rank | Player | Position group | Functional role | Minutes | Unified rating | VAEP/90 |
| --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**
> Model: `transition-conceded-v2`
> Target: `transition_conceded`
> Calibration: `platt`
> Threshold status: `no validated threshold`
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

# Top tournament-role players by position

These leaderboards contain only players with at least 300 tournament minutes. Every player uses the same unified VAEP+xT formula, so team rankings no longer sort role-standardized values across incompatible peer groups. Position sections remain navigation aids.

## Unified V4 rating construction

- 360-Augmented VAEP total per 90: 50%.
- VAEP per touch: 30%.
- Independent successful-pass/carry xT per 90: 20%.
- Successful event endpoints and SB360 actor snapshots use the StatsBomb 120x80 pitch.
- Fullbacks above 35% combined final-third share are classified as Attacking Wingbacks.


**Goalkeeper warning:** the source features do not provide a complete provider post-shot-xG model. The report uses on-target StatsBomb shot xG as an explicitly labeled proxy, then adds goals prevented, claims, sweeping location, and pressured distribution. It remains unsuitable as a standalone goalkeeper selection model.

## Goalkeeper

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Damián Emiliano Martínez | Argentina | Goalkeeper | Goalkeeper | 734 | 0.0776 | 0.256 | 0.002 | 0.00 | 0.00 | 3.68 |
| 2 | Andries Noppert | Netherlands | Goalkeeper | Goalkeeper | 510 | -0.0018 | 0.054 | 0.001 | 0.00 | 0.00 | 4.59 |
| 3 | Hugo Lloris | France | Goalkeeper | Goalkeeper | 614 | -0.0381 | -0.065 | 0.006 | 0.00 | 0.00 | 2.34 |
| 4 | Edouard Mendy | Senegal | Goalkeeper | Goalkeeper | 387 | -0.0516 | -0.104 | 0.005 | 0.00 | 0.00 | 3.72 |
| 5 | Diogo Meireles Costa | Portugal | Goalkeeper | Goalkeeper | 489 | -0.0528 | -0.107 | 0.002 | 0.00 | 0.18 | 2.76 |
| 6 | Alisson Ramsés Becker | Brazil | Goalkeeper | Goalkeeper | 395 | -0.0537 | -0.109 | 0.001 | 0.00 | 0.00 | 5.01 |
| 7 | Jordan Pickford | England | Goalkeeper | Goalkeeper | 486 | -0.0552 | -0.115 | 0.003 | 0.00 | 0.00 | 2.96 |
| 8 | Lawrence Ati-Zigi | Ghana | Goalkeeper | Goalkeeper | 301 | -0.0554 | -0.119 | 0.007 | 0.00 | 0.00 | 2.39 |
| 9 | Matthew Charles Turner | United States | Goalkeeper | Goalkeeper | 391 | -0.0581 | -0.126 | 0.003 | 0.00 | 0.00 | 3.91 |
| 10 | Unai Simón Mendibil | Spain | Goalkeeper | Goalkeeper | 414 | -0.0582 | -0.125 | 0.001 | 0.00 | 0.00 | 2.61 |

The goalkeeper ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Center Back

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Harry Maguire | England | Left Center Back | Deep Playmaker | 454 | 0.0462 | 0.150 | 0.035 | 0.76 | 4.36 | 2.98 |
| 2 | Kléper Laveran Lima Ferreira | Portugal | Right Center Back | Sweeper CB | 389 | 0.0182 | 0.068 | 0.024 | 0.65 | 4.86 | 4.16 |
| 3 | Rodrigo Hernández Cascante | Spain | Right Center Back | Deep Playmaker | 414 | 0.0147 | 0.043 | 0.050 | 0.75 | 5.00 | 4.35 |
| 4 | John Stones | England | Right Center Back | Deep Playmaker | 465 | 0.0140 | 0.052 | 0.010 | 0.73 | 3.10 | 1.94 |
| 5 | Young-Gwon Kim | South Korea | Left Center Back | Sweeper CB | 373 | 0.0134 | 0.052 | 0.023 | 0.78 | 5.06 | 1.93 |
| 6 | Morteza Pouraliganji | Iran | Right Center Back | Sweeper CB | 305 | 0.0105 | 0.054 | 0.009 | 0.75 | 10.62 | 2.36 |
| 7 | Kalidou Koulibaly | Senegal | Right Center Back | Sweeper CB | 387 | 0.0102 | 0.044 | 0.011 | 0.80 | 9.30 | 4.65 |
| 8 | Aymeric Laporte | Spain | Left Center Back | Deep Playmaker | 317 | 0.0089 | 0.040 | 0.025 | 0.67 | 4.26 | 1.14 |
| 9 | Manuel Obafemi Akanji | Switzerland | Left Center Back | Deep Playmaker | 387 | 0.0063 | 0.031 | 0.011 | 0.73 | 6.98 | 2.10 |
| 10 | Ibrahima Konaté | France | Left Center Back | Deep Playmaker | 331 | 0.0052 | 0.023 | 0.029 | 0.90 | 6.80 | 3.54 |

The center back ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Fullback/Wingback

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Marcos Javier Acuña | Argentina | Left Back | Attacking Wingback | 397 | 0.1687 | 0.446 | 0.068 | 0.56 | 12.45 | 4.08 |
| 2 | Luke Shaw | England | Left Back | Wide Creator | 457 | 0.1223 | 0.269 | 0.085 | 0.43 | 6.69 | 2.76 |
| 3 | Raphaël Adelino José Guerreiro | Portugal | Left Back | Wide Creator | 304 | 0.1134 | 0.267 | 0.076 | 0.67 | 8.30 | 2.37 |
| 4 | João Pedro Cavaco Cancelo | Portugal | Right Back | Box-to-Box Runner | 345 | 0.1023 | 0.221 | 0.068 | 0.93 | 6.01 | 5.75 |
| 5 | Nicolás Alejandro Tagliafico | Argentina | Left Back | Wide Creator | 393 | 0.1020 | 0.232 | 0.021 | 0.89 | 13.73 | 2.97 |
| 6 | Jin-Su Kim | South Korea | Left Back | Attacking Wingback | 341 | 0.0983 | 0.216 | 0.041 | 0.56 | 7.66 | 3.17 |
| 7 | Antonee Robinson | United States | Left Back | Wide Creator | 386 | 0.0958 | 0.186 | 0.085 | 0.25 | 14.45 | 7.22 |
| 8 | Theo Bernard François Hernández | France | Left Back | Wide Creator | 548 | 0.0850 | 0.159 | 0.047 | 0.60 | 12.63 | 3.94 |
| 9 | Yahia Attiyat allah | Morocco | Left Back | Wide Creator | 350 | 0.0839 | 0.165 | 0.033 | 0.20 | 11.31 | 5.14 |
| 10 | Aziz Eraltay Behich | Australia | Left Back | Wide Creator | 387 | 0.0793 | 0.144 | 0.044 | 0.75 | 9.07 | 3.49 |

The fullback/wingback ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Defensive Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jude Bellingham | England | Right Defensive Midfield | Ball-Winner | 442 | 0.1069 | 0.300 | 0.042 | 0.44 | 15.08 | 6.11 |
| 2 | Rodrigo Javier De Paul | Argentina | Right Defensive Midfield | Box-to-Box Runner | 635 | 0.0940 | 0.227 | 0.052 | 0.33 | 18.01 | 4.82 |
| 3 | Adrien Rabiot | France | Left Defensive Midfield | Ball-Winner | 529 | 0.0915 | 0.246 | 0.013 | 0.67 | 15.98 | 3.57 |
| 4 | Lucas Tolentino Coelho de Lima | Brazil | Right Defensive Midfield | Ball-Winner | 319 | 0.0589 | 0.155 | 0.043 | 0.50 | 17.79 | 2.54 |
| 5 | In-Beom Hwang | South Korea | Left Defensive Midfield | Box-to-Box Runner | 360 | 0.0494 | 0.106 | 0.061 | 0.44 | 13.50 | 6.50 |
| 6 | Granit Xhaka | Switzerland | Left Defensive Midfield | Ball-Winner | 387 | 0.0345 | 0.056 | 0.049 | 0.58 | 7.92 | 2.10 |
| 7 | Frenkie de Jong | Netherlands | Left Defensive Midfield | Ball-Winner | 499 | 0.0336 | 0.060 | 0.028 | 0.86 | 14.96 | 3.60 |
| 8 | Remo Freuler | Switzerland | Right Defensive Midfield | Ball-Winner | 346 | 0.0287 | 0.047 | 0.020 | 0.62 | 17.17 | 3.12 |
| 9 | Declan Rice | England | Left Defensive Midfield | Ball-Winner | 450 | 0.0276 | 0.043 | 0.022 | 0.56 | 10.01 | 3.80 |
| 10 | Enzo Fernandez | Argentina | Center Defensive Midfield | Ball-Winner | 601 | 0.0209 | 0.009 | 0.060 | 0.42 | 17.52 | 3.74 |

The defensive midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Central/Wide Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ángel Fabián Di María Hernández | Argentina | Right Midfield | Progressive Winger | 305 | 0.2879 | 0.786 | 0.200 | 0.00 | 10.92 | 2.95 |
| 2 | Vinícius José Paixão de Oliveira Júnior | Brazil | Left Midfield | Progressive Winger | 307 | 0.2296 | 0.584 | 0.124 | 0.00 | 12.04 | 4.40 |
| 3 | Alexis Mac Allister | Argentina | Left Center Midfield | Ball-Winner | 552 | 0.1423 | 0.284 | 0.007 | 0.31 | 12.38 | 4.40 |
| 4 | Bernardo Mota Veiga de Carvalho e Silva | Portugal | Right Center Midfield | Ball-Winner | 382 | 0.1382 | 0.251 | 0.058 | 0.12 | 14.60 | 4.95 |
| 5 | Mathew Leckie | Australia | Right Midfield | Target Forward | 342 | 0.1368 | 0.259 | 0.021 | 0.57 | 18.44 | 4.22 |
| 6 | Mateo Kovačić | Croatia | Left Center Midfield | Ball-Winner | 650 | 0.1302 | 0.225 | 0.065 | 0.75 | 21.19 | 3.88 |
| 7 | Sofiane Boufal | Morocco | Left Midfield | Progressive Winger | 477 | 0.1268 | 0.205 | 0.079 | 0.25 | 18.50 | 3.21 |
| 8 | Pedro González López | Spain | Left Center Midfield | Ball-Winner | 372 | 0.1236 | 0.180 | 0.105 | 0.60 | 14.74 | 6.28 |
| 9 | Yunus Dimoara Musah | United States | Right Center Midfield | Ball-Winner | 365 | 0.1005 | 0.118 | 0.046 | 0.25 | 19.24 | 4.44 |
| 10 | Azzedine Ounahi | Morocco | Right Center Midfield | Ball-Winner | 589 | 0.0974 | 0.137 | 0.036 | 0.29 | 16.04 | 4.73 |

The central/wide midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Attacking Midfield/Wing

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Right Wing | Progressive Winger | 734 | 0.3297 | 0.694 | 0.158 | 0.33 | 10.91 | 3.68 |
| 2 | Daniel Olmo Carvajal | Spain | Left Wing | Progressive Winger | 388 | 0.2554 | 0.555 | 0.072 | 0.17 | 12.05 | 3.94 |
| 3 | Christian Pulisic | United States | Left Wing | Progressive Winger | 336 | 0.2496 | 0.527 | 0.114 | 0.40 | 11.77 | 4.55 |
| 4 | Raphael Dias Belloli | Brazil | Right Wing | Progressive Winger | 330 | 0.2420 | 0.477 | 0.170 | 0.00 | 15.52 | 4.36 |
| 5 | Ismaïla Sarr | Senegal | Left Wing | Target Forward | 365 | 0.2237 | 0.436 | 0.090 | 0.50 | 13.31 | 3.94 |
| 6 | Timothy Weah | United States | Right Wing | Progressive Winger | 318 | 0.2230 | 0.466 | 0.018 | 0.20 | 7.36 | 3.68 |
| 7 | Ivan Perišić | Croatia | Left Wing | Wide Creator | 687 | 0.2144 | 0.407 | 0.065 | 0.50 | 14.28 | 2.75 |
| 8 | João Félix Sequeira | Portugal | Left Wing | Target Forward | 340 | 0.2101 | 0.405 | 0.046 | 0.50 | 8.99 | 2.38 |
| 9 | Heung-Min Son | South Korea | Left Wing | Target Forward | 390 | 0.2082 | 0.385 | 0.078 | 0.17 | 8.78 | 3.23 |
| 10 | Ousmane Dembélé | France | Right Wing | Progressive Winger | 448 | 0.2020 | 0.351 | 0.112 | 0.50 | 18.88 | 4.22 |

The attacking midfield/wing ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Forward

| Rank | Player | Team | Detailed position | Role | Min. | Rating | VAEP/90 | xT/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kylian Mbappé Lottin | France | Left Center Forward | Progressive Winger | 654 | 0.3127 | 0.643 | 0.134 | 0.25 | 5.23 | 3.99 |
| 2 | Richarlison de Andrade | Brazil | Center Forward | Target Forward | 328 | 0.2984 | 0.708 | 0.012 | 0.23 | 16.45 | 4.39 |
| 3 | Julián Álvarez | Argentina | Center Forward | Target Forward | 485 | 0.2905 | 0.636 | 0.032 | 0.25 | 22.26 | 2.60 |
| 4 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Center Forward | Target Forward | 303 | 0.2844 | 0.665 | 0.009 | 0.50 | 6.24 | 1.49 |
| 5 | Memphis Depay | Netherlands | Left Center Forward | Target Forward | 316 | 0.2694 | 0.589 | 0.047 | 0.20 | 13.12 | 2.00 |
| 6 | Olivier Giroud | France | Center Forward | Target Forward | 433 | 0.2377 | 0.476 | 0.008 | 0.56 | 12.69 | 0.62 |
| 7 | Mehdi Taremi | Iran | Center Forward | Target Forward | 305 | 0.2247 | 0.412 | 0.053 | 0.39 | 19.47 | 3.54 |
| 8 | Robert Lewandowski | Poland | Center Forward | Target Forward | 390 | 0.2195 | 0.410 | 0.019 | 0.45 | 9.70 | 2.77 |
| 9 | Breel-Donald Embolo | Switzerland | Center Forward | Target Forward | 330 | 0.1938 | 0.312 | 0.011 | 0.22 | 13.08 | 1.09 |
| 10 | Harry Kane | England | Center Forward | Target Forward | 422 | 0.1828 | 0.275 | 0.047 | 0.48 | 6.62 | 2.56 |

The forward ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

# Recommended coaching workflow

1. Select the opponent's team section and identify its observed attack style, transition exposure, and physical matchup deltas.
2. Pull video for the stated highest-volume review pattern; confirm that the possession labels match the intended tactical interpretation.
3. Use the position leaderboard only to identify candidate role profiles, then check the player's own team context and tournament minutes.
4. Re-run the substitution or style scenario with the expected match state and available squad before training it.
5. Record the pre-match hypothesis and post-match outcome so future calibration can separate useful signals from tournament-specific noise.

# Limitations and validity

- The analysis is valid as an exploratory and predictive decision-support artifact over the supplied tournament data. It is not a randomized or causal study.
- V4 preserves the schema-checked calibrated transition classifier and 64-match leave-one-match-out audit while replacing the player layer with 300-minute eligibility, SB360 spatial context, and unified VAEP+xT scoring. Threshold abstention still prevents weak transition warnings.
- Rare transition events create high variance. Aggregate patterns and precision-aware decisions are safer than interpreting individual possessions as certain events.
- Player physicality uses event-derived proxies: ground-duel wins approximate tackle-related success, and recoveries approximate defensive recovery activity.
- Player rankings cover 142 eligible 300+ minute players from 680 observed players; they do not measure performance outside this competition.
- Recommended actions require video confirmation and domain review. Medical status, fatigue, tactical instructions, score state, and opposition substitutions can materially change the correct decision.

---

Generated reproducibly from the processed possession, player-profile, matchup, audit, and simulation artifacts in this repository.

<!-- PROSPECTIVE_VALIDATION_START -->
## Prospective possession-model validation

**Overall status: `PARTIAL_PASS_ROLLBACK`.** Box-entry prediction passed every discrimination, calibration, and paired match-bootstrap gate. The shot challenger improved numerically but its confidence interval crossed zero, so it was rejected. The combined prospective artifact was not deployed and the stable production state was preserved.

| Target | Status | Baseline ROC-AUC | Challenger ROC-AUC | PR-AUC | Brier | ECE | Paired ROC gain (90% interval) |
|---|---|---:|---:|---:|---:|---:|---:|
| Box entry | **PASSED** | 0.6888 | 0.7268 | 0.6131 | 0.1722 | 0.0309 | +0.0155 [+0.0106, +0.0205] |
| Shot | **REJECTED** | 0.6642 | 0.6841 | 0.2686 | 0.0960 | 0.0118 | +0.0038 [-0.0030, +0.0120] |

_This challenger is isolated from 360-VAEP/xT player ratings, transition risk, retrospective possession models, and tactical clustering. Player and team descriptive metrics therefore remain unchanged._
<!-- PROSPECTIVE_VALIDATION_END -->

<!-- PLAYER_ROLE_VALIDATION_START -->
## Player-role and valuation validation status

**Production state retained.** The probabilistic role matrix and learned valuation were evaluated as challengers but were not promoted because they missed their predeclared statistical gates.

| Component | Decision | Validation evidence |
|---|---|---|
| Probabilistic GMM roles | **REJECTED** | K=9; silhouette 0.3159; median 500-bootstrap ARI 0.6961 vs required 0.70 |
| Learned Ridge valuation | **REJECTED** | OOF Spearman 0.7095 → 0.7150; gain 95% CI [-0.0053, +0.0165] crosses zero |

The active calibrated 360-VAEP model therefore remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123. Messi remains Argentina rank #1 and Mbappé remains France rank #1; no player-name override was used.
<!-- PLAYER_ROLE_VALIDATION_END -->

<!-- ROLE_AWARE_VALUATION_START -->
## Continuous role-aware valuation A/B test

**Decision: `REJECTED_RETAIN_INCUMBENT`.** The challenger was not promoted. Its Spearman correlation with the incumbent ranking was 0.9854, above the predeclared 0.90 ceiling, so it did not change the overall ordering enough to qualify as the intended systemic correction.

| Benchmark | Incumbent | Challenger diagnostic |
|---|---:|---:|
| Messi global rank | 1 | 1 |
| Mbappé global rank | 2 | 2 |
| Griezmann global rank | 21 | 6 |

The diagnostic Griezmann movement came from creation (0.799), pressing (0.711), and completeness (0.862), with no player-name rule. Nevertheless, all published player/team rankings retain the incumbent 360-VAEP+xT rating.

Foundational model performance remains unchanged: OOF ROC-AUC 0.948994, PR-AUC 0.084827, Brier 0.001123, ECE 0.000336.
<!-- ROLE_AWARE_VALUATION_END -->
