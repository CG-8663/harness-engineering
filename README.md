# harness-engineering

**Harness Engineering with Jev for efficient agent usage, agentic loops, and measurable
goal management.**

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

## Cut agent context usage

> **This is Harness Engineering with Jev for efficient agent usage.** It is a small,
> tested control layer around your existing agent. It is not another model, agent, proxy,
> or replacement for Claude Code, Grok, OpenCode, or Codex. Your native harness still
> owns the session and performs every approved context action.

The [portable Jev context-budget hook](docs/context-budget-hook.md) helps Claude Code,
Grok, OpenCode, Codex, and other agent harnesses decide when to retain a session, compact
it, or create a clean handoff.

Deterministic code owns hard limits, privacy, validation, and execution. Jev sees only six
small telemetry buckets and supplies one typed choice inside the ambiguous middle band.
Prompts, transcripts, source code, paths, command text, and credentials remain local.

**Hook order:** local deterministic privacy and hard-limit checks run first. Jev is then
the **first intelligent hook**. Any other semantic or model-backed context processor runs
after Jev. The native harness remains the only component that executes a context action.

### 1. Clone the project

```bash
git clone https://github.com/CG-8663/harness-engineering.git
cd harness-engineering
```

### 2. Install the TypeSafe skill once

Use the portable installer before running any of the agent commands below:

```bash
npx skills add typesafe-ai/skills --skill typesafe-ai
```

Select Claude Code, Grok, OpenCode, Codex, or your other target agent when prompted. Keep
the installation project-local unless you deliberately want the skill loaded in every
project.

Claude Code users may use the official plugin instead of the `npx` route:

```bash
claude plugin marketplace add typesafe-ai/skills
claude plugin install typesafe@typesafe-ai
```

Use one installation method so the agent does not load duplicate skill copies. If you use
the `npx` command, do not also install the Claude plugin for the same project.

### 3. Ask your preferred agent to install the hook

Complete the TypeSafe installation in step 2 first. The same reviewed task prompt then
works across harnesses.

**What to ask the agent:**

```text
Using the TypeSafe skill, install this repository's context-budget hook for the active
agent harness. First inspect the installed harness version and its native idle, stop, or
pre-request hook support. Keep context limits, privacy checks, hard compaction, fallbacks,
and execution deterministic in code. Use Jev only in the ambiguous advisory band for the
typed retain | compact | handoff Choice. Never send prompts, messages, source code,
commands, paths, credentials, or transcripts to Jev. Add adapter tests first, run the
existing test suite, and complete a no-spend dry run before any live request. Measure
baseline and candidate median/p95 token usage and task quality across at least 20
representative tasks. Preserve existing configuration, make changes reversible, report
rollback steps, and ask before changing global configuration or unrelated projects.
```

The commands below send the fuller reviewed version of this request from
[`AGENT_PROMPT.md`](hooks/context-budget/AGENT_PROMPT.md), so users do not need to retype
it.

#### Claude Code

```bash
claude -p < hooks/context-budget/AGENT_PROMPT.md
```

Claude users can invoke the installed skill directly with `/typesafe:typesafe-ai` when
working interactively.

#### Grok

```bash
grok --cwd . --prompt-file hooks/context-budget/AGENT_PROMPT.md
```

#### OpenCode

```bash
opencode run -f hooks/context-budget/AGENT_PROMPT.md \
  "Use the TypeSafe skill and complete the attached context-budget installation task."
```

#### Codex

```bash
codex exec -C . - < hooks/context-budget/AGENT_PROMPT.md
```

The agent should inspect the current harness version, add the smallest native adapter,
run the existing tests, perform a no-spend dry run, and report rollback instructions.
It must ask before changing global configuration or unrelated projects.

### 4. Judge the savings

Always compare representative completed tasks with the model, repository revision,
tools, and task set held constant. Track median and p95 input tokens, output tokens,
latency, task success, compactions, handoffs, and context-loss regressions.

Use these evaluation bands as engineering guidance, not promised savings:

| Reduction in median input tokens per completed task | Interpretation |
| --- | --- |
| Less than 10% | Marginal. Simplify the setup or remove the hook. |
| 10% to 25% | Useful when quality and latency do not regress. |
| 25% to 40% | Strong result. Confirm the same tasks still pass. |
| More than 40% | Excellent if genuine, but audit carefully for missing context or an unusually bloated baseline. |

Calculate the observed reduction with:

```text
savings % = 100 * (baseline median input - candidate median input) / baseline median input
```

Static cleanup often matters more than routing. Measure three stages separately:

1. Existing harness configuration.
2. Project-scoped skills, commands, instructions, and MCP servers only.
3. The scoped configuration plus the context-budget hook.

Do not claim a saving from one run. Use at least 20 representative tasks per
configuration and reject any result that lowers the task success rate beyond your chosen
tolerance. See the [full implementation and measurement guide](docs/context-budget-hook.md).
**Latest smoke test:** one identical advisory-band sample produced `retain` both without
and with Jev. Jev preferred `compact`, but confidence was 0.53 and the 0.65 safety gate
rejected it.

The hook correctly rejected the uncertain recommendation. No compaction occurred, so
observed savings were 0 percent, with approximately 0.88 seconds additional decision
latency. This is a useful safety result, but only one observation. We require at least 20
paired representative tasks before changing the threshold or claiming production
savings.

[See the diagnostic repeat](benchmarks/context-savings/2026-09-21-simple/with-jev.json)
or review the [complete sanitized evidence](benchmarks/context-savings/2026-09-21-simple/).
A public savings ledger will be added only after a qualified benchmark demonstrates
realized savings. Until then, no savings are claimed.

### Codex pilot: first-turn benefit is break-even

A controlled Codex CLI pair preserved exact-answer quality and reduced Codex input by
426 tokens (1.93%). The Jev decision itself used 477 tokens and 826 ms, making the first
continued turn effectively break-even across the two services. The result supports an
amortized strategy: compact only when at least two useful continued turns are expected.
It does not support a production savings claim.

[Review the sanitized Codex pilot](benchmarks/codex-token-burn/2026-09-21-pilot/) and use
the [numeric-only Codex usage monitor](hooks/codex-usage/) for future paired runs. The
monitor consumes the official `codex exec --json` stream and never stores prompts,
messages, transcripts or tool payloads.

### PR feedback wanted

Please [open a pull request](https://github.com/CG-8663/harness-engineering/pulls) or
[start an issue](https://github.com/CG-8663/harness-engineering/issues) if you can improve:

- native Claude Code, Grok, or OpenCode adapters;
- reliable token collection across harness versions;
- Windows and Linux installation flows;
- privacy and failure-mode tests;
- threshold calibration from real task suites;
- before-and-after charts that include quality as well as token usage.

For measurement PRs, include the harness and model versions, context limit, task count,
baseline and candidate median/p95 values, quality metric, configuration diff, and rollback
steps. Never include API keys, private transcripts, proprietary source, or raw prompts.

## Run the LFD loop

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
