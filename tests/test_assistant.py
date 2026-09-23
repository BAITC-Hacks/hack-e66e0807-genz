"""Assistant safety and grounding tests over synthetic reports."""
import json
import tempfile
import threading
import unittest
import urllib.error
import urllib.request
import os
from pathlib import Path
from unittest.mock import patch


SOURCES = [str(9007199254740993 + i) for i in range(5)]
RECIPIENT = "9007199254741099"
RIVAL = "9007199254741199"


def fixture_report():
    gids = SOURCES + [RECIPIENT, RIVAL]
    nodes = [{"gid": gid, "depth": 4 if gid == RECIPIENT else 0,
              "role": "peripheral", "priority_score": 0.1, "in_sum": 0.0,
              "out_sum": 0.0, "in_degree": 0, "out_degree": 0,
              "cluster_id": 0, "evidence": "untrusted text",
              "boundary_censored": gid == RECIPIENT, "is_seed": gid in SOURCES}
             for gid in gids]
    edges = [{"src": gid, "dst": RECIPIENT, "sum_kzt": float(10000 + i * 1000), "n_tx": 1}
             for i, gid in enumerate(SOURCES)]
    edges += [{"src": gid, "dst": RIVAL, "sum_kzt": 5000.0, "n_tx": 1}
              for gid in SOURCES[:3]]
    return {"schema_version": "1.0", "nodes": nodes, "edges": edges,
            "clusters": [{"cluster_id": 0, "n_nodes": len(nodes)}],
            "top_nodes": [{"gid": RECIPIENT, "rank": 1, "priority_score": 0.1}]}


class QueryTests(unittest.TestCase):
    def setUp(self):
        from solution.assistant import ReportTools
        self.tools = ReportTools(fixture_report())

    def test_common_recipients_rank_all_five_and_sum_complete_edges(self):
        result = self.tools.call("get_common_recipients", {"gids": SOURCES})
        self.assertEqual(result[0]["gid"], RECIPIENT)
        self.assertEqual(result[0]["payer_count"], 5)
        self.assertEqual(result[0]["sum_kzt"], 60000.0)
        self.assertEqual(len(result[0]["source_edges"]), 5)
        self.assertEqual(result[1]["payer_count"], 3)

    def test_rejects_unknown_tool_gid_and_invalid_limits(self):
        from solution.assistant import AssistantInputError
        for name, args in [("read_file", {"path": "/etc/passwd"}),
                           ("get_node", {"gid": "999"}),
                           ("get_incoming", {"gid": RECIPIENT, "limit": 999}),
                           ("get_common_recipients", {"gids": SOURCES + SOURCES})]:
            with self.subTest(name=name), self.assertRaises(AssistantInputError):
                self.tools.call(name, args)

    def test_common_answer_rederives_values_and_every_edge_citation(self):
        from solution.assistant import render_model_answer
        result = self.tools.call("get_common_recipients", {"gids": SOURCES})
        answer = render_model_answer(self.tools, {"recipient_gid": RECIPIENT},
                                     [("get_common_recipients", {"gids": SOURCES}, result)])
        self.assertIn(RECIPIENT, answer["answer"])
        self.assertIn("5", answer["answer"])
        self.assertIn("60 000", answer["answer"])
        self.assertEqual(len([c for c in answer["citations"] if c["kind"] == "edge"]), 5)
        self.assertIn("нет дат", " ".join(answer["limitations"]).lower())

    def test_rejects_proposed_aggregate_or_invalid_scalar_claim(self):
        from solution.assistant import AssistantEvidenceError, render_model_answer
        result = self.tools.call("get_common_recipients", {"gids": SOURCES})
        for payload in ({"recipient_gid": RECIPIENT, "payer_count": 5},
                        {"recipient_gid": RECIPIENT, "source_edges": result[0]["source_edges"][:-1]},
                        {"recipient_gid": RIVAL, "sum_kzt": 60000},
                        {"claims": [{"reference": f"edge/{SOURCES[0]}/{RECIPIENT}/sum_kzt", "value": 90000.0}]}):
            with self.subTest(payload=payload), self.assertRaises(AssistantEvidenceError):
                render_model_answer(self.tools, payload,
                                    [("get_common_recipients", {"gids": SOURCES}, result)])

    def test_selected_gid_question_uses_real_tool_then_exact_claim(self):
        from solution.assistant import AssistantConfig, answer_question
        seen = []
        replies = [
            {"role": "assistant", "tool_calls": [{"id": "one", "function": {
                "name": "get_node", "arguments": json.dumps({"gid": RECIPIENT})}}]},
            {"role": "assistant", "content": json.dumps({"claims": [
                {"reference": f"node/{RECIPIENT}/priority_score", "value": 0.1},
                {"reference": f"node/{RECIPIENT}/role", "value": "peripheral"}]})},
        ]

        def provider(_config, messages, _specs, _timeout, _choice):
            seen.append(messages)
            return replies.pop(0)

        config = AssistantConfig(True, "http://127.0.0.1:1234", "test", "", "local")
        answer = answer_question(fixture_report(), "Почему этот участник в приоритетах?",
                                 RECIPIENT, config, provider)
        self.assertEqual(len(answer["citations"]), 6)
        self.assertIn("эвристический приоритет", answer["answer"])
        self.assertEqual(len(seen), 1)

    def test_free_openrouter_config_and_missing_key(self):
        from solution.assistant import AssistantConfig
        with patch.object(AssistantConfig, "_local_env", return_value={}):
            with patch.dict(os.environ, {}, clear=True):
                self.assertEqual(AssistantConfig.from_env().status()["status"], "disabled")
            with patch.dict(os.environ, {"OPENROUTER_API_KEY": "test-only",
                                      "ASSISTANT_MODEL": "paid-model"}, clear=True):
                config = AssistantConfig.from_env()
                self.assertEqual(config.model, "openrouter/free")
                self.assertEqual(config.provider, "remote")
                self.assertEqual(config.status()["status"], "ready")

    def test_model_json_wrapping_is_discarded_but_ambiguous_or_prose_only_refused(self):
        from solution.assistant import AssistantEvidenceError, _structured_payload
        wrapped = 'Result:\n```json\n{"recipient_gid":"' + RECIPIENT + '"}\n```'
        self.assertEqual(_structured_payload(wrapped, True), {"recipient_gid": RECIPIENT})
        nested = 'Here: {"claims":[{"reference":"node/' + RECIPIENT + '/role","value":"peripheral"}]}'
        self.assertEqual(len(_structured_payload(nested, False)["claims"]), 1)
        with self.assertRaises(AssistantEvidenceError):
            _structured_payload("The recipient is obvious.", True)
        with self.assertRaises(AssistantEvidenceError):
            _structured_payload('{"recipient_gid":"' + RECIPIENT + '"}{"recipient_gid":"' + RIVAL + '"}', True)

    def test_priority_method_question_requires_real_tool_call_and_cites_example(self):
        from solution.assistant import AssistantConfig, AssistantEvidenceError, answer_question
        config = AssistantConfig(True, "http://127.0.0.1:1234", "test", "", "local")
        seen = []

        def provider(_config, _messages, specs, _timeout, _choice):
            seen.extend(spec["function"]["name"] for spec in specs)
            return {"role": "assistant", "tool_calls": [{"id": "method-1", "function": {
                "name": "get_priority_method", "arguments": "{}"}}]}

        answer = answer_question(fixture_report(), "Как отбираются участники для приоритета?",
                                 config=config, provider_call=provider)
        self.assertIn("0.30", answer["answer"])
        self.assertEqual(answer["citations"][0]["reference"], f"node/{RECIPIENT}/priority_score")
        self.assertIn("get_priority_method", seen)
        with self.assertRaises(AssistantEvidenceError):
            answer_question(fixture_report(), "Как отбираются участники для приоритета?",
                            config=config, provider_call=lambda *_: {"role": "assistant", "content": "guess"})


