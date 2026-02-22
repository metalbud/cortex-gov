#!/usr/bin/env python3
"""
System Health Monitor for Cortex-GOV
Continuously monitors system metrics and generates optimization suggestions
"""

import json
import time
import psutil
import os
import sys
import subprocess
import requests
import re
from datetime import datetime, timezone, timedelta
from pathlib import Path
import argparse

class SystemHealthMonitor:
    def __init__(self, workspace_path=None):
        self.workspace_path = Path(workspace_path) if workspace_path else Path.cwd().parent
        self.metrics_dir = self.workspace_path / "artifacts" / "metrics"
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        # Health thresholds (configurable)
        self.thresholds = {
            "memory_usage_percent": 85.0,
            "cpu_usage_percent": 80.0,
            "disk_usage_percent": 90.0,
            "api_latency_ms": 1000.0,
            "error_rate_percent": 5.0
        }
        
    def collect_system_metrics(self):
        """Collect current system metrics"""
        metrics = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "memory": {
                "total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
                "used_gb": round(psutil.virtual_memory().used / (1024**3), 2),
                "usage_percent": round(psutil.virtual_memory().percent, 2)
            },
            "cpu": {
                "usage_percent": round(psutil.cpu_percent(interval=1), 2),
                "cores": psutil.cpu_count(),
                "load_avg": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            "disk": {
                "total_gb": round(psutil.disk_usage('/').total / (1024**3), 2),
                "used_gb": round(psutil.disk_usage('/').used / (1024**3), 2),
                "free_gb": round(psutil.disk_usage('/').free / (1024**3), 2),
                "usage_percent": round(psutil.disk_usage('/').percent, 2)
            },
            "python_process": {
                "memory_mb": round(psutil.Process().memory_info().rss / 1024 / 1024, 2),
                "threads": psutil.Process().num_threads(),
                "open_files": len(psutil.Process().open_files())
            }
        }
        
        # Add execution time metrics
        metrics["execution"] = self._collect_execution_metrics()
        
        # Add error rate metrics
        metrics["error_rates"] = self._collect_error_rates()
        
        # Add API latency metrics
        metrics["api_latency"] = self._collect_api_latency()
        
        return metrics
    
    def _to_serializable(self, obj):
        """Convert non-serializable objects to JSON-serializable format"""
        if isinstance(obj, Path):
            return str(obj)
        elif isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, (list, tuple)):
            return [self._to_serializable(item) for item in obj]
        elif isinstance(obj, dict):
            return {key: self._to_serializable(value) for key, value in obj.items()}
        else:
            return obj
    
    def _collect_execution_metrics(self):
        """Collect execution time metrics"""
        metrics = {}
        
        try:
            # Get process execution times
            proc = psutil.Process()
            metrics["process_user_time"] = round(proc.cpu_times().user, 2)
            metrics["process_system_time"] = round(proc.cpu_times().system, 2)
            metrics["process_create_time"] = round(proc.create_time(), 2)
            
            # Get command execution times (test some common commands)
            start_time = time.time()
            try:
                subprocess.run(["echo", "test"], capture_output=True, timeout=5)
                metrics["shell_command_time"] = round((time.time() - start_time) * 1000, 2)
            except:
                metrics["shell_command_time"] = None
                
        except Exception as e:
            metrics["error"] = f"Failed to collect execution metrics: {str(e)}"
        
        return metrics
    
    def _collect_error_rates(self):
        """Collect error rate metrics from logs"""
        metrics = {}
        
        try:
            # Look for error patterns in recent logs
            error_patterns = [
                r'ERROR|error|Error',
                r'FATAL|fatal|Fatal',
                r'Exception|exception',
                r'Traceback|traceback'
            ]
            
            # Check cortex-gov related log files
            log_locations = [
                Path.cwd().parent / "artifacts" / "verification",
                Path.cwd().parent / "artifacts" / "metrics",
                Path.cwd() / "logs"
            ]
            
            total_lines = 0
            error_count = 0
            recent_threshold = datetime.now(timezone.utc) - timedelta(hours=24)
            
            for log_dir in log_locations:
                if log_dir.exists():
                    for file_path in log_dir.rglob("*.md"):
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                total_lines += len(lines)
                                
                                # Check recent lines for errors
                                for line in lines[-100:]:  # Check last 100 lines
                                    line_time_str = line.strip().split(' ')[0] if line.strip() else ''
                                    try:
                                        line_time = datetime.strptime(line_time_str, '%Y-%m-%d')
                                        if line_time >= recent_threshold:
                                            for pattern in error_patterns:
                                                if re.search(pattern, line, re.IGNORECASE):
                                                    error_count += 1
                                                    break
                                    except ValueError:
                                        # If we can't parse the timestamp, check the line anyway
                                        for pattern in error_patterns:
                                            if re.search(pattern, line, re.IGNORECASE):
                                                error_count += 1
                                                break
                        except:
                            pass
            
            metrics["recent_errors_24h"] = error_count
            metrics["total_log_lines_sampled"] = total_lines
            metrics["error_rate_percent"] = round((error_count / max(total_lines, 1)) * 100, 4) if total_lines > 0 else 0
            
        except Exception as e:
            metrics["error"] = f"Failed to collect error rates: {str(e)}"
        
        return metrics
    
    def _collect_api_latency(self):
        """Collect API latency metrics"""
        metrics = {}
        
        try:
            # Test some common API endpoints
            test_endpoints = [
                "https://api.github.com",
                "https://httpbin.org/delay/1",  # This has artificial delay
            ]
            
            latencies = []
            for endpoint in test_endpoints:
                try:
                    start_time = time.time()
                    response = requests.get(endpoint, timeout=10)
                    latency = (time.time() - start_time) * 1000  # Convert to milliseconds
                    latencies.append(latency)
                except:
                    latencies.append(None)
            
            metrics["endpoint_latencies_ms"] = latencies
            metrics["avg_latency_ms"] = round(sum(l for l in latencies if l is not None) / len([l for l in latencies if l is not None]), 2) if any(l is not None for l in latencies) else None
            metrics["max_latency_ms"] = max([l for l in latencies if l is not None], default=None)
            metrics["min_latency_ms"] = min([l for l in latencies if l is not None], default=None)
            
        except Exception as e:
            metrics["error"] = f"Failed to collect API latency: {str(e)}"
        
        return metrics
    
    def check_thresholds(self, metrics):
        """Check metrics against thresholds and return warnings"""
        warnings = []
        
        # Memory warnings
        if metrics["memory"]["usage_percent"] > self.thresholds["memory_usage_percent"]:
            warnings.append({
                "type": "memory_high_usage",
                "message": f"Memory usage at {metrics['memory']['usage_percent']}% (threshold: {self.thresholds['memory_usage_percent']}%)",
                "severity": "warning" if metrics["memory"]["usage_percent"] < 95 else "critical"
            })
        
        # CPU warnings
        if metrics["cpu"]["usage_percent"] > self.thresholds["cpu_usage_percent"]:
            warnings.append({
                "type": "high_cpu_usage",
                "message": f"CPU usage at {metrics['cpu']['usage_percent']}% (threshold: {self.thresholds['cpu_usage_percent']}%)",
                "severity": "warning" if metrics["cpu"]["usage_percent"] < 95 else "critical"
            })
        
        # Disk warnings
        if metrics["disk"]["usage_percent"] > self.thresholds["disk_usage_percent"]:
            warnings.append({
                "type": "disk_high_usage",
                "message": f"Disk usage at {metrics['disk']['usage_percent']}% (threshold: {self.thresholds['disk_usage_percent']}%)",
                "severity": "warning" if metrics["disk"]["usage_percent"] < 95 else "critical"
            })
        
        # Process warnings
        if metrics["python_process"]["memory_mb"] > 500:  # 500MB threshold
            warnings.append({
                "type": "process_memory_high",
                "message": f"Python process using {metrics['python_process']['memory_mb']}MB memory",
                "severity": "warning"
            })
        
        return warnings
    
    def save_metrics(self, metrics, warnings):
        """Save metrics to JSON file"""
        filename = f"system-health-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        filepath = self.metrics_dir / filename
        
        data = {
            "metrics": self._to_serializable(metrics),
            "warnings": self._to_serializable(warnings),
            "thresholds": self._to_serializable(self.thresholds)
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"Metrics saved to {filepath}")
        return filepath
    
    def generate_dashboard(self):
        """Generate a simple text-based dashboard"""
        metrics = self.collect_system_metrics()
        warnings = self.check_thresholds(metrics)
        
        dashboard = f"""
# System Health Dashboard
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S %Z')}

## Resource Usage
- Memory: {metrics['memory']['used_gb']:.1f}GB / {metrics['memory']['total_gb']:.1f}GB ({metrics['memory']['usage_percent']:.1f}%)
- CPU: {metrics['cpu']['usage_percent']:.1f}% (Load: {metrics['cpu']['load_avg'][0]:.2f})
- Disk: {metrics['disk']['used_gb']:.1f}GB / {metrics['disk']['total_gb']:.1f}GB ({metrics['disk']['usage_percent']:.1f}%)
- Python Process: {metrics['python_process']['memory_mb']:.1f}MB, {metrics['python_process']['threads']} threads

## Warnings ({len(warnings)})
"""
        
        if warnings:
            for warning in warnings:
                dashboard += f"- {warning['severity'].upper()}: {warning['message']}\n"
        else:
            dashboard += "- All metrics within normal thresholds\n"
        
        # Save dashboard
        dashboard_filename = f"system-health-dashboard-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        dashboard_path = self.metrics_dir / dashboard_filename
        
        with open(dashboard_path, 'w') as f:
            f.write(dashboard)
        
        print(f"Dashboard saved to {dashboard_path}")
        return dashboard_path
    
    def suggest_optimizations(self):
        """Generate optimization suggestions based on collected metrics"""
        metrics = self.collect_system_metrics()
        warnings = self.check_thresholds(metrics)
        
        suggestions = []
        
        # Memory-based suggestions
        if metrics["memory"]["usage_percent"] > 75:
            suggestions.append({
                "priority": "high" if metrics["memory"]["usage_percent"] > 85 else "medium",
                "category": "memory_optimization",
                "title": "Memory Usage Optimization",
                "description": f"High memory usage detected: {metrics['memory']['usage_percent']}%",
                "actions": [
                    "Review running processes and terminate unnecessary ones",
                    "Check for memory leaks in long-running applications",
                    "Consider increasing system RAM if usage consistently high",
                    "Implement memory cleanup routines in applications"
                ]
            })
        
        # CPU-based suggestions
        if metrics["cpu"]["usage_percent"] > 75:
            suggestions.append({
                "priority": "high" if metrics["cpu"]["usage_percent"] > 85 else "medium",
                "category": "cpu_optimization",
                "title": "CPU Usage Optimization",
                "description": f"High CPU usage detected: {metrics['cpu']['usage_percent']}%",
                "actions": [
                    "Identify CPU-intensive processes and optimize them",
                    "Consider load balancing for CPU-heavy workloads",
                    "Review and optimize algorithms for better efficiency",
                    "Implement caching strategies to reduce recomputation"
                ]
            })
        
        # Disk-based suggestions
        if metrics["disk"]["usage_percent"] > 75:
            suggestions.append({
                "priority": "high" if metrics["disk"]["usage_percent"] > 85 else "medium",
                "category": "disk_optimization",
                "title": "Disk Space Optimization",
                "description": f"High disk usage detected: {metrics['disk']['usage_percent']}%",
                "actions": [
                    "Clean up temporary files and unnecessary data",
                    "Archive or compress old logs and documents",
                    "Consider expanding storage capacity",
                    "Implement data retention policies"
                ]
            })
        
        # Process-specific suggestions
        if metrics["python_process"]["memory_mb"] > 300:
            suggestions.append({
                "priority": "medium",
                "category": "python_optimization",
                "title": "Python Process Optimization",
                "description": f"Python process using {metrics['python_process']['memory_mb']}MB memory",
                "actions": [
                    "Review Python application code for memory leaks",
                    "Implement proper cleanup of objects and resources",
                    "Consider using memory-efficient data structures",
                    "Monitor and profile Python application memory usage"
                ]
            })
        
        # Save optimization suggestions
        suggestions_filename = f"optimization-suggestions-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        suggestions_path = self.metrics_dir / suggestions_filename
        
        optimization_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metrics": metrics,
            "warnings": warnings,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions)
        }
        
        with open(suggestions_path, 'w') as f:
            json.dump(optimization_report, f, indent=2)
        
        print(f"Optimization suggestions saved to {suggestions_path}")
        return suggestions_path
    
    def run_quarterly_optimization(self):
        """Execute quarterly system optimization cycle with human review"""
        print("Starting quarterly system optimization cycle...")
        
        # Collect current metrics
        metrics = self.collect_system_metrics()
        warnings = self.check_thresholds(metrics)
        suggestions_data = self.suggest_optimizations()
        
        # Load the suggestions data from the saved file
        try:
            with open(suggestions_data, 'r') as f:
                suggestions = json.load(f)
        except:
            suggestions = {}
        
        # Generate optimization report
        report = {
            "cycle_start": datetime.now(timezone.utc).isoformat(),
            "cycle_type": "quarterly",
            "metrics": metrics,
            "warnings": warnings,
            "suggestions": suggestions,
            "executed_optimizations": [],
            "human_review_required": True,
            "human_review_status": "pending",
            "human_reviewer": None,
            "review_comments": None
        }
        
        # Save initial report
        report_filename = f"quarterly-optimization-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        report_path = self.metrics_dir / report_filename
        
        with open(report_path, 'w') as f:
            json.dump(self._to_serializable(report), f, indent=2)
        
        print(f"Quarterly optimization report saved to {report_path}")
        print(f"Human review required: {report['human_review_required']}")
        print(f"Report location: {report_path}")
        
        return report_path
    
    def approve_optimization_cycle(self, report_path, reviewer_name, comments=None):
        """Approve and execute an optimization cycle"""
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
            
            if report["human_review_required"]:
                report["human_review_status"] = "approved"
                report["human_reviewer"] = reviewer_name
                report["review_comments"] = comments
                report["approval_timestamp"] = datetime.now(timezone.utc).isoformat()
                
                # Execute optimizations based on suggestions
                executed = []
                for suggestion in report["suggestions"].get("suggestions", []):
                    if suggestion.get("priority") in ["high", "medium"]:
                        optimization_result = self._execute_optimization(suggestion)
                        executed.append({
                            "suggestion": suggestion,
                            "result": optimization_result,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        })
                
                report["executed_optimizations"] = executed
                report["cycle_end"] = datetime.now(timezone.utc).isoformat()
                
                # Save updated report
                with open(report_path, 'w') as f:
                    json.dump(report, f, indent=2)
                
                print(f"Optimization cycle completed and saved to {report_path}")
                return True
            else:
                print("No human review required for this optimization cycle.")
                return False
                
        except Exception as e:
            print(f"Error approving optimization cycle: {str(e)}")
            return False
    
    def _execute_optimization(self, suggestion):
        """Execute a specific optimization suggestion"""
        result = {
            "suggestion_id": suggestion.get("title", "unknown"),
            "status": "attempted",
            "details": {},
            "rollback_info": {}
        }
        
        try:
            category = suggestion.get("category", "")
            actions = suggestion.get("actions", [])
            
            if "memory_optimization" in category:
                # Example: Clear system cache
                try:
                    subprocess.run(["sync"], shell=True, timeout=10)
                    result["details"]["cache_cleared"] = True
                except:
                    result["details"]["cache_cleared"] = False
                    
            elif "disk_optimization" in category:
                # Example: Clean temporary files (simulate)
                result["details"]["temp_files_cleaned"] = "simulated"
                
            # Record rollback information
            result["rollback_info"]["original_metrics"] = self.collect_system_metrics()
            result["rollback_info"]["revert_command"] = "system_health_monitor --revert-optimization"
            
        except Exception as e:
            result["status"] = "failed"
            result["error"] = str(e)
        
        return result
    
    def continuous_monitor(self, interval_seconds=60):
        """Run continuous monitoring"""
        print(f"Starting continuous monitoring every {interval_seconds} seconds...")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                metrics = self.collect_system_metrics()
                warnings = self.check_thresholds(metrics)
                self.save_metrics(metrics, warnings)
                
                # Print status
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Memory: {metrics['memory']['usage_percent']:.1f}%, CPU: {metrics['cpu']['usage_percent']:.1f}%")
                
                if warnings:
                    for warning in warnings:
                        print(f"  WARNING: {warning['message']}")
                
                time.sleep(interval_seconds)
        except KeyboardInterrupt:
            print("\nMonitoring stopped.")
    
    def status(self):
        """Get current system status"""
        metrics = self.collect_system_metrics()
        warnings = self.check_thresholds(metrics)
        
        print("## System Status")
        print(f"Memory: {metrics['memory']['usage_percent']:.1f}%")
        print(f"CPU: {metrics['cpu']['usage_percent']:.1f}%")
        print(f"Disk: {metrics['disk']['usage_percent']:.1f}%")
        print(f"Python Process: {metrics['python_process']['memory_mb']:.1f}MB")
        
        if warnings:
            print("\n## Warnings")
            for warning in warnings:
                print(f"- {warning['severity'].upper()}: {warning['message']}")
        else:
            print("\n## Status: All metrics within normal thresholds")


