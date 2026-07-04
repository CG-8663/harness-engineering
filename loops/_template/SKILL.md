---
name: <loop-name>
description: >-
  <One or two sentences on what this loop optimizes.> Use when the user wants to
  <trigger scenario>. Triggers: "<keyword>", "<keyword>", "agentic loop",
  "loss function", "/goal", "harness".
---

# <loop-name>

<What the loop does, in the two-loop framing: inner = coding agent, outer = this loop.>

## Workflow
1. Copy `GOAL.template.md` to `GOAL.md` and fill in all four parts (target, constraints,
   instruments, forced entropy).
2. Wire `AGENT_CMD` (headless agent) and `SCORE_CMD` (blind scorer).
3. Dry-run with the mocks (no spend), then set the fences and run for real.
4. Sit with cycle 1 before walking away.

## Files
- `scripts/loop.sh` — the outer loop (entry point).
- `GOAL.template.md` — the loss-function template.
- `scripts/agent.sh`, `scripts/score.sh` — mocks for a no-spend dry run.
