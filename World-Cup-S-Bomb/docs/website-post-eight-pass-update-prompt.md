# Post–Eight-Pass Website Refresh Execution Prompt

Use this prompt only after
`docs/ranking-repair-eight-pass-prompt.md` has completed successfully and the
analytics repository contains regenerated ranking, profile, team, methodology,
model-summary, audit, and manifest artifacts.

This prompt updates the static publication website. It must preserve the
existing visual system and change information only.

---

## Role and objective

You are the lead frontend and research-publication engineer working across:

1. Analytics source of truth

`C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb`

2. Website publication repository

`C:\cosmos\final_proj_website\the-worlds-coach`

Note: the website folder is `the-worlds-coach`, not `world_coach`. If a path
variant is missing, search under `C:\cosmos\final_proj_website` and continue
only after confirming the SvelteKit package root containing
`scripts/build-site-data.mjs`.

Implement a complete website refresh that:

- keeps the current style, layout, tokens, typography, and component system;
- replaces stale ranking information with post–Pass-8 artifacts;
- adds two player ranking tabs;
- regenerates or republishes every player profile;
- refreshes methodology from the repaired model summary JSON and Markdown;
- refreshes patterns cluster definitions, visuals, and effectiveness labeling;
- refreshes team pages from repaired team artifacts;
- replaces the story player carousel with the new top 10;
- corrects Patient Build-up and other pattern values from source CSVs;
- mixes basic and advanced player-role definitions into the methodology Patterns
  stage without inventing a new visual language;
- updates Models, Validation, and Limits from the repaired validation metrics.

Do not redesign the site. Do not invent metrics. Do not flatten incompatible
score systems into one field.

---

## Preconditions

Confirm all of the following before editing the website:

1. Eight-pass repair completed and champion/challenger decisions recorded.
2. Analytics artifacts regenerated and hash-manifested.
3. These files exist and are internally consistent:

- `results/reports/ranking/player_rankings.csv`
- `results/reports/ranking/player_rankings.json`
- `results/reports/ranking/player_rankings_300plus.csv`
- `results/reports/ranking/global_rankings_outfield.csv`
- `results/reports/ranking/global_rankings_outfield_300min.csv`
- `results/reports/ranking/unified_tournament_rankings.csv`
- `results/reports/ranking/goalkeeper_rankings.csv`
- `results/reports/ranking/goalkeeper_rankings_unified.csv`
- `results/reports/ranking/by_team_unified/*.csv`
- `results/reports/ranking/ranking_methodology.md`
- `results/reports/ranking/ranking_audit.md`
- `results/reports/ranking/ranking_audit.json`
- `results/reports/player_profiles/*.md`
- `results/reports/team_profiles/*.md`
- `results/reports/model_summary.json`
- `results/reports/model_summary.md`
- `results/reports/canonical/model_summary.json`
- `results/reports/canonical/model_summary.md`
- `results/reports/final_summary.md`
- `results/MIscellaneous/attacking_style_profiles.csv`
- `results/MIscellaneous/defensive_style_profiles.csv`
- `results/MIscellaneous/style_matchup_effectiveness.csv`
- `results/MIscellaneous/attacking_style_summary.md`
- `results/MIscellaneous/defensive_style_summary.md`
- `results/MIscellaneous/team_defensive_style_profiles.csv`
- `data/processed/player_heatmap_cells.csv`

4. Website package scripts are available:

```sh
pnpm data:build
pnpm data:refresh
pnpm claims:validate
pnpm check
pnpm lint
pnpm test
pnpm test:static
pnpm build
```

If any precondition fails, stop and report the missing artifact. Do not patch
the website onto stale analytics.

---

## Non-negotiable product rules

### Style preservation

Keep:

- SvelteKit + Svelte 5 + Tailwind v4 + ShadCN tokens
- Inter Variable body and Climate Crisis display usage
- black/white editorial surfaces and restrained primary/chart colors
- existing components such as `HorizontalRail`, `PlayerFinder`,
  `PlayerPortrait`, `RoleSignature`, `PossessionStory`, `MatchupMatrix`,
  `ResearchFrame`, `EvidenceNote`, `TechnicalDisclosure`
- current responsive, reduced-motion, keyboard, and no-JS behaviors
- the present player-profile visual treatment, information hierarchy, portrait
  treatment, spacing, cards, rails, and disclosures for existing players;
- the present visual treatment of pressure-related defensive styles, pressure
  metrics, and their bars/chapters. Refresh their values and explanatory text
  from post–Pass-8 sources without visually redesigning those sections.

Forbidden:

- new palette or brand redesign
- replacing semantic tokens with ad-hoc hex colors
- inventing a charting library unless required for an existing pattern
- rewriting route architecture for fashion rather than data contracts

