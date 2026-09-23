---
phase: 01-polnyy-lokalnyy-mvp
verified: 2026-09-23T12:09:10Z
status: passed
score: 5/5 must-haves verified
covered_files: [.planning/phases/01-polnyy-lokalnyy-mvp/01-01-PLAN.md, .planning/phases/01-polnyy-lokalnyy-mvp/01-01-SUMMARY.md, .planning/phases/01-polnyy-lokalnyy-mvp/01-02-PLAN.md, .planning/phases/01-polnyy-lokalnyy-mvp/01-02-SUMMARY.md, .planning/phases/01-polnyy-lokalnyy-mvp/01-03-PLAN.md, .planning/phases/01-polnyy-lokalnyy-mvp/01-03-SUMMARY.md, DESIGN.md, README.md, docs/ARCHITECTURE.md, docs/DATA-CONTRACT.md, docs/DEMO.md, docs/METHODOLOGY.md, frontend/components.json, frontend/index.html, frontend/package-lock.json, frontend/package.json, frontend/scripts/ui-smoke.mjs, frontend/src/App.test.tsx, frontend/src/App.tsx, frontend/src/components/Graph.test.tsx, frontend/src/components/Graph.tsx, frontend/src/components/Inspector.tsx, frontend/src/contract.ts, frontend/src/index.css, frontend/src/main.tsx, frontend/src/presentation.test.ts, frontend/src/presentation.ts, frontend/vite.config.ts, requirements-dev.txt, requirements.txt, run.py, scripts/verify_delivery.py, scripts/verify_temporal.py, solution/__init__.py, solution/__main__.py, solution/analytics.py, solution/pipeline.py, solution/server.py, solution/temporal.py, tests/test_analytics.py, tests/test_contracts.py, tests/test_temporal.py]
covered_digest: "v1:sha256:814175f10ffc4d5d688b9e7cb8ca942bd094b6906d046f7237f31f526078ee1b"
behavior_unverified: 0
overrides_applied: 0
acceptance_scope: "historical MVP technical capabilities; UI-04 visual acceptance remains open in Phase 3"
---

# Phase 1: Полный локальный MVP Verification Report

**Phase goal:** As a local AML analyst, I want to inspect explainable transaction-network priorities, so that I can reproduce and demonstrate all five required case capabilities.

**Status:** `passed` — all five roadmap truths have code and execution evidence. The MVP user-story format passes `user-story.validate`. The user explicitly authorized autonomous verification; the agent reviewed the real desktop/mobile interface and executable demo artifacts. This is agent acceptance, not a claim of human sign-off or a witnessed fresh-machine installation.

## User Flow Coverage

| Step | Expected | Code and execution evidence | Status |
| --- | --- | --- | --- |
| Calculate | Run one command on the three parquet inputs | `solution/__main__.py` calls `run_pipeline`; independent `scripts/verify_delivery.py --browser` ran two complete CLI processes in 0.516 s each. | VERIFIED |
| Open priorities | See ranked participants and reasons | `App.tsx` renders `report.top_nodes`; actual `top_nodes.csv` has 50 unique ranks with `why`, and browser smoke selected rank 1. | VERIFIED |
| Inspect any gid | Search exact string and see role, evidence, cluster and links | `App.tsx` keeps gid strings, searches all nodes and renders `Inspector` plus `Graph`; real browser smoke covered search, isolate and boundary nodes. | VERIFIED |
| Interpret result | Understand why this participant deserves review | Rules, precedence and heuristic priority formula are in README; actual card shows amounts, degrees, seed ancestry, evidence and warnings. Agent inspection of the actual desktop and mobile UI found readable labels, arrow direction, visible focus and caveats. | VERIFIED |
| Demonstrate outcome | Reproduce and explain the five case capabilities | README commands and dependencies, Mermaid diagram and five-minute scenario with three real nodes; prepared-workspace CLI, local UI, tests and browser acceptance passed. | VERIFIED |

## Goal Achievement

