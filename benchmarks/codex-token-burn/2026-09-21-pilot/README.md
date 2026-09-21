# Codex token-burn pilot

Run on 21 September 2026 with Codex CLI 0.155.1, `gpt-5.6-luna`, and low reasoning
effort. This is one controlled synthetic pair, not a production savings claim and not a
public savings ledger.

Both runs answered the same threshold-retrieval task with the exact expected JSON. The
baseline received the full public implementation guide. The candidate received a compact
verified handoff after a live Jev decision approved `compact` at confidence 0.75.

| Measurement | Full context | Jev plus compact context | Difference |
| --- | ---: | ---: | ---: |
| Codex input tokens | 22,089 | 21,663 | -426 (-1.93%) |
| Codex uncached input tokens | 12,105 | 11,679 | -426 (-3.52%) |
| Codex output tokens | 81 | 20 | -61 |
| Codex total tokens | 22,170 | 21,683 | -487 (-2.20%) |
| Exact-answer quality | pass | pass | unchanged |
| Observed Codex wall time | 24.7 s | 17.6 s | -7.1 s |

Jev used 437 input and 40 output tokens and added 826 ms. Adding those 477 Jev tokens
to the candidate yields 22,160 combined tokens, only 10 fewer than the 22,170-token
baseline. That is effectively break-even for the first continued turn. Jev and Codex
tokens are not cost-equivalent, so this arithmetic is not a currency saving.

The useful design implication is amortization. At the observed 426 Codex input-token
reduction per continued turn, the 477-token Jev decision is recovered after about 1.12
similar turns. In practice, require at least two useful post-compaction turns before
expecting a clear token benefit. Longer retained histories may produce a much larger
benefit, but this pilot does not prove that.

The equal cached-input count in both Codex runs (9,984) makes the 426-token difference
attributable to the supplied task context rather than a cache-count change. Wall time is
reported only as an observation because two network calls do not control service
variance.

No threshold changed. No savings ledger is published. Run at least 20 representative
paired production tasks with equal quality before claiming savings.

Evidence:

- [`baseline.json`](baseline.json)
- [`candidate.json`](candidate.json)
- [`jev-request.json`](jev-request.json)
- [`jev-response.json`](jev-response.json)
