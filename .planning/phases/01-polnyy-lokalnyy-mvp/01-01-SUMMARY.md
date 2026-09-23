---
phase: 01-polnyy-lokalnyy-mvp
plan: "01"
subsystem: analytics
tags: [pandas, parquet, networkx, louvain, aml, deterministic]
requires:
  - phase: shared-contract
    provides: docs/DATA-CONTRACT.md and audited Python environment
provides:
  - Validated parquet-to-CSV/JSON pipeline preserving every input node
  - Six numerical role hypotheses with censoring and seed caveats
  - Weighted communities and deterministic structural review priorities
affects: [01-02, 01-03, verification]
tech-stack:
  added: []
  patterns: [first-match explainable rules, fixed-seed graph analysis, strict input validation]
key-files:
  created: [solution/analytics.py, solution/pipeline.py, tests/test_analytics.py]
  modified: []
key-decisions:
  - "First-match role precedence: coordinator, consolidator, distributor, transit, terminal, peripheral."
  - "Seed and zero-inflow pass-through is null; seed and depth>=4 cannot satisfy terminal or transit rules."
  - "Louvain uses summed opposite-direction monetary weights; centrality uses directed unweighted paths."
  - "Priority combines normalized observed flow, degree, reachable seeds and centrality, without a seed-membership bonus."
requirements-completed: [DATA-02, DATA-03, ROLE-01, ROLE-02, ROLE-03, CLUS-01, RANK-01, TEST-01]
actuals:
  tokens: 6025.5
  tasks: 3
  commits: 12
plan_head_before: 630bed88edf36ee65372e3e693ba834fdbce6fe1
duration: 6min
completed: 2026-09-23
status: complete
---

# Phase 1 Plan 1: Explainable Local Analytics Summary

**Real parquet data produces six censoring-aware role hypotheses, 91 weighted communities and 50 ranked review candidates while retaining all 2248 nodes.**

## Delivered and verified

`solution.pipeline.run_pipeline(Path, Path)` validates and reads the three organizer parquet files, then writes `report.json`, `nodes_roles.csv`, `clusters.csv` and `top_nodes.csv`. Output is available in `output/`. JSON identifiers are strings, CSV identifiers retain exact integer digits, schemas match the shared contract, and invalid floating values cannot enter JSON.

Required columns, integer identifier precision, boolean seed status, nulls, finite nonnegative amounts, duplicate nodes/pairs, node references, valid dates and transaction-to-edge aggregation are checked. Monetary aggregation uses an explicit 0.01 KZT absolute tolerance; counts must match exactly.

Measured from the provided inputs:

| Metric | Observed |
|---|---:|
| Nodes | 2248 |
| Directed edges | 3119 |
| Transactions | 4840 |
| Seeds | 81 |
| Total edge amount | 365890012.01 KZT |
| Weak components including isolates | 35 |
| Isolated nodes | 19 |
| Louvain communities | 91 |
| Ranked unique nodes | 50 |
| Reported calculation time | 0.197621 seconds |
| Date range | 2026-07-01 through 2026-07-31 |

The organizer's 16-component description excludes the 19 isolated nodes; all 35 observed components are preserved. Counts above are measured diagnostics, not constants in the implementation.

## Formal rules and scores

First matching rule wins:

1. **Coordinator:** `seed_ancestors >= 3`, `in_degree >= 3`, `out_degree >= 2`, `betweenness > 0`. Strength `0.6 + 0.4*min(seed_ancestors/10,1)`.
2. **Consolidator:** `in_degree >= 3` and (`out_degree <= 2` or `in_degree >= 2*out_degree`). Strength `0.5 + 0.5*min(in_degree/10,1)`.
3. **Distributor:** `out_degree >= 5` and `out_degree >= 2*in_degree`. Strength `0.5 + 0.5*min(out_degree/20,1)`.
4. **Transit:** non-seed, non-boundary, positive in/out degrees, and `0.8 <= pass_through <= 1.2`. Strength `max(0.5,1-abs(1-pass_through))`.
5. **Terminal:** non-seed, non-boundary, positive incoming amount, and `pass_through <= 0.2`. Strength `0.5+0.5*(1-pass_through/0.2)`.
6. **Peripheral:** no stronger rule matches; strength 0.2 expresses weak observed evidence, not innocence or guilt.