| # | Roadmap success criterion | Status | Decisive evidence |
| --- | --- | --- | --- |
| 1 | One command, <300 s, four fixed outputs, every gid, string JSON IDs and input consistency | VERIFIED | Independent two-run validator: 2,248 nodes, 3,119 edges, 4,840 transactions, 81 seed, 19 isolates, 365,890,012.01 KZT; both processes 0.516 s; exact CSV schemas, all gid/reference/sum/count checks and deterministic CSV/JSON passed. |
| 2 | Six explained roles, bounded scores, censoring/seed caveats and documented rules | VERIFIED | `classify_role` first-match rules and scores, `analyze` warnings and null pass-through, `App.tsx` card, README thresholds; named role/cluster test and independent real-export validator passed. No boundary or seed node is terminal/transit. |
| 3 | Community for each node and ranked top ≥20 | VERIFIED | Louvain membership built from all nodes including isolates; `cluster_hypothesis` uses observed role counts and internal sum; real output has 91 clusters and 50 unique ranked rows, independently validated. CR-01 regression test passed. |
| 4 | Directed local shadcn UI, any-gid search, exports, states, keyboard and narrow screen | VERIFIED | React `App`, `Graph`, local shadcn components and static server are wired. Eleven actual-data browser checks passed, including arrows, exports, keyboard and 390 px width. Agent visual review of live desktop and 390 px screenshot found readable stacked content, direction, legend, focus and caveats. |
| 5 | Reproducible setup, rules/scale docs, diagram, five-minute demo and passing checks | VERIFIED | README gives installation/build/run commands, formulas and a credible million-node path; Mermaid architecture and timed demo script use three actual nodes. Independent full Python suite, UI tests/build and real-data browser acceptance passed. No separate clean-machine or live-audience rehearsal was performed. |

**Score:** 5/5 roadmap truths verified; 0 present-but-behavior-unverified state transitions.

## Required Artifacts and Key Links

| Artifact or link | Level 1/2 | Level 3/4 conclusion |
| --- | --- | --- |
| `solution/pipeline.py` → parquet inputs → `solution/analytics.py` | Substantive validation and calculation | `read_parquet` consumes all three named inputs; graph includes all source nodes before edges; generated roles, clusters, rankings and JSON pass independent source comparison. |
| `solution/__main__.py` → `run_pipeline` | Substantive CLI | Direct import/call forwards user paths; subprocess result observed. |
| `solution/server.py` → built UI and four output files | Substantive allowlisted HTTP handler | Real HTTP byte equality passed for index, JSON and three CSVs. |
| `frontend/src/App.tsx` → `/data/report.json` → render | Substantive fetch/schema handling | `parseReport` validates version, strings and references; fetched report populates search, ranking, card and Graph. Real browser acceptance passed. |
| `Graph.tsx` ↔ selected gid and report edges | Substantive neighborhood render | `App` passes shared selection and callback; SVG marker ends encode edge direction; all omitted neighbors remain in card lists. |
| `App.tsx` → three `/data/*.csv` downloads | Substantive generated links | Browser checked each href and fetched all files. |
| `scripts/verify_delivery.py` → browser smoke | Substantive independent validator | Invokes `frontend/scripts/ui-smoke.mjs` against its own real-data loopback server; exit 0. |
| Tests, README, architecture and demo | Substantive content | Analytics, contract and UI tests execute; docs contain runnable commands, formulae, caveats, diagram and actual-node script. |

The `verify.key-links` helper reports false negatives for links represented by imports, parameterized paths or callbacks rather than literal target-file strings. Manual source tracing and executed checks above establish those links; no key link remains unwired.

## Data Flow

`FINANCE-CASE/data/{nodes,edges,transactions}.parquet` → pandas validation → NetworkX metrics/roles/communities → `output/{nodes_roles,clusters,top_nodes}.csv` and `report.json` → allowlisted `/data` HTTP mapping → `parseReport` → `report` state → ranking, graph and inspector. Generated values and browser views come from real input; the synthetic large-gid fixture appears only in `App.test.tsx`.

## Behavioral and Probe Checks