All new copy, fields, figures, tabs, badges, disclosures, and methodology
details must be inserted into the existing design grammar. Reuse current
containers, max widths, grids, breakpoints, spacing rhythm, type classes,
surfaces, borders, focus states, and component primitives. New content must
stay aligned with adjacent headings and content columns at every breakpoint.
Do not widen sections, create isolated visual styles, reorder unrelated
content, or cause clipping, overflow, layout shift, uneven card heights, or
broken reading order. Capture before/after screenshots at desktop and mobile
for every changed route family and treat any unintended format change as a
release blocker.

### Score and cohort separation

Publish three distinct populations:

1. **300+ minute cohort**
   - Current website-facing 142-player reliability publication.
   - Prefer `player_rankings_300plus.csv` / outfield 300+ plus eligible main GKs
     if the repaired 300+ export still includes them.
   - This is the continuity tab for the existing site audience.

2. **Unified / larger ranking cohort**
   - `unified_tournament_rankings.csv`
   - Eligible outfield players plus exactly 32 team-main goalkeepers.
   - Score field: `Tournament Performance Score`
   - Backup goalkeepers remain unranked in this list.

3. **All profiles**
   - Every markdown profile under `results/reports/player_profiles/`
   - Includes unranked backup goalkeepers and lower-minute players when present.
   - Every profile must have a prerendered route.

Never collapse these into one generic `rank`/`rating` without discrimination.

### Goalkeeper semantics

- Outfield model scores and GK-only scores are not interchangeable.
- Unified GK placement is an order-preserving publication bridge, not absolute
  cross-position value.
- Backup GKs may have profiles and team-page presence, but no unified rank.
- Profile pages must conditionally render outfield versus GK sections.

### Truthfulness

- All public numbers must come from regenerated artifacts or governed claims.
- Missing evidence stays missing; do not coerce to zero.
- Observational pattern cells remain observational; do not claim causality.
- Rejected challengers and limits remain visible.

---

## Pass A — Freeze website champion and research-root resolution

### Goal

Make the website importer able to read the repaired analytics tree without
changing public content yet.

### Work

1. Fix research-root resolution in:

- `scripts/build-site-data.mjs`
- `scripts/validate-claims.mjs`
- `scripts/site-data.sources.json`

Current relative root is wrong for
`C:\cosmos\final_proj_website\the-worlds-coach`. Support:

- `RESEARCH_ROOT` environment override
- fallback `../../26-the-pattern-seekers-analysis/World-Cup-S-Bomb`

2. Snapshot the current generated JSON and public claims as the website
   champion before mutation.

3. Record current hard-coded assumptions that must change:

- expected players = 142 only
- 300-minute exclusive publication
- old ranking path `results/reports/player_rankings.csv`
- old formula language in Models/Limits/About
- sitemap count magic number 191
- portrait sync limited to 142

### Exit gate

Importer can locate the analytics root and list required repaired files. No
public route content has changed yet.

---

## Pass B — Redesign data contracts and source manifests

### Goal

Replace the single-cohort importer contract with a two-tab ranking contract plus
full profile publication.

### Update

- `scripts/site-data.sources.json`
- `scripts/site-data.claims.json`
- `src/lib/data/types.ts`
- generated schema expectations in `scripts/build-site-data.mjs`

### Required source IDs

Keep existing pattern/team/model sources where still authoritative. Replace or
add ranking sources:

- `player-rankings-full` → `results/reports/ranking/player_rankings.csv`
- `player-rankings-300plus` → `results/reports/ranking/player_rankings_300plus.csv`
  or `global_rankings_outfield_300min.csv` plus documented GK handling
- `unified-tournament-rankings` → `results/reports/ranking/unified_tournament_rankings.csv`
- `goalkeeper-rankings` → `results/reports/ranking/goalkeeper_rankings.csv`
- `goalkeeper-rankings-unified` → `results/reports/ranking/goalkeeper_rankings_unified.csv`
- `ranking-methodology` → `results/reports/ranking/ranking_methodology.md`
- `ranking-audit` → `results/reports/ranking/ranking_audit.json`
- `player-profiles` → `results/reports/player_profiles`
- `team-profiles` → `results/reports/team_profiles`
- `model-summary-json` → `results/reports/model_summary.json`
  or canonical mirror if that becomes the authority
- `model-summary-md` → `results/reports/model_summary.md`
- `final-summary` → `results/reports/final_summary.md`
- attacking/defensive/matchup CSVs and summaries unchanged unless digests drift

Discover the post–Pass-8 pipeline/artifact manifest authority. Do not keep a
dead `results/reports/pipeline_manifest.json` path if the file no longer exists.
Use the actual repaired location and update all source links accordingly.