`pass_through = out_sum/in_sum` only for non-seeds with positive incoming amount; otherwise null. `boundary_censored = depth >= 4`. Seed ancestors count distinct other seed nodes reaching the node along directed paths, excluding self. Directed normalized unweighted betweenness samples at most 128 sources with seed 42. Monetary weights express interaction strength and are not used as shortest-path distances.

Role counts: terminal 1112, peripheral 816, coordinator 98, consolidator 90, distributor 77, transit 55. All evidence is numerical and 1–200 characters. Scores are bounded heuristic strengths, not probabilities. Warnings preserve seed incompleteness, depth censoring and observed outflow exceeding inflow. Observed retention is never described as a full account balance.

## Community and priority methods

The undirected projection adds opposite directed monetary weights: `w(u,v)=amount(u,v)+amount(v,u)`. Louvain uses positive weights, resolution 1 and seed 42. All nodes are added first; zero-weight-only and isolated nodes remain singleton communities. Cluster IDs follow ascending minimum numeric gid. Internal amounts are summed from original directed edges. Cluster hypotheses explicitly avoid claims of common control.

Priority is `0.30*L(in_sum+out_sum) + 0.25*L(in_degree+out_degree) + 0.20*L(seed_ancestors) + 0.25*B`, where `L(x)=log1p(x)/log1p(global maximum)` and `B=betweenness/max(betweenness)`. Zero maxima contribute zero. Scores round to six decimals; ties use ascending numeric gid. Top lists and cluster representatives use this same stable ordering. Exact methodology is also exposed as additive `report.methodology` metadata.

## Tests and commits

`.venv/bin/python -m unittest discover -s tests -p test_analytics.py -v`: **9 tests passed**, latest run 0.550 seconds. Coverage includes real fixture file traversal, reference/sum/count failures, duplicate nodes, nonfinite amounts, blank dates, all six rules and precedence, ratio boundaries, seed/boundary exclusion, weighted bridge partition, isolates, real-data completeness and identical CSV bytes across two runs.

- Task 1 RED: `cde7b7c`; GREEN: `a7e726f`.
- Task 2 RED: `d3714e7` (shared commit with integration tests); GREEN: `9e178c1`.
- Task 3 weighted-community failing test was observed before implementation; the parent snapshot included it in `9e178c1`. GREEN: `0cf784e`.
- Follow-up blank-date regression was observed failing and fixed; the parent serializes its commit with the final summary.

RED evidence was checked successfully by the GSD runtime for each planned task (`/tmp/analytics-red1.json`, `/tmp/analytics-red2.json`, `/tmp/analytics-red3.json`). Python unittest failures were converted into TAP records for the runtime's Node-oriented classifier; raw failure tracebacks remain in those records.

Metrics caveat: the parent exclusively serializes git operations in a shared branch. The measured 12 commits from `630bed8..878ff63` include interleaved UI/integration work and are not twelve analytics-only commits. No per-plan ledger existed before the parent's first commit, so the base is derived from the first analytics test's parent and this limitation is explicit. Diff-based tokens are `len(git diff baseline -- owned files)/4`, not model usage. Parent owns shared STATE/ROADMAP updates.

## Deviations from plan

**[Rule 1 — Bug] Reject blank parsed dates.** During final QA, pandas converted an empty date string to NaT even with `errors='raise'`. Added an explicit post-parse null check in `solution/pipeline.py` and a regression test. Previously the report could contain an invalid period string; the pipeline now fails clearly before writing outputs.

No new network, authentication or external-data surface was introduced. No unresolved stubs, skipped tests or unrun plan verification commands remain. Integration owns CLI/server, dependencies and README; formulas and measured output paths were sent directly to that executor.

## Self-Check: PASSED

All three owned source/test files and four output files exist. Listed completed task commit hashes were verified in git history. Nine tests pass and actual input/output invariants are covered. This summary completes plan 01-01 only; full phase verification remains with the orchestrator.
