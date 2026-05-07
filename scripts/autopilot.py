#!/usr/bin/env python3
"""
Generate daily execution plan with risks and budget alerts.

Usage:
  python scripts/autopilot.py daily
  python scripts/autopilot.py daily --output reports/daily-YYYY-MM-DD.md
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "tasks"
USAGE_LOG = ROOT / "logs" / "token_usage.jsonl"
PRICING = ROOT / "config" / "pricing.json"

STATUS_RE = re.compile(r"^-\s*Status:\s*`?([a-z]+)`?\s*$", re.IGNORECASE)
PRIORITY_RE = re.compile(r"^-\s*Priority:\s*`?([A-Za-z0-9]+)`?\s*$", re.IGNORECASE)
DEPENDS_RE = re.compile(r"^-\s*Depends On:\s*`?(.+?)`?\s*$", re.IGNORECASE)
DUE_RE = re.compile(r"^-\s*Due:\s*`?([0-9]{4}-[0-9]{2}-[0-9]{2})`?\s*$", re.IGNORECASE)
OWNER_RE = re.compile(r"^-\s*Owner:\s*`?([a-z/]+)`?\s*$", re.IGNORECASE)


@dataclass
class Task:
    task_id: str
    status: str
    priority: str
    depends_on: List[str]
    due: str
    owner: str
    path: Path


def read_task(path: Path) -> Task:
    status = "todo"
    priority = "P2"
    depends = []
    due = ""
    owner = "pm"
    for line in path.read_text(encoding="utf-8").splitlines():
        s = line.strip()
        m = STATUS_RE.match(s)
        if m:
            status = m.group(1).lower()
            continue
        m = PRIORITY_RE.match(s)
        if m:
            priority = m.group(1).upper()
            continue
        m = DEPENDS_RE.match(s)
        if m:
            raw = m.group(1).strip()
            if raw.lower() != "none":
                depends = [x.strip() for x in raw.split(",") if x.strip()]
            continue
        m = DUE_RE.match(s)
        if m:
            due = m.group(1)
            continue
        m = OWNER_RE.match(s)
        if m:
            owner = m.group(1).lower()
    return Task(path.stem, status, priority, depends, due, owner, path)


def load_tasks() -> List[Task]:
    return [read_task(p) for p in sorted(TASK_DIR.glob("TASK-*.md"))]


def task_map(tasks: List[Task]) -> Dict[str, Task]:
    return {t.task_id: t for t in tasks}


def blocked_by(task: Task, tmap: Dict[str, Task]) -> List[str]:
    out: List[str] = []
    for d in task.depends_on:
        dep = tmap.get(d) or tmap.get(f"{d}")
        if dep is None:
            out.append(f"{d} (missing)")
            continue
        if dep.status != "done":
            out.append(dep.task_id)
    return out


def priority_rank(p: str) -> int:
    order = {"P0": 0, "P1": 1, "P2": 2}
    return order.get(p.upper(), 99)


def parse_ts(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def current_week_key() -> str:
    y, w, _ = datetime.now(timezone.utc).isocalendar()
    return f"{y}-W{w:02d}"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def usage_cost_snapshot() -> Tuple[float, float]:
    if not USAGE_LOG.exists():
        return 0.0, 0.0
    rows = [json.loads(x) for x in USAGE_LOG.read_text(encoding="utf-8").splitlines() if x.strip()]
    today = datetime.now(timezone.utc).date()
    wk = current_week_key()
    daily = 0.0
    weekly = 0.0
    for r in rows:
        ts = parse_ts(r["timestamp_utc"])
        c = float(r.get("cost", 0.0))
        if ts.date() == today:
            daily += c
        y, w, _ = ts.isocalendar()
        if f"{y}-W{w:02d}" == wk:
            weekly += c
    return daily, weekly


def budget_alerts() -> List[str]:
    conf = load_json(PRICING)
    limits = conf.get("budget_limits", {})
    daily_limit = float(limits.get("daily", 0.0))
    weekly_limit = float(limits.get("weekly", 0.0))
    daily, weekly = usage_cost_snapshot()
    alerts: List[str] = []
    if daily_limit > 0:
        pct = daily / daily_limit
        if pct >= 1.0:
            alerts.append(f"Daily budget exceeded: {daily:.4f}/{daily_limit:.4f} USD")
        elif pct >= 0.8:
            alerts.append(f"Daily budget >80%: {daily:.4f}/{daily_limit:.4f} USD")
    if weekly_limit > 0:
        pct = weekly / weekly_limit
        if pct >= 1.0:
            alerts.append(f"Weekly budget exceeded: {weekly:.4f}/{weekly_limit:.4f} USD")
        elif pct >= 0.8:
            alerts.append(f"Weekly budget >80%: {weekly:.4f}/{weekly_limit:.4f} USD")
    return alerts


def generate_daily_plan(tasks: List[Task]) -> str:
    tmap = task_map(tasks)
    todo = [t for t in tasks if t.status in {"todo", "doing", "qa", "release"}]
    candidates: List[Tuple[int, str, Task]] = []
    blocked: List[Tuple[Task, List[str]]] = []

    for t in todo:
        bl = blocked_by(t, tmap)
        if bl and t.status == "todo":
            blocked.append((t, bl))
            continue
        due = t.due if t.due else "9999-12-31"
        candidates.append((priority_rank(t.priority), due, t))

    candidates.sort(key=lambda x: (x[0], x[1], x[2].task_id))
    top = [x[2] for x in candidates[:5]]
    alerts = budget_alerts()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    lines = [
        f"# Autopilot Daily Plan {today}",
        "",
        "## Recommended Top Tasks",
    ]
    if not top:
        lines.append("- No active tasks available.")
    else:
        for t in top:
            lines.append(
                f"- {t.task_id} | priority={t.priority} | status={t.status} | owner={t.owner} | due={t.due or 'N/A'}"
            )

    lines += ["", "## Blocked Tasks"]
    if not blocked:
        lines.append("- None")
    else:
        for t, bl in blocked:
            lines.append(f"- {t.task_id}: blocked by {', '.join(bl)}")

    lines += ["", "## Budget Alerts"]
    if not alerts:
        lines.append("- None")
    else:
        for a in alerts:
            lines.append(f"- {a}")

    lines += [
        "",
        "## Next Actions",
        "1. Move one P0/P1 task to doing if unblocked.",
        "2. Run dependency audit plan on target business repo before release tasks.",
        "3. Refresh weekly scorecard after major state transitions.",
        "",
    ]
    return "\n".join(lines)


def main() -> None:
    p = argparse.ArgumentParser(description="Autopilot planner")
    sub = p.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("daily")
    d.add_argument("--output", default="", help="Optional markdown output path")
    args = p.parse_args()

    if args.cmd != "daily":
        raise RuntimeError("unknown command")
    md = generate_daily_plan(load_tasks())
    print(md)
    if args.output:
        out = Path(args.output)
        if not out.is_absolute():
            out = ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(md, encoding="utf-8")
        print(f"saved: {out}")


if __name__ == "__main__":
    main()

