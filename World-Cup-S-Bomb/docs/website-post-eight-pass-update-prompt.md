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
2. The pulled eight-pass history contains:
   - implementation commit
     `87eef9fc47f4741df8d01edf074068ef8287fadb`;
   - generated release-artifact commit
     `8a1250b7b17cb7b3f91b4b4b474f42a2284504be`.
3. Do **not** treat the artifact commit above as website-ready by itself. The
   verification recorded below found release-family failures. Obtain a
   corrective commit descended from `8a1250b7...`, rerun all release tests, and
   use that passing commit’s exact 40-character SHA as `PASS8_COMMIT`. Do not
   use a moving branch name, `HEAD`, a date, or “latest” as publication
   provenance.
4. Check out or otherwise verify the analytics repository at exactly
   `PASS8_COMMIT`. The governed source, generator, ranking, report, profile,
   figure, and manifest paths must have no uncommitted differences from that
   commit.
5. Analytics artifacts have been regenerated and hash-manifested by that
   committed state.
6. These files exist and are internally consistent:

- `results/reports/ranking/player_rankings_v3.csv`
- `results/reports/ranking/player_rankings_v3.json`
- byte-identical active aliases:
  `player_rankings.csv`, `player_rankings.json`, `player_rankings_v2.csv`,
  `v5_player_rankings.csv`, and `v5_player_rankings.json`
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
- `results/reports/ranking/refresh_manifest.json`
- `results/diagnostics/ranking_repair/v3_release_audit.json`
- `results/diagnostics/ranking_repair/pass_checklist.json`
- `results/diagnostics/unified_team_validation.json`
- `results/diagnostics/v3_validation_summary.json`
- `results/reports/player_profiles/*.md`
- `results/reports/team_profiles/*.md`
- `results/reports/canonical/model_summary.json`
- `results/reports/canonical/model_summary.md`
- byte-identical model-summary aliases:
  `results/reports/model_summary.json`,
  `results/reports/model_summary.md`, and
  `results/Summary/model_summary.md`
- `results/reports/canonical/final_summary.md`
- byte-identical final-summary aliases:
  `results/reports/final_summary.md` and
  `results/reports/final/world_cup_team_performance_and_top_players.md`
- `results/reports/canonical/coaches_notebook.md`
- byte-identical compatibility copy:
  `results/reports/coaches_notebook.md`
- `results/reports/docs/final_summary.docx`
- `results/reports/v3_figures/*.png`
- `results/metadata/artifact_manifest.json`
- `results/reports/artifact_manifest.json`
- `results/MIscellaneous/attacking_style_profiles.csv`
- `results/MIscellaneous/defensive_style_profiles.csv`
- `results/MIscellaneous/style_matchup_effectiveness.csv`
- `results/MIscellaneous/attacking_style_summary.md`
- `results/MIscellaneous/defensive_style_summary.md`
- `results/MIscellaneous/team_defensive_style_profiles.csv`
- `data/processed/player_heatmap_cells.csv`

7. Website package scripts are available:

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

### Verified pulled-release state and blockers

The following observations are grounded in the actual Git range
`0e1f2b3b9f89e59ebc482c0bbe0ef0c3776917b7..8a1250b7b17cb7b3f91b4b4b474f42a2284504be`:

- all eight checklist passes report `PASS`;
- active model version is `ranking-repair-v3.0-qatar-2022`;
- 593 rich player rows and 593 player profiles were regenerated;
- 553 outfield rows, 126 300+ outfield rows, 142 all-position 300+ rows,
  32 ranked main goalkeepers, 585 unified rows, and 8 profile-only backup
  goalkeepers are present;
- all 32 `by_team` files, all 32 `by_team_unified` files, and all 32
  `team_profiles` were regenerated;
