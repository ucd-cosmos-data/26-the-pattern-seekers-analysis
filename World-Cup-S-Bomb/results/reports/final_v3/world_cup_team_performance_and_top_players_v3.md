# World Cup Team Performance and Position-Specific Player Report

## Executive summary

This report consolidates **32 national teams**, **142 players with at least 300 tournament minutes**, **64 matches**, and **11,016 analyzed possessions** into one coaching reference. It combines observed possession outcomes with the regularized empirical hurdle-pipeline scenario audit. The strongest use is opponent preparation, video-review prioritization, and formation of testable tactical hypotheses.

**Important boundary:** observed goals, xG, shots, box entries, and transition exposure describe this tournament sample. Expected net xG, EvA gaps, optimal styles, and substitution gains are model-generated scenarios. They are not causal claims, guarantees, transfer valuations, or replacements for scouting, medical, training, and match-context evidence.

## How to read the metrics

- **xG:** summed shot quality created during the team's possessions.
- **Shot rate:** percentage of possessions containing at least one shot.
- **Box-entry rate:** percentage of possessions entering the penalty area.
- **Transition xG conceded:** opponent xG generated immediately after the team's possessions; lower is better and it is not total defensive xG conceded.
- **Mean EvA gap:** average difference between the best modeled tactic and the observed tactic. It identifies review candidates, not proven coaching errors.
- **Wasted net xG:** cumulative modeled EvA gap across possessions. It scales with possession volume, so compare it alongside the mean gap.
- **Physical matchup deltas:** lineup-minus-opponent aerial, pressing, and recovery proxies. Positive values indicate a modeled lineup edge.
- **Position-impact score:** a within-position V4 shortlist score. For attacking positions, 55% comes from raw and pressure-adjusted OBV, with xG, progressive carries, and SB360-informed final-third presence completing the score. It cannot compare absolute quality across position groups.

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, GAIN_BELOW_THRESHOLD: 15, INSUFFICIENT_MINUTES: 6.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Attacking Midfield/Wing | Progressive Winger | 734 | 77.1 | -0.039 | 46.6% |
| 2 | Ángel Fabián Di María Hernández | Central/Wide Midfield | Progressive Winger | 305 | 59.6 | -0.179 | 62.9% |
| 3 | Enzo Fernandez | Defensive Midfield | Ball-Winner | 601 | 55.8 | 0.159 | 16.4% |
| 4 | Nicolás Alejandro Tagliafico | Fullback/Wingback | Box-to-Box Runner | 393 | 52.6 | -0.113 | 29.8% |
| 5 | Cristian Gabriel Romero | Center Back | Holding Anchor | 576 | 45.4 | 0.229 | 3.8% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 7.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `SUPPORTED_CHANGE`. The style change cleared the tactical effect floor.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Mathew Ryan | Goalkeeper | Goalkeeper | 387 | 61.2 | 0.498 | 1.9% |
| 2 | Aziz Eraltay Behich | Fullback/Wingback | Box-to-Box Runner | 387 | 47.3 | -0.014 | 23.6% |
| 3 | Jackson Irvine | Forward | Ball-Winner | 374 | 46.2 | -0.080 | 25.0% |
| 4 | Harry Souttar | Center Back | Deep Playmaker | 387 | 46.0 | 0.242 | 3.2% |
| 5 | Aaron Mooy | Defensive Midfield | Ball-Winner | 387 | 43.6 | 0.094 | 14.0% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, GAIN_BELOW_THRESHOLD: 10, INSUFFICIENT_MINUTES: 7.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 140, GAIN_BELOW_THRESHOLD: 24, INSUFFICIENT_MINUTES: 1.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Éder Gabriel Militão | Fullback/Wingback | Ball-Winner | 364 | 69.0 | 0.200 | 19.9% |
| 2 | Marcos Aoás Corrêa | Center Back | Holding Anchor | 455 | 60.0 | 0.367 | 8.1% |
| 3 | Thiago Emiliano da Silva | Center Back | Holding Anchor | 409 | 59.8 | 0.436 | 3.4% |
| 4 | Vinícius José Paixão de Oliveira Júnior | Central/Wide Midfield | Progressive Winger | 307 | 57.8 | -0.276 | 62.9% |
| 5 | Carlos Henrique Casimiro | Defensive Midfield | Ball-Winner | 409 | 56.1 | 0.099 | 28.8% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 106, GAIN_BELOW_THRESHOLD: 9, INSUFFICIENT_MINUTES: 6.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 74, INSUFFICIENT_MINUTES: 8, GAIN_BELOW_THRESHOLD: 6.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, GAIN_BELOW_THRESHOLD: 11, INSUFFICIENT_MINUTES: 5.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, GAIN_BELOW_THRESHOLD: 15.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Luka Modrić | Central/Wide Midfield | Ball-Winner | 673 | 69.2 | 0.181 | 21.7% |
| 2 | Dominik Livaković | Goalkeeper | Goalkeeper | 720 | 58.3 | 0.243 | 0.8% |
| 3 | Borna Sosa | Fullback/Wingback | Box-to-Box Runner | 440 | 58.2 | 0.071 | 31.1% |
| 4 | Josip Juranović | Fullback/Wingback | Wide Creator | 624 | 53.2 | 0.037 | 27.8% |
| 5 | Mateo Kovačić | Central/Wide Midfield | Ball-Winner | 650 | 52.8 | 0.081 | 20.7% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 87, GAIN_BELOW_THRESHOLD: 10, INSUFFICIENT_MINUTES: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 68, GAIN_BELOW_THRESHOLD: 7, INSUFFICIENT_MINUTES: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 82, GAIN_BELOW_THRESHOLD: 15, INSUFFICIENT_MINUTES: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | John Stones | Center Back | Holding Anchor | 465 | 57.3 | 0.450 | 2.9% |
| 2 | Harry Kane | Forward | Target Forward | 422 | 52.8 | -0.345 | 53.8% |
| 3 | Jordan Pickford | Goalkeeper | Goalkeeper | 486 | 52.4 | 0.342 | 1.0% |
| 4 | Luke Shaw | Fullback/Wingback | Box-to-Box Runner | 457 | 50.5 | 0.014 | 24.9% |
| 5 | Harry Maguire | Center Back | Holding Anchor | 454 | 48.0 | 0.494 | 5.0% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 122, GAIN_BELOW_THRESHOLD: 17, INSUFFICIENT_MINUTES: 4.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kylian Mbappé Lottin | Forward | Progressive Winger | 654 | 74.9 | -0.157 | 62.8% |
| 2 | Aurélien Djani Tchouaméni | Defensive Midfield | Ball-Winner | 662 | 59.6 | 0.157 | 14.6% |
| 3 | Hugo Lloris | Goalkeeper | Goalkeeper | 614 | 53.1 | 0.431 | 1.1% |
| 4 | Ousmane Dembélé | Attacking Midfield/Wing | Progressive Winger | 448 | 53.0 | -0.123 | 57.3% |
| 5 | Olivier Giroud | Forward | Target Forward | 433 | 52.7 | -0.256 | 41.8% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, GAIN_BELOW_THRESHOLD: 9, INSUFFICIENT_MINUTES: 6.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

