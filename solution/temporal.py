"""Explain date-based observations without inferring intraday order or fund identity."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from statistics import median


def enrich_temporal(records, transactions, period_start, period_end):
    """Return node records augmented from validated transaction rows."""
    incoming = defaultdict(list)
    outgoing = defaultdict(list)
    incident = defaultdict(Counter)
    for row in transactions.itertuples(index=False):
        source, destination = str(int(row.src)), str(int(row.dst))
        day = row.date.date()
        amount = float(row.sum_kzt)
        outgoing[source].append((day, amount, destination))
        incoming[destination].append((day, amount, source))
        incident[source][day] += 1
        if destination != source:
            incident[destination][day] += 1

    enriched = []
    for record in records:
        node = dict(record)
        gid = node["gid"]
        in_rows = incoming[gid]
        out_rows = outgoing[gid]
        in_dates = {day for day, _, _ in in_rows}
        one_day = 0
        one_or_two_days = 0
        examples = set()
        for out_day, _, _ in out_rows:
            candidates = [out_day - timedelta(days=days) for days in (1, 2)
                          if out_day - timedelta(days=days) in in_dates]
            if out_day - timedelta(days=1) in in_dates:
                one_day += 1
            if candidates:
                one_or_two_days += 1
                examples.update((day.isoformat(), out_day.isoformat()) for day in candidates)

        node["temporal"] = {
            "incoming_tx_count": len(in_rows),
            "outgoing_tx_count": len(out_rows),
            "outgoing_after_1d_count": one_day,
            "outgoing_after_1_or_2d_count": one_or_two_days,
            "after_1_or_2d_examples": [
                {"incoming_date": start, "outgoing_date": end}
                for start, end in sorted(examples)[:3]
            ],
            "incoming_profile": {
                "active_days": len(in_dates),
                "total_kzt": float(sum(amount for _, amount, _ in in_rows)),
                "distinct_payers": len({source for _, _, source in in_rows}),
                "median_kzt": float(median(amount for _, amount, _ in in_rows)) if in_rows else 0.0,
            },
            "synchronous_incoming": None,
            "peak_day": None,
        }
        node["next_data_requests"] = [
            f"Запросить выписку и точное время переводов gid {gid} для проверки наблюдаемых дат; "
            "совпадение дат не устанавливает движение одних и тех же средств."
        ]
        enriched.append(node)
    return enriched
