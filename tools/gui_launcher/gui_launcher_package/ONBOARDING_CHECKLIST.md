# Cortex-GOV GUI Onboarding Checklist

This checklist will help you get started with the Cortex-GOV GUI for managing your project.

## Prerequisites

- [ ] Install Python 3.7 or higher
- [ ] Install OpenClaw CLI and ensure it's in your PATH
- [ ] Have a project with PROJECT.md file

## Setup

1. [ ] Place the launcher files in your project directory:
   - Copy `launcher.py` to your project root
   - Copy `cortex_gov_gui.py` to your project root
   - Copy `assets/` directory to your project root (if it exists)

2. [ ] Make the launcher executable:
   - On macOS/Linux: `chmod +x launcher.py`
   - On Windows: The script should run directly with Python

## First Launch

3. [ ] Launch the GUI:
   ```bash
   python launcher.py
   ```
   Or on macOS/Linux (if made executable):
   ```bash
   ./launcher.py
   ```

4. [ ] Verify the GUI opens in your web browser

## Using the GUI

5. [ ] **Project Selection**:
   - Select your project from the sidebar
   - Verify your project details appear correctly

6. [ ] **Agent Management**:
   - View existing agents for your project
   - Add new agents using the "Add Agent" button
   - Configure agent settings (model, heartbeat, etc.)

7. [ ] **PROJECT.md Editing**:
   - View your PROJECT.md in the conversational interface
   - Make edits and save changes
   - Verify the changes are reflected in your PROJECT.md file

## Advanced Features

8. [ ] **Trend Analysis**:
   - Use the integrated Brave Search for trend analysis
   - Review trends for your project domain

9. [ ] **Monitoring**:
   - Check system health metrics
   - Review proposal history and status

## Troubleshooting

### Common Issues

- **GUI doesn't open**: Check if OpenClaw CLI is installed and in PATH
- **Project not found**: Ensure PROJECT.md exists in your project directory
- **Agent creation fails**: Verify workspace paths and permissions

### Getting Help

- Check the OpenClaw documentation
- Review the Cortex-GOV artifacts for examples
- Contact the OpenClaw community for support

## Next Steps

Once comfortable with the GUI:
- Customize agent templates for your specific needs
- Set up regular monitoring schedules
- Integrate with your development workflow

---
*Created for Cortex-GOV project operationalization*
