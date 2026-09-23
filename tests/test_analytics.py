"""Behavior checks for the real parquet-to-artifact boundary."""
import csv
import importlib.util
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


if __name__ == "__main__":
    unittest.main()
