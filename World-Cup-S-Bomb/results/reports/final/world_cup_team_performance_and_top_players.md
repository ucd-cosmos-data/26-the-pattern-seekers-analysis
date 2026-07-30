# 2022 FIFA World Cup Player Ranking Report

## Executive summary

This report consolidates **32 national teams** and **593 eligible rated players** (outfield 45+ minutes; goalkeepers 90+). It uses StatsBomb events, lineups, minutes, and coverage-qualified 360 freeze frames. It does not use optical tracking, external ratings, or player-name adjustments.

The position-aware tournament rankings are stored under `results/reports/ranking/`. They add formal 360 groups while preserving the source position and role detail.

## Global top 10 players - unified tournament rating

| Global Rank | Team Rank | Player Name | Team | Position Group 360 | Functional Role | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 1 | Lionel Andrés Messi Cuccittini | Argentina | AM | Progressive Winger | 0.9999 |
| 2 | 1 | Kylian Mbappé Lottin | France | FW | Progressive Winger | 0.9996 |
| 3 | 2 | Theo Bernard François Hernández | France | FB | Attacking Wingback | 0.9981 |
| 4 | 1 | Joško Gvardiol | Croatia | CB | Ball-Playing Centre-Back | 0.9973 |
| 5 | 2 | Mateo Kovačić | Croatia | CM | Deep Playmaker / Metronome | 0.9955 |
| 6 | 3 | Luka Modrić | Croatia | CM | Deep Playmaker / Metronome | 0.9953 |
| 7 | 1 | Rodrigo Hernández Cascante | Spain | CB | Ball-Playing Centre-Back | 0.9936 |
| 8 | 1 | Jude Bellingham | England | DM | Box-to-Box / Engine Midfielder | 0.9912 |
| 9 | 1 | Frenkie de Jong | Netherlands | DM | Holding Anchor | 0.9909 |
| 10 | 1 | Bruno Miguel Borges Fernandes | Portugal | AM | Progressive Winger | 0.9865 |

## Global top five goalkeepers — tournament ranking v2

| Gk Rank V2 | Player Name | Team | Gk Rating V2 |
|---|---|---|---|
| 1 | Dominik Livaković | Croatia | 1.0000 |
| 2 | Damián Emiliano Martínez | Argentina | 0.5971 |
| 3 | Yassine Bounou | Morocco | 0.5876 |
| 4 | Wojciech Szczęsny | Poland | 0.4394 |
| 5 | Unai Simón Mendibil | Spain | 0.3417 |

The active contribution layer is `role_aware_fallback`. The experimental attention challenger remains available but affects rankings only when it passes its match-disjoint metric gate.

## How to read the player rating

The preserved V5 contribution score uses the development-gated baseline VAEP feature set and grouped ElasticNet offense/defense heads with explicit role weights, VAEP/touch, open-play and set-piece-aware xT, sample-adjusted completeness, coverage-qualified off-ball value, and xD-style defensive disruption. Positive ElasticNet calibration selects the composite weights with team-disjoint folds, followed by minutes/(minutes+450) position-prior shrinkage.

The tournament ranking v2 adds explicit goals, xG, shots, xA, chance creation, progression, possession, defending, and off-ball components normalized within `position_group_360`. A capped, general role-based finishing treatment corrects the structural penalty on goal-centric forwards; it never checks player names.

Goalkeepers use a separate tournament-v2 matrix led by a match-disjoint PSxG-GA proxy, reliability-shrunk save rates, penalty performance, box command, sweeping, distribution under pressure, and an explicit shootout-impact term. Their dedicated goalkeeper order is mapped into the unified table through a finite-sample Blom empirical-quantile bridge against the outfield score distribution. This preserves goalkeeper order without turning the maximum of a 32-player cohort into an automatic global podium place. Missing 360 evidence remains missing, and role labels never award rating points.

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

_No eligible observations._

### Largest downward rank movements

_No eligible observations._

Rank movement compares the prior global ordering with tournament ranking v2 ordering; it does not compare raw rating magnitudes.

## All-team overview

