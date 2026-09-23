# Independent plan review: optional case enhancements

**Result: PASS — 0 blockers, 0 warnings.** Reviewed the frozen nine plans across Phases 4–7 on 2026-09-23. This is a pre-execution judgment; no feature was implemented or run as part of this review. Execution remains on hold until a separate user request.

| Phase | Plans | Roadmap requirements | Case option delivered by plan |
|---|---:|---|---|
| 4 | 2 | ROUTE-01–03 | Bounded A→B→C routes and 2–3-node returns, distinct-day recurrence, directed leg evidence and date caveats |
| 5 | 2 | RES-01–03 | Fixed-priority top-N removal with surviving and original denominators, isolates and hypothetical UI scenario |
| 6 | 2 | ANOM-01–03 | Same-depth robust comparisons and observed 5,000–10,000 KZT concentration with small-cohort, zero-MAD and censoring rules |
| 7 | 3 | AI-01–04 | Optional real LLM, bounded server-owned tools, checked citations/claims, five-source question, live-model gate and offline baseline |

The other four optional case features are existing Phase 1–2 work: depth-4 boundary handling, temporal patterns, generated node cards and requests for missing data. Every phase's independent regression task explicitly includes them, the five mandatory case functions, unchanged three CSV schemas/values, exact string JSON gids and a measured batch below 300 seconds.

All nine `verify.plan-structure` results are valid with zero errors/warnings. Plans have 2–3 tasks and 4–7 listed files each; declared dependencies are acyclic and waves match the edges. The `check decision-coverage-plan` gate passes Phase 4 **5/5**, Phase 5 **4/4**, Phase 6 **4/4**, Phase 7 **6/6**. Scope estimates are 12,000–22,000 tokens against a 100,000-token smart-zone budget; confidence is low because there are no project calibration samples. No project skill directory, phase RESEARCH/PATTERNS/REVIEWS, or responsibility map was present; those conditional checks do not apply.

The orchestrator's UI plan gate reported no blockers in any of the four phases. Its post-plan gap analysis passed Phase 4 **8/8**, Phase 5 **7/7**, Phase 6 **7/7**, and Phase 7 **10/10** (13 roadmap requirements and 19 context decisions in total).

The review required revisions before passing: route plans now distinguish strict later-day tuples from same-day ambiguity and count recurrence by distinct first-leg days under pre-materialization caps; the AI contract now renders only validated structured claims, distinguishes path/cycle citations, and resolves exact resilience scenarios. A bounded common-recipient tool and test cover the case's five-source question. Phase 7 separates controlled mock evaluations from a **required live local CPU-model smoke**; absence of the configured model leaves that phase unverified while the ordinary offline product still runs. Tracer UI tasks have behavioral assertions, and each later plan carries source-backed or independent verification. The frozen planned contract is the common pre-code interface; each first plan synchronizes its portion into `docs/DATA-CONTRACT.md` before later independent work.

Final citation delta: the five-source `get_common_recipients` count and sum are derived values, so the assistant no longer pretends they are report scalar fields. The model may select only a recipient from the bounded tool result. The server recomputes the aggregate from the complete matching directed report-edge set for the validated source gids, renders the count and `math.fsum` amount itself, and attaches the recipient node plus every contributing edge-sum citation. The AI-SPEC and 07-02/07-03 tasks require rejection tests for model-supplied aggregates, omitted or extra edges, and an unknown recipient. This closes the provenance gap in the canonical five-source answer without changing the PASS verdict.

The live model is an execution-time precondition, not evidence of a current run. No provider, package or production implementation was installed during this review.
