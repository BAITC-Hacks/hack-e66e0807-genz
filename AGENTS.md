<!-- GSD:project-start source:PROJECT.md -->

## Project

**Граф денег — Money Graph**

A local analytical pipeline and viewer for a bank AML analyst investigating a directed network of transfers originating from 81 known seed clients. It assigns an explainable structural role and investigation priority to every client, groups related nodes, and lets the analyst inspect money flows and locate a given `gid`. The initial release is a working hackathon solution built within one hour, using the supplied anonymized July 2026 dataset and starter code as inputs.

**Core Value:** An analyst can identify which client to review first and explain why using observable graph and transaction evidence, without treating a structural hypothesis as proof of guilt.

### Constraints

- **Timeline**: one hour for a working minimal solution — prioritize the five mandatory case functions and reproducibility.
- **Performance**: raw Parquet to required outputs within five minutes on an ordinary laptop — explicit case acceptance criterion.
- **Infrastructure**: local batch processing with no required network, cloud, GPU, or paid service — case constraints and reliable judging.
- **Data scope**: synthetic `gid` values and observed transactions only — no external enrichment or invented personal attributes.
- **Interpretation**: roles, clusters, and priorities are hypotheses for review — sampling bias and missing ground truth prevent definitive conclusions.
- **Compatibility**: preserve the fixed required CSV schemas and all 2,248 nodes — the judges check them mechanically.
- **Language**: write analyst-facing narrative text in Russian without mechanically translating technical terms — requested for the demo and deliverables.

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

## Context7 Documentation Lookup

When the user asks about a library, framework, SDK, API, CLI tool, or cloud service, use Context7 MCP for current documentation, including syntax, configuration, migration, setup, and library-specific debugging. Do this even for familiar technologies. Prefer Context7 over web search for library documentation.

1. Start with `resolve-library-id` using the library name and a description of what to look up, unless the user supplies an exact `/org/project` ID.
2. Select the best match by exact name, relevant description, snippet count, source reputation, and benchmark score. Use a version-specific ID when the user names a version; retry with alternate terms if results are poor.
3. Call `query-docs` with the chosen ID and a focused question about one concept. Make separate calls for distinct concepts unless the question concerns their interaction.
4. Answer using the fetched documentation.

This lookup is unnecessary for refactoring, scripts written from scratch, business-logic debugging, code review, and general programming concepts.