| Team | Eligible Players | Observed Players | Top Ranked Player | Top Global Rank | Total Xt | Pressure Resistance | Mean Creation | Mean Defensive | Mean Ball Security |
|---|---|---|---|---|---|---|---|---|---|
| Argentina | 20 | 20 | Lionel Andrés Messi Cuccittini | 1 | 4.0073 | 0.7447 | 0.4948 | 0.5032 | 0.5631 |
| Australia | 17 | 17 | Craig Goodwin | 216 | 1.1032 | 0.6496 | 0.4821 | 0.5524 | 0.4073 |
| Belgium | 17 | 17 | Kevin De Bruyne | 93 | 1.4404 | 0.7696 | 0.5216 | 0.4606 | 0.5504 |
| Brazil | 25 | 24 | Thiago Emiliano da Silva | 23 | 3.8085 | 0.7291 | 0.5582 | 0.5207 | 0.5394 |
| Cameroon | 18 | 17 | Jean-Charles Castelletto | 42 | 1.0760 | 0.6971 | 0.5205 | 0.5087 | 0.5478 |
| Canada | 16 | 16 | Alistair Johnston | 43 | 1.7913 | 0.7118 | 0.5417 | 0.5160 | 0.5611 |
| Costa Rica | 17 | 17 | Kendall Jamaal Waston Manley | 86 | 0.4184 | 0.6509 | 0.3933 | 0.5727 | 0.5415 |
| Croatia | 20 | 20 | Joško Gvardiol | 4 | 3.7160 | 0.7430 | 0.5431 | 0.5524 | 0.4884 |
| Denmark | 18 | 18 | Andreas Christensen | 61 | 1.7188 | 0.7086 | 0.5094 | 0.5011 | 0.4851 |
| Ecuador | 16 | 16 | Pervis Josué Estupiñán Tenorio | 53 | 1.0181 | 0.6954 | 0.4626 | 0.5420 | 0.5067 |
| England | 19 | 19 | Jude Bellingham | 8 | 2.5219 | 0.7556 | 0.5374 | 0.4677 | 0.6180 |
| France | 22 | 21 | Kylian Mbappé Lottin | 2 | 3.9248 | 0.6863 | 0.5247 | 0.5475 | 0.5195 |
| Germany | 17 | 17 | Joshua Kimmich | 15 | 2.4318 | 0.7731 | 0.6119 | 0.5340 | 0.5662 |
| Ghana | 17 | 17 | Mohamed Salisu | 119 | 0.9360 | 0.6763 | 0.4424 | 0.5817 | 0.5040 |
| Iran | 20 | 19 | Mehdi Taremi | 32 | 1.2461 | 0.6687 | 0.5135 | 0.5081 | 0.4805 |
| Japan | 22 | 22 | Wataru Endo | 74 | 1.5415 | 0.6415 | 0.5311 | 0.5298 | 0.3974 |
| Mexico | 18 | 18 | Luis Gerardo Chávez Magallón | 107 | 1.3586 | 0.6241 | 0.5345 | 0.5386 | 0.4373 |
| Morocco | 23 | 22 | Achraf Hakimi Mouh | 14 | 2.4078 | 0.6771 | 0.4573 | 0.5519 | 0.4718 |
| Netherlands | 18 | 18 | Frenkie de Jong | 9 | 2.0451 | 0.7135 | 0.5206 | 0.4882 | 0.5096 |
| Poland | 16 | 16 | Wojciech Szczęsny | 67 | 1.1292 | 0.6818 | 0.4694 | 0.5129 | 0.5278 |
| Portugal | 22 | 22 | Bruno Miguel Borges Fernandes | 10 | 2.6573 | 0.7085 | 0.5171 | 0.4842 | 0.5829 |
| Qatar | 15 | 14 | Abdelkarim Hassan Al Haj Fadlalla | 101 | 0.7960 | 0.6995 | 0.4849 | 0.4605 | 0.5492 |
| Saudi Arabia | 20 | 20 | Salem Mohammed Al Dawsari | 54 | 1.0502 | 0.6235 | 0.4610 | 0.5524 | 0.4362 |
| Senegal | 18 | 18 | Kalidou Koulibaly | 29 | 1.6919 | 0.6875 | 0.5320 | 0.5050 | 0.5330 |
| Serbia | 16 | 16 | Nikola Milenković | 72 | 1.3908 | 0.6740 | 0.4786 | 0.4911 | 0.4913 |
| South Korea | 19 | 19 | Moon-Hwan Kim | 76 | 1.8015 | 0.6712 | 0.5134 | 0.5248 | 0.5144 |
| Spain | 20 | 20 | Rodrigo Hernández Cascante | 7 | 2.5669 | 0.8268 | 0.4769 | 0.4885 | 0.5700 |
| Switzerland | 19 | 18 | Manuel Obafemi Akanji | 46 | 1.4531 | 0.7318 | 0.5231 | 0.4384 | 0.5397 |
| Tunisia | 18 | 18 | Ali Abdi | 95 | 1.2810 | 0.5839 | 0.5512 | 0.5960 | 0.3517 |
| United States | 18 | 18 | Christian Pulisic | 24 | 2.0784 | 0.7900 | 0.5144 | 0.4811 | 0.5368 |
| Uruguay | 17 | 17 | Mathías Olivera Miramontes | 21 | 1.4720 | 0.6460 | 0.5435 | 0.5093 | 0.4344 |
| Wales | 15 | 14 | Chris Mepham | 113 | 0.8960 | 0.6856 | 0.5076 | 0.5235 | 0.4787 |

