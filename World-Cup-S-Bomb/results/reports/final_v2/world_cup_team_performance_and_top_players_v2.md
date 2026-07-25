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
| Argentina | 7 | 639 | 14 | 13.48 | 13.9 | 28.5 | 0.00 | 0.0076 | No meaningful change |
| France | 7 | 616 | 16 | 11.75 | 14.1 | 30.8 | 0.02 | 0.0022 | No meaningful change |
| Brazil | 5 | 470 | 8 | 10.50 | 18.1 | 37.7 | 0.01 | 0.0044 | No meaningful change |
| England | 5 | 403 | 13 | 8.74 | 14.6 | 36.2 | 0.00 | 0.0007 | No meaningful change |
| Germany | 3 | 277 | 6 | 8.23 | 20.6 | 45.1 | 0.00 | nan | Not available |
| Portugal | 5 | 456 | 12 | 7.31 | 14.0 | 34.9 | 0.42 | nan | Not available |
| Croatia | 7 | 696 | 8 | 6.84 | 9.5 | 31.2 | 0.00 | 0.0003 | No meaningful change |
| Switzerland | 4 | 339 | 5 | 6.09 | 9.4 | 26.0 | 0.00 | nan | Not available |
| Morocco | 7 | 552 | 5 | 5.13 | 9.6 | 21.9 | 0.04 | 0.0028 | No meaningful change |
| Netherlands | 5 | 427 | 10 | 4.99 | 8.7 | 31.1 | 0.02 | 0.0038 | No meaningful change |
| Spain | 4 | 372 | 9 | 4.75 | 12.1 | 32.5 | 0.00 | nan | Not available |
| Senegal | 4 | 333 | 5 | 4.27 | 13.8 | 30.0 | 0.00 | 0.0028 | No meaningful change |
| Japan | 4 | 326 | 5 | 4.25 | 10.4 | 28.2 | 0.03 | nan | Not available |
| Poland | 4 | 313 | 2 | 4.18 | 8.6 | 23.6 | 0.26 | nan | Not available |
| United States | 4 | 333 | 3 | 3.94 | 12.6 | 34.8 | 0.00 | nan | Not available |
| Canada | 3 | 272 | 2 | 3.93 | 11.8 | 30.1 | 0.04 | nan | Not available |
| Iran | 3 | 234 | 4 | 3.83 | 11.1 | 29.5 | 0.00 | nan | Not available |
| Ecuador | 3 | 253 | 4 | 3.81 | 9.9 | 31.6 | 0.00 | nan | Not available |
| Belgium | 3 | 242 | 1 | 3.68 | 12.8 | 33.9 | 0.00 | 0.0025 | No meaningful change |
| South Korea | 4 | 314 | 5 | 3.58 | 13.4 | 30.6 | 0.00 | nan | Not available |
| Ghana | 3 | 260 | 5 | 3.35 | 9.2 | 26.2 | 0.00 | nan | Not available |
| Uruguay | 3 | 248 | 2 | 3.27 | 12.9 | 32.3 | 0.00 | nan | Not available |
| Saudi Arabia | 3 | 255 | 3 | 3.20 | 9.8 | 30.2 | 0.48 | nan | Not available |
| Denmark | 3 | 270 | 1 | 3.19 | 11.1 | 36.7 | 0.00 | 0.0008 | No meaningful change |
| Serbia | 3 | 264 | 5 | 3.08 | 11.0 | 29.9 | 0.14 | 0.0026 | No meaningful change |
| Mexico | 3 | 263 | 2 | 3.06 | 13.7 | 34.6 | 0.00 | nan | Not available |
| Cameroon | 3 | 247 | 4 | 2.93 | 9.7 | 30.0 | 0.00 | 0.0000 | No meaningful change |
| Tunisia | 3 | 283 | 1 | 2.41 | 10.2 | 30.4 | 0.00 | 0.0006 | No meaningful change |
| Wales | 3 | 259 | 1 | 2.22 | 8.1 | 23.9 | 0.00 | nan | Not available |
| Australia | 4 | 311 | 4 | 1.56 | 8.0 | 26.0 | 0.28 | 0.0022 | No meaningful change |
| Qatar | 3 | 255 | 1 | 1.39 | 7.5 | 20.8 | 0.00 | nan | Not available |
| Costa Rica | 3 | 234 | 3 | 1.23 | 3.8 | 14.5 | 0.00 | nan | Not available |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 2.70; the possession-level scenario ceiling summed to 3.99, producing 1.29 modeled cumulative net xG of review opportunity and a 0.0076 mean EvA gap.

