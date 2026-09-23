"""Independently compare optional route, removal, and anomaly evidence with parquet."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from itertools import islice, product
from pathlib import Path
from statistics import median

import networkx as nx
import pandas as pd


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def close(actual, expected, label):
    require(type(actual) in (int, float) and math.isfinite(actual) and
            math.isclose(actual, expected, rel_tol=1e-10, abs_tol=1e-7),
            f"{label}: {actual} != {expected}")


def verify(data: Path, out: Path, baseline: Path | None = None):
    report = json.loads((out / "report.json").read_text(encoding="utf-8"))
    nodes = {str(row.gid): row for row in pd.read_parquet(data / "nodes.parquet").itertuples(index=False)}
    source_edges = {(str(row.src), str(row.dst)): row for row in
                    pd.read_parquet(data / "edges.parquet").itertuples(index=False)}
    source_tx = pd.read_parquet(data / "transactions.parquet")
    rows_by_pair = defaultdict(list)
    incident, near = Counter(), Counter()
    for row in source_tx.itertuples(index=False):
        src, dst = str(row.src), str(row.dst)
        rows_by_pair[(src, dst)].append((pd.Timestamp(row.date).date().isoformat(), float(row.sum_kzt)))
        for gid in {src, dst}:
            incident[gid] += 1
            near[gid] += 5000 <= float(row.sum_kzt) < 10000
    require({node["gid"] for node in report["nodes"]} == set(nodes), "node coverage")
    require(len(report["edges"]) == len(source_edges), "edge coverage")
    if baseline is not None:
        for name in ("nodes_roles.csv", "clusters.csv", "top_nodes.csv"):
            require((out / name).read_bytes() == (baseline / name).read_bytes(), f"CSV drift: {name}")

    routes = report["routes"]
    require(routes["max_routes_per_node"] == routes["max_cycles_per_node"] == 20, "route output caps")
    require(routes["max_candidate_tuples_per_node"] == routes["max_date_combinations_per_candidate"] == 2000,
            "route work caps")
    require(set(routes["truncated_nodes"]) <= set(nodes), "unknown truncated gid")
    seen_paths, seen_cycles = set(), set()
    per_path_start, per_cycle_start = Counter(), Counter()
    for kind, evidences in (("paths", routes["paths"]), ("cycles", routes["cycles"])):
        for item in evidences:
            gids = tuple(item["gids"])
            require(len(gids) == (3 if kind == "paths" else len(gids)), "path arity")
            require(len(gids) in (2, 3) and len(set(gids)) == len(gids) and set(gids) <= set(nodes),
                    "invalid route members")
            if kind == "cycles":
                require(int(gids[0]) == min(map(int, gids)), "noncanonical cycle")
                require(gids not in seen_cycles, "duplicate cycle")
                seen_cycles.add(gids)
                per_cycle_start[gids[0]] += 1
            else:
                require(gids not in seen_paths, "duplicate path")
                seen_paths.add(gids)
                per_path_start[gids[0]] += 1
            pairs = list(zip(gids, gids[1:] + (gids[0],) if kind == "cycles" else gids[1:]))
            require(len(item["legs"]) == len(pairs), "leg arity")
            for pair, leg in zip(pairs, item["legs"]):
                edge = source_edges.get(pair)
                require(edge is not None and (leg["src"], leg["dst"]) == pair, "route leg not in source")
                close(leg["sum_kzt"], float(edge.sum_kzt), "route leg amount")
                require(leg["n_tx"] == int(edge.n_tx), "route leg count")
            sorted_dates = [tuple(day for day, _ in sorted(rows_by_pair[pair])) for pair in pairs]
            strict, ambiguous, start_days = set(), set(), set()
            scanned = 0
            for days in islice(product(*sorted_dates), 2001):
                scanned += 1
                if scanned > 2000:
                    break
                if all(a < b for a, b in zip(days, days[1:])):
                    strict.add(days)
                    start_days.add(days[0])
                elif all(a <= b for a, b in zip(days, days[1:])) and any(a == b for a, b in zip(days, days[1:])):
                    ambiguous.add(days)
            require(item["strict_date_examples"] == [{"dates": list(days)} for days in sorted(strict)[:3]],
                    "wrong strict examples")
            require(item["same_day_ambiguous_examples"] == [{"dates": list(days)} for days in sorted(ambiguous)[:3]],
                    "wrong ambiguous examples")
            require(item["strict_episode_days"] == len(start_days), "wrong recurrence days")
            require(item["repeated"] is (len(start_days) >= 2), "wrong repeated flag")
            require(item["date_search_truncated"] is (scanned > 2000), "wrong date truncation")
            require(item["limitations"], "route lacks limitations")
    require(all(count <= 20 for count in per_path_start.values()), "path cap exceeded")
    require(all(count <= 20 for count in per_cycle_start.values()), "cycle cap exceeded")

    graph = nx.DiGraph()
    graph.add_nodes_from(int(gid) for gid in nodes)
    graph.add_edges_from((int(src), int(dst)) for src, dst in source_edges)
    resilience = report["resilience"]
    require(resilience["selection"] == "fixed-priority-prefix", "resilience order")
    priority = [item["gid"] for item in report["top_nodes"]]
    cap = min(20, len(priority), len(nodes))
    require(resilience["max_n"] == cap and len(resilience["scenarios"]) == cap + 1,
            "resilience scenario coverage")

    def check_connectivity(item, surviving):
        components = list(nx.weakly_connected_components(surviving))
        largest = max(map(len, components), default=0)
        expected = {"n_nodes": surviving.number_of_nodes(), "n_weak_components": len(components),
                    "largest_component_nodes": largest, "n_isolates": nx.number_of_isolates(surviving),
                    "largest_share_surviving": largest / len(surviving) if len(surviving) else 0,
                    "largest_share_original": largest / len(nodes)}
        for key, value in expected.items():
            if isinstance(value, float):
                close(item[key], value, f"resilience {key}")
            else:
                require(item[key] == value, f"resilience {key}")

    check_connectivity(resilience["baseline"], graph)
    for n, scenario in enumerate(resilience["scenarios"]):
        require(scenario["n_removed"] == n and scenario["removed_gids"] == priority[:n],
                "wrong fixed priority prefix")
        check_connectivity(scenario, graph.subgraph(set(graph.nodes) - {int(gid) for gid in priority[:n]}))

    report_nodes = {node["gid"]: node for node in report["nodes"]}
    by_depth = defaultdict(list)
    for node in report["nodes"]:
        by_depth[node["depth"]].append(node)
    metrics = ("in_degree", "out_degree", "in_sum", "out_sum", "incoming_tx_count",
               "outgoing_tx_count", "near_cutoff_share")
    in_metrics = {"in_degree", "in_sum", "incoming_tx_count"}
    out_metrics = {"out_degree", "out_sum", "outgoing_tx_count"}

    def value(node, metric):
        if metric == "near_cutoff_share":
            return near[node["gid"]] / incident[node["gid"]] if incident[node["gid"]] else 0.0
        if metric in ("incoming_tx_count", "outgoing_tx_count"):
            return node["temporal"][metric]
        return node[metric]

    flagged_count = 0
    for node in report["nodes"]:
        require(isinstance(node.get("anomalies"), list), "missing evaluated anomalies")
        expected = {}
        for metric in metrics:
            if metric in in_metrics and node["is_seed"]:
                continue
            if metric in out_metrics and node["boundary_censored"]:
                continue
            peers = [peer for peer in by_depth[node["depth"]] if peer["gid"] != node["gid"]
                     and (metric not in in_metrics or not peer["is_seed"])
                     and (metric not in out_metrics or not peer["boundary_censored"])]
            if len(peers) < 10:
                continue
            peer_median = median([value(peer, metric) for peer in peers])
            mad = median([abs(value(peer, metric) - peer_median) for peer in peers])
            observed = value(node, metric)
            deviation = (observed - peer_median) / (1.4826 * mad) if mad else None
            if mad:
                flagged = deviation >= 3.5
            else:
                ranked = sorted(peers + [node], key=lambda peer: (value(peer, metric), int(peer["gid"])))
                rank = next(i + 1 for i, peer in enumerate(ranked) if peer["gid"] == node["gid"])
                flagged = len(peers) >= 20 and observed > peer_median and rank / len(ranked) >= .95
            if flagged:
                expected[metric] = (observed, len(peers), peer_median, mad, deviation)
        actual = {finding["metric"]: finding for finding in node["anomalies"]}
        require(set(actual) == set(expected), f"{node['gid']}: anomaly flags differ")
        for metric, (observed, n, peer_median, mad, deviation) in expected.items():
            finding = actual[metric]
            require(finding["peer_depth"] == node["depth"] and finding["peer_n"] == n,
                    "anomaly cohort")
            require(finding["kind"] == ("observed_near_cutoff" if metric == "near_cutoff_share" else "depth_peer_profile"),
                    "anomaly kind")
            for key, expected_value in (("value", observed), ("peer_median", peer_median), ("peer_mad", mad)):
                close(finding[key], expected_value, f"anomaly {key}")
            if deviation is None:
                require(finding["deviation"] is None, "zero-MAD deviation must be null")
            else:
                close(finding["deviation"], deviation, "anomaly deviation")
            require(finding["method"] and finding["limitations"], "anomaly explanation")
            if metric == "near_cutoff_share":
                require(str(near[node["gid"]]) in finding["method"] and
                        str(incident[node["gid"]]) in finding["method"] and
                        any("ниже 5000" in note for note in finding["limitations"]),
                        "near-cutoff source limitation")
            flagged_count += 1
    return {"status": "PASS", "paths": len(routes["paths"]), "cycles": len(routes["cycles"]),
            "scenarios": len(resilience["scenarios"]), "anomaly_findings": flagged_count,
            "csv_baseline": "PASS" if baseline else "not_requested"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("FINANCE-CASE/data"))
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--baseline", type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.data, args.out, args.baseline), ensure_ascii=False, indent=2))
