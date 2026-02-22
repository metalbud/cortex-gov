#!/usr/bin/env python3
"""
Resource Manager for Cortex-GOV
Allocates resources based on workload analysis and tuning strategies.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List
import psutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ResourceManager:
    def __init__(self):
        self.policy = {
            "cpu_priority_threshold": 10.0,
            "memory_priority_threshold": 5.0,
            "disk_cleanup_threshold": 85.0,
            "cpu_reserve": 20.0,
            "memory_reserve": 25.0
        }

    def collect_workload_snapshot(self) -> Dict[str, Any]:
        """Collect current workload snapshot."""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "top_processes": self._get_top_processes()
        }
        return snapshot

    def _get_top_processes(self) -> List[Dict[str, Any]]:
        processes = []
        for proc in psutil.process_iter(['cpu_percent', 'memory_percent', 'name']):
            try:
                info = proc.info
                if info['cpu_percent'] is None or info['memory_percent'] is None:
                    continue
                if info['cpu_percent'] >= self.policy['cpu_priority_threshold'] or info['memory_percent'] >= self.policy['memory_priority_threshold']:
                    processes.append({
                        "pid": proc.pid,
                        "name": info['name'],
                        "cpu_percent": info['cpu_percent'],
                        "memory_percent": info['memory_percent']
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda p: (p['cpu_percent'], p['memory_percent']), reverse=True)
        return processes[:10]

    def generate_resource_plan(self, snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a resource plan from the snapshot."""
        plan = {
            "timestamp": datetime.now().isoformat(),
            "cpu_action": "none",
            "memory_action": "none",
            "disk_action": "none",
            "notes": []
        }

        if snapshot['cpu_percent'] > (100 - self.policy['cpu_reserve']):
            plan['cpu_action'] = "throttle_low_priority"
            plan['notes'].append("CPU usage high; recommend throttling low priority processes.")

        if snapshot['memory_percent'] > (100 - self.policy['memory_reserve']):
            plan['memory_action'] = "cleanup_cache"
            plan['notes'].append("Memory usage high; recommend cache cleanup.")

        if snapshot['disk_percent'] > self.policy['disk_cleanup_threshold']:
            plan['disk_action'] = "cleanup_temp_files"
            plan['notes'].append("Disk usage high; recommend cleanup of temp artifacts.")

        return plan

    def save_plan(self, plan: Dict[str, Any], path: str) -> None:
        with open(path, 'w') as f:
            json.dump(plan, f, indent=2)
        logger.info("Resource plan saved to %s", path)


def main():
    manager = ResourceManager()
    snapshot = manager.collect_workload_snapshot()
    plan = manager.generate_resource_plan(snapshot)
    out_path = "C:\\Users\\metalbud\\clawd\\cortex-gov\\artifacts\\performance\\H019-resource-plan.json"
    manager.save_plan(plan, out_path)
    print(json.dumps(plan, indent=2))


if __name__ == '__main__':
    main()
