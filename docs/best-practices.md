# Best Practices

## Project Governance

- Keep `PROJECT.md` as the single source of truth.
- Update task status immediately after tangible progress.
- Always attach evidence in `Verification Evidence` before moving to `DONE`.

## Error Handling

- Use `tools/system/error_handler.py` to standardize recovery patterns.
- Record fatal errors and recovery attempts in `artifacts/logs`.
- Prefer safe defaults when recovering from config or dependency issues.

## Cross-Tool Communication

- Use `tools/system/data_bus.py` to share tool state across modules.
- Publish events for major operations (integration scans, validations, deployments).
- Store shared data keys for last-known-good runs.

## Monitoring

- Keep alert thresholds realistic for your environment.
- Export metrics periodically and archive old metrics.
- Review `alerts.log` weekly for recurring performance issues.

## Testing

- Keep unit tests in `tests/` and run them before major changes.
- Add regression tests for tools that affect safety or governance rules.

## Documentation

- Document every new tool in `docs/api-documentation.md`.
- Update `docs/system-architecture.md` when integration points change.
- Add release notes to `README.md` for major workflow changes.
