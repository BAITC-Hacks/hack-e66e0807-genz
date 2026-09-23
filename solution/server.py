"""Loopback-only static UI and explicitly allowlisted published data."""
import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

DATA_FILES = frozenset({"report.json", "nodes_roles.csv", "clusters.csv", "top_nodes.csv"})


def make_server(data_dir, ui_dir, port=8000):
    data_root, ui_root = Path(data_dir).resolve(), Path(ui_dir).resolve()
    if not (ui_root / "index.html").is_file():
        raise ValueError(f"Built UI missing: {ui_root / 'index.html'}; run npm --prefix frontend run build")
    for name in sorted(DATA_FILES):
        if not (data_root / name).is_file():
            raise ValueError(f"Published data missing: {data_root / name}; run python -m solution first")

    class Handler(SimpleHTTPRequestHandler):
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
