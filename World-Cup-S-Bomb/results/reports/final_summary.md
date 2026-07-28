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
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Attacking Midfield/Wing | Progressive Winger | 0.8371 |
| 2 | Kylian Mbappé Lottin | France | Forward | Progressive Winger | 0.8258 |
| 3 | Julián Álvarez | Argentina | Forward | Target Forward | 0.7526 |
| 4 | Vinícius José Paixão de Oliveira Júnior | Brazil | Central/Wide Midfield | Progressive Winger | 0.7354 |
| 5 | Ángel Fabián Di María Hernández | Argentina | Central/Wide Midfield | Progressive Winger | 0.7329 |
| 6 | Raphaël Adelino José Guerreiro | Portugal | Fullback/Wingback | Wide Creator | 0.7296 |
| 7 | Richarlison de Andrade | Brazil | Forward | Target Forward | 0.7289 |
| 8 | Memphis Depay | Netherlands | Forward | Target Forward | 0.7260 |
| 9 | Christian Pulisic | United States | Attacking Midfield/Wing | Progressive Winger | 0.6972 |
| 10 | Marcos Javier Acuña | Argentina | Fullback/Wingback | Attacking Wingback | 0.6948 |
| 11 | Daniel Olmo Carvajal | Spain | Attacking Midfield/Wing | Progressive Winger | 0.6910 |
| 12 | Theo Bernard François Hernández | France | Fullback/Wingback | Attacking Wingback | 0.6874 |
| 13 | Jude Bellingham | England | Defensive Midfield | Box-to-Box / Engine Midfielder | 0.6766 |
| 14 | Luke Shaw | England | Fullback/Wingback | Attacking Wingback | 0.6671 |
| 15 | Daley Blind | Netherlands | Fullback/Wingback | Wide Creator | 0.6665 |
| 16 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Forward | Target Forward | 0.6632 |
| 17 | Adrien Rabiot | France | Defensive Midfield | Ball-Winner | 0.6586 |
| 18 | Nicolás Alejandro Tagliafico | Argentina | Fullback/Wingback | Wide Creator | 0.6573 |
| 19 | Ismaïla Sarr | Senegal | Attacking Midfield/Wing | Target Forward | 0.6553 |
| 20 | Raphael Dias Belloli | Brazil | Attacking Midfield/Wing | Progressive Winger | 0.6537 |

### Position-group leaders

