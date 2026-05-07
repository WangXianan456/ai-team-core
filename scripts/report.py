#!/usr/bin/env python3
"""
Generate weekly orchestration report from logs/orchestration_events.jsonl.

Usage:
  python scripts/report.py weekly
  python scripts/report.py weekly --week 2026-W19
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
LOG_PATH = ROOT / "logs" / "orchestration_events.jsonl"


@dataclass
class Event:
    ts: datetime
    action: str
    task_id: str
    from_status: str
    to_status: str
    owner: str

    @property
    def week_key(self) -> str:
        y, w, _ = self.ts.isocalendar()
        return f"{y}-W{w:02d}"


def parse_ts(raw: str) -> datetime:
    # Support "Z" and "+00:00"
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def load_events(path: Path) -> List[Event]:
    if not path.exists():
        return []
    out: List[Event] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        out.append(
            Event(
                ts=parse_ts(row["timestamp_utc"]),
                action=row.get("action", ""),
                task_id=row.get("task_id", ""),
                from_status=row.get("from_status", ""),
                to_status=row.get("to_status", ""),
                owner=row.get("owner", ""),
            )
        )
    return out


def current_week_key() -> str:
    now = datetime.now(timezone.utc)
    y, w, _ = now.isocalendar()
    return f"{y}-W{w:02d}"


def filter_week(events: Iterable[Event], week: str) -> List[Event]:
    return [e for e in events if e.week_key == week]


def transitions_by_pair(events: Iterable[Event]) -> Counter:
    c: Counter = Counter()
    for e in events:
        c[(e.from_status, e.to_status)] += 1
    return c


def transitions_by_owner(events: Iterable[Event]) -> Counter:
    c: Counter = Counter()
    for e in events:
        c[e.owner] += 1
    return c


def _stage_index(status: str) -> int:
    order = ["todo", "doing", "qa", "release", "done"]
    return order.index(status) if status in order else -1


def cycle_times_hours(events: Iterable[Event]) -> Tuple[Dict[str, float], Optional[float]]:
    grouped: Dict[str, List[Event]] = defaultdict(list)
    for e in events:
        grouped[e.task_id].append(e)

    result: Dict[str, float] = {}
    for task_id, arr in grouped.items():
        arr.sort(key=lambda x: x.ts)
        start: Optional[datetime] = None
        end: Optional[datetime] = None
        for e in arr:
            if start is None and _stage_index(e.to_status) >= _stage_index("doing"):
                start = e.ts
            if e.to_status == "done":
                end = e.ts
                break
        if start and end and end >= start:
            result[task_id] = (end - start).total_seconds() / 3600.0

    avg: Optional[float] = None
    if result:
        avg = sum(result.values()) / len(result)
    return result, avg


def print_weekly_report(events: List[Event], week: str) -> None:
    scoped = filter_week(events, week)
    print(f"Weekly Report: {week}")
    print(f"Events: {len(scoped)}")
    if not scoped:
        print("No events found for this week.")
        return

    pair = transitions_by_pair(scoped)
    owner = transitions_by_owner(scoped)
    cycle, avg = cycle_times_hours(scoped)

    print("\nTransitions:")
    for (s1, s2), n in sorted(pair.items(), key=lambda x: (-x[1], x[0])):
        print(f"- {s1} -> {s2}: {n}")

    print("\nBy Owner:")
    for role, n in sorted(owner.items(), key=lambda x: (-x[1], x[0])):
        print(f"- {role}: {n}")

    print("\nTask Lead Time (hours, doing->done):")
    if not cycle:
        print("- No completed task cycle in this week.")
    else:
        for task_id, hrs in sorted(cycle.items(), key=lambda x: x[0]):
            print(f"- {task_id}: {hrs:.2f}h")
        print(f"- Average: {avg:.2f}h")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Orchestration report")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("weekly", help="Generate weekly report")
    w.add_argument("--week", default=current_week_key(), help="ISO week key, e.g. 2026-W19")
    return p


def main() -> None:
    args = build_parser().parse_args()
    events = load_events(LOG_PATH)
    if args.cmd == "weekly":
        print_weekly_report(events, args.week)
    else:
        raise RuntimeError("unknown command")


if __name__ == "__main__":
    main()

