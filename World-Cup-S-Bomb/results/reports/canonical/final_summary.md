# World Cup V5 Role-Aware Final Report

## Executive summary

This report consolidates **32 national teams** and **593 eligible rated players** (outfield 45+ minutes; goalkeepers 90+). It uses StatsBomb events, lineups, minutes, and coverage-qualified 360 freeze frames. It does not use optical tracking, external ratings, or player-name adjustments.

The active contribution layer is `role_aware_fallback`. The experimental attention challenger remains available but affects rankings only when it passes its match-disjoint metric gate.

## How to read the player rating

The v2 outfield score uses the development-gated baseline VAEP feature set and grouped ElasticNet offense/defense heads with explicit role weights, VAEP/touch, open-play and set-piece-aware xT, sample-adjusted completeness, coverage-qualified off-ball value, and xD-style defensive disruption. Positive ElasticNet calibration selects the composite weights with team-disjoint folds, followed by minutes/(minutes+450) position-prior shrinkage.

Goalkeepers use a separate weighted seven-component matrix and ranking, including high-leverage saves. They are excluded from the outfield global ranking because StatsBomb Open Data does not contain native post-shot xG. Missing 360 evidence remains missing, and role labels never award rating points.

## General player summary

### Overall leaders

| Global Rank | Player Name | Team | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Attacking Midfield/Wing | Progressive Winger | 0.7739 |
| 3 | Kylian Mbappé Lottin | France | Forward | Progressive Winger | 0.6558 |
| 5 | Christian Pulisic | United States | Attacking Midfield/Wing | Progressive Winger | 0.6370 |
| 6 | Ángel Fabián Di María Hernández | Argentina | Central/Wide Midfield | Progressive Winger | 0.6357 |
| 8 | Daniel Olmo Carvajal | Spain | Attacking Midfield/Wing | Progressive Winger | 0.6259 |
| 9 | Vinícius José Paixão de Oliveira Júnior | Brazil | Central/Wide Midfield | Progressive Winger | 0.6163 |
| 10 | Marcos Javier Acuña | Argentina | Fullback/Wingback | Attacking Wingback | 0.6148 |
| 11 | Rodrigo Javier De Paul | Argentina | Defensive Midfield | Deep Playmaker | 0.6104 |
| 12 | Ismaïla Sarr | Senegal | Attacking Midfield/Wing | Progressive Winger | 0.6070 |
| 13 | Ivan Perišić | Croatia | Attacking Midfield/Wing | Wide Creator | 0.6035 |
| 14 | Raphael Dias Belloli | Brazil | Attacking Midfield/Wing | Progressive Winger | 0.6014 |
| 16 | Luke Shaw | England | Fullback/Wingback | Attacking Wingback | 0.5996 |
| 22 | Raphaël Adelino José Guerreiro | Portugal | Fullback/Wingback | Attacking Wingback | 0.5849 |
| 24 | Denzel Dumfries | Netherlands | Fullback/Wingback | Attacking Wingback | 0.5827 |
| 27 | Jude Bellingham | England | Defensive Midfield | Box-to-Box / Engine Midfielder | 0.5771 |
| 29 | Nicolás Alejandro Tagliafico | Argentina | Fullback/Wingback | Wide Creator | 0.5764 |
| 33 | Theo Bernard François Hernández | France | Fullback/Wingback | Attacking Wingback | 0.5745 |
| 35 | Heung-Min Son | South Korea | Attacking Midfield/Wing | Target Forward | 0.5729 |
| 38 | Ousmane Dembélé | France | Attacking Midfield/Wing | Progressive Winger | 0.5711 |
| 44 | Antonee Robinson | United States | Fullback/Wingback | Attacking Wingback | 0.5662 |

### Position-group leaders

