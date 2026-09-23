"""Same-depth robust flags and observed near-cutoff semantics."""
import unittest

import pandas as pd

from solution.anomalies import enrich_anomalies


def record(gid, depth=1, seed=False, boundary=False, incoming=1, outgoing=1):
    return {"gid": str(gid), "depth": depth, "is_seed": seed,
            "boundary_censored": boundary, "in_degree": incoming,
            "out_degree": outgoing, "in_sum": incoming * 5000.0,
            "out_sum": outgoing * 5000.0,
            "temporal": {"incoming_tx_count": incoming,
                         "outgoing_tx_count": outgoing}}


class AnomalyTests(unittest.TestCase):
    def test_small_peer_cohort_has_no_flags(self):
        nodes = [record(n, incoming=100 if n == 1 else 1) for n in range(1, 11)]
        enriched = enrich_anomalies(nodes, pd.DataFrame(columns=["src", "dst", "sum_kzt"]))
        self.assertTrue(all(node["anomalies"] == [] for node in enriched))

    def test_zero_mad_requires_twenty_peers_and_null_deviation(self):
        nodes = [record(n, incoming=100 if n == 1 else 1) for n in range(1, 22)]
        enriched = enrich_anomalies(nodes, pd.DataFrame(columns=["src", "dst", "sum_kzt"]))
        flags = [f for f in enriched[0]["anomalies"] if f["metric"] == "in_degree"]
        self.assertEqual(len(flags), 1)
        self.assertEqual(flags[0]["peer_n"], 20)
        self.assertEqual(flags[0]["peer_median"], 1)
        self.assertEqual(flags[0]["peer_mad"], 0)
        self.assertIsNone(flags[0]["deviation"])
        self.assertEqual(enriched[1]["anomalies"], [])

    def test_incoming_seed_and_outgoing_boundary_are_excluded(self):
        nodes = [record(n, depth=4, seed=n == 1, boundary=n == 2,
                        incoming=100 if n == 1 else 1,
                        outgoing=100 if n == 2 else 1) for n in range(1, 24)]
        enriched = enrich_anomalies(nodes, pd.DataFrame(columns=["src", "dst", "sum_kzt"]))
        self.assertFalse(any(f["metric"] in ("in_degree", "in_sum", "incoming_tx_count") for f in enriched[0]["anomalies"]))
        self.assertFalse(any(f["metric"] in ("out_degree", "out_sum", "outgoing_tx_count") for f in enriched[1]["anomalies"]))

    def test_near_cutoff_uses_observed_incident_rows_once_for_self_loop(self):
        nodes = [record(n) for n in range(1, 23)]
        rows = [(1, 1, 6000.0)] * 20 + [(1, 2, 12000.0)] * 2
        rows += [(n, 2, 12000.0) for n in range(3, 23)]
        tx = pd.DataFrame(rows, columns=["src", "dst", "sum_kzt"])
        enriched = enrich_anomalies(nodes, tx)
        flags = [f for f in enriched[0]["anomalies"] if f["metric"] == "near_cutoff_share"]
        self.assertEqual(len(flags), 1)
        self.assertAlmostEqual(flags[0]["value"], 20 / 22)
        self.assertIn("20 из 22", flags[0]["method"])
        self.assertTrue(any("ниже 5000" in text for text in flags[0]["limitations"]))


if __name__ == "__main__":
    unittest.main()