### Expected counts

Derive counts from artifacts; do not hard-code stale values. Validate:

- 3 attacking styles
- 4 defensive responses
- 12 matchup cells
- 32 teams
- 300+ cohort size from repaired 300+ export
- unified ranked size from unified CSV
- exactly 32 main goalkeepers
- profile count equals generated profile markdown files

### Discriminated player schema

Every player record must carry:

```ts
kind: 'outfield' | 'goalkeeper'
cohorts: {
  outfield300: boolean
  unified: boolean
  profileOnly: boolean
}
scores: {
  outfieldModel: number | null
  goalkeeperModel: number | null
  unifiedTournament: number | null
}
ranks: {
  outfieldGlobal: number | null
  outfieldPosition: number | null
  outfieldRole: number | null
  outfieldTeam: number | null
  goalkeeper: number | null
  unifiedGlobal: number | null
  unifiedTeam: number | null
}
status: string
```

Prefer generating:

- `players-profiles.json`
- `players-outfield-300.json`
- `players-unified.json`

or one `players.json` with explicit cohort arrays in `meta.json`. Either way,
route loaders must be able to select cohorts without reinterpreting score
fields.

### Exit gate

`pnpm data:build` either succeeds under the new contract or fails with precise
schema diagnostics. No silent coercion between score systems.

---

## Pass C — Rebuild importer and regenerate site data

### Goal

Make `scripts/build-site-data.mjs` consume repaired artifacts and write correct
generated JSON.

### Implementation requirements

1. Parse full ranking tables with repaired column names.
2. Join by numeric `player_id`, never by display name alone.
3. Parse profile markdown with discriminated outfield/GK parsers.
4. Parse repaired team profiles (`Top 5`, full outfield list, GK list) instead
   of the old exclusive `Squad ratings` 300+ assumption.
5. Preserve pattern imports from attacking/defensive/matchup sources.
6. Rebuild governed claims from actual metric index values.
7. Write generated files under `src/lib/data/generated/`.
8. Keep claim and source digest governance.

### Patient Build-up accuracy

Pull Patient Build-up and sibling cluster values directly from:

- `results/MIscellaneous/attacking_style_profiles.csv`
- `results/MIscellaneous/attacking_style_summary.md`

Do not round inconsistently across homepage, patterns pages, methodology, and
claims. Use one canonical formatting helper for shares, shot rates, and xG per
100 possessions.

Current source shares for verification:

- Patient Build-up ≈ 50.215%
- Short Under Pressure ≈ 34.560%
- Direct Long Play ≈ 15.225%

Re-read after Pass 8 rather than hard-coding if the analytics rebuild changes
them.

### Pattern effectiveness labeling

For attack, defense, and matchup visuals:

- color compares values within the relevant group;
- labels must state what the bar/cell measures;
- bars/cells must not look identical when values differ;
- volume and effectiveness must not be confused;
- matchup cells remain observational sample associations.

Update copy wherever current UI implies interchangeable bars or unspecified
meaning.

### Recompute every pattern and observed-matchup bar

This is a data-and-encoding update, not copy-only cleanup. Audit and update
every bar, segmented bar, heat strip, heat cell, and width calculation used by:

- homepage pattern/story sections;
- `/styles/`;
- `/styles/attacking/`;
- `/styles/defensive/`;
- `/styles/matchups/`;
- `PossessionStory.svelte`;
- `MatchupMatrix.svelte`;
- `StyleChapter.svelte`;
- any duplicated pattern visual on team or methodology pages.

For each visual mark:

1. Trace the displayed value to its post–Pass-8 source column.
2. Recompute its domain from the relevant peer group rather than reusing a
   hard-coded width or a domain for a different metric.
3. Set width/fill/heat level from the actual finite value.
4. Show the exact formatted value beside or in the visual.
5. Give the visual an accessible label containing the metric, value, unit, and
   comparison basis.
6. Handle null, non-finite, and equal-domain values explicitly.
7. Test that unequal inputs normally produce unequal visual lengths or heat
   levels; if five-bin heat quantization intentionally groups nearby values,
   retain exact values and explain the binning.

The **Observed matchup** selected-result bars in `MatchupMatrix.svelte`
currently render five equal-size blocks and only vary the number of filled
blocks. Replace or update that encoding so shot rate, penalty-area entry rate,
and mean xG visibly reflect their actual relative values. A continuous
proportional bar is preferred; a clearly labeled segmented scale is acceptable
only when its filled segments and exact values are correct. Do not let all
three metrics appear identical merely because they fall in the same coarse
bin.