- canonical/root/Summary model-summary Markdown files are byte-identical;
- canonical/root/final-path final summaries are byte-identical;
- canonical/root coaches notebooks are byte-identical;
- the final DOCX validation reports `PASS`;
- v3 ranking, goalkeeper, defensive, event-scope, documentation, and DOCX
  generators/tests were added.

The pulled artifact commit is nevertheless **not website-ready**. Verification
produced 47 passing tests and these 3 failing release tests:

1. `test_champion_copies_match_frozen_hashes` — all five frozen copies
   (`player_rankings`, `unified_rankings`, `goalkeeper_rankings`,
   `model_summary`, and `ranking_audit`) disagree with their recorded hashes in
   `champion_snapshot.json`.
2. `test_release_manifests_use_portable_current_paths` — the master artifact
   manifest does not match the current result tree, including path-case
   inconsistencies around `MIscellaneous`.
3. `test_profile_starter_team_and_figure_families_are_complete` — starter JSON
   lacks `active_model_version`; inspection also shows all 593 starter reports
   and all 32 team coaching reports were left unchanged and still contain
   legacy V5/rating language. The required seven files under
   `results/reports/v3_figures/` are absent.

Treat those as release blockers. Repair the analytics generators and regenerate
the affected champion snapshot, manifests, starter reports/JSON, team coaching
reports/JSON, and v3 figures before setting `PASS8_COMMIT`. The website must
never import the stale starter/team-coaching ranking sections or old V5 figures.

The pulled history proves that implementation and artifact commits exist, but
the current artifact commit fails release validation. `PASS8_COMMIT` therefore
means the later owner-reviewed corrective commit—not `87eef9f...` and not the
failing `8a1250b...` release candidate.

### Commit-pinned Pass-8 consistency gate

Before website work, validate the complete publication bundle at
`PASS8_COMMIT`:

1. Record:
   - `git rev-parse PASS8_COMMIT`
   - analytics repository remote URL
   - ranking refresh-manifest hash
   - artifact-manifest hash
2. Verify `results/reports/ranking/refresh_manifest.json` reports a passed
   audit and its hashes match the files from `PASS8_COMMIT`.
3. Verify `results/metadata/artifact_manifest.json` covers all regenerated
   report/profile/figure/document outputs and matches the committed bytes.
4. Verify these active ranking families agree:
   - feature-rich full and 300+ rankings;
   - outfield full and 300+ rankings;
   - dedicated and unified GK rankings;
   - global unified ranking;
   - all 32 `by_team` and `by_team_unified` partitions.
5. Verify all ranking-dependent publications were generated from those same
   committed rankings:
   - every player profile;
   - every starter Markdown/JSON report;
   - every team coaching Markdown/JSON report and every team profile;
   - canonical and compatibility final summaries;
   - canonical coaches notebook and every compatibility copy;
   - model-summary JSON and Markdown variants;
   - all seven required v3 ranking/model figures;
   - final DOCX;
   - documentation dictionaries and manifests.
6. Compare the following mirrored outputs byte-for-byte where their contracts
   say they are aliases:
   - canonical/root/Summary model-summary variants;
   - canonical/root/final-path final-summary variants;
   - canonical and compatibility coaches-notebook variants.
7. Semantically validate non-identical formats:
   - profile ranks/scores equal ranking rows;
   - team player order equals `by_team_unified`;
   - final-summary leaders equal active ranking leaders;
   - coaches-notebook tables and claims equal active rankings/team profiles;
   - model-summary formulas, selected layers, metrics, confidence intervals,
     and gate decisions equal the ranking audit;
   - DOCX text/tables equal the Markdown final-summary contract.
8. Compute the dependency closure of every source/data/model change made
   between the pre-repair champion and `PASS8_COMMIT`. Regenerate every derived
   metric family reached by those dependencies. This includes possession,
   attacking/defensive pattern, matchup, coaching-model, player, goalkeeper,
   team, validation, and summary metrics when their inputs changed. Metrics
   outside that dependency closure may retain identical values, but their
   unchanged hashes and provenance must be verified rather than assumed.

