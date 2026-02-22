"""Cortex-GOV H011 Safety Guardian - Enforces immutable governance constraints.

This tool provides automated validation for proposed changes to cortex-gov systems,
enforcing that core governance principles cannot be altered by autonomous agents.

Enhanced with H027 AI Safety Rails and Autonomous Coding Capabilities:
- Configurable safety thresholds for autonomous operations
- Autonomous coding feedback mechanisms
- Industry guardrails based on current trends
- Progressive autonomy with monitoring and controls

Core Immutable Constraints:
- Status model (TODO → IN_PROGRESS → VERIFY → DONE) cannot be modified
- An approval gate is mandatory for all proposals (human or autonomous policy)
- One-task-at-a-time rule cannot be removed
- Document-driven governance cannot be bypassed
- Verification requirements cannot be eliminated

All validation attempts are logged to artifacts/metrics/H011-audit-log.json.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Set

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT_LOG_PATH = BASE_DIR / "artifacts" / "metrics" / "H011-audit-log.json"
DEFAULT_CONSTRAINTS_PATH = BASE_DIR / "artifacts" / "validation" / "H011-immutable-constraints.json"
DEFAULT_VALIDATION_REPORT_PATH = BASE_DIR / "artifacts" / "verification" / "H011-validation-report.md"

# Core immutable constraints that cannot be modified
IMMUTABLE_CONSTRAINTS = {
    "status_model": {
        "description": "Task state transition rules are immutable",
        "allowed_transitions": {
            "TODO": ["IN_PROGRESS"],
            "IN_PROGRESS": ["VERIFY", "BLOCKED", "TODO"],
            "VERIFY": ["DONE", "IN_PROGRESS"],
            "BLOCKED": ["IN_PROGRESS", "TODO"],
            "DONE": [],
        },
        "forbidden_modifications": [
            "Add new status outside of defined states",
            "Remove any existing status",
            "Bypass IN_PROGRESS before DONE",
            "Allow DONE → any other status (except manual override)",
        ],
    },
    "human_gate": {
        "description": "An approval gate is mandatory for all proposals and modifications",
        "forbidden_modifications": [
            "Remove approval gate requirement from proposal schema",
            "Allow implementation without any approval decision",
            "Override or bypass recorded rejection",
            "Disable both human and autonomous policy gating",
        ],
    },
    "one_task_at_a_time": {
        "description": "Only one task may be IN_PROGRESS at a time",
        "forbidden_modifications": [
            "Allow multiple IN_PROGRESS tasks simultaneously",
            "Remove one-task-at-a-time rule",
            "Create parallel work streams without human approval",
        ],
    },
    "document_driven": {
        "description": "All work must be documented in PROJECT.md",
        "forbidden_modifications": [
            "Allow implicit work without PROJECT.md updates",
            "Remove requirement to update task status in PROJECT.md",
            "Eliminate evidence collection requirements",
        ],
    },
    "verification_required": {
        "description": "DONE requires verification with evidence",
        "forbidden_modifications": [
            "Remove verification step before DONE",
            "Allow DONE without evidence",
            "Eliminate verification checklists",
        ],
    },
}

# Protected file patterns that require enhanced scrutiny
PROTECTED_PATTERNS = {
    "PROJECT.md": {
        "description": "Main project governance document",
        "protected_sections": ["Rules", "Constraints", "Epics", "Status definitions"],
        "required_presence": ["TODO", "IN_PROGRESS", "VERIFY", "DONE", "BLOCKED"],
    },
    "**/artifacts/proposals/*.json": {
        "description": "Proposal storage files",
        "protected_fields": ["humanGate", "id", "proposedAt", "history"],
    },
    "**/tools/self_improvement/*.py": {
        "description": "Self-improvement tooling",
        "immutable_files": [
            "safety_guardian.py",  # This file is self-protecting
        ],
    },
}

# Modification scope limits
MODIFICATION_SCOPE_LIMITS = {
    "allowed_without_approval": [
        "Adding new TODO tasks",
        "Updating task work items (checkboxes)",
        "Adding verification evidence",
        "Creating metric logs",
        "Adding documentation",
    ],
    "requires_approval": [
        "Modifying task status (especially DONE)",
        "Changing Epic definitions",
        "Modifying Rules section",
        "Changing Constraints",
        "Modifying immutable constraint definitions",
        "Changing proposal schema",
        "Removing or modifying archived evidence",
    ],
    "prohibited": [
        "Modifying DONE tasks to hide failures",
        "Deleting audit logs or history",
        "Disabling approval gates to reduce oversight",
        "Removing safety validation systems",
        "Circumventing one-task-at-a-time",
        "Allowing parallel IN_PROGRESS without approval",
    ],
}


class SafetyViolation(RuntimeError):
    """Raised when a proposed change violates safety constraints."""
    pass


class ConstraintValidationError(RuntimeError):
    """Raised when constraint validation fails."""
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def append_json_array(path: Path, entry: Dict[str, Any]) -> None:
    data = load_json(path, default=[])
    if not isinstance(data, list):
        data = []
    data.append(entry)
    ensure_parent(path)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def log_audit_event(
    event_type: str,
    actor: str,
    target: str,
    result: str,
    details: Dict[str, Any],
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> None:
    """Log a validation event to the audit trail."""
    entry = {
        "timestamp": utc_now(),
        "eventType": event_type,
        "actor": actor,
        "target": target,
        "result": result,
        "details": details,
    }
    append_json_array(audit_log_path, entry)


def validate_status_model_protection(
    proposed_changes: Dict[str, Any],
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Tuple[bool, List[str]]:
    """Validate that status model cannot be modified.
    
    Returns (is_valid, violations_list)
    """
    violations = []
    
    # Check for any attempt to modify status transitions
    if "status" in proposed_changes or "Status" in str(proposed_changes):
        # Check for forbidden status modifications
        forbidden = IMMUTABLE_CONSTRAINTS["status_model"]["forbidden_modifications"]
        for forbidden_pattern in forbidden:
            if forbidden_pattern.lower() in str(proposed_changes).lower():
                violations.append(f"Attempted to modify status model: {forbidden_pattern}")
    
    # Check if trying to add new status states
    if "add" in str(proposed_changes).lower() and "status" in str(proposed_changes).lower():
        violations.append("Attempted to add new status states to the model")
    
    is_valid = len(violations) == 0
    
    log_audit_event(
        event_type="STATUS_MODEL_VALIDATION",
        actor=actor,
        target="status_model",
        result="PASS" if is_valid else "BLOCK",
        details={"violations": violations, "proposed": proposed_changes},
        audit_log_path=audit_log_path,
    )
    
    return is_valid, violations


def validate_human_gate_protection(
    proposed_changes: Dict[str, Any],
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Tuple[bool, List[str]]:
    """Validate that proposal approval gates cannot be bypassed or removed."""
    violations = []
    changes_str = str(proposed_changes).lower()
    normalized = changes_str.replace("_", "").replace("-", "")
    autonomous_gate_markers = [
        "autonomous-policy-gate",
        "\"approvalmode\": \"autonomous\"",
        "'approvalmode': 'autonomous'",
        "autonomous gating",
        "policy gate",
    ]
    autonomous_gate_requested = any(marker in changes_str for marker in autonomous_gate_markers)
    
    # Check for attempts to modify humanGate
    if "humangate" in normalized:
        # Check for removal of human gate requirement without explicit policy gate replacement
        if any(pattern in changes_str for pattern in ["false", "remove", "disable", "bypass"]):
            if not autonomous_gate_requested:
                violations.append("Attempted to disable approval gate requirement")
        
        # Check for self-approval mechanisms without explicit policy gate declaration
        if "self-approve" in changes_str or "auto-approve" in changes_str:
            if not autonomous_gate_requested:
                violations.append("Attempted to implement ungated self-approval mechanism")
    
    # Check for implementation without approval patterns
    if "implementation" in changes_str:
        has_approval_signal = "approve" in changes_str or autonomous_gate_requested
        if "implement" in changes_str and not has_approval_signal:
            violations.append("Attempted to implement without explicit approval gate")
    
    is_valid = len(violations) == 0
    
    log_audit_event(
        event_type="HUMAN_GATE_VALIDATION",
        actor=actor,
        target="human_gate",
        result="PASS" if is_valid else "BLOCK",
        details={"violations": violations, "proposed": proposed_changes},
        audit_log_path=audit_log_path,
    )
    
    return is_valid, violations


def validate_one_task_at_a_time(
    project_md_content: str,
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Tuple[bool, List[str]]:
    """Validate that only one task is IN_PROGRESS at a time."""
    violations = []
    
    # Count IN_PROGRESS tasks
    in_progress_count = project_md_content.count("Status: IN_PROGRESS")
    
    if in_progress_count > 1:
        violations.append(f"Multiple IN_PROGRESS tasks detected: {in_progress_count}")
    
    # Check if the rule itself is being removed
    if "one task" in project_md_content.lower() and "may be" in project_md_content.lower():
        if any(term in project_md_content.lower() for term in ["remove", "delete", "eliminate"]):
            violations.append("Attempted to remove one-task-at-a-time rule")
    
    is_valid = len(violations) == 0
    
    log_audit_event(
        event_type="ONE_TASK_VALIDATION",
        actor=actor,
        target="one_task_at_a_time",
        result="PASS" if is_valid else "BLOCK",
        details={"violations": violations, "in_progress_count": in_progress_count},
        audit_log_path=audit_log_path,
    )
    
    return is_valid, violations


def validate_document_driven(
    proposed_changes: Dict[str, Any],
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Tuple[bool, List[str]]:
    """Validate document-driven governance is maintained."""
    violations = []
    changes_str = str(proposed_changes).lower()
    
    # Check for attempts to bypass documentation
    bypass_patterns = [
        "implicit work",
        "no documentation required",
        "skip project.md",
        "without updating",
    ]
    
    for pattern in bypass_patterns:
        if pattern in changes_str:
            violations.append(f"Attempted to bypass documentation requirement: {pattern}")
    
    # Check for evidence removal
    if "evidence" in changes_str:
        if any(term in changes_str for term in ["remove", "delete", "skip", "omit"]):
            violations.append("Attempted to remove or skip evidence collection")
    
    is_valid = len(violations) == 0
    
    log_audit_event(
        event_type="DOCUMENT_DRIVEN_VALIDATION",
        actor=actor,
        target="document_driven",
        result="PASS" if is_valid else "BLOCK",
        details={"violations": violations, "proposed": proposed_changes},
        audit_log_path=audit_log_path,
    )
    
    return is_valid, violations


def validate_verification_required(
    proposed_changes: Dict[str, Any],
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Tuple[bool, List[str]]:
    """Validate that verification requirements cannot be eliminated."""
    violations = []
    changes_str = str(proposed_changes).lower()
    
    # Check for verification removal
    if "verification" in changes_str:
        if any(term in changes_str for term in ["remove", "skip", "bypass", "eliminate"]):
            violations.append("Attempted to remove or bypass verification requirements")
    
    # Check for DONE without verification
    if "done without" in changes_str or "skip verify" in changes_str:
        violations.append("Attempted to allow DONE without verification")
    
    # Check for evidence removal
    if "evidence" in changes_str:
        if "not required" in changes_str or "optional" in changes_str:
            violations.append("Attempted to make evidence optional for DONE")
    
    is_valid = len(violations) == 0
    
    log_audit_event(
        event_type="VERIFICATION_VALIDATION",
        actor=actor,
        target="verification_required",
        result="PASS" if is_valid else "BLOCK",
        details={"violations": violations, "proposed": proposed_changes},
        audit_log_path=audit_log_path,
    )
    
    return is_valid, violations


def validate_modification_scope(
    target_file: str,
    change_type: str,
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Tuple[str, List[str]]:
    """Validate if modification is within allowed scope.
    
    Returns (decision, warnings) where decision is one of:
    - "ALLOWED": No approval needed
    - "REQUIRES_APPROVAL": Must go through proposal workflow
    - "BLOCKED": Prohibited modification
    """
    warnings = []
    
    # Check prohibited modifications
    prohibited = MODIFICATION_SCOPE_LIMITS["prohibited"]
    for pattern in prohibited:
        if pattern.lower() in change_type.lower() or pattern.lower() in target_file.lower():
            warnings.append(f"Prohibited modification detected: {pattern}")
            log_audit_event(
                event_type="SCOPE_VALIDATION",
                actor=actor,
                target=target_file,
                result="BLOCK",
                details={"change_type": change_type, "matched_prohibition": pattern},
                audit_log_path=audit_log_path,
            )
            return "BLOCKED", warnings
    
    # Check if requires approval
    requires_approval = MODIFICATION_SCOPE_LIMITS["requires_approval"]
    for pattern in requires_approval:
        if pattern.lower() in change_type.lower():
            warnings.append(f"Modification requires approval: {pattern}")
            log_audit_event(
                event_type="SCOPE_VALIDATION",
                actor=actor,
                target=target_file,
                result="REQUIRES_APPROVAL",
                details={"change_type": change_type, "matched_pattern": pattern},
                audit_log_path=audit_log_path,
            )
            return "REQUIRES_APPROVAL", warnings
    
    # Check if allowed without approval
    allowed = MODIFICATION_SCOPE_LIMITS["allowed_without_approval"]
    for pattern in allowed:
        if pattern.lower() in change_type.lower():
            log_audit_event(
                event_type="SCOPE_VALIDATION",
                actor=actor,
                target=target_file,
                result="ALLOWED",
                details={"change_type": change_type},
                audit_log_path=audit_log_path,
            )
            return "ALLOWED", warnings
    
    # Default to requires approval for unknown changes
    warnings.append("Unknown modification type - defaulting to approval required")
    return "REQUIRES_APPROVAL", warnings


def comprehensive_validation(
    proposed_changes: Dict[str, Any],
    project_md_content: Optional[str],
    target_file: str,
    change_type: str,
    actor: str,
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
) -> Dict[str, Any]:
    """Run all safety validations comprehensively.
    
    Returns validation report with:
    - is_valid: Overall validation result
    - blocked: List of blocking violations
    - warnings: List of non-blocking warnings
    - scope_decision: Modification scope decision
    - audit_trail: Reference to audit log
    """
    blocked = []
    warnings = []
    
    # Run all constraint validations
    validations = [
        ("status_model", validate_status_model_protection(proposed_changes, actor, audit_log_path)),
        ("human_gate", validate_human_gate_protection(proposed_changes, actor, audit_log_path)),
        ("document_driven", validate_document_driven(proposed_changes, actor, audit_log_path)),
        ("verification_required", validate_verification_required(proposed_changes, actor, audit_log_path)),
    ]
    
    if project_md_content:
        validations.append(
            ("one_task_at_a_time", validate_one_task_at_a_time(project_md_content, actor, audit_log_path))
        )
    
    for constraint_name, (is_valid, violations) in validations:
        if not is_valid:
            blocked.extend([f"[{constraint_name}] {v}" for v in violations])
    
    # Check modification scope
    scope_decision, scope_warnings = validate_modification_scope(
        target_file, change_type, actor, audit_log_path
    )
    warnings.extend(scope_warnings)
    
    if scope_decision == "BLOCKED":
        blocked.append(f"[scope] Modification is in prohibited category")
    
    # Final validation result
    is_valid = len(blocked) == 0
    
    report = {
        "timestamp": utc_now(),
        "actor": actor,
        "target": target_file,
        "change_type": change_type,
        "is_valid": is_valid,
        "blocked": blocked,
        "warnings": warnings,
        "scope_decision": scope_decision,
        "audit_log": str(audit_log_path),
    }
    
    # Log comprehensive validation event
    log_audit_event(
        event_type="COMPREHENSIVE_VALIDATION",
        actor=actor,
        target=target_file,
        result="PASS" if is_valid else "BLOCK",
        details={
            "change_type": change_type,
            "violations_count": len(blocked),
            "warnings_count": len(warnings),
            "scope_decision": scope_decision,
        },
        audit_log_path=audit_log_path,
    )
    
    return report


def export_immutable_constraints(output_path: Path = DEFAULT_CONSTRAINTS_PATH) -> None:
    """Export the immutable constraints to a JSON file for reference."""
    ensure_parent(output_path)
    
    export_data = {
        "version": "1.0.0",
        "exported_at": utc_now(),
        "immutable_constraints": IMMUTABLE_CONSTRAINTS,
        "protected_patterns": PROTECTED_PATTERNS,
        "modification_scope_limits": MODIFICATION_SCOPE_LIMITS,
        "description": "These constraints define the core governance rules of cortex-gov. They cannot be modified without explicit human approval and proper procedure.",
    }
    
    output_path.write_text(json.dumps(export_data, indent=2), encoding="utf-8")
    print(f"Exported immutable constraints to {output_path}")


def generate_validation_report(
    audit_log_path: Path = DEFAULT_AUDIT_LOG_PATH,
    output_path: Path = DEFAULT_VALIDATION_REPORT_PATH,
) -> None:
    """Generate a human-readable validation report from audit log."""
    audit_entries = load_json(audit_log_path, default=[])
    
    if not audit_entries:
        print("No audit entries found. Run validations first.")
        return
    
    # Calculate statistics
    total_validations = len([e for e in audit_entries if e.get("eventType") == "COMPREHENSIVE_VALIDATION"])
    blocked_count = len([e for e in audit_entries if e.get("result") == "BLOCK"])
    allowed_count = len([e for e in audit_entries if e.get("result") == "ALLOWED"])
    approval_required_count = len([e for e in audit_entries if e.get("result") == "REQUIRES_APPROVAL"])
    
    # Recent blocks (last 10)
    recent_blocks = [
        e for e in audit_entries 
        if e.get("result") == "BLOCK"
    ][-10:]
    
    # Build report
    lines = [
        "# H011 Safety Guardian Validation Report",
        "",
        f"Generated: {utc_now()}",
        "",
        "## Overview",
        "",
        f"- **Total Validations**: {total_validations}",
        f"- **Blocked**: {blocked_count}",
        f"- **Allowed**: {allowed_count}",
        f"- **Requires Approval**: {approval_required_count}",
        "",
        "## Immutable Constraints",
        "",
    ]
    
    for constraint_name, constraint_data in IMMUTABLE_CONSTRAINTS.items():
        lines.append(f"### {constraint_name}")
        lines.append(f"- **Description**: {constraint_data['description']}")
        if "forbidden_modifications" in constraint_data:
            lines.append("- **Forbidden Modifications**:")
            for fm in constraint_data["forbidden_modifications"]:
                lines.append(f"  - {fm}")
        lines.append("")
    
    lines.extend([
        "## Modification Scope Limits",
        "",
        "### Allowed Without Approval",
    ])
    for item in MODIFICATION_SCOPE_LIMITS["allowed_without_approval"]:
        lines.append(f"- {item}")
    
    lines.extend([
        "",
        "### Requires Approval",
    ])
    for item in MODIFICATION_SCOPE_LIMITS["requires_approval"]:
        lines.append(f"- {item}")
    
    lines.extend([
        "",
        "### Prohibited",
    ])
    for item in MODIFICATION_SCOPE_LIMITS["prohibited"]:
        lines.append(f"- ❌ {item}")
    
    if recent_blocks:
        lines.extend([
            "",
            "## Recent Blocked Attempts (Last 10)",
            "",
        ])
        for entry in recent_blocks:
            lines.append(f"- **{entry['timestamp']}**: {entry['target']} by {entry['actor']}")
            if entry.get("details", {}).get("violations"):
                for v in entry["details"]["violations"]:
                    lines.append(f"  - {v}")
    
    lines.extend([
        "",
        "## Audit Trail",
        f"Full audit log: `{audit_log_path}`",
        "",
        "---",
        "This report is generated from the H011 safety guardian audit log.",
        "Each validation attempt is recorded with timestamp, actor, target, and result.",
    ])
    
    ensure_parent(output_path)
    output_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Generated validation report: {output_path}")


def cmd_validate(args: argparse.Namespace) -> None:
    """Validate a proposed change against all safety constraints."""
    proposed = {}
    if args.proposed_json:
        proposed = json.loads(args.proposed_json)
    elif args.proposed_file:
        proposed = json.loads(Path(args.proposed_file).read_text(encoding="utf-8"))
    
    project_md = None
    if args.project_md:
        project_md = Path(args.project_md).read_text(encoding="utf-8")
    
    report = comprehensive_validation(
        proposed_changes=proposed,
        project_md_content=project_md,
        target_file=args.target or "unknown",
        change_type=args.change_type or "unknown",
        actor=args.actor,
        audit_log_path=args.audit_log,
    )
    
    print(json.dumps(report, indent=2))
    
    if not report["is_valid"]:
        print("\n[!] SAFETY VIOLATIONS DETECTED - Change is BLOCKED")
        for violation in report["blocked"]:
            print(f"  - {violation}")
        raise SystemExit(1)
    elif report["scope_decision"] == "REQUIRES_APPROVAL":
        print("\n[!] CHANGE REQUIRES APPROVAL")
        print("This modification must go through the proposal workflow gate.")
        raise SystemExit(2)
    else:
        print("\n[OK] Validation passed - Change is allowed")


def cmd_constraints(args: argparse.Namespace) -> None:
    """Export immutable constraints to JSON file."""
    export_immutable_constraints(args.output)
    print(f"Immutable constraints exported to: {args.output}")


def cmd_report(args: argparse.Namespace) -> None:
    """Generate validation report from audit log."""
    generate_validation_report(args.audit_log, args.output)


def cmd_audit_log(args: argparse.Namespace) -> None:
    """Display or filter audit log entries."""
    entries = load_json(args.audit_log, default=[])
    
    if args.filter_type:
        entries = [e for e in entries if e.get("eventType") == args.filter_type]
    if args.filter_result:
        entries = [e for e in entries if e.get("result") == args.filter_result]
    if args.limit:
        entries = entries[-args.limit:]
    
    if args.json_output:
        print(json.dumps(entries, indent=2))
    else:
        print(f"{'Timestamp':<28} {'Type':<25} {'Result':<12} {'Actor':<15} Target")
        print("-" * 100)
        for entry in entries:
            print(
                f"{entry['timestamp']:<28} "
                f"{entry.get('eventType', ''):<25} "
                f"{entry.get('result', ''):<12} "
                f"{entry.get('actor', ''):<15} "
                f"{entry.get('target', '')}"
            )


def cmd_test(args: argparse.Namespace) -> None:
    """Run built-in safety validation tests."""
    print("Running H011 Safety Guardian validation tests...")
    
    test_results = []
    
    # Test 1: Status model protection
    test_proposed = {"status_changes": "Add new status 'HOLDING'"}
    valid, violations = validate_status_model_protection(test_proposed, "test", args.audit_log)
    test_results.append(("Status Model Protection", not valid and len(violations) > 0))
    
    # Test 2: Human gate protection
    test_proposed = {"humanGate.required": False}
    valid, violations = validate_human_gate_protection(test_proposed, "test", args.audit_log)
    test_results.append(("Human Gate Protection", not valid and len(violations) > 0))
    
    # Test 3: One task at a time
    test_md = "Status: IN_PROGRESS\nStatus: IN_PROGRESS\nStatus: IN_PROGRESS"
    valid, violations = validate_one_task_at_a_time(test_md, "test", args.audit_log)
    test_results.append(("One Task At A Time", not valid and len(violations) > 0))
    
    # Test 4: Document driven
    test_proposed = {"action": "Implicit work without PROJECT.md updates"}
    valid, violations = validate_document_driven(test_proposed, "test", args.audit_log)
    test_results.append(("Document Driven", not valid and len(violations) > 0))
    
    # Test 5: Verification required
    test_proposed = {"remove": "eliminate verification step"}
    valid, violations = validate_verification_required(test_proposed, "test", args.audit_log)
    test_results.append(("Verification Required", not valid and len(violations) > 0))
    
    # Test 6: Scope validation
    decision, warnings = validate_modification_scope(
        "PROJECT.md", "Modifying DONE tasks to hide failures", "test", args.audit_log
    )
    test_results.append(("Scope Validation", decision == "BLOCKED"))
    
    # Print results
    print(f"\n{'Test Name':<30} {'Result':<10}")
    print("-" * 42)
    all_passed = True
    for name, passed in test_results:
        status = "PASS" if passed else "FAIL"
        print(f"{name:<30} {status:<10}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n[OK] All safety validation tests passed")
    else:
        print("\n[X] Some tests failed - safety system may be compromised")
        raise SystemExit(1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="H011 Safety Guardian - Enforces immutable governance constraints for cortex-gov"
    )
    parser.add_argument(
        "--audit-log",
        type=Path,
        default=DEFAULT_AUDIT_LOG_PATH,
        help="Path to audit log JSON file",
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # validate command
    validate_parser = subparsers.add_parser(
        "validate", help="Validate a proposed change against safety constraints"
    )
    validate_parser.add_argument(
        "--proposed-json",
        help="JSON string of proposed changes",
    )
    validate_parser.add_argument(
        "--proposed-file",
        type=Path,
        help="Path to JSON file with proposed changes",
    )
    validate_parser.add_argument(
        "--project-md",
        type=Path,
        help="Path to PROJECT.md for context validation",
    )
    validate_parser.add_argument(
        "--target",
        required=True,
        help="Target file being modified",
    )
    validate_parser.add_argument(
        "--change-type",
        required=True,
        help="Description of the change type",
    )
    validate_parser.add_argument(
        "--actor",
        required=True,
        help="Actor making the change (for audit trail)",
    )
    validate_parser.set_defaults(func=cmd_validate)
    
    # constraints command
    constraints_parser = subparsers.add_parser(
        "constraints", help="Export immutable constraints to JSON"
    )
    constraints_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_CONSTRAINTS_PATH,
        help="Output path for constraints JSON",
    )
    constraints_parser.set_defaults(func=cmd_constraints)
    
    # report command
    report_parser = subparsers.add_parser(
        "report", help="Generate validation report from audit log"
    )
    report_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_VALIDATION_REPORT_PATH,
        help="Output path for report",
    )
    report_parser.set_defaults(func=cmd_report)
    
    # audit-log command
    audit_parser = subparsers.add_parser("audit-log", help="View audit log entries")
    audit_parser.add_argument("--filter-type", help="Filter by event type")
    audit_parser.add_argument("--filter-result", help="Filter by result")
    audit_parser.add_argument("--limit", type=int, help="Limit to N most recent entries")
    audit_parser.add_argument("--json-output", action="store_true", help="Output as JSON")
    audit_parser.set_defaults(func=cmd_audit_log)
    
    # test command
    test_parser = subparsers.add_parser("test", help="Run safety validation tests")
    test_parser.set_defaults(func=cmd_test)
    
    # enhanced-validation command (H027)
    enhanced_parser = subparsers.add_parser(
        "enhanced-validation", help="Run enhanced validation with AI safety rails"
    )
    enhanced_parser.add_argument(
        "--operation-json",
        help="JSON string of autonomous operation to validate",
    )
    enhanced_parser.add_argument(
        "--operation-file",
        type=Path,
        help="Path to JSON file with autonomous operation",
    )
    enhanced_parser.add_argument(
        "--audit-log",
        type=Path,
        default=DEFAULT_AUDIT_LOG_PATH,
        help="Path to audit log JSON file",
    )
    enhanced_parser.set_defaults(func=cmd_enhanced_validation)
    
    # record-operation command (H027)
    record_parser = subparsers.add_parser(
        "record-operation", help="Record an autonomous operation for feedback analysis"
    )
    record_parser.add_argument(
        "--operation-json",
        help="JSON string of operation to record",
    )
    record_parser.add_argument(
        "--operation-file",
        type=Path,
        help="Path to JSON file with operation to record",
    )
    record_parser.add_argument(
        "--success",
        action="store_true",
        help="Mark operation as successful",
    )
    record_parser.add_argument(
        "--audit-log",
        type=Path,
        default=DEFAULT_AUDIT_LOG_PATH,
        help="Path to audit log JSON file",
    )
    record_parser.set_defaults(func=cmd_record_operation)
    
    # analyze-feedback command (H027)
    analyze_parser = subparsers.add_parser(
        "analyze-feedback", help="Analyze autonomous coding feedback patterns"
    )
    analyze_parser.add_argument(
        "--audit-log",
        type=Path,
        default=DEFAULT_AUDIT_LOG_PATH,
        help="Path to audit log JSON file",
    )
    analyze_parser.set_defaults(func=cmd_analyze_feedback)
    
    return parser.parse_args()


# H027 Enhanced AI Safety Rails and Autonomous Coding Functions

class SafetyRailManager:
    """Manages configurable safety rails for autonomous operations."""
    
    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self.config_path = BASE_DIR / "artifacts" / "config" / "H027-safety-rails.json"
        self.default_thresholds = {
            "autonomy_level": 0.7,  # Maximum autonomy level (0.0 to 1.0)
            "consecutive_failures": 3,  # Max consecutive failures before intervention
            "risk_threshold": 0.5,  # Risk level threshold for intervention
            "confidence_requirement": 0.8,  # Minimum confidence required for autonomous actions
            "feedback_sensitivity": 0.6,  # Sensitivity to feedback for adjusting behavior
        }
        self.load_config()
    
    def load_config(self) -> None:
        """Load safety rail configuration from file or create defaults."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.config = self.default_thresholds.copy()
            self.save_config()
    
    def save_config(self) -> None:
        """Save current configuration to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def evaluate_safety_rails(self, operation: Dict[str, Any], actor: str) -> Tuple[bool, List[str]]:
        """
        Evaluate if an operation passes safety rail checks.
        
        Returns:
            Tuple of (is_safe, warnings)
        """
        warnings = []
        
        # Check autonomy level
        if operation.get("autonomy_level", 0) > self.config["autonomy_level"]:
            warnings.append(f"Autonomy level {operation.get('autonomy_level', 0)} exceeds threshold {self.config['autonomy_level']}")
        
        # Check risk level
        if operation.get("risk_level", 0) > self.config["risk_threshold"]:
            warnings.append(f"Risk level {operation.get('risk_level', 0)} exceeds threshold {self.config['risk_threshold']}")
        
        # Check confidence
        if operation.get("confidence", 0) < self.config["confidence_requirement"]:
            warnings.append(f"Confidence {operation.get('confidence', 0)} below required minimum {self.config['confidence_requirement']}")
        
        # Log evaluation
        log_audit_event(
            "safety_rails_evaluation",
            actor,
            "operation_check",
            "OK" if not warnings else "WARNING",
            {"operation_type": operation.get("type"), "warnings": warnings},
            self.audit_log_path
        )
        
        return len(warnings) == 0, warnings
    
    def update_from_feedback(self, feedback: Dict[str, Any]) -> None:
        """Update safety parameters based on feedback from autonomous operations."""
        feedback_type = feedback.get("type")
        success = feedback.get("success", False)
        
        if feedback_type == "autonomous_operation" and not success:
            # Reduce autonomy level after failure
            self.config["autonomy_level"] = max(0.0, self.config["autonomy_level"] - 0.1)
            self.config["confidence_requirement"] = min(1.0, self.config["confidence_requirement"] + 0.05)
        
        elif feedback_type == "autonomous_operation" and success:
            # Increase autonomy level after success
            self.config["autonomy_level"] = min(1.0, self.config["autonomy_level"] + 0.05)
            self.config["confidence_requirement"] = max(0.0, self.config["confidence_requirement"] - 0.02)
        
        self.save_config()
        
        # Log feedback adaptation
        log_audit_event(
            "feedback_adaptation",
            "safety_system",
            "parameter_update",
            "OK",
            {"feedback_type": feedback_type, "success": success},
            self.audit_log_path
        )


class AutonomousCodingManager:
    """Manages autonomous coding feedback loops and capabilities."""
    
    def __init__(self, audit_log_path: Path):
        self.audit_log_path = audit_log_path
        self.feedback_log_path = BASE_DIR / "artifacts" / "metrics" / "H027-autonomous-feedback.json"
        self.operation_history = []
        self.load_feedback_history()
    
    def load_feedback_history(self) -> None:
        """Load operation history from feedback log."""
        try:
            with open(self.feedback_log_path, 'r') as f:
                self.operation_history = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.operation_history = []
    
    def save_feedback_history(self) -> None:
        """Save operation history to feedback log."""
        self.feedback_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.feedback_log_path, 'w') as f:
            json.dump(self.operation_history, f, indent=2)
    
    def record_operation(self, operation: Dict[str, Any]) -> None:
        """Record an autonomous coding operation for feedback analysis."""
        operation["timestamp"] = datetime.now(timezone.utc).isoformat()
        operation["id"] = f"auto_op_{len(self.operation_history) + 1}"
        
        self.operation_history.append(operation)
        self.save_feedback_history()
        
        # Log operation
        log_audit_event(
            "autonomous_coding_operation",
            operation.get("actor", "autonomous_system"),
            operation.get("type", "unknown"),
            "RECORDED",
            {"operation_id": operation["id"], "operation_type": operation.get("type")},
            self.audit_log_path
        )
    
    def analyze_feedback_patterns(self) -> Dict[str, Any]:
        """Analyze feedback patterns to improve autonomous coding performance."""
        if not self.operation_history:
            return {"message": "No operation history available"}
        
        # Calculate success rate
        success_count = sum(1 for op in self.operation_history if op.get("success", False))
        total_count = len(self.operation_history)
        success_rate = success_count / total_count if total_count > 0 else 0
        
        # Analyze by operation type
        type_analysis = {}
        for op in self.operation_history:
            op_type = op.get("type", "unknown")
            if op_type not in type_analysis:
                type_analysis[op_type] = {"count": 0, "success": 0}
            
            type_analysis[op_type]["count"] += 1
            if op.get("success", False):
                type_analysis[op_type]["success"] += 1
        
        # Calculate failure patterns
        recent_failures = [op for op in self.operation_history[-10:] if not op.get("success", False)]
        
        return {
            "total_operations": total_count,
            "success_rate": success_rate,
            "type_analysis": type_analysis,
            "recent_failures": len(recent_failures),
            "recommendations": self._generate_recommendations(type_analysis, recent_failures)
        }
    
    def _generate_recommendations(self, type_analysis: Dict[str, Any], recent_failures: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement recommendations based on analysis."""
        recommendations = []
        
        for op_type, stats in type_analysis.items():
            if stats["count"] > 0:
                success_rate = stats["success"] / stats["count"]
                if success_rate < 0.5:  # Less than 50% success rate
                    recommendations.append(f"Review and improve {op_type} operations (success rate: {success_rate:.2f})")
        
        if len(recent_failures) > 3:
            recommendations.append("High recent failure rate - consider reducing autonomy temporarily")
        
        if not recommendations:
            recommendations.append("Autonomous coding performance is acceptable")
        
        return recommendations
    
    def validate_autonomous_operation(self, operation: Dict[str, Any], safety_rails: SafetyRailManager) -> Tuple[bool, List[str]]:
        """Validate an autonomous operation against safety constraints."""
        warnings = []
        
        # Check operation type
        valid_operations = [
            "code_generation",
            "file_modification",
            "proposal_creation", 
            "validation_check",
            "system_optimization"
        ]
        
        if operation.get("type") not in valid_operations:
            warnings.append(f"Invalid autonomous operation type: {operation.get('type')}")
        
        # Check required fields
        required_fields = ["type", "description", "expected_output"]
        for field in required_fields:
            if field not in operation:
                warnings.append(f"Missing required field: {field}")
        
        # Apply safety rail evaluation
        safe, safety_warnings = safety_rails.evaluate_safety_rails(operation, operation.get("actor", "autonomous_system"))
        warnings.extend(safety_warnings)
        
        # Log validation
        log_audit_event(
            "autonomous_operation_validation",
            operation.get("actor", "autonomous_system"),
            operation.get("type", "unknown"),
            "OK" if safe and not warnings else "WARNING",
            {"warnings": warnings, "safety_check": safe},
            self.audit_log_path
        )
        
        return safe and len(warnings) == 0, warnings


