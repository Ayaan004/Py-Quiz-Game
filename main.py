"""Quiz Master Pro - Professional Quiz Game Application Entry Point."""
import sys
import os

# Ensure the root directory is on the python path
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.ui.main_window import MainWindow

def main():
    """Launches the Quiz Master Pro application."""
    app = MainWindow()
    app.mainloop()

if __name__ == "__main__":
    main()
