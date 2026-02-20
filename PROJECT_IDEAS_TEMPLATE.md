# PROJECT_IDEAS.md (Template)

<!--
This file is the ACTIVE initiative queue for autonomous agents.
Use it for in-progress and upcoming initiatives that are not yet fully verified in PROJECT.md.

How it fits:
- HEARTBEAT.md tells agents to read this file + PROJECT.md
- PROJECT_IDEAS.md holds TODO/IN_PROGRESS initiative tasks
- PROJECT.md is the validated execution ledger (VERIFY/DONE evidence)

Recommended workflow:
1) Add new initiative here as TODO
2) Move to IN_PROGRESS when work starts
3) When evidence is complete, summarize and move final verified record to PROJECT.md
4) Keep this file lean and current
-->

## Context
<!-- Brief business/product context so agents make aligned decisions -->
- Parent brand/site:
- Primary products/apps:
- Current strategic focus:

## Governance Workflow
All work follows: `TODO -> IN_PROGRESS -> VERIFY -> DONE`

---

<!--
INITIATIVE TEMPLATE (copy/paste this block)
Keep IDs stable (e.g., I017, I018...).
Priorities: P0 (critical), P1 (important), P2 (nice-to-have)
-->

## I000: <Initiative Title>
Epic: <Epic Name>
Status: TODO
Priority: P1
Owner: agent

Governance Flow:
- TODO -> IN_PROGRESS (start date)

Work:
- [ ] <Concrete deliverable 1>
- [ ] <Concrete deliverable 2>
- [ ] <Concrete deliverable 3>

Owner Direction (<YYYY-MM-DD>):
- <Priority guidance from owner>
- <Constraints/preferences>

Acceptance Criteria:
- [ ] <Outcome-based criterion 1>
- [ ] <Outcome-based criterion 2>
- [ ] <Outcome-based criterion 3>

Verification Evidence:
- File paths:
  - <path/to/output-1>
  - <path/to/output-2>
- Commands/output:
  - <command run>
  - <key output>
- Notes:
  - <important implementation/validation notes>

---

## Operating Note for Cron/Heartbeat Agents
During scheduled checks, agents should:
1. Pick highest-priority TODO task not blocked.
2. Move status through governance stages with evidence.
3. Report blockers with concrete next action.
4. If no priority work exists, run incubation/backlog routine.
5. Avoid creating duplicate tasks unless explicitly requested.
