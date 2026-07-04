# Concepts & vocabulary

Shared language for the loops in this repo. Read this once; each loop assumes it.

## Harness engineering
Before an agent can solve a problem, it needs to *observe and act on it like a member of
the team*. A harness is the set of tools, commands, logs, and sandboxed surface that lets
it do that. "Give it everything it needs to debug like a real dev" is harness engineering.
A great agent with no harness flails; a modest agent with a great harness one-shots hard
bugs.

## Inner loop vs outer loop
- **Inner loop** — the coding agent's own cycle: write code → run tests → fix. One
  objective (make the tests pass), fast feedback, short horizon. Already automated.
- **Outer loop** — driving the whole system toward an *outcome metric* across many cycles:
  ship → measure → change tack → descend. Sparse feedback, long horizon. This is the
  product team's loop, compressed into a run. The loops in this repo automate it.

## Spec-driven vs loss-function-driven development
- **Spec-driven (SDD):** "Build this. Make the tests pass." A test suite is *finite* — done
  the moment it's green.
- **Loss-function-driven (LFD):** "Build this. Make the tests pass. *Then* iterate against
  these 1,000 eval cases." A large eval at 95% is a *target you descend toward* — there's
  no exit short of the bar. The spec becomes the **starting** line, not the finish line.

Why it matters: the agent makes hundreds of decisions you never see, and each resolves
against *something*. If you didn't write the target, the agent picks one — and it picks
whatever is cheapest to satisfy.

## The four parts of a loss function
1. **Target** — the metric + bar; a *large*, **blind** eval; measured at the right
   resolution (a proxy metric gets optimized instead of the real thing).
2. **Constraints** — time, money, surface, methodology. What the agent may and may not do.
3. **Instruments** — one CLI per constraint. *You can't optimize what you can't see*, and a
   constraint the agent can't measure is one it violates cheerfully.
4. **Forced entropy** — overfit reflection, a non-obvious jump on stall, an iteration log.

## Why agents "cheat" (and why it's your bug, not theirs)
An agent is an optimizer. Every cheap path you don't fence off is a direction it will
sprint down. Classic failure ladder:

| Round | What the agent did | The fix |
|-------|--------------------|---------|
| 1 | Generated seed data mirroring the eval, "100%" in 5 min | **Blind** the eval |
| 2 | Learned by miss — one keyword per missed item | **Cap** the list |
| 3 | Enumerated anyway across a bigger eval | **Widen** the eval |
| 4 | Nothing left but genuinely getting better | ✅ it ran for real |

The cheating isn't a bug in the agent; it's a bug in the *target*. Close the cheap paths
until the only direction that moves the number is doing the task well.

## Forced entropy
Each cycle continues from the previous run's context — the agent reads its own last hundred
decisions and keeps walking up the same hill. Local maxima are the default. So entropy must
be *forced*: reflect on overfitting every cycle, and on a stall, require a real non-obvious
jump instead of "the same knob, harder."

## Budget discipline
Agents have no innate sense of **time** or **money**. An 80% solution in 2 hours beats a
100% one in 30 days. Always set a wall-clock budget and a hard dollar cap on a **disposable**
key, and give the agent instruments to read both.

## Ethics: publicly findable only
LFD is distillation at prompt-time, fit to artifacts a company *publishes* to win customers
— fair to learn from, the oldest move in software. It is **not** for ToS-gated, login-walled,
or paid output, and never for enumerating a codebase's attack surface. Lean on *publicly*.
