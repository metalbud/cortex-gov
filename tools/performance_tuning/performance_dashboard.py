#!/usr/bin/env python3
"""
Performance Dashboard generator for Cortex-GOV.
Creates a markdown dashboard with real-time metrics and recommendations.
"""

import json
from datetime import datetime
from typing import Dict, Any
import psutil


def collect_metrics() -> Dict[str, Any]:
    return {
        "timestamp": datetime.now().isoformat(),
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "process_count": len(psutil.pids())
    }


def format_dashboard(metrics: Dict[str, Any]) -> str:
    lines = [
        "# H019 Performance Dashboard",
        "",
        f"Generated: {metrics['timestamp']}",
        "",
        "## Current Metrics",
        f"- CPU Usage: {metrics['cpu_percent']}%",
        f"- Memory Usage: {metrics['memory_percent']}%",
        f"- Disk Usage: {metrics['disk_percent']}%",
        f"- Process Count: {metrics['process_count']}",
        "",
        "## Recommendations",
    ]

    if metrics['cpu_percent'] > 75:
        lines.append("- CPU usage elevated; consider throttling background tasks.")
    else:
        lines.append("- CPU usage within normal range.")

    if metrics['memory_percent'] > 80:
        lines.append("- Memory usage high; review cached workloads.")
    else:
        lines.append("- Memory usage within normal range.")

    if metrics['disk_percent'] > 85:
        lines.append("- Disk usage high; recommend cleanup of old artifacts.")
    else:
        lines.append("- Disk usage within normal range.")

    return "\n".join(lines)


def write_dashboard(path: str) -> None:
    metrics = collect_metrics()
    content = format_dashboard(metrics)
    
    # Convert to absolute path
    import os
    abs_path = os.path.abspath(path)
    abs_metrics_path = abs_path.replace('.md', '.json')
    
    with open(abs_path, 'w') as f:
        f.write(content)

    with open(abs_metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)


if __name__ == '__main__':
    output_path = "C:\\Users\\metalbud\\clawd\\cortex-gov\\artifacts\\performance\\H019-performance-dashboard.md"
    write_dashboard(output_path)
    print(f"Dashboard saved to {output_path}")