**Best substitution scenario:** Kamaldeen Sulemana for Jordan Ayew under Patient Build-up produced the largest estimated team gain (+0.0053 expected net xG). The match-bootstrap 95% interval was [+0.0050, +0.0057]. Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `SUPPORTED_CHANGE`. The style change cleared the tactical effect floor.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 301 | 55.8 | 0.157 | 14.5% |
| 2 | Daniel Amartey | Center Back | Deep Playmaker | 301 | 53.9 | 0.216 | 3.7% |
| 3 | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 301 | 47.8 | 0.309 | 1.2% |
| 4 | Mohamed Salisu | Center Back | Deep Playmaker | 301 | 47.1 | 0.325 | 5.3% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 96, GAIN_BELOW_THRESHOLD: 11, INSUFFICIENT_MINUTES: 3.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Mehdi Taremi | Forward | Target Forward | 305 | 54.7 | -0.233 | 44.3% |
| 2 | Morteza Pouraliganji | Center Back | Deep Playmaker | 305 | 46.3 | 0.133 | 5.0% |
| 3 | Seyed Majid Hosseini | Center Back | Deep Playmaker | 305 | 31.2 | 0.108 | 1.4% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 105, GAIN_BELOW_THRESHOLD: 16.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Shūichi Gonda | Goalkeeper | Goalkeeper | 413 | 56.8 | 0.329 | 1.3% |
| 2 | Wataru Endo | Defensive Midfield | Ball-Winner | 326 | 54.7 | 0.052 | 22.6% |
| 3 | Maya Yoshida | Center Back | Deep Playmaker | 413 | 46.3 | 0.246 | 1.9% |
| 4 | Daichi Kamada | Attacking Midfield/Wing | Ball-Winner | 337 | 42.1 | -0.265 | 38.7% |
| 5 | Junya Ito | Fullback/Wingback | Attacking Wingback | 346 | 41.2 | -0.179 | 42.5% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 95, GAIN_BELOW_THRESHOLD: 12, INSUFFICIENT_MINUTES: 3.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 128, GAIN_BELOW_THRESHOLD: 22, INSUFFICIENT_MINUTES: 4.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Achraf Hakimi Mouh | Fullback/Wingback | Wide Creator | 661 | 60.6 | -0.013 | 28.0% |
| 2 | Romain Saïss | Center Back | Deep Playmaker | 486 | 59.3 | 0.265 | 2.2% |
| 3 | Yahia Attiyat allah | Fullback/Wingback | Box-to-Box Runner | 350 | 57.2 | 0.033 | 20.9% |
| 4 | Hakim Ziyech | Attacking Midfield/Wing | Wide Creator | 663 | 57.0 | -0.048 | 32.4% |
| 5 | Yassine Bounou | Goalkeeper | Goalkeeper | 603 | 52.3 | 0.330 | 0.6% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 92, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 4.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jurriën David Norman Timber | Center Back | Ball-Winner | 409 | 60.1 | 0.218 | 5.4% |
| 2 | Virgil van Dijk | Center Back | Deep Playmaker | 510 | 58.5 | 0.375 | 2.0% |
| 3 | Frenkie de Jong | Defensive Midfield | Ball-Winner | 499 | 55.0 | 0.018 | 18.2% |
| 4 | Daley Blind | Fullback/Wingback | Box-to-Box Runner | 452 | 51.4 | -0.060 | 28.8% |
| 5 | Nathan Aké | Center Back | Holding Anchor | 506 | 49.6 | 0.316 | 5.3% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 90, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 7.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `SUPPORTED_CHANGE`. The style change cleared the tactical effect floor.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Wojciech Szczęsny | Goalkeeper | Goalkeeper | 390 | 73.0 | 0.599 | 2.6% |
| 2 | Piotr Zieliński | Central/Wide Midfield | Wide Creator | 344 | 58.7 | 0.034 | 25.8% |
| 3 | Robert Lewandowski | Forward | Target Forward | 390 | 55.7 | -0.431 | 52.4% |
| 4 | Grzegorz Krychowiak | Defensive Midfield | Ball-Winner | 348 | 53.7 | 0.068 | 16.5% |
| 5 | Matty Cash | Fullback/Wingback | Wide Creator | 390 | 44.9 | 0.003 | 27.2% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 123, GAIN_BELOW_THRESHOLD: 16, INSUFFICIENT_MINUTES: 4.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Raphaël Adelino José Guerreiro | Fullback/Wingback | Box-to-Box Runner | 304 | 59.1 | -0.036 | 33.7% |
| 2 | Bruno Miguel Borges Fernandes | Attacking Midfield/Wing | Wide Creator | 385 | 57.7 | -0.070 | 38.6% |
| 3 | Kléper Laveran Lima Ferreira | Center Back | Deep Playmaker | 389 | 53.1 | 0.388 | 4.1% |
| 4 | Rúben Santos Gato Alves Dias | Center Back | Deep Playmaker | 392 | 51.3 | 0.282 | 1.7% |
| 5 | João Pedro Cavaco Cancelo | Fullback/Wingback | Box-to-Box Runner | 345 | 50.9 | -0.004 | 33.9% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 81, INSUFFICIENT_MINUTES: 11, GAIN_BELOW_THRESHOLD: 7.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 118, GAIN_BELOW_THRESHOLD: 12, INSUFFICIENT_MINUTES: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 79, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 6.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kalidou Koulibaly | Center Back | Deep Playmaker | 387 | 64.1 | 0.321 | 3.3% |
| 2 | Abdou Diallo | Center Back | Deep Playmaker | 349 | 60.5 | 0.356 | 9.0% |
| 3 | Youssouf Sabaly | Fullback/Wingback | Attacking Wingback | 387 | 57.7 | 0.078 | 36.2% |
| 4 | Ismaïla Sarr | Attacking Midfield/Wing | Target Forward | 365 | 55.9 | -0.247 | 65.3% |
| 5 | Edouard Mendy | Goalkeeper | Goalkeeper | 387 | 49.0 | 0.277 | 1.5% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 112, INSUFFICIENT_MINUTES: 12, GAIN_BELOW_THRESHOLD: 8.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 93, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 3.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Young-Gwon Kim | Center Back | Deep Playmaker | 373 | 75.2 | 0.445 | 3.8% |
| 2 | Woo-Young Jung | Defensive Midfield | Ball-Winner | 318 | 70.6 | 0.231 | 17.3% |
| 3 | In-Beom Hwang | Defensive Midfield | Ball-Winner | 360 | 54.6 | 0.173 | 34.6% |
| 4 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 341 | 54.5 | 0.000 | 46.0% |
| 5 | Seung-Gyu Kim | Goalkeeper | Goalkeeper | 390 | 49.7 | 0.327 | 1.2% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 95, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Hernández Cascante | Center Back | Holding Anchor | 414 | 75.8 | 0.667 | 6.9% |
| 2 | Aymeric Laporte | Center Back | Holding Anchor | 317 | 57.6 | 0.641 | 2.1% |
| 3 | Pedro González López | Central/Wide Midfield | Ball-Winner | 372 | 51.8 | 0.083 | 28.3% |
| 4 | Sergio Busquets i Burgos | Defensive Midfield | Ball-Winner | 379 | 49.2 | 0.010 | 22.1% |
| 5 | Daniel Olmo Carvajal | Attacking Midfield/Wing | Progressive Winger | 388 | 44.6 | -0.397 | 54.3% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 121, GAIN_BELOW_THRESHOLD: 13, INSUFFICIENT_MINUTES: 9.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Breel-Donald Embolo | Forward | Target Forward | 330 | 53.4 | -0.338 | 46.4% |
| 2 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Box-to-Box Runner | 380 | 52.3 | 0.037 | 20.9% |
| 3 | Remo Freuler | Defensive Midfield | Ball-Winner | 346 | 49.4 | -0.058 | 25.5% |
| 4 | Manuel Obafemi Akanji | Center Back | Holding Anchor | 387 | 49.3 | 0.360 | 3.7% |
| 5 | Granit Xhaka | Defensive Midfield | Ball-Winner | 387 | 45.3 | 0.102 | 16.0% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 91, GAIN_BELOW_THRESHOLD: 14, INSUFFICIENT_MINUTES: 5.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 84, GAIN_BELOW_THRESHOLD: 11, INSUFFICIENT_MINUTES: 4.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sergino Dest | Fullback/Wingback | Wide Creator | 308 | 73.4 | 0.100 | 31.7% |
| 2 | Christian Pulisic | Attacking Midfield/Wing | Progressive Winger | 336 | 61.6 | -0.171 | 51.7% |
| 3 | Tyler Adams | Defensive Midfield | Ball-Winner | 391 | 59.7 | 0.050 | 14.9% |
| 4 | Antonee Robinson | Fullback/Wingback | Box-to-Box Runner | 386 | 53.9 | -0.066 | 34.3% |
| 5 | Yunus Dimoara Musah | Central/Wide Midfield | Ball-Winner | 365 | 48.9 | -0.058 | 32.8% |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 80, GAIN_BELOW_THRESHOLD: 5, INSUFFICIENT_MINUTES: 3.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

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

