#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cortex-GOV System Integration Checker

This tool analyzes system integration points, identifies communication gaps,
and validates cross-tool communication pathways.
"""

import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
CONFIG_DIR = BASE_DIR / "artifacts" / "config"
ANALYSIS_DIR = BASE_DIR / "artifacts" / "system-analysis"

# Tool categories and their expected integration points
TOOL_CATEGORIES = {
    "self_improvement": {
        "tools": [
            "self_improvement/proposal_manager.py",
            "self_improvement/safety_guardian.py",
            "self_improvement/autonomous_feedback_manager.py",
            "self_improvement/brave_trend_pulse.py",
            "self_improvement/metrics_collector.py",
            "self_improvement/pattern_analysis.py"
        ],
        "integration_points": [
            "shared_config",
            "proposal_workflow",
            "safety_validation",
            "feedback_loop",
            "trend_context"
        ]
    },
    "gui_launcher": {
        "tools": [
            "gui_launcher/package_gui.py",
            "gui_launcher/gui_launcher_package/cortex_gov_gui.py",
            "gui_launcher/gui_launcher_package/launcher.py",
            "gui_launcher/gui_launcher_package/launch_gui.py"
        ],
        "integration_points": [
            "project_discovery",
            "agent_spawn",
            "configuration_management"
        ]
    },
    "analysis": {
        "tools": [
            "efficiency_analysis/optimization_analyzer.py",
            "analysis/backlog_analyzer.py",
            "cleanup/todo_cleaner.py"
        ],
        "integration_points": [
            "data_collection",
            "reporting",
            "cross_analysis"
        ]
    },
    "performance": {
        "tools": [
            "metrics_health/monitor.py",
            "performance_tuning/autotune.py",
            "performance_tuning/performance_dashboard.py"
        ],
        "integration_points": [
            "metrics_collection",
            "performance_tracking",
            "adaptive_optimization"
        ]
    }
}

class IntegrationChecker:
    def __init__(self):
        """Initialize the integration checker."""
        self.ensure_directories()
        self.integration_issues = []
        self.tool_status = {}
        
    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        ANALYSIS_DIR.mkdir(parents=True, exist_ok=True)
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
    def check_tool_existence(self) -> None:
        """Check if all expected tools exist."""
        logger.info("Checking tool existence...")
        
        for category, category_data in TOOL_CATEGORIES.items():
            self.tool_status[category] = {}
            
            for tool in category_data["tools"]:
                tool_path = BASE_DIR / "tools" / tool
                exists = tool_path.exists()
                self.tool_status[category][tool] = {
                    "exists": exists,
                    "path": str(tool_path),
                    "size": tool_path.stat().st_size if exists else 0
                }
                
                if not exists:
                    self.integration_issues.append({
                        "type": "missing_tool",
                        "category": category,
                        "tool": tool,
                        "severity": "high",
                        "description": f"Expected tool {tool} in category {category} is missing"
                    })
                    logger.warning(f"Missing tool: {tool_path}")
    
    def check_command_line_interface(self) -> None:
        """Check if tools have proper CLI interfaces."""
        logger.info("Checking command line interfaces...")
        
        for category, category_data in TOOL_CATEGORIES.items():
            for tool in category_data["tools"]:
                tool_path = BASE_DIR / "tools" / tool
                if tool_path.exists():
                    try:
                        # Try to get help output
                        result = os.system(f"python \"{tool_path}\" --help >nul 2>&1")
                        if result != 0:
                            self.integration_issues.append({
                                "type": "cli_error",
                                "category": category,
                                "tool": tool,
                                "severity": "medium",
                                "description": f"Tool {tool} has CLI interface issues"
                            })
                            logger.warning(f"CLI error in {tool}")
                    except Exception as e:
                        self.integration_issues.append({
                            "type": "cli_exception",
                            "category": category,
                            "tool": tool,
                            "severity": "medium",
                            "description": f"Exception testing CLI for {tool}: {str(e)}"
                        })
    
    def check_file_dependencies(self) -> None:
        """Check inter-tool file dependencies."""
        logger.info("Checking file dependencies...")
        
        # Key dependency files to check
        dependency_files = [
            "artifacts/config/monitor-config.json",
            "artifacts/config/H027-safety-rails.json",
            "artifacts/config/H028-feedback-config.json",
            "artifacts/metrics/H008-metrics-log.json",
            "artifacts/proposals/H010-proposals.json",
            "artifacts/metrics/H013-planning-context.json",
            "artifacts/verification/H013-brave-trends.md"
        ]
        
        for dep_file in dependency_files:
            file_path = BASE_DIR / dep_file
            if not file_path.exists():
                # Check if any tools depend on this file
                tools_using_file = self.find_tools_using_file(dep_file)
                if tools_using_file:
                    self.integration_issues.append({
                        "type": "missing_dependency",
                        "file": dep_file,
                        "tools": tools_using_file,
                        "severity": "high",
                        "description": f"Missing dependency file {dep_file} used by {len(tools_using_file)} tools"
                    })
                    logger.warning(f"Missing dependency: {dep_file}")
    
    def find_tools_using_file(self, file_path: str) -> List[str]:
        """Find tools that reference a specific file."""
        tools_using = []
        
        for category, category_data in TOOL_CATEGORIES.items():
            for tool in category_data["tools"]:
                tool_path = BASE_DIR / "tools" / tool
                if tool_path.exists():
                    try:
                        content = tool_path.read_text()
                        if file_path in content or file_path.replace("/", "\\") in content:
                            tools_using.append(f"{category}/{tool}")
                    except Exception:
                        continue
        
        return tools_using
    
    def check_cross_tool_communication(self) -> None:
        """Check potential communication pathways between tools."""
        logger.info("Checking cross-tool communication...")
        
        # Communication patterns to verify
        communication_patterns = [
            {
                "from": "self_improvement/proposal_manager.py",
                "to": "self_improvement/safety_guardian.py",
                "mechanism": "shared audit log",
                "critical": True
            },
            {
                "from": "self_improvement/brave_trend_pulse.py",
                "to": "self_improvement/proposal_manager.py",
                "mechanism": "trend context files",
                "critical": True
            },
            {
                "from": "efficiency_analysis/optimization_analyzer.py",
                "to": "metrics_health/monitor.py",
                "mechanism": "metrics sharing",
                "critical": False
            },
            {
                "from": "gui_launcher/gui_launcher_package/cortex_gov_gui.py",
                "to": "analysis/backlog_analyzer.py",
                "mechanism": "project scanning",
                "critical": False
            }
        ]
        
        for comm in communication_patterns:
            from_tool = BASE_DIR / "tools" / comm["from"].replace("/", "\\")
            to_tool = BASE_DIR / "tools" / comm["to"].replace("/", "\\")
            
            if from_tool.exists() and to_tool.exists():
                # Check if communication mechanism exists
                mechanism_exists = self.check_communication_mechanism(comm["mechanism"])
                
                if not mechanism_exists and comm["critical"]:
                    self.integration_issues.append({
                        "type": "broken_communication",
                        "from": comm["from"],
                        "to": comm["to"],
                        "mechanism": comm["mechanism"],
                        "severity": "high",
                        "description": f"Critical communication broken between {comm['from']} and {comm['to']}"
                    })
    
    def check_communication_mechanism(self, mechanism: str) -> bool:
        """Check if a specific communication mechanism exists."""
        if mechanism == "shared audit log":
            return (BASE_DIR / "artifacts" / "metrics" / "H011-audit-log.json").exists()
        elif mechanism == "trend context files":
            return (BASE_DIR / "artifacts" / "metrics" / "H013-planning-context.json").exists()
        elif mechanism == "metrics sharing":
            return (BASE_DIR / "artifacts" / "metrics" / "H008-metrics-log.json").exists()
        return False
    
    def generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration analysis report."""
        logger.info("Generating integration report...")
        
        # Count issues by severity
        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for issue in self.integration_issues:
            severity_counts[issue["severity"]] += 1
        
        # Tool existence summary
        tool_summary = {}
        for category, category_data in TOOL_CATEGORIES.items():
            expected_count = len(category_data["tools"])
            existing_count = sum(1 for tool in category_data["tools"] 
                               if self.tool_status.get(category, {}).get(tool, {}).get("exists", False))
            
            tool_summary[category] = {
                "expected_tools": expected_count,
                "existing_tools": existing_count,
                "health": f"{existing_count}/{expected_count}"
            }
        
        report = {
            "scan_timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_health": "good" if severity_counts["high"] == 0 else "needs_attention",
            "severity_counts": severity_counts,
            "total_issues": len(self.integration_issues),
            "tool_summary": tool_summary,
            "integration_issues": self.integration_issues,
            "recommendations": self.generate_recommendations()
        }
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on integration analysis."""
        recommendations = []
        
        # High priority recommendations
        high_issues = [issue for issue in self.integration_issues if issue["severity"] == "high"]
        if high_issues:
            recommendations.append(f"URGENT: Address {len(high_issues)} high-severity integration issues")
        
        # Missing tools
        missing_tools = [issue for issue in self.integration_issues if issue["type"] == "missing_tool"]
        if missing_tools:
            recommendations.append(f"Implement {len(missing_tools)} missing tools")
        
        # Broken communication
        broken_comm = [issue for issue in self.integration_issues if issue["type"] == "broken_communication"]
        if broken_comm:
            recommendations.append(f"Fix {len(broken_comm)} critical communication pathways")
        
        # Dependency issues
        dep_issues = [issue for issue in self.integration_issues if issue["type"] == "missing_dependency"]
        if dep_issues:
            recommendations.append(f"Create {len(dep_issues)} missing dependency files")
        
        if not recommendations:
            recommendations.append("All integration checks passed - system is healthy")
        
        return recommendations
    
    def save_report(self, report: Dict[str, Any], output_path: Optional[str] = None) -> None:
        """Save integration report to file."""
        if output_path is None:
            output_path = str(ANALYSIS_DIR / "integration-gaps.json")
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Integration report saved to: {output_path}")
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print human-readable summary of integration analysis."""
        print("\n" + "="*50)
        print("CORTEX-GOV INTEGRATION ANALYSIS SUMMARY")
        print("="*50)
        
        print(f"\nOverall Health: {report['overall_health'].upper()}")
        print(f"Scan Timestamp: {report['scan_timestamp']}")
        print(f"Total Issues: {report['total_issues']}")
        
        print("\nIssue Severity Breakdown:")
        for severity, count in report['severity_counts'].items():
            print(f"  {severity.upper()}: {count}")
        
        print("\nTool Summary:")
        for category, summary in report['tool_summary'].items():
            print(f"  {category}: {summary['health']} tools ({summary['existing_tools']}/{summary['expected_tools']})")
        
        print("\nRecommendations:")
        for i, rec in enumerate(report['recommendations'], 1):
            print(f"  {i}. {rec}")
        
        if report['integration_issues']:
            print(f"\nTop {min(5, len(report['integration_issues']))} Issues:")
            for i, issue in enumerate(report['integration_issues'][:5], 1):
                print(f"  {i}. [{issue['severity'].upper()}] {issue['description']}")
        
        print("\n" + "="*50)

