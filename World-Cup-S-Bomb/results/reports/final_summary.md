# 2022 FIFA World Cup Player Ranking Report

## Executive summary

This report consolidates **32 national teams** and **593 eligible rated players** (outfield 45+ minutes; goalkeepers 90+). It uses StatsBomb events, lineups, minutes, and coverage-qualified 360 freeze frames. It does not use optical tracking, external ratings, or player-name adjustments.

The position-aware tournament rankings are stored under `results/reports/ranking/`. They add formal 360 groups while preserving the source position and role detail.

## Global top 10 outfield players — tournament ranking v2

| Global Rank V2 | Player Name | Team | Position Group 360 | Functional Role | Final Player Rating V2 |
|---|---|---|---|---|---|
| 1.0000 | Lionel Andrés Messi Cuccittini | Argentina | AM | Progressive Winger | 1.0000 |
| 2.0000 | Kylian Mbappé Lottin | France | FW | Progressive Winger | 0.9389 |
| 3.0000 | Bruno Miguel Borges Fernandes | Portugal | AM | Progressive Winger | 0.8365 |
| 4.0000 | Robert Lewandowski | Poland | FW | Target Forward / Penalty-Box Anchor | 0.8227 |
| 5.0000 | Christian Pulisic | United States | AM | Progressive Winger | 0.7847 |
| 6.0000 | Mehdi Taremi | Iran | FW | Target Forward | 0.7779 |
| 7.0000 | Harry Kane | England | FW | Target Forward | 0.7777 |
| 8.0000 | Mateo Kovačić | Croatia | CM | Deep Playmaker / Metronome | 0.7730 |
| 9.0000 | Neymar da Silva Santos Junior | Brazil | AM | Progressive Winger | 0.7702 |
| 10.0000 | Luka Modrić | Croatia | CM | Deep Playmaker / Metronome | 0.7648 |

## Global top five goalkeepers — tournament ranking v2

| Gk Rank V2 | Player Name | Team | Gk Rating V2 |
|---|---|---|---|
| 1.0000 | Dominik Livaković | Croatia | 1.0000 |
| 2.0000 | Damián Emiliano Martínez | Argentina | 0.5971 |
| 3.0000 | Yassine Bounou | Morocco | 0.5876 |
| 4.0000 | Wojciech Szczęsny | Poland | 0.4394 |
| 5.0000 | Unai Simón Mendibil | Spain | 0.3417 |

The active contribution layer is `role_aware_fallback`. The experimental attention challenger remains available but affects rankings only when it passes its match-disjoint metric gate.

## How to read the player rating

The preserved V5 contribution score uses the development-gated baseline VAEP feature set and grouped ElasticNet offense/defense heads with explicit role weights, VAEP/touch, open-play and set-piece-aware xT, sample-adjusted completeness, coverage-qualified off-ball value, and xD-style defensive disruption. Positive ElasticNet calibration selects the composite weights with team-disjoint folds, followed by minutes/(minutes+450) position-prior shrinkage.

The tournament ranking v2 adds explicit goals, xG, shots, xA, chance creation, progression, possession, defending, and off-ball components normalized within `position_group_360`. A capped, general role-based finishing treatment corrects the structural penalty on goal-centric forwards; it never checks player names.

Goalkeepers use a separate tournament-v2 matrix led by a match-disjoint PSxG-GA proxy, reliability-shrunk save rates, penalty performance, box command, sweeping, distribution under pressure, and an explicit shootout-impact term. They are excluded from the outfield global ranking because StatsBomb Open Data does not contain native post-shot xG. Missing 360 evidence remains missing, and role labels never award rating points.

## General player summary

### Overall leaders

| Global Rank V2 | Player Name | Team | Position Group 360 | Functional Role | Final Player Rating V2 |
|---|---|---|---|---|---|
| 1.0000 | Lionel Andrés Messi Cuccittini | Argentina | AM | Progressive Winger | 1.0000 |
| 2.0000 | Kylian Mbappé Lottin | France | FW | Progressive Winger | 0.9389 |
| 3.0000 | Bruno Miguel Borges Fernandes | Portugal | AM | Progressive Winger | 0.8365 |
| 4.0000 | Robert Lewandowski | Poland | FW | Target Forward / Penalty-Box Anchor | 0.8227 |
| 5.0000 | Christian Pulisic | United States | AM | Progressive Winger | 0.7847 |
| 6.0000 | Mehdi Taremi | Iran | FW | Target Forward | 0.7779 |
| 7.0000 | Harry Kane | England | FW | Target Forward | 0.7777 |
| 8.0000 | Mateo Kovačić | Croatia | CM | Deep Playmaker / Metronome | 0.7730 |
| 10.0000 | Luka Modrić | Croatia | CM | Deep Playmaker / Metronome | 0.7648 |
| 11.0000 | Antoine Griezmann | France | AM | Hybrid Playmaker / Roaming Creator | 0.7607 |
| 12.0000 | Ángel Fabián Di María Hernández | Argentina | AM | Progressive Winger | 0.7554 |
| 13.0000 | Olivier Giroud | France | FW | Target Forward / Penalty-Box Anchor | 0.7453 |
| 14.0000 | Richarlison de Andrade | Brazil | FW | Pressing Forward | 0.7381 |
| 18.0000 | Memphis Depay | Netherlands | FW | Target Forward | 0.7234 |
| 20.0000 | Julián Álvarez | Argentina | FW | Pressing Forward | 0.7086 |
| 22.0000 | Theo Bernard François Hernández | France | FB | Attacking Wingback | 0.6969 |
| 24.0000 | Cristiano Ronaldo dos Santos Aveiro | Portugal | FW | Target Forward | 0.6923 |
| 27.0000 | Vinícius José Paixão de Oliveira Júnior | Brazil | AM | Progressive Winger | 0.6809 |
| 29.0000 | Cody Mathès Gakpo | Netherlands | AM | Progressive Winger | 0.6788 |
| 30.0000 | Hakim Ziyech | Morocco | AM | Deep Playmaker | 0.6748 |

