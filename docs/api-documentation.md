# Cortex-GOV API Documentation

This document provides comprehensive API documentation for all Cortex-GOV tools and components.

## Overview

Cortex-GOV consists of multiple tools organized into different categories:
- Self-Improvement Tools
- GUI and Launcher Tools  
- Analysis Tools
- Performance and Monitoring Tools
- System Integration Tools

## Self-Improvement Tools

### proposal_manager.py

**Purpose**: Create, manage, and approve improvement proposals with safety gates and trend context.

**Usage**:
```bash
python tools/self_improvement/proposal_manager.py <command> [options]
```

**Commands**:
- `create`: Create a new improvement proposal
- `show`: Display a specific proposal
- `list`: List all proposals
- `update`: Update proposal status
- `approve`: Approve a proposal
- `reject`: Reject a proposal
- `implement`: Mark proposal as implemented
- `rollback`: Rollback implemented changes
- `validate`: Validate proposal against safety requirements

**Example - Create Proposal**:
```bash
python tools/self_improvement/proposal_manager.py create \
  --title "Improve System Documentation" \
  --what "Add comprehensive API documentation" \
  --why "Current documentation lacks tool-specific usage examples" \
  --evidence tools/analysis/backlog_analyzer.py \
  --type workflow \
  --source meta_agent \
  --proposed-by agent \
  --priority P1 \
  --expected-impact "Improve developer onboarding" \
  --risk-level low \
  --risk-concern "None identified" \
  --risk-mitigation "Review documentation thoroughly" \
  --rollback-plan "Revert to current state without documentation" \
  --reference PROJECT.md
```

**Outputs**:
- Creates proposal in `artifacts/proposals/` directory
- Updates audit log in `artifacts/metrics/H011-audit-log.json`
- Generates event log entry

### safety_guardian.py

**Purpose**: Implement configurable safety rails and autonomous coding feedback loop.

**Usage**:
```bash
python tools/self_improvement/safety_guardian.py <command> [options]
```

**Commands**:
- `enhanced-validation`: Validate operations against safety thresholds
- `record-operation`: Record autonomous operation outcome
- `analyze-feedback`: Analyze feedback patterns and adapt thresholds
- `report`: Generate markdown report of safety status

**Example - Enhanced Validation**:
```bash
python tools/self_improvement/safety_guardian.py enhanced-validation \
  --operation-file artifacts/operations/test-operation.json \
  --audit-log artifacts/metrics/H011-audit-log.json
```

### autonomous_feedback_manager.py

**Purpose**: Implement autonomous development feedback loop with pattern monitoring.

**Usage**:
```bash
python tools/self_improvement/autonomous_feedback_manager.py <command> [options]
```

**Commands**:
- `analyze`: Analyze code patterns and identify issues
- `adapt`: Apply adaptive coding strategies
- `predict`: Predict potential issues based on patterns
- `report`: Generate comprehensive feedback report

**Example - Analyze Code Patterns**:
```bash
python tools/self_improvement/autonomous_feedback_manager.py analyze \
  --operation-file artifacts/operations/development-operation.json
```

### brave_trend_pulse.py

**Purpose**: Generate trend analysis from Brave Search for context-aware development.

**Usage**:
```bash
python tools/self_improvement/brave_trend_pulse.py --query <search_term> [options]
```

**Example - Generate Trends**:
```bash
python tools/self_improvement/brave_trend_pulse.py \
  --query "AI autonomous development tools" \
  --max-results 5 \
  --country US
```

**Outputs**:
- Creates trend analysis in `artifacts/verification/H013-brave-trends.md`
- Updates planning context in `artifacts/metrics/H013-planning-context.json`

## GUI and Launcher Tools

### package_gui.py

**Purpose**: Package the GUI launcher for distribution and easy deployment.

**Usage**:
```bash
python tools/gui_launcher/package_gui.py [options]
```

**Options**:
- `--source`: Source directory of cortex-gov-gui skill
- `--target`: Target directory for packaged GUI

