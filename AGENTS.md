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

Technology stack not yet documented. Will populate after codebase mapping or first phase.
<!-- GSD:stack-end -->

<!-- GSD:conventions-start source:CONVENTIONS.md -->

## Conventions

Conventions not yet established. Will populate as patterns emerge during development.
<!-- GSD:conventions-end -->

<!-- GSD:architecture-start source:ARCHITECTURE.md -->

## Architecture

Architecture not yet mapped. Follow existing patterns found in the codebase.
<!-- GSD:architecture-end -->

<!-- GSD:skills-start source:skills/ -->

## Project Skills

No project skills found. Add skills to any of: `.claude/skills/`, `.agents/skills/`, `.cursor/skills/`, `.github/skills/`, or `.codex/skills/` with a `SKILL.md` index file.
<!-- GSD:skills-end -->

<!-- GSD:workflow-start source:GSD defaults -->

## GSD Workflow Enforcement

Hackathon delivery: commit each completed small task promptly. Parallel agents notify the parent with exact ready file paths; the parent serializes git operations. User explicitly authorized autonomous GSD loops, parallel work after shared contracts, and repair/retest when acceptance criteria fail. Do not wait for an entire phase before committing.

Library documentation: use Context7 resolve-library-id then query-docs for current library/SDK/API/CLI facts. Read docs/DATA-CONTRACT.md before changing analytics or frontend interfaces. Preserve organizer inputs under FINANCE-CASE.

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
