# Context-budget hook TDD evidence

## Source plan

No separate plan file was supplied. The user requested a public GitHub guide, a context
classification hook, and an agent command that installs it safely.

## User journeys

- As a harness operator, I want deterministic context limits so that a classifier cannot
  overrun the model window.
- As a privacy-conscious operator, I want only bounded telemetry sent to Jev so that
  prompts and repository content remain local.
- As an agent user, I want a copy-paste command and measurement method so that I can
  install the hook and verify whether it actually reduces usage.

## RED and GREEN evidence

| Stage | Command | Result | Meaning |
| --- | --- | --- | --- |
| RED | `python3 -m unittest discover -s hooks/context-budget/tests -v` | Import failed because `context_budget.py` did not exist | The tests exercised a genuinely missing implementation |
| GREEN | `python3 -m unittest discover -s hooks/context-budget/tests -v` | 18 tests passed | The classifier, privacy allowlist, fallbacks, boundaries, TypeSafe transport, and CLI contract work as specified |

## Test specification

| # | Guarantee | Test type | Result |
| --- | --- | --- | --- |
| 1 | Below the soft limit, context is retained without calling Jev | Unit | PASS |
| 2 | At the hard ceiling, context is compacted without calling Jev | Unit | PASS |
| 3 | An explicit phase boundary produces a deterministic handoff | Unit | PASS |
| 4 | A valid high-confidence Jev choice is accepted in the advisory band | Unit | PASS |
| 5 | Only six bucketed fields reach the injected Jev evaluator | Unit | PASS |
| 6 | Handoff is rejected without an explicit boundary | Unit | PASS |
| 7 | Low confidence and service failure use deterministic fallback | Unit | PASS |
| 8 | Unknown input fields and invalid capacity contracts fail closed | Unit | PASS |
| 9 | The CLI reads and emits one JSON object and rejects a non-object | Integration | PASS |

## Coverage and known gaps

The standard-library trace report measured 94 percent line coverage for
`context_budget.py`. The suite covers the complete local decision path, mocked TypeSafe
transport, and CLI without making a network call. A live TypeSafe request is intentionally
not exercised in automated tests because it needs a secret and would create external
spend. A target-harness adapter remains environment specific and must add its own tests
before activation.

## Merge evidence

- RED checkpoint: `43c0153 test: define context budget hook contract`
- GREEN checkpoint: `fbd6090 feat: add deterministic Jev context budget hook`
