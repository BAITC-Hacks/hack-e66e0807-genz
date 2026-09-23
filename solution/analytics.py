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
    "priority": "0.30*L(in_sum+out_sum) + 0.25*L(in_degree+out_degree) + 0.20*L(seed_ancestors) + 0.25*B; L(x)=log1p(x)/log1p(max(x)); B=betweenness/max(betweenness); zero maxima contribute 0",
    "community": "Louvain on undirected projection: w(u,v)=sum_kzt(u,v)+sum_kzt(v,u), positive weights, resolution=1, seed=42; singleton isolates; cluster ids ordered by minimum numeric gid",
    "centrality": "Directed unweighted normalized betweenness; k=min(128,n), seed=42; monetary amounts are strengths, not shortest-path distances",
    "seed_ancestors": "Number of distinct other seed nodes with a directed path to this node; excludes the node itself; not an allegation",
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
    projection = nx.Graph()
    projection.add_nodes_from(graph.nodes)
    for source, destination, data in graph.edges(data=True):
        weight = data["sum_kzt"]
        if weight > 0:
            previous = projection.get_edge_data(source, destination, {}).get("weight", 0.0)
            projection.add_edge(source, destination, weight=previous + weight)
    communities = (nx.community.louvain_communities(projection, weight="weight", resolution=1, seed=RANDOM_SEED)
                   if projection.number_of_edges() else [{gid} for gid in graph])
    communities = sorted(communities, key=min)
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
    max_flow = max((n["in_sum"] + n["out_sum"] for n in records), default=0)
    max_degree = max((n["in_degree"] + n["out_degree"] for n in records), default=0)
    max_seeds = max((n["seed_ancestors"] for n in records), default=0)
    max_between = max(between.values(), default=0)

    def log_norm(value, maximum):
        return math.log1p(value) / math.log1p(maximum) if maximum > 0 else 0.0

    for node in records:
        node["priority_score"] = round(
            0.30 * log_norm(node["in_sum"] + node["out_sum"], max_flow)
            + 0.25 * log_norm(node["in_degree"] + node["out_degree"], max_degree)
            + 0.20 * log_norm(node["seed_ancestors"], max_seeds)
            + 0.25 * (node["betweenness"] / max_between if max_between > 0 else 0), 6)
    ranked = sorted(records, key=lambda n: (-n["priority_score"], int(n["gid"])))
    by_gid = {int(n["gid"]): n for n in records}
    clusters = [{"cluster_id": i, "n_nodes": len(group),
                 "n_seed": sum(n["is_seed"] for n in records if int(n["gid"]) in group),
                 "sum_kzt_internal": math.fsum(d["sum_kzt"] for u, v, d in graph.edges(data=True) if u in group and v in group),
                 "top_gids": [str(g) for g in sorted(group, key=lambda g: (-by_gid[g]["priority_score"], g))[:5]],
                 "hypothesis": f"Гипотеза сообщества: {len(group)} узлов, {sum(by_gid[g]['is_seed'] for g in group)} seed; денежные связи не доказывают общий контроль."}
                for i, group in enumerate(communities)]
    top = [{"rank": i + 1, "gid": n["gid"], "role": n["role"], "priority_score": n["priority_score"],
            "why": f"Приоритет проверки {n['priority_score']:.3f}: оборот {n['in_sum']+n['out_sum']:.2f} KZT; связей {n['in_degree']+n['out_degree']}; путей от seed {n['seed_ancestors']}; посредничество {n['betweenness']:.5f}."}
           for i, n in enumerate(ranked[:50])]
    return records, clusters, top, graph
