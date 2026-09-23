---
phase: "2"
slug: "vremennye-patterny-i-uglublennaya-proverka"
status: approved
shadcn_initialized: true
preset: radix-nova
created: "2026-09-23"
---

# Phase 2 — UI Design Contract

Sources: `02-CONTEXT.md` decisions D-01–D-08, `REQUIREMENTS.md` TIME-01 and EXPL-01, `ROADMAP.md` Phase 2, `docs/DATA-CONTRACT.md`, the Phase 1 UI contract, and current `frontend/src/App.tsx` and `frontend/src/index.css`. This contract adds to the accepted Phase 1 UI. It does not change global gid search, graph interaction, priority ranking, CSV links, or the six role labels.

## Design System

| Property | Value |
|---|---|
| Tool | Installed official shadcn/ui local components |
| Preset | `frontend/components.json`: `radix-nova`, neutral base, CSS variables, subtle menu accent; current app CSS supplies final slate/teal palette |
| Component library | Radix via installed `radix-ui`; reuse local shadcn components |
| Icon library | `lucide-react`; 16px inline, 20px standalone |
| Font | Existing system-ui sans stack from frontend/src/index.css; no network font |
| Surfaces | Existing white cards on slate page, 8px radius, 1px slate border, no decorative gradient |

No new route, service, or large dashboard surface. Official shadcn Select installation is the only component/dependency extension. Preserve existing React/Vite app structure.

## Component Inventory

Enumerated by `find frontend/src/components/ui -maxdepth 1 -name '*.tsx' -printf '%f\n' | sort` — 7 components — `shadcn@4.21.0` (resolved with `node -p "require('./frontend/node_modules/shadcn/package.json').version"`) — 2026-09-23.

This is a non-exhaustive list of installed local components, not a closed allowlist. Check the local directory before using any additional component.

| Component | Import path | Phase 2 use |
|---|---|---|
| Alert | `@/components/ui/alert` | Existing load error; optional report issue |
| Badge | `@/components/ui/badge` | Role, seed, boundary and active filter labels |
| Button | `@/components/ui/button` | Filter controls, reset and gid navigation |
| Card | `@/components/ui/card` | Inspector sections and cluster overview |
| Input | `@/components/ui/input` | Existing exact gid search |
| Select | `@/components/ui/select` | Four exploration filters; installed official CLI4.21 after MCP lookup |
| Table | `@/components/ui/table` | Existing priority table; compact exploration list if tabular |

## Spacing Scale

| Token | Value | Usage |
|---|---|---|
| xs | 4px | Inline badge and icon gap |
| sm | 8px | Filter control gap and compact rows |
| md | 16px | Card content, filter groups and inspector sections |
| lg | 24px | Panel padding and desktop section gap |
| xl | 32px | Major workspace separation |
| 2xl | 48px | Empty/loading state padding |
| 3xl | 64px | Existing header height reference |

Controls and icon hit targets remain at least 44px high; existing search is 48px. Mobile page gutter is 16px. These are the only spacing exceptions.

## Typography

Exactly four sizes and two weights, inherited from Phase 1. Use tabular numerals, selectable full gids, and wrapping Russian explanation text.

| Role | Size | Weight | Line height |
|---|---|---|---|
| Helper, filter label, table | 14px | 400 or 600 | 1.5 |
| Body, value, subsection title | 16px | 400 or 600 | 1.5 |
| Section heading | 20px | 600 | 1.2 |
| Page heading / summary count | 28px | 600 | 1.2 |

## Color

| Role | Value | Usage |
|---|---|---|
| Dominant (60%) | `#FFFFFF` | Existing cards, graph and inspector |
| Secondary (30%) | `#F1F5F9` | Page, quiet rows and table headers |
| Accent (10% maximum) | `#0F766E` | Existing primary search, active selection border, focus ring and selected node halo; Phase 2 selected filter state and active cluster row only |
| Text | `#0F172A` | Primary text |
| Muted text | `#475569` | Labels, caveats and secondary descriptions |
| Border | `#CBD5E1` | Panel boundaries |
| Destructive | `#B91C1C` | Reserved; no destructive Phase 2 actions |

Do not color temporal counts or risk hypotheses red/green. Date and count evidence is text, not a severity grade. Existing role and cluster graph colors remain as documented in Phase 1; every color has a visible text label.

## Layout and Interaction Contract

Keep the existing order of summary, exact gid search, graph and inspector, priority table, and downloads. Insert a compact **«Исследование выборки»** section after the search and before the graph/inspector workspace. Its first row is labeled filters: **Роль**, **Кластер**, **Seed**, **Граница выгрузки**. Use official shadcn Select controls with visible labels; default each to **Все**. Role uses the existing six Russian role translations. Seed choices are **Все / Только seed / Без seed**; boundary choices are **Все / Граничные / Неграничные**. Cluster options are actual report cluster IDs in deterministic numeric order. Filters combine with AND and update only the named **«Результаты исследования»** list and its count. Never filter the report used by exact gid search, graph selected-neighborhood display, or priority ranking. Search always finds arbitrary gid including a filtered-out result or isolate. Show **«Сбросить фильтры»** whenever any filter differs from default; reset restores all four defaults. A filter change does not silently replace an already selected node.

