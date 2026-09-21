# Jev context and compaction savings ledger

This ledger publishes the measured effect of placing the Jev context-budget hook first in
the intelligent hook chain. It tracks input-token reduction and task quality together. A
smaller prompt is not a saving if the task fails or important context is lost.

## Current status

**No paired production benchmark has been completed, so no compaction saving is claimed
yet.** The hook has 18 passing tests and 94 percent measured line coverage, but those facts
verify implementation behavior rather than token savings.

One development-harness observation recorded 61,004 input tokens for a one-line request.
It demonstrates that startup context can dominate a small request, but there is no matched
candidate run for that task. It is therefore baseline evidence only and is excluded from
the savings calculation.

## Published results

| Date | Change | Harness and model | Tasks | Baseline input p50 / p95 | Candidate input p50 / p95 | Median saving | Quality result | Status |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| 2026-09-21 | Portable hook, multi-harness setup, and measurement policy | Not yet benchmarked | 0 | Not available | Not available | Not claimed | 18 tests pass; no paired task eval | Benchmark pending |
| 2026-09-21 | One advisory-band smoke test, without and with Jev | Python hook; Jev 1.13.0 | 1 | 55,000 / not available | 55,000 / not available | 0% observed | Same final `retain` action; no compaction executed | Observation only |

## Latest smoke-test result

The [one-sample evidence](../benchmarks/context-savings/2026-09-21-simple/) compares the
same 55,000-token advisory state. Without Jev, deterministic fallback returned `retain` in
0.07 seconds. The live Jev path also returned `retain` in 0.95 seconds because the typed
response did not pass the confidence gate.

A diagnostic repeat showed Jev preferred `compact` with probability 0.69 and confidence
0.53. The 0.65 production floor rejected that advice. The diagnostic request used 438
input tokens and 40 output tokens with 864 ms measured client latency. No compaction ran,
so observed compaction savings were 0 percent. This single sample is not a production
savings benchmark.

## Required calculation

```text
median saving % = 100 * (baseline median input - candidate median input)
                    / baseline median input
```

Report p95 separately. Do not average percentages from unrelated harnesses or models.

## Benchmark contract

Use at least 20 representative tasks for the baseline and the candidate. Keep the model,
model context limit, repository revision, task set, permissions, tools, and scoring method
constant. Record:

- harness name and version;
- model identifier and context limit;
- hook order and threshold configuration;
- number of completed and failed tasks;
- input and output token p50 and p95;
- wall-clock p50 and p95;
- compaction and handoff counts;
- task success or eval score;
- any missing-context regression;
- a repository path or public artifact containing sanitized raw measurements.

Compare three configurations when possible:

1. Existing harness configuration.
2. Project-scoped static context cleanup only.
3. Static cleanup plus Jev as the first intelligent hook.

This separates savings from ordinary configuration cleanup and savings attributable to
the Jev-assisted compaction policy.

## Publication rules

- A single run is an observation, not a saving.
- Estimated, simulated, or projected values must be labeled and cannot enter the results
  table as measured savings.
- Quality must remain inside the declared tolerance.
- Raw evidence must exclude secrets, private transcripts, proprietary source, and prompts.
- Regressions stay visible. Do not delete an unfavorable result when adding a later one.
- Every hook release must update this page or explicitly retain `benchmark pending`.
