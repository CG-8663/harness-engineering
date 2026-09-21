# One-sample Jev context smoke test

Run on 21 September 2026 against the same 55,000-token advisory-band state. The sample
contains only bounded numeric and enum metadata.

## Results

| Mode | Final action | Wall time | Jev usage | Observed compaction saving |
| --- | --- | ---: | ---: | ---: |
| Without Jev | `retain` | 0.07 s | 0 tokens | 0% |
| With live Jev | `retain` through confidence fallback | 0.95 s | See diagnostic repeat | 0% |

The live hook does not expose rejected response details. A second request with the exact
same sanitized state and Choice captured the diagnostic evidence: Jev 1.13.0 preferred
`compact` with probability 0.69, but confidence was 0.53. The production confidence floor
is 0.65, so the hook correctly rejected automatic compaction and retained the session.
The diagnostic request used 438 input tokens and 40 output tokens with 864 ms measured
client latency. [See the diagnostic repeat](with-jev.json).

## Interpretation

This is a safety and integration smoke test, not a savings benchmark. No compaction was
executed, so observed compaction savings are 0 percent. The result adds Jev decision
overhead without changing the action. It demonstrates that low-confidence advice cannot
override the deterministic fallback.

At least 20 paired representative tasks, followed by native compaction and a measured
subsequent turn, are required before publishing a positive or negative production savings
claim.

## Reproduce

Deterministic run:

```bash
python3 hooks/context-budget/context_budget.py \
  < benchmarks/context-savings/2026-09-21-simple/input.json
```

Live run, with `TYPESAFE_API_KEY` supplied by a secret-safe environment:

```bash
python3 hooks/context-budget/context_budget.py --use-jev \
  < benchmarks/context-savings/2026-09-21-simple/input.json
```

Do not place the API key in this repository or in a command argument.
