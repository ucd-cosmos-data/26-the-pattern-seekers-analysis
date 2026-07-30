# World Cup V5 Role-Aware Final Report

## Executive summary

This report consolidates **32 national teams** and **142 players meeting the 300-minute cutoff**. It uses StatsBomb events, lineups, minutes, and coverage-qualified 360 freeze frames. It does not use optical tracking, external ratings, or player-name adjustments.

The active contribution layer is `attention`. The experimental attention challenger remains available but affects rankings only when it passes its match-disjoint metric gate.

## How to read the player rating

The V5 outfield score combines independently scaled offensive and defensive VAEP, VAEP/touch, open-play and set-piece-aware xT, match-grouped ElasticNet contribution, quality-adjusted top-three completeness, and coverage-qualified off-ball value. It is then reliability-shrunk using tournament minutes.

Goalkeepers use a separate goalkeeper-only matrix and ranking. They are excluded from the outfield global ranking because StatsBomb Open Data does not contain native post-shot xG. Missing 360 evidence remains missing, and role labels never award rating points.

## General player summary

### Overall leaders

| Global Rank | Player Name | Team | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Attacking Midfield/Wing | Progressive Winger | 0.7870 |
| 2 | Kylian Mbappé Lottin | France | Forward | Progressive Winger | 0.7401 |
| 3 | Christian Pulisic | United States | Attacking Midfield/Wing | Progressive Winger | 0.7066 |
| 4 | Julián Álvarez | Argentina | Forward | Target Forward | 0.7024 |
| 5 | Ángel Fabián Di María Hernández | Argentina | Central/Wide Midfield | Progressive Winger | 0.7023 |
| 6 | Richarlison de Andrade | Brazil | Forward | Target Forward | 0.7007 |
| 7 | Vinícius José Paixão de Oliveira Júnior | Brazil | Central/Wide Midfield | Progressive Winger | 0.6966 |
| 8 | Daniel Olmo Carvajal | Spain | Attacking Midfield/Wing | Progressive Winger | 0.6955 |
| 9 | Mehdi Taremi | Iran | Forward | Target Forward | 0.6946 |
| 10 | Bruno Miguel Borges Fernandes | Portugal | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 0.6935 |
| 11 | Antoine Griezmann | France | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 0.6900 |
| 12 | Ismaïla Sarr | Senegal | Attacking Midfield/Wing | Target Forward | 0.6893 |
| 13 | Cody Mathès Gakpo | Netherlands | Attacking Midfield/Wing | Progressive Winger | 0.6868 |
| 14 | Raphael Dias Belloli | Brazil | Attacking Midfield/Wing | Progressive Winger | 0.6856 |
| 15 | João Félix Sequeira | Portugal | Attacking Midfield/Wing | Target Forward | 0.6783 |
| 16 | Memphis Depay | Netherlands | Forward | Target Forward | 0.6755 |
| 17 | Ousmane Dembélé | France | Attacking Midfield/Wing | Progressive Winger | 0.6709 |
| 18 | Robert Lewandowski | Poland | Forward | Target Forward / Penalty-Box Anchor | 0.6684 |
| 19 | Ivan Perišić | Croatia | Attacking Midfield/Wing | Wide Creator | 0.6590 |
| 20 | Breel-Donald Embolo | Switzerland | Forward | Target Forward | 0.6571 |

### Position-group leaders

