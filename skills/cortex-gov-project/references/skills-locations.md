# Skills locations and precedence

OpenClaw loads skills from:

1) Workspace skills: <workspace>/skills (highest precedence)
2) Managed/local skills: ~/.openclaw/skills
3) Bundled skills: shipped with OpenClaw (lowest precedence)

If a skill name conflicts, workspace wins.

Multi-agent setups:
- Each agent has its own workspace. Put per-agent skills in <workspace>/skills.
- Shared skills can live in ~/.openclaw/skills.