| Position Group | Position Rank | Player Name | Team | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| Attacking Midfield/Wing | 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 0.7739 |
| Attacking Midfield/Wing | 4 | Christian Pulisic | United States | Progressive Winger | 0.6370 |
| Attacking Midfield/Wing | 6 | Daniel Olmo Carvajal | Spain | Progressive Winger | 0.6259 |
| Attacking Midfield/Wing | 7 | Ismaïla Sarr | Senegal | Progressive Winger | 0.6070 |
| Attacking Midfield/Wing | 8 | Ivan Perišić | Croatia | Wide Creator | 0.6035 |
| Center Back | 1 | Harry Maguire | England | Sweeper CB | 0.5562 |
| Center Back | 3 | Marcos Aoás Corrêa | Brazil | Ball-Playing Centre-Back | 0.4811 |
| Center Back | 6 | Rodrigo Hernández Cascante | Spain | Ball-Playing Centre-Back | 0.4787 |
| Center Back | 7 | Young-Gwon Kim | South Korea | Sweeper CB | 0.4779 |
| Center Back | 9 | Raphaël Varane | France | Ball-Playing Centre-Back | 0.4704 |
| Central/Wide Midfield | 1 | Ángel Fabián Di María Hernández | Argentina | Progressive Winger | 0.6357 |
| Central/Wide Midfield | 2 | Vinícius José Paixão de Oliveira Júnior | Brazil | Progressive Winger | 0.6163 |
| Central/Wide Midfield | 12 | Sofiane Boufal | Morocco | Progressive Winger | 0.5042 |
| Central/Wide Midfield | 18 | Mateo Kovačić | Croatia | Deep Playmaker / Metronome | 0.4947 |
| Central/Wide Midfield | 21 | Pedro González López | Spain | Holding Anchor | 0.4897 |
| Defensive Midfield | 1 | Rodrigo Javier De Paul | Argentina | Deep Playmaker | 0.6104 |
| Defensive Midfield | 2 | Jude Bellingham | England | Box-to-Box / Engine Midfielder | 0.5771 |
| Defensive Midfield | 3 | Adrien Rabiot | France | Holding Anchor | 0.5224 |
| Defensive Midfield | 5 | Lucas Tolentino Coelho de Lima | Brazil | Holding Anchor | 0.5191 |
| Defensive Midfield | 6 | In-Beom Hwang | South Korea | Holding Anchor | 0.5033 |
| Forward | 1 | Kylian Mbappé Lottin | France | Progressive Winger | 0.6558 |
| Forward | 6 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Target Forward | 0.5547 |
| Forward | 8 | Richarlison de Andrade | Brazil | Ball-Winner | 0.5369 |
| Forward | 11 | Julián Álvarez | Argentina | Ball-Winner | 0.5328 |
| Forward | 15 | Memphis Depay | Netherlands | Target Forward | 0.5245 |
| Fullback/Wingback | 1 | Marcos Javier Acuña | Argentina | Attacking Wingback | 0.6148 |
| Fullback/Wingback | 2 | Luke Shaw | England | Attacking Wingback | 0.5996 |
| Fullback/Wingback | 4 | Raphaël Adelino José Guerreiro | Portugal | Attacking Wingback | 0.5849 |
| Fullback/Wingback | 5 | Denzel Dumfries | Netherlands | Attacking Wingback | 0.5827 |
| Fullback/Wingback | 9 | Nicolás Alejandro Tagliafico | Argentina | Wide Creator | 0.5764 |
| Goalkeeper | 1 | Wojciech Szczęsny | Poland | Goalkeeper | 0.6318 |
| Goalkeeper | 2 | Mohammed Khalil Al Owais | Saudi Arabia | Goalkeeper | 0.6055 |
| Goalkeeper | 3 | Matthew Charles Turner | United States | Goalkeeper | 0.6048 |
| Goalkeeper | 4 | Diogo Meireles Costa | Portugal | Goalkeeper | 0.5730 |
| Goalkeeper | 5 | Yassine Bounou | Morocco | Goalkeeper | 0.5696 |

### Largest upward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Harry Maguire | England | 335 | 55 | 280 |
| Joshua Kimmich | Germany | 273 | 28 | 245 |
| Rodrigo Javier De Paul | Argentina | 250 | 11 | 239 |
| Denzel Dumfries | Netherlands | 262 | 24 | 238 |
| Gonzalo Ariel Montiel | Argentina | 367 | 138 | 229 |
| Theo Bernard François Hernández | France | 261 | 33 | 228 |
| Angelo Smit Preciado Quiñónez | Ecuador | 286 | 58 | 228 |
| Jude Bellingham | England | 254 | 27 | 227 |
| Fran Karačić | Australia | 312 | 85 | 227 |
| Pervis Josué Estupiñán Tenorio | Ecuador | 245 | 20 | 225 |

### Largest downward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Youssef En-Nesyri | Morocco | 127 | 529 | -402 |
| Jackson Irvine | Australia | 186 | 544 | -358 |
| Joel Nathaniel Campbell Samuels | Costa Rica | 150 | 481 | -331 |
| Iñaki Williams Arthuer | Ghana | 122 | 446 | -324 |
| Almoez Ali Zainalabiddin Abdulla | Qatar | 98 | 418 | -320 |
| Anthony Daniel Contreras Enríquez | Costa Rica | 99 | 395 | -296 |
| Michael Steveen Estrada Martínez | Ecuador | 88 | 382 | -294 |
| Riley McGree | Australia | 124 | 417 | -293 |
| Mitchell Thomas Duke | Australia | 90 | 380 | -290 |
| Akram Hassan Afif | Qatar | 131 | 414 | -283 |

Rank movement compares ordering, not raw rating differences, because the V4 and V5 rating scales are different.

## All-team overview

