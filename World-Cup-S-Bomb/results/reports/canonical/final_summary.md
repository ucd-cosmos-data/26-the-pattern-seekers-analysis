# 2022 FIFA World Cup Player Ranking Report

## Executive summary

This report consolidates **32 national teams** and **593 eligible rated players** (outfield 45+ minutes; goalkeepers 90+). It uses StatsBomb events, lineups, minutes, and coverage-qualified 360 freeze frames. It does not use optical tracking, external ratings, or player-name adjustments.

The position-aware tournament rankings are stored under `results/reports/ranking/`. They add formal 360 groups while preserving the source position and role detail.

## Global top 10 outfield players — tournament ranking v2

| Global Rank V2 | Player Name | Team | Position Group 360 | Functional Role | Final Player Rating V2 |
|---|---|---|---|---|---|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | AM | Progressive Winger | 1.0000 |
| 2 | Kylian Mbappé Lottin | France | FW | Progressive Winger | 0.9389 |
| 3 | Bruno Miguel Borges Fernandes | Portugal | AM | Progressive Winger | 0.8365 |
| 4 | Robert Lewandowski | Poland | FW | Target Forward / Penalty-Box Anchor | 0.8227 |
| 5 | Christian Pulisic | United States | AM | Progressive Winger | 0.7847 |
| 6 | Mehdi Taremi | Iran | FW | Target Forward | 0.7779 |
| 7 | Harry Kane | England | FW | Target Forward | 0.7777 |
| 8 | Mateo Kovačić | Croatia | CM | Deep Playmaker / Metronome | 0.7730 |
| 9 | Neymar da Silva Santos Junior | Brazil | AM | Progressive Winger | 0.7702 |
| 10 | Luka Modrić | Croatia | CM | Deep Playmaker / Metronome | 0.7648 |

## Global top five goalkeepers — tournament ranking v2

| Gk Rank V2 | Player Name | Team | Gk Rating V2 |
|---|---|---|---|
| 1 | Wojciech Szczęsny | Poland | 1.0000 |
| 2 | Dominik Livaković | Croatia | 0.8915 |
| 3 | Yassine Bounou | Morocco | 0.7854 |
| 4 | Thibaut Courtois | Belgium | 0.6513 |
| 5 | Sergio Rochet Álvarez | Uruguay | 0.5813 |

The active contribution layer is `role_aware_fallback`. The experimental attention challenger remains available but affects rankings only when it passes its match-disjoint metric gate.

## How to read the player rating

The preserved V5 contribution score uses the development-gated baseline VAEP feature set and grouped ElasticNet offense/defense heads with explicit role weights, VAEP/touch, open-play and set-piece-aware xT, sample-adjusted completeness, coverage-qualified off-ball value, and xD-style defensive disruption. Positive ElasticNet calibration selects the composite weights with team-disjoint folds, followed by minutes/(minutes+450) position-prior shrinkage.

The tournament ranking v2 adds explicit goals, xG, shots, xA, chance creation, progression, possession, defending, and off-ball components normalized within `position_group_360`. A capped, general role-based finishing treatment corrects the structural penalty on goal-centric forwards; it never checks player names.

Goalkeepers use a separate weighted seven-component matrix and ranking, including high-leverage saves. They are excluded from the outfield global ranking because StatsBomb Open Data does not contain native post-shot xG. Missing 360 evidence remains missing, and role labels never award rating points.

## General player summary

### Overall leaders

