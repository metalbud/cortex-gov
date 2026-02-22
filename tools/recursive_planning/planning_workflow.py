#!/usr/bin/env python3
"""
Recursive Planning Workflow Integration (H021)

Integrates trend context (H013), pattern analysis (H009), and proposal drafting
into a cohesive recursive planning workflow with auditable artifacts.
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parents[2]


def resolve_workspace_path(raw_workspace: str = None) -> Path:
    if raw_workspace:
        return Path(raw_workspace).resolve()
    return BASE_DIR


class RecursivePlanningWorkflow:
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.artifacts_dir = workspace_path / "artifacts"
        self.planning_dir = self.artifacts_dir / "planning"
        self.proposals_dir = self.artifacts_dir / "proposals"
        self.metrics_dir = self.artifacts_dir / "metrics"

        self.planning_dir.mkdir(parents=True, exist_ok=True)
        self.proposals_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)

    def trigger_planning_cycle(self, manual: bool = False) -> Dict[str, Any]:
        cycle_id = f"H021-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}"

        if manual:
            print(f"Manual planning cycle initiated: {cycle_id}")
        else:
            print(f"Automatic planning cycle triggered: {cycle_id}")

        trend_context = self._read_trend_context()
        pattern_analysis = self._read_pattern_analysis()
        metrics_summary = self._read_metrics_summary()

        proposals = self._generate_improvement_proposals(
            trend_context=trend_context,
            pattern_analysis=pattern_analysis,
            metrics_summary=metrics_summary,
            cycle_id=cycle_id,
        )

        planning_report = self._generate_planning_report(
            cycle_id=cycle_id,
            trend_context=trend_context,
            pattern_analysis=pattern_analysis,
            metrics_summary=metrics_summary,
            proposals=proposals,
        )

        cycle_payload = {
            "cycle_id": cycle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "manual": manual,
            "trend_context": trend_context,
            "pattern_analysis": pattern_analysis,
            "metrics_summary": metrics_summary,
            "proposals": proposals,
            "planning_report": planning_report,
        }

        return cycle_payload

    def _read_trend_context(self) -> Dict[str, Any]:
        trend_file = self.metrics_dir / "H013-planning-context.json"
        if trend_file.exists():
            with open(trend_file, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"keywords": [], "competitors": [], "pulse": None, "queries": []}

    def _read_pattern_analysis(self) -> Dict[str, Any]:
        pattern_json = self.artifacts_dir / "patterns" / "H009-pattern-analysis.json"
        if pattern_json.exists():
            with open(pattern_json, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            data = raw_data if isinstance(raw_data, dict) else {}
            patterns = data.get("patterns", [])
            bottlenecks = data.get("bottlenecks", [])
            insights = data.get("insights", [])
            return {
                "source": str(pattern_json),
                "format": "json",
                "raw": json.dumps(data, indent=2),
                "patterns": patterns if isinstance(patterns, list) else [],
                "bottlenecks": bottlenecks if isinstance(bottlenecks, list) else [],
                "insights": insights if isinstance(insights, list) else [],
            }

        legacy_paths = [
            self.metrics_dir / "H009-pattern-analysis.md",
            self.artifacts_dir / "patterns" / "H009-pattern-analysis.md",
        ]
        for pattern_md in legacy_paths:
            if pattern_md.exists():
                with open(pattern_md, "r", encoding="utf-8") as f:
                    text = f.read()
                return {
                    "source": str(pattern_md),
                    "format": "markdown",
                    "raw": text,
                    "patterns": [],
                    "bottlenecks": [],
                    "insights": [],
                }
        return {
            "source": None,
            "format": None,
            "raw": "",
            "patterns": [],
            "bottlenecks": [],
            "insights": [],
        }

    def _read_metrics_summary(self) -> Dict[str, Any]:
        metrics_log = self.metrics_dir / "H008-metrics-log.json"
        if not metrics_log.exists():
            return {"source": None, "summary": {}}

        with open(metrics_log, "r", encoding="utf-8") as f:
            data = json.load(f)

        status_counts: Dict[str, int] = {}
        total_tasks = 0

        if isinstance(data, list) and data:
            # Use the most recent capture entry
            latest_capture = data[-1]
            tasks = latest_capture.get("tasks", []) if isinstance(latest_capture, dict) else []
            total_tasks = len(tasks)
            for task in tasks:
                status = task.get("status", "UNKNOWN") if isinstance(task, dict) else "UNKNOWN"
                status_counts[status] = status_counts.get(status, 0) + 1
        elif isinstance(data, dict):
            # Legacy dict format
            total_tasks = len(data)
            for task_id, task_data in data.items():
                if not isinstance(task_data, dict):
                    continue
                history = task_data.get("status_history", [])
                if history:
                    current_status = history[-1].get("status", "UNKNOWN")
                    status_counts[current_status] = status_counts.get(current_status, 0) + 1

        return {
            "source": str(metrics_log),
            "summary": {
                "total_tasks": total_tasks,
                "status_counts": status_counts,
            },
        }

    def _generate_improvement_proposals(
        self,
        trend_context: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        metrics_summary: Dict[str, Any],
        cycle_id: str,
    ) -> List[Dict[str, Any]]:
        proposals: List[Dict[str, Any]] = []

        trend_keywords = trend_context.get("keywords", [])
        has_trends = len(trend_keywords) > 0
        pattern_text = pattern_analysis.get("raw", "")
        pattern_source = pattern_analysis.get("source") or "H009-pattern-analysis.json"
        pattern_evidence = Path(pattern_source).name
        stalled_patterns = [
            pattern
            for pattern in pattern_analysis.get("patterns", [])
            if isinstance(pattern, dict) and str(pattern.get("status", "")).lower() == "stalled"
        ]

        if has_trends:
            proposals.append(
                {
                    "id": f"PROP-{cycle_id}-TREND-1",
                    "title": "Trend-aligned workflow optimization",
                    "what": "Update recursive planning cadence and scope to align with current AI orchestration trends.",
                    "why": "Trend context highlights momentum in AI orchestration and productivity automation.",
                    "priority": "P1",
                    "type": "workflow",
                    "status": "DRAFT",
                    "evidence": ["H013-planning-context.json"],
                    "trendPulseId": (trend_context.get("pulse") or {}).get("pulseId"),
                }
            )

        if "TODO backlog" in pattern_text or "TODO" in pattern_text or stalled_patterns:
            proposals.append(
                {
                    "id": f"PROP-{cycle_id}-BACKLOG-1",
                    "title": "Reduce recursive planning TODO backlog",
                    "what": "Review and clear stale TODOs to prevent planning cycle drift.",
                    "why": "Pattern analysis indicates TODO backlog accumulation.",
                    "priority": "P0",
                    "type": "cleanup",
                    "status": "DRAFT",
                    "evidence": [pattern_evidence],
                }
            )

        status_counts = metrics_summary.get("summary", {}).get("status_counts", {})
        if status_counts:
            proposals.append(
                {
                    "id": f"PROP-{cycle_id}-METRICS-1",
                    "title": "Balance task status distribution",
                    "what": "Adjust planning cadence based on the current status distribution of tasks.",
                    "why": "Metrics show current status distribution that can inform planning cadence decisions.",
                    "priority": "P1",
                    "type": "metrics",
                    "status": "DRAFT",
                    "evidence": ["H008-metrics-log.json"],
                    "status_counts": status_counts,
                }
            )

        return proposals

    def _generate_planning_report(
        self,
        cycle_id: str,
        trend_context: Dict[str, Any],
        pattern_analysis: Dict[str, Any],
        metrics_summary: Dict[str, Any],
        proposals: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        insights: List[Dict[str, str]] = []

        if trend_context.get("keywords"):
            insights.append(
                {
                    "type": "trend",
                    "insight": f"Trend keywords: {', '.join(trend_context['keywords'][:6])}",
                    "source": "H013",
                }
            )

        if pattern_analysis.get("raw"):
            insights.append(
                {
                    "type": "pattern",
                    "insight": "Pattern analysis available; review for TODO backlog and stalled tasks.",
                    "source": "H009",
                }
            )

        if metrics_summary.get("summary"):
            insights.append(
                {
                    "type": "metrics",
                    "insight": "Metrics summary captured for current task status distribution.",
                    "source": "H008",
                }
            )

        return {
            "cycle_id": cycle_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "proposal_count": len(proposals),
        }


def save_cycle_artifacts(workspace_path: Path, cycle_payload: Dict[str, Any]) -> Dict[str, Path]:
    artifacts_dir = workspace_path / "artifacts"
    planning_dir = artifacts_dir / "planning"
    proposals_dir = artifacts_dir / "proposals"

    planning_dir.mkdir(parents=True, exist_ok=True)
    proposals_dir.mkdir(parents=True, exist_ok=True)

    cycle_id = cycle_payload["cycle_id"]
    cycle_json = planning_dir / f"{cycle_id}-cycle-execution.json"
    report_md = planning_dir / f"{cycle_id}-planning-report.md"
    proposals_json = proposals_dir / "H021-auto-generated-proposals.json"

    with open(cycle_json, "w", encoding="utf-8") as f:
        json.dump(cycle_payload, f, indent=2)

    with open(proposals_json, "w", encoding="utf-8") as f:
        json.dump(cycle_payload["proposals"], f, indent=2)

    with open(report_md, "w", encoding="utf-8") as f:
        f.write(f"# Recursive Planning Report - {cycle_id}\n\n")
        f.write(f"Generated: {cycle_payload['timestamp']}\n\n")
        f.write("## Insights\n")
        for insight in cycle_payload["planning_report"]["insights"]:
            f.write(f"- **{insight['type'].upper()}**: {insight['insight']} (Source: {insight['source']})\n")
        f.write("\n## Proposals\n")
        for proposal in cycle_payload["proposals"]:
            f.write(f"- {proposal['id']}: {proposal['title']} [{proposal['priority']}]\n")

    return {
        "cycle_json": cycle_json,
        "report_md": report_md,
        "proposals_json": proposals_json,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Recursive Planning Workflow Integration")
    parser.add_argument("--trigger", action="store_true", help="Trigger planning cycle")
    parser.add_argument("--manual", action="store_true", help="Trigger manual planning cycle")
    parser.add_argument("--full-cycle", action="store_true", help="Execute full planning cycle")
    parser.add_argument("--workspace", type=str, help="Path to cortex-gov workspace")

    args = parser.parse_args()
    workspace_path = resolve_workspace_path(args.workspace)

    workflow = RecursivePlanningWorkflow(workspace_path)

    if args.trigger or args.manual or args.full_cycle:
        cycle_payload = workflow.trigger_planning_cycle(manual=args.manual)
        outputs = save_cycle_artifacts(workspace_path, cycle_payload)

        print("Planning cycle completed successfully:")
        print(f"- Cycle ID: {cycle_payload['cycle_id']}")
        print(f"- Cycle execution: {outputs['cycle_json']}")
        print(f"- Planning report: {outputs['report_md']}")
        print(f"- Proposals: {outputs['proposals_json']}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
