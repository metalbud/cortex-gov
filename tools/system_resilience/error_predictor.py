#!/usr/bin/env python3
"""
Cortex-GOV H017 Error Prediction and Prevention

Analyzes historical metrics to predict potential system issues and recommend
preventive actions.
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import statistics


def load_metrics(log_paths: List[Path]) -> List[Dict[str, Any]]:
    metrics = []
    for path in log_paths:
        if path.exists():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "metrics" in data:
                    metrics.append(data["metrics"])
                elif isinstance(data, list):
                    metrics.extend(data)
            except Exception:
                continue
    return metrics


def extract_series(metrics: List[Dict[str, Any]], key_path: List[str]) -> List[float]:
    values = []
    for entry in metrics:
        cursor = entry
        for key in key_path:
            if not isinstance(cursor, dict) or key not in cursor:
                cursor = None
                break
            cursor = cursor[key]
        if isinstance(cursor, (int, float)):
            values.append(float(cursor))
    return values


def predict_trends(metrics: List[Dict[str, Any]]) -> Dict[str, Any]:
    predictions = []
    
    memory_series = extract_series(metrics, ["memory", "usage_percent"])
    cpu_series = extract_series(metrics, ["cpu", "usage_percent"])
    disk_series = extract_series(metrics, ["disk", "usage_percent"])
    
    def analyze(series: List[float], label: str, threshold: float) -> None:
        if len(series) < 2:
            return
        slope = series[-1] - series[0]
        avg = statistics.mean(series)
        latest = series[-1]
        if latest > threshold or slope > 5:
            predictions.append({
                "type": f"PREDICTED_{label.upper()}_ISSUE",
                "confidence": "high" if latest > threshold else "medium",
                "description": f"{label.title()} usage trending high (avg={avg:.1f}, latest={latest:.1f})",
                "recommended_action": f"Review {label} usage and apply cleanup",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })

    analyze(memory_series, "memory", 85)
    analyze(cpu_series, "cpu", 80)
    analyze(disk_series, "disk", 90)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "metrics_analyzed": len(metrics),
        "predictions": predictions,
        "summary": {
            "memory_samples": len(memory_series),
            "cpu_samples": len(cpu_series),
            "disk_samples": len(disk_series),
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Cortex-GOV H017 Error Predictor")
    parser.add_argument("--analyze", action="store_true", help="Analyze historical metrics")
    parser.add_argument("--log", action="append", help="Metrics log path (repeatable)")
    parser.add_argument("--output", type=str, help="Output file path for predictions")
    args = parser.parse_args()

    if not args.analyze:
        parser.print_help()
        return

    log_paths = [Path(p) for p in (args.log or [])]
    if not log_paths:
        print("No log paths provided.")
        return

    metrics = load_metrics(log_paths)
    report = predict_trends(metrics)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        print(f"Prediction report saved to {args.output}")
    else:
        print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
