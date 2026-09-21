import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


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

    def test_rejects_unknown_input_fields_to_prevent_content_leakage(self):
        with self.assertRaisesRegex(ValueError, "unsupported fields"):
            context_budget.classify(sample(prompt="private source code"))

    def test_rejects_invalid_capacity_contract(self):
        with self.assertRaisesRegex(ValueError, "usable ceiling"):
            context_budget.classify(sample(compaction_reserve=130_000))


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


if __name__ == "__main__":
    unittest.main()
