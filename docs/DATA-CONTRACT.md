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
