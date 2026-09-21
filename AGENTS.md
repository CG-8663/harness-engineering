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
- update `docs/context-savings.md` in the same commit;
- publish only measured savings with baseline and candidate evidence;
- record task count, median and p95 input tokens, quality result, harness/model versions,
  and the evidence location;
- mark results `benchmark pending` when paired measurements do not exist;
- run the relevant tests and record the result in `ACTIONS.md` and `SESSION.md`;
- keep changes reversible and never commit credentials or private prompt content;
- keep the configured GitHub branch current after publication has been authorized.

Documentation-only changes still receive a savings-ledger entry when they affect public
claims or measurement guidance. Never turn an estimate or a single run into a savings
claim.
