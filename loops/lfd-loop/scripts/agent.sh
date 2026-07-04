#!/usr/bin/env bash
# Mock inner-loop agent for dry-running lfd-loop.sh. Reads the cycle prompt on
# stdin, pretends to work, and echoes what it "did". Replace with `claude -p ...`
# or `codex exec` for real runs.
cat > /dev/null   # consume the prompt
echo "[mock-agent] read goal + instruments; wrote code; ran tests; yielding."
sleep 0.2