### Position-group leaders

| Position Group 360 | Position Rank V2 | Player Name | Team | Functional Role | Final Player Rating V2 |
|---|---|---|---|---|---|
| AM | 1.0000 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 1.0000 |
| AM | 2.0000 | Bruno Miguel Borges Fernandes | Portugal | Progressive Winger | 0.8365 |
| AM | 3.0000 | Christian Pulisic | United States | Progressive Winger | 0.7847 |
| AM | 4.0000 | Neymar da Silva Santos Junior | Brazil | Progressive Winger | 0.7702 |
| AM | 5.0000 | Antoine Griezmann | France | Hybrid Playmaker / Roaming Creator | 0.7607 |
| CB | 1.0000 | Rodrigo Hernández Cascante | Spain | Ball-Playing Centre-Back | 0.6520 |
| CB | 2.0000 | Ibrahima Konaté | France | Ball-Playing Centre-Back | 0.6300 |
| CB | 3.0000 | Joško Gvardiol | Croatia | Ball-Playing Centre-Back | 0.6128 |
| CB | 4.0000 | Harry Maguire | England | Sweeper CB | 0.5924 |
| CB | 5.0000 | Thiago Emiliano da Silva | Brazil | Ball-Playing Centre-Back | 0.5571 |
| CM | 1.0000 | Mateo Kovačić | Croatia | Deep Playmaker / Metronome | 0.7730 |
| CM | 2.0000 | Luka Modrić | Croatia | Deep Playmaker / Metronome | 0.7648 |
| CM | 3.0000 | Pedro González López | Spain | Holding Anchor | 0.6630 |
| CM | 4.0000 | Alexis Mac Allister | Argentina | Ball-Winner | 0.6482 |
| CM | 5.0000 | Christian Dannemann Eriksen | Denmark | Progressive Winger | 0.6217 |
| DM | 1.0000 | Jude Bellingham | England | Box-to-Box / Engine Midfielder | 0.6702 |
| DM | 2.0000 | Frenkie de Jong | Netherlands | Holding Anchor | 0.6481 |
| DM | 3.0000 | Rodrigo Bentancur Colmán | Uruguay | Box-to-Box / Engine Midfielder | 0.6246 |
| DM | 4.0000 | Enzo Fernandez | Argentina | Holding Anchor | 0.5957 |
| DM | 5.0000 | Rodrigo Javier De Paul | Argentina | Deep Playmaker | 0.5941 |
| FB | 1.0000 | Theo Bernard François Hernández | France | Attacking Wingback | 0.6969 |
| FB | 2.0000 | Joshua Kimmich | Germany | Attacking Wingback | 0.6896 |
| FB | 3.0000 | David Raum | Germany | Attacking Wingback | 0.6543 |
| FB | 4.0000 | Jordi Alba Ramos | Spain | Attacking Wingback | 0.6251 |
| FB | 5.0000 | Alistair Johnston | Canada | Attacking Wingback | 0.6040 |
| FW | 1.0000 | Kylian Mbappé Lottin | France | Progressive Winger | 0.9389 |
| FW | 2.0000 | Robert Lewandowski | Poland | Target Forward / Penalty-Box Anchor | 0.8227 |
| FW | 3.0000 | Mehdi Taremi | Iran | Target Forward | 0.7779 |
| FW | 4.0000 | Harry Kane | England | Target Forward | 0.7777 |
| FW | 5.0000 | Olivier Giroud | France | Target Forward / Penalty-Box Anchor | 0.7453 |

### Largest upward rank movements

| Player Name | Team | Old Global Rank | New Global Rank | Rank Improvement |
|---|---|---|---|---|
| Leandro Daniel Paredes | Argentina | 505 | 75 | 430 |
| Marcelo Brozović | Croatia | 510 | 106 | 404 |
| Aurélien Djani Tchouaméni | France | 476 | 78 | 398 |
| Tyler Adams | United States | 492 | 105 | 387 |
| Sergio Busquets i Burgos | Spain | 466 | 99 | 367 |
| Luka Modrić | Croatia | 371 | 10 | 361 |
| Youssef En-Nesyri | Morocco | 529 | 196 | 333 |
| Nikola Milenković | Serbia | 547 | 217 | 330 |
| Jean-Charles Castelletto | Cameroon | 518 | 191 | 327 |
| Thomas Teye Partey | Ghana | 519 | 193 | 326 |

### Largest downward rank movements

| Player Name | Team | Old Global Rank | New Global Rank | Rank Improvement |
|---|---|---|---|---|
| Aziz Eraltay Behich | Australia | 97 | 509 | -412 |
| Sultan Abdullah Salim Al Ghannam | Saudi Arabia | 101 | 478 | -377 |
| Bartosz Bereszyński | Poland | 168 | 541 | -373 |
| Brennan Johnson | Wales | 51 | 420 | -369 |
| Jesper Lindstrøm | Denmark | 157 | 497 | -340 |
| Yasir Gharsan Al Shahrani | Saudi Arabia | 208 | 544 | -336 |
| Jewison Bennette | Costa Rica | 164 | 498 | -334 |
| Nicholas Williams Arthuer | Spain | 150 | 475 | -325 |
| Takefusa Kubo | Japan | 170 | 491 | -321 |
| Kamaldeen Sulemana | Ghana | 82 | 402 | -320 |