| Position Group | Position Rank | Player Name | Team | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| Attacking Midfield/Wing | 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 0.7870 |
| Attacking Midfield/Wing | 2 | Christian Pulisic | United States | Progressive Winger | 0.7066 |
| Attacking Midfield/Wing | 3 | Daniel Olmo Carvajal | Spain | Progressive Winger | 0.6955 |
| Attacking Midfield/Wing | 4 | Bruno Miguel Borges Fernandes | Portugal | Hybrid Playmaker / Roaming Creator | 0.6935 |
| Attacking Midfield/Wing | 5 | Antoine Griezmann | France | Hybrid Playmaker / Roaming Creator | 0.6900 |
| Center Back | 1 | Harry Maguire | England | Deep Playmaker | 0.4010 |
| Center Back | 2 | Manuel Obafemi Akanji | Switzerland | Ball-Playing Centre-Back | 0.3784 |
| Center Back | 3 | Young-Gwon Kim | South Korea | Sweeper CB | 0.3765 |
| Center Back | 4 | Kléper Laveran Lima Ferreira | Portugal | Sweeper CB | 0.3755 |
| Center Back | 5 | Rodrigo Hernández Cascante | Spain | Ball-Playing Centre-Back | 0.3626 |
| Central/Wide Midfield | 1 | Ángel Fabián Di María Hernández | Argentina | Progressive Winger | 0.7023 |
| Central/Wide Midfield | 2 | Vinícius José Paixão de Oliveira Júnior | Brazil | Progressive Winger | 0.6966 |
| Central/Wide Midfield | 3 | Mateo Kovačić | Croatia | Box-to-Box / Engine Midfielder | 0.6438 |
| Central/Wide Midfield | 4 | Sofiane Boufal | Morocco | Box-to-Box / Engine Midfielder | 0.6350 |
| Central/Wide Midfield | 5 | Alexis Mac Allister | Argentina | Ball-Winner | 0.6272 |
| Defensive Midfield | 1 | Jude Bellingham | England | Box-to-Box / Engine Midfielder | 0.5737 |
| Defensive Midfield | 2 | Rodrigo Javier De Paul | Argentina | Box-to-Box / Engine Midfielder | 0.5586 |
| Defensive Midfield | 3 | Adrien Rabiot | France | Ball-Winner | 0.5516 |
| Defensive Midfield | 4 | Lucas Tolentino Coelho de Lima | Brazil | Ball-Winner | 0.5408 |
| Defensive Midfield | 5 | Frenkie de Jong | Netherlands | Box-to-Box / Engine Midfielder | 0.4931 |
| Forward | 1 | Kylian Mbappé Lottin | France | Progressive Winger | 0.7401 |
| Forward | 2 | Julián Álvarez | Argentina | Target Forward | 0.7024 |
| Forward | 3 | Richarlison de Andrade | Brazil | Target Forward | 0.7007 |
| Forward | 4 | Mehdi Taremi | Iran | Target Forward | 0.6946 |
| Forward | 5 | Memphis Depay | Netherlands | Target Forward | 0.6755 |
| Fullback/Wingback | 1 | Theo Bernard François Hernández | France | Attacking Wingback | 0.5994 |
| Fullback/Wingback | 2 | Raphaël Adelino José Guerreiro | Portugal | Wide Creator | 0.5960 |
| Fullback/Wingback | 3 | Marcos Javier Acuña | Argentina | Attacking Wingback | 0.5892 |
| Fullback/Wingback | 4 | Daley Blind | Netherlands | Wide Creator | 0.5828 |
| Fullback/Wingback | 5 | Luke Shaw | England | Attacking Wingback | 0.5711 |
| Goalkeeper | 1 | Wojciech Szczęsny | Poland | Goalkeeper | 0.6156 |
| Goalkeeper | 2 | Dominik Livaković | Croatia | Goalkeeper | 0.5805 |
| Goalkeeper | 3 | Matthew Charles Turner | United States | Goalkeeper | 0.5790 |
| Goalkeeper | 4 | Yassine Bounou | Morocco | Goalkeeper | 0.5696 |
| Goalkeeper | 5 | Unai Simón Mendibil | Spain | Goalkeeper | 0.5695 |

### Largest upward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Aurélien Djani Tchouaméni | France | 103 | 84 | 19 |
| Bruno Miguel Borges Fernandes | Portugal | 27 | 10 | 17 |
| Luka Modrić | Croatia | 51 | 34 | 17 |
| Carlos Henrique Casimiro | Brazil | 85 | 68 | 17 |
| Sergio Busquets i Burgos | Spain | 98 | 81 | 17 |
| Thomas Teye Partey | Ghana | 102 | 85 | 17 |
| Piotr Zieliński | Poland | 48 | 32 | 16 |
| Sofyan Amrabat | Morocco | 105 | 90 | 15 |
| Theo Bernard François Hernández | France | 52 | 38 | 14 |
| Sergino Dest | United States | 61 | 47 | 14 |

### Largest downward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Jackson Irvine | Australia | 39 | 58 | -19 |
| Harry Maguire | England | 70 | 87 | -17 |
| Cristiano Ronaldo dos Santos Aveiro | Portugal | 6 | 22 | -16 |
| Marcos Javier Acuña | Argentina | 26 | 41 | -15 |
| Youssef En-Nesyri | Morocco | 29 | 42 | -13 |
| Kléper Laveran Lima Ferreira | Portugal | 80 | 93 | -13 |
| João Pedro Cavaco Cancelo | Portugal | 42 | 54 | -12 |
| John Stones | England | 84 | 96 | -12 |
| Morteza Pouraliganji | Iran | 89 | 101 | -12 |
| Aymeric Laporte | Spain | 91 | 103 | -12 |

Rank movement compares ordering, not raw rating differences, because the V4 and V5 rating scales are different.

## All-team overview

