"""Error detection, classification, and recovery for cortex-gov."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from typing import Dict, List

if __package__ is None:  # allow running as a script
    sys.path.append(os.path.dirname(__file__))
    from recovery_procedures import RECOVERY_MAP
else:
    from .recovery_procedures import RECOVERY_MAP


ERROR_CLASSES = {
    "api_latency_spike": "api_latency",
    "disk_space_low": "disk_full",
    "memory_leak": "memory_pressure",
    "process_crash": "process_crash",
    "artifact_corruption": "data_corruption",
    "config_schema_violation": "config_invalid",
    "network_timeout": "network_timeout",
}


def classify_error(error: Dict) -> Dict:
    kind = error.get("kind")
    category = ERROR_CLASSES.get(kind, "unknown")
    severity = error.get("severity", "medium")
    auto_recover = category in RECOVERY_MAP
    return {
        "kind": kind,
        "category": category,
        "severity": severity,
        "auto_recover": auto_recover,
        "timestamp": error.get("timestamp"),
    }


def recover_error(classification: Dict, context: Dict) -> Dict:
    category = classification["category"]
    if category not in RECOVERY_MAP:
        return {
            "category": category,
            "success": False,
            "actions": [],
            "notes": "No automated recovery available.",
        }
    result = RECOVERY_MAP[category](context)
    return {
        "category": result.category,
        "success": result.success,
        "actions": result.actions,
        "notes": result.notes,
    }


def simulate_failures() -> List[Dict]:
    now = datetime.now(timezone.utc).isoformat()
    return [
        {"kind": "api_latency_spike", "severity": "medium", "timestamp": now},
        {"kind": "disk_space_low", "severity": "high", "timestamp": now},
        {"kind": "memory_leak", "severity": "high", "timestamp": now},
        {"kind": "process_crash", "severity": "critical", "timestamp": now},
        {"kind": "artifact_corruption", "severity": "high", "timestamp": now},
        {"kind": "config_schema_violation", "severity": "medium", "timestamp": now},
        {"kind": "network_timeout", "severity": "medium", "timestamp": now},
    ]


def run_simulation(output_path: str) -> Dict:
    errors = simulate_failures()
    results = []
    for error in errors:
        classification = classify_error(error)
        recovery = recover_error(classification, context={"error": error})
        results.append({
            "error": error,
            "classification": classification,
            "recovery": recovery,
        })

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total": len(results),
        "results": results,
    }
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Cortex-GOV error handler")
    parser.add_argument("--simulate", action="store_true", help="Run simulated failure detection")
    parser.add_argument("--output", default="cortex-gov/artifacts/metrics/H017-error-simulation-test.json")
    args = parser.parse_args()

    if args.simulate:
        payload = run_simulation(args.output)
        print(f"Simulated {payload['total']} failures")
        print(f"Results written to {args.output}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
