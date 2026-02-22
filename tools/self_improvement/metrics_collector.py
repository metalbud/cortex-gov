"""Collect execution metrics for Cortex GOV tasks and generate aggregated summaries."""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parents[2]
PROJECT_PATH = BASE_DIR / "PROJECT.md"
METRICS_DIR = BASE_DIR / "artifacts" / "metrics"
LOG_PATH = METRICS_DIR / "H008-metrics-log.json"
SUMMARY_PATH = METRICS_DIR / "H008-metrics-summary.md"

TASK_SECTION_SPLIT = r"\n---\n\n"
TASK_HEADER_REGEX = re.compile(r"### (?P<key>H\d+): (?P<title>.+)")
STATUS_LINE_RE = re.compile(r"Status: (\w+)", flags=re.IGNORECASE)
PRIORITY_LINE_RE = re.compile(r"Priority: (\w+)" , flags=re.IGNORECASE)
OWNER_LINE_RE = re.compile(r"Owner: (?P<owner>\w+)", flags=re.IGNORECASE)
WORK_ITEM_RE = re.compile(r"- \[[ xX]\] (?P<item>.+)")


def ensure_metrics_dirs() -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)


def clean_line(line: str) -> str:
    return line.strip().rstrip("\\n").strip()


def parse_tasks() -> List[Dict[str, Any]]:
    text = PROJECT_PATH.read_text()
    raw_sections = re.split(TASK_SECTION_SPLIT, text)
    tasks: List[Dict[str, Any]] = []

    for section in raw_sections:
        section = section.strip()
        if not section.startswith("### H"):
            continue

        lines = [clean_line(line) for line in section.splitlines() if clean_line(line)]
        header = lines[0]
        header_match = TASK_HEADER_REGEX.match(header)
        if not header_match:
            continue

        key = header_match.group("key")
        title = header_match.group("title")
        status = next((m.group(1) for l in lines if (m := STATUS_LINE_RE.match(l))), "UNKNOWN")
        priority = next((m.group(1) for l in lines if (m := PRIORITY_LINE_RE.match(l))), "UNSPECIFIED")
        owner = next((m.group("owner") for l in lines if (m := OWNER_LINE_RE.match(l))), "unknown")
        work_items = [m.group("item") for l in lines if (m := WORK_ITEM_RE.match(l))]

        tasks.append(
            {
                "key": key,
                "title": title,
                "status": status.upper(),
                "priority": priority.upper(),
                "owner": owner,
                "workItems": work_items,
                "snapshot": "\n".join(lines[: min(len(lines), 8)]),
            }
        )

    return tasks


def capture_metrics() -> Dict[str, Any]:
    ensure_metrics_dirs()
    tasks = parse_tasks()
    timestamp = datetime.utcnow().isoformat() + "Z"
    entry = {
        "capturedAt": timestamp,
        "taskCount": len(tasks),
        "tasks": tasks,
    }

    if LOG_PATH.exists():
        existing = json.loads(LOG_PATH.read_text())
    else:
        existing = []

    existing.append(entry)
    LOG_PATH.write_text(json.dumps(existing, indent=2))
    return entry


def aggregate_metrics(entries: List[Dict[str, Any]]) -> Dict[str, Any]:
    flattened = [task for entry in entries for task in entry.get("tasks", [])]
    if not flattened:
        return {"summary": "No task metrics collected yet."}

    statuses = [task["status"] for task in flattened]
    status_counts = Counter(statuses)
    latest_per_task: Dict[str, Dict[str, Any]] = {}
    for task in flattened:
        latest_per_task[task["key"]] = task

    summary = {
        "totalTasks": len(latest_per_task),
        "statusCounts": dict(status_counts),
        "latest": sorted(
            [
                {
                    "key": task["key"],
                    "status": task["status"],
                    "title": task["title"],
                    "priority": task["priority"],
                }
                for task in latest_per_task.values()
            ],
            key=lambda x: x["key"],
        ),
    }
    summary["mostRecentCapture"] = entries[-1]["capturedAt"]
    return summary


def render_summary(summary: Dict[str, Any]) -> str:
    lines = ["# H008 Execution Metrics Snapshot", ""]
    if summary.get("summary"):
        lines.append(summary["summary"])
        return "\n".join(lines)

    lines.append(f"Snapshot generated at: {datetime.utcnow().isoformat()}Z")
    lines.append(f"Most recent capture: {summary.get('mostRecentCapture')}\n")
    lines.append("## Task distribution")
    lines.append("| Status | Count |")
    lines.append("| --- | ---: |")
    for status, count in summary.get("statusCounts", {}).items():
        lines.append(f"| {status} | {count} |")

    lines.append("\n## Latest known statuses")
    lines.append("| Task | Status | Priority | Title |")
    lines.append("| --- | --- | --- | --- |")
    for task in summary.get("latest", []):
        lines.append(
            f"| {task['key']} | {task['status']} | {task['priority']} | {task['title']} |"
        )

    return "\n".join(lines)


def write_summary(summary: Dict[str, Any]) -> Path:
    ensure_metrics_dirs()
    content = render_summary(summary)
    SUMMARY_PATH.write_text(content)
    return SUMMARY_PATH


def load_log() -> List[Dict[str, Any]]:
    if not LOG_PATH.exists():
        return []
    return json.loads(LOG_PATH.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description="Brings Cortex GOV project metrics into view.")
    parser.add_argument("--capture", action="store_true", help="Capture the latest task snapshot into the metrics log.")
    parser.add_argument("--summary", action="store_true", help="Generate a human-readable summary from logged snapshots.")
    args = parser.parse_args()

    if not args.capture and not args.summary:
        parser.error("At least one of --capture or --summary must be supplied.")

    if args.capture:
        entry = capture_metrics()
        print(f"Captured {entry['taskCount']} tasks at {entry['capturedAt']}")

    if args.summary:
        log = load_log()
        summary = aggregate_metrics(log)
        path = write_summary(summary)
        print(f"Summary written to {path}")


if __name__ == "__main__":
    main()
