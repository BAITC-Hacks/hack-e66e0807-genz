"""Validate organizer inputs and export the versioned local report contract."""
from __future__ import annotations

import csv
import json
import math
import time
from pathlib import Path

import pandas as pd

from .analytics import analyze

CSV_SCHEMAS = {
    "nodes_roles.csv": ["gid", "role", "role_score", "cluster_id", "priority_score", "evidence"],
    "clusters.csv": ["cluster_id", "n_nodes", "n_seed", "sum_kzt_internal", "top_gids", "hypothesis"],
    "top_nodes.csv": ["rank", "gid", "role", "priority_score", "why"],
}
REQUIRED_COLUMNS = {
    "nodes": {"gid", "depth", "is_seed"},
    "edges": {"src", "dst", "sum_kzt", "n_tx", "depth"},
    "transactions": {"src", "dst", "sum_kzt", "date"},
}


def load_and_validate(data_dir: Path):
    tables = {}
    for name, required in REQUIRED_COLUMNS.items():
        path = data_dir / f"{name}.parquet"
        if not path.is_file():
            raise ValueError(f"Missing input: {path}")
        table = pd.read_parquet(path)
        missing = required - set(table.columns)
        if missing:
            raise ValueError(f"{name}: missing columns {sorted(missing)}")
        if table[list(required)].isna().any().any():
            raise ValueError(f"{name}: null values in required columns")
        for column in required & {"gid", "src", "dst", "depth", "n_tx"}:
            if not pd.api.types.is_integer_dtype(table[column]):
                raise ValueError(f"{name}.{column}: integer values required (identifier precision must be preserved)")
        for column in required & {"depth", "n_tx", "sum_kzt"}:
            if not pd.api.types.is_numeric_dtype(table[column]) or not table[column].map(math.isfinite).all() or (table[column] < 0).any():
                raise ValueError(f"{name}.{column}: finite nonnegative values required")
        tables[name] = table
    nodes, edges, tx = (tables[k] for k in ("nodes", "edges", "transactions"))
    if nodes.empty:
        raise ValueError("nodes: at least one node required")
    if not pd.api.types.is_bool_dtype(nodes.is_seed):
        raise ValueError("nodes.is_seed: boolean values required")
    if nodes.gid.duplicated().any():
        raise ValueError("nodes: duplicate gid")
    if edges.duplicated(["src", "dst"]).any():
        raise ValueError("edges: duplicate src/dst pair")
    known = set(nodes.gid)
    for name, table in (("edges", edges), ("transactions", tx)):
        if not (set(table.src) | set(table.dst)) <= known:
            raise ValueError(f"{name}: unknown node reference")
    if (edges.n_tx < 1).any():
        raise ValueError("edges.n_tx: positive count required")
    try:
        tx["date"] = pd.to_datetime(tx.date, errors="raise")
    except (ValueError, TypeError) as error:
        raise ValueError("transactions.date: invalid date") from error
    agg = tx.groupby(["src", "dst"]).agg(tx_sum=("sum_kzt", "sum"), tx_count=("sum_kzt", "size")).reset_index()
    joined = edges.merge(agg, on=["src", "dst"], how="outer", indicator=True, validate="one_to_one")
    if not (joined["_merge"] == "both").all():
        raise ValueError("edges/transactions: inconsistent src/dst pairs")
    if ((joined.sum_kzt - joined.tx_sum).abs() > 0.01).any():
        raise ValueError("edges/transactions: inconsistent sum_kzt (tolerance 0.01 KZT)")
    if not (joined.n_tx == joined.tx_count).all():
        raise ValueError("edges/transactions: inconsistent n_tx")
    return nodes.sort_values("gid"), edges.sort_values(["src", "dst"]), tx


def run_pipeline(data_dir: Path, out_dir: Path) -> dict:
    started = time.perf_counter()
    nodes, edges, tx = load_and_validate(Path(data_dir))
    records, clusters, top, graph = analyze(nodes, edges)
    report = {
        "schema_version": "1.0",
        "meta": {"n_nodes": len(nodes), "n_edges": len(edges), "n_transactions": len(tx),
                 "n_seed": int(nodes.is_seed.sum()), "total_kzt": math.fsum(edges.sum_kzt),
                 "period_start": tx.date.min().date().isoformat() if len(tx) else "",
                 "period_end": tx.date.max().date().isoformat() if len(tx) else "",
                 "elapsed_seconds": round(time.perf_counter() - started, 6),
                 "warnings": ["Роли и оценки — эвристические гипотезы для проверки, не вероятность вины.",
                              "Наблюдаются только внутрибанковские исходящие переводы июля 2026 от 5000 KZT до depth=4; это не полный баланс."]},
        "nodes": records,
        "edges": [{"src": str(int(r.src)), "dst": str(int(r.dst)), "sum_kzt": float(r.sum_kzt), "n_tx": int(r.n_tx)} for r in edges.itertuples(index=False)],
        "clusters": clusters, "top_nodes": top,
    }
    serialized = json.dumps(report, ensure_ascii=False, allow_nan=False, separators=(",", ":"))
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, rows in (("nodes_roles.csv", records), ("clusters.csv", clusters), ("top_nodes.csv", top)):
        with (out_dir / name).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=CSV_SCHEMAS[name], extrasaction="ignore", lineterminator="\n")
            writer.writeheader()
            for row in rows:
                values = dict(row)
                if "top_gids" in values:
                    values["top_gids"] = ";".join(values["top_gids"])
                writer.writerow(values)
    (out_dir / "report.json").write_text(serialized, encoding="utf-8")
    return report