| Team | Eligible Players | Observed Players | Top Ranked Player | Top Global Rank | Total Xt | Pressure Resistance | Mean Creation | Mean Defensive | Mean Ball Security |
|---|---|---|---|---|---|---|---|---|---|
| Argentina | 20 | 20 | Lionel Andrés Messi Cuccittini | 1 | 4.0073 | 0.7447 | 0.4948 | 0.5032 | 0.5631 |
| Australia | 17 | 17 | Mathew Ryan | Not globally ranked | 1.1032 | 0.6496 | 0.4821 | 0.5524 | 0.4073 |
| Belgium | 17 | 17 | Thibaut Courtois | Not globally ranked | 1.4404 | 0.7696 | 0.5216 | 0.4606 | 0.5504 |
| Brazil | 25 | 25 | Vinícius José Paixão de Oliveira Júnior | 9 | 3.8085 | 0.7291 | 0.5582 | 0.5207 | 0.5394 |
| Cameroon | 18 | 18 | Devis Rogers Epassy Mboka | Not globally ranked | 1.0760 | 0.6971 | 0.5205 | 0.5087 | 0.5478 |
| Canada | 16 | 16 | Milan Borjan | Not globally ranked | 1.7913 | 0.7118 | 0.5417 | 0.5160 | 0.5611 |
| Costa Rica | 17 | 17 | Keylor Navas Gamboa | Not globally ranked | 0.4184 | 0.6509 | 0.3933 | 0.5727 | 0.5415 |
| Croatia | 20 | 20 | Ivan Perišić | 13 | 3.7160 | 0.7430 | 0.5431 | 0.5524 | 0.4884 |
| Denmark | 18 | 18 | Kasper Schmeichel | Not globally ranked | 1.7188 | 0.7086 | 0.5094 | 0.5011 | 0.4851 |
| Ecuador | 16 | 16 | Hernán Ismael Galíndez | Not globally ranked | 1.0181 | 0.6954 | 0.4626 | 0.5420 | 0.5067 |
| England | 19 | 19 | Luke Shaw | 16 | 2.5219 | 0.7556 | 0.5374 | 0.4677 | 0.6180 |
| France | 22 | 22 | Kylian Mbappé Lottin | 3 | 3.9248 | 0.6863 | 0.5247 | 0.5475 | 0.5195 |
| Germany | 17 | 17 | Manuel Neuer | Not globally ranked | 2.4318 | 0.7731 | 0.6119 | 0.5340 | 0.5662 |
| Ghana | 17 | 17 | Mohamed Salisu | 347 | 0.9360 | 0.6763 | 0.4424 | 0.5817 | 0.5040 |
| Iran | 20 | 20 | Mehdi Taremi | 159 | 1.2461 | 0.6687 | 0.5135 | 0.5081 | 0.4805 |
| Japan | 22 | 22 | Junya Ito | 105 | 1.5415 | 0.6415 | 0.5311 | 0.5298 | 0.3974 |
| Mexico | 18 | 18 | Francisco Guillermo Ochoa Magaña | Not globally ranked | 1.3586 | 0.6241 | 0.5345 | 0.5386 | 0.4373 |
| Morocco | 23 | 23 | Yassine Bounou | Not globally ranked | 2.4078 | 0.6771 | 0.4573 | 0.5519 | 0.4718 |
| Netherlands | 18 | 18 | Denzel Dumfries | 24 | 2.0451 | 0.7135 | 0.5206 | 0.4882 | 0.5096 |
| Poland | 16 | 16 | Wojciech Szczęsny | Not globally ranked | 1.1292 | 0.6818 | 0.4694 | 0.5129 | 0.5278 |
| Portugal | 22 | 22 | Raphaël Adelino José Guerreiro | 22 | 2.6573 | 0.7085 | 0.5171 | 0.4842 | 0.5829 |
| Qatar | 15 | 15 | Ismaeel Mohammad Mohammad | 224 | 0.7960 | 0.6995 | 0.4849 | 0.4605 | 0.5492 |
| Saudi Arabia | 20 | 20 | Mohammed Khalil Al Owais | Not globally ranked | 1.0502 | 0.6235 | 0.4610 | 0.5524 | 0.4362 |
| Senegal | 18 | 18 | Ismaïla Sarr | 12 | 1.6919 | 0.6875 | 0.5320 | 0.5050 | 0.5330 |
| Serbia | 16 | 16 | Vanja Milinković Savić | Not globally ranked | 1.3908 | 0.6740 | 0.4786 | 0.4911 | 0.4913 |
| South Korea | 19 | 19 | Heung-Min Son | 35 | 1.8015 | 0.6712 | 0.5134 | 0.5248 | 0.5144 |
| Spain | 20 | 20 | Daniel Olmo Carvajal | 8 | 2.5669 | 0.8268 | 0.4769 | 0.4885 | 0.5700 |
| Switzerland | 19 | 19 | Yann Sommer | Not globally ranked | 1.4531 | 0.7318 | 0.5231 | 0.4384 | 0.5397 |
| Tunisia | 18 | 18 | Aymen Dahmen | Not globally ranked | 1.2810 | 0.5839 | 0.5512 | 0.5960 | 0.3517 |
| United States | 18 | 18 | Christian Pulisic | 5 | 2.0784 | 0.7900 | 0.5144 | 0.4811 | 0.5368 |
| Uruguay | 17 | 17 | Sergio Rochet Álvarez | Not globally ranked | 1.4720 | 0.6460 | 0.5435 | 0.5093 | 0.4344 |
| Wales | 15 | 15 | Neco Williams | 122 | 0.8960 | 0.6856 | 0.5076 | 0.5235 | 0.4787 |

# Team-by-team summary

## Argentina

- Total xT created: 4.0073
- Total xA created: 6.7228
- Pass completion under pressure: 0.7447
- Mean defensive hull area: 647.6227
- Mean defensive density: 0.0258

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 1 | Lionel Andrés Messi Cuccittini | Forward | Progressive Winger | 733.9000 | 0.7739 | Ranked (300+ min) |
| 2 | 6 | Ángel Fabián Di María Hernández | Attacking Midfield/Wing | Progressive Winger | 304.8167 | 0.6357 | Ranked (300+ min) |
| 3 | 10 | Marcos Javier Acuña | Fullback/Wingback | Attacking Wingback | 397.4833 | 0.6148 | Ranked (300+ min) |
| 4 | 11 | Rodrigo Javier De Paul | Central/Wide Midfield | Deep Playmaker | 634.7333 | 0.6104 | Ranked (300+ min) |
| 5 | 29 | Nicolás Alejandro Tagliafico | Fullback/Wingback | Wide Creator | 393.3333 | 0.5764 | Ranked (300+ min) |


## Australia

- Total xT created: 1.1032
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | — | Mathew Ryan | Goalkeeper | Goalkeeper | 386.9167 | 0.5576 | Ranked (270+ min) |
| 3 | 97 | Aziz Eraltay Behich | Fullback/Wingback | Wide Creator | 386.9167 | 0.5377 | Ranked (300+ min) |
| 9 | 332 | Mathew Leckie | Central/Wide Midfield | Target Forward | 341.6167 | 0.4655 | Ranked (300+ min) |
| 13 | 474 | Aaron Mooy | Defensive Midfield | Holding Anchor | 386.9167 | 0.4197 | Ranked (300+ min) |
| 15 | 544 | Jackson Irvine | Defensive Midfield | Holding Anchor | 373.7500 | 0.3688 | Ranked (300+ min) |


## Belgium