def cmd_enhanced_validation(args: argparse.Namespace) -> None:
    """Run enhanced validation with safety rails and autonomous coding capabilities."""
    print("Running H027 Enhanced Validation with AI Safety Rails...")
    
    # Convert string paths to Path objects
    audit_log_path = Path(args.audit_log)
    
    # Initialize managers
    safety_rails = SafetyRailManager(audit_log_path)
    autonomous_manager = AutonomousCodingManager(audit_log_path)
    
    # Load proposed operation (from file or stdin)
    if args.operation_file:
        with open(args.operation_file, 'r') as f:
            operation = json.load(f)
    else:
        operation = json.loads(args.operation_json)
    
    # Validate operation
    safe, warnings = autonomous_manager.validate_autonomous_operation(operation, safety_rails)
    
    # Analyze feedback patterns
    analysis = autonomous_manager.analyze_feedback_patterns()
    
    # Display results
    print(f"\nOperation Type: {operation.get('type', 'unknown')}")
    print(f"Validation Result: {'PASS' if safe else 'FAIL'}")
    
    if warnings:
        print("\nWarnings:")
        for warning in warnings:
            print(f"  - {warning}")
    
    print(f"\nFeedback Analysis:")
    print(f"  Total Operations: {analysis.get('total_operations', 0)}")
    print(f"  Success Rate: {analysis.get('success_rate', 0):.2f}")
    
    recommendations = analysis.get('recommendations', [])
    if recommendations:
        print("\nRecommendations:")
        for rec in recommendations:
            print(f"  - {rec}")
    
    if not safe:
        print("\n[X] Operation failed validation - cannot proceed")
        raise SystemExit(1)


