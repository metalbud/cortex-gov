# Cortex GOV — Autonomous Agent Quickstart

This repo runs on a **document-governed autonomy model**.

If you're another OpenClaw agent (or human operator), this is the shortest path to running it correctly.

## The catalyst that made this autonomous
Autonomy became reliable when execution switched from ad-hoc behavior to:

1. **Strict state machine**: `TODO -> IN_PROGRESS -> VERIFY -> DONE`
2. **Heartbeat loop**: agent repeatedly reads control docs and executes
3. **Evidence-gated completion**: no `DONE` without proof
4. **Doc-as-control-surface**: state lives in files, not hidden memory

---

## Core control files
- `HEARTBEAT.md` → runtime instructions and status summary
- `PROJECT.md` → verified execution log / completed work history
- `PROJECT_IDEAS.md` → active in-progress + TODO initiatives

If any required control file is missing, treat that as a blocker and report it.

---

## Required operating loop (every heartbeat)
1. Read `HEARTBEAT.md`
2. Read `PROJECT.md` and `PROJECT_IDEAS.md`
3. Pick highest-priority unblocked task per governance rules
4. Execute one meaningful increment
5. Capture evidence (files, commands, outputs, notes)
6. Update task status and docs
7. Report blockers with a concrete next action

---

## Governance rules (non-negotiable)
- Do not skip states.
- Do not mark `DONE` directly from `IN_PROGRESS`.
- `VERIFY` requires explicit evidence.
- Keep work auditable and reproducible.

---

## Evidence standard
Each task should include:
- Work checklist
- Acceptance criteria
- Verification steps
- Verification evidence:
  - file paths
  - commands/output
  - notes

No evidence = no completion.

---

## Internal vs shared files
- Internal planning docs (like `PROJECT_IDEAS.md`) may be gitignored depending on sharing policy.
- Public repo content should focus on runnable skill/runtime assets.

---

## Full runbook
For the extended version, see:

`docs/AUTONOMOUS_AGENT_RUNBOOK.md`

## Token optimization
To reduce governance token overhead while keeping verification strong, use:

`docs/LEAN_EVIDENCE_STANDARD.md`

---

## Philosophy
Human defines intent and constraints.
Agent executes within governance.
Progress must be provable.

**No proof, no progress.**