The homepage **Observed matchup** step in `PossessionStory.svelte` must also be
updated from the repaired selected matchup cell. If it displays bars, their
widths must use metric-specific domains. If it remains numeric, verify all four
values and labels against the same generated cell used by the full matchup
page.

### Exit gate

Generated JSON populations match repaired CSVs. Claims validate against the
metric index. Pattern values match source CSVs to formatting tolerance. The
pattern and Observed matchup visuals have source-traceable values and no
incorrect identical-bar presentation.

---

## Pass D — Players: two tabs, all profiles, media

### Goal

Replace the single 142-only players experience with two ranking tabs and full
profile coverage.

### Files

- `src/routes/players/+page.server.ts`
- `src/routes/players/+page.svelte`
- `src/routes/players/[player]/+page.server.ts`
- `src/routes/players/[player]/+page.svelte`
- `src/lib/components/PlayerFinder.svelte`
- `src/lib/server/project.ts`
- `src/lib/data/index.ts`
- `src/lib/data/types.ts`
- `scripts/sync-player-media.mjs`
- `src/lib/data/player-media.json`
- `static/media/players/credits.json`
- `tests/data-integrity.test.mjs`
- `tests/static-output.test.mjs`

### Players index UX

Keep the existing visual language. Add accessible tabs:

1. **300+ minutes**
   - continuity cohort
   - explain reliability threshold
   - score = published 300+ model/reliability score used by that export

2. **Unified tournament ranking**
   - larger ranking list
   - score = `Tournament Performance Score`
   - identify goalkeepers clearly
   - explain GK bridge limitation briefly

Suggested query contract:

- `/players/?cohort=300plus`
- `/players/?cohort=unified`

Requirements:

- keyboard-accessible tabs
- useful no-JS directories for both cohorts
- finder works for both
- leading rail/cards use the active tab’s ordering
- copy no longer says the site only has one 142-player universe when the
  unified tab exists

### Profile pages

Prerender every profile.

Treat existing and newly published players consistently:

- Keep every existing player route and its current visual style.
- Refresh every existing player’s identity-independent metrics, ranks, scores,
  cohort membership, role information, team information, source links, and
  methodology text from post–Pass-8 artifacts.
- Add every newly eligible or newly generated player using the same profile
  template and design system—not a reduced “new player” template.
- Preserve valid existing portrait, heatmap, role-signature, and context
  information; add newly available information without deleting valid content.
- Populate new portraits/heatmaps/context only when authoritative artifacts
  exist; otherwise use the existing neutral unavailable/fallback treatment.
- Ensure new information appears for both existing and new players wherever
  the applicable source fields exist.
- Do not overwrite an existing player’s richer profile with nulls merely
  because one repaired ranking export is narrower; join the full profile,
  event/context, media, outfield/GK, and cohort sources by `player_id`.

Each profile must show, as applicable:

- identity, team, minutes, role labels
- tournament / unified rank and score when published
- 300+ membership badge when applicable
- outfield components for outfield players
- GK components for goalkeepers
- unranked backup-GK state when relevant
- role signature / heatmap / coverage only when data exists
- methodology links to repaired ranking methodology and model summary

Remove or rewrite stale hard-coded outfield weight copy if Pass 8 changed the
formula. Derive active formula language from
`ranking_methodology.md` and `model_summary.md`.

### Media

Expand portrait sync to the full profile population. Add a deliberate package
script such as `media:sync`. Do not download during ordinary `data:build`.
Missing portraits may use the existing neutral fallback treatment, but credits
and tests must account for the expanded set.

### Exit gate

- Both tabs render and sort correctly.
- Profile route count equals generated profile count.
- Every pre-existing profile still renders in the same visual system with
  refreshed information.
- Every new profile has the same applicable information and presentation
  quality as an existing profile.
- Existing valid profile detail is not lost during the broader-cohort import.
- No outfield formula is shown as if it were the GK model.
- No backup GK appears as ranked in the unified tab.

---

## Pass E — Story section

### Goal

Refresh the homepage story without redesigning it.

### Files

- `src/routes/+page.server.ts`
- `src/routes/+page.svelte`
- `src/lib/components/PossessionStory.svelte` only if needed for accurate values
- related format helpers

### Required changes

1. Replace the player carousel/rail with the new top 10 from the chosen
   publication ranking.
   - Default: unified top 10 after Pass 8.
   - Label the score source in nearby copy.
2. Keep `HorizontalRail` behavior and portrait card styling.
3. Make Patient Build-up and related story values exact to source artifacts:
   - share
   - selected matchup possessions
   - shot rate
   - box-entry rate
   - mean xG
4. Ensure the illustrative possession story still distinguishes:
   - recorded actions
   - possession row
   - attacking tendency
   - defensive response
   - observed matchup