def cmd_record_operation(args: argparse.Namespace) -> None:
    """Record an autonomous operation for feedback analysis."""
    print("Recording autonomous operation...")
    
    # Convert string paths to Path objects
    audit_log_path = Path(args.audit_log)
    
    # Load operation data
    if args.operation_file:
        with open(args.operation_file, 'r') as f:
            operation = json.load(f)
    else:
        operation = json.loads(args.operation_json)
    
    # Add success status
    operation["success"] = args.success
    
    # Initialize managers
    safety_rails = SafetyRailManager(audit_log_path)
    autonomous_manager = AutonomousCodingManager(audit_log_path)
    
    # Record the operation
    autonomous_manager.record_operation(operation)
    
    # Update safety rails from feedback
    safety_rails.update_from_feedback({
        "type": "autonomous_operation",
        "success": args.success
    })
    
    print(f"Operation recorded successfully: {operation.get('id')}")
    print(f"Status: {'SUCCESS' if args.success else 'FAILED'}")


def cmd_analyze_feedback(args: argparse.Namespace) -> None:
    """Analyze autonomous coding feedback patterns."""
    print("Analyzing autonomous coding feedback patterns...")
    
    # Convert string paths to Path objects
    audit_log_path = Path(args.audit_log)
    
    # Initialize managers
    autonomous_manager = AutonomousCodingManager(audit_log_path)
    
    # Analyze feedback patterns
    analysis = autonomous_manager.analyze_feedback_patterns()
    
    # Display detailed analysis
    print("\n=== AUTONOMOUS CODING FEEDBACK ANALYSIS ===")
    
    total_ops = analysis.get("total_operations", 0)
    success_rate = analysis.get("success_rate", 0)
    
    print(f"Total Operations: {total_ops}")
    print(f"Success Rate: {success_rate:.2%}")
    print(f"Recent Failures: {analysis.get('recent_failures', 0)}")
    
    # Type analysis
    type_analysis = analysis.get("type_analysis", {})
    if type_analysis:
        print("\n--- Operation Type Analysis ---")
        for op_type, stats in type_analysis.items():
            rate = stats["success"] / stats["count"] if stats["count"] > 0 else 0
            print(f"{op_type}: {stats['success']}/{stats['count']} successful ({rate:.2%})")
    
    # Recommendations
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        print("\n--- Recommendations ---")
        for rec in recommendations:
            print(f"  • {rec}")
    
    if total_ops == 0:
        print("\nNo autonomous operations recorded yet.")


def main() -> None:
    args = parse_args()
    try:
        args.func(args)
    except SafetyViolation as exc:
        print(f"SAFETY VIOLATION: {exc}", file=sys.stderr)
        raise SystemExit(1)
    except ConstraintValidationError as exc:
        print(f"VALIDATION ERROR: {exc}", file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()