If any comparison fails, do not work around it in the website importer. Return
to the analytics repository, fix the responsible generator, regenerate the
entire dependent artifact family, rerun Pass-8 validation, obtain a newly
reviewed commit SHA, and restart this gate. Never manually make summaries agree
with rankings.

Store `PASS8_COMMIT`, the two manifest hashes, and the analytics remote in the
website source manifest and generated snapshot metadata. All website source
links should point to files at that immutable commit (for example GitHub
`.../blob/<PASS8_COMMIT>/...` URLs), not a moving `main` branch.

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
   - Exactly 142 rows in the verified v3 release:
     126 outfield players plus 16 main goalkeepers with 300+ minutes.
   - Source: `player_rankings_300plus.csv`.
   - This is the continuity tab for the existing site audience.

2. **Unified / larger ranking cohort**
   - `unified_tournament_rankings.csv`
   - Exactly 585 rows in the verified v3 release:
     all 553 outfield players plus exactly 32 team-main goalkeepers.
   - Score field: `Tournament Performance Score`
   - Backup goalkeepers remain unranked in this list.

3. **All profiles**
   - Exactly 593 Markdown profiles under `results/reports/player_profiles/`.
   - Includes all 553 outfield players, 32 ranked main goalkeepers, and 8
     unranked backup goalkeepers.
   - Every profile must have a prerendered route.

Never collapse these into one generic `rank`/`rating` without discrimination.

### Ranking source-of-truth matrix

Do not choose a ranking file because its name appears newer or because it has
more columns. After Pass 8, validate `results/reports/ranking/refresh_manifest.json`,
require `audit_passed: true`, verify every selected file’s SHA-256 digest, and
route each website surface to exactly one ranking authority:

| Website use | Authoritative ranking artifact | Fields/order to publish |
| --- | --- | --- |
| Unified player tab | `ranking/unified_tournament_rankings.csv` | Exact row order; `Global Rank`, `Team Rank`, `Tournament Performance Score` |
| Homepage/story top 10 | `ranking/unified_tournament_rankings.csv` | First 10 rows after validating contiguous global rank |
| Unified ordering on each team page | `ranking/by_team_unified/<TEAM>.csv` | Exact team rows ordered by `Team Rank`; retain unified global rank and score |
| 300+ continuity tab | `ranking/player_rankings_300plus.csv` | The post–Pass-8 300+ export contract, including only rows whose ranking status and minutes satisfy that export |
| Outfield-only global reference | `ranking/global_rankings_outfield.csv` | Outfield model/ranks only; never substitute for unified ordering |
| Outfield-only 300+ reference | `ranking/global_rankings_outfield_300min.csv` | 300+ outfield analysis only; do not silently use it for the all-position continuity tab |
| Dedicated goalkeeper rank | `ranking/goalkeeper_rankings.csv` | `dedicated_goalkeeper_score_v3`, `continuous_goalkeeper_rating_v3`, `shootout_component_v3`, `goalkeeper_rank_v3`, score/rank intervals, uncertainty and main-GK status |
| GK-to-unified publication mapping | `ranking/goalkeeper_rankings_unified.csv` | `percentile_equivalent_placement`, `percentile_equivalent_score_v3`, publication global/team rank; never substitute the dedicated GK score |
| Rich profile metrics and repaired component fields | `ranking/player_rankings_v3.csv` / `.json` and profile Markdown | `tournament_impact_v3`, `role_quality_v3`, v3 rank fields, v3 uncertainty fields, active attack/defense components; v2/v5 columns are provenance only |
| Team tactical/narrative values | `results/reports/team_profiles/<team>.md` | Active v3 team leaders, component totals, and main-GK table; unified player order still comes from `by_team_unified` |

The non-unified `ranking/by_team/*.csv` files must never power the website’s
unified team ordering. Likewise, `global_rankings_outfield*.csv` must never be
used to fill goalkeeper or unified score fields.

