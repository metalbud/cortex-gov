#!/usr/bin/env python3
"""
Planning Report Generator

Generates comprehensive planning reports for recursive planning workflow.
"""

import json
import argparse
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parents[2]


def resolve_workspace_path(raw_workspace: str = None) -> Path:
    if raw_workspace:
        return Path(raw_workspace).resolve()
    return BASE_DIR


class PlanningReporter:
    """Generates planning reports with insights and recommendations"""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.artifacts_dir = workspace_path / "artifacts"
        
    def generate_report(self, cycle_id: str = None, output_file: str = None) -> Dict[str, Any]:
        """Generate comprehensive planning report"""
        if cycle_id:
            # Load specific cycle data
            cycle_file = self.artifacts_dir / "planning" / f"{cycle_id}-cycle-execution.json"
            if not cycle_file.exists():
                raise FileNotFoundError(f"Cycle data not found: {cycle_file}")
            
            with open(cycle_file, 'r', encoding='utf-8') as f:
                cycle_data = json.load(f)
        else:
            # Generate from current state
            cycle_data = self._generate_current_state_report()
        
        # Generate markdown report
        markdown_content = self._generate_markdown_report(cycle_data)
        
        # Save report if output file specified
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
        
        return {
            "cycle_id": cycle_data.get("cycle_id", "current-state"),
            "markdown_content": markdown_content,
            "json_data": cycle_data,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
    
    def _generate_current_state_report(self) -> Dict[str, Any]:
        """Generate report from current system state"""
        # Read current metrics
        trend_context = self._read_trend_context()
        pattern_analysis = self._analyze_patterns()
        
        # Generate insights
        insights = []
        
        # Trend insights
        trend_keywords = trend_context.get("keywords", [])
        if trend_keywords:
            insights.append({
                "type": "trend",
                "insight": f"Current trends focus on: {', '.join(trend_keywords[:5])}",
                "relevance": "high",
                "source": "H013-trend-pulse"
            })
        
        # Pattern insights
        stalled_patterns = [p for p in pattern_analysis.get("patterns", []) 
                          if p.get("status") == "stalled"]
        if stalled_patterns:
            insights.append({
                "type": "pattern",
                "insight": f"Identified {len(stalled_patterns)} stalled patterns requiring attention",
                "relevance": "critical",
                "source": "H009-pattern-analysis"
            })
        
        # Project status
        project_file = self.workspace_path / "PROJECT.md"
        if project_file.exists():
            content = project_file.read_text(encoding='utf-8')
            todo_count = content.count("Status: TODO")
            done_count = content.count("Status: DONE")
            
            insights.append({
                "type": "project",
                "insight": f"Project status: {done_count} completed, {todo_count} pending tasks",
                "relevance": "medium",
                "source": "PROJECT.md"
            })
        
        return {
            "cycle_id": f"H021-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "insights": insights,
            "trend_context": trend_context,
            "pattern_analysis": pattern_analysis,
            "proposals": [],  # No proposals in current state mode
            "recommendations": self._generate_recommendations(insights)
        }
    
    def _read_trend_context(self) -> Dict[str, Any]:
        """Read trend context from H013"""
        trend_file = self.artifacts_dir / "metrics" / "H013-planning-context.json"
        if trend_file.exists():
            with open(trend_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"keywords": [], "competitors": [], "pulse": None}
    
    def _analyze_patterns(self) -> Dict[str, Any]:
        """Analyze execution patterns from H009"""
        pattern_file = self.artifacts_dir / "patterns" / "H009-pattern-analysis.json"
        if pattern_file.exists():
            with open(pattern_file, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
                data = raw_data if isinstance(raw_data, dict) else {}
                return {
                    "source": str(pattern_file),
                    "format": "json",
                    "patterns": data.get("patterns", []) if isinstance(data.get("patterns", []), list) else [],
                    "bottlenecks": data.get("bottlenecks", []) if isinstance(data.get("bottlenecks", []), list) else [],
                    "insights": data.get("insights", []) if isinstance(data.get("insights", []), list) else [],
                }

        legacy_paths = [
            self.artifacts_dir / "metrics" / "H009-pattern-analysis.md",
            self.artifacts_dir / "patterns" / "H009-pattern-analysis.md",
        ]
        for legacy_file in legacy_paths:
            if legacy_file.exists():
                return {
                    "source": str(legacy_file),
                    "format": "markdown",
                    "raw": legacy_file.read_text(encoding='utf-8'),
                    "patterns": [],
                    "bottlenecks": [],
                    "insights": [],
                }

        return {"source": None, "format": None, "patterns": [], "bottlenecks": [], "insights": []}
    
    def _generate_recommendations(self, insights: List[Dict[str, Any]]) -> List[str]:
        """Generate strategic recommendations"""
        recommendations = []
        
        critical_insights = [i for i in insights if i.get("relevance") == "critical"]
        if critical_insights:
            recommendations.append("Address critical issues immediately")
        
        stalled_insights = [i for i in insights if i.get("type") == "pattern" and "stalled" in i.get("insight", "")]
        if stalled_insights:
            recommendations.append("Review and resolve stalled execution patterns")
        
        trend_insights = [i for i in insights if i.get("type") == "trend"]
        if trend_insights:
            recommendations.append("Leverage trend insights for optimization opportunities")
            
        if not recommendations:
            recommendations.append("System operating normally, continue monitoring")

        return recommendations
    
    def _generate_markdown_report(self, cycle_data: Dict[str, Any]) -> str:
        """Generate markdown report content"""
        cycle_id = cycle_data.get("cycle_id", "current-state")
        timestamp = cycle_data.get("timestamp", datetime.now(timezone.utc).isoformat())
        
        markdown = f"""# Recursive Planning Report - {cycle_id}

**Generated:** {timestamp}

## Executive Summary

This report summarizes the findings from the recursive planning cycle, combining trend analysis, pattern detection, and system optimization insights.

## Key Insights

"""
        
        # Add insights
        for insight in cycle_data.get("insights", []):
            relevance = insight.get("relevance", "medium").upper()
            markdown += f"### {insight['type'].upper()} Insight\n"
            markdown += f"**{relevance}:** {insight['insight']}\n\n"
            markdown += f"**Source:** {insight['source']}\n\n---\n\n"
        
        # Add recommendations
        markdown += "## Strategic Recommendations\n\n"
        for i, rec in enumerate(cycle_data.get("recommendations", []), 1):
            markdown += f"{i}. **{rec}**\n\n"
        
        # Add proposals section if available
        proposals = cycle_data.get("proposals", [])
        if proposals:
            markdown += "## Proposed Actions\n\n"
            for prop in proposals:
                markdown += f"### {prop['id']}: {prop['title']}\n\n"
                markdown += f"**Priority:** {prop['priority']}\n"
                markdown += f"**Type:** {prop['type']}\n"
                markdown += f"**What:** {prop['what']}\n"
                markdown += f"**Why:** {prop['why']}\n\n"
        
        # Add trend context summary
        trend_context = cycle_data.get("trend_context", {})
        if trend_context.get("keywords"):
            markdown += "## Trend Context\n\n"
            markdown += f"**Current Keywords:** {', '.join(trend_context.get('keywords', [])[:5])}\n\n"
        
        # Add pattern analysis summary
        pattern_analysis = cycle_data.get("pattern_analysis", {})
        if pattern_analysis.get("patterns"):
            markdown += "## Pattern Analysis\n\n"
            stalled_count = sum(1 for p in pattern_analysis.get("patterns", []) if p.get("status") == "stalled")
            if stalled_count > 0:
                markdown += f"⚠️ **{stalled_count} stalled patterns detected**\n\n"
            
            for pattern in pattern_analysis.get("patterns", [])[:3]:  # Show first 3 patterns
                status = pattern.get("status", "unknown")
                markdown += f"- **{pattern.get('name', 'Unnamed')}** ({status})\n"
            
            markdown += "\n"
        
        return markdown


def main():
    parser = argparse.ArgumentParser(description="Planning Report Generator")
    parser.add_argument("--cycle-id", type=str, help="Specific cycle ID to report on")
    parser.add_argument("--output", type=str, help="Output file path for markdown report")
    parser.add_argument("--current-state", action="store_true", help="Generate report from current system state")
    parser.add_argument("--workspace", type=str, help="Path to cortex-gov workspace")
    
    args = parser.parse_args()
    
    workspace_path = resolve_workspace_path(args.workspace)
    reporter = PlanningReporter(workspace_path)
    
    try:
        report_data = reporter.generate_report(
            cycle_id=args.cycle_id,
            output_file=args.output
        )
        
        print(f"Planning report generated successfully:")
        print(f"- Cycle ID: {report_data['cycle_id']}")
        print(f"- Timestamp: {report_data['timestamp']}")
        
        if args.output:
            print(f"- Output file: {args.output}")
        else:
            print("\n--- Report Content ---")
            print(report_data['markdown_content'])
            
    except Exception as e:
        print(f"Error generating report: {e}")
        return 1
        
    return 0


if __name__ == "__main__":
    exit(main())
