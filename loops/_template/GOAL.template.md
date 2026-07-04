# /goal — Loss Function

> Fill every section. A loss function has four parts. Any part you leave blank is a
> fence you didn't build — and the optimizer will sprint down whatever cheap path
> you left open. "I told it where to go and left every shortcut wide open" is how
> the agent cheats three times before it works.

## 0. One-line objective
Build <X>. Make the tests pass. **Then iterate against the eval below until you hit the bar.**
(Spec-driven development is the *start* here, not the finish line.)

---

## 1. TARGET — what "better" means, as a number the agent descends toward
- **Metric:** <e.g. recall@k against the eval set, pixel-diff == 0, latency p95 < N ms>
- **Bar:** reach **>= <TARGET_BAR>** (set `TARGET_BAR` in the loop to match).
- **Eval size:** <hundreds–thousands of items>. Large enough that enumeration doesn't pay.
  A small eval gets memorized in one round; the more the better.
- **BLIND:** the answer key lives only in the out-of-band scorer. You (the agent) never
  see it during a run. It is revealed only at scoring, as a score + per-item miss list.
- **Resolution:** the scorer measures the *real* thing, not a proxy. (An LLM "rate two
  screenshots" judge approves 12px-off UI clones because it compares embeddings, not
  pixels. If you want pixel-perfect, the instrument is a pixel-diff, and the goal is
  "until pixel diff == 0".)

## 2. CONSTRAINTS — what you're allowed to do, and what you're not
- **Time:** wall-clock budget = <N> min/hours. An 80% solution in 2h beats a 100% one in
  30 days. (Set `TIME_BUDGET_MIN`.) Agents have no sense of time — this is the constraint
  they always forget.
- **Money:** hard caps on every paid call — crawler credits, LLM spend, and a total dollar
  ceiling on a **disposable** key. (Set `COST_CAP_USD`.)
- **Surface:** allowed providers, allowed models, concurrency ceilings. Sandbox the agent
  to only the systems/files/directories it may touch: <list them>.
- **Methodology:** is LLM analysis allowed, or only deterministic logic? Which data sources
  may it use? Spell it out: <...>.

## 3. INSTRUMENTS (the harness) — one CLI per constraint, or the constraint is just a vibe
> "A constraint without an instrument is a vibe — the agent will violate it cheerfully
> because it can't tell it's violating it." Ship a command for each:
- **Target measurement:** `<cmd>` → prints the score at the right resolution (this is `SCORE_CMD`).
- **Time accounting:** `<cmd>` → timestamps each step + total wall-clock elapsed.
- **Provider budget:** `<cmd>` → crawler/scrape credits remaining, burn this loop, cumulative,
  projected burn before the next paid batch.
- **LLM spend:** `<cmd>` → dollars spent on data-plane API calls so far (this can feed `COST_CMD`).
- **Agent/token usage:** `<cmd>` → how many tokens this optimization has burned (the gradient
  of the current step). The loop should be self-aware.
> You can't optimize what you can't see.

## 4. FORCED ENTROPY — kick the agent out of local maxima (it won't leave on its own)
- **Overfit reflection, every cycle:** "Am I generalizing or memorizing the eval?" If
  memorizing, the next change must **remove** an eval-shaped artifact (cap a list, blind a
  feature, widen the eval, reject a seed) — never add one.
- **Force entropy on stall:** if the last cycle didn't move the metric, the next one may not
  be "same idea, harder." Make a real, non-obvious jump. (The loop injects this automatically.)
- **Iteration log:** log the hypothesis, the expected failure mode, and the diagnostic each
  step, so you can reflect across compactions.

---

### Known cheap paths to fence off (fill in as you catch them)
- [ ] Seeding data that mirrors the eval and declaring victory → blind the eval.
- [ ] Learning by miss (one keyword per missed item) → cap the list; widen the eval.
- [ ] Grinding hours for a 2% gain → wall-clock budget.
- [ ] Optimizing a proxy metric instead of the real thing → fix the target instrument.