Rank movement compares the prior global ordering with tournament ranking v2 ordering; it does not compare raw rating magnitudes.

## All-team overview

| Team | Eligible Players | Observed Players | Top Ranked Player | Top Global Rank | Total Xt | Pressure Resistance | Mean Creation | Mean Defensive | Mean Ball Security |
|---|---|---|---|---|---|---|---|---|---|
| Argentina | 20 | 19 | Lionel Andrés Messi Cuccittini | 1 | 4.0073 | 0.7447 | 0.4948 | 0.5032 | 0.5631 |
| Australia | 17 | 16 | Craig Goodwin | 128 | 1.1032 | 0.6496 | 0.4821 | 0.5524 | 0.4073 |
| Belgium | 17 | 16 | Kevin De Bruyne | 48 | 1.4404 | 0.7696 | 0.5216 | 0.4606 | 0.5504 |
| Brazil | 25 | 23 | Neymar da Silva Santos Junior | 9 | 3.8085 | 0.7291 | 0.5582 | 0.5207 | 0.5394 |
| Cameroon | 18 | 16 | Vincent Paté Aboubakar | 60 | 1.0760 | 0.6971 | 0.5205 | 0.5087 | 0.5478 |
| Canada | 16 | 15 | Alistair Johnston | 61 | 1.7913 | 0.7118 | 0.5417 | 0.5160 | 0.5611 |
| Costa Rica | 17 | 16 | Francisco Javier Calvo Quesada | 292 | 0.4184 | 0.6509 | 0.3933 | 0.5727 | 0.5415 |
| Croatia | 20 | 19 | Mateo Kovačić | 8 | 3.7160 | 0.7430 | 0.5431 | 0.5524 | 0.4884 |
| Denmark | 18 | 17 | Christian Dannemann Eriksen | 54 | 1.7188 | 0.7086 | 0.5094 | 0.5011 | 0.4851 |
| Ecuador | 16 | 15 | Pervis Josué Estupiñán Tenorio | 72 | 1.0181 | 0.6954 | 0.4626 | 0.5420 | 0.5067 |
| England | 19 | 18 | Harry Kane | 7 | 2.5219 | 0.7556 | 0.5374 | 0.4677 | 0.6180 |
| France | 22 | 20 | Kylian Mbappé Lottin | 2 | 3.9248 | 0.6863 | 0.5247 | 0.5475 | 0.5195 |
| Germany | 17 | 16 | Jamal Musiala | 16 | 2.4318 | 0.7731 | 0.6119 | 0.5340 | 0.5662 |
| Ghana | 17 | 16 | Mohammed Kudus | 183 | 0.9360 | 0.6763 | 0.4424 | 0.5817 | 0.5040 |
| Iran | 20 | 18 | Mehdi Taremi | 6 | 1.2461 | 0.6687 | 0.5135 | 0.5081 | 0.4805 |
| Japan | 22 | 21 | Takuma Asano | 21 | 1.5415 | 0.6415 | 0.5311 | 0.5298 | 0.3974 |
| Mexico | 18 | 17 | Hirving Rodrigo Lozano Bahena | 56 | 1.3586 | 0.6241 | 0.5345 | 0.5386 | 0.4373 |
| Morocco | 23 | 21 | Hakim Ziyech | 30 | 2.4078 | 0.6771 | 0.4573 | 0.5519 | 0.4718 |
| Netherlands | 18 | 17 | Memphis Depay | 18 | 2.0451 | 0.7135 | 0.5206 | 0.4882 | 0.5096 |
| Poland | 16 | 15 | Robert Lewandowski | 4 | 1.1292 | 0.6818 | 0.4694 | 0.5129 | 0.5278 |
| Portugal | 22 | 21 | Bruno Miguel Borges Fernandes | 3 | 2.6573 | 0.7085 | 0.5171 | 0.4842 | 0.5829 |
| Qatar | 15 | 13 | Mohammed Muntari | 127 | 0.7960 | 0.6995 | 0.4849 | 0.4605 | 0.5492 |
| Saudi Arabia | 20 | 19 | Salem Mohammed Al Dawsari | 15 | 1.0502 | 0.6235 | 0.4610 | 0.5524 | 0.4362 |
| Senegal | 18 | 17 | Ismaïla Sarr | 57 | 1.6919 | 0.6875 | 0.5320 | 0.5050 | 0.5330 |
| Serbia | 16 | 15 | Aleksandar Mitrović | 42 | 1.3908 | 0.6740 | 0.4786 | 0.4911 | 0.4913 |
| South Korea | 19 | 18 | Kang-In Lee | 89 | 1.8015 | 0.6712 | 0.5134 | 0.5248 | 0.5144 |
| Spain | 20 | 19 | Álvaro Borja Morata Martín | 19 | 2.5669 | 0.8268 | 0.4769 | 0.4885 | 0.5700 |
| Switzerland | 19 | 17 | Breel-Donald Embolo | 46 | 1.4531 | 0.7318 | 0.5231 | 0.4384 | 0.5397 |
| Tunisia | 18 | 17 | Youssef Msakni | 68 | 1.2810 | 0.5839 | 0.5512 | 0.5960 | 0.3517 |
| United States | 18 | 17 | Christian Pulisic | 5 | 2.0784 | 0.7900 | 0.5144 | 0.4811 | 0.5368 |
| Uruguay | 17 | 16 | Rodrigo Bentancur Colmán | 52 | 1.4720 | 0.6460 | 0.5435 | 0.5093 | 0.4344 |
| Wales | 15 | 13 | Gareth Frank Bale | 114 | 0.8960 | 0.6856 | 0.5076 | 0.5235 | 0.4787 |

