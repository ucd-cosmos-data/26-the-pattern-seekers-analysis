# World Cup Team Performance and Position-Specific Player Report

## Executive summary

This report consolidates **32 national teams**, **342 tournament-role player profiles**, **64 matches**, and **11,016 analyzed possessions** into one coaching reference. It combines observed possession outcomes with the regularized empirical hurdle-pipeline scenario audit. The strongest use is opponent preparation, video-review prioritization, and formation of testable tactical hypotheses.

**Important boundary:** observed goals, xG, shots, box entries, and transition exposure describe this tournament sample. Expected net xG, EvA gaps, optimal styles, and substitution gains are model-generated scenarios. They are not causal claims, guarantees, transfer valuations, or replacements for scouting, medical, training, and match-context evidence.

## How to read the metrics

- **xG:** summed shot quality created during the team's possessions.
- **Shot rate:** percentage of possessions containing at least one shot.
- **Box-entry rate:** percentage of possessions entering the penalty area.
- **Transition xG conceded:** opponent xG generated immediately after the team's possessions; lower is better and it is not total defensive xG conceded.
- **Mean EvA gap:** average difference between the best modeled tactic and the observed tactic. It identifies review candidates, not proven coaching errors.
- **Wasted net xG:** cumulative modeled EvA gap across possessions. It scales with possession volume, so compare it alongside the mean gap.
- **Physical matchup deltas:** lineup-minus-opponent aerial, pressing, and recovery proxies. Positive values indicate a modeled lineup edge.
- **Position score (0–100):** a within-position, tournament-only composite of role-relevant percentiles. It cannot compare players across position groups.

## Tournament overview

| Team | Matches | Poss. | Goals | xG | Shot % | Box entry % | Transition xG conceded | Mean EvA gap | Modeled style |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Argentina | 7 | 639 | 14 | 13.48 | 13.9 | 28.5 | 0.00 | 0.0055 | Patient Build-up |
| France | 7 | 616 | 16 | 11.75 | 14.1 | 30.8 | 0.02 | 0.0034 | Patient Build-up |
| Brazil | 5 | 470 | 8 | 10.50 | 18.1 | 37.7 | 0.01 | 0.0046 | Patient Build-up |
| England | 5 | 403 | 13 | 8.74 | 14.6 | 36.2 | 0.00 | 0.0008 | Patient Build-up |
| Germany | 3 | 277 | 6 | 8.23 | 20.6 | 45.1 | 0.00 | 0.0069 | Patient Build-up |
| Portugal | 5 | 456 | 12 | 7.31 | 14.0 | 34.9 | 0.42 | 0.0021 | Patient Build-up |
| Croatia | 7 | 696 | 8 | 6.84 | 9.5 | 31.2 | 0.00 | 0.0029 | Patient Build-up |
| Switzerland | 4 | 339 | 5 | 6.09 | 9.4 | 26.0 | 0.00 | 0.0027 | Patient Build-up |
| Morocco | 7 | 552 | 5 | 5.13 | 9.6 | 21.9 | 0.04 | 0.0035 | Patient Build-up |
| Netherlands | 5 | 427 | 10 | 4.99 | 8.7 | 31.1 | 0.02 | 0.0025 | Patient Build-up |
| Spain | 4 | 372 | 9 | 4.75 | 12.1 | 32.5 | 0.00 | 0.0023 | Patient Build-up |
| Senegal | 4 | 333 | 5 | 4.27 | 13.8 | 30.0 | 0.00 | 0.0041 | Patient Build-up |
| Japan | 4 | 326 | 5 | 4.25 | 10.4 | 28.2 | 0.03 | 0.0083 | Patient Build-up |
| Poland | 4 | 313 | 2 | 4.18 | 8.6 | 23.6 | 0.26 | 0.0021 | Patient Build-up |
| United States | 4 | 333 | 3 | 3.94 | 12.6 | 34.8 | 0.00 | 0.0017 | Patient Build-up |
| Canada | 3 | 272 | 2 | 3.93 | 11.8 | 30.1 | 0.04 | 0.0013 | Patient Build-up |
| Iran | 3 | 234 | 4 | 3.83 | 11.1 | 29.5 | 0.00 | 0.0049 | Patient Build-up |
| Ecuador | 3 | 253 | 4 | 3.81 | 9.9 | 31.6 | 0.00 | 0.0057 | Short Under Pressure |
| Belgium | 3 | 242 | 1 | 3.68 | 12.8 | 33.9 | 0.00 | 0.0044 | Patient Build-up |
| South Korea | 4 | 314 | 5 | 3.58 | 13.4 | 30.6 | 0.00 | 0.0012 | Patient Build-up |
| Ghana | 3 | 260 | 5 | 3.35 | 9.2 | 26.2 | 0.00 | 0.0058 | Patient Build-up |
| Uruguay | 3 | 248 | 2 | 3.27 | 12.9 | 32.3 | 0.00 | 0.0069 | Patient Build-up |
| Saudi Arabia | 3 | 255 | 3 | 3.20 | 9.8 | 30.2 | 0.48 | 0.0037 | Patient Build-up |
| Denmark | 3 | 270 | 1 | 3.19 | 11.1 | 36.7 | 0.00 | 0.0025 | Patient Build-up |
| Serbia | 3 | 264 | 5 | 3.08 | 11.0 | 29.9 | 0.14 | 0.0029 | Patient Build-up |
| Mexico | 3 | 263 | 2 | 3.06 | 13.7 | 34.6 | 0.00 | 0.0018 | Patient Build-up |
| Cameroon | 3 | 247 | 4 | 2.93 | 9.7 | 30.0 | 0.00 | 0.0023 | Patient Build-up |
| Tunisia | 3 | 283 | 1 | 2.41 | 10.2 | 30.4 | 0.00 | 0.0010 | Short Under Pressure |
| Wales | 3 | 259 | 1 | 2.22 | 8.1 | 23.9 | 0.00 | 0.0019 | Patient Build-up |
| Australia | 4 | 311 | 4 | 1.56 | 8.0 | 26.0 | 0.28 | 0.0043 | Patient Build-up |
| Qatar | 3 | 255 | 1 | 1.39 | 7.5 | 20.8 | 0.00 | 0.0038 | Patient Build-up |
| Costa Rica | 3 | 234 | 3 | 1.23 | 3.8 | 14.5 | 0.00 | 0.0048 | Patient Build-up |

The table is sorted by observed xG rather than a synthetic overall rank. That preserves the distinction between attack volume, transition control, and model-estimated tactical opportunity.

# Team-by-team performance

## Argentina (ARG)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 8.87; the possession-level scenario ceiling summed to 11.98, producing 3.10 modeled cumulative net xG of review opportunity and a 0.0055 mean EvA gap.

Average lineup matchup deltas were **-0.043 aerial**, **-2.135 pressing**, and **+0.730 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 80 possessions with 1.05 cumulative modeled gap (0.0131 per possession).