> **No validated substitution:** No bench substitution met the +0.0050 Net xG floor and strictly positive confidence interval requirement. Reason codes: POSITIONAL_INCOMPATIBILITY: 71, INSUFFICIENT_MINUTES: 4, GAIN_BELOW_THRESHOLD: 2.

### Tier 3 — Exploratory and Suppressed Decisions

**Tactical decision reason code:** `GAIN_BELOW_THRESHOLD`. The best alternative failed to exceed +0.0050 Net xG.

**Rare-event reason code:** `CLASSIFIER_ABSTAINED`. No probability threshold achieved the required 0.30 precision, so transition warnings remain suppressed rather than converted into weak positive claims.

### Leading V4 position-impact profiles

| Rank | Player | Position group | Functional role | Minutes | Position impact | OBV/90 | Final-third share |
| --- | --- | --- | --- | --- | --- | --- | --- |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

> **Model provenance**  
> Model: `transition-conceded-v2`  
> Target: `transition_conceded`  
> Calibration: `platt`  
> Threshold status: `no validated threshold`  
> OOF audit: 64 matches, 32 teams; each evaluated match was excluded from model fitting and calibration.

# Top tournament-role players by position

These leaderboards use only players with at least 300 tournament minutes. The V4 role score remains normalized strictly within functional role. The coach-facing position-impact score is a separate within-position ranking. For forwards and attacking midfielders/wingers, OBV-family value is the primary signal (55%), followed by xG (30%), progressive carries (10%), and the event-plus-SB360 final-third footprint (5%).

