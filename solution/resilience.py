"""Fixed-priority node removal scenarios with explicit graph denominators."""
from __future__ import annotations

import networkx as nx


def _connectivity(graph, original_count):
    count = graph.number_of_nodes()
    components = list(nx.weakly_connected_components(graph))
    largest = max((len(component) for component in components), default=0)
    return {
        "n_nodes": count,
        "n_weak_components": len(components),
        "largest_component_nodes": largest,
        "n_isolates": nx.number_of_isolates(graph),
        "largest_share_surviving": largest / count if count else 0.0,
        "largest_share_original": largest / original_count if original_count else 0.0,
    }


def calculate_resilience(graph, top, max_n=20):
    """Return N=0..cap while leaving the original directed graph untouched."""
    priority = [str(item["gid"]) for item in top]
    cap = min(max_n, len(priority), graph.number_of_nodes())
    original_count = graph.number_of_nodes()
    baseline = _connectivity(graph, original_count)
    scenarios = []
    for n in range(cap + 1):
        removed = priority[:n]
        surviving = graph.subgraph(set(graph.nodes) - {int(gid) for gid in removed})
        scenarios.append({"n_removed": n, "removed_gids": removed,
                          **_connectivity(surviving, original_count)})
    return {"selection": "fixed-priority-prefix", "max_n": cap,
            "baseline": baseline, "scenarios": scenarios}
