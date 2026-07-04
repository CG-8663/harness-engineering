# lfd-loop — /goal + Loss Function Development harness

An efficient, reusable outer loop that runs a coding agent against a **blind** eval score,
fenced by hard time/money limits and kicked out of local maxima with forced entropy.

| File | What it is |
|------|-----------|
| `scripts/lfd-loop.sh` | The outer loop (entry point). Runs your agent, scores blind, reflects, forces entropy on stall, stops on success/time/money/iters. |
| `GOAL.template.md` | The loss-function template — target, constraints, instruments, forced entropy. Copy to `GOAL.md`. |
| `scripts/agent.sh` / `scripts/score.sh` | Mock agent + blind scorer for a no-spend dry run. |
| `SKILL.md` | Agent-Skill wrapper (lets a Cowork/Claude Code agent invoke this loop). |

## Dry run (no spend)

```bash
cd scripts && chmod +x *.sh
cp ../GOAL.template.md GOAL.md
AGENT_CMD=./agent.sh SCORE_CMD=./score.sh \
TARGET_BAR=95 MAX_ITERS=30 TIME_BUDGET_MIN=300 COST_CAP_USD=40 ./lfd-loop.sh
```

The mocks simulate a run that climbs, stalls at cycle 4 (triggering forced entropy), then
crosses the bar — so you can watch the whole control flow before spending a cent.

## Wiring a real run

- `AGENT_CMD` — a **headless** agent that reads the cycle prompt on stdin.
  E.g. `claude -p --max-turns 40 --dangerously-skip-permissions` or `codex exec`.
- `SCORE_CMD` — a **blind** scorer. Prints the numeric score on its **last** stdout line;
  lines above it are the per-item miss list fed back to the agent. It reads the hidden
  answer key itself and never exposes it.
- `COST_CMD` *(optional)* — prints cumulative dollars spent so the loop enforces the cap.

## Knobs (env vars)

| Var | Default | Meaning |
|-----|---------|---------|
| `TARGET_BAR` | 95 | Success bar; loop exits 0 when score ≥ this. |
| `MAX_ITERS` | 50 | Hard cycle cap (budget stop). |
| `TIME_BUDGET_MIN` | 300 | Wall-clock budget — the constraint agents always forget. |
| `COST_CAP_USD` | 40 | Total dollar ceiling on a disposable key. |
| `STALL_EPSILON` | 0.1 | Improvement below this = stalled → forced entropy next cycle. |
| `GOAL_FILE` | GOAL.md | Your loss function. |
| `RUN_DIR` | `./lfd-run-<ts>` | Per-run artifacts: prompts, agent output, `iteration-log.md`. |

Exit codes: `0` success · `10` time budget · `11` cost cap · `12` max iters · `2` config error.

## How it maps to the playbook

- **Blind target** — the loop passes only score + misses to the agent, never the answer key.
- **Constraints as hard stops** — time, money and iteration caps enforced by the loop.
- **Instruments in every prompt** — each cycle injects live readings (elapsed, spend, last score).
- **Forced entropy** — a stalled cycle forbids "same idea, harder" and demands a real jump.
- **Iteration log** — every cycle's hypothesis/score/misses is appended and fed back.
