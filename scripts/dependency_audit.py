#!/usr/bin/env python3
"""
Dependency audit command selector and runner.

Usage:
  python scripts/dependency_audit.py plan --repo F:\\path\\to\\repo
  python scripts/dependency_audit.py run --repo F:\\path\\to\\repo
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple


@dataclass
class AuditCommand:
    ecosystem: str
    command: List[str]
    required_bin: str
    note: str


def detect_ecosystems(repo: Path) -> List[str]:
    out: List[str] = []
    if (repo / "package-lock.json").exists() or (repo / "package.json").exists():
        out.append("node")
    if (repo / "requirements.txt").exists() or (repo / "pyproject.toml").exists():
        out.append("python")
    if (repo / "go.mod").exists():
        out.append("go")
    if (repo / "Cargo.toml").exists():
        out.append("rust")
    return out


def build_commands(repo: Path) -> List[AuditCommand]:
    ecs = detect_ecosystems(repo)
    cmds: List[AuditCommand] = []
    for e in ecs:
        if e == "node":
            cmds.append(
                AuditCommand(
                    ecosystem="node",
                    command=["npm", "audit", "--audit-level=high"],
                    required_bin="npm",
                    note="Runs npm audit using package-lock or package metadata.",
                )
            )
        elif e == "python":
            cmds.append(
                AuditCommand(
                    ecosystem="python",
                    command=["pip-audit"],
                    required_bin="pip-audit",
                    note="Runs pip-audit; install with 'pip install pip-audit' if missing.",
                )
            )
        elif e == "go":
            cmds.append(
                AuditCommand(
                    ecosystem="go",
                    command=["govulncheck", "./..."],
                    required_bin="govulncheck",
                    note="Runs govulncheck across modules.",
                )
            )
        elif e == "rust":
            cmds.append(
                AuditCommand(
                    ecosystem="rust",
                    command=["cargo", "audit"],
                    required_bin="cargo-audit",
                    note="Runs cargo audit; install with 'cargo install cargo-audit'.",
                )
            )
    return cmds


def print_plan(cmds: List[AuditCommand], repo: Path) -> None:
    print(f"Dependency audit plan for: {repo}")
    if not cmds:
        print("No known ecosystem detected.")
        return
    for c in cmds:
        present = shutil.which(c.required_bin) is not None
        status = "ok" if present else "missing"
        print(f"- [{c.ecosystem}] ({status}) {' '.join(c.command)}")
        print(f"  note: {c.note}")


def run_commands(cmds: List[AuditCommand], repo: Path) -> int:
    if not cmds:
        print("No known ecosystem detected. Nothing to run.")
        return 0
    overall = 0
    for c in cmds:
        if shutil.which(c.required_bin) is None:
            print(f"[skip] {c.ecosystem}: missing '{c.required_bin}'")
            overall = max(overall, 2)
            continue
        print(f"[run] {c.ecosystem}: {' '.join(c.command)}")
        proc = subprocess.run(c.command, cwd=str(repo), capture_output=True, text=True)
        print(f"[exit={proc.returncode}] {c.ecosystem}")
        if proc.stdout.strip():
            print(proc.stdout.strip())
        if proc.stderr.strip():
            print(proc.stderr.strip())
        overall = max(overall, proc.returncode)
    return overall


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Dependency audit helper")
    sub = p.add_subparsers(dest="cmd", required=True)
    for name in ("plan", "run"):
        s = sub.add_parser(name)
        s.add_argument("--repo", required=True, help="Target repository path")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    repo = Path(args.repo).resolve()
    cmds = build_commands(repo)
    if args.cmd == "plan":
        print_plan(cmds, repo)
        return
    code = run_commands(cmds, repo)
    raise SystemExit(code)


if __name__ == "__main__":
    main()

