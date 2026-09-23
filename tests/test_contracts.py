"""Independent delivery and local HTTP boundary tests."""
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
import threading
import urllib.request
import urllib.error
import json
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


class CliTests(unittest.TestCase):
    def test_cli_documents_data_and_output_arguments(self):
        result = subprocess.run([sys.executable, "-m", "solution", "--help"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--data", result.stdout)
        self.assertIn("--out", result.stdout)

    def test_missing_input_reports_path_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, "-m", "solution", "--data", directory],
                                    cwd=ROOT, capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing input file", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_forwards_custom_paths(self):
        from solution.__main__ import main
        import types
        fake = types.ModuleType("solution.pipeline")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            for name in ("nodes", "edges", "transactions"):
                (path / f"{name}.parquet").touch()
            with patch.dict(sys.modules, {"solution.pipeline": fake}):
                with patch.object(fake, "run_pipeline", create=True, return_value={
                    "meta": {"n_nodes": 1, "n_edges": 0, "n_transactions": 0, "elapsed_seconds": 0}
                }) as run:
                    self.assertEqual(main(["--data", directory, "--out", str(path / "result")]), 0)
                    run.assert_called_once_with(path, path / "result")


class ServerTests(unittest.TestCase):
    def setUp(self):
        from solution.server import DATA_FILES, make_server
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.data, self.ui = self.root / "data", self.root / "ui"
        self.data.mkdir()
        self.ui.mkdir()
        (self.ui / "index.html").write_text("<h1>Real built UI</h1>")
        for name in DATA_FILES:
            (self.data / name).write_text(f"content of {name}")
        (self.root / "secret.txt").write_text("secret outside roots")
        (self.ui / "escape.txt").symlink_to(self.root / "secret.txt")
        self.server = make_server(self.data, self.ui, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def stop(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def test_serves_exact_exports_and_ui(self):
        from solution.server import DATA_FILES
        self.assertEqual(self.server.server_address[0], "127.0.0.1")
        with urllib.request.urlopen(self.base) as response:
            self.assertEqual(response.read(), (self.ui / "index.html").read_bytes())
        for name in DATA_FILES:
            with urllib.request.urlopen(self.base + "/data/" + name) as response:
                self.assertEqual(response.read(), (self.data / name).read_bytes())
                self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")

    def test_rejects_traversal_symlinks_and_unknown_data(self):
        for path in ("/../secret.txt", "/%2e%2e/secret.txt", "/data/../secret.txt",
                     "/data/%2e%2e%2fsecret.txt", "/escape.txt", "/data/secret.txt", "/data/", "/missing.js"):
            with self.subTest(path=path), self.assertRaises(urllib.error.HTTPError) as error:
                urllib.request.urlopen(self.base + path)
            self.assertIn(error.exception.code, (403, 404))
            error.exception.close()

    def test_missing_build_or_export_is_clear_error(self):
        from solution.server import make_server
        with self.assertRaisesRegex(ValueError, "Built UI missing"):
            make_server(self.data, self.root / "missing", 0)
        (self.data / "report.json").unlink()
        with self.assertRaisesRegex(ValueError, "Published data missing"):
            make_server(self.data, self.ui, 0)


class ValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pandas as pd
        from solution.pipeline import run_pipeline
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        cls.data = Path(cls.tmp.name) / "inputs"
        cls.out = Path(cls.tmp.name) / "outputs"
        cls.data.mkdir()
        ids = [9007199254740993 + i for i in range(21)]
        pd.DataFrame({"gid": ids, "depth": [0] + [4] * 20, "is_seed": [True] + [False] * 20}).to_parquet(cls.data / "nodes.parquet")
        pd.DataFrame({"src": [ids[0]], "dst": [ids[1]], "sum_kzt": [10000.0], "n_tx": [1], "depth": [1]}).to_parquet(cls.data / "edges.parquet")
        pd.DataFrame({"src": [ids[0]], "dst": [ids[1]], "sum_kzt": [10000.0], "date": pd.to_datetime(["2025-07-01"])}).to_parquet(cls.data / "transactions.parquet")
        run_pipeline(cls.data, cls.out)
        cls.original = {p.name: p.read_bytes() for p in cls.out.iterdir() if p.is_file()}

    def setUp(self):
        for name, content in self.original.items():
            (self.out / name).write_bytes(content)

    def test_accepts_valid_exports_and_preserves_large_gid_and_isolates(self):
        from scripts.verify_delivery import validate_exports
        result = validate_exports(self.data, self.out)
        self.assertEqual(result["nodes"], 21)
        self.assertEqual(result["isolates"], 19)

    def test_rejects_csv_schema_missing_duplicate_gid_and_bad_evidence(self):
        from scripts.verify_delivery import validate_exports
        import csv
        path = self.out / "nodes_roles.csv"
        for mutation in ("schema", "missing", "duplicate", "score", "evidence", "empty_evidence", "cluster"):
            with self.subTest(mutation=mutation):
                self.setUp()
                with path.open(newline="") as stream:
                    reader = csv.DictReader(stream)
                    fields, rows = reader.fieldnames, list(reader)
                if mutation == "schema": fields = list(reversed(fields))
                elif mutation == "missing": rows.pop()
                elif mutation == "duplicate": rows[1]["gid"] = rows[0]["gid"]
                elif mutation == "score": rows[0]["role_score"] = "1.01"
                elif mutation == "evidence": rows[0]["evidence"] = "x" * 201
                elif mutation == "empty_evidence": rows[0]["evidence"] = ""
                elif mutation == "cluster": rows[0]["cluster_id"] = "999999"
                with path.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)
                with self.assertRaises(ValueError):
                    validate_exports(self.data, self.out)

    def test_rejects_nonstring_gid_nonfinite_json_and_rank_reference(self):
        from scripts.verify_delivery import validate_exports
        path = self.out / "report.json"
        for mutation in ("gid", "nan", "numeric_string", "rank", "cluster", "endpoint", "cluster_gid"):
            with self.subTest(mutation=mutation):
                self.setUp()
                report = json.loads(path.read_text())
                if mutation == "gid": report["nodes"][0]["gid"] = int(report["nodes"][0]["gid"])
                elif mutation == "nan": report["nodes"][0]["role_score"] = float("nan")
                elif mutation == "numeric_string": report["nodes"][0]["in_degree"] = "1"
                elif mutation == "rank": report["top_nodes"][0]["gid"] = "missing"
                elif mutation == "cluster": report["clusters"][0]["n_nodes"] += 1
                elif mutation == "endpoint": report["edges"][0]["src"] = int(report["edges"][0]["src"])
                elif mutation == "cluster_gid": report["clusters"][0]["top_gids"][0] = int(report["clusters"][0]["top_gids"][0])
                path.write_text(json.dumps(report))
                with self.assertRaises(ValueError):
                    validate_exports(self.data, self.out)

    def test_rejects_cluster_sums_and_top_rank_order(self):
        from scripts.verify_delivery import validate_exports
        import csv
        for filename, mutation in (("clusters.csv", "sum"), ("top_nodes.csv", "rank"), ("top_nodes.csv", "order")):
            with self.subTest(mutation=mutation):
                self.setUp()
                path = self.out / filename
                with path.open(newline="") as stream:
                    reader = csv.DictReader(stream)
                    fields, rows = reader.fieldnames, list(reader)
                if mutation == "sum": rows[0]["sum_kzt_internal"] = "99999999"
                elif mutation == "rank": rows[0]["rank"] = "2"
                else:
                    rows[0], rows[1] = rows[1], rows[0]
                    rows[0]["rank"], rows[1]["rank"] = "1", "2"
                with path.open("w", newline="") as stream:
                    writer = csv.DictWriter(stream, fieldnames=fields)
                    writer.writeheader()
                    writer.writerows(rows)
                with self.assertRaises(ValueError):
                    validate_exports(self.data, self.out)


if __name__ == "__main__":
    unittest.main()
