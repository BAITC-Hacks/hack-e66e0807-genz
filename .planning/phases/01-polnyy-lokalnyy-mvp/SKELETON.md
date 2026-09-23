# Walking Skeleton — Граф денег

Phase 1, 2026-09-23. Planned capability: read real parquet, calculate explained hypotheses, write CSV/JSON, serve the bundled interface locally, search a real gid and inspect directed links. This document records architecture; completion requires the checks in 01-03.

| Decision | Choice | Rationale |
|---|---|---|
| UI | React/Vite, shadcn/ui, Russian labels, local bundled assets | Locked interface choice and local reproducibility |
| Analytics | Python batch, existing pandas/networkx/parquet stack | Real provided inputs and transparent numerical rules |
| Persistence | Real parquet reads and CSV/JSON file writes | Locked no-DB/no-API architecture; files are the persistent boundary |
| Integration | docs/DATA-CONTRACT.md version 1.0, browser IDs strings | Independent concurrent analytics/UI development |
| Deployment | Loopback Python static server, frontend/dist plus /data | One local machine, no cloud/CDN dependency |
| Auth | None | Local anonymized dataset, no hosted service |
| Ownership | Analytics: solution/analytics.py,pipeline.py; UI: frontend/; integration: CLI/server/tests/docs | Avoid concurrent file conflicts |

## Waves and dependencies

Contract documentation is already established. Wave 1: 01-01 analytics and 01-02 UI run concurrently with zero file overlap. Each leads with a working file-to-result or fetch-to-card tracer. UI uses an explicitly synthetic test fixture until real output exists. Wave 2: 01-03 consumes both outputs, proves the whole local flow and documentation. The orchestrator may provision audited dependencies and CLI glue alongside wave 1, without changing lane ownership.

## Source coverage audit

CONTEXT has six unnumbered locked bullets. For traceability only, D-01…D-06 below refer to those bullets in order; their source text is unchanged. Research is disabled and no RESEARCH.md exists at planning time. Library-specific implementation must consult Context7; package provisioning remains orchestrator-owned and requires a Package Legitimacy Audit before installation.

| Source | ID | Item | Plan | Status |
|---|---|---|---|---|
| GOAL | Phase 1 | Explain who to inspect, search every gid, complete five must-haves | 01-01,01-02,01-03 | COVERED |
| REQ | DATA-01 | One real batch under 300 seconds | 01-03 | COVERED |
| REQ | DATA-02 | Complete gid and input consistency | 01-01,01-03 | COVERED |
| REQ | DATA-03 | Shared versioned contract/string browser IDs | 01-01,01-02,01-03 | COVERED |
| REQ | ROLE-01 | Six roles, scores, evidence | 01-01 | COVERED |
| REQ | ROLE-02 | Formal thresholds and arbitrary-gid explanations | 01-01,01-02,01-03 | COVERED |
| REQ | ROLE-03 | Censoring, seeds and cautious hypotheses | 01-01,01-02 | COVERED |
| REQ | CLUS-01 | Complete communities and exact CSV | 01-01 | COVERED |
| REQ | RANK-01 | At least 20 ranked unique nodes | 01-01 | COVERED |
| REQ | UI-01 | Directed graph, roles, communities, legend | 01-02 | COVERED |
| REQ | UI-02 | Every-gid search and linked priorities | 01-02 | COVERED |
| REQ | UI-03 | CSV downloads and all states | 01-02,01-03 | COVERED |
| REQ | UI-04 | Responsive keyboard-accessible offline build | 01-02,01-03 | COVERED |
| REQ | SHIP-01 | README, formulas, caveats and scale | 01-03 | COVERED |
| REQ | SHIP-02 | Diagram and five-minute demo | 01-03 | COVERED |
| REQ | TEST-01 | Analytical/contract/repeat/browser/real-run checks | 01-01,01-02,01-03 | COVERED |
| CONTEXT | D-01 | Python plus React/Vite shadcn, static data, no API/DB | All | COVERED |
| CONTEXT | D-02 | Existing common contract before parallel lanes | 01-01,01-02 | COVERED |
| CONTEXT | D-03 | All gid, seed/boundary limits, hypotheses | 01-01,01-02 | COVERED |
| CONTEXT | D-04 | Verify every requirement, fix and retest | 01-03 | COVERED |
| CONTEXT | D-05 | Separate file ownership, shared CLI/docs orchestrator | All | COVERED |
| CONTEXT | D-06 | Complete mandatory milestone before improvements | 01-03 | COVERED |
| RESEARCH | — | No research artifact; existing starter and contract inspected | All | N/A |

Discovery: existing local starter patterns and contract inspected; no prior phase history or knowledge graph exists. Estimates use calibration factor 1, zero samples, confidence low. No deferred LLM/cloud/auth/streaming/complex ML or Phase-2 temporal feature enters this phase.

## Acceptance checklist

- [ ] Real file read/write and exact output contracts pass.
- [ ] Both wave-1 tracers expand to the complete required behaviors.
- [ ] Full batch runs twice below 300 seconds with reproducible CSVs.
- [ ] Real selected gid travels from generated output to browser graph/card.
- [ ] Local documented run, downloads, diagram and demo verified.

Phase 2 adds temporal hypotheses and suggested missing-data requests after a green Phase-1 verifier; the shared contract permits additive fields.