# Team-by-team summary

Scope note: every team top five below contains outfield players only. Goalkeepers are excluded because `gk_rating_v2` uses a separate, non-comparable scale; consult the goalkeeper leaderboard for their ordering.

## Argentina

- Total xT created: 4.0073
- Total xA created: 6.7228
- Pass completion under pressure: 0.7447
- Mean defensive hull area: 647.6227
- Mean defensive density: 0.0258

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 1.0000 | Lionel Andrés Messi Cuccittini | AM | Progressive Winger | 733.9000 | 1.0000 |
| 2.0000 | 12.0000 | Ángel Fabián Di María Hernández | AM | Progressive Winger | 304.8167 | 0.7554 |
| 3.0000 | 20.0000 | Julián Álvarez | FW | Pressing Forward | 485.2333 | 0.7086 |
| 4.0000 | 43.0000 | Alexis Mac Allister | CM | Ball-Winner | 552.3500 | 0.6482 |
| 5.0000 | 63.0000 | Lautaro Javier Martínez | FW | Target Forward / Penalty-Box Anchor | 273.0000 | 0.5979 |


## Australia

- Total xT created: 1.1032
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 128.0000 | Craig Goodwin | AM | Wide Creator | 241.7000 | 0.5007 |
| 2.0000 | 206.0000 | Fran Karačić | FB | Attacking Wingback | 100.3667 | 0.4304 |
| 3.0000 | 231.0000 | Garang Kuol | FW | Pressing Forward | 50.1167 | 0.4046 |
| 4.0000 | 243.0000 | Mitchell Thomas Duke | FW | Target Forward / Penalty-Box Anchor | 272.2667 | 0.3993 |
| 5.0000 | 273.0000 | Mathew Leckie | AM | Target Forward | 341.6167 | 0.3716 |


## Belgium

- Total xT created: 1.4404
- Total xA created: 2.5562
- Pass completion under pressure: 0.7696
- Mean defensive hull area: 640.6988
- Mean defensive density: 0.0190

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 48.0000 | Kevin De Bruyne | AM | Progressive Winger | 284.2667 | 0.6319 |
| 2.0000 | 119.0000 | Michy Batshuayi Tunga | FW | Target Forward | 151.9000 | 0.5099 |
| 3.0000 | 136.0000 | Dries Mertens | AM | Target Forward | 80.5833 | 0.4926 |
| 4.0000 | 150.0000 | Romelu Lukaku Menama | FW | Target Forward / Penalty-Box Anchor | 63.5167 | 0.4797 |
| 5.0000 | 195.0000 | Thorgan Hazard | AM | Progressive Winger | 109.9500 | 0.4392 |


## Brazil

- Total xT created: 3.8085
- Total xA created: 6.8525
- Pass completion under pressure: 0.7291
- Mean defensive hull area: 579.4863
- Mean defensive density: 0.0211

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 9.0000 | Neymar da Silva Santos Junior | AM | Progressive Winger | 281.4833 | 0.7702 |
| 2.0000 | 14.0000 | Richarlison de Andrade | FW | Pressing Forward | 328.2500 | 0.7381 |
| 3.0000 | 27.0000 | Vinícius José Paixão de Oliveira Júnior | AM | Progressive Winger | 306.5833 | 0.6809 |
| 4.0000 | 34.0000 | Rodrygo Silva de Goes | AM | Progressive Winger | 199.3000 | 0.6664 |
| 5.0000 | 38.0000 | Raphael Dias Belloli | AM | Progressive Winger | 330.4500 | 0.6558 |


## Cameroon

- Total xT created: 1.0760
- Total xA created: 1.8107
- Pass completion under pressure: 0.6971
- Mean defensive hull area: 518.5576
- Mean defensive density: 0.0268

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 60.0000 | Vincent Paté Aboubakar | FW | Target Forward | 164.2333 | 0.6054 |
| 2.0000 | 124.0000 | Jean-Eric Maxim Choupo-Moting | FW | Target Forward | 269.9833 | 0.5058 |
| 3.0000 | 191.0000 | Jean-Charles Castelletto | CB | Sweeper CB | 192.4500 | 0.4406 |
| 4.0000 | 192.0000 | Karl Brillant Toko Ekambi | AM | Ball-Winner | 177.3833 | 0.4405 |
| 5.0000 | 220.0000 | André-Frank Zambo Anguissa | DM | Box-to-Box / Engine Midfielder | 276.6500 | 0.4139 |


## Canada

- Total xT created: 1.7913
- Total xA created: 2.0764
- Pass completion under pressure: 0.7118
- Mean defensive hull area: 569.4089
- Mean defensive density: 0.0243

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 61.0000 | Alistair Johnston | FB | Attacking Wingback | 284.9667 | 0.6040 |
| 2.0000 | 92.0000 | Tajon Buchanan | AM | Progressive Winger | 270.0833 | 0.5503 |
| 3.0000 | 95.0000 | Alphonso Davies | CM | Box-to-Box / Engine Midfielder | 284.9667 | 0.5472 |
| 4.0000 | 118.0000 | David Junior Hoilett | AM | Progressive Winger | 167.4000 | 0.5109 |
| 5.0000 | 142.0000 | Atiba Hutchinson | DM | Holding Anchor | 164.2000 | 0.4844 |