# Team-by-team summary

Scope note: every team top five below uses the unified tournament score and includes the ranked team-main goalkeeper when that score places the goalkeeper in the top five. Backup goalkeepers remain unranked.

## Argentina

- Total xT created: 4.0073
- Total xA created: 6.7228
- Pass completion under pressure: 0.7447
- Mean defensive hull area: 647.6227
- Mean defensive density: 0.0258

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 1 | Lionel Andrés Messi Cuccittini | AM | Progressive Winger | 733.9000 | 0.9999 |
| 2 | 11 | Rodrigo Javier De Paul | DM | Deep Playmaker | 634.7333 | 0.9857 |
| 3 | 13 | Enzo Fernandez | DM | Holding Anchor | 601.1167 | 0.9843 |
| 4 | 26 | Damián Emiliano Martínez | GK | Goalkeeper | 733.9000 | 0.9558 |
| 5 | 27 | Julián Álvarez | FW | Pressing Forward | 485.2333 | 0.9558 |


## Australia

- Total xT created: 1.1032
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 216 | Craig Goodwin | AM | Wide Creator | 241.7000 | 0.5496 |
| 2 | 218 | Harry Souttar | CB | Sweeper CB | 386.9167 | 0.5406 |
| 3 | 219 | Fran Karačić | FB | Attacking Wingback | 100.3667 | 0.5379 |
| 4 | 246 | Aziz Eraltay Behich | FB | Wide Creator | 386.9167 | 0.4766 |
| 5 | 248 | Mathew Ryan | GK | Goalkeeper | 386.9167 | 0.4727 |


## Belgium

- Total xT created: 1.4404
- Total xA created: 2.5562
- Pass completion under pressure: 0.7696
- Mean defensive hull area: 640.6988
- Mean defensive density: 0.0190

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 93 | Kevin De Bruyne | AM | Progressive Winger | 284.2667 | 0.7940 |
| 2 | 121 | Thibaut Courtois | GK | Goalkeeper | 284.2667 | 0.7420 |
| 3 | 272 | Thomas Meunier | FB | Attacking Wingback | 217.3667 | 0.4318 |
| 4 | 273 | Axel Witsel | DM | Holding Anchor | 284.2667 | 0.4295 |
| 5 | 293 | Michy Batshuayi Tunga | FW | Target Forward | 151.9000 | 0.3987 |


## Brazil

- Total xT created: 3.8085
- Total xA created: 6.8525
- Pass completion under pressure: 0.7291
- Mean defensive hull area: 579.4863
- Mean defensive density: 0.0211

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 23 | Thiago Emiliano da Silva | CB | Ball-Playing Centre-Back | 409.0667 | 0.9586 |
| 2 | 30 | Marcos Aoás Corrêa | CB | Ball-Playing Centre-Back | 455.0167 | 0.9462 |
| 3 | 40 | Richarlison de Andrade | FW | Pressing Forward | 328.2500 | 0.9313 |
| 4 | 45 | Neymar da Silva Santos Junior | AM | Progressive Winger | 281.4833 | 0.9264 |
| 5 | 58 | Alex Sandro Lobo Silva | FB | Attacking Wingback | 199.5333 | 0.9029 |


## Cameroon

