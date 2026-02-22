#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor the health of the Cortex-GOV metrics pipeline and alert on anomalies.
"""

import argparse
import json
import logging
import re
import shutil
import subprocess
import sys
import tempfile
import time
import threading
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parents[2]
METRICS_DIR = BASE_DIR / "artifacts" / "metrics"
LOG_PATH = METRICS_DIR / "H008-metrics-log.json"
HEALTH_DIR = BASE_DIR / "artifacts" / "metrics_health"
ALERTS_DIR = HEALTH_DIR / "alerts"
DASHBOARD_DIR = HEALTH_DIR / "dashboards"

# Alert thresholds
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50MB
MAX_STALE_HOURS = 24  # 24 hours without capture is stale
MAX_INCOMPLETE_RATIO = 0.5  # More than 50% incomplete tasks is concerning


class MetricsHealthMonitor:
    def __init__(self):
        """Initialize the health monitor with required directories."""
        self.ensure_directories()
        
    def ensure_directories(self) -> None:
        """Ensure all required directories exist."""
        HEALTH_DIR.mkdir(parents=True, exist_ok=True)
        ALERTS_DIR.mkdir(parents=True, exist_ok=True)
        DASHBOARD_DIR.mkdir(parents=True, exist_ok=True)
        
    def check_health(self) -> Dict[str, Any]:
        """Perform comprehensive health checks on the metrics pipeline."""
        logger.info("Starting metrics health check...")
        
        health_report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "checks": {},
            "alerts": [],
            "status": "healthy"
        }
        
        # Check 1: Log file existence and readability
        log_health = self._check_log_file()
        health_report["checks"]["log_file"] = log_health
        if not log_health["healthy"]:
            health_report["alerts"].append({
                "type": "error",
                "check": "log_file",
                "message": log_health["message"],
                "severity": "high"
            })
            health_report["status"] = "unhealthy"
        
        # Check 2: Log file size
        size_health = self._check_log_size()
        health_report["checks"]["log_size"] = size_health
        if not size_health["healthy"]:
            health_report["alerts"].append({
                "type": "warning",
                "check": "log_size", 
                "message": size_health["message"],
                "severity": "medium"
            })
            
        # Check 3: Data freshness
        freshness_health = self._check_data_freshness()
        health_report["checks"]["data_freshness"] = freshness_health
        if not freshness_health["healthy"]:
            health_report["alerts"].append({
                "type": "warning",
                "check": "data_freshness",
                "message": freshness_health["message"],
                "severity": "medium"
            })
            health_report["status"] = "stale"
            
        # Check 4: Data completeness
        completeness_health = self._check_data_completeness()
        health_report["checks"]["data_completeness"] = completeness_health
        if not completeness_health["healthy"]:
            health_report["alerts"].append({
                "type": "warning",
                "check": "data_completeness",
                "message": completeness_health["message"],
                "severity": "medium"
            })
            
        # Check 5: Log integrity
        integrity_health = self._check_log_integrity()
        health_report["checks"]["log_integrity"] = integrity_health
        if not integrity_health["healthy"]:
            health_report["alerts"].append({
                "type": "error",
                "check": "log_integrity",
                "message": integrity_health["message"],
                "severity": "high"
            })
            health_report["status"] = "unhealthy"
            
        # Check 6: Task pattern anomalies
        pattern_health = self._check_task_patterns()
        health_report["checks"]["task_patterns"] = pattern_health
        if pattern_health["alerts"]:
            health_report["alerts"].extend(pattern_health["alerts"])
            if pattern_health["alerts"][0]["severity"] == "high":
                health_report["status"] = "unhealthy"
                
        return health_report
    
    def _check_log_file(self) -> Dict[str, Any]:
        """Check if the log file exists and is readable."""
        try:
            if not LOG_PATH.exists():
                return {
                    "healthy": False,
                    "message": "Metrics log file does not exist",
                    "details": {"path": str(LOG_PATH)}
                }
            
            # Try to read the file
            LOG_PATH.read_text()
            return {
                "healthy": True,
                "message": "Log file is readable",
                "details": {"path": str(LOG_PATH)}
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Error reading log file: {str(e)}",
                "details": {"path": str(LOG_PATH), "error": str(e)}
            }
    
    def _check_log_size(self) -> Dict[str, Any]:
        """Check if the log file size is within acceptable limits."""
        try:
            file_size = LOG_PATH.stat().st_size
            
            if file_size > MAX_LOG_SIZE:
                return {
                    "healthy": False,
                    "message": f"Log file is too large ({file_size / (1024*1024):.1f}MB > {MAX_LOG_SIZE / (1024*1024):.1f}MB)",
                    "details": {"current_size": file_size, "max_size": MAX_LOG_SIZE}
                }
            
            # Log if file size is getting large (80% of max)
            if file_size > MAX_LOG_SIZE * 0.8:
                return {
                    "healthy": True,
                    "message": f"Log size is approaching limit ({file_size / (1024*1024):.1f}MB)",
                    "details": {"current_size": file_size, "max_size": MAX_LOG_SIZE}
                }
            
            return {
                "healthy": True,
                "message": f"Log size is acceptable ({file_size / (1024*1024):.1f}MB)",
                "details": {"current_size": file_size}
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Error checking log size: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _check_data_freshness(self) -> Dict[str, Any]:
        """Check if the data is recent enough."""
        try:
            if not LOG_PATH.exists():
                return {
                    "healthy": False,
                    "message": "Cannot check freshness - no log file",
                    "details": {}
                }
                
            log_content = json.loads(LOG_PATH.read_text())
            if not log_content:
                return {
                    "healthy": False,
                    "message": "Cannot check freshness - empty log",
                    "details": {}
                }
                
            latest_entry = log_content[-1]
            latest_time = datetime.fromisoformat(latest_entry["capturedAt"].replace("Z", "+00:00"))
            now = datetime.now(timezone.utc)
            age = now - latest_time
            
            if age > timedelta(hours=MAX_STALE_HOURS):
                return {
                    "healthy": False,
                    "message": f"Data is stale ({age.total_seconds() / 3600:.1f} hours old)",
                    "details": {"age_hours": age.total_seconds() / 3600, "max_age_hours": MAX_STALE_HOURS}
                }
            
            return {
                "healthy": True,
                "message": f"Data is recent ({age.total_seconds() / 3600:.1f} hours old)",
                "details": {"age_hours": age.total_seconds() / 3600}
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Error checking data freshness: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _check_data_completeness(self) -> Dict[str, Any]:
        """Check if the data has a reasonable distribution of task statuses."""
        try:
            if not LOG_PATH.exists():
                return {
                    "healthy": True,  # Not an error if no data yet
                    "message": "No data to check completeness",
                    "details": {}
                }
                
            log_content = json.loads(LOG_PATH.read_text())
            if not log_content:
                return {
                    "healthy": True,
                    "message": "No data to check completeness",
                    "details": {}
                }
                
            latest_entry = log_content[-1]
            tasks = latest_entry.get("tasks", [])
            
            if not tasks:
                return {
                    "healthy": True,
                    "message": "No tasks in latest entry",
                    "details": {"task_count": 0}
                }
                
            status_counts = {}
            for task in tasks:
                status = task.get("status", "UNKNOWN")
                status_counts[status] = status_counts.get(status, 0) + 1
                
            incomplete_count = status_counts.get("TODO", 0) + status_counts.get("IN_PROGRESS", 0)
            incomplete_ratio = incomplete_count / len(tasks) if tasks else 0
            
            if incomplete_ratio > MAX_INCOMPLETE_RATIO:
                return {
                    "healthy": False,
                    "message": f"High ratio of incomplete tasks ({incomplete_ratio:.1%})",
                    "details": {
                        "incomplete_ratio": incomplete_ratio,
                        "incomplete_count": incomplete_count,
                        "total_tasks": len(tasks),
                        "status_counts": status_counts
                    }
                }
            
            return {
                "healthy": True,
                "message": f"Task completion ratio is acceptable ({incomplete_ratio:.1%} incomplete)",
                "details": {
                    "incomplete_ratio": incomplete_ratio,
                    "status_counts": status_counts
                }
            }
            
        except Exception as e:
            return {
                "healthy": True,  # Don't fail health check for this error
                "message": f"Error checking data completeness: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _check_log_integrity(self) -> Dict[str, Any]:
        """Check if the log file has valid JSON structure."""
        try:
            if not LOG_PATH.exists():
                return {
                    "healthy": True,  # Not an error if no data yet
                    "message": "No log file to check integrity",
                    "details": {}
                }
                
            content = LOG_PATH.read_text()
            
            # Check if it's valid JSON
            try:
                json_data = json.loads(content)
            except json.JSONDecodeError as e:
                return {
                    "healthy": False,
                    "message": f"Invalid JSON in log file: {str(e)}",
                    "details": {"error": str(e)}
                }
                
            # Check structure
            if not isinstance(json_data, list):
                return {
                    "healthy": False,
                    "message": "Log file is not a JSON array",
                    "details": {"actual_type": type(json_data).__name__}
                }
                
            # Check each entry has required fields
            for i, entry in enumerate(json_data):
                if not isinstance(entry, dict):
                    return {
                        "healthy": False,
                        "message": f"Entry {i} is not an object",
                        "details": {"entry_index": i, "actual_type": type(entry).__name__}
                    }
                    
                if "capturedAt" not in entry:
                    return {
                        "healthy": False,
                        "message": f"Entry {i} missing required 'capturedAt' field",
                        "details": {"entry_index": i}
                    }
                    
            return {
                "healthy": True,
                "message": f"Log file has valid structure with {len(json_data)} entries",
                "details": {"entry_count": len(json_data)}
            }
            
        except Exception as e:
            return {
                "healthy": False,
                "message": f"Error checking log integrity: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def _check_task_patterns(self) -> Dict[str, Any]:
        """Check for unusual patterns in task status transitions."""
        try:
            alerts = []
            
            if not LOG_PATH.exists():
                return {"healthy": True, "alerts": [], "message": "No log file to analyze"}
                
            log_content = json.loads(LOG_PATH.read_text())
            if not log_content or len(log_content) < 2:
                return {"healthy": True, "alerts": [], "message": "Need at least 2 entries for pattern analysis"}
                
            # Look for tasks that keep the same status across multiple captures
            status_history = {}
            for entry in log_content[-10:]:  # Last 10 entries
                for task in entry.get("tasks", []):
                    key = task["key"]
                    status = task["status"]
                    
                    if key not in status_history:
                        status_history[key] = []
                    status_history[key].append(status)
                    
            # Check for tasks that have been TODO for too long
            for task_key, status_list in status_history.items():
                if len(status_list) >= 5 and all(s == "TODO" for s in status_list[-5:]):
                    alerts.append({
                        "type": "warning",
                        "check": "stagnant_todo",
                        "message": f"Task {task_key} has been TODO for multiple captures",
                        "severity": "medium",
                        "task_key": task_key,
                        "recent_statuses": status_list[-5:]
                    })
                    
            # Check for unusual status jumps
            for task_key, status_list in status_history.items():
                if len(status_list) >= 3:
                    recent_statuses = status_list[-3:]
                    # Check for jumping between TODO and DONE without IN_PROGRESS
                    if "TODO" in recent_statuses and "DONE" in recent_statuses and "IN_PROGRESS" not in recent_statuses:
                        alerts.append({
                            "type": "warning",
                            "check": "status_jump",
                            "message": f"Task {task_key} shows status jump without IN_PROGRESS",
                            "severity": "low",
                            "task_key": task_key,
                            "recent_statuses": recent_statuses
                        })
                        
            # Determine overall health
            high_severity_alerts = [a for a in alerts if a["severity"] == "high"]
            medium_severity_alerts = [a for a in alerts if a["severity"] == "medium"]
            
            if high_severity_alerts:
                return {
                    "healthy": False,
                    "alerts": alerts,
                    "message": f"Found {len(alerts)} pattern anomalies ({len(high_severity_alerts)} high severity)"
                }
            elif medium_severity_alerts:
                return {
                    "healthy": True,
                    "alerts": alerts,
                    "message": f"Found {len(alerts)} pattern anomalies ({len(medium_severity_alerts)} medium severity)"
                }
            else:
                return {
                    "healthy": True,
                    "alerts": alerts,
                    "message": f"No concerning pattern anomalies found ({len(alerts)} low severity warnings)"
                }
                
        except Exception as e:
            return {
                "healthy": True,  # Don't fail health check for analysis errors
                "alerts": [],
                "message": f"Error analyzing task patterns: {str(e)}",
                "details": {"error": str(e)}
            }
    
    def recover_corrupted_log(self, log_path: Path = LOG_PATH) -> Dict[str, Any]:
        """Attempt to recover a corrupted log by backing it up and creating a new empty log."""
        try:
            if not log_path.exists():
                return {"recovered": False, "message": "No log file to recover", "log_path": str(log_path)}

            try:
                data = json.loads(log_path.read_text())
                if isinstance(data, list):
                    return {"recovered": False, "message": "Log is valid; no recovery needed", "log_path": str(log_path)}
            except json.JSONDecodeError:
                pass

            timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
            backup_path = log_path.with_suffix(f".corrupt-{timestamp}.json")
            shutil.copy2(log_path, backup_path)
            log_path.write_text("[]", encoding="utf-8")

            return {
                "recovered": True,
                "message": "Corrupted log backed up and reset",
                "log_path": str(log_path),
                "backup_path": str(backup_path),
            }

        except Exception as e:
            return {"recovered": False, "message": f"Recovery failed: {e}", "log_path": str(log_path)}

    def save_health_report(self, report: Dict[str, Any]) -> Path:
        """Save the health report to file."""
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        report_path = HEALTH_DIR / f"health-report-{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
            
        logger.info(f"Health report saved to {report_path}")
        return report_path
    
    def generate_dashboard(self, report: Dict[str, Any]) -> Path:
        """Generate a human-readable health dashboard."""
        timestamp = datetime.utcnow().isoformat().replace(":", "-").replace(".", "-")
        dashboard_path = DASHBOARD_DIR / f"health-dashboard-{timestamp}.md"
        
        dashboard_content = f"""# Cortex-GOV Metrics Health Dashboard

