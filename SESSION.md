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
