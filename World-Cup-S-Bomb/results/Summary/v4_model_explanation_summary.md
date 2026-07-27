# World Cup V4 Model Summary

## V4 Model Explanations

This document is the canonical technical summary for the consolidated World
Cup coaching pipeline. The production pipeline has schema version 4 and uses
the locked `transition-conceded-v2` classifier bundle for rare-event
probabilities. The player-evaluation, spatial, simulation, and reporting layers
are V4.

The system is intended for coaching review, opponent preparation, and
prioritizing possessions for video analysis. It is not a causal model, an
automated lineup selector, or a substitute for medical, scouting, and
match-context judgment.

## System architecture

The pipeline combines four connected layers:

1. **Rare transition classifier:** estimates the probability that a possession
   leads to `transition_conceded`.
2. **Probability calibration and decision gate:** applies Platt calibration and
   abstains when no threshold reaches the required precision.
3. **Hurdle and counterfactual evaluation:** combines calibrated event risk with
   conditional xG, tactical scenarios, lineup context, and substitution
   constraints.
4. **V4 player and spatial evaluation:** integrates event value, pressure,
   tournament minutes, functional roles, successful action endpoints, and
   StatsBomb 360 freeze-frame context.

## Offensive and defensive variable dictionary

### How influence is reported

The production rare-event classifier is Logistic Regression. Its numeric
inputs are median-imputed, standardized, and then multiplied by the learned
coefficient. A positive coefficient raises the fitted log-odds of
`transition_conceded`; a negative coefficient lowers them. These are learned
associations, not causal effects. With only seven positive training examples,
coefficient signs can be unstable or counterintuitive.

Categorical inputs are one-hot encoded. Each learned category coefficient moves
the log-odds relative to the fitted intercept. Team and opponent effects are
tournament-specific context controls, not general team-strength ratings.

### Direct production-classifier variables

These 16 variables are the complete serialized input schema in
`models/coaching_model_benchmark_v2.joblib`.

| Variable | Side | Meaning and model influence |
|---|---|---|
| `play_pattern` | Both | One-hot possession origin. In the fitted model, goal kicks (+2.390), free kicks (+1.964), and throw-ins (+1.463) raise fitted transition-concession log-odds; regular play (-2.107), kickoffs (-1.215), keeper restarts (-1.197), corners (-0.800), and counters (-0.561) lower them. |
| `competition_stage` | Context | One-hot tournament round. Round of 16 (+2.334) and third-place final (+1.062) raise fitted log-odds; group stage (-0.231), quarter-finals (-0.701), final (-1.053), and semi-finals (-1.475) lower them. These effects should be treated as sample context. |
| `score_state` | Both | Whether the attacking team is trailing, tied, or leading. Trailing has a positive fitted effect (+2.193); leading (-1.490) and tied (-0.768) have negative fitted effects. |
| `attacking_style` | Offense | Tactical possession label. `Short Under Pressure` raises fitted log-odds (+2.753), `Direct Long Play` lowers them (-2.789), and `Patient Build-up` is close to neutral (-0.029) in this sample. |
| `team` | Both | One-hot attacking-team identity used to absorb tournament-specific baseline differences. Coefficients range from Tunisia (-2.304) to Poland (+3.776); they are not transferable quality ratings. |
| `opponent` | Defense | One-hot defending-team identity used to absorb opponent-specific context. Coefficients range from Spain (-2.346) to Croatia (+3.042); they are not causal defensive ratings. |
| `period` | Context | Match period. One-standard-deviation increase has coefficient -0.951. |
| `start_minute` | Context | Possession start minute. Later possessions raise fitted log-odds in the current model (+1.201 per standard deviation). |
| `start_x` | Offense | Possession starting X coordinate on the 120x80 pitch. More advanced starts lower fitted log-odds in the current model (-1.220 per standard deviation). |
| `start_y` | Both | Possession starting lateral coordinate. The fitted effect is small and positive (+0.313 per standard deviation). |
| `score_difference` | Context | Attacking-team score minus opponent score. The fitted effect is nearly neutral (+0.081 per standard deviation). |
| `team_prior_xg_per_possession` | Offense | Cross-fitted historical attacking threat before the evaluated match. The fitted coefficient is -0.689 per standard deviation. |
| `team_prior_transition_shot_conceded` | Defense | Cross-fitted prior transition-shot exposure for the attacking team. The fitted coefficient is -0.853 per standard deviation. The counterintuitive sign is a warning about rarity and correlated priors. |
| `opponent_prior_counter_shot` | Defense | Cross-fitted prior counterattacking-shot threat of the opponent. The fitted coefficient is -1.005 per standard deviation and should not be interpreted causally. |
| `matchup_rest_defense_vs_counter` | Defense | `(attacking-lineup recoveries/90 + pressures/90) / (1 + opponent progressive passes/90 + progressive carries/90)`. Higher values currently raise fitted log-odds (+1.453 per standard deviation), another rarity-sensitive association rather than proof that better rest defense is harmful. |
| `matchup_turnover_counter_pressure` | Both | `attacking-lineup turnovers/90 × (opponent progressive passes/90 + progressive carries/90)`. This is the strongest positive numeric effect (+2.513 per standard deviation): frequent turnovers combined with an opponent capable of progressing counters increase fitted transition risk. |

