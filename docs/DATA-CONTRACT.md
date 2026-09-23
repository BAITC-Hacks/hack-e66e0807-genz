# Контракт данных v1.0

Этот документ описывает границу пакетного расчёта и интерфейса. Сервер раздаёт статические результаты по HTTP: `/data/report.json`, `/data/nodes_roles.csv`, `/data/clusters.csv`, `/data/top_nodes.csv`. Динамических запросов к аналитике нет: выбор узла и фильтрация выполняются в браузере. Python пишет файлы в каталог `--out`, а сервер публикует этот каталог по указанным четырём адресам.

JSON — UTF-8; числа конечные, без NaN/Infinity; `gid`, `src`, `dst` всегда строки. В CSV идентификатор записан целыми десятичными цифрами. При импорте CSV в электронные таблицы выбирайте тип «текст», чтобы избежать округления длинных gid.

## Входные таблицы

| Файл | Обязательные поля | Инварианты |
|---|---|---|
| `nodes.parquet` | `gid: integer`, `depth: integer`, `is_seed: boolean` | Непустая таблица; уникальный gid; depth ≥ 0; изоляты допустимы |
| `edges.parquet` | `src,dst: integer`, `sum_kzt: number`, `n_tx,depth: integer` | Одна строка на направленную пару; известные узлы; сумма ≥ 0, n_tx ≥ 1 |
| `transactions.parquet` | `src,dst: integer`, `sum_kzt: number`, `date: date-compatible` | Известные узлы; сумма ≥ 0; дата разбирается без пропусков |

Дополнительные входные колонки не используются. Обязательные поля не могут содержать null. Агрегация транзакций по `(src,dst)` должна дать тот же набор пар, число транзакций и суммы, что edges; допуск суммы 0,01 KZT. Самоперевод допустим. `depth` — характеристика исходной выгрузки, а не вычисленная роль.

## Выходной JSON

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

Публичная Python-функция: `solution.pipeline.run_pipeline(data_dir: Path, out_dir: Path) -> dict`. Она возвращает отчёт и записывает четыре файла. CLI: `python -m solution --data <каталог> --out <каталог>`. Неверный вход приводит к ошибке до записи результатов.

### Дополнительные поля верхнего уровня

Писатель также выдаёт `meta.n_weak_components`, `meta.n_isolates` и `methodology: Record<string,string>` с текстовыми правилами. Они не обязательны для чтения базового отчёта. Потребитель игнорирует неизвестные добавочные поля. Поля `has_invalid_optional` в файле нет: это внутренний результат проверки отчёта в браузере.

### Ссылочная целостность и единицы

- Все `edges.src/dst` и элементы `clusters.top_gids`/`top_nodes.gid` ссылаются на существующие `nodes.gid`.
- У каждого узла один cluster_id, которому соответствует строка clusters. Роль входит в закрытый словарь, обе оценки лежат в [0,1].
- Денежные поля — наблюдаемые KZT, не остаток на счёте. `in_degree/out_degree` — число контрагентов, а не число транзакций.
- `pass_through=null` означает seed или отсутствие наблюдаемого входа. Числовое значение на depth=4 всё равно не разрешает делать вывод об удержании: действует boundary_censored.
- `evidence` и `why` — непустые объяснения; evidence ограничено 200 символами. Даты — календарные `YYYY-MM-DD`; пустой период допустим для набора без транзакций.
- При отсутствии необязательной аналитики интерфейс показывает отсутствие данных; `null` у peak/synchrony в полном отчёте означает, что порог не выполнен.

### Совместимость и ошибки чтения

Версия `1.0` допускает добавочные поля, но не изменение смысла существующих. Неподдерживаемая версия, ошибочные обязательные поля или неизвестные ссылки вызывают видимую ошибку загрузки. Ошибки необязательных временных данных дают предупреждение: базовая карточка остаётся доступной. Frontend проверяет форму и часть смысловых ограничений; полный независимый валидатор дополнительно сверяет результаты с исходными таблицами. Наличие frontend-парсера не заменяет эту проверку.

Determinism: fixed random seed, stable gid sorting and stable cluster numbering. Tied top ranks use numeric gid. elapsed_seconds may vary; deterministic CSVs must not.

## Необязательные временные поля (`schema_version: 1.0`)

