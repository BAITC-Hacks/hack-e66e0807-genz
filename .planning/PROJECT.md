# Граф денег — Money Graph

## What This Is

A local analytical pipeline and viewer for a bank AML analyst investigating a directed network of transfers originating from 81 known seed clients. It assigns an explainable structural role and investigation priority to every client, groups related nodes, and lets the analyst inspect money flows and locate a given `gid`. The initial release is a working hackathon solution built within one hour, using the supplied anonymized July 2026 dataset and starter code as inputs.

## Core Value

An analyst can identify which client to review first and explain why using observable graph and transaction evidence, without treating a structural hypothesis as proof of guilt.

## Requirements

### Validated

(None yet — the supplied starter writes empty output schemas but does not deliver the required analysis.)

### Active

- [ ] One documented local command reads the three supplied Parquet files and produces `nodes_roles.csv`, `clusters.csv`, `top_nodes.csv`, and a viewable network screen without manual intermediate steps; a full run takes under five minutes on the provided dataset.
- [ ] `nodes_roles.csv` includes exactly one row for each of the 2,248 nodes, including isolated seeds; every row has a valid role from the six-role dictionary, a 0–1 `role_score`, a cluster ID, a 0–1 `priority_score`, and nonempty numeric evidence no longer than 200 characters.
- [ ] Each role has a documented, deterministic rule or interpretable metric and threshold; the explanation for an arbitrary `gid` can be defended using its measured values within a minute.
- [ ] The classifier accounts for the four-hop truncation and incomplete observed inflow, especially for depth-4 nodes and seeds, so it does not equate an observed zero out-degree with proven settlement.
- [ ] Every node belongs to a cluster; `clusters.csv` reports the required size, seed count, internal KZT total, top gids, and a cautious hypothesis for each cluster.
- [ ] `top_nodes.csv` lists at least 20 nodes in descending investigation priority with an evidence-based `why` value.
- [ ] The viewer shows directed flows, role and cluster distinctions, and search by `gid` with the selected node's connections, suitable for a live five-minute demonstration.
- [ ] The repository README explains the single-command run, role rules and thresholds, output files, analytical limits, and how the approach would change near one million nodes; a simple data-to-decision diagram and demo walkthrough are available.
- [ ] Analyst-facing descriptions and submission explanations are written in Russian, while required CSV column names, role codes, `gid`, and other technical terms retain their canonical spelling.

### Out of Scope

- Temporal transit patterns, recurring routes and cycles, anomaly models, network removal simulations, and an AI assistant — optional case extensions that threaten the one-hour delivery of mandatory criteria.
- External enrichment, fabricated client attributes, and claims of criminal guilt — prohibited by the case and unsupported by anonymized graph data.
- Online ingestion, cloud infrastructure, paid services, and GPU training — the case requires a local batch workflow.

## Context

- Source brief: `FINANCE-CASE/case.md`; dataset description: `FINANCE-CASE/additional.md`; organizer starter: `FINANCE-CASE/starter/`. These local case materials are currently ignored by Git, so implementation and README must make the runnable solution self-contained while documenting how to supply the data.
- Intended user: an AML analyst at a second-tier bank. The analyst starts with 81 seed `gid`s from law enforcement, follows outgoing transfers up to four hops, reviews ranked candidates, and requests deeper investigation.
- Supplied data: 2,248 nodes, 3,119 directed aggregated edges, and 4,840 individual transactions from July 2026. Input files are `nodes.parquet`, `edges.parquet`, and `transactions.parquet`. The planning stage used the case documentation and did not inspect the Parquet contents.
- The graph contains only outgoing within-bank transfers above 5,000 KZT. At depth 4, 444 nodes have no recorded outgoing edge because traversal stops. Seed inflow from outside the sample is missing; observed `out_kzt / in_kzt` is therefore unreliable for them. Nineteen seeds have no edges and twelve appear only as recipients. There are 16 weakly connected components. No client attributes or role labels are available.
- Required roles: `consolidator`, `transit`, `distributor`, `terminal`, `coordinator`, and `peripheral`. Scores are interpretable heuristic strengths, not calibrated probabilities of criminal conduct.
- Case judging has strict gates: reproducible run, complete role output and explanations, clustering, a ranked list, and a directed viewer with `gid` lookup. Required delivery artifacts also include a README, solution diagram, and five-minute demo.

## Constraints

- **Timeline**: one hour for a working minimal solution — prioritize the five mandatory case functions and reproducibility.
- **Performance**: raw Parquet to required outputs within five minutes on an ordinary laptop — explicit case acceptance criterion.
- **Infrastructure**: local batch processing with no required network, cloud, GPU, or paid service — case constraints and reliable judging.
- **Data scope**: synthetic `gid` values and observed transactions only — no external enrichment or invented personal attributes.
- **Interpretation**: roles, clusters, and priorities are hypotheses for review — sampling bias and missing ground truth prevent definitive conclusions.
- **Compatibility**: preserve the fixed required CSV schemas and all 2,248 nodes — the judges check them mechanically.
- **Language**: write analyst-facing narrative text in Russian without mechanically translating technical terms — requested for the demo and deliverables.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Treat this repository as greenfield and skip codebase mapping | It contains organizer case materials and a starter, not an existing product | — Pending |
| Build from the supplied Python starter and keep a single local run | Existing loader, graph construction, and output schemas save scarce implementation time | — Pending |
| Prioritize all five mandatory case functions before optional analysis | Missing any one can fail the submission | — Pending |
| Use deterministic, documented role and priority rules | Arbitrary `gid`s must be explainable to an analyst and judge | — Pending |
| Handle depth-4 censoring and incomplete seed inflow explicitly | Naive terminal and pass-through labels would be misleading | — Pending |
| Use Russian for analyst-facing descriptions, retaining technical identifiers | Matches the requested presentation language without breaking fixed schemas | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `$gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `$gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-09-23 after initialization*
