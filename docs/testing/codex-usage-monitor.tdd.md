# Codex usage monitor TDD evidence

## User journey

As a harness engineer, I want to retain only numeric Codex usage telemetry so that I can
measure Jev's effect without storing prompts, transcripts, tool payloads or agent output.

## RED and GREEN

| Gate | Command | Result |
| --- | --- | --- |
| RED | `python3 -m unittest discover -s hooks/codex-usage/tests -v` | Import failed because `codex_usage.py` did not exist |
| GREEN | `python3 -m unittest discover -s hooks/codex-usage/tests -v` | 9 tests passed |
| Regression | `python3 -m unittest discover -s hooks/context-budget/tests -v` | 18 tests passed |
| Coverage | stdlib `trace --count --summary` over the monitor suite | 98% of `codex_usage.py` executable lines |

## Guarantees

| # | Guarantee | Test type | Result |
| --- | --- | --- | --- |
| 1 | Only the last `turn.completed` numeric usage is summarized | unit | pass |
| 2 | Agent messages and their text are not retained | unit and CLI | pass |
| 3 | Invalid, negative, Boolean or impossible counts fail closed | unit | pass |
| 4 | Invalid JSON is reported without echoing its content | unit and CLI | pass |
| 5 | Optional metrics files contain sanitized JSONL and use mode `0600` | unit and CLI | pass |

The monitor intentionally supports the documented `codex exec --json` stream. It does
not parse interactive-session transcripts because that format is not a stable public
contract.
