<!-- GSD:project-start source:PROJECT.md -->

## Project

**Граф денег**

Локальный инструмент AML-аналитика для восстановления структуры транзакционной сети: объяснимые роли, сообщества, приоритеты проверки и интерактивный граф. На входе три parquet организаторов; на выходе три CSV фиксированных схем и чистый понятный интерфейс на shadcn/ui.

**Core Value:** Аналитик видит, кого проверять первым и почему, и может найти любой gid и исследовать его связи.

### Constraints

- Время: час от начала реализации (2026-09-23 10:47 UTC); сначала сдаваемый MVP, затем улучшения.
- Данные: ожидаются 2248 узлов, 3119 рёбер, 4840 транзакций; проверить на реальных файлах, не хардкодить результаты.
- Обрыв на depth=4 не доказывает terminal; seed имеют неполный вход; изоляты должны сохраняться.
- Все оценки — эвристики и гипотезы, не вероятность вины. Никаких выдуманных атрибутов.
- Работать автономно; вопрос нужен только при неустранимом препятствии. При провале критерия исправлять и перепроверять.
- Context7 для актуальной документации библиотек. Для UI использовать shadcn MCP при доступности; обнаружить и сообщить техническое ограничение, если инструмент недоступен.

<!-- GSD:project-end -->

<!-- GSD:stack-start source:STACK.md -->

## Technology Stack

Python 3.12+ (exclude 3.14.1), pandas/pyarrow/NetworkX; React/TypeScript/Vite and official shadcn/ui. Exact dependencies: requirements*.txt and frontend/package-lock.json.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Deterministic scoring and tie-breaking; fixed CSV schemas; additive JSON changes. Test real semantics, seed censoring and boundary cases. When changing data interfaces, read docs/DATA-CONTRACT.md first.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Local parquet → solution.pipeline + analytics → output CSV/JSON → allowlisted loopback server → frontend. Read docs/ARCHITECTURE.md when changing module boundaries or deployment.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Hackathon delivery: commit each completed small task promptly and immediately push to origin/main (explicit user authorization). Parallel agents notify the parent with exact ready file paths; the parent serializes git operations. User explicitly authorized autonomous GSD loops, parallel work after shared contracts, and repair/retest when acceptance criteria fail. Do not wait for an entire phase before committing.

Context continuity: after each phase write SUMMARY and VERIFICATION evidence, update STATE/ROADMAP/REQUIREMENTS, then reread STATE.md and ROADMAP.md before selecting the next phase. Before context compaction record active agents, ownership, pending checks, server sessions, latest commit/push and exact next action in .planning/STATE.md. Refresh this AGENTS.md when workflow or stable project conventions change. Never infer passing checks from an old summary after code changes.

Subagents: user permits choosing lower-cost models and effort. For new work prefer gpt-6-sol (high for implementation/verification, medium for bounded checks/docs); use gpt-6-luna only for simple read-only inventory. For Phase 3 UI redesign the user explicitly selected gpt-6-astra with high effort; use that override for the frontend executor. Preserve already-running agents rather than restarting completed work.

Project commands: Judge launch is `python3 run.py` (prepares dependencies when needed, builds, computes, serves on port 8000); `python3 run.py --check` builds, computes, validates and exits; `--skip-install` uses prepared dependencies. Python runtime after setup is .venv/bin/python; batch is `python3 -m solution --data FINANCE-CASE/data --out output`. Frontend lives in frontend/; build/test commands are its package.json scripts. In the Codex sandbox, installation/network and loopback server tests may need exec escalation. This is an environment restriction, not a product workaround.

UI changes: read DESIGN.md before modifying frontend layout, typography or graph presentation. Preserve original calculation evidence alongside readable explanations. For live development preview use Vite on port 8000 and the report server on 8765; stop that preview before the jury launcher uses port 8000.

Working ownership: analytics owns solution/analytics.py and pipeline.py; frontend owns frontend/; integration owns CLI/server/independent contract tests/README. Interfaces live in docs/DATA-CONTRACT.md. Report JSON ids are strings (actual gid exceeds JS safe integers); CSV ids remain int64. All original organizer files stay unchanged.

Library documentation: use Context7 resolve-library-id then query-docs for current library/SDK/API/CLI facts. Read docs/DATA-CONTRACT.md before changing analytics or frontend interfaces. Preserve organizer inputs under FINANCE-CASE.

Judge clarity gate: before claiming delivery ready, follow README.md from its first screen as a new reviewer: identify the product and analyst decision, run the single launch command, find an arbitrary gid, inspect a boundary node and an isolate, see temporal evidence and its limits, and locate the three CSV exports and independent verification command. If any step is unclear or fails, repair it and repeat the journey. A formal documentation checklist alone does not close this gate. Functional browser checks do not prove usability: the user rejected the original graph readability, so Phase 3 must separately inspect screenshots and demonstrate direction, amounts, roles and the next analyst action at desktop and narrow widths.

Before using Edit, Write, or other file-changing tools, start work through a GSD command so planning artifacts and execution context stay in sync.

Use these entry points:

- `$gsd-quick` for small fixes, doc updates, and ad-hoc tasks
- `$gsd-debug` for investigation and bug fixing
- `$gsd-execute-phase` for planned phase work

Do not make direct repo edits outside a GSD workflow unless the user explicitly asks to bypass it.
<!-- GSD:workflow-end -->

<!-- GSD:profile-start -->

## Developer Profile

> Profile not yet configured. Run `$gsd-profile-user` to generate your developer profile.
> This section is managed by `generate-claude-profile` -- do not edit manually.
<!-- GSD:profile-end -->
