# World Cup V5 Role-Aware Final Report

## Executive summary

This report consolidates **32 national teams** and **142 players meeting the 300-minute cutoff**. It uses StatsBomb events, lineups, minutes, and coverage-qualified 360 freeze frames. It does not use optical tracking, external ratings, or player-name adjustments.

The active contribution layer is `role_aware_fallback`. The experimental attention challenger remains available but affects rankings only when it passes its match-disjoint metric gate.

## How to read the player rating

The V5 score combines 40% VAEP/90, 15% VAEP/touch, 15% xT/90, 15% continuous role-adjusted value, 10% completeness, and 5% coverage-qualified off-ball contribution. It is then shrunk toward the broad position-group mean according to tournament minutes.

Missing 360 evidence remains missing. Roles modulate the weights applied to observed contribution; neither functional nor probabilistic role labels directly award rating points.

## General player summary

### Overall leaders

| Global Rank | Player Name | Team | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | Lionel Andrés Messi Cuccittini | Argentina | Attacking Midfield/Wing | Progressive Winger | 0.8479 |
| 2 | Kylian Mbappé Lottin | France | Forward | Progressive Winger | 0.8086 |
| 3 | Christian Pulisic | United States | Attacking Midfield/Wing | Progressive Winger | 0.8081 |
| 4 | Raphael Dias Belloli | Brazil | Attacking Midfield/Wing | Progressive Winger | 0.8012 |
| 5 | Antoine Griezmann | France | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 0.8001 |
| 6 | Daniel Olmo Carvajal | Spain | Attacking Midfield/Wing | Progressive Winger | 0.7996 |
| 7 | Ismaïla Sarr | Senegal | Attacking Midfield/Wing | Target Forward | 0.7976 |
| 8 | Ángel Fabián Di María Hernández | Argentina | Central/Wide Midfield | Progressive Winger | 0.7925 |
| 9 | Ousmane Dembélé | France | Attacking Midfield/Wing | Progressive Winger | 0.7850 |
| 10 | Vinícius José Paixão de Oliveira Júnior | Brazil | Central/Wide Midfield | Progressive Winger | 0.7835 |
| 11 | Ivan Perišić | Croatia | Attacking Midfield/Wing | Wide Creator | 0.7778 |
| 12 | Cody Mathès Gakpo | Netherlands | Attacking Midfield/Wing | Progressive Winger | 0.7771 |
| 13 | Mehdi Taremi | Iran | Forward | Target Forward | 0.7679 |
| 14 | Julián Álvarez | Argentina | Forward | Target Forward | 0.7630 |
| 15 | Heung-Min Son | South Korea | Attacking Midfield/Wing | Target Forward | 0.7624 |
| 16 | Memphis Depay | Netherlands | Forward | Target Forward | 0.7622 |
| 17 | João Félix Sequeira | Portugal | Attacking Midfield/Wing | Target Forward | 0.7621 |
| 18 | Bruno Miguel Borges Fernandes | Portugal | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 0.7574 |
| 19 | Richarlison de Andrade | Brazil | Forward | Target Forward | 0.7494 |
| 20 | Timothy Weah | United States | Attacking Midfield/Wing | Progressive Winger | 0.7446 |

### Position-group leaders