## Costa Rica

- Total xT created: 0.4184
- Total xA created: 0.4012
- Pass completion under pressure: 0.6509
- Mean defensive hull area: 510.3123
- Mean defensive density: 0.0278

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 292.0000 | Francisco Javier Calvo Quesada | CB | Sweeper CB | 194.4167 | 0.3606 |
| 2.0000 | 376.0000 | Kendall Jamaal Waston Manley | CB | Sweeper CB | 249.4500 | 0.3079 |
| 3.0000 | 382.0000 | Joel Nathaniel Campbell Samuels | FW | Progressive Winger | 292.4333 | 0.3049 |
| 4.0000 | 386.0000 | Yeltsin Ignacio Tejeda Valverde | CM | Holding Anchor | 286.9500 | 0.3033 |
| 5.0000 | 408.0000 | Youstin Delfin Salas Gómez | FB | Two-Way Fullback | 62.5667 | 0.2882 |


## Croatia

- Total xT created: 3.7160
- Total xA created: 5.6716
- Pass completion under pressure: 0.7430
- Mean defensive hull area: 480.9343
- Mean defensive density: 0.0281

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 8.0000 | Mateo Kovačić | CM | Deep Playmaker / Metronome | 649.9167 | 0.7730 |
| 2.0000 | 10.0000 | Luka Modrić | CM | Deep Playmaker / Metronome | 672.6667 | 0.7648 |
| 3.0000 | 28.0000 | Marko Livaja | FW | Target Forward | 255.5333 | 0.6802 |
| 4.0000 | 36.0000 | Ivan Perišić | AM | Wide Creator | 686.8167 | 0.6629 |
| 5.0000 | 37.0000 | Mislav Oršić | AM | Progressive Winger | 187.3167 | 0.6612 |


## Denmark

- Total xT created: 1.7188
- Total xA created: 2.1738
- Pass completion under pressure: 0.7086
- Mean defensive hull area: 439.0378
- Mean defensive density: 0.0278

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 54.0000 | Christian Dannemann Eriksen | CM | Progressive Winger | 290.8000 | 0.6217 |
| 2.0000 | 103.0000 | Andreas Christensen | CB | Ball-Playing Centre-Back | 290.8000 | 0.5346 |
| 3.0000 | 130.0000 | Andreas Evald Cornelius | FW | Target Forward / Penalty-Box Anchor | 104.8333 | 0.4978 |
| 4.0000 | 141.0000 | Kasper Dolberg | FW | Pressing Forward | 126.5000 | 0.4850 |
| 5.0000 | 145.0000 | Mathias Jensen | CM | Progressive Winger | 92.1167 | 0.4825 |


## Ecuador

- Total xT created: 1.0181
- Total xA created: 1.1631
- Pass completion under pressure: 0.6954
- Mean defensive hull area: 440.9376
- Mean defensive density: 0.0261

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 72.0000 | Pervis Josué Estupiñán Tenorio | FB | Attacking Wingback | 288.3833 | 0.5852 |
| 2.0000 | 83.0000 | Enner Remberto Valencia Lastra | AM | Target Forward | 261.9167 | 0.5623 |
| 3.0000 | 207.0000 | Angelo Smit Preciado Quiñónez | FB | Deep Playmaker | 276.2167 | 0.4287 |
| 4.0000 | 237.0000 | Gonzalo Jordy Plata Jiménez | CM | Box-to-Box / Engine Midfielder | 281.4000 | 0.4030 |
| 5.0000 | 244.0000 | Piero Martín Hincapié Reyna | CB | Sweeper CB | 288.3833 | 0.3979 |


## England

- Total xT created: 2.5219
- Total xA created: 4.8703
- Pass completion under pressure: 0.7556
- Mean defensive hull area: 482.2597
- Mean defensive density: 0.0278

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 7.0000 | Harry Kane | FW | Target Forward | 421.5167 | 0.7777 |
| 2.0000 | 32.0000 | Jude Bellingham | DM | Box-to-Box / Engine Midfielder | 441.7667 | 0.6702 |
| 3.0000 | 33.0000 | Bukayo Saka | AM | Progressive Winger | 291.3167 | 0.6691 |
| 4.0000 | 55.0000 | Phil Foden | AM | Ball-Winner | 275.5333 | 0.6206 |
| 5.0000 | 69.0000 | Harry Maguire | CB | Sweeper CB | 453.7167 | 0.5924 |


## France

- Total xT created: 3.9248
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 2.0000 | Kylian Mbappé Lottin | FW | Progressive Winger | 654.3000 | 0.9389 |
| 2.0000 | 11.0000 | Antoine Griezmann | AM | Hybrid Playmaker / Roaming Creator | 586.0500 | 0.7607 |
| 3.0000 | 13.0000 | Olivier Giroud | FW | Target Forward / Penalty-Box Anchor | 432.6167 | 0.7453 |
| 4.0000 | 22.0000 | Theo Bernard François Hernández | FB | Attacking Wingback | 548.5000 | 0.6969 |
| 5.0000 | 47.0000 | Ousmane Dembélé | AM | Progressive Winger | 448.0000 | 0.6323 |


## Germany

