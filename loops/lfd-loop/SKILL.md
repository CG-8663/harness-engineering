---
name: lfd-loop
description: >-
  Run a coding agent (Codex / Claude Code) in an unattended optimization loop
  that descends toward a blind eval score — Elvis Sun's /goal + Loss Function
  Development (LFD) playbook, operationalized. Use when the user wants to build,
  clone, or optimize something against measurable expected outputs; set up a
  "/goal" or agentic outer loop; run an overnight/long-running agent loop with
  time and dollar budgets; design a loss function, eval harness, or scoring
  instrument; or stop an agent from cheating/overfitting an eval. Triggers:
  "agentic loop", "loss function", "LFD", "/goal", "harness", "spec-driven",
  "optimize against an eval", "run the agent overnight", "make it match theirs".
---

# LFD Loop — /goal + Loss Function Development

Operationalizes the two-loop model: the **inner loop** is a coding agent
(write code, run tests, fix); the **outer loop** (`scripts/lfd-loop.sh`) drives
the whole system toward an outcome metric across many cycles, fenced by hard
time/money limits and kicked out of local maxima with forced entropy.

The human's only real job is **defining the loss function**. This skill helps
do that, then runs it.

## When to use
- Building or cloning something where "good" is a public, measurable artifact
  (recall against an eval set, pixel-perfect UI, latency, output match).
- Setting up an unattended / overnight agent run that must not burn unbounded
  time or money.
- An agent keeps overfitting or "cheating" an eval and needs fencing.

## Workflow
1. **Copy the template.** `cp GOAL.template.md GOAL.md` and fill in all four
   parts. Do not skip any — every empty section is an open cheap path the
   optimizer will sprint down.
   - **Target** — the metric + bar, a *large* eval, **blinded** (answer key never
     shown to the agent), measured at the right resolution.
   - **Constraints** — wall-clock budget (agents have no sense of time), money
     caps on a disposable key, allowed surface/providers, methodology.
   - **Instruments** — one CLI per constraint (score, time, provider budget, LLM
     spend, token usage). A constraint without an instrument is just a vibe.
   - **Forced entropy** — overfit reflection each cycle, a non-obvious jump on
     stall, and an iteration log.

2. **Wire two commands.**
   - `AGENT_CMD` — headless agent reading the cycle prompt on stdin, e.g.
     `claude -p --max-turns 40 --dangerously-skip-permissions` or `codex exec`.
   - `SCORE_CMD` — **blind** scorer; prints the numeric score on its LAST stdout
     line, miss list above it. It reads the hidden key itself and never exposes it.
   - `COST_CMD` *(optional)* — prints cumulative dollars so the loop enforces the cap.

3. **Dry-run first (no spend)** with the bundled mocks to watch the control flow
   (climb → stall → forced entropy → cross the bar):
   ```bash
   cd scripts && chmod +x *.sh
   cp ../GOAL.template.md GOAL.md
   AGENT_CMD=./agent.sh SCORE_CMD=./score.sh \
   TARGET_BAR=95 MAX_ITERS=30 TIME_BUDGET_MIN=300 COST_CAP_USD=40 ./lfd-loop.sh
   ```

4. **Real run.** Swap in real `AGENT_CMD`/`SCORE_CMD` and set the fences
   (`TARGET_BAR`, `TIME_BUDGET_MIN`, `COST_CAP_USD`, `MAX_ITERS`). Then — per the
   playbook — **sit with cycle 1**, confirm the harness is actually being used,
   *then* let it run.

## Knobs (env vars)
`TARGET_BAR` (95) · `MAX_ITERS` (50) · `TIME_BUDGET_MIN` (300) ·
`COST_CAP_USD` (40) · `STALL_EPSILON` (0.1) · `GOAL_FILE` (GOAL.md) ·
`RUN_DIR` (`./lfd-run-<ts>`). Exit codes: `0` success · `10` time · `11` cost ·
`12` max iters · `2` config error.

## Files
- `scripts/lfd-loop.sh` — the outer loop (main entry point).
- `GOAL.template.md` — the loss-function template (four parts).
- `scripts/agent.sh`, `scripts/score.sh` — mocks for the no-spend dry run.

## Ethics
LFD is distillation at prompt-time, fit to **publicly** findable artifacts only.
Not for ToS-gated, login-walled, or paid output, and never for enumerating a
codebase's attack surface. Lean on the word *publicly*.

## Reference
Skill by Elvis Sun that auto-generates these goals/harnesses:
https://github.com/elvisun/loss-function-development