The classifier target is `transition_conceded`, derived from
`opponent_transition_shot`. Current-possession shot, goal, xG, box-entry, and
transition outcomes are not direct predictor columns. Historical priors are
computed outside the evaluated match to preserve leakage safety.

### Offensive player and lineup variables

The player-aware feature builder creates both lineup mean and lineup maximum
for every variable below. These variables support model benchmarking, matchup
construction, role evaluation, and simulations. Only
`matchup_rest_defense_vs_counter` and `matchup_turnover_counter_pressure` from
this larger layer enter the final serialized transition classifier directly.

| Offensive variable | Definition | Influence on evaluation |
|---|---|---|
| `pass_completion` | Completed passes / passes | Rewards reliable possession and supports pressure-resistance interpretation. |
| `progressive_passes_p90` | Progressive passes per 90 | Increases measured ball advancement and opponent counter capacity when calculated for the defending lineup after a regain. |
| `final_third_passes_p90` | Final-third passes per 90 | Represents sustained territorial penetration. |
| `box_passes_p90` | Passes into the penalty area per 90 | Represents direct creation near goal. |
| `key_passes_p90` | Key passes per 90 | Adds creative contribution; contributes positively to the displayed Net xG proxy. |
| `crosses_p90` | Crosses per 90 | Captures wide creation and helps identify `Wide Creator` roles. |
| `switches_p90` | Switches of play per 90 | Represents ability to move a defense laterally. |
| `through_balls_p90` | Through balls per 90 | Represents line-breaking chance creation. |
| `progressive_carries_p90` | Progressive carries per 90 | Rewards ball progression, helps identify Progressive Wingers, and increases modeled opponent counter threat when measured on the opponent. |
| `dribble_success` | Successful dribbles / dribbles | Measures ability to beat defenders; combined with defensive duel ability in `matchup_dribble_vs_duel`. |
| `shots_p90` | Shots per 90 | Measures shooting volume and helps identify Target Forwards. |
| `xg_p90` | StatsBomb shot xG per 90 | Measures shot quality and is the largest positive term in the displayed Net xG proxy. |
| `pressure_retention` | Successful under-pressure actions / under-pressure actions | Measures resistance to defensive pressure; combined with opponent pressure volume in `matchup_pressure_resistance`. |
| `turnovers_p90` | Turnovers per 90 | Negative possession-security signal; directly increases `matchup_turnover_counter_pressure`. |
| `pass_progression_per_pass` | Total pass progression / passes | Measures forward distance gained per pass and helps identify Deep Playmakers. |
| `carry_progression_per_carry` | Total carry progression / carries | Measures forward distance gained per carry. |
| `aerial_win_rate` | Aerial wins / aerial events | Measures direct-play and target ability; compared with opponent aerial strength in `matchup_aerial_edge`. |

The displayed descriptive Net xG proxy is:

`xg_p90 + 0.015×key_passes_p90 + 0.004×progressive_passes_p90 + 0.003×progressive_carries_p90 + 0.002×interceptions_p90 - 0.002×turnovers_p90`.

It is a report diagnostic, not the rare-event classifier target.