| Team | Eligible Players | Observed Players | Top Ranked Player | Top Global Rank | Total Xt | Pressure Resistance |
|---|---|---|---|---|---|---|
| Argentina | 13 | 24 | Lionel Andrés Messi Cuccittini | 1 | 3.4707 | 0.7447 |
| Australia | 7 | 20 | Mathew Leckie | 35 | 0.9578 | 0.6496 |
| Belgium | 0 | 20 | Jan Vertonghen | Not globally ranked | 1.1828 | 0.7696 |
| Brazil | 9 | 26 | Richarlison de Andrade | 6 | 3.3449 | 0.7291 |
| Cameroon | 0 | 22 | Nouhou Tolo | Not globally ranked | 0.9097 | 0.6971 |
| Canada | 0 | 19 | Steven de Sousa Vitoria | Not globally ranked | 1.4035 | 0.7118 |
| Costa Rica | 0 | 22 | Keylor Navas Gamboa | Not globally ranked | 0.3533 | 0.6509 |
| Croatia | 10 | 20 | Ivan Perišić | 19 | 3.0319 | 0.7430 |
| Denmark | 0 | 20 | Christian Dannemann Eriksen | Not globally ranked | 1.5191 | 0.7086 |
| Ecuador | 0 | 18 | Pervis Josué Estupiñán Tenorio | Not globally ranked | 0.8517 | 0.6954 |
| England | 7 | 20 | Harry Kane | 23 | 2.2192 | 0.7556 |
| France | 12 | 24 | Kylian Mbappé Lottin | 2 | 3.4775 | 0.6863 |
| Germany | 0 | 20 | Antonio Rüdiger | Not globally ranked | 2.3732 | 0.7731 |
| Ghana | 4 | 20 | Lawrence Ati-Zigi | Not globally ranked | 0.7889 | 0.6763 |
| Iran | 3 | 21 | Mehdi Taremi | 9 | 1.0611 | 0.6687 |
| Japan | 5 | 22 | Daichi Kamada | 37 | 1.3961 | 0.6415 |
| Mexico | 0 | 21 | Héctor Alfredo Moreno Herrera | Not globally ranked | 1.2560 | 0.6241 |
| Morocco | 13 | 25 | Sofiane Boufal | 26 | 2.0022 | 0.6771 |
| Netherlands | 9 | 21 | Cody Mathès Gakpo | 13 | 1.7121 | 0.7135 |
| Poland | 8 | 21 | Robert Lewandowski | 18 | 0.9662 | 0.6818 |
| Portugal | 9 | 24 | Bruno Miguel Borges Fernandes | 10 | 2.1783 | 0.7085 |
| Qatar | 0 | 20 | Akram Hassan Afif | Not globally ranked | 0.6696 | 0.6995 |
| Saudi Arabia | 0 | 23 | Salem Mohammed Al Dawsari | Not globally ranked | 0.9437 | 0.6235 |
| Senegal | 6 | 20 | Ismaïla Sarr | 12 | 1.4521 | 0.6875 |
| Serbia | 0 | 23 | Nikola Milenković | Not globally ranked | 1.1887 | 0.6740 |
| South Korea | 7 | 21 | Heung-Min Son | 27 | 1.4549 | 0.6712 |
| Spain | 6 | 21 | Daniel Olmo Carvajal | 8 | 2.1806 | 0.8268 |
| Switzerland | 5 | 24 | Breel-Donald Embolo | 20 | 1.2567 | 0.7318 |
| Tunisia | 0 | 21 | Ellyes Joris Skhiri | Not globally ranked | 1.1588 | 0.5839 |
| United States | 9 | 20 | Christian Pulisic | 3 | 1.6176 | 0.7900 |
| Uruguay | 0 | 19 | José María Giménez de Vargas | Not globally ranked | 1.3303 | 0.6460 |
| Wales | 0 | 18 | Chris Mepham | Not globally ranked | 0.7680 | 0.6856 |

# Team-by-team summary

## Argentina

- Total xT created: 3.4707
- Total xA created: 6.7228
- Pass completion under pressure: 0.7447
- Mean defensive hull area: 647.6227
- Mean defensive density: 0.0258

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 1 | Lionel Andrés Messi Cuccittini | Forward | Progressive Winger | 733.9000 | 0.7870 | Ranked (300+ min) |
| 2.0000 | 4 | Julián Álvarez | Attacking Midfield/Wing | Target Forward | 485.2333 | 0.7024 | Ranked (300+ min) |
| 3.0000 | 5 | Ángel Fabián Di María Hernández | Attacking Midfield/Wing | Progressive Winger | 304.8167 | 0.7023 | Ranked (300+ min) |
| 4.0000 | 29 | Alexis Mac Allister | Central/Wide Midfield | Ball-Winner | 552.3500 | 0.6272 | Ranked (300+ min) |
| 5.0000 | 41 | Marcos Javier Acuña | Fullback/Wingback | Attacking Wingback | 397.4833 | 0.5892 | Ranked (300+ min) |


## Australia

- Total xT created: 0.9578
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 35 | Mathew Leckie | Central/Wide Midfield | Target Forward | 341.6167 | 0.6018 | Ranked (300+ min) |
| 2.0000 | — | Mathew Ryan | Goalkeeper | Goalkeeper | 386.9167 | 0.5469 | Ranked (300+ min) |
| 3.0000 | 58 | Jackson Irvine | Defensive Midfield | Ball-Winner | 373.7500 | 0.5304 | Ranked (300+ min) |
| 4.0000 | 64 | Aziz Eraltay Behich | Fullback/Wingback | Wide Creator | 386.9167 | 0.5045 | Ranked (300+ min) |
| 5.0000 | 88 | Aaron Mooy | Defensive Midfield | Box-to-Box Runner | 386.9167 | 0.3950 | Ranked (300+ min) |


## Belgium

