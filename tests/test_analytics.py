"""Behavior checks for the real parquet-to-artifact boundary."""
import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd


def fixture(directory):
    pd.DataFrame({"gid": [1, 2, 3], "depth": [0, 1, 0],
                  "is_seed": [True, False, True]}).to_parquet(directory / "nodes.parquet")
    pd.DataFrame({"src": [1], "dst": [2], "sum_kzt": [10000.0],
                  "n_tx": [1], "depth": [1]}).to_parquet(directory / "edges.parquet")
    pd.DataFrame({"src": [1], "dst": [2], "sum_kzt": [10000.0],
                  "date": ["2026-07-01"]}).to_parquet(directory / "transactions.parquet")


class PipelineTests(unittest.TestCase):
    def pipeline(self):
        self.assertTrue(Path("solution/pipeline.py").exists(), "Parquet pipeline must exist")
        from solution.pipeline import run_pipeline
        return run_pipeline

    def test_parquet_pipeline_retains_isolate_and_writes_contract(self):
        run = self.pipeline()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            fixture(data)
            report = run(data, data / "out")
            self.assertEqual([n["gid"] for n in report["nodes"]], ["1", "2", "3"])
            self.assertEqual(report["schema_version"], "1.0")
            for node in report["nodes"]:
                self.assertTrue(node["role"])
                self.assertTrue(node["evidence"])
                self.assertTrue(0 <= node["priority_score"] <= 1)
            with (data / "out/nodes_roles.csv").open() as stream:
                self.assertEqual(next(csv.reader(stream)), ["gid", "role", "role_score", "cluster_id", "priority_score", "evidence"])
            self.assertTrue((data / "out/report.json").exists())
            self.assertTrue((data / "out/clusters.csv").exists())
            self.assertTrue((data / "out/top_nodes.csv").exists())

    def test_invalid_references_and_aggregate_disagreement_are_rejected(self):
        run = self.pipeline()
        for column, value, expected in [("src", 99, "unknown"), ("sum_kzt", 20000, "sum_kzt"), ("n_tx", 2, "n_tx")]:
            with self.subTest(column=column), tempfile.TemporaryDirectory() as tmp:
                data = Path(tmp)
                fixture(data)
                edges = pd.read_parquet(data / "edges.parquet")
                edges.loc[0, column] = value
                edges.to_parquet(data / "edges.parquet")
                with self.assertRaisesRegex(ValueError, expected):
                    run(data, data / "out")


class RoleTests(unittest.TestCase):
    def classify(self, **changes):
        import solution.analytics as analytics
        self.assertTrue(callable(getattr(analytics, "classify_role", None)), "Formal role classifier must exist")
        node = {"in_degree": 1, "out_degree": 1, "in_sum": 100000.0,
                "out_sum": 50000.0, "pass_through": 0.5, "is_seed": False,
                "boundary_censored": False, "seed_ancestors": 0, "betweenness": 0.0}
        node.update(changes)
        return analytics.classify_role(node)

    def test_all_six_roles_and_precedence(self):
        cases = [
            ("coordinator", {"in_degree": 6, "out_degree": 2, "seed_ancestors": 3, "betweenness": 0.001}),
            ("consolidator", {"in_degree": 3, "out_degree": 0, "pass_through": 0.0}),
            ("distributor", {"in_degree": 2, "out_degree": 5}),
            ("transit", {"pass_through": 0.8}),
            ("terminal", {"out_degree": 0, "pass_through": 0.0}),
            ("peripheral", {}),
        ]
        for expected, metrics in cases:
            with self.subTest(expected=expected):
                role, score, evidence = self.classify(**metrics)
                self.assertEqual(role, expected)
                self.assertTrue(0 <= score <= 1)
                self.assertTrue(1 <= len(evidence) <= 200)

    def test_seed_and_boundary_cannot_be_terminal(self):
        for changes in ({"is_seed": True, "pass_through": None}, {"boundary_censored": True, "pass_through": 0.0}):
            self.assertEqual(self.classify(out_degree=0, **changes)[0], "peripheral")

    def test_transit_and_terminal_threshold_boundaries(self):
        for ratio, expected in [(0.2, "terminal"), (0.20001, "peripheral"), (0.79999, "peripheral"), (0.8, "transit"), (1.2, "transit"), (1.20001, "peripheral")]:
            self.assertEqual(self.classify(pass_through=ratio)[0], expected)
        self.assertEqual(self.classify(in_degree=2, out_degree=0, pass_through=0)[0], "terminal")
        self.assertEqual(self.classify(in_degree=3, out_degree=0, pass_through=0)[0], "consolidator")


if __name__ == "__main__":
    unittest.main()