5. Featured teams section must use repaired team metrics when displayed.

### Exit gate

Homepage top 10 matches the declared ranking CSV order. Patient Build-up story
metrics match source values after formatting.

---

## Pass F — Patterns section

### Goal

Define all clusters, show visuals, and make effectiveness labeling unambiguous.

### Files

- `src/routes/styles/+page.svelte`
- `src/routes/styles/attacking/+page.svelte`
- `src/routes/styles/defensive/+page.svelte`
- `src/routes/styles/matchups/+page.svelte`
- related server loaders
- `src/lib/components/MatchupMatrix.svelte`
- `src/lib/components/StyleChapter.svelte`
- homepage pattern blocks if they duplicate values

### Required content

For each attacking tendency:

- name
- share
- distinguishing features
- shot rate / xG / box-entry or equivalent source metrics
- plain-language summary

For each defensive response:

- name
- share
- shape distinctions
- shot/xG allowed metrics from source
- plain-language summary
- preserve the existing pressure-style presentation and chapter structure while
  refreshing pressure values, labels, and evidence from the final artifacts

For matchups:

- all 12 cells
- possessions / sample size
- effectiveness metrics with clear labels
- observational disclaimer
- color encodes the labeled measure, not an unlabeled decoration

### Visual requirements

- Rebuild all pattern bars and Observed matchup result bars from the refreshed
  generated values; do not preserve stale inline widths.
- Bars with different normalized values must render at different lengths.
- Heat cells with different bins must render differently; exact values must
  remain visible when nearby values share a bin.
- Relative color scales must be group-local and explained.
- Do not present volume as if it were quality.
- The selected Observed matchup card must use metric-specific scales for shot
  rate, penalty-area entry rate, and mean xG. Never compare raw percentages and
  xG on one undocumented common domain.
- Add focused component tests using deliberately low, middle, and high values
  to prove widths/levels are data-driven and accessible labels are correct.
- Keep current CSS/semantic visual approach; do not introduce a new chart stack
  unless an existing component already needs a minimal extension.

### Exit gate

All 3/4/12 entities appear. Effectiveness labels are explicit. Visual encoding
is distinguishable and explained. Pattern and Observed matchup bars are
verified against refreshed source rows.

---

## Pass G — Methodology Patterns stage: basic and advanced roles

### Goal

In the methodology Patterns area, mix in basic and advanced role definitions
plus a diagram, using the existing formatting language.

### Where

There is no separate `/method/patterns` route today. Patterns are linked from:

- `/method/` stage 02 → `/styles/`
- and related method pages

Implement by:

1. Extending `/method/` stage 02 content and/or
2. Adding a methodology-compatible section on `/styles/` and/or
3. Adding a nested method page only if necessary to avoid overcrowding

Prefer extending existing ResearchFrame/style-chapter formatting over creating
an orphan page.

### Content sources

Use repaired analytics text/data:

- `results/reports/model_summary.md`
- `results/reports/model_summary.json` (`role_labels`, role-weight sources,
  probabilistic versus functional role counts)
- `results/reports/ranking/ranking_methodology.md`
- role fields on player tables (`position_group`, `functional_role`,
  `probabilistic_role`)

### Required explanation

**Basic roles / position groups**

- GK, CB, FB, DM, CM, AM, FW
- what they mean in this tournament publication
- that position groups are reporting/normalization structure, not identity-based
  scoring

**Advanced / functional and probabilistic roles**

- functional roles such as Progressive Winger, Target Forward, Attacking
  Wingback, etc.
- probabilistic/advanced role labels from `role_labels`
- that advanced roles condition interpretation and weighting, and do not award
  points by player name

### Diagram

Create or regenerate a diagram that fits the current site style:

- semantic HTML/CSS diagram preferred
- optional static asset only if it matches existing black/white/red editorial
  language
- show basic position groups and how advanced roles sit within or across them
- caption the diagram with source and limits

Mix the diagram into the existing method/patterns formatting: stage chips,
ruled sections, evidence notes, technical disclosures. Do not drop a raw
notebook figure into the page unstyled.

### Exit gate

A reader can understand basic versus advanced roles from the methodology
Patterns materials without leaving the site’s visual system.

---

## Pass H — Teams refresh

### Goal

Update all team index and detail pages from repaired post–Pass-8 values.

### Files

- `scripts/build-site-data.mjs` team parsing
- `src/routes/teams/+page.server.ts`
- `src/routes/teams/+page.svelte`
- `src/routes/teams/[team]/+page.server.ts`
- `src/routes/teams/[team]/+page.svelte`

### Required team content

For each of the 32 teams:

- repaired threat / pressure / defensive metrics from team profiles
- dominant defensive response and response shares
- unified team player ordering from `by_team_unified`
- 300+ subset clearly labeled if shown
- main goalkeeper
- unranked backup goalkeepers with status
- links to every available player profile

Remove copy that says only 300-minute players exist if the team page now
exposes the broader repaired roster.

### Exit gate

All 32 team routes prerender. Team metrics and player lists match repaired
artifacts.

---

## Pass I — Models, Validation, and Limits

### Goal

Rewrite method pages from the repaired model summary and validation metrics.

### Files

- `src/routes/method/+page.svelte`
- `src/routes/method/data/+page.svelte`
- `src/routes/method/models/+page.svelte`
- `src/routes/method/models/+page.server.ts`
- `src/routes/method/validation/+page.svelte`
- `src/routes/method/validation/+page.server.ts`
- `src/routes/method/limitations/+page.svelte`
- `src/routes/about/+page.svelte`
- related loaders

### Models page must describe

From `model_summary.json` / `.md` and ranking methodology:

- active player-ranking version after Pass 8
- outfield score contract
- GK dedicated model and separate scale
- unified publication layer and its limits
- retrospective possession models still selected
- prospective package status
- rejected/retained challengers
- no identity-based scoring

Replace stale statements such as:

- only 300-minute players are in the publication universe
- old one-sided defensive lift is active if retired
- old shootout-save point formula if retired
- old within-position z-score is absolute global value if retired

### Current player-rating methodology

Replace the complete player-rating methodology—not only the headline or model
status—with the final post–Pass-8 method. Reconcile the methodology overview,
`/method/models/`, `/method/validation/`, `/method/limitations/`, Players
introductory copy, finder labels, profile explanations, About, team-page
explanations, evidence notes, technical disclosures, and source links.

Use these authorities together:

- `results/reports/ranking/ranking_methodology.md`
- `results/reports/ranking/ranking_audit.json`
- `results/reports/ranking/ranking_audit.md`
- `results/reports/model_summary.json`
- `results/reports/model_summary.md`
- the final ranking CSV schemas and refresh manifest

Explain accurately and in the existing editorial format:

- the final outfield inputs, component definitions, scaling, weights, and
  validation-selected layer;
- the separate goalkeeper model, inputs, eligibility, and score scale;
- the 300+ publication threshold and any distinct profile/GK thresholds;
- uncertainty, exposure/reliability treatment, and missing-data behavior;
- the unified Tournament Performance Score and GK bridge;
- rank scopes: global, position, role, team, GK-only, and unified;
- which challengers were accepted, rejected, or rolled back in Pass 8.

Do not retain the old V5 formula, old fixed weights, old 142-only eligibility
statement, or retired corrections as current methodology. Preserve historical
comparisons only when explicitly labeled.

### “Three questions” before “Three models”

On `src/routes/method/models/+page.svelte`, keep the current
`ResearchFrame`, spacing, typography, responsive behavior, section surfaces,
cards, disclosures, and route structure exactly intact, but change the hero
title hierarchy from **“Three models. Three questions.”** to:

1. **“Three questions.”** on the top line;
2. **“Three models.”** on the line below.

This is an order and content correction, not a redesign. Use the existing
heading classes and width constraints. Add only the minimal inline/block markup
needed to guarantee that order across breakpoints without overflow or layout
shift.

Keep the three model families and questions in this same order throughout the
page, methodology overview, accessibility labels, navigation summaries, and
technical disclosures:

1. Completed possessions — retrospective explanation after the full sequence.
2. Earlier prediction — prospective evaluation using only information
   available before the target outcome.
3. Player ratings — tournament player evaluation under the final repaired
   methodology.

### Completed possessions and earlier predictions

Refresh both model families from the final-stage artifacts; do not merely swap
their headings:

- selected completed-possession models and target definitions;
- information boundaries and leakage controls;
- features/layouts and calibration method;
- held-out, match-disjoint validation metrics;
- prospective candidates, targets, gates, uncertainty intervals, and final
  keep/reject/rollback decisions;
- exact ROC-AUC, PR-AUC, log loss, Brier score, calibration error, sample
  counts, and statuses where the final artifacts publish them.

Authoritative inputs include:

- `results/MIscellaneous/coaching_model_leaderboard.csv`
- `results/MIscellaneous/coaching_model_fold_metrics.csv`
- `results/MIscellaneous/coaching_model_uncertainty.csv`
- `results/MIscellaneous/coaching_model_selection.md`
- `results/MIscellaneous/coaching_model_benchmark.md`
- `results/MIscellaneous/coaching_model_explanations.md`
- `results/MIscellaneous/coaching_model_validation_v2.json`
- `results/diagnostics/prospective_model_validation.csv`
- final `model_summary.json` / `.md`