- Total xT created: 1.1828
- Total xA created: 2.5562
- Pass completion under pressure: 0.7696
- Mean defensive hull area: 640.6988
- Mean defensive density: 0.0190

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Jan Vertonghen | Center Back | — | 284.2667 | — | Coverage only (<300 min) |
| — | — | Kevin De Bruyne | Attacking Midfield/Wing | — | 284.2667 | — | Coverage only (<300 min) |
| — | — | Thibaut Courtois | Goalkeeper | — | 284.2667 | — | Coverage only (<300 min) |
| — | — | Axel Witsel | Defensive Midfield | — | 284.2667 | — | Coverage only (<300 min) |
| — | — | Timothy Castagne | Fullback/Wingback | — | 284.2667 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Brazil

- Total xT created: 3.3449
- Total xA created: 6.8525
- Pass completion under pressure: 0.7291
- Mean defensive hull area: 579.4863
- Mean defensive density: 0.0211

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 6 | Richarlison de Andrade | Forward | Target Forward | 328.2500 | 0.7007 | Ranked (300+ min) |
| 2.0000 | 7 | Vinícius José Paixão de Oliveira Júnior | Attacking Midfield/Wing | Progressive Winger | 306.5833 | 0.6966 | Ranked (300+ min) |
| 3.0000 | 14 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 330.4500 | 0.6856 | Ranked (300+ min) |
| 4.0000 | 53 | Lucas Tolentino Coelho de Lima | Defensive Midfield | Ball-Winner | 318.7667 | 0.5408 | Ranked (300+ min) |
| 5.0000 | 61 | Éder Gabriel Militão | Fullback/Wingback | Box-to-Box Runner | 363.5833 | 0.5223 | Ranked (300+ min) |


## Cameroon

- Total xT created: 0.9097
- Total xA created: 1.8107
- Pass completion under pressure: 0.6971
- Mean defensive hull area: 518.5576
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Nouhou Tolo | Fullback/Wingback | — | 292.5500 | — | Coverage only (<300 min) |
| — | — | Ngoran Suiru Fai Collins | Fullback/Wingback | — | 292.5500 | — | Coverage only (<300 min) |
| — | — | André-Frank Zambo Anguissa | Central/Wide Midfield | — | 276.6500 | — | Coverage only (<300 min) |
| — | — | Jean-Eric Maxim Choupo-Moting | Forward | — | 269.9833 | — | Coverage only (<300 min) |
| — | — | Bryan Mbeumo | Attacking Midfield/Wing | — | 224.2333 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Canada

- Total xT created: 1.4035
- Total xA created: 2.0764
- Pass completion under pressure: 0.7118
- Mean defensive hull area: 569.4089
- Mean defensive density: 0.0243

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Steven de Sousa Vitoria | Center Back | — | 284.9667 | — | Coverage only (<300 min) |
| — | — | Alphonso Davies | Fullback/Wingback | — | 284.9667 | — | Coverage only (<300 min) |
| — | — | Milan Borjan | Goalkeeper | — | 284.9667 | — | Coverage only (<300 min) |
| — | — | Kamal Miller | Center Back | — | 284.9667 | — | Coverage only (<300 min) |
| — | — | Alistair Johnston | Center Back | — | 284.9667 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Costa Rica

- Total xT created: 0.3533
- Total xA created: 0.4012
- Pass completion under pressure: 0.6509
- Mean defensive hull area: 510.3123
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Keylor Navas Gamboa | Goalkeeper | — | 294.4500 | — | Coverage only (<300 min) |
| — | — | Óscar Esau Duarte Gaitán | Center Back | — | 294.4500 | — | Coverage only (<300 min) |
| — | — | Joel Nathaniel Campbell Samuels | Forward | — | 292.4333 | — | Coverage only (<300 min) |
| — | — | Yeltsin Ignacio Tejeda Valverde | Central/Wide Midfield | — | 286.9500 | — | Coverage only (<300 min) |
| — | — | Bryan Oviedo | Fullback/Wingback | — | 269.9000 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Croatia

- Total xT created: 3.0319
- Total xA created: 5.6716
- Pass completion under pressure: 0.7430
- Mean defensive hull area: 480.9343
- Mean defensive density: 0.0281

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 19 | Ivan Perišić | Attacking Midfield/Wing | Wide Creator | 686.8167 | 0.6590 | Ranked (300+ min) |
| 2.0000 | 25 | Mateo Kovačić | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 649.9167 | 0.6438 | Ranked (300+ min) |
| 3.0000 | 28 | Andrej Kramarić | Forward | Target Forward | 478.4333 | 0.6326 | Ranked (300+ min) |
| 4.0000 | 34 | Luka Modrić | Central/Wide Midfield | Deep Playmaker / Metronome | 672.6667 | 0.6046 | Ranked (300+ min) |
| 5.0000 | — | Dominik Livaković | Goalkeeper | Goalkeeper | 720.2833 | 0.5805 | Ranked (300+ min) |


## Denmark

