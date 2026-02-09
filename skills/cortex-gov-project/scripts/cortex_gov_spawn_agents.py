#!/usr/bin/env python3
"""
Spawn OpenClaw isolated agents for a Cortex GOV project workspace and (optionally)
configure per-agent heartbeat prompts to point directly at the project's control doc.

Why this exists:
- OpenClaw heartbeats default to: "Read HEARTBEAT.md..."
- Cortex GOV uses a control doc (default: PROJECT.md) as the single source of truth
- In multi-project setups, it's cleaner to spawn per-project agents whose heartbeat
  prompt reads that project's PROJECT.md in its own workspace.

Usage:
  python cortex_gov_spawn_agents.py --project-dir <dir>
  python cortex_gov_spawn_agents.py --project-dir <dir> --agents bot ui qa
  python cortex_gov_spawn_agents.py --project-dir <dir> --prefix cp --count 3

OpenClaw profile control:
  python cortex_gov_spawn_agents.py ... --openclaw-dev
  python cortex_gov_spawn_agents.py ... --openclaw-profile dev
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple


ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")


DEFAULT_MAIN_HEARTBEAT_PROMPT = (
    "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. "
    "Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
)


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def extract_json(text: str):
    cleaned = strip_ansi(text).strip()
    start = min(
        [i for i in (cleaned.find("{"), cleaned.find("[")) if i != -1],
        default=-1,
    )
    if start == -1:
        raise ValueError("No JSON object/array found in output")
    return json.loads(cleaned[start:])


def build_openclaw_cmd(base_args: Sequence[str], profile: Optional[str], dev: bool) -> List[str]:
    exe = shutil.which("openclaw") or "openclaw"
    cmd = [exe, "--no-color"]
    if dev:
        cmd.append("--dev")
    elif profile:
        cmd.extend(["--profile", profile])
    cmd.extend(base_args)
    return cmd


def run_cmd(cmd: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(list(cmd), capture_output=True, text=True)


def normalize_agent_id(raw: str) -> str:
    val = (raw or "").strip().lower()
    val = re.sub(r"[^a-z0-9_-]+", "-", val).strip("-_")
    if not val:
        return "proj"
    if val[0].isdigit():
        val = f"p-{val}"
    return val[:32]


def default_agent_prefix(project_dir: Path) -> str:
    return normalize_agent_id(project_dir.name)


def make_agent_ids(prefix: str, count: int) -> List[str]:
    prefix = normalize_agent_id(prefix)
    if count <= 1:
        return [prefix]

    max_digits = len(str(count))
    # 32 = max id length; reserve "-" + digits.
    max_prefix_len = max(1, 32 - (1 + max_digits))
    safe_prefix = prefix[:max_prefix_len].strip("-_") or "proj"
    return [f"{safe_prefix}-{i}" for i in range(1, count + 1)]


def get_agents_config(project_profile: Optional[str], dev: bool) -> Dict:
    cmd = build_openclaw_cmd(["config", "get", "agents", "--json"], project_profile, dev)
    result = run_cmd(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return extract_json(result.stdout)

def normalize_workspace_path(p: str) -> str:
    try:
        return str(Path(p).resolve())
    except Exception:
        return str(Path(p))

def workspaces_match(config_workspace: str, project_dir: Path) -> bool:
    if not config_workspace:
        return False
    return normalize_workspace_path(config_workspace).casefold() == str(project_dir.resolve()).casefold()

def next_available_agent_id(base_id: str, taken: set) -> str:
    base = normalize_agent_id(base_id)
    if base not in taken:
        return base

    i = 2
    while True:
        suffix = f"-{i}"
        max_base_len = max(1, 32 - len(suffix))
        cand_base = base[:max_base_len].rstrip("-_") or "proj"
        cand = f"{cand_base}{suffix}"
        if cand not in taken:
            return cand
        i += 1

def resolve_agent_ids(
    desired_ids: List[str],
    project_dir: Path,
    profile: Optional[str],
    dev: bool,
) -> Tuple[List[str], Dict[str, str]]:
    agents_cfg = get_agents_config(profile, dev)
    existing_entries = {e.get("id"): e for e in (agents_cfg.get("list") or []) if e.get("id")}
    taken = set(existing_entries.keys())

    resolved: List[str] = []
    collisions: Dict[str, str] = {}
    for raw in desired_ids:
        desired = normalize_agent_id(raw)
        if desired in existing_entries:
            ws = (existing_entries[desired] or {}).get("workspace") or ""
            if workspaces_match(ws, project_dir):
                final = desired
            else:
                final = next_available_agent_id(desired, taken | set(resolved))
                collisions[desired] = final
        else:
            final = desired

        resolved.append(final)
        taken.add(final)

    return resolved, collisions


def find_agent_index(agents_cfg: Dict, agent_id: str) -> Optional[int]:
    lst = agents_cfg.get("list") or []
    for idx, entry in enumerate(lst):
        if (entry.get("id") or "") == agent_id:
            return idx
    return None


def ensure_agent_exists(
    agent_id: str,
    workspace: Path,
    model: Optional[str],
    binds: Sequence[str],
    profile: Optional[str],
    dev: bool,
) -> None:
    args = ["agents", "add", agent_id, "--workspace", str(workspace), "--non-interactive", "--json"]
    if model:
        args.extend(["--model", model])
    for b in binds:
        args.extend(["--bind", b])

    cmd = build_openclaw_cmd(args, profile, dev)
    result = run_cmd(cmd)
    if result.returncode == 0:
        return

    # If it already exists, we fall back to setting workspace/model via config.
    msg = (result.stderr or result.stdout).strip()
    if "already exists" not in msg.lower():
        raise RuntimeError(msg)


def set_config_value(
    path: str,
    value: str,
    profile: Optional[str],
    dev: bool,
    json_value: bool = False,
) -> None:
    args = ["config", "set"]
    if json_value:
        args.append("--json")
    args.extend([path, value])
    cmd = build_openclaw_cmd(args, profile, dev)
    result = run_cmd(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def configure_agent_heartbeat(
    agent_id: str,
    *,
    control_doc: str,
    every: Optional[str],
    prompt: Optional[str],
    profile: Optional[str],
    dev: bool,
) -> None:
    agents_cfg = get_agents_config(profile, dev)
    idx = find_agent_index(agents_cfg, agent_id)
    if idx is None:
        raise RuntimeError(f"Could not find agent in config: {agent_id}")

    hb_prompt = prompt or (
        f"Read {control_doc} if it exists (workspace context). Follow the rules set in that doc strictly. "
        f"Do not infer or repeat old tasks from prior chats. Complete the first available TODO task in {control_doc} "
        f"and update its status and evidence. If no task to do in {control_doc} reply with HEARTBEAT_OK and include your agent ID."
    )

    set_config_value(f"agents.list[{idx}].heartbeat.prompt", hb_prompt, profile, dev)
    if every:
        set_config_value(f"agents.list[{idx}].heartbeat.every", every, profile, dev)


def ensure_agent_workspace_and_model(
    agent_id: str,
    *,
    workspace: Path,
    model: Optional[str],
    profile: Optional[str],
    dev: bool,
) -> None:
    agents_cfg = get_agents_config(profile, dev)
    idx = find_agent_index(agents_cfg, agent_id)
    if idx is None:
        raise RuntimeError(f"Could not find agent in config: {agent_id}")

    set_config_value(f"agents.list[{idx}].workspace", str(workspace), profile, dev)
    if model:
        set_config_value(f"agents.list[{idx}].model", model, profile, dev)


def maybe_preserve_main_heartbeat(profile: Optional[str], dev: bool) -> None:
    agents_cfg = get_agents_config(profile, dev)
    idx = find_agent_index(agents_cfg, "main")
    if idx is None:
        return
    entry = (agents_cfg.get("list") or [])[idx]
    if isinstance(entry.get("heartbeat"), dict):
        return
    set_config_value(f"agents.list[{idx}].heartbeat.prompt", DEFAULT_MAIN_HEARTBEAT_PROMPT, profile, dev)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--project-dir", required=True, help="Project directory (agent workspace)")
    ap.add_argument("--control-doc", default="PROJECT.md", help="Control doc filename in the project workspace")
    ap.add_argument("--agents", nargs="*", default=None, help="Explicit agent ids to create (space-separated)")
    ap.add_argument("--prefix", default=None, help="Agent id prefix (default: slugified project dir name)")
    ap.add_argument("--count", type=int, default=1, help="How many agents to create when using --prefix (default: 1)")
    ap.add_argument("--model", default=None, help="Model id for spawned agents (optional)")
    ap.add_argument("--bind", action="append", default=[], help="Route binding channel[:accountId] (repeatable)")
    ap.add_argument("--heartbeat-every", default=None, help="Heartbeat interval (e.g. 30m, 2h). Omit to keep defaults.")
    ap.add_argument("--heartbeat-prompt", default=None, help="Override heartbeat prompt text (optional)")
    ap.add_argument("--preserve-main-heartbeat", action="store_true", default=True, help="Ensure main agent keeps heartbeats when per-agent heartbeat config is added (default: true)")
    ap.add_argument("--no-preserve-main-heartbeat", dest="preserve_main_heartbeat", action="store_false")
    ap.add_argument("--openclaw-profile", default=None, help="OpenClaw profile name (optional)")
    ap.add_argument("--openclaw-dev", action="store_true", help="Use OpenClaw --dev profile (isolated state)")
    args = ap.parse_args()

    project_dir = Path(args.project_dir).resolve()
    project_dir.mkdir(parents=True, exist_ok=True)

    control_doc = Path(args.control_doc).name

    if args.agents is not None and len(args.agents) > 0:
        agent_ids = [normalize_agent_id(a) for a in args.agents]
    else:
        prefix = args.prefix or default_agent_prefix(project_dir)
        agent_ids = make_agent_ids(prefix, args.count)

    agent_ids, collisions = resolve_agent_ids(agent_ids, project_dir, args.openclaw_profile, args.openclaw_dev)
    if collisions:
        print("Agent id collisions detected (existing agent had a different workspace):")
        for old, new in collisions.items():
            print(f"  - {old} -> {new}")

    # Create agents (or ensure they exist)
    for agent_id in agent_ids:
        ensure_agent_exists(agent_id, project_dir, args.model, args.bind, args.openclaw_profile, args.openclaw_dev)
        ensure_agent_workspace_and_model(
            agent_id,
            workspace=project_dir,
            model=args.model,
            profile=args.openclaw_profile,
            dev=args.openclaw_dev,
        )

    # Configure heartbeats to point directly at the control doc
    for agent_id in agent_ids:
        configure_agent_heartbeat(
            agent_id,
            control_doc=control_doc,
            every=args.heartbeat_every,
            prompt=args.heartbeat_prompt,
            profile=args.openclaw_profile,
            dev=args.openclaw_dev,
        )

    if args.preserve_main_heartbeat:
        maybe_preserve_main_heartbeat(args.openclaw_profile, args.openclaw_dev)

    print("Spawned/updated agents:")
    for agent_id in agent_ids:
        print(f"  - {agent_id} (workspace: {project_dir})")
    print("Note: OpenClaw may require a gateway restart for heartbeat config changes to apply.")


if __name__ == "__main__":
    main()
