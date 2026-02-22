#!/usr/bin/env python3
"""
Test Error Handling and Rollback for Recursive Planning Workflow

Demonstrates error handling capabilities and validates rollback mechanisms.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def test_error_handling():
    """Test error handling functionality"""
    # Import here to test import error handling
    from planning_error_handler import PlanningErrorHandler
    
    workspace_path = Path.cwd().parent
    error_handler = PlanningErrorHandler(workspace_path)
    
    # Test various error scenarios
    test_cases = [
        {
            "name": "File Not Found",
            "error": FileNotFoundError("Test file not found"),
            "context": {
                "operation": "planning_cycle",
                "cycle_id": "H021-TEST-01",
                "component": "data_loader"
            }
        },
        {
            "name": "Key Missing",
            "error": KeyError("missing_key"),
            "context": {
                "operation": "proposal_generation", 
                "cycle_id": "H021-TEST-02",
                "component": "proposal_manager"
            }
        },
        {
            "name": "Invalid Value",
            "error": ValueError("invalid_parameter_value"),
            "context": {
                "operation": "trigger_check",
                "cycle_id": "H021-TEST-03", 
                "component": "trigger_system"
            }
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        print(f"Testing {test_case['name']} error handling...")
        
        try:
            result = error_handler.handle_error(test_case["error"], test_case["context"])
            results.append({
                "test": test_case["name"],
                "success": True,
                "error_id": result["error_id"],
                "severity": result["severity"],
                "rollback_suggestions": len(result["rollback_suggestions"]),
                "resolution_steps": len(result["resolution_steps"])
            })
            print(f"  [PASS] Handled with {result['severity']} severity")
            print(f"  [PASS] {len(result['rollback_suggestions'])} rollback suggestions")
            print(f"  [PASS] {len(result['resolution_steps'])} resolution steps")
            
            # Test rollback for critical/high severity errors
            if result["severity"] in ["critical", "high"]:
                print(f"  [ROLLBACK] Executing rollback for {result['severity']} error...")
                rollback_result = error_handler.execute_rollback(test_case["context"])
                results[-1]["rollback_executed"] = rollback_result
                print(f"  [PASS] Rollback completed: {rollback_result['rollback_id']}")
                
        except Exception as e:
            results.append({
                "test": test_case["name"],
                "success": False,
                "error": str(e)
            })
            print(f"  [FAIL] Failed: {e}")
    
    return results


def test_error_decorator():
    """Test error handling decorator"""
    from planning_error_handler import PlanningErrorHandler
    
    workspace_path = Path.cwd().parent
    error_handler = PlanningErrorHandler(workspace_path)
    
    # Create decorated function that will fail
    @error_handler.create_error_handler_decorator("test_operation")
    def failing_function():
        raise RuntimeError("Test error in decorated function")
    
    # Create decorated function that will succeed
    @error_handler.create_error_handler_decorator("test_operation")  
    def succeeding_function():
        return {"status": "success", "data": "test_result"}
    
    print("\nTesting error handling decorator...")
    
    # Test failing function
    result = failing_function()
    if result["success"]:
        print("  [FAIL] Expected failure but got success")
        return False
    else:
        print("  [PASS] Decorated function correctly caught error")
        print(f"  Error ID: {result['error']['error_id']}")
    
    # Test succeeding function
    result = succeeding_function()
    if result["success"]:
        print("  [PASS] Decorated function succeeded correctly")
        print(f"  Result: {result['result']}")
    else:
        print("  [FAIL] Expected success but got error")
        return False
    
    return True


def main():
    print("Testing Planning Error Handler and Rollback Capabilities")
    print("=" * 60)
    
    # Test error handling
    print("\n1. Testing Error Handling:")
    error_results = test_error_handling()
    
    # Test error decorator
    print("\n2. Testing Error Decorator:")
    decorator_success = test_error_decorator()
    
    # Generate test report
    report = {
        "test_timestamp": datetime.now(timezone.utc).isoformat(),
        "error_handling_results": error_results,
        "decorator_test": {
            "success": decorator_success,
            "tests_run": 1 if decorator_success else 0
        },
        "summary": {
            "error_handling_tests": len([r for r in error_results if r.get("success", False)]),
            "total_error_tests": len(error_results),
            "decorator_success": decorator_success
        }
    }
    
    # Save test report
    test_dir = Path.cwd().parent / "artifacts" / "planning" / "H021-error-tests"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = test_dir / "error-handler-test-results.json"
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
    
    # Summary
    print(f"\nTest Summary:")
    print(f"Error Handling Tests: {report['summary']['error_handling_tests']}/{report['summary']['total_error_tests']} passed")
    print(f"Decorator Test: {'[PASS]' if report['summary']['decorator_success'] else '[FAIL]'}")
    print(f"Test Report: {test_file}")
    
    error_handling_success = all([r.get("success", False) for r in error_results])
    return 0 if (error_handling_success and decorator_success) else 1


if __name__ == "__main__":
    exit(main())