- Total xT created: 1.5191
- Total xA created: 2.1738
- Pass completion under pressure: 0.7086
- Mean defensive hull area: 439.0378
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Christian Dannemann Eriksen | Central/Wide Midfield | — | 290.8000 | — | Coverage only (<300 min) |
| — | — | Pierre-Emile Højbjerg | Central/Wide Midfield | — | 290.8000 | — | Coverage only (<300 min) |
| — | — | Kasper Schmeichel | Goalkeeper | — | 290.8000 | — | Coverage only (<300 min) |
| — | — | Andreas Christensen | Center Back | — | 290.8000 | — | Coverage only (<300 min) |
| — | — | Joachim Andersen | Center Back | — | 290.8000 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Ecuador

- Total xT created: 0.8517
- Total xA created: 1.1631
- Pass completion under pressure: 0.6954
- Mean defensive hull area: 440.9376
- Mean defensive density: 0.0261

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Pervis Josué Estupiñán Tenorio | Fullback/Wingback | — | 288.3833 | — | Coverage only (<300 min) |
| — | — | Felix Eduardo Torres Caicedo | Center Back | — | 288.3833 | — | Coverage only (<300 min) |
| — | — | Hernán Ismael Galíndez | Goalkeeper | — | 288.3833 | — | Coverage only (<300 min) |
| — | — | Piero Martín Hincapié Reyna | Center Back | — | 288.3833 | — | Coverage only (<300 min) |
| — | — | Moisés Isaac Caicedo Corozo | Defensive Midfield | — | 282.9667 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## England

- Total xT created: 2.2192
- Total xA created: 4.8703
- Pass completion under pressure: 0.7556
- Mean defensive hull area: 482.2597
- Mean defensive density: 0.0278

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 23 | Harry Kane | Forward | Target Forward | 421.5167 | 0.6516 | Ranked (300+ min) |
| 2.0000 | 44 | Jude Bellingham | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 441.7667 | 0.5737 | Ranked (300+ min) |
| 3.0000 | 46 | Luke Shaw | Fullback/Wingback | Attacking Wingback | 457.1667 | 0.5711 | Ranked (300+ min) |
| 4.0000 | — | Jordan Pickford | Goalkeeper | Goalkeeper | 486.3333 | 0.4751 | Ranked (300+ min) |
| 5.0000 | 76 | Declan Rice | Defensive Midfield | Ball-Winner | 449.5500 | 0.4492 | Ranked (300+ min) |


## France

- Total xT created: 3.4775
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 2 | Kylian Mbappé Lottin | Attacking Midfield/Wing | Progressive Winger | 654.3000 | 0.7401 | Ranked (300+ min) |
| 2.0000 | 11 | Antoine Griezmann | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 586.0500 | 0.6900 | Ranked (300+ min) |
| 3.0000 | 17 | Ousmane Dembélé | Attacking Midfield/Wing | Progressive Winger | 448.0000 | 0.6709 | Ranked (300+ min) |
| 4.0000 | 21 | Olivier Giroud | Forward | Target Forward / Penalty-Box Anchor | 432.6167 | 0.6564 | Ranked (300+ min) |
| 5.0000 | 38 | Theo Bernard François Hernández | Fullback/Wingback | Attacking Wingback | 548.5000 | 0.5994 | Ranked (300+ min) |


## Germany

- Total xT created: 2.3732
- Total xA created: 6.0997
- Pass completion under pressure: 0.7731
- Mean defensive hull area: 489.2536
- Mean defensive density: 0.0243

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Antonio Rüdiger | Center Back | — | 294.0000 | — | Coverage only (<300 min) |
| — | — | Manuel Neuer | Goalkeeper | — | 294.0000 | — | Coverage only (<300 min) |
| — | — | Joshua Kimmich | Defensive Midfield | — | 294.0000 | — | Coverage only (<300 min) |
| — | — | Niklas Süle | Center Back | — | 287.5833 | — | Coverage only (<300 min) |
| — | — | Jamal Musiala | Attacking Midfield/Wing | — | 274.0667 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Ghana

- Total xT created: 0.7889
- Total xA created: 0.9937
- Pass completion under pressure: 0.6763
- Mean defensive hull area: 432.5226
- Mean defensive density: 0.0269

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | — | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 301.2000 | 0.4816 | Ranked (300+ min) |
| 2.0000 | 85 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 301.2000 | 0.4215 | Ranked (300+ min) |
| 3.0000 | 100 | Mohamed Salisu | Center Back | Sweeper CB | 301.2000 | 0.3393 | Ranked (300+ min) |
| 4.0000 | 119 | Daniel Amartey | Center Back | Sweeper CB | 301.2000 | 0.2526 | Ranked (300+ min) |
| — | — | Iñaki Williams Arthuer | Forward | — | 272.7833 | — | Coverage only (<300 min) |


## Iran

- Total xT created: 1.0611
- Total xA created: 2.6253
- Pass completion under pressure: 0.6687
- Mean defensive hull area: 460.4993
- Mean defensive density: 0.0330

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 9 | Mehdi Taremi | Forward | Target Forward | 305.1000 | 0.6946 | Ranked (300+ min) |
| 2.0000 | 101 | Morteza Pouraliganji | Center Back | Sweeper CB | 305.1000 | 0.3195 | Ranked (300+ min) |
| 3.0000 | 120 | Seyed Majid Hosseini | Center Back | Sweeper CB | 305.1000 | 0.2498 | Ranked (300+ min) |
| — | — | Ehsan Hajsafi | Fullback/Wingback | — | 249.9333 | — | Coverage only (<300 min) |
| — | — | Saeid Ezatolahi Afagh | Defensive Midfield | — | 240.1500 | — | Coverage only (<300 min) |