| Global Rank V2 | Player Name | Team | Position Group 360 | Functional Role | Final Player Rating V2 |
|---|---|---|---|---|---|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | AM | Progressive Winger | 1.0000 |
| 2 | Kylian Mbappé Lottin | France | FW | Progressive Winger | 0.9389 |
| 3 | Bruno Miguel Borges Fernandes | Portugal | AM | Progressive Winger | 0.8365 |
| 4 | Robert Lewandowski | Poland | FW | Target Forward / Penalty-Box Anchor | 0.8227 |
| 5 | Christian Pulisic | United States | AM | Progressive Winger | 0.7847 |
| 6 | Mehdi Taremi | Iran | FW | Target Forward | 0.7779 |
| 7 | Harry Kane | England | FW | Target Forward | 0.7777 |
| 8 | Mateo Kovačić | Croatia | CM | Deep Playmaker / Metronome | 0.7730 |
| 10 | Luka Modrić | Croatia | CM | Deep Playmaker / Metronome | 0.7648 |
| 11 | Antoine Griezmann | France | AM | Hybrid Playmaker / Roaming Creator | 0.7607 |
| 12 | Ángel Fabián Di María Hernández | Argentina | AM | Progressive Winger | 0.7554 |
| 13 | Olivier Giroud | France | FW | Target Forward / Penalty-Box Anchor | 0.7453 |
| 14 | Richarlison de Andrade | Brazil | FW | Pressing Forward | 0.7381 |
| 18 | Memphis Depay | Netherlands | FW | Target Forward | 0.7234 |
| 20 | Julián Álvarez | Argentina | FW | Pressing Forward | 0.7086 |
| 22 | Theo Bernard François Hernández | France | FB | Attacking Wingback | 0.6969 |
| 24 | Cristiano Ronaldo dos Santos Aveiro | Portugal | FW | Target Forward | 0.6923 |
| 27 | Vinícius José Paixão de Oliveira Júnior | Brazil | AM | Progressive Winger | 0.6809 |
| 29 | Cody Mathès Gakpo | Netherlands | AM | Progressive Winger | 0.6788 |
| 30 | Hakim Ziyech | Morocco | AM | Deep Playmaker | 0.6748 |

### Position-group leaders

| Position Group 360 | Position Rank V2 | Player Name | Team | Functional Role | Final Player Rating V2 |
|---|---|---|---|---|---|
| AM | 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 1.0000 |
| AM | 2 | Bruno Miguel Borges Fernandes | Portugal | Progressive Winger | 0.8365 |
| AM | 3 | Christian Pulisic | United States | Progressive Winger | 0.7847 |
| AM | 4 | Neymar da Silva Santos Junior | Brazil | Progressive Winger | 0.7702 |
| AM | 5 | Antoine Griezmann | France | Hybrid Playmaker / Roaming Creator | 0.7607 |
| CB | 1 | Rodrigo Hernández Cascante | Spain | Ball-Playing Centre-Back | 0.6520 |
| CB | 2 | Ibrahima Konaté | France | Ball-Playing Centre-Back | 0.6300 |
| CB | 3 | Joško Gvardiol | Croatia | Ball-Playing Centre-Back | 0.6128 |
| CB | 4 | Harry Maguire | England | Sweeper CB | 0.5924 |
| CB | 5 | Thiago Emiliano da Silva | Brazil | Ball-Playing Centre-Back | 0.5571 |
| CM | 1 | Mateo Kovačić | Croatia | Deep Playmaker / Metronome | 0.7730 |
| CM | 2 | Luka Modrić | Croatia | Deep Playmaker / Metronome | 0.7648 |
| CM | 3 | Pedro González López | Spain | Holding Anchor | 0.6630 |
| CM | 4 | Alexis Mac Allister | Argentina | Ball-Winner | 0.6482 |
| CM | 5 | Christian Dannemann Eriksen | Denmark | Progressive Winger | 0.6217 |
| DM | 1 | Jude Bellingham | England | Box-to-Box / Engine Midfielder | 0.6702 |
| DM | 2 | Frenkie de Jong | Netherlands | Holding Anchor | 0.6481 |
| DM | 3 | Rodrigo Bentancur Colmán | Uruguay | Box-to-Box / Engine Midfielder | 0.6246 |
| DM | 4 | Enzo Fernandez | Argentina | Holding Anchor | 0.5957 |
| DM | 5 | Rodrigo Javier De Paul | Argentina | Deep Playmaker | 0.5941 |
| FB | 1 | Theo Bernard François Hernández | France | Attacking Wingback | 0.6969 |
| FB | 2 | Joshua Kimmich | Germany | Attacking Wingback | 0.6896 |
| FB | 3 | David Raum | Germany | Attacking Wingback | 0.6543 |
| FB | 4 | Jordi Alba Ramos | Spain | Attacking Wingback | 0.6251 |
| FB | 5 | Alistair Johnston | Canada | Attacking Wingback | 0.6040 |
| FW | 1 | Kylian Mbappé Lottin | France | Progressive Winger | 0.9389 |
| FW | 2 | Robert Lewandowski | Poland | Target Forward / Penalty-Box Anchor | 0.8227 |
| FW | 3 | Mehdi Taremi | Iran | Target Forward | 0.7779 |
| FW | 4 | Harry Kane | England | Target Forward | 0.7777 |
| FW | 5 | Olivier Giroud | France | Target Forward / Penalty-Box Anchor | 0.7453 |

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