## Position-impact construction

- **Attacking positions:** pressure-adjusted OBV/90 30%, raw OBV/90 25%, xG/90 30%, progressive carries/90 10%, final-third share 5%.
- **Other positions:** the V4 functional-role composite is re-expressed within position group for the coach-facing shortlist.

**Goalkeeper warning:** the source features do not provide a complete provider post-shot-xG model. The report uses on-target StatsBomb shot xG as an explicitly labeled proxy, then adds goals prevented, claims, sweeping location, and pressured distribution. It remains unsuitable as a standalone goalkeeper selection model.

## Goalkeeper

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Wojciech Szczęsny | Poland | Goalkeeper | Goalkeeper | 390 | 73.0 | 1 | 73.0 | 0.599 | 2.6% |
| 2 | Mathew Ryan | Australia | Goalkeeper | Goalkeeper | 387 | 61.2 | 2 | 61.2 | 0.498 | 1.9% |
| 3 | Dominik Livaković | Croatia | Goalkeeper | Goalkeeper | 720 | 58.3 | 3 | 58.3 | 0.243 | 0.8% |
| 4 | Shūichi Gonda | Japan | Goalkeeper | Goalkeeper | 413 | 56.8 | 4 | 56.8 | 0.329 | 1.3% |
| 5 | Hugo Lloris | France | Goalkeeper | Goalkeeper | 614 | 53.1 | 5 | 53.1 | 0.431 | 1.1% |
| 6 | Jordan Pickford | England | Goalkeeper | Goalkeeper | 486 | 52.4 | 6 | 52.4 | 0.342 | 1.0% |
| 7 | Yassine Bounou | Morocco | Goalkeeper | Goalkeeper | 603 | 52.3 | 7 | 52.3 | 0.330 | 0.6% |
| 8 | Diogo Meireles Costa | Portugal | Goalkeeper | Goalkeeper | 489 | 50.6 | 8 | 50.6 | 0.295 | 0.8% |
| 9 | Seung-Gyu Kim | South Korea | Goalkeeper | Goalkeeper | 390 | 49.7 | 9 | 49.7 | 0.327 | 1.2% |
| 10 | Edouard Mendy | Senegal | Goalkeeper | Goalkeeper | 387 | 49.0 | 10 | 49.0 | 0.277 | 1.5% |