def main():
    parser = argparse.ArgumentParser(description="System Health Monitor for Cortex-GOV")
    parser.add_argument("--status", action="store_true", help="Show current system status")
    parser.add_argument("--capture", action="store_true", help="Capture metrics once")
    parser.add_argument("--continuous", action="store_true", help="Run continuous monitoring")
    parser.add_argument("--generate-dashboard", action="store_true", help="Generate dashboard")
    parser.add_argument("--suggest-optimizations", action="store_true", help="Generate optimization suggestions")
    parser.add_argument("--quarterly-optimization", action="store_true", help="Execute quarterly optimization cycle")
    parser.add_argument("--approve-optimization", type=str, help="Path to optimization report file to approve")
    parser.add_argument("--reviewer", type=str, help="Name of reviewer (required for --approve-optimization)")
    parser.add_argument("--comments", type=str, help="Review comments")
    parser.add_argument("--revert-optimization", action="store_true", help="Revert last optimization")
    parser.add_argument("--interval", type=int, default=60, help="Interval for continuous monitoring in seconds")
    parser.add_argument("--workspace", type=str, help="Path to cortex-gov workspace")
    
    args = parser.parse_args()
    
    # Initialize monitor
    monitor = SystemHealthMonitor(args.workspace)
    
    if args.status:
        monitor.status()
    elif args.capture:
        metrics = monitor.collect_system_metrics()
        warnings = monitor.check_thresholds(metrics)
        monitor.save_metrics(metrics, warnings)
    elif args.continuous:
        monitor.continuous_monitor(args.interval)
    elif args.generate_dashboard:
        monitor.generate_dashboard()
    elif args.suggest_optimizations:
        monitor.suggest_optimizations()
    elif args.quarterly_optimization:
        monitor.run_quarterly_optimization()
    elif args.approve_optimization:
        if not args.reviewer:
            print("Error: --reviewer is required when using --approve-optimization")
            return
        monitor.approve_optimization_cycle(args.approve_optimization, args.reviewer, args.comments)
    elif args.revert_optimization:
        print("Revert optimization functionality would be implemented here")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()