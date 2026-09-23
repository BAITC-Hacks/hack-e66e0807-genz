# Phase 03 UI design contract

Canonical public design: [DESIGN.md](../../../..//DESIGN.md). Full gids are now displayed on every visible graph node, strengthening the minimum focus/selection requirement below. Geist is explicitly imported from the existing font package.

## Design read and audit
Minimal professional analyst workbench; Design Taste plus minimalist-ui adapted to functional product UI. Existing radial graph hides direction in crossing lines; stacked summaries and filters push the primary task below the fold. Preserve installed Geist, official shadcn controls and trusted semantic data. No decorative hero, gradients, photography or new library. Dials: variance 3, motion 1, density 5. Existing lucide dependency is retained for consistent controls; no extra icon system.

## Layout
Compact header: brand and local status left, methodology and exports right. Search + compact dataset counts below. Desktop workspace: 280px investigation list / flexible large graph / 310px inspector. At widths below 1200px inspector moves below the graph; below 760px stack list, graph, inspector with bounded lists and no page overflow. Workspace surfaces have 1px neutral borders, 8px corners, no shadows. Warm-white background and charcoal type, one teal action accent; role colors are semantic exception, muted and always text-labeled.

## Investigation list
Two labeled modes: priorities (at least 20 supplied rows with rank, gid, role, score and rationale) and entire sample (all-node four-filter exploration, paging in 20-row increments). Cluster overview is a separate disclosure in sample mode; selecting cluster sets filter. Global gid search always ignores list filters. Selection is shared and visibly marked. Compact narrative evidence wraps, gids never convert to numbers.

## Directional graph
Three columns titled «Отправители», «Выбранный участник», «Получатели». Center node shows full gid and role, adjacent nodes show recognizable short ids with full gid available on focus/hover and selection. Each visible edge has arrowhead, amount label, and accessible payer→recipient label; stroke width reflects relative observed amount only. Incoming/outgoing lanes independently page six connections, sorted by amount then gid. Counts state visible/total; no hidden-neighbor ambiguity. Reciprocal neighbors can appear in both lanes because direction matters. Self-transfers use explicit loop treatment. Role/cluster segmented controls recolor nodes with textual legend. Zoom and reset labeled controls. Keyboard enter/space selects graph node. Empty isolate keeps central node plus an explanation. Graph is local one-hop neighborhood, stated explicitly; no fake whole-network view.

## Inspector and disclosure
Always visible: full gid, role hypothesis, priority, evidence, incoming/outgoing totals, seed/boundary warnings. Native accessible details disclose temporal evidence, all neighbor links, community, and detailed metrics. Temporal caution remains adjacent to evidence: «Совпадение дат не доказывает, что переводились те же деньги». Partial optional data says unavailable rather than zero. Next data requests remain accessible. Methodology contains limitations, pipeline and metric interpretation. Header exports disclose three CSV links.

## Interaction/accessibility/state contract
Official shadcn Button/Input/Select/Badge/Alert remain. Controls have visible names, 40–44px touch targets and strong focus rings. Loading, retryable error, empty report, empty filter and optional-invalid warnings remain. Long report strings wrap. Reduced-motion supported; no unnecessary motion. Selection updates graph and inspector immediately; search success visibly identifies opened gid. All source text remains escaped by React.

## Acceptance
Automated: search outside filters, isolate/boundary warnings, combined filters/reset, cluster navigation, >=20 priority rationales, optional temporal safety, role/cluster graph modes, arrow direction, amount labels, neighbor paging and keyboard selection. Production build. Parent independently captures desktop and mobile screenshots and completes real-data judge journey before declaring usability passed.

## Tool provenance
Context7 React official docs resolved and queried for derived useMemo state. No new dependency needed. shadcn MCP is unavailable in this agent's exposed tool inventory; inspected installed official shadcn components are used directly.