- Total xT created: 1.0760
- Total xA created: 1.8107
- Pass completion under pressure: 0.6971
- Mean defensive hull area: 518.5576
- Mean defensive density: 0.0268

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 42 | Jean-Charles Castelletto | CB | Sweeper CB | 192.4500 | 0.9291 |
| 2 | 124 | Nouhou Tolo | FB | Wide Creator | 292.5500 | 0.7399 |
| 3 | 180 | André-Frank Zambo Anguissa | DM | Box-to-Box / Engine Midfielder | 276.6500 | 0.6274 |
| 4 | 200 | Jean-Eric Maxim Choupo-Moting | FW | Target Forward | 269.9833 | 0.5731 |
| 5 | 208 | Vincent Paté Aboubakar | FW | Target Forward | 164.2333 | 0.5652 |


## Canada

- Total xT created: 1.7913
- Total xA created: 2.0764
- Pass completion under pressure: 0.7118
- Mean defensive hull area: 569.4089
- Mean defensive density: 0.0243

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 43 | Alistair Johnston | FB | Attacking Wingback | 284.9667 | 0.9284 |
| 2 | 108 | Atiba Hutchinson | DM | Holding Anchor | 164.2000 | 0.7635 |
| 3 | 116 | Alphonso Davies | CM | Box-to-Box / Engine Midfielder | 284.9667 | 0.7500 |
| 4 | 209 | Tajon Buchanan | AM | Progressive Winger | 270.0833 | 0.5622 |
| 5 | 255 | Steven de Sousa Vitoria | CB | Sweeper CB | 284.9667 | 0.4600 |


## Costa Rica

- Total xT created: 0.4184
- Total xA created: 0.4012
- Pass completion under pressure: 0.6509
- Mean defensive hull area: 510.3123
- Mean defensive density: 0.0278

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 86 | Kendall Jamaal Waston Manley | CB | Sweeper CB | 249.4500 | 0.8398 |
| 2 | 173 | Óscar Esau Duarte Gaitán | CB | Sweeper CB | 294.4500 | 0.6410 |
| 3 | 205 | Francisco Javier Calvo Quesada | CB | Sweeper CB | 194.4167 | 0.5702 |
| 4 | 231 | Juan Pablo Vargas Campos | CB | Sweeper CB | 100.0333 | 0.5049 |
| 5 | 256 | Celso Borges Mora | DM | Holding Anchor | 260.0500 | 0.4599 |


## Croatia

- Total xT created: 3.7160
- Total xA created: 5.6716
- Pass completion under pressure: 0.7430
- Mean defensive hull area: 480.9343
- Mean defensive density: 0.0281

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 4 | Joško Gvardiol | CB | Ball-Playing Centre-Back | 720.2833 | 0.9973 |
| 2 | 5 | Mateo Kovačić | CM | Deep Playmaker / Metronome | 649.9167 | 0.9955 |
| 3 | 6 | Luka Modrić | CM | Deep Playmaker / Metronome | 672.6667 | 0.9953 |
| 4 | 19 | Dominik Livaković | GK | Goalkeeper | 720.2833 | 0.9677 |
| 5 | 25 | Ivan Perišić | AM | Wide Creator | 686.8167 | 0.9558 |


## Denmark

- Total xT created: 1.7188
- Total xA created: 2.1738
- Pass completion under pressure: 0.7086
- Mean defensive hull area: 439.0378
- Mean defensive density: 0.0278

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 61 | Andreas Christensen | CB | Ball-Playing Centre-Back | 290.8000 | 0.8923 |
| 2 | 83 | Christian Dannemann Eriksen | CM | Progressive Winger | 290.8000 | 0.8472 |
| 3 | 102 | Joachim Andersen | CB | Sweeper CB | 290.8000 | 0.7842 |
| 4 | 194 | Rasmus Nissen Kristensen | FB | Attacking Wingback | 234.2167 | 0.5867 |
| 5 | 224 | Simon Thorup Kjær | CB | Ball-Playing Centre-Back | 63.9833 | 0.5210 |


## Ecuador

- Total xT created: 1.0181
- Total xA created: 1.1631
- Pass completion under pressure: 0.6954
- Mean defensive hull area: 440.9376
- Mean defensive density: 0.0261

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 53 | Pervis Josué Estupiñán Tenorio | FB | Attacking Wingback | 288.3833 | 0.9153 |
| 2 | 125 | Piero Martín Hincapié Reyna | CB | Sweeper CB | 288.3833 | 0.7398 |
| 3 | 150 | Enner Remberto Valencia Lastra | AM | Target Forward | 261.9167 | 0.6777 |
| 4 | 156 | Angelo Smit Preciado Quiñónez | FB | Deep Playmaker | 276.2167 | 0.6662 |
| 5 | 213 | Jackson Gabriel Porozo Vernaza | CB | Defensive Centre-Back | 108.3000 | 0.5589 |