## Japan

- Total xT created: 1.3961
- Total xA created: 2.4186
- Pass completion under pressure: 0.6415
- Mean defensive hull area: 501.4214
- Mean defensive density: 0.0229

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 37 | Daichi Kamada | Attacking Midfield/Wing | Target Forward | 337.2167 | 0.6008 | Ranked (300+ min) |
| 2.0000 | — | Shūichi Gonda | Goalkeeper | Goalkeeper | 412.5167 | 0.5341 | Ranked (300+ min) |
| 3.0000 | 63 | Junya Ito | Fullback/Wingback | Attacking Wingback | 346.3333 | 0.5126 | Ranked (300+ min) |
| 4.0000 | 77 | Wataru Endo | Defensive Midfield | Ball-Winner | 326.0167 | 0.4487 | Ranked (300+ min) |
| 5.0000 | 122 | Maya Yoshida | Center Back | Sweeper CB | 412.5167 | 0.2473 | Ranked (300+ min) |


## Mexico

- Total xT created: 1.2560
- Total xA created: 2.6085
- Pass completion under pressure: 0.6241
- Mean defensive hull area: 639.3089
- Mean defensive density: 0.0298

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Héctor Alfredo Moreno Herrera | Center Back | — | 291.5000 | — | Coverage only (<300 min) |
| — | — | Jesús Daniel Gallardo Vasconcelos | Fullback/Wingback | — | 291.5000 | — | Coverage only (<300 min) |
| — | — | Francisco Guillermo Ochoa Magaña | Goalkeeper | — | 291.5000 | — | Coverage only (<300 min) |
| — | — | César Jasib Montes Castro | Center Back | — | 291.5000 | — | Coverage only (<300 min) |
| — | — | Luis Gerardo Chávez Magallón | Defensive Midfield | — | 291.5000 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Morocco

- Total xT created: 2.0022
- Total xA created: 3.2076
- Pass completion under pressure: 0.6771
- Mean defensive hull area: 518.2011
- Mean defensive density: 0.0225

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 26 | Sofiane Boufal | Attacking Midfield/Wing | Box-to-Box / Engine Midfielder | 476.6667 | 0.6350 | Ranked (300+ min) |
| 2.0000 | 39 | Hakim Ziyech | Attacking Midfield/Wing | Box-to-Box Runner | 662.6333 | 0.5978 | Ranked (300+ min) |
| 3.0000 | 42 | Youssef En-Nesyri | Forward | Target Forward / Penalty-Box Anchor | 553.8167 | 0.5838 | Ranked (300+ min) |
| 4.0000 | 45 | Azzedine Ounahi | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 589.2500 | 0.5722 | Ranked (300+ min) |
| 5.0000 | — | Yassine Bounou | Goalkeeper | Goalkeeper | 603.1500 | 0.5696 | Ranked (300+ min) |


## Netherlands

- Total xT created: 1.7121
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 13 | Cody Mathès Gakpo | Forward | Progressive Winger | 460.2167 | 0.6868 | Ranked (300+ min) |
| 2.0000 | 16 | Memphis Depay | Forward | Target Forward | 315.5833 | 0.6755 | Ranked (300+ min) |
| 3.0000 | 43 | Daley Blind | Fullback/Wingback | Wide Creator | 452.4833 | 0.5828 | Ranked (300+ min) |
| 4.0000 | — | Andries Noppert | Goalkeeper | Goalkeeper | 509.5167 | 0.5469 | Ranked (300+ min) |
| 5.0000 | 59 | Denzel Dumfries | Fullback/Wingback | Attacking Wingback | 509.5167 | 0.5299 | Ranked (300+ min) |


## Poland

- Total xT created: 0.9662
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 18 | Robert Lewandowski | Forward | Target Forward / Penalty-Box Anchor | 389.7500 | 0.6684 | Ranked (300+ min) |
| 2.0000 | — | Wojciech Szczęsny | Goalkeeper | Goalkeeper | 389.7500 | 0.6156 | Ranked (300+ min) |
| 3.0000 | 32 | Piotr Zieliński | Central/Wide Midfield | Ball-Winner | 344.4167 | 0.6106 | Ranked (300+ min) |
| 4.0000 | 70 | Bartosz Bereszyński | Fullback/Wingback | Wide Creator | 365.7333 | 0.4876 | Ranked (300+ min) |
| 5.0000 | 83 | Grzegorz Krychowiak | Defensive Midfield | Ball-Winner | 347.8833 | 0.4309 | Ranked (300+ min) |


## Portugal

