#!/usr/bin/env bash
# =============================================================================
# lfd-loop.sh — Loss-Function-Development outer loop
# -----------------------------------------------------------------------------
# Operationalizes Elvis Sun's /goal + LFD playbook: drop a coding agent in a
# feedback loop that descends toward a BLIND eval score, fenced in by hard
# time/money limits, watched by instruments, and kicked out of local maxima
# with forced entropy.
#
#   Inner loop  = your agent (codex / claude): write code, run tests, fix.
#   Outer loop  = THIS script: score -> reflect -> nudge -> repeat until the
#                 only direction left that moves the number is getting genuinely
#                 better at the task.
#
# You provide two pluggable commands and one goal file:
#   AGENT_CMD   headless agent invocation; receives the cycle prompt on stdin.
#   SCORE_CMD   BLIND scorer; prints "<score>" on the last stdout line, and may
#               print a per-item miss list above it. Never exposes the answer key.
#   GOAL_FILE   your loss function (see GOAL.template.md): target, constraints,
#               instruments, forced entropy.
#
# Stops on the FIRST of: score >= TARGET_BAR (success), wall-clock budget,
# dollar cap, or MAX_ITERS (budget stops). Failure never runs forever.
# =============================================================================
set -euo pipefail

# ----- Config (override via env or a sourced config file) --------------------
GOAL_FILE="${GOAL_FILE:-GOAL.md}"
AGENT_CMD="${AGENT_CMD:-}"          # e.g. "codex exec --dangerously-bypass ..." or "claude -p --max-turns 40"
SCORE_CMD="${SCORE_CMD:-}"          # e.g. "./score.sh"  (BLIND: reads hidden key, prints score)
COST_CMD="${COST_CMD:-}"           # optional: prints cumulative dollars spent so far

TARGET_BAR="${TARGET_BAR:-95}"     # success bar for the eval score (descend toward it)
MAX_ITERS="${MAX_ITERS:-50}"       # hard cap on cycles
TIME_BUDGET_MIN="${TIME_BUDGET_MIN:-300}"   # wall-clock budget in minutes (agents have NO sense of time)
COST_CAP_USD="${COST_CAP_USD:-40}"          # hard dollar ceiling on the whole run
STALL_EPSILON="${STALL_EPSILON:-0.1}"       # improvement below this = "stalled" -> force entropy
RUN_DIR="${RUN_DIR:-./lfd-run-$(date +%Y%m%d-%H%M%S)}"

# ----- Setup -----------------------------------------------------------------
[[ -n "$AGENT_CMD" ]] || { echo "FATAL: set AGENT_CMD (headless agent invocation)"; exit 2; }
[[ -n "$SCORE_CMD" ]] || { echo "FATAL: set SCORE_CMD (blind scorer -> prints score)"; exit 2; }
[[ -f "$GOAL_FILE" ]] || { echo "FATAL: GOAL_FILE '$GOAL_FILE' not found"; exit 2; }

mkdir -p "$RUN_DIR"
ITER_LOG="$RUN_DIR/iteration-log.md"
: > "$ITER_LOG"
START_EPOCH=$(date +%s)

log()  { printf '%s\n' "$*" | tee -a "$RUN_DIR/loop.log" >&2; }
elapsed_min() { echo $(( ( $(date +%s) - START_EPOCH ) / 60 )); }
spend_usd()   { [[ -n "$COST_CMD" ]] && $COST_CMD 2>/dev/null || echo 0; }

log "=== LFD loop started ==="
log "goal=$GOAL_FILE  target>=$TARGET_BAR  time<=${TIME_BUDGET_MIN}m  cost<=\$${COST_CAP_USD}  max_iters=$MAX_ITERS"

prev_score="-inf"
entropy_flag=0

