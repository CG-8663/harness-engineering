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

- [ ] `docs/context-savings.md` is updated in this PR.
- [ ] Baseline and candidate use the same model, task set, tools, and scoring method.
- [ ] The report includes task count, input-token p50/p95, quality, and harness/model versions.
- [ ] Any unmeasured result is labeled `benchmark pending`, not presented as a saving.

Evidence or benchmark path:

Quality result and accepted tolerance:

Measured median input-token saving, or `not claimed`:

## Privacy

- [ ] No secrets, private transcripts, proprietary source, or raw prompts are included.
