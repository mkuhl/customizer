"""Entry point for template customizer when run as a module or with PyInstaller."""

import sys

from template_customizer.cli import main

if __name__ == "__main__":
    sys.exit(main())
