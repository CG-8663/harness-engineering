#!/usr/bin/env python3
"""Portable context-budget classifier with an optional Jev advisory step."""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Dict, Mapping, Optional


API_URL = "https://api.typesafe.ai/v1/systemone"
ALLOWED_FIELDS = {
    "input_tokens",
    "context_limit",
    "reply_reserve",
    "compaction_reserve",
    "turn_count",
    "failed_attempts",
    "phase",
    "cache_mode",
    "phase_boundary",
}
PHASES = {"discovery", "planning", "implementation", "verification", "handoff", "unknown"}
CACHE_MODES = {"cold", "warm", "unknown"}
ACTIONS = {"retain", "compact", "handoff"}
MAX_STDIN_BYTES = 16_384


@dataclass(frozen=True)
class Policy:
    soft_ratio: float = 0.63
    fallback_ratio: float = 0.84
    confidence_floor: float = 0.65

    def validate(self) -> None:
        if not 0 < self.soft_ratio < self.fallback_ratio < 1:
            raise ValueError("policy ratios must satisfy 0 < soft < fallback < 1")
        if not 0 <= self.confidence_floor <= 1:
            raise ValueError("confidence floor must be between 0 and 1")


def _integer(payload: Mapping[str, Any], name: str, minimum: int = 0) -> int:
    value = payload.get(name)
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError("{} must be an integer >= {}".format(name, minimum))
    return value


def _enum(payload: Mapping[str, Any], name: str, allowed: set[str]) -> str:
    value = payload.get(name, "unknown")
    if not isinstance(value, str) or value not in allowed:
        raise ValueError("{} must be one of {}".format(name, ", ".join(sorted(allowed))))
    return value


def _bucket(value: int, boundaries: tuple[int, ...], labels: tuple[str, ...]) -> str:
    for boundary, label in zip(boundaries, labels):
        if value <= boundary:
            return label
    return labels[-1]


def _validated_input(payload: Mapping[str, Any]) -> Dict[str, Any]:
    if not isinstance(payload, Mapping):
        raise ValueError("input must be a JSON object")
    unknown = set(payload) - ALLOWED_FIELDS
    if unknown:
        raise ValueError("unsupported fields: {}".format(", ".join(sorted(unknown))))

    values = {
        "input_tokens": _integer(payload, "input_tokens"),
        "context_limit": _integer(payload, "context_limit", 1),
        "reply_reserve": _integer(payload, "reply_reserve"),
        "compaction_reserve": _integer(payload, "compaction_reserve"),
        "turn_count": _integer(payload, "turn_count"),
        "failed_attempts": _integer(payload, "failed_attempts"),
        "phase": _enum(payload, "phase", PHASES),
        "cache_mode": _enum(payload, "cache_mode", CACHE_MODES),
        "phase_boundary": payload.get("phase_boundary", False),
    }
    if not isinstance(values["phase_boundary"], bool):
        raise ValueError("phase_boundary must be a boolean")
    return values


def _fallback_action(input_tokens: int, fallback: int) -> str:
    return "compact" if input_tokens >= fallback else "retain"


def _jev_state(values: Mapping[str, Any], fallback: int) -> Dict[str, Any]:
    return {
        "pressure_band": "elevated" if values["input_tokens"] >= fallback else "advisory",
        "turn_band": _bucket(values["turn_count"], (5, 15, 30, math.inf), ("0-5", "6-15", "16-30", "31+")),
        "failure_band": _bucket(values["failed_attempts"], (0, 1, math.inf), ("0", "1", "2+")),
        "phase": values["phase"],
        "cache_mode": values["cache_mode"],
        "phase_boundary": values["phase_boundary"],
    }


def _validated_jev_action(response: Mapping[str, Any], confidence_floor: float) -> Optional[Dict[str, Any]]:
    try:
        answer = response["answers"]["context_action"]
        choice = answer["choice"]
        confidence = answer["confidence"]
        probabilities = answer["probabilities"]
        if answer["type"] != "choice" or choice not in ACTIONS:
            return None
        if isinstance(confidence, bool) or not isinstance(confidence, (int, float)):
            return None
        if not 0 <= confidence <= 1 or confidence < confidence_floor:
            return None
        if set(probabilities) != ACTIONS:
            return None
        if any(isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 for value in probabilities.values()):
            return None
        if not math.isclose(sum(probabilities.values()), 1.0, abs_tol=1e-6):
            return None
        return {
            "action": choice,
            "model": response.get("model", "unknown"),
            "confidence": confidence,
            "probabilities": probabilities,
            "usage": response.get("usage"),
        }
    except (KeyError, TypeError):
        return None