| Position Group | Position Rank | Player Name | Team | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| Attacking Midfield/Wing | 1 | Lionel Andrés Messi Cuccittini | Argentina | Progressive Winger | 0.8479 |
| Attacking Midfield/Wing | 2 | Christian Pulisic | United States | Progressive Winger | 0.8081 |
| Attacking Midfield/Wing | 3 | Raphael Dias Belloli | Brazil | Progressive Winger | 0.8012 |
| Attacking Midfield/Wing | 4 | Antoine Griezmann | France | Hybrid Playmaker / Roaming Creator | 0.8001 |
| Attacking Midfield/Wing | 5 | Daniel Olmo Carvajal | Spain | Progressive Winger | 0.7996 |
| Center Back | 1 | Harry Maguire | England | Deep Playmaker | 0.5361 |
| Center Back | 2 | Rodrigo Hernández Cascante | Spain | Ball-Playing Centre-Back | 0.4818 |
| Center Back | 3 | Kléper Laveran Lima Ferreira | Portugal | Sweeper CB | 0.4796 |
| Center Back | 4 | Young-Gwon Kim | South Korea | Sweeper CB | 0.4653 |
| Center Back | 5 | Ibrahima Konaté | France | Ball-Playing Centre-Back | 0.4551 |
| Central/Wide Midfield | 1 | Ángel Fabián Di María Hernández | Argentina | Progressive Winger | 0.7925 |
| Central/Wide Midfield | 2 | Vinícius José Paixão de Oliveira Júnior | Brazil | Progressive Winger | 0.7835 |
| Central/Wide Midfield | 3 | Mateo Kovačić | Croatia | Box-to-Box / Engine Midfielder | 0.7244 |
| Central/Wide Midfield | 4 | Sofiane Boufal | Morocco | Box-to-Box / Engine Midfielder | 0.7188 |
| Central/Wide Midfield | 5 | Bernardo Mota Veiga de Carvalho e Silva | Portugal | Box-to-Box / Engine Midfielder | 0.7162 |
| Defensive Midfield | 1 | Rodrigo Javier De Paul | Argentina | Box-to-Box / Engine Midfielder | 0.6584 |
| Defensive Midfield | 2 | Jude Bellingham | England | Box-to-Box / Engine Midfielder | 0.6575 |
| Defensive Midfield | 3 | Adrien Rabiot | France | Ball-Winner | 0.6165 |
| Defensive Midfield | 4 | Lucas Tolentino Coelho de Lima | Brazil | Ball-Winner | 0.5959 |
| Defensive Midfield | 5 | In-Beom Hwang | South Korea | Box-to-Box / Engine Midfielder | 0.5809 |
| Forward | 1 | Kylian Mbappé Lottin | France | Progressive Winger | 0.8086 |
| Forward | 2 | Mehdi Taremi | Iran | Target Forward | 0.7679 |
| Forward | 3 | Julián Álvarez | Argentina | Target Forward | 0.7630 |
| Forward | 4 | Memphis Depay | Netherlands | Target Forward | 0.7622 |
| Forward | 5 | Richarlison de Andrade | Brazil | Target Forward | 0.7494 |
| Fullback/Wingback | 1 | Marcos Javier Acuña | Argentina | Attacking Wingback | 0.7182 |
| Fullback/Wingback | 2 | Luke Shaw | England | Attacking Wingback | 0.6932 |
| Fullback/Wingback | 3 | Raphaël Adelino José Guerreiro | Portugal | Wide Creator | 0.6856 |
| Fullback/Wingback | 4 | João Pedro Cavaco Cancelo | Portugal | Box-to-Box Runner | 0.6614 |
| Fullback/Wingback | 5 | Antonee Robinson | United States | Attacking Wingback | 0.6612 |
| Goalkeeper | 1 | Damián Emiliano Martínez | Argentina | Goalkeeper | 0.4695 |
| Goalkeeper | 2 | Andries Noppert | Netherlands | Goalkeeper | 0.3400 |
| Goalkeeper | 3 | Hugo Lloris | France | Goalkeeper | 0.2042 |
| Goalkeeper | 4 | Edouard Mendy | Senegal | Goalkeeper | 0.1977 |
| Goalkeeper | 5 | Jordan Pickford | England | Goalkeeper | 0.1870 |

### Largest upward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Antoine Griezmann | France | 21 | 5 | 16 |
| Luka Modrić | Croatia | 51 | 37 | 14 |
| Thomas Teye Partey | Ghana | 103 | 89 | 14 |
| Sergio Busquets i Burgos | Spain | 99 | 86 | 13 |
| Aurélien Djani Tchouaméni | France | 104 | 91 | 13 |
| Daniel Amartey | Ghana | 137 | 124 | 13 |
| Cody Mathès Gakpo | Netherlands | 24 | 12 | 12 |
| Ousmane Dembélé | France | 20 | 9 | 11 |
| Mateo Kovačić | Croatia | 34 | 23 | 11 |
| Sofiane Boufal | Morocco | 35 | 24 | 11 |

### Largest downward rank movements

