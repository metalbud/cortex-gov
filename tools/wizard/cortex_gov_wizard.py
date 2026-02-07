#!/usr/bin/env python3
"""
Cortex GOV - Project Document Wizard
Cross-platform (Windows/macOS/Linux) interactive CLI to generate a PROJECT.md and a HEARTBEAT.md
with Cortex GOV rules, epics, and an initial ordered task list.

Usage:
  python cortex_gov_wizard.py
Optional:
  python cortex_gov_wizard.py --out PROJECT.md
  python cortex_gov_wizard.py --non-interactive --config project_config.json

Notes:
- This script intentionally prefers clarity over cleverness.
- It produces a deterministic, agent-friendly Markdown control document.
"""

from __future__ import annotations
import argparse
import json
import os
import re
from dataclasses import dataclass, asdict
from typing import List, Optional

DEFAULT_RULES = [
    "Only one task may be IN_PROGRESS at a time.",
    "Tasks must move: TODO → IN_PROGRESS → VERIFY → DONE (or BLOCKED).",
    "DONE may not be set directly from IN_PROGRESS.",
    "Each task must include acceptance criteria.",
    "Each task must include verification steps and evidence before DONE.",
    "Pick the first TODO task that is not BLOCKED.",
    "Epics never have status; only tasks do.",
]

DEFAULT_SELECTION_RULES = [
    "If any task is IN_PROGRESS or VERIFY, do not start a new task.",
    "Select the first TODO task by order that is not BLOCKED.",
    "Confirm prerequisites are satisfied before starting.",
    "Move task to IN_PROGRESS before doing any work.",
    "Do not change status to VERIFY or DONE until evidence exists.",
]

STATUSES = ["TODO", "IN_PROGRESS", "VERIFY", "DONE", "BLOCKED"]
PRIORITIES = ["P0", "P1", "P2", "P3"]

def slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "project"

def ask(prompt: str, default: Optional[str] = None) -> str:
    if default:
        q = f"{prompt} [{default}]: "
    else:
        q = f"{prompt}: "
    val = input(q).strip()
    return val if val else (default or "")

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    d = "Y/n" if default else "y/N"
    val = input(f"{prompt} ({d}): ").strip().lower()
    if not val:
        return default
    return val in ("y", "yes")

def pick(prompt: str, options: List[str], default_index: int = 0) -> str:
    print(prompt)
    for i, opt in enumerate(options, 1):
        marker = " (default)" if i-1 == default_index else ""
        print(f"  {i}. {opt}{marker}")
    while True:
        raw = input("Choose number: ").strip()
        if not raw:
            return options[default_index]
        if raw.isdigit():
            idx = int(raw) - 1
            if 0 <= idx < len(options):
                return options[idx]
        print("Invalid choice. Try again.")

@dataclass
class Epic:
    key: str
    title: str
    outcome: List[str]

@dataclass
class Task:
    key: str
    title: str
    epic: str
    status: str
    priority: str
    owner: str
    work: List[str]
    acceptance: List[str]
    verification_steps: List[str]
    evidence_fields: List[str]

@dataclass
class ProjectConfig:
    project_name: str
    project_slug: str
    summary: str
    constraints: List[str]
    epics: List[Epic]
    tasks: List[Task]

def ensure_unique_keys(prefix: str, count: int, start: int = 1, width: int = 3) -> List[str]:
    return [f"{prefix}{str(i).zfill(width)}" for i in range(start, start + count)]

def to_markdown(cfg: ProjectConfig) -> str:
    md = []
    md.append(f"# {cfg.project_name}\n")
    if cfg.summary.strip():
        md.append("## Summary\n")
        md.append(cfg.summary.strip() + "\n")
    if cfg.constraints:
        md.append("## Constraints\n")
        for c in cfg.constraints:
            md.append(f"- {c}")
        md.append("")

    md.append("## Rules")
    for r in DEFAULT_RULES:
        md.append(f"- {r}")
    md.append("")

    md.append("## Task Selection Rules (for Agents)")
    for i, r in enumerate(DEFAULT_SELECTION_RULES, 1):
        md.append(f"{i}. {r}")
    md.append("")

    md.append("## Epics\n")
    for e in cfg.epics:
        md.append(f"### {e.key}: {e.title}")
        md.append("Outcome:")
        for o in e.outcome:
            md.append(f"- {o}")
        md.append("")
    md.append("")

    md.append("## Tasks (Ordered)\n")
    for t in cfg.tasks:
        md.append(f"### {t.key}: {t.title}")
        md.append(f"Epic: {t.epic}  ")
        md.append(f"Status: {t.status}  ")
        md.append(f"Priority: {t.priority}  ")
        md.append(f"Owner: {t.owner}  \n")
        if t.work:
            md.append("Work:")
            for w in t.work:
                md.append(f"- [ ] {w}")
            md.append("")
        md.append("Acceptance Criteria:")
        for a in t.acceptance:
            md.append(f"- [ ] {a}")
        md.append("")
        md.append("Verification Steps:")
        for v in t.verification_steps:
            md.append(f"- [ ] {v}")
        md.append("")
        md.append("Verification Evidence:")
        for ef in t.evidence_fields:
            md.append(f"- {ef}: ")
        md.append("\n---\n")
    return "\n".join(md).strip() + "\n"