| Position Group | Position Rank | Player Name | Team | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| Attacking Midfield/Wing | 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 0.8371 |
| Attacking Midfield/Wing | 2 | Christian Pulisic | United States | Progressive Winger | 0.6972 |
| Attacking Midfield/Wing | 3 | Daniel Olmo Carvajal | Spain | Progressive Winger | 0.6910 |
| Attacking Midfield/Wing | 4 | Ismaïla Sarr | Senegal | Target Forward | 0.6553 |
| Attacking Midfield/Wing | 5 | Raphael Dias Belloli | Brazil | Progressive Winger | 0.6537 |
| Center Back | 1 | Harry Maguire | England | Deep Playmaker | 0.6336 |
| Center Back | 2 | Young-Gwon Kim | South Korea | Sweeper CB | 0.6239 |
| Center Back | 3 | Kléper Laveran Lima Ferreira | Portugal | Sweeper CB | 0.5942 |
| Center Back | 4 | Kalidou Koulibaly | Senegal | Sweeper CB | 0.5927 |
| Center Back | 5 | Manuel Obafemi Akanji | Switzerland | Ball-Playing Centre-Back | 0.5879 |
| Central/Wide Midfield | 1 | Vinícius José Paixão de Oliveira Júnior | Brazil | Progressive Winger | 0.7354 |
| Central/Wide Midfield | 2 | Ángel Fabián Di María Hernández | Argentina | Progressive Winger | 0.7329 |
| Central/Wide Midfield | 3 | Mathew Leckie | Australia | Target Forward | 0.6183 |
| Central/Wide Midfield | 4 | Sofiane Boufal | Morocco | Box-to-Box / Engine Midfielder | 0.6071 |
| Central/Wide Midfield | 5 | Bernardo Mota Veiga de Carvalho e Silva | Portugal | Box-to-Box / Engine Midfielder | 0.5649 |
| Defensive Midfield | 1 | Jude Bellingham | England | Box-to-Box / Engine Midfielder | 0.6766 |
| Defensive Midfield | 2 | Adrien Rabiot | France | Ball-Winner | 0.6586 |
| Defensive Midfield | 3 | Lucas Tolentino Coelho de Lima | Brazil | Ball-Winner | 0.6459 |
| Defensive Midfield | 4 | Rodrigo Javier De Paul | Argentina | Box-to-Box / Engine Midfielder | 0.6436 |
| Defensive Midfield | 5 | In-Beom Hwang | South Korea | Box-to-Box / Engine Midfielder | 0.5706 |
| Forward | 1 | Kylian Mbappé Lottin | France | Progressive Winger | 0.8258 |
| Forward | 2 | Julián Álvarez | Argentina | Target Forward | 0.7526 |
| Forward | 3 | Richarlison de Andrade | Brazil | Target Forward | 0.7289 |
| Forward | 4 | Memphis Depay | Netherlands | Target Forward | 0.7260 |
| Forward | 5 | Cristiano Ronaldo dos Santos Aveiro | Portugal | Target Forward | 0.6632 |
| Fullback/Wingback | 1 | Raphaël Adelino José Guerreiro | Portugal | Wide Creator | 0.7296 |
| Fullback/Wingback | 2 | Marcos Javier Acuña | Argentina | Attacking Wingback | 0.6948 |
| Fullback/Wingback | 3 | Theo Bernard François Hernández | France | Attacking Wingback | 0.6874 |
| Fullback/Wingback | 4 | Luke Shaw | England | Attacking Wingback | 0.6671 |
| Fullback/Wingback | 5 | Daley Blind | Netherlands | Wide Creator | 0.6665 |
| Goalkeeper | 1 | Matthew Charles Turner | United States | Goalkeeper | 0.6497 |
| Goalkeeper | 2 | Wojciech Szczęsny | Poland | Goalkeeper | 0.6371 |
| Goalkeeper | 3 | Unai Simón Mendibil | Spain | Goalkeeper | 0.6107 |
| Goalkeeper | 4 | Diogo Meireles Costa | Portugal | Goalkeeper | 0.5835 |
| Goalkeeper | 5 | Andries Noppert | Netherlands | Goalkeeper | 0.5806 |

### Largest upward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Young-Gwon Kim | South Korea | 86 | 32 | 54 |
| Marcos Aoás Corrêa | Brazil | 108 | 60 | 48 |
| Manuel Obafemi Akanji | Switzerland | 93 | 46 | 47 |
| Kalidou Koulibaly | Senegal | 90 | 45 | 45 |
| Harry Maguire | England | 70 | 28 | 42 |
| Theo Bernard François Hernández | France | 52 | 12 | 40 |
| Daley Blind | Netherlands | 55 | 15 | 40 |
| Lucas Tolentino Coelho de Lima | Brazil | 65 | 25 | 40 |
| Mohamed Salisu | Ghana | 101 | 63 | 38 |
| Sergino Dest | United States | 61 | 24 | 37 |

### Largest downward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Jackson Irvine | Australia | 39 | 118 | -79 |
| Hakim Ziyech | Morocco | 41 | 113 | -72 |
| Yunus Dimoara Musah | United States | 44 | 112 | -68 |
| Boulaye Dia | Senegal | 28 | 94 | -66 |
| Youssef En-Nesyri | Morocco | 29 | 95 | -66 |
| Selim Amallah | Morocco | 62 | 126 | -64 |
| Luka Modrić | Croatia | 51 | 109 | -58 |
| Mateo Kovačić | Croatia | 34 | 90 | -56 |
| Daichi Kamada | Japan | 30 | 85 | -55 |
| Alexis Mac Allister | Argentina | 31 | 73 | -42 |

Rank movement compares ordering, not raw rating differences, because the V4 and V5 rating scales are different.

## All-team overview