## England

- Total xT created: 2.5219
- Total xA created: 4.8703
- Pass completion under pressure: 0.7556
- Mean defensive hull area: 482.2597
- Mean defensive density: 0.0278

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 8 | Jude Bellingham | DM | Box-to-Box / Engine Midfielder | 441.7667 | 0.9912 |
| 2 | 12 | Harry Maguire | CB | Sweeper CB | 453.7167 | 0.9848 |
| 3 | 33 | Luke Shaw | FB | Attacking Wingback | 457.1667 | 0.9418 |
| 4 | 49 | Harry Kane | FW | Target Forward | 421.5167 | 0.9238 |
| 5 | 56 | John Stones | CB | Ball-Playing Centre-Back | 464.8833 | 0.9075 |


## France

- Total xT created: 3.9248
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 2 | Kylian Mbappé Lottin | FW | Progressive Winger | 654.3000 | 0.9996 |
| 2 | 3 | Theo Bernard François Hernández | FB | Attacking Wingback | 548.5000 | 0.9981 |
| 3 | 16 | Aurélien Djani Tchouaméni | DM | Holding / Controlling Midfielder | 662.2167 | 0.9798 |
| 4 | 17 | Ibrahima Konaté | CB | Ball-Playing Centre-Back | 330.8167 | 0.9791 |
| 5 | 18 | Adrien Rabiot | DM | Holding Anchor | 529.2500 | 0.9715 |


## Germany

- Total xT created: 2.4318
- Total xA created: 6.0997
- Pass completion under pressure: 0.7731
- Mean defensive hull area: 489.2536
- Mean defensive density: 0.0243

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 15 | Joshua Kimmich | FB | Attacking Wingback | 294.0000 | 0.9800 |
| 2 | 34 | David Raum | FB | Attacking Wingback | 250.3000 | 0.9413 |
| 3 | 75 | Serge Gnabry | AM | Progressive Winger | 273.3333 | 0.8624 |
| 4 | 144 | Jamal Musiala | AM | Hybrid Playmaker / Roaming Creator | 274.0667 | 0.6966 |
| 5 | 171 | İlkay Gündoğan | AM | Linking Attacker | 190.0500 | 0.6436 |


## Ghana

- Total xT created: 0.9360
- Total xA created: 0.9937
- Pass completion under pressure: 0.6763
- Mean defensive hull area: 432.5226
- Mean defensive density: 0.0269

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 119 | Mohamed Salisu | CB | Sweeper CB | 301.2000 | 0.7441 |
| 2 | 137 | Thomas Teye Partey | DM | Holding Anchor | 301.2000 | 0.7064 |
| 3 | 172 | Salis Abdul Samed | DM | Holding Anchor | 264.9500 | 0.6416 |
| 4 | 197 | Tariq Lamptey | FB | Deep Playmaker | 112.2167 | 0.5788 |
| 5 | 237 | Daniel Amartey | CB | Sweeper CB | 301.2000 | 0.5005 |


## Iran

- Total xT created: 1.2461
- Total xA created: 2.6253
- Pass completion under pressure: 0.6687
- Mean defensive hull area: 460.4993
- Mean defensive density: 0.0330

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 32 | Mehdi Taremi | FW | Target Forward | 305.1000 | 0.9440 |
| 2 | 132 | Milad Mohammadi | FB | Wide Creator | 211.9833 | 0.7256 |
| 3 | 160 | Ramin Rezaeian | FB | Attacking Wingback | 202.0167 | 0.6647 |
| 4 | 162 | Morteza Pouraliganji | CB | Sweeper CB | 305.1000 | 0.6593 |
| 5 | 249 | Saeid Ezatolahi Afagh | DM | Holding Anchor | 240.1500 | 0.4667 |


## Japan

