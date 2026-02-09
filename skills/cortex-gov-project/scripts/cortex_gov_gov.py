#!/usr/bin/env python3
"""
`/gov` helper for Cortex GOV.

Non-interactive (safe for agent tool execution):
1) Creates a per-project folder (default: ./projects/<project_slug>/)
2) Writes <project-dir>/project_config.json (wizard-compatible schema)
3) Runs cortex_gov_bootstrap.py to generate PROJECT.md + HEARTBEAT.md in that folder
   and spawn an OpenClaw isolated agent whose heartbeat prompt reads PROJECT.md.

This script must NOT prompt for stdin input. If required fields are missing,
fail fast with a clear error.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

TEMPLATE_FILES = {
    "webapp": "general-webapp-config.json",
    "content": "content-site-config.json",
    "community": "recipe-community-config.json",
}


def slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "project"


def default_slug() -> str:
    ts = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return f"project-{ts}"


def infer_template(idea: str) -> str:
    t = (idea or "").lower()
    if any(k in t for k in ("blog", "seo", "content", "marketing", "landing", "docs", "documentation")):
        return "content"
    if any(k in t for k in ("community", "forum", "social", "ugc", "recipe", "recipes", "comments", "chat")):
        return "community"
    return "webapp"


def find_examples_dir() -> Optional[Path]:
    env_root = (os.environ.get("CORTEX_GOV_REPO") or "").strip()
    if env_root:
        c = Path(env_root) / "examples"
        if c.is_dir():
            return c

    script_path = Path(__file__).resolve()
    base = script_path.parents[3]  # workspace root or cortex-gov repo root

    candidates = [
        base / "examples",
        base / "cortex-gov" / "examples",
        Path.cwd() / "examples",
        Path.cwd() / "cortex-gov" / "examples",
    ]
    for c in candidates:
        if c.is_dir():
            return c
    return None


def builtin_template() -> Dict[str, Any]:
    return {
        "project_name": "New Project",
        "project_slug": "new-project",
        "summary": "A project to be defined.",
        "constraints": [
            "Evidence-based verification for all tasks",
        ],
        "epics": [
            {"key": "E001", "title": "Foundations", "outcome": ["Repo scaffolded", "Core architecture decided"]},
            {"key": "E002", "title": "Implementation", "outcome": ["Core features implemented end-to-end"]},
            {"key": "E003", "title": "DevEx + Ops", "outcome": ["Local run workflow", "Basic CI checks"]},
        ],
        "tasks": [
            {
                "key": "H001",
                "title": "Repo scaffold + baseline docs",
                "epic": "E001",
                "status": "TODO",
                "priority": "P0",
                "owner": "agent",
                "work": ["Create project structure", "Add README + run instructions", "Add env/secrets notes"],
                "acceptance": ["Project runs locally", "README documents how to run"],
                "verification_steps": ["Run local dev start", "Review README for completeness"],
                "evidence_fields": ["File paths", "Commands/output", "Notes", "URLs"],
            },
            {
                "key": "H002",
                "title": "Core feature slice (end-to-end)",
                "epic": "E002",
                "status": "TODO",
                "priority": "P0",
                "owner": "agent",
                "work": ["Implement one vertical slice", "Wire UI/API/storage as needed", "Add basic error handling"],
                "acceptance": ["A primary user flow works end-to-end"],
                "verification_steps": ["Run the app and execute the flow", "Capture evidence (paths + commands)"],
                "evidence_fields": ["File paths", "Commands/output", "Screenshots", "Notes"],
            },
            {
                "key": "H003",
                "title": "Basic CI + verification workflow",
                "epic": "E003",
                "status": "TODO",
                "priority": "P2",
                "owner": "agent",
                "work": ["Add lint/test/build checks", "Document verification process"],
                "acceptance": ["CI checks run", "Verification steps documented"],
                "verification_steps": ["Run CI locally or validate config", "Confirm evidence artifacts are linked"],
                "evidence_fields": ["File paths", "Commands/output", "Notes", "URLs"],
            },
        ],
    }


def load_template_config(template: str) -> Dict[str, Any]:
    examples_dir = find_examples_dir()
    if not examples_dir:
        return builtin_template()

    fname = TEMPLATE_FILES.get(template)
    if not fname:
        return builtin_template()

    path = examples_dir / fname
    if not path.exists():
        return builtin_template()

    return json.loads(path.read_text(encoding="utf-8"))


def build_project_config(
    *,
    project_name: str,
    project_slug: str,
    summary: Optional[str],
    template: str,
    owner: str,
    extra_constraints: List[str],
) -> Dict[str, Any]:
    cfg = load_template_config(template)
    cfg["project_name"] = project_name
    cfg["project_slug"] = project_slug
    if summary:
        cfg["summary"] = summary

    constraints = list(cfg.get("constraints") or [])
    for c in extra_constraints:
        c = (c or "").strip()
        if c and c not in constraints:
            constraints.append(c)
    cfg["constraints"] = constraints

    for t in cfg.get("tasks") or []:
        t["owner"] = owner
        t.setdefault("status", "TODO")

    return cfg


def run_bootstrap(
    bootstrap_path: Path,
    *,
    project_dir: Path,
    config_path: Path,
    control_doc: str,
    agent_prefix: str,
    agent_count: int,
    model: Optional[str],
    binds: List[str],
    heartbeat_every: Optional[str],
    openclaw_profile: Optional[str],
    openclaw_dev: bool,
) -> None:
    cmd = [
        sys.executable,
        str(bootstrap_path),
        "--project-dir",
        str(project_dir),
        "--config",
        str(config_path),
        "--control-doc",
        control_doc,
        "--prefix",
        agent_prefix,
        "--count",
        str(agent_count),
    ]
    if model:
        cmd.extend(["--model", model])
    for b in binds:
        cmd.extend(["--bind", b])
    if heartbeat_every:
        cmd.extend(["--heartbeat-every", heartbeat_every])
    if openclaw_profile:
        cmd.extend(["--openclaw-profile", openclaw_profile])
    if openclaw_dev:
        cmd.append("--openclaw-dev")

    result = subprocess.run(cmd)
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("project_name", nargs="?", help="Optional project name (recommended)")
    ap.add_argument("--idea", "--summary", dest="summary", default=None, help="1-2 sentence success summary")
    ap.add_argument("--template", default="auto", choices=["auto", "webapp", "content", "community"], help="Project template (default: auto)")
    ap.add_argument("--project-dir", default=None, help="Project directory (default: ./projects/<slug>)")
    ap.add_argument("--projects-root", default="projects", help="Root folder for new projects (default: ./projects)")
    ap.add_argument("--owner", default="agent", help="Default task owner (default: agent)")
    ap.add_argument("--constraint", action="append", default=[], help="Extra constraint to append (repeatable)")
    ap.add_argument("--overwrite", action="store_true", help="Overwrite an existing project_config.json")

    # Agent spawn defaults
    ap.add_argument("--agent-prefix", default=None, help="Agent id prefix (default: <project_slug>)")
    ap.add_argument("--agent-count", type=int, default=1, help="How many agents to spawn (default: 1)")
    ap.add_argument("--control-doc", default="PROJECT.md", help="Control doc filename (default: PROJECT.md)")

    # OpenClaw passthrough
    ap.add_argument("--model", default=None, help="Model id for spawned agents (optional)")
    ap.add_argument("--bind", action="append", default=[], help="Route binding channel[:accountId] (repeatable)")
    ap.add_argument("--heartbeat-every", default=None, help="Heartbeat interval (e.g. 30m, 2h). Omit to keep defaults.")
    ap.add_argument("--openclaw-profile", default=None, help="OpenClaw profile name (optional)")
    ap.add_argument("--openclaw-dev", action="store_true", help="Use OpenClaw --dev profile (isolated state)")
    args = ap.parse_args()

    project_name = (args.project_name or "").strip() or "New Project"
    project_slug = slugify(project_name) if args.project_name else default_slug()

    if args.template == "auto":
        template = infer_template(args.summary or "")
    else:
        template = args.template

    if args.project_dir:
        project_dir = Path(args.project_dir).resolve()
    else:
        project_dir = (Path.cwd() / args.projects_root / project_slug).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    config_path = project_dir / "project_config.json"
    if config_path.exists() and not args.overwrite:
        raise SystemExit(f"Refusing to overwrite existing config: {config_path} (use --overwrite)")

    cfg = build_project_config(
        project_name=project_name,
        project_slug=project_slug,
        summary=args.summary,
        template=template,
        owner=args.owner,
        extra_constraints=args.constraint,
    )

    config_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote: {config_path}")

    bootstrap_path = Path(__file__).resolve().parent / "cortex_gov_bootstrap.py"
    if not bootstrap_path.exists():
        raise SystemExit(f"Missing bootstrap script: {bootstrap_path}")

    agent_prefix = args.agent_prefix or project_slug

    run_bootstrap(
        bootstrap_path,
        project_dir=project_dir,
        config_path=config_path,
        control_doc=Path(args.control_doc).name,
        agent_prefix=agent_prefix,
        agent_count=max(1, int(args.agent_count)),
        model=args.model,
        binds=args.bind,
        heartbeat_every=args.heartbeat_every,
        openclaw_profile=args.openclaw_profile,
        openclaw_dev=args.openclaw_dev,
    )


if __name__ == "__main__":
    main()

