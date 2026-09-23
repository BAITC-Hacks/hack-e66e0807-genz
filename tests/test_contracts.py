"""Independent delivery and local HTTP boundary tests."""
from pathlib import Path
import subprocess
import sys
import unittest
import tempfile
import threading
import urllib.request
import urllib.error
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

    def test_missing_build_or_export_is_clear_error(self):
        from solution.server import make_server
        with self.assertRaisesRegex(ValueError, "Built UI missing"):
            make_server(self.data, self.root / "missing", 0)
        (self.data / "report.json").unlink()
        with self.assertRaisesRegex(ValueError, "Published data missing"):
            make_server(self.data, self.ui, 0)


if __name__ == "__main__":
    unittest.main()