class ApiTests(unittest.TestCase):
    def setUp(self):
        from solution.server import DATA_FILES, make_server
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = self.root = Path(self.tmp.name)
        data, ui = root / "data", root / "ui"
        data.mkdir(); ui.mkdir()
        (ui / "index.html").write_text("working")
        for name in DATA_FILES:
            (data / name).write_text(json.dumps(fixture_report()) if name == "report.json" else "csv")
        self.env = patch.dict("os.environ", {"ASSISTANT_ENABLED": "0"})
        self.env.start(); self.addCleanup(self.env.stop)
        self.server = make_server(data, ui, 0)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop)
        self.base = f"http://127.0.0.1:{self.server.server_port}"

    def stop(self):
        self.server.shutdown(); self.server.server_close(); self.thread.join()

    def test_disabled_status_and_static_report(self):
        with urllib.request.urlopen(self.base + "/api/assistant/status") as response:
            self.assertEqual(json.load(response)["status"], "disabled")
        with urllib.request.urlopen(self.base + "/data/report.json") as response:
            self.assertEqual(json.load(response)["nodes"][0]["gid"], SOURCES[0])
        request = urllib.request.Request(self.base + "/api/assistant/query", data=b'{}', method="POST",
                                         headers={"Content-Type": "application/json"})
        with self.assertRaises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        self.assertEqual(error.exception.code, 503)
        self.assertEqual(json.load(error.exception)["status"], "disabled")
        error.exception.close()

    def test_enabled_endpoint_bounds_body_origin_and_preserves_exports(self):
        from solution.server import make_server
        # A second server snapshots enabled configuration at startup.
        with patch.dict(os.environ, {"ASSISTANT_ENABLED": "1",
                                  "ASSISTANT_BASE_URL": "http://127.0.0.1:8766",
                                  "ASSISTANT_MODEL": "test-model"}):
            server = make_server(self.root / "data", self.root / "ui", 0)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(lambda: (server.shutdown(), server.server_close(), thread.join()))
        endpoint = f"http://127.0.0.1:{server.server_port}/api/assistant/query"

        def send(raw, headers=None):
            request = urllib.request.Request(endpoint, data=raw, method="POST",
                                             headers={"Content-Type": "application/json", **(headers or {})})
            try:
                with urllib.request.urlopen(request) as response:
                    return response.status, json.load(response)
            except urllib.error.HTTPError as error:
                with error:
                    return error.code, json.load(error)

        self.assertEqual(send(b"x" * 4097)[0], 413)
        self.assertEqual(send(b"not-json")[0], 400)
        self.assertEqual(send(json.dumps({"question": "hi", "selected_gid": "999"}).encode())[0], 400)
        self.assertEqual(send(b'{"question":"hi"}', {"Origin": "https://evil.example"})[0], 403)
        with patch("solution.server.answer_question", return_value={"answer": "verified", "citations": [], "limitations": []}):
            status, payload = send(b'{"question":"hi"}')
            self.assertEqual((status, payload["answer"]), (200, "verified"))
        with urllib.request.urlopen(f"http://127.0.0.1:{server.server_port}/data/report.json") as response:
            self.assertEqual(response.status, 200)


if __name__ == "__main__":
    unittest.main()
