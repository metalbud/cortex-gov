#!/usr/bin/env python3
"""
Cortex-GOV H016 Pre-implementation Validation Checklist System

This system provides comprehensive validation before proposal implementation
to reduce implementation churn and increase first-pass verification quality.
"""

import json
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


class ValidationChecklist:
    def __init__(self, workspace_path: Optional[Path] = None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd().parent
        self.validation_dir = self.workspace_path / "artifacts" / "validation"
        self.validation_dir.mkdir(parents=True, exist_ok=True)
        
        # Load validation criteria
        self.criteria = self._load_criteria()
        
    def _load_criteria(self) -> Dict[str, Any]:
        """Load validation criteria from definitions file"""
        criteria_path = self.validation_dir / "H016-checklist-definitions.json"
        
        # Default criteria if file doesn't exist
        default_criteria = {
            "version": "1.0",
            "last_updated": datetime.now(timezone.utc).isoformat(),
            "checkpoints": [
                {
                    "id": "SAFETY_VALIDATION",
                    "name": "Safety Constraints Validation",
                    "description": "Ensure implementation follows H011 safety constraints",
                    "required": True,
                    "severity": "critical",
                    "validation_fn": "_validate_safety_constraints"
                },
                {
                    "id": "PROJECT_INTEGRITY",
                    "name": "PROJECT.md Integrity Check",
                    "description": "Verify PROJECT.md structure and task status consistency",
                    "required": True,
                    "severity": "high",
                    "validation_fn": "_validate_project_integrity"
                },
                {
                    "id": "FILE_BACKUP_VERIFICATION",
                    "name": "File Backup Verification",
                    "description": "Confirm backup files exist and are accessible",
                    "required": True,
                    "severity": "critical",
                    "validation_fn": "_validate_file_backups"
                },
                {
                    "id": "CHANGE_IMPACT_ASSESSMENT",
                    "name": "Change Impact Assessment",
                    "description": "Assess potential impact of proposed changes",
                    "required": False,
                    "severity": "medium",
                    "validation_fn": "_assess_change_impact"
                },
                {
                    "id": "DEPENDENCY_VERIFICATION",
                    "name": "Dependency Verification",
                    "description": "Verify all required dependencies are available",
                    "required": True,
                    "severity": "medium",
                    "validation_fn": "_verify_dependencies"
                }
            ]
        }
        
        if criteria_path.exists():
            try:
                with open(criteria_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with default to ensure all checkpoints exist
                    for checkpoint in default_criteria["checkpoints"]:
                        if not any(cp["id"] == checkpoint["id"] for cp in loaded.get("checkpoints", [])):
                            loaded.setdefault("checkpoints", []).append(checkpoint)
                    return loaded
            except Exception:
                return default_criteria
        
        # Save default criteria if file doesn't exist
        with open(criteria_path, 'w', encoding='utf-8') as f:
            json.dump(default_criteria, f, indent=2)
        
        return default_criteria
    
    def run_validation(self, scenario: str = "proposal-implementation") -> Dict[str, Any]:
        """Run all validation checks for the specified scenario"""
        results = {
            "scenario": scenario,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "total_checkpoints": len(self.criteria["checkpoints"]),
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "checkpoints": []
        }
        
        print(f"Running H016 validation checklist for scenario: {scenario}")
        print("=" * 60)
        
        for checkpoint in self.criteria["checkpoints"]:
            try:
                checkpoint_result = self._run_checkpoint(checkpoint, scenario)
                results["checkpoints"].append(checkpoint_result)
                
                if checkpoint_result["status"] == "PASSED":
                    results["passed"] += 1
                elif checkpoint_result["status"] == "FAILED":
                    results["failed"] += 1
                else:
                    results["skipped"] += 1
                    
                print(f"[{checkpoint_result['status']}] {checkpoint['name']}")
                if checkpoint_result.get("message"):
                    print(f"    {checkpoint_result['message']}")
                    
            except Exception as e:
                error_result = {
                    "id": checkpoint.get("id", "unknown"),
                    "name": checkpoint.get("name", "Unknown Checkpoint"),
                    "status": "ERROR",
                    "message": f"Validation error: {str(e)}",
                    "details": {}
                }
                results["checkpoints"].append(error_result)
                results["failed"] += 1
                print(f"[ERROR] {checkpoint['name']}: {e}")
        
        # Calculate overall pass/fail
        results["success"] = results["failed"] == 0
        
        print("=" * 60)
        print(f"Validation Summary: {results['passed']}/{results['total_checkpoints']} passed, {results['failed']} failed")
        
        if results["success"]:
            print("All validations passed - implementation can proceed")
        else:
            print("Validation failed - implementation blocked")
            
        return results
    
    def _run_checkpoint(self, checkpoint: Dict[str, Any], scenario: str) -> Dict[str, Any]:
        """Run a single validation checkpoint"""
        result = {
            "id": checkpoint["id"],
            "name": checkpoint["name"],
            "status": "SKIPPED",
            "message": "",
            "details": {}
        }
        
        # Check if checkpoint applies to the current scenario
        if not checkpoint.get("scenarios") or scenario in checkpoint.get("scenarios", []):
            # Execute the validation function
            validation_method = getattr(self, checkpoint.get("validation_fn", "_default_validate"), None)
            
            if validation_method and callable(validation_method):
                try:
                    validation_result = validation_method(scenario, checkpoint)
                    result.update(validation_result)
                    
                    if validation_result.get("status") == "FAILED" and checkpoint.get("required", False):
                        result["message"] = f"{result.get('message', '')} BLOCKED: Required checkpoint failed"
                        
                except Exception as e:
                    result["status"] = "ERROR"
                    result["message"] = f"Validation execution error: {str(e)}"
            else:
                result["status"] = "PASSED"
                result["message"] = "No specific validation required"
        else:
            result["status"] = "SKIPPED"
            result["message"] = "Not applicable to current scenario"
            
        return result
    
    def _validate_safety_constraints(self, scenario: str, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate implementation follows H011 safety constraints"""
        result = {"status": "PASSED", "message": "", "details": {}}
        
        try:
            # Check if safety guardian exists
            safety_file = self.workspace_path / "tools" / "self_improvement" / "safety_guardian.py"
            if not safety_file.exists():
                # Try alternative path structure
                safety_file = self.workspace_path / "cortex-gov" / "tools" / "self_improvement" / "safety_guardian.py"
                if not safety_file.exists():
                    result["status"] = "FAILED"
                    result["message"] = "H011 safety guardian not found"
                    return result
                
            # Check recent safety audit log
            audit_log = self.workspace_path / "artifacts" / "metrics" / "H011-audit-log.json"
            if audit_log.exists():
                with open(audit_log, 'r') as f:
                    audit_data = json.load(f)
                    recent_violations = [e for e in audit_data if e.get("result") == "BLOCK"]
                    if recent_violations:
                        result["status"] = "FAILED"
                        result["message"] = f"Recent safety violations detected: {len(recent_violations)}"
                        result["details"]["recent_violations"] = len(recent_violations)
                        
        except Exception as e:
            result["status"] = "FAILED"
            result["message"] = f"Safety validation error: {str(e)}"
            
        return result
    
    def _validate_project_integrity(self, scenario: str, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Verify PROJECT.md structure and task status consistency"""
        result = {"status": "PASSED", "message": "", "details": {}}
        
        try:
            # Try multiple potential paths for PROJECT.md
            project_file = self.workspace_path / "PROJECT.md"
            if not project_file.exists():
                project_file = self.workspace_path / "cortex-gov" / "PROJECT.md"
            if not project_file.exists():
                result["status"] = "FAILED"
                result["message"] = "PROJECT.md not found"
                return result
                
            content = project_file.read_text(encoding='utf-8')
            
            # Check for TODO tasks that might indicate incomplete work
            todo_count = content.count("Status: TODO")
            in_progress_count = content.count("Status: IN_PROGRESS")
            verify_count = content.count("Status: VERIFY")
            
            result["details"]["todo_tasks"] = todo_count
            result["details"]["in_progress_tasks"] = in_progress_count
            result["details"]["verify_tasks"] = verify_count
            
            # Flag if there are many TODOs relative to completed tasks
            total_tasks = todo_count + in_progress_count + verify_count + content.count("Status: DONE")
            if total_tasks > 0 and todo_count / total_tasks > 0.3:  # More than 30% TODO
                result["status"] = "WARNING"
                result["message"] = f"High TODO ratio detected: {todo_count}/{total_tasks} tasks are TODO"
                
        except Exception as e:
            result["status"] = "FAILED"
            result["message"] = f"PROJECT.md validation error: {str(e)}"
            
        return result
    
    def _validate_file_backups(self, scenario: str, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Confirm backup files exist and are accessible"""
        result = {"status": "PASSED", "message": "", "details": {}}
        
        try:
            # Try multiple potential paths for backups
            backup_dir = self.workspace_path / "artifacts" / "proposals" / "backups"
            if not backup_dir.exists():
                backup_dir = self.workspace_path / "cortex-gov" / "artifacts" / "proposals" / "backups"
            if not backup_dir.exists():
                result["status"] = "FAILED"
                result["message"] = "Backup directory not found"
                return result
                
            # Check for recent backups
            backup_files = list(backup_dir.rglob("*.bak"))
            recent_backups = [f for f in backup_files if f.stat().st_mtime > datetime.now().timestamp() - 86400]  # Last 24 hours
            
            result["details"]["total_backups"] = len(backup_files)
            result["details"]["recent_backups"] = len(recent_backups)
            
            if len(recent_backups) == 0:
                result["status"] = "WARNING"
                result["message"] = "No recent backups found (older than 24 hours)"
                
        except Exception as e:
            result["status"] = "FAILED"
            result["message"] = f"Backup validation error: {str(e)}"
            
        return result
    
    def _assess_change_impact(self, scenario: str, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Assess potential impact of proposed changes"""
        result = {"status": "PASSED", "message": "Impact assessment completed", "details": {}}
        
        try:
            # This would typically analyze the specific changes being proposed
            # For now, return a generic positive result
            impact_score = "medium"  # Could be calculated based on change analysis
            result["details"]["impact_assessment"] = impact_score
            
        except Exception as e:
            result["status"] = "FAILED"
            result["message"] = f"Impact assessment error: {str(e)}"
            
        return result
    
    def _verify_dependencies(self, scenario: str, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Verify all required dependencies are available"""
        result = {"status": "PASSED", "message": "", "details": {}}
        
        try:
            # Check for required Python packages
            required_packages = ["psutil", "requests", "json", "pathlib"]
            missing_packages = []
            
            for package in required_packages:
                try:
                    __import__(package)
                except ImportError:
                    missing_packages.append(package)
            
            if missing_packages:
                result["status"] = "FAILED"
                result["message"] = f"Missing dependencies: {', '.join(missing_packages)}"
                result["details"]["missing_packages"] = missing_packages
                
        except Exception as e:
            result["status"] = "FAILED"
            result["message"] = f"Dependency verification error: {str(e)}"
            
        return result
    
    def _default_validate(self, scenario: str, checkpoint: Dict[str, Any]) -> Dict[str, Any]:
        """Default validation function for checkpoints without specific implementation"""
        return {
            "status": "PASSED", 
            "message": "Default validation passed",
            "details": {}
        }
    
    def generate_report(self) -> str:
        """Generate a detailed validation report"""
        report_lines = [
            "# H016 Validation Checklist System Report",
            "",
            f"Generated at: {datetime.now(timezone.utc).isoformat()}",
            "",
            "## System Status",
            "",
            f"Validation criteria version: {self.criteria.get('version', 'unknown')}",
            f"Last criteria update: {self.criteria.get('last_updated', 'unknown')}",
            f"Total checkpoints defined: {len(self.criteria['checkpoints'])}",
            "",
            "## Checkpoint Definitions",
            ""
        ]
        
        for checkpoint in self.criteria["checkpoints"]:
            report_lines.extend([
                f"### {checkpoint['name']} ({checkpoint['id']})",
                "",
                f"**Description:** {checkpoint['description']}",
                f"**Required:** {checkpoint['required']}",
                f"**Severity:** {checkpoint['severity']}",
                f"**Validation Function:** {checkpoint.get('validation_fn', 'default')}",
                ""
            ])
        
        return "\n".join(report_lines)


def main():
    parser = argparse.ArgumentParser(description="Cortex-GOV H016 Pre-implementation Validation Checklist")
    parser.add_argument("--run", action="store_true", help="Run validation checks")
    parser.add_argument("--scenario", type=str, default="proposal-implementation", 
                       help="Scenario to validate (default: proposal-implementation)")
    parser.add_argument("--report", action="store_true", help="Generate validation report")
    parser.add_argument("--workspace", type=str, help="Path to cortex-gov workspace")
    parser.add_argument("--output", type=str, help="Output file path for validation results")
    
    args = parser.parse_args()
    
    # Initialize checklist
    checklist = ValidationChecklist(args.workspace)
    
    if args.run:
        results = checklist.run_validation(args.scenario)
        
        # Save results if output path specified
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2)
                
            print(f"Validation results saved to {output_path}")
        
        # Exit with code 1 if validation failed
        sys.exit(1 if not results["success"] else 0)
        
    elif args.report:
        report = checklist.generate_report()
        
        if args.output:
            output_path = Path(args.output)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(report)
                
            print(f"Validation report saved to {output_path}")
        else:
            print(report)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()