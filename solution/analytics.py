"""Deterministic directed-flow features and explainable structural hypotheses."""
from __future__ import annotations

import math

import networkx as nx

RANDOM_SEED = 42


def analyze(nodes, edges):
    graph = nx.DiGraph()
    graph.add_nodes_from(int(row.gid) for row in nodes.itertuples(index=False))
    for row in edges.itertuples(index=False):
        graph.add_edge(int(row.src), int(row.dst), sum_kzt=float(row.sum_kzt), n_tx=int(row.n_tx))
    communities = sorted(nx.weakly_connected_components(graph), key=min)
    membership = {gid: i for i, group in enumerate(communities) for gid in group}
    records = []
    for row in nodes.itertuples(index=False):
        gid = int(row.gid)
        incoming = float(graph.in_degree(gid, weight="sum_kzt"))
        outgoing = float(graph.out_degree(gid, weight="sum_kzt"))
        seed = bool(row.is_seed)
        boundary = int(row.depth) >= 4
        warnings = []
        if seed:
            warnings.append("Seed: входящие из-за пределов выборки не наблюдаются; коэффициент пропуска не интерпретируется.")
        if boundary:
            warnings.append("Граница depth=4: исходящие за границей обхода не наблюдаются; нулевой выход не доказывает удержание.")
        if outgoing > incoming:
            warnings.append("Наблюдаемый выход больше входа: входящие потоки неполны; это не полный баланс счёта.")
        records.append({"gid": str(gid), "depth": int(row.depth), "is_seed": seed,
                        "role": "peripheral", "role_score": 0.2, "cluster_id": membership[gid],
                        "priority_score": 0.0, "evidence": f"Гипотеза периферии: входов {graph.in_degree(gid)}, выходов {graph.out_degree(gid)}; вход {incoming:.2f}, выход {outgoing:.2f} KZT.",
                        "in_degree": graph.in_degree(gid), "out_degree": graph.out_degree(gid),
                        "in_sum": incoming, "out_sum": outgoing,
                        "pass_through": outgoing / incoming if incoming > 0 and not seed else None,
                        "boundary_censored": boundary, "seed_ancestors": 0,
                        "betweenness": 0.0, "warnings": warnings})
    clusters = [{"cluster_id": i, "n_nodes": len(group),
                 "n_seed": sum(n["is_seed"] for n in records if int(n["gid"]) in group),
                 "sum_kzt_internal": math.fsum(d["sum_kzt"] for u, v, d in graph.edges(data=True) if u in group and v in group),
                 "top_gids": [str(g) for g in sorted(group)[:5]],
                 "hypothesis": f"Структурная группа: {len(group)} узлов; связи требуют проверки."}
                for i, group in enumerate(communities)]
    top = [{"rank": i + 1, "gid": n["gid"], "role": n["role"], "priority_score": n["priority_score"], "why": n["evidence"]}
           for i, n in enumerate(records[:50])]
    return records, clusters, top, graph