- Total xT created: 2.1783
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 10 | Bruno Miguel Borges Fernandes | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 384.9500 | 0.6935 | Ranked (300+ min) |
| 2.0000 | 15 | João Félix Sequeira | Forward | Target Forward | 340.2333 | 0.6783 | Ranked (300+ min) |
| 3.0000 | 22 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 302.8000 | 0.6545 | Ranked (300+ min) |
| 4.0000 | 31 | Bernardo Mota Veiga de Carvalho e Silva | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 382.1000 | 0.6221 | Ranked (300+ min) |
| 5.0000 | 40 | Raphaël Adelino José Guerreiro | Fullback/Wingback | Wide Creator | 303.6167 | 0.5960 | Ranked (300+ min) |


## Qatar

- Total xT created: 0.6696
- Total xA created: 1.1791
- Pass completion under pressure: 0.6995
- Mean defensive hull area: 451.6214
- Mean defensive density: 0.0529

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Akram Hassan Afif | Forward | — | 287.4000 | — | Coverage only (<300 min) |
| — | — | Boualem Khoukhi | Center Back | — | 287.4000 | — | Coverage only (<300 min) |
| — | — | Abdelkarim Hassan Al Haj Fadlalla | Center Back | — | 287.4000 | — | Coverage only (<300 min) |
| — | — | Pedro Miguel Correia | Fullback/Wingback | — | 273.6000 | — | Coverage only (<300 min) |
| — | — | Homam Alamin Ahmed | Fullback/Wingback | — | 273.5000 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Saudi Arabia

- Total xT created: 0.9437
- Total xA created: 1.2324
- Pass completion under pressure: 0.6235
- Mean defensive hull area: 480.3764
- Mean defensive density: 0.0271

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Salem Mohammed Al Dawsari | Attacking Midfield/Wing | — | 298.5500 | — | Coverage only (<300 min) |
| — | — | Mohammed Kanoo | Forward | — | 298.5500 | — | Coverage only (<300 min) |
| — | — | Mohammed Khalil Al Owais | Goalkeeper | — | 298.5500 | — | Coverage only (<300 min) |
| — | — | Saud Abdullah Abdul Hamid | Fullback/Wingback | — | 298.5500 | — | Coverage only (<300 min) |
| — | — | Firas Tariq Nasser Al Albirakan | Central/Wide Midfield | — | 283.1333 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Senegal

- Total xT created: 1.4521
- Total xA created: 2.0598
- Pass completion under pressure: 0.6875
- Mean defensive hull area: 550.7399
- Mean defensive density: 0.0216

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 12 | Ismaïla Sarr | Attacking Midfield/Wing | Target Forward | 365.2000 | 0.6893 | Ranked (300+ min) |
| 2.0000 | 33 | Boulaye Dia | Forward | Target Forward | 330.0500 | 0.6086 | Ranked (300+ min) |
| 3.0000 | 52 | Youssouf Sabaly | Fullback/Wingback | Attacking Wingback | 387.2833 | 0.5471 | Ranked (300+ min) |
| 4.0000 | — | Edouard Mendy | Goalkeeper | Goalkeeper | 387.2833 | 0.4931 | Ranked (300+ min) |
| 5.0000 | 95 | Kalidou Koulibaly | Center Back | Sweeper CB | 387.2833 | 0.3610 | Ranked (300+ min) |


## Serbia

- Total xT created: 1.1887
- Total xA created: 2.0346
- Pass completion under pressure: 0.6740
- Mean defensive hull area: 611.0415
- Mean defensive density: 0.0224

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Nikola Milenković | Center Back | — | 293.6500 | — | Coverage only (<300 min) |
| — | — | Vanja Milinković Savić | Goalkeeper | — | 293.6500 | — | Coverage only (<300 min) |
| — | — | Aleksandar Mitrović | Forward | — | 279.4167 | — | Coverage only (<300 min) |
| — | — | Dušan Tadić | Attacking Midfield/Wing | — | 270.9333 | — | Coverage only (<300 min) |
| — | — | Saša Lukić | Defensive Midfield | — | 261.6500 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## South Korea

- Total xT created: 1.4549
- Total xA created: 2.3972
- Pass completion under pressure: 0.6712
- Mean defensive hull area: 410.9954
- Mean defensive density: 0.0297

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 27 | Heung-Min Son | Attacking Midfield/Wing | Target Forward | 389.6500 | 0.6348 | Ranked (300+ min) |
| 2.0000 | 55 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 340.6833 | 0.5381 | Ranked (300+ min) |
| 3.0000 | 56 | Moon-Hwan Kim | Fullback/Wingback | Attacking Wingback | 389.6500 | 0.5321 | Ranked (300+ min) |
| 4.0000 | — | Seung-Gyu Kim | Goalkeeper | Goalkeeper | 389.6500 | 0.5290 | Ranked (300+ min) |
| 5.0000 | 69 | In-Beom Hwang | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 360.1167 | 0.4894 | Ranked (300+ min) |


## Spain