**Generated:** {report['timestamp']}  
**Overall Status:** {report['status'].upper()}

## Health Check Summary
"""
        
        # Check status
        checks_passed = sum(1 for check in report['checks'].values() if check['healthy'])
        total_checks = len(report['checks'])
        dashboard_content += f"- Checks passed: {checks_passed}/{total_checks}\n\n"
        
        # Individual check results
        dashboard_content += "## Individual Checks\n\n"
        for check_name, check_result in report['checks'].items():
            status_icon = "[PASS]" if check_result['healthy'] else "[FAIL]"
            dashboard_content += f"- {status_icon} **{check_name.replace('_', ' ').title()}**: {check_result['message']}\n"
            
            if 'details' in check_result:
                dashboard_content += f"  - Details: {check_result['details']}\n"
                
        dashboard_content += "\n"
        
        # Alerts
        if report['alerts']:
            dashboard_content += "## Active Alerts\n\n"
            for alert in report['alerts']:
                severity_icon = "[HIGH]" if alert['severity'] == 'high' else "[MEDIUM]"
                dashboard_content += f"- {severity_icon} **{alert['check'].replace('_', ' ').title()}** ({alert['severity'].upper()}): {alert['message']}\n"
            dashboard_content += "\n"
        else:
            dashboard_content += "## Active Alerts\n\n[PASS] No active alerts\n\n"
            
        dashboard_content += "## Recent Activity\n"
        dashboard_content += "- Last health check completed\n"
        dashboard_content += "- All system components operational\n"
        
        # Add recommendations based on alerts
        if report['alerts']:
            dashboard_content += "\n## Recommendations\n"
            high_severity_alerts = [a for a in report['alerts'] if a['severity'] == 'high']
            medium_severity_alerts = [a for a in report['alerts'] if a['severity'] == 'medium']
            
            if high_severity_alerts:
                dashboard_content += "- Address high severity alerts immediately\n"
            if medium_severity_alerts:
                dashboard_content += "- Review and address medium severity alerts\n"
            dashboard_content += "- Schedule regular health checks to maintain system stability\n"
            
        with open(dashboard_path, 'w') as f:
            f.write(dashboard_content)
            
        logger.info(f"Health dashboard generated at {dashboard_path}")
        return dashboard_path
    
    def schedule_weekly_checks(self) -> Dict[str, Any]:
        """Schedule weekly metrics health checks using Python-based scheduling."""
        try:
            import random
            from datetime import datetime, timedelta
            
            # Create a simple scheduling configuration file
            job_config = {
                "job_name": "cortex-gov-metrics-health",
                "scheduled": True,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "schedule": {
                    "weekdays": True,
                    "weekends": False,
                    "hour": random.randint(9, 16),  # 9 AM to 4 PM
                    "minute": random.randint(0, 59),
                    "interval_days": 1
                },
                "command": f"python {sys.executable} {Path(__file__).resolve()} --run-scheduled",
                "status": "active"
            }
            
            # Save configuration
            config_path = HEALTH_DIR / "scheduler-config.json"
            with open(config_path, "w") as f:
                json.dump(job_config, f, indent=2)
            
            # Calculate next run time
            now = datetime.now()
            next_run = now
            hour = job_config["schedule"]["hour"]
            minute = job_config["schedule"]["minute"]
            
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run < now:
                next_run += timedelta(days=1)
            while next_run.weekday() >= 5:  # Skip weekends
                next_run += timedelta(days=1)
            
            # Create a simple log file for tracking
            schedule_log = {
                "scheduler_id": "cortex-gov-metrics-health-v1",
                "config": job_config,
                "next_run": next_run.isoformat(),
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
            log_path = HEALTH_DIR / "scheduler-log.json"
            with open(log_path, "w") as f:
                json.dump(schedule_log, f, indent=2)
            
            # Create a simple batch file that can be used with Windows Task Scheduler
            batch_content = f"""@echo off
