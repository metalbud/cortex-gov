#!/usr/bin/env python3
"""
System-wide Monitoring and Alerting for Cortex GOV
Provides real-time monitoring, metrics collection, and alerting capabilities
"""

import json
import logging
import os
import psutil
import time
import argparse
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import threading
import queue
import subprocess
import sys
from collections import defaultdict, deque


class Alert:
    """Represents an alert with severity and threshold information"""
    
    def __init__(self, 
                 alert_id: str,
                 name: str,
                 severity: str,  # "low", "medium", "high", "critical"
                 message: str,
                 threshold: float,
                 current_value: float,
                 metric_name: str):
        self.alert_id = alert_id
        self.name = name
        self.severity = severity
        self.message = message
        self.threshold = threshold
        self.current_value = current_value
        self.metric_name = metric_name
        self.timestamp = datetime.now()
        self.resolved = False
        self.resolution_time = None
    
    def resolve(self):
        """Mark the alert as resolved"""
        self.resolved = True
        self.resolution_time = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary representation"""
        return {
            "alert_id": self.alert_id,
            "name": self.name,
            "severity": self.severity,
            "message": self.message,
            "threshold": self.threshold,
            "current_value": self.current_value,
            "metric_name": self.metric_name,
            "timestamp": self.timestamp.isoformat(),
            "resolved": self.resolved,
            "resolution_time": self.resolution_time.isoformat() if self.resolution_time else None
        }


class AlertManager:
    """Manages alerts, notifications, and alert policies"""
    
    def __init__(self, log_dir: str = "artifacts/logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("AlertManager")
        
        # Alert storage
        self.active_alerts = {}
        self.resolved_alerts = deque(maxlen=1000)  # Keep last 1000 resolved alerts
        
        # Alert policies
        self.alert_policies = {}
        
        # Notification handlers
        self.notification_handlers = []
        
        # Alert statistics
        self.alert_stats = {
            "total_alerts": 0,
            "active_alerts": 0,
            "resolved_alerts": 0,
            "critical_alerts": 0,
            "high_severity_alerts": 0
        }
    
    def add_alert_policy(self, 
                         policy_id: str,
                         metric_name: str,
                         condition: str,  # "gt", "lt", "eq", "ne"
                         threshold: float,
                         severity: str,
                         name: str,
                         message_template: str):
        """Add an alert policy"""
        self.alert_policies[policy_id] = {
            "metric_name": metric_name,
            "condition": condition,
            "threshold": threshold,
            "severity": severity,
            "name": name,
            "message_template": message_template
        }
        self.logger.info(f"Added alert policy: {policy_id}")
    
    def evaluate_metric(self, 
                        metric_name: str, 
                        current_value: float, 
                        timestamp: datetime = None) -> List[Alert]:
        """Evaluate a metric against all alert policies"""
        if timestamp is None:
            timestamp = datetime.now()
        
        alerts_triggered = []
        
        for policy_id, policy in self.alert_policies.items():
            if policy["metric_name"] != metric_name:
                continue
            
            # Check condition
            trigger_alert = False
            message = ""
            
            if policy["condition"] == "gt" and current_value > policy["threshold"]:
                trigger_alert = True
                message = policy["message_template"].format(
                    value=current_value, threshold=policy["threshold"]
                )
            elif policy["condition"] == "lt" and current_value < policy["threshold"]:
                trigger_alert = True
                message = policy["message_template"].format(
                    value=current_value, threshold=policy["threshold"]
                )
            elif policy["condition"] == "eq" and current_value == policy["threshold"]:
                trigger_alert = True
                message = policy["message_template"].format(
                    value=current_value, threshold=policy["threshold"]
                )
            elif policy["condition"] == "ne" and current_value != policy["threshold"]:
                trigger_alert = True
                message = policy["message_template"].format(
                    value=current_value, threshold=policy["threshold"]
                )
            
            if trigger_alert:
                # Check if alert already exists
                existing_alert_id = f"{policy_id}_{metric_name}_{timestamp.strftime('%Y%m%d%H%M%S')}"
                
                if existing_alert_id not in self.active_alerts:
                    alert = Alert(
                        alert_id=existing_alert_id,
                        name=policy["name"],
                        severity=policy["severity"],
                        message=message,
                        threshold=policy["threshold"],
                        current_value=current_value,
                        metric_name=metric_name
                    )
                    
                    alerts_triggered.append(alert)
                    self.active_alerts[existing_alert_id] = alert
                    self.alert_stats["total_alerts"] += 1
                    self.alert_stats["active_alerts"] += 1
                    
                    if policy["severity"] == "critical":
                        self.alert_stats["critical_alerts"] += 1
                    elif policy["severity"] == "high":
                        self.alert_stats["high_severity_alerts"] += 1
                    
                    self.logger.warning(f"Alert triggered: {alert.name} - {message}")
                    self._send_notifications(alert)
        
        return alerts_triggered
    
    def resolve_alert(self, alert_id: str) -> bool:
        """Resolve an alert by ID"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert.resolve()
            
            # Move to resolved alerts
            del self.active_alerts[alert_id]
            self.resolved_alerts.append(alert)
            
            # Update stats
            self.alert_stats["active_alerts"] -= 1
            self.alert_stats["resolved_alerts"] += 1
            
            self.logger.info(f"Alert resolved: {alert.name}")
            self._send_notifications(alert, resolved=True)
            
            return True
        return False
    
    def resolve_all_alerts(self):
        """Resolve all active alerts"""
        alert_ids = list(self.active_alerts.keys())
        for alert_id in alert_ids:
            self.resolve_alert(alert_id)
    
    def _send_notifications(self, alert: Alert, resolved: bool = False):
        """Send notifications for an alert"""
        notification_type = "resolved" if resolved else "triggered"
        
        for handler in self.notification_handlers:
            try:
                handler.send(alert, notification_type)
            except Exception as e:
                self.logger.error(f"Notification failed for {handler.__class__.__name__}: {e}")
    
    def add_notification_handler(self, handler):
        """Add a notification handler"""
        self.notification_handlers.append(handler)
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts"""
        return list(self.active_alerts.values())
    
    def get_alert_stats(self) -> Dict[str, Any]:
        """Get alert statistics"""
        return self.alert_stats.copy()
    
    def export_alerts(self, output_path: str = None, include_resolved: bool = True) -> str:
        """Export alerts to JSON file"""
        if output_path is None:
            output_path = self.log_dir / f"alerts_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "stats": self.alert_stats,
            "active_alerts": [alert.to_dict() for alert in self.get_active_alerts()]
        }
        
        if include_resolved:
            export_data["resolved_alerts"] = [alert.to_dict() for alert in self.resolved_alerts]
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Alerts exported to: {output_path}")
        return output_path


class SystemMonitor:
    """Main system monitoring component"""
    
    def __init__(self, 
                 alert_manager: AlertManager,
                 metrics_dir: str = "artifacts/metrics",
                 log_dir: str = "artifacts/logs"):
        self.alert_manager = alert_manager
        self.metrics_dir = Path(metrics_dir)
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = logging.getLogger("SystemMonitor")
        
        # Metrics collection
        self.metrics = defaultdict(lambda: deque(maxlen=1000))  # Keep last 1000 values
        self.metric_metadata = {}
        
        # Monitoring configuration
        self.monitoring_config = {
            "collection_interval": 5,  # seconds
            "export_interval": 60,    # seconds
            "enabled_metrics": [
                "cpu_usage", "memory_usage", "disk_usage", "disk_io",
                "network_io", "process_count", "thread_count"
            ]
        }
        
        # Threading
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        self.metrics_queue = queue.Queue()
        
        # Initialize default alert policies
        self._initialize_default_alert_policies()
        
        # Setup notification handlers
        self._setup_notification_handlers()
    
    def _initialize_default_alert_policies(self):
        """Initialize default alert policies for system metrics"""
        # CPU Usage
        self.alert_manager.add_alert_policy(
            policy_id="cpu_high_usage",
            metric_name="cpu_usage",
            condition="gt",
            threshold=80.0,
            severity="high",
            name="High CPU Usage",
            message_template="CPU usage is {value:.1f}% (threshold: {threshold}%)"
        )
        
        self.alert_manager.add_alert_policy(
            policy_id="cpu_critical_usage",
            metric_name="cpu_usage",
            condition="gt",
            threshold=95.0,
            severity="critical",
            name="Critical CPU Usage",
            message_template="CPU usage is {value:.1f}% (threshold: {threshold}%) - System performance degraded"
        )
        
        # Memory Usage
        self.alert_manager.add_alert_policy(
            policy_id="memory_high_usage",
            metric_name="memory_usage",
            condition="gt",
            threshold=85.0,
            severity="high",
            name="High Memory Usage",
            message_template="Memory usage is {value:.1f}% (threshold: {threshold}%)"
        )
        
        self.alert_manager.add_alert_policy(
            policy_id="memory_critical_usage",
            metric_name="memory_usage",
            condition="gt",
            threshold=95.0,
            severity="critical",
            name="Critical Memory Usage",
            message_template="Memory usage is {value:.1f}% (threshold: {threshold}%) - Risk of system instability"
        )
        
        # Disk Usage
        self.alert_manager.add_alert_policy(
            policy_id="disk_high_usage",
            metric_name="disk_usage",
            condition="gt",
            threshold=90.0,
            severity="high",
            name="High Disk Usage",
            message_template="Disk usage is {value:.1f}% (threshold: {threshold}%)"
        )
        
        self.alert_manager.add_alert_policy(
            policy_id="disk_critical_usage",
            metric_name="disk_usage",
            condition="gt",
            threshold=98.0,
            severity="critical",
            name="Critical Disk Usage",
            message_template="Disk usage is {value:.1f}% (threshold: {threshold}%) - Risk of disk full error"
        )
    
    def _setup_notification_handlers(self):
        """Setup default notification handlers"""
        # Console notification handler
        self.alert_manager.add_notification_handler(ConsoleNotificationHandler())
        
        # File notification handler
        self.alert_manager.add_notification_handler(FileNotificationHandler(self.log_dir))
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect system metrics"""
        metrics = {}
        
        try:
            # CPU Usage
            cpu_percent = psutil.cpu_percent(interval=1)
            metrics["cpu_usage"] = cpu_percent
            
            # Memory Usage
            memory = psutil.virtual_memory()
            metrics["memory_usage"] = memory.percent
            metrics["memory_total_gb"] = memory.total / (1024**3)
            metrics["memory_available_gb"] = memory.available / (1024**3)
            metrics["memory_used_gb"] = memory.used / (1024**3)
            
            # Disk Usage
            disk_root = os.path.abspath(os.sep)
            disk = psutil.disk_usage(disk_root)
            metrics["disk_usage"] = disk.percent
            metrics["disk_total_gb"] = disk.total / (1024**3)
            metrics["disk_free_gb"] = disk.free / (1024**3)
            metrics["disk_used_gb"] = disk.used / (1024**3)
            
            # Disk I/O
            disk_io = psutil.disk_io_counters()
            if disk_io:
                metrics["disk_read_bytes"] = disk_io.read_bytes
                metrics["disk_write_bytes"] = disk_io.write_bytes
                metrics["disk_read_count"] = disk_io.read_count
                metrics["disk_write_count"] = disk_io.write_count
            
            # Network I/O
            net_io = psutil.net_io_counters()
            if net_io:
                metrics["network_bytes_sent"] = net_io.bytes_sent
                metrics["network_bytes_recv"] = net_io.bytes_recv
                metrics["network_packets_sent"] = net_io.packets_sent
                metrics["network_packets_recv"] = net_io.packets_recv
            
            # Process Information
            metrics["process_count"] = len(psutil.pids())
            metrics["thread_count"] = sum(p.num_threads() for p in psutil.process_iter(['num_threads']) if p.info['num_threads'])
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
        
        return metrics
    
    def record_metric(self, metric_name: str, value: float, timestamp: datetime = None):
        """Record a metric value"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": timestamp.isoformat()
        })
    
    def start_monitoring(self):
        """Start the monitoring thread"""
        if self.monitoring_thread is not None and self.monitoring_thread.is_alive():
            self.logger.warning("Monitoring is already running")
            return
        
        self.stop_event.clear()
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        self.logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        if self.monitoring_thread is None:
            return
        
        self.stop_event.set()
        self.monitoring_thread.join(timeout=5)
        self.logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        last_export_time = time.time()
        
        while not self.stop_event.is_set():
            try:
                # Collect metrics
                metrics = self.collect_system_metrics()
                
                # Record metrics
                timestamp = datetime.now()
                for metric_name, value in metrics.items():
                    self.record_metric(metric_name, value, timestamp)
                    
                    # Evaluate against alert policies
                    self.alert_manager.evaluate_metric(metric_name, value, timestamp)
                
                # Export metrics periodically
                current_time = time.time()
                if current_time - last_export_time >= self.monitoring_config["export_interval"]:
                    self.export_metrics()
                    last_export_time = current_time
                
                # Wait for next collection
                time.sleep(self.monitoring_config["collection_interval"])
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(5)  # Wait before retrying
    
    def export_metrics(self, output_path: str = None) -> str:
        """Export collected metrics to JSON file"""
        if output_path is None:
            output_path = self.metrics_dir / f"system_metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            "timestamp": datetime.now().isoformat(),
            "config": self.monitoring_config,
            "metrics": {}
        }
        
        # Convert metrics to export format
        for metric_name, values in self.metrics.items():
            export_data["metrics"][metric_name] = list(values)
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        self.logger.info(f"Metrics exported to: {output_path}")
        return output_path
    
    def get_metric_summary(self, metric_name: str = None) -> Dict[str, Any]:
        """Get summary statistics for a metric or all metrics"""
        if metric_name and metric_name in self.metrics:
            values = [entry["value"] for entry in self.metrics[metric_name]]
            
            if not values:
                return {}
            
            return {
                "metric_name": metric_name,
                "count": len(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "latest": values[-1] if values else None,
                "first_timestamp": self.metrics[metric_name][0]["timestamp"] if self.metrics[metric_name] else None,
                "last_timestamp": self.metrics[metric_name][-1]["timestamp"] if self.metrics[metric_name] else None
            }
        else:
            # Return summary for all metrics
            summary = {}
            for name in self.metrics.keys():
                summary[name] = self.get_metric_summary(name)
            return summary
    
    def validate_system_health(self) -> Dict[str, Any]:
        """Validate overall system health based on metrics and alerts"""
        health_status = {
            "overall": "healthy",
            "timestamp": datetime.now().isoformat(),
            "alert_count": len(self.alert_manager.get_active_alerts()),
            "metrics_summary": self.get_metric_summary(),
            "recommendations": []
        }
        
        # Check for critical alerts
        critical_alerts = [alert for alert in self.alert_manager.get_active_alerts() 
                          if alert.severity == "critical"]
        
        if critical_alerts:
            health_status["overall"] = "critical"
            health_status["critical_alerts"] = [alert.to_dict() for alert in critical_alerts]
        
        # Check for high severity alerts
        high_alerts = [alert for alert in self.alert_manager.get_active_alerts() 
                      if alert.severity == "high"]
        
        if high_alerts and health_status["overall"] != "critical":
            health_status["overall"] = "warning"
            health_status["high_alerts"] = [alert.to_dict() for alert in high_alerts]
        
        # Generate recommendations based on metrics
        metrics_summary = health_status["metrics_summary"]
        
        if "cpu_usage" in metrics_summary:
            if metrics_summary["cpu_usage"]["avg"] > 70:
                health_status["recommendations"].append(
                    f"High CPU usage detected (avg: {metrics_summary['cpu_usage']['avg']:.1f}%) - Consider optimizing processes"
                )
        
        if "memory_usage" in metrics_summary:
            if metrics_summary["memory_usage"]["avg"] > 80:
                health_status["recommendations"].append(
                    f"High memory usage detected (avg: {metrics_summary['memory_usage']['avg']:.1f}%) - Check for memory leaks"
                )
        
        if "disk_usage" in metrics_summary:
            if metrics_summary["disk_usage"]["avg"] > 85:
                health_status["recommendations"].append(
                    f"High disk usage detected (avg: {metrics_summary['disk_usage']['avg']:.1f}%) - Clean up unnecessary files"
                )
        
        return health_status


class ConsoleNotificationHandler:
    """Console notification handler for alerts"""
    
    def send(self, alert: Alert, notification_type: str):
        """Send alert notification to console"""
        if notification_type == "triggered":
            print(f"\n🚨 ALERT: {alert.severity.upper()} - {alert.name}")
            print(f"   Message: {alert.message}")
            print(f"   Metric: {alert.metric_name} = {alert.current_value} (threshold: {alert.threshold})")
            print(f"   Time: {alert.timestamp}")
        else:  # resolved
            print(f"\n✅ RESOLVED: {alert.name}")
            print(f"   Time: {alert.timestamp}")


class FileNotificationHandler:
    """File notification handler for alerts"""
    
    def __init__(self, log_dir: str):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.alert_log = self.log_dir / "alerts.log"
    
    def send(self, alert: Alert, notification_type: str):
        """Send alert notification to file"""
        with open(self.alert_log, 'a') as f:
            timestamp = alert.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            if notification_type == "triggered":
                f.write(f"[{timestamp}] ALERT {alert.severity.upper()}: {alert.name}\n")
                f.write(f"  Message: {alert.message}\n")
                f.write(f"  Metric: {alert.metric_name} = {alert.current_value} (threshold: {alert.threshold})\n")
            else:  # resolved
                f.write(f"[{timestamp}] RESOLVED: {alert.name}\n")
            f.write("\n")


def load_config(config_path: str) -> Dict[str, Any]:
    """Load monitoring config from JSON file."""
    if not Path(config_path).exists():
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Validate monitoring configuration."""
    errors = []
    if "collection_interval" in config and config["collection_interval"] <= 0:
        errors.append("collection_interval must be > 0")
    if "export_interval" in config and config["export_interval"] <= 0:
        errors.append("export_interval must be > 0")
    if "enabled_metrics" in config and not isinstance(config["enabled_metrics"], list):
        errors.append("enabled_metrics must be a list")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "config": config
    }


