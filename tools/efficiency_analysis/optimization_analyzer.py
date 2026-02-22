import argparse
import json
import os
from datetime import datetime, timezone
from collections import defaultdict

DEFAULT_METRICS_LOG = os.path.join("cortex-gov", "artifacts", "metrics", "H008-metrics-log.json")
DEFAULT_OUTPUT = os.path.join("cortex-gov", "artifacts", "analysis", "H018-efficiency-baseline.json")

ISO_FORMATS = [
    "%Y-%m-%dT%H:%M:%S.%fZ",
    "%Y-%m-%dT%H:%M:%SZ",
    "%Y-%m-%dT%H:%M:%S.%f%z",
    "%Y-%m-%dT%H:%M:%S%z",
]


def parse_timestamp(value):
    if not value:
        return None
    for fmt in ISO_FORMATS:
        try:
            return datetime.strptime(value, fmt).astimezone(timezone.utc)
        except ValueError:
            continue
    try:
        return datetime.fromisoformat(value).astimezone(timezone.utc)
    except ValueError:
        return None


def load_metrics(log_path):
    with open(log_path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_proposals(proposals_dir):
    proposals = []
    if not os.path.isdir(proposals_dir):
        return proposals
    for name in os.listdir(proposals_dir):
        if not name.endswith(".json"):
            continue
        if name == "proposals.json":
            continue
        path = os.path.join(proposals_dir, name)
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
            if isinstance(data, dict) and "proposals" in data:
                for proposal in data.get("proposals", []):
                    proposal["__source_file"] = path
                proposals.extend(data.get("proposals", []))
        except Exception:
            continue
    return proposals


def summarize_metrics(captures):
    summary = {
        "captures": len(captures),
        "firstCaptureAt": None,
        "lastCaptureAt": None,
        "tasks": {},
    }
    if not captures:
        return summary
    first_ts = parse_timestamp(captures[0]["capturedAt"])
    last_ts = parse_timestamp(captures[-1]["capturedAt"])
    summary["firstCaptureAt"] = first_ts.isoformat() if first_ts else captures[0]["capturedAt"]
    summary["lastCaptureAt"] = last_ts.isoformat() if last_ts else captures[-1]["capturedAt"]

    task_timelines = defaultdict(list)
    for capture in captures:
        ts = parse_timestamp(capture["capturedAt"])
        for task in capture.get("tasks", []):
            task_timelines[task["key"]].append({
                "timestamp": ts,
                "status": task.get("status"),
                "title": task.get("title"),
                "priority": task.get("priority"),
            })

    task_stats = {}
    for key, events in task_timelines.items():
        events_sorted = sorted(events, key=lambda e: e["timestamp"] or datetime.min.replace(tzinfo=timezone.utc))
        first_seen = events_sorted[0]
        first_in_progress = next((e for e in events_sorted if e["status"] == "IN_PROGRESS"), None)
        first_done = next((e for e in events_sorted if e["status"] == "DONE"), None)
        last_event = events_sorted[-1]
        todo_duration = None
        in_progress_duration = None
        if first_in_progress and first_seen["timestamp"] and first_in_progress["timestamp"]:
            todo_duration = (first_in_progress["timestamp"] - first_seen["timestamp"]).total_seconds()
        if first_done and first_in_progress and first_done["timestamp"] and first_in_progress["timestamp"]:
            in_progress_duration = (first_done["timestamp"] - first_in_progress["timestamp"]).total_seconds()
        task_stats[key] = {
            "title": first_seen.get("title"),
            "priority": first_seen.get("priority"),
            "firstSeenAt": first_seen["timestamp"].isoformat() if first_seen["timestamp"] else None,
            "firstInProgressAt": first_in_progress["timestamp"].isoformat() if first_in_progress and first_in_progress["timestamp"] else None,
            "firstDoneAt": first_done["timestamp"].isoformat() if first_done and first_done["timestamp"] else None,
            "lastStatus": last_event.get("status"),
            "todoLagSeconds": todo_duration,
            "inProgressDurationSeconds": in_progress_duration,
        }
    summary["tasks"] = task_stats
    return summary


def analyze_proposals(proposals):
    results = {
        "count": len(proposals),
        "approvalDurationsSeconds": [],
        "implementationDurationsSeconds": [],
        "missingApprovalCount": 0,
        "missingImplementationCount": 0,
    }
    for proposal in proposals:
        proposed_at = parse_timestamp(proposal.get("proposedAt") or proposal.get("createdAt"))
        approved_at = parse_timestamp(proposal.get("humanGate", {}).get("approvedAt"))
        implemented_at = parse_timestamp(proposal.get("implementation", {}).get("implementedAt"))
        if approved_at and proposed_at:
            results["approvalDurationsSeconds"].append((approved_at - proposed_at).total_seconds())
        else:
            results["missingApprovalCount"] += 1
        if implemented_at and approved_at:
            results["implementationDurationsSeconds"].append((implemented_at - approved_at).total_seconds())
        else:
            results["missingImplementationCount"] += 1
    return results


def percentile(values, pct):
    if not values:
        return None
    values_sorted = sorted(values)
    idx = int(round((pct / 100.0) * (len(values_sorted) - 1)))
    return values_sorted[idx]


def derive_bottlenecks(summary, proposals):
    bottlenecks = []
    tasks = summary.get("tasks", {})
    long_todo = [(k, v) for k, v in tasks.items() if v.get("todoLagSeconds")]
    long_todo = sorted(long_todo, key=lambda item: item[1]["todoLagSeconds"], reverse=True)
    if long_todo:
        key, data = long_todo[0]
        bottlenecks.append({
            "type": "TODO_LAG",
            "task": key,
            "title": data.get("title"),
            "seconds": data.get("todoLagSeconds"),
            "note": "Longest time between first seen and IN_PROGRESS.",
        })

    long_in_progress = [(k, v) for k, v in tasks.items() if v.get("inProgressDurationSeconds")]
    long_in_progress = sorted(long_in_progress, key=lambda item: item[1]["inProgressDurationSeconds"], reverse=True)
    if long_in_progress:
        key, data = long_in_progress[0]
        bottlenecks.append({
            "type": "IN_PROGRESS_DURATION",
            "task": key,
            "title": data.get("title"),
            "seconds": data.get("inProgressDurationSeconds"),
            "note": "Longest IN_PROGRESS duration before DONE.",
        })

    proposal_stats = analyze_proposals(proposals)
    if proposal_stats["missingApprovalCount"]:
        bottlenecks.append({
            "type": "PROPOSAL_APPROVAL_GAP",
            "count": proposal_stats["missingApprovalCount"],
            "note": "Proposals missing approval timestamps; slows efficiency metrics.",
        })
    if proposal_stats["missingImplementationCount"]:
        bottlenecks.append({
            "type": "PROPOSAL_IMPLEMENTATION_GAP",
            "count": proposal_stats["missingImplementationCount"],
            "note": "Approved proposals missing implementation timestamps.",
        })
    return bottlenecks


def build_dashboard(summary, proposals):
    tasks = summary.get("tasks", {})
    total_tasks = len(tasks)
    done_tasks = len([t for t in tasks.values() if t.get("lastStatus") == "DONE"])
    avg_todo = [t.get("todoLagSeconds") for t in tasks.values() if t.get("todoLagSeconds")]
    avg_progress = [t.get("inProgressDurationSeconds") for t in tasks.values() if t.get("inProgressDurationSeconds")]
    proposal_stats = analyze_proposals(proposals)
    avg_approval = sum(proposal_stats["approvalDurationsSeconds"]) / len(proposal_stats["approvalDurationsSeconds"]) if proposal_stats["approvalDurationsSeconds"] else None

    lines = [
        "# H018 Efficiency Dashboard",
        "",
        "## Task Throughput",
        f"- Total tasks tracked: **{total_tasks}**",
        f"- DONE tasks: **{done_tasks}**",
        "",
        "## Cycle Timing",
        f"- Avg TODO lag (sec): **{round(sum(avg_todo) / len(avg_todo), 2) if avg_todo else 'n/a'}**",
        f"- Avg IN_PROGRESS duration (sec): **{round(sum(avg_progress) / len(avg_progress), 2) if avg_progress else 'n/a'}**",
        f"- 90th percentile TODO lag (sec): **{round(percentile(avg_todo, 90), 2) if avg_todo else 'n/a'}**",
        f"- 90th percentile IN_PROGRESS duration (sec): **{round(percentile(avg_progress, 90), 2) if avg_progress else 'n/a'}**",
        "",
        "## Proposal Flow",
        f"- Proposals tracked: **{proposal_stats['count']}**",
        f"- Avg approval time (sec): **{round(avg_approval, 2) if avg_approval else 'n/a'}**",
        f"- Proposals missing approval: **{proposal_stats['missingApprovalCount']}**",
        f"- Proposals missing implementation: **{proposal_stats['missingImplementationCount']}**",
        "",
        "Generated at: " + datetime.now(timezone.utc).isoformat(),
    ]
    return "\n".join(lines)


def write_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)


