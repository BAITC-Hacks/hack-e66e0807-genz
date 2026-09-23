"""Independent acceptance checks; does not import analytics implementation."""
import argparse
import csv
import json
import math
import subprocess
import sys
import tempfile
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SCHEMAS = {
    "nodes_roles.csv": ["gid", "role", "role_score", "cluster_id", "priority_score", "evidence"],
    "clusters.csv": ["cluster_id", "n_nodes", "n_seed", "sum_kzt_internal", "top_gids", "hypothesis"],
    "top_nodes.csv": ["rank", "gid", "role", "priority_score", "why"],
}
ROLES = {"consolidator", "transit", "distributor", "terminal", "coordinator", "peripheral"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite_tree(value):
    if isinstance(value, float):
        require(math.isfinite(value), "JSON contains non-finite number")
    elif isinstance(value, dict):
        for item in value.values():
            finite_tree(item)
    elif isinstance(value, list):
        for item in value:
            finite_tree(item)


def load_exports(out_dir):
    out_dir = Path(out_dir)
    tables = {}
    for name, schema in SCHEMAS.items():
        with (out_dir / name).open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            require(reader.fieldnames == schema, f"Wrong schema: {name}")
            tables[name] = list(reader)
    report = json.loads((out_dir / "report.json").read_text(encoding="utf-8"))
    finite_tree(report)
    require(report.get("schema_version") == "1.0", "Unsupported schema_version")
    return tables, report


def validate_exports(data_dir, out_dir):
    import pandas as pd
    tables, report = load_exports(out_dir)
    nodes_input = pd.read_parquet(Path(data_dir) / "nodes.parquet").to_dict("records")
    edges_input = pd.read_parquet(Path(data_dir) / "edges.parquet").to_dict("records")
    tx_input = pd.read_parquet(Path(data_dir) / "transactions.parquet").to_dict("records")
    expected = {str(row["gid"]): row for row in nodes_input}
    require(len(expected) == len(nodes_input), "Source gid duplicates")
    rows = tables["nodes_roles.csv"]
    require(len(rows) == len(expected) and {r["gid"] for r in rows} == set(expected),
            "Role CSV missing or duplicate gid")
    json_nodes = report["nodes"]
    require(all(type(n["gid"]) is str for n in json_nodes), "JSON gid must be string")
    require(len(json_nodes) == len(expected) and {n["gid"] for n in json_nodes} == set(expected),
            "JSON nodes missing or duplicate gid")
    by_gid = {n["gid"]: n for n in json_nodes}
    membership, seeds, internal = Counter(), Counter(), defaultdict(float)
    incoming, outgoing = defaultdict(set), defaultdict(set)
    in_sum, out_sum = defaultdict(float), defaultdict(float)
    for edge in edges_input:
        src, dst = str(edge["src"]), str(edge["dst"])
        incoming[dst].add(src)
        outgoing[src].add(dst)
        in_sum[dst] += edge["sum_kzt"]
        out_sum[src] += edge["sum_kzt"]
        if by_gid[src]["cluster_id"] == by_gid[dst]["cluster_id"]:
            internal[by_gid[src]["cluster_id"]] += edge["sum_kzt"]
    isolates = 0
    for row in rows:
        gid = row["gid"]
        node, source = by_gid[gid], expected[gid]
        require(row["role"] in ROLES and node["role"] == row["role"], f"Invalid role: {gid}")
        for key in ("role_score", "priority_score"):
            score = float(row[key])
            require(math.isfinite(score) and 0 <= score <= 1, f"Invalid {key}: {gid}")
            require(abs(score - node[key]) <= 1e-6, f"JSON/CSV {key} mismatch: {gid}")
        require(1 <= len(row["evidence"]) <= 200, f"Invalid evidence: {gid}")
        require(row["evidence"] == node["evidence"], f"Evidence mismatch: {gid}")
        cluster = int(row["cluster_id"])
        require(type(node["cluster_id"]) is int and cluster == node["cluster_id"], "Cluster mismatch")
        membership[cluster] += 1
        seeds[cluster] += int(source["is_seed"])
        require(node["depth"] == source["depth"] and node["is_seed"] == bool(source["is_seed"]), "Source metadata changed")
        require(node["in_degree"] == len(incoming[gid]) and node["out_degree"] == len(outgoing[gid]), "Degree mismatch")
        require(abs(node["in_sum"] - in_sum[gid]) <= .01 and abs(node["out_sum"] - out_sum[gid]) <= .01, "Node sum mismatch")
        require(node["boundary_censored"] == (source["depth"] >= 4), "Boundary flag mismatch")
        if source["is_seed"] or in_sum[gid] == 0:
            require(node["pass_through"] is None, "Seed/zero-input pass-through must be null")
        else:
            require(isinstance(node["pass_through"], (float, int)) and abs(node["pass_through"] - out_sum[gid] / in_sum[gid]) <= 1e-6, "Pass-through ratio mismatch")
        if source["is_seed"] or source["depth"] >= 4:
            require(node["role"] != "terminal", "Seed/boundary must not be terminal")
        if not incoming[gid] and not outgoing[gid]:
            isolates += 1
            require(node["role"] == "peripheral", "Isolate must be peripheral")
    clusters = tables["clusters.csv"]
    require(len(clusters) == len(membership) and {int(c["cluster_id"]) for c in clusters} == set(membership), "Cluster coverage mismatch")
    json_clusters = {c["cluster_id"]: c for c in report["clusters"]}
    require(len(json_clusters) == len(report["clusters"]) == len(clusters), "JSON cluster duplicates")
    for cluster in clusters:
        cid = int(cluster["cluster_id"])
        require(int(cluster["n_nodes"]) == membership[cid], "Cluster n_nodes mismatch")
        require(int(cluster["n_seed"]) == seeds[cid], "Cluster n_seed mismatch")
        require(abs(float(cluster["sum_kzt_internal"]) - internal[cid]) <= .01, "Cluster internal sum mismatch")
        top_gids = cluster["top_gids"].split(";") if cluster["top_gids"] else []
        require(bool(top_gids) and len(set(top_gids)) == len(top_gids), "Invalid cluster top_gids")
        require(all(g in by_gid and by_gid[g]["cluster_id"] == cid for g in top_gids), "Cluster top gid membership mismatch")
        require(all(type(g) is str for g in json_clusters[cid]["top_gids"]), "JSON cluster gid must be string")
        for key in ("n_nodes", "n_seed"):
            require(int(cluster[key]) == json_clusters[cid][key], "JSON cluster count mismatch")
        require(abs(float(cluster["sum_kzt_internal"]) - json_clusters[cid]["sum_kzt_internal"]) <= .01, "JSON cluster sum mismatch")
        require(top_gids == json_clusters[cid]["top_gids"], "JSON cluster top_gids mismatch")
        require(bool(cluster["hypothesis"].strip()), "Empty cluster hypothesis")
        require(cluster["hypothesis"] == json_clusters[cid]["hypothesis"], "JSON cluster hypothesis mismatch")
    top = tables["top_nodes.csv"]
    require(len(top) >= min(20, len(expected)), "Top list shorter than 20")
    require([int(r["rank"]) for r in top] == list(range(1, len(top) + 1)), "Top ranks not consecutive")
    require(len({r["gid"] for r in top}) == len(top), "Top gid duplicates")
    ranked = sorted(json_nodes, key=lambda n: (-n["priority_score"], int(n["gid"])))
    require([r["gid"] for r in top] == [n["gid"] for n in ranked[:len(top)]], "Top ordering mismatch")
    require(len(report["top_nodes"]) == len(top), "JSON top length mismatch")
    for row, record in zip(top, report["top_nodes"]):
        require(type(record["gid"]) is str and row["gid"] == record["gid"], "JSON top gid mismatch")
        node = by_gid[row["gid"]]
        require(row["role"] == node["role"] == record["role"], "Top role mismatch")
        require(abs(float(row["priority_score"]) - node["priority_score"]) <= 1e-6, "Top score mismatch")
        require(abs(record["priority_score"] - node["priority_score"]) <= 1e-6, "JSON top score mismatch")
        require(int(row["rank"]) == record["rank"] and row["why"] == record["why"], "JSON top text/rank mismatch")
        require(1 <= len(row["why"]) <= 200, "Invalid top evidence")
    require(len(report["edges"]) == len(edges_input), "JSON edge count mismatch")
    edge_map = {(str(e["src"]), str(e["dst"])): e for e in edges_input}
    seen = set()
    for edge in report["edges"]:
        require(type(edge["src"]) is str and type(edge["dst"]) is str, "JSON endpoints must be strings")
        key = (edge["src"], edge["dst"])
        require(key in edge_map and key not in seen, "JSON invalid/duplicate edge")
        seen.add(key)
        require(abs(edge["sum_kzt"] - edge_map[key]["sum_kzt"]) <= .01, "Edge sum mismatch")
        require(edge["n_tx"] == edge_map[key]["n_tx"], "Edge transaction count mismatch")
    meta = report["meta"]
    for key, count in (("n_nodes", len(expected)), ("n_edges", len(edges_input)),
                       ("n_transactions", len(tx_input)), ("n_seed", sum(seeds.values()))):
        require(meta[key] == count, f"Metadata {key} mismatch")
    total = sum(t["sum_kzt"] for t in tx_input)
    require(abs(meta["total_kzt"] - total) <= .01, "Total transactions sum mismatch")
    require(abs(sum(e["sum_kzt"] for e in edges_input) - total) <= .01, "Input edge/transaction sum mismatch")
    require(sum(e["n_tx"] for e in edges_input) == len(tx_input), "Input transaction count mismatch")
    if tx_input:
        dates = [pd.Timestamp(t["date"]).date().isoformat() for t in tx_input]
        require(meta["period_start"] == min(dates) and meta["period_end"] == max(dates), "Date range mismatch")
    return {"nodes": len(expected), "edges": len(edges_input), "transactions": len(tx_input),
            "seeds": sum(seeds.values()), "isolates": isolates, "clusters": len(clusters), "total_kzt": round(total, 2)}


def verify_http(out_dir, ui_dir):
    from solution.server import DATA_FILES, make_server
    server = make_server(out_dir, ui_dir, 0)
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urlopen(base) as response:
            require(response.read() == (Path(ui_dir) / "index.html").read_bytes(), "UI bytes mismatch")
        for name in DATA_FILES:
            with urlopen(base + "/data/" + name) as response:
                require(response.read() == (Path(out_dir) / name).read_bytes(), f"HTTP bytes mismatch: {name}")
        return base, server, worker
    except Exception:
        server.shutdown()
        server.server_close()
        worker.join()
        raise


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "FINANCE-CASE/data")
    parser.add_argument("--out", type=Path, default=ROOT / "output")
    parser.add_argument("--ui", type=Path, default=ROOT / "frontend/dist")
    parser.add_argument("--browser", action="store_true", help="also run frontend browser smoke (requires browser installation)")
    args = parser.parse_args(argv)
    timings = []
    with tempfile.TemporaryDirectory(prefix="money-graph-verify-") as repeat:
        outputs = (args.out.resolve(), Path(repeat))
        for output in outputs:
            started = time.perf_counter()
            subprocess.run([sys.executable, "-m", "solution", "--data", str(args.data.resolve()), "--out", str(output)], cwd=ROOT, check=True, timeout=300)
            elapsed = time.perf_counter() - started
            require(elapsed < 300, "Full batch exceeds 300 seconds")
            timings.append(round(elapsed, 3))
            counts = validate_exports(args.data, output)
        for name in SCHEMAS:
            require((outputs[0] / name).read_bytes() == (outputs[1] / name).read_bytes(), f"Non-deterministic CSV: {name}")
        reports = [load_exports(output)[1] for output in outputs]
        for report in reports:
            report["meta"].pop("elapsed_seconds")
        require(reports[0] == reports[1], "Non-deterministic JSON apart from elapsed_seconds")
    base, server, worker = verify_http(args.out, args.ui)
    try:
        if args.browser:
            subprocess.run(["node", "frontend/scripts/ui-smoke.mjs", base], cwd=ROOT, check=True, timeout=120)
    finally:
        server.shutdown()
        server.server_close()
        worker.join()
    result = {"status": "PASS", "counts": counts, "batch_seconds": timings,
              "deterministic_csv_and_json": True, "http_exports": True,
              "browser": "PASS" if args.browser else "separate browser verification required"}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, subprocess.SubprocessError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