### Defensive player and lineup variables

The feature builder calculates lineup means and maxima for these defensive
variables. It evaluates both the defending lineup and the attacking lineup's
rest-defense capacity after a turnover.

| Defensive variable | Definition | Influence on evaluation |
|---|---|---|
| `pressures_p90` | Pressures per 90 | Raises pressing activity and the attacking lineup's rest-defense numerator. |
| `counterpressures_p90` | Counterpressures per 90 | Measures immediate pressure following loss of possession. |
| `duel_win_rate` | Duels won / duels | Represents ability to stop dribblers and is used in `matchup_dribble_vs_duel`. |
| `interceptions_won_p90` | Won interceptions per 90 | Measures passing-lane disruption and reduces `matchup_progression_vs_interception`. |
| `interception_win_rate` | Won interceptions / interception attempts | Measures interception efficiency. |
| `recoveries_p90` | Recoveries per 90 | Raises the rest-defense numerator in `matchup_rest_defense_vs_counter`. |
| `blocks_p90` | Blocks per 90 | Represents shot/pass obstruction. |
| `clearances_p90` | Clearances per 90 | Represents emergency box and defensive-zone removal. |
| `dribbled_past_p90` | Times dribbled past per 90 | Defensive vulnerability indicator; higher values are unfavorable. |
| `fouls_p90` | Fouls per 90 | Represents disruption but also set-piece and disciplinary risk; it is not assumed to be uniformly beneficial. |
| `aerial_win_rate` | Aerial wins / aerial events | Represents defensive control of direct balls and is used in the aerial matchup edge. |

The physicality layer also derives:

- `aerial_dominance_index = aerial_wins / aerial_events`.
- `pressing_intensity_index = 90 × (non-aerial duel-win proxy + interceptions + pressures) / minutes`.
- `speed_recovery_index = 90 × recoveries / minutes`. This is an event-derived
  recovery proxy, not optical-tracking speed.

### Derived offense-versus-defense matchup variables

| Derived variable | Formula and influence |
|---|---|
| `matchup_dribble_vs_duel` | `att_max_dribble_success × (1 - def_max_duel_win_rate)`. Higher values indicate an attacker-versus-defender dribbling advantage. |
| `matchup_pressure_resistance` | `att_mean_pressure_retention / (1 + def_mean_pressures_p90)`. Higher values indicate better retention against the opponent's press. |
| `matchup_aerial_edge` | `att_max_aerial_win_rate - def_max_aerial_win_rate`. Positive values favor the attacking lineup aerially. |
| `matchup_progression_vs_interception` | `att_mean_progressive_passes_p90 / (1 + def_mean_interceptions_won_p90)`. Higher values indicate a progression advantage over passing-lane disruption. |
| `matchup_rest_defense_vs_counter` | Attacking-lineup recovery and pressure capacity divided by opponent progressive counter capacity. This is a direct classifier input. |
| `matchup_turnover_counter_pressure` | Attacking turnovers multiplied by opponent progressive counter capacity. This is a direct classifier input and currently has the strongest positive numeric coefficient. |

### Hurdle offense, defense, and physical-adjustment variables

| Variable | Side | Role in expected Net xG |
|---|---|---|
| `team` | Both | Selects the regularized team-by-style hurdle table. |
| `attacking_style` | Offense | Selects Patient Build-up, Short Under Pressure, or Direct Long Play scenario rates. |
| `shot` | Offense | Estimates attack-event probability by style. |
| `xg_generated` | Offense | Estimates conditional attacking xG given a shot event. |
| `transition_conceded` | Defense | Estimates transition-event probability before the calibrated classifier replaces/gates it. |
| `opponent_transition_xg` | Defense | Estimates conditional transition xG and trains the transition physical residual model. |
| `net_xg_15` | Both | Residual target used to fit the regularized physical Net xG adjustment. |
| `lineup_avg_aerial_dominance` | Both | Mean attacking-lineup aerial strength. Its residual influence is learned by Ridge regression. |
| `lineup_max_pressing_rate` | Defense | Strongest lineup pressing value; used for pressing-boost sensitivity and residual adjustment. |
| `lineup_min_recovery_speed` | Defense | Weakest lineup recovery proxy; exposes the slowest recovery link. |
| `lineup_overall_lineup_chemistry_score` | Offense | Mean pairwise lineup chemistry; higher values represent broader passing familiarity. |
| `lineup_weakest_link_chemistry` | Offense | Minimum pairwise chemistry; represents the least-connected lineup relationship. |
| `delta_aerial` | Both | Attacking lineup aerial value minus opponent aerial value. |
| `delta_pressing` | Defense | Attacking lineup pressing value minus opponent pressing value. |
| `delta_recovery` | Defense | Attacking lineup recovery value minus opponent recovery value. |

