---
phase: 02-vremennye-patterny-i-uglublennaya-proverka
plan: 01
subsystem: analytics
tags: [python, parquet, temporal-evidence, aml]
requires:
  - phase: 01-polnyy-lokalnyy-mvp
    provides: Validated parquet pipeline, fixed CSV exports, and versioned report
provides:
  - Calendar-day incoming-to-outgoing evidence per gid
  - Daily peaks, incoming profiles, synchronized arrivals, and next-data requests
affects: [02-02-frontend-exploration, 02-03-verification]
actuals:
  tokens: 3740
  tasks: 2
  commits: 2
plan_head_before: 3c0a8e2e7cbc48fd026ee912a3755eff3d2d8afd
tech-stack:
  added: []
  patterns: [Pure enrichment after structural analysis, date-indexed transaction observations]
key-files:
  created: [solution/temporal.py, tests/test_temporal.py]
  modified: [solution/pipeline.py, output/report.json]
key-decisions:
  - "Count each outgoing transaction once per qualifying calendar window, independent of incoming multiplicity."
  - "Treat temporal signals as observations and analyst follow-up requests; never feed them into role or priority scoring."
requirements-completed: [TIME-01, EXPL-01]
duration: 5min
completed: 2026-09-23
status: complete
---

# Phase 2 Plan 1: Temporal evidence and next-data requests Summary

Every node in the local report now has measured calendar-day evidence and concrete Russian follow-up requests, while existing roles, priorities, version 1.0, and all three CSV exports remain unchanged.

## Accomplishments

- Added one-day and one-or-two-day outgoing counts, with at most three sorted distinct date pairs. Same-day or later incoming rows cannot qualify; multiple incoming rows do not multiply one outgoing row.
- Added observed incoming activity, same-day concentration from at least three distinct payers, and a thresholded peak day. An incident self-loop contributes once to daily activity. Depth-four profiles remain observations, never terminal assertions.
- Added gid-specific requests for incomplete seed incoming history, missing incoming rows, depth-four output censoring, temporal uncertainty, or coverage beyond the bank and observed period.

## Task Commits

1. **Task 1: Carry one-day observation to report** — `90d4135` (`feat`)
2. **Task 2: Complete peaks, synchronous arrivals, and boundary semantics** — `8315a60` (`feat`)

## TDD Evidence

- Task 1 RED: the parquet-to-report test failed with `KeyError: 'temporal'`; GREEN: the one-day fixture passed after enrichment was connected.
- Task 2 RED: five temporal tests reported missing `synchronous_incoming` and `peak_day`; GREEN: all five passed after the full calendar logic and limitation-specific requests were added.

## Verification

- `.venv/bin/python -m unittest discover -s tests -p test_temporal.py -v`: 5 passed.
- `.venv/bin/python -m unittest discover -s tests -p test_analytics.py -v`: 10 passed.
- Full Python suite with loopback socket access: 25 passed. The first sandboxed full-suite run could not bind three existing server tests; the authorized loopback run passed all three.
- Real parquet run: 2248 nodes, 3119 edges, 4840 transactions. All 2248 nodes have complete temporal evidence and requests; 1002 one-day matches, 1594 one-or-two-day matches, 265 qualified peaks, and 38 synchronized arrivals across nodes. These per-node counts may count one transaction at multiple incident nodes where applicable.
- `cmp` against `/tmp/money-graph-phase1-csv` passed for `nodes_roles.csv`, `clusters.csv`, and `top_nodes.csv` byte for byte. The independent verifier also passed for all 2248 nodes.

## Deviations from Plan

None. The validated date parser and original CSV schemas were preserved.

## Known Stubs

None.

## Self-Check: PASSED

`solution/temporal.py`, `solution/pipeline.py`, `tests/test_temporal.py`, and `output/report.json` exist; commits `90d4135` and `8315a60` exist.
