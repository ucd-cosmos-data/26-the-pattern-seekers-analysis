# Project Proposal: Discovering Attacking Styles and Their Effectiveness Against Different Defensive Systems in the 2022 FIFA World Cup

## Research Question

**Can unsupervised machine learning discover distinct attacking styles in the 2022 FIFA World Cup, and which of those styles are most effective against different defensive approaches?**

Rather than manually defining tactics like "counterattack" or "possession football," this project uses clustering to identify naturally occurring attacking styles from StatsBomb event data. The project then evaluates how effective each style is against various defensive systems.

---

# Motivation

Most soccer analytics projects answer descriptive questions like:

- Who completed the most passes?
- Which player had the highest xG?
- Which team had the most possession?

While interesting, these analyses rarely explain **why** attacks succeed.

This project focuses on tactical decision-making by asking:

- What kinds of attacking styles naturally emerged during the tournament?
- Which defensive systems struggle against which attacking styles?
- Are some teams more tactically flexible than others?
- Can we predict the success of an attack based on its style?

---

# Dataset

**StatsBomb Open Data**
- 2022 FIFA World Cup
- Event-level data
- 64 matches

Every possession will become a single observation in the dataset.

---

# Step 1: Create Possession-Level Features

For every possession, engineer features describing how the attack develops.

## Speed
- Possession duration
- Seconds from first touch to final action
- Average time between actions

## Passing
- Number of passes
- Pass completion %
- Average pass length
- Progressive passes
- Through balls
- Long balls
- Switches of play

## Ball Carrying
- Number of carries
- Progressive carries
- Total carry distance
- Longest carry

## Progression
- Net forward distance
- Distance toward goal
- Final third entries
- Penalty area entries

## Width
- Average field width
- Standard deviation of y-coordinate
- Number of wide switches

## Pressure
- Pressure events faced
- Number of defenders bypassed

## Possession Structure
- Starting zone
- Ending zone
- Number of players involved
- Average player touches

## Outcome Variables
- Shot?
- Goal?
- xG generated
- xThreat generated
- Possession value

---

# Step 2: Discover Attacking Styles

Instead of manually assigning labels, use clustering to identify natural groups of possessions.

Possible algorithms:

- K-Means
- Gaussian Mixture Models
- Hierarchical Clustering

After clustering, interpret each cluster based on its average characteristics.

Possible discovered styles may include:

## Patient Build-up
Characteristics:
- Many short passes
- Long possessions
- Slow progression
- High possession %

---

## Vertical Progression
Characteristics:
- Forward passes
- Central progression
- Line-breaking passes
- Moderate speed

---

## Counterattack
Characteristics:
- Very fast
- Few passes
- Large forward gain
- High transition speed

---

## Wing Overload
Characteristics:
- Wide attacks
- Switches of play
- Crosses
- Penalty box entries from wide areas

---

## Direct Play
Characteristics:
- Long passes
- Few touches
- Skip midfield

---

## Combination Play
Characteristics:
- One-twos
- Third-man runs
- Dense passing around the box

---

## Carry-Oriented Attack
Characteristics:
- Long progressive dribbles
- Few passes
- High carry distance

---

## Hybrid Style
Characteristics:
- Mix of multiple approaches
- Adaptable based on game situation

---

# Step 3: Identify Defensive Styles

For each opposing defensive sequence, engineer defensive features.

## Defensive Features

- Average defensive line height
- PPDA (Passes Allowed Per Defensive Action)
- Number of pressure events
- Defensive compactness
- Number of defenders behind the ball
- Recovery speed after turnovers
- Pressure intensity
- Defensive width

Cluster these defensive possessions into natural defensive systems.

Potential defensive styles include:

## High Press
- High defensive line
- Aggressive pressing
- Many pressure events

---

## Mid Block
- Moderate pressure
- Compact midfield
- Balanced defensive shape

---

## Low Block
- Deep defensive line
- Protect penalty area
- Allow possession