The hurdle equations are:

- `expected_attack_xg = attack_probability × attack_conditional_xg`
- `expected_transition_xg = gated_calibrated_transition_probability × transition_conditional_xg`
- `expected_net_xg = expected_attack_xg - expected_transition_xg + physical_net_adjustment`

Because no precision-valid threshold exists, the current deployed transition
probability is gated to zero for actionable recommendations. The calibrated
probability is still retained for evaluation and calibration diagnostics.

### Spatial and player-ranking variables

| Variable | Side | Influence |
|---|---|---|
| `start_x`, `start_y`, `end_x`, `end_y` | Offense | Define on-ball movement and the open-event value change. |
| `pass_start_x`, `pass_start_y` | Offense | Describe average passing origin for spatial role clustering. |
| `pass_receipt_x`, `pass_receipt_y` | Offense | Describe average receipt location for spatial role clustering. |
| `line_breaking_pass_rate` | Offense | Share of passes gaining at least 15 X units or entering the final third. |
| `final_third_share` | Offense | Share of successful action endpoints and linked SB360 actor points with X > 80. |
| `pressure_state_rate` | Defense/context | Share of passes attempted under event pressure. |
| `distribution_under_pressure` | Both | Completion rate on pressured passes. |
| `under_pressure` / `event_under_pressure` | Defense/context | Event-provider pressure flag. |
| `nearest_defender_distance` | Defense | SB360 distance context; distance ≤3 contributes to freeze-frame pressure. |
| `defenders_within_5` | Defense | SB360 local pressure count; at least two contributes to freeze-frame pressure. |
| `defensive_density` | Defense | SB360 local density; top-quartile density contributes to freeze-frame pressure. |
| `pressure_augmented` | Defense/context | OR of event pressure and SB360-derived pressure. |
| `raw_on_ball_value` | Offense | Native OBV when available; otherwise the documented pitch-value fallback. |
| `standard_turnover_penalty` | Both | Location-sensitive cost: `0.010 + 0.030×start_x/120` for turnovers. |
| `turnover_penalty_multiplier` | Defense/context | Equals 0.5 for pressured turnovers and 1.0 otherwise. |
| `risk_adjusted_on_ball_value` | Offense | Raw on-ball value minus the applied turnover penalty. |
| `obv_per_90` | Offense | Risk-adjusted on-ball value per 90 and the primary attacking-role score input. |
| `pressure_adjusted_turnover_penalty_per_90` | Both | Turnover-cost burden after the 50% pressure discount. Lower burden improves turnover-resilience score. |
| `aerial_dominance_index` | Defense/direct play | Role-relative aerial component. |
| `pressing_intensity_index` | Defense | Role-relative pressing component. |

For attacking position groups, the V4 role composite uses 65%
`role_obv_z`, 20% `role_final_third_z`, and 15%
`role_turnover_resilience_z`. For other positions it uses 35% `role_obv_z`,
15% `role_final_third_z`, 20% `role_turnover_resilience_z`, 15%
`role_pressing_z`, and 15% `role_aerial_z`. The resulting composite is
standardized only within `Functional role`.

### Supporting attacking-style clustering variables

These variables are standardized and passed to K-Means to discover attacking
styles. They influence the assigned `attacking_style` through distance to the
learned cluster centroids; they are not individually passed to the final
transition classifier. Shot, goal, xG, penalty-area entry, and final-third
entry outcomes are deliberately excluded from the clustering inputs.