| Team | Eligible Players | Observed Players | Top Ranked Player | Top Global Rank | Total Xt | Pressure Resistance |
|---|---|---|---|---|---|---|
| Argentina | 13 | 24 | Lionel Andrés Messi Cuccittini | 1 | 3.4707 | 0.7447 |
| Australia | 7 | 20 | Mathew Leckie | 35 | 0.9578 | 0.6496 |
| Belgium | 0 | 20 | Jan Vertonghen | Not globally ranked | 1.1828 | 0.7696 |
| Brazil | 9 | 26 | Vinícius José Paixão de Oliveira Júnior | 4 | 3.3449 | 0.7291 |
| Cameroon | 0 | 22 | Nouhou Tolo | Not globally ranked | 0.9097 | 0.6971 |
| Canada | 0 | 19 | Steven de Sousa Vitoria | Not globally ranked | 1.4035 | 0.7118 |
| Costa Rica | 0 | 22 | Keylor Navas Gamboa | Not globally ranked | 0.3533 | 0.6509 |
| Croatia | 10 | 20 | Borna Sosa | 36 | 3.0319 | 0.7430 |
| Denmark | 0 | 20 | Christian Dannemann Eriksen | Not globally ranked | 1.5191 | 0.7086 |
| Ecuador | 0 | 18 | Pervis Josué Estupiñán Tenorio | Not globally ranked | 0.8517 | 0.6954 |
| England | 7 | 20 | Jude Bellingham | 13 | 2.2192 | 0.7556 |
| France | 12 | 24 | Kylian Mbappé Lottin | 2 | 3.4775 | 0.6863 |
| Germany | 0 | 20 | Antonio Rüdiger | Not globally ranked | 2.3732 | 0.7731 |
| Ghana | 4 | 20 | Mohamed Salisu | 63 | 0.7889 | 0.6763 |
| Iran | 3 | 21 | Mehdi Taremi | 22 | 1.0611 | 0.6687 |
| Japan | 5 | 22 | Junya Ito | 49 | 1.3961 | 0.6415 |
| Mexico | 0 | 21 | Héctor Alfredo Moreno Herrera | Not globally ranked | 1.2560 | 0.6241 |
| Morocco | 13 | 25 | Yahia Attiyat allah | 34 | 2.0022 | 0.6771 |
| Netherlands | 9 | 21 | Memphis Depay | 8 | 1.7121 | 0.7135 |
| Poland | 8 | 21 | Wojciech Szczęsny | Not globally ranked | 0.9662 | 0.6818 |
| Portugal | 9 | 24 | Raphaël Adelino José Guerreiro | 6 | 2.1783 | 0.7085 |
| Qatar | 0 | 20 | Akram Hassan Afif | Not globally ranked | 0.6696 | 0.6995 |
| Saudi Arabia | 0 | 23 | Salem Mohammed Al Dawsari | Not globally ranked | 0.9437 | 0.6235 |
| Senegal | 6 | 20 | Ismaïla Sarr | 19 | 1.4521 | 0.6875 |
| Serbia | 0 | 23 | Nikola Milenković | Not globally ranked | 1.1887 | 0.6740 |
| South Korea | 7 | 21 | Jin-Su Kim | 21 | 1.4549 | 0.6712 |
| Spain | 6 | 21 | Daniel Olmo Carvajal | 11 | 2.1806 | 0.8268 |
| Switzerland | 5 | 24 | Manuel Obafemi Akanji | 46 | 1.2567 | 0.7318 |
| Tunisia | 0 | 21 | Ellyes Joris Skhiri | Not globally ranked | 1.1588 | 0.5839 |
| United States | 9 | 20 | Christian Pulisic | 9 | 1.6176 | 0.7900 |
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
| 1.0000 | 1 | Lionel Andrés Messi Cuccittini | Forward | Progressive Winger | 733.9000 | 0.8371 | Ranked (300+ min) |
| 2.0000 | 3 | Julián Álvarez | Attacking Midfield/Wing | Target Forward | 485.2333 | 0.7526 | Ranked (300+ min) |
| 3.0000 | 5 | Ángel Fabián Di María Hernández | Attacking Midfield/Wing | Progressive Winger | 304.8167 | 0.7329 | Ranked (300+ min) |
| 4.0000 | 10 | Marcos Javier Acuña | Fullback/Wingback | Attacking Wingback | 397.4833 | 0.6948 | Ranked (300+ min) |
| 5.0000 | 18 | Nicolás Alejandro Tagliafico | Fullback/Wingback | Wide Creator | 393.3333 | 0.6573 | Ranked (300+ min) |


## Australia

- Total xT created: 0.9578
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 35 | Mathew Leckie | Central/Wide Midfield | Target Forward | 341.6167 | 0.6183 | Ranked (300+ min) |
| 2.0000 | 40 | Aziz Eraltay Behich | Fullback/Wingback | Wide Creator | 386.9167 | 0.6064 | Ranked (300+ min) |
| 3.0000 | — | Mathew Ryan | Goalkeeper | Goalkeeper | 386.9167 | 0.5583 | Ranked (300+ min) |
| 4.0000 | 97 | Aaron Mooy | Defensive Midfield | Box-to-Box Runner | 386.9167 | 0.4732 | Ranked (300+ min) |
| 5.0000 | 118 | Jackson Irvine | Defensive Midfield | Ball-Winner | 373.7500 | 0.3902 | Ranked (300+ min) |


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
| 1.0000 | 4 | Vinícius José Paixão de Oliveira Júnior | Attacking Midfield/Wing | Progressive Winger | 306.5833 | 0.7354 | Ranked (300+ min) |
| 2.0000 | 7 | Richarlison de Andrade | Forward | Target Forward | 328.2500 | 0.7289 | Ranked (300+ min) |
| 3.0000 | 20 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 330.4500 | 0.6537 | Ranked (300+ min) |
| 4.0000 | 25 | Lucas Tolentino Coelho de Lima | Defensive Midfield | Ball-Winner | 318.7667 | 0.6459 | Ranked (300+ min) |
| 5.0000 | 60 | Marcos Aoás Corrêa | Center Back | Ball-Playing Centre-Back | 455.0167 | 0.5648 | Ranked (300+ min) |


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
| 1.0000 | 36 | Borna Sosa | Fullback/Wingback | Wide Creator | 440.4667 | 0.6170 | Ranked (300+ min) |
| 2.0000 | 38 | Ivan Perišić | Attacking Midfield/Wing | Wide Creator | 686.8167 | 0.6081 | Ranked (300+ min) |
| 3.0000 | 48 | Andrej Kramarić | Forward | Target Forward | 478.4333 | 0.5837 | Ranked (300+ min) |
| 4.0000 | — | Dominik Livaković | Goalkeeper | Goalkeeper | 720.2833 | 0.5503 | Ranked (300+ min) |
| 5.0000 | 80 | Joško Gvardiol | Center Back | Ball-Playing Centre-Back | 720.2833 | 0.5028 | Ranked (300+ min) |


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
| 1.0000 | 13 | Jude Bellingham | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 441.7667 | 0.6766 | Ranked (300+ min) |
| 2.0000 | 14 | Luke Shaw | Fullback/Wingback | Attacking Wingback | 457.1667 | 0.6671 | Ranked (300+ min) |
| 3.0000 | 28 | Harry Maguire | Center Back | Deep Playmaker | 453.7167 | 0.6336 | Ranked (300+ min) |
| 4.0000 | 47 | Harry Kane | Forward | Target Forward | 421.5167 | 0.5879 | Ranked (300+ min) |
| 5.0000 | 68 | John Stones | Center Back | Ball-Playing Centre-Back | 464.8833 | 0.5345 | Ranked (300+ min) |


## France

- Total xT created: 3.4775
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 2 | Kylian Mbappé Lottin | Attacking Midfield/Wing | Progressive Winger | 654.3000 | 0.8258 | Ranked (300+ min) |
| 2.0000 | 12 | Theo Bernard François Hernández | Fullback/Wingback | Attacking Wingback | 548.5000 | 0.6874 | Ranked (300+ min) |
| 3.0000 | 17 | Adrien Rabiot | Defensive Midfield | Ball-Winner | 529.2500 | 0.6586 | Ranked (300+ min) |
| 4.0000 | 31 | Olivier Giroud | Forward | Target Forward / Penalty-Box Anchor | 432.6167 | 0.6245 | Ranked (300+ min) |
| 5.0000 | 51 | Antoine Griezmann | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 586.0500 | 0.5794 | Ranked (300+ min) |


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
| 1.0000 | 63 | Mohamed Salisu | Center Back | Sweeper CB | 301.2000 | 0.5546 | Ranked (300+ min) |
| 2.0000 | — | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 301.2000 | 0.4223 | Ranked (300+ min) |
| 3.0000 | 114 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 301.2000 | 0.4125 | Ranked (300+ min) |
| 4.0000 | 123 | Daniel Amartey | Center Back | Sweeper CB | 301.2000 | 0.3654 | Ranked (300+ min) |
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
| 1.0000 | 22 | Mehdi Taremi | Forward | Target Forward | 305.1000 | 0.6492 | Ranked (300+ min) |
| 2.0000 | 71 | Morteza Pouraliganji | Center Back | Sweeper CB | 305.1000 | 0.5266 | Ranked (300+ min) |
| 3.0000 | 116 | Seyed Majid Hosseini | Center Back | Sweeper CB | 305.1000 | 0.4105 | Ranked (300+ min) |
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
| 1.0000 | 49 | Junya Ito | Fullback/Wingback | Attacking Wingback | 346.3333 | 0.5802 | Ranked (300+ min) |
| 2.0000 | — | Shūichi Gonda | Goalkeeper | Goalkeeper | 412.5167 | 0.5397 | Ranked (300+ min) |
| 3.0000 | 85 | Daichi Kamada | Attacking Midfield/Wing | Target Forward | 337.2167 | 0.4990 | Ranked (300+ min) |
| 4.0000 | 89 | Wataru Endo | Defensive Midfield | Ball-Winner | 326.0167 | 0.4856 | Ranked (300+ min) |
| 5.0000 | 103 | Maya Yoshida | Center Back | Sweeper CB | 412.5167 | 0.4598 | Ranked (300+ min) |


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
| 1.0000 | 34 | Yahia Attiyat allah | Fullback/Wingback | Wide Creator | 350.1833 | 0.6202 | Ranked (300+ min) |
| 2.0000 | 39 | Sofiane Boufal | Attacking Midfield/Wing | Box-to-Box / Engine Midfielder | 476.6667 | 0.6071 | Ranked (300+ min) |
| 3.0000 | 43 | Noussair Mazraoui | Fullback/Wingback | Wide Creator | 376.8333 | 0.5972 | Ranked (300+ min) |
| 4.0000 | — | Yassine Bounou | Goalkeeper | Goalkeeper | 603.1500 | 0.5796 | Ranked (300+ min) |
| 5.0000 | 84 | Achraf Hakimi Mouh | Fullback/Wingback | Attacking Wingback | 660.8000 | 0.5007 | Ranked (300+ min) |


## Netherlands

- Total xT created: 1.7121
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 8 | Memphis Depay | Forward | Target Forward | 315.5833 | 0.7260 | Ranked (300+ min) |
| 2.0000 | 15 | Daley Blind | Fullback/Wingback | Wide Creator | 452.4833 | 0.6665 | Ranked (300+ min) |
| 3.0000 | 29 | Denzel Dumfries | Fullback/Wingback | Attacking Wingback | 509.5167 | 0.6312 | Ranked (300+ min) |
| 4.0000 | 42 | Cody Mathès Gakpo | Forward | Progressive Winger | 460.2167 | 0.5976 | Ranked (300+ min) |
| 5.0000 | — | Andries Noppert | Goalkeeper | Goalkeeper | 509.5167 | 0.5806 | Ranked (300+ min) |


## Poland

- Total xT created: 0.9662
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | — | Wojciech Szczęsny | Goalkeeper | Goalkeeper | 389.7500 | 0.6371 | Ranked (300+ min) |
| 2.0000 | 30 | Robert Lewandowski | Forward | Target Forward / Penalty-Box Anchor | 389.7500 | 0.6260 | Ranked (300+ min) |
| 3.0000 | 57 | Bartosz Bereszyński | Fullback/Wingback | Wide Creator | 365.7333 | 0.5679 | Ranked (300+ min) |
| 4.0000 | 78 | Grzegorz Krychowiak | Defensive Midfield | Ball-Winner | 347.8833 | 0.5033 | Ranked (300+ min) |
| 5.0000 | 79 | Piotr Zieliński | Central/Wide Midfield | Ball-Winner | 344.4167 | 0.5030 | Ranked (300+ min) |


## Portugal

- Total xT created: 2.1783
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 6 | Raphaël Adelino José Guerreiro | Fullback/Wingback | Wide Creator | 303.6167 | 0.7296 | Ranked (300+ min) |
| 2.0000 | 16 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 302.8000 | 0.6632 | Ranked (300+ min) |
| 3.0000 | 27 | João Pedro Cavaco Cancelo | Fullback/Wingback | Box-to-Box Runner | 344.5500 | 0.6406 | Ranked (300+ min) |
| 4.0000 | 37 | João Félix Sequeira | Forward | Target Forward | 340.2333 | 0.6119 | Ranked (300+ min) |
| 5.0000 | 44 | Kléper Laveran Lima Ferreira | Center Back | Sweeper CB | 389.2833 | 0.5942 | Ranked (300+ min) |


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
| 1.0000 | 19 | Ismaïla Sarr | Attacking Midfield/Wing | Target Forward | 365.2000 | 0.6553 | Ranked (300+ min) |
| 2.0000 | 33 | Youssouf Sabaly | Fullback/Wingback | Attacking Wingback | 387.2833 | 0.6216 | Ranked (300+ min) |
| 3.0000 | 45 | Kalidou Koulibaly | Center Back | Sweeper CB | 387.2833 | 0.5927 | Ranked (300+ min) |
| 4.0000 | 93 | Abdou Diallo | Center Back | Sweeper CB | 348.5833 | 0.4803 | Ranked (300+ min) |
| 5.0000 | 94 | Boulaye Dia | Forward | Target Forward | 330.0500 | 0.4795 | Ranked (300+ min) |


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
| 1.0000 | 21 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 340.6833 | 0.6518 | Ranked (300+ min) |
| 2.0000 | 32 | Young-Gwon Kim | Center Back | Sweeper CB | 373.1833 | 0.6239 | Ranked (300+ min) |
| 3.0000 | 52 | Moon-Hwan Kim | Fullback/Wingback | Attacking Wingback | 389.6500 | 0.5775 | Ranked (300+ min) |
| 4.0000 | 53 | Heung-Min Son | Attacking Midfield/Wing | Target Forward | 389.6500 | 0.5768 | Ranked (300+ min) |
| 5.0000 | 54 | In-Beom Hwang | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 360.1167 | 0.5706 | Ranked (300+ min) |


## Spain

- Total xT created: 2.1806
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 11 | Daniel Olmo Carvajal | Attacking Midfield/Wing | Progressive Winger | 388.2500 | 0.6910 | Ranked (300+ min) |
| 2.0000 | — | Unai Simón Mendibil | Goalkeeper | Goalkeeper | 413.9500 | 0.6107 | Ranked (300+ min) |
| 3.0000 | 56 | Rodrigo Hernández Cascante | Center Back | Ball-Playing Centre-Back | 413.9500 | 0.5688 | Ranked (300+ min) |
| 4.0000 | 70 | Aymeric Laporte | Center Back | Deep Playmaker | 316.9333 | 0.5273 | Ranked (300+ min) |
| 5.0000 | 72 | Pedro González López | Central/Wide Midfield | Ball-Winner | 372.4000 | 0.5198 | Ranked (300+ min) |


## Switzerland

- Total xT created: 1.2567
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five player summary

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Minutes | Final Player Rating | Ranking Status |
|---|---|---|---|---|---|---|---|
| 1.0000 | 46 | Manuel Obafemi Akanji | Center Back | Ball-Playing Centre-Back | 386.5833 | 0.5879 | Ranked (300+ min) |
| 2.0000 | 58 | Breel-Donald Embolo | Forward | Target Forward | 330.1500 | 0.5661 | Ranked (300+ min) |
| 3.0000 | 64 | Granit Xhaka | Defensive Midfield | Ball-Winner | 386.5833 | 0.5512 | Ranked (300+ min) |
| 4.0000 | 82 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Wide Creator | 380.2333 | 0.5013 | Ranked (300+ min) |
| 5.0000 | 83 | Remo Freuler | Defensive Midfield | Ball-Winner | 346.0500 | 0.5010 | Ranked (300+ min) |


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
| 1.0000 | 9 | Christian Pulisic | Central/Wide Midfield | Progressive Winger | 336.3167 | 0.6972 | Ranked (300+ min) |
| 2.0000 | — | Matthew Charles Turner | Goalkeeper | Goalkeeper | 391.2000 | 0.6497 | Ranked (300+ min) |
| 3.0000 | 23 | Timothy Weah | Forward | Progressive Winger | 317.8833 | 0.6484 | Ranked (300+ min) |
| 4.0000 | 24 | Sergino Dest | Fullback/Wingback | Attacking Wingback | 307.5667 | 0.6472 | Ranked (300+ min) |
| 5.0000 | 41 | Antonee Robinson | Fullback/Wingback | Attacking Wingback | 386.2667 | 0.6006 | Ranked (300+ min) |


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
