# World Cup S-Bomb Model Summary

## Active release

- Outfield: `ranking-repair-v3.0-qatar-2022`, unchanged.
- Goalkeeper: `goalkeeper_consolidated_value_v5`, one active metric.
- Publication separation: global and 300-minute rankings are outfield-only;
  goalkeepers are ranked exclusively in their dedicated v5 table.

## Goalkeeper v5 equation

`GKComponent = 0.45*PSxG + 0.25*ClutchResidual
+ 0.05*RegularPenalty + 0.20*ShootoutWPA + 0.05*Support`

`GKRaw = Reliability*GKComponent + (1-Reliability)*CohortMean`

PSxG prevention is `p(post-shot goal) - observed goal`. The calibrated
post-shot model is trained with match-disjoint GroupKFold. The clutch channel
adds only incremental late/high-consequence residual, preventing the base save
from being counted twice. Penalties and shootouts use sample-reliability
shrinkage; shootouts enter through bounded win-probability added.

For keepers with at least 360 minutes, if expected threat faced per 90 is below
the goalkeeper-cohort median and the ordinary-play component is below its
cohort mean:

`OrdinaryAdjusted = OrdinaryMean
+ min(1, ThreatFaced90/MedianThreatFaced90)^2
* (Ordinary-OrdinaryMean)`

This is a downside-confidence correction for sparse, defense-limited
shot-stopping evidence. It never increases positive ordinary-play evidence and
does not change penalties, shootouts, or support play.

## Inputs and exclusions

The model uses event-derived shot location/height, body part, technique, shot
type, one-on-one and first-time indicators; pre-action score/time/stage state;
regular penalties; shootout state; and low-weight support actions. It does not
use goalkeeper identity, team advancement, awards, trophies, reputation,
pedigree, or named-opponent strength.

## Release gates

The single metric was promoted only after all twelve hard gates passed,
including identity blindness, PSxG integrity, Kolo Muani save monotonicity,
shootout-removal monotonicity, one-metric publication, no pedigree feature,
and byte-preservation of the v3/v4 baselines. Six of eight soft checks passed.
The model remains a tournament-sample valuation rather than a career-quality
claim.

## Preserved outfield products

**Tournament Impact** remains the active outfield estimand. **Role Quality**
and **Uncertainty** remain separate explanatory products rather than score
bonuses. Ordinary outfield evidence uses periods 1–4; Period 5 shootouts are
excluded. The historical goalkeeper v3 publication used 40% shot stopping and
a 10% cap and a cross-position bridge. Those details are retained only to
explain the frozen baseline, not as the active goalkeeper formula.
