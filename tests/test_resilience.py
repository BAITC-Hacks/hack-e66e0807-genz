"""Fixed-priority induced survivor graph scenarios."""
import unittest

import networkx as nx

from solution.resilience import calculate_resilience


class ResilienceTests(unittest.TestCase):
    def test_isolates_denominators_and_empty_survivors(self):
        graph = nx.DiGraph()
        graph.add_nodes_from([1, 2, 3])
        graph.add_edges_from([(1, 2), (2, 3)])
        top = [{"gid": str(gid)} for gid in [2, 1, 3]]
        before = set(graph.edges)
        data = calculate_resilience(graph, top)
        self.assertEqual(data["selection"], "fixed-priority-prefix")
        self.assertEqual([s["n_removed"] for s in data["scenarios"]], [0, 1, 2, 3])
        self.assertEqual(data["baseline"], {key: value for key, value in data["scenarios"][0].items()
                                             if key not in ("n_removed", "removed_gids")})
        one = data["scenarios"][1]
        self.assertEqual(one["removed_gids"], ["2"])
        self.assertEqual((one["n_weak_components"], one["n_isolates"], one["largest_component_nodes"]), (2, 2, 1))
        self.assertEqual((one["largest_share_surviving"], one["largest_share_original"]), (0.5, 1 / 3))
        self.assertEqual(data["scenarios"][3]["largest_share_surviving"], 0)
        self.assertEqual(data["scenarios"][3]["largest_share_original"], 0)
        self.assertEqual(set(graph.edges), before)

    def test_cap(self):
        graph = nx.DiGraph()
        graph.add_nodes_from(range(30))
        data = calculate_resilience(graph, [{"gid": str(n)} for n in range(30)])
        self.assertEqual(data["max_n"], 20)
        self.assertEqual(len(data["scenarios"]), 21)
        self.assertEqual(data["baseline"]["n_isolates"], 30)


if __name__ == "__main__":
    unittest.main()