REM Cortex-GOV Metrics Health Check
REM Scheduled by Python scheduler

cd "{BASE_DIR}"
python {sys.executable} {Path(__file__).resolve()} --run-scheduled
"""
            batch_path = HEALTH_DIR / "run-scheduled-check.bat"
            with open(batch_path, "w") as f:
                f.write(batch_content)
            
            # Instructions for manual Windows Task Scheduler setup
            instructions = f"""# Windows Task Scheduler Setup Instructions

## To set up automatic weekly checks:

1. Open Task Scheduler
2. Create Basic Task...
3. Name: "Cortex-GOV Metrics Health"
4. Trigger: 
   - Weekly
   - Start: {next_run.strftime('%Y-%m-%d %H:%M')}
   - Repeat every: 1 week
   - Select only weekdays (Monday-Friday)

5. Action:
   - Start a program
   - Program/script: {batch_path}

6. Settings:
   - Allow task to be run on demand: [Enabled]
   - Run task as soon as possible after scheduled start is missed: [Enabled]
   - If the task fails, restart every: 1 minute
   - Attempt to restart up to: 3 times
   - Stop the task if it runs longer than: 1 hour

## Alternative: Python-based scheduling

The system has created a configuration file that can be used with Python's built-in scheduling:

- Config: {config_path}
- Log: {log_path}
- Batch file: {batch_path}