**Example**:
```bash
python tools/gui_launcher/package_gui.py \
  --source skills/cortex-gov-gui \
  --target ./packaged_gui
```

### cortex_gov_gui.py

**Purpose**: Launch a local GUI to manage Cortex-GOV projects.

**Usage**:
```bash
python scripts/openclaw_projects_gui.py [options]
```

**Features**:
- Scan workspace for PROJECT.md folders
- List available projects and their agents
- Spawn agents with configurable model/heartbeat settings
- Edit model and heartbeat configurations
- Project dashboard view

## Analysis Tools

### optimization_analyzer.py

**Purpose**: Analyze recursive governance efficiency and identify bottlenecks.

**Usage**:
```bash
python tools/efficiency_analysis/optimization_analyzer.py <command> [options]
```

**Commands**:
- `--analyze`: Perform comprehensive efficiency analysis
- `--map-bottlenecks`: Identify system bottlenecks
- `--strategies`: Generate optimization strategies
- `--dashboard`: Create visualization dashboard

**Example - Map Bottlenecks**:
```bash
python tools/efficiency_analysis/optimization_analyzer.py \
  --map-bottlenecks \
  --metrics-log artifacts/metrics/H008-metrics-log.json \
  --bottleneck-output artifacts/analysis/bottlenecks.json
```

### backlog_analyzer.py

**Purpose**: Analyze TODO backlog items and identify stale or problematic tasks.

**Usage**:
```bash
python tools/analysis/backlog_analyzer.py [options]
```

**Options**:
- `--directory`: Directory to analyze (default: current directory)
- `--max-age`: Maximum age in days (default: 30)
- `--report`: Generate comprehensive report
- `--output`: Output file for results

### todo_cleaner.py

**Purpose**: Clean up stale TODO items and maintain healthy backlog.

**Usage**:
```bash
python tools/cleanup/todo_cleaner.py [options]
```

**Options**:
- `--directory`: Target directory (default: current)
- `--max-age`: Maximum age in days for "stale" classification
- `--dry-run`: Show what would be cleaned without actually doing it
- `--verbose`: Detailed output

## Performance and Monitoring Tools

### monitor.py

**Purpose**: Monitor health of the Cortex-GOV metrics pipeline and alert on anomalies.

**Usage**:
```bash
python tools/metrics_health/monitor.py <command> [options]
```

**Commands**:
- `check-health`: Perform comprehensive health checks
- `analyze-logs`: Analyze metrics log patterns
- `generate-dashboard`: Create visualization dashboard
- `simulate-failure`: Test failure recovery mechanisms

**Example - Check Health**:
```bash
python tools/metrics_health/monitor.py check-health \
  --metrics-log artifacts/metrics/H008-metrics-log.json \
  --config artifacts/config/monitor-config.json
```

### autotune.py

**Purpose**: Autotune system parameters for optimal performance.

**Usage**:
```bash
python tools/performance_tuning/autotune.py [options]
```

## System Integration Tools

### integration_checker.py

**Purpose**: Check system integration points and identify communication gaps.

**Usage**:
```bash
python tools/system/integration_checker.py [options]
```

**Commands**:
- `--scan`: Scan system for integration issues
- `--test`: Test cross-tool communication
- `--output`: Write results to file

### data_bus.py

**Purpose**: Cross-tool communication and data sharing via a JSON-backed event/data bus.

**Usage**:
```bash
python tools/system/data_bus.py
```

**Common Operations**:
- `publish_event(name, payload, source)`: Emit a shared event
- `get_events(name=None, limit=50)`: Fetch recent events
- `set_data(key, value, source)`: Store shared data for other tools
- `get_data(key)`: Read shared data entry

### error_handler.py

**Purpose**: Centralized error handling and recovery strategies for system tools.

**Usage**:
```bash
python tools/system/error_handler.py
```

**Capabilities**:
- Detect error types and categorize severity
- Attempt recoveries (file, config, dependency, process, timeout)
- Export recovery statistics and logs