- Total xT created: 1.4404
- Total xA created: 2.5562
- Pass completion under pressure: 0.7696
- Mean defensive hull area: 640.6988
- Mean defensive density: 0.0190

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 2 | — | Thibaut Courtois | Goalkeeper | Goalkeeper | 284.2667 | 0.5655 | Ranked (270+ min) |
| 3 | 50 | Kevin De Bruyne | Attacking Midfield/Wing | Progressive Winger | 284.2667 | 0.5610 | Ranked (180–299 min) |
| 9 | 193 | Thomas Meunier | Fullback/Wingback | Attacking Wingback | 217.3667 | 0.5076 | Ranked (180–299 min) |
| 10 | 270 | Timothy Castagne | Fullback/Wingback | Sweeper CB | 284.2667 | 0.4850 | Ranked (180–299 min) |
| 14 | 488 | Jan Vertonghen | Center Back | Sweeper CB | 284.2667 | 0.4137 | Ranked (180–299 min) |


## Brazil

- Total xT created: 3.8085
- Total xA created: 6.8525
- Pass completion under pressure: 0.7291
- Mean defensive hull area: 579.4863
- Mean defensive density: 0.0211

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 2 | 9 | Vinícius José Paixão de Oliveira Júnior | Attacking Midfield/Wing | Progressive Winger | 306.5833 | 0.6163 | Ranked (300+ min) |
| 3 | 14 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 330.4500 | 0.6014 | Ranked (300+ min) |
| 8 | 99 | Richarlison de Andrade | Forward | Ball-Winner | 328.2500 | 0.5369 | Ranked (300+ min) |
| 11 | 154 | Lucas Tolentino Coelho de Lima | Defensive Midfield | Holding Anchor | 318.7667 | 0.5191 | Ranked (300+ min) |
| 13 | 188 | Éder Gabriel Militão | Fullback/Wingback | Two-Way Fullback | 363.5833 | 0.5099 | Ranked (300+ min) |


## Cameroon

- Total xT created: 1.0760
- Total xA created: 1.8107
- Pass completion under pressure: 0.6971
- Mean defensive hull area: 518.5576
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 2 | — | Devis Rogers Epassy Mboka | Goalkeeper | Goalkeeper | 196.3167 | 0.5452 | Ranked (180–269 min) |
| 3 | 184 | Bryan Mbeumo | Attacking Midfield/Wing | Progressive Winger | 224.2333 | 0.5106 | Ranked (180–299 min) |
| 7 | 304 | Ngoran Suiru Fai Collins | Fullback/Wingback | Deep Playmaker | 292.5500 | 0.4739 | Ranked (180–299 min) |
| 9 | 317 | Nouhou Tolo | Fullback/Wingback | Wide Creator | 292.5500 | 0.4704 | Ranked (180–299 min) |
| 11 | 374 | André-Frank Zambo Anguissa | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 276.6500 | 0.4516 | Ranked (180–299 min) |


## Canada

- Total xT created: 1.7913
- Total xA created: 2.0764
- Pass completion under pressure: 0.7118
- Mean defensive hull area: 569.4089
- Mean defensive density: 0.0243

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 9 | — | Milan Borjan | Goalkeeper | Goalkeeper | 284.9667 | 0.4870 | Ranked (270+ min) |
| 1 | 54 | Alistair Johnston | Center Back | Attacking Wingback | 284.9667 | 0.5570 | Ranked (180–299 min) |
| 2 | 56 | Jonathan David | Forward | Target Forward | 201.6167 | 0.5556 | Ranked (180–299 min) |
| 3 | 67 | Alphonso Davies | Fullback/Wingback | Box-to-Box / Engine Midfielder | 284.9667 | 0.5511 | Ranked (180–299 min) |
| 5 | 111 | Tajon Buchanan | Attacking Midfield/Wing | Progressive Winger | 270.0833 | 0.5341 | Ranked (180–299 min) |


## Costa Rica

- Total xT created: 0.4184
- Total xA created: 0.4012
- Pass completion under pressure: 0.6509
- Mean defensive hull area: 510.3123
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 7 | — | Keylor Navas Gamboa | Goalkeeper | Goalkeeper | 294.4500 | 0.4645 | Ranked (270+ min) |
| 6 | 324 | Keysher Fuller Spence | Fullback/Wingback | Deep Playmaker | 267.9167 | 0.4694 | Ranked (180–299 min) |
| 10 | 396 | Bryan Oviedo | Fullback/Wingback | Wide Creator | 269.9000 | 0.4429 | Ranked (180–299 min) |
| 11 | 477 | Kendall Jamaal Waston Manley | Center Back | Sweeper CB | 249.4500 | 0.4182 | Ranked (180–299 min) |
| 12 | 480 | Francisco Javier Calvo Quesada | Center Back | Sweeper CB | 194.4167 | 0.4173 | Ranked (180–299 min) |


## Croatia

- Total xT created: 3.7160
- Total xA created: 5.6716
- Pass completion under pressure: 0.7430
- Mean defensive hull area: 480.9343
- Mean defensive density: 0.0281

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 13 | Ivan Perišić | Attacking Midfield/Wing | Wide Creator | 686.8167 | 0.6035 | Ranked (300+ min) |
| 2 | 66 | Borna Sosa | Fullback/Wingback | Attacking Wingback | 440.4667 | 0.5514 | Ranked (300+ min) |
| 4 | — | Dominik Livaković | Goalkeeper | Goalkeeper | 720.2833 | 0.5458 | Ranked (270+ min) |
| 8 | 190 | Andrej Kramarić | Forward | Ball-Winner | 478.4333 | 0.5091 | Ranked (300+ min) |
| 10 | 235 | Mateo Kovačić | Central/Wide Midfield | Deep Playmaker / Metronome | 649.9167 | 0.4947 | Ranked (300+ min) |