def classify(
    payload: Mapping[str, Any],
    evaluator: Optional[Callable[[Mapping[str, Any]], Mapping[str, Any]]] = None,
    policy: Policy = Policy(),
) -> Dict[str, Any]:
    """Return retain, compact, or handoff without performing the action."""
    policy.validate()
    values = _validated_input(payload)
    hard = values["context_limit"] - values["reply_reserve"] - values["compaction_reserve"]
    if hard <= 0:
        raise ValueError("usable ceiling must be greater than zero")
    soft = math.floor(hard * policy.soft_ratio)
    fallback = math.floor(hard * policy.fallback_ratio)
    telemetry = {"soft": soft, "fallback": fallback, "hard": hard}

    if values["phase_boundary"]:
        return {
            "action": "handoff",
            "source": "deterministic",
            "reason": "explicit_phase_boundary",
            "telemetry": telemetry,
        }
    if values["input_tokens"] < soft:
        return {
            "action": "retain",
            "source": "deterministic",
            "reason": "below_soft_limit",
            "telemetry": telemetry,
        }
    if values["input_tokens"] >= hard:
        return {
            "action": "compact",
            "source": "deterministic",
            "reason": "at_or_above_hard_ceiling",
            "telemetry": telemetry,
        }

    fallback_action = _fallback_action(values["input_tokens"], fallback)
    if evaluator is None:
        return {
            "action": fallback_action,
            "source": "fallback",
            "reason": "jev_not_configured",
            "telemetry": telemetry,
        }

    try:
        jev = _validated_jev_action(evaluator(_jev_state(values, fallback)), policy.confidence_floor)
    except Exception:
        jev = None
    if jev is None or (jev["action"] == "handoff" and not values["phase_boundary"]):
        return {
            "action": fallback_action,
            "source": "fallback",
            "reason": "jev_unavailable_invalid_or_uncertain",
            "telemetry": telemetry,
        }
    return {
        "action": jev["action"],
        "source": "jev",
        "reason": "confidence_gate_passed",
        "telemetry": telemetry,
        "jev": jev,
    }


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: ANN001
        return None


def jev_evaluator(api_key: str, timeout_seconds: float = 10.0) -> Callable[[Mapping[str, Any]], Mapping[str, Any]]:
    if not api_key:
        raise ValueError("TYPESAFE_API_KEY is required when --use-jev is set")

    def evaluate(state: Mapping[str, Any]) -> Mapping[str, Any]:
        body = {
            "state": dict(state),
            "model": "jev-latest",
            "questions": {
                "context_action": {
                    "type": "choice",
                    "instructions": (
                        "Choose the lowest-cost safe context action for the next agent turn "
                        "using only the bounded telemetry in state. Do not infer missing content."
                    ),
                    "criteria": {
                        "retain": "Keep the current session because continuity is worth its context cost.",
                        "compact": "Summarize verified state, discard replaceable history, and continue this phase.",
                        "handoff": "Start a fresh session from a durable handoff, only at an explicit phase boundary.",
                    },
                }
            },
        }
        request = urllib.request.Request(
            API_URL,
            data=json.dumps(body, separators=(",", ":")).encode("utf-8"),
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            method="POST",
        )
        opener = urllib.request.build_opener(_NoRedirect())
        with opener.open(request, timeout=timeout_seconds) as response:
            if response.status != 200:
                raise OSError("unexpected TypeSafe response")
            return json.loads(response.read().decode("utf-8"))

    return evaluate


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-jev", action="store_true", help="ask Jev inside the advisory band")
    parser.add_argument("--timeout", type=float, default=10.0, help="Jev request timeout in seconds")
    args = parser.parse_args(argv)
    try:
        raw = sys.stdin.read(MAX_STDIN_BYTES + 1)
        if len(raw.encode("utf-8")) > MAX_STDIN_BYTES:
            raise ValueError("input exceeds 16384 bytes")
        payload = json.loads(raw)
        evaluator = None
        if args.use_jev:
            evaluator = jev_evaluator(os.environ.get("TYPESAFE_API_KEY", ""), args.timeout)
        result = classify(payload, evaluator=evaluator)
    except (ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(json.dumps({"error": "invalid_input", "message": str(error)}) + "\n")
        return 2
    print(json.dumps(result, separators=(",", ":"), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
