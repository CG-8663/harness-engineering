# Contributing a new loop

This repo is a collection. Each loop is a self-contained folder under `loops/` that anyone
can clone and run. To add one, copy the scaffold and fill it in.

## 1. Scaffold

```bash
cp -R loops/_template loops/<your-loop-name>
cd loops/<your-loop-name>
chmod +x scripts/*.sh
```

## 2. Required files

Every loop folder must contain:

- **`README.md`** — what the loop does, quick start (with a no-spend dry run), the env-var
  knobs, and exit codes.
- **`scripts/loop.sh`** (or similar) — the runnable entry point. Keep config in env vars
  with sane defaults; enforce hard stops (time, money, iterations) in the loop itself, not
  in the agent prompt.
- **`GOAL.template.md`** — if the loop is goal/eval-driven, ship the loss-function template
  users copy to `GOAL.md`.
- **`SKILL.md`** *(optional)* — an Agent-Skill wrapper so a Cowork/Claude Code agent can
  invoke the loop. Frontmatter needs `name` and a trigger-rich `description`.
- Mock `agent.sh` / `score.sh` (or equivalent) so the loop can be dry-run with **no spend**.

## 3. Design checklist

A loop is ready when:

- [ ] It runs end-to-end against **mocks** with zero API spend.
- [ ] Every constraint has an **instrument** (a CLI/command that reports it).
- [ ] Hard stops exist for **success**, **failure**, and **budget** (time + money + iters).
- [ ] Any eval is **blind** — the agent never sees the answer key during a run.
- [ ] There's a **forced-entropy** mechanism (or a documented reason it isn't needed).
- [ ] An **iteration log** records hypothesis + result each cycle.
- [ ] The README documents knobs, exit codes, and the "sit with cycle 1" rule.

## 4. Register it

Add a row to the table in the top-level [`README.md`](README.md) so people can find it.

## 5. Style

- Bash loops: `set -euo pipefail`, absolute-safe, config via env with defaults.
- Never bake secrets or API keys into files. Use disposable keys and hard dollar caps.
- Keep the ethics line: loops target **publicly** findable artifacts only.