## Argentina

- Total xT created: 4.0073
- Total xA created: 6.7228
- Pass completion under pressure: 0.7447
- Mean defensive hull area: 647.6227
- Mean defensive density: 0.0258

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 1 | Lionel Andrés Messi Cuccittini | AM | Progressive Winger | 733.9000 | 1.0000 |
| 2 | 12 | Ángel Fabián Di María Hernández | AM | Progressive Winger | 304.8167 | 0.7554 |
| 3 | 20 | Julián Álvarez | FW | Pressing Forward | 485.2333 | 0.7086 |
| 4 | 43 | Alexis Mac Allister | CM | Ball-Winner | 552.3500 | 0.6482 |
| 5 | 63 | Lautaro Javier Martínez | FW | Target Forward / Penalty-Box Anchor | 273.0000 | 0.5979 |


## Australia

- Total xT created: 1.1032
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 128 | Craig Goodwin | AM | Wide Creator | 241.7000 | 0.5007 |
| 2 | 206 | Fran Karačić | FB | Attacking Wingback | 100.3667 | 0.4304 |
| 3 | 231 | Garang Kuol | FW | Pressing Forward | 50.1167 | 0.4046 |
| 4 | 243 | Mitchell Thomas Duke | FW | Target Forward / Penalty-Box Anchor | 272.2667 | 0.3993 |
| 5 | 273 | Mathew Leckie | AM | Target Forward | 341.6167 | 0.3716 |


## Belgium

- Total xT created: 1.4404
- Total xA created: 2.5562
- Pass completion under pressure: 0.7696
- Mean defensive hull area: 640.6988
- Mean defensive density: 0.0190

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 48 | Kevin De Bruyne | AM | Progressive Winger | 284.2667 | 0.6319 |
| 2 | 119 | Michy Batshuayi Tunga | FW | Target Forward | 151.9000 | 0.5099 |
| 3 | 136 | Dries Mertens | AM | Target Forward | 80.5833 | 0.4926 |
| 4 | 150 | Romelu Lukaku Menama | FW | Target Forward / Penalty-Box Anchor | 63.5167 | 0.4797 |
| 5 | 195 | Thorgan Hazard | AM | Progressive Winger | 109.9500 | 0.4392 |


## Brazil

- Total xT created: 3.8085
- Total xA created: 6.8525
- Pass completion under pressure: 0.7291
- Mean defensive hull area: 579.4863
- Mean defensive density: 0.0211

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 9 | Neymar da Silva Santos Junior | AM | Progressive Winger | 281.4833 | 0.7702 |
| 2 | 14 | Richarlison de Andrade | FW | Pressing Forward | 328.2500 | 0.7381 |
| 3 | 27 | Vinícius José Paixão de Oliveira Júnior | AM | Progressive Winger | 306.5833 | 0.6809 |
| 4 | 34 | Rodrygo Silva de Goes | AM | Progressive Winger | 199.3000 | 0.6664 |
| 5 | 38 | Raphael Dias Belloli | AM | Progressive Winger | 330.4500 | 0.6558 |


## Cameroon

- Total xT created: 1.0760
- Total xA created: 1.8107
- Pass completion under pressure: 0.6971
- Mean defensive hull area: 518.5576
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 60 | Vincent Paté Aboubakar | FW | Target Forward | 164.2333 | 0.6054 |
| 2 | 124 | Jean-Eric Maxim Choupo-Moting | FW | Target Forward | 269.9833 | 0.5058 |
| 3 | 191 | Jean-Charles Castelletto | CB | Sweeper CB | 192.4500 | 0.4406 |
| 4 | 192 | Karl Brillant Toko Ekambi | AM | Ball-Winner | 177.3833 | 0.4405 |
| 5 | 220 | André-Frank Zambo Anguissa | DM | Box-to-Box / Engine Midfielder | 276.6500 | 0.4139 |


