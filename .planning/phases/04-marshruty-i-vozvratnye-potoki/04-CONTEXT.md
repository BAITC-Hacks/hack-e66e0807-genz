# Phase 4 — Маршруты и возвратные потоки

## Decisions
- **D-01:** Keep all three case CSV schemas and values unchanged; extend `report.json` only with optional version-1.0 sections and string gid references. The planned shared contract is `04-PLANNED-CONTRACT.md` and must be fixed before parallel backend/frontend execution.
- **D-02:** Separate directed topology (candidate path/cycle in aggregate edges) from observed ordered transaction dates. Date order is calendar resolution and cannot establish that the same money traversed the path.
- **D-03:** Enumerate only bounded, deduplicated length-two A→B→C routes and simple return cycles of length two or three, including reciprocal edges; deterministic gid ordering, pre-materialization work budget and explicit count/cap/truncation metadata prevent unbounded search. “Repeated” requires strict ordered observations on at least two distinct first-leg calendar days.
- **D-04:** Preserve isolates and boundary/seed caveats. Repetition means multiple observed transaction rows on each directed leg, not repeated movement of a matched amount. Never infer control, guilt or below-cutoff transfers.
- **D-05:** Show a selected-node routes section with source/target, each leg's sum/count and date evidence, linked gid navigation, method and limitations. Keep the first-screen priority→graph→evidence hierarchy from Phase 3.

## Deferred Ideas
- Transaction identity tracing and causality, which the organizer data cannot establish.

## Execution hold
Planning only. Phase 4 does not start until the user separately requests execution, regardless of `auto_advance` configuration.