def main():
    """Main function for testing, validation, and monitoring."""
    parser = argparse.ArgumentParser(description="Cortex GOV System Monitor")
    parser.add_argument("--validate", action="store_true", help="Validate monitoring config")
    parser.add_argument("--config", default="artifacts/monitoring/monitor-config.json", help="Path to monitoring config")
    parser.add_argument("--run", action="store_true", help="Run system monitoring")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    if args.validate:
        config = load_config(args.config)
        result = validate_config(config)
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["valid"] else 1)

    if args.run:
        alert_manager = AlertManager()
        system_monitor = SystemMonitor(alert_manager)

        config = load_config(args.config)
        if config:
            system_monitor.monitoring_config.update(config)

        system_monitor.start_monitoring()

        try:
            print("System monitoring running... Press Ctrl+C to stop")
            while True:
                time.sleep(1)
                if int(time.time()) % 30 == 0:
                    print(f"\nSystem Health: {system_monitor.validate_system_health()['overall']}")
                    print(f"Active Alerts: {len(alert_manager.get_active_alerts())}")
                    print(f"CPU Usage: {system_monitor.get_metric_summary('cpu_usage')['latest']:.1f}%")
                    print(f"Memory Usage: {system_monitor.get_metric_summary('memory_usage')['latest']:.1f}%")
                    print("-" * 50)
        except KeyboardInterrupt:
            print("\nStopping monitoring...")
            system_monitor.stop_monitoring()
            metrics_path = system_monitor.export_metrics()
            alerts_path = alert_manager.export_alerts()
            print(f"Metrics exported to: {metrics_path}")
            print(f"Alerts exported to: {alerts_path}")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
