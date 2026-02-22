# Developer Guide for Cortex GOV Examples

This guide explains how to use the example project configurations provided in this directory.

## Overview

The example configurations demonstrate different types of projects you can create using the Cortex GOV wizard. Each example is self-contained and can be used as a starting point for your own projects.

## Examples Included

### 1. Content Site (`content-site-config.json`)
A marketing/content-focused site with:
- Static-first approach
- SEO optimization
- Publishing workflow
- Performance-focused constraints

**Best for:** Blogs, documentation sites, marketing landing pages

### 2. Recipe Community App (`recipe-community-config.json`)
A community-driven application featuring:
- User accounts and profiles
- Content creation and moderation
- Discovery and categorization
- Social features

**Best for:** Community platforms, user-generated content sites

### 3. General Web App (`general-webapp-config.json`)
A full-stack web application with:
- Authentication system
- Database integration
- API endpoints
- UI components

**Best for:** Traditional web applications with backend services

## Using the Examples

### Quick Start

To generate a project from any example configuration:

```bash
# From the cortex-gov directory
python tools/wizard/cortex_gov_wizard.py \
  --config examples/<example-name>-config.json \
  --non-interactive \
  --out PROJECT.md \
  --heartbeat-out HEARTBEAT.md
```

### Interactive Mode

For a more guided experience, you can use the wizard in interactive mode with an empty configuration:

```bash
python tools/wizard/cortex_gov_wizard.py
```

## Creating Your Own Configuration

### Basic Structure

All configurations follow this JSON structure:

```json
{
  "project_name": "Your Project Name",
  "project_slug": "your-project-slug",
  "summary": "Brief description of your project",
  "constraints": [
    "Constraint 1",
    "Constraint 2"
  ],
  "epics": [
    {
      "key": "E001",
      "title": "Epic Title",
      "outcome": [
        "Outcome description 1",
        "Outcome description 2"
      ]
    }
  ],
  "tasks": [
    {
      "key": "H001",
      "title": "Task Title",
      "epic": "E001",
      "status": "TODO",
      "priority": "P0",
      "owner": "agent",
      "work": [
        "Work item 1",
        "Work item 2"
      ],
      "acceptance": [
        "Acceptance criteria 1",
        "Acceptance criteria 2"
      ],
      "verification_steps": [
        "Verification step 1",
        "Verification step 2"
      ],
      "evidence_fields": [
        "Evidence field type 1",
        "Evidence field type 2"
      ]
    }
  ]
}
```

### Task Keys and Status

- **Task Keys**: Use `H` followed by a number (e.g., `H001`, `H002`)
- **Status**: One of `TODO`, `IN_PROGRESS`, `VERIFY`, `DONE`, `BLOCKED`
- **Priority**: `P0` (highest), `P1`, `P2` (lowest)
- **Owner**: Usually `agent` for automated execution

### Evidence Fields

Common evidence field types:
- `URLs`: Links to documentation, demos, or live sites
- `File paths`: Locations of generated files or code
- `Commands/output`: Command-line commands and their results
- `Screenshots`: Visual verification of UI elements
- `Notes`: Additional context or explanations

## Validation

The wizard automatically validates configurations before generating PROJECT.md files:

- ✅ JSON syntax validation
- ✅ Required field presence
- ✅ Epic/task relationships
- ✅ Task status values
- ✅ Evidence field types

## Integration with OpenClaw

Each generated PROJECT.md includes:
- Complete task management workflow
- Heartbeat-compatible instructions
- Evidence collection framework
- Task selection rules for agents

The corresponding HEARTBEAT.md file directs OpenClaw agents to follow the project rules and work on tasks.

## Testing Your Configuration

To test a configuration before using it:

```bash
# Generate test files
python tools/wizard/cortex_gov_wizard.py \
  --config examples/your-config.json \
  --non-interactive \
  --out TEST_PROJECT.md \
  --heartbeat-out TEST_HEARTBEAT.md

# Review the generated files
cat TEST_PROJECT.md
cat TEST_HEARTBEAT.md
```

## Best Practices

1. **Start with an example** - Use one of the provided configurations as a template
2. **Keep epics focused** - Each epic should represent a major feature area
3. **Break down work** - Tasks should be small enough to complete in a single session
4. **Include verification** - Always define how to verify task completion
5. **Document evidence** - Specify what proof is required for each task

## Troubleshooting

### Common Issues

**JSON Syntax Errors**
- Use a JSON validator to check syntax
- Ensure proper comma usage
- Validate quotes around string values

**Missing Required Fields**
- All top-level fields are required
- Epics and tasks arrays cannot be empty
- Each task must have all required fields

**Task Relationship Errors**
- Epic keys must exist in the epics array
- Task references to non-existent epics will fail
- Ensure consistent numbering in task keys

### Getting Help

- Check the main [README.md](README.md) for general documentation
- Review the wizard [README](tools/wizard/README.md) for usage details
- Examine existing examples for reference implementations