- Total xT created: 2.4318
- Total xA created: 6.0997
- Pass completion under pressure: 0.7731
- Mean defensive hull area: 489.2536
- Mean defensive density: 0.0243

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 16.0000 | Jamal Musiala | AM | Hybrid Playmaker / Roaming Creator | 274.0667 | 0.7310 |
| 2.0000 | 23.0000 | Serge Gnabry | AM | Progressive Winger | 273.3333 | 0.6948 |
| 3.0000 | 25.0000 | Kai Havertz | FW | Pressing Forward | 112.4167 | 0.6908 |
| 4.0000 | 26.0000 | Joshua Kimmich | FB | Attacking Wingback | 294.0000 | 0.6896 |
| 5.0000 | 31.0000 | Niclas Füllkrug | FW | Target Forward / Penalty-Box Anchor | 92.5833 | 0.6731 |


## Ghana

- Total xT created: 0.9360
- Total xA created: 0.9937
- Pass completion under pressure: 0.6763
- Mean defensive hull area: 432.5226
- Mean defensive density: 0.0269

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 183.0000 | Mohammed Kudus | AM | Progressive Winger | 254.9333 | 0.4450 |
| 2.0000 | 193.0000 | Thomas Teye Partey | DM | Holding Anchor | 301.2000 | 0.4401 |
| 3.0000 | 208.0000 | Osman Bukari | AM | Ball-Winner | 79.6167 | 0.4275 |
| 4.0000 | 211.0000 | Mohamed Salisu | CB | Sweeper CB | 301.2000 | 0.4224 |
| 5.0000 | 226.0000 | Jordan Ayew | AM | Progressive Winger | 146.5500 | 0.4121 |


## Iran

- Total xT created: 1.2461
- Total xA created: 2.6253
- Pass completion under pressure: 0.6687
- Mean defensive hull area: 460.4993
- Mean defensive density: 0.0330

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 6.0000 | Mehdi Taremi | FW | Target Forward | 305.1000 | 0.7779 |
| 2.0000 | 140.0000 | Ramin Rezaeian | FB | Attacking Wingback | 202.0167 | 0.4864 |
| 3.0000 | 161.0000 | Sardar Azmoun | FW | Target Forward | 138.6833 | 0.4699 |
| 4.0000 | 230.0000 | Saman Ghoddos | AM | Target Forward | 54.8833 | 0.4050 |
| 5.0000 | 256.0000 | Mehdi Torabi | CM | Ball-Winner | 95.8667 | 0.3870 |


## Japan

- Total xT created: 1.5415
- Total xA created: 2.4186
- Pass completion under pressure: 0.6415
- Mean defensive hull area: 501.4214
- Mean defensive density: 0.0229

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 21.0000 | Takuma Asano | FW | Target Forward | 186.3500 | 0.6976 |
| 2.0000 | 134.0000 | Wataru Endo | DM | Box-to-Box / Engine Midfielder | 326.0167 | 0.4946 |
| 3.0000 | 144.0000 | Kaoru Mitoma | FB | Attacking Wingback | 186.1167 | 0.4830 |
| 4.0000 | 152.0000 | Ritsu Doan | AM | Progressive Winger | 231.8667 | 0.4792 |
| 5.0000 | 190.0000 | Daizen Maeda | FW | Target Forward | 181.1667 | 0.4408 |


## Mexico

- Total xT created: 1.3586
- Total xA created: 2.6085
- Pass completion under pressure: 0.6241
- Mean defensive hull area: 639.3089
- Mean defensive density: 0.0298

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 56.0000 | Hirving Rodrigo Lozano Bahena | AM | Progressive Winger | 267.3167 | 0.6197 |
| 2.0000 | 64.0000 | Henry Josué Martín Mex | FW | Target Forward | 146.7667 | 0.5960 |
| 3.0000 | 155.0000 | Luis Gerardo Chávez Magallón | DM | Holding / Controlling Midfielder | 291.5000 | 0.4776 |
| 4.0000 | 212.0000 | Edson Omar Álvarez Velázquez | DM | Box-to-Box / Engine Midfielder | 183.2333 | 0.4224 |
| 5.0000 | 214.0000 | Orbelín Pineda Alvarado | AM | Pressing Attacker | 76.3833 | 0.4220 |


## Morocco

- Total xT created: 2.4078
- Total xA created: 3.2076
- Pass completion under pressure: 0.6771
- Mean defensive hull area: 518.2011
- Mean defensive density: 0.0225

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 30.0000 | Hakim Ziyech | AM | Deep Playmaker | 662.6333 | 0.6748 |
| 2.0000 | 82.0000 | Achraf Hakimi Mouh | FB | Attacking Wingback | 660.8000 | 0.5656 |
| 3.0000 | 96.0000 | Sofiane Boufal | AM | Progressive Winger | 476.6667 | 0.5447 |
| 4.0000 | 117.0000 | Zakaria Aboukhlal | FW | Wide Creator | 100.6667 | 0.5120 |
| 5.0000 | 138.0000 | Azzedine Ounahi | CM | Box-to-Box / Engine Midfielder | 589.2500 | 0.4871 |


## Netherlands

- Total xT created: 2.0451
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 18.0000 | Memphis Depay | FW | Target Forward | 315.5833 | 0.7234 |
| 2.0000 | 29.0000 | Cody Mathès Gakpo | AM | Progressive Winger | 460.2167 | 0.6788 |
| 3.0000 | 44.0000 | Frenkie de Jong | DM | Holding Anchor | 499.4500 | 0.6481 |
| 4.0000 | 62.0000 | Wout Weghorst | FW | Target Forward / Penalty-Box Anchor | 77.5000 | 0.5979 |
| 5.0000 | 77.0000 | Luuk de Jong | FW | Target Forward / Penalty-Box Anchor | 57.0333 | 0.5763 |


