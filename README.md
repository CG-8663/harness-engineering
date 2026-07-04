# harness-engineering — Agentic Loops & Goals Management

A growing collection of **agentic loops** and **goal/loss-function harnesses** for AI
engineering. Each loop here is a self-contained, runnable pattern for putting a coding
agent (Codex, Claude Code, or any headless agent) inside a feedback loop and letting it
descend toward a measurable outcome — safely, cheaply, and without babysitting.

> The premise, borrowed from the practitioners who popularized it: you can solve almost
> any engineering problem if you stop trying to solve it yourself, build a **harness** so
> an agent can observe and act on it, and drop it in its **own feedback loop** until it's
> solved. Your job shifts from *writing code* to *designing the loop that writes the code*.

## The two loops

Everything here is gradient descent all the way down, at two scales:

- **Inner loop — the coding agent.** Write code, run tests, fix. Short horizon, fast
  feedback, one objective: make the tests pass. This is already automated by coding agents.
- **Outer loop — goal / loss-function management.** Drive the whole system toward an
  *outcome metric* across many cycles: measure → reflect → change tack → descend. Long
  horizon, sparse feedback. This is the part this repo helps you run.

What's left for you is **defining the loss function** — what the loop optimizes toward,
and which cheap shortcuts you fence off so the agent can't cheat the metric.

## What's in here

| Loop | What it does | Status |
|------|--------------|--------|
| [`loops/lfd-loop`](loops/lfd-loop) | Loss-Function-Development outer loop: run an agent against a **blind** eval score, fenced by hard time/money limits, with forced entropy to escape local maxima. | ✅ ready |
| _more coming_ | Add your own — see [CONTRIBUTING](CONTRIBUTING.md). | |

## Quick start

```bash
git clone https://github.com/cg-8663/harness-engineering.git
cd harness-engineering/loops/lfd-loop

# 1. Define your loss function
cp GOAL.template.md GOAL.md      # then fill in all four sections

# 2. Dry-run with the mocks (no API spend) to see the control flow
cd scripts && chmod +x *.sh
AGENT_CMD=./agent.sh SCORE_CMD=./score.sh \
TARGET_BAR=95 MAX_ITERS=30 TIME_BUDGET_MIN=300 COST_CAP_USD=40 ./lfd-loop.sh

# 3. Real run: swap in your headless agent + blind scorer, set the fences
AGENT_CMD='claude -p --max-turns 40' \
SCORE_CMD='python eval/score.py --eval eval/hidden.jsonl' \
COST_CMD='python eval/spend.py --total' \
TARGET_BAR=95 TIME_BUDGET_MIN=300 COST_CAP_USD=40 ./lfd-loop.sh
```

See each loop's own `README.md` and `SKILL.md` for details. Concepts and vocabulary live
in [docs/concepts.md](docs/concepts.md).

## Anatomy of a good loss function

Four parts. Any part you leave blank is a fence you didn't build — and the optimizer will
sprint down whatever cheap path you left open.

1. **Target** — the metric and bar, over a *large*, **blinded** eval (the agent never sees
   the answer key), measured at the right resolution.
2. **Constraints** — wall-clock budget, money caps on a disposable key, allowed
   surface/providers, methodology. Agents have no sense of time or money unless you give
   them one.
3. **Instruments** — one CLI per constraint (score, time, provider budget, LLM spend, token
   usage). *A constraint without an instrument is just a vibe.*
4. **Forced entropy** — overfit reflection each cycle, a non-obvious jump on stall, and an
   iteration log. Left alone, an agent walks up the same hill forever.

## One rule before you walk away

Don't kick a loop off and go to bed on cycle 1. **Sit with the first cycle.** Watch what it
touches. Confirm the harness you built is actually being used. *Then* let it run overnight.

## Ethics

These loops are a form of distillation moved to prompt-time — fitting to **publicly**
findable artifacts. Distilling ToS-gated, login-walled, or paid output, or enumerating a
codebase's attack surface, is out of bounds. Lean on the word *publicly*.

## License

[Apache-2.0](LICENSE).

## Credits

The LFD pattern operationalized here follows the `/goal` + Loss-Function-Development
playbook by Elvis Sun ([loss-function-development](https://github.com/elvisun/loss-function-development)).
