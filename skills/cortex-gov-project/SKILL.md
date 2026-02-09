---
name: cortex-gov-project
description: Bootstrap Cortex GOV project control docs and spawn OpenClaw agents that follow a project folder’s control document (default: PROJECT.md) with evidence-based verification.
---

# Cortex GOV Project Creator

## Overview

Generate a Cortex GOV control document (default: `PROJECT.md`, but can be named) and an OpenClaw-compatible `HEARTBEAT.md` from a user’s project idea, then (optionally) spawn OpenClaw isolated agents whose workspace is the project folder and whose heartbeat prompt is directed to the control document.

If you want a short slash command, use the `gov` skill (`/gov ...`) which wraps these scripts.

## Workflow (follow in order)

### 1) Confirm project inputs
Collect:
- Project name
- One-paragraph success summary
- Constraints (3–8 bullets)
- Epics (key + outcome bullets)
- Ordered tasks (H001… with acceptance + verification)

If the user is vague, propose a draft and ask for approval.

### 2) Choose a project folder
Prefer a dedicated project folder (example): `./projects/<project_slug>/`.

### 3) Generate project config JSON
Create `project_config.json` in the project folder. Use the wizard-compatible schema.

### 4) Bootstrap the project folder + spawn agents (preferred)
Use the bootstrap script (end-to-end):

`python "{baseDir}/scripts/cortex_gov_bootstrap.py" --project-dir "<projectDir>" --config "<projectDir>/project_config.json" --prefix "<shortPrefix>" --count <n>`

This will:
- Write the control doc + `HEARTBEAT.md` into the project folder
- Spawn OpenClaw isolated agents with `workspace=<projectDir>`
- Configure per-agent heartbeat prompt to read the control doc directly (so it points at `PROJECT.md`, not `HEARTBEAT.md`)

### 5) Multi-agent heartbeat contract
If no task is available, reply with `HEARTBEAT_OK` (underscore). Do not use `HEARTBEAT OK`.

Heartbeat checklist format (optional, but recommended to keep around):

```
-Agent: Read <CONTROL_DOC> if it exists in workspace context. Follow the rules set in that doc strictly. Do not infer or repeat old tasks from prior chats. Complete the first available TODO task and update your status, then post a short summary of changes in #dev (discord) with your agent ID.
-If no task to do in <CONTROL_DOC> reply with HEARTBEAT_OK and include your agent ID
-Workspace: <absolute workspace path>
```

### 6) Record evidence
Update the verification evidence in the control doc when tasks are completed.

## Scripts

Use the scripts below:
- `scripts/cortex_gov_bootstrap.py` — create control doc + spawn project agents (preferred)
- `scripts/cortex_gov_spawn_agents.py` — spawn/configure agents for an existing project folder
- `scripts/cortex_gov_create.py` — create control doc + `HEARTBEAT.md` (prints the chosen control doc name; supports `--control-doc`)
- `scripts/cortex_gov_validate.py` — validate evidence; auto-advance VERIFY → DONE

### Auto-verify toggle

`cortex_gov_validate.py` accepts `--auto-verify true|false`.
- `true` (default): auto-advance VERIFY → DONE
- `false`: validate but stop for manual approval

## References

- `references/skills-locations.md` (skills precedence + workspace rules)
- `references/heartbeat-format.md` (multi-agent heartbeat format)

## Notes

- Never mark DONE without verification evidence.
- Do not start a new task if one is IN_PROGRESS or VERIFY.
- Keep the control doc as the single source of truth.