- Total xT created: 2.1806
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 8 | Daniel Olmo Carvajal | Attacking Midfield/Wing | Progressive Winger | 388.2500 | 0.6955 | Ranked (300+ min) |
| 2.0000 | 30 | Pedro González López | Central/Wide Midfield | Ball-Winner | 372.4000 | 0.6255 | Ranked (300+ min) |
| 3.0000 | — | Unai Simón Mendibil | Goalkeeper | Goalkeeper | 413.9500 | 0.5695 | Ranked (300+ min) |
| 4.0000 | 81 | Sergio Busquets i Burgos | Defensive Midfield | Ball-Winner | 379.2833 | 0.4341 | Ranked (300+ min) |
| 5.0000 | 94 | Rodrigo Hernández Cascante | Center Back | Ball-Playing Centre-Back | 413.9500 | 0.3626 | Ranked (300+ min) |


## Switzerland

- Total xT created: 1.2567
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 20 | Breel-Donald Embolo | Forward | Target Forward | 330.1500 | 0.6571 | Ranked (300+ min) |
| 2.0000 | 71 | Granit Xhaka | Defensive Midfield | Ball-Winner | 386.5833 | 0.4864 | Ranked (300+ min) |
| 3.0000 | 75 | Remo Freuler | Defensive Midfield | Ball-Winner | 346.0500 | 0.4576 | Ranked (300+ min) |
| 4.0000 | 79 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Wide Creator | 380.2333 | 0.4426 | Ranked (300+ min) |
| 5.0000 | 91 | Manuel Obafemi Akanji | Center Back | Ball-Playing Centre-Back | 386.5833 | 0.3784 | Ranked (300+ min) |


## Tunisia

- Total xT created: 1.1588
- Total xA created: 1.9897
- Pass completion under pressure: 0.5839
- Mean defensive hull area: 396.7358
- Mean defensive density: 0.0421

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Ellyes Joris Skhiri | Defensive Midfield | — | 296.5667 | — | Coverage only (<300 min) |
| — | — | Yassine Meriah | Center Back | — | 296.5667 | — | Coverage only (<300 min) |
| — | — | Montassar Omar Talbi | Center Back | — | 296.5667 | — | Coverage only (<300 min) |
| — | — | Aymen Dahmen | Goalkeeper | — | 296.5667 | — | Coverage only (<300 min) |
| — | — | Aïssa Bilal Laïdouni | Defensive Midfield | — | 257.2333 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## United States

- Total xT created: 1.6176
- Total xA created: 3.2488
- Pass completion under pressure: 0.7900
- Mean defensive hull area: 451.8615
- Mean defensive density: 0.0339

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 3 | Christian Pulisic | Central/Wide Midfield | Progressive Winger | 336.3167 | 0.7066 | Ranked (300+ min) |
| 2.0000 | 24 | Timothy Weah | Forward | Progressive Winger | 317.8833 | 0.6508 | Ranked (300+ min) |
| 3.0000 | 36 | Yunus Dimoara Musah | Defensive Midfield | Box-to-Box / Engine Midfielder | 364.8667 | 0.6009 | Ranked (300+ min) |
| 4.0000 | — | Matthew Charles Turner | Goalkeeper | Goalkeeper | 391.2000 | 0.5790 | Ranked (300+ min) |
| 5.0000 | 47 | Sergino Dest | Fullback/Wingback | Attacking Wingback | 307.5667 | 0.5614 | Ranked (300+ min) |


## Uruguay

- Total xT created: 1.3303
- Total xA created: 1.9893
- Pass completion under pressure: 0.6460
- Mean defensive hull area: 457.0204
- Mean defensive density: 0.0260

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | José María Giménez de Vargas | Center Back | — | 298.0833 | — | Coverage only (<300 min) |
| — | — | Federico Santiago Valverde Dipetta | Defensive Midfield | — | 298.0833 | — | Coverage only (<300 min) |
| — | — | Sergio Rochet Álvarez | Goalkeeper | — | 298.0833 | — | Coverage only (<300 min) |
| — | — | Mathías Olivera Miramontes | Fullback/Wingback | — | 263.6333 | — | Coverage only (<300 min) |
| — | — | Darwin Gabriel Núñez Ribeiro | Forward | — | 249.2167 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Wales

- Total xT created: 0.7680
- Total xA created: 1.2536
- Pass completion under pressure: 0.6856
- Mean defensive hull area: 599.2348
- Mean defensive density: 0.0252

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| — | — | Chris Mepham | Center Back | — | 296.7167 | — | Coverage only (<300 min) |
| — | — | Joe Rodon | Center Back | — | 296.7167 | — | Coverage only (<300 min) |
| — | — | Aaron Ramsey | Attacking Midfield/Wing | — | 281.3833 | — | Coverage only (<300 min) |
| — | — | Ethan Ampadu | Defensive Midfield | — | 265.5667 | — | Coverage only (<300 min) |
| — | — | Ben Davies | Fullback/Wingback | — | 261.3333 | — | Coverage only (<300 min) |
_Coverage-only names are selected by tournament minutes and receive no model rating or implied rank._

## Interpretation boundary

These rankings summarize performance in the 2022 tournament sample. They are not transfer valuations, causal estimates, medical assessments, or replacements for video and scouting review.