## Canada

- Total xT created: 1.7913
- Total xA created: 2.0764
- Pass completion under pressure: 0.7118
- Mean defensive hull area: 569.4089
- Mean defensive density: 0.0243

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 61 | Alistair Johnston | FB | Attacking Wingback | 284.9667 | 0.6040 |
| 2 | 92 | Tajon Buchanan | AM | Progressive Winger | 270.0833 | 0.5503 |
| 3 | 95 | Alphonso Davies | CM | Box-to-Box / Engine Midfielder | 284.9667 | 0.5472 |
| 4 | 118 | David Junior Hoilett | AM | Progressive Winger | 167.4000 | 0.5109 |
| 5 | 142 | Atiba Hutchinson | DM | Holding Anchor | 164.2000 | 0.4844 |


## Costa Rica

- Total xT created: 0.4184
- Total xA created: 0.4012
- Pass completion under pressure: 0.6509
- Mean defensive hull area: 510.3123
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 292 | Francisco Javier Calvo Quesada | CB | Sweeper CB | 194.4167 | 0.3606 |
| 2 | 376 | Kendall Jamaal Waston Manley | CB | Sweeper CB | 249.4500 | 0.3079 |
| 3 | 382 | Joel Nathaniel Campbell Samuels | FW | Progressive Winger | 292.4333 | 0.3049 |
| 4 | 386 | Yeltsin Ignacio Tejeda Valverde | CM | Holding Anchor | 286.9500 | 0.3033 |
| 5 | 408 | Youstin Delfin Salas Gómez | FB | Two-Way Fullback | 62.5667 | 0.2882 |


## Croatia

- Total xT created: 3.7160
- Total xA created: 5.6716
- Pass completion under pressure: 0.7430
- Mean defensive hull area: 480.9343
- Mean defensive density: 0.0281

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 8 | Mateo Kovačić | CM | Deep Playmaker / Metronome | 649.9167 | 0.7730 |
| 2 | 10 | Luka Modrić | CM | Deep Playmaker / Metronome | 672.6667 | 0.7648 |
| 3 | 28 | Marko Livaja | FW | Target Forward | 255.5333 | 0.6802 |
| 4 | 36 | Ivan Perišić | AM | Wide Creator | 686.8167 | 0.6629 |
| 5 | 37 | Mislav Oršić | AM | Progressive Winger | 187.3167 | 0.6612 |


## Denmark

- Total xT created: 1.7188
- Total xA created: 2.1738
- Pass completion under pressure: 0.7086
- Mean defensive hull area: 439.0378
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 54 | Christian Dannemann Eriksen | CM | Progressive Winger | 290.8000 | 0.6217 |
| 2 | 103 | Andreas Christensen | CB | Ball-Playing Centre-Back | 290.8000 | 0.5346 |
| 3 | 130 | Andreas Evald Cornelius | FW | Target Forward / Penalty-Box Anchor | 104.8333 | 0.4978 |
| 4 | 141 | Kasper Dolberg | FW | Pressing Forward | 126.5000 | 0.4850 |
| 5 | 145 | Mathias Jensen | CM | Progressive Winger | 92.1167 | 0.4825 |


## Ecuador

- Total xT created: 1.0181
- Total xA created: 1.1631
- Pass completion under pressure: 0.6954
- Mean defensive hull area: 440.9376
- Mean defensive density: 0.0261

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 72 | Pervis Josué Estupiñán Tenorio | FB | Attacking Wingback | 288.3833 | 0.5852 |
| 2 | 83 | Enner Remberto Valencia Lastra | AM | Target Forward | 261.9167 | 0.5623 |
| 3 | 207 | Angelo Smit Preciado Quiñónez | FB | Deep Playmaker | 276.2167 | 0.4287 |
| 4 | 237 | Gonzalo Jordy Plata Jiménez | CM | Box-to-Box / Engine Midfielder | 281.4000 | 0.4030 |
| 5 | 244 | Piero Martín Hincapié Reyna | CB | Sweeper CB | 288.3833 | 0.3979 |


## England

