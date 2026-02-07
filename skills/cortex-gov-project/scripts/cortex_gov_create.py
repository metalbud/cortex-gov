#!/usr/bin/env python3
"""
Create Cortex GOV project files and OpenClaw-compatible HEARTBEAT.md.

Usage:
  python cortex_gov_create.py --config <project_config.json> --workspace <workspace-path>
  python cortex_gov_create.py --interactive --workspace <workspace-path>
"""

import argparse
import json
import os
import subprocess
from pathlib import Path

WIZARD_PATH = Path(r"C:\Users\metalbud\clawd\cortex-gov\tools\wizard\cortex_gov_wizard.py")

MULTI_AGENT_HEARTBEAT = (
"-Agent: Read PROJECT.md if it exists in workspace context. Follow the rules set in that doc strictly. "
"Do not infer or repeat old tasks from prior chats. Complete the first available TODO task and update your status, "
"then post a short summary of changes in #dev (discord) with your agent ID.\n"
"-If no task to do in PROJECT.md reply with HEARTBEAT OK and include your agent ID\n"
"-Workspace: {workspace}\n"
)


def write_heartbeat(workspace: Path):
    heartbeat_path = workspace / "HEARTBEAT.md"
    heartbeat_path.write_text(MULTI_AGENT_HEARTBEAT.format(workspace=str(workspace)))
    return heartbeat_path


def run_wizard(config_path: Path, out_path: Path, heartbeat_out: Path):
    cmd = [
        "python",
        str(WIZARD_PATH),
        "--non-interactive",
        "--config",
        str(config_path),
        "--out",
        str(out_path),
        "--heartbeat-out",
        str(heartbeat_out),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", help="Path to project_config.json")
    parser.add_argument("--workspace", required=True, help="Workspace root path")
    parser.add_argument("--interactive", action="store_true")
    args = parser.parse_args()

    workspace = Path(args.workspace)
    workspace.mkdir(parents=True, exist_ok=True)

    project_md = workspace / "PROJECT.md"
    heartbeat_md = workspace / "HEARTBEAT.md"

    if args.interactive:
        # In interactive mode, invoke the wizard directly (user input required)
        cmd = ["python", str(WIZARD_PATH), "--out", str(project_md), "--heartbeat-out", str(heartbeat_md)]
        subprocess.run(cmd, check=True)
    else:
        if not args.config:
            raise SystemExit("--config is required unless --interactive is used")
        config_path = Path(args.config)
        if not config_path.exists():
            raise SystemExit(f"Config not found: {config_path}")
        run_wizard(config_path, project_md, heartbeat_md)

    # Ensure multi-agent heartbeat format
    write_heartbeat(workspace)

    print("Created:")
    print(f"  PROJECT.md -> {project_md}")
    print(f"  HEARTBEAT.md -> {heartbeat_md}")


if __name__ == "__main__":
    main()