Следующие поля расширяют `NodeRecord`; ранее рассчитанные отчёты без них остаются допустимыми. The three CSV schemas above, roles, and scores do not change. JSON identifiers remain strings.

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
interface EnrichedNodeRecord extends NodeRecord {
  temporal?: TemporalEvidence;
  next_data_requests?: string[];
}
```

For a given gid, count each outgoing transaction row once in `outgoing_after_1d_count` when at least one incoming row to that gid is dated exactly one calendar day earlier. Count each outgoing row once in `outgoing_after_1_or_2d_count` when at least one incoming row is dated one or two calendar days earlier. The one-day set is a subset of the one-or-two-day set. Multiple incoming rows never multiply a matched outgoing row. Use parsed calendar dates; same-day and later incoming rows do not match. The examples contain up to three distinct qualifying date pairs sorted by incoming date then outgoing date; they illustrate temporal coincidence, not matched amounts or traced funds.

Daily activity counts each transaction row incident to the gid once, whether incoming or outgoing; a self-loop counts once. `baseline_daily_count` is total incident rows divided by the inclusive number of calendar days from report `period_start` through `period_end`. A `peak_day` is emitted only if its incident count is at least 3 and at least twice the baseline. Pick the maximum qualifying count, breaking ties by earliest date. `share` is peak count divided by total incident rows. If no day qualifies, `peak_day` is `null`. All counts are nonnegative integers; share is in [0,1]; baseline is finite and nonnegative. For an isolate, counts and examples are empty/zero and peak is null.

`incoming_profile` describes observed incoming transaction rows for the gid: `active_days` is the number of distinct calendar dates with incoming rows; `total_kzt` is their amount sum; `distinct_payers` is the number of distinct source gid strings; `median_kzt` is the median incoming row amount, or 0 when there are no incoming rows. Amounts are finite, nonnegative KZT. `synchronous_incoming` is a same-calendar-day concentration of incoming rows from at least three distinct payer gids. Choose the qualifying date with the most distinct payers, breaking ties by earliest date. Its `tx_count` and `sum_kzt` cover all incoming rows on that date, including repeated rows from one payer; `distinct_payers` counts each payer once. Otherwise it is `null`. These measures apply to depth-4 nodes; a depth-4 incoming profile does not prove the node is a terminal recipient. No within-day order is inferred.

`next_data_requests` contains at least one concise, actionable Russian request derived from observed limitations for that gid: missing incoming history for seeds or nodes with no observed incoming rows; continuation beyond depth 4 for boundary-censored nodes; transaction timestamps, reference identifiers and account statements where temporal coincidence needs testing; or data beyond the bank/period boundary. Every request names the gid or observed date/metric and does not infer guilt or identity of funds. The UI displays these strings as analyst follow-up requests, and gracefully handles their absence in older reports.

The Python writer emits a complete `TemporalEvidence` object. A reader of an older or partial report treats absent optional fields as unavailable evidence, never as a measured zero. Invalid optional values are ignored with a nonfatal UI warning while valid required base node fields remain available. No optional value can invalidate the entire report.


## Additive extension contract

The following optional interfaces are frozen for the current implementation work. An absent report section means unavailable, not zero; existing mandatory fields and all three CSV schemas stay unchanged. All gid values are decimal strings. Current delivered behavior is described in README and verified against the emitted report.

### Routes: `report.routes`

`routes: {max_routes_per_node:20,max_cycles_per_node:20,max_candidate_tuples_per_node:2000,max_date_combinations_per_candidate:2000,truncated_nodes:string[],paths:RouteEvidence[],cycles:CycleEvidence[]}`. `RouteEvidence` has `gids:[string,string,string]`, `legs:[{src:string,dst:string,sum_kzt:number,n_tx:number}, ...]`, `strict_date_examples:[{dates:[string,string]}]` (at most 3), `same_day_ambiguous_examples:[{dates:[string,string]}]` (at most 3), `strict_episode_days:number`, `repeated:boolean`, `date_search_truncated:boolean`, `limitations:string[]`; `CycleEvidence` has `gids:string[]` of 2 or 3 distinct members with implicit closure to the first, corresponding ordered `legs`, date-example arrays of matching arity, and the same recurrence/truncation fields. Strict example means each consecutive leg's calendar date is strictly later; equal-day combinations are separately ambiguous because no timestamps exist. `strict_episode_days` counts distinct first-leg calendar days with at least one strict tuple, never combinations or presumed matched money; `repeated` means count ≥2. Enumerate source transaction rows by sorted `(date,src,dst,sum_kzt)` and deduplicate identical date tuples; the 2000-combination budget applies before counting, so a truncated search is visibly incomplete and `repeated=false` never implies absence of recurrence when truncated. Routes are unique by directed gid tuple; cycles are unique under rotation to the numerically smallest gid, preserving orientation. Include self-loop only as a separately documented observed edge; it is not a multi-party return cycle. Sort adjacency by numeric gid; per node inspect at most 2000 candidate tuples before materializing at most 20 paths and 20 cycles. `truncated_nodes` identifies nodes where either candidate or output budget cut off enumeration. The UI validates references, leg orientation and date classification, warns on malformed optional data and keeps base report usable.

### Resilience: `report.resilience`

`resilience: {selection:"fixed-priority-prefix", max_n:number, baseline:Connectivity, scenarios:Scenario[]}`. `Connectivity` is `{n_nodes:number,n_weak_components:number,largest_component_nodes:number,n_isolates:number,largest_share_surviving:number,largest_share_original:number}`; baseline has both shares relative to original node count. `Scenario` adds `n_removed:number, removed_gids:string[]` and a `Connectivity` for the induced surviving graph. Include N=0 and every integer through `max_n` (at most 20 and at most top list size), preserving isolates. At N=all nodes, surviving share is 0 with denominator stated; no divide-by-zero. Original denominator is baseline `n_nodes`. UI checks ascending N, exact priority prefix and all values within bounds.

### Anomalies: `NodeRecord.anomalies`

Optional `anomalies: AnomalyEvidence[]`; each item has `{kind:"depth_peer_profile"|"observed_near_cutoff",metric:"in_degree"|"out_degree"|"in_sum"|"out_sum"|"incoming_tx_count"|"outgoing_tx_count"|"near_cutoff_share",value:number,peer_depth:number,peer_n:number,peer_median:number,peer_mad:number|null,deviation:number|null,method:string,limitations:string[]}`. Cohorts are exact `depth`, excluding the subject itself; for incoming metrics exclude all seed nodes from both candidate and peers, and for outgoing metrics exclude all `boundary_censored` nodes from both; the candidate must have at least 10 eligible peers. Median absolute deviation uses those peers; a high-side flag requires `(value-median)/(1.4826*MAD) >= 3.5` with positive MAD. For zero MAD, `deviation=null`, and a high-side flag requires at least 20 peers, `value>median`, and empirical rank at or above the 95th percentile (ties resolved by numeric gid). Smaller/unsupported cohorts have no flag, with no probability claim. `near_cutoff_share` is count of **observed** incident transaction rows with `5000 <= sum_kzt < 10000` divided by all observed incident rows, with self-loop counted once, zero-denominator share defined as 0; report numerator and denominator in `method`. It uses the same cohort/flag rule. Seed incoming and depth-4 outgoing limitations accompany affected findings; near-cutoff wording always notes that rows below 5000 are not in the export. `[]` means evaluated with no flags; absence means unavailable.

### Assistant: local assistant API

Only when explicitly enabled, the loopback server accepts `POST /api/assistant/query` with JSON `{question:string,selected_gid?:string}`; response `{answer:string,citations:Citation[],limitations:string[]}` or explicit unavailable/error. Body ≤4096 bytes, question ≤1000 Unicode characters, ≤4 model/tool rounds, ≤20 rows per tool result, ≤16 KB total tool payload, ≤2048 output characters, ≤20 seconds request time. `Citation` is `{gid:string,kind:"node"|"edge"|"temporal"|"route"|"resilience"|"anomaly",reference:string}`. Reference grammar is `node/<gid>/<field>`, `edge/<src>/<dst>/<field>`, `temporal/<gid>/<field>`, `route/<path|cycle>/<numeric-index>/<field>`, `resilience/<n>/<field>`, `anomaly/<gid>/<numeric-index>/<field>`; route index resolves in exactly the named `paths[]` or `cycles[]`, and resilience N resolves in the unique `scenarios[]` item with `n_removed=N` (or `resilience/0/...` to its matching N=0 scenario). Each component must resolve exactly in the validated report, the citation `gid` must participate in that source object, and scalar numeric/string values must equal its field rather than merely coincidentally equal another object. Model output is a structured list of claim objects `{reference,value}` and optional nonfactual connective text. The server validates all claims, then renders numeric/factual sentences from approved templates; it never displays unconstrained factual prose. Invalid or absent claims yield inability to answer. Tool names and parameters are allowlisted (`get_node`, `get_incoming`, `get_outgoing`, `get_common_recipients`, `get_top_priorities`, `get_cluster`, `get_route_evidence`, `get_resilience_scenario`, `get_anomalies`), with gid/limit validation and bounded output. Credentials are environment-only. When disabled, route returns unavailable and static data still works. No report text is executable instruction. `get_common_recipients(gids)` accepts 2–20 distinct existing source gid strings and returns at most 20 direct recipients ranked by descending distinct supplied payer count, then descending sum of their directed edge amounts, then numeric recipient gid. Each result carries `payer_count`, `sum_kzt`, and `source_edges` with exact src/dst/sum/n_tx. The assistant distinguishes all-five from partial matches and never infers control or multi-hop routing. Pair-specific dates are unavailable from aggregate edges and must be said unavailable unless separate cited temporal evidence exists. For the common-recipient answer, the model may select only a recipient gid from the validated `get_common_recipients` result; it may not supply `payer_count` or `sum_kzt` claim values. The server reselects every directed report edge from the validated tool-input source gid set to that recipient, requires the complete matching edge set (no omission and no out-of-set source), derives distinct payer count and KZT sum itself, and renders the aggregate sentence using a recipient node citation plus one exact `edge/<src>/<dst>/sum_kzt` citation per contributing payer. These derived figures cite their full underlying edge set, not a nonexistent scalar report field. A model-proposed count/sum, omitted edge, extra edge or recipient outside the tool result is rejected. No arbitrary model result ID is accepted.