The exploration list contains one row per matching node, sorted by priority descending then gid numeric ascending as a stable tie-breaker. Show full gid, translated role, cluster ID, priority score to two decimals, and seed/boundary badges when true. State **«Показано X из Y узлов»** near the list; Y is full report nodes count. At typical dataset size, keep this list to 20 visible rows with an explicit **«Показать ещё»** step of 20, preserving active filters and order. Do not create hundreds of focus stops up front. Each result is a real button named **«Открыть узел {gid}»**; selecting it updates the existing inspector and graph. For zero matches show the documented empty copy and reset control. One match uses **«1 узел»**; other counts use correct Russian plural forms. Long gid and explanation text wrap without truncating identifiers. A list/table region may scroll within its own named container on narrow screens; the page itself has no horizontal overflow.

Place a compact **«Обзор кластеров»** card adjacent to or immediately below the exploration list, before the graph on narrow screens. One row per actual cluster shows ID, n_nodes, n_seed and sum_kzt_internal in ₸, plus the supplied hypothesis; no fabricated metrics. A cluster row button **«Исследовать кластер {id}»** sets the cluster filter and moves focus to the results heading; it does not change the current selected node. The existing inspector's cluster member buttons still open individual nodes. If a cluster has no members in a partial/old report, show its supplied summary without inventing members. If there are no clusters, show **«Кластеры не представлены в этой выгрузке.»**. Use compact rows with a bounded scroll region for many clusters rather than expanding the whole page indefinitely.

Inside the existing node inspector, after the metric grid and before neighbor lists, add **«Временные признаки»** only when the optional `node.temporal` object exists and is valid under the shared additive JSON contract. Show `incoming_tx_count` and `outgoing_tx_count` as factual totals. Label `outgoing_after_1d_count` **«Через 1 день после поступления»** and `outgoing_after_1_or_2d_count` **«Через 1–2 дня после поступления»**; the accompanying description identifies these as counts of outgoing transactions by calendar-date difference. Explain that each qualifying outgoing transaction is counted once in each applicable measure; the second measure is cumulative and includes the 1-day count, so the two values must never be visually summed. For each supplied `after_1_or_2d_examples` pair show actual incoming and outgoing dates, without inventing amounts or claiming transfer of identical funds. State **«Совпадение дат не доказывает, что переводились те же деньги.»** visibly whenever the temporal block appears. Show `peak_day` only when non-null, with its date, `count`, `share` and `baseline_daily_count`, all labeled as observed calendar-day activity; explain the documented peak rule in plain language without claiming a statistical anomaly or fraud probability. Never suggest within-day ordering or reverse ordering. A valid zero count reads **«0 наблюдений»**; unknown/missing field reads **«Нет данных»**, never zero. If there is no optional temporal object in a Phase 1 report, omit the whole temporal block and keep all Phase 1 card fields functioning.

Add **«Какие данные запросить дальше»** after temporal evidence and before neighbors when `node.next_data_requests` supplies one or more valid request strings. Render actionable Russian bullets in backend order, with the triggering limitation in the same line or nearby. Supported contexts are incomplete incoming data for seed, depth=4 boundary censoring, missing external inflows, and temporal uncertainty. Treat the strings as plain text, not HTML. Do not invent a generic request when metadata is absent. Existing seed/boundary warnings remain visible. If the additive field is absent in an old report, omit this section. If present but empty, show **«Дополнительный запрос данных не определён для этого узла.»**.

At ≥1200px retain graph plus 360px inspector columns and 24px gap. At 768–1199px stack inspector below graph. At 390px the filter controls become one full-width control per row, exploration/cluster cards stack, 44px buttons remain tappable, gid and hypotheses wrap, and no page horizontal scroll appears. The graph remains 400px high below 768px. New sections must not push the existing search below a large overview; exploration panels may use bounded internal scrolling.

All filters have visible labels and Radix Select keyboard behavior. Tab reaches filters, reset, result buttons and cluster buttons in reading order. Enter/Space activates buttons. Active filter values and result count are visible text, with a polite live region for count changes; avoid announcing the entire list. On cluster selection, focus lands on results heading (`tabIndex=-1`) and the active cluster value is explicit. Focus ring remains 2px teal with offset. Reduced-motion preference disables animated scroll/transitions. Do not rely on hover or graph color to convey meaning.

## Data Contract

The temporal object also includes incoming_profile and synchronous_incoming as defined in docs/DATA-CONTRACT.md; the inspector must render their observed values and boundary caveat.