| Variable | Influence on the attacking-style representation |
|---|---|
| `duration_log` | Log possession duration; separates patient sequences from fast attacks while limiting extreme-duration leverage. |
| `players_involved` | Number of distinct attacking players; higher values indicate broader collective involvement. |
| `pass_count_log` | Log pass volume; raises the build-up component without allowing very long sequences to dominate. |
| `pass_completion_pct` | Possession passing reliability. |
| `average_pass_length` | Distinguishes short circulation from direct distribution. |
| `progressive_pass_share` | Progressive passes divided by all passes; raises vertical-progression character. |
| `long_ball_share` | Long balls divided by all passes; raises direct-play character. |
| `switch_share` | Switches divided by all passes; raises lateral-redirection character. |
| `cross_share` | Crosses divided by all passes; raises wide-delivery character. |
| `carry_count_log` | Log carry volume; raises carry-oriented style character. |
| `progressive_carry_share` | Progressive carries divided by all carries; raises ball-carry progression character. |
| `total_carry_distance_log` | Log total carry distance; captures cumulative carrying while limiting outlier leverage. |
| `longest_carry_distance` | Longest carry in the possession; identifies possessions containing a major individual advance. |
| `dribble_count_log` | Log dribble volume; raises one-versus-one attacking character. |
| `net_forward_distance` | Net X-axis advance from possession start to finish. |
| `total_forward_progression_log` | Log cumulative forward progression from passes and carries. |
| `directness_ratio` | Forward displacement relative to total movement; higher values indicate a straighter route to goal. |
| `progression_speed` | Forward progression per unit of possession time; raises fast-vertical style character. |
| `width_std_y` | Standard deviation of lateral action locations; captures how dispersed the possession is across width. |
| `width_span_y` | Maximum minus minimum lateral location; raises wide-possession character. |
| `under_pressure_rate` | Pressured attacking actions divided by attacking actions; identifies play performed under pressure. |
| `opponent_pressure_rate` | Opponent pressure events divided by attacking actions; represents external press intensity faced. |

The recommendation table also stores each of these standardized cluster
coordinates with the `candidate_z_` prefix:
`candidate_z_duration_log`, `candidate_z_players_involved`,
`candidate_z_pass_count_log`, `candidate_z_pass_completion_pct`,
`candidate_z_average_pass_length`, `candidate_z_progressive_pass_share`,
`candidate_z_long_ball_share`, `candidate_z_switch_share`,
`candidate_z_cross_share`, `candidate_z_carry_count_log`,
`candidate_z_progressive_carry_share`,
`candidate_z_total_carry_distance_log`,
`candidate_z_longest_carry_distance`, `candidate_z_dribble_count_log`,
`candidate_z_net_forward_distance`,
`candidate_z_total_forward_progression_log`,
`candidate_z_directness_ratio`, `candidate_z_progression_speed`,
`candidate_z_width_std_y`, `candidate_z_width_span_y`,
`candidate_z_under_pressure_rate`, and
`candidate_z_opponent_pressure_rate`. In benchmark alternatives these describe
the proposed attacking style relative to the tournament distribution.

### Supporting defensive-style and defensive-role clustering variables

The defensive-style variables below are standardized and clustered. Their
influence is geometric: larger or smaller values move a possession toward a
different defensive centroid. They define `defensive_style` and historical
opponent style shares, but are not direct inputs to the serialized production
classifier.

| Variable | Influence on the defensive-style representation |
|---|---|
| `back_line_height` | Average X location of the deepest defensive line; higher values indicate a more advanced line. |
| `line_height_stability` | Stability of line height across frames; distinguishes a fixed block from a vertically variable line. |
| `hull_area_per_defender_log` | Log convex-hull area per defender; higher values indicate a more spatially spread shape. |
| `defensive_width` | Lateral span of defenders; higher values indicate a wider block. |
| `defensive_depth` | Front-to-back span of defenders; higher values indicate a deeper or more stretched block. |
| `behind_ball_share` | Share of visible defenders behind the ball; raises rest-defense/block protection character. |
| `central_defender_share` | Share of defenders in the central corridor; raises central compactness character. |
| `near_ball_5_share` | Share of defenders within five pitch units of the ball; raises immediate local pressure character. |
| `near_ball_10_share` | Share within ten units; raises surrounding pressure density. |
| `nearest_defender_distance` | Distance from the ball to the nearest defender; lower values indicate tighter pressure. |
| `mean_defender_distance` | Mean defender-to-ball distance; lower values indicate collective compression around the ball. |
| `pressure_rate` | Pressure events per eligible possession/action unit; raises active-press character. |
| `counterpress_rate` | Counterpress events per eligible unit; raises immediate post-loss pressure character. |
| `defensive_action_rate` | Defensive actions per eligible unit; raises overall defensive activity. |

