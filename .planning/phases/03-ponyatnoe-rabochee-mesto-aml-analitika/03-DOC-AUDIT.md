# Public documentation and case constraints audit

## Findings and repair
- Current README had no direct `.planning` links, but `docs/HACKATHON-MVP-PLAN.md` contained obsolete development history. Moved it to `.planning/reference/`.
- DATA-CONTRACT mixed public schema with agent ownership and development-phase labels. Removed ownership and phase labels; documented input validation, static HTTP boundary, references, units, optional fields, compatibility and errors.
- Architecture was a brief diagram/module list. Expanded actual domain entities, module responsibilities, lifecycle, repeatability, static routes, error handling, deployment limits and scale bottlenecks.
- Added source-verified METHODOLOGY rationale/edge cases and public DESIGN navigation. Exact role rules remain available in README as required by the case.
- Tracked-file inventory found no virtualenv, dependency directory, Python cache, secrets file or runtime lock. Ignore local milestone.lock. Source archives exclude `.planning` and AGENTS through export-ignore; git history retains GSD evidence.

## Evidence
- Read implementation: solution/analytics.py, pipeline.py, temporal.py, server.py, run.py, frontend/src/contract.ts and package.json.
- All public relative documentation links resolve; no public planning/AGENTS links.
- `git diff --check` passes; `git archive HEAD` inventory confirms no `.planning/` or AGENTS in the source archive.
- Initial dependency installation requires internet. Runtime uses local assets and `/data/report.json`; there is no external LLM or enrichment.

## Case section 9
| Constraint | Evidence / limitation |
|---|---|
| No hardcoded correct gids | No 16–20 digit gid literals in production solution/frontend source; rankings computed from records |
| Explainable roles/top | Ordered classify_role rules and RULES; per-node evidence and per-rank why; thresholds and formula in public docs |
| No invented client attributes | Only organizer fields and derived metrics; no enrichment clients or personal identity fields |
| No cloud/GPU/paid dependency | Local Python, NetworkX and React static output |
| Hypotheses and privacy | Synthetic gids, warnings and explicit non-guilt wording in reports/docs |
| Runtime ≤300 seconds | Independent pre-redesign real CLI checks ~0.6 seconds each; backend unchanged by UI redesign |
| Local operation | Loopback server, local fonts/assets; package installation is a prerequisite requiring network/cache |
| Million-node discussion | README and ARCHITECTURE distinguish future compact graph/server pagination from current full in-memory snapshot |

Final redesigned UI passed 24 real-data browser checks and desktop/390px/304px screenshot inspection after reboot. This is agent-observed readability evidence; user usability acceptance remains open.

## Isolated launch evidence

From git archive at 2259e0f, a new temporary directory without .venv/node_modules ran `python3 run.py --data <organizer data> --check`: PASS in 16.51 seconds using package caches. It created 2248 nodes, 3119 edges and 4840 transactions; CLI timings 0.616/0.566 seconds; deterministic exports, HTTP and independent temporal checks passed. This is not a clean operating-system VM test. Later font-only dependency changes require production build and installed package validation.