| Player Name | Team | Legacy Global Rank | Global Rank | Rank Improvement |
|---|---|---|---|---|
| Jackson Irvine | Australia | 39 | 66 | -27 |
| Damián Emiliano Martínez | Argentina | 59 | 85 | -26 |
| Youssef En-Nesyri | Morocco | 29 | 51 | -22 |
| Olivier Giroud | France | 11 | 28 | -17 |
| Richarlison de Andrade | Brazil | 3 | 19 | -16 |
| Cristiano Ronaldo dos Santos Aveiro | Portugal | 6 | 22 | -16 |
| Andries Noppert | Netherlands | 105 | 121 | -16 |
| Boulaye Dia | Senegal | 28 | 40 | -12 |
| Julián Álvarez | Argentina | 4 | 14 | -10 |
| Adrien Rabiot | France | 50 | 60 | -10 |

Rank movement compares ordering, not raw rating differences, because the V4 and V5 rating scales are different.

## All-team overview

| Team | Eligible Players | Top Ranked Player | Top Global Rank | Total Xt | Pressure Resistance |
|---|---|---|---|---|---|
| Argentina | 13 | Lionel Andrés Messi Cuccittini | 1 | 3.4707 | 0.7447 |
| Australia | 7 | Mathew Leckie | 34 | 0.9578 | 0.6496 |
| Belgium | 0 | No player at 300-minute cutoff | — | 1.1828 | 0.7696 |
| Brazil | 9 | Raphael Dias Belloli | 4 | 3.3449 | 0.7291 |
| Cameroon | 0 | No player at 300-minute cutoff | — | 0.9097 | 0.6971 |
| Canada | 0 | No player at 300-minute cutoff | — | 1.4035 | 0.7118 |
| Costa Rica | 0 | No player at 300-minute cutoff | — | 0.3533 | 0.6509 |
| Croatia | 10 | Ivan Perišić | 11 | 3.0319 | 0.7430 |
| Denmark | 0 | No player at 300-minute cutoff | — | 1.5191 | 0.7086 |
| Ecuador | 0 | No player at 300-minute cutoff | — | 0.8517 | 0.6954 |
| England | 7 | Harry Kane | 26 | 2.2192 | 0.7556 |
| France | 12 | Kylian Mbappé Lottin | 2 | 3.4775 | 0.6863 |
| Germany | 0 | No player at 300-minute cutoff | — | 2.3732 | 0.7731 |
| Ghana | 4 | Thomas Teye Partey | 89 | 0.7889 | 0.6763 |
| Iran | 3 | Mehdi Taremi | 13 | 1.0611 | 0.6687 |
| Japan | 5 | Daichi Kamada | 33 | 1.3961 | 0.6415 |
| Mexico | 0 | No player at 300-minute cutoff | — | 1.2560 | 0.6241 |
| Morocco | 13 | Sofiane Boufal | 24 | 2.0022 | 0.6771 |
| Netherlands | 9 | Cody Mathès Gakpo | 12 | 1.7121 | 0.7135 |
| Poland | 8 | Robert Lewandowski | 21 | 0.9662 | 0.6818 |
| Portugal | 9 | João Félix Sequeira | 17 | 2.1783 | 0.7085 |
| Qatar | 0 | No player at 300-minute cutoff | — | 0.6696 | 0.6995 |
| Saudi Arabia | 0 | No player at 300-minute cutoff | — | 0.9437 | 0.6235 |
| Senegal | 6 | Ismaïla Sarr | 7 | 1.4521 | 0.6875 |
| Serbia | 0 | No player at 300-minute cutoff | — | 1.1887 | 0.6740 |
| South Korea | 7 | Heung-Min Son | 15 | 1.4549 | 0.6712 |
| Spain | 6 | Daniel Olmo Carvajal | 6 | 2.1806 | 0.8268 |
| Switzerland | 5 | Breel-Donald Embolo | 31 | 1.2567 | 0.7318 |
| Tunisia | 0 | No player at 300-minute cutoff | — | 1.1588 | 0.5839 |
| United States | 9 | Christian Pulisic | 3 | 1.6176 | 0.7900 |
| Uruguay | 0 | No player at 300-minute cutoff | — | 1.3303 | 0.6460 |
| Wales | 0 | No player at 300-minute cutoff | — | 0.7680 | 0.6856 |