# ----- Outer loop ------------------------------------------------------------
for (( iter=1; iter<=MAX_ITERS; iter++ )); do

  # --- Budget stops (checked BEFORE spending another cycle) ---
  el=$(elapsed_min); sp=$(spend_usd)
  if (( el >= TIME_BUDGET_MIN )); then log "STOP: wall-clock budget hit (${el}m)"; exit 10; fi
  if awk "BEGIN{exit !($sp >= $COST_CAP_USD)}"; then log "STOP: cost cap hit (\$$sp)"; exit 11; fi

  log ""
  log "----- cycle $iter/$MAX_ITERS  (elapsed ${el}m, spent \$$sp) -----"

  # --- Build the cycle prompt: goal + live instrument readings + forced entropy ---
  PROMPT_FILE="$RUN_DIR/cycle-$iter.prompt.md"
  {
    cat "$GOAL_FILE"
    echo
    echo "## Live instruments (this cycle)"
    echo "- cycle: $iter / $MAX_ITERS"
    echo "- wall-clock: ${el}m elapsed of ${TIME_BUDGET_MIN}m budget"
    echo "- spend: \$$sp of \$$COST_CAP_USD cap"
    echo "- last blind score: $prev_score  (target >= $TARGET_BAR)"
    echo
    echo "## Required this cycle"
    echo "1. OVERFIT REFLECTION: are you building a more general solution, or memorizing the eval?"
    echo "   If memorizing, your next change must REMOVE an eval-shaped artifact (cap a list, blind a"
    echo "   feature, widen the eval, reject a seed) — never add one."
    echo "2. Log your HYPOTHESIS, the expected failure mode, and the diagnostic before you code."
    echo "3. Do NOT read the eval answer key. It is scored out-of-band. Cheating the metric = failing."
    if (( entropy_flag == 1 )); then
      echo
      echo "## FORCED ENTROPY (last cycle stalled)"
      echo "The metric did not move. You may NOT run 'the same idea, harder' or turn the same knob again."
      echo "Make a real, non-obvious jump. Think outside the box: try a different mechanism entirely."
    fi
    if [[ -s "$ITER_LOG" ]]; then
      echo
      echo "## Iteration log so far (your own past decisions — reflect across it)"
      tail -n 40 "$ITER_LOG"
    fi
  } > "$PROMPT_FILE"

  # --- INNER LOOP: hand the agent control until it yields ---
  log "running agent..."
  set +e
  $AGENT_CMD < "$PROMPT_FILE" > "$RUN_DIR/cycle-$iter.agent.out" 2>&1
  agent_rc=$?
  set -e
  (( agent_rc == 0 )) || log "warn: agent exited rc=$agent_rc (continuing to score anyway)"

  # --- SCORE: blind. scorer prints score on its LAST line ---
  log "scoring (blind)..."
  set +e
  score_out="$($SCORE_CMD 2>>"$RUN_DIR/loop.log")"
  set -e
  score="$(printf '%s\n' "$score_out" | tail -n1 | tr -dc '0-9.-')"
  [[ -n "$score" ]] || { log "warn: scorer returned no number; treating as 0"; score=0; }
  miss="$(printf '%s\n' "$score_out" | sed '$d')"   # everything above the score line = miss list

  # --- Record to the iteration log ---
  {
    echo "### cycle $iter — score=$score (prev=$prev_score) elapsed=${el}m spend=\$$sp"
    [[ -n "$miss" ]] && { echo "misses:"; printf '%s\n' "$miss" | sed 's/^/  /'; }
    echo
  } >> "$ITER_LOG"
  log "score=$score (prev=$prev_score)"

  # --- Success stop ---
  if awk "BEGIN{exit !($score >= $TARGET_BAR)}"; then
    log "SUCCESS: score $score >= target $TARGET_BAR after $iter cycles (${el}m, \$$sp)"
    log "run artifacts in: $RUN_DIR"
    exit 0
  fi

  # --- Stall detection -> arm forced entropy for next cycle ---
  if [[ "$prev_score" == "-inf" ]]; then
    entropy_flag=0
  elif awk "BEGIN{exit !(($score - $prev_score) < $STALL_EPSILON)}"; then
    log "stall detected (delta < $STALL_EPSILON) -> forcing entropy next cycle"
    entropy_flag=1
  else
    entropy_flag=0
  fi
  prev_score="$score"
done

log "STOP: reached MAX_ITERS ($MAX_ITERS) without hitting target $TARGET_BAR"
log "best/last score: $prev_score  —  run artifacts in: $RUN_DIR"
exit 12