Separate defensive-player role clustering uses:

| Variable | Influence on the defensive-player role |
|---|---|
| `pressure_share` | Player pressures divided by all defensive actions; raises Pressing Disruptor character. |
| `counterpress_share` | Counterpressures divided by defensive actions; raises post-loss pressing character. |
| `duel_share` | Duels divided by defensive actions; raises Duel Specialist character. |
| `interception_share` | Interceptions divided by defensive actions; raises passing-lane protection character. |
| `block_share` | Blocks divided by defensive actions; raises deep obstruction character. |
| `clearance_share` | Clearances divided by defensive actions; raises emergency/deep defending character. |
| `recovery_share` | Ball recoveries divided by defensive actions; raises Ball-Winning/Recovery character. |
| `foul_share` | Fouls divided by defensive actions; captures disruptive but potentially costly intervention. |
| `actor_x` | Average X location when performing defensive actions; separates high defenders from deep defenders. |
| `lateral_distance` | Absolute distance from pitch center (`abs(actor_y - 40)`); separates central and wide defensive roles. |

### Benchmark-only offense, defense, and context variables

The benchmark scripts compare richer alternatives with the locked production
classifier. The following variables can influence those benchmark predictions,
but are not all present in `models/coaching_model_benchmark_v2.joblib`.

The shared start context is `period`, `start_minute`, `start_x`, and `start_y`.
Transition benchmarks additionally use `score_difference`; categorical
context is `attacking_style`, `first_play_pattern`, `competition_stage`, and,
for transition benchmarks, `score_state`.

Historical attacking-team variables are:

- `team_goals_before`, `team_prior_matches`, and `team_prior_possessions`
  control the amount and context of prior evidence.
- `team_prior_xg_per_possession`, `team_prior_shot_rate`, and
  `team_prior_box_rate` describe prior attacking quality and penetration.
- `team_prior_transition_final_third_conceded`,
  `team_prior_transition_box_conceded`,
  `team_prior_transition_shot_conceded`, and
  `team_prior_transition_xg_conceded` describe prior rest-defense exposure.
- `team_attack_share__Patient Build-up`,
  `team_attack_share__Short Under Pressure`, and
  `team_attack_share__Direct Long Play` describe the team's historical style
  mixture.

Historical opponent variables are:

- `opponent_goals_before`, `opponent_prior_matches`, and
  `opponent_prior_possessions` control score and evidence context.
- `opponent_prior_xg_allowed`, `opponent_prior_shot_allowed`, and
  `opponent_prior_box_allowed` describe prior defensive allowance.
- `opponent_prior_counter_final_third`, `opponent_prior_counter_box`,
  `opponent_prior_counter_shot`, and `opponent_prior_counter_xg` describe
  prior counterattacking threat.
- `opponent_defense_share__Wide Retreating Block`,
  `opponent_defense_share__High-Intensity Press`,
  `opponent_defense_share__Set-Piece Compact Shape`, and
  `opponent_defense_share__Compact Pressure Block` describe historical
  defensive-style mixture.
- `opponent_prior_avg_back_line_height`,
  `opponent_prior_std_back_line_height`,
  `opponent_prior_avg_defensive_hull_area`,
  `opponent_prior_avg_defensive_width`,
  `opponent_prior_avg_defensive_depth`,
  `opponent_prior_avg_defenders_behind_ball`,
  `opponent_prior_avg_central_defenders`,
  `opponent_prior_avg_defenders_within_5`,
  `opponent_prior_avg_defenders_within_10`,
  `opponent_prior_avg_nearest_defender_distance`, and
  `opponent_prior_avg_mean_defender_distance` describe the opponent's
  historical SB360 defensive geometry. Higher/lower effects are learned by
  each benchmark estimator rather than imposed as fixed causal weights.

