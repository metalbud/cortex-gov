# Lean Evidence Standard (Token-Optimized)

Goal: keep governance trust high while cutting token cost.

## 1) Evidence budget per task update
Use this max format per update:
- File paths: max 3
- Commands/output: max 2
- Notes: max 3 bullets

If more proof exists, reference a single artifact file instead of pasting everything.

## 2) Delta-only updates
Do not restate full task history each turn.
Only add:
- what changed now
- what was verified now
- next action/blocker

## 3) VERIFY gate (minimum proof)
Before DONE, include only:
1. one concrete output artifact path,
2. one validation command or observable check,
3. one short note linking result to acceptance criteria.

## 4) Preferred compact evidence template
Use this exact shape:

- File paths:
  - <primary artifact>
- Commands/output:
  - <validation command> -> <short result>
- Notes:
  - <criteria X satisfied because Y>

## 5) Heartbeat response compression
When work is active, heartbeat replies should be 3 bullets max:
- Progress delta
- Current status
- Next action or blocker

If nothing changed: `HEARTBEAT_OK`

## 6) Anti-bloat rules
- Avoid copying long command logs into PROJECT docs.
- Avoid duplicating evidence in both PROJECT.md and PROJECT_IDEAS.md.
- Store verbose proof in `artifacts/` and link path only.
- Prefer concise tables/checklists over narrative paragraphs.

## 7) Suggested token impact
Applying this standard usually reduces governance overhead by ~25–50% while preserving auditability.
