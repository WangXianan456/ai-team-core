#!/usr/bin/env python3
"""
Generate cost report from logs/token_usage.jsonl.

Usage:
  python scripts/cost_report.py weekly
  python scripts/cost_report.py weekly --week 2026-W19
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]
USAGE_LOG = ROOT / "logs" / "token_usage.jsonl"


@dataclass
class Usage:
    ts: datetime
    task_id: str
    role: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    currency: str

    @property
    def week_key(self) -> str:
        y, w, _ = self.ts.isocalendar()
        return f"{y}-W{w:02d}"


def parse_ts(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_usage() -> List[Usage]:
    if not USAGE_LOG.exists():
        return []
    out: List[Usage] = []
    for line in USAGE_LOG.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out.append(
            Usage(
                ts=parse_ts(row["timestamp_utc"]),
                task_id=row.get("task_id", ""),
                role=row.get("role", ""),
                model=row.get("model", ""),
                input_tokens=int(row.get("input_tokens", 0)),
                output_tokens=int(row.get("output_tokens", 0)),
                cost=float(row.get("cost", 0.0)),
                currency=row.get("currency", "USD"),
            )
        )
    return out


def current_week_key() -> str:
    y, w, _ = datetime.now(timezone.utc).isocalendar()
    return f"{y}-W{w:02d}"


def scoped_week(items: Iterable[Usage], week: str) -> List[Usage]:
    return [x for x in items if x.week_key == week]


def report_weekly(items: List[Usage], week: str) -> None:
    rows = scoped_week(items, week)
    print(f"Cost Report: {week}")
    print(f"Entries: {len(rows)}")
    if not rows:
        print("No usage rows found for this week.")
        return

    currency = rows[0].currency
    total_cost = sum(x.cost for x in rows)
    total_in = sum(x.input_tokens for x in rows)
    total_out = sum(x.output_tokens for x in rows)

    by_role = Counter()
    by_model = Counter()
    by_task = defaultdict(float)
    for x in rows:
        by_role[x.role] += x.cost
        by_model[x.model] += x.cost
        by_task[x.task_id] += x.cost

    print(f"Total Cost: {total_cost:.6f} {currency}")
    print(f"Total Tokens: input={total_in}, output={total_out}")

    print("\nCost By Role:")
    for role, cost in sorted(by_role.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"- {role}: {cost:.6f} {currency}")

    print("\nCost By Model:")
    for model, cost in sorted(by_model.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"- {model}: {cost:.6f} {currency}")

    print("\nCost By Task:")
    for task, cost in sorted(by_task.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f"- {task}: {cost:.6f} {currency}")


def main() -> None:
    p = argparse.ArgumentParser(description="Token usage cost report")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("weekly")
    w.add_argument("--week", default=current_week_key())
    args = p.parse_args()

    usage = load_usage()
    if args.cmd == "weekly":
        report_weekly(usage, args.week)
    else:
        raise RuntimeError("unknown command")


if __name__ == "__main__":
    main()

