## What changed

Describe the harness, hook, threshold, adapter, prompt, or documentation change.

## Jev-first ordering

- [ ] Local deterministic privacy and hard-limit checks still run before external calls.
- [ ] Jev remains the first semantic or model-backed context hook.
- [ ] No prompt, transcript, source, path, command, or credential is sent to Jev.
- [ ] The native harness still owns context actions and side effects.

## Verification

- [ ] Relevant tests pass.
- [ ] A no-spend dry run passes.
- [ ] Rollback steps are documented.

## Savings evidence

- [ ] Baseline and candidate use the same model, task set, tools, and scoring method.
- [ ] The report includes task count, input-token p50/p95, quality, and harness/model versions.
- [ ] A savings ledger is published or updated only if at least 20 paired tasks show
      realized savings without an unacceptable quality regression.
- [ ] Zero-saving, negative, estimated, or unmeasured results are kept as safety evidence
      and are not presented in a savings ledger.

Evidence or benchmark path:

Quality result and accepted tolerance:

Measured median input-token saving, or `not realized`:

## Privacy

- [ ] No secrets, private transcripts, proprietary source, or raw prompts are included.
