"""Calendar evidence at the public parquet-to-report boundary."""
import csv
import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from solution.analytics import analyze
from solution.pipeline import CSV_SCHEMAS, load_and_validate, run_pipeline


def write_fixture(directory, node_rows, transaction_rows):
    pd.DataFrame(node_rows, columns=["gid", "depth", "is_seed"]).astype(
        {"gid": "int64", "depth": "int64", "is_seed": "bool"}
    ).to_parquet(directory / "nodes.parquet")
    transactions = pd.DataFrame(transaction_rows, columns=["src", "dst", "sum_kzt", "date"])
    transactions = transactions.astype({"src": "int64", "dst": "int64", "sum_kzt": "float64"})
    transactions.to_parquet(directory / "transactions.parquet")
    edges = transactions.groupby(["src", "dst"], as_index=False).agg(
        sum_kzt=("sum_kzt", "sum"), n_tx=("sum_kzt", "size")
    )
    edges["depth"] = edges.dst.map(dict((gid, depth) for gid, depth, _ in node_rows)).astype("int64")
    edges.to_parquet(directory / "edges.parquet")


class TemporalPipelineTests(unittest.TestCase):
    def test_one_day_observation_reaches_json_without_changing_exports(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            write_fixture(data,
                          [(1, 0, True), (2, 1, False), (3, 2, False), (4, 0, False)],
                          [(1, 2, 100.0, "2026-07-01"), (2, 3, 80.0, "2026-07-02")])
            nodes, edges, _ = load_and_validate(data)
            original, _, _, _ = analyze(nodes, edges)
            report = run_pipeline(data, data / "out")
            saved = json.loads((data / "out/report.json").read_text(encoding="utf-8"))
            self.assertEqual(saved["schema_version"], "1.0")
            by_gid = {node["gid"]: node for node in saved["nodes"]}
            temporal = by_gid["2"]["temporal"]
            self.assertEqual(temporal["outgoing_after_1d_count"], 1)
            self.assertEqual(temporal["outgoing_after_1_or_2d_count"], 1)
            self.assertEqual(temporal["after_1_or_2d_examples"], [
                {"incoming_date": "2026-07-01", "outgoing_date": "2026-07-02"}])
            self.assertTrue(any("2" in request for request in by_gid["2"]["next_data_requests"]))
            for before in original:
                after = by_gid[before["gid"]]
                self.assertEqual((after["role"], after["role_score"], after["priority_score"]),
                                 (before["role"], before["role_score"], before["priority_score"]))
            self.assertEqual(report["nodes"], saved["nodes"])
            for filename, expected in CSV_SCHEMAS.items():
                with (data / "out" / filename).open(newline="") as stream:
                    self.assertEqual(next(csv.reader(stream)), expected)

    def test_two_day_window_deduplicates_outgoing_and_excludes_same_day_and_reverse(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            write_fixture(data,
                          [(1, 0, True), (2, 0, True), (10, 1, False), (11, 2, False)],
                          [(1, 10, 10.0, "2026-07-01"), (2, 10, 20.0, "2026-07-01"),
                           (10, 11, 5.0, "2026-06-30"), (10, 11, 5.0, "2026-07-01"),
                           (10, 11, 5.0, "2026-07-03"), (10, 11, 5.0, "2026-07-03"),
                           (2, 10, 30.0, "2026-07-03")])
            temporal = next(node["temporal"] for node in run_pipeline(data, data / "out")["nodes"]
                            if node["gid"] == "10")
            self.assertEqual(temporal["outgoing_after_1d_count"], 0)
            self.assertEqual(temporal["outgoing_after_1_or_2d_count"], 2)
            self.assertEqual(temporal["after_1_or_2d_examples"], [
                {"incoming_date": "2026-07-01", "outgoing_date": "2026-07-03"}])

    def test_profile_synchronous_peak_and_depth_boundary_are_observations(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            write_fixture(data,
                          [(1, 0, True), (2, 0, True), (3, 0, True), (10, 4, False),
                           (11, 2, False), (12, 1, False), (13, 0, False)],
                          [(1, 10, 10.0, "2026-07-01"), (1, 10, 20.0, "2026-07-01"),
                           (2, 10, 30.0, "2026-07-01"), (3, 10, 40.0, "2026-07-01"),
                           (10, 11, 5.0, "2026-07-03"), (10, 11, 5.0, "2026-07-03"),
                           (10, 11, 5.0, "2026-07-03"), (10, 11, 5.0, "2026-07-03"),
                           (12, 13, 2.0, "2026-07-05")])
            nodes = {node["gid"]: node for node in run_pipeline(data, data / "out")["nodes"]}
            node = nodes["10"]
            temporal = node["temporal"]
            self.assertEqual(temporal["incoming_profile"], {
                "active_days": 1, "total_kzt": 100.0, "distinct_payers": 3, "median_kzt": 25.0})
            self.assertEqual(temporal["synchronous_incoming"], {
                "date": "2026-07-01", "distinct_payers": 3, "tx_count": 4, "sum_kzt": 100.0})
            self.assertEqual(temporal["peak_day"], {
                "date": "2026-07-01", "count": 4, "share": 0.5, "baseline_daily_count": 1.6})
            self.assertTrue(node["boundary_censored"])
            self.assertNotEqual(node["role"], "terminal")
            self.assertTrue(any("10" in item and "depth=4" in item
                                for item in node["next_data_requests"]))
            self.assertTrue(any("10" in item and "врем" in item.lower()
                                for item in node["next_data_requests"]))
            self.assertTrue(any("1" in item and "входящ" in item.lower()
                                for item in nodes["1"]["next_data_requests"]))
            self.assertTrue(any("12" in item and "входящ" in item.lower()
                                for item in nodes["12"]["next_data_requests"]))
            self.assertTrue(any("13" in item and "период" in item.lower()
                                for item in nodes["13"]["next_data_requests"]))

    def test_isolate_self_loop_and_sorted_three_examples(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            write_fixture(data,
                          [(1, 0, True), (2, 1, False), (3, 1, False), (4, 0, False)],
                          [(1, 2, 10.0, "2026-07-01"), (1, 2, 10.0, "2026-07-02"),
                           (1, 2, 10.0, "2026-07-03"), (2, 2, 10.0, "2026-07-03"),
                           (2, 3, 10.0, "2026-07-03"), (2, 3, 10.0, "2026-07-04"),
                           (2, 3, 10.0, "2026-07-05")])
            nodes = {node["gid"]: node for node in run_pipeline(data, data / "out")["nodes"]}
            self.assertEqual(nodes["2"]["temporal"]["peak_day"]["count"], 3)
            self.assertEqual(nodes["2"]["temporal"]["after_1_or_2d_examples"], [
                {"incoming_date": "2026-07-01", "outgoing_date": "2026-07-03"},
                {"incoming_date": "2026-07-02", "outgoing_date": "2026-07-03"},
                {"incoming_date": "2026-07-02", "outgoing_date": "2026-07-04"}])
            self.assertEqual(nodes["4"]["temporal"]["incoming_tx_count"], 0)
            self.assertEqual(nodes["4"]["temporal"]["outgoing_tx_count"], 0)
            self.assertEqual(nodes["4"]["temporal"]["peak_day"], None)
            self.assertEqual(nodes["4"]["temporal"]["incoming_profile"], {
                "active_days": 0, "total_kzt": 0.0, "distinct_payers": 0, "median_kzt": 0.0})

    def test_invalid_date_never_becomes_temporal_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = Path(tmp)
            write_fixture(data, [(1, 0, True), (2, 1, False)],
                          [(1, 2, 10.0, "not-a-date")])
            with self.assertRaisesRegex(ValueError, "date"):
                run_pipeline(data, data / "out")
            self.assertFalse((data / "out/report.json").exists())


if __name__ == "__main__":
    unittest.main()
