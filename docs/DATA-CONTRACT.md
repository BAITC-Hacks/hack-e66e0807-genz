# Data contract v1

This is the shared authoritative analytics/UI boundary. No network API: UI fetches `/data/report.json` and downloads `/data/nodes_roles.csv`, `/data/clusters.csv`, `/data/top_nodes.csv`. Python writes into chosen `--out` directory. Integration copies/mounts it as `/data`. JSON UTF-8, finite numbers, no NaN/Infinity, gid/src/dst always strings; CSV gid remains integer.

```ts
type Role = 'consolidator'|'transit'|'distributor'|'terminal'|'coordinator'|'peripheral';
interface NodeRecord {
  gid: string; depth: number; is_seed: boolean;
  role: Role; role_score: number; cluster_id: number; priority_score: number;
  evidence: string; in_degree: number; out_degree: number;
  in_sum: number; out_sum: number; pass_through: number|null;
  boundary_censored: boolean; seed_ancestors: number; betweenness: number;
  warnings: string[];
}
interface EdgeRecord { src:string; dst:string; sum_kzt:number; n_tx:number; }
interface ClusterRecord {
  cluster_id:number; n_nodes:number; n_seed:number; sum_kzt_internal:number;
  top_gids:string[]; hypothesis:string;
}
interface TopRecord { rank:number; gid:string; role:Role; priority_score:number; why:string; }
interface Report {
  schema_version:'1.0';
  meta: { n_nodes:number; n_edges:number; n_transactions:number; n_seed:number;
    total_kzt:number; period_start:string; period_end:string;
    elapsed_seconds:number; warnings:string[]; };
  nodes:NodeRecord[]; edges:EdgeRecord[]; clusters:ClusterRecord[]; top_nodes:TopRecord[];
}
```

Optional additive fields are allowed, existing fields must not change. UI must reject unsupported schema versions clearly and handle fetch errors/empty datasets. Roles and scores are hypotheses. No seed or boundary zero-outflow terminal inference. `pass_through=null` means not interpretable (seed or zero incoming); boundary limitation must remain visible.

CSV exact schemas:
- nodes_roles.csv: gid,role,role_score,cluster_id,priority_score,evidence
- clusters.csv: cluster_id,n_nodes,n_seed,sum_kzt_internal,top_gids,hypothesis (`top_gids` serialized with `;`)
- top_nodes.csv: rank,gid,role,priority_score,why

Backend public entry: `solution.pipeline.run_pipeline(data_dir: Path, out_dir: Path) -> dict` returns Report and writes all outputs. CLI parent calls it. Python package entry may delegate to this function. Analytics owner owns solution/pipeline.py and solution/analytics.py (may add supporting files), tests/test_analytics.py. Integration owns solution/__main__.py, solution/server.py, tests/test_contracts.py, scripts/, README, root dependency files. UI owner owns frontend/ exclusively.

Determinism: fixed random seed, stable gid sorting and stable cluster numbering. Tied top ranks use numeric gid. elapsed_seconds may vary; deterministic CSVs must not.

## Phase 2 additive node fields (schema_version remains `1.0`)

Phase 2 adds optional fields to `NodeRecord`; existing reports without them remain valid. The three CSV schemas above, roles, and scores do not change. JSON identifiers remain strings.

```ts
interface TemporalExample { incoming_date: string; outgoing_date: string } // YYYY-MM-DD
interface TemporalEvidence {
  incoming_tx_count: number;
  outgoing_tx_count: number;
  outgoing_after_1d_count: number;
  outgoing_after_1_or_2d_count: number;
  after_1_or_2d_examples: TemporalExample[]; // at most 3; ascending date pairs
  incoming_profile: {
    active_days: number; total_kzt: number; distinct_payers: number; median_kzt: number;
  };
  synchronous_incoming: null | {
    date: string; distinct_payers: number; tx_count: number; sum_kzt: number;
  };
  peak_day: null | {
    date: string; count: number; share: number; baseline_daily_count: number;
  };
}
interface NodeRecordPhase2 extends NodeRecord {
  temporal?: TemporalEvidence;
  next_data_requests?: string[];
}
```

For a given gid, count each outgoing transaction row once in `outgoing_after_1d_count` when at least one incoming row to that gid is dated exactly one calendar day earlier. Count each outgoing row once in `outgoing_after_1_or_2d_count` when at least one incoming row is dated one or two calendar days earlier. The one-day set is a subset of the one-or-two-day set. Multiple incoming rows never multiply a matched outgoing row. Use parsed calendar dates; same-day and later incoming rows do not match. The examples contain up to three distinct qualifying date pairs sorted by incoming date then outgoing date; they illustrate temporal coincidence, not matched amounts or traced funds.

Daily activity counts each transaction row incident to the gid once, whether incoming or outgoing; a self-loop counts once. `baseline_daily_count` is total incident rows divided by the inclusive number of calendar days from report `period_start` through `period_end`. A `peak_day` is emitted only if its incident count is at least 3 and at least twice the baseline. Pick the maximum qualifying count, breaking ties by earliest date. `share` is peak count divided by total incident rows. If no day qualifies, `peak_day` is `null`. All counts are nonnegative integers; share is in [0,1]; baseline is finite and nonnegative. For an isolate, counts and examples are empty/zero and peak is null.

`incoming_profile` describes observed incoming transaction rows for the gid: `active_days` is the number of distinct calendar dates with incoming rows; `total_kzt` is their amount sum; `distinct_payers` is the number of distinct source gid strings; `median_kzt` is the median incoming row amount, or 0 when there are no incoming rows. Amounts are finite, nonnegative KZT. `synchronous_incoming` is a same-calendar-day concentration of incoming rows from at least three distinct payer gids. Choose the qualifying date with the most distinct payers, breaking ties by earliest date. Its `tx_count` and `sum_kzt` cover all incoming rows on that date, including repeated rows from one payer; `distinct_payers` counts each payer once. Otherwise it is `null`. These measures apply to depth-4 nodes; a depth-4 incoming profile does not prove the node is a terminal recipient. No within-day order is inferred.

`next_data_requests` contains at least one concise, actionable Russian request derived from observed limitations for that gid: missing incoming history for seeds or nodes with no observed incoming rows; continuation beyond depth 4 for boundary-censored nodes; transaction timestamps, reference identifiers and account statements where temporal coincidence needs testing; or data beyond the bank/period boundary. Every request names the gid or observed date/metric and does not infer guilt or identity of funds. The UI displays these strings as analyst follow-up requests, and gracefully handles their absence in older reports.

The Python writer emits a complete `TemporalEvidence` object. A reader of an older or partial report treats absent optional fields as unavailable evidence, never as a measured zero. Invalid optional values are ignored with a nonfatal UI warning while valid required Phase 1 node fields remain available. No optional value can invalidate the entire report.
