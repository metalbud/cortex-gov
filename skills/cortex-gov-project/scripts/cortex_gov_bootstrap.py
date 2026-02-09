#!/usr/bin/env python3
"""
Bootstrap a governed project folder and spawn OpenClaw agents for it.

Creates:
- <project-dir>/<CONTROL_DOC> (default: PROJECT.md)
- <project-dir>/HEARTBEAT.md (multi-agent checklist, optional but useful)

Then spawns OpenClaw isolated agents whose workspaces point at <project-dir> and
configures their heartbeat prompt to read the control doc directly.

Usage:
  python cortex_gov_bootstrap.py --project-dir <dir> --config <project_config.json>
  python cortex_gov_bootstrap.py --project-dir <dir> --interactive

Optional:
  --agents bot ui qa
  --prefix cp --count 3
  --control-doc PROJECT.md
  --openclaw-dev | --openclaw-profile <name>
"""

from __future__ import annotations

import argparse
from pathlib import Path

from cortex_gov_create import (
    choose_control_doc_filename,
    load_project_slug,
    normalize_control_doc_name,
    run_wizard,
    write_heartbeat,
)

from cortex_gov_spawn_agents import main as spawn_main


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", required=True, help="Directory to create/initialize the governed project")
    ap.add_argument("--config", default=None, help="Path to project_config.json (required unless --interactive)")
    ap.add_argument("--interactive", action="store_true", help="Run the wizard interactively (prompts)")
    ap.add_argument("--control-doc", default=None, help="Control doc filename (default: PROJECT.md or a simple fallback)")
    ap.add_argument("--heartbeat-out", default=None, help="Optional HEARTBEAT.md path (default: <project-dir>/HEARTBEAT.md)")

    # Forwarded to cortex_gov_spawn_agents.py (keep names aligned)
    ap.add_argument("--agents", nargs="*", default=None)
    ap.add_argument("--prefix", default=None)
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--model", default=None)
    ap.add_argument("--bind", action="append", default=[])
    ap.add_argument("--heartbeat-every", default=None)
    ap.add_argument("--heartbeat-prompt", default=None)
    ap.add_argument("--no-preserve-main-heartbeat", dest="preserve_main_heartbeat", action="store_false")
    ap.add_argument("--openclaw-profile", default=None)
    ap.add_argument("--openclaw-dev", action="store_true")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    config_path = Path(args.config).resolve() if args.config else None
    project_slug = load_project_slug(config_path) if config_path else ""

    control_doc_name = choose_control_doc_filename(project_dir, args.control_doc, project_slug)
    if args.interactive and not args.control_doc:
        raw = input(f"Control document filename [{control_doc_name}]: ").strip()
        control_doc_name = normalize_control_doc_name(raw, control_doc_name)

    control_doc_path = project_dir / control_doc_name
    heartbeat_path = Path(args.heartbeat_out).resolve() if args.heartbeat_out else (project_dir / "HEARTBEAT.md")

    if args.interactive:
        # Interactive: invoke the wizard directly (user input required)
        from cortex_gov_create import find_wizard_path  # lazy import for speed
        import subprocess

        wizard_path = find_wizard_path()
        cmd = [
            "python",
            str(wizard_path),
            "--out",
            str(control_doc_path),
            "--heartbeat-out",
            str(heartbeat_path),
            "--control-doc",
            control_doc_name,
        ]
        subprocess.run(cmd, check=True)
    else:
        if not config_path:
            raise SystemExit("--config is required unless --interactive is used")
        if not config_path.exists():
            raise SystemExit(f"Config not found: {config_path}")
        run_wizard(config_path, control_doc_path, heartbeat_path, control_doc_name)

    # Ensure multi-agent heartbeat checklist exists (even if you set heartbeat.prompt to read PROJECT.md directly)
    write_heartbeat(project_dir, control_doc_name)

    # Spawn agents (calls OpenClaw)
    # We reuse the spawn script's CLI to keep behavior identical.
    spawn_args = [
        "--project-dir",
        str(project_dir),
        "--control-doc",
        control_doc_name,
    ]
    if args.agents is not None:
        spawn_args.extend(["--agents", *args.agents])
    if args.prefix:
        spawn_args.extend(["--prefix", args.prefix])
    if args.count:
        spawn_args.extend(["--count", str(args.count)])
    if args.model:
        spawn_args.extend(["--model", args.model])
    for b in args.bind:
        spawn_args.extend(["--bind", b])
    if args.heartbeat_every:
        spawn_args.extend(["--heartbeat-every", args.heartbeat_every])
    if args.heartbeat_prompt:
        spawn_args.extend(["--heartbeat-prompt", args.heartbeat_prompt])
    if args.openclaw_profile:
        spawn_args.extend(["--openclaw-profile", args.openclaw_profile])
    if args.openclaw_dev:
        spawn_args.append("--openclaw-dev")
    if args.preserve_main_heartbeat is False:
        spawn_args.append("--no-preserve-main-heartbeat")

    import sys

    old_argv = sys.argv
    try:
        sys.argv = ["cortex_gov_spawn_agents.py", *spawn_args]
        spawn_main()
    finally:
        sys.argv = old_argv

    print("Bootstrapped:")
    print(f"  Control doc: {control_doc_path}")
    print(f"  HEARTBEAT.md: {heartbeat_path}")


if __name__ == "__main__":
    main()

