---
phase: 01-polnyy-lokalnyy-mvp
reviewed: 2026-09-23T11:03:13Z
depth: deep
files_reviewed: 8
files_reviewed_list:
  - solution/analytics.py
  - solution/pipeline.py
  - solution/server.py
  - solution/__main__.py
  - tests/test_analytics.py
  - tests/test_contracts.py
  - scripts/verify_delivery.py
  - README.md
findings:
  critical: 1
  warning: 0
  info: 0
  total: 1
status: issues_found
---

# Phase 01: Backend Code Review

## Summary

The pipeline preserves large `gid` values as strings in JSON, retains isolates, guards seed and depth-4 terminal inference, and writes the contracted CSV schemas. The focused analytics and export tests pass. Three HTTP tests could not run in this sandbox because socket creation is denied before application code executes.

## Narrative Findings (AI reviewer)

### CR-01 — BLOCKER: Cluster `hypothesis` does not describe a cluster's possible purpose

**File:** `solution/analytics.py:122`

**Issue:** Every cluster receives the same template: its size, seed count, and the disclaimer that monetary links do not prove common control. The real `output/clusters.csv` shows this for large, multi-seed, seed-free, and tiny clusters alike. The case requires `hypothesis` to be a hypothesis about the cluster's *purpose*; size and seed count are already separate columns. As written, this mandatory output field provides no purpose to evaluate, and `scripts/verify_delivery.py:128` checks only that it is nonempty, so acceptance tests cannot catch the gap.

**Fix:** Derive a cautious, cluster-specific statement from observed structure: for example, classify whether its members show predominantly consolidation, distribution, or transit; cite the counts or flow metrics supporting that label. For an isolate or inconclusive cluster, state that its purpose is undetermined from observed transfers. Add a test that distinguishes these cases and rejects a generic size/seed restatement.

---

_Reviewer: gsd-code-reviewer_
_Depth: deep_
