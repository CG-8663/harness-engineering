# Agent task: install the context-budget hook

Use the TypeSafe skill and its current live documentation for this task.

Audit this repository's agent startup context and native hook capabilities. Integrate
`hooks/context-budget/context_budget.py` with the smallest supported idle, stop, or
pre-request adapter for the active harness.

Requirements:

1. Keep context limits, reserves, hard compaction, privacy checks, action execution, and
   failure fallback deterministic in code.
2. Use Jev only inside the hook's advisory band and only for the typed
   `retain | compact | handoff` Choice.
3. Never send prompts, messages, source code, command text, file paths, credentials, or
   transcripts to Jev. Send only the six bucketed fields produced by the hook.
4. Read `TYPESAFE_API_KEY` only from the harness's approved secret store or inherited
   environment. Never print, persist, or place it in a command argument.
5. Do not enable automatic `handoff` unless the harness supplies an explicit observed
   phase boundary.
6. Preserve existing user configuration and make every change reversible.
7. Run the existing unit tests, add adapter tests first, and verify one disposable dry run
   without API spend before any live Jev request.
8. Measure baseline and candidate input tokens, output tokens, latency, and task success.
   Report medians and p95 values. Do not claim savings from a single run.
9. Report the exact files changed, native event used, rollback steps, and any capability
   the harness does not support.

First identify unused skills, commands, instruction duplication, and MCP schemas in this
project's startup scope. Narrow project-local configuration reversibly before adding the
adapter. Report global cleanup opportunities separately, and do not modify unrelated
projects or global configuration unless the user explicitly approves that wider scope.
