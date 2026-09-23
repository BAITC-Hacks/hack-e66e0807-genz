"""High-side, same-depth observations; no guilt probability is inferred."""
from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median


METRICS = ("in_degree", "out_degree", "in_sum", "out_sum",
           "incoming_tx_count", "outgoing_tx_count", "near_cutoff_share")
INCOMING = {"in_degree", "in_sum", "incoming_tx_count"}
OUTGOING = {"out_degree", "out_sum", "outgoing_tx_count"}


def enrich_anomalies(records, transactions):
    """Add evaluated anomaly arrays using eligible peers excluding the subject."""
    incident = Counter()
    near = Counter()
    for row in transactions.itertuples(index=False):
        members = {str(int(row.src)), str(int(row.dst))}  # a self-loop counts once
        for gid in members:
            incident[gid] += 1
            if 5000 <= float(row.sum_kzt) < 10000:
                near[gid] += 1
    values = {}
    for node in records:
        gid = node["gid"]
        values[gid] = {
            "in_degree": node["in_degree"], "out_degree": node["out_degree"],
            "in_sum": node["in_sum"], "out_sum": node["out_sum"],
            "incoming_tx_count": node["temporal"]["incoming_tx_count"],
            "outgoing_tx_count": node["temporal"]["outgoing_tx_count"],
            "near_cutoff_share": near[gid] / incident[gid] if incident[gid] else 0.0,
        }
    by_depth = defaultdict(list)
    for node in records:
        by_depth[node["depth"]].append(node)
    result = []
    for original in records:
        node = dict(original)
        gid = node["gid"]
        findings = []
        for metric in METRICS:
            if metric in INCOMING and node["is_seed"]:
                continue
            if metric in OUTGOING and node["boundary_censored"]:
                continue
            peers = [peer for peer in by_depth[node["depth"]]
                     if peer["gid"] != gid
                     and (metric not in INCOMING or not peer["is_seed"])
                     and (metric not in OUTGOING or not peer["boundary_censored"])]
            if len(peers) < 10:
                continue
            peer_values = [values[peer["gid"]][metric] for peer in peers]
            baseline = float(median(peer_values))
            mad = float(median(abs(value - baseline) for value in peer_values))
            value = float(values[gid][metric])
            deviation = (value - baseline) / (1.4826 * mad) if mad > 0 else None
            if mad > 0:
                flagged = deviation >= 3.5
            else:
                # Numeric-gid tie breaking makes the empirical rank reproducible.
                ordered = sorted(peers + [node], key=lambda peer: (values[peer["gid"]][metric], int(peer["gid"])))
                rank = next(index + 1 for index, peer in enumerate(ordered) if peer["gid"] == gid)
                flagged = len(peers) >= 20 and value > baseline and rank / len(ordered) >= 0.95
            if not flagged:
                continue
            limitations = ["Сравнение по наблюдаемой выгрузке; отклонение — повод для проверки, не вероятность вины."]
            if node["is_seed"]:
                limitations.append("У seed входящая история неполна.")
            if node["boundary_censored"]:
                limitations.append("За depth=4 исходящий поток может продолжаться.")
            if metric == "near_cutoff_share":
                limitations.append("Переводы ниже 5000 KZT отсутствуют в выгрузке; дробление не доказано.")
                method = (f"Наблюдаемые строки 5000≤сумма<10000 KZT: "
                          f"{near[gid]} из {incident[gid]}; доля среди видимых операций.")
            elif mad > 0:
                method = "Высокое отклонение ≥3,5 масштабированных MAD от медианы ровесников по колену."
            else:
                method = "MAD=0; выше медианы и эмпирический ранг ≥95-го процентиля (по gid при равенстве)."
            findings.append({
                "kind": "observed_near_cutoff" if metric == "near_cutoff_share" else "depth_peer_profile",
                "metric": metric, "value": value, "peer_depth": node["depth"],
                "peer_n": len(peers), "peer_median": baseline,
                "peer_mad": mad, "deviation": deviation,
                "method": method, "limitations": limitations,
            })
        node["anomalies"] = findings
        result.append(node)
    return result