Player-aware benchmark columns apply explicit prefixes to the lineup
statistics already defined above:

- `att_mean_...` and `att_max_...` are the attacking lineup's mean and best
  attacking-skill values.
- `att_recovery_mean_...` and `att_recovery_max_...` are the attacking
  lineup's mean and best defensive/rest-defense values.
- `def_mean_...` and `def_max_...` are the defending lineup's mean and best
  defensive values.
- `opp_counter_mean_...` and `opp_counter_max_...` are the opponent lineup's
  mean and best attacking values used as counterattack capacity.
- The exact suffixes for `att_` and `opp_counter_` are
  `pass_completion`, `progressive_passes_p90`, `final_third_passes_p90`,
  `box_passes_p90`, `key_passes_p90`, `crosses_p90`, `switches_p90`,
  `through_balls_p90`, `progressive_carries_p90`, `dribble_success`,
  `shots_p90`, `xg_p90`, `pressure_retention`, `turnovers_p90`,
  `pass_progression_per_pass`, `carry_progression_per_carry`, and
  `aerial_win_rate`.
- The exact suffixes for `att_recovery_` and `def_` are `pressures_p90`,
  `counterpressures_p90`, `duel_win_rate`, `interceptions_won_p90`,
  `interception_win_rate`, `recoveries_p90`, `blocks_p90`,
  `clearances_p90`, `dribbled_past_p90`, `fouls_p90`, and
  `aerial_win_rate`.
- `att_mean_profile_minutes`, `att_recovery_mean_profile_minutes`,
  `def_mean_profile_minutes`, and `opp_counter_mean_profile_minutes`
  describe the evidence volume behind lineup profiles.
- `att_known_player_share`, `att_recovery_known_player_share`,
  `def_known_player_share`, and `opp_counter_known_player_share` describe
  lineup coverage; lower coverage signals greater reliance on priors.

Finally, all six `matchup_` variables documented earlier are included in the
player-aware benchmarks. The benchmark classification targets are `shot`,
`entered_penalty_area`, `transition_final_third_15`,
`transition_box_15`, and `transition_shot_15`; the hurdle regressions also use
`xg_generated`, `opponent_transition_xg`, and expected Net xG outputs. Targets
measure outcomes and are never treated as same-possession predictor inputs.

## Rare-event classification model

| Item | Production value |
|---|---|
| Target | `transition_conceded` |
| Selected classifier | Logistic Regression |
| Serialized model | `models/coaching_model_benchmark_v2.joblib` |
| Calibration | Platt |
| Threshold status | No validated threshold; abstention |
| Training matches | 35 |
| Calibration matches | 10 |
| Threshold-selection matches | 10 |
| Untouched test matches | 9 |
| Test rows / positives | 1,349 / 2 |
| Test positive rate | 0.1483% |
| Unique test probabilities | 1,252 |
| Test Brier score | 0.001478 |
| Test PR-AUC | 0.016655 |
| Test ROC-AUC | 0.742019 |

Logistic Regression was selected from Logistic Regression, Random Forest,
Histogram Gradient Boosting, and XGBoost candidates. Training, calibration,
threshold selection, and test match sets are disjoint. Serialized-artifact
replay reproduces the saved probabilities.

The threshold optimizer did not find a threshold satisfying the required
precision floor. The production behavior is therefore to abstain rather than
emit low-confidence transition warnings. Precision, recall, and F-0.5 are
undefined for this abstaining policy, not zero.

## Tournament out-of-fold validation

| Metric | Result |
|---|---:|
| Matches | 64 |
| Teams | 32 |
| OOF possessions | 9,685 |
| Positive events | 13 |
| Brier score | 0.001339 |
| PR-AUC | 0.005958 |
| ROC-AUC | 0.689341 |
| Unique probabilities | 8,739 |

Every evaluated match was excluded from model fitting and fold calibration.
The nonconstant probability output confirms that the classifier has not
collapsed to a single prediction. The very low PR-AUC nevertheless shows that
individual positive-event identification remains difficult at this event
rate.

## Hurdle and counterfactual layer

The hurdle evaluator estimates expected transition cost from the calibrated
event probability and the conditional xG model. If the classifier abstains or
the calibrated probability is below a validated threshold, the actionable
transition-risk contribution resolves to zero.

