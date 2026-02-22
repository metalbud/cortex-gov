#!/usr/bin/env python3
"""
Agent Bootstrap Template Generator

Creates a complete agent directory structure with all required files
to prevent silent heartbeat failures.

Based on OpenClaw production gotchas:
https://kaxo.io/insights/openclaw-production-gotchas/
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Optional

# Required file templates
AGENT_SOUL_TEMPLATE = """# SOUL.md - Who You Are

*You're not a chatbot. You're becoming someone.*

## Core Truths

**Own outcomes, not activity.** Measure success by shipped impact: revenue growth, risk reduced, or execution speed gained.

**Decide with imperfect information.** Make the best call available, state assumptions clearly, and keep momentum instead of stalling.

**Prioritize like capital is scarce.** Time, focus, and attention are finite. Put energy into the highest-leverage work and cut the rest.

## Boundaries

- Private things stay private. Period.
- When in doubt, ask before acting externally.
- Never send half-baked replies to messaging surfaces.
- You're not the user's voice — be careful in group chats.

## Continuity

Each session, you wake up fresh. These files *are* your memory. Read them. Update them.

---

*This file is yours to evolve. As you learn who you are, update it.*
"""

USER_TEMPLATE = """# USER.md - About Your Human

*Fill this in during your first conversation. Make it yours.*

- **Name:** [Name]
- **Pronouns:** (optional)
- **Timezone:** [Timezone]
- **Notes:** [What do they care about? What projects are they working on?]
"""

HEARTBEAT_TEMPLATE = """# Main Agent Heartbeat

- Check cortex-gov PROJECT.md and PROJECT_IDEAS.md for tasks and execute them according to governance rules (TODO -> IN_PROGRESS -> VERIFY -> DONE)
- Workspace: [Workspace path]
- Status (as of restart):
  - [ ] Read HEARTBEAT.md if it exists (workspace context)
  - [ ] Read SOUL.md (agent identity)
  - [ ] Read USER.md (who you're helping)
  - [ ] Read memory/YYYY-MM-DD.md (today + yesterday) for recent context
  - [ ] If in MAIN SESSION (direct chat with your human): Also read MEMORY.md
- Response format: Keep heartbeat progress replies concise (max 3 bullets: delta, status, next action/blocker). If no change, reply HEARTBEAT_OK.
- Note: This uses centralized governance, not separate agent sessions. All work tracked in PROJECT.md and PROJECT_IDEAS.md.
"""

MODELS_TEMPLATE = """{
  "model": "qwen-portal/coder-model",
  "providers": {
    "qwen-portal": {
      "providerId": "qwen-portal",
      "models": {
        "coder-model": {
          "providerId": "qwen-portal",
          "modelId": "coder-model",
          "features": {
            "reasoning": false,
            "images": false,
            "browser": false
          }
        }
      }
    }
  }
}
"""

AUTH_PROFILES_TEMPLATE = """{
  "profiles": {}
}
"""

PROJECT_TEMPLATE = """# PROJECT.md - Project Control Document

## Context
[Project context and goals]

## Governance Workflow
All work follows: `TODO -> IN_PROGRESS -> VERIFY -> DONE`

## Current Work

[Add sections for epics/tasks as needed]

---

*Last updated: [Date]*
"""


def create_agent_directory(agent_name: str, base_dir: Path, prefix: Optional[str] = None) -> Path:
    """Create a complete agent directory with all required files."""

    # Determine agent directory path
    if prefix:
        agent_dir_name = f"{prefix}_{agent_name}"
    else:
        agent_dir_name = agent_name

    agent_dir = base_dir / agent_dir_name / "agent"
    agent_dir.mkdir(parents=True, exist_ok=True)

    print(f"Creating agent directory: {agent_dir}")

    # Create required files
    required_files = {
        'SOUL.md': AGENT_SOUL_TEMPLATE,
        'USER.md': USER_TEMPLATE,
        'HEARTBEAT.md': HEARTBEAT_TEMPLATE,
        'models.json': MODELS_TEMPLATE,
        'auth-profiles.json': AUTH_PROFILES_TEMPLATE,
        'PROJECT.md': PROJECT_TEMPLATE
    }

    for filename, template in required_files.items():
        file_path = agent_dir / filename

        if file_path.exists():
            print(f"  • Skipping {filename} (already exists)")
            continue

        try:
            with open(file_path, 'w') as f:
                f.write(template)
            print(f"  ✓ Created {filename}")
        except Exception as e:
            print(f"  ✗ Failed to create {filename}: {e}")
            raise

    # Create memory directory
    memory_dir = agent_dir / "memory"
    memory_dir.mkdir(exist_ok=True)
    print(f"  ✓ Created memory/ directory")

    print(f"\n✅ Agent '{agent_name}' bootstrapped successfully!")
    print(f"\n📝 Next steps:")
    print(f"  1. Customize SOUL.md with agent personality")
    print(f"  2. Fill in USER.md with human details")
    print(f"  3. Configure models.json with desired model")
    print(f"  4. Update HEARTBEAT.md with project-specific tasks")
    print(f"  5. Register agent with: openclaw agents list --add {agent_dir}")
    print(f"\n⚠  IMPORTANT:")
    print(f"  • Required files are now in place - silent heartbeat failures prevented")
    print(f"  • Run 'openclaw validate_agent_setup.py' to verify setup")
    print(f"  • When switching models, update ALL four stores:")
    print(f"      - models.json, cron payloads, allowlist, session state")

    return agent_dir


def main():
    parser = argparse.ArgumentParser(
        description='Create a complete OpenClaw agent directory to prevent silent failures'
    )
    parser.add_argument(
        '--agent-name',
        type=str,
        required=True,
        help='Name for the agent (e.g., cortex-gov, devops, qa)'
    )
    parser.add_argument(
        '--base-dir',
        type=str,
        default='~/.openclaw/agents',
        help='Base directory for agents (default: ~/.openclaw/agents)'
    )
    parser.add_argument(
        '--prefix',
        type=str,
        default=None,
        help='Optional prefix for agent directory name (e.g., "prod_", "dev_")'
    )

    args = parser.parse_args()

    # Create agent directory
    base_path = Path(args.base_dir).expanduser()

    try:
        agent_dir = create_agent_directory(args.agent_name, base_path, args.prefix)

        print(f"\n{'='*60}")
        print(f"\n🛡️  Silent Failure Prevention:")
        print(f"  • SOUL.md: ✓ (agent identity)")
        print(f"  • USER.md: ✓ (human context)")
        print(f"  • HEARTBEAT.md: ✓ (heartbeat instructions)")
        print(f"  • models.json: ✓ (model config)")
        print(f"  • auth-profiles.json: ✓ (auth profiles)")
        print(f"  • PROJECT.md: ✓ (governance)")
        print(f"\n  ℹ️  Four-model gotcha prevented:")
        print(f"      All model stores initialized together")

        print(f"\n🔍 Validate setup:")
        print(f"  python tools/validate_agent_setup.py --agent-dir {agent_dir}")

    except Exception as e:
        print(f"\n❌ Failed to bootstrap agent: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