The goalkeeper ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Center Back

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Hernández Cascante | Spain | Right Center Back | Holding Anchor | 414 | 75.8 | 1 | 76.1 | 0.667 | 6.9% |
| 2 | Young-Gwon Kim | South Korea | Left Center Back | Deep Playmaker | 373 | 75.2 | 2 | 75.5 | 0.445 | 3.8% |
| 3 | Kalidou Koulibaly | Senegal | Right Center Back | Deep Playmaker | 387 | 64.1 | 3 | 64.4 | 0.321 | 3.3% |
| 4 | Abdou Diallo | Senegal | Left Center Back | Deep Playmaker | 349 | 60.5 | 4 | 60.8 | 0.356 | 9.0% |
| 5 | Jurriën David Norman Timber | Netherlands | Right Center Back | Ball-Winner | 409 | 60.1 | 5 | 60.4 | 0.218 | 5.4% |
| 6 | Marcos Aoás Corrêa | Brazil | Left Center Back | Holding Anchor | 455 | 60.0 | 6 | 60.3 | 0.367 | 8.1% |
| 7 | Thiago Emiliano da Silva | Brazil | Right Center Back | Holding Anchor | 409 | 59.8 | 7 | 60.0 | 0.436 | 3.4% |
| 8 | Romain Saïss | Morocco | Left Center Back | Deep Playmaker | 486 | 59.3 | 8 | 59.6 | 0.265 | 2.2% |
| 9 | Virgil van Dijk | Netherlands | Center Back | Deep Playmaker | 510 | 58.5 | 9 | 58.8 | 0.375 | 2.0% |
| 10 | Aymeric Laporte | Spain | Left Center Back | Holding Anchor | 317 | 57.6 | 10 | 57.9 | 0.641 | 2.1% |

