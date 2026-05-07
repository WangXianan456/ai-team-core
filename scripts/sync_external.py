#!/usr/bin/env python3
"""
Sync external repository mirrors (clone missing repos, pull existing repos).

Usage:
  python scripts/sync_external.py
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Tuple


ROOT = Path(__file__).resolve().parents[1]
EXTERNAL = ROOT / "external"


@dataclass
class RepoSpec:
    name: str
    url: str

    @property
    def path(self) -> Path:
        return EXTERNAL / self.name


REPOS: List[RepoSpec] = [
    RepoSpec("openai-codex", "https://github.com/openai/codex.git"),
    RepoSpec("anthropic-claude-code", "https://github.com/anthropics/claude-code.git"),
    RepoSpec("anthropic-skills", "https://github.com/anthropics/skills.git"),
    RepoSpec(
        "anthropic-claude-plugins-official",
        "https://github.com/anthropics/claude-plugins-official.git",
    ),
    RepoSpec("mcp-servers", "https://github.com/modelcontextprotocol/servers.git"),
]


def run(cmd: List[str], cwd: Path | None = None) -> Tuple[int, str]:
    p = subprocess.run(cmd, cwd=str(cwd) if cwd else None, capture_output=True, text=True)
    msg = (p.stdout or "").strip()
    err = (p.stderr or "").strip()
    joined = "\n".join(x for x in [msg, err] if x)
    return p.returncode, joined


def sync_repo(spec: RepoSpec) -> Tuple[str, str]:
    if spec.path.exists() and (spec.path / ".git").exists():
        code, out = run(["git", "-C", str(spec.path), "pull", "--ff-only"])
        return ("updated" if code == 0 else "failed"), out
    if spec.path.exists() and not (spec.path / ".git").exists():
        return "failed", f"path exists but is not a git repo: {spec.path}"
    code, out = run(["git", "clone", "--depth", "1", spec.url, str(spec.path)])
    return ("cloned" if code == 0 else "failed"), out


def write_readme(results: List[Tuple[RepoSpec, str, str]]) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ok = [r for r in results if r[1] in {"cloned", "updated"}]
    fail = [r for r in results if r[1] == "failed"]
    lines = [
        "# External Repositories (Local Mirror)",
        "",
        "Downloaded into this project for local reference and skill import.",
        "",
        f"- Last sync: `{now}`",
        "",
        "## Sync Status",
        "",
    ]
    for spec, status, _ in results:
        lines.append(f"- `{spec.name}`: {status} ({spec.url})")

    lines += ["", "## Available Locally", ""]
    if ok:
        for spec, status, _ in ok:
            lines.append(f"- `external/{spec.name}` ({status})")
    else:
        lines.append("- None")

    lines += ["", "## Failed This Round", ""]
    if fail:
        for spec, _status, output in fail:
            lines.append(f"- `{spec.url}`")
            if output:
                short = output.splitlines()[-1]
                lines.append(f"  - reason: `{short}`")
    else:
        lines.append("- None")

    lines += [
        "",
        "## Imported Skill Packs",
        "",
        "Imported to `skills/anthropic_imports/`:",
        "",
        "- `claude-api`",
        "- `mcp-builder`",
        "- `webapp-testing`",
        "- `skill-creator`",
        "- `frontend-design`",
        "",
    ]
    (EXTERNAL / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    EXTERNAL.mkdir(parents=True, exist_ok=True)
    results: List[Tuple[RepoSpec, str, str]] = []
    for spec in REPOS:
        status, output = sync_repo(spec)
        results.append((spec, status, output))
        print(f"{spec.name}: {status}")
        if output:
            print(output.splitlines()[-1])
    write_readme(results)
    print(f"updated: {EXTERNAL / 'README.md'}")


if __name__ == "__main__":
    main()