# Team-by-team summary

## Argentina

- Total xT created: 3.4707
- Total xA created: 6.7228
- Pass completion under pressure: 0.7447
- Mean defensive hull area: 647.6227
- Mean defensive density: 0.0258

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 1 | Lionel Andrés Messi Cuccittini | Attacking Midfield/Wing | Progressive Winger | 0.8479 |
| 2 | 8 | Ángel Fabián Di María Hernández | Central/Wide Midfield | Progressive Winger | 0.7925 |
| 3 | 14 | Julián Álvarez | Forward | Target Forward | 0.7630 |
| 4 | 25 | Marcos Javier Acuña | Fullback/Wingback | Attacking Wingback | 0.7182 |
| 5 | 36 | Alexis Mac Allister | Central/Wide Midfield | Ball-Winner | 0.6838 |

## Australia

- Total xT created: 0.9578
- Total xA created: 1.3333
- Pass completion under pressure: 0.6496
- Mean defensive hull area: 507.7118
- Mean defensive density: 0.5985

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 34 | Mathew Leckie | Central/Wide Midfield | Target Forward | 0.6881 |
| 2 | 57 | Aziz Eraltay Behich | Fullback/Wingback | Wide Creator | 0.6231 |
| 3 | 66 | Jackson Irvine | Forward | Ball-Winner | 0.5723 |
| 4 | 90 | Aaron Mooy | Defensive Midfield | Box-to-Box Runner | 0.4618 |
| 5 | 127 | Harry Souttar | Center Back | Sweeper CB | 0.2990 |

## Belgium

- Total xT created: 1.1828
- Total xA created: 2.5562
- Pass completion under pressure: 0.7696
- Mean defensive hull area: 640.6988
- Mean defensive density: 0.0190

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Brazil

- Total xT created: 3.3449
- Total xA created: 6.8525
- Pass completion under pressure: 0.7291
- Mean defensive hull area: 579.4863
- Mean defensive density: 0.0211

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 4 | Raphael Dias Belloli | Attacking Midfield/Wing | Progressive Winger | 0.8012 |
| 2 | 10 | Vinícius José Paixão de Oliveira Júnior | Central/Wide Midfield | Progressive Winger | 0.7835 |
| 3 | 19 | Richarlison de Andrade | Forward | Target Forward | 0.7494 |
| 4 | 61 | Lucas Tolentino Coelho de Lima | Defensive Midfield | Ball-Winner | 0.5959 |
| 5 | 62 | Éder Gabriel Militão | Fullback/Wingback | Box-to-Box Runner | 0.5869 |

## Cameroon

- Total xT created: 0.9097
- Total xA created: 1.8107
- Pass completion under pressure: 0.6971
- Mean defensive hull area: 518.5576
- Mean defensive density: 0.0268

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Canada

- Total xT created: 1.4035
- Total xA created: 2.0764
- Pass completion under pressure: 0.7118
- Mean defensive hull area: 569.4089
- Mean defensive density: 0.0243

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Costa Rica

- Total xT created: 0.3533
- Total xA created: 0.4012
- Pass completion under pressure: 0.6509
- Mean defensive hull area: 510.3123
- Mean defensive density: 0.0278

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Croatia

- Total xT created: 3.0319
- Total xA created: 5.6716
- Pass completion under pressure: 0.7430
- Mean defensive hull area: 480.9343
- Mean defensive density: 0.0281

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 11 | Ivan Perišić | Attacking Midfield/Wing | Wide Creator | 0.7778 |
| 2 | 23 | Mateo Kovačić | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 0.7244 |
| 3 | 29 | Andrej Kramarić | Attacking Midfield/Wing | Target Forward | 0.7020 |
| 4 | 37 | Luka Modrić | Central/Wide Midfield | Deep Playmaker / Metronome | 0.6724 |
| 5 | 55 | Borna Sosa | Fullback/Wingback | Wide Creator | 0.6271 |

## Denmark

- Total xT created: 1.5191
- Total xA created: 2.1738
- Pass completion under pressure: 0.7086
- Mean defensive hull area: 439.0378
- Mean defensive density: 0.0278

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Ecuador

