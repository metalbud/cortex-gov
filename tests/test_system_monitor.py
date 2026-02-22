from tools.monitoring.system_monitor import AlertManager, SystemMonitor, validate_config


def test_validate_config_accepts_defaults():
    config = {"collection_interval": 5, "export_interval": 60, "enabled_metrics": ["cpu_usage"]}
    result = validate_config(config)
    assert result["valid"] is True


def test_alert_manager_policy_and_trigger():
    manager = AlertManager(log_dir="artifacts/logs")
    manager.add_alert_policy(
        policy_id="cpu_high",
        metric_name="cpu_usage",
        condition="gt",
        threshold=1,
        severity="high",
        name="CPU High",
        message_template="CPU is {value}"
    )

    alerts = manager.evaluate_metric("cpu_usage", 5)
    assert len(alerts) == 1


def test_system_monitor_initialization():
    manager = AlertManager(log_dir="artifacts/logs")
    monitor = SystemMonitor(manager)
    assert monitor.monitoring_config["collection_interval"] == 5
