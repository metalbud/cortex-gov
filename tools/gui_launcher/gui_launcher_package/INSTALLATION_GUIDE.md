# Cortex-GOV GUI Installation Guide

This guide explains how to install and deploy the Cortex-GOV GUI for your project.

## Quick Start

1. **Download the package**:
   ```bash
   git clone <repository-url>
   cd cortex-gov
   ```

2. **Run the packaging script**:
   ```bash
   python tools/gui_launcher/package_gui.py
   ```

3. **Deploy to your project**:
   ```bash
   cp -r gui_launcher/ /path/to/your/project/
   cd /path/to/your/project/
   ```

4. **Launch the GUI**:
   ```bash
   python launcher.py
   ```

## Detailed Installation

### Prerequisites

- Python 3.7 or higher
- OpenClaw CLI installed and accessible in your PATH
- Git (for cloning the repository)

### Step-by-Step Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-org/cortex-gov.git
   cd cortex-gov
   ```

2. **Create the GUI Package**:
   ```bash
   python tools/gui_launcher/package_gui.py
   ```
   This will create a `gui_launcher/` directory with all necessary files.

3. **Copy to Your Project**:
   ```bash
   # Create the launcher directory in your project
   mkdir -p /path/to/your/project/.cortex-gov
   cp -r gui_launcher/* /path/to/your/project/.cortex-gov/
   ```

4. **Verify Installation**:
   ```bash
   cd /path/to/your/project
   python .cortex-gov/launcher.py
   ```

### Project Structure After Installation

Your project should have the following structure:

```
your-project/
├── PROJECT.md
├── HEARTBEAT.md (optional)
├── .cortex-gov/
│   ├── launcher.py
│   ├── cortex_gov_gui.py
│   ├── assets/
│   │   ├── index.html
│   │   ├── app.js
│   │   └── styles.css
│   └── ONBOARDING_CHECKLIST.md
└── ... (your other project files)
```

## Configuration

### Environment Variables

The GUI launcher respects the following environment variables:

- `OPENCLAW_PROFILE`: OpenClaw profile to use (optional)
- `OPENCLAW_DEV`: Enable development mode (set to "true" to enable)

### Customization

#### Adding Custom Templates

You can add custom agent templates by modifying the `templates.json` file in the assets directory.

#### Styling

The GUI can be styled by modifying the CSS files in the `assets/styles.css` file.

## Troubleshooting

### Common Issues

1. **OpenClaw CLI Not Found**
   - Ensure OpenClaw is installed and in your PATH
   - Try running `openclaw --version` to verify

2. **Permission Denied on Launch**
   - On Unix systems, make sure the script is executable
   - Run: `chmod +x .cortex-gov/launcher.py`

3. **GUI Doesn't Open in Browser**
   - Check your browser settings for pop-up blockers
   - Try manually navigating to the URL shown in the terminal

4. **Project Not Detected**
   - Ensure PROJECT.md exists in your project root
   - Verify the file has proper formatting

### Getting Help

- Check the [OpenClaw documentation](https://docs.openclaw.ai)
- Review the Cortex-GOV artifacts for examples
- Open an issue in the GitHub repository

## Maintenance

### Updating the GUI

To update to a newer version:

1. Pull the latest changes:
   ```bash
   cd cortex-gov
   git pull origin main
   ```

2. Repackage the GUI:
   ```bash
   python tools/gui_launcher/package_gui.py
   ```

3. Copy the updated files to your project:
   ```bash
   cp -r gui_launcher/* /path/to/your/project/.cortex-gov/
   ```

### Backup Important Files

Before updating, consider backing up:
- Your custom templates
- Modified CSS files
- Any other customizations

---
*Created for Cortex-GOV project operationalization*