## Denmark

- Total xT created: 1.7188
- Total xA created: 2.1738
- Pass completion under pressure: 0.7086
- Mean defensive hull area: 439.0378
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | — | Kasper Schmeichel | Goalkeeper | Goalkeeper | 290.8000 | 0.5694 | Ranked (270+ min) |
| 3 | 69 | Rasmus Nissen Kristensen | Fullback/Wingback | Attacking Wingback | 234.2167 | 0.5480 | Ranked (180–299 min) |
| 5 | 110 | Joakim Mæhle | Fullback/Wingback | Attacking Wingback | 264.1000 | 0.5344 | Ranked (180–299 min) |
| 7 | 157 | Jesper Lindstrøm | Attacking Midfield/Wing | Progressive Winger | 213.4500 | 0.5188 | Ranked (180–299 min) |
| 10 | 218 | Christian Dannemann Eriksen | Central/Wide Midfield | Progressive Winger | 290.8000 | 0.4987 | Ranked (180–299 min) |


## Ecuador

- Total xT created: 1.0181
- Total xA created: 1.1631
- Pass completion under pressure: 0.6954
- Mean defensive hull area: 440.9376
- Mean defensive density: 0.0261

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 8 | — | Hernán Ismael Galíndez | Goalkeeper | Goalkeeper | 288.3833 | 0.4556 | Ranked (270+ min) |
| 1 | 20 | Pervis Josué Estupiñán Tenorio | Fullback/Wingback | Attacking Wingback | 288.3833 | 0.5858 | Ranked (180–299 min) |
| 2 | 37 | Enner Remberto Valencia Lastra | Attacking Midfield/Wing | Target Forward | 261.9167 | 0.5711 | Ranked (180–299 min) |
| 3 | 58 | Angelo Smit Preciado Quiñónez | Fullback/Wingback | Deep Playmaker | 276.2167 | 0.5554 | Ranked (180–299 min) |
| 4 | 215 | Gonzalo Jordy Plata Jiménez | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 281.4000 | 0.4994 | Ranked (180–299 min) |


## England

- Total xT created: 2.5219
- Total xA created: 4.8703
- Pass completion under pressure: 0.7556
- Mean defensive hull area: 482.2597
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 16 | Luke Shaw | Fullback/Wingback | Attacking Wingback | 457.1667 | 0.5996 | Ranked (300+ min) |
| 4 | 27 | Jude Bellingham | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 441.7667 | 0.5771 | Ranked (300+ min) |
| 6 | 55 | Harry Maguire | Center Back | Sweeper CB | 453.7167 | 0.5562 | Ranked (300+ min) |
| 13 | 301 | Harry Kane | Forward | Target Forward | 421.5167 | 0.4760 | Ranked (300+ min) |
| 15 | 358 | John Stones | Center Back | Ball-Playing Centre-Back | 464.8833 | 0.4570 | Ranked (300+ min) |


## France

- Total xT created: 3.9248
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 3 | Kylian Mbappé Lottin | Attacking Midfield/Wing | Progressive Winger | 654.3000 | 0.6558 | Ranked (300+ min) |
| 2 | 33 | Theo Bernard François Hernández | Fullback/Wingback | Attacking Wingback | 548.5000 | 0.5745 | Ranked (300+ min) |
| 3 | 38 | Ousmane Dembélé | Attacking Midfield/Wing | Progressive Winger | 448.0000 | 0.5711 | Ranked (300+ min) |
| 4 | 52 | Antoine Griezmann | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 586.0500 | 0.5590 | Ranked (300+ min) |
| 7 | 146 | Adrien Rabiot | Defensive Midfield | Holding Anchor | 529.2500 | 0.5224 | Ranked (300+ min) |


## Germany

- Total xT created: 2.4318
- Total xA created: 6.0997
- Pass completion under pressure: 0.7731
- Mean defensive hull area: 489.2536
- Mean defensive density: 0.0243

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 9 | — | Manuel Neuer | Goalkeeper | Goalkeeper | 294.0000 | 0.5283 | Ranked (270+ min) |
| 1 | 2 | Jamal Musiala | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 274.0667 | 0.6694 | Ranked (180–299 min) |
| 2 | 7 | Serge Gnabry | Attacking Midfield/Wing | Progressive Winger | 273.3333 | 0.6336 | Ranked (180–299 min) |
| 3 | 28 | Joshua Kimmich | Defensive Midfield | Attacking Wingback | 294.0000 | 0.5769 | Ranked (180–299 min) |
| 5 | 34 | David Raum | Fullback/Wingback | Attacking Wingback | 250.3000 | 0.5730 | Ranked (180–299 min) |


## Ghana

- Total xT created: 0.9360
- Total xA created: 0.9937
- Pass completion under pressure: 0.6763
- Mean defensive hull area: 432.5226
- Mean defensive density: 0.0269

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 10 | 347 | Mohamed Salisu | Center Back | Sweeper CB | 301.2000 | 0.4611 | Ranked (300+ min) |
| 11 | — | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 301.2000 | 0.4610 | Ranked (270+ min) |
| 16 | 519 | Thomas Teye Partey | Defensive Midfield | Holding Anchor | 301.2000 | 0.3973 | Ranked (300+ min) |
| 17 | 550 | Daniel Amartey | Center Back | Sweeper CB | 301.2000 | 0.3237 | Ranked (300+ min) |
| 1 | 23 | Mohammed Kudus | Attacking Midfield/Wing | Progressive Winger | 254.9333 | 0.5841 | Ranked (180–299 min) |


## Iran

