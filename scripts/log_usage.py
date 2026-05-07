#!/usr/bin/env python3
"""
Append token usage record and computed cost.

Usage:
  python scripts/log_usage.py --task TASK-001 --role dev --model gpt-5.5 --input 1200 --output 800
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRICING_PATH = ROOT / "config" / "pricing.json"
LOG_DIR = ROOT / "logs"
USAGE_LOG = LOG_DIR / "token_usage.jsonl"


def load_pricing() -> dict:
    if not PRICING_PATH.exists():
        raise FileNotFoundError(f"Missing pricing config: {PRICING_PATH}")
    return json.loads(PRICING_PATH.read_text(encoding="utf-8"))


def calc_cost(model: str, input_tokens: int, output_tokens: int, pricing: dict) -> float:
    table = pricing.get("per_million_tokens", {})
    if model not in table:
        raise ValueError(f"Unknown model in pricing config: {model}")
    unit = table[model]
    in_cost = (input_tokens / 1_000_000.0) * float(unit["input"])
    out_cost = (output_tokens / 1_000_000.0) * float(unit["output"])
    return in_cost + out_cost


def main() -> None:
    p = argparse.ArgumentParser(description="Log token usage with cost")
    p.add_argument("--task", required=True, help="Task id, e.g. TASK-001")
    p.add_argument("--role", required=True, choices=["orchestrator", "pm", "dev", "qa", "ops"])
    p.add_argument("--model", required=True, help="Model name in config/pricing.json")
    p.add_argument("--input", required=True, type=int, dest="input_tokens")
    p.add_argument("--output", required=True, type=int, dest="output_tokens")
    args = p.parse_args()

    pricing = load_pricing()
    cost = calc_cost(args.model, args.input_tokens, args.output_tokens, pricing)
    currency = pricing.get("currency", "USD")

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": args.task,
        "role": args.role,
        "model": args.model,
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "cost": round(cost, 8),
        "currency": currency,
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with USAGE_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    print(
        f"logged: task={args.task} role={args.role} model={args.model} "
        f"input={args.input_tokens} output={args.output_tokens} cost={payload['cost']} {currency}"
    )


if __name__ == "__main__":
    main()

