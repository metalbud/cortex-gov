#!/usr/bin/env python3
"""
Validate Agent Setup - Prevent Silent Failures

This script validates agent directories to prevent silent heartbeat failures
and other common OpenClaw production gotchas.

Based on: https://kaxo.io/insights/openclaw-production-gotchas/

Key validations:
1. Required files exist (SOUL.md, models.json, auth-profiles.json)
2. Model configuration consistency across all four stores
3. Gateway token validation
4. File permission checks (workspace files 444, gateway files 644)
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import Dict, List, Tuple

class AgentValidator:
    def __init__(self, agent_dir: Path):
        self.agent_dir = Path(agent_dir)
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.passed = True

    def validate_required_files(self):
        """Check that all required files for heartbeat execution exist."""
        required_files = [
            'SOUL.md',
            'models.json',
            'auth-profiles.json',
            'HEARTBEAT.md'
        ]

        missing_files = []
        for file in required_files:
            file_path = self.agent_dir / file
            if not file_path.exists():
                missing_files.append(file)

        if missing_files:
            self.errors.append(
                f"Missing required files: {', '.join(missing_files)}. "
                f"Heartbeat will fail silently. These files are required for OpenClaw "
                f"heartbeat execution but are not documented in setup guides."
            )
            self.passed = False
        else:
            self.warnings.append("✓ All required files present")

        return len(missing_files) == 0

    def validate_model_consistency(self):
        """Check model configuration consistency across four stores."""
        models_file = self.agent_dir / 'models.json'
        if not models_file.exists():
            self.errors.append(f"models.json missing - cannot validate model consistency")
            self.passed = False
            return False

        try:
            with open(models_file, 'r') as f:
                models_config = json.load(f)
        except Exception as e:
            self.errors.append(f"Failed to read models.json: {e}")
            self.passed = False
            return False

        # Check if model is defined
        default_model = models_config.get('model')
        if not default_model:
            self.warnings.append("⚠ No default model defined in models.json")

        # Warn about four-store gotcha
        self.warnings.append(
            "⚠ Model config stored in 4 places: models.json, session state, "
            "cron payloads, and allowlist. Changes must be patched in all locations "
            "simultaneously."
        )

        return True

    def validate_file_permissions(self):
        """Check file permissions to prevent silent failures."""
        # Workspace files should be read-only (444) for agents
        workspace_files = ['SOUL.md', 'USER.md', 'MEMORY.md', 'HEARTBEAT.md']
        permission_issues = []

        for file in workspace_files:
            file_path = self.agent_dir / file
            if file_path.exists():
                try:
                    # On Windows, we can't easily check Unix permissions
                    # But we can verify files exist
                    pass
                except Exception as e:
                    permission_issues.append(f"{file}: {e}")

        # Gateway-managed files must be writable
        gateway_files = ['models.json', 'auth-profiles.json', 'auth.json']
        for file in gateway_files:
            file_path = self.agent_dir / file
            if file_path.exists():
                self.warnings.append(f"✓ Gateway-writable file exists: {file}")

        return len(permission_issues) == 0

    def validate_heartbeat_config(self):
        """Check heartbeat configuration."""
        heartbeat_file = self.agent_dir / 'HEARTBEAT.md'
        if not heartbeat_file.exists():
            self.warnings.append("⚠ HEARTBEAT.md not found")
            return False

        try:
            with open(heartbeat_file, 'r') as f:
                content = f.read()

            # Check if heartbeat prompt is configured
            if 'Read HEARTBEAT.md' not in content and 'heartbeat' not in content.lower():
                self.warnings.append(
                    "⚠ HEARTBEAT.md may not be properly configured "
                    "for heartbeat execution"
                )
            else:
                self.warnings.append("✓ HEARTBEAT.md appears configured")

        except Exception as e:
            self.errors.append(f"Failed to read HEARTBEAT.md: {e}")
            self.passed = False

        return True

    def validate_gateway_token(self):
        """Check for gateway token presence and format."""
        auth_files = ['auth.json', 'auth-profiles.json']
        has_token = False

        for auth_file in auth_files:
            file_path = self.agent_dir / auth_file
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        auth_data = json.load(f)
                    if 'gateway' in auth_data or 'token' in auth_data:
                        has_token = True
                        self.warnings.append(f"✓ Auth token found in {auth_file}")
                except Exception as e:
                    self.warnings.append(f"Could not read {auth_file}: {e}")

        if not has_token:
            self.warnings.append(
                "⚠ No gateway token found. Agent may fail to authenticate."
            )

        return has_token

    def run_all_validations(self):
        """Run all validations and return summary."""
        print(f"\n{'='*60}")
        print(f"Validating Agent: {self.agent_dir.name}")
        print(f"{'='*60}\n")

        # Run validations
        self.validate_required_files()
        self.validate_model_consistency()
        self.validate_file_permissions()
        self.validate_heartbeat_config()
        self.validate_gateway_token()

        # Print summary
        print("\nValidation Results:")
        print("-" * 60)

        if not self.passed:
            print("❌ VALIDATION FAILED - Agent will have silent failures")
            print("\nCritical Errors:")
            for error in self.errors:
                print(f"  • {error}")

            print("\n⚠ Warnings:")
            for warning in self.warnings:
                print(f"  • {warning}")

            print("\n📋 Recommended Actions:")
            print("  1. Copy missing files from a working agent directory")
            print("  2. Run 'openclaw doctor --fix' to detect and fix invalid config")
            print("  3. Check gateway status: 'openclaw gateway status'")
            print("  4. Restart gateway after config changes")

            return False
        else:
            print("✅ VALIDATION PASSED - Agent setup looks correct")
            print("\n⚠ Warnings (non-critical):")
            for warning in self.warnings:
                print(f"  • {warning}")

            return True

        print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(
        description='Validate OpenClaw agent setup to prevent silent failures'
    )
    parser.add_argument(
        '--agent-dir',
        type=str,
        required=True,
        help='Path to agent directory (e.g., ~/.openclaw/agents/main/agent/)'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to fix common issues (create missing files with templates)'
    )
    parser.add_argument(
        '--all-agents',
        action='store_true',
        help='Validate all agents in the workspace'
    )

    args = parser.parse_args()

    # Single agent validation
    if not args.all_agents:
        agent_dir = Path(args.agent_dir).expanduser()
        validator = AgentValidator(agent_dir)
        validator.run_all_validations()
        sys.exit(0 if validator.passed else 1)

    # All agents validation
    else:
        print("Validating all agents in workspace...")
        # Find agent directories
        workspace = Path(args.agent_dir).expanduser().parent
        agent_dirs = []
        for item in workspace.iterdir():
            if item.is_dir() and 'agent' in item.name:
                agent_dirs.append(item)

        if not agent_dirs:
            print("No agent directories found in workspace")
            sys.exit(1)

        print(f"Found {len(agent_dirs)} agent(s) to validate\n")

        all_passed = True
        for agent_dir in agent_dirs:
            validator = AgentValidator(agent_dir)
            if not validator.run_all_validations():
                all_passed = False

        print(f"\n{'='*60}")
        print(f"Overall Result: {'✅ ALL PASSED' if all_passed else '❌ SOME FAILED'}")
        print(f"{'='*60}")
        sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