- Total xT created: 2.5219
- Total xA created: 4.8703
- Pass completion under pressure: 0.7556
- Mean defensive hull area: 482.2597
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 7 | Harry Kane | FW | Target Forward | 421.5167 | 0.7777 |
| 2 | 32 | Jude Bellingham | DM | Box-to-Box / Engine Midfielder | 441.7667 | 0.6702 |
| 3 | 33 | Bukayo Saka | AM | Progressive Winger | 291.3167 | 0.6691 |
| 4 | 55 | Phil Foden | AM | Ball-Winner | 275.5333 | 0.6206 |
| 5 | 69 | Harry Maguire | CB | Sweeper CB | 453.7167 | 0.5924 |


## France

- Total xT created: 3.9248
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 2 | Kylian Mbappé Lottin | FW | Progressive Winger | 654.3000 | 0.9389 |
| 2 | 11 | Antoine Griezmann | AM | Hybrid Playmaker / Roaming Creator | 586.0500 | 0.7607 |
| 3 | 13 | Olivier Giroud | FW | Target Forward / Penalty-Box Anchor | 432.6167 | 0.7453 |
| 4 | 22 | Theo Bernard François Hernández | FB | Attacking Wingback | 548.5000 | 0.6969 |
| 5 | 47 | Ousmane Dembélé | AM | Progressive Winger | 448.0000 | 0.6323 |


## Germany

- Total xT created: 2.4318
- Total xA created: 6.0997
- Pass completion under pressure: 0.7731
- Mean defensive hull area: 489.2536
- Mean defensive density: 0.0243

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 16 | Jamal Musiala | AM | Hybrid Playmaker / Roaming Creator | 274.0667 | 0.7310 |
| 2 | 23 | Serge Gnabry | AM | Progressive Winger | 273.3333 | 0.6948 |
| 3 | 25 | Kai Havertz | FW | Pressing Forward | 112.4167 | 0.6908 |
| 4 | 26 | Joshua Kimmich | FB | Attacking Wingback | 294.0000 | 0.6896 |
| 5 | 31 | Niclas Füllkrug | FW | Target Forward / Penalty-Box Anchor | 92.5833 | 0.6731 |


## Ghana

- Total xT created: 0.9360
- Total xA created: 0.9937
- Pass completion under pressure: 0.6763
- Mean defensive hull area: 432.5226
- Mean defensive density: 0.0269

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 183 | Mohammed Kudus | AM | Progressive Winger | 254.9333 | 0.4450 |
| 2 | 193 | Thomas Teye Partey | DM | Holding Anchor | 301.2000 | 0.4401 |
| 3 | 208 | Osman Bukari | AM | Ball-Winner | 79.6167 | 0.4275 |
| 4 | 211 | Mohamed Salisu | CB | Sweeper CB | 301.2000 | 0.4224 |
| 5 | 226 | Jordan Ayew | AM | Progressive Winger | 146.5500 | 0.4121 |


## Iran

- Total xT created: 1.2461
- Total xA created: 2.6253
- Pass completion under pressure: 0.6687
- Mean defensive hull area: 460.4993
- Mean defensive density: 0.0330

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 6 | Mehdi Taremi | FW | Target Forward | 305.1000 | 0.7779 |
| 2 | 140 | Ramin Rezaeian | FB | Attacking Wingback | 202.0167 | 0.4864 |
| 3 | 161 | Sardar Azmoun | FW | Target Forward | 138.6833 | 0.4699 |
| 4 | 230 | Saman Ghoddos | AM | Target Forward | 54.8833 | 0.4050 |
| 5 | 256 | Mehdi Torabi | CM | Ball-Winner | 95.8667 | 0.3870 |


## Japan

- Total xT created: 1.5415
- Total xA created: 2.4186
- Pass completion under pressure: 0.6415
- Mean defensive hull area: 501.4214
- Mean defensive density: 0.0229

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 21 | Takuma Asano | FW | Target Forward | 186.3500 | 0.6976 |
| 2 | 134 | Wataru Endo | DM | Box-to-Box / Engine Midfielder | 326.0167 | 0.4946 |
| 3 | 144 | Kaoru Mitoma | FB | Attacking Wingback | 186.1167 | 0.4830 |
| 4 | 152 | Ritsu Doan | AM | Progressive Winger | 231.8667 | 0.4792 |
| 5 | 190 | Daizen Maeda | FW | Target Forward | 181.1667 | 0.4408 |


