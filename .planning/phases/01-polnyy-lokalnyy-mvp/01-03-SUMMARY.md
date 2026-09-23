---
phase: 01-polnyy-lokalnyy-mvp
plan: "03"
subsystem: integration
tags: [python, http, csv, json, validation, reproducibility, playwright]
requires:
  - phase: 01-01
    provides: validated parquet pipeline and analytic exports
  - phase: 01-02
    provides: built analyst interface and real browser smoke
provides:
  - Reproducible batch CLI and loopback UI/data server
  - Independent CSV/JSON source validation and deterministic repeated execution
  - Reproduction instructions, architecture diagram and five-minute actual-data demo
affects: [delivery, phase-02]
tech-stack:
  added: [Python standard-library HTTP server]
  patterns: [allowlisted static publication, independent artifact verification, string browser identifiers]
key-files:
  created: [solution/__init__.py, solution/__main__.py, solution/server.py, tests/test_contracts.py, scripts/verify_delivery.py, docs/DEMO.md, docs/ARCHITECTURE.md, requirements.txt, requirements-dev.txt]
  modified: [README.md, .gitignore]
key-decisions:
  - Server binds exclusively to loopback and exposes four named data files plus the built UI.
  - Validator reads source parquet independently and compares repeated CSV bytes and JSON except elapsed_seconds.
  - All 19 isolates remain present; 35 weak components include 16 nontrivial components and 19 isolates.
  - Pin tested Python dependencies and state Python 3.12+ excluding 3.14.1 as the supported baseline.
requirements-completed: [DATA-01, DATA-02, DATA-03, ROLE-01, ROLE-02, ROLE-03, CLUS-01, RANK-01, UI-01, UI-02, UI-03, UI-04, SHIP-01, SHIP-02, TEST-01]
actuals:
  tokens: 11705
  tasks: 3
  commits: 17
plan_head_before: cde7b7c57b29d520d5ac8118c66e2082441efc08
coverage:
  - id: delivery-cli-server
    description: Batch calculation and safe local publication of actual data
    requirement: SHIP-01
    verification:
      - kind: integration
        ref: tests/test_contracts.py
        status: pass
    human_judgment: false
  - id: independent-output-contract
    description: Actual parquet, export invariants, repeatability and runtime validation
    requirement: TEST-01
    verification:
      - kind: integration
        ref: scripts/verify_delivery.py --data FINANCE-CASE/data --out output --browser
        status: pass
    human_judgment: false
  - id: actual-browser-flow
    description: Search, graph directions, ranks, isolates, boundaries, exports and mobile keyboard flow
    requirement: UI-04
    verification:
      - kind: automated_ui
        ref: frontend/scripts/ui-smoke.mjs
        status: pass
    human_judgment: false
duration: 14min
completed: 2026-09-23
status: complete
---

# Phase 1 Plan 3: Local delivery and independent verification Summary

**Real parquet produces reproducible CSV/JSON through one CLI command; the loopback interface and actual-data browser workflow pass independent acceptance.**

## Accomplishments

- CLI forwards selected data/output directories, reports missing inputs clearly and invokes the shared pipeline.
- HTTP serves built UI and exactly report.json plus three CSVs; URL traversal and symlink escapes are rejected, directory listing is unavailable, sockets bind to 127.0.0.1.
- Independent validator verifies exact CSV columns, all source gids, string browser identifiers, finite numerical types, roles/scores/evidence, source degrees/amounts, seeds/boundaries/isolates, cluster membership/counts/sums, top ranks/order, edge references and input totals.
- Corruption tests confirm rejection of duplicate/missing gids, schema changes, invalid scores, empty/long evidence, corrupt community sums, wrong ranking, numeric JSON strings, NaN, and numeric browser identifiers.
- README records every role threshold, precedence and role-strength formula, priority calculation, Louvain method and community-purpose hypothesis rule. Architecture and five-minute demonstration use actual selected examples with caveats.

## Verification evidence

Command (browser binaries were installed in a temporary local cache for this environment):

```bash
PLAYWRIGHT_BROWSERS_PATH=/tmp/money-graph-browsers .venv/bin/python scripts/verify_delivery.py --data FINANCE-CASE/data --out output --browser
```