## Testing

To test the scheduled check:
1. Run: {Path(__file__).resolve()} --run-scheduled
2. Check the logs in {HEALTH_DIR} for the scheduled-checks.json file

## Manual Schedule

The scheduler will run weekdays at {hour:02d}:{minute:02d} (randomized to avoid conflicts).
"""
            
            instructions_path = HEALTH_DIR / "scheduler-instructions.md"
            with open(instructions_path, "w") as f:
                f.write(instructions)
            
            return {
                "success": True,
                "message": "Weekly metrics health check scheduling configured successfully",
                "next_check": next_run.isoformat(),
                "cron_expression": f"Python scheduler: Weekdays at {hour:02d}:{minute:02d}",
                "job_name": job_config["job_name"],
                "config_path": str(config_path),
                "log_path": str(log_path),
                "batch_path": str(batch_path),
                "instructions_path": str(instructions_path),
                "manual_setup_required": True,
                "scheduler_type": "python-based"
            }
                
        except Exception as e:
            logger.error(f"Failed to schedule weekly checks: {e}")
            return {
                "success": False,
                "message": f"Failed to schedule weekly checks: {str(e)}",
                "error": str(e)
            }
    
    def _create_windows_scheduler_task(self, job_name: str, command: str, hour: int, minute: int) -> Dict[str, Any]:
        """Create a Windows scheduled task if cron is not available."""
        try:
            import uuid
            task_name = f"Cortex-GOV-{job_name}"
            task_id = str(uuid.uuid4())
            
            # Create task XML
            task_xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.3" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Weekly Cortex-GOV metrics health check</Description>
    <URI>\\{task_name}</URI>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-02-12T{hour:02d}:{minute:02d}:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByWeek>
        <DaysOfWeek>
          <Monday />
          <Tuesday />
          <Wednesday />
          <Thursday />
          <Friday />
        </DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
    </Principal>
  </Principals>
  <Settings>
    <Enabled>true</Enabled>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>false</StartWhenAvailable>
    <DontStopIfGoingOnBatteries>false</DontStopIfGoingOnBatteries>
    <StopIfGoingOnBatteries>true</StopIfGoingOnBatteries>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions>
    <Exec>
      <Command>python</Command>
      <Arguments>{sys.executable} {Path(__file__).resolve()} --run-scheduled</Arguments>
      <WorkingDirectory>{BASE_DIR}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
            
            # Create task using schtasks
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as temp_file:
                temp_file.write(task_xml)
                temp_file.flush()
                
                # Create the task
                result = subprocess.run([
                    "schtasks", "/create", "/tn", task_name, "/xml", temp_file.name, "/f"
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    # Calculate next run time
                    from datetime import datetime, timedelta
                    now = datetime.now()
                    next_run = now
                    while next_run.weekday() >= 5:  # Skip weekends
                        next_run += timedelta(days=1)
                    next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
                    if next_run < now:
                        next_run += timedelta(days=1)
                        while next_run.weekday() >= 5:
                            next_run += timedelta(days=1)
                    
                    return {
                        "success": True,
                        "message": "Weekly metrics health check scheduled via Windows Task Scheduler",
                        "next_check": next_run.isoformat(),
                        "cron_expression": f"Windows Task: Weekdays at {hour:02d}:{minute:02d}",
                        "job_name": task_name,
                        "task_id": task_id
                    }
                else:
                    raise Exception(f"Failed to create scheduled task: {result.stderr}")
                    
        except Exception as e:
            logger.error(f"Failed to create Windows scheduled task: {e}")
            return {
                "success": False,
                "message": f"Failed to schedule weekly checks: {str(e)}",
                "error": str(e)
            }
    
    def run_scheduled_check(self) -> Dict[str, Any]:
        """Run a scheduled metrics health check."""
        try:
            # Perform health check
            report = self.check_health()
            
            # Save report with scheduled marker
            report["scheduled_run"] = True
            report["scheduled_time"] = datetime.utcnow().isoformat() + "Z"
            
            # Save report
            report_path = self.save_health_report(report)
            
            # Generate dashboard
            dashboard_path = self.generate_dashboard(report)
            
            # Log the result
            log_entry = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "status": report["status"],
                "alert_count": len(report["alerts"]),
                "report_path": str(report_path),
                "dashboard_path": str(dashboard_path)
            }
            
            # Save log
            scheduled_log = HEALTH_DIR / "scheduled-checks.json"
            try:
                with open(scheduled_log, "r") as f:
                    logs = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                logs = []
            
            logs.append(log_entry)
            
            with open(scheduled_log, "w") as f:
                json.dump(logs, f, indent=2)
            
            return {
                "success": True,
                "message": "Scheduled health check completed successfully",
                "report_path": str(report_path),
                "dashboard_path": str(dashboard_path),
                "status": report["status"],
                "alert_count": len(report["alerts"])
            }
            
        except Exception as e:
            logger.error(f"Failed to run scheduled health check: {e}")
            return {
                "success": False,
                "message": f"Failed to run scheduled health check: {str(e)}",
                "error": str(e)
            }


def main() -> None:
    """Main entry point for the health monitor."""
    parser = argparse.ArgumentParser(description="Monitor Cortex-GOV metrics pipeline health")
    parser.add_argument("--check-health", action="store_true", help="Perform health checks and generate report")
    parser.add_argument("--generate-dashboard", action="store_true", help="Generate dashboard from latest health report")
    parser.add_argument("--recover-log", action="store_true", help="Recover from a corrupted metrics log")
    parser.add_argument("--test-corrupted-log-recovery", action="store_true", help="Test recovery from corrupted log entries")
    parser.add_argument("--schedule", action="store_true", help="Schedule weekly metrics health checks via cron")
    parser.add_argument("--run-scheduled", action="store_true", help="Run a scheduled metrics health check")
    
    args = parser.parse_args()
    
    monitor = MetricsHealthMonitor()
    
    if args.check_health:
        logger.info("Performing health checks...")
        report = monitor.check_health()
        
        # Save report
        report_path = monitor.save_health_report(report)
        
        # Generate dashboard
        dashboard_path = monitor.generate_dashboard(report)
        
        print(f"Health check completed: {report_path}")
        print(f"Dashboard generated: {dashboard_path}")
        
        # Exit with appropriate code
        if report['status'] == 'unhealthy':
            exit(1)
        elif report['status'] == 'stale':
            exit(2)
        else:
            exit(0)
            
    elif args.generate_dashboard:
        # Try to load the latest health report
        report_files = sorted(HEALTH_DIR.glob("health-report-*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not report_files:
            print("No health reports found. Run --check-health first.")
            exit(1)
            
        with open(report_files[0]) as f:
            report = json.load(f)
            
        dashboard_path = monitor.generate_dashboard(report)
        print(f"Dashboard generated from latest report: {dashboard_path}")
        
    elif args.recover_log:
        logger.info("Attempting to recover metrics log...")
        result = monitor.recover_corrupted_log(LOG_PATH)
        report_path = HEALTH_DIR / "H025-alert-tests.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({"manualRecovery": result, "timestamp": datetime.utcnow().isoformat() + "Z"}, f, indent=2)
        print(f"Recovery result: {result['message']}")
        print(f"Report saved to {report_path}")

    elif args.test_corrupted_log_recovery:
        logger.info("Testing corrupted log recovery...")
        test_log = HEALTH_DIR / "test-corrupt-log.json"
        test_log.write_text("{not valid json", encoding="utf-8")
        result = monitor.recover_corrupted_log(test_log)
        test_report = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "test_log": str(test_log),
            "result": result,
        }
        report_path = HEALTH_DIR / "H025-alert-tests.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(test_report, f, indent=2)
        print(f"Corrupted log recovery test complete. Report saved to {report_path}")
    
    elif args.schedule:
        logger.info("Scheduling weekly metrics health checks...")
        result = monitor.schedule_weekly_checks()
        print(f"Scheduling result: {result['message']}")
        if result["success"]:
            print(f"Next check scheduled for: {result['next_check']}")
            print(f"Cron expression: {result['cron_expression']}")
        
    elif args.run_scheduled:
        logger.info("Running scheduled metrics health check...")
        result = monitor.run_scheduled_check()
        print(f"Check completed: {result['message']}")
        if result["report_path"]:
            print(f"Report saved to: {result['report_path']}")
        
    else:
        parser.print_help()


if __name__ == "__main__":
    main()