- Total xT created: 0.8517
- Total xA created: 1.1631
- Pass completion under pressure: 0.6954
- Mean defensive hull area: 440.9376
- Mean defensive density: 0.0261

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## England

- Total xT created: 2.2192
- Total xA created: 4.8703
- Pass completion under pressure: 0.7556
- Mean defensive hull area: 482.2597
- Mean defensive density: 0.0278

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 26 | Harry Kane | Forward | Target Forward | 0.7175 |
| 2 | 32 | Luke Shaw | Fullback/Wingback | Attacking Wingback | 0.6932 |
| 3 | 47 | Jude Bellingham | Defensive Midfield | Box-to-Box / Engine Midfielder | 0.6575 |
| 4 | 73 | Harry Maguire | Center Back | Deep Playmaker | 0.5361 |
| 5 | 77 | Declan Rice | Defensive Midfield | Ball-Winner | 0.5097 |

## France

- Total xT created: 3.4775
- Total xA created: 8.4503
- Pass completion under pressure: 0.6863
- Mean defensive hull area: 524.0383
- Mean defensive density: 0.2887

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 2 | Kylian Mbappé Lottin | Forward | Progressive Winger | 0.8086 |
| 2 | 5 | Antoine Griezmann | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 0.8001 |
| 3 | 9 | Ousmane Dembélé | Attacking Midfield/Wing | Progressive Winger | 0.7850 |
| 4 | 28 | Olivier Giroud | Forward | Target Forward / Penalty-Box Anchor | 0.7159 |
| 5 | 46 | Theo Bernard François Hernández | Fullback/Wingback | Attacking Wingback | 0.6582 |

## Germany

- Total xT created: 2.3732
- Total xA created: 6.0997
- Pass completion under pressure: 0.7731
- Mean defensive hull area: 489.2536
- Mean defensive density: 0.0243

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Ghana

- Total xT created: 0.7889
- Total xA created: 0.9937
- Pass completion under pressure: 0.6763
- Mean defensive hull area: 432.5226
- Mean defensive density: 0.0269

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 89 | Thomas Teye Partey | Defensive Midfield | Ball-Winner | 0.4639 |
| 2 | 101 | Mohamed Salisu | Center Back | Sweeper CB | 0.4153 |
| 3 | 124 | Daniel Amartey | Center Back | Sweeper CB | 0.3131 |
| 4 | 132 | Lawrence Ati-Zigi | Goalkeeper | Goalkeeper | 0.1857 |

## Iran

- Total xT created: 1.0611
- Total xA created: 2.6253
- Pass completion under pressure: 0.6687
- Mean defensive hull area: 460.4993
- Mean defensive density: 0.0330

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 13 | Mehdi Taremi | Forward | Target Forward | 0.7679 |
| 2 | 97 | Morteza Pouraliganji | Center Back | Sweeper CB | 0.4487 |
| 3 | 122 | Seyed Majid Hosseini | Center Back | Sweeper CB | 0.3303 |

## Japan

- Total xT created: 1.3961
- Total xA created: 2.4186
- Pass completion under pressure: 0.6415
- Mean defensive hull area: 501.4214
- Mean defensive density: 0.0229

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 33 | Daichi Kamada | Attacking Midfield/Wing | Target Forward | 0.6899 |
| 2 | 59 | Junya Ito | Fullback/Wingback | Attacking Wingback | 0.6170 |
| 3 | 81 | Wataru Endo | Defensive Midfield | Ball-Winner | 0.4934 |
| 4 | 125 | Maya Yoshida | Center Back | Sweeper CB | 0.3098 |
| 5 | 139 | Shūichi Gonda | Goalkeeper | Goalkeeper | 0.1752 |

## Mexico

- Total xT created: 1.2560
- Total xA created: 2.6085
- Pass completion under pressure: 0.6241
- Mean defensive hull area: 639.3089
- Mean defensive density: 0.0298

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Morocco