### system_monitor.py

**Purpose**: System-wide monitoring and alerting infrastructure.

**Usage**:
```bash
python tools/monitoring/system_monitor.py [options]
```

**Commands**:
- `--validate`: Validate monitoring configuration
- `--run`: Start continuous monitoring
- `--config`: Path to monitoring configuration file

## Tool Dependencies

### External Dependencies
- `argparse`: Command-line argument parsing
- `json`: JSON data handling
- `pathlib`: Path manipulation
- `datetime`: Timestamp handling
- `hashlib`: Data integrity verification
- `sqlite3`: Database operations
- `requests`: HTTP requests
- `brave-search`: Trend analysis

### Internal Dependencies
- `cortex-gov/artifacts/config/`: Configuration files
- `cortex-gov/artifacts/metrics/`: Metrics and logs
- `cortex-gov/artifacts/proposals/`: Proposal storage
- `cortex-gov/artifacts/verification/`: Verification artifacts

## Configuration Files

### monitor-config.json
```json
{
  "collection_interval": 5,
  "export_interval": 60,
  "enabled_metrics": [
    "cpu_usage",
    "memory_usage",
    "disk_usage",
    "disk_io",
    "network_io",
    "process_count",
    "thread_count"
  ]
}
```

### H027-safety-rails.json
```json
{
  "autonomy_threshold": 0.75,
  "risk_threshold": 0.6,
  "confidence_threshold": 0.8,
  "adaptive_updates": true
}
```

### H028-feedback-config.json
```json
{
  "pattern_recognition": {
    "nesting_depth_threshold": 10,
    "cyclomatic_complexity_threshold": 30
  },
  "monitoring": {
    "response_time_threshold_ms": 1000,
    "memory_usage_threshold_mb": 200
  }
}
```

## Error Handling and Recovery

### Common Error Patterns

1. **File Not Found Errors**
   - Check file paths in configuration
   - Verify artifact directories exist
   - Use absolute paths when possible

2. **JSON Parse Errors**
   - Validate JSON syntax before processing
   - Handle malformed files gracefully
   - Provide backup data sources

3. **Network/HTTP Errors**
   - Implement retry logic
   - Provide offline fallback modes
   - Validate connectivity before operations

### Recovery Strategies

1. **Automatic Recovery**
   - System health checks detect issues
   - Recovery procedures initiated automatically
   - Audit logs document recovery actions

2. **Manual Recovery**
   - Detailed error messages guide users
   - Backup mechanisms preserve data
   - Rollback procedures for critical operations

## Testing and Validation

### Unit Tests
- Individual tool functionality
- Error handling and edge cases
- Configuration validation

### Integration Tests
- Cross-tool communication
- Data flow between components
- System-wide consistency

### Performance Tests
- Response time benchmarks
- Memory usage monitoring
- Throughput measurements

## Best Practices

### Tool Development
1. **Consistent CLI Interface**
   - Standard argument naming conventions
   - Clear help text
   - Proper error handling

2. **Data Management**
   - Structured logging
   - Versioned artifact storage
   - Data integrity verification

3. **Security Considerations**
   - Input validation
   - Secure file handling
   - Audit logging

### Usage Guidelines
1. **Regular Monitoring**
   - Run health checks periodically
   - Review logs and metrics
   - Update configurations as needed

2. **Documentation Updates**
   - Keep documentation current
   - Record configuration changes
   - Document tool updates and changes

3. **Performance Optimization**
   - Monitor system performance
   - Tune configurations based on usage patterns
   - Scale resources as needed

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```
   Solution: Add cortex-gov/tools to Python path
   ```
   
2. **Permission Denied Errors**
   ```
   Solution: Check file permissions and access rights
   ```

3. **Configuration File Not Found**
   ```
   Solution: Verify config file paths and create defaults
   ```

### Debug Mode

Most tools support debug mode for troubleshooting:
```bash
python <tool>.py --debug --verbose
```

This provides detailed logging and debugging information.