The center back ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Fullback/Wingback

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Sergino Dest | United States | Right Back | Wide Creator | 308 | 73.4 | 1 | 66.3 | 0.100 | 31.7% |
| 2 | Éder Gabriel Militão | Brazil | Right Back | Ball-Winner | 364 | 69.0 | 2 | 67.0 | 0.200 | 19.9% |
| 3 | Achraf Hakimi Mouh | Morocco | Right Back | Wide Creator | 661 | 60.6 | 3 | 53.7 | -0.013 | 28.0% |
| 4 | Raphaël Adelino José Guerreiro | Portugal | Left Back | Box-to-Box Runner | 304 | 59.1 | 4 | 50.1 | -0.036 | 33.7% |
| 5 | Borna Sosa | Croatia | Left Back | Box-to-Box Runner | 440 | 58.2 | 5 | 71.9 | 0.071 | 31.1% |
| 6 | Youssouf Sabaly | Senegal | Right Back | Attacking Wingback | 387 | 57.7 | 6 | 62.2 | 0.078 | 36.2% |
| 7 | Yahia Attiyat allah | Morocco | Left Back | Box-to-Box Runner | 350 | 57.2 | 7 | 58.1 | 0.033 | 20.9% |
| 8 | Jin-Su Kim | South Korea | Left Back | Attacking Wingback | 341 | 54.5 | 8 | 63.8 | 0.000 | 46.0% |
| 9 | Antonee Robinson | United States | Left Back | Box-to-Box Runner | 386 | 53.9 | 9 | 37.4 | -0.066 | 34.3% |
| 10 | Josip Juranović | Croatia | Right Back | Wide Creator | 624 | 53.2 | 10 | 59.2 | 0.037 | 27.8% |

