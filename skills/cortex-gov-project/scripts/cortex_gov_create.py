#!/usr/bin/env python3
"""
Create Cortex GOV project files and OpenClaw-compatible HEARTBEAT.md.

Usage:
  python cortex_gov_create.py --config <project_config.json> --workspace <workspace-path>
  python cortex_gov_create.py --interactive --workspace <workspace-path>
  python cortex_gov_create.py --config <project_config.json> --workspace <workspace-path> --control-doc CONTROL.md
"""

import argparse
import json
import os
import subprocess
from pathlib import Path
from typing import Optional

DEFAULT_WIZARD_REL = Path("tools") / "wizard" / "cortex_gov_wizard.py"

MULTI_AGENT_HEARTBEAT = (
"-Agent: Read {control_doc} if it exists in workspace context. Follow the rules set in that doc strictly. "
"Do not infer or repeat old tasks from prior chats. Complete the first available TODO task and update your status, "
"then post a short summary of changes in #dev (discord) with your agent ID.\n"
"-If no task to do in {control_doc} reply with HEARTBEAT_OK and include your agent ID\n"
"-Workspace: {workspace}\n"
)

def find_wizard_path() -> Path:
    """
    Locate the Cortex GOV wizard script.

    Supports:
    - Running inside the cortex-gov repo (skill lives at <repo>/skills/...)
    - Running from a workspace that contains the cortex-gov repo as a subfolder
      (skill lives at <workspace>/skills/...)
    - Explicit override via CORTEX_GOV_REPO env var
    """
    env_root = (os.environ.get("CORTEX_GOV_REPO") or "").strip()
    if env_root:
        candidate = Path(env_root) / DEFAULT_WIZARD_REL
        if candidate.exists():
            return candidate

    script_path = Path(__file__).resolve()
    base = script_path.parents[3]  # <repo> when in cortex-gov; <workspace> when copied to workspace skills

    candidates = [
        base / DEFAULT_WIZARD_REL,
        base / "cortex-gov" / DEFAULT_WIZARD_REL,
        Path.cwd() / DEFAULT_WIZARD_REL,
        Path.cwd() / "cortex-gov" / DEFAULT_WIZARD_REL,
    ]
    for c in candidates:
        if c.exists():
            return c

    raise SystemExit(
        "Could not find cortex_gov_wizard.py. Set CORTEX_GOV_REPO to the cortex-gov repo root, "
        "or ensure tools/wizard/cortex_gov_wizard.py exists (repo root or ./cortex-gov/...)."
    )


def write_heartbeat(workspace: Path, control_doc: str):
    heartbeat_path = workspace / "HEARTBEAT.md"
    heartbeat_path.write_text(MULTI_AGENT_HEARTBEAT.format(workspace=str(workspace), control_doc=control_doc))
    return heartbeat_path


def run_wizard(config_path: Path, out_path: Path, heartbeat_out: Path, control_doc: str):
    wizard_path = find_wizard_path()
    cmd = [
        "python",
        str(wizard_path),
        "--non-interactive",
        "--config",
        str(config_path),
        "--out",
        str(out_path),
        "--heartbeat-out",
        str(heartbeat_out),
        "--control-doc",
        control_doc,
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()

def load_project_slug(config_path: Path) -> str:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
        slug = (data.get("project_slug") or "").strip()
        return slug
    except Exception:
        return ""

def normalize_control_doc_name(raw: str, default_name: str) -> str:
    name = (raw or "").strip()
    if not name:
        name = default_name
    name = Path(name).name
    if not name.lower().endswith(".md"):
        name = f"{name}.md"
    return name

def choose_control_doc_filename(workspace: Path, preferred: Optional[str], project_slug: str) -> str:
    """
    Choose a simple, human-typable control doc name.
    - Defaults to PROJECT.md (if available)
    - Falls back to PROJECT-<slug>.md
    - Otherwise increments PROJECT-2.md, PROJECT-3.md ...
    """
    def exists(name: str) -> bool:
        return (workspace / name).exists()

    if preferred:
        return normalize_control_doc_name(preferred, "PROJECT.md")

    if not exists("PROJECT.md"):
        return "PROJECT.md"

    if project_slug:
        candidate = f"PROJECT-{project_slug}.md"
        if not exists(candidate):
            return candidate

    i = 2
    while True:
        candidate = f"PROJECT-{i}.md"
        if not exists(candidate):
            return candidate
        i += 1


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to project_config.json")
    parser.add_argument("--workspace", required=True, help="Workspace root path")
    parser.add_argument("--interactive", action="store_true")
    parser.add_argument("--control-doc", default=None, help="Control doc filename to generate (default: PROJECT.md or a simple fallback)")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    project_slug = load_project_slug(Path(args.config)) if args.config else ""
    control_doc_name = choose_control_doc_filename(workspace, args.control_doc, project_slug)
    if args.interactive and not args.control_doc:
        raw = input(f"Control document filename [{control_doc_name}]: ").strip()
        control_doc_name = normalize_control_doc_name(raw, control_doc_name)
    project_md = workspace / control_doc_name
    heartbeat_md = workspace / "HEARTBEAT.md"

    if args.interactive:
        # In interactive mode, invoke the wizard directly (user input required)
        wizard_path = find_wizard_path()
        cmd = ["python", str(wizard_path), "--out", str(project_md), "--heartbeat-out", str(heartbeat_md), "--control-doc", control_doc_name]
        subprocess.run(cmd, check=True)
    else:
        if not args.config:
            raise SystemExit("--config is required unless --interactive is used")
        config_path = Path(args.config)
        if not config_path.exists():
            raise SystemExit(f"Config not found: {config_path}")
        run_wizard(config_path, project_md, heartbeat_md, control_doc_name)

    # Ensure multi-agent heartbeat format
    write_heartbeat(workspace, control_doc_name)

    print("Created:")
    print(f"  Control doc -> {project_md.name}")
    print(f"    Path: {project_md}")
    print(f"  HEARTBEAT.md -> {heartbeat_md}")


if __name__ == "__main__":
    main()
