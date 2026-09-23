# Implementation preparation

Scope: dependency and integration facts only; no broad domain research needed after the supplied case analysis.

## Package provenance
| Package | Source / reason | State |
|---|---|---|
| pandas, pyarrow, networkx, numpy | Organizer requirements.txt; local Python analysis | Installed into .venv from PyPI; versions recorded at delivery |
| pytest | Standard Python tests, PyPI | Installed into .venv |
| shadcn 4.21.0 | Official shadcn-ui/ui project, current docs via Context7 | Official CLI installed; MCP initialize/tools-list/get_add_command_for_items invoked successfully |
| React, React DOM, Vite, TypeScript | Standard local UI build; official docs via Context7 at implementation | UI executor installs in frontend only, lockfile retained |
| Tailwind, Radix/shadcn component dependencies, lucide-react | Official shadcn registry dependency chain | UI executor uses official registry, keeps lockfile |

## Confirmed input facts
Read-only parquet inspection confirms 2248 nodes, 3119 edges, 4840 transactions and declared columns. gid examples are 18-digit int64: JSON MUST serialize ids as strings to avoid browser precision loss. No data is modified or uploaded.

## MCP
Official server started with `node <installed shadcn>/dist/index.js mcp` over stdio; it exposes registry search, view, examples, installation-command and audit tools. MCP get_add_command_for_items returned official add command for button/card/input/badge/tabs/table/select/separator. Local probe script lives in /tmp, not a product dependency.

## Runtime adaptation
Native GSD typed subagents are available. User explicitly requested parallel UI and analytics after common contract. They operate in shared workspace with disjoint file ownership; parent serializes commits. No concurrent git operations or cross-owned file edits. This avoids worktree setup overhead while retaining independent plan-checker/verifier contexts.

## Sources
- Organizer FINANCE-CASE/case.md, additional.md, starter/requirements.txt.
- https://github.com/shadcn-ui/ui/blob/main/skills/shadcn/mcp.md (via Context7).
- https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.community.louvain.louvain_communities.html (via Context7 in initial analysis).
