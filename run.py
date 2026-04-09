"""
Launcher script for Virtual Environment Manager
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from venv_manager.main import main

if __name__ == "__main__":
    main()