The only data source remains `/data/report.json` with `schema_version: '1.0'`; required CSV schemas are unchanged. Additive fields are `node.temporal?` with `incoming_tx_count`, `outgoing_tx_count`, `outgoing_after_1d_count`, `outgoing_after_1_or_2d_count`, `after_1_or_2d_examples: {incoming_date, outgoing_date}[]`, and nullable `peak_day: {date, count, share, baseline_daily_count}`; and `node.next_data_requests?: string[]`. Follow the authoritative updated `docs/DATA-CONTRACT.md` for exact validation. UI must parse unknown/missing optional fields safely, preserve string gid exactly, reject malformed optional values without crashing the whole report, and never render missing evidence as a measured zero. The existing required fields remain mandatory. All counts, dates, requests and cluster metrics come from actual report data. No new runtime request, API, or route.

## Copywriting Contract

| Element | Exact copy |
|---|---|
| Existing primary CTA | Найти узел |
| Exploration heading | Исследование выборки |
| Results heading | Результаты исследования |
| Reset CTA | Сбросить фильтры |
| More CTA | Показать ещё |
| Filtered empty heading | По этим фильтрам узлы не найдены |
| Filtered empty body | Измените условия или сбросьте фильтры, чтобы увидеть всю выборку. |
| Cluster empty | Кластеры не представлены в этой выгрузке. |
| Temporal heading | Временные признаки |
| Temporal caveat | Совпадение дат не доказывает, что переводились те же деньги. |
| Temporal unavailable value | Нет данных |
| Request heading | Какие данные запросить дальше |
| Optional empty requests | Дополнительный запрос данных не определён для этого узла. |
| Load error | Не удалось загрузить результаты анализа. Проверьте, что локальный расчёт завершён, и повторите загрузку. |
| Malformed optional data | Часть дополнительных данных недоступна. Основные сведения об узле сохранены. |
| Destructive confirmation | Не применяется: разрушительных действий нет |

## UI Considerations

Applicable state considerations resolved: 8 covered, 0 backstop, 0 unresolved.

| Category | Element(s) | Status | Resolution / Reason |
|---|---|---|---|
| Empty | Exploration list, cluster overview, optional card sections | ✅ covered | Filter empty and cluster empty use copy above; absent optional fields omit their sections without losing Phase 1 data. |
| Loading | Exploration and cluster panels | ✅ covered | Existing report-level loading state covers both because they derive from the single report fetch. |
| Error | Report and optional sections | ✅ covered | Existing retry alert handles fetch/required schema failure; malformed optional values show the nonfatal message and Phase 1 details. |
| Populated | Results, cluster rows, temporal evidence | ✅ covered | Rows and evidence fields are specified above, with actions to select nodes. |
| Partial | Old reports and incomplete temporal objects | ✅ covered | Absent object hides section; missing measures say «Нет данных» where a partial object is displayed. |
| Overflow | Results, clusters, long gids and hypotheses | ✅ covered | Results page by 20; cluster list bounded; text wraps; narrow page has no horizontal overflow. |
| Zero / one / many | Exploration list and clusters | ✅ covered | Empty copy, singular/plural count, stable many-row controls and internal scroll. |
| Long text | Requests, hypothesis, gid, buttons | ✅ covered | Wrap content, keep gid intact/selectable, buttons grow vertically above 44px. |

## Registry Safety

| Registry | Blocks used | Safety gate |
|---|---|---|
| shadcn official installed local | Button, Card, Input, Table, Alert, Badge | Existing local components inspected 2026-09-23; no new registry install |
| Third-party | None | Not applicable |

## Checker Sign-Off

- [x] Dimension 1 Copywriting: PASS
- [x] Dimension 2 Visuals: PASS
- [x] Dimension 3 Color: PASS
- [x] Dimension 4 Typography: PASS
- [x] Dimension 5 Spacing: PASS
- [x] Dimension 6 Registry Safety: PASS
- [x] Dimension 7 Inventory Provenance: PASS

**Approval:** independent gsd-ui-checker approved; typography description corrected to actual system sans after nonblocking flag.

## User clarification — before execution

Add observed incoming profile to temporal card: distinct_payers,active_days,total_kzt,median_kzt from temporal.incoming_profile. Add temporal.synchronous_incoming when present: date,distinct_payers,tx_count,sum_kzt; threshold>=3 distinct payers on a calendar date. Explain that this is synchronous observation without intraday sequence or identity of funds. On boundary-censored nodes keep the depth4 caveat adjacent to this profile, never call them proven terminal recipients. Shared contract defines precise tie selection.

Filters exclusively use installed official shadcn Select/SelectTrigger/SelectValue/SelectContent/SelectItem. Official shadcn4.21 MCP get_add_command_for_items returned npx shadcn@latest add @shadcn/select on2026-09-23; root/implementer installs using pinned available4.21 CLI and verifies inventory. AI assistant remains deferred by explicit user choice.