## Mexico

- Total xT created: 1.3586
- Total xA created: 2.6085
- Pass completion under pressure: 0.6241
- Mean defensive hull area: 639.3089
- Mean defensive density: 0.0298

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 56 | Hirving Rodrigo Lozano Bahena | AM | Progressive Winger | 267.3167 | 0.6197 |
| 2 | 64 | Henry Josué Martín Mex | FW | Target Forward | 146.7667 | 0.5960 |
| 3 | 155 | Luis Gerardo Chávez Magallón | DM | Holding / Controlling Midfielder | 291.5000 | 0.4776 |
| 4 | 212 | Edson Omar Álvarez Velázquez | DM | Box-to-Box / Engine Midfielder | 183.2333 | 0.4224 |
| 5 | 214 | Orbelín Pineda Alvarado | AM | Pressing Attacker | 76.3833 | 0.4220 |


## Morocco

- Total xT created: 2.4078
- Total xA created: 3.2076
- Pass completion under pressure: 0.6771
- Mean defensive hull area: 518.2011
- Mean defensive density: 0.0225

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 30 | Hakim Ziyech | AM | Deep Playmaker | 662.6333 | 0.6748 |
| 2 | 82 | Achraf Hakimi Mouh | FB | Attacking Wingback | 660.8000 | 0.5656 |
| 3 | 96 | Sofiane Boufal | AM | Progressive Winger | 476.6667 | 0.5447 |
| 4 | 117 | Zakaria Aboukhlal | FW | Wide Creator | 100.6667 | 0.5120 |
| 5 | 138 | Azzedine Ounahi | CM | Box-to-Box / Engine Midfielder | 589.2500 | 0.4871 |


## Netherlands

- Total xT created: 2.0451
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 18 | Memphis Depay | FW | Target Forward | 315.5833 | 0.7234 |
| 2 | 29 | Cody Mathès Gakpo | AM | Progressive Winger | 460.2167 | 0.6788 |
| 3 | 44 | Frenkie de Jong | DM | Holding Anchor | 499.4500 | 0.6481 |
| 4 | 62 | Wout Weghorst | FW | Target Forward / Penalty-Box Anchor | 77.5000 | 0.5979 |
| 5 | 77 | Luuk de Jong | FW | Target Forward / Penalty-Box Anchor | 57.0333 | 0.5763 |


## Poland

- Total xT created: 1.1292
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 4 | Robert Lewandowski | FW | Target Forward / Penalty-Box Anchor | 389.7500 | 0.8227 |
| 2 | 58 | Piotr Zieliński | CM | Holding Anchor | 344.4167 | 0.6136 |
| 3 | 247 | Krystian Bielik | DM | Holding Anchor | 240.0167 | 0.3935 |
| 4 | 321 | Jakub Kamiński | AM | Progressive Winger | 253.6333 | 0.3461 |
| 5 | 323 | Karol Świderski | FW | Pressing Forward | 45.0000 | 0.3458 |


## Portugal

- Total xT created: 2.6573
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 3 | Bruno Miguel Borges Fernandes | AM | Progressive Winger | 384.9500 | 0.8365 |
| 2 | 17 | Gonçalo Matias Ramos | FW | Target Forward | 171.8833 | 0.7308 |
| 3 | 24 | Cristiano Ronaldo dos Santos Aveiro | FW | Target Forward | 302.8000 | 0.6923 |
| 4 | 70 | João Félix Sequeira | AM | Ball-Winner | 340.2333 | 0.5924 |
| 5 | 71 | Bernardo Mota Veiga de Carvalho e Silva | CM | Ball-Winner | 382.1000 | 0.5894 |


## Qatar

- Total xT created: 0.7960
- Total xA created: 1.1791
- Pass completion under pressure: 0.6995
- Mean defensive hull area: 451.6214
- Mean defensive density: 0.0529

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 127 | Mohammed Muntari | FW | Target Forward / Penalty-Box Anchor | 77.7500 | 0.5019 |
| 2 | 169 | Abdelkarim Hassan Al Haj Fadlalla | CB | Ball-Playing Centre-Back | 287.4000 | 0.4625 |
| 3 | 203 | Boualem Khoukhi | CB | Sweeper CB | 287.4000 | 0.4312 |
| 4 | 288 | Akram Hassan Afif | FW | Progressive Winger | 287.4000 | 0.3632 |
| 5 | 332 | Bassam Hisham Al Rawi | CB | Sweeper CB | 95.3167 | 0.3369 |


