#!/usr/bin/env python3
"""
Version extraction script for GitHub Actions and CI/CD.

This script extracts the version from the template_customizer package
for use in automated workflows, Docker builds, and releases.
"""

import sys
from pathlib import Path

# Add src directory to path to import template_customizer
repo_root = Path(__file__).parent.parent
src_path = repo_root / "src"
sys.path.insert(0, str(src_path))

try:
    from template_customizer import __version__

    def get_version():
        """Get the current version string."""
        return __version__

    def get_version_info():
        """Get detailed version information."""
        return {
            "version": __version__,
            "major": int(__version__.split('.')[0]),
            "minor": int(__version__.split('.')[1]),
            "patch": int(__version__.split('.')[2]),
            "is_release": not any(
                char in __version__ for char in ["a", "b", "rc", "dev"]
            ),
        }

    def get_docker_tags():
        """Get appropriate Docker tags for this version."""
        version = get_version()
        info = get_version_info()

        tags = [version]  # Always include exact version

        if info["is_release"]:
            # For releases, also tag as latest
            tags.append("latest")

            # Add major.minor tag for stable releases
            tags.append(f"{info['major']}.{info['minor']}")

            # Add major tag for major releases (if not 0.x.x)
            if info["major"] > 0:
                tags.append(str(info["major"]))
        else:
            # For pre-releases, tag as dev
            tags.append("dev")

        return tags

    def main():
        """Main CLI interface for the script."""
        if len(sys.argv) < 2:
            print("Usage: python get-version.py [version|tags|info]")
            sys.exit(1)

        command = sys.argv[1].lower()

        if command == "version":
            print(get_version())
        elif command == "tags":
            tags = get_docker_tags()
            print(" ".join(tags))
        elif command == "info":
            info = get_version_info()
            for key, value in info.items():
                print(f"{key}={value}")
        else:
            print(f"Unknown command: {command}")
            print("Available commands: version, tags, info")
            sys.exit(1)

except ImportError as e:
    print(f"Error importing template_customizer: {e}", file=sys.stderr)
    print("Make sure you're running this from the repository root.", file=sys.stderr)
    sys.exit(1)

if __name__ == "__main__":
    main()