def interactive_build() -> ProjectConfig:
    print("Cortex GOV - Project Document Wizard\n")

    project_name = ask("Project name", "PROJECT")
    project_slug = slugify(project_name)
    summary = ask("One-paragraph summary of what success looks like (can be blank)", "")
    print("\nConstraints help agents avoid guessing. Examples: budget limits, tech stack, deadlines, do-not-do.")
    constraints = []
    if ask_yes_no("Add constraints?", True):
        while True:
            c = ask("Constraint (blank to stop)", "")
            if not c.strip():
                break
            constraints.append(c.strip())

    print("\nDefine Epics (outcome buckets). Keep outcomes testable.")
    epics: List[Epic] = []
    epic_count_raw = ask("How many epics?", "4")
    try:
        epic_count = max(1, int(epic_count_raw))
    except ValueError:
        epic_count = 4
    epic_keys = ensure_unique_keys("E", epic_count, start=1, width=3)
    for i in range(epic_count):
        key = epic_keys[i]
        title = ask(f"Epic {key} title", f"Epic {i+1}")
        outcomes = []
        print(f"Enter outcomes for {key} (blank to stop).")
        while True:
            o = ask("Outcome", "")
            if not o.strip():
                break
            outcomes.append(o.strip())
        if not outcomes:
            outcomes = ["Define outcomes here."]
        epics.append(Epic(key=key, title=title, outcome=outcomes))

    print("\nDefine Tasks (ordered). Keep tasks small enough to verify.")
    tasks: List[Task] = []
    task_count_raw = ask("How many tasks to start with?", "8")
    try:
        task_count = max(1, int(task_count_raw))
    except ValueError:
        task_count = 8
    task_keys = ensure_unique_keys("H", task_count, start=1, width=3)

    default_owner = ask("Default owner label (e.g., agent, human, team-name)", "agent")

    for i in range(task_count):
        key = task_keys[i]
        title = ask(f"Task {key} title", f"Task {i+1}")
        epic_choice = pick(f"Select epic for {key}", [f"{e.key}: {e.title}" for e in epics], 0).split(":")[0]
        priority = pick(f"Select priority for {key}", PRIORITIES, 1 if i > 0 else 0)
        owner = ask(f"Owner for {key}", default_owner)

        status = "TODO"
        if i == 0 and ask_yes_no("Mark first task as IN_PROGRESS now?", False):
            status = "IN_PROGRESS"

        work = []
        if ask_yes_no(f"Add work checklist items for {key}?", True):
            while True:
                w = ask("Work item (blank to stop)", "")
                if not w.strip():
                    break
                work.append(w.strip())

        acceptance = []
        print("Acceptance criteria (required). Provide testable checks.")
        while True:
            a = ask("Acceptance criterion (blank to stop)", "")
            if not a.strip():
                break
            acceptance.append(a.strip())
        if not acceptance:
            acceptance = ["Define testable acceptance criteria."]

        verification_steps = []
        print("Verification steps (required). Provide explicit steps to prove completion.")
        while True:
            v = ask("Verification step (blank to stop)", "")
            if not v.strip():
                break
            verification_steps.append(v.strip())
        if not verification_steps:
            verification_steps = ["Define explicit verification steps."]

        evidence_fields = ["URLs", "File paths", "Commands/output", "Notes"]
        tasks.append(Task(
            key=key, title=title, epic=epic_choice, status=status, priority=priority,
            owner=owner, work=work, acceptance=acceptance,
            verification_steps=verification_steps, evidence_fields=evidence_fields
        ))

    return ProjectConfig(
        project_name=project_name,
        project_slug=project_slug,
        summary=summary,
        constraints=constraints,
        epics=epics,
        tasks=tasks
    )

def load_config(path: str) -> ProjectConfig:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    epics = [Epic(**e) for e in data.get("epics", [])]
    tasks = [Task(**t) for t in data.get("tasks", [])]

    return ProjectConfig(
        project_name=data.get("project_name", "PROJECT"),
        project_slug=data.get("project_slug", slugify(data.get("project_name", "PROJECT"))),
        summary=data.get("summary", ""),
        constraints=data.get("constraints", []),
        epics=epics,
        tasks=tasks
    )

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="PROJECT.md", help="Output markdown file path")
    ap.add_argument("--heartbeat-out", default="HEARTBEAT.md", help="Output HEARTBEAT.md path")
    ap.add_argument("--control-doc", default=None, help="Path/name of the control doc agents should follow (defaults to --out basename)")
    ap.add_argument("--non-interactive", action="store_true", help="Use --config and do not prompt")
    ap.add_argument("--config", help="Path to JSON config for non-interactive mode")
    args = ap.parse_args()

    if args.non_interactive:
        if not args.config:
            raise SystemExit("--non-interactive requires --config path")
        cfg = load_config(args.config)
    else:
        cfg = interactive_build()

    md = to_markdown(cfg)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)

    control_doc = args.control_doc or os.path.basename(args.out)
    heartbeat_lines = [
        f"-Check {control_doc} read and follow the rules set in that doc complete a task and update your status, then post a short summary of changes in #dev (discord)",
        f"-If no task to do {control_doc} reply with HEARTBEAT OK",
    ]
    with open(args.heartbeat_out, "w", encoding="utf-8") as hf:
        hf.write("\n".join(heartbeat_lines) + "\n")

    print(f"\nWrote: {args.out}")
    print("Next: commit PROJECT.md to your repo. Point your agent loop at it as the single source of truth.\n")

if __name__ == "__main__":
    main()
