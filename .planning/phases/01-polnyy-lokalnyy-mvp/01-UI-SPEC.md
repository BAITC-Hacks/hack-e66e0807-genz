---
phase: "1"
slug: "explainable-aml-mvp"
status: draft
shadcn_initialized: true
preset: radix-nova-b2fA
created: "2026-09-23"
---

# Phase 1 — UI Design Contract

Source decisions: PROJECT.md, REQUIREMENTS.md UI-01–04, ROLE-01–03, FINANCE-CASE/case.md and docs/DATA-CONTRACT.md. Autonomous defaults fill visual details. This is the canonical phase contract at `.planning/phases/01-polnyy-lokalnyy-mvp/01-UI-SPEC.md`.

## Design System

| Property | Value |
|---|---|
| Tool | shadcn/ui; initialization owned by orchestrator |
| Preset | Slate light theme, CSS variables; CLI preset not yet detected |
| Component library | Official shadcn components; preserve primitive choice produced by CLI |
| Icon library | lucide-react, locally bundled; 16px inline, 20px standalone |
| Font | system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; no remote fonts |
| Surfaces | White panels, slate page; 8px corners; subtle 1px border; no decorative gradients |

No existing frontend, components.json, styles or project-local skills were found during initial inspection. The user already selected shadcn and autonomous setup, so initialization needs no repeated question. The orchestrator subsequently verified official shadcn 4.21.0 MCP over local stdio using `/tmp/shadcn_mcp_probe.py`; `tools/list` and `get_add_command_for_items` succeeded. Semantic theme pairing follows current [official shadcn theming documentation](https://github.com/shadcn-ui/ui/blob/main/apps/v4/content/docs/(root)/theming.mdx), retrieved through Context7 `/shadcn-ui/ui` on 2026-09-23.

## Component Inventory

Could not enumerate: no components.json or installed frontend package exists at research time; `test -f components.json && npx shadcn info` and frontend equivalent returned status 1 on 2026-09-23. Orchestrator is initializing the package concurrently.

The following is a non-exhaustive implementation request, not a claim of installed exports or a closed allowlist. After installation record `npx shadcn info`, resolved CLI version, and actual `src/components/ui` files.

| Requested component | Expected local path after CLI add | Purpose |
|---|---|---|
| Button | @/components/ui/button | Search, retry, graph controls, downloads |
| Input | @/components/ui/input | Exact gid search with visible label |
| Badge | @/components/ui/badge | Role, seed, depth and boundary labels |
| Card | @/components/ui/card | Priority list, graph and inspector surfaces |
| Table | @/components/ui/table | Ranked review candidates and neighbors |
| Alert | @/components/ui/alert | Load error and dataset limitations |

## Spacing Scale

| Token | Value | Usage |
|---|---|---|
| xs | 4px | Badge and icon spacing |
| sm | 8px | Control gaps and label separation |
| md | 16px | Card internals and compact gutters |
| lg | 24px | Desktop page padding and section gaps |
| xl | 32px | Header spacing |
| 2xl | 48px | Empty-state padding |
| 3xl | 64px | Header minimum height |

Controls: minimum 44px height and icon-only hit area. Page padding 16px below 768px. Border thickness and graph geometry are not spacing tokens. No other spacing exceptions.

## Typography

Exactly four sizes and two weights. Numbers use tabular numerals. Gid remains selectable text.

| Role | Size | Weight | Line Height |
|---|---|---|---|
| Body | 16px | 400 | 1.5 |
| Label / table / helper | 14px | 400 or 600 | 1.5 |
| Section heading | 20px | 600 | 1.2 |
| Page heading / summary count | 28px | 600 | 1.2 |

## Color

| Role | Value | Usage |
|---|---|---|
| Dominant (60%) | #FFFFFF | Cards, graph canvas and inspector |
| Secondary (30%) | #F1F5F9 | Page background, quiet panels and table headers |
| Accent (10% maximum) | #0F766E | Primary search button, active selection border, focus ring and selected node halo |
| Foreground | #0F172A | Main text |
| Muted foreground | #475569 | Supporting text |
| Border | #CBD5E1 | Panel boundaries |
| Destructive | #B91C1C | Reserved for destructive operations; none exist in this phase |

Accent reserved for the four elements above. Secondary buttons stay neutral. Theme `primary-foreground` is white; `accent` hover surfaces use #F0FDFA with dark foreground. Data colors are separate categorical encodings, confined to graph nodes and compact legend markers: consolidator #2563EB, transit #0891B2, distributor #7C3AED, terminal #A16207, coordinator #BE185D, peripheral #64748B. Every role also has a textual label; color never implies guilt. Cluster mode uses a stable categorical palette keyed by cluster_id with explicit cluster labels, and replaces role fill rather than overlaying a second fill.

## Layout and Interaction Contract

Header: «Граф денег», subtitle «Приоритеты проверки и связи участников», compact dataset period from available metadata and three CSV links. A muted, always-visible sentence states «Роли и приоритеты — гипотезы для проверки, не оценка виновности».

Main order: factual summary counts; exact gid search; graph and inspector; ranked priority list. At widths ≥1200px use graph plus 360px inspector columns with 24px gap. At 768–1199px inspector stacks below graph; below 768px all content stacks, controls wrap and page has no horizontal overflow. Graph height is 560px desktop and 400px mobile. Ranking table may scroll horizontally inside its named region.

Initial selection is the first top_nodes item when present. Show ranking position, full gid, translated role, priority formatted as 0.00 and why. Each gid is a real button; activation selects the same node in inspector and graph. Do not treat priority_score or role_score as probability of guilt or calibrated certainty. Display «Приоритет проверки» and «Оценка правила роли».

Search indexes the entire nodes array, never the currently visible graph subset. Treat identifiers as strings throughout; trim surrounding whitespace without numeric conversion. Enter and «Найти узел» select an exact match, reveal its neighborhood and update inspector. Search can always recover a filtered-out or isolated gid. A nonexistent gid preserves the current selection and shows the documented search message. Empty search shows a field hint without changing selection.

Graph displays arrowheads from src to dst and a visible legend «Стрелка: плательщик → получатель». Controls: «Приблизить», «Отдалить», «Показать целиком», «Цвет: роли / кластеры». Support pan and zoom; dragging never opens the inspector accidentally. Show selected node, its incoming and outgoing neighbors by default to keep connections readable. A network overview can display all nodes; any subset must say «Показано X из Y узлов» and retain full-dataset search. Isolated selection shows its single node, not an empty graph. Stable layout avoids movement after settling; reduced-motion users get immediate layout changes.

Inspector heading «Узел {gid}». Show role, cluster, depth, seed label, evidence, priority_score, role_score, in_degree, out_degree, in_sum, out_sum, pass_through, seed_ancestors and warnings. Money uses ru-RU separators and «₸»; nullable pass_through uses «Нет данных» instead of zero. For seed show «Входящие переводы вне выборки не видны». For boundary_censored show «Граница выгрузки: отсутствие исходящих не доказывает конечного получателя». Incoming/outgoing neighbor lists expose full gid, amount and n_tx; every neighbor can be selected without touching the canvas.

Role translations: consolidator «Консолидация», transit «Транзит», distributor «Распределение», terminal «Конечный получатель», coordinator «Координация», peripheral «Периферия». Inspector presents them as hypotheses via its persistent explanatory caption. Cluster summary uses actual n_nodes, n_seed, sum_kzt_internal, top_gids and hypothesis when supplied; never invent attributes.

Use labeled inputs, semantic headings, buttons and tables. All actions operate via Tab, Enter or Space, with a 2px visible focus ring. Canvas is supplemented by equivalent neighbor lists and ranking controls. Selection changes announce gid in a polite live region. Do not put every graph node into the tab sequence. Avoid hover-only facts. Any tooltip has an accessible name and equivalent visible inspector text.

## Data Contract

Fetch local `/data/report.json` once with explicit loading, error and retry states. The report has `schema_version: '1.0'` (a string) and contains meta, nodes, edges, clusters, top_nodes, as specified by authoritative `docs/DATA-CONTRACT.md`. Reject unsupported schema versions with a clear error. Node gid and edge src/dst are STRING; top_nodes.gid is STRING. Keep gid text intact even above JavaScript safe-integer range. Validate arrays and references before rendering. Contract keys: nodes include gid, depth, is_seed, role, role_score, cluster_id, priority_score, evidence, in_degree, out_degree, in_sum, out_sum, nullable pass_through, boundary_censored, seed_ancestors, betweenness, warnings:string[]. Edges contain src,dst,sum_kzt,n_tx. top_nodes contain rank,gid,role,priority_score,why. Counts and totals derive from actual report content, never case-example constants.

Downloads use `/data/nodes_roles.csv`, `/data/clusters.csv`, `/data/top_nodes.csv` with descriptive download link names. They remain secondary actions. No backend API, uploads or destructive actions are in scope. No remote fonts, CDN assets or runtime external requests.

## Copywriting Contract

| Element | Copy |
|---|---|
| Primary CTA | Найти узел |
| Search label / placeholder | Поиск по gid / Введите gid |
| Empty search | Введите gid, чтобы открыть узел и его связи. |
| Unknown gid | Узел не найден. Проверьте gid и повторите поиск. |
| Empty dataset heading | В выгрузке пока нет узлов |
| Empty dataset body | Выполните локальный расчёт и обновите страницу. |
| Empty ranking | Список приоритетов пуст. Найдите узел по gid, чтобы изучить его связи. |
| No selection | Выберите узел на графе, в списке или найдите его по gid. |
| Isolated node | В этой выгрузке у узла нет связей. Это не доказывает отсутствие переводов за её пределами. |
| Loading | Загружаем граф и результаты анализа… |
| Load / format error | Не удалось загрузить результаты анализа. Проверьте, что локальный расчёт завершён, и повторите загрузку. |
| Retry action | Повторить загрузку |
| Downloads | Скачать роли CSV / Скачать кластеры CSV / Скачать приоритеты CSV |
| Destructive confirmation | Не применимо: удаление и изменение данных отсутствуют |

## UI Considerations

Applicable state considerations resolved: 8 covered, 0 backstop, 0 unresolved. Covered means prescribed by this contract, not yet implementation-verified.

| Category | Element(s) | Status | Resolution / Reason |
|---|---|---|---|
| empty | report, ranking, search, graph | ✅ covered | Use corresponding Copywriting Contract rows; isolated node is a valid one-node graph |
| loading | report, graph, controls | ✅ covered | Stable-height skeletons, visible status text, disable search until index is ready; retry cannot overlap requests |
| error | report, search | ✅ covered | Visible error and retry for report; unknown gid is inline search feedback preserving current selection |
| populated | graph, ranking, inspector | ✅ covered | Ranked list opens full evidence and directed neighborhood; all values derive from report |
| partial | inspector, metadata | ✅ covered | Null metrics say Нет данных; omit unavailable optional period; warnings retain seed and boundary limitations |
| overflow | ranking, neighbors, page | ✅ covered | Contained table scroll, neighbor vertical flow, wrap controls; full page fits 375px width |
| zero-one-many | nodes, ranking, edges | ✅ covered | Zero has state copy, one has valid layout, many have scrolling and visible rendered counts |
| long-text | gid, why, evidence, warnings | ✅ covered | Wrap explanations and gid with overflow-wrap:anywhere; never permanently truncate full identifier or reason |

## Registry Safety

| Registry | Blocks Used | Safety Gate |
|---|---|---|
| shadcn official | Only requested primitives above; installation owned by orchestrator | Official source; third-party vetting not required; installation not yet verified 2026-09-23 |
| Third-party | None | Not applicable |

## Checker Sign-Off

- [ ] Dimension 1 Copywriting: PASS
- [ ] Dimension 2 Visuals: PASS
- [ ] Dimension 3 Color: PASS
- [ ] Dimension 4 Typography: PASS
- [ ] Dimension 5 Spacing: PASS
- [ ] Dimension 6 Registry Safety: PASS
- [ ] Dimension 7 Inventory Provenance: PASS

**Approval:** pending. Inventory must be refreshed after concurrent shadcn initialization; no false claim of installed components is made.

## Installed inventory — 2026-09-23

Official shadcn 4.21.0 MCP `get_add_command_for_items` was called successfully via `/tmp/shadcn_mcp_probe.py`. The official installed CLI initialized `frontend/` using `--template vite --base radix --preset nova`, then added card, input, badge, alert and table. `shadcn info -c frontend` confirms Vite, TypeScript, Tailwind v4, base radix, style radix-nova and preset b2fA. Installed source paths are `frontend/src/components/ui/{button,card,input,badge,alert,table}.tsx`; all six are consumed by App/Graph. The generated preset's neutral palette is overridden by this contract's slate/teal light tokens, and its bundled Geist import is removed in favor of system fonts. No third-party registry or external runtime assets are used.

Implementation inventory includes required generated `frontend/components.json`, `frontend/src/lib/utils.ts` and the npm lockfile beyond the initial plan's 13-file estimate. CLI output retained its official primitive implementation. Component tests cover exact string gid, neighbor/rank selection, boundary/isolate warnings, malformed input, load/error/retry/empty states and downloads. Production build and TypeScript check pass.
