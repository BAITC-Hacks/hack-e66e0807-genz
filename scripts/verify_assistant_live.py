"""Required live free-provider five-source assistant check; mock tests are separate."""
import argparse
import collections
import json
import math
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from solution.assistant import AssistantConfig, _provider_call, answer_question


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, default=Path("output/report.json"))
    args = parser.parse_args()
    config = AssistantConfig.from_env()
    if config.status()["status"] != "ready":
        print("LIVE FAIL: assistant key or endpoint is unavailable", file=sys.stderr)
        return 2
    report = json.loads(args.report.read_text(encoding="utf-8"))
    by_recipient = collections.defaultdict(list)
    for edge in report["edges"]:
        by_recipient[edge["dst"]].append(edge)
    candidates = [(dst, edges) for dst, edges in by_recipient.items()
                  if len({e["src"] for e in edges}) >= 5]
    if not candidates:
        print("LIVE FAIL: no recipient with five payers", file=sys.stderr)
        return 2
    recipient, edges = min(candidates, key=lambda item: (-len(item[1]), int(item[0])))
    sources = sorted({e["src"] for e in edges}, key=int)[:5]
    question = "Кто собирает деньги с этих пятерых: " + ", ".join(sources) + "?"
    observed_calls = []

    def observed_provider(config, messages, specs, timeout, choice):
        message = _provider_call(config, messages, specs, timeout, choice)
        for tool in message.get("tool_calls") or []:
            observed_calls.append(tool.get("function", {}).get("name"))
        return message

    start = time.monotonic()
    try:
        answer = answer_question(report, question, config=config, provider_call=observed_provider)
    except Exception as exc:
        print(f"LIVE FAIL: {type(exc).__name__}: {str(exc)[:100]}", file=sys.stderr)
        return 1
    matching = [e for e in report["edges"] if e["src"] in sources and e["dst"] == recipient]
    expected_sum = math.fsum(e["sum_kzt"] for e in matching)
    citations = answer["citations"]
    edge_refs = {c["reference"] for c in citations if c["kind"] == "edge"}
    expected_refs = {f"edge/{e['src']}/{recipient}/sum_kzt" for e in matching}
    valid = ("get_common_recipients" in observed_calls
             and recipient in answer["answer"]
             and str(len(sources)) in answer["answer"]
             and f"{expected_sum:,.2f}".replace(",", " ") in answer["answer"]
             and edge_refs == expected_refs)
    if not valid:
        print("LIVE FAIL: tool, recipient, count, sum or complete edge citations differ", file=sys.stderr)
        return 1
    print(f"LIVE PASS: provider={config.provider}, tool=get_common_recipients, "
          f"payers={len(sources)}, sum_kzt={expected_sum:.2f}, "
          f"edge_citations={len(edge_refs)}, elapsed_s={time.monotonic()-start:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
