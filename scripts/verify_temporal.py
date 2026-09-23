"""Recompute Phase 2 evidence independently from source transaction rows."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import timedelta
from pathlib import Path
from statistics import median

import pandas as pd

if __package__:
    from .verify_delivery import load_exports, require
else:
    from verify_delivery import load_exports, require


def check_number(actual, expected, label):
    require(type(actual) in (int, float) and math.isfinite(actual), f"{label}: invalid number")
    require(math.isclose(actual, expected, rel_tol=1e-12, abs_tol=1e-7), f"{label}: {actual} != {expected}")


def validate(data: Path, out: Path, baseline: Path | None = None):
    tables, report = load_exports(out)
    source = pd.read_parquet(data / "transactions.parquet").to_dict("records")
    nodes = pd.read_parquet(data / "nodes.parquet").to_dict("records")
    incoming, outgoing, incident = defaultdict(list), defaultdict(list), defaultdict(Counter)
    dates = []
    for row in source:
        day = pd.Timestamp(row["date"]).date()
        src, dst, amount = str(row["src"]), str(row["dst"]), float(row["sum_kzt"])
        dates.append(day)
        incoming[dst].append((day, src, amount))
        outgoing[src].append(day)
        for gid in {src, dst}:
            incident[gid][day] += 1
    span = (max(dates) - min(dates)).days + 1 if dates else 1
    actual_nodes = {node["gid"]: node for node in report["nodes"]}
    require(set(actual_nodes) == {str(row["gid"]) for row in nodes}, "Temporal node coverage mismatch")
    temporal_nodes = sync_nodes = peak_nodes = boundary_profiles = 0
    for row in nodes:
        gid = str(row["gid"])
        node = actual_nodes[gid]
        temporal = node.get("temporal")
        require(isinstance(temporal, dict), f"{gid}: temporal evidence missing")
        arrivals = incoming[gid]
        in_days = {d for d, _, _ in arrivals}
        one = sum(d - timedelta(days=1) in in_days for d in outgoing[gid])
        two = sum(any(d - timedelta(days=lag) in in_days for lag in (1, 2)) for d in outgoing[gid])
        expected_counts = {"incoming_tx_count": len(arrivals), "outgoing_tx_count": len(outgoing[gid]),
                           "outgoing_after_1d_count": one, "outgoing_after_1_or_2d_count": two}
        for key, value in expected_counts.items():
            require(type(temporal.get(key)) is int and temporal[key] == value, f"{gid}: wrong {key}")
        pairs = sorted({(d - timedelta(days=lag), d) for d in outgoing[gid] for lag in (1, 2)
                        if d - timedelta(days=lag) in in_days})[:3]
        expected_examples = [{"incoming_date": a.isoformat(), "outgoing_date": b.isoformat()} for a, b in pairs]
        require(temporal.get("after_1_or_2d_examples") == expected_examples, f"{gid}: incorrect or unordered examples")
        profile = temporal.get("incoming_profile")
        require(isinstance(profile, dict), f"{gid}: incoming profile missing")
        require(profile.get("active_days") == len(in_days), f"{gid}: active days incorrect")
        require(profile.get("distinct_payers") == len({payer for _, payer, _ in arrivals}), f"{gid}: payer count incorrect")
        check_number(profile.get("total_kzt"), math.fsum(amount for _, _, amount in arrivals), f"{gid} incoming total")
        check_number(profile.get("median_kzt"), median([amount for _, _, amount in arrivals]) if arrivals else 0, f"{gid} median")
        per_day = defaultdict(list)
        for day, payer, amount in arrivals:
            per_day[day].append((payer, amount))
        candidates = [(day, values) for day, values in per_day.items() if len({p for p, _ in values}) >= 3]
        sync = temporal.get("synchronous_incoming")
        if candidates:
            day, values = min(candidates, key=lambda item: (-len({p for p, _ in item[1]}), item[0]))
            require(isinstance(sync, dict), f"{gid}: synchronous incoming missing")
            require(sync.get("date") == day.isoformat(), f"{gid}: wrong synchronous date")
            require(sync.get("distinct_payers") == len({p for p, _ in values}), f"{gid}: wrong synchronous payers")
            require(sync.get("tx_count") == len(values), f"{gid}: wrong synchronous count")
            check_number(sync.get("sum_kzt"), math.fsum(amount for _, amount in values), f"{gid} synchronous sum")
            sync_nodes += 1
        else:
            require(sync is None, f"{gid}: false synchronous event")
        activity = incident[gid]
        total_incident = sum(activity.values())
        daily_baseline = total_incident / span
        qualifies = [(day, count) for day, count in activity.items() if count >= 3 and count >= 2 * daily_baseline]
        peak = temporal.get("peak_day")
        if qualifies:
            day, count = min(qualifies, key=lambda item: (-item[1], item[0]))
            require(isinstance(peak, dict), f"{gid}: peak missing")
            require(peak.get("date") == day.isoformat() and peak.get("count") == count, f"{gid}: peak date/count incorrect")
            check_number(peak.get("share"), count / total_incident, f"{gid} peak share")
            check_number(peak.get("baseline_daily_count"), daily_baseline, f"{gid} baseline")
            peak_nodes += 1
        else:
            require(peak is None, f"{gid}: false peak")
        requests = node.get("next_data_requests")
        require(isinstance(requests, list) and requests and all(isinstance(r, str) and r.strip() for r in requests), f"{gid}: requests missing")
        require(any(gid in request for request in requests), f"{gid}: requests lack node-specific context")
        if node["boundary_censored"]:
            require(any("границ" in request.lower() or "depth=4" in request.lower() or "глубин" in request.lower() for request in requests), f"{gid}: boundary request missing")
            require(node["role"] != "terminal", f"{gid}: censored node falsely terminal")
            boundary_profiles += 1
        if node["is_seed"]:
            require(any("вход" in request.lower() or "истори" in request.lower() for request in requests), f"{gid}: seed-history request missing")
        temporal_nodes += bool(two)
    if baseline is not None:
        for name in tables:
            require((out / name).read_bytes() == (baseline / name).read_bytes(), f"Phase 1 CSV changed: {name}")
    return {"status": "PASS", "nodes": len(nodes), "nodes_with_1_or_2day_observations": temporal_nodes,
            "nodes_with_synchronous_payers": sync_nodes, "nodes_with_daily_peak": peak_nodes,
            "boundary_profiles": boundary_profiles, "csv_baseline_comparison": "PASS" if baseline is not None else "not_requested"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("FINANCE-CASE/data"))
    parser.add_argument("--out", type=Path, default=Path("output"))
    parser.add_argument("--baseline", type=Path, help="optional pre-Phase-2 CSV directory for byte comparison")
    args = parser.parse_args()
    print(json.dumps(validate(args.data, args.out, args.baseline), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
