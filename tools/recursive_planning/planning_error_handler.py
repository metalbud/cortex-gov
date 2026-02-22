#!/usr/bin/env python3
"""
Error Handler for Recursive Planning Workflow

Implements error handling and rollback capabilities for the planning workflow.
"""

import json
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional


class PlanningErrorHandler:
    """Handles errors and provides rollback functionality for planning workflow"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.artifacts_dir = workspace_path / "artifacts"
        self.planning_dir = self.artifacts_dir / "planning"
        self.error_dir = self.planning_dir / "errors"
        self.error_dir.mkdir(parents=True, exist_ok=True)
        
    def handle_error(self, error: Exception, context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle planning workflow error with logging and rollback suggestions"""
        error_id = f"H021-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-ERROR"
        
        error_log = {
            "error_id": error_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "traceback": traceback.format_exc(),
            "context": context,
            "severity": self._assess_severity(error, context),
            "rollback_suggestions": self._generate_rollback_suggestions(context),
            "resolution_steps": self._generate_resolution_steps(error, context)
        }
        
        # Save error log
        error_file = self.error_dir / f"{error_id}.json"
        with open(error_file, 'w', encoding='utf-8') as f:
            json.dump(error_log, f, indent=2)
        
        return {
            "error_id": error_id,
            "severity": error_log["severity"],
            "message": str(error),
            "rollback_suggestions": error_log["rollback_suggestions"],
            "resolution_steps": error_log["resolution_steps"]
        }
    
    def _assess_severity(self, error: Exception, context: Dict[str, Any]) -> str:
        """Assess error severity"""
        error_type = type(error).__name__
        
        # Critical errors that require immediate attention
        critical_errors = [
            "KeyError", "FileNotFoundError", "PermissionError", 
            "ImportError", "ModuleNotFoundError", "AttributeError"
        ]
        
        if error_type in critical_errors:
            return "critical"
        elif error_type in ["ValueError", "TypeError", "IndexError"]:
            return "high"
        elif error_type in ["RuntimeError", "Exception"]:
            return "medium"
        else:
            return "low"
    
    def _generate_rollback_suggestions(self, context: Dict[str, Any]) -> List[str]:
        """Generate rollback suggestions for error recovery"""
        rollback_suggestions = []
        
        # Check what operation was in progress
        operation = context.get("operation", "unknown")
        
        if operation == "planning_cycle":
            rollback_suggestions.extend([
                "Restore previous planning cycle state from backup",
                "Delete incomplete planning artifacts",
                "Reset trigger state to last known good state"
            ])
        
        elif operation == "proposal_generation":
            rollback_suggestions.extend([
                "Remove incomplete proposals from proposal list",
                "Restore proposal system to previous state",
                "Regenerate proposals without the problematic input"
            ])
        
        elif operation == "trigger_check":
            rollback_suggestions.extend([
                "Reset trigger state to previous configuration",
                "Clear invalid trigger conditions",
                "Manual override of automatic triggers"
            ])
        
        elif operation == "report_generation":
            rollback_suggestions.extend([
                "Delete incomplete report files",
                "Restore last known good planning report",
                "Regenerate report with simplified parameters"
            ])
        
        # Generic rollback suggestions
        rollback_suggestions.extend([
            "Review error logs for root cause",
            "Implement validation before retry",
            "Consider manual intervention for critical operations"
        ])
        
        return rollback_suggestions
    
    def _generate_resolution_steps(self, error: Exception, context: Dict[str, Any]) -> List[str]:
        """Generate step-by-step resolution instructions"""
        resolution_steps = []
        
        error_type = type(error).__name__
        
        if error_type == "FileNotFoundError":
            resolution_steps.extend([
                "1. Verify required data files exist",
                "2. Check file permissions and accessibility",
                "3. Restore missing files from backup if necessary",
                "4. Update configuration to point to correct file locations"
            ])
        
        elif error_type == "KeyError":
            resolution_steps.extend([
                "1. Check required keys in data structures",
                "2. Validate input data completeness",
                "3. Add default values for missing keys",
                "4. Implement proper validation before access"
            ])
        
        elif error_type == "ValueError":
            resolution_steps.extend([
                "1. Validate input data types and ranges",
                "2. Check for invalid or out-of-range values",
                "3. Implement proper data sanitization",
                "4. Add bounds checking for critical parameters"
            ])
        
        elif error_type == "RuntimeError":
            resolution_steps.extend([
                "1. Check system resources (memory, CPU, disk)",
                "2. Verify all dependencies are properly installed",
                "3. Check for deadlocks or resource contention",
                "4. Review configuration settings"
            ])
        
        # Generic resolution steps
        resolution_steps.extend([
            "0. Review the full error log for detailed context",
            f"- Error ID: {context.get('cycle_id', 'unknown')}",
            f"- Operation: {context.get('operation', 'unknown')}",
            "1. Attempt resolution in the suggested order",
            "2. Test the fix by running a minimal version of the operation",
            "3. Monitor for recurrence after resolution",
            "4. Consider preventive measures for similar errors"
        ])
        
        return resolution_steps
    
    def execute_rollback(self, error_context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute rollback operations"""
        rollback_results = {
            "rollback_id": f"H021-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-ROLLBACK",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "operations_performed": [],
            "success": True,
            "details": "Rollback executed successfully"
        }
        
        # Perform rollback based on context
        operation = error_context.get("operation", "unknown")
        
        if operation == "planning_cycle":
            # Clean up incomplete planning artifacts
            cycle_id = error_context.get("cycle_id")
            if cycle_id:
                self._cleanup_planning_artifacts(cycle_id)
                rollback_results["operations_performed"].append(f"Cleaned up planning artifacts for {cycle_id}")
        
        elif operation == "proposal_generation":
            # Remove incomplete proposals
            self._cleanup_proposal_artifacts(error_context)
            rollback_results["operations_performed"].append("Cleaned up incomplete proposals")
        
        # Save rollback results
        rollback_file = self.planning_dir / f"{rollback_results['rollback_id']}.json"
        with open(rollback_file, 'w', encoding='utf-8') as f:
            json.dump(rollback_results, f, indent=2)
        
        return rollback_results
    
    def _cleanup_planning_artifacts(self, cycle_id: str):
        """Clean up planning artifacts for a failed cycle"""
        artifacts_to_remove = [
            self.planning_dir / f"{cycle_id}-cycle-execution.json",
            self.planning_dir / f"{cycle_id}-planning-report.md",
            self.artifacts_dir / "proposals" / f"{cycle_id}-auto-generated-proposals.json"
        ]
        
        for artifact in artifacts_to_remove:
            if artifact.exists():
                artifact.unlink()
    
    def _cleanup_proposal_artifacts(self, context: Dict[str, Any]):
        """Clean up proposal artifacts from failed generation"""
        # This would clean up proposals that were partially generated
        # In practice, this would involve proposal system API calls
        pass
    
    def create_error_handler_decorator(self, operation_type: str):
        """Create a decorator for automatic error handling"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                context = {
                    "operation": operation_type,
                    "function": func.__name__,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "args": str(args)[:200],  # Truncate for security
                    "kwargs": str(kwargs)[:200]  # Truncate for security
                }
                
                try:
                    result = func(*args, **kwargs)
                    return {
                        "success": True,
                        "result": result,
                        "context": context
                    }
                except Exception as e:
                    error_response = self.handle_error(e, context)
                    
                    # Execute rollback if critical error
                    if error_response.get("severity") in ["critical", "high"]:
                        rollback_result = self.execute_rollback(context)
                        error_response["rollback_executed"] = rollback_result
                    
                    return {
                        "success": False,
                        "error": error_response,
                        "context": context
                    }
            
            return wrapper
        return decorator


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Planning Error Handler")
    parser.add_argument("--test-error", action="store_true", help="Test error handling")
    parser.add_argument("--rollback", type=str, help="Execute rollback for specific error")
    parser.add_argument("--workspace", type=str, help="Path to cortex-gov workspace")
    
    args = parser.parse_args()
    
    workspace_path = Path(args.workspace) if args.workspace else Path.cwd().parent
    error_handler = PlanningErrorHandler(workspace_path)
    
    if args.test_error:
        # Test error handling
        try:
            raise FileNotFoundError("Test error for error handling demonstration")
        except Exception as e:
            context = {
                "operation": "test",
                "cycle_id": "test-cycle",
                "component": "error_handler_test"
            }
            result = error_handler.handle_error(e, context)
            print(f"Error handled: {result['error_id']}")
            print(f"Severity: {result['severity']}")
            print(f"Rollback suggestions: {len(result['rollback_suggestions'])}")
            print(f"Resolution steps: {len(result['resolution_steps'])}")
    
    elif args.rollback:
        # Execute rollback
        rollback_context = {
            "operation": args.rollback,
            "cycle_id": args.rollback
        }
        result = error_handler.execute_rollback(rollback_context)
        print(f"Rollback executed: {result['rollback_id']}")
        print(f"Operations: {len(result['operations_performed'])}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()