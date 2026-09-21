# Repository instructions for agents

This repository is the public source of truth for Harness Engineering with Jev. Keep the
repository, its documentation, and published measurement evidence synchronized whenever
the context-budget hook, its adapters, thresholds, prompts, or operating guidance change.

## Jev is the first intelligent hook

Jev must be the first semantic or model-backed hook in the context-management chain. A
small local preflight runs before it only to validate the schema, enforce the privacy
allowlist, calculate deterministic thresholds, and handle hard safety limits. That
preflight is code, not another intelligent router.

Required order:

1. Local deterministic validation, privacy filtering, and hard-limit checks.
2. The Jev context-budget Choice, when the request is inside the advisory band.
3. Any later model-backed hook or optional context processor.
4. Native harness execution of the validated `retain`, `compact`, or `handoff` action.

Never send prompts, messages, source code, paths, command text, credentials, or transcripts
to Jev. Jev advises; deterministic code and the native harness control side effects.

## Update contract

For every material update:

- update the implementation guide and README when behavior or setup changes;
- publish a savings ledger only after a qualified benchmark demonstrates realized
  savings with baseline and candidate evidence;
- before savings are realized, keep zero-saving and negative observations in sanitized
  benchmark evidence and describe them explicitly as safety results, not savings;
- record task count, median and p95 input tokens, quality result, harness/model versions,
  and the evidence location;
- require at least 20 representative paired tasks before changing thresholds or making a
  production savings claim;
- run the relevant tests and record the result in `ACTIONS.md` and `SESSION.md`;
- keep changes reversible and never commit credentials or private prompt content;
- keep the configured GitHub branch current after publication has been authorized.

Do not publish an empty or zero-saving savings ledger. Never turn an estimate, a single
run, or a rejected compaction into a savings claim.
