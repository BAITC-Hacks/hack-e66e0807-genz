---
phase: 01-polnyy-lokalnyy-mvp
plan: "02"
subsystem: ui
tags: [react, vite, typescript, shadcn, svg, playwright]
status: complete
requires:
  - phase: shared-contract
    provides: docs/DATA-CONTRACT.md version 1.0
provides:
  - Russian analyst dashboard with exact string gid search and explained node inspection
  - Directed neighborhood, role/community legends, ranked selection and complete neighbor access
  - Local CSV downloads, validated report loading and browser acceptance script
affects: [01-03, phase-verification]
tech-stack:
  added: [React 19.3, Vite 8.3, TypeScript, Tailwind CSS 4, shadcn radix-nova, Vitest 5, Playwright]
  patterns: [validated local JSON boundary, shared selectedGid, bounded SVG rendering]
key-files:
  created: [frontend/src/App.tsx, frontend/src/contract.ts, frontend/src/components/Graph.tsx, frontend/src/App.test.tsx, frontend/scripts/ui-smoke.mjs, frontend/package-lock.json]
  modified: [.planning/phases/01-polnyy-lokalnyy-mvp/01-UI-SPEC.md]
key-decisions:
  - IDs remain strings at every frontend boundary and are never converted to numbers.
  - SVG renders selected node plus up to 36 neighbors; full neighbor lists and global search remain available.
  - Official shadcn radix-nova primitives use contract-specific slate/teal tokens and system fonts.
requirements-completed: [DATA-03, ROLE-02, ROLE-03, UI-01, UI-02, UI-03, UI-04, TEST-01]
plan_head_before: a7e726fbbef1ae443437bbcb6d1dfe5bb363146c
actuals:
  tokens: 89114
  tasks: 3
  commits: 13
duration: 14min
completed: 2026-09-23
---

# Phase 1 Plan 2: Explainable analyst UI Summary

**Russian shadcn dashboard connects exact long-gid search, directed neighborhoods, ranked review candidates and numerical evidence to the real local report.**

## Accomplishments

- Fetches `/data/report.json`, checks schema version, arrays, finite numeric fields, string IDs, duplicate IDs and edge/top/cluster references before rendering. Report strings are React text.
- Initial ranked selection, search, graph click, complete directed neighbor lists and cluster leaders share one selection. Unknown searches preserve the previous node. Isolates remain searchable.
- Displays all contracted role/priority scores, degrees, amounts, nullable pass-through, seed ancestors, depth, evidence, seed and boundary limitations, cluster hypothesis and actual counts.
- Role/cluster color switch, textual legends, payer-to-recipient arrows, pan, zoom and reset. Bounded graph renders at most 37 nodes and discloses omitted neighbors; full lists remain actionable.
- Light white/slate/teal layout, system fonts, responsive graph/inspector stacking, visible keyboard focus, polite selection announcements and minimum 44px controls. Three actual CSV download links.
- Distinct loading, retryable error, incompatible schema, empty report, empty ranking, unknown search and no-selection states. Synthetic data exists only in component tests.

## Verification

- `npm --prefix frontend run test -- --run`: **7/7 passing**.
- `npm --prefix frontend run typecheck`: **passed**.
- `npm --prefix frontend run build`: **passed**; local CSS 39.41 kB and JS 278.91 kB before gzip, no remote runtime assets.
- `PLAYWRIGHT_BROWSERS_PATH=/tmp/money-graph-browsers node frontend/scripts/ui-smoke.mjs http://127.0.0.1:8765`: **passed twice**, including after visual repair. Real report contained **2248 nodes / 3119 edges**. Checks cover exact ID, ranking, arrow markers, community mode, zoom/reset, actual isolate, actual censored-boundary node, CSV HTTP responses, keyboard and 390px no horizontal overflow. Browser emitted no runtime errors.
- Mobile screenshot reviewed at `/tmp/money-graph-mobile.png`; oversized pan-hint icon found and fixed before rerun.
- `npm --prefix frontend audit --omit=dev`: **0 vulnerabilities**. Initial dependency provisioning audit also reported zero vulnerabilities.
- Official Context7 resolve/query calls verified Vite React config/aliases and React effect cleanup. Official shadcn MCP `get_add_command_for_items` succeeded; CLI 4.21.0 init/add/info confirms six installed Radix primitives. Provenance appended to canonical UI-SPEC.

## Task Commits

Parent serialized commits as required by AGENTS.md:

1. Tracer/scaffold: `ccd0d10`; report-to-search implementation: `19f4ea1`.
2. Expanded behavior tests: `878ff63`; graph/inspector implementation: `69e925f`.
3. Responsive presentation and state coverage: `c1e0e91`. Browser smoke and visual-repair files handed to parent for immediate commit.

Commit actuals are the measured shared branch range `git rev-list --count a7e726fbbef1ae443437bbcb6d1dfe5bb363146c..HEAD` at summary creation, which includes concurrent backend/integration commits. Parent owns final ledger reconciliation and shared STATE/ROADMAP/REQUIREMENTS updates to avoid races. Token actuals use realized frontend diff plus new smoke source characters divided by four; package-lock accounts for most of the total.

## TDD Gate Compliance

Tracer and expanded interaction tests were written and run before corresponding implementation. GSD `check tdd-red-evidence` returned `RED_EVIDENCE_OK` for `/tmp/ui-tracer-red.json` and `/tmp/ui-expanded-red.json`. Vitest TAP-flat output was normalized by appending summary counts derived from its actual `ok` / `not ok` assertions, since GSD expects Node TAP summary comments. Task 3 state tests verified behavior already introduced with Task 2 and were green immediately; they are regression coverage, not an invented RED cycle. Parent combined RED tests/scaffold under its small-batch commit policy; the initial commit prefix is `feat`, so strict test-prefix history is not claimed.

## Deviations from Plan

- **Authorized provisioning change:** parent explicitly transferred frontend dependency installation to this executor. Official packages were installed with a committed lockfile; no substitute package was used.
- **Rule 3:** official shadcn CLI generated components.json, utils and four additional primitives beyond the original 13-file estimate. Required for actual shadcn setup and the design inventory; no mock components.
- **Rule 1:** graph canvas CSS unintentionally sized its nested help icon to 100%. Screenshot review exposed it; the icon now has explicit 16px dimensions. Production build and actual-data browser smoke passed after repair.
- Shared git and planning-state mutations are parent-owned under project AGENTS.md; executor supplied exact ready paths after each batch.

## Known Limitations

Only the selected node's immediate neighborhood appears on canvas. Above 36 neighbors the remaining nodes are disclosed and reachable through complete incoming/outgoing lists and global search. This is intentional bounded rendering, not missing data. Graph amounts/counts are available in titles and equivalent always-visible neighbor rows. Categorical cluster colors repeat with explicit cluster labels.

No production data stubs, skipped tests or unrun verification commands remain.

## Self-Check: PASSED

All declared frontend files exist, production build exists, named commits are present in the parent-owned history, all seven component tests and real-data browser acceptance pass.
