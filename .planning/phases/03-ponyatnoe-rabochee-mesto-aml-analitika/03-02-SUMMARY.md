---
phase: 03-ponyatnoe-rabochee-mesto-aml-analitika
plan: 02
status: complete
subsystem: integration
requirements-completed: [SHIP-01, SHIP-02]
provides: [public-technical-docs, independent-ui-regression, live-development-preview]
key-files:
  modified: [README.md, docs/ARCHITECTURE.md, docs/DATA-CONTRACT.md, docs/METHODOLOGY.md, docs/DEMO.md, frontend/scripts/ui-smoke.mjs, frontend/vite.config.ts, .gitattributes]
completed: 2026-09-23
---

# Phase 3 Plan 2: Public documentation and independent acceptance

## Delivered

- Public README identifies the analyst decision, one-command launch, technologies, outputs, rules and thresholds, limitations, million-node scaling and verification steps. Architecture, methodology and data contract now describe actual modules and fields without relying on internal planning documents.
- Removed obsolete public development-plan navigation; retained GSD history internally. Git source archives exclude planning and agent instructions; dependency caches, environments and runtime locks remain ignored.
- Five-minute demo follows three actual nodes: priority coordinator, boundary consolidator and isolate. It uses current graph/inspector labels and explains hypotheses rather than guilt.
- Browser regression preserves the case checks while exercising the redesigned graph, all high-degree outgoing pages, arbitrary gid search, filters, cluster navigation, keyboard, source evidence, temporal details and downloads.
- Restored live preview after reboot: Vite at loopback port 8000 proxies `/data` to the local backend at 8765. Normal jury launch remains `python3 run.py`; preview process must be stopped before using the same port for that launcher.

## Validation evidence

- Public documentation audit and source-archive check: see `03-DOC-AUDIT.md`. All public local links resolved; technical assertions were compared with production implementation.
- Isolated source archive at 2259e0f with new Python/frontend dependency directories completed launcher `--check` in 16.51 seconds using package caches. This was not a clean operating-system VM. Subsequent font/UI changes passed production builds.
- Post-reboot independent Python suite: 26/26 tests passed. Final polished frontend: 29/29 tests and production build passed.
- Final real-data browser verifier: 24 checks passed; two full calculations took 0.618 and 0.567 seconds. Deterministic outputs and HTTP exports passed. Backend semantics were unchanged by the UI polish.
- Root and independent verifier inspected fresh desktop and mobile screenshots. Directed lanes show selected gid, roles and amounts; mobile has explicit incoming/outgoing flow and a direct inspector link. At 304 pixels the page has no horizontal overflow. The narrow search placeholder is truncated but its accessible label remains available.
- The actual live preview was opened in the in-app browser and displayed the report with 2,248 nodes, 3,119 edges and 4,840 transactions.

## Acceptance boundary

Implementation and integration tasks are complete. The user previously rejected graph readability, so final human usability acceptance remains open and is tracked separately by `03-VERIFICATION.md`. Passing tests and agent screenshot inspection are not represented as user approval. Phases 4–7 are being planned only; no additional feature implementation is included here.

## Commits

Public docs and archive cleanup: 585385f, c5b02fe. Final UI polish: 0cb3089 (already pushed). Parent serializes the remaining integration-summary/runtime commits and immediate pushes.

## Self-Check: PASSED

Documented outputs exist; current automated checks and screenshot observations are recorded with their practical limits.