---

## Counter Press
- Immediate pressure after losing possession
- Quick recoveries
- High pressing intensity

---

## Passive Defense
- Little pressure
- Wait for mistakes
- Conservative shape

---

## Compact Central Block
- Protect central areas
- Force attacks wide

---

## Wide-Oriented Defense
- Prevent crosses
- Force attacks inside

---

# Step 4: Analyze Matchups

After clustering both attacking and defensive possessions, evaluate how effective each attacking style is against each defensive style.

Example:

| Attacking Style | High Press | Mid Block | Low Block |
|-----------------|-----------:|----------:|----------:|
| Counterattack | 0.31 xG | 0.18 xG | 0.09 xG |
| Patient Build-up | 0.17 xG | 0.24 xG | 0.33 xG |
| Wing Overload | 0.20 xG | 0.28 xG | 0.36 xG |
| Direct Play | 0.29 xG | 0.19 xG | 0.13 xG |

This reveals tactical strengths and weaknesses rather than simple team statistics.

---

# Step 5: Predict Possession Success

Train machine learning models to predict whether a possession becomes dangerous.

Possible targets:

- Generates a shot
- Generates xG > 0.20
- Results in a goal
- High xThreat
- Enters penalty area

Possible models:

- Random Forest
- XGBoost
- Gradient Boosting
- Logistic Regression (baseline)

Evaluate using:

- Accuracy
- Precision
- Recall
- F1 Score
- ROC-AUC

Explain predictions using SHAP values or feature importance.

---

# Additional Analyses

## Team Tactical Profiles

Determine the percentage of possessions each team spends in every attacking style.

Example:

Spain
- 65% Patient Build-up
- 10% Counterattack
- 15% Combination Play
- 10% Wing Overload

France
- 20% Patient Build-up
- 45% Counterattack
- 20% Direct Play
- 15% Carry-Oriented

Argentina
- Balanced distribution across multiple styles

---

## Tactical Flexibility

Measure how diverse each team's attacking styles are.

Possible metrics:

- Shannon Entropy
- Simpson Diversity Index

Question:

**Are more tactically flexible teams more successful?**

---

## Predict Style Early

Train a classifier using only the first 5–10 seconds of a possession.

Research question:

**Can the eventual attacking style be predicted before the attack develops?**

Potential applications:

- Live tactical analysis
- Match broadcasts
- Opponent scouting

---

# Visualizations

## Cluster Radar Charts

Compare the average characteristics of each attacking style.

---

## Heatmaps

Show where each attacking style progresses on the field.

---

## Pass Networks

Visualize passing structures for different styles.

---

## Sankey Diagrams

Illustrate movement from:

Starting Zone → Attacking Style → Final Outcome

---

## Scatter Plots

Examples:

- Possession duration vs. directness
- Carry distance vs. xG
- Width vs. shot probability

Colored by attacking cluster.

---

## Effectiveness Heatmap

Visualize attacking style effectiveness against defensive styles.

---

## Team Tactical Profiles

Display each team's distribution of attacking styles using stacked bar charts.

---

# Expected Outcomes

This project aims to:

- Discover natural attacking styles using unsupervised learning.
- Identify common defensive systems during the 2022 World Cup.
- Quantify which attacking styles perform best against specific defensive approaches.
- Measure tactical flexibility across teams.
- Predict possession success using machine learning.
- Provide interpretable insights through feature importance and visualizations.

---

# Why This Project Is Different

Most World Cup analyses focus on descriptive statistics such as possession, passing accuracy, or expected goals.

This project instead asks:

> **Can machine learning discover how teams actually attack, and under which defensive conditions those attacking styles are most effective?**

By combining:
- Feature engineering
- Unsupervised learning
- Supervised machine learning
- Tactical soccer analysis
- Advanced visualization

the project produces insights that are both analytically rigorous and directly relevant to coaches, analysts, and performance staff.