- Total xT created: 1.5415
- Total xA created: 2.4186
- Pass completion under pressure: 0.6415
- Mean defensive hull area: 501.4214
- Mean defensive density: 0.0229

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 74 | Wataru Endo | DM | Box-to-Box / Engine Midfielder | 326.0167 | 0.8646 |
| 2 | 115 | Kaoru Mitoma | FB | Attacking Wingback | 186.1167 | 0.7511 |
| 3 | 118 | Takuma Asano | FW | Target Forward | 186.3500 | 0.7449 |
| 4 | 129 | Maya Yoshida | CB | Sweeper CB | 412.5167 | 0.7302 |
| 5 | 174 | Hidemasa Morita | DM | Box-to-Box / Engine Midfielder | 298.3667 | 0.6393 |


## Mexico

- Total xT created: 1.3586
- Total xA created: 2.6085
- Pass completion under pressure: 0.6241
- Mean defensive hull area: 639.3089
- Mean defensive density: 0.0298

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 107 | Luis Gerardo Chávez Magallón | DM | Holding / Controlling Midfielder | 291.5000 | 0.7668 |
| 2 | 123 | Hirving Rodrigo Lozano Bahena | AM | Progressive Winger | 267.3167 | 0.7402 |
| 3 | 127 | Edson Omar Álvarez Velázquez | DM | Box-to-Box / Engine Midfielder | 183.2333 | 0.7368 |
| 4 | 163 | Héctor Alfredo Moreno Herrera | CB | Sweeper CB | 291.5000 | 0.6584 |
| 5 | 223 | Jesús Daniel Gallardo Vasconcelos | FB | Wide Creator | 291.5000 | 0.5222 |


## Morocco

- Total xT created: 2.4078
- Total xA created: 3.2076
- Pass completion under pressure: 0.6771
- Mean defensive hull area: 518.2011
- Mean defensive density: 0.0225

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 14 | Achraf Hakimi Mouh | FB | Attacking Wingback | 660.8000 | 0.9816 |
| 2 | 22 | Hakim Ziyech | AM | Deep Playmaker | 662.6333 | 0.9598 |
| 3 | 44 | Yassine Bounou | GK | Goalkeeper | 603.1500 | 0.9281 |
| 4 | 92 | Azzedine Ounahi | CM | Box-to-Box / Engine Midfielder | 589.2500 | 0.7969 |
| 5 | 104 | Sofiane Boufal | AM | Progressive Winger | 476.6667 | 0.7737 |


## Netherlands

- Total xT created: 2.0451
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 9 | Frenkie de Jong | DM | Holding Anchor | 499.4500 | 0.9909 |
| 2 | 38 | Cody Mathès Gakpo | AM | Progressive Winger | 460.2167 | 0.9337 |
| 3 | 48 | Daley Blind | FB | Attacking Wingback | 452.4833 | 0.9242 |
| 4 | 52 | Jurriën David Norman Timber | CB | Sweeper CB | 409.4000 | 0.9183 |
| 5 | 68 | Memphis Depay | FW | Target Forward | 315.5833 | 0.8828 |


## Poland

- Total xT created: 1.1292
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 67 | Wojciech Szczęsny | GK | Goalkeeper | 389.7500 | 0.8837 |
| 2 | 71 | Piotr Zieliński | CM | Holding Anchor | 344.4167 | 0.8728 |
| 3 | 90 | Krystian Bielik | DM | Holding Anchor | 240.0167 | 0.8126 |
| 4 | 109 | Robert Lewandowski | FW | Target Forward / Penalty-Box Anchor | 389.7500 | 0.7619 |
| 5 | 128 | Grzegorz Krychowiak | DM | Box-to-Box / Engine Midfielder | 347.8833 | 0.7339 |


## Portugal

- Total xT created: 2.6573
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 10 | Bruno Miguel Borges Fernandes | AM | Progressive Winger | 384.9500 | 0.9865 |
| 2 | 63 | Raphaël Adelino José Guerreiro | FB | Attacking Wingback | 303.6167 | 0.8906 |
| 3 | 73 | Bernardo Mota Veiga de Carvalho e Silva | CM | Ball-Winner | 382.1000 | 0.8662 |
| 4 | 82 | João Pedro Cavaco Cancelo | FB | Wide Creator | 344.5500 | 0.8478 |
| 5 | 94 | João Félix Sequeira | AM | Ball-Winner | 340.2333 | 0.7935 |


## Qatar