## Poland

- Total xT created: 1.1292
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 4.0000 | Robert Lewandowski | FW | Target Forward / Penalty-Box Anchor | 389.7500 | 0.8227 |
| 2.0000 | 58.0000 | Piotr Zieliński | CM | Holding Anchor | 344.4167 | 0.6136 |
| 3.0000 | 247.0000 | Krystian Bielik | DM | Holding Anchor | 240.0167 | 0.3935 |
| 4.0000 | 321.0000 | Jakub Kamiński | AM | Progressive Winger | 253.6333 | 0.3461 |
| 5.0000 | 323.0000 | Karol Świderski | FW | Pressing Forward | 45.0000 | 0.3458 |


## Portugal

- Total xT created: 2.6573
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 3.0000 | Bruno Miguel Borges Fernandes | AM | Progressive Winger | 384.9500 | 0.8365 |
| 2.0000 | 17.0000 | Gonçalo Matias Ramos | FW | Target Forward | 171.8833 | 0.7308 |
| 3.0000 | 24.0000 | Cristiano Ronaldo dos Santos Aveiro | FW | Target Forward | 302.8000 | 0.6923 |
| 4.0000 | 70.0000 | João Félix Sequeira | AM | Ball-Winner | 340.2333 | 0.5924 |
| 5.0000 | 71.0000 | Bernardo Mota Veiga de Carvalho e Silva | CM | Ball-Winner | 382.1000 | 0.5894 |


## Qatar

- Total xT created: 0.7960
- Total xA created: 1.1791
- Pass completion under pressure: 0.6995
- Mean defensive hull area: 451.6214
- Mean defensive density: 0.0529

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 127.0000 | Mohammed Muntari | FW | Target Forward / Penalty-Box Anchor | 77.7500 | 0.5019 |
| 2.0000 | 169.0000 | Abdelkarim Hassan Al Haj Fadlalla | CB | Ball-Playing Centre-Back | 287.4000 | 0.4625 |
| 3.0000 | 203.0000 | Boualem Khoukhi | CB | Sweeper CB | 287.4000 | 0.4312 |
| 4.0000 | 288.0000 | Akram Hassan Afif | FW | Progressive Winger | 287.4000 | 0.3632 |
| 5.0000 | 332.0000 | Bassam Hisham Al Rawi | CB | Sweeper CB | 95.3167 | 0.3369 |


## Saudi Arabia

- Total xT created: 1.0502
- Total xA created: 1.2324
- Pass completion under pressure: 0.6235
- Mean defensive hull area: 480.3764
- Mean defensive density: 0.0271

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 15.0000 | Salem Mohammed Al Dawsari | AM | Progressive Winger | 298.5500 | 0.7362 |
| 2.0000 | 174.0000 | Saleh Khalid Al Shehri | FW | Target Forward | 223.4000 | 0.4596 |
| 3.0000 | 228.0000 | Sami Khalil Al Naji | AM | Progressive Winger | 45.0000 | 0.4058 |
| 4.0000 | 234.0000 | Saud Abdullah Abdul Hamid | FB | Attacking Wingback | 298.5500 | 0.4038 |
| 5.0000 | 238.0000 | Mohammed Al Burayk | FB | Attacking Wingback | 69.9833 | 0.4011 |


## Senegal

- Total xT created: 1.6919
- Total xA created: 2.0598
- Pass completion under pressure: 0.6875
- Mean defensive hull area: 550.7399
- Mean defensive density: 0.0216

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 57.0000 | Ismaïla Sarr | AM | Progressive Winger | 365.2000 | 0.6180 |
| 2.0000 | 116.0000 | Youssouf Sabaly | FB | Attacking Wingback | 387.2833 | 0.5127 |
| 3.0000 | 137.0000 | Kalidou Koulibaly | CB | Sweeper CB | 387.2833 | 0.4896 |
| 4.0000 | 146.0000 | Cheikh Ahmadou Bamba Mbacke Dieng | FW | Target Forward | 126.2500 | 0.4823 |
| 5.0000 | 166.0000 | Krépin Diatta | AM | Progressive Winger | 181.9167 | 0.4647 |


## Serbia

- Total xT created: 1.3908
- Total xA created: 2.0346
- Pass completion under pressure: 0.6740
- Mean defensive hull area: 611.0415
- Mean defensive density: 0.0224

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 42.0000 | Aleksandar Mitrović | FW | Target Forward | 279.4167 | 0.6498 |
| 2.0000 | 81.0000 | Dušan Tadić | AM | Progressive Winger | 270.9333 | 0.5684 |
| 3.0000 | 154.0000 | Dušan Vlahović | FW | Target Forward / Penalty-Box Anchor | 86.0667 | 0.4779 |
| 4.0000 | 168.0000 | Andrija Živković | FB | Attacking Wingback | 212.0833 | 0.4628 |
| 5.0000 | 172.0000 | Strahinja Pavlović | CB | Ball-Playing Centre-Back | 252.8500 | 0.4609 |


## South Korea

- Total xT created: 1.8015
- Total xA created: 2.3972
- Pass completion under pressure: 0.6712
- Mean defensive hull area: 410.9954
- Mean defensive density: 0.0297

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 89.0000 | Kang-In Lee | CM | Deep Playmaker / Metronome | 170.0500 | 0.5551 |
| 2.0000 | 112.0000 | Hee-Chan Hwang | AM | Progressive Winger | 125.5667 | 0.5156 |
| 3.0000 | 120.0000 | Gue-Sung Cho | FW | Target Forward / Penalty-Box Anchor | 297.4167 | 0.5090 |
| 4.0000 | 179.0000 | Heung-Min Son | AM | Target Forward | 389.6500 | 0.4499 |
| 5.0000 | 186.0000 | Moon-Hwan Kim | FB | Attacking Wingback | 389.6500 | 0.4431 |


