# <loop-name>

> One-line description of what this loop optimizes and when to reach for it.

## What it does
<2–4 sentences: the outcome metric it descends toward, and the inner/outer split.>

## Dry run (no spend)
```bash
cd scripts && chmod +x *.sh
AGENT_CMD=./agent.sh SCORE_CMD=./score.sh \
TARGET_BAR=95 MAX_ITERS=30 TIME_BUDGET_MIN=300 COST_CAP_USD=40 ./loop.sh
```

## Real run
```bash
AGENT_CMD='<headless agent>' SCORE_CMD='<blind scorer>' COST_CMD='<spend reporter>' \
TARGET_BAR=<n> TIME_BUDGET_MIN=<m> COST_CAP_USD=<$> ./loop.sh
```

## Knobs (env vars)
| Var | Default | Meaning |
|-----|---------|---------|
| `TARGET_BAR` | 95 | Success bar. |
| `MAX_ITERS` | 50 | Hard cycle cap. |
| `TIME_BUDGET_MIN` | 300 | Wall-clock budget. |
| `COST_CAP_USD` | 40 | Dollar ceiling. |

Exit codes: `0` success · `10` time · `11` cost · `12` max iters · `2` config error.

## Notes
<Cheap paths you've fenced off; anything a runner should watch on cycle 1.>