- Total xT created: 0.7960
- Total xA created: 1.1791
- Pass completion under pressure: 0.6995
- Mean defensive hull area: 451.6214
- Mean defensive density: 0.0529

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 101 | Abdelkarim Hassan Al Haj Fadlalla | CB | Ball-Playing Centre-Back | 287.4000 | 0.7844 |
| 2 | 112 | Boualem Khoukhi | CB | Sweeper CB | 287.4000 | 0.7552 |
| 3 | 148 | Assim Omer Al Haj Madibo | DM | Holding Anchor | 159.8500 | 0.6792 |
| 4 | 336 | Hassan Khalid Al Heidos | CM | Ball-Winner | 209.0833 | 0.3331 |
| 5 | 349 | Akram Hassan Afif | FW | Progressive Winger | 287.4000 | 0.3146 |


## Saudi Arabia

- Total xT created: 1.0502
- Total xA created: 1.2324
- Pass completion under pressure: 0.6235
- Mean defensive hull area: 480.3764
- Mean defensive density: 0.0271

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 54 | Salem Mohammed Al Dawsari | AM | Progressive Winger | 298.5500 | 0.9144 |
| 2 | 103 | Mohammed Khalil Al Owais | GK | Goalkeeper | 298.5500 | 0.7813 |
| 3 | 152 | Abdulelah Al Amri | CB | Sweeper CB | 210.8167 | 0.6709 |
| 4 | 178 | Saud Abdullah Abdul Hamid | FB | Attacking Wingback | 298.5500 | 0.6325 |
| 5 | 222 | Hassan Mohammed Al-Tambakti | CB | Sweeper CB | 201.4667 | 0.5224 |


## Senegal

- Total xT created: 1.6919
- Total xA created: 2.0598
- Pass completion under pressure: 0.6875
- Mean defensive hull area: 550.7399
- Mean defensive density: 0.0216

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 29 | Kalidou Koulibaly | CB | Sweeper CB | 387.2833 | 0.9492 |
| 2 | 62 | Youssouf Sabaly | FB | Attacking Wingback | 387.2833 | 0.8913 |
| 3 | 99 | Pathé Ismaël Ciss | DM | Box-to-Box / Engine Midfielder | 151.1667 | 0.7866 |
| 4 | 170 | Ismaïla Sarr | AM | Progressive Winger | 365.2000 | 0.6445 |
| 5 | 206 | Ismail Jakobs | FB | Attacking Wingback | 296.4833 | 0.5691 |


## Serbia

- Total xT created: 1.3908
- Total xA created: 2.0346
- Pass completion under pressure: 0.6740
- Mean defensive hull area: 611.0415
- Mean defensive density: 0.0224

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 72 | Nikola Milenković | CB | Sweeper CB | 293.6500 | 0.8671 |
| 2 | 89 | Aleksandar Mitrović | FW | Target Forward | 279.4167 | 0.8163 |
| 3 | 97 | Strahinja Pavlović | CB | Ball-Playing Centre-Back | 252.8500 | 0.7873 |
| 4 | 139 | Vanja Milinković Savić | GK | Goalkeeper | 293.6500 | 0.7039 |
| 5 | 143 | Dušan Tadić | AM | Progressive Winger | 270.9333 | 0.6974 |


## South Korea

- Total xT created: 1.8015
- Total xA created: 2.3972
- Pass completion under pressure: 0.6712
- Mean defensive hull area: 410.9954
- Mean defensive density: 0.0297

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 76 | Moon-Hwan Kim | FB | Attacking Wingback | 389.6500 | 0.8602 |
| 2 | 110 | Woo-Young Jung | DM | Holding Anchor | 317.9167 | 0.7606 |
| 3 | 134 | Jin-Su Kim | FB | Attacking Wingback | 340.6833 | 0.7197 |
| 4 | 161 | Min Jae Kim | CB | Sweeper CB | 283.4500 | 0.6640 |
| 5 | 169 | Young-Gwon Kim | CB | Sweeper CB | 373.1833 | 0.6446 |


## Spain

- Total xT created: 2.5669
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 7 | Rodrigo Hernández Cascante | CB | Ball-Playing Centre-Back | 413.9500 | 0.9936 |
| 2 | 37 | Jordi Alba Ramos | FB | Attacking Wingback | 270.7667 | 0.9352 |
| 3 | 47 | Pedro González López | CM | Holding Anchor | 372.4000 | 0.9252 |
| 4 | 55 | Sergio Busquets i Burgos | DM | Holding Anchor | 379.2833 | 0.9097 |
| 5 | 64 | Daniel Olmo Carvajal | AM | Progressive Winger | 388.2500 | 0.8891 |


