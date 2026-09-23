"""Directed route chronology and bounded enumeration."""
import tempfile
import unittest
from pathlib import Path

from solution.pipeline import run_pipeline
from tests.test_temporal import write_fixture


class RouteTests(unittest.TestCase):
    def test_strict_recurrence_same_day_and_canonical_cycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            write_fixture(data, [(1, 0, True), (2, 1, False), (3, 2, False), (4, 4, False)], [
                (1, 2, 5000, "2026-07-01"), (2, 3, 6000, "2026-07-02"),
                (3, 1, 7000, "2026-07-03"),
                (1, 2, 5000, "2026-07-10"), (2, 3, 6000, "2026-07-11"),
                (3, 1, 7000, "2026-07-12"),
                (1, 2, 5000, "2026-07-15"), (2, 3, 6000, "2026-07-15"),
            ])
            routes = run_pipeline(data, data / "out")["routes"]
            path = next(item for item in routes["paths"] if item["gids"] == ["1", "2", "3"])
            self.assertEqual(path["strict_episode_days"], 2)
            self.assertTrue(path["repeated"])
            self.assertEqual(path["same_day_ambiguous_examples"][0]["dates"],
                             ["2026-07-15", "2026-07-15"])
            cycle = next(item for item in routes["cycles"] if item["gids"] == ["1", "2", "3"])
            self.assertEqual(cycle["strict_episode_days"], 2)
            self.assertEqual([leg["src"] for leg in cycle["legs"]], ["1", "2", "3"])
            self.assertFalse(any("4" in item["gids"] for item in routes["paths"] + routes["cycles"]))

    def test_order_independent_numeric_gid_and_self_loop_exclusion(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            nodes = [(100000000000000002, 0, True), (100000000000000010, 1, False),
                     (100000000000000003, 2, False)]
            tx = [(nodes[0][0], nodes[1][0], 5000, "2026-07-01"),
                  (nodes[1][0], nodes[2][0], 5000, "2026-07-02"),
                  (nodes[1][0], nodes[1][0], 5000, "2026-07-03")]
            write_fixture(data, nodes, tx)
            first = run_pipeline(data, data / "out1")["routes"]
            write_fixture(data, list(reversed(nodes)), list(reversed(tx)))
            second = run_pipeline(data, data / "out2")["routes"]
            self.assertEqual(first, second)
            self.assertEqual(first["paths"][0]["gids"],
                             [str(nodes[0][0]), str(nodes[1][0]), str(nodes[2][0])])
            self.assertEqual(first["cycles"], [])

    def test_date_budget_marks_incomplete_search(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            tx = ([(1, 2, 5000, "2026-07-01")] * 50 +
                  [(2, 3, 5000, "2026-07-02")] * 50)
            write_fixture(data, [(1, 0, True), (2, 1, False), (3, 2, False)], tx)
            path = run_pipeline(data, data / "out")["routes"]["paths"][0]
            self.assertTrue(path["date_search_truncated"])
            self.assertEqual(path["strict_episode_days"], 1)
            self.assertFalse(path["repeated"])
            self.assertTrue(any("ограничен" in text for text in path["limitations"]))


if __name__ == "__main__":
    unittest.main()
