"""Loopback-only static UI and explicitly allowlisted published data."""
import argparse
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from solution.assistant import (MAX_BODY, AssistantConfig, AssistantEvidenceError,
                                AssistantInputError, AssistantUnavailable, answer_question)

DATA_FILES = frozenset({"report.json", "nodes_roles.csv", "clusters.csv", "top_nodes.csv"})


def make_server(data_dir, ui_dir, port=8000):
    data_root, ui_root = Path(data_dir).resolve(), Path(ui_dir).resolve()
    if not (ui_root / "index.html").is_file():
        raise ValueError(f"Built UI missing: {ui_root / 'index.html'}; run npm --prefix frontend run build")
    for name in sorted(DATA_FILES):
        if not (data_root / name).is_file():
            raise ValueError(f"Published data missing: {data_root / name}; run python -m solution first")
    assistant_config = AssistantConfig.from_env()
    dev_origin = os.getenv("ASSISTANT_DEV_ORIGIN", AssistantConfig._local_env().get("ASSISTANT_DEV_ORIGIN", ""))
    parsed_dev_origin = urlsplit(dev_origin)
    if (parsed_dev_origin.scheme != "http" or parsed_dev_origin.hostname not in ("127.0.0.1", "localhost")
            or parsed_dev_origin.path or parsed_dev_origin.query or parsed_dev_origin.fragment):
        dev_origin = ""
    assistant_report = None
    if assistant_config.enabled:
        try:
            assistant_report = json.loads((data_root / "report.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            # Optional AI must never prevent the ordinary report/CSV UI from
            # being served, even when its snapshot cannot be decoded.
            assistant_report = None

    class Handler(SimpleHTTPRequestHandler):
        def _assistant_json(self, code, payload):
            data = json.dumps(payload, ensure_ascii=False, allow_nan=False).encode("utf-8")
            self.send_response(code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def _assistant_host_allowed(self):
            host = self.headers.get("Host", "")
            return host in (f"127.0.0.1:{self.server.server_port}",
                            f"localhost:{self.server.server_port}")

        def do_GET(self):
            if urlsplit(self.path).path == "/api/assistant/status":
                if not self._assistant_host_allowed():
                    self._assistant_json(403, {"status": "invalid_request", "error": "Invalid host"})
                    return
                status = assistant_config.status()
                if status["status"] == "ready" and assistant_report is None:
                    status = {**status, "status": "unavailable", "message": "Отчёт недоступен ассистенту."}
                self._assistant_json(200, status)
                return
            super().do_GET()

        def do_POST(self):
            if urlsplit(self.path).path != "/api/assistant/query" or urlsplit(self.path).query:
                self._assistant_json(404, {"status": "invalid_request", "error": "Unknown route"})
                return
            if not self._assistant_host_allowed():
                self._assistant_json(403, {"status": "invalid_request", "error": "Invalid host"})
                return
            origin = self.headers.get("Origin")
            if origin and origin not in (f"http://127.0.0.1:{self.server.server_port}",
                                         f"http://localhost:{self.server.server_port}", dev_origin):
                self._assistant_json(403, {"status": "invalid_request", "error": "Invalid origin"})
                return
            if not assistant_config.enabled:
                self._assistant_json(503, {"status": "disabled", "error": "Assistant is disabled"})
                return
            if not assistant_config.status()["configured"]:
                self._assistant_json(503, {"status": "unavailable", "error": "Assistant is not configured"})
                return
            if assistant_report is None:
                self._assistant_json(503, {"status": "unavailable", "error": "Assistant report unavailable"})
                return
            if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
                self._assistant_json(415, {"status": "invalid_request", "error": "JSON required"})
                return
            try:
                size = int(self.headers.get("Content-Length", ""))
            except ValueError:
                size = -1
            if not 1 <= size <= MAX_BODY:
                self._assistant_json(413, {"status": "invalid_request", "error": "Request size exceeds limit"})
                return
            try:
                payload = json.loads(self.rfile.read(size))
                if not isinstance(payload, dict) or set(payload) - {"question", "selected_gid"}:
                    raise AssistantInputError("Invalid request fields")
                result = answer_question(assistant_report, payload.get("question"), payload.get("selected_gid"), assistant_config)
            except AssistantEvidenceError:
                self._assistant_json(422, {"status": "insufficient_evidence", "error": "Недостаточно проверяемых данных для ответа."})
                return
            except AssistantUnavailable:
                self._assistant_json(503, {"status": "unavailable", "error": "Модель недоступна; отчёт и экспорты работают."})
                return
            except (AssistantInputError, ValueError, UnicodeError) as exc:
                self._assistant_json(400, {"status": "invalid_request", "error": str(exc)[:160]})
                return
            self._assistant_json(200, result)

        def send_head(self):
            try:
                route = unquote(urlsplit(self.path).path, errors="strict")
            except (UnicodeError, ValueError):
                self.send_error(400, "Invalid URL")
                return None
            if "\x00" in route or "\\" in route or any(part in ("..", ".") for part in route.split("/")):
                self.send_error(403, "Path traversal is forbidden")
                return None
            if route.startswith("/data/"):
                name = route.removeprefix("/data/")
                if name not in DATA_FILES:
                    self.send_error(404, "Unknown published file")
                    return None
                root, target = data_root, data_root / name
            else:
                root = ui_root
                target = ui_root / ("index.html" if route == "/" else route.lstrip("/"))
            resolved = target.resolve()
            if not resolved.is_relative_to(root):
                self.send_error(403, "Path outside published root")
                return None
            if not resolved.is_file():
                self.send_error(404, "File not found")
                return None
            try:
                stream = resolved.open("rb")
            except OSError:
                self.send_error(404, "File unavailable")
                return None
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(str(resolved)))
            self.send_header("Content-Length", str(resolved.stat().st_size))
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Cache-Control", "no-cache")
            if route.startswith("/data/") and resolved.suffix == ".csv":
                self.send_header("Content-Disposition", f'attachment; filename="{resolved.name}"')
            self.end_headers()
            return stream

        def log_message(self, format, *args):
            pass

    return ThreadingHTTPServer(("127.0.0.1", port), Handler)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Serve the local graph UI at http://127.0.0.1:8000")
    parser.add_argument("--data", type=Path, default=Path("output"))
    parser.add_argument("--ui", type=Path, default=Path("frontend/dist"))
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args(argv)
    try:
        server = make_server(args.data, args.ui, args.port)
    except (ValueError, OSError) as exc:
        parser.error(str(exc))
    print(f"Graph UI: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
