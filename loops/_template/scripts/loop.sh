#!/usr/bin/env bash
# =============================================================================
# loop.sh — scaffold for a new outer loop. Copy loops/_template to loops/<name>
# and adapt. Keeps the non-negotiables: hard stops for success/time/money/iters,
# a blind scorer, an iteration log, and forced entropy on stall.
# See loops/lfd-loop/scripts/lfd-loop.sh for a complete reference implementation.
# =============================================================================
set -euo pipefail

GOAL_FILE="${GOAL_FILE:-GOAL.md}"
AGENT_CMD="${AGENT_CMD:-}"            # headless agent; reads cycle prompt on stdin
SCORE_CMD="${SCORE_CMD:-}"           # BLIND scorer; prints score on last stdout line
COST_CMD="${COST_CMD:-}"             # optional: prints cumulative dollars spent

TARGET_BAR="${TARGET_BAR:-95}"
MAX_ITERS="${MAX_ITERS:-50}"
TIME_BUDGET_MIN="${TIME_BUDGET_MIN:-300}"
COST_CAP_USD="${COST_CAP_USD:-40}"
STALL_EPSILON="${STALL_EPSILON:-0.1}"

[[ -n "$AGENT_CMD" ]] || { echo "FATAL: set AGENT_CMD"; exit 2; }
[[ -n "$SCORE_CMD" ]] || { echo "FATAL: set SCORE_CMD"; exit 2; }

start=$(date +%s)
elapsed_min(){ echo $(( ( $(date +%s) - start ) / 60 )); }
spend_usd(){ [[ -n "$COST_CMD" ]] && $COST_CMD 2>/dev/null || echo 0; }

prev="-inf"; entropy=0
for (( i=1; i<=MAX_ITERS; i++ )); do
  el=$(elapsed_min); sp=$(spend_usd)
  (( el >= TIME_BUDGET_MIN )) && { echo "STOP: time"; exit 10; }
  awk "BEGIN{exit !($sp >= $COST_CAP_USD)}" && { echo "STOP: cost"; exit 11; }

  # TODO: build the cycle prompt from $GOAL_FILE + live instruments + (entropy? kick),
  #       run the agent, then score BLIND. Model it on lfd-loop.sh.
  #   $AGENT_CMD < prompt.md
  #   score=$($SCORE_CMD | tail -n1 | tr -dc '0-9.-')

  score=0   # <- replace with real blind score
  awk "BEGIN{exit !($score >= $TARGET_BAR)}" && { echo "SUCCESS ($score)"; exit 0; }

  if [[ "$prev" != "-inf" ]] && awk "BEGIN{exit !(($score-$prev) < $STALL_EPSILON)}"; then
    entropy=1   # force a non-obvious jump next cycle
  else
    entropy=0
  fi
  prev="$score"
done
echo "STOP: max iters ($MAX_ITERS), last=$prev"; exit 12
