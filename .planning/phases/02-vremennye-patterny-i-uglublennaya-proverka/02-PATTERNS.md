# Phase 2: Временные паттерны и углубленная проверка — Pattern Map

**Mapped:** 2026-09-23. **Files analyzed:** 8 executable files. **Analogs found:** 8/8; all git tracked.

## File Classification

| Planned file | Role / data flow | Closest tracked analog | Match |
|---|---|---|---|
| `solution/temporal.py` | analytics service / batch transform | `solution/analytics.py` | exact role |
| `solution/pipeline.py` | pipeline / file I/O, batch | itself | exact |
| `tests/test_temporal.py` | test / file I/O, batch | `tests/test_analytics.py` | exact |
| `frontend/src/contract.ts` | model and validator / transform | itself | exact |
| `frontend/src/App.tsx` | component / event driven | itself; `frontend/src/components/Graph.tsx` | exact |
| `frontend/src/App.test.tsx` | test / event driven | itself | exact |
| `frontend/src/index.css` | styling / event driven | itself | exact |
| `scripts/verify_temporal.py` | independent verifier / file I/O, batch | `scripts/verify_delivery.py` | exact role |

No new frontend component file is planned: `02-02-PLAN.md` places the card and filters in `App.tsx`.

## Pattern Assignments

### `solution/temporal.py` and `solution/pipeline.py`

`solution/analytics.py:2-6,82-87` uses future annotations, standard imports, and a pure `analyze(nodes, edges)` entry returning data to the pipeline. Keep temporal logic deterministic and separate from `classify_role`. `solution/pipeline.py:61-66` parses validated dates with `pd.to_datetime(..., errors="raise")`; use these validated timestamps. Integration point is `solution/pipeline.py:78-95`: call enrichment after `analyze(nodes, edges)` and before the report dict. Preserve `CSV_SCHEMAS` at lines 15-19 and JSON finite serialization at line 97:

```python
nodes, edges, tx = load_and_validate(Path(data_dir))
records, clusters, top, graph = analyze(nodes, edges)
serialized = json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
```

### `tests/test_temporal.py`

Copy the small parquet fixture and temporary output structure from `tests/test_analytics.py:11-40`; vary transaction dates and edges per test, then inspect both returned report and exported schema:

```python
with tempfile.TemporaryDirectory() as tmp:
    data = Path(tmp)
    fixture(data)
    report = run_pipeline(data, data / "out")
    self.assertEqual(report["schema_version"], "1.0")
```

Use `self.subTest(...)` as in `tests/test_analytics.py:44-54`. Cover outgoing row uniqueness, date boundaries, self-loops, isolates, and unchanged role/priority.

### `frontend/src/contract.ts`

Extend `NodeRecord` at line 4 with optional fields. Keep `Report.schema_version: '1.0'` at line 8. `parseReport` lines 13-24 validates unknown data before casting; optional fields should validate only when present. Reuse `object`, `strings`, `number`, and `nums` at lines 9-12, including `Number.isFinite`:

```typescript
const number = (v:unknown) => typeof v==='number'&&Number.isFinite(v)
if(value.schema_version!=='1.0') throw new Error('Неподдерживаемая версия схемы отчёта.')
```

### `frontend/src/App.tsx` and `frontend/src/index.css`

Use `Inspector` at `App.tsx:11-19` for the optional temporal block: existing `Card`/`CardContent`, `metrics` definition list, caution text, and conditional `cluster-details` are the exact layout analog. Keep selection centralized through `select(id)` (`App.tsx:24-26`); ranking, cluster buttons, and `Graph` already call the same callback (`App.tsx:18,34-35`, `Graph.tsx:6,24`). Filter state belongs beside report/query/selected at `App.tsx:21-26`; derive filtered lists from report without changing global gid lookup. Match existing CSS class structure in `frontend/src/index.css` for compact cards and empty states.

### `frontend/src/App.test.tsx`

Reuse `App.test.tsx:1-9` fixture with string gid beyond JS safe integer, and `:11-28` fetch/render/interact pattern. `:55-59` directly tests `parseReport` rejection; add optional-field malformed/present/absent cases. Assert filter/reset and cluster navigation with `fireEvent` and accessible names, as in existing UI tests.

### `scripts/verify_temporal.py`

Copy independent input/output checks from `scripts/verify_delivery.py:25-85`: `require`, `finite_tree`, `numeric_record`, CSV header comparison, and direct parquet reads. Use CLI handling from `:209-215` and concise failure exit from `:247-252`. Recompute temporal values directly from parquet; do not import `solution.temporal`.

```python
parser.add_argument("--data", type=Path, default=ROOT / "FINANCE-CASE/data")
parser.add_argument("--out", type=Path, default=ROOT / "output")
require(reader.fieldnames == schema, f"Wrong schema: {name}")
```

## Shared Patterns

- **Identifiers:** `pipeline.py:94` serializes JSON gid as `str(int(...))`; `contract.ts:18-23` requires string IDs.
- **Errors:** `pipeline.py:27-74` raises `ValueError`; `contract.ts:13-24` raises Russian `Error`; `verify_delivery.py:247-252` exits 1.
- **Compatibility:** Keep CSV headers (`pipeline.py:15-19`), additive JSON, and absent optional fields accepted.