Treat `by_team_unified` as a materialized partition of
`unified_tournament_rankings.csv`, not an independent ranking. Validate before
import:

- exactly 32 team files exist;
- concatenating all team files produces the same row multiset as the unified
  global table;
- every team file has only its named team;
- `Team Rank` is unique and contiguous within each team;
- `Global Rank`, `Team Rank`, `Player`, `Team`, `Position Group`, and
  `Tournament Performance Score` match the global unified row exactly;
- sorting each team file by `Team Rank` gives the displayed team order;
- all file hashes match the post–Pass-8 refresh manifest.

The six-column unified release intentionally lacks `player_id`. Resolve it
through an exact, validated crosswalk to `player_rankings.csv` using the
canonical player name plus team, then carry the numeric `player_id` internally.
Require one and only one match for every unified row; fail the build on a
missing or duplicate match. Never use fuzzy name matching or name-only joins.

If the post–Pass-8 manifest or audit changes any file contract, stop and update
this matrix explicitly before importing. Do not guess between ranking variants.

### v3 report and notebook authority

Use these exact publication authorities after the corrective commit passes:

- ultimate model summary:
  `results/reports/canonical/model_summary.json` and
  `results/reports/canonical/model_summary.md`;
- final summary:
  `results/reports/canonical/final_summary.md`;
- coaches notebook:
  `results/reports/canonical/coaches_notebook.md`;
- team summaries:
  all 32 files under `results/reports/team_profiles/`;
- player summaries:
  all 593 files under `results/reports/player_profiles/`;
- final document:
  `results/reports/docs/final_summary.docx`;
- release decisions and metrics:
  `results/diagnostics/ranking_repair/v3_release_audit.json`;
- pass status:
  `results/diagnostics/ranking_repair/pass_checklist.json`;
- ranking-file hashes:
  `results/reports/ranking/refresh_manifest.json`;
- complete result-tree hashes:
  `results/metadata/artifact_manifest.json`.

Verify the documented compatibility copies are byte-identical, but import the
canonical/explicit-v3 paths above. Do not use `results/reports/teams/` or
`results/reports/starters/` for ranking copy until their corrective regeneration
removes V5 language and adds v3 provenance. They may be used later for
non-ranking tactical material only after a field-by-field stale-content audit.

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
- old ranking path `results/reports/player_rankings.csv` instead of explicit
  active path `results/reports/ranking/player_rankings_v3.csv`
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

- `player-rankings-full-v3` → `results/reports/ranking/player_rankings_v3.csv`
- `player-rankings-full-v3-json` → `results/reports/ranking/player_rankings_v3.json`
- `player-rankings-300plus` → `results/reports/ranking/player_rankings_300plus.csv`
- `outfield-rankings-full-v3` → `results/reports/ranking/global_rankings_outfield.csv`
- `outfield-rankings-300plus-v3` → `results/reports/ranking/global_rankings_outfield_300min.csv`
- `unified-tournament-rankings` → `results/reports/ranking/unified_tournament_rankings.csv`
- `goalkeeper-rankings` → `results/reports/ranking/goalkeeper_rankings.csv`
- `goalkeeper-rankings-unified` → `results/reports/ranking/goalkeeper_rankings_unified.csv`
- `ranking-methodology` → `results/reports/ranking/ranking_methodology.md`
- `ranking-audit` → `results/reports/ranking/ranking_audit.json`
- `v3-release-audit` → `results/diagnostics/ranking_repair/v3_release_audit.json`
- `pass-checklist` → `results/diagnostics/ranking_repair/pass_checklist.json`
- `player-profiles` → `results/reports/player_profiles`
- `team-profiles` → `results/reports/team_profiles`
- `model-summary-json` → `results/reports/canonical/model_summary.json`
- `model-summary-md` → `results/reports/canonical/model_summary.md`
- `final-summary` → `results/reports/canonical/final_summary.md`
- `coaches-notebook` → `results/reports/canonical/coaches_notebook.md`
- `final-summary-docx` → `results/reports/docs/final_summary.docx`
- `ranking-refresh-manifest` → `results/reports/ranking/refresh_manifest.json`
- `artifact-manifest` → `results/metadata/artifact_manifest.json`
- `v3-figures` → `results/reports/v3_figures/*.png`
- attacking/defensive/matchup CSVs and summaries unchanged unless digests drift