Exit 0, status PASS. Full subprocess batch wall times **0.617 s and 0.666 s**, both below 300 s. Internal analytics timings were 0.215 s and 0.227 s. CSV bytes match across independent output directories; JSON matches after removing only elapsed_seconds. HTTP returns exact built index and published report/CSV bytes.

Measured inputs: **2248 nodes, 3119 edges, 4840 transactions, 81 seeds, 19 isolates, 365890012.01 KZT**. Outputs contain 91 communities and 50 priority rows. The period is July 1–31, 2026. The case's 16-component prose omits isolated nodes; preserving them yields 35 weak components.

Browser smoke passed real-data loading, string gid search, ranking selection, directed arrows, cluster mode, zoom, isolate messaging, depth boundary warning, three CSV downloads, keyboard focus and a 390-pixel viewport without horizontal overflow. No runtime page errors occurred. The automated screenshot is `/tmp/money-graph-mobile.png`.

`.venv/bin/python -m unittest discover -s tests -v`: **20 tests passed in 2.192 s** (10 analytics and 10 integration tests). Both CLI help commands and Python compileall succeeded. Frontend owner supplied the built UI and browser script; source ownership remained separated.

## Task commits

Git operations are serialized by the parent under AGENTS.md; workers do not commit. Ready file batches were reported as soon as checks passed.

1. CLI/server: `9b2efbf` test, `eef9956` implementation, `d3714e7` HTTP tests.
2. Independent validation: `878ff63`, `d8ece12`; final hardening included in the parent's subsequent integration commit.
3. Reproduction, diagram and demo: `6c10263`; final measured runtime and community-purpose documentation prepared for the parent metadata commit.

The recorded 17-commit range was measured with `git rev-list --count cde7b7c..HEAD` at summary creation. The shared branch also contains parallel analytics/UI commits, so this count is the shared execution interval, not 17 commits exclusively authored by this plan. `actuals.tokens` is ceil(realized owned-file diff characters / 4), not harness token usage. The parent finalizes metadata and serialized state updates.

## Decisions and deviations

- **[Rule 2 — correctness]** Root dependencies require Python 3.12+ (numpy/NetworkX metadata), excluding NetworkX-incompatible 3.14.1; documentation records the actual tested 3.14.4 environment.
- **[Rule 3 — environment]** Sandbox denied socket creation even on loopback. Approved escalated tests verified the real HTTP boundary; tests were not skipped.
- **[Rule 3 — environment]** First browser attempt failed because the browser executable was not installed. Frontend owner installed the existing Playwright package's official Chromium binaries; the complete acceptance command was rerun and passed.
- Parent review requested meaningful community-purpose hypotheses. Analytics owner implemented and tested the change; this plan updated documentation and reran final real-data validation successfully.
- Work began on independent CLI/server preparation while wave-1 owners implemented the agreed interfaces, as explicitly allowed by the plan and parent.

## TDD Gate Compliance

CLI help test was observed failing its assertion before the entry point existed and was committed before implementation. Server and export mutation coverage were completed during implementation rather than through a strict separate RED commit for every behavior. The GSD RED-evidence utility parses Node TAP, while this project runs Python unittest; no compatible machine-verified TAP evidence was claimed. Project tdd_mode is false. Functional acceptance is green; strict per-task RED/GREEN chronology is a documented workflow deviation.

## Limitations

Heuristic roles and priorities lack labeled ground truth or calibrated guilt probabilities. Observations are intra-bank transfers in July 2026 at or above 5000 KZT; seed incoming flow and depth-4 continuation are incomplete. No external identity attributes are inferred. The local server is intended for local analysis. Million-node processing and neighborhood-serving architecture are documented future work. Live presentation quality remains a human judgment; the complete automated desktop/mobile interaction flow passed.

## Known Stubs

None. Scan of all owned source and delivery documents found no TODO, FIXME or placeholder implementation preventing delivery.

## Self-Check: PASSED

All 11 owned deliverable files exist. Listed task commit hashes were confirmed in git history. Real output validation, full HTTP/browser acceptance and the final combined Python suite passed. No plan-owned tracked files were deleted.