The fullback/wingback ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Defensive Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Woo-Young Jung | South Korea | Left Defensive Midfield | Ball-Winner | 318 | 70.6 | 1 | 66.7 | 0.231 | 17.3% |
| 2 | Tyler Adams | United States | Center Defensive Midfield | Ball-Winner | 391 | 59.7 | 2 | 58.9 | 0.050 | 14.9% |
| 3 | Aurélien Djani Tchouaméni | France | Right Defensive Midfield | Ball-Winner | 662 | 59.6 | 3 | 58.8 | 0.157 | 14.6% |
| 4 | Carlos Henrique Casimiro | Brazil | Left Defensive Midfield | Ball-Winner | 409 | 56.1 | 4 | 56.3 | 0.099 | 28.8% |
| 5 | Enzo Fernandez | Argentina | Center Defensive Midfield | Ball-Winner | 601 | 55.8 | 5 | 56.1 | 0.159 | 16.4% |
| 6 | Thomas Teye Partey | Ghana | Right Defensive Midfield | Ball-Winner | 301 | 55.8 | 6 | 56.1 | 0.157 | 14.5% |
| 7 | Frenkie de Jong | Netherlands | Left Defensive Midfield | Ball-Winner | 499 | 55.0 | 7 | 55.5 | 0.018 | 18.2% |
| 8 | Wataru Endo | Japan | Right Defensive Midfield | Ball-Winner | 326 | 54.7 | 8 | 55.4 | 0.052 | 22.6% |
| 9 | In-Beom Hwang | South Korea | Left Defensive Midfield | Ball-Winner | 360 | 54.6 | 9 | 55.3 | 0.173 | 34.6% |
| 10 | Grzegorz Krychowiak | Poland | Center Defensive Midfield | Ball-Winner | 348 | 53.7 | 10 | 54.6 | 0.068 | 16.5% |

The defensive midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Central/Wide Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Luka Modrić | Croatia | Right Center Midfield | Ball-Winner | 673 | 69.2 | 1 | 59.9 | 0.181 | 21.7% |
| 2 | Ángel Fabián Di María Hernández | Argentina | Right Midfield | Progressive Winger | 305 | 59.6 | 2 | 53.6 | -0.179 | 62.9% |
| 3 | Piotr Zieliński | Poland | Right Center Midfield | Wide Creator | 344 | 58.7 | 3 | 57.9 | 0.034 | 25.8% |
| 4 | Vinícius José Paixão de Oliveira Júnior | Brazil | Left Midfield | Progressive Winger | 307 | 57.8 | 4 | 45.6 | -0.276 | 62.9% |
| 5 | Mateo Kovačić | Croatia | Left Center Midfield | Ball-Winner | 650 | 52.8 | 5 | 55.5 | 0.081 | 20.7% |
| 6 | Pedro González López | Spain | Left Center Midfield | Ball-Winner | 372 | 51.8 | 6 | 55.0 | 0.083 | 28.3% |
| 7 | Sofiane Boufal | Morocco | Left Midfield | Progressive Winger | 477 | 50.5 | 7 | 60.5 | -0.076 | 43.6% |
| 8 | Bernardo Mota Veiga de Carvalho e Silva | Portugal | Right Center Midfield | Ball-Winner | 382 | 49.8 | 8 | 41.3 | -0.070 | 29.8% |
| 9 | Yunus Dimoara Musah | United States | Right Center Midfield | Ball-Winner | 365 | 48.9 | 9 | 45.0 | -0.058 | 32.8% |
| 10 | Azzedine Ounahi | Morocco | Right Center Midfield | Ball-Winner | 589 | 44.1 | 10 | 35.9 | -0.105 | 22.4% |

The central/wide midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Attacking Midfield/Wing

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Right Wing | Progressive Winger | 734 | 77.1 | 1 | 60.2 | -0.039 | 46.6% |
| 2 | Christian Pulisic | United States | Left Wing | Progressive Winger | 336 | 61.6 | 2 | 47.3 | -0.171 | 51.7% |
| 3 | Bruno Miguel Borges Fernandes | Portugal | Center Attacking Midfield | Wide Creator | 385 | 57.7 | 3 | 47.1 | -0.070 | 38.6% |
| 4 | Hakim Ziyech | Morocco | Right Wing | Wide Creator | 663 | 57.0 | 4 | 47.4 | -0.048 | 32.4% |
| 5 | Raphael Dias Belloli | Brazil | Right Wing | Progressive Winger | 330 | 56.0 | 5 | 50.2 | -0.198 | 56.9% |
| 6 | Ismaïla Sarr | Senegal | Left Wing | Target Forward | 365 | 55.9 | 6 | 63.7 | -0.247 | 65.3% |
| 7 | Ousmane Dembélé | France | Right Wing | Progressive Winger | 448 | 53.0 | 7 | 61.3 | -0.123 | 57.3% |
| 8 | Antoine Griezmann | France | Center Attacking Midfield | Wide Creator | 586 | 49.8 | 8 | 42.5 | -0.128 | 36.5% |
| 9 | João Félix Sequeira | Portugal | Left Wing | Target Forward | 340 | 46.7 | 9 | 64.1 | -0.216 | 47.7% |
| 10 | Cody Mathès Gakpo | Netherlands | Center Attacking Midfield | Wide Creator | 460 | 46.5 | 10 | 27.4 | -0.300 | 57.2% |

