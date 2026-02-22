# Deployment Guide

This guide describes how to deploy Cortex GOV in local, VM, or production environments.

## Requirements

- Python 3.9+
- Git
- Windows, macOS, or Linux

## Quick Start (Local)

```bash
git clone <your-repo>
cd cortex-gov
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## Environment Setup

- Ensure `PROJECT.md` and `HEARTBEAT.md` are committed.
- Create the artifacts folder tree:

```bash
mkdir -p artifacts/logs artifacts/metrics artifacts/monitoring
```

## Monitoring Setup

1. Review the default monitoring config:
   - `artifacts/monitoring/monitor-config.json`
2. Validate it:

```bash
python tools/monitoring/system_monitor.py --validate --config artifacts/monitoring/monitor-config.json
```

3. Run the monitor (optional):

```bash
python tools/monitoring/system_monitor.py --run --config artifacts/monitoring/monitor-config.json
```

## Production Checklist

- [ ] Ensure `PROJECT.md` is up to date and tasks follow the lifecycle rules
- [ ] Validate monitoring config and alert thresholds
- [ ] Configure log rotation for `artifacts/logs`
- [ ] Run tests: `python -m pytest tests/ --verbose`
- [ ] Back up critical artifacts before major changes
- [ ] Confirm any external integrations have proper credentials stored securely

## Rollback

- Keep backups of `project_config.json` and `artifacts/` before large changes
- If a deployment fails, restore previous artifacts and re-run validation

## Notes

- Cortex GOV expects a document-driven flow; avoid running tools without updating `PROJECT.md`.
- Use the integration checker before major releases:

```bash
python tools/system/integration_checker.py --scan --output artifacts/system-analysis/integration-gaps.json
```