Update `src/routes/method/+page.svelte`,
`src/routes/method/models/+page.svelte`, their server loaders, and
`src/routes/lab/prospective-models/+page.svelte` together so completed
possessions and earlier predictions cannot disagree. Replace dead legacy source
paths such as `results/reports/prospective_model_validation.csv` with the
manifest-authoritative final path.

### Figures and source links

Use suitable, final-stage visualizations from the analytics figures directory:

`C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb\results\figures`

Candidate figures include:

- `coaching_model_explanations.png`
- `calibrated_brier_curve.png`
- `attacking_styles_overview.png`
- `attacking_style_pca.png`
- `defensive_style_fingerprints.png`
- `attacking_defensive_matchups.png`
- `vaep_vs_xt_scatter.png`
- final regenerated player/GK ranking figures

Rules:

1. Inventory `results/figures/` after Pass 8 and use only figures whose content
   and digest match the final selected models/data.
2. Do not publish stale `v5_*` figures unless Pass 8 regenerated and relabeled
   them as current. Prefer final unversioned or current-version outputs.
3. Select figures that directly support the surrounding section; do not add
   decorative or unrelated plots.
4. Copy approved web-optimized derivatives into the website’s existing static
   media structure while retaining the research filename in provenance.
5. Preserve aspect ratio, avoid cumulative layout shift, provide useful alt
   text and a caption, and use the existing image/card/figure formatting. Do
   not change section widths, palette, type scale, or responsive grid.
6. Put an adjacent `SourceLink` on every imported visualization linking to its
   exact research file, for example
   `results/figures/coaching_model_explanations.png`, using the repository’s
   existing `sourceUrl(...)` helper.
7. Add the figure paths and hashes to `site-data.sources.json`, the generated
   provenance/claims metadata, credits if required, and relevant tests.
8. If no final figure supports a section, keep the existing in-format semantic
   visualization rather than inserting a stale image.

For the Three Questions / Three Models page, prioritize the current coaching
model explanation and calibration figures for completed possessions and
earlier predictions. For the player-rating section, use only a ranking/model
figure regenerated by Pass 8 and link it to its exact file in
`results/figures/`.

### Validation page must describe

- Pass 8 gate outcomes
- champion/challenger decisions by component
- retained fallbacks
- non-inferiority / calibration / stability results available in audits
- cluster stability notes if still relevant
- recommendation abstention if still true

### Limits page must describe

- one-tournament scope
- observational matchups
- freeze frames are not continuous tracking
- overlapping cluster labels
- 300+ versus unified versus profile-only populations
- GK bridge is not absolute cross-position value
- uncertainty and small-sample limits
- what the site does not claim

### Exit gate

Method/About copy matches repaired summaries. No retired formula remains
presented as active.

---

## Pass J — Site-wide post–Pass-8 truth sweep, SEO, claims, and docs

### Goal

Make every public area—not only the routes named above—agree with the final
post–Pass-8 artifacts, then update discovery metadata and documentation.

### Work

1. Inventory every public route, shared component, server loader, generated
   data file, download, metadata endpoint, and public claim. Include:
   - homepage/story;
   - all Styles and Observed matchup pages;
   - Players indexes and every profile;
   - Teams index and every team;
   - Method, Data, Models, Validation, Limits;
   - Lab pages and scenarios;
   - About, credits, sitemap, robots, social metadata, and CSV downloads.
2. Build a reconciliation checklist mapping every displayed number, cohort
   count, rank, score, formula, threshold, model name, validation statement,
   source link, and dated snapshot identifier to an authoritative post–Pass-8
   artifact.
3. Correct every mismatch discovered. Do not limit work to the examples in
   this prompt. If a final-stage artifact changes information anywhere on the
   site, update that area, its loader/generated data, governed claim, tests,
   downloads, and metadata together.
4. Update sitemap generation to include all profile routes.
5. Derive expected route counts from generated meta rather than magic numbers.
6. Fix `PUBLIC_SITE_ORIGIN` handling so production canonical/robots/sitemap do
   not publish `localhost` values.
7. Refresh governed claims for:
   - player counts by cohort
   - Patient Build-up and other pattern shares
   - all 12 Observed matchup cells and their visual domains
   - model/validation metrics that changed
8. Regenerate downloadable CSVs and verify they match the data displayed in
   the corresponding pages.
9. Update README/`PRODUCT.md` for the two-tab ranking publication.
10. Search the entire website repo—not only route files—for stale strings and
    old numeric literals:

- `142` used as the only universe
- old ranking path `results/reports/player_rankings.csv`
- `role_aware_fallback` presented incorrectly if superseded
- retired shootout/exposure/z-score formula language
- old top-10 names/scores
- dead pipeline manifest path
- pre–Pass-8 snapshot IDs and hashes
- old player/team ranks, ratings, counts, and thresholds
- stale Patient Build-up, defensive-response, and matchup values
- hard-coded bar widths, heat levels, or domains
- obsolete source URLs, filenames, and validation metrics

Classify each remaining match as active, historical/labeled, test fixture, or
stale. Historical values may remain only when clearly labeled as historical
and necessary for explaining the repair.

### Exit gate

No stale active claims or visual encodings remain. Every route family has a
completed reconciliation record. Sitemap and robots use the configured origin.

---

## Mandatory commands

From `C:\cosmos\final_proj_website\the-worlds-coach`:

```powershell
$env:RESEARCH_ROOT = "C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb"
pnpm install
pnpm data:build
pnpm claims:validate
pnpm check
pnpm lint
pnpm test
```

After reviewed source digest updates:

```powershell
pnpm data:refresh
pnpm claims:validate
```

If profile population expanded and portraits need sync:

```powershell
pnpm media:sync
```

or the equivalent script added by this work. Review licenses before committing
new media.

Final static verification:

```powershell
$env:PUBLIC_SITE_ORIGIN = "https://worldscoach.netlify.app"
pnpm test:static
pnpm build
pnpm budget
```

If the production origin differs, use the owner-confirmed origin instead.

---

## Acceptance tests

### Data

- 300+ tab population matches repaired 300+ export rules.
- Unified tab population matches `unified_tournament_rankings.csv`.
- Unified ranks are unique, finite, and ordered by
  `Tournament Performance Score`.
- Exactly 32 main GKs are ranked in dedicated and unified GK publications.
- Backup GKs are unranked in unified ranking.
- Every profile markdown has a prerendered route.
- Existing and new players receive all applicable repaired profile information;
  no valid existing detail is dropped by the new cohort joins.
- Team pages match `by_team_unified` and repaired team profiles.
- Pattern shares and effectiveness metrics match source CSVs.
- Every Observed matchup value and visual domain matches the refreshed
  12-cell source.
- Model/validation/limits copy matches model summary and audits.
- Every rendered number, formula, threshold, model label, rank, and source link
  has been reconciled against a post–Pass-8 artifact or explicitly marked
  historical.
- The player-rating, completed-possession, and earlier-prediction methodology
  sections all match their final-stage artifacts.
- Every displayed research figure is current, hash-governed, and linked to its
  exact file under `results/figures/`.
- Source digests are pinned after review.

### UI

- Style/tokens/components remain recognizably the same.
- Two player tabs work with mouse, keyboard, and no-JS fallback.
- Existing and new player profiles share the same established visual style and
  information quality.
- The Models hero shows “Three questions.” above “Three models.” without
  changing its established layout or responsive behavior.
- Completed-possession and earlier-prediction sections contain final metrics,
  decisions, and source links.
- Imported figures remain inside the existing layout and each includes an
  exact `results/figures/<filename>` source link.
- Story carousel shows the new top 10 in order.
- Patient Build-up values are accurate and consistent across story and patterns.
- Pattern bars/cells with different values are visually distinct and labeled.
- Observed matchup result bars use refreshed values and metric-specific,
  documented domains; different values do not appear as identical bars.
- Methodology Patterns materials include basic and advanced roles plus diagram.
- Team pages show repaired values and broader roster states where applicable.
- GK and outfield profiles show the correct score semantics.

### Release

- `pnpm check`, `pnpm lint`, `pnpm test`, and `pnpm test:static` pass.
- Budgets still pass unless an owner-approved budget change is documented.
- Sitemap count equals static routes + 32 teams + all profile routes.
- No localhost canonical/robots/sitemap in the production build.
- Final response lists changed files, regenerated data products, test results,
  unresolved portrait/media gaps, and remaining publication limits.

---

## Final response format

Return:

1. **Outcome**
   - website data version / snapshot id
   - ranking cohorts published
2. **Pass results**
   - one concise subsection per Pass A–J
3. **Cohort counts**
   - 300+, unified, profiles, main GKs, backup GKs
4. **Content updates**
   - story top 10 source
   - pattern value verification
   - methodology role diagram location
   - models/validation/limits source artifacts
5. **Artifacts**
   - changed website files
   - regenerated `src/lib/data/generated/*`
   - media/credits updates
6. **Tests and commands**
   - exact commands and results
7. **Remaining limitations**
   - any unresolved media rights, origin confirmation, or retained fallbacks

Do not claim success because selected pages look better. Success requires
artifact agreement, cohort integrity, style preservation, and passing quality
gates.
