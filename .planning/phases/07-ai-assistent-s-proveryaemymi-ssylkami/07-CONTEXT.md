# Phase 7 — AI-ассистент с проверяемыми ссылками

## Decisions
- **D-01:** Deliver a real configured LLM-backed assistant for natural-language questions; deterministic rules alone do not count as AI. The feature is disabled by default, so baseline local analysis/UI remains offline and free with no GPU or paid-provider requirement.
- **D-02:** Use a configurable local CPU inference endpoint by default with optional compatible remote provider configuration. Store endpoint/model/credential only in local environment; never commit secrets, and show unavailable/configuration state honestly.
- **D-03:** The model can call only server-owned, bounded, read-only query tools over the validated report snapshot. No arbitrary SQL, Python, filesystem, network access, or direct raw parquet exposure. Validate requested gids, limits and output references.
- **D-04:** Every factual answer cites existing gid strings and, when relevant, directed edge/metric/date evidence. A citation validator rejects unsupported claims or yields an explicit inability to answer. Prompt injection in report text or user questions cannot alter tool policy.
- **D-05:** UI uses a compact, clearly optional assistant panel integrated with selected gid. It shows citations that navigate to existing cards and distinguishes observation, heuristic inference and missing information.
- **D-06:** Preserve existing report/CSV contracts and all five must-haves. AI failure, timeout or absent model must not block analysis, exports or the ordinary UI.

## Deferred Ideas
- Autonomous external actions, case decisions, user data upload by default and claim of guilt probability.

## Execution hold
The earlier user deferral applied to AI implementation. The latest request authorizes this plan only; do not execute without a separate user request, irrespective of `auto_advance`.
