#!/usr/bin/env bash
# Mock BLIND scorer for dry-running lfd-loop.sh. Simulates a run that climbs,
# stalls (to trigger forced entropy), then crosses the bar. Prints a miss list,
# then the score on the LAST line. Real scorer reads a hidden eval key and never
# exposes it to the agent.
STATE="${TMPDIR:-/tmp}/lfd_mock_score_state"
n=$(( $(cat "$STATE" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$STATE"
case "$n" in
  1) s=40 ;; 2) s=70 ;; 3) s=88 ;; 4) s=88.05 ;;  # cycle 4 stalls -> entropy
  5) s=93 ;; *) s=96; rm -f "$STATE" ;;           # cross the bar, reset for reruns
esac
echo "miss: item-17 (recall), item-42 (recall), item-88 (dupe)"
echo "$s"
