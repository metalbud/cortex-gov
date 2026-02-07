---
name: cortex-gov-project
description: Create Cortex GOV project control files (PROJECT.md + HEARTBEAT.md) from a user’s idea and configure OpenClaw heartbeat for multi-agent governance. Use when a user wants a structured, evidence-based project plan, strict task status workflow (TODO→IN_PROGRESS→VERIFY→DONE), or asks to “turn my idea into a governed project.”
---

# Cortex GOV Project Creator

## Overview

Generate a Cortex GOV project control document and OpenClaw-compatible HEARTBEAT.md from a user’s project idea, then place them in the workspace `/skills` and root for immediate agent execution.

## Workflow (follow in order)

### 1) Confirm project inputs
Collect:
- Project name
- One-paragraph success summary
- Constraints (3–8 bullets)
- Epics (key + outcome bullets)
- Ordered tasks (H001… with acceptance + verification)

If the user is vague, propose a draft and ask for approval.

### 2) Generate project config JSON
Create `project_config.json` in the target project folder. Use the wizard-compatible schema.

### 3) Create project files with the wizard
Use the bundled wizard (from the cortex-gov repo) to generate:
- `PROJECT.md`
- `HEARTBEAT.md`

Use the script in `scripts/cortex_gov_create.py` (preferred) which wraps the wizard and places outputs in the workspace.

### 4) Place files for OpenClaw
OpenClaw reads workspace skills and heartbeat files from the workspace root. Ensure:
- `PROJECT.md` is in the workspace root
- `HEARTBEAT.md` is in the workspace root

If the project lives in a subfolder, also keep a copy there.

### 5) Ensure multi-agent heartbeat format
Heartbeat must include agent ID guidance, and workspace path:

```
-Agent: Read PROJECT.md if it exists in workspace context. Follow the rules set in that doc strictly. Do not infer or repeat old tasks from prior chats. Complete the first available TODO task and update your status, then post a short summary of changes in #dev (discord) with your agent ID.
-If no task to do in PROJECT.md reply with HEARTBEAT OK and include your agent ID
-Workspace: <absolute workspace path>
```

### 6) Record evidence
Update the verification evidence in `PROJECT.md` when tasks are completed.

## Scripts

Use the scripts below:
- `scripts/cortex_gov_create.py` — create PROJECT.md + HEARTBEAT.md
- `scripts/cortex_gov_validate.py` — validate evidence; auto-advance VERIFY → DONE

### Auto-verify toggle

`cortex_gov_validate.py` accepts `--auto-verify true|false`.
- **true (default):** auto-advance VERIFY → DONE
- **false:** validate but stop for manual approval

## References

- `references/skills-locations.md` (skills precedence + workspace rules)
- `references/heartbeat-format.md` (multi-agent heartbeat format)

## Notes

- Never mark DONE without verification evidence.
- Do not start a new task if one is IN_PROGRESS or VERIFY.
- Keep PROJECT.md as the single source of truth.