The attacking midfield/wing ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Forward

| Rank | Player | Team | Detailed position | Role | Min. | Position impact | Position rank | Role score | OBV/90 | Final third |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kylian Mbappé Lottin | France | Left Center Forward | Progressive Winger | 654 | 74.9 | 1 | 55.1 | -0.157 | 62.8% |
| 2 | Robert Lewandowski | Poland | Center Forward | Target Forward | 390 | 55.7 | 2 | 43.2 | -0.431 | 52.4% |
| 3 | Mehdi Taremi | Iran | Center Forward | Target Forward | 305 | 54.7 | 3 | 60.7 | -0.233 | 44.3% |
| 4 | Breel-Donald Embolo | Switzerland | Center Forward | Target Forward | 330 | 53.4 | 4 | 52.3 | -0.338 | 46.4% |
| 5 | Harry Kane | England | Center Forward | Target Forward | 422 | 52.8 | 5 | 52.1 | -0.345 | 53.8% |
| 6 | Olivier Giroud | France | Center Forward | Target Forward | 433 | 52.7 | 6 | 59.2 | -0.256 | 41.8% |
| 7 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Center Forward | Target Forward | 303 | 47.8 | 7 | 47.5 | -0.408 | 50.5% |
| 8 | Richarlison de Andrade | Brazil | Center Forward | Target Forward | 328 | 47.1 | 8 | 53.3 | -0.369 | 59.7% |
| 9 | Jackson Irvine | Australia | Left Center Forward | Ball-Winner | 374 | 46.2 | 9 | 43.0 | -0.080 | 25.0% |
| 10 | Julián Álvarez | Argentina | Center Forward | Target Forward | 485 | 44.6 | 10 | 49.5 | -0.408 | 58.4% |

The forward ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

# Recommended coaching workflow

1. Select the opponent's team section and identify its observed attack style, transition exposure, and physical matchup deltas.
2. Pull video for the stated highest-volume review pattern; confirm that the possession labels match the intended tactical interpretation.
3. Use the position leaderboard only to identify candidate role profiles, then check the player's own team context and tournament minutes.
4. Re-run the substitution or style scenario with the expected match state and available squad before training it.
5. Record the pre-match hypothesis and post-match outcome so future calibration can separate useful signals from tournament-specific noise.

# Limitations and validity

- The analysis is valid as an exploratory and predictive decision-support artifact over the supplied tournament data. It is not a randomized or causal study.
- The final_v3 delivery now consumes the V4 spatial player evaluation while preserving the schema-checked calibrated classifier and tournament-wide leave-one-match-out audit coverage. Threshold abstention still gates transition risk to zero rather than converting it into a weak positive recommendation.
- Rare transition events create high variance. Aggregate patterns and precision-aware decisions are safer than interpreting individual possessions as certain events.
- Player physicality uses event-derived proxies: ground-duel wins approximate tackle-related success, and recoveries approximate defensive recovery activity.
- Player rankings cover the 142 players who cleared the 300-minute cutoff, not every registered player and not performance outside this competition.
- Recommended actions require video confirmation and domain review. Medical status, fatigue, tactical instructions, score state, and opposition substitutions can materially change the correct decision.

---

Generated reproducibly from the processed possession, player-profile, matchup, audit, and simulation artifacts in this repository.