## Saudi Arabia

- Total xT created: 1.0502
- Total xA created: 1.2324
- Pass completion under pressure: 0.6235
- Mean defensive hull area: 480.3764
- Mean defensive density: 0.0271

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 15 | Salem Mohammed Al Dawsari | AM | Progressive Winger | 298.5500 | 0.7362 |
| 2 | 174 | Saleh Khalid Al Shehri | FW | Target Forward | 223.4000 | 0.4596 |
| 3 | 228 | Sami Khalil Al Naji | AM | Progressive Winger | 45.0000 | 0.4058 |
| 4 | 234 | Saud Abdullah Abdul Hamid | FB | Attacking Wingback | 298.5500 | 0.4038 |
| 5 | 238 | Mohammed Al Burayk | FB | Attacking Wingback | 69.9833 | 0.4011 |


## Senegal

- Total xT created: 1.6919
- Total xA created: 2.0598
- Pass completion under pressure: 0.6875
- Mean defensive hull area: 550.7399
- Mean defensive density: 0.0216

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 57 | Ismaïla Sarr | AM | Progressive Winger | 365.2000 | 0.6180 |
| 2 | 116 | Youssouf Sabaly | FB | Attacking Wingback | 387.2833 | 0.5127 |
| 3 | 137 | Kalidou Koulibaly | CB | Sweeper CB | 387.2833 | 0.4896 |
| 4 | 146 | Cheikh Ahmadou Bamba Mbacke Dieng | FW | Target Forward | 126.2500 | 0.4823 |
| 5 | 166 | Krépin Diatta | AM | Progressive Winger | 181.9167 | 0.4647 |


## Serbia

- Total xT created: 1.3908
- Total xA created: 2.0346
- Pass completion under pressure: 0.6740
- Mean defensive hull area: 611.0415
- Mean defensive density: 0.0224

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 42 | Aleksandar Mitrović | FW | Target Forward | 279.4167 | 0.6498 |
| 2 | 81 | Dušan Tadić | AM | Progressive Winger | 270.9333 | 0.5684 |
| 3 | 154 | Dušan Vlahović | FW | Target Forward / Penalty-Box Anchor | 86.0667 | 0.4779 |
| 4 | 168 | Andrija Živković | FB | Attacking Wingback | 212.0833 | 0.4628 |
| 5 | 172 | Strahinja Pavlović | CB | Ball-Playing Centre-Back | 252.8500 | 0.4609 |


## South Korea

- Total xT created: 1.8015
- Total xA created: 2.3972
- Pass completion under pressure: 0.6712
- Mean defensive hull area: 410.9954
- Mean defensive density: 0.0297

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 89 | Kang-In Lee | CM | Deep Playmaker / Metronome | 170.0500 | 0.5551 |
| 2 | 112 | Hee-Chan Hwang | AM | Progressive Winger | 125.5667 | 0.5156 |
| 3 | 120 | Gue-Sung Cho | FW | Target Forward / Penalty-Box Anchor | 297.4167 | 0.5090 |
| 4 | 179 | Heung-Min Son | AM | Target Forward | 389.6500 | 0.4499 |
| 5 | 186 | Moon-Hwan Kim | FB | Attacking Wingback | 389.6500 | 0.4431 |


## Spain

- Total xT created: 2.5669
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 19 | Álvaro Borja Morata Martín | FW | Target Forward | 200.8333 | 0.7100 |
| 2 | 35 | Pedro González López | CM | Holding Anchor | 372.4000 | 0.6630 |
| 3 | 40 | Rodrigo Hernández Cascante | CB | Ball-Playing Centre-Back | 413.9500 | 0.6520 |
| 4 | 41 | Daniel Olmo Carvajal | AM | Progressive Winger | 388.2500 | 0.6512 |
| 5 | 50 | Marco Asensio Willemsen | FW | Progressive Winger | 236.9667 | 0.6280 |


## Switzerland

