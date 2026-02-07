# Cortex GOV Wizard (Heartbeat Compatible)

This folder contains a cross-platform CLI wizard that helps a human create a Cortex GOV project control document and an OpenClaw-compatible `HEARTBEAT.md`.

## What it does
- Prompts a human for project name, summary, constraints
- Collects epics (outcome buckets)
- Collects an ordered task list
- Writes a deterministic Markdown control document compatible with Cortex GOV rules
- Writes `HEARTBEAT.md` instructions that direct your Heartbeat system to the control doc

## Outputs
- A control document (default: `PROJECT.md`) — the single source of truth the agent must read/write
- `HEARTBEAT.md` (default) — a short instruction file for OpenClaw Heartbeat

## Requirements
- Python 3.9+ recommended (works on Windows/macOS/Linux)

## Quick start
From this folder:

```bash
python cortex_gov_wizard.py
```

In interactive mode, the wizard will prompt for an **easy-to-type** control document filename if `--out` is not provided.

## Point Heartbeat at a different control document name
If you name your control doc something else (e.g., `CONTROL_DOC.md`), pass `--control-doc`:

```bash
python cortex_gov_wizard.py --out CONTROL_DOC.md --control-doc CONTROL_DOC.md
```

## Non-interactive mode
You can provide a JSON config (useful for CI or generating multiple projects):

```bash
python cortex_gov_wizard.py --non-interactive --config project_config.json --out PROJECT.md --heartbeat-out HEARTBEAT.md
```

## HEARTBEAT.md format
The wizard writes `HEARTBEAT.md` in this format:

-Check <CONTROL_DOC> read and follow the rules set in that doc complete a task and update your status, then post a short summary of changes in #dev (discord)
-If no task to do <CONTROL_DOC> reply with HEARTBEAT OK

## Tip
Keep evidence artifacts in `/artifacts/` and link them from each task’s "Verification Evidence" section.

