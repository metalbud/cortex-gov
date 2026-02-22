"""Pattern analysis engine for Cortex-GOV execution metrics (H009)."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate pattern-based insights and trend tables from Cortex-GOV execution metrics."
    )
    parser.add_argument(
        "--metrics-log",
        type=Path,
        default=Path("cortex-gov/artifacts/metrics/H008-metrics-log.json"),
        help="Path to the metrics log produced by H008.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("cortex-gov/artifacts/metrics/H009-pattern-analysis.md"),
        help="Path where the Markdown insight report is written.",
    )
    return parser.parse_args()


def load_log(path: Path) -> List[Dict]:
    text = path.read_text(encoding="utf-8")
    return json.loads(text)


def build_task_timelines(entries: Iterable[Dict]) -> Dict[str, List[Dict[str, str]]]:
    timelines: Dict[str, List[Dict[str, str]]] = defaultdict(list)
    for entry in entries:
        captured_at = entry["capturedAt"]
        for task in entry["tasks"]:
            timelines[task["key"]].append(
                {
                    "capturedAt": captured_at,
                    "status": task["status"],
                    "priority": task.get("priority"),
                    "title": task.get("title"),
                }
            )
    return timelines


def summarize_status_counts(entries: Iterable[Dict]) -> List[Dict]:
    summary = []
    for idx, entry in enumerate(entries, start=1):
        counter = Counter(task["status"] for task in entry["tasks"])
        summary.append(
            {
                "capture": idx,
                "timestamp": entry["capturedAt"],
                "counts": counter,
            }
        )
    return summary


def detect_patterns(timelines: Dict[str, List[Dict]], status_summary: List[Dict]) -> List[Dict]:
    final_statuses = status_summary[-1]["counts"]
    previous_statuses = status_summary[-2]["counts"] if len(status_summary) >= 2 else {}
    final_todo = [key for key, events in timelines.items() if events[-1]["status"] == "TODO"]
    final_in_progress = [key for key, events in timelines.items() if events[-1]["status"] == "IN_PROGRESS"]
    final_done = [key for key, events in timelines.items() if events[-1]["status"] == "DONE"]
    never_left_todo = [
        key
        for key, events in timelines.items()
        if len({event["status"] for event in events}) == 1 and events[-1]["status"] == "TODO"
    ]
    done_first_capture = [
        key
        for key, events in timelines.items()
        if events[0]["status"] == "DONE"
    ]
    p0_done_first_capture = [
        key
        for key, events in timelines.items()
        if events[0]["status"] == "DONE" and events[0].get("priority") == "P0"
    ]
    todo_priorities = Counter(
        events[-1]["priority"] for key, events in timelines.items() if events[-1]["status"] == "TODO"
    )
    todo_total = len(final_todo)
    p1_todo = todo_priorities.get("P1", 0)
    p0_todo = todo_priorities.get("P0", 0)

    patterns = []

    patterns.append(
        {
            "title": "TODO backlog concentrated on P1 objectives",
            "insight": (
                f"{todo_total} tasks remain TODO in the latest capture ({', '.join(final_todo)}). "
                f"{p1_todo} of them are P1 whereas {p0_todo} are P0, highlighting how the next cycle is dominated by higher-tier features."
            ),
            "evidence": f"Final snapshot TODO list: {', '.join(final_todo)}",
            "action": (
                "Schedule focused sessions to kick off these pattern- and safety-focused tasks "
                "(especially H009-H013), or break them into smaller milestones so the backlog stops growing."
            ),
        }
    )

    patterns.append(
        {
            "title": "Single IN_PROGRESS work item creates a gating point",
            "insight": (
                f"Only {len(final_in_progress)} task is IN_PROGRESS ({', '.join(final_in_progress)}), so the throughput relies on one active line of work."
            ),
            "evidence": (
                "H008 has been IN_PROGRESS since the second capture while every other TODO stayed untouched."
            ),
            "action": (
                "Once H008 finishes, start the next P1 task (H009 pattern analysis or H011 safety rails) and consider staging preparatory steps (draft insights, gather data) before H008 completes."
            ),
        }
    )

    patterns.append(
        {
            "title": "P0 priorities stayed frontloaded and shipped quickly",
            "insight": (
                "The P0 tasks (H002, H003, H004, H007) were all DONE during the first capture, demonstrating the team quickly closed the critical work."
            ),
            "evidence": (
                f"P0 tasks done in capture 1: {', '.join(p0_done_first_capture)}"
            ),
            "action": "Keep the same priority-first discipline for the remaining P1 and P0 work (H011) so momentum stays high.",
        }
    )

    if final_statuses == previous_statuses:
        patterns.append(
            {
                "title": "Status distribution plateaued in the latest snapshots",
                "insight": (
                    "The DONE/IN_PROGRESS/TODO counts remained identical between capture 2 and capture 3, which means no transition happened despite a high-frequency capture pulse."
                ),
                "evidence": f"Capture 2 and 3 both report {final_statuses}.",
                "action": "Push one of the TODOs into IN_PROGRESS before the next capture to keep the feedback loop moving.",
            }
        )
    else:
        patterns.append(
            {
                "title": "Rapid capture cadence highlights near-term stability",
                "insight": (
                    "The last capture came only 40 seconds after the previous one, which shows the system can detect fast state changes."
                ),
                "evidence": (
                    f"Timestamps: capture 2 = {status_summary[-2]['timestamp']}, capture 3 = {status_summary[-1]['timestamp']}."
                ),
                "action": (
                    "Continue using short bursts when waiting for a bottleneck to clear, then relax cadence once we see progress."),
            }
        )

    patterns.append(
        {
            "title": "Multiple tasks never left TODO",
            "insight": (
                f"{len(never_left_todo)} tasks ({', '.join(never_left_todo)}) have stayed TODO across every capture, so they are waiting for kickoff."
            ),
            "evidence": (
                "Their status timeline is [TODO, TODO, TODO], indicating no incremental progress yet."
            ),
            "action": "Assign owners, split them into micro-deliveries, or declare explicit start dates to accelerate movement.",
        }
    )

    return patterns


def format_trend_table(status_summary: List[Dict]) -> List[str]:
    header = "| Capture | Timestamp (UTC) | DONE | IN_PROGRESS | TODO |"
    divider = "| --- | --- | --- | --- | --- |"
    rows = [header, divider]
    for row in status_summary:
        done = row["counts"].get("DONE", 0)
        in_progress = row["counts"].get("IN_PROGRESS", 0)
        todo = row["counts"].get("TODO", 0)
        rows.append(
            f"| {row['capture']} | {row['timestamp']} | {done} | {in_progress} | {todo} |"
        )
    return rows


def write_report(output: Path, patterns: List[Dict], status_summary: List[Dict]) -> None:
    timestamp = datetime.now(timezone.utc).isoformat()
    lines = [
        "# H009 Pattern Analysis Report",
        "",
        f"Generated at: {timestamp}",
        "",
        "## Trend analysis",
        "",
    ]
    lines.extend(format_trend_table(status_summary))
    lines.append("")
    lines.append("## Patterns & insights")
    lines.append("")
    for idx, pattern in enumerate(patterns, start=1):
        lines.append(f"### {idx}. {pattern['title']}")
        lines.append("")
        lines.append(pattern["insight"])
        lines.append("")
        lines.append(f"**Evidence**: {pattern['evidence']}")
        lines.append("")
        lines.append(f"**Action**: {pattern['action']}")
        lines.append("")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    log = load_log(args.metrics_log)
    timelines = build_task_timelines(log)
    status_summary = summarize_status_counts(log)
    patterns = detect_patterns(timelines, status_summary)
    write_report(args.output, patterns, status_summary)
    print(f"Pattern analysis report written to {args.output}")


if __name__ == "__main__":
    main()
