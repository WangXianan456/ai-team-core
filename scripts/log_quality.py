#!/usr/bin/env python3
"""
Log quality events for expert scorecards.

Usage:
  python scripts/log_quality.py --task TASK-010 --type escaped_defect --severity critical --notes "prod issue"
  python scripts/log_quality.py --task TASK-013 --type rollback --severity high --notes "deploy rollback"
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
QUALITY_LOG = LOG_DIR / "quality_events.jsonl"


def main() -> None:
    p = argparse.ArgumentParser(description="Log quality event")
    p.add_argument("--task", required=True, help="Task id")
    p.add_argument(
        "--type",
        required=True,
        choices=["escaped_defect", "rollback", "security_find", "rework"],
        help="Event type",
    )
    p.add_argument("--severity", default="medium", choices=["low", "medium", "high", "critical"])
    p.add_argument("--notes", default="", help="Free text note")
    args = p.parse_args()

    payload = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "task_id": args.task,
        "event_type": args.type,
        "severity": args.severity,
        "notes": args.notes,
    }

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    with QUALITY_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")

    print(
        f"logged: task={args.task} event_type={args.type} severity={args.severity}"
    )


if __name__ == "__main__":
    main()

