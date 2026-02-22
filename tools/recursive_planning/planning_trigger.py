#!/usr/bin/env python3
"""
Planning Trigger for Recursive Planning Workflow

Handles automatic and manual triggering of planning cycles.
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parents[2]
FALLBACK_LAST_CYCLE = datetime(2020, 1, 1, tzinfo=timezone.utc)


def resolve_workspace_path(raw_workspace: str = None) -> Path:
    if raw_workspace:
        return Path(raw_workspace).resolve()
    return BASE_DIR


def parse_utc_timestamp(raw_timestamp: str) -> datetime:
    value = (raw_timestamp or "").strip()
    if not value:
        return FALLBACK_LAST_CYCLE

    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return FALLBACK_LAST_CYCLE

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class PlanningTrigger:
    """Manages planning cycle triggers"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.artifacts_dir = workspace_path / "artifacts"
        self.planning_dir = self.artifacts_dir / "planning"
        self.planning_dir.mkdir(parents=True, exist_ok=True)
        
    def check_auto_trigger(self) -> bool:
        """Check if automatic planning trigger should be activated"""
        # Load last planning cycle timestamp
        last_cycle_file = self.planning_dir / "last-planning-cycle.json"
        
        # If no last cycle, trigger now
        if not last_cycle_file.exists():
            return True
            
        # Read last cycle
        try:
            with open(last_cycle_file, 'r', encoding='utf-8') as f:
                last_cycle = json.load(f)
        except (json.JSONDecodeError, OSError):
            return True

        last_time = parse_utc_timestamp(last_cycle.get("timestamp", ""))
        
        # Check if 24 hours have passed since last cycle
        time_diff = datetime.now(timezone.utc) - last_time
        return time_diff.total_seconds() >= 86400  # 24 hours
    
    def check_project_stagnation(self) -> bool:
        """Check for project stagnation patterns that should trigger planning"""
        pattern_data = self._load_pattern_analysis()
        patterns = pattern_data.get("patterns", [])

        # Check for stalled patterns from structured JSON analysis
        stalled_count = sum(1 for p in patterns if p.get("status") == "stalled")
        if stalled_count > 0:
            return True

        # Legacy markdown fallback: detect explicit "stalled" signals.
        if "stalled" in str(pattern_data.get("raw", "")).lower():
            return True

        # Check for task accumulation in TODO state
        todo_count = 0
        project_file = self.workspace_path / "PROJECT.md"
        if project_file.exists():
            content = project_file.read_text(encoding='utf-8')
            todo_count = content.count("Status: TODO")
            
        return todo_count > 2  # More than 2 TODO tasks

    def _load_pattern_analysis(self) -> Dict[str, Any]:
        pattern_json = self.artifacts_dir / "patterns" / "H009-pattern-analysis.json"
        if pattern_json.exists():
            try:
                with open(pattern_json, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
                data = raw_data if isinstance(raw_data, dict) else {}
                patterns = data.get("patterns", [])
                return {
                    "source": str(pattern_json),
                    "format": "json",
                    "patterns": patterns if isinstance(patterns, list) else [],
                    "raw": "",
                }
            except (json.JSONDecodeError, OSError):
                return {"source": str(pattern_json), "format": "json", "patterns": [], "raw": ""}

        legacy_paths = [
            self.artifacts_dir / "metrics" / "H009-pattern-analysis.md",
            self.artifacts_dir / "patterns" / "H009-pattern-analysis.md",
        ]
        for legacy_file in legacy_paths:
            if legacy_file.exists():
                return {
                    "source": str(legacy_file),
                    "format": "markdown",
                    "patterns": [],
                    "raw": legacy_file.read_text(encoding='utf-8'),
                }

        return {"source": None, "format": None, "patterns": [], "raw": ""}
    
    def trigger_manual_planning(self) -> Dict[str, Any]:
        """Trigger manual planning cycle"""
        return {
            "trigger_type": "manual",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": "Manual trigger requested",
            "triggered": True
        }
    
    def trigger_auto_planning(self) -> Dict[str, Any]:
        """Trigger automatic planning cycle"""
        trigger_reason = ""
        
        if self.check_project_stagnation():
            trigger_reason = "Project stagnation detected"
        else:
            trigger_reason = "Scheduled 24-hour interval"
            
        return {
            "trigger_type": "automatic",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "reason": trigger_reason,
            "triggered": True
        }
    
    def save_trigger_info(self, trigger_info: Dict[str, Any]):
        """Save trigger information for tracking"""
        trigger_file = self.planning_dir / "last-trigger.json"
        with open(trigger_file, 'w', encoding='utf-8') as f:
            json.dump(trigger_info, f, indent=2)
            
        # Also update last planning cycle if triggered
        if trigger_info.get("triggered"):
            cycle_file = self.planning_dir / "last-planning-cycle.json"
            with open(cycle_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": trigger_info["timestamp"],
                    "trigger_type": trigger_info["trigger_type"],
                    "reason": trigger_info["reason"]
                }, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Planning Trigger for Recursive Planning")
    parser.add_argument("--check", action="store_true", help="Check if auto-trigger should activate")
    parser.add_argument("--manual", action="store_true", help="Trigger manual planning cycle")
    parser.add_argument("--auto", action="store_true", help="Trigger automatic planning cycle")
    parser.add_argument("--workspace", type=str, help="Path to cortex-gov workspace")
    
    args = parser.parse_args()
    
    workspace_path = resolve_workspace_path(args.workspace)
    trigger = PlanningTrigger(workspace_path)
    
    if args.check:
        should_trigger = trigger.check_auto_trigger() or trigger.check_project_stagnation()
        print(f"Auto-trigger should activate: {should_trigger}")
        
        if should_trigger:
            print("Trigger reasons:")
            if trigger.check_project_stagnation():
                print("- Project stagnation detected")
            if trigger.check_auto_trigger():
                print("- Scheduled 24-hour interval")
                
    elif args.manual:
        trigger_info = trigger.trigger_manual_planning()
        trigger.save_trigger_info(trigger_info)
        print(f"Manual planning triggered: {trigger_info['timestamp']}")
        
    elif args.auto:
        trigger_info = trigger.trigger_auto_planning()
        trigger.save_trigger_info(trigger_info)
        print(f"Automatic planning triggered: {trigger_info['timestamp']} ({trigger_info['reason']})")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
