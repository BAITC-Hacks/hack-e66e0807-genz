"""Behavior checks for the real parquet-to-artifact boundary."""
import csv
import math
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

    def test_blank_transaction_date_is_rejected(self):
        run = self.pipeline()
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            fixture(data)
            transactions = pd.read_parquet(data / "transactions.parquet")
            transactions.loc[0, "date"] = ""
            transactions.to_parquet(data / "transactions.parquet")
            with self.assertRaisesRegex(ValueError, "date"):
                run(data, data / "out")

    def test_duplicate_node_and_nonfinite_amount_are_rejected(self):
        run = self.pipeline()
        for invalid in ("duplicate", "infinite"):
            with self.subTest(invalid=invalid), tempfile.TemporaryDirectory() as tmp:
                data = Path(tmp)
                fixture(data)
                if invalid == "duplicate":
                    nodes = pd.read_parquet(data / "nodes.parquet")
                    pd.concat([nodes, nodes.iloc[:1]]).to_parquet(data / "nodes.parquet")
                    message = "duplicate gid"
                else:
                    edges = pd.read_parquet(data / "edges.parquet")
                    edges.loc[0, "sum_kzt"] = float("inf")
                    edges.to_parquet(data / "edges.parquet")
                    message = "finite"
                with self.assertRaisesRegex(ValueError, message):
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


class CommunityTests(unittest.TestCase):
    def test_weighted_communities_split_bridge_and_preserve_isolate(self):
        from solution.analytics import analyze
        nodes = pd.DataFrame({"gid": range(1, 8), "depth": [0, 1, 2, 1, 2, 3, 0], "is_seed": [True, False, False, False, False, False, True]})
        pairs = [(1, 2, 1000), (2, 3, 1000), (3, 1, 1000), (4, 5, 1000), (5, 6, 1000), (6, 4, 1000), (3, 4, 1)]
        edges = pd.DataFrame([{"src": a, "dst": b, "sum_kzt": float(w), "n_tx": 1} for a, b, w in pairs])
        records, clusters, top, _ = analyze(nodes, edges)
        by_gid = {n["gid"]: n for n in records}
        self.assertNotEqual(by_gid["1"]["cluster_id"], by_gid["4"]["cluster_id"])
        isolate = next(c for c in clusters if c["cluster_id"] == by_gid["7"]["cluster_id"])
        self.assertEqual(isolate["n_nodes"], 1)
        self.assertEqual(isolate["sum_kzt_internal"], 0)
        self.assertGreater(top[0]["priority_score"], 0)
        self.assertEqual(by_gid["7"]["priority_score"], 0)
        self.assertEqual(math.fsum(c["sum_kzt_internal"] for c in clusters), 6000)

    def test_real_pipeline_is_complete_and_csv_deterministic(self):
        from solution.pipeline import run_pipeline
        data = Path("FINANCE-CASE/data")
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "first", Path(tmp) / "second"
            report = run_pipeline(data, first)
            run_pipeline(data, second)
            expected = pd.read_parquet(data / "nodes.parquet")
            self.assertEqual({n["gid"] for n in report["nodes"]}, {str(g) for g in expected.gid})
            self.assertEqual(len(report["nodes"]), len(expected))
            self.assertGreaterEqual(len(report["top_nodes"]), 20)
            self.assertEqual(len({n["gid"] for n in report["top_nodes"]}), len(report["top_nodes"]))
            self.assertEqual(report["top_nodes"], sorted(report["top_nodes"], key=lambda n: (-n["priority_score"], int(n["gid"]))))
            for filename in ("nodes_roles.csv", "clusters.csv", "top_nodes.csv"):
                self.assertEqual((first / filename).read_bytes(), (second / filename).read_bytes())
            self.assertEqual(sum(c["n_nodes"] for c in report["clusters"]), len(expected))
            for n in report["nodes"]:
                self.assertTrue(math.isfinite(n["priority_score"]))
                self.assertTrue(0 <= n["priority_score"] <= 1)
                self.assertTrue(1 <= len(n["evidence"]) <= 200)
                if n["is_seed"] or n["in_sum"] == 0:
                    self.assertIsNone(n["pass_through"])
                if n["boundary_censored"] or n["is_seed"]:
                    self.assertNotEqual(n["role"], "terminal")


if __name__ == "__main__":
    unittest.main()