| Check | Result |
| --- | --- |
| `PLAYWRIGHT_BROWSERS_PATH=/tmp/money-graph-browsers .venv/bin/python scripts/verify_delivery.py --data FINANCE-CASE/data --out /tmp/gsd-verifier-phase1-output --browser` | PASS, 0.516/0.516 s; 11 browser checks; isolates and boundary exercised. Needed loopback sandbox escalation after expected `Operation not permitted` on first attempt. |
| `.venv/bin/python -m unittest tests.test_analytics.CommunityTests.test_cluster_hypotheses_distinguish_flow_purposes_and_uncertainty -v` | PASS; repaired cluster hypothesis distinguishes collection, distribution, transit and insufficient evidence. |
| `.venv/bin/python -m unittest discover -s tests -v` | PASS, all 20 tests. The first sandbox run failed only three socket-creation tests with `PermissionError`; the same suite passed in an escalated loopback-capable process. |
| `npm --prefix frontend run test -- --run` | PASS, 7 tests. |
| `npm --prefix frontend run build` | PASS, local CSS/JS bundles. |

No phase probe script was declared or found. The full Python suite, focused cluster regression, real-data acceptance, UI tests and build were rerun by this verifier rather than taken from a SUMMARY claim.

## Requirements Coverage

| Requirement | Verdict | Evidence |
| --- | --- | --- |
| DATA-01 | SATISFIED | One CLI and measured 0.516 s real runs. |
| DATA-02 | SATISFIED | Independent source/output gid, reference, sum and count checks; 19 isolates retained. |
| DATA-03 | SATISFIED | Documented v1.0 contract, browser string gid parser, real JSON/CSV comparison. |
| ROLE-01 | SATISFIED | All 2,248 source gid have six-role dictionary values, bounded scores and 1–200-character evidence. |
| ROLE-02 | SATISFIED | README rules/thresholds/precedence, actual numerical card and visual inspection of caveats. |
| ROLE-03 | SATISFIED | Boundary/seed exclusion in classifier, warnings in JSON/card, null pass-through and hypothesis wording; real validator enforces. |
| CLUS-01 | SATISFIED | Every gid has cluster id; 91 CSV clusters with validated size, seeds, sums, top gids and meaningful purpose hypothesis. |
| RANK-01 | SATISFIED | 50 unique consecutive ranks sorted by score then numeric gid with `why`. |
| UI-01 | SATISFIED | SVG directed arrows, role/cluster switch and legends; browser checks. |
| UI-02 | SATISFIED | Shared exact-string selection from search/rank/neighbor; browser tested isolate and boundary. |
| UI-03 | SATISFIED | Three HTTP downloads; distinct loading, error, empty, unknown and unsupported-schema states in code/tests. |
| UI-04 | SATISFIED | Local bundle, keyboard smoke and 390 px width passed; agent inspected live desktop/mobile presentation, focus, legend and caveats. |
| SHIP-01 | SATISFIED | README commands, pinned dependencies, rules, limits and million-node approach; actual calculation/build/server commands executed in the prepared workspace. |
| SHIP-02 | SATISFIED | Mermaid solution diagram and timed five-minute scenario with three real gids exist and its data matches the generated report. |
| TEST-01 | SATISFIED | Real-data acceptance, deterministic output, named cluster regression, seven UI tests and build pass. |

All 15 v1 IDs are claimed by phase plans; no orphaned phase requirement. Phase 2 explicitly owns TIME-01/EXPL-01, so those are outside this verdict.

## Anti-patterns and Disconfirmation

No unresolved `TBD`, `FIXME` or `XXX` markers in phase implementation/tests/delivery documents. No production fixture or hardcoded result list was found; demo example gids are documented as selected from actual output. The agent inspected the actual browser presentation after the automated width/keyboard smoke, because those assertions alone cannot prove readable text. The pipeline's error paths have coverage for missing/invalid parquet and the static server's traversal path in `tests/test_contracts.py`.

## Acceptance Boundary

The plan suggested end-of-phase human checks for visual clarity and a live presentation. The user's explicit autonomous instruction authorizes agent acceptance: real desktop/390 px views were inspected and the five-minute script, command path and actual-node examples were checked. No human sign-off, separate clean-machine installation or live-audience demo was observed. Those are presentation/reproduction limitations, not missing phase artifacts or a failed executable criterion. There are no gaps requiring `$gsd-plan-phase --gaps`.

_Verifier: gsd-verifier agent; no commit made._

## Follow-up acceptance correction — 2026-09-23 11:26UTC

