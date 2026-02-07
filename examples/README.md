# Project Examples

This directory contains **generic** example configurations for the wizard. They are intentionally not tied to any real/private project.

All example configs are compatible with:

```bash
python tools/wizard/cortex_gov_wizard.py --non-interactive --config <file>
```

## Available Examples

### 1) Content Site (`content-site-config.json`)
A marketing/content site with an SEO baseline and a simple publishing workflow.

### 2) Recipe Community App (`recipe-community-config.json`)
A generic community app with profiles, content creation, moderation, and planning features.

### 3) General Web App (`general-webapp-config.json`)
A generic full-stack web app: auth, database, API, UI components, and forms.

## Usage

From the repo root:

```bash
python tools/wizard/cortex_gov_wizard.py --non-interactive --config examples/content-site-config.json --out PROJECT.md --heartbeat-out HEARTBEAT.md
```

## Create your own config

- Copy one of the JSON files in this folder
- Edit `project_name`, `summary`, `constraints`, `epics`, and `tasks`
- Run the wizard in non-interactive mode to generate a control doc and heartbeat file

