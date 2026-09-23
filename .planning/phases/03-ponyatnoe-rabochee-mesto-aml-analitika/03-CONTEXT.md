# Phase 3 — Понятное рабочее место AML-аналитика

## User-approved scope
The user rejected the current interface as difficult to understand, especially graph visualization. Redesign with the installed Design Taste plugin and Astra high effort; retain minimal, clean and functional shadcn UI. Graph libraries are allowed but 3D is not a requirement. Autonomous execution and immediate frequent GitHub pushes remain authorized. AI assistant remains deferred.

## Decisions
- D01: Make the analyst task primary: whom to inspect and why → money direction → evidence and next action.
- D02: Use shadcn controls, restrained monochrome surfaces, semantic role colors and readable labels. Apply Design Taste/minimalist guidance relevant to an analytical app.
- D03: Give the graph a large dedicated workspace. Distinguish incoming and outgoing flows spatially; expose amounts and direction without relying on color alone. Show full gid on selection/focus.
- D04: Keep arbitrary gid search, priority list with reasons, role/cluster modes, filters/cluster overview, all three CSV exports, temporal evidence, boundary and seed caveats, isolate states, architecture explanation.
- D05: All figures come from the existing report. Preserve data contract and analytic rules; no invented client attributes or guilt claims.
- D06: Test dense neighborhoods, reciprocal edges, isolates and depth=4. Reduced/default graph scope must disclose any hidden neighbors and offer a way to reach them.
- D07: Automated pass is functional evidence only. Independently inspect actual screenshots at desktop and mobile; document observed clarity and remaining limits without claiming human approval.
- D08: Astra owns frontend and UI specification/plan; parent owns integration tests, docs, state and serial commits/pushes. Backend unchanged.

## Acceptance
A first-time reviewer can locate the priority list and reason, open any account, distinguish who paid it and whom it paid, read the amount for a chosen connection, inspect role explanation and data limits, and export results. Important controls and selected-account context remain visible without scrolling through a long dashboard.
