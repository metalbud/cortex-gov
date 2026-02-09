#!/usr/bin/env python3
"""
Local GUI for managing OpenClaw projects and agents.

- Scans a workspace root for directories that contain PROJECT.md
- Reads OpenClaw agent config via CLI
- Lets you update model + heartbeat settings per agent
- Lets you spawn agents for a project workspace
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from urllib.parse import urlparse

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "venv",
    "node_modules",
    "__pycache__",
    ".openclaw",
    ".clawd",
}

DEFAULT_MAIN_HEARTBEAT_PROMPT = (
    "Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. "
    "Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK."
)

PROJECT_DOC_NAME = "PROJECT.md"


def strip_ansi(s: str) -> str:
    return ANSI_RE.sub("", s)


def extract_json(text: str) -> Any:
    cleaned = strip_ansi(text).strip()
    start = min([i for i in (cleaned.find("{"), cleaned.find("[")) if i != -1], default=-1)
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


def get_agents_config(profile: Optional[str], dev: bool) -> Dict[str, Any]:
    cmd = build_openclaw_cmd(["config", "get", "agents", "--json"], profile, dev)
    result = run_cmd(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    return extract_json(result.stdout)


def set_config_value(path: str, value: str, profile: Optional[str], dev: bool, json_value: bool = False) -> None:
    args = ["config", "set"]
    if json_value:
        args.append("--json")
    args.extend([path, value])
    cmd = build_openclaw_cmd(args, profile, dev)
    result = run_cmd(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def unset_config_value(path: str, profile: Optional[str], dev: bool) -> None:
    cmd = build_openclaw_cmd(["config", "unset", path], profile, dev)
    result = run_cmd(cmd)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())


def normalize_workspace_path(p: str) -> str:
    raw = os.path.expandvars(os.path.expanduser(p))
    try:
        return str(Path(raw).resolve())
    except Exception:
        return str(Path(raw))


def workspaces_match(config_workspace: str, project_dir: Path) -> bool:
    if not config_workspace:
        return False
    return normalize_workspace_path(config_workspace).casefold() == str(project_dir.resolve()).casefold()


def default_workspace_root(profile: Optional[str], dev: bool, agents_cfg: Optional[Dict[str, Any]]) -> Path:
    defaults = (agents_cfg or {}).get("defaults") or {}
    ws = (defaults.get("workspace") or "").strip()
    if ws:
        return Path(os.path.expandvars(os.path.expanduser(ws)))
    return Path("~/.openclaw/workspace").expanduser()


def read_project_meta(project_md: Path) -> Dict[str, str]:
    title = ""
    summary = ""
    try:
        for line in project_md.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not title and line.lstrip().startswith("#"):
                title = line.lstrip("#").strip()
                continue
            if title and not summary and line.strip():
                summary = line.strip()
                break
    except Exception:
        pass
    return {"title": title, "summary": summary}


def scan_projects(root: Path, max_depth: int) -> List[Dict[str, Any]]:
    projects: List[Dict[str, Any]] = []
    if not root.exists():
        return projects

    root = root.resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        rel_parts = current.relative_to(root).parts
        if len(rel_parts) > max_depth:
            dirnames[:] = []
            continue

        dirnames[:] = [
            d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")
        ]

        if any(f.lower() == PROJECT_DOC_NAME.lower() for f in filenames):
            project_md = current / PROJECT_DOC_NAME
            meta = read_project_meta(project_md)
            projects.append(
                {
                    "name": meta["title"] or current.name,
                    "summary": meta["summary"],
                    "path": str(current),
                    "control_doc": PROJECT_DOC_NAME,
                    "heartbeat_exists": (current / "HEARTBEAT.md").exists(),
                }
            )
            dirnames[:] = []

    projects.sort(key=lambda p: p["name"].lower())
    return projects


def normalize_agent_id(raw: str) -> str:
    val = (raw or "").strip().lower()
    val = re.sub(r"[^a-z0-9_-]+", "-", val).strip("-_")
    if not val:
        return "proj"
    if val[0].isdigit():
        val = f"p-{val}"
    return val[:32]


def make_agent_ids(prefix: str, count: int) -> List[str]:
    prefix = normalize_agent_id(prefix)
    if count <= 1:
        return [prefix]
    max_digits = len(str(count))
    max_prefix_len = max(1, 32 - (1 + max_digits))
    safe_prefix = prefix[:max_prefix_len].strip("-_") or "proj"
    return [f"{safe_prefix}-{i}" for i in range(1, count + 1)]


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
    desired_ids: List[str], project_dir: Path, profile: Optional[str], dev: bool
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


def find_agent_index(agents_cfg: Dict[str, Any], agent_id: str) -> Optional[int]:
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
    msg = (result.stderr or result.stdout).strip()
    if "already exists" not in msg.lower():
        raise RuntimeError(msg)


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
    hb_prompt = prompt or default_project_prompt(control_doc)
    if hb_prompt:
        set_config_value(f"agents.list[{idx}].heartbeat.prompt", hb_prompt, profile, dev)
    if every:
        set_config_value(f"agents.list[{idx}].heartbeat.every", every, profile, dev)


def maybe_preserve_main_heartbeat(profile: Optional[str], dev: bool) -> None:
    agents_cfg = get_agents_config(profile, dev)
    idx = find_agent_index(agents_cfg, "main")
    if idx is None:
        return
    entry = (agents_cfg.get("list") or [])[idx]
    if isinstance(entry.get("heartbeat"), dict):
        return
    set_config_value(f"agents.list[{idx}].heartbeat.prompt", DEFAULT_MAIN_HEARTBEAT_PROMPT, profile, dev)


def default_project_prompt(control_doc: str) -> str:
    return (
        f"Read {control_doc} if it exists (workspace context). Follow the rules set in that doc strictly. "
        f"Do not infer or repeat old tasks from prior chats. Complete the first available TODO task in {control_doc} "
        f"and update its status and evidence. If no task to do in {control_doc} reply with HEARTBEAT_OK and include your agent ID."
    )


def build_state(
    *,
    workspace_root: Path,
    max_depth: int,
    profile: Optional[str],
    dev: bool,
) -> Dict[str, Any]:
    errors: List[str] = []
    agents_cfg: Optional[Dict[str, Any]] = None
    try:
        agents_cfg = get_agents_config(profile, dev)
    except Exception as exc:
        errors.append(f"OpenClaw config error: {exc}")

    projects = scan_projects(workspace_root, max_depth=max_depth)
    project_map = {normalize_workspace_path(p["path"]): p for p in projects}
    for p in projects:
        p["agents"] = []

    defaults = (agents_cfg or {}).get("defaults") or {}
    default_heartbeat = defaults.get("heartbeat") or {}

    agents: List[Dict[str, Any]] = []
    for entry in (agents_cfg or {}).get("list") or []:
        agent_id = entry.get("id") or ""
        if not agent_id:
            continue
        workspace = entry.get("workspace") or defaults.get("workspace") or ""
        model = entry.get("model") or defaults.get("model") or ""
        heartbeat = entry.get("heartbeat") or {}
        hb_every = heartbeat.get("every") or default_heartbeat.get("every") or ""
        hb_prompt = heartbeat.get("prompt") or default_heartbeat.get("prompt") or ""

        agent_info = {
            "id": agent_id,
            "workspace": workspace,
            "model": model,
            "model_source": "agent" if entry.get("model") else ("default" if defaults.get("model") else "unset"),
            "heartbeat_every": hb_every,
            "heartbeat_prompt": hb_prompt,
            "heartbeat_source": "agent" if entry.get("heartbeat") else ("default" if default_heartbeat else "unset"),
        }

        normalized_ws = normalize_workspace_path(workspace) if workspace else ""
        project = project_map.get(normalized_ws)
        if project:
            agent_info["project_path"] = project["path"]
            project["agents"].append(agent_id)
        else:
            agent_info["project_path"] = ""
        agents.append(agent_info)

    return {
        "workspace_root": str(workspace_root),
        "projects": projects,
        "agents": agents,
        "defaults": {
            "workspace": defaults.get("workspace") or "",
            "model": defaults.get("model") or "",
            "heartbeat_every": default_heartbeat.get("every") or "",
            "heartbeat_prompt": default_heartbeat.get("prompt") or "",
        },
        "errors": errors,
        "timestamp": int(time.time()),
    }


class GuiHandler(BaseHTTPRequestHandler):
    server_version = "OpenClawProjectsGUI/0.1"

    def log_message(self, format: str, *args: Any) -> None:
        return

    def _send(self, code: int, body: bytes, content_type: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self._send(code, body, "application/json; charset=utf-8")

    def _read_json(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        if path == "/" or path == "/index.html":
            index = self.server.assets_dir / "index.html"
            body = index.read_bytes()
            self._send(200, body, "text/html; charset=utf-8")
            return
        if path == "/styles.css":
            body = (self.server.assets_dir / "styles.css").read_bytes()
            self._send(200, body, "text/css; charset=utf-8")
            return
        if path == "/app.js":
            body = (self.server.assets_dir / "app.js").read_bytes()
            self._send(200, body, "application/javascript; charset=utf-8")
            return
        if path == "/api/state":
            payload = build_state(
                workspace_root=self.server.workspace_root,
                max_depth=self.server.max_depth,
                profile=self.server.profile,
                dev=self.server.dev,
            )
            self._send_json(200, payload)
            return
        self._send(404, b"Not Found", "text/plain; charset=utf-8")

    def do_POST(self) -> None:
        parsed = urlparse(self.path)
        path = parsed.path
        try:
            payload = self._read_json()
        except Exception as exc:
            self._send_json(400, {"error": f"Invalid JSON: {exc}"})
            return

        if path == "/api/agents/update":
            self._handle_agent_update(payload)
            return
        if path == "/api/agents/create":
            self._handle_agent_create(payload)
            return
        self._send(404, b"Not Found", "text/plain; charset=utf-8")

    def _handle_agent_update(self, payload: Dict[str, Any]) -> None:
        agent_id = (payload.get("agent_id") or "").strip()
        updates = payload.get("updates") or {}
        preserve_main = payload.get("preserve_main", True)
        if not agent_id:
            self._send_json(400, {"error": "agent_id is required"})
            return

        try:
            agents_cfg = get_agents_config(self.server.profile, self.server.dev)
            idx = find_agent_index(agents_cfg, agent_id)
            if idx is None:
                self._send_json(404, {"error": f"Agent not found: {agent_id}"})
                return

            model = updates.get("model")
            if model is not None:
                if model == "":
                    unset_config_value(f"agents.list[{idx}].model", self.server.profile, self.server.dev)
                else:
                    set_config_value(f"agents.list[{idx}].model", model, self.server.profile, self.server.dev)

            hb_every = updates.get("heartbeat_every")
            if hb_every is not None:
                if hb_every == "":
                    unset_config_value(
                        f"agents.list[{idx}].heartbeat.every", self.server.profile, self.server.dev
                    )
                else:
                    set_config_value(
                        f"agents.list[{idx}].heartbeat.every", hb_every, self.server.profile, self.server.dev
                    )

            hb_prompt = updates.get("heartbeat_prompt")
            if hb_prompt is not None:
                if hb_prompt == "":
                    unset_config_value(
                        f"agents.list[{idx}].heartbeat.prompt", self.server.profile, self.server.dev
                    )
                else:
                    set_config_value(
                        f"agents.list[{idx}].heartbeat.prompt", hb_prompt, self.server.profile, self.server.dev
                    )

            if preserve_main:
                maybe_preserve_main_heartbeat(self.server.profile, self.server.dev)
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})
            return

        payload = build_state(
            workspace_root=self.server.workspace_root,
            max_depth=self.server.max_depth,
            profile=self.server.profile,
            dev=self.server.dev,
        )
        self._send_json(200, payload)

    def _handle_agent_create(self, payload: Dict[str, Any]) -> None:
        project_dir = (payload.get("project_dir") or "").strip()
        if not project_dir:
            self._send_json(400, {"error": "project_dir is required"})
            return
        project_path = Path(project_dir).resolve()

        control_doc = (payload.get("control_doc") or PROJECT_DOC_NAME).strip() or PROJECT_DOC_NAME
        agent_id = (payload.get("agent_id") or "").strip()
        prefix = (payload.get("prefix") or "").strip()
        count = int(payload.get("count") or 1)
        model = (payload.get("model") or "").strip() or None
        binds = payload.get("binds") or []
        hb_every = (payload.get("heartbeat_every") or "").strip() or None
        hb_prompt = (payload.get("heartbeat_prompt") or "").strip() or None
        preserve_main = payload.get("preserve_main", True)

        try:
            if agent_id:
                agent_ids = [normalize_agent_id(agent_id)]
            else:
                if not prefix:
                    prefix = normalize_agent_id(project_path.name)
                agent_ids = make_agent_ids(prefix, max(1, count))

            agent_ids, collisions = resolve_agent_ids(
                agent_ids, project_path, self.server.profile, self.server.dev
            )
            for raw, resolved in collisions.items():
                sys.stderr.write(f"[warn] id collision: {raw} -> {resolved}\n")

            for aid in agent_ids:
                ensure_agent_exists(aid, project_path, model, binds, self.server.profile, self.server.dev)
                ensure_agent_workspace_and_model(
                    aid,
                    workspace=project_path,
                    model=model,
                    profile=self.server.profile,
                    dev=self.server.dev,
                )
                configure_agent_heartbeat(
                    aid,
                    control_doc=control_doc,
                    every=hb_every,
                    prompt=hb_prompt,
                    profile=self.server.profile,
                    dev=self.server.dev,
                )

            if preserve_main:
                maybe_preserve_main_heartbeat(self.server.profile, self.server.dev)
        except Exception as exc:
            self._send_json(500, {"error": str(exc)})
            return

        payload = build_state(
            workspace_root=self.server.workspace_root,
            max_depth=self.server.max_depth,
            profile=self.server.profile,
            dev=self.server.dev,
        )
        self._send_json(200, payload)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1", help="Bind host (default: 127.0.0.1)")
    ap.add_argument("--port", type=int, default=8765, help="Bind port (default: 8765)")
    ap.add_argument("--workspace", default=None, help="Workspace root to scan (default: OpenClaw workspace)")
    ap.add_argument("--scan-depth", type=int, default=3, help="Max folder depth to scan (default: 3)")
    ap.add_argument("--open", action="store_true", help="Open the GUI in a browser on start")
    ap.add_argument("--openclaw-profile", default=None, help="OpenClaw profile name (optional)")
    ap.add_argument("--openclaw-dev", action="store_true", help="Use OpenClaw --dev profile (isolated state)")
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    agents_cfg: Optional[Dict[str, Any]] = None
    if not args.workspace:
        try:
            agents_cfg = get_agents_config(args.openclaw_profile, args.openclaw_dev)
        except Exception:
            agents_cfg = None
    workspace_root = Path(args.workspace) if args.workspace else default_workspace_root(
        args.openclaw_profile, args.openclaw_dev, agents_cfg
    )

    server = ThreadingHTTPServer((args.host, args.port), GuiHandler)
    server.assets_dir = Path(__file__).resolve().parents[1] / "assets"
    server.workspace_root = workspace_root
    server.max_depth = max(1, int(args.scan_depth))
    server.profile = args.openclaw_profile
    server.dev = bool(args.openclaw_dev)

    url = f"http://{args.host}:{args.port}/"
    print(f"Cortex GOV Projects GUI running at {url}")
    print(f"Workspace root: {server.workspace_root}")
    if args.open:
        try:
            webbrowser.open(url)
        except Exception:
            pass
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
