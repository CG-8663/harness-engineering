import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


HOOK_DIR = Path(__file__).resolve().parents[1]
MODULE_PATH = HOOK_DIR / "codex_usage.py"


def load_module():
    spec = importlib.util.spec_from_file_location("codex_usage", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


codex_usage = load_module()


def completed(input_tokens=1_000, cached=400, output=50, reasoning=20):
    return {
        "type": "turn.completed",
        "usage": {
            "input_tokens": input_tokens,
            "cached_input_tokens": cached,
            "cache_write_input_tokens": 0,
            "output_tokens": output,
            "reasoning_output_tokens": reasoning,
        },
    }


class ParseTests(unittest.TestCase):
    def test_extracts_only_numeric_usage_from_last_completed_turn(self):
        stream = [
            {"type": "item.completed", "item": {"type": "agent_message", "text": "private"}},
            completed(input_tokens=900),
            completed(input_tokens=1_000),
        ]

        result = codex_usage.summarize(stream, label="candidate")

        self.assertEqual("candidate", result["label"])
        self.assertEqual(1_000, result["usage"]["input_tokens"])
        self.assertEqual(600, result["usage"]["uncached_input_tokens"])
        self.assertEqual(1_070, result["usage"]["total_tokens"])
        self.assertNotIn("private", json.dumps(result))

    def test_rejects_missing_completed_turn(self):
        with self.assertRaisesRegex(ValueError, "turn.completed"):
            codex_usage.summarize([{"type": "thread.started"}], label="baseline")

    def test_rejects_invalid_or_impossible_usage(self):
        with self.assertRaisesRegex(ValueError, "non-negative integer"):
            codex_usage.summarize([completed(input_tokens=True)], label="bad")
        with self.assertRaisesRegex(ValueError, "cannot exceed"):
            codex_usage.summarize([completed(input_tokens=100, cached=101)], label="bad")


class CommandLineTests(unittest.TestCase):
    def test_cli_appends_sanitized_jsonl_record(self):
        payload = "\n".join(
            json.dumps(item)
            for item in [
                {"type": "item.completed", "item": {"type": "agent_message", "text": "secret"}},
                completed(),
            ]
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            ledger = Path(temp_dir) / "usage.jsonl"
            completed_process = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--label", "pilot", "--append", str(ledger)],
                input=payload,
                text=True,
                capture_output=True,
                check=False,
            )

            self.assertEqual(0, completed_process.returncode, completed_process.stderr)
            stdout_record = json.loads(completed_process.stdout)
            stored_record = json.loads(ledger.read_text())
            self.assertEqual(stdout_record, stored_record)
            self.assertNotIn("secret", ledger.read_text())

    def test_cli_reports_invalid_json_without_echoing_input(self):
        completed_process = subprocess.run(
            [sys.executable, str(MODULE_PATH), "--label", "pilot"],
            input='{not-json "private payload"}',
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(2, completed_process.returncode)
        self.assertEqual("", completed_process.stdout)
        self.assertNotIn("private payload", completed_process.stderr)


if __name__ == "__main__":
    unittest.main()
