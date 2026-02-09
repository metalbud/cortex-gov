---
name: cortex-gov-gui
description: Launch a local GUI to manage Cortex GOV projects and their agents. Use when you need a dashboard that scans the main OpenClaw workspace for PROJECT.md folders, lists their agents, and lets you spawn agents or edit model/heartbeat settings via the OpenClaw CLI.
---

# Cortex GOV Projects GUI

## Overview

Start a local web dashboard that discovers Cortex GOV PROJECT.md folders in the main OpenClaw workspace and lets you manage the agents tied to those project workspaces.

## Quick Start

Run the GUI server (prints a local URL):

```bash
python "skills/cortex-gov-gui/scripts/openclaw_projects_gui.py" --open
```

Slash command usage:

`/cortex-gov-gui` (launches the GUI and shares the local URL)

## What This GUI Does

- Scans a workspace root for directories containing `PROJECT.md`
- Shows each Cortex GOV project's agents (matched by OpenClaw agent workspace)
- Lets you update per-agent model, heartbeat interval, and heartbeat prompt
- Lets you spawn new agents for a project workspace

## Common Operations

### Launch with a specific workspace root

```bash
python "skills/cortex-gov-gui/scripts/openclaw_projects_gui.py" --workspace "C:\path\to\workspace"
```

### Target a specific OpenClaw profile or dev config

```bash
python "skills/cortex-gov-gui/scripts/openclaw_projects_gui.py" --openclaw-profile dev
python "skills/cortex-gov-gui/scripts/openclaw_projects_gui.py" --openclaw-dev
```

### Control scan depth

```bash
python "skills/cortex-gov-gui/scripts/openclaw_projects_gui.py" --scan-depth 2
```

## Notes

- The GUI uses `openclaw config get/set/unset` and `openclaw agents add` under the hood. Ensure `openclaw` is on PATH.
- "Use defaults" clears per-agent overrides (uses `openclaw config unset`) so agents fall back to defaults.
- Heartbeat prompt defaults to a PROJECT.md-focused prompt unless you override it.
