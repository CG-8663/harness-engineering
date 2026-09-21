import importlib.util
import json
import subprocess
import sys
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock


HOOK_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = HOOK_DIR / "context_budget.py"


def load_module():
    spec = importlib.util.spec_from_file_location("context_budget", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


context_budget = load_module()


def sample(**overrides):
    payload = {
        "input_tokens": 55_000,
        "context_limit": 131_072,
        "reply_reserve": 4_096,
        "compaction_reserve": 49_152,
        "turn_count": 18,
        "failed_attempts": 1,
        "phase": "implementation",
        "cache_mode": "warm",
        "phase_boundary": False,
    }
    payload.update(overrides)
    return payload


def jev_answer(choice="compact", confidence=0.9):
    probabilities = {"retain": 0.05, "compact": 0.9, "handoff": 0.05}
    probabilities[choice] = confidence
    remainder = (1 - confidence) / 2
    for option in probabilities:
        if option != choice:
            probabilities[option] = remainder
    return {
        "model": "jev-test",
        "answers": {
            "context_action": {
                "type": "choice",
                "choice": choice,
                "probabilities": probabilities,
                "confidence": confidence,
            }
        },
        "usage": {"input_tokens": 120, "output_tokens": 12},
    }


class ClassificationTests(unittest.TestCase):
    def test_retains_below_soft_limit_without_calling_jev(self):
        called = False

        def evaluator(_state):
            nonlocal called
            called = True
            return jev_answer()

        result = context_budget.classify(sample(input_tokens=20_000), evaluator=evaluator)

        self.assertEqual("retain", result["action"])
        self.assertEqual("deterministic", result["source"])
        self.assertFalse(called)

    def test_compacts_at_hard_ceiling_without_calling_jev(self):
        result = context_budget.classify(sample(input_tokens=77_824), evaluator=lambda _: self.fail())

        self.assertEqual("compact", result["action"])
        self.assertEqual("deterministic", result["source"])

    def test_explicit_phase_boundary_hands_off_without_jev(self):
        result = context_budget.classify(
            sample(input_tokens=20_000, phase="verification", phase_boundary=True),
            evaluator=lambda _: self.fail(),
        )

        self.assertEqual("handoff", result["action"])
        self.assertEqual("deterministic", result["source"])

    def test_accepts_high_confidence_jev_choice_in_advisory_band(self):
        captured = {}

        def evaluator(state):
            captured.update(state)
            return jev_answer("compact", 0.91)

        result = context_budget.classify(sample(), evaluator=evaluator)

        self.assertEqual("compact", result["action"])
        self.assertEqual("jev", result["source"])
        self.assertEqual(
            {"pressure_band", "turn_band", "failure_band", "phase", "cache_mode", "phase_boundary"},
            set(captured),
        )
        self.assertNotIn("input_tokens", captured)

    def test_rejects_jev_handoff_without_explicit_boundary(self):
        result = context_budget.classify(sample(), evaluator=lambda _: jev_answer("handoff", 0.95))

        self.assertEqual("retain", result["action"])
        self.assertEqual("fallback", result["source"])

    def test_low_confidence_uses_conservative_fallback(self):
        result = context_budget.classify(
            sample(input_tokens=70_000), evaluator=lambda _: jev_answer("retain", 0.40)
        )

        self.assertEqual("compact", result["action"])
        self.assertEqual("fallback", result["source"])

    def test_service_failure_uses_fallback(self):
        def unavailable(_state):
            raise OSError("offline")

        result = context_budget.classify(sample(input_tokens=50_000), evaluator=unavailable)

        self.assertEqual("retain", result["action"])
        self.assertEqual("fallback", result["source"])
        self.assertNotIn("offline", json.dumps(result))

    def test_missing_evaluator_uses_fallback(self):
        result = context_budget.classify(sample(input_tokens=50_000))

        self.assertEqual("retain", result["action"])
        self.assertEqual("jev_not_configured", result["reason"])

    def test_rejects_unknown_input_fields_to_prevent_content_leakage(self):
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            context_budget.classify(sample(prompt="private source code"))

    def test_rejects_invalid_capacity_contract(self):
        with self.assertRaisesRegex(ValueError, "usable ceiling"):
            context_budget.classify(sample(compaction_reserve=130_000))

    def test_rejects_invalid_policy_and_input_types(self):
        with self.assertRaisesRegex(ValueError, "policy ratios"):
            context_budget.classify(sample(), policy=context_budget.Policy(soft_ratio=0.9, fallback_ratio=0.8))
        with self.assertRaisesRegex(ValueError, "confidence floor"):
            context_budget.classify(sample(), policy=context_budget.Policy(confidence_floor=1.1))
        with self.assertRaisesRegex(ValueError, "input_tokens"):
            context_budget.classify(sample(input_tokens=True))
        with self.assertRaisesRegex(ValueError, "phase must be one of"):
            context_budget.classify(sample(phase="secret phase notes"))
        with self.assertRaisesRegex(ValueError, "phase_boundary"):
            context_budget.classify(sample(phase_boundary="yes"))

    def test_malformed_jev_responses_use_fallback(self):
        invalid = [
            {},
            jev_answer("retain", 0.9),
            jev_answer("retain", 0.9),
            jev_answer("retain", 0.9),
        ]
        invalid[1]["answers"]["context_action"]["type"] = "score"
        invalid[2]["answers"]["context_action"]["probabilities"].pop("handoff")
        invalid[3]["answers"]["context_action"]["probabilities"]["compact"] = -0.1

        for response in invalid:
            with self.subTest(response=response):
                result = context_budget.classify(sample(), evaluator=lambda _, value=response: value)
                self.assertEqual("fallback", result["source"])


class JevTransportTests(unittest.TestCase):
    def test_requires_api_key(self):
        with self.assertRaisesRegex(ValueError, "TYPESAFE_API_KEY"):
            context_budget.jev_evaluator("")

    def test_posts_only_bounded_state_to_official_endpoint(self):
        response_body = json.dumps(jev_answer()).encode("utf-8")

        class Response:
            status = 200

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return response_body

        class Opener:
            request = None
            timeout = None

            def open(self, request, timeout):
                self.request = request
                self.timeout = timeout
                return Response()

        opener = Opener()
        state = {
            "pressure_band": "advisory",
            "turn_band": "16-30",
            "failure_band": "1",
            "phase": "implementation",
            "cache_mode": "warm",
            "phase_boundary": False,
        }
        with mock.patch.object(context_budget.urllib.request, "build_opener", return_value=opener):
            result = context_budget.jev_evaluator("test-only-key", 3.0)(state)

        sent = json.loads(opener.request.data.decode("utf-8"))
        self.assertEqual(context_budget.API_URL, opener.request.full_url)
        self.assertEqual(state, sent["state"])
        self.assertEqual("jev-latest", sent["model"])
        self.assertEqual(3.0, opener.timeout)
        self.assertEqual("compact", result["answers"]["context_action"]["choice"])

    def test_redirect_handler_refuses_redirect(self):
        handler = context_budget._NoRedirect()
        self.assertIsNone(handler.redirect_request(None, None, 302, "redirect", {}, "https://example.test"))


class CommandLineTests(unittest.TestCase):
    def test_cli_reads_one_json_object_and_emits_one_json_object(self):
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH)],
            input=json.dumps(sample(input_tokens=20_000)),
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(0, completed.returncode, completed.stderr)
        output = json.loads(completed.stdout)
        self.assertEqual("retain", output["action"])
        self.assertEqual("deterministic", output["source"])

    def test_cli_fails_closed_on_non_object_input(self):
        completed = subprocess.run(
            [sys.executable, str(MODULE_PATH)],
            input="[]",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(2, completed.returncode)
        error = json.loads(completed.stderr)
        self.assertEqual("invalid_input", error["error"])

    def test_main_reports_missing_key_without_reading_network(self):
        stdin = StringIO(json.dumps(sample()))
        stdout = StringIO()
        stderr = StringIO()
        with mock.patch.object(context_budget.sys, "stdin", stdin), mock.patch.object(
            context_budget.sys, "stdout", stdout
        ), mock.patch.object(context_budget.sys, "stderr", stderr), mock.patch.dict(
            context_budget.os.environ, {}, clear=True
        ):
            code = context_budget.main(["--use-jev"])

        self.assertEqual(2, code)
        self.assertEqual("invalid_input", json.loads(stderr.getvalue())["error"])
        self.assertEqual("", stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
