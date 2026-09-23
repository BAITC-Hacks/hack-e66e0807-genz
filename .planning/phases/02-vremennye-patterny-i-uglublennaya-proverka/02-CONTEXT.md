# Phase2: Временные паттерны и углублённая проверка — Context

Gathered:2026-09-23. Status:Ready for planning. Discuss mode:auto, explicitly authorized autonomous work.

<domain>
TIME-01 and EXPL-01 only: temporal evidence, next-data requests, node/cluster exploration. Phase1 is independently accepted5/5; preserve it. Deadline11:47UTC.
</domain>
<decisions>
- **D-01:** Keep fixed CSV schemas and schema_version1.0; add optional JSON fields. Publish exact shared field contract before parallel backend/UI execution.
- **D-02:** Calendar dates have no intraday order. Count an outgoing transaction once if an incoming transaction exists1day before, and separately within1–2days before. Exclude same-day ordering claims and reverse order. Do not claim tracing identical funds; report observed date examples and quantities.
- **D-03:** Daily activity peak uses explicit counts, share, date and a documented reproducible threshold. No opaque fraud score or change to existing roles/priority during this phase.
- **D-04:** Next-data requests derive from seed incompleteness, depth4 censoring, missing external inputs and temporal uncertainty. Russian concise actionable explanation, not generic advice.
- **D-05:** Add compact role/cluster/seed/boundary filters and a cluster overview with counts, internal sum, hypothesis and member navigation. Filters apply to clearly labeled exploration results, arbitrary-gid search remains global. Show reset and empty state; selecting a result opens current card/graph.
- **D-06:** Reuse current clean shadcn design; temporal block in card, no new routes/services or giant dashboard redesign. Optional fields absent in1.0 reports must degrade gracefully.
- **D-07:** Tests cover temporal1day/2day boundaries, same-day/reverse dates, double counting, isolates and real data; UI filters/card/old-report compatibility and browser smoke. Independent verifier and repair loop before phase completion.
- **D-08:** All implementation questions resolved autonomously within existing preferences; no further user decisions needed. Parent serializes frequent commits and immediate pushes.
- **D-09:** User clarification: show incoming profile (distinct payers, active dates, total/median amounts) to explain depth4 hypotheses, never assert true terminal status from censored outputs. Add synchronous incoming: >=3 distinct payers in one calendar day, with date/count/amount evidence.
- **D-10:** Standard controls must use real shadcn components; four new filters use official shadcn Select, not native HTML select. Graph remains custom SVG, as no standard network graph primitive exists. Narrow dependency exception for official Select installation.
- **D-11:** User explicitly chose to finish analytics and visual now; AI assistant remains deferred, no false AI claim.
</decisions>
<canonical_refs>
- FINANCE-CASE/case.md — original requirements, temporal ideas and limits.
- .planning/ROADMAP.md — phase2 success criteria.
- .planning/REQUIREMENTS.md — TIME-01 and EXPL-01.
- docs/DATA-CONTRACT.md — authoritative shared data boundary.
- .planning/phases/01-polnyy-lokalnyy-mvp/01-UI-SPEC.md — design system inherited unchanged.
</canonical_refs>
<code_context>
solution.pipeline.run_pipeline already loads validated timestamped transactions; attach optional metadata after analytics. frontend Inspector in App.tsx, parseReport in contract.ts, Graph reusable. shadcn Card/Button/Input/Table installed. Existing browser smoke11checks and independent20Python tests protect Phase1.
</code_context>
<deferred>
AI assistant, full million-node runtime, new external services, account enrichment. No additional scope.
</deferred>
