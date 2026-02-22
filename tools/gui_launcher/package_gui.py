#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Package the GUI launcher for easy deployment and use with new projects.
Creates a standalone launcher script that can be distributed to new project owners.
"""

import os
import shutil
import json
import argparse
from pathlib import Path
from typing import Dict, Any

def copy_gui_files(target_dir: Path, source_dir: Path) -> None:
    """Copy necessary GUI files to the target directory."""
    # Create the target directory if it doesn't exist
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy the GUI script
    gui_script = source_dir / "scripts" / "openclaw_projects_gui.py"
    if gui_script.exists():
        shutil.copy2(gui_script, target_dir / "cortex_gov_gui.py")
        print(f"Copied GUI script to {target_dir / 'cortex_gov_gui.py'}")
    else:
        raise FileNotFoundError(f"GUI script not found at {gui_script}")
    
    # Copy supporting files if they exist
    assets_dir = source_dir / "assets"
    if assets_dir.exists():
        shutil.copytree(assets_dir, target_dir / "assets", dirs_exist_ok=True)
        print(f"Copied assets to {target_dir / 'assets'}")

def create_launcher_script(target_dir: Path, gui_name: str = "cortex_gov_gui.py") -> None:
    """Create a launcher script that can create projects and run the GUI."""
    launcher_content = f"""#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Find the script directory
script_dir = Path(__file__).parent
gui_script = script_dir / "{gui_name}"

if not gui_script.exists():
    print(f"Error: GUI script not found at {{gui_script}}")
    print("Make sure the GUI launcher files are in the correct location.")
    sys.exit(1)

# Add the script directory to Python path so we can import it
sys.path.insert(0, str(script_dir))

PROJECT_TEMPLATE = '''# {{name}}

## Summary
Describe the project here.

## Constraints
- List any constraints here

## Rules
- Tasks must move: TODO -> IN_PROGRESS -> VERIFY -> DONE (or BLOCKED)
- Only one task may be IN_PROGRESS at a time

## Tasks (Ordered)

### T001: First task placeholder
Epic: E000
Status: TODO
Priority: P1
Owner: agent

Work:
- [ ] Define the first task

Acceptance Criteria:
- [ ] Placeholder criteria

Verification Steps:
- [ ] Placeholder verification

Evidence Requirements:
- File paths:
- Commands/output:
- Notes:
'''


def create_project(project_root: Path, name: str) -> Path:
    project_root.mkdir(parents=True, exist_ok=True)
    project_md = project_root / "PROJECT.md"
    if project_md.exists():
        print(f"PROJECT.md already exists at {{project_md}}")
    else:
        project_md.write_text(PROJECT_TEMPLATE.format(name=name), encoding="utf-8")
        print(f"Created PROJECT.md at {{project_md}}")
    return project_root


def main():
    parser = argparse.ArgumentParser(description="Cortex-GOV GUI Launcher")
    parser.add_argument("--new-project", type=str, help="Create a new project folder with PROJECT.md")
    parser.add_argument("--project-root", type=str, default=".", help="Root directory for the project")
    parser.add_argument("--no-gui", action="store_true", help="Only create the project, do not launch the GUI")
    args = parser.parse_args()

    project_root = Path(args.project_root).resolve()
    if args.new_project:
        project_root = project_root / args.new_project
        create_project(project_root, args.new_project)

    if args.no_gui:
        print("Skipping GUI launch (--no-gui).")
        return

    from cortex_gov_gui import main as gui_main
    gui_main()


if __name__ == "__main__":
    main()
"""

    launcher_path = target_dir / "launcher.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)

    # Make it executable
    launcher_path.chmod(0o755)
    print(f"Created launcher script at {launcher_path}")

def create_onboarding_checklist(target_dir: Path) -> None:
    """Create an onboarding checklist for project owners."""
    checklist_content = """# Cortex-GOV GUI Onboarding Checklist

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
"""
    
    checklist_path = target_dir / "ONBOARDING_CHECKLIST.md"
    with open(checklist_path, 'w', encoding='utf-8') as f:
        f.write(checklist_content)
    print(f"Created onboarding checklist at {checklist_path}")

def create_installation_guide(target_dir: Path) -> None:
    """Create installation documentation."""
    guide_content = """# Cortex-GOV GUI Installation Guide

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
"""
    
    guide_path = target_dir / "INSTALLATION_GUIDE.md"
    with open(guide_path, 'w', encoding='utf-8') as f:
        f.write(guide_content)
    print(f"Created installation guide at {guide_path}")

def main():
    parser = argparse.ArgumentParser(description="Package the GUI launcher for deployment")
    parser.add_argument("--source", type=str, default="C:/Users/metalbud/clawd/skills/cortex-gov-gui",
                       help="Source directory of the cortex-gov-gui skill")
    parser.add_argument("--target", type=str, default="gui_launcher_package",
                       help="Target directory for the packaged GUI")
    
    args = parser.parse_args()
    
    source_dir = Path(args.source)
    target_dir = Path(args.target)
    
    print(f"Packaging GUI from {source_dir} to {target_dir}")
    
    # Verify source directory exists
    if not source_dir.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    # Copy GUI files
    copy_gui_files(target_dir, source_dir)
    
    # Create launcher script
    create_launcher_script(target_dir)
    
    # Create onboarding checklist
    create_onboarding_checklist(target_dir)
    
    # Create installation guide
    create_installation_guide(target_dir)
    
    print("\nGUI packaging complete!")
    print(f"Package created at: {target_dir.absolute()}")
    print("\nTo use the package:")
    print("1. Copy the contents to your project directory")
    print("2. Run 'python launcher.py' to start the GUI")

if __name__ == "__main__":
    main()