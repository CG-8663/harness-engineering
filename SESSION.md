# Session

## 2026-09-21: context-budget hook

Built a harness-neutral classifier that emits `retain`, `compact`, or `handoff` advice.
It rejects unknown input fields and sends Jev only six bucketed telemetry fields. Hard
capacity limits, explicit phase boundaries, response validation, fallbacks, and action
execution remain deterministic. See `docs/context-budget-hook.md` and
`docs/testing/context-budget-hook.tdd.md`.

The README now leads with a four-step context-efficiency flow. Command syntax was checked
against Claude Code 2.1.278, Grok 1.0.34, and OpenCode 1.18.31. Savings are presented as
evaluation bands rather than guarantees, and contributors are asked to include quality,
privacy, version, measurement, and rollback evidence in feedback.

Public positioning is now explicit: Harness Engineering with Jev for efficient agent
usage. Jev provides a bounded typed judgment while deterministic code and the native
harness retain control.

Step 3 now includes the important agent request inline instead of exposing only harness
commands. The prompt covers native hook discovery, deterministic ownership, Jev privacy,
test-first adapter work, no-spend validation, measurement, reversibility, and scope.

The repository now has a durable update contract in `AGENTS.md`. Jev is the first
intelligent context hook, but local deterministic privacy validation and hard safety
limits remain ahead of every external call. `docs/context-savings.md` is the public
append-only measurement ledger. The initial entry says benchmark pending because there
is no paired production result from which to calculate a truthful saving.

The first one-sample smoke test used a 55,000-token advisory-band state. Deterministic
mode retained in 0.07 seconds. The live Jev path retained through fallback in 0.95 seconds.
An exact diagnostic repeat returned `compact` at probability 0.69 and confidence 0.53,
using 438 input and 40 output tokens with 864 ms client latency. Because confidence was
below 0.65 and no compaction executed, the published observed saving is 0 percent.