User found README insufficiently understandable for independent jury evaluation. Original automated verification proved artifact presence and executable commands, not sufficient first-use clarity. Delivery documentation is reopened for focused acceptance under Phase2 plan03: one-command launcher, unfamiliar-reviewer instructions, architecture presentation and timed demo. Original implementation evidence remains valid, but final submission readiness must not be claimed until this follow-up is verified. No human sign-off is implied.

## Follow-up acceptance closure — 2026-09-23 11:35 UTC

The reopened jury-clarity criterion is now verified against the delivered files and workflow. README's first screen identifies the AML analyst's decision, explains the three separately supplied organizer parquet files, gives one launch command (`python3 run.py`), local URL, CSV exports and a four-step analyst journey. The technology section and Mermaid diagram explain how parquet becomes metrics, roles, communities, CSV/JSON and the local interface. The linked five-minute demo specifies a live launch and three actual nodes: a top-ranked coordinator with temporal evidence, a depth-four boundary node, and an isolated seed. Their stated roles, counts, amounts and dates match the current real report. The independent checks and limits, including `depth=4`, seed incompleteness and temporal uncertainty, are easy to locate.

Execution evidence is current: `python3 run.py --skip-install --check` passed on the prepared machine; the same launcher on port 8010 served HTML, report and CSV with HTTP 200. This verifier independently reran the original delivery validator with its browser path: 18 real-data checks passed, two complete calculations took 0.616 seconds each, all 2,248 gids and 19 isolates were retained, three CSVs were deterministic, and the UI handled arbitrary search, boundary and isolate nodes. The exact new command's first dependency installation on a separate clean machine and a live jury presentation were not observed, so this closure does not assert either. The user's autonomous acceptance instruction permits the agent to close the documentation gap from these code, report and browser observations without inventing human sign-off.

## User acceptance correction: UI redesign required

After the functional checks above, the user rejected interface and graph readability. These results remain evidence of the previous implementation’s technical behavior, not user approval of usability. UI-04 is reopened and Phase 3 must verify the redesigned graph and analyst workflow. The earlier documentation check is also superseded by the requested deeper public technical documentation audit.

## Dated technical regression refresh — 2026-09-23T12:09:10Z

The 11:35:41Z observations above are retained as historical evidence. The Phase 1 `passed` verdict means its **technical MVP capabilities** still exist in the current codebase: one local parquet-to-exports launch, six explained roles, community and priority outputs, exact-gid graph navigation, CSV downloads and reproducible public documentation. It does **not** reverse the user's later rejection of the original presentation. UI-04's subjective readability is explicitly reopened and tracked by [Phase 3 verification](../03-ponyatnoe-rabochee-mesto-aml-analitika/03-VERIFICATION.md), whose current status is `human_needed`; final user visual acceptance has not been claimed.

After the reboot, I independently reran the current delivery verifier on the actual three organizer parquet files. It recalculated twice in 0.618 and 0.567 seconds, validated all 2,248 gids (including 19 isolates), 3,119 edges, 4,840 transactions, 81 seeds, 91 clusters, exact three CSV schemas, string JSON gids, sums/references and deterministic output, then passed 24 browser checks. The browser covered arbitrary gids, all 50 ranked recipients, isolate/boundary cautions, directed links, all pages of a dense outgoing neighborhood, temporal details, filters, keyboard and downloads without external runtime requests. The current Python suite passed 26/26, frontend suite 29/29 and production build passed. The separate temporal oracle passed all 2,248 nodes with 297 one-/two-day observations, 38 synchronous-payer nodes, 265 peaks and 444 boundary profiles. Agent inspection of fresh desktop, 390px and 304px screenshots found visible direction, amounts, full gid and evidence access; at 304px the page did not overflow horizontally. These checks establish current technical functionality, while Phase 3 retains the human usability decision.

The refreshed digest covers original Phase 1 plans/summaries, current production/data/browser code, tests and public documentation that substantiate those capabilities. Volatile `ROADMAP.md`, `REQUIREMENTS.md`, `STATE.md`, regenerated output and agent coordination files are excluded because later phase administration changes them without altering the Phase 1 implementation. The earlier isolated source-copy launcher check used package caches on this machine; it does not prove a clean operating-system installation. No full-suite rerun beyond the fresh checks above was needed for this addendum.
