---
phase: 03-ponyatnoe-rabochee-mesto-aml-analitika
plan: 01
status: complete
subsystem: frontend
tags: [react, shadcn, analyst-workbench, directed-graph, responsive]
requires: [phase-02-report-contract, installed-shadcn-components]
provides: [directional-analyst-workbench, mobile-money-flow-view, public-design-contract]
affects: [judge-journey, browser-acceptance]
tech-stack:
  added: ["@fontsource/ibm-plex-serif@5.3.0"]
  patterns: [deterministic-directed-lanes, bounded-neighbor-pages, progressive-disclosure]
key-files:
  created: [DESIGN.md, frontend/src/components/Inspector.tsx, frontend/src/components/Graph.test.tsx, frontend/src/presentation.ts, frontend/src/presentation.test.ts]
  modified: [frontend/package.json, frontend/package-lock.json, frontend/src/App.tsx, frontend/src/components/Graph.tsx, frontend/src/index.css, frontend/src/App.test.tsx]
key-decisions:
  - Use a deterministic two-dimensional incoming/selected/outgoing graph instead of a radial network or 3D rendering.
  - Display full gid strings for every visible participant and keep all neighbor pages accessible.
  - On narrow screens use the same directed edges as a selected-account card and incoming/outgoing lists with exact amounts.
  - Reuse official installed shadcn controls and pair local Geist with locally bundled IBM Plex Serif for the user's final typography direction.
duration: not measured
completed: 2026-09-23
tasks_completed: 2
commits: 5
plan_head_before: c5b02fe71fab0fd0a33e81963726c178efa2fb70
---

# Phase 03 Plan 01: Understandable analyst workbench Summary

The analyst now sees priorities, a directional money-flow graph and selected-account evidence together; mobile keeps selected identity and direction visible through a dedicated compact view.

## Delivered behavior

- A compact header contains methodology and all three CSV exports; global exact-string gid search remains independent of list filters.
- Desktop places the ranked priority list on the left, a large directed graph in the center and an account inspector on the right. Every priority retains rank, role, score and its supplied rationale.
- The graph separates senders and recipients, labels observed amounts and arrow directions, displays full gids, supports keyboard selection and role/cluster coloring, and pages six neighbors per side in deterministic amount/gid order. High-degree nodes retain access to every neighbor.
- The all-node mode preserves combined role, cluster, seed and boundary filters, reset, twenty-row pagination, and cluster hypotheses/member exploration.
- The inspector preserves all original metrics and boundary/seed/isolate cautions; dated evidence, next-data requests, all neighbors and community details are available through labeled disclosures. Labels now distinguish the ratio “Выход / вход” from money amounts.
- Below 760px, the selected gid stays above incoming/outgoing controls, explicit money direction and neighbor cards with exact amounts and transaction counts. The clipped desktop SVG is hidden at this breakpoint.
- DESIGN.md is the public canonical design contract. The final user-directed visual refinement pairs locally bundled IBM Plex Serif headings with Geist body text and monospace gids. One verified official font package was added; organizer inputs, analytics rules, report schemas and CSV schemas are unchanged.

## Task commits

| Task | Commit | Result |
|---|---|---|
| 1: Workbench and directional graph | d494bb5 | Rebuilt the main screen, extracted inspector and replaced radial graph. |
| 2: Interaction coverage | 2259e0f | Covered directed lanes, pagination, full identity, keyboard and shared navigation. |
| Browser-driven refinement | 68aa137 | Added compact mobile flow, clearer metric labels and 21-test coverage. |
| Final user-directed refinement | 1531067 | Added local IBM Plex Serif typography, corrected mobile count scope and neutral transaction-count wording. |
| Resumed readability closure | 0cb3089 | Increased meaningful labels and contrast, translated known role/seed explanations with exact source disclosure, and linked mobile selection directly to its evidence. |

The parent serialized all commits and pushes as required by project instructions. Count above is measured with `git rev-list --count c5b02fe71fab0fd0a33e81963726c178efa2fb70..0cb3089` at this summary update; later parent integration/documentation commits belong to 03-02.

## Resumed work after shutdown

The saved implementation was recovered and compared with DESIGN.md and fresh real-data screenshots. The directed layout and navigation were already implemented; remaining gaps were small weak-contrast labels, raw English role/seed terms in evidence, and the distance from mobile graph to the inspector. The actionable audit is recorded in `03-UI-RESUME-GAPS.md`.

