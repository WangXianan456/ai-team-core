#!/usr/bin/env python3
"""
Generate weekly expert scorecard from orchestration/cost/quality logs.

Usage:
  python scripts/scorecard.py weekly
  python scripts/scorecard.py weekly --week 2026-W19 --output reports/scorecard-2026-W19.md
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional


ROOT = Path(__file__).resolve().parents[1]
ORCH_LOG = ROOT / "logs" / "orchestration_events.jsonl"
USAGE_LOG = ROOT / "logs" / "token_usage.jsonl"
QUALITY_LOG = ROOT / "logs" / "quality_events.jsonl"


def parse_ts(raw: str) -> datetime:
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    dt = datetime.fromisoformat(raw)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def week_key(dt: datetime) -> str:
    y, w, _ = dt.isocalendar()
    return f"{y}-W{w:02d}"


def current_week_key() -> str:
    return week_key(datetime.now(timezone.utc))


def load_jsonl(path: Path) -> List[dict]:
    if not path.exists():
        return []
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def scoped(rows: Iterable[dict], week: str) -> List[dict]:
    out = []
    for r in rows:
        ts = parse_ts(r["timestamp_utc"])
        if week_key(ts) == week:
            out.append(r)
    return out


def build_metrics(week: str) -> Dict[str, object]:
    orch = scoped(load_jsonl(ORCH_LOG), week)
    usage = scoped(load_jsonl(USAGE_LOG), week)
    quality = scoped(load_jsonl(QUALITY_LOG), week)

    transitions = Counter((r.get("from_status", ""), r.get("to_status", "")) for r in orch)
    tasks_done = transitions.get(("release", "done"), 0) + transitions.get(("todo", "done"), 0)

    qa_entries = sum(1 for r in orch if r.get("to_status") == "qa")
    qa_rework = sum(1 for r in orch if r.get("from_status") == "qa" and r.get("to_status") == "doing")
    first_pass_qa_rate: Optional[float] = None
    if qa_entries > 0:
        first_pass_qa_rate = max(0.0, (qa_entries - qa_rework) / qa_entries)

    escaped = sum(1 for r in quality if r.get("event_type") == "escaped_defect")
    rollbacks = sum(1 for r in quality if r.get("event_type") == "rollback")
    security_finds = sum(1 for r in quality if r.get("event_type") == "security_find")

    total_cost = sum(float(r.get("cost", 0.0)) for r in usage)
    total_input = sum(int(r.get("input_tokens", 0)) for r in usage)
    total_output = sum(int(r.get("output_tokens", 0)) for r in usage)
    cost_per_task: Optional[float] = None
    if tasks_done > 0:
        cost_per_task = total_cost / tasks_done

    by_role_cost = defaultdict(float)
    for r in usage:
        by_role_cost[r.get("role", "")] += float(r.get("cost", 0.0))

    return {
        "week": week,
        "tasks_done": tasks_done,
        "first_pass_qa_rate": first_pass_qa_rate,
        "qa_rework_count": qa_rework,
        "escaped_defects": escaped,
        "rollbacks": rollbacks,
        "security_finds": security_finds,
        "total_cost": total_cost,
        "total_input_tokens": total_input,
        "total_output_tokens": total_output,
        "cost_per_task": cost_per_task,
        "by_role_cost": dict(sorted(by_role_cost.items(), key=lambda kv: (-kv[1], kv[0]))),
    }


def to_markdown(m: Dict[str, object]) -> str:
    fp = m["first_pass_qa_rate"]
    fp_text = "N/A" if fp is None else f"{float(fp) * 100:.2f}%"
    cpt = m["cost_per_task"]
    cpt_text = "N/A" if cpt is None else f"{float(cpt):.6f} USD"
    lines = [
        f"# Expert Scorecard {m['week']}",
        "",
        "## Delivery",
        f"- Tasks done: {m['tasks_done']}",
        f"- First-pass QA rate: {fp_text}",
        f"- QA rework count: {m['qa_rework_count']}",
        "",
        "## Quality",
        f"- Escaped defects: {m['escaped_defects']}",
        f"- Rollbacks: {m['rollbacks']}",
        f"- Security findings: {m['security_finds']}",
        "",
        "## Cost",
        f"- Total cost: {float(m['total_cost']):.6f} USD",
        f"- Cost per completed task: {cpt_text}",
        f"- Tokens: input={m['total_input_tokens']}, output={m['total_output_tokens']}",
        "",
        "## Cost By Role",
    ]
    by_role = m["by_role_cost"]
    if by_role:
        for role, cost in by_role.items():
            lines.append(f"- {role}: {float(cost):.6f} USD")
    else:
        lines.append("- No token usage logged.")
    return "\n".join(lines) + "\n"


def main() -> None:
    p = argparse.ArgumentParser(description="Generate expert scorecard")
    sub = p.add_subparsers(dest="cmd", required=True)
    w = sub.add_parser("weekly", help="Generate weekly scorecard")
    w.add_argument("--week", default=current_week_key())
    w.add_argument("--output", default="", help="Optional markdown output path")
    args = p.parse_args()

    if args.cmd != "weekly":
        raise RuntimeError("unknown command")

    metrics = build_metrics(args.week)
    md = to_markdown(metrics)
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

