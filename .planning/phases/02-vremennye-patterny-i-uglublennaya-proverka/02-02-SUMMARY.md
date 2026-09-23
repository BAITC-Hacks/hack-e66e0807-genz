---
phase: 02-vremennye-patterny-i-uglublennaya-proverka
plan: 02
subsystem: ui
tags: [react, typescript, shadcn, temporal-evidence, exploration, playwright]
requires:
  - phase: 01-polnyy-lokalnyy-mvp
    provides: searchable graph, node inspector, report parser, ranking and shadcn interface
provides:
  - dated temporal evidence and next-data requests in the selected node card
  - four composable shadcn Select filters, paged exploration results and cluster navigation
  - real-browser checks of temporal evidence, filters, keyboard use and mobile layout
affects: [phase-02-verification, frontend]
actuals:
  tokens: 12818
  tasks: 2
  commits: 4
commits: 4
plan_head_before: 7a0e4a99825068c9a6038e82613004789a97b5dd
tech-stack:
  added: []
  patterns:
    - validate additive report fields independently while preserving required version 1.0 data
    - filter a local sorted result list without narrowing global gid search or selected graph
key-files:
  created: []
  modified:
    - frontend/src/contract.ts
    - frontend/src/App.tsx
    - frontend/src/App.test.tsx
    - frontend/src/index.css
    - frontend/scripts/ui-smoke.mjs
key-decisions:
  - "Malformed optional evidence is discarded with a nonfatal warning; required node data remains usable."
  - "The 1–2 day count is labeled cumulative and is never added visually to the 1-day count."
  - "All four filters use installed official shadcn Select and affect only the exploration list."
requirements-completed: [TIME-01, EXPL-01]
coverage:
  - id: D1
    description: Selected nodes show dated temporal evidence, incoming profile, synchronous payers, peaks and ordered next-data requests while older reports remain usable.
    requirement: TIME-01
    verification:
      - kind: unit
        ref: frontend/src/App.test.tsx#selected node shows dated temporal evidence, incoming profile and ordered requests
        status: pass
      - kind: automated_ui
        ref: frontend/scripts/ui-smoke.mjs#temporal
        status: pass
    human_judgment: false
  - id: D2
    description: Four filters compose over a paged result list, cluster actions focus results, and global gid search remains available.
    requirement: EXPL-01
    verification:
      - kind: unit
        ref: frontend/src/App.test.tsx#exploration pages all report nodes and combines four labeled filters without narrowing gid search
        status: pass
      - kind: automated_ui
        ref: frontend/scripts/ui-smoke.mjs#select-filters
        status: pass
    human_judgment: false
  - id: D3
    description: The interface visibly explains the four stages from organizer data to graph, cards and CSV files.
    verification:
      - kind: automated_ui
        ref: frontend/scripts/ui-smoke.mjs#analysis-flow
        status: pass
    human_judgment: false
duration: 7min
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 2: Temporal card and exploration Summary

**The local analyst UI now shows observed timing and incoming evidence for a selected gid and lets analysts narrow all report nodes by role, cluster, seed and boundary without losing global search.**

## Performance

- **Started:** 2026-09-23T11:21:18Z
- **Completed:** 2026-09-23T11:27:38Z
- **Tasks:** 2
- **Files modified:** 5
- **Measured diff:** 51,271 characters, or 12,818 estimate-scale tokens after dividing by four.
- **Measured commit range:** 4 commits from `plan_head_before` through `1b92bd2`; two are concurrent backend commits in the shared branch.

## Accomplishments

- Parsed optional temporal metrics and requests independently from required report fields. Invalid optional values raise the exact nonfatal message; old reports omit the optional sections.
- Displayed one-day and cumulative two-day observations with dated examples, incoming profile, same-day distinct-payer concentration, qualifying peak activity, depth-four caution, and the explicit warning that matching dates do not trace identical funds.
- Added four official shadcn Select controls, deterministic results sorted by priority then numeric gid, 20-row paging, empty/reset states, cluster metrics and focus-aware cluster navigation.
- Added a compact visible analysis-flow Card for judging and extended the real-browser smoke to new interactions.

## Task Commits

1. **Task 1 RED:** `3c0a8e2` — failing tests for temporal card and optional field behavior.
2. **Tasks 1 and 2 GREEN:** `1b92bd2` — parser, card, exploration, tests, CSS and smoke checks. Task 2's two intentional RED failures were observed before implementation; concurrent shared-branch commits required one serialized frontend GREEN commit.

The official shadcn Select was installed before this plan in `54bc9c9`.

## Verification

- `npm --prefix frontend run test -- --run`: 11/11 passed.
- `npm --prefix frontend run build`: TypeScript and Vite build passed.
- `PLAYWRIGHT_BROWSERS_PATH=/tmp/money-graph-browsers node frontend/scripts/ui-smoke.mjs http://127.0.0.1:8765`: passed 18 browser checks on the real report with 2,248 nodes and 3,119 edges, including temporal data, filters, cluster focus, keyboard selection and 390px overflow.
- Screenshots captured at `/tmp/money-graph-desktop-phase2.png` and `/tmp/money-graph-mobile.png`.

## Deviations from Plan

- Added the user-requested four-stage “Как устроен анализ” Card before CSV downloads. It uses existing report architecture and introduces no new data interface.
- The shared branch serialized Task 2's RED and GREEN into one frontend commit after the failing test run; tests still preceded implementation.

## Known Stubs

None. The parser's internal empty object is a temporary accumulator, and absent optional evidence is intentionally omitted from the UI.

## Threat Flags

None. The UI renders report strings as React text, validates optional data, filters only the already-loaded report and adds no routes or trust boundary.

## Next Phase Readiness

The browser UI is ready for independent Phase 2 verification against the regenerated report. The parent executor owns shared STATE, ROADMAP and REQUIREMENTS updates and the final metadata commit.

## Self-Check: PASSED

All five modified frontend files and this summary exist. Commits `3c0a8e2` and `1b92bd2` are present, and the recorded range contains four commits.
