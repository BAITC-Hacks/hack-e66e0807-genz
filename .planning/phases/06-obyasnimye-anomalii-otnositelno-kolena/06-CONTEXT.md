# Phase 6 — Объяснимые аномалии относительно колена

## Decisions
- **D-01:** Compare each node to peers at the same observed depth, with explicit cohort size, metric, baseline and robust deviation; seed and depth-4 boundary censoring must be visible in each finding's interpretation.
- **D-02:** Use deterministic robust statistics, including small-cohort and zero-MAD fallbacks that avoid infinite scores and spurious certainty. Findings are review candidates, not probabilities of guilt.
- **D-03:** Detect observed near-threshold amount concentration only within transactions present in the input. The 5,000 KZT cutoff is left-censoring; never assert split transfers below the threshold.
- **D-04:** Add optional report evidence and a compact selected-node anomaly section with raw metric, peer baseline and caution. Keep the original three CSV schemas and values.

## Deferred Ideas
- Supervised risk probability and detection of unseen transactions below the export threshold.

## Execution hold
Planning only; no execution is authorized by this artifact.
