"""Explain date-based observations without inferring intraday order or fund identity."""
from __future__ import annotations

from collections import Counter, defaultdict
from datetime import timedelta
from math import fsum
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
    period_days = (period_end - period_start).days + 1 if period_start and period_end else 0
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

        rows_by_day = defaultdict(list)
        for day, amount, source in in_rows:
            rows_by_day[day].append((amount, source))
        concentrations = [
            (day, rows, len({source for _, source in rows}))
            for day, rows in rows_by_day.items()
            if len({source for _, source in rows}) >= 3
        ]
        concentrations.sort(key=lambda item: (-item[2], item[0]))
        synchronous = None
        if concentrations:
            day, rows, payer_count = concentrations[0]
            synchronous = {"date": day.isoformat(), "distinct_payers": payer_count,
                           "tx_count": len(rows), "sum_kzt": fsum(amount for amount, _ in rows)}

        total_incident = sum(incident[gid].values())
        baseline = total_incident / period_days if period_days else 0.0
        qualifying_peaks = [(day, count) for day, count in incident[gid].items()
                            if count >= 3 and count >= 2 * baseline]
        qualifying_peaks.sort(key=lambda item: (-item[1], item[0]))
        peak = None
        if qualifying_peaks:
            day, count = qualifying_peaks[0]
            peak = {"date": day.isoformat(), "count": count,
                    "share": count / total_incident, "baseline_daily_count": baseline}

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
                "total_kzt": fsum(amount for _, amount, _ in in_rows),
                "distinct_payers": len({source for _, _, source in in_rows}),
                "median_kzt": float(median(amount for _, amount, _ in in_rows)) if in_rows else 0.0,
            },
            "synchronous_incoming": synchronous,
            "peak_day": peak,
        }
        requests = []
        if node["is_seed"]:
            requests.append(f"Запросить входящую историю gid {gid} до начала выборки: входящие seed не наблюдаются полностью.")
        elif not in_rows:
            requests.append(f"Запросить входящие переводы gid {gid} вне выборки: наблюдаемой входящей истории нет.")
        if node["boundary_censored"]:
            requests.append(f"Запросить продолжение исходящих переводов gid {gid} за depth=4: граница обхода скрывает дальнейший поток.")
        if one_or_two_days:
            first_example = min(examples)
            requests.append(
                f"Запросить точное время, референсы переводов и выписку gid {gid} за {first_example[0]}–{first_example[1]}: "
                "временное совпадение не подтверждает движение одних и тех же средств."
            )
        if not requests:
            requests.append(f"Запросить операции gid {gid} за пределами банка и периода выборки для проверки полноты наблюдаемого потока.")
        node["next_data_requests"] = requests
        enriched.append(node)
    return enriched
