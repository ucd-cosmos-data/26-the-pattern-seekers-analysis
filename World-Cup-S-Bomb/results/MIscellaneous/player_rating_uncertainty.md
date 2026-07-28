# Player Rating Uncertainty (match-cluster bootstrap)

<!-- V5_CANONICAL_NOTICE -->
> **Historical V4 player-rating packet.** Player ratings, ranks, role-challenger decisions, and rating uncertainty below are superseded by `results/reports/player_rankings.csv`, `results/reports/player_profiles/`, and `results/reports/model_summary.md`. Possession, tactical, and match-bootstrap material remains a historical V4 result.


- Replicates: 2,000 (whole matches resampled with replacement)
- Scope: match-sampling uncertainty — how much a rating depends on the
  particular matches a player featured in. Per-action VAEP/xT are held fixed.
- No grade is changed; this is an additive companion to `player_evaluations.csv`.
- Teams with a statistically clear #1 (P(#1 > #2) ≥ 0.90): **12** of 18; effectively a coin-flip (< 0.60): **1**.
- Median rating standard error is 25.2% of the rating.

## Is each team's #1 statistically separated from its #2?

| Team | #1 | #2 | P(#1 > #2) | Verdict |
|---|---|---|---:|---|
| Ghana | Mohamed Salisu | Thomas Teye Partey | 0.49 | coin-flip |
| Croatia | Ivan Perišić | Andrej Kramarić | 0.72 | leaning |
| Australia | Mathew Leckie | Jackson Irvine | 0.77 | leaning |
| Argentina | Lionel Andrés Messi Cuccittini | Julián Álvarez | 0.79 | leaning |
| Morocco | Youssef En-Nesyri | Sofiane Boufal | 0.81 | leaning |
| United States | Christian Pulisic | Timothy Weah | 0.84 | leaning |
| Brazil | Richarlison de Andrade | Raphael Dias Belloli | 0.93 | clear |
| France | Kylian Mbappé Lottin | Olivier Giroud | 0.94 | clear |
| Netherlands | Memphis Depay | Cody Mathès Gakpo | 0.95 | clear |
| Senegal | Ismaïla Sarr | Boulaye Dia | 0.97 | clear |
| England | Harry Kane | Luke Shaw | 1.00 | clear |
| Japan | Daichi Kamada | Junya Ito | 1.00 | clear |
| Iran | Mehdi Taremi | Morteza Pouraliganji | 1.00 | clear |
| Poland | Robert Lewandowski | Piotr Zieliński | 1.00 | clear |
| Portugal | Cristiano Ronaldo dos Santos Aveiro | João Félix Sequeira | 1.00 | clear |
| South Korea | Heung-Min Son | Jin-Su Kim | 1.00 | clear |
| Spain | Daniel Olmo Carvajal | Pedro González López | 1.00 | clear |
| Switzerland | Breel-Donald Embolo | Ricardo Iván Rodríguez Araya | 1.00 | clear |

## Most and least certain grades

| Player | Team | Rating | SE | 95% CI | Rank | P(rank 1) |
|---|---|---:|---:|---|---:|---:|
| Lionel Andrés Messi Cuccittini | Argentina | 0.330 | 0.061 | [0.211, 0.452] | 1 | 0.63 |
| Mathew Leckie | Australia | 0.137 | 0.023 | [0.102, 0.185] | 1 | 0.76 |
| Ivan Perišić | Croatia | 0.214 | 0.031 | [0.156, 0.275] | 1 | 0.71 |
| Richarlison de Andrade | Brazil | 0.298 | 0.019 | [0.253, 0.327] | 1 | 0.89 |
| Mehdi Taremi | Iran | 0.225 | 0.017 | [0.193, 0.256] | 1 | 0.95 |
| Mohamed Salisu | Ghana | 0.001 | 0.004 | [-0.008, 0.007] | 1 | 0.47 |

Interpretation: a high P(#1 > #2) means the team's top grade is robust to which
matches happened to be played; a low value means the top two are interchangeable
given the sample. This does not change any rating — it says how much to trust each.