def write_text(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


def main():
    parser = argparse.ArgumentParser(description="Analyze recursive governance efficiency and bottlenecks")
    parser.add_argument("--metrics-log", default=DEFAULT_METRICS_LOG)
    parser.add_argument("--proposals-dir", default=os.path.join("cortex-gov", "artifacts", "proposals"))
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--map-bottlenecks", action="store_true")
    parser.add_argument("--strategies", action="store_true")
    parser.add_argument("--dashboard", action="store_true")
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--bottleneck-output", default=os.path.join("cortex-gov", "artifacts", "analysis", "H018-bottleneck-map.md"))
    parser.add_argument("--strategy-output", default=os.path.join("cortex-gov", "artifacts", "analysis", "H018-optimization-strategies.md"))
    parser.add_argument("--dashboard-output", default=os.path.join("cortex-gov", "artifacts", "analysis", "H018-efficiency-dashboard.md"))
    args = parser.parse_args()

    captures = load_metrics(args.metrics_log)
    proposals = load_proposals(args.proposals_dir)
    summary = summarize_metrics(captures)

    if args.analyze:
        baseline = {
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "metricsLog": args.metrics_log,
            "taskSummary": summary,
            "proposalSummary": analyze_proposals(proposals),
        }
        write_json(args.output, baseline)
        print(f"Efficiency analysis completed, results saved to {args.output}")

    if args.map_bottlenecks:
        bottlenecks = derive_bottlenecks(summary, proposals)
        lines = ["# H018 Bottleneck Map", "", "## Bottlenecks"]
        if not bottlenecks:
            lines.append("- No bottlenecks detected with current thresholds.")
        else:
            for item in bottlenecks:
                if item.get("task"):
                    lines.append(f"- **{item['type']}**: {item['task']} — {item.get('title')} ({item.get('seconds')}s). {item.get('note')}")
                else:
                    lines.append(f"- **{item['type']}**: {item.get('count')} occurrences. {item.get('note')}")
        lines.append("")
        lines.append("Generated at: " + datetime.now(timezone.utc).isoformat())
        write_text(args.bottleneck_output, "\n".join(lines))
        print(f"Bottleneck map created, saved to {args.bottleneck_output}")

    if args.strategies:
        strategies = [
            "Prioritize starting tasks within one capture window to reduce TODO lag.",
            "Require proposal approval timestamps to unblock implementation metrics.",
            "Add auto-capture after task status changes to reduce stale intervals.",
            "Introduce explicit implementation time logging for proposals.",
            "Batch verification steps to minimize IN_PROGRESS stalls.",
        ]
        lines = ["# H018 Optimization Strategies", "", "## Ranked Strategies"]
        for idx, strategy in enumerate(strategies, 1):
            lines.append(f"{idx}. {strategy}")
        lines.append("")
        lines.append("Generated at: " + datetime.now(timezone.utc).isoformat())
        write_text(args.strategy_output, "\n".join(lines))
        print(f"Optimization strategies saved to {args.strategy_output}")

    if args.dashboard:
        dashboard = build_dashboard(summary, proposals)
        write_text(args.dashboard_output, dashboard)
        print(f"Efficiency dashboard saved to {args.dashboard_output}")


if __name__ == "__main__":
    main()