- Total xT created: 1.2461
- Total xA created: 2.6253
- Pass completion under pressure: 0.6687
- Mean defensive hull area: 460.4993
- Mean defensive density: 0.0330

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 6 | 159 | Mehdi Taremi | Forward | Target Forward | 305.1000 | 0.5184 | Ranked (300+ min) |
| 15 | 398 | Morteza Pouraliganji | Center Back | Sweeper CB | 305.1000 | 0.4415 | Ranked (300+ min) |
| 20 | 526 | Seyed Majid Hosseini | Center Back | Sweeper CB | 305.1000 | 0.3917 | Ranked (300+ min) |
| 5 | 143 | Ramin Rezaeian | Fullback/Wingback | Attacking Wingback | 202.0167 | 0.5230 | Ranked (180–299 min) |
| 7 | 167 | Ehsan Hajsafi | Fullback/Wingback | Attacking Wingback | 249.9333 | 0.5150 | Ranked (180–299 min) |


## Japan

- Total xT created: 1.5415
- Total xA created: 2.4186
- Pass completion under pressure: 0.6415
- Mean defensive hull area: 501.4214
- Mean defensive density: 0.0229

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 2 | 105 | Junya Ito | Fullback/Wingback | Attacking Wingback | 346.3333 | 0.5356 | Ranked (300+ min) |
| 3 | — | Shūichi Gonda | Goalkeeper | Goalkeeper | 412.5167 | 0.5231 | Ranked (270+ min) |
| 10 | 223 | Daichi Kamada | Attacking Midfield/Wing | Ball-Winner | 337.2167 | 0.4977 | Ranked (300+ min) |
| 18 | 404 | Wataru Endo | Defensive Midfield | Box-to-Box / Engine Midfielder | 326.0167 | 0.4403 | Ranked (300+ min) |
| 22 | 513 | Maya Yoshida | Center Back | Sweeper CB | 412.5167 | 0.4022 | Ranked (300+ min) |


## Mexico

- Total xT created: 1.3586
- Total xA created: 2.6085
- Pass completion under pressure: 0.6241
- Mean defensive hull area: 639.3089
- Mean defensive density: 0.0298

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 13 | — | Francisco Guillermo Ochoa Magaña | Goalkeeper | Goalkeeper | 291.5000 | 0.4524 | Ranked (270+ min) |
| 1 | 31 | Hirving Rodrigo Lozano Bahena | Attacking Midfield/Wing | Progressive Winger | 267.3167 | 0.5758 | Ranked (180–299 min) |
| 3 | 87 | Ernesto Alexis Vega Rojas | Attacking Midfield/Wing | Progressive Winger | 194.1667 | 0.5399 | Ranked (180–299 min) |
| 5 | 149 | Luis Gerardo Chávez Magallón | Defensive Midfield | Progressive Winger | 291.5000 | 0.5214 | Ranked (180–299 min) |
| 6 | 165 | Jorge Eduardo Sánchez Ramos | Fullback/Wingback | Deep Playmaker | 183.1000 | 0.5156 | Ranked (180–299 min) |


## Morocco

- Total xT created: 2.4078
- Total xA created: 3.2076
- Pass completion under pressure: 0.6771
- Mean defensive hull area: 518.2011
- Mean defensive density: 0.0225

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | — | Yassine Bounou | Goalkeeper | Goalkeeper | 603.1500 | 0.5696 | Ranked (270+ min) |
| 2 | 76 | Yahia Attiyat allah | Fullback/Wingback | Attacking Wingback | 350.1833 | 0.5451 | Ranked (300+ min) |
| 5 | 183 | Noussair Mazraoui | Fullback/Wingback | Wide Creator | 376.8333 | 0.5107 | Ranked (300+ min) |
| 6 | 202 | Sofiane Boufal | Attacking Midfield/Wing | Progressive Winger | 476.6667 | 0.5042 | Ranked (300+ min) |
| 11 | 345 | Hakim Ziyech | Attacking Midfield/Wing | Deep Playmaker | 662.6333 | 0.4615 | Ranked (300+ min) |


## Netherlands

- Total xT created: 2.0451
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 24 | Denzel Dumfries | Fullback/Wingback | Attacking Wingback | 509.5167 | 0.5827 | Ranked (300+ min) |
| 2 | — | Andries Noppert | Goalkeeper | Goalkeeper | 509.5167 | 0.5529 | Ranked (270+ min) |
| 3 | 68 | Cody Mathès Gakpo | Forward | Progressive Winger | 460.2167 | 0.5509 | Ranked (300+ min) |
| 4 | 128 | Daley Blind | Fullback/Wingback | Attacking Wingback | 452.4833 | 0.5282 | Ranked (300+ min) |
| 5 | 136 | Memphis Depay | Forward | Target Forward | 315.5833 | 0.5245 | Ranked (300+ min) |


## Poland

- Total xT created: 1.1292
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | — | Wojciech Szczęsny | Goalkeeper | Goalkeeper | 389.7500 | 0.6318 | Ranked (270+ min) |
| 2 | 144 | Robert Lewandowski | Forward | Target Forward / Penalty-Box Anchor | 389.7500 | 0.5228 | Ranked (300+ min) |
| 3 | 168 | Bartosz Bereszyński | Fullback/Wingback | Wide Creator | 365.7333 | 0.5146 | Ranked (300+ min) |
| 7 | 330 | Piotr Zieliński | Central/Wide Midfield | Holding Anchor | 344.4167 | 0.4657 | Ranked (300+ min) |
| 10 | 394 | Jakub Piotr Kiwior | Center Back | Sweeper CB | 376.7000 | 0.4437 | Ranked (300+ min) |


## Portugal