def main():
    """Main entry point for the integration checker."""
    parser = argparse.ArgumentParser(description="Check Cortex-GOV system integration points")
    parser.add_argument("--scan", action="store_true", help="Perform full system scan")
    parser.add_argument("--test", action="store_true", help="Test cross-tool communication")
    parser.add_argument("--output", help="Output file for integration report")
    parser.add_argument("--verbose", action="store_true", help="Detailed logging")
    parser.add_argument("--quiet", action="store_true", help="Minimal output")
    
    args = parser.parse_args()
    
    # Initialize checker
    checker = IntegrationChecker()
    
    # Perform checks based on arguments
    if args.scan or not (args.test or args.output):
        # Full scan
        checker.check_tool_existence()
        checker.check_command_line_interface()
        checker.check_file_dependencies()
        checker.check_cross_tool_communication()
    elif args.test:
        # Just test communication
        checker.check_cross_tool_communication()
    
    # Generate and save report
    report = checker.generate_integration_report()
    checker.save_report(report, args.output)
    
    # Print summary unless quiet
    if not args.quiet:
        checker.print_summary(report)
    
    # Exit with appropriate code
    if report['overall_health'] == "good":
        print(f"\nIntegration analysis complete - system is healthy")
        return 0
    else:
        print(f"\nIntegration analysis complete - {report['total_issues']} issues found")
        return 1

if __name__ == "__main__":
    sys.exit(main())