- Total xT created: 2.0022
- Total xA created: 3.2076
- Pass completion under pressure: 0.6771
- Mean defensive hull area: 518.2011
- Mean defensive density: 0.0225

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 24 | Sofiane Boufal | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 0.7188 |
| 2 | 39 | Hakim Ziyech | Attacking Midfield/Wing | Box-to-Box Runner | 0.6699 |
| 3 | 44 | Azzedine Ounahi | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 0.6611 |
| 4 | 51 | Youssef En-Nesyri | Forward | Target Forward / Penalty-Box Anchor | 0.6363 |
| 5 | 52 | Yahia Attiyat allah | Fullback/Wingback | Wide Creator | 0.6353 |

## Netherlands

- Total xT created: 1.7121
- Total xA created: 2.8899
- Pass completion under pressure: 0.7135
- Mean defensive hull area: 559.8047
- Mean defensive density: 0.0575

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 12 | Cody Mathès Gakpo | Attacking Midfield/Wing | Progressive Winger | 0.7771 |
| 2 | 16 | Memphis Depay | Forward | Target Forward | 0.7622 |
| 3 | 50 | Daley Blind | Fullback/Wingback | Wide Creator | 0.6441 |
| 4 | 58 | Denzel Dumfries | Fullback/Wingback | Attacking Wingback | 0.6188 |
| 5 | 71 | Frenkie de Jong | Defensive Midfield | Box-to-Box / Engine Midfielder | 0.5535 |

## Poland

- Total xT created: 0.9662
- Total xA created: 1.5400
- Pass completion under pressure: 0.6818
- Mean defensive hull area: 457.5096
- Mean defensive density: 0.0296

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 21 | Robert Lewandowski | Forward | Target Forward / Penalty-Box Anchor | 0.7329 |
| 2 | 38 | Piotr Zieliński | Central/Wide Midfield | Ball-Winner | 0.6704 |
| 3 | 63 | Bartosz Bereszyński | Fullback/Wingback | Wide Creator | 0.5850 |
| 4 | 82 | Grzegorz Krychowiak | Defensive Midfield | Ball-Winner | 0.4934 |
| 5 | 96 | Matty Cash | Fullback/Wingback | Box-to-Box Runner | 0.4505 |

## Portugal

- Total xT created: 2.1783
- Total xA created: 4.5349
- Pass completion under pressure: 0.7085
- Mean defensive hull area: 596.9005
- Mean defensive density: 0.0206

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 17 | João Félix Sequeira | Attacking Midfield/Wing | Target Forward | 0.7621 |
| 2 | 18 | Bruno Miguel Borges Fernandes | Attacking Midfield/Wing | Hybrid Playmaker / Roaming Creator | 0.7574 |
| 3 | 22 | Cristiano Ronaldo dos Santos Aveiro | Forward | Target Forward | 0.7282 |
| 4 | 27 | Bernardo Mota Veiga de Carvalho e Silva | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 0.7162 |
| 5 | 35 | Raphaël Adelino José Guerreiro | Fullback/Wingback | Wide Creator | 0.6856 |

## Qatar

- Total xT created: 0.6696
- Total xA created: 1.1791
- Pass completion under pressure: 0.6995
- Mean defensive hull area: 451.6214
- Mean defensive density: 0.0529

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Saudi Arabia

- Total xT created: 0.9437
- Total xA created: 1.2324
- Pass completion under pressure: 0.6235
- Mean defensive hull area: 480.3764
- Mean defensive density: 0.0271

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Senegal

- Total xT created: 1.4521
- Total xA created: 2.0598
- Pass completion under pressure: 0.6875
- Mean defensive hull area: 550.7399
- Mean defensive density: 0.0216

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 7 | Ismaïla Sarr | Attacking Midfield/Wing | Target Forward | 0.7976 |
| 2 | 40 | Boulaye Dia | Attacking Midfield/Wing | Target Forward | 0.6646 |
| 3 | 53 | Youssouf Sabaly | Fullback/Wingback | Attacking Wingback | 0.6306 |
| 4 | 95 | Kalidou Koulibaly | Center Back | Sweeper CB | 0.4534 |
| 5 | 111 | Abdou Diallo | Center Back | Sweeper CB | 0.3828 |

## Serbia

- Total xT created: 1.1887
- Total xA created: 2.0346
- Pass completion under pressure: 0.6740
- Mean defensive hull area: 611.0415
- Mean defensive density: 0.0224

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## South Korea

- Total xT created: 1.4549
- Total xA created: 2.3972
- Pass completion under pressure: 0.6712
- Mean defensive hull area: 410.9954
- Mean defensive density: 0.0297

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 15 | Heung-Min Son | Attacking Midfield/Wing | Target Forward | 0.7624 |
| 2 | 49 | Jin-Su Kim | Fullback/Wingback | Attacking Wingback | 0.6469 |
| 3 | 56 | Moon-Hwan Kim | Fullback/Wingback | Attacking Wingback | 0.6242 |
| 4 | 65 | In-Beom Hwang | Defensive Midfield | Box-to-Box / Engine Midfielder | 0.5809 |
| 5 | 78 | Woo-Young Jung | Defensive Midfield | Ball-Winner | 0.5092 |

## Spain

- Total xT created: 2.1806
- Total xA created: 2.7253
- Pass completion under pressure: 0.8268
- Mean defensive hull area: 501.6197
- Mean defensive density: 0.0268

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 6 | Daniel Olmo Carvajal | Attacking Midfield/Wing | Progressive Winger | 0.7996 |
| 2 | 30 | Pedro González López | Central/Wide Midfield | Ball-Winner | 0.7003 |
| 3 | 83 | Rodrigo Hernández Cascante | Center Back | Ball-Playing Centre-Back | 0.4818 |
| 4 | 86 | Sergio Busquets i Burgos | Defensive Midfield | Ball-Winner | 0.4694 |
| 5 | 99 | Aymeric Laporte | Center Back | Deep Playmaker | 0.4370 |

## Switzerland

- Total xT created: 1.2567
- Total xA created: 4.1514
- Pass completion under pressure: 0.7318
- Mean defensive hull area: 558.4177
- Mean defensive density: 0.0247

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 31 | Breel-Donald Embolo | Forward | Target Forward | 0.6985 |
| 2 | 67 | Granit Xhaka | Defensive Midfield | Ball-Winner | 0.5634 |
| 3 | 72 | Ricardo Iván Rodríguez Araya | Fullback/Wingback | Wide Creator | 0.5390 |
| 4 | 75 | Remo Freuler | Defensive Midfield | Ball-Winner | 0.5162 |
| 5 | 100 | Manuel Obafemi Akanji | Center Back | Ball-Playing Centre-Back | 0.4367 |

## Tunisia

- Total xT created: 1.1588
- Total xA created: 1.9897
- Pass completion under pressure: 0.5839
- Mean defensive hull area: 396.7358
- Mean defensive density: 0.0421

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## United States

- Total xT created: 1.6176
- Total xA created: 3.2488
- Pass completion under pressure: 0.7900
- Mean defensive hull area: 451.8615
- Mean defensive density: 0.0339

### Top five eligible players

| Team Rank | Global Rank | Player Name | Position Group | Functional Role | Final Player Rating |
|---|---|---|---|---|---|
| 1 | 3 | Christian Pulisic | Attacking Midfield/Wing | Progressive Winger | 0.8081 |
| 2 | 20 | Timothy Weah | Attacking Midfield/Wing | Progressive Winger | 0.7446 |
| 3 | 41 | Yunus Dimoara Musah | Central/Wide Midfield | Box-to-Box / Engine Midfielder | 0.6638 |
| 4 | 43 | Antonee Robinson | Fullback/Wingback | Attacking Wingback | 0.6612 |
| 5 | 54 | Sergino Dest | Fullback/Wingback | Attacking Wingback | 0.6278 |

## Uruguay

- Total xT created: 1.3303
- Total xA created: 1.9893
- Pass completion under pressure: 0.6460
- Mean defensive hull area: 457.0204
- Mean defensive density: 0.0260

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Wales

- Total xT created: 0.7680
- Total xA created: 1.2536
- Pass completion under pressure: 0.6856
- Mean defensive hull area: 599.2348
- Mean defensive density: 0.0252

### Top five eligible players

_No player from this team reached the configured 300-minute ranking cutoff. No lower-minute player is promoted as a substitute ranking._

## Interpretation boundary

These rankings summarize performance in the 2022 tournament sample. They are not transfer valuations, causal estimates, medical assessments, or replacements for video and scouting review.