`results/reports/pipeline_manifest.json` now exists as a compatibility pointer,
but the complete artifact authority is
`results/metadata/artifact_manifest.json`; the ranking-family authority is
`results/reports/ranking/refresh_manifest.json`. Do not confuse these scopes.

### Expected counts

Derive counts from artifacts; do not hard-code stale values. Validate:

- 3 attacking styles
- 4 defensive responses
- 12 matchup cells
- 32 teams and 32 team profiles
- 593 rich player rows and 593 player profiles
- 553 outfield rows
- 126 300+ outfield rows
- 142 all-position 300+ rows, including 16 main GKs
- 585 unified rows
- exactly 32 main goalkeepers
- exactly 8 profile-only backup goalkeepers

### Discriminated player schema

Every player record must carry:

```ts
kind: 'outfield' | 'goalkeeper'
cohorts: {
  minutes300: boolean
  outfield300: boolean
  unified: boolean
  profileOnly: boolean
}
scores: {
  tournamentImpact: number | null
  roleQuality: number | null
  dedicatedGoalkeeper: number | null
  continuousGoalkeeper: number | null
  shootoutGoalkeeper: number | null
  unifiedTournamentPerformance: number | null
}
ranks: {
  impactGlobal: number | null
  roleQualityPosition: number | null
  roleQualityRole: number | null
  impactTeam: number | null
  goalkeeper: number | null
  unifiedGlobal: number | null
  unifiedTeam: number | null
}
uncertainty: {
  low: number | null
  high: number | null
  rankBest: number | null
  rankWorst: number | null
  status: string | null
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
2. Join tables carrying IDs by numeric `player_id`. For the six-column unified
   releases, create the strict canonical-name-plus-team crosswalk described in
   the ranking source-of-truth matrix and convert it to `player_id` before all
   downstream joins.
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
   - continuity cohort of exactly 142 players
   - explain that it contains 126 outfield players and 16 main GKs
   - preserve the export’s publication ordering
   - use `Global Rank`, `Team Rank`, and `Tournament Performance Score` for the
     common publication list
   - additionally label outfield `Tournament Impact` and GK
     `Dedicated Goalkeeper Score` as separate, non-interchangeable products

2. **Unified tournament ranking**
   - larger 585-player ranking list
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
- outfield `Tournament Impact` (`tournament_impact_v3`) and global/team rank;
- outfield `Role Quality` (`role_quality_v3`) and position/role rank;
- uncertainty interval, bootstrap rank band, and uncertainty status;
- unified publication rank and `Tournament Performance Score` when published;
- 300+ membership badge when applicable
- active attack, signed-defense, and other components for outfield players
- continuous GK rating, dedicated GK score/rank, shootout component, score/rank
  intervals, and GK uncertainty for main goalkeepers
- unranked backup-GK state when relevant
- role signature / heatmap / coverage only when data exists
- methodology links to repaired ranking methodology and model summary

Remove the stale single weighted-rating formula. The v3 publication has three
separate products: Tournament Impact, Role Quality, and Uncertainty. Derive
active language from `ranking_methodology.md` and the canonical model summary.
State that attack selected `process_only`, defense promoted `signed_ridge`,
goalkeepers promoted `goalkeeper_v3`, ordinary evidence uses periods 1–4, and
the GK cross-position bridge is `percentile_equivalent_placement`.

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

- `results/reports/canonical/model_summary.md`
- `results/reports/canonical/model_summary.json` (`role_labels`, role-weight sources,
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

- v3 team player ordering, Tournament Impact, Role Quality, Uncertainty,
  outfield component totals, and main-GK values from `team_profiles`
- threat / pressure / defensive tactical metrics from their existing governed
  tactical sources, not from `team_profiles` (the regenerated v3 team profiles
  do not contain those tactical sections)
- dominant defensive response and response shares
- unified team player ordering from `by_team_unified`
- 300+ subset clearly labeled if shown
- main goalkeeper
- unranked backup goalkeepers with status
- links to every available player profile

Remove copy that says only 300-minute players exist if the team page now
exposes the broader repaired roster.

The displayed unified player order must come only from
`results/reports/ranking/by_team_unified/<TEAM>.csv`. Do not infer it by sorting
`final_player_rating_v2`, `gk_rating_v2`, a legacy `team_rank`, or the
non-unified `by_team/<TEAM>.csv`. Cross-check every displayed row against the
corresponding global row in `unified_tournament_rankings.csv`.

The 32 files in `results/reports/teams/` were not regenerated by the pulled
artifact commit and still contain headings such as “V5 role-aware player
leaders,” old rating values, and `ROLE_AWARE_FALLBACK`. Do not import those
ranking sections. Before using team-coaching reports at all, the corrective
analytics release must regenerate their Markdown/JSON with v3 provenance and
replace their ranking sections from active v3 tables. Non-ranking tactical
sections may remain unchanged only when their upstream hashes did not change.

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

From canonical `model_summary.json` / `.md`, the v3 release audit, and ranking
methodology:

- active version `ranking-repair-v3.0-qatar-2022`
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
- `results/reports/canonical/model_summary.json`
- `results/reports/canonical/model_summary.md`
- `results/diagnostics/ranking_repair/v3_release_audit.json`
- `results/diagnostics/ranking_repair/pass_checklist.json`
- the final ranking CSV schemas and refresh manifest

Explain accurately and in the existing editorial format:

- Tournament Impact as signed total common-unit contribution for outfield
  global/team ordering, with no position normalization;
- Role Quality as a once-shrunk empirical-Bayes posterior rate for
  position/role comparison only;
- Uncertainty as a match-bootstrap interval and rank band, never a score
  penalty;
- attack selection `process_only` (`retain_champion`);
- defense selection `signed_ridge` (`promote_challenger`);
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

Use two explicitly separated figure authorities:

1. Active v3 ranking/model figures:
   `results/reports/v3_figures/`
2. Existing tactical/model figures:
   `results/figures/`, only when their upstream inputs were not changed by the
   ranking repair and their manifest hashes remain valid.

The corrective v3 release must generate exactly:

- `v3_global_outfield_rankings.png`
- `v3_global_outfield_300min.png`
- `v3_goalkeeper_rankings.png`
- `v3_representative_team_rankings.png`
- `v3_defensive_feature_importance.png`
- `v3_champion_challenger_movement.png`
- `v3_position_composition_and_stability.png`

Existing non-ranking candidates include:

- `coaching_model_explanations.png`
- `calibrated_brier_curve.png`
- `attacking_styles_overview.png`
- `attacking_style_pca.png`
- `defensive_style_fingerprints.png`
- `attacking_defensive_matchups.png`
- `vaep_vs_xt_scatter.png`
- no v5 ranking figure

Rules:

1. Require all seven `results/reports/v3_figures/` files before website work.
2. Do not publish `v5_*` ranking figures. The pulled artifact commit modified
   old v5 filenames but did not produce the required v3 figure family.
3. Select figures that directly support the surrounding section; do not add
   decorative or unrelated plots.
4. Copy approved web-optimized derivatives into the website’s existing static
   media structure while retaining the research filename in provenance.
5. Preserve aspect ratio, avoid cumulative layout shift, provide useful alt
   text and a caption, and use the existing image/card/figure formatting. Do
   not change section widths, palette, type scale, or responsive grid.
6. Put an adjacent `SourceLink` on every imported visualization linking to its
   exact research file, for example
   `results/figures/coaching_model_explanations.png` or
   `results/reports/v3_figures/v3_goalkeeper_rankings.png`, using the
   repository’s existing `sourceUrl(...)` helper.
7. Add the figure paths and hashes to `site-data.sources.json`, the generated
   provenance/claims metadata, credits if required, and relevant tests.
8. If no final figure supports a section, keep the existing in-format semantic
   visualization rather than inserting a stale image.

For the Three Questions / Three Models page, prioritize the current coaching
model explanation and calibration figures for completed possessions and
earlier predictions. For the player-rating section, use only a passing v3
figure from `results/reports/v3_figures/` and link it to that exact file.

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

Before entering the website repository, use the Python 3.12 analytics
environment and run from
`C:\cosmos\26-the-pattern-seekers-analysis\World-Cup-S-Bomb`:

```powershell
python -m pytest `
  tests/test_ranking_repair_champion.py `
  tests/test_event_scope.py `
  tests/test_defensive_challenger.py `
  tests/test_tournament_rankings_v3.py `
  tests/test_goalkeeper_valuation_v3.py `
  tests/test_goalkeeper_publication_bridge_v3.py `
  tests/test_ranking_repair_release_v3.py `
  tests/test_final_summary_docx_v3.py `
  tests/test_ranking_documentation_v3.py `
  tests/test_stale_content_scan.py
