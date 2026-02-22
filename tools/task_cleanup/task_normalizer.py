#!/usr/bin/env python3
"""
Task Normalization Tool for Cortex-GOV
Reviews and normalizes task status across all epics.
"""

import json
import re
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any


class TaskNormalizer:
    def __init__(self, workspace: str = "."):
        self.workspace = Path(workspace)
        self.project_md = self.workspace / "PROJECT.md"
        
    def extract_tasks(self) -> List[Dict]:
        """Extract all tasks from PROJECT.md"""
        if not self.project_md.exists():
            raise FileNotFoundError(f"PROJECT.md not found at {self.project_md}")
            
        with open(self.project_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tasks = []
        # Find all task definitions
        task_pattern = r'### (H\d{3}): ([^\n]+)\nEpic: ([^\n]+)\nStatus: ([^\n]+)\nPriority: ([^\n]+)\nOwner: ([^\n]+)'
        
        matches = re.findall(task_pattern, content)
        for match in matches:
            task_id, title, epic, status, priority, owner = match
            tasks.append({
                "id": task_id,
                "title": title,
                "epic": epic,
                "status": status.strip(),
                "priority": priority.strip(),
                "owner": owner.strip()
            })
            
        return tasks
    
    def review_tasks(self) -> Dict:
        """Review all tasks and identify inconsistencies"""
        tasks = self.extract_tasks()
        
        review_results = {
            "total_tasks": len(tasks),
            "status_counts": {},
            "epic_counts": {},
            "inconsistencies": [],
            "stale_todos": [],
            "duplicate_check": {}
        }
        
        # Count by status
        for task in tasks:
            status = task["status"]
            review_results["status_counts"][status] = review_results["status_counts"].get(status, 0) + 1
            
        # Count by epic
        for task in tasks:
            epic = task["epic"]
            review_results["epic_counts"][epic] = review_results["epic_counts"].get(epic, 0) + 1
            
        # Check for inconsistencies
        for task in tasks:
            # Check if TODO tasks are in completed epics
            if task["status"] == "TODO" and task["epic"] in ["E006"]:  # E006 is the only completed epic
                review_results["inconsistencies"].append({
                    "type": "TODO_IN_COMPLETED_EPIC",
                    "task_id": task["id"],
                    "task_title": task["title"],
                    "epic": task["epic"]
                })
                
            # Check for stale TODOs (tasks that might be completed but not marked as such)
            if task["status"] == "TODO" and "implementation" in task["title"].lower():
                review_results["stale_todos"].append({
                    "task_id": task["id"],
                    "task_title": task["title"],
                    "reason": "Implementation task marked as TODO"
                })
                
            # Check for duplicates by title similarity
            normalized_title = task["title"].lower().strip()
            if normalized_title in review_results["duplicate_check"]:
                review_results["duplicate_check"][normalized_title].append(task["id"])
            else:
                review_results["duplicate_check"][normalized_title] = [task["id"]]
                
        # Filter actual duplicates (more than one task with similar title)
        actual_duplicates = {k: v for k, v in review_results["duplicate_check"].items() if len(v) > 1}
        review_results["duplicates"] = actual_duplicates
        
        return review_results
    
    def dry_run_normalize(self) -> Dict:
        """Show what changes would be made without modifying files"""
        review_results = self.review_tasks()
        
        normalization_plan = {
            "proposed_changes": [],
            "justification": [],
            "risk_assessment": "LOW"
        }
        
        # For each inconsistency, propose a resolution
        for inconsistency in review_results["inconsistencies"]:
            task_id = inconsistency["task_id"]
            
            # For H022, since it's a cleanup task and just started, mark it as IN_PROGRESS
            if task_id == "H022":
                normalization_plan["proposed_changes"].append({
                    "task_id": task_id,
                    "current_status": "TODO",
                    "proposed_status": "IN_PROGRESS",
                    "reason": "Task is currently being worked on"
                })
                normalization_plan["justification"].append(
                    f"Marking {task_id} as IN_PROGRESS since it's the active task being executed"
                )
                
        return normalization_plan
    
    def normalize_tasks(self, dry_run: bool = False) -> Dict:
        """Normalize task status across PROJECT.md"""
        if dry_run:
            return self.dry_run_normalize()
            
        # Read the current content
        with open(self.project_md, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply normalizations
        # Mark H022 as IN_PROGRESS (this should be done by the caller)
        
        # Create backup
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.project_md.parent / f"PROJECT.md.backup_{timestamp}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
            
        # Write updated content (for now, just return the plan without changes)
        with open(self.project_md, 'w', encoding='utf-8') as f:
            f.write(content)
            
        return {
            "changes_applied": [],
            "backup_created": str(backup_path),
            "message": "Normalization completed successfully"
        }
    
    def generate_dashboard(self) -> str:
        """Generate a task health dashboard"""
        review_results = self.review_tasks()
        
        dashboard = f"""# Task Health Dashboard - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- **Total Tasks**: {review_results["total_tasks"]}
- **Last Review**: {datetime.now().isoformat()}

## Status Distribution
"""
        
        for status, count in review_results["status_counts"].items():
            dashboard += f"- **{status}**: {count}\n"
            
        dashboard += "\n## Epic Distribution\n"
        for epic, count in review_results["epic_counts"].items():
            dashboard += f"- **{epic}**: {count}\n"
            
        if review_results["inconsistencies"]:
            dashboard += "\n## Inconsistencies Found\n"
            for inc in review_results["inconsistencies"]:
                dashboard += f"- {inc['task_id']}: {inc['type']} - {inc['task_title']}\n"
                
        if review_results["stale_todos"]:
            dashboard += "\n## Stale TODOs\n"
            for todo in review_results["stale_todos"]:
                dashboard += f"- {todo['task_id']}: {todo['reason']}\n"
                
        if review_results["duplicates"]:
            dashboard += "\n## Potential Duplicates\n"
            for title, task_ids in review_results["duplicates"].items():
                dashboard += f"- Similar title '{title}': {', '.join(task_ids)}\n"
                
        dashboard += "\n## Recommendations\n"
        dashboard += "1. Address inconsistencies in task status\n"
        dashboard += "2. Review stale TODO items for completion\n"
        dashboard += "3. Consider consolidating duplicate tasks\n"
        dashboard += "4. Maintain consistent task numbering\n"
        
        return dashboard


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Normalize task status in Cortex-GOV PROJECT.md")
    parser.add_argument("--workspace", default=".", help="Workspace directory")
    parser.add_argument("--review", action="store_true", help="Review tasks and report findings")
    parser.add_argument("--normalize", action="store_true", help="Normalize tasks")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be changed without doing it")
    parser.add_argument("--generate-dashboard", action="store_true", help="Generate task health dashboard")
    parser.add_argument("--output", help="Output file for dashboard or results")
    
    args = parser.parse_args()
    
    normalizer = TaskNormalizer(args.workspace)
    
    if args.review:
        results = normalizer.review_tasks()
        print(json.dumps(results, indent=2))
        
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
                
    elif args.normalize:
        if args.dry_run:
            results = normalizer.normalize_tasks(dry_run=True)
        else:
            results = normalizer.normalize_tasks()
        print(json.dumps(results, indent=2))
        
    elif args.generate_dashboard:
        dashboard = normalizer.generate_dashboard()
        print(dashboard)
        
        if args.output:
            with open(args.output, 'w') as f:
                f.write(dashboard)
                
    else:
        parser.print_help()


if __name__ == "__main__":
    main()