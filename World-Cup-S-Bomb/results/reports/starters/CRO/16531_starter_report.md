# Dominik Livaković — Qatar 2022 Goalkeeper Profile

## Active tournament valuation

- Team: Croatia
- Minutes: 720.3
- Status: Ranked (team main goalkeeper)
- Goalkeeper rank: 1
- Consolidated Goalkeeper Value: 1.0000
- Raw consolidated value: 0.2016
- 95% score interval: 0.1667 to 1.0000
- Bootstrap rank interval: 1 to 27

## Evidence channels

| Channel | Value |
|---|---:|
| PSxG shot-stopping | 0.3067 |
| Clutch-save residual | 0.4903 |
| Regular-penalty impact | -0.2265 |
| Shootout win probability added | 0.3333 |
| Support value | -0.2359 |
| Expected threat faced per 90 | 1.2079 |
| Defensive-shield downside adjustment | 0.0000 |
| Reliability | 0.6155 |

The active goalkeeper ranking is one consolidated, identity-blind metric. It values
ordinary shot prevention from calibrated post-shot probabilities, adds only the
incremental residual for late high-consequence saves, and applies sample-size
reliability to penalties, shootouts, and the final score. When at least four
matches of evidence show below-median threat faced, a below-prior ordinary-play
downside is additionally shrunk toward the cohort prior; positive evidence,
penalties, shootouts, and support play are unchanged. Advancement, awards,
reputation, and named-player rules are not scoring inputs.

Goalkeepers are excluded from the global outfield and 300-minute rankings.