```

All tests must pass. Specifically confirm the three failures documented in the
verified pulled-release section are gone and that the figure-family assertions
run to completion. Then record the corrective `PASS8_COMMIT`.

From `C:\cosmos\final_proj_website\the-worlds-coach`:

```powershell
$env:PASS8_COMMIT = "<owner-reviewed 40-character analytics commit SHA>"
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

- Website snapshot metadata records the exact `PASS8_COMMIT`, analytics remote,
  refresh-manifest hash, and artifact-manifest hash.
- Every governed analytics input matches its byte content at `PASS8_COMMIT`;
  moving-branch source URLs are not used.
- Rankings, player/team profiles, final summaries, coaches notebook, model
  summaries, figures, DOCX, dictionaries, and manifests pass the commit-pinned
  consistency gate before import.
- The complete analytics test command above passes with no failure or skipped
  release-family assertion.
- Frozen champion hashes match `champion_snapshot.json`.
- Master and ranking manifests exactly cover their governed current files with
  portable, case-correct paths and valid SHA-256 values.
- All 593 starter Markdown/JSON pairs and all 32 team coaching Markdown/JSON
  pairs carry v3 provenance and contain no active V5 ranking copy.
- All seven required files under `results/reports/v3_figures/` exist and pass
  size/hash checks.
- 300+ tab contains exactly 142 rows: 126 outfield and 16 main GKs.
- Unified tab contains exactly 585 rows: 553 outfield and 32 main GKs.
- Unified ranks are unique, finite, and ordered by
  `Tournament Performance Score`.
- Every team’s displayed unified order exactly matches its
  `by_team_unified/<TEAM>.csv`, and all 32 team files exactly partition the
  unified global table.
- No website surface substitutes outfield, GK-only, legacy, or non-unified
  rank fields for unified rank or `Tournament Performance Score`.
- Exactly 32 main GKs are ranked in dedicated and unified GK publications.
- Exactly 8 backup GKs are unranked in unified ranking but retain profiles.
- All 593 profile Markdown files have prerendered routes.
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
  exact file under `results/reports/v3_figures/` or `results/figures/`,
  according to its authority.
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
  exact source link to `results/reports/v3_figures/<filename>` or
  `results/figures/<filename>`.
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
   - exact `PASS8_COMMIT` and manifest hashes
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
