---
phase: 02-vremennye-patterny-i-uglublennaya-proverka
reviewed: 2026-09-23T11:31:00Z
depth: deep
files_reviewed: 7
files_reviewed_list:
  - solution/temporal.py
  - solution/pipeline.py
  - run.py
  - scripts/verify_temporal.py
  - frontend/src/contract.ts
  - frontend/src/App.tsx
  - frontend/src/components/ui/select.tsx
findings:
  critical: 1
  warning: 1
  info: 0
  total: 2
status: resolved
---

# Phase 2: Code Review Report

**Reviewed:** 2026-09-23T11:31:00Z  
**Depth:** deep  
**Files Reviewed:** 7  
**Status:** resolved

## Summary

The temporal producer matches the specified date windows, row counting, peak threshold, and payer tie breaks. The report reader can nevertheless present an invalid date pair as temporal evidence. The independent verifier also accepts a missing boundary request for many gids.

## Narrative Findings (AI reviewer)

### CR-01 — BLOCKER: Invalid date pairs appear as qualifying temporal evidence

**File:** `frontend/src/contract.ts:36-38`  
**Issue:** `parseTemporal` checks that each example has two valid calendar dates, but does not check that the outgoing date is exactly one or two days after the incoming date. A reversed, same-day, or three-day pair survives parsing and is rendered in `frontend/src/App.tsx:23` under “Примеры дат,” even though the data contract defines these examples as qualifying 1–2-day coincidences. The malformed optional value should be ignored with a nonfatal warning, preserving the Phase 1 node fields. The parser also permits an example when the corresponding outgoing count is explicitly zero.

**Fix:** Parse both dates as UTC calendar dates and retain a pair only when its day difference is 1 or 2. Mark rejected entries as invalid; when a corresponding count is supplied, reject examples that contradict a zero count. Add same-day, reversed, and three-day regression cases while retaining valid 1- and 2-day examples.

### WR-01 — WARNING: Boundary request verification can pass on the gid alone

**File:** `scripts/verify_temporal.py:95-96`  
**Issue:** The independent check accepts any request containing the character `4`. A generic request such as `Запросить операции gid 1234` passes for a boundary node despite never asking for continuation beyond depth 4. In the current generated report, 240 of 444 boundary nodes have a gid containing `4`, so this false pass is not merely theoretical.

**Fix:** Check for a phrase that identifies the boundary limitation or requested continuation, such as `depth=4`, `глубин`, or `границ`, rather than a bare digit; add a verifier negative case with a gid containing `4` and only a generic request.

---

_Reviewed: 2026-09-23T11:31:00Z_  
_Reviewer: gsd-code-reviewer_  
_Depth: deep_

## Repair and regression evidence — 2026-09-23 11:33UTC

CR-01: UTC day-difference1or2 required; unsorted/duplicate/over-cap examples ignored; examples contradicting explicitzero counts ignored; count1<=count2<=outflow and peak>=2baseline enforced. Four new tests first failed; explicitzero test also failed before its fix. Final16/16frontend tests andbuildPASS. Base report remains accessible with nonfatalwarning.

WR-01: boundary verifier now requires semantic boundary/depth wording, not digit4. Persistent tests/test_contracts.py regression mutates a synthetic boundary node whose gidcontains4; genericrequest is rejected. Full26/26Python testsPASS.

After repairs: realdata delivery+browser18checksPASS, fullCLI0.566/0.616s, no skipped checks. Independent final phase verifier confirms closure separately.