- Total xT created: 2.6573
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 22 | Raphaël Adelino José Guerreiro | Fullback/Wingback | Attacking Wingback | 303.6167 | 0.5849 | Ranked (300+ min) |
| 2 | — | Diogo Meireles Costa | Goalkeeper | Goalkeeper | 489.4000 | 0.5730 | Ranked (270+ min) |
| 4 | 61 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 302.8000 | 0.5547 | Ranked (300+ min) |
| 5 | 63 | João Pedro Cavaco Cancelo | Fullback/Wingback | Wide Creator | 344.5500 | 0.5542 | Ranked (300+ min) |
| 6 | 75 | João Félix Sequeira | Forward | Ball-Winner | 340.2333 | 0.5451 | Ranked (300+ min) |


## Qatar

- Total xT created: 0.7960
- Total xA created: 1.1791
- Pass completion under pressure: 0.6995
- Mean defensive hull area: 451.6214
- Mean defensive density: 0.0529

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 224 | Ismaeel Mohammad Mohammad | Fullback/Wingback | Attacking Wingback | 180.6167 | 0.4975 | Ranked (180–299 min) |
| 4 | 292 | Pedro Miguel Correia | Fullback/Wingback | Deep Playmaker | 273.6000 | 0.4799 | Ranked (180–299 min) |
| 5 | 293 | Homam Alamin Ahmed | Fullback/Wingback | Wide Creator | 273.5000 | 0.4797 | Ranked (180–299 min) |
| 6 | — | Meshaal Aissa Barsham | Goalkeeper | Goalkeeper | 192.0833 | 0.4698 | Ranked (180–269 min) |
| 7 | 329 | Abdelkarim Hassan Al Haj Fadlalla | Center Back | Wide Creator | 287.4000 | 0.4657 | Ranked (180–299 min) |


## Saudi Arabia

- Total xT created: 1.0502
- Total xA created: 1.2324
- Pass completion under pressure: 0.6235
- Mean defensive hull area: 480.3764
- Mean defensive density: 0.0271

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | — | Mohammed Khalil Al Owais | Goalkeeper | Goalkeeper | 298.5500 | 0.6055 | Ranked (270+ min) |
| 2 | 19 | Salem Mohammed Al Dawsari | Attacking Midfield/Wing | Progressive Winger | 298.5500 | 0.5861 | Ranked (180–299 min) |
| 8 | 174 | Saud Abdullah Abdul Hamid | Fullback/Wingback | Attacking Wingback | 298.5500 | 0.5139 | Ranked (180–299 min) |
| 10 | 263 | Firas Tariq Nasser Al Albirakan | Central/Wide Midfield | Target Forward | 283.1333 | 0.4862 | Ranked (180–299 min) |
| 11 | 288 | Saleh Khalid Al Shehri | Forward | Target Forward | 223.4000 | 0.4807 | Ranked (180–299 min) |


## Senegal

- Total xT created: 1.6919
- Total xA created: 2.0598
- Pass completion under pressure: 0.6875
- Mean defensive hull area: 550.7399
- Mean defensive density: 0.0216

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 12 | Ismaïla Sarr | Attacking Midfield/Wing | Progressive Winger | 365.2000 | 0.6070 | Ranked (300+ min) |
| 2 | 65 | Youssouf Sabaly | Fullback/Wingback | Attacking Wingback | 387.2833 | 0.5530 | Ranked (300+ min) |
| 8 | 271 | Boulaye Dia | Forward | Target Forward | 330.0500 | 0.4849 | Ranked (300+ min) |
| 11 | — | Edouard Mendy | Goalkeeper | Goalkeeper | 387.2833 | 0.4737 | Ranked (270+ min) |
| 13 | 366 | Abdou Diallo | Center Back | Sweeper CB | 348.5833 | 0.4543 | Ranked (300+ min) |


## Serbia

- Total xT created: 1.3908
- Total xA created: 2.0346
- Pass completion under pressure: 0.6740
- Mean defensive hull area: 611.0415
- Mean defensive density: 0.0224

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 3 | — | Vanja Milinković Savić | Goalkeeper | Goalkeeper | 293.6500 | 0.5504 | Ranked (270+ min) |
| 1 | 26 | Filip Kostić | Fullback/Wingback | Attacking Wingback | 191.1833 | 0.5778 | Ranked (180–299 min) |
| 2 | 39 | Dušan Tadić | Attacking Midfield/Wing | Progressive Winger | 270.9333 | 0.5699 | Ranked (180–299 min) |
| 4 | 80 | Andrija Živković | Fullback/Wingback | Attacking Wingback | 212.0833 | 0.5422 | Ranked (180–299 min) |
| 6 | 228 | Aleksandar Mitrović | Forward | Target Forward | 279.4167 | 0.4969 | Ranked (180–299 min) |


## South Korea

- Total xT created: 1.8015
- Total xA created: 2.3972
- Pass completion under pressure: 0.6712
- Mean defensive hull area: 410.9954
- Mean defensive density: 0.0297

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 35 | Heung-Min Son | Attacking Midfield/Wing | Target Forward | 389.6500 | 0.5729 | Ranked (300+ min) |
| 2 | 45 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 340.6833 | 0.5652 | Ranked (300+ min) |
| 6 | 130 | Moon-Hwan Kim | Fullback/Wingback | Attacking Wingback | 389.6500 | 0.5277 | Ranked (300+ min) |
| 8 | — | Seung-Gyu Kim | Goalkeeper | Goalkeeper | 389.6500 | 0.5200 | Ranked (270+ min) |
| 10 | 205 | In-Beom Hwang | Central/Wide Midfield | Holding Anchor | 360.1167 | 0.5033 | Ranked (300+ min) |


## Spain