- Total xT created: 1.4531
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 46 | Breel-Donald Embolo | FW | Pressing Forward | 330.1500 | 0.6327 |
| 2 | 76 | Xherdan Shaqiri | AM | Progressive Winger | 233.5833 | 0.5804 |
| 3 | 111 | Manuel Obafemi Akanji | CB | Ball-Playing Centre-Back | 386.5833 | 0.5216 |
| 4 | 135 | Ruben Vargas | AM | Progressive Winger | 286.9500 | 0.4945 |
| 5 | 181 | Silvan Widmer | FB | Attacking Wingback | 281.8500 | 0.4494 |


## Tunisia

- Total xT created: 1.2810
- Total xA created: 1.9897
- Pass completion under pressure: 0.5839
- Mean defensive hull area: 396.7358
- Mean defensive density: 0.0421

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 68 | Youssef Msakni | AM | Progressive Winger | 176.0667 | 0.5934 |
| 2 | 108 | Wahbi Khazri | FW | Progressive Winger | 88.5667 | 0.5244 |
| 3 | 158 | Aïssa Bilal Laïdouni | DM | Box-to-Box / Engine Midfielder | 257.2333 | 0.4754 |
| 4 | 175 | Issam Jebali | FW | Pressing Forward | 196.3500 | 0.4585 |
| 5 | 177 | Naïm Sliti | AM | Progressive Winger | 127.1667 | 0.4514 |


## United States

- Total xT created: 2.0784
- Total xA created: 3.2488
- Pass completion under pressure: 0.7900
- Mean defensive hull area: 451.8615
- Mean defensive density: 0.0339

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 5 | Christian Pulisic | AM | Progressive Winger | 336.3167 | 0.7847 |
| 2 | 79 | Haji Wright | FW | Target Forward / Penalty-Box Anchor | 161.8833 | 0.5716 |
| 3 | 80 | Yunus Dimoara Musah | CM | Box-to-Box / Engine Midfielder | 364.8667 | 0.5715 |
| 4 | 90 | Weston McKennie | CM | Deep Playmaker / Metronome | 273.5500 | 0.5548 |
| 5 | 105 | Tyler Adams | DM | Holding / Controlling Midfielder | 391.2000 | 0.5329 |


## Uruguay

- Total xT created: 1.4720
- Total xA created: 1.9893
- Pass completion under pressure: 0.6460
- Mean defensive hull area: 457.0204
- Mean defensive density: 0.0260

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 52 | Rodrigo Bentancur Colmán | DM | Box-to-Box / Engine Midfielder | 231.6667 | 0.6246 |
| 2 | 66 | Giorgian Daniel De Arrascaeta Benedetti | AM | Progressive Winger | 118.1000 | 0.5948 |
| 3 | 91 | Federico Santiago Valverde Dipetta | DM | Holding Anchor | 298.0833 | 0.5543 |
| 4 | 102 | Mathías Olivera Miramontes | FB | Wide Creator | 263.6333 | 0.5353 |
| 5 | 125 | José María Giménez de Vargas | CB | Sweeper CB | 298.0833 | 0.5047 |


## Wales

- Total xT created: 0.8960
- Total xA created: 1.2536
- Pass completion under pressure: 0.6856
- Mean defensive hull area: 599.2348
- Mean defensive density: 0.0252

### Top five player summary

| Team Rank V2 | Global Rank V2 | Player Name | Position Group 360 | Functional Role | Minutes Played | Final Player Rating V2 |
|---|---|---|---|---|---|---|
| 1 | 114 | Gareth Frank Bale | FW | Target Forward | 247.7167 | 0.5128 |
| 2 | 162 | Kieffer Roberto Francisco Moore | FW | Target Forward / Penalty-Box Anchor | 251.7167 | 0.4696 |
| 3 | 222 | Chris Mepham | CB | Sweeper CB | 296.7167 | 0.4135 |
| 4 | 271 | Harry Wilson | CM | Wide Creator | 167.2333 | 0.3733 |
| 5 | 291 | Neco Williams | FB | Wide Creator | 216.3833 | 0.3611 |


## Interpretation boundary

These rankings summarize performance in the 2022 tournament sample. They are not transfer valuations, causal estimates, medical assessments, or replacements for video and scouting review.
