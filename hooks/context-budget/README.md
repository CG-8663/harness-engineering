# Context-budget hook

This directory contains a portable classifier for agent-session context pressure. Read
the full [GitHub guide](../../docs/context-budget-hook.md) before connecting it to a live
harness.

## Contract

`context_budget.py` reads one JSON object from standard input and writes one JSON object
to standard output. It returns exit code `0` for a decision and `2` for invalid input.

Accepted fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `input_tokens` | non-negative integer | Current request input estimate |
| `context_limit` | positive integer | Model context window |
| `reply_reserve` | non-negative integer | Space protected for the next answer |
| `compaction_reserve` | non-negative integer | Space protected for summary and continued work |
| `turn_count` | non-negative integer | Turns in the current phase |
| `failed_attempts` | non-negative integer | Repeated unsuccessful attempts |
| `phase` | enum | `discovery`, `planning`, `implementation`, `verification`, `handoff`, or `unknown` |
| `cache_mode` | enum | `cold`, `warm`, or `unknown` |
| `phase_boundary` | boolean | An explicit, observed phase boundary |

The output `action` is `retain`, `compact`, or `handoff`. The caller owns the action.

## Test

```bash
python3 -m unittest discover -s hooks/context-budget/tests -v
```

The suite performs no network calls.
