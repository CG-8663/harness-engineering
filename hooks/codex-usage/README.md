# Codex usage monitor

`codex_usage.py` reduces Codex's supported `exec --json` event stream to one numeric
usage record. It ignores agent messages, tool arguments, command output, prompts and
transcripts. The optional JSONL destination is created with mode `0600`.

Run a measured task like this:

```bash
codex exec --ephemeral --json -C . "TASK" |
  python3 hooks/codex-usage/codex_usage.py \
    --label baseline-task-01 \
    --append .harness-metrics/codex-usage.jsonl
```

The record contains input, cached-input, uncached-input, cache-write, output, reasoning
and total token counts. `output_tokens` already includes reasoning tokens, so
`total_tokens` is `input_tokens + output_tokens`.

This monitor measures Codex tokens. It does not infer the ChatGPT/Codex weekly quota or
convert Jev and Codex tokens into money. Those units can have different pricing and
accounting rules.

Official Codex references:

- [Non-interactive mode and JSONL events](https://learn.chatgpt.com/docs/non-interactive-mode)
- [Codex hooks](https://learn.chatgpt.com/docs/hooks)

## Test

```bash
python3 -m unittest discover -s hooks/codex-usage/tests -v
```
