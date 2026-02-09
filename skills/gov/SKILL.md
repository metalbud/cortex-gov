---
name: gov
description: Short Cortex GOV slash command to bootstrap a governed project folder and spawn OpenClaw agents that follow its PROJECT.md.
---

# GOV (Cortex GOV Bootstrap)

## What this skill does

This is a **short, easy-to-type** alias skill intended to be used as a slash command (e.g. `/gov ...`).

It bootstraps a Cortex GOV project folder (control doc + heartbeat checklist) and/or spawns OpenClaw isolated agents whose heartbeat prompt is directed to the project's control document (default: `PROJECT.md`).

This skill depends on the `cortex-gov-project` skill scripts in this repo.

## How to use (interpret user input)

Treat `/gov` as the **entrypoint** for creating a governed project.

Parse the user's `/gov ...` args as one of:

### 1) Create a new governed project (default)

If the user runs:
- `/gov`
- `/gov <project-name>`

Then:

1. If `<project-name>` is missing, ask for it (keep it short).
2. Ask for a 1-2 sentence success summary (vague is fine).
3. Optional: ask for 0-5 extra constraints (bullets).
4. Run the non-interactive script (this writes the schema + spawns a project agent):

`python "{baseDir}/../cortex-gov-project/scripts/cortex_gov_gov.py" "<project-name>" --idea "<summary>" --template auto --agent-count 1`

If constraints were provided, append them as repeatable flags:

`--constraint "<constraint>"`

Result:
- Creates `./projects/<project_slug>/PROJECT.md`
- Spawns an OpenClaw isolated agent with `workspace=./projects/<project_slug>/`
- Sets that agent’s `heartbeat.prompt` to read the project’s `PROJECT.md`

### 2) Spawn agents for an existing project folder

If the user starts args with `spawn`:

`python "{baseDir}/../cortex-gov-project/scripts/cortex_gov_spawn_agents.py" --project-dir "<projectDir>" --control-doc "PROJECT.md" --prefix "<shortPrefix>" --count <n>`

### 3) Help

If args are `help` or unclear, ask only what you need:
- project name or project folder path
- desired agent count (default: 1)
- any constraints you want encoded

## Rules

- Treat the control doc as the single source of truth.
- Never mark `DONE` without verification evidence.
- Keep commands short and paths local to the project folder.
