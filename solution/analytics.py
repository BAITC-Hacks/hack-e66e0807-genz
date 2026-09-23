"""Deterministic directed-flow features and explainable structural hypotheses."""
from __future__ import annotations

import math

import networkx as nx

RANDOM_SEED = 42
MIN_CONSOLIDATOR_INPUTS = 3
MIN_DISTRIBUTOR_OUTPUTS = 5
MIN_COORDINATOR_SEEDS = 3
TRANSIT_RANGE = (0.8, 1.2)
MAX_TERMINAL_RATIO = 0.2
RULES = {
    "precedence": ["coordinator", "consolidator", "distributor", "transit", "terminal", "peripheral"],
    "coordinator": "seed_ancestors >= 3 AND in_degree >= 3 AND out_degree >= 2 AND betweenness > 0",
    "consolidator": "in_degree >= 3 AND (out_degree <= 2 OR in_degree >= 2*out_degree)",
    "distributor": "out_degree >= 5 AND out_degree >= 2*in_degree",
    "transit": "NOT is_seed AND NOT boundary_censored AND in_degree > 0 AND out_degree > 0 AND 0.8 <= pass_through <= 1.2",
    "terminal": "NOT is_seed AND NOT boundary_censored AND in_sum > 0 AND pass_through <= 0.2",
    "peripheral": "No preceding rule matched; insufficient structural evidence, including isolates",
    "scores": "role_score is rule strength, not a calibrated probability; priority is structural review importance, not guilt",
}


def classify_role(node):
    """First matching rule wins. Scores express observed rule strength only."""
    inc, out = node["in_degree"], node["out_degree"]
    ratio = node["pass_through"]
    interpretable = not node["is_seed"] and not node["boundary_censored"] and ratio is not None
    if node["seed_ancestors"] >= MIN_COORDINATOR_SEEDS and inc >= 3 and out >= 2 and node["betweenness"] > 0:
        role, score = "coordinator", 0.6 + 0.4 * min(node["seed_ancestors"] / 10, 1)
        detail = f"связь с {node['seed_ancestors']} seed по путям; входов {inc}, выходов {out}; посредничество {node['betweenness']:.5f}"
    elif inc >= MIN_CONSOLIDATOR_INPUTS and (out <= 2 or inc >= 2 * out):
        role, score = "consolidator", 0.5 + 0.5 * min(inc / 10, 1)
        detail = f"вход от {inc} плательщиков; {out} получателей; вход {node['in_sum']:.2f} KZT"
    elif out >= MIN_DISTRIBUTOR_OUTPUTS and out >= 2 * inc:
        role, score = "distributor", 0.5 + 0.5 * min(out / 20, 1)
        detail = f"выход к {out} получателям при {inc} плательщиках; выход {node['out_sum']:.2f} KZT"
    elif interpretable and inc > 0 and out > 0 and TRANSIT_RANGE[0] <= ratio <= TRANSIT_RANGE[1]:
        role, score = "transit", max(0.5, 1 - abs(1 - ratio))
        detail = f"входов {inc}, выходов {out}; наблюдаемый выход/вход {ratio:.3f}; вход {node['in_sum']:.2f} KZT"
    elif interpretable and node["in_sum"] > 0 and ratio <= MAX_TERMINAL_RATIO:
        role, score = "terminal", 0.5 + 0.5 * (1 - ratio / MAX_TERMINAL_RATIO)
        detail = f"наблюдаемый выход/вход {ratio:.3f} ≤ 0.2; вход {node['in_sum']:.2f} KZT; вне границы обхода"
    else:
        role, score = "peripheral", 0.2
        detail = f"входов {inc}, выходов {out}; вход {node['in_sum']:.2f}, выход {node['out_sum']:.2f} KZT; сильные правила не выполнены"
    evidence = f"Гипотеза {role}: {detail}."
    return role, round(min(max(score, 0), 1), 6), evidence[:200]


def analyze(nodes, edges):
    graph = nx.DiGraph()
    graph.add_nodes_from(int(row.gid) for row in nodes.itertuples(index=False))
    for row in edges.itertuples(index=False):
        graph.add_edge(int(row.src), int(row.dst), sum_kzt=float(row.sum_kzt), n_tx=int(row.n_tx))
    communities = sorted(nx.weakly_connected_components(graph), key=min)
    membership = {gid: i for i, group in enumerate(communities) for gid in group}
    between = nx.betweenness_centrality(graph, k=min(128, len(graph)), normalized=True, weight=None, seed=RANDOM_SEED)
    seed_ancestors = dict.fromkeys(graph, 0)
    for seed_gid in nodes.loc[nodes.is_seed, "gid"]:
        for reachable in nx.descendants(graph, int(seed_gid)):
            seed_ancestors[reachable] += 1
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
                        "boundary_censored": boundary, "seed_ancestors": seed_ancestors[gid],
                        "betweenness": float(between[gid]), "warnings": warnings})
        record = records[-1]
        record["role"], record["role_score"], record["evidence"] = classify_role(record)
    clusters = [{"cluster_id": i, "n_nodes": len(group),
                 "n_seed": sum(n["is_seed"] for n in records if int(n["gid"]) in group),
                 "sum_kzt_internal": math.fsum(d["sum_kzt"] for u, v, d in graph.edges(data=True) if u in group and v in group),
                 "top_gids": [str(g) for g in sorted(group)[:5]],
                 "hypothesis": f"Структурная группа: {len(group)} узлов; связи требуют проверки."}
                for i, group in enumerate(communities)]
    top = [{"rank": i + 1, "gid": n["gid"], "role": n["role"], "priority_score": n["priority_score"], "why": n["evidence"]}
           for i, n in enumerate(records[:50])]
    return records, clusters, top, graph
