# Cortex GOV Autonomous Agent Runbook

## Purpose
This document explains how this workspace achieved reliable autonomous execution, and how another OpenClaw agent can operate the same way.

---

## What catalyzed autonomy in this system
The key catalyst was **switching from ad-hoc agent behavior to document-governed execution**:

1. **A strict governance model** (`TODO -> IN_PROGRESS -> VERIFY -> DONE`) became mandatory.
2. **Heartbeat-driven execution** was wired in so the agent repeatedly checks control docs and advances work.
3. **Evidence requirements** were enforced before completion (`DONE` needs proof).
4. **Centralized control documents** (`PROJECT.md`, `PROJECT_IDEAS.md`, `HEARTBEAT.md`) became the source of truth.

In short: autonomy started working once the system removed ambiguity and made progress auditable.

---

## Core operating model

### 1) Control surface
- `HEARTBEAT.md` = scheduler instructions + current operating status
- `PROJECT.md` = validated/completed execution log + governance history
- `PROJECT_IDEAS.md` = active pipeline for in-progress/todo initiative work

### 2) State machine (non-negotiable)
`TODO -> IN_PROGRESS -> VERIFY -> DONE`

Rules:
- No skipping states
- No `DONE` without verification evidence
- If blocked, report blocker + concrete next action

### 3) Task selection policy
On each heartbeat:
1. Read `HEARTBEAT.md`
2. Read `PROJECT.md` + `PROJECT_IDEAS.md`
3. Select highest-priority unblocked task per governance note
4. Execute work
5. Capture evidence
6. Update task status and heartbeat summary

---

## Why this works
- **Deterministic loop**: every cycle follows the same steps
- **No hidden memory dependence**: docs hold state
- **Auditability**: every completion contains evidence paths/commands/notes
- **Human override remains intact**: priorities and constraints stay human-directed

---

## Implementation pattern for another agent

### Step A — Bootstrap
1. Create/confirm these files exist:
   - `HEARTBEAT.md`
   - `PROJECT.md`
   - `PROJECT_IDEAS.md`
2. Put explicit governance language in heartbeat:
   - “check docs, execute via TODO->IN_PROGRESS->VERIFY->DONE”

### Step B — Enforce behavior
For each task section, require:
- Work checklist
- Acceptance criteria
- Verification steps
- Verification evidence (file paths, commands, notes)

### Step C — Operate in cycles
On every heartbeat:
- detect next actionable item
- execute one meaningful increment
- update docs in-place
- report blockers only when real

### Step D — Keep boundaries clean
- Internal-only docs should be gitignored if needed (example: `PROJECT_IDEAS.md`)
- Share only skill/runtime artifacts externally

---

## Suggested checklist for autonomous turns
- [ ] Read heartbeat instructions
- [ ] Read control docs
- [ ] Pick next governed task
- [ ] Execute scoped work
- [ ] Verify with evidence
- [ ] Update statuses and notes
- [ ] Emit concise status update

---

## Notes for OpenClaw agents
- Treat docs as system state, not conversation memory.
- If required files are missing, flag immediately.
- Prefer incremental verified progress over broad unverified claims.
- Keep `HEARTBEAT.md` current so future sessions resume correctly.

---

## File reference
- `cortex-gov/README.md` (governance philosophy and model)
- `HEARTBEAT.md` (runtime instruction loop)
- `cortex-gov/PROJECT.md` (verified execution record)
- `cortex-gov/PROJECT_IDEAS.md` (active initiative queue)
