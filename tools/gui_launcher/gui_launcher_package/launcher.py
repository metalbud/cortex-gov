#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path

# Find the script directory
script_dir = Path(__file__).parent
gui_script = script_dir / "cortex_gov_gui.py"

if not gui_script.exists():
    print(f"Error: GUI script not found at {gui_script}")
    print("Make sure the GUI launcher files are in the correct location.")
    sys.exit(1)

# Add the script directory to Python path so we can import it
sys.path.insert(0, str(script_dir))

PROJECT_TEMPLATE = '''# {name}

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
        print(f"PROJECT.md already exists at {project_md}")
    else:
        project_md.write_text(PROJECT_TEMPLATE.format(name=name), encoding="utf-8")
        print(f"Created PROJECT.md at {project_md}")
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
