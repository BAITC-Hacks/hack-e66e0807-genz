# Requirements: Граф денег — Money Graph

**Defined:** 2026-09-23
**Core Value:** An analyst can identify which client to review first and explain why using observable graph and transaction evidence, without treating a structural hypothesis as proof of guilt.

## v1 Requirements

Requirements for the one-hour hackathon release. Every item below supports a stated case acceptance criterion or required submission artifact.

### Reproducible Pipeline

- [ ] **PIPE-01**: An analyst can run one documented local command against the supplied `edges.parquet`, `nodes.parquet`, and `transactions.parquet` to produce `nodes_roles.csv`, `clusters.csv`, `top_nodes.csv`, and an openable network viewer without manual intermediate steps.
- [ ] **PIPE-02**: The run checks that required input files and columns are present and reports a clear error if they are not; it includes all rows in `nodes.parquet`, even nodes with no observed edge.
- [ ] **PIPE-03**: A full run on the supplied 2,248-node, 3,119-edge, 4,840-transaction dataset completes within five minutes on an ordinary laptop.

### Node Roles and Evidence

- [ ] **ROLE-01**: An analyst can find exactly one `nodes_roles.csv` row per supplied `gid` (2,248 rows for the case data), with `role` chosen from `consolidator`, `transit`, `distributor`, `terminal`, `coordinator`, or `peripheral`.
- [ ] **ROLE-02**: Every node row has finite `role_score` and `priority_score` values in the inclusive range 0–1 and a nonmissing integer `cluster_id`.
- [ ] **ROLE-03**: Every node row has a nonempty, human-readable `evidence` value of at most 200 characters that cites numeric measurements supporting its role.
- [ ] **ROLE-04**: An analyst can explain the role of any selected `gid` using documented deterministic rules, measured graph features, and explicit thresholds for all six roles.
- [ ] **ROLE-05**: A depth-4 node with no observed outgoing edge is treated as censored by the four-hop extraction and is not labeled `terminal` solely because its observed out-degree is zero.
- [ ] **ROLE-06**: Seed-node rules do not treat the observed incoming amount or observed outflow/inflow ratio as a complete balance, because transfers into seeds from outside the sample are absent.

### Clusters

- [ ] **CLUS-01**: Every supplied node, including isolated seeds, has a `cluster_id` that appears exactly once in `clusters.csv`.
- [ ] **CLUS-02**: Each `clusters.csv` row has `cluster_id`, `n_nodes`, `n_seed`, `sum_kzt_internal`, and `top_gids`; cluster node counts sum to the number of input nodes and internal KZT uses only edges with both endpoints in that cluster.
- [ ] **CLUS-03**: Each cluster row has a nonempty, cautious `hypothesis` describing its observed structural purpose without asserting criminal guilt.

### Investigation Priority

- [ ] **PRIO-01**: Every node's 0–1 `priority_score` is derived from documented, interpretable graph and money-flow measurements that favor meaningful review candidates rather than hardcoded `gid`s.
- [ ] **PRIO-02**: `top_nodes.csv` contains at least 20 distinct `gid`s, with contiguous `rank` values beginning at 1, valid roles, and `priority_score` sorted from highest to lowest.
- [ ] **PRIO-03**: Each `top_nodes.csv` row has a nonempty `why` explanation grounded in measurements, so an analyst can state why the node is prioritized.

### Network Viewer

- [ ] **VIEW-01**: An analyst can open a local network view that shows transfer direction and visually distinguishes node roles and clusters.
- [ ] **VIEW-02**: An analyst can search for any supplied `gid`, including isolated nodes, and inspect that node's visible incoming and outgoing connections, role, priority, and explanation during the demo.
- [ ] **VIEW-03**: The viewer works locally without a required internet connection, cloud account, or paid service.

### Submission and Explanation

- [ ] **DOCS-01**: The repository README gives a reproducible setup and one-command run from a clean machine, identifies the required inputs, and describes each output file and viewer location.
- [ ] **DOCS-02**: The README states the formal rules and thresholds for every role and priority, distinguishes structural hypotheses from guilt, explains the four-hop and seed-inflow limits, and describes what would change near one million nodes.
- [ ] **DOCS-03**: The submission includes a one-page data → metrics → roles/priorities → viewer diagram and a five-minute demo walkthrough that covers a live run and evidence for two or three selected nodes.
- [ ] **DOCS-04**: Analyst-facing `evidence`, `why`, cluster `hypothesis`, viewer descriptions, README explanations, diagram labels, and demo text are in Russian; fixed CSV column names, role codes, `gid`, and established technical terms keep their canonical spelling.

## v2 Requirements

Deferred beyond the one-hour mandatory release.

### Additional Signals

- **TIME-01**: An analyst can review short-delay transit and synchronized activity derived from transaction dates.
- **ROUTE-01**: An analyst can inspect repeated paths and return cycles.
- **ANOM-01**: An analyst can review unusual amount or topology patterns relative to a node's hop depth.
- **RESI-01**: An analyst can estimate how network connectivity changes after removing top-ranked nodes.
- **GAPS-01**: An analyst can see which missing data would most improve a role hypothesis.
- **AI-01**: An analyst can ask natural-language questions and receive answers linked to specific graph nodes.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Hardcoded role or top-node lists by `gid` | Prohibited by the case and not reproducible on changed inputs. |
| External client enrichment or invented personal attributes | The anonymized case provides no such information and forbids unsupported enrichment. |
| Claims that a node is guilty or that funds definitively settled | The graph is censored and role labels have no ground truth. |
| Online streaming, cloud clusters, GPU training, or paid services | The case requires a local batch solution within five minutes. |

## Traceability

Roadmap creation will assign each v1 requirement to exactly one phase.

| Requirement | Phase | Status |
|-------------|-------|--------|
| PIPE-01 | Phase 2 | Pending |
| PIPE-02 | Phase 1 | Pending |
| PIPE-03 | Phase 2 | Pending |
| ROLE-01 | Phase 1 | Pending |
| ROLE-02 | Phase 1 | Pending |
| ROLE-03 | Phase 1 | Pending |
| ROLE-04 | Phase 1 | Pending |
| ROLE-05 | Phase 1 | Pending |
| ROLE-06 | Phase 1 | Pending |
| CLUS-01 | Phase 1 | Pending |
| CLUS-02 | Phase 1 | Pending |
| CLUS-03 | Phase 1 | Pending |
| PRIO-01 | Phase 1 | Pending |
| PRIO-02 | Phase 1 | Pending |
| PRIO-03 | Phase 1 | Pending |
| VIEW-01 | Phase 2 | Pending |
| VIEW-02 | Phase 2 | Pending |
| VIEW-03 | Phase 2 | Pending |
| DOCS-01 | Phase 2 | Pending |
| DOCS-02 | Phase 2 | Pending |
| DOCS-03 | Phase 2 | Pending |
| DOCS-04 | Phase 1 | Pending |

**Coverage:**
- v1 requirements: 22 total
- Mapped to phases: 22
- Unmapped: 0 ✓

---
*Requirements defined: 2026-09-23*
*Last updated: 2026-09-23 after roadmap mapping*
