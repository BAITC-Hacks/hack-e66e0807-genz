# Phase 5 — Устойчивость сети при удалении узлов

## Decisions
- **D-01:** Remove the first N nodes in the existing deterministic `top_nodes` priority order, with N from 0 through a documented cap; do not recompute priorities between removals and do not mutate the original graph or exports.
- **D-02:** Include all nodes including isolates in baseline denominators. Publish both surviving-node and original-node fractions, baseline/after weak-component counts, largest-component sizes and isolate counts, and removed gid strings.
- **D-03:** Present a bounded N selector and before/after comparison with a clear statement that structural removal is a scenario, not proof of real disruption or criminal control.
- **D-04:** Retain three CSV schemas/values and optional additive JSON compatibility per `04-PLANNED-CONTRACT.md`; old reports remain usable without resilience data.

## Deferred Ideas
- Dynamic intervention optimization and inference about downstream cash balances.

## Execution hold
Planning only; no execution is authorized by this artifact.
