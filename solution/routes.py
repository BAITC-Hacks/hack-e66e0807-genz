"""Bounded directed route and return-cycle observations from calendar dates."""
from __future__ import annotations

from collections import defaultdict
from itertools import islice, product


MAX_PER_NODE = 20
MAX_CANDIDATES = 2000
MAX_DATE_COMBINATIONS = 2000


def _evidence(gids, edges, dates, cycle=False):
    pairs = list(zip(gids, gids[1:] + (gids[0],) if cycle else gids[1:]))
    legs = [edges[pair] for pair in pairs]
    row_dates = [dates[pair] for pair in pairs]
    combinations = product(*row_dates)
    seen = set()
    strict, ambiguous, starts = set(), set(), set()
    scanned = 0
    for days in islice(combinations, MAX_DATE_COMBINATIONS + 1):
        scanned += 1
        if scanned > MAX_DATE_COMBINATIONS:
            break
        if days in seen:
            continue
        seen.add(days)
        if all(a < b for a, b in zip(days, days[1:])):
            strict.add(days)
            starts.add(days[0])
        elif all(a <= b for a, b in zip(days, days[1:])) and any(a == b for a, b in zip(days, days[1:])):
            ambiguous.add(days)
    truncated = scanned > MAX_DATE_COMBINATIONS
    limitations = ["Даты показывают порядок наблюдений, но не движение тех же средств или внутридневное время."]
    if truncated:
        limitations.append("Поиск комбинаций дат ограничен; отсутствие повторения не доказано.")
    return {
        "gids": list(gids), "legs": legs,
        "strict_date_examples": [{"dates": list(days)} for days in sorted(strict)[:3]],
        "same_day_ambiguous_examples": [{"dates": list(days)} for days in sorted(ambiguous)[:3]],
        "strict_episode_days": len(starts), "repeated": len(starts) >= 2,
        "date_search_truncated": truncated, "limitations": limitations,
    }


def find_routes(nodes, edges, transactions):
    """Enumerate directed length-two paths and simple 2/3-party cycles.

    Candidate and output budgets are charged to the route's first gid and the
    cycle's numerically smallest gid. A capped node is named in truncated_nodes.
    """
    adjacency = defaultdict(set)
    edge_by_pair = {}
    for row in edges.itertuples(index=False):
        src, dst = str(int(row.src)), str(int(row.dst))
        pair = (src, dst)
        edge_by_pair[pair] = {"src": src, "dst": dst, "sum_kzt": float(row.sum_kzt), "n_tx": int(row.n_tx)}
        if src != dst:
            adjacency[src].add(dst)
    dates = defaultdict(list)
    for row in transactions.itertuples(index=False):
        dates[(str(int(row.src)), str(int(row.dst)))].append((row.date.date().isoformat(), float(row.sum_kzt)))
    # Transaction rows are sorted before deriving date combinations. Duplicate
    # date tuples are collapsed by _evidence, but rows still consume the budget.
    date_rows = {pair: tuple(day for day, _ in sorted(rows)) for pair, rows in dates.items()}
    ordered_nodes = [str(int(gid)) for gid in sorted(nodes.gid)]
    paths, cycles, truncated = [], [], set()
    for start in ordered_nodes:
        candidates = 0
        path_count = cycle_count = 0
        stop = False
        for middle in sorted(adjacency[start], key=int):
            # The reciprocal two-party cycle is canonical at its smallest gid.
            if (middle, start) in edge_by_pair and int(start) < int(middle):
                candidates += 1
                if candidates > MAX_CANDIDATES:
                    stop = True
                    break
                if cycle_count < MAX_PER_NODE:
                    cycles.append(_evidence((start, middle), edge_by_pair, date_rows, True))
                    cycle_count += 1
                else:
                    truncated.add(start)
            for end in sorted(adjacency[middle], key=int):
                if end == start or end == middle:
                    continue
                candidates += 1
                if candidates > MAX_CANDIDATES:
                    stop = True
                    break
                if path_count < MAX_PER_NODE:
                    paths.append(_evidence((start, middle, end), edge_by_pair, date_rows))
                    path_count += 1
                else:
                    truncated.add(start)
                if (end, start) in edge_by_pair and int(start) < int(middle) and int(start) < int(end):
                    candidates += 1
                    if candidates > MAX_CANDIDATES:
                        stop = True
                        break
                    if cycle_count < MAX_PER_NODE:
                        cycles.append(_evidence((start, middle, end), edge_by_pair, date_rows, True))
                        cycle_count += 1
                    else:
                        truncated.add(start)
            if stop:
                break
        if stop:
            truncated.add(start)
    return {
        "max_routes_per_node": MAX_PER_NODE,
        "max_cycles_per_node": MAX_PER_NODE,
        "max_candidate_tuples_per_node": MAX_CANDIDATES,
        "max_date_combinations_per_candidate": MAX_DATE_COMBINATIONS,
        "truncated_nodes": sorted(truncated, key=int),
        "paths": paths, "cycles": cycles,
    }
