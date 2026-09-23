# Roadmap: Граф денег — Money Graph

## Overview

Deliver a one-hour, judge-ready AML investigation aid in two vertical slices. First, turn the supplied Parquet files into complete, explainable roles, clusters, and ranked CSVs. Then add offline visual inspection and prove that a clean local run reproduces all required outputs within the case limit. Every analyst-facing description uses Russian while technical identifiers retain their specified names.

## Phases

**Phase Numbering:** Integer phases are planned milestone work; decimal phases are reserved for urgent insertions.

- [ ] **Phase 1: Explainable Investigation Results** - An analyst can use complete CSV outputs to identify and defend priority clients.
- [ ] **Phase 2: Visual Review and Reproducible Submission** - An analyst can inspect the directed network and judges can run and explain the full solution.

## Phase Details

### Phase 1: Explainable Investigation Results
**Goal:** An analyst can derive a complete, defensible investigation shortlist from the supplied transaction network.
**Mode:** mvp
**Depends on:** Nothing (first phase)
**Requirements:** PIPE-02, ROLE-01, ROLE-02, ROLE-03, ROLE-04, ROLE-05, ROLE-06, CLUS-01, CLUS-02, CLUS-03, PRIO-01, PRIO-02, PRIO-03, DOCS-04
**Success Criteria** (what must be TRUE):
  1. A run over the supplied input files writes three CSVs with one valid, fully populated role row for each of the 2,248 nodes, including isolated seeds.
  2. For any selected `gid`, an analyst can read a Russian explanation with numeric measurements for its role and priority; the rules visibly account for depth-4 truncation and missing seed inflow.
  3. Every node maps to one reported cluster, and cluster totals and cautious hypotheses can be checked against the directed input graph.
  4. `top_nodes.csv` contains at least 20 distinct, correctly ranked candidates with defensible Russian reasons.
**Plans:** TBD

### Phase 2: Visual Review and Reproducible Submission
**Goal:** An analyst can inspect directed flows around any client, and judges can reproduce and explain the complete local solution.
**Mode:** mvp
**Depends on:** Phase 1
**Requirements:** PIPE-01, PIPE-03, VIEW-01, VIEW-02, VIEW-03, DOCS-01, DOCS-02, DOCS-03
**Success Criteria** (what must be TRUE):
  1. One documented command produces all three required CSVs and an openable offline viewer from raw Parquet in under five minutes on the supplied dataset.
  2. An analyst can search any `gid`, including an isolated node, and inspect incoming and outgoing directed links, role, cluster, priority, and Russian explanation.
  3. A judge can follow the Russian README on a clean machine to install dependencies, supply the data, run the solution, and understand every role threshold, limitation, and the proposed million-node scaling path.
  4. A data-to-decision diagram and five-minute demo walkthrough let the team explain two or three selected nodes using measured evidence and cautious language.
**UI hint:** yes
**Plans:** TBD

## Progress

**Execution Order:** Phase 1 → Phase 2

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Explainable Investigation Results | 0/TBD | Not started | - |
| 2. Visual Review and Reproducible Submission | 0/TBD | Not started | - |