## Spain

- Total xT created: 2.5669
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 19.0000 | Álvaro Borja Morata Martín | FW | Target Forward | 200.8333 | 0.7100 |
| 2.0000 | 35.0000 | Pedro González López | CM | Holding Anchor | 372.4000 | 0.6630 |
| 3.0000 | 40.0000 | Rodrigo Hernández Cascante | CB | Ball-Playing Centre-Back | 413.9500 | 0.6520 |
| 4.0000 | 41.0000 | Daniel Olmo Carvajal | AM | Progressive Winger | 388.2500 | 0.6512 |
| 5.0000 | 50.0000 | Marco Asensio Willemsen | FW | Progressive Winger | 236.9667 | 0.6280 |


## Switzerland

- Total xT created: 1.4531
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 46.0000 | Breel-Donald Embolo | FW | Pressing Forward | 330.1500 | 0.6327 |
| 2.0000 | 76.0000 | Xherdan Shaqiri | AM | Progressive Winger | 233.5833 | 0.5804 |
| 3.0000 | 111.0000 | Manuel Obafemi Akanji | CB | Ball-Playing Centre-Back | 386.5833 | 0.5216 |
| 4.0000 | 135.0000 | Ruben Vargas | AM | Progressive Winger | 286.9500 | 0.4945 |
| 5.0000 | 181.0000 | Silvan Widmer | FB | Attacking Wingback | 281.8500 | 0.4494 |


## Tunisia

- Total xT created: 1.2810
- Total xA created: 1.9897
- Pass completion under pressure: 0.5839
- Mean defensive hull area: 396.7358
- Mean defensive density: 0.0421

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 68.0000 | Youssef Msakni | AM | Progressive Winger | 176.0667 | 0.5934 |
| 2.0000 | 108.0000 | Wahbi Khazri | FW | Progressive Winger | 88.5667 | 0.5244 |
| 3.0000 | 158.0000 | Aïssa Bilal Laïdouni | DM | Box-to-Box / Engine Midfielder | 257.2333 | 0.4754 |
| 4.0000 | 175.0000 | Issam Jebali | FW | Pressing Forward | 196.3500 | 0.4585 |
| 5.0000 | 177.0000 | Naïm Sliti | AM | Progressive Winger | 127.1667 | 0.4514 |


## United States

- Total xT created: 2.0784
- Total xA created: 3.2488
- Pass completion under pressure: 0.7900
- Mean defensive hull area: 451.8615
- Mean defensive density: 0.0339

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 5.0000 | Christian Pulisic | AM | Progressive Winger | 336.3167 | 0.7847 |
| 2.0000 | 79.0000 | Haji Wright | FW | Target Forward / Penalty-Box Anchor | 161.8833 | 0.5716 |
| 3.0000 | 80.0000 | Yunus Dimoara Musah | CM | Box-to-Box / Engine Midfielder | 364.8667 | 0.5715 |
| 4.0000 | 90.0000 | Weston McKennie | CM | Deep Playmaker / Metronome | 273.5500 | 0.5548 |
| 5.0000 | 105.0000 | Tyler Adams | DM | Holding / Controlling Midfielder | 391.2000 | 0.5329 |


## Uruguay

- Total xT created: 1.4720
- Total xA created: 1.9893
- Pass completion under pressure: 0.6460
- Mean defensive hull area: 457.0204
- Mean defensive density: 0.0260

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 52.0000 | Rodrigo Bentancur Colmán | DM | Box-to-Box / Engine Midfielder | 231.6667 | 0.6246 |
| 2.0000 | 66.0000 | Giorgian Daniel De Arrascaeta Benedetti | AM | Progressive Winger | 118.1000 | 0.5948 |
| 3.0000 | 91.0000 | Federico Santiago Valverde Dipetta | DM | Holding Anchor | 298.0833 | 0.5543 |
| 4.0000 | 102.0000 | Mathías Olivera Miramontes | FB | Wide Creator | 263.6333 | 0.5353 |
| 5.0000 | 125.0000 | José María Giménez de Vargas | CB | Sweeper CB | 298.0833 | 0.5047 |


## Wales

- Total xT created: 0.8960
- Total xA created: 1.2536
- Pass completion under pressure: 0.6856
- Mean defensive hull area: 599.2348
- Mean defensive density: 0.0252

### Top five outfield-player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1.0000 | 114.0000 | Gareth Frank Bale | FW | Target Forward | 247.7167 | 0.5128 |
| 2.0000 | 162.0000 | Kieffer Roberto Francisco Moore | FW | Target Forward / Penalty-Box Anchor | 251.7167 | 0.4696 |
| 3.0000 | 222.0000 | Chris Mepham | CB | Sweeper CB | 296.7167 | 0.4135 |
| 4.0000 | 271.0000 | Harry Wilson | CM | Wide Creator | 167.2333 | 0.3733 |
| 5.0000 | 291.0000 | Neco Williams | FB | Wide Creator | 216.3833 | 0.3611 |


## Interpretation boundary

These rankings summarize performance in the 2022 tournament sample. They are not transfer valuations, causal estimates, medical assessments, or replacements for video and scouting review.