## Switzerland

- Total xT created: 1.4531
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 46 | Manuel Obafemi Akanji | CB | Ball-Playing Centre-Back | 386.5833 | 0.9258 |
| 2 | 105 | Granit Xhaka | DM | Holding Anchor | 386.5833 | 0.7732 |
| 3 | 106 | Breel-Donald Embolo | FW | Pressing Forward | 330.1500 | 0.7705 |
| 4 | 133 | Silvan Widmer | FB | Attacking Wingback | 281.8500 | 0.7200 |
| 5 | 153 | Xherdan Shaqiri | AM | Progressive Winger | 233.5833 | 0.6699 |


## Tunisia

- Total xT created: 1.2810
- Total xA created: 1.9897
- Pass completion under pressure: 0.5839
- Mean defensive hull area: 396.7358
- Mean defensive density: 0.0421

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 95 | Ali Abdi | FB | Attacking Wingback | 213.6333 | 0.7891 |
| 2 | 98 | Montassar Omar Talbi | CB | Sweeper CB | 296.5667 | 0.7873 |
| 3 | 130 | Aïssa Bilal Laïdouni | DM | Box-to-Box / Engine Midfielder | 257.2333 | 0.7276 |
| 4 | 135 | Ellyes Joris Skhiri | DM | Box-to-Box / Engine Midfielder | 296.5667 | 0.7189 |
| 5 | 199 | Yassine Meriah | CB | Sweeper CB | 296.5667 | 0.5743 |


## United States

- Total xT created: 2.0784
- Total xA created: 3.2488
- Pass completion under pressure: 0.7900
- Mean defensive hull area: 451.8615
- Mean defensive density: 0.0339

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 24 | Christian Pulisic | AM | Progressive Winger | 336.3167 | 0.9577 |
| 2 | 57 | Tyler Adams | DM | Holding / Controlling Midfielder | 391.2000 | 0.9051 |
| 3 | 81 | Sergino Dest | FB | Attacking Wingback | 307.5667 | 0.8482 |
| 4 | 84 | Antonee Robinson | FB | Attacking Wingback | 386.2667 | 0.8426 |
| 5 | 87 | Yunus Dimoara Musah | CM | Box-to-Box / Engine Midfielder | 364.8667 | 0.8376 |


## Uruguay

- Total xT created: 1.4720
- Total xA created: 1.9893
- Pass completion under pressure: 0.6460
- Mean defensive hull area: 457.0204
- Mean defensive density: 0.0260

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 21 | Mathías Olivera Miramontes | FB | Wide Creator | 263.6333 | 0.9647 |
| 2 | 50 | José María Giménez de Vargas | CB | Sweeper CB | 298.0833 | 0.9232 |
| 3 | 60 | Rodrigo Bentancur Colmán | DM | Box-to-Box / Engine Midfielder | 231.6667 | 0.8957 |
| 4 | 69 | Federico Santiago Valverde Dipetta | DM | Holding Anchor | 298.0833 | 0.8811 |
| 5 | 279 | Giorgian Daniel De Arrascaeta Benedetti | AM | Progressive Winger | 118.1000 | 0.4215 |


## Wales

- Total xT created: 0.8960
- Total xA created: 1.2536
- Pass completion under pressure: 0.6856
- Mean defensive hull area: 599.2348
- Mean defensive density: 0.0252

### Top five unified player summary

| Team Rank | Global Rank | Player Name | Position Group 360 | Functional Role | Minutes Played | Tournament Performance Score |
|---|---|---|---|---|---|---|
| 1 | 113 | Chris Mepham | CB | Sweeper CB | 296.7167 | 0.7543 |
| 2 | 207 | Neco Williams | FB | Wide Creator | 216.3833 | 0.5662 |
| 3 | 210 | Gareth Frank Bale | FW | Target Forward | 247.7167 | 0.5613 |
| 4 | 227 | Ben Davies | CB | Ball-Playing Centre-Back | 261.3333 | 0.5151 |
| 5 | 247 | Joe Rodon | CB | Sweeper CB | 296.7167 | 0.4743 |


## Interpretation boundary

These rankings summarize performance in the 2022 tournament sample. They are not transfer valuations, causal estimates, medical assessments, or replacements for video and scouting review.