- Total xT created: 2.5669
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 8 | Daniel Olmo Carvajal | Attacking Midfield/Wing | Progressive Winger | 388.2500 | 0.6259 | Ranked (300+ min) |
| 5 | — | Unai Simón Mendibil | Goalkeeper | Goalkeeper | 413.9500 | 0.5530 | Ranked (270+ min) |
| 13 | 249 | Pedro González López | Central/Wide Midfield | Holding Anchor | 372.4000 | 0.4897 | Ranked (300+ min) |
| 14 | 295 | Rodrigo Hernández Cascante | Center Back | Ball-Playing Centre-Back | 413.9500 | 0.4787 | Ranked (300+ min) |
| 16 | 333 | Aymeric Laporte | Center Back | Sweeper CB | 316.9333 | 0.4651 | Ranked (300+ min) |


## Switzerland

- Total xT created: 1.4531
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 2 | — | Yann Sommer | Goalkeeper | Goalkeeper | 286.2833 | 0.5336 | Ranked (270+ min) |
| 11 | 338 | Manuel Obafemi Akanji | Center Back | Ball-Playing Centre-Back | 386.5833 | 0.4637 | Ranked (300+ min) |
| 12 | 346 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Attacking Wingback | 380.2333 | 0.4614 | Ranked (300+ min) |
| 13 | 363 | Breel-Donald Embolo | Forward | Ball-Winner | 330.1500 | 0.4557 | Ranked (300+ min) |
| 14 | 370 | Granit Xhaka | Defensive Midfield | Holding Anchor | 386.5833 | 0.4528 | Ranked (300+ min) |


## Tunisia

- Total xT created: 1.2810
- Total xA created: 1.9897
- Pass completion under pressure: 0.5839
- Mean defensive hull area: 396.7358
- Mean defensive density: 0.0421

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 3 | — | Aymen Dahmen | Goalkeeper | Goalkeeper | 296.5667 | 0.5405 | Ranked (270+ min) |
| 8 | 141 | Ali Abdi | Fullback/Wingback | Attacking Wingback | 213.6333 | 0.5234 | Ranked (180–299 min) |
| 11 | 214 | Issam Jebali | Forward | Ball-Winner | 196.3500 | 0.4996 | Ranked (180–299 min) |
| 12 | 269 | Aïssa Bilal Laïdouni | Defensive Midfield | Box-to-Box / Engine Midfielder | 257.2333 | 0.4850 | Ranked (180–299 min) |
| 13 | 319 | Montassar Omar Talbi | Center Back | Sweeper CB | 296.5667 | 0.4703 | Ranked (180–299 min) |


## United States

- Total xT created: 2.0784
- Total xA created: 3.2488
- Pass completion under pressure: 0.7900
- Mean defensive hull area: 451.8615
- Mean defensive density: 0.0339

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | 5 | Christian Pulisic | Central/Wide Midfield | Progressive Winger | 336.3167 | 0.6370 | Ranked (300+ min) |
| 2 | — | Matthew Charles Turner | Goalkeeper | Goalkeeper | 391.2000 | 0.6048 | Ranked (270+ min) |
| 4 | 44 | Antonee Robinson | Fullback/Wingback | Attacking Wingback | 386.2667 | 0.5662 | Ranked (300+ min) |
| 6 | 86 | Sergino Dest | Fullback/Wingback | Attacking Wingback | 307.5667 | 0.5399 | Ranked (300+ min) |
| 7 | 91 | Timothy Weah | Forward | Ball-Winner | 317.8833 | 0.5393 | Ranked (300+ min) |


## Uruguay

- Total xT created: 1.4720
- Total xA created: 1.9893
- Pass completion under pressure: 0.6460
- Mean defensive hull area: 457.0204
- Mean defensive density: 0.0260

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1 | — | Sergio Rochet Álvarez | Goalkeeper | Goalkeeper | 298.0833 | 0.5541 | Ranked (270+ min) |
| 2 | 102 | Facundo Pellistri Rebollo | Central/Wide Midfield | Ball-Winner | 191.2333 | 0.5362 | Ranked (180–299 min) |
| 3 | 107 | Darwin Gabriel Núñez Ribeiro | Forward | Target Forward | 249.2167 | 0.5351 | Ranked (180–299 min) |
| 4 | 134 | Mathías Olivera Miramontes | Fullback/Wingback | Wide Creator | 263.6333 | 0.5259 | Ranked (180–299 min) |
| 6 | 163 | José María Giménez de Vargas | Center Back | Sweeper CB | 298.0833 | 0.5158 | Ranked (180–299 min) |


## Wales

- Total xT created: 0.8960
- Total xA created: 1.2536
- Pass completion under pressure: 0.6856
- Mean defensive hull area: 599.2348
- Mean defensive density: 0.0252

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 2 | 122 | Neco Williams | Fullback/Wingback | Wide Creator | 216.3833 | 0.5312 | Ranked (180–299 min) |
| 3 | 198 | Connor Roberts | Fullback/Wingback | Deep Playmaker | 215.5333 | 0.5062 | Ranked (180–299 min) |
| 6 | 287 | Kieffer Roberto Francisco Moore | Forward | Target Forward / Penalty-Box Anchor | 251.7167 | 0.4807 | Ranked (180–299 min) |
| 7 | 341 | Gareth Frank Bale | Attacking Midfield/Wing | Target Forward | 247.7167 | 0.4623 | Ranked (180–299 min) |
| 9 | — | Wayne Hennessey | Goalkeeper | Goalkeeper | 202.7167 | 0.4616 | Ranked (180–269 min) |


## Interpretation boundary

These rankings summarize performance in the 2022 tournament sample. They are not transfer valuations, causal estimates, medical assessments, or replacements for video and scouting review.