Average lineup matchup deltas were **-0.043 aerial**, **-2.135 pressing**, and **+0.730 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 27 possessions with 0.46 cumulative modeled gap (0.0169 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Lautaro Javier Martínez | Forward | Target Forward | 273 | 83.4 | 0.823 |
| 2 | Lionel Andrés Messi Cuccittini | Attacking Midfield/Wing | Progressive Winger | 734 | 80.6 | 1.004 |
| 3 | Leandro Daniel Paredes | Defensive Midfield | Ball-Winner | 235 | 77.7 | 0.488 |
| 4 | Rodrigo Javier De Paul | Defensive Midfield | Holding Anchor | 635 | 66.0 | 0.138 |
| 5 | Damián Emiliano Martínez | Goalkeeper | Goalkeeper | 734 | 65.2 | 0.016 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Australia (AUS)

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

### Tactical and matchup read

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 0.45; the possession-level scenario ceiling summed to 0.58, producing 0.14 modeled cumulative net xG of review opportunity and a 0.0022 mean EvA gap.

Average lineup matchup deltas were **+0.083 aerial**, **+3.342 pressing**, and **-0.799 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 8 possessions with 0.04 cumulative modeled gap (0.0054 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Harry Souttar | Center Back | Deep Playmaker | 387 | 56.7 | 0.070 |
| 2 | Mathew Ryan | Goalkeeper | Goalkeeper | 387 | 52.9 | 0.042 |
| 3 | Aaron Mooy | Defensive Midfield | Ball-Winner | 387 | 43.7 | 0.041 |
| 4 | Mitchell Thomas Duke | Forward | Target Forward | 272 | 43.3 | 0.247 |
| 5 | Jackson Irvine | Forward | Ball-Winner | 374 | 40.8 | 0.104 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Belgium (BEL)

Across the analyzed possessions, Belgium's total xG was near the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates a moderate modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 1.75; the possession-level scenario ceiling summed to 2.13, producing 0.37 modeled cumulative net xG of review opportunity and a 0.0025 mean EvA gap.

Average lineup matchup deltas were **-0.008 aerial**, **+0.226 pressing**, and **-0.856 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 16 possessions with 0.10 cumulative modeled gap (0.0062 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Thomas Meunier | Fullback/Wingback | Holding Anchor | 217 | 52.8 | 0.053 |
| 2 | Kevin De Bruyne | Attacking Midfield/Wing | Progressive Winger | 284 | 51.6 | 0.221 |
| 3 | Jan Vertonghen | Center Back | Sweeper CB | 284 | 47.4 | 0.101 |
| 4 | Thibaut Courtois | Goalkeeper | Goalkeeper | 284 | 46.5 | 0.007 |
| 5 | Timothy Castagne | Fullback/Wingback | Sweeper CB | 284 | 38.4 | 0.029 |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 1.57; the possession-level scenario ceiling summed to 1.92, producing 0.35 modeled cumulative net xG of review opportunity and a 0.0044 mean EvA gap.

Average lineup matchup deltas were **-0.126 aerial**, **-6.128 pressing**, and **+0.692 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 9 possessions with 0.12 cumulative modeled gap (0.0130 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Éder Gabriel Militão | Fullback/Wingback | Ball-Winner | 364 | 75.2 | 0.140 |
| 2 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 330 | 74.4 | 0.294 |
| 3 | Neymar da Silva Santos Junior | Attacking Midfield/Wing | Progressive Winger | 281 | 69.5 | 0.628 |
| 4 | Alex Sandro Lobo Silva | Fullback/Wingback | Wide Creator | 200 | 67.1 | 0.061 |
| 5 | Rodrygo Silva de Goes | Central/Wide Midfield | Progressive Winger | 199 | 64.7 | 0.399 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Cameroon (CMR)

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

### Tactical and matchup read

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 1.44; the possession-level scenario ceiling summed to 1.44, producing 0.00 modeled cumulative net xG of review opportunity and a 0.0000 mean EvA gap.

Average lineup matchup deltas were **+0.078 aerial**, **+4.206 pressing**, and **-0.111 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Patient Build-up were most often improved in the model by No meaningful change. This pattern covered 41 possessions with 0.00 cumulative modeled gap (0.0000 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Jean-Charles Castelletto | Center Back | Deep Playmaker | 192 | 80.7 | 0.304 |
| 2 | Nicolas Alexis Julio N'Koulou Ndoubena | Center Back | Deep Playmaker | 192 | 56.0 | 0.162 |
| 3 | Ngoran Suiru Fai Collins | Fullback/Wingback | Holding Anchor | 293 | 50.9 | 0.024 |
| 4 | André-Frank Zambo Anguissa | Defensive Midfield | Ball-Winner | 277 | 47.9 | 0.082 |
| 5 | Jean-Eric Maxim Choupo-Moting | Forward | Target Forward | 270 | 44.3 | 0.325 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.027 aerial**, **-1.282 pressing**, and **+0.782 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Alistair Johnston | Fullback/Wingback | Holding Anchor | 285 | 74.2 | 0.186 |
| 2 | Jonathan David | Forward | Target Forward | 202 | 64.0 | 0.439 |
| 3 | Alphonso Davies | Central/Wide Midfield | Progressive Winger | 285 | 63.1 | 0.248 |
| 4 | Steven de Sousa Vitoria | Center Back | Sweeper CB | 285 | 59.0 | 0.067 |
| 5 | Tajon Buchanan | Central/Wide Midfield | Progressive Winger | 270 | 56.6 | 0.227 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Costa Rica (CRC)

Across the analyzed possessions, Costa Rica's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.101 aerial**, **+0.962 pressing**, and **-0.471 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Francisco Javier Calvo Quesada | Center Back | Deep Playmaker | 194 | 59.6 | 0.083 |
| 2 | Yeltsin Ignacio Tejeda Valverde | Central/Wide Midfield | Ball-Winner | 287 | 47.1 | 0.167 |
| 3 | Keysher Fuller Spence | Fullback/Wingback | Holding Anchor | 268 | 46.1 | 0.073 |
| 4 | Óscar Esau Duarte Gaitán | Center Back | Deep Playmaker | 294 | 45.5 | 0.037 |
| 5 | Keylor Navas Gamboa | Goalkeeper | Goalkeeper | 294 | 37.7 | -0.030 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Croatia (CRO)

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

### Tactical and matchup read

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 1.04; the possession-level scenario ceiling summed to 1.07, producing 0.03 modeled cumulative net xG of review opportunity and a 0.0003 mean EvA gap.

Average lineup matchup deltas were **+0.041 aerial**, **-2.690 pressing**, and **+0.290 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 1 possessions with 0.01 cumulative modeled gap (0.0068 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Luka Modrić | Central/Wide Midfield | Ball-Winner | 673 | 82.4 | 0.241 |
| 2 | Marcelo Brozović | Defensive Midfield | Ball-Winner | 570 | 79.3 | 0.288 |
| 3 | Mateo Kovačić | Central/Wide Midfield | Ball-Winner | 650 | 72.6 | 0.121 |
| 4 | Dominik Livaković | Goalkeeper | Goalkeeper | 720 | 72.2 | 0.037 |
| 5 | Marko Livaja | Forward | Target Forward | 256 | 67.3 | 0.610 |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 0.80; the possession-level scenario ceiling summed to 0.87, producing 0.07 modeled cumulative net xG of review opportunity and a 0.0008 mean EvA gap.

Average lineup matchup deltas were **-0.157 aerial**, **-2.172 pressing**, and **-0.546 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Direct Long Play were most often improved in the model by Short Under Pressure. This pattern covered 7 possessions with 0.05 cumulative modeled gap (0.0071 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Joachim Andersen | Center Back | Deep Playmaker | 291 | 66.4 | 0.119 |
| 2 | Christian Dannemann Eriksen | Central/Wide Midfield | Progressive Winger | 291 | 65.6 | 0.129 |
| 3 | Pierre-Emile Højbjerg | Central/Wide Midfield | Ball-Winner | 291 | 51.8 | 0.094 |
| 4 | Kasper Schmeichel | Goalkeeper | Goalkeeper | 291 | 50.7 | -0.007 |
| 5 | Andreas Christensen | Center Back | Sweeper CB | 291 | 48.5 | 0.202 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Ecuador (ECU)

Across the analyzed possessions, Ecuador's total xG was near the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.004 aerial**, **+1.896 pressing**, and **+0.400 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pervis Josué Estupiñán Tenorio | Fullback/Wingback | Wide Creator | 288 | 67.9 | 0.083 |
| 2 | Angelo Smit Preciado Quiñónez | Fullback/Wingback | Holding Anchor | 276 | 59.9 | 0.032 |
| 3 | Enner Remberto Valencia Lastra | Attacking Midfield/Wing | Target Forward | 262 | 57.7 | 0.574 |
| 4 | Moisés Isaac Caicedo Corozo | Defensive Midfield | Ball-Winner | 283 | 56.7 | 0.199 |
| 5 | Piero Martín Hincapié Reyna | Center Back | Deep Playmaker | 288 | 56.1 | 0.065 |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 3.10; the possession-level scenario ceiling summed to 3.21, producing 0.11 modeled cumulative net xG of review opportunity and a 0.0007 mean EvA gap.

Average lineup matchup deltas were **+0.012 aerial**, **-3.654 pressing**, and **+0.987 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Direct Long Play were most often improved in the model by Short Under Pressure. This pattern covered 4 possessions with 0.05 cumulative modeled gap (0.0133 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Harry Kane | Forward | Target Forward | 422 | 68.3 | 0.517 |
| 2 | Harry Maguire | Center Back | Sweeper CB | 454 | 62.5 | 0.207 |
| 3 | Jordan Pickford | Goalkeeper | Goalkeeper | 486 | 62.5 | 0.029 |
| 4 | Jude Bellingham | Defensive Midfield | Ball-Winner | 442 | 59.7 | 0.216 |
| 5 | Bukayo Saka | Attacking Midfield/Wing | Progressive Winger | 291 | 59.5 | 0.278 |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 1.06; the possession-level scenario ceiling summed to 1.21, producing 0.14 modeled cumulative net xG of review opportunity and a 0.0022 mean EvA gap.

Average lineup matchup deltas were **+0.105 aerial**, **+1.067 pressing**, and **-0.652 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 4 possessions with 0.05 cumulative modeled gap (0.0120 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Olivier Giroud | Forward | Target Forward | 433 | 83.2 | 0.633 |
| 2 | Randal Kolo Muani | Forward | Target Forward | 204 | 78.7 | 0.736 |
| 3 | Kylian Mbappé Lottin | Forward | Progressive Winger | 654 | 75.5 | 0.728 |
| 4 | Theo Bernard François Hernández | Fullback/Wingback | Wide Creator | 548 | 72.7 | 0.118 |
| 5 | Aurélien Djani Tchouaméni | Defensive Midfield | Ball-Winner | 662 | 65.9 | 0.227 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Germany (GER)

Across the analyzed possessions, Germany's total xG was among the tournament leaders, while its possession-to-shot rate was among the tournament leaders. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.032 aerial**, **+0.154 pressing**, and **-0.075 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Joshua Kimmich | Fullback/Wingback | Ball-Winner | 294 | 78.5 | 0.133 |
| 2 | Jamal Musiala | Attacking Midfield/Wing | Progressive Winger | 274 | 78.3 | 0.428 |
| 3 | Niklas Süle | Fullback/Wingback | Sweeper CB | 288 | 63.2 | 0.090 |
| 4 | İlkay Gündoğan | Attacking Midfield/Wing | Ball-Winner | 190 | 61.7 | 0.508 |
| 5 | David Raum | Fullback/Wingback | Wide Creator | 250 | 60.8 | 0.037 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Ghana (GHA)

Across the analyzed possessions, Ghana's total xG was below the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.156 aerial**, **+1.137 pressing**, and **+0.026 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Best substitution scenario:** Kamaldeen Sulemana for Jordan Ayew under Patient Build-up produced the largest estimated team gain (+0.0053 expected net xG). Treat this as a video and training-ground hypothesis; the simulation does not encode fatigue, injury, match state, or all role constraints.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Mohammed Kudus | Attacking Midfield/Wing | Progressive Winger | 255 | 60.0 | 0.302 |
| 2 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 301 | 51.6 | 0.126 |
| 3 | Mohamed Salisu | Center Back | Deep Playmaker | 301 | 49.4 | 0.169 |
| 4 | Daniel Amartey | Center Back | Sweeper CB | 301 | 46.4 | 0.076 |
| 5 | André Ayew Pelé | Attacking Midfield/Wing | Target Forward | 199 | 44.4 | 0.483 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Iran (IRN)

Across the analyzed possessions, Iran's total xG was near the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.058 aerial**, **+1.725 pressing**, and **-1.059 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Morteza Pouraliganji | Center Back | Deep Playmaker | 305 | 68.7 | 0.125 |
| 2 | Mehdi Taremi | Forward | Target Forward | 305 | 62.2 | 0.447 |
| 3 | Ramin Rezaeian | Fullback/Wingback | Holding Anchor | 202 | 61.5 | 0.095 |
| 4 | Ehsan Hajsafi | Fullback/Wingback | Wide Creator | 250 | 49.0 | 0.033 |
| 5 | Seyed Majid Hosseini | Center Back | Deep Playmaker | 305 | 48.2 | 0.027 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Japan (JPN)

Across the analyzed possessions, Japan's total xG was above the tournament median, while its possession-to-shot rate was near the tournament median. Its suppression of immediate opponent transition xG was below the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.029 aerial**, **+10.178 pressing**, and **-0.086 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Wataru Endo | Defensive Midfield | Ball-Winner | 326 | 63.1 | 0.095 |
| 2 | Hidemasa Morita | Defensive Midfield | Ball-Winner | 298 | 58.5 | 0.109 |
| 3 | Shūichi Gonda | Goalkeeper | Goalkeeper | 413 | 54.1 | 0.015 |
| 4 | Maya Yoshida | Center Back | Sweeper CB | 413 | 51.4 | 0.223 |
| 5 | Ritsu Doan | Attacking Midfield/Wing | Progressive Winger | 232 | 50.5 | 0.300 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.071 aerial**, **+1.266 pressing**, and **-0.714 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Hirving Rodrigo Lozano Bahena | Attacking Midfield/Wing | Progressive Winger | 267 | 62.1 | 0.224 |
| 2 | Jesús Daniel Gallardo Vasconcelos | Fullback/Wingback | Wide Creator | 292 | 58.5 | 0.019 |
| 3 | Ernesto Alexis Vega Rojas | Attacking Midfield/Wing | Progressive Winger | 194 | 57.2 | 0.351 |
| 4 | Francisco Guillermo Ochoa Magaña | Goalkeeper | Goalkeeper | 292 | 49.8 | 0.001 |
| 5 | Luis Gerardo Chávez Magallón | Defensive Midfield | Progressive Winger | 292 | 41.1 | 0.115 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Morocco (MAR)

Across the analyzed possessions, Morocco's total xG was above the tournament median, while its possession-to-shot rate was below the tournament median. Its suppression of immediate opponent transition xG was among the lower values in this tournament sample (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 0.59; the possession-level scenario ceiling summed to 0.76, producing 0.17 modeled cumulative net xG of review opportunity and a 0.0028 mean EvA gap.

Average lineup matchup deltas were **-0.018 aerial**, **+4.404 pressing**, and **-0.129 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 10 possessions with 0.07 cumulative modeled gap (0.0066 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Achraf Hakimi Mouh | Fullback/Wingback | Holding Anchor | 661 | 80.0 | 0.171 |
| 2 | Yassine Bounou | Goalkeeper | Goalkeeper | 603 | 71.8 | 0.041 |
| 3 | Romain Saïss | Center Back | Deep Playmaker | 486 | 70.8 | 0.148 |
| 4 | Achraf Dari | Center Back | Deep Playmaker | 200 | 59.3 | 0.191 |
| 5 | Yahia Attiyat allah | Fullback/Wingback | Wide Creator | 350 | 58.7 | 0.123 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Netherlands (NED)

Across the analyzed possessions, Netherlands's total xG was above the tournament median, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was below the tournament median (lower transition exposure is better). The audit indicates a relatively large modeled opportunity for tactical tightening. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 1.13; the possession-level scenario ceiling summed to 1.48, producing 0.35 modeled cumulative net xG of review opportunity and a 0.0038 mean EvA gap.

Average lineup matchup deltas were **+0.024 aerial**, **+0.739 pressing**, and **+0.057 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 11 possessions with 0.11 cumulative modeled gap (0.0099 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Daley Blind | Fullback/Wingback | Wide Creator | 452 | 68.9 | 0.151 |
| 2 | Andries Noppert | Goalkeeper | Goalkeeper | 510 | 68.4 | 0.069 |
| 3 | Frenkie de Jong | Defensive Midfield | Ball-Winner | 499 | 62.3 | 0.194 |
| 4 | Teun Koopmeiners | Defensive Midfield | Ball-Winner | 242 | 57.6 | 0.273 |
| 5 | Memphis Depay | Forward | Target Forward | 316 | 54.1 | 0.339 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.054 aerial**, **+1.148 pressing**, and **-0.413 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Robert Lewandowski | Forward | Target Forward | 390 | 77.9 | 0.733 |
| 2 | Piotr Zieliński | Central/Wide Midfield | Ball-Winner | 344 | 62.1 | 0.208 |
| 3 | Wojciech Szczęsny | Goalkeeper | Goalkeeper | 390 | 58.3 | 0.039 |
| 4 | Jakub Kamiński | Central/Wide Midfield | Progressive Winger | 254 | 40.6 | 0.107 |
| 5 | Jakub Piotr Kiwior | Center Back | Deep Playmaker | 377 | 39.5 | 0.079 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.006 aerial**, **-4.222 pressing**, and **-0.010 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 303 | 70.9 | 0.587 |
| 2 | Bruno Miguel Borges Fernandes | Attacking Midfield/Wing | Progressive Winger | 385 | 63.8 | 0.303 |
| 3 | Bernardo Mota Veiga de Carvalho e Silva | Central/Wide Midfield | Ball-Winner | 382 | 62.2 | 0.092 |
| 4 | Kléper Laveran Lima Ferreira | Center Back | Sweeper CB | 389 | 61.6 | 0.142 |
| 5 | Diogo Meireles Costa | Goalkeeper | Goalkeeper | 489 | 59.2 | 0.037 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Qatar (QAT)

Across the analyzed possessions, Qatar's total xG was among the lower values in this tournament sample, while its possession-to-shot rate was among the lower values in this tournament sample. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.005 aerial**, **+2.608 pressing**, and **-0.286 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pedro Miguel Correia | Center Back | Deep Playmaker | 274 | 56.1 | 0.045 |
| 2 | Abdelkarim Hassan Al Haj Fadlalla | Center Back | Sweeper CB | 287 | 50.6 | 0.133 |
| 3 | Hassan Khalid Al Heidos | Central/Wide Midfield | Ball-Winner | 209 | 50.2 | 0.078 |
| 4 | Boualem Khoukhi | Center Back | Sweeper CB | 287 | 47.9 | 0.077 |
| 5 | Karim Boudiaf | Defensive Midfield | Ball-Winner | 196 | 37.8 | 0.087 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Saudi Arabia (KSA)

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

### Tactical and matchup read

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.117 aerial**, **-0.540 pressing**, and **+0.714 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Abdulelah Al Amri | Center Back | Deep Playmaker | 211 | 66.6 | 0.089 |
| 2 | Salem Mohammed Al Dawsari | Central/Wide Midfield | Progressive Winger | 299 | 64.5 | 0.392 |
| 3 | Mohammed Kanoo | Central/Wide Midfield | Ball-Winner | 299 | 56.2 | 0.131 |
| 4 | Mohammed Khalil Al Owais | Goalkeeper | Goalkeeper | 299 | 48.0 | -0.030 |
| 5 | Abdulelah Saad Hameed Al-Malki | Defensive Midfield | Ball-Winner | 189 | 46.4 | 0.109 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Senegal (SEN)

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

### Tactical and matchup read

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 0.67; the possession-level scenario ceiling summed to 0.84, producing 0.17 modeled cumulative net xG of review opportunity and a 0.0028 mean EvA gap.

Average lineup matchup deltas were **+0.016 aerial**, **-1.491 pressing**, and **-0.488 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 8 possessions with 0.05 cumulative modeled gap (0.0064 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Kalidou Koulibaly | Center Back | Deep Playmaker | 387 | 81.2 | 0.112 |
| 2 | Ismaïla Sarr | Attacking Midfield/Wing | Progressive Winger | 365 | 69.8 | 0.481 |
| 3 | Youssouf Sabaly | Fullback/Wingback | Holding Anchor | 387 | 67.4 | 0.080 |
| 4 | Krépin Diatta | Attacking Midfield/Wing | Progressive Winger | 182 | 54.0 | 0.231 |
| 5 | Edouard Mendy | Goalkeeper | Goalkeeper | 387 | 50.1 | 0.030 |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 0.76; the possession-level scenario ceiling summed to 0.96, producing 0.20 modeled cumulative net xG of review opportunity and a 0.0026 mean EvA gap.

Average lineup matchup deltas were **+0.055 aerial**, **-2.400 pressing**, and **-0.287 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Compact Pressure Block, possessions labeled Short Under Pressure were most often improved in the model by Patient Build-up. This pattern covered 13 possessions with 0.07 cumulative modeled gap (0.0052 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Strahinja Pavlović | Center Back | Deep Playmaker | 253 | 79.2 | 0.114 |
| 2 | Aleksandar Mitrović | Forward | Target Forward | 279 | 59.0 | 0.523 |
| 3 | Nikola Milenković | Center Back | Sweeper CB | 294 | 53.3 | 0.088 |
| 4 | Filip Kostić | Fullback/Wingback | Wide Creator | 191 | 53.1 | 0.019 |
| 5 | Vanja Milinković Savić | Goalkeeper | Goalkeeper | 294 | 48.2 | -0.004 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.118 aerial**, **+6.170 pressing**, and **+0.195 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Young-Gwon Kim | Center Back | Deep Playmaker | 373 | 62.5 | 0.249 |
| 2 | Min Jae Kim | Center Back | Sweeper CB | 283 | 60.2 | 0.108 |
| 3 | Woo-Young Jung | Defensive Midfield | Ball-Winner | 318 | 58.1 | 0.066 |
| 4 | Gue-Sung Cho | Forward | Target Forward | 297 | 57.8 | 0.336 |
| 5 | In-Beom Hwang | Defensive Midfield | Ball-Winner | 360 | 57.6 | 0.101 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.046 aerial**, **-12.554 pressing**, and **+0.142 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Pedro González López | Central/Wide Midfield | Ball-Winner | 372 | 73.1 | 0.109 |
| 2 | Álvaro Borja Morata Martín | Forward | Target Forward | 201 | 69.7 | 0.521 |
| 3 | Jordi Alba Ramos | Fullback/Wingback | Wide Creator | 271 | 68.8 | 0.065 |
| 4 | Unai Simón Mendibil | Goalkeeper | Goalkeeper | 414 | 67.0 | 0.059 |
| 5 | Rodrigo Hernández Cascante | Center Back | Sweeper CB | 414 | 61.4 | 0.199 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Switzerland (SUI)

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

### Tactical and matchup read

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.030 aerial**, **+2.987 pressing**, and **-0.646 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Breel-Donald Embolo | Forward | Target Forward | 330 | 66.4 | 0.656 |
| 2 | Manuel Obafemi Akanji | Center Back | Sweeper CB | 387 | 61.0 | 0.303 |
| 3 | Silvan Widmer | Fullback/Wingback | Holding Anchor | 282 | 54.1 | 0.033 |
| 4 | Ruben Vargas | Attacking Midfield/Wing | Progressive Winger | 287 | 46.7 | 0.222 |
| 5 | Remo Freuler | Defensive Midfield | Ball-Winner | 346 | 46.6 | 0.158 |

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

The scenario evaluator selected **No meaningful change** most often. Observed expected net xG was 0.89; the possession-level scenario ceiling summed to 0.93, producing 0.04 modeled cumulative net xG of review opportunity and a 0.0006 mean EvA gap.

Average lineup matchup deltas were **-0.059 aerial**, **-2.788 pressing**, and **+1.194 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

**Highest-volume review pattern:** against Wide Retreating Block, possessions labeled Direct Long Play were most often improved in the model by Patient Build-up. This pattern covered 4 possessions with 0.03 cumulative modeled gap (0.0082 per possession).

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ellyes Joris Skhiri | Defensive Midfield | Ball-Winner | 297 | 66.8 | 0.098 |
| 2 | Yassine Meriah | Center Back | Deep Playmaker | 297 | 53.9 | 0.066 |
| 3 | Ali Abdi | Fullback/Wingback | Wide Creator | 214 | 51.7 | 0.016 |
| 4 | Aïssa Bilal Laïdouni | Defensive Midfield | Ball-Winner | 257 | 50.9 | 0.102 |
| 5 | Montassar Omar Talbi | Center Back | Sweeper CB | 297 | 47.0 | 0.064 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.068 aerial**, **-0.925 pressing**, and **+0.496 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Christian Pulisic | Attacking Midfield/Wing | Progressive Winger | 336 | 74.1 | 0.350 |
| 2 | Tyler Adams | Defensive Midfield | Ball-Winner | 391 | 72.7 | 0.068 |
| 3 | Sergino Dest | Fullback/Wingback | Holding Anchor | 308 | 66.6 | 0.134 |
| 4 | Yunus Dimoara Musah | Central/Wide Midfield | Ball-Winner | 365 | 66.4 | 0.101 |
| 5 | Antonee Robinson | Fullback/Wingback | Wide Creator | 386 | 65.7 | 0.042 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

## Uruguay (URU)

Across the analyzed possessions, Uruguay's total xG was below the tournament median, while its possession-to-shot rate was above the tournament median. Its suppression of immediate opponent transition xG was above the tournament median (lower transition exposure is better). The audit indicates one of the smaller modeled tactic gaps in the sample. These are tournament-sample tendencies, not causal estimates of what would have happened under a different lineup or tactic.

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **+0.090 aerial**, **-0.252 pressing**, and **-0.035 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Rodrigo Bentancur Colmán | Defensive Midfield | Ball-Winner | 232 | 74.3 | 0.236 |
| 2 | José María Giménez de Vargas | Center Back | Deep Playmaker | 298 | 64.7 | 0.098 |
| 3 | Mathías Olivera Miramontes | Fullback/Wingback | Wide Creator | 264 | 63.6 | 0.044 |
| 4 | Sebastián Coates Nión | Center Back | Deep Playmaker | 200 | 58.3 | 0.097 |
| 5 | Federico Santiago Valverde Dipetta | Defensive Midfield | Ball-Winner | 298 | 55.1 | 0.118 |

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

The scenario evaluator selected **Not available** most often. Observed expected net xG was nan; the possession-level scenario ceiling summed to nan, producing nan modeled cumulative net xG of review opportunity and a nan mean EvA gap.

Average lineup matchup deltas were **-0.031 aerial**, **+1.564 pressing**, and **-0.189 recovery**. These are relative proxies, so the signs are more useful for matchup planning than the raw magnitudes.

### Leading tournament-role profiles

| Rank | Player | Position group | Functional role | Minutes | Role score | Net xG/90 |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Ben Davies | Center Back | Deep Playmaker | 261 | 74.3 | 0.146 |
| 2 | Chris Mepham | Center Back | Sweeper CB | 297 | 59.3 | 0.075 |
| 3 | Neco Williams | Fullback/Wingback | Wide Creator | 216 | 57.8 | 0.035 |
| 4 | Kieffer Roberto Francisco Moore | Forward | Target Forward | 252 | 56.0 | 0.363 |
| 5 | Wayne Hennessey | Goalkeeper | Goalkeeper | 203 | 42.5 | -0.005 |

Coaching interpretation: begin with the observed style and matchup signals, then inspect the flagged possessions on video. Test the modeled style or personnel change in a comparable game-state segment before adopting it as a match plan.

# Top tournament-role players by position

These leaderboards rank only the analyzed tournament cohort and use different weights for different roles. A score of 80 means a strong blend of the selected within-position indicators; it does not mean an 80% chance of success. Sample size, team tactics, opponent quality, and role assignment all affect the component metrics. To meet the preregistered rank-stability gate, the published score blends 70% objective baseline rank score with 30% smoothed v2 role score; the unblended v2 score is retained in the profile CSV.

## Position-score construction

- **Goalkeeper:** goals prevented p90 35%, cross claims p90 15%, sweeping distance 10%, distribution under pressure 15%, pass completion 10%, minutes 15%.
- **Center Back:** aerial dominance index 25%, pressing intensity index 15%, speed recovery index 20%, net xg contribution p90 15%, pass progression per pass 15%, minutes 10%.
- **Fullback/Wingback:** aerial dominance index 10%, pressing intensity index 20%, speed recovery index 20%, net xg contribution p90 20%, progressive passes p90 15%, key passes p90 5%, minutes 10%.
- **Defensive Midfield:** aerial dominance index 10%, pressing intensity index 20%, speed recovery index 20%, net xg contribution p90 20%, progressive passes p90 15%, pass completion 5%, minutes 10%.
- **Central/Wide Midfield:** pressing intensity index 20%, speed recovery index 15%, net xg contribution p90 25%, progressive passes p90 20%, key passes p90 10%, minutes 10%.
- **Attacking Midfield/Wing:** pressing intensity index 15%, speed recovery index 10%, net xg contribution p90 30%, progressive carries p90 15%, key passes p90 15%, xg p90 5%, minutes 10%.
- **Forward:** aerial dominance index 15%, pressing intensity index 10%, net xg contribution p90 30%, shots p90 15%, xg p90 20%, minutes 10%.

**Goalkeeper warning:** the source features do not provide a complete provider post-shot-xG model. The report uses on-target StatsBomb shot xG as an explicitly labeled proxy, then adds goals prevented, claims, sweeping location, and pressured distribution. It remains unsuitable as a standalone goalkeeper selection model.

## Goalkeeper

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Dominik Livaković | Croatia | Goalkeeper | Goalkeeper | 720 | 72.2 | 0.037 | 0.00 | 0.25 | 4.12 |
| 2 | Yassine Bounou | Morocco | Goalkeeper | Goalkeeper | 603 | 71.8 | 0.041 | 0.00 | 0.15 | 3.73 |
| 3 | Andries Noppert | Netherlands | Goalkeeper | Goalkeeper | 510 | 68.4 | 0.069 | 0.00 | 0.00 | 4.59 |
| 4 | Unai Simón Mendibil | Spain | Goalkeeper | Goalkeeper | 414 | 67.0 | 0.059 | 0.00 | 0.00 | 2.61 |
| 5 | Matthew Charles Turner | United States | Goalkeeper | Goalkeeper | 391 | 65.6 | 0.039 | 0.00 | 0.00 | 3.91 |
| 6 | Damián Emiliano Martínez | Argentina | Goalkeeper | Goalkeeper | 734 | 65.2 | 0.016 | 0.00 | 0.00 | 3.68 |
| 7 | Alisson Ramsés Becker | Brazil | Goalkeeper | Goalkeeper | 395 | 62.5 | 0.022 | 0.00 | 0.00 | 5.01 |
| 8 | Jordan Pickford | England | Goalkeeper | Goalkeeper | 486 | 62.5 | 0.029 | 0.00 | 0.00 | 2.96 |
| 9 | Diogo Meireles Costa | Portugal | Goalkeeper | Goalkeeper | 489 | 59.2 | 0.037 | 0.00 | 0.18 | 2.76 |
| 10 | Hugo Lloris | France | Goalkeeper | Goalkeeper | 614 | 58.6 | 0.028 | 0.00 | 0.00 | 2.34 |

The goalkeeper ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Center Back

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Kalidou Koulibaly | Senegal | Right Center Back | Deep Playmaker | 387 | 81.2 | 0.112 | 0.80 | 9.30 | 4.65 |
| 2 | Jean-Charles Castelletto | Cameroon | Right Center Back | Deep Playmaker | 192 | 80.7 | 0.304 | 1.00 | 9.46 | 3.14 |
| 3 | Strahinja Pavlović | Serbia | Left Center Back | Deep Playmaker | 253 | 79.2 | 0.114 | 1.00 | 9.89 | 3.93 |
| 4 | Ben Davies | Wales | Left Center Back | Deep Playmaker | 261 | 74.3 | 0.146 | 0.73 | 8.46 | 4.36 |
| 5 | Romain Saïss | Morocco | Left Center Back | Deep Playmaker | 486 | 70.8 | 0.148 | 0.80 | 7.60 | 2.22 |
| 6 | Morteza Pouraliganji | Iran | Right Center Back | Deep Playmaker | 305 | 68.7 | 0.125 | 0.75 | 10.62 | 2.36 |
| 7 | Abdulelah Al Amri | Saudi Arabia | Right Center Back | Deep Playmaker | 211 | 66.6 | 0.089 | 0.71 | 8.06 | 4.08 |
| 8 | Joachim Andersen | Denmark | Right Center Back | Deep Playmaker | 291 | 66.4 | 0.119 | 0.67 | 8.34 | 3.38 |
| 9 | Ibrahima Konaté | France | Left Center Back | Sweeper CB | 331 | 65.7 | 0.133 | 0.90 | 6.80 | 3.54 |
| 10 | José María Giménez de Vargas | Uruguay | Right Center Back | Deep Playmaker | 298 | 64.7 | 0.098 | 0.85 | 8.54 | 2.28 |

The center back ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Fullback/Wingback

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Achraf Hakimi Mouh | Morocco | Right Back | Holding Anchor | 661 | 80.0 | 0.171 | 0.57 | 16.21 | 4.90 |
| 2 | Joshua Kimmich | Germany | Right Back | Ball-Winner | 294 | 78.5 | 0.133 | 0.71 | 12.41 | 4.18 |
| 3 | Éder Gabriel Militão | Brazil | Right Back | Ball-Winner | 364 | 75.2 | 0.140 | 0.40 | 13.86 | 4.95 |
| 4 | Alistair Johnston | Canada | Right Back | Holding Anchor | 285 | 74.2 | 0.186 | 0.73 | 12.29 | 3.94 |
| 5 | Theo Bernard François Hernández | France | Left Back | Wide Creator | 548 | 72.7 | 0.118 | 0.60 | 12.63 | 3.94 |
| 6 | Daley Blind | Netherlands | Left Wing Back | Wide Creator | 452 | 68.9 | 0.151 | 0.43 | 17.70 | 2.59 |
| 7 | Jordi Alba Ramos | Spain | Left Back | Wide Creator | 271 | 68.8 | 0.065 | 0.25 | 12.76 | 4.19 |
| 8 | Pervis Josué Estupiñán Tenorio | Ecuador | Left Back | Wide Creator | 288 | 67.9 | 0.083 | 0.57 | 12.37 | 4.37 |
| 9 | Youssouf Sabaly | Senegal | Right Back | Holding Anchor | 387 | 67.4 | 0.080 | 0.43 | 11.85 | 6.04 |
| 10 | Alex Sandro Lobo Silva | Brazil | Left Back | Wide Creator | 200 | 67.1 | 0.061 | 0.83 | 11.87 | 4.25 |

The fullback/wingback ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Defensive Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Marcelo Brozović | Croatia | Center Defensive Midfield | Ball-Winner | 570 | 79.3 | 0.288 | 0.62 | 16.74 | 5.05 |
| 2 | Leandro Daniel Paredes | Argentina | Right Defensive Midfield | Ball-Winner | 235 | 77.7 | 0.488 | 1.00 | 17.64 | 4.15 |
| 3 | Rodrigo Bentancur Colmán | Uruguay | Left Defensive Midfield | Ball-Winner | 232 | 74.3 | 0.236 | 0.73 | 17.25 | 5.36 |
| 4 | Tyler Adams | United States | Center Defensive Midfield | Ball-Winner | 391 | 72.7 | 0.068 | 0.60 | 20.48 | 6.21 |
| 5 | Ellyes Joris Skhiri | Tunisia | Right Defensive Midfield | Ball-Winner | 297 | 66.8 | 0.098 | 0.67 | 17.49 | 5.38 |
| 6 | Rodrigo Javier De Paul | Argentina | Right Defensive Midfield | Holding Anchor | 635 | 66.0 | 0.138 | 0.33 | 18.01 | 4.82 |
| 7 | Aurélien Djani Tchouaméni | France | Right Defensive Midfield | Ball-Winner | 662 | 65.9 | 0.227 | 0.75 | 10.74 | 4.89 |
| 8 | Wataru Endo | Japan | Right Defensive Midfield | Ball-Winner | 326 | 63.1 | 0.095 | 0.53 | 20.43 | 6.35 |
| 9 | Enzo Fernandez | Argentina | Center Defensive Midfield | Ball-Winner | 601 | 63.1 | 0.222 | 0.42 | 17.52 | 3.74 |
| 10 | Frenkie de Jong | Netherlands | Left Defensive Midfield | Ball-Winner | 499 | 62.3 | 0.194 | 0.86 | 14.96 | 3.60 |

The defensive midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Central/Wide Midfield

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Luka Modrić | Croatia | Right Center Midfield | Ball-Winner | 673 | 82.4 | 0.241 | 0.50 | 17.93 | 4.95 |
| 2 | Pedro González López | Spain | Left Center Midfield | Ball-Winner | 372 | 73.1 | 0.109 | 0.60 | 14.74 | 6.28 |
| 3 | Mateo Kovačić | Croatia | Left Center Midfield | Ball-Winner | 650 | 72.6 | 0.121 | 0.75 | 21.19 | 3.88 |
| 4 | Yunus Dimoara Musah | United States | Right Center Midfield | Ball-Winner | 365 | 66.4 | 0.101 | 0.25 | 19.24 | 4.44 |
| 5 | Christian Dannemann Eriksen | Denmark | Left Center Midfield | Progressive Winger | 291 | 65.6 | 0.129 | 0.25 | 13.35 | 4.51 |
| 6 | Weston McKennie | United States | Right Midfield | Ball-Winner | 274 | 65.3 | 0.168 | 0.62 | 14.70 | 4.49 |
| 7 | Rodrygo Silva de Goes | Brazil | Left Midfield | Progressive Winger | 199 | 64.7 | 0.399 | 0.60 | 16.88 | 4.08 |
| 8 | Salem Mohammed Al Dawsari | Saudi Arabia | Left Midfield | Progressive Winger | 299 | 64.5 | 0.392 | 0.50 | 14.38 | 4.30 |
| 9 | Alphonso Davies | Canada | Left Midfield | Progressive Winger | 285 | 63.1 | 0.248 | 0.56 | 16.26 | 4.86 |
| 10 | Bernardo Mota Veiga de Carvalho e Silva | Portugal | Right Center Midfield | Ball-Winner | 382 | 62.2 | 0.092 | 0.12 | 14.60 | 4.95 |

The central/wide midfield ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Attacking Midfield/Wing

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Right Wing | Progressive Winger | 734 | 80.6 | 1.004 | 0.33 | 10.91 | 3.68 |
| 2 | Jamal Musiala | Germany | Center Attacking Midfield | Progressive Winger | 274 | 78.3 | 0.428 | 0.20 | 14.25 | 4.72 |
| 3 | Raphael Dias Belloli | Brazil | Right Wing | Progressive Winger | 330 | 74.4 | 0.294 | 0.00 | 15.52 | 4.36 |
| 4 | Christian Pulisic | United States | Left Wing | Progressive Winger | 336 | 74.1 | 0.350 | 0.40 | 11.77 | 4.55 |
| 5 | Ismaïla Sarr | Senegal | Left Wing | Progressive Winger | 365 | 69.8 | 0.481 | 0.50 | 13.31 | 3.94 |
| 6 | Neymar da Silva Santos Junior | Brazil | Center Attacking Midfield | Progressive Winger | 281 | 69.5 | 0.628 | 0.20 | 11.13 | 3.88 |
| 7 | Bruno Miguel Borges Fernandes | Portugal | Center Attacking Midfield | Progressive Winger | 385 | 63.8 | 0.303 | 0.21 | 15.20 | 3.27 |
| 8 | Antoine Griezmann | France | Center Attacking Midfield | Ball-Winner | 586 | 63.5 | 0.149 | 0.64 | 20.89 | 3.84 |
| 9 | Kingsley Coman | France | Right Wing | Progressive Winger | 206 | 62.2 | 0.384 | 0.14 | 16.36 | 3.58 |
| 10 | Hirving Rodrigo Lozano Bahena | Mexico | Right Wing | Progressive Winger | 267 | 62.1 | 0.224 | 0.07 | 15.69 | 4.46 |

The attacking midfield/wing ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

## Forward

| Rank | Player | Team | Detailed position | Role | Min. | Score | Net xG/90 | Aerial | Pressing | Recovery |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lautaro Javier Martínez | Argentina | Left Center Forward | Target Forward | 273 | 83.4 | 0.823 | 0.55 | 10.48 | 2.11 |
| 2 | Olivier Giroud | France | Center Forward | Target Forward | 433 | 83.2 | 0.633 | 0.56 | 12.69 | 0.62 |
| 3 | Randal Kolo Muani | France | Center Forward | Target Forward | 204 | 78.7 | 0.736 | 0.53 | 17.44 | 2.40 |
| 4 | Robert Lewandowski | Poland | Center Forward | Target Forward | 390 | 77.9 | 0.733 | 0.45 | 9.70 | 2.77 |
| 5 | Kylian Mbappé Lottin | France | Left Center Forward | Progressive Winger | 654 | 75.5 | 0.728 | 0.25 | 5.23 | 3.99 |
| 6 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Center Forward | Target Forward | 303 | 70.9 | 0.587 | 0.50 | 6.24 | 1.49 |
| 7 | Álvaro Borja Morata Martín | Spain | Center Forward | Target Forward | 201 | 69.7 | 0.521 | 0.67 | 12.89 | 1.88 |
| 8 | Harry Kane | England | Center Forward | Target Forward | 422 | 68.3 | 0.517 | 0.48 | 6.62 | 2.56 |
| 9 | Marko Livaja | Croatia | Center Forward | Target Forward | 256 | 67.3 | 0.610 | 0.31 | 15.34 | 2.50 |
| 10 | Breel-Donald Embolo | Switzerland | Center Forward | Target Forward | 330 | 66.4 | 0.656 | 0.22 | 13.08 | 1.09 |

The forward ordering is a role-fit shortlist for this tournament sample. Review component columns, minutes, opponent context, and the player's team section before treating a small score difference as meaningful.

# Recommended coaching workflow

1. Select the opponent's team section and identify its observed attack style, transition exposure, and physical matchup deltas.
2. Pull video for the stated highest-volume review pattern; confirm that the possession labels match the intended tactical interpretation.
3. Use the position leaderboard only to identify candidate role profiles, then check the player's own team context and tournament minutes.
4. Re-run the substitution or style scenario with the expected match state and available squad before training it.
5. Record the pre-match hypothesis and post-match outcome so future calibration can separate useful signals from tournament-specific noise.

# Limitations and validity

- The analysis is valid as an exploratory and predictive decision-support artifact over the supplied tournament data. It is not a randomized or causal study.
- The v2 scenario pipeline requires a schema-checked calibrated classifier bundle. If threshold validation abstains, transition risk is gated to zero rather than converted into a weak positive recommendation.
- Rare transition events create high variance. Aggregate patterns and precision-aware decisions are safer than interpreting individual possessions as certain events.
- Player physicality uses event-derived proxies: ground-duel wins approximate tackle-related success, and recoveries approximate defensive recovery activity.
- Player rankings cover the 342-player tournament-minute cohort used by the pipeline, not every registered player and not performance outside this competition.
- Recommended actions require video confirmation and domain review. Medical status, fatigue, tactical instructions, score state, and opposition substitutions can materially change the correct decision.

---

Generated reproducibly from the processed possession, player-profile, matchup, audit, and simulation artifacts in this repository.