- Meaningful HTML labels, metrics, cautions and mobile direction text now use at least 12px. Secondary text #5e6b62 has contrast 5.59:1 on white and 5.25:1 on the canvas; warning text #775d28 has 5.75:1 against its background. SVG labels still scale with graph zoom, explicitly documented in DESIGN.md.
- A narrow presentation helper translates known role prefixes and seed reachability phrases, preserves every number and unknown report prose, and never mutates the report. The inspector exposes exact original evidence and ranking rationale in «Исходный текст расчёта». Methodology defines seed and filters say «Исходные узлы (seed)».
- The mobile selected-account card links directly to the current participant's inspector. Existing graph directions, pagination, filters, exports, analytics and schemas remain unchanged.
- Expanded the compressed stylesheet into readable declarations. No new dependency, endpoint or trust boundary was introduced.
- Fresh frontend run: **29/29 tests passed**, including all six role translations, unchanged numeric/unknown text, exact original source access and mobile inspector target. Production build and `git diff --check` passed.
- Independent verifier repeated **24 real-data browser checks** against 2248 nodes, 3119 edges and 4840 transactions. It confirmed arbitrary gid navigation, boundary/isolate semantics, all neighbor pages, current filters and exact source disclosure. Fresh desktop, 390px and 304px screenshots were inspected; this executor also inspected desktop and 304px images. Direction, full identity, amounts, role and warnings remained readable without overlapping labels. At 304px `document.scrollWidth` was 304: no horizontal page overflow. The search placeholder truncates at that width, while the labeled input and search button remain usable.

Evidence paths: `/tmp/money-graph-desktop-phase3.png`, `/tmp/money-graph-mobile-phase3.png`, `/tmp/money-graph-mobile-304-phase3.png`. These are runtime screenshots; durable verification belongs to the parent's phase verification artifact. User usability approval is not inferred from these checks.

## Initial delivery validation evidence

- `npm --prefix frontend run typecheck`: passed before task-one handoff.
- `npm --prefix frontend run test -- --run`: 21/21 passed after the mobile refinement.
- `npm --prefix frontend run build`: passed after the mobile refinement and final typography; local Geist and IBM Plex Serif Cyrillic/Latin assets are included in production output.
- `git diff --check`: passed.
- Parent independently inspected the 1440px desktop screenshot and reported readable lanes, identity, amounts and account context without visible overlap.
- Parent reported the real-data browser journey passed 22 checks, including three arbitrary gids, all 116 recipients across 20 pages and same-origin assets. Parent separately inspected the mobile refinement: selected identity, recipient, direction and amount were readable. The resumed verification above supersedes the original session's pending final recheck.

Automated checks and independent screenshots do not constitute manual user usability approval; that approval is not claimed here.

## Deviations from Plan

### Auto-fixed issues

1. **[Rule 1 — Bug] Narrow-screen desktop SVG clipped selected and recipient context.** Parent screenshot inspection at approximately 304px exposed a partial graph and clipped toolbar. Replaced that narrow presentation with a selected-gid card, directional incoming/outgoing lists, full identities, amounts and paging. Added a focused mobile interaction test and rebuilt successfully. Files: Graph.tsx, Graph.test.tsx, index.css. Commit: 68aa137.
2. **[Rule 2 — Correctness] Neighbor identity could be ambiguous when shortened.** Real gids can share prefixes and suffixes. Every visible graph node now displays its full gid, with unchanged full-gid focus text and accessible name. Files: Graph.tsx, Graph.test.tsx. Commit: 2259e0f.
3. **[Rule 1 — Bug] Mobile count described both desktop lanes.** Changed narrow-screen counts to the current visible direction and retained combined counts on desktop; tested switching between incoming and outgoing scopes. Also replaced count-dependent Russian transaction noun forms with neutral “Переводов: N”. Files: Graph.tsx, Graph.test.tsx, Inspector.tsx, index.css. Commit: 1531067.

## Tooling and design choices

Applied installed Design Taste entry, frontend-design and minimalist guidance to a functional application rather than a marketing page. Context7 official React documentation was resolved and queried for derived memoized state. This agent did not expose a shadcn MCP tool; existing official shadcn component source was reused. Later user steering explicitly requested a stronger distinctive aesthetic: verified the official Fontsource IBM Plex Serif package through npm metadata, fetched Context7 Fontsource subset/Vite guidance, and installed the pinned 5.3.0 package with scripts disabled. All font assets remain local; no runtime network service was added.

## Remaining acceptance

The independent real-data browser journey and screenshots have been repeated after resumed changes as documented above. Parent owns durable phase verification, shared STATE/ROADMAP/REQUIREMENTS updates and phase acceptance. User usability acceptance remains distinct. No implementation stubs or new threat surfaces were found in this plan's source scan; the sole matching “placeholder” token is the real gid input hint.

## Self-Check: PASSED

Created source/design files and installed Cyrillic font CSS exist. Commits d494bb5, 2259e0f, 68aa137, 1531067 and 0cb3089 are present. The resumed helper, its tests and gap audit exist. The fresh 29-test run, production build, diff check and independently repeated 24-check browser journey cover the final resumed implementation. No stubs were introduced. Summary claims distinguish implementation and verification from manual user usability approval.
