#!/usr/bin/env python3
"""Reduce a Codex JSONL event stream to one privacy-safe numeric usage record."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
from pathlib import Path
from typing import Any, Iterable, Mapping, Optional


USAGE_FIELDS = (
    "input_tokens",
    "cached_input_tokens",
    "cache_write_input_tokens",
    "output_tokens",
    "reasoning_output_tokens",
)
LABEL_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$")


def _token_count(usage: Mapping[str, Any], name: str) -> int:
    value = usage.get(name, 0)
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError("{} must be a non-negative integer".format(name))
    return value


def summarize(events: Iterable[Mapping[str, Any]], label: str) -> dict[str, Any]:
    """Return numeric usage from the last completed turn; discard all other content."""
    if not LABEL_PATTERN.fullmatch(label):
        raise ValueError("label must contain only letters, numbers, dot, underscore, or hyphen")

    last_usage: Optional[Mapping[str, Any]] = None
    completed_turns = 0
    for event in events:
        if isinstance(event, Mapping) and event.get("type") == "turn.completed":
            usage = event.get("usage")
            if not isinstance(usage, Mapping):
                raise ValueError("turn.completed usage must be an object")
            last_usage = usage
            completed_turns += 1
    if last_usage is None:
        raise ValueError("no turn.completed usage event found")

    numeric = {name: _token_count(last_usage, name) for name in USAGE_FIELDS}
    if numeric["cached_input_tokens"] > numeric["input_tokens"]:
        raise ValueError("cached_input_tokens cannot exceed input_tokens")
    numeric["uncached_input_tokens"] = numeric["input_tokens"] - numeric["cached_input_tokens"]
    numeric["total_tokens"] = numeric["input_tokens"] + numeric["output_tokens"]
    return {
        "schema_version": 1,
        "source": "codex_exec_json",
        "label": label,
        "completed_turns": completed_turns,
        "usage": numeric,
    }


def _read_events(stream: Iterable[str]) -> Iterable[Mapping[str, Any]]:
    for line in stream:
        if not line.strip():
            continue
        event = json.loads(line)
        if not isinstance(event, Mapping):
            raise ValueError("each JSONL event must be an object")
        yield event


def _append_record(path: Path, record: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        os.chmod(path, 0o600)
        handle.write(json.dumps(record, separators=(",", ":"), sort_keys=True) + "\n")


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--label", required=True, help="sanitized run label")
    parser.add_argument("--append", type=Path, help="optional JSONL metrics destination")
    args = parser.parse_args(argv)
    try:
        record = summarize(_read_events(sys.stdin), args.label)
        record["recorded_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        if args.append:
            _append_record(args.append, record)
    except (ValueError, json.JSONDecodeError, OSError) as error:
        sys.stderr.write(json.dumps({"error": "usage_monitor_failed", "message": str(error)}) + "\n")
        return 2
    print(json.dumps(record, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