**Best substitution scenario:** Thiago Ezequiel Almada for Julián Álvarez under Patient Build-up produced the largest estimated team gain (+0.0029 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Lautaro Javier Martínez | Forward | Target Forward | 273 | 84.1 | 0.943 |
| 2 | Lionel Andrés Messi Cuccittini | Attacking Midfield/Wing | Progressive Winger | 734 | 80.4 | 1.004 |
| 3 | Leandro Daniel Paredes | Defensive Midfield | Sweeper CB | 235 | 78.2 | 0.716 |
| 4 | Damián Emiliano Martínez | Goalkeeper | Deep Playmaker | 734 | 65.6 | 0.016 |
| 5 | Rodrigo Javier De Paul | Defensive Midfield | Wide Creator | 635 | 64.8 | 0.138 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Australia (AUS)

Across the analyzed possessions, Australia's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 1.49; the possession-level scenario ceiling summed to 2.64, producing 1.15 modeled cumulative net xG of review opportunity and a 0.0043 mean EvA gap.

Average lineup matchup deltas were **+0.083 aerial**, **+3.342 pressing**, and **-0.799 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 37 possessions with 0.33 cumulative modeled gap (0.0089 per possession).

**Best substitution scenario:** Jamie MacLaren for Mitchell Thomas Duke under Patient Build-up produced the largest estimated team gain (+0.0006 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Harry Souttar | Center Back | Holding Anchor | 387 | 57.3 | 0.070 |
| 2 | Mathew Ryan | Goalkeeper | Deep Playmaker | 387 | 55.6 | 0.042 |
| 3 | Aaron Mooy | Defensive Midfield | Box-to-Box Runner | 387 | 44.1 | 0.041 |
| 4 | Jackson Irvine | Forward | Holding Anchor | 374 | 43.9 | 0.104 |
| 5 | Mitchell Thomas Duke | Forward | Target Forward | 272 | 43.3 | 0.069 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Belgium (BEL)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.79; the possession-level scenario ceiling summed to 3.76, producing 0.97 modeled cumulative net xG of review opportunity and a 0.0044 mean EvA gap.

Average lineup matchup deltas were **-0.008 aerial**, **+0.226 pressing**, and **-0.856 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 23 possessions with 0.24 cumulative modeled gap (0.0105 per possession).

**Best substitution scenario:** Dries Mertens for Eden Hazard under Patient Build-up produced the largest estimated team gain (+0.0018 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Thomas Meunier | Fullback/Wingback | Wide Creator | 217 | 53.8 | 0.087 |
| 2 | Kevin De Bruyne | Attacking Midfield/Wing | Progressive Winger | 284 | 51.1 | 0.125 |
| 3 | Jan Vertonghen | Center Back | Sweeper CB | 284 | 47.3 | 0.108 |
| 4 | Thibaut Courtois | Goalkeeper | Deep Playmaker | 284 | 41.6 | 0.064 |
| 5 | Timothy Castagne | Fullback/Wingback | Holding Anchor | 284 | 38.5 | 0.050 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Brazil (BRA)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 7.83; the possession-level scenario ceiling summed to 9.76, producing 1.93 modeled cumulative net xG of review opportunity and a 0.0046 mean EvA gap.

Average lineup matchup deltas were **-0.126 aerial**, **-6.128 pressing**, and **+0.692 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 43 possessions with 0.51 cumulative modeled gap (0.0120 per possession).

**Best substitution scenario:** Weverton Pereira da Silva for Lucas Tolentino Coelho de Lima under Patient Build-up produced the largest estimated team gain (+0.0023 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 330 | 73.9 | 0.294 |
| 2 | Éder Gabriel Militão | Fullback/Wingback | Box-to-Box Runner | 364 | 73.5 | 0.140 |
| 3 | Neymar da Silva Santos Junior | Attacking Midfield/Wing | Progressive Winger | 281 | 69.5 | 0.731 |
| 4 | Alex Sandro Lobo Silva | Fullback/Wingback | Sweeper CB | 200 | 68.2 | 0.101 |
| 5 | Alisson Ramsés Becker | Goalkeeper | Deep Playmaker | 395 | 65.0 | 0.022 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Cameroon (CMR)

Across the analyzed possessions, Cameroon's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.33; the possession-level scenario ceiling summed to 2.84, producing 0.51 modeled cumulative net xG of review opportunity and a 0.0023 mean EvA gap.

Average lineup matchup deltas were **+0.078 aerial**, **+4.206 pressing**, and **-0.111 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 27 possessions with 0.12 cumulative modeled gap (0.0044 per possession).

**Best substitution scenario:** Christopher Wooh for André-Frank Zambo Anguissa under Patient Build-up produced the largest estimated team gain (+0.0019 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Jean-Charles Castelletto | Center Back | Sweeper CB | 192 | 81.6 | 0.478 |
| 2 | Nicolas Alexis Julio N'Koulou Ndoubena | Center Back | Holding Anchor | 192 | 57.1 | 0.216 |
| 3 | Ngoran Suiru Fai Collins | Fullback/Wingback | Wide Creator | 293 | 51.9 | 0.043 |
| 4 | André-Frank Zambo Anguissa | Defensive Midfield | Box-to-Box Runner | 277 | 47.6 | 0.057 |
| 5 | Jean-Eric Maxim Choupo-Moting | Forward | Target Forward | 270 | 44.9 | 0.186 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Canada (CAN)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.71; the possession-level scenario ceiling summed to 3.02, producing 0.31 modeled cumulative net xG of review opportunity and a 0.0013 mean EvA gap.

Average lineup matchup deltas were **-0.027 aerial**, **-1.282 pressing**, and **+0.782 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 31 possessions with 0.07 cumulative modeled gap (0.0021 per possession).

**Best substitution scenario:** David Wallace Wotherspoon for Alphonso Davies under Patient Build-up produced the largest estimated team gain (+0.0028 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Alistair Johnston | Fullback/Wingback | Box-to-Box Runner | 285 | 74.8 | 0.283 |
| 2 | Jonathan David | Forward | Target Forward | 202 | 64.2 | 0.359 |
| 3 | Alphonso Davies | Central/Wide Midfield | Progressive Winger | 285 | 63.6 | 0.307 |
| 4 | Steven de Sousa Vitoria | Center Back | Holding Anchor | 285 | 59.0 | 0.057 |
| 5 | Tajon Buchanan | Central/Wide Midfield | Progressive Winger | 270 | 56.9 | 0.278 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Costa Rica (CRC)

Across the analyzed possessions, Costa Rica's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 1.30; the possession-level scenario ceiling summed to 2.23, producing 0.93 modeled cumulative net xG of review opportunity and a 0.0048 mean EvA gap.

Average lineup matchup deltas were **+0.101 aerial**, **+0.962 pressing**, and **-0.471 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 34 possessions with 0.32 cumulative modeled gap (0.0094 per possession).

**Best substitution scenario:** Daniel Alonso Chacón Salas for Jewison Bennette under Patient Build-up produced the largest estimated team gain (+0.0007 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Francisco Javier Calvo Quesada | Center Back | Box-to-Box Runner | 194 | 59.8 | 0.070 |
| 2 | Keylor Navas Gamboa | Goalkeeper | Deep Playmaker | 294 | 46.9 | 0.009 |
| 3 | Yeltsin Ignacio Tejeda Valverde | Central/Wide Midfield | Holding Anchor | 287 | 46.4 | 0.187 |
| 4 | Óscar Esau Duarte Gaitán | Center Back | Holding Anchor | 294 | 45.7 | 0.015 |
| 5 | Keysher Fuller Spence | Fullback/Wingback | Holding Anchor | 268 | 45.5 | 0.116 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Croatia (CRO)

Across the analyzed possessions, Croatia's total xG was among the tournament leaders, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 6.57; the possession-level scenario ceiling summed to 8.35, producing 1.78 modeled cumulative net xG of review opportunity and a 0.0029 mean EvA gap.

Average lineup matchup deltas were **+0.041 aerial**, **-2.690 pressing**, and **+0.290 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 72 possessions with 0.48 cumulative modeled gap (0.0066 per possession).

**Best substitution scenario:** Nikola Vlašić for Mateo Kovačić under Patient Build-up produced the largest estimated team gain (-0.0000 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Luka Modrić | Central/Wide Midfield | Wide Creator | 673 | 81.4 | 0.241 |
| 2 | Marcelo Brozović | Defensive Midfield | Box-to-Box Runner | 570 | 78.4 | 0.288 |
| 3 | Dominik Livaković | Goalkeeper | Deep Playmaker | 720 | 73.4 | 0.037 |
| 4 | Mateo Kovačić | Central/Wide Midfield | Box-to-Box Runner | 650 | 71.8 | 0.121 |
| 5 | Marko Livaja | Forward | Target Forward | 256 | 67.7 | 0.629 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Denmark (DEN)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.61; the possession-level scenario ceiling summed to 3.23, producing 0.62 modeled cumulative net xG of review opportunity and a 0.0025 mean EvA gap.

Average lineup matchup deltas were **-0.157 aerial**, **-2.172 pressing**, and **-0.546 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 37 possessions with 0.20 cumulative modeled gap (0.0054 per possession).

**Best substitution scenario:** Mathias Jensen for Kasper Dolberg under Patient Build-up produced the largest estimated team gain (+0.0010 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Joachim Andersen | Center Back | Sweeper CB | 291 | 66.7 | 0.135 |
| 2 | Christian Dannemann Eriksen | Central/Wide Midfield | Ball-Winner | 291 | 65.5 | 0.131 |
| 3 | Pierre-Emile Højbjerg | Central/Wide Midfield | Box-to-Box Runner | 291 | 50.9 | 0.079 |
| 4 | Kasper Schmeichel | Goalkeeper | Deep Playmaker | 291 | 48.8 | 0.043 |
| 5 | Andreas Christensen | Center Back | Sweeper CB | 291 | 48.6 | 0.255 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Ecuador (ECU)

Across the analyzed possessions, Ecuador's total xG was near the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Short Under Pressure** most often. Observed expected net xG was 2.63; the possession-level scenario ceiling summed to 3.87, producing 1.24 modeled cumulative net xG of review opportunity and a 0.0057 mean EvA gap.

Average lineup matchup deltas were **-0.004 aerial**, **+1.896 pressing**, and **+0.400 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Patient Build-up were most often improved in the model by Short Under Pressure. This pattern covered 63 possessions with 0.48 cumulative modeled gap (0.0077 per possession).

**Best substitution scenario:** Djorkaeff Neicer Reasco González for Gonzalo Jordy Plata Jiménez under Short Under Pressure produced the largest estimated team gain (+0.0021 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pervis Josué Estupiñán Tenorio | Fullback/Wingback | Wide Creator | 288 | 68.9 | 0.130 |
| 2 | Angelo Smit Preciado Quiñónez | Fullback/Wingback | Wide Creator | 276 | 61.4 | 0.055 |
| 3 | Enner Remberto Valencia Lastra | Attacking Midfield/Wing | Target Forward | 262 | 57.0 | 0.665 |
| 4 | Moisés Isaac Caicedo Corozo | Defensive Midfield | Box-to-Box Runner | 283 | 56.7 | 0.232 |
| 5 | Piero Martín Hincapié Reyna | Center Back | Holding Anchor | 288 | 55.8 | 0.055 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## England (ENG)

Across the analyzed possessions, England's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 5.60; the possession-level scenario ceiling summed to 5.90, producing 0.30 modeled cumulative net xG of review opportunity and a 0.0008 mean EvA gap.

Average lineup matchup deltas were **+0.012 aerial**, **-3.654 pressing**, and **+0.987 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 36 possessions with 0.06 cumulative modeled gap (0.0016 per possession).

**Best substitution scenario:** Trent Alexander-Arnold for Bukayo Saka under Patient Build-up produced the largest estimated team gain (+0.0020 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Harry Kane | Forward | Target Forward | 422 | 68.7 | 0.517 |
| 2 | Jordan Pickford | Goalkeeper | Deep Playmaker | 486 | 64.1 | 0.029 |
| 3 | Harry Maguire | Center Back | Sweeper CB | 454 | 62.3 | 0.207 |
| 4 | Jude Bellingham | Defensive Midfield | Box-to-Box Runner | 442 | 60.2 | 0.216 |
| 5 | Bukayo Saka | Attacking Midfield/Wing | Ball-Winner | 291 | 59.4 | 0.210 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## France (FRA)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 7.69; the possession-level scenario ceiling summed to 9.50, producing 1.81 modeled cumulative net xG of review opportunity and a 0.0034 mean EvA gap.

Average lineup matchup deltas were **+0.105 aerial**, **+1.067 pressing**, and **-0.652 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 60 possessions with 0.37 cumulative modeled gap (0.0061 per possession).

**Best substitution scenario:** Ibrahima Konaté for Antoine Griezmann under Patient Build-up produced the largest estimated team gain (-0.0001 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Olivier Giroud | Forward | Target Forward | 433 | 82.7 | 0.633 |
| 2 | Randal Kolo Muani | Forward | Target Forward | 204 | 79.9 | 0.890 |
| 3 | Kylian Mbappé Lottin | Forward | Progressive Winger | 654 | 75.1 | 0.728 |
| 4 | Theo Bernard François Hernández | Fullback/Wingback | Box-to-Box Runner | 548 | 71.2 | 0.118 |
| 5 | Antoine Griezmann | Attacking Midfield/Wing | Wide Creator | 586 | 66.4 | 0.149 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Germany (GER)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 5.20; the possession-level scenario ceiling summed to 6.89, producing 1.69 modeled cumulative net xG of review opportunity and a 0.0069 mean EvA gap.

Average lineup matchup deltas were **-0.032 aerial**, **+0.154 pressing**, and **-0.075 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 32 possessions with 0.55 cumulative modeled gap (0.0172 per possession).

**Best substitution scenario:** Youssoufa Moukoko for Thomas Müller under Patient Build-up produced the largest estimated team gain (+0.0006 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Joshua Kimmich | Fullback/Wingback | Wide Creator | 294 | 79.2 | 0.202 |
| 2 | Jamal Musiala | Attacking Midfield/Wing | Progressive Winger | 274 | 78.5 | 0.435 |
| 3 | Niklas Süle | Fullback/Wingback | Sweeper CB | 288 | 63.5 | 0.140 |
| 4 | David Raum | Fullback/Wingback | Wide Creator | 250 | 61.3 | 0.060 |
| 5 | İlkay Gündoğan | Attacking Midfield/Wing | Box-to-Box Runner | 190 | 61.0 | 0.620 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Ghana (GHA)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 1.77; the possession-level scenario ceiling summed to 3.09, producing 1.31 modeled cumulative net xG of review opportunity and a 0.0058 mean EvA gap.

Average lineup matchup deltas were **-0.156 aerial**, **+1.137 pressing**, and **+0.026 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 36 possessions with 0.41 cumulative modeled gap (0.0114 per possession).

**Best substitution scenario:** Kamaldeen Sulemana for Jordan Ayew under Patient Build-up produced the largest estimated team gain (+0.0021 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mohammed Kudus | Attacking Midfield/Wing | Progressive Winger | 255 | 59.8 | 0.243 |
| 2 | Thomas Teye Partey | Defensive Midfield | Box-to-Box Runner | 301 | 52.7 | 0.126 |
| 3 | Mohamed Salisu | Center Back | Sweeper CB | 301 | 50.1 | 0.169 |
| 4 | Lawrence Ati-Zigi | Goalkeeper | Deep Playmaker | 301 | 46.3 | 0.016 |
| 5 | Daniel Amartey | Center Back | Sweeper CB | 301 | 46.0 | 0.076 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Iran (IRN)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.03; the possession-level scenario ceiling summed to 2.99, producing 0.96 modeled cumulative net xG of review opportunity and a 0.0049 mean EvA gap.

Average lineup matchup deltas were **+0.058 aerial**, **+1.725 pressing**, and **-1.059 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 31 possessions with 0.28 cumulative modeled gap (0.0091 per possession).

**Best substitution scenario:** Saman Ghoddos for Milad Mohammadi under Patient Build-up produced the largest estimated team gain (+0.0014 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Morteza Pouraliganji | Center Back | Holding Anchor | 305 | 68.5 | 0.125 |
| 2 | Ramin Rezaeian | Fullback/Wingback | Wide Creator | 202 | 62.9 | 0.162 |
| 3 | Mehdi Taremi | Forward | Ball-Winner | 305 | 62.0 | 0.447 |
| 4 | Ehsan Hajsafi | Fullback/Wingback | Wide Creator | 250 | 49.5 | 0.054 |
| 5 | Seyed Majid Hosseini | Center Back | Box-to-Box Runner | 305 | 47.8 | 0.027 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Japan (JPN)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 3.45; the possession-level scenario ceiling summed to 5.75, producing 2.30 modeled cumulative net xG of review opportunity and a 0.0083 mean EvA gap.

Average lineup matchup deltas were **-0.029 aerial**, **+10.178 pressing**, and **-0.086 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 47 possessions with 0.69 cumulative modeled gap (0.0146 per possession).

**Best substitution scenario:** Ao Tanaka for Ritsu Doan under Patient Build-up produced the largest estimated team gain (+0.0003 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Wataru Endo | Defensive Midfield | Box-to-Box Runner | 326 | 64.0 | 0.095 |
| 2 | Hidemasa Morita | Defensive Midfield | Box-to-Box Runner | 298 | 58.8 | 0.101 |
| 3 | Shūichi Gonda | Goalkeeper | Deep Playmaker | 413 | 54.1 | 0.015 |
| 4 | Maya Yoshida | Center Back | Holding Anchor | 413 | 52.2 | 0.223 |
| 5 | Yuto Nagatomo | Fullback/Wingback | Wide Creator | 210 | 50.9 | 0.036 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Mexico (MEX)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.51; the possession-level scenario ceiling summed to 2.95, producing 0.44 modeled cumulative net xG of review opportunity and a 0.0018 mean EvA gap.

Average lineup matchup deltas were **+0.071 aerial**, **+1.266 pressing**, and **-0.714 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 15 possessions with 0.12 cumulative modeled gap (0.0077 per possession).

**Best substitution scenario:** Rogelio Gabriel Funes Mori for Ernesto Alexis Vega Rojas under Patient Build-up produced the largest estimated team gain (+0.0002 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Hirving Rodrigo Lozano Bahena | Attacking Midfield/Wing | Progressive Winger | 267 | 61.3 | 0.123 |
| 2 | Jesús Daniel Gallardo Vasconcelos | Fullback/Wingback | Wide Creator | 292 | 59.1 | 0.036 |
| 3 | Ernesto Alexis Vega Rojas | Attacking Midfield/Wing | Ball-Winner | 194 | 56.5 | 0.327 |
| 4 | Francisco Guillermo Ochoa Magaña | Goalkeeper | Deep Playmaker | 292 | 51.2 | 0.055 |
| 5 | Luis Gerardo Chávez Magallón | Defensive Midfield | Ball-Winner | 292 | 40.9 | 0.109 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Morocco (MAR)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 4.27; the possession-level scenario ceiling summed to 5.93, producing 1.66 modeled cumulative net xG of review opportunity and a 0.0035 mean EvA gap.

Average lineup matchup deltas were **-0.018 aerial**, **+4.404 pressing**, and **-0.129 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 61 possessions with 0.44 cumulative modeled gap (0.0073 per possession).

**Best substitution scenario:** Ilias Chair for Selim Amallah under Patient Build-up produced the largest estimated team gain (+0.0015 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Achraf Hakimi Mouh | Fullback/Wingback | Box-to-Box Runner | 661 | 79.0 | 0.171 |
| 2 | Romain Saïss | Center Back | Holding Anchor | 486 | 71.4 | 0.148 |
| 3 | Yassine Bounou | Goalkeeper | Deep Playmaker | 603 | 68.4 | 0.041 |
| 4 | Achraf Dari | Center Back | Sweeper CB | 200 | 60.2 | 0.265 |
| 5 | Hakim Ziyech | Attacking Midfield/Wing | Ball-Winner | 663 | 58.7 | 0.175 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Netherlands (NED)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 4.09; the possession-level scenario ceiling summed to 5.03, producing 0.94 modeled cumulative net xG of review opportunity and a 0.0025 mean EvA gap.

Average lineup matchup deltas were **+0.024 aerial**, **+0.739 pressing**, and **+0.057 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 41 possessions with 0.23 cumulative modeled gap (0.0056 per possession).

**Best substitution scenario:** Kenneth Taylor for Teun Koopmeiners under Patient Build-up produced the largest estimated team gain (+0.0015 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Andries Noppert | Goalkeeper | Deep Playmaker | 510 | 70.0 | 0.069 |
| 2 | Daley Blind | Fullback/Wingback | Box-to-Box Runner | 452 | 68.9 | 0.151 |
| 3 | Frenkie de Jong | Defensive Midfield | Box-to-Box Runner | 499 | 63.4 | 0.194 |
| 4 | Teun Koopmeiners | Defensive Midfield | Box-to-Box Runner | 242 | 57.6 | 0.360 |
| 5 | Memphis Depay | Forward | Target Forward | 316 | 54.9 | 0.339 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Poland (POL)

Across the analyzed possessions, Poland's total xG was near the tournament median, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.78; the possession-level scenario ceiling summed to 3.37, producing 0.59 modeled cumulative net xG of review opportunity and a 0.0021 mean EvA gap.

Average lineup matchup deltas were **+0.054 aerial**, **+1.148 pressing**, and **-0.413 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 22 possessions with 0.15 cumulative modeled gap (0.0069 per possession).

**Best substitution scenario:** Michał Skóraś for Przemysław Frankowski under Patient Build-up produced the largest estimated team gain (+0.0014 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Robert Lewandowski | Forward | Target Forward | 390 | 77.6 | 0.733 |
| 2 | Piotr Zieliński | Central/Wide Midfield | Box-to-Box Runner | 344 | 62.8 | 0.208 |
| 3 | Wojciech Szczęsny | Goalkeeper | Deep Playmaker | 390 | 56.6 | 0.039 |
| 4 | Jakub Piotr Kiwior | Center Back | Holding Anchor | 377 | 40.1 | 0.079 |
| 5 | Jakub Kamiński | Central/Wide Midfield | Ball-Winner | 254 | 39.6 | 0.095 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Portugal (POR)

Across the analyzed possessions, Portugal's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 4.59; the possession-level scenario ceiling summed to 5.46, producing 0.87 modeled cumulative net xG of review opportunity and a 0.0021 mean EvA gap.

Average lineup matchup deltas were **+0.006 aerial**, **-4.222 pressing**, and **-0.010 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 50 possessions with 0.22 cumulative modeled gap (0.0043 per possession).

**Best substitution scenario:** Nuno Mendes for Bruno Miguel Borges Fernandes under Patient Build-up produced the largest estimated team gain (+0.0014 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 303 | 70.4 | 0.587 |
| 2 | Bruno Miguel Borges Fernandes | Attacking Midfield/Wing | Ball-Winner | 385 | 64.5 | 0.303 |
| 3 | Bernardo Mota Veiga de Carvalho e Silva | Central/Wide Midfield | Box-to-Box Runner | 382 | 62.4 | 0.092 |
| 4 | Kléper Laveran Lima Ferreira | Center Back | Sweeper CB | 389 | 61.3 | 0.142 |
| 5 | Diogo Meireles Costa | Goalkeeper | Deep Playmaker | 489 | 60.0 | 0.037 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Qatar (QAT)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 1.59; the possession-level scenario ceiling summed to 2.48, producing 0.89 modeled cumulative net xG of review opportunity and a 0.0038 mean EvA gap.

Average lineup matchup deltas were **+0.005 aerial**, **+2.608 pressing**, and **-0.286 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 39 possessions with 0.36 cumulative modeled gap (0.0092 per possession).

**Best substitution scenario:** Bassam Hisham Al Rawi for Hassan Khalid Al Heidos under Patient Build-up produced the largest estimated team gain (+0.0011 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pedro Miguel Correia | Center Back | Wide Creator | 274 | 56.1 | 0.022 |
| 2 | Abdelkarim Hassan Al Haj Fadlalla | Center Back | Sweeper CB | 287 | 51.4 | 0.155 |
| 3 | Hassan Khalid Al Heidos | Central/Wide Midfield | Ball-Winner | 209 | 49.6 | 0.038 |
| 4 | Boualem Khoukhi | Center Back | Sweeper CB | 287 | 47.5 | 0.073 |
| 5 | Karim Boudiaf | Defensive Midfield | Holding Anchor | 196 | 35.8 | 0.048 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Saudi Arabia (KSA)

Across the analyzed possessions, Saudi Arabia's total xG was below the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 1.99; the possession-level scenario ceiling summed to 2.76, producing 0.77 modeled cumulative net xG of review opportunity and a 0.0037 mean EvA gap.

Average lineup matchup deltas were **-0.117 aerial**, **-0.540 pressing**, and **+0.714 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 26 possessions with 0.20 cumulative modeled gap (0.0077 per possession).

**Best substitution scenario:** Haitham Mohammed Asiri for Sultan Abdullah Salim Al Ghannam under Patient Build-up produced the largest estimated team gain (+0.0018 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Abdulelah Al Amri | Center Back | Sweeper CB | 211 | 66.9 | 0.083 |
| 2 | Salem Mohammed Al Dawsari | Central/Wide Midfield | Ball-Winner | 299 | 64.1 | 0.511 |
| 3 | Mohammed Kanoo | Central/Wide Midfield | Box-to-Box Runner | 299 | 55.9 | 0.133 |
| 4 | Saud Abdullah Abdul Hamid | Fullback/Wingback | Wide Creator | 299 | 47.0 | 0.043 |
| 5 | Abdulelah Saad Hameed Al-Malki | Defensive Midfield | Box-to-Box Runner | 189 | 46.6 | 0.087 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Senegal (SEN)

Across the analyzed possessions, Senegal's total xG was above the tournament median, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.84; the possession-level scenario ceiling summed to 4.03, producing 1.19 modeled cumulative net xG of review opportunity and a 0.0041 mean EvA gap.

Average lineup matchup deltas were **+0.016 aerial**, **-1.491 pressing**, and **-0.488 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 35 possessions with 0.32 cumulative modeled gap (0.0091 per possession).

**Best substitution scenario:** Fodé Ballo Touré for Krépin Diatta under Patient Build-up produced the largest estimated team gain (+0.0006 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Kalidou Koulibaly | Center Back | Sweeper CB | 387 | 80.2 | 0.112 |
| 2 | Ismaïla Sarr | Attacking Midfield/Wing | Ball-Winner | 365 | 69.4 | 0.481 |
| 3 | Youssouf Sabaly | Fullback/Wingback | Box-to-Box Runner | 387 | 66.9 | 0.080 |
| 4 | Edouard Mendy | Goalkeeper | Deep Playmaker | 387 | 53.4 | 0.030 |
| 5 | Krépin Diatta | Attacking Midfield/Wing | Ball-Winner | 182 | 51.8 | 0.099 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Serbia (SRB)

Across the analyzed possessions, Serbia's total xG was below the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.21; the possession-level scenario ceiling summed to 2.88, producing 0.68 modeled cumulative net xG of review opportunity and a 0.0029 mean EvA gap.

Average lineup matchup deltas were **+0.055 aerial**, **-2.400 pressing**, and **-0.287 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 35 possessions with 0.21 cumulative modeled gap (0.0060 per possession).

**Best substitution scenario:** Srđan Babić for Saša Lukić under Patient Build-up produced the largest estimated team gain (+0.0016 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Strahinja Pavlović | Center Back | Sweeper CB | 253 | 80.0 | 0.127 |
| 2 | Aleksandar Mitrović | Forward | Target Forward | 279 | 58.6 | 0.485 |
| 3 | Filip Kostić | Fullback/Wingback | Wide Creator | 191 | 54.1 | 0.024 |
| 4 | Nikola Milenković | Center Back | Holding Anchor | 294 | 53.0 | 0.088 |
| 5 | Vanja Milinković Savić | Goalkeeper | Deep Playmaker | 294 | 50.0 | 0.047 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## South Korea (KOR)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 3.08; the possession-level scenario ceiling summed to 3.40, producing 0.32 modeled cumulative net xG of review opportunity and a 0.0012 mean EvA gap.

Average lineup matchup deltas were **+0.118 aerial**, **+6.170 pressing**, and **+0.195 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 46 possessions with 0.07 cumulative modeled gap (0.0016 per possession).

**Best substitution scenario:** Yu-Min Cho for Jae-Sung Lee under Patient Build-up produced the largest estimated team gain (+0.0023 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Young-Gwon Kim | Center Back | Sweeper CB | 373 | 63.4 | 0.249 |
| 2 | Min Jae Kim | Center Back | Sweeper CB | 283 | 60.4 | 0.118 |
| 3 | Woo-Young Jung | Defensive Midfield | Holding Anchor | 318 | 60.0 | 0.066 |
| 4 | In-Beom Hwang | Defensive Midfield | Box-to-Box Runner | 360 | 58.5 | 0.101 |
| 5 | Gue-Sung Cho | Forward | Target Forward | 297 | 57.9 | 0.211 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Spain (ESP)

Across the analyzed possessions, Spain's total xG was above the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 3.84; the possession-level scenario ceiling summed to 4.64, producing 0.80 modeled cumulative net xG of review opportunity and a 0.0023 mean EvA gap.

Average lineup matchup deltas were **-0.046 aerial**, **-12.554 pressing**, and **+0.142 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 43 possessions with 0.34 cumulative modeled gap (0.0080 per possession).

**Best substitution scenario:** Jorge Resurrección Merodio for Pablo Martín Páez Gavira under Patient Build-up produced the largest estimated team gain (+0.0011 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pedro González López | Central/Wide Midfield | Box-to-Box Runner | 372 | 73.5 | 0.109 |
| 2 | Álvaro Borja Morata Martín | Forward | Target Forward | 201 | 70.4 | 0.507 |
| 3 | Jordi Alba Ramos | Fullback/Wingback | Wide Creator | 271 | 69.7 | 0.104 |
| 4 | Unai Simón Mendibil | Goalkeeper | Deep Playmaker | 414 | 63.1 | 0.059 |
| 5 | Rodrigo Hernández Cascante | Center Back | Sweeper CB | 414 | 61.2 | 0.199 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Switzerland (SUI)

Across the analyzed possessions, Switzerland's total xG was above the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 4.36; the possession-level scenario ceiling summed to 5.18, producing 0.82 modeled cumulative net xG of review opportunity and a 0.0027 mean EvA gap.

Average lineup matchup deltas were **-0.030 aerial**, **+2.987 pressing**, and **-0.646 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 37 possessions with 0.19 cumulative modeled gap (0.0052 per possession).

**Best substitution scenario:** Haris Seferović for Remo Freuler under Patient Build-up produced the largest estimated team gain (+0.0011 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Breel-Donald Embolo | Forward | Target Forward | 330 | 66.8 | 0.656 |
| 2 | Manuel Obafemi Akanji | Center Back | Sweeper CB | 387 | 61.8 | 0.303 |
| 3 | Silvan Widmer | Fullback/Wingback | Wide Creator | 282 | 55.2 | 0.055 |
| 4 | Remo Freuler | Defensive Midfield | Holding Anchor | 346 | 46.8 | 0.158 |
| 5 | Ruben Vargas | Attacking Midfield/Wing | Ball-Winner | 287 | 45.8 | 0.126 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Tunisia (TUN)

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

### Tactical and matchup read

The scenario evaluator selected **Short Under Pressure** most often. Observed expected net xG was 2.75; the possession-level scenario ceiling summed to 3.00, producing 0.25 modeled cumulative net xG of review opportunity and a 0.0010 mean EvA gap.

Average lineup matchup deltas were **-0.059 aerial**, **-2.788 pressing**, and **+1.194 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Short Under Pressure. This pattern covered 15 possessions with 0.09 cumulative modeled gap (0.0058 per possession).

**Best substitution scenario:** Hannibal Mejbri for Ellyes Joris Skhiri under Short Under Pressure produced the largest estimated team gain (+0.0025 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ellyes Joris Skhiri | Defensive Midfield | Box-to-Box Runner | 297 | 67.2 | 0.084 |
| 2 | Yassine Meriah | Center Back | Holding Anchor | 297 | 54.0 | 0.056 |
| 3 | Ali Abdi | Fullback/Wingback | Wide Creator | 214 | 52.7 | 0.021 |
| 4 | Aïssa Bilal Laïdouni | Defensive Midfield | Box-to-Box Runner | 257 | 50.8 | 0.085 |
| 5 | Montassar Omar Talbi | Center Back | Sweeper CB | 297 | 47.2 | 0.055 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## United States (USA)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 3.60; the possession-level scenario ceiling summed to 4.11, producing 0.51 modeled cumulative net xG of review opportunity and a 0.0017 mean EvA gap.

Average lineup matchup deltas were **-0.068 aerial**, **-0.925 pressing**, and **+0.496 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 36 possessions with 0.13 cumulative modeled gap (0.0037 per possession).

**Best substitution scenario:** Kellyn Kai Perry-Acosta for Tyler Adams under Patient Build-up produced the largest estimated team gain (-0.0001 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Christian Pulisic | Attacking Midfield/Wing | Progressive Winger | 336 | 74.1 | 0.350 |
| 2 | Tyler Adams | Defensive Midfield | Box-to-Box Runner | 391 | 73.0 | 0.068 |
| 3 | Yunus Dimoara Musah | Central/Wide Midfield | Box-to-Box Runner | 365 | 66.8 | 0.101 |
| 4 | Weston McKennie | Central/Wide Midfield | Box-to-Box Runner | 274 | 65.4 | 0.189 |
| 5 | Sergino Dest | Fullback/Wingback | Ball-Winner | 308 | 64.6 | 0.134 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Uruguay (URU)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 2.82; the possession-level scenario ceiling summed to 4.30, producing 1.48 modeled cumulative net xG of review opportunity and a 0.0069 mean EvA gap.

Average lineup matchup deltas were **+0.090 aerial**, **-0.252 pressing**, and **-0.035 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 38 possessions with 0.54 cumulative modeled gap (0.0142 per possession).

**Best substitution scenario:** Edinson Roberto Cavani Gómez for Facundo Pellistri Rebollo under Patient Build-up produced the largest estimated team gain (+0.0000 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Bentancur Colmán | Defensive Midfield | Box-to-Box Runner | 232 | 76.0 | 0.303 |
| 2 | Mathías Olivera Miramontes | Fullback/Wingback | Wide Creator | 264 | 64.6 | 0.072 |
| 3 | José María Giménez de Vargas | Center Back | Holding Anchor | 298 | 64.3 | 0.104 |
| 4 | Sebastián Coates Nión | Center Back | Sweeper CB | 200 | 58.0 | 0.096 |
| 5 | Federico Santiago Valverde Dipetta | Defensive Midfield | Box-to-Box Runner | 298 | 55.7 | 0.113 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Wales (WAL)

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

### Tactical and matchup read

The scenario evaluator selected **Patient Build-up** most often. Observed expected net xG was 1.09; the possession-level scenario ceiling summed to 1.53, producing 0.44 modeled cumulative net xG of review opportunity and a 0.0019 mean EvA gap.

Average lineup matchup deltas were **-0.031 aerial**, **+1.564 pressing**, and **-0.189 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 31 possessions with 0.12 cumulative modeled gap (0.0040 per possession).

**Best substitution scenario:** Daniel James for Harry Wilson under Patient Build-up produced the largest estimated team gain (-0.0000 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ben Davies | Center Back | Box-to-Box Runner | 261 | 74.9 | 0.176 |
| 2 | Chris Mepham | Center Back | Sweeper CB | 297 | 59.0 | 0.070 |
| 3 | Neco Williams | Fullback/Wingback | Box-to-Box Runner | 216 | 58.5 | 0.056 |
| 4 | Kieffer Roberto Francisco Moore | Forward | Target Forward | 252 | 55.8 | 0.240 |
| 5 | Wayne Hennessey | Goalkeeper | Deep Playmaker | 203 | 45.3 | 0.048 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

# Top tournament-role players by position

These leaderboards rank only the analyzed tournament cohort and use different weights for different roles. A score of 80 means a strong blend of the selected within-position indicators; it does not mean an 80% chance of success. Sample size, team tactics, opponent quality, and role assignment all affect the component metrics.

## Position-score construction

- **Goalkeeper:** minutes 40%, pass completion 30%, pass progression per pass 20%, speed recovery index 10%.
- **Center Back:** aerial dominance index 25%, pressing intensity index 15%, speed recovery index 20%, net xg contribution p90 15%, pass progression per pass 15%, minutes 10%.
- **Fullback/Wingback:** aerial dominance index 10%, pressing intensity index 20%, speed recovery index 20%, net xg contribution p90 20%, progressive passes p90 15%, key passes p90 5%, minutes 10%.
- **Defensive Midfield:** aerial dominance index 10%, pressing intensity index 20%, speed recovery index 20%, net xg contribution p90 20%, progressive passes p90 15%, pass completion 5%, minutes 10%.
- **Central/Wide Midfield:** pressing intensity index 20%, speed recovery index 15%, net xg contribution p90 25%, progressive passes p90 20%, key passes p90 10%, minutes 10%.
- **Attacking Midfield/Wing:** pressing intensity index 15%, speed recovery index 10%, net xg contribution p90 30%, progressive carries p90 15%, key passes p90 15%, xg p90 5%, minutes 10%.
- **Forward:** aerial dominance index 15%, pressing intensity index 10%, net xg contribution p90 30%, shots p90 15%, xg p90 20%, minutes 10%.

**Goalkeeper warning:** the source features do not provide a complete post-shot shot-stopping evaluation. The goalkeeper list therefore reflects minutes, distribution, progression, and a recovery proxy—not overall goalkeeping quality. Do not use it to make goalkeeper selection decisions without save-quality, cross-claim, sweeping, and error data.

## Goalkeeper

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Dominik Livaković | Croatia | Goalkeeper | Deep Playmaker | 720 | 73.4 | 0.037 | 0.00 | 0.25 | 4.12 |
| 2 | Andries Noppert | Netherlands | Goalkeeper | Deep Playmaker | 510 | 70.0 | 0.069 | 0.00 | 0.00 | 4.59 |
| 3 | Yassine Bounou | Morocco | Goalkeeper | Deep Playmaker | 603 | 68.4 | 0.041 | 0.00 | 0.15 | 3.73 |
| 4 | Damián Emiliano Martínez | Argentina | Goalkeeper | Deep Playmaker | 734 | 65.6 | 0.016 | 0.00 | 0.00 | 3.68 |
| 5 | Alisson Ramsés Becker | Brazil | Goalkeeper | Deep Playmaker | 395 | 65.0 | 0.022 | 0.00 | 0.00 | 5.01 |
| 6 | Jordan Pickford | England | Goalkeeper | Deep Playmaker | 486 | 64.1 | 0.029 | 0.00 | 0.00 | 2.96 |
| 7 | Unai Simón Mendibil | Spain | Goalkeeper | Deep Playmaker | 414 | 63.1 | 0.059 | 0.00 | 0.00 | 2.61 |
| 8 | Hugo Lloris | France | Goalkeeper | Deep Playmaker | 614 | 61.3 | 0.028 | 0.00 | 0.00 | 2.34 |
| 9 | Matthew Charles Turner | United States | Goalkeeper | Deep Playmaker | 391 | 60.9 | 0.039 | 0.00 | 0.00 | 3.91 |
| 10 | Diogo Meireles Costa | Portugal | Goalkeeper | Deep Playmaker | 489 | 60.0 | 0.037 | 0.00 | 0.18 | 2.76 |

The goalkeeper ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Center Back

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Jean-Charles Castelletto | Cameroon | Right Center Back | Sweeper CB | 192 | 81.6 | 0.478 | 1.00 | 12.16 | 3.74 |
| 2 | Kalidou Koulibaly | Senegal | Right Center Back | Sweeper CB | 387 | 80.2 | 0.112 | 0.80 | 9.30 | 4.65 |
| 3 | Strahinja Pavlović | Serbia | Left Center Back | Sweeper CB | 253 | 80.0 | 0.127 | 1.00 | 12.46 | 5.34 |
| 4 | Ben Davies | Wales | Left Center Back | Box-to-Box Runner | 261 | 74.9 | 0.176 | 0.73 | 9.30 | 6.20 |
| 5 | Romain Saïss | Morocco | Left Center Back | Holding Anchor | 486 | 71.4 | 0.148 | 0.80 | 7.60 | 2.22 |
| 6 | Morteza Pouraliganji | Iran | Right Center Back | Holding Anchor | 305 | 68.5 | 0.125 | 0.75 | 10.62 | 2.36 |
| 7 | Abdulelah Al Amri | Saudi Arabia | Right Center Back | Sweeper CB | 211 | 66.9 | 0.083 | 0.71 | 8.54 | 5.98 |
| 8 | Joachim Andersen | Denmark | Right Center Back | Sweeper CB | 291 | 66.7 | 0.135 | 0.67 | 8.98 | 4.02 |
| 9 | Ibrahima Konaté | France | Left Center Back | Sweeper CB | 331 | 65.1 | 0.133 | 0.90 | 6.80 | 3.54 |
| 10 | José María Giménez de Vargas | Uruguay | Right Center Back | Holding Anchor | 298 | 64.3 | 0.104 | 0.85 | 9.36 | 1.81 |

The center back ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Fullback/Wingback

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Joshua Kimmich | Germany | Right Back | Wide Creator | 294 | 79.2 | 0.202 | 0.71 | 12.86 | 4.90 |
| 2 | Achraf Hakimi Mouh | Morocco | Right Back | Box-to-Box Runner | 661 | 79.0 | 0.171 | 0.57 | 16.21 | 4.90 |
| 3 | Alistair Johnston | Canada | Right Back | Box-to-Box Runner | 285 | 74.8 | 0.283 | 0.73 | 12.63 | 4.42 |
| 4 | Éder Gabriel Militão | Brazil | Right Back | Box-to-Box Runner | 364 | 73.5 | 0.140 | 0.40 | 13.86 | 4.95 |
| 5 | Theo Bernard François Hernández | France | Left Back | Box-to-Box Runner | 548 | 71.2 | 0.118 | 0.60 | 12.63 | 3.94 |
| 6 | Jordi Alba Ramos | Spain | Left Back | Wide Creator | 271 | 69.7 | 0.104 | 0.25 | 13.63 | 4.99 |
| 7 | Daley Blind | Netherlands | Left Wing Back | Box-to-Box Runner | 452 | 68.9 | 0.151 | 0.43 | 17.70 | 2.59 |
| 8 | Pervis Josué Estupiñán Tenorio | Ecuador | Left Back | Wide Creator | 288 | 68.9 | 0.130 | 0.57 | 12.80 | 5.31 |
| 9 | Alex Sandro Lobo Silva | Brazil | Left Back | Sweeper CB | 200 | 68.2 | 0.101 | 0.83 | 11.73 | 5.41 |
| 10 | Youssouf Sabaly | Senegal | Right Back | Box-to-Box Runner | 387 | 66.9 | 0.080 | 0.43 | 11.85 | 6.04 |

The fullback/wingback ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Defensive Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Marcelo Brozović | Croatia | Center Defensive Midfield | Box-to-Box Runner | 570 | 78.4 | 0.288 | 0.62 | 16.74 | 5.05 |
| 2 | Leandro Daniel Paredes | Argentina | Right Defensive Midfield | Sweeper CB | 235 | 78.2 | 0.716 | 1.00 | 20.27 | 3.82 |
| 3 | Rodrigo Bentancur Colmán | Uruguay | Left Defensive Midfield | Box-to-Box Runner | 232 | 76.0 | 0.303 | 0.73 | 19.42 | 6.60 |
| 4 | Tyler Adams | United States | Center Defensive Midfield | Box-to-Box Runner | 391 | 73.0 | 0.068 | 0.60 | 20.48 | 6.21 |
| 5 | Ellyes Joris Skhiri | Tunisia | Right Defensive Midfield | Box-to-Box Runner | 297 | 67.2 | 0.084 | 0.67 | 19.42 | 6.37 |
| 6 | Aurélien Djani Tchouaméni | France | Right Defensive Midfield | Box-to-Box Runner | 662 | 65.4 | 0.227 | 0.75 | 10.74 | 4.89 |
| 7 | Rodrigo Javier De Paul | Argentina | Right Defensive Midfield | Wide Creator | 635 | 64.8 | 0.138 | 0.33 | 18.01 | 4.82 |
| 8 | Wataru Endo | Japan | Right Defensive Midfield | Box-to-Box Runner | 326 | 64.0 | 0.095 | 0.53 | 20.43 | 6.35 |
| 9 | Frenkie de Jong | Netherlands | Left Defensive Midfield | Box-to-Box Runner | 499 | 63.4 | 0.194 | 0.86 | 14.96 | 3.60 |
| 10 | Enzo Fernandez | Argentina | Center Defensive Midfield | Box-to-Box Runner | 601 | 62.8 | 0.222 | 0.42 | 17.52 | 3.74 |

The defensive midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Central/Wide Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Luka Modrić | Croatia | Right Center Midfield | Wide Creator | 673 | 81.4 | 0.241 | 0.50 | 17.93 | 4.95 |
| 2 | Pedro González López | Spain | Left Center Midfield | Box-to-Box Runner | 372 | 73.5 | 0.109 | 0.60 | 14.74 | 6.28 |
| 3 | Mateo Kovačić | Croatia | Left Center Midfield | Box-to-Box Runner | 650 | 71.8 | 0.121 | 0.75 | 21.19 | 3.88 |
| 4 | Yunus Dimoara Musah | United States | Right Center Midfield | Box-to-Box Runner | 365 | 66.8 | 0.101 | 0.25 | 19.24 | 4.44 |
| 5 | Christian Dannemann Eriksen | Denmark | Left Center Midfield | Ball-Winner | 291 | 65.5 | 0.131 | 0.25 | 10.83 | 4.95 |
| 6 | Weston McKennie | United States | Right Midfield | Box-to-Box Runner | 274 | 65.4 | 0.189 | 0.62 | 13.49 | 4.94 |
| 7 | Rodrygo Silva de Goes | Brazil | Left Midfield | Progressive Winger | 199 | 64.5 | 0.616 | 0.60 | 18.51 | 4.06 |
| 8 | Salem Mohammed Al Dawsari | Saudi Arabia | Left Midfield | Ball-Winner | 299 | 64.1 | 0.511 | 0.50 | 12.96 | 4.52 |
| 9 | Alphonso Davies | Canada | Left Midfield | Progressive Winger | 285 | 63.6 | 0.307 | 0.56 | 16.74 | 5.68 |
| 10 | Piotr Zieliński | Poland | Right Center Midfield | Box-to-Box Runner | 344 | 62.8 | 0.208 | 0.50 | 13.33 | 3.92 |

The central/wide midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Attacking Midfield/Wing

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Right Wing | Progressive Winger | 734 | 80.4 | 1.004 | 0.33 | 10.91 | 3.68 |
| 2 | Jamal Musiala | Germany | Center Attacking Midfield | Progressive Winger | 274 | 78.5 | 0.435 | 0.20 | 14.12 | 5.91 |
| 3 | Christian Pulisic | United States | Left Wing | Progressive Winger | 336 | 74.1 | 0.350 | 0.40 | 11.77 | 4.55 |
| 4 | Raphael Dias Belloli | Brazil | Right Wing | Progressive Winger | 330 | 73.9 | 0.294 | 0.00 | 15.52 | 4.36 |
| 5 | Neymar da Silva Santos Junior | Brazil | Center Attacking Midfield | Progressive Winger | 281 | 69.5 | 0.731 | 0.20 | 7.67 | 4.16 |
| 6 | Ismaïla Sarr | Senegal | Left Wing | Ball-Winner | 365 | 69.4 | 0.481 | 0.50 | 13.31 | 3.94 |
| 7 | Antoine Griezmann | France | Center Attacking Midfield | Wide Creator | 586 | 66.4 | 0.149 | 0.64 | 20.89 | 3.84 |
| 8 | Bruno Miguel Borges Fernandes | Portugal | Center Attacking Midfield | Ball-Winner | 385 | 64.5 | 0.303 | 0.21 | 15.20 | 3.27 |
| 9 | Ousmane Dembélé | France | Right Wing | Progressive Winger | 448 | 62.2 | 0.119 | 0.50 | 18.88 | 4.22 |
| 10 | Mislav Oršić | Croatia | Left Wing | Ball-Winner | 187 | 62.2 | 0.550 | 0.00 | 14.89 | 1.92 |

The attacking midfield/wing ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Forward

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lautaro Javier Martínez | Argentina | Left Center Forward | Target Forward | 273 | 84.1 | 0.943 | 0.55 | 6.92 | 1.65 |
| 2 | Olivier Giroud | France | Center Forward | Target Forward | 433 | 82.7 | 0.633 | 0.56 | 12.69 | 0.62 |
| 3 | Randal Kolo Muani | France | Center Forward | Target Forward | 204 | 79.9 | 0.890 | 0.53 | 22.93 | 2.20 |
| 4 | Robert Lewandowski | Poland | Center Forward | Target Forward | 390 | 77.6 | 0.733 | 0.45 | 9.70 | 2.77 |
| 5 | Kylian Mbappé Lottin | France | Left Center Forward | Progressive Winger | 654 | 75.1 | 0.728 | 0.25 | 5.23 | 3.99 |
| 6 | Álvaro Borja Morata Martín | Spain | Center Forward | Target Forward | 201 | 70.4 | 0.507 | 0.67 | 11.65 | 0.90 |
| 7 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Center Forward | Target Forward | 303 | 70.4 | 0.587 | 0.50 | 6.24 | 1.49 |
| 8 | Harry Kane | England | Center Forward | Target Forward | 422 | 68.7 | 0.517 | 0.48 | 6.62 | 2.56 |
| 9 | Marko Livaja | Croatia | Center Forward | Target Forward | 256 | 67.7 | 0.629 | 0.31 | 17.26 | 2.47 |
| 10 | Breel-Donald Embolo | Switzerland | Center Forward | Target Forward | 330 | 66.8 | 0.656 | 0.22 | 13.08 | 1.09 |

The forward ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

# Recommended coaching workflow

1. Select the opponent's team section and identify its observed attack style, transition exposure, and physical matchup deltas.
2. Pull video for the stated highest-volume review pattern; confirm that the possession labels match the intended tactical interpretation.
3. Use the position leaderboard only to identify candidate role profiles, then check the player's own team context and tournament minutes.
4. Re-run the substitution or style scenario with the expected match state and available squad before training it.
5. Record the pre-match hypothesis and post-match outcome so future calibration can separate useful signals from tournament-specific noise.

# Limitations and validity

- The analysis is valid as an exploratory and predictive decision-support artifact over the supplied tournament data. It is not a randomized or causal study.
- The underlying serialized coaching benchmark was unavailable, so the downstream scenario pipeline used the documented regularized empirical hurdle fallback. Results should be revalidated when a healthy calibrated model bundle is available.
- Rare transition events create high variance. Aggregate patterns and precision-aware decisions are safer than interpreting individual possessions as certain events.
- Player physicality uses event-derived proxies: ground-duel wins approximate tackle-related success, and recoveries approximate defensive recovery activity.
- Player rankings cover the 342-player tournament-minute cohort used by the pipeline, not every registered player and not performance outside this competition.
- Recommended actions require video confirmation and domain review. Medical status, fatigue, tactical instructions, score state, and opposition substitutions can materially change the correct decision.

---

Generated reproducibly from the processed possession, player-profile, matchup, audit, and simulation artifacts in this repository.
