#!/usr/bin/env python3
import os
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

# Launch the GUI
if __name__ == "__main__":
    from cortex_gov_gui import main
    main()