Substitution simulations enforce position compatibility, formation
requirements, available minutes, realistic timing, a minimum expected Net xG
gain of `0.0050`, and a match-bootstrap confidence interval strictly above
zero. In the current production run:

| Counterfactual result | Count |
|---|---:|
| Tactical scenarios evaluated | 29,055 |
| Validated substitutions | 0 |
| Suppressed substitutions | 3,608 |

This is a safety result: the model found no substitution with enough evidence
to publish as a validated intervention.

## Player evaluation

Players with fewer than 300 tournament minutes are excluded before ranking.
The current cohort contains 142 of 680 observed players; 538 were removed by
the sample-size cutoff.

For attacking roles, the primary value signal is risk-adjusted OBV per 90.
Turnovers receive a location-sensitive penalty, and a turnover under event or
SB360-derived pressure receives exactly 50% of the normal penalty. This avoids
penalizing difficult high-block possessions as heavily as unpressured losses.

The supplied open-data export does not contain licensed StatsBomb proprietary
OBV. The production artifact therefore uses the explicitly labeled
`open_event_value_fallback`. It must not be described as native proprietary
OBV.

The role composite is standardized with
`groupby("Functional role")`. A score of 50 is the role mean and 10 score
points represent one population standard deviation within that role.

## Standard event, metadata, and StatsBomb 360 distinctions

1. **Standard event data** supplies player actions, outcomes, start locations,
   pass endpoints, carry endpoints, shot xG, and the event-level
   `under_pressure` flag.
2. **Player and match metadata** supplies player identity, team, position,
   lineup context, and tournament minutes.
3. **StatsBomb 360** links event UUIDs to visible actor locations, defensive
   density, nearby-defender counts, and nearest-defender distance.

The spatial layer includes 81,231 successful action endpoints and 72,016 linked
SB360 actor snapshots. A total of 203,454 events have SB360 context, producing
142 player heatmaps over 9,394 pitch-density cells.

StatsBomb 360 contains event-time freeze-frame snapshots, not continuous
optical tracking. The heatmaps represent observed successful endpoints and
visible actor positions; they do not reconstruct unobserved movement between
events.

Fullbacks and wingbacks are protected from the `Holding Anchor` role. Players
above the 35% combined final-third spatial threshold are classified as
`Attacking Wingback`. Hakimi and Dest are currently classified as
`Wide Creator`, not `Holding Anchor`.

## Report artifacts

| Artifact | Count or path |
|---|---|
| Team reports | 32 |
| Player heatmaps | 142 |
| Compiled report files | 64 |
| Final tournament report | `results/reports/final/world_cup_team_performance_and_top_players.md` |
| Pipeline manifest | `results/reports/pipeline_manifest.json` |
| Full validation output | `results/MIscellaneous/eda_validation_report.json` |

## Known limitations

- The event prevalence is approximately 0.13%, leaving only 13 OOF positive
  examples. Metrics and threshold estimates therefore have high uncertainty.
- The current classifier abstains because no tested threshold achieved the
  required precision. It should not be represented as a validated binary alert
  model.
- ROC-AUC is moderate, but PR-AUC is low. For this rare-event problem, PR-AUC,
  calibration, and decision utility are more informative than accuracy.
- Player scores are normalized within functional role and are not valid
  cross-role measures of absolute quality.
- The consolidated team leaderboard currently sorts role-relative scores
  across different roles. This can produce misleading team-wide ordering, such
  as Mbappé appearing fifth for France despite leading France in displayed Net
  xG/90. That ordering is a report-layer limitation and should be corrected
  before treating the list as an overall player rank.
- Open-event value is a documented fallback rather than licensed StatsBomb
  OBV.
- Counterfactual results are predictive scenarios, not causal estimates of
  what would have happened under another tactic or lineup.

## Current validity statement

The pipeline is valid for exploratory, probability-aware coaching support and
video-review prioritization over the supplied tournament data. Its leakage
controls, calibration split, artifact replay, spatial provenance, minute
cutoff, and counterfactual suppression rules are defensible. It is not yet
strong enough for autonomous rare-event alerts or cross-role player ranking.
