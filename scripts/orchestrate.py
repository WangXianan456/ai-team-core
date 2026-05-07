#!/usr/bin/env python3
"""
Minimal task orchestrator for agent-system.

Usage:
  python scripts/orchestrate.py list
  python scripts/orchestrate.py next TASK-001-bootstrap-agent-system
  python scripts/orchestrate.py advance TASK-001-bootstrap-agent-system
  python scripts/orchestrate.py set TASK-001-bootstrap-agent-system qa
  python scripts/orchestrate.py blockers TASK-001-bootstrap-agent-system
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[1]
TASK_DIR = ROOT / "tasks"
LOG_DIR = ROOT / "logs"
EVENT_LOG = LOG_DIR / "orchestration_events.jsonl"

STATE_FLOW: List[str] = ["todo", "doing", "qa", "release", "done"]
OWNER_BY_STATE: Dict[str, str] = {
    "todo": "pm",
    "doing": "dev",
    "qa": "qa",
    "release": "ops",
    "done": "orchestrator",
}


STATUS_RE = re.compile(r"^-\s*Status:\s*`?([a-z]+)`?\s*$", re.IGNORECASE)
OWNER_RE = re.compile(r"^-\s*Owner:\s*`?([a-z/]+)`?\s*$", re.IGNORECASE)
DEPENDS_RE = re.compile(r"^-\s*Depends On:\s*`?(.+?)`?\s*$", re.IGNORECASE)


def task_path(task_id: str) -> Path:
    exact = TASK_DIR / f"{task_id}.md"
    if exact.exists():
        return exact
    matches = sorted(TASK_DIR.glob(f"{task_id}*.md"))
    if not matches:
        raise FileNotFoundError(f"Task not found: {task_id}")
    return matches[0]


def read_task_meta(path: Path) -> Tuple[str, str]:
    status = ""
    owner = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        m = STATUS_RE.match(line.strip())
        if m:
            status = m.group(1).lower()
            continue
        m = OWNER_RE.match(line.strip())
        if m:
            owner = m.group(1).lower()
    if not status:
        raise ValueError(f"Missing Status in {path.name}")
    if not owner:
        raise ValueError(f"Missing Owner in {path.name}")
    return status, owner


def read_task_dependencies(path: Path) -> List[str]:
    raw = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        m = DEPENDS_RE.match(line.strip())
        if m:
            raw = m.group(1).strip()
            break
    if not raw or raw.lower() == "none":
        return []
    deps = [x.strip() for x in raw.split(",")]
    return [d for d in deps if d]


def unresolved_dependencies(path: Path) -> List[str]:
    unresolved: List[str] = []
    for dep in read_task_dependencies(path):
        try:
            dep_path = task_path(dep)
            dep_status, _ = read_task_meta(dep_path)
            if dep_status != "done":
                unresolved.append(dep_path.stem)
        except FileNotFoundError:
            unresolved.append(f"{dep} (missing)")
    return unresolved


def write_task_meta(path: Path, new_status: str, new_owner: str) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    out = []
    replaced_status = False
    replaced_owner = False
    for line in lines:
        stripped = line.strip()
        if STATUS_RE.match(stripped):
            out.append(f"- Status: `{new_status}`")
            replaced_status = True
            continue
        if OWNER_RE.match(stripped):
            out.append(f"- Owner: `{new_owner}`")
            replaced_owner = True
            continue
        out.append(line)
    if not replaced_status or not replaced_owner:
        raise ValueError(f"Cannot rewrite meta fields in {path.name}")
    path.write_text("\n".join(out) + "\n", encoding="utf-8")


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(event: Dict[str, str]) -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    payload = {"timestamp_utc": now_utc_iso(), **event}
    with EVENT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def list_tasks() -> None:
    files = sorted(TASK_DIR.glob("TASK-*.md"))
    if not files:
        print("No task files found.")
        return
    for f in files:
        status, owner = read_task_meta(f)
        print(f"{f.stem}: status={status}, owner={owner}")


def next_action(task_id: str) -> None:
    path = task_path(task_id)
    status, owner = read_task_meta(path)
    if status not in STATE_FLOW:
        print(f"{path.stem}: unknown status '{status}'")
        return
    if status == "done":
        print(f"{path.stem}: completed. Owner={owner}.")
        return
    target_owner = OWNER_BY_STATE[status]
    deps = unresolved_dependencies(path)
    deps_text = ", ".join(deps) if deps else "none"
    print(
        f"{path.stem}: current status={status}, current owner={owner}, "
        f"next role should act={target_owner}, unresolved dependencies={deps_text}"
    )


def advance(task_id: str) -> None:
    path = task_path(task_id)
    status, _owner = read_task_meta(path)
    if status not in STATE_FLOW:
        raise ValueError(f"Unknown status '{status}' in {path.name}")
    idx = STATE_FLOW.index(status)
    if idx == len(STATE_FLOW) - 1:
        print(f"{path.stem}: already done.")
        return
    new_status = STATE_FLOW[idx + 1]
    if status == "todo" and new_status == "doing":
        deps = unresolved_dependencies(path)
        if deps:
            print(f"{path.stem}: blocked by dependencies: {', '.join(deps)}")
            return
    new_owner = OWNER_BY_STATE[new_status]
    write_task_meta(path, new_status, new_owner)
    append_event(
        {
            "action": "advance",
            "task_id": path.stem,
            "from_status": status,
            "to_status": new_status,
            "owner": new_owner,
        }
    )
    print(f"{path.stem}: advanced to status={new_status}, owner={new_owner}")


def set_status(task_id: str, new_status: str) -> None:
    path = task_path(task_id)
    old_status, _old_owner = read_task_meta(path)
    new_status = new_status.lower()
    if new_status not in STATE_FLOW:
        raise ValueError(f"Invalid status: {new_status}")
    if new_status == "doing":
        deps = unresolved_dependencies(path)
        if deps:
            print(f"{path.stem}: blocked by dependencies: {', '.join(deps)}")
            return
    new_owner = OWNER_BY_STATE[new_status]
    write_task_meta(path, new_status, new_owner)
    append_event(
        {
            "action": "set",
            "task_id": path.stem,
            "from_status": old_status,
            "to_status": new_status,
            "owner": new_owner,
        }
    )
    print(f"{path.stem}: set status={new_status}, owner={new_owner}")


def blockers(task_id: str) -> None:
    path = task_path(task_id)
    deps = unresolved_dependencies(path)
    if not deps:
        print(f"{path.stem}: no unresolved dependencies.")
        return
    print(f"{path.stem}: unresolved dependencies:")
    for dep in deps:
        print(f"- {dep}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Task orchestrator")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list", help="List all tasks")

    p_next = sub.add_parser("next", help="Show next acting role")
    p_next.add_argument("task_id", help="Task id prefix, e.g. TASK-001")

    p_advance = sub.add_parser("advance", help="Advance task to next stage")
    p_advance.add_argument("task_id", help="Task id prefix, e.g. TASK-001")

    p_set = sub.add_parser("set", help="Set task status directly")
    p_set.add_argument("task_id", help="Task id prefix, e.g. TASK-001")
    p_set.add_argument("status", choices=STATE_FLOW, help="Target status")

    p_block = sub.add_parser("blockers", help="Show unresolved dependencies")
    p_block.add_argument("task_id", help="Task id prefix, e.g. TASK-001")
    return p


def main() -> None:
    args = build_parser().parse_args()
    if args.cmd == "list":
        list_tasks()
    elif args.cmd == "next":
        next_action(args.task_id)
    elif args.cmd == "advance":
        advance(args.task_id)
    elif args.cmd == "set":
        set_status(args.task_id, args.status)
    elif args.cmd == "blockers":
        blockers(args.task_id)
    else:
        raise RuntimeError("Unknown command")


if __name__ == "__main__":
    main()
