#!/usr/bin/env python3
"""Generic release automation script for Template Customizer.

This script handles various release-related tasks that need to be automated
during the release process. It's designed to be extensible for future needs.
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Callable, Tuple


class ReleaseAutomation:
    """Generic release automation handler."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.tasks: Dict[str, Callable] = {
            'update-version-badge': self.update_version_badge,
            'update-changelog': self.update_changelog,
            'update-docker-tags': self.update_docker_tags,
        }
    
    def update_version_badge(self, version: str) -> Tuple[bool, str]:
        """Update the version badge in README.md.
        
        Args:
            version: New version string (e.g., "0.4.0")
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            return False, f"README.md not found at {readme_path}"
        
        # Read current content
        content = readme_path.read_text()
        
        # Pattern to match the version badge
        pattern = r'(\[!\[Version\]\(https://img\.shields\.io/badge/version-)[^-]+(-blue\.svg\)\])'
        
        # Check if pattern exists
        if not re.search(pattern, content):
            return False, "Version badge pattern not found in README.md"
        
        # Replace with new version
        new_content = re.sub(pattern, rf'\g<1>{version}\g<2>', content)
        
        # Check if anything changed
        if content == new_content:
            return True, f"Version badge already shows {version}"
        
        # Write updated content
        readme_path.write_text(new_content)
        return True, f"Updated version badge to {version}"
    
    def update_changelog(self, version: str) -> Tuple[bool, str]:
        """Update CHANGELOG.md with new version (placeholder for future implementation).
        
        Args:
            version: New version string
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Placeholder for future changelog automation
        return True, f"Changelog update for {version} (not implemented yet)"
    
    def update_docker_tags(self, version: str) -> Tuple[bool, str]:
        """Update Docker-related documentation with new version tags.
        
        Args:
            version: New version string
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        # Placeholder for future Docker tag automation
        return True, f"Docker tags update for {version} (not implemented yet)"
    
    def run_task(self, task_name: str, version: str) -> Tuple[bool, str]:
        """Run a specific release automation task.
        
        Args:
            task_name: Name of the task to run
            version: Version string to use
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if task_name not in self.tasks:
            available_tasks = ', '.join(self.tasks.keys())
            return False, f"Unknown task '{task_name}'. Available tasks: {available_tasks}"
        
        return self.tasks[task_name](version)
    
    def run_all_tasks(self, version: str) -> List[Tuple[str, bool, str]]:
        """Run all available release automation tasks.
        
        Args:
            version: Version string to use
            
        Returns:
            List of tuples (task_name, success, message)
        """
        results = []
        for task_name in self.tasks:
            success, message = self.run_task(task_name, version)
            results.append((task_name, success, message))
        return results
    
    def list_tasks(self) -> List[str]:
        """Get list of available tasks."""
        return list(self.tasks.keys())


def main():
    """Main function to handle command line arguments and execute tasks."""
    parser = argparse.ArgumentParser(
        description="Release automation script for Template Customizer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Update version badge only
  python release-automation.py update-version-badge 0.4.0
  
  # Run all release automation tasks
  python release-automation.py all 0.4.0
  
  # List available tasks
  python release-automation.py list
        """
    )
    
    parser.add_argument(
        'task', 
        help='Task to run or "all" to run all tasks or "list" to show available tasks'
    )
    parser.add_argument(
        'version', 
        nargs='?',
        help='Version string (e.g., 0.4.0 or v0.4.0)'
    )
    
    args = parser.parse_args()
    
    # Handle list command
    if args.task == 'list':
        script_dir = Path(__file__).parent
        project_root = script_dir.parent
        automation = ReleaseAutomation(project_root)
        
        print("Available release automation tasks:")
        for task in automation.list_tasks():
            print(f"  - {task}")
        return
    
    # Version is required for all other commands
    if not args.version:
        print("Error: Version argument is required")
        parser.print_help()
        sys.exit(1)
    
    version = args.version
    
    # Remove 'v' prefix if present
    if version.startswith('v'):
        version = version[1:]
    
    # Validate version format (basic check)
    if not re.match(r'^\d+\.\d+\.\d+', version):
        print(f"Error: Invalid version format '{version}'. Expected format: x.y.z")
        sys.exit(1)
    
    # Initialize automation
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    automation = ReleaseAutomation(project_root)
    
    # Handle different task modes
    if args.task == 'all':
        print(f"🚀 Running all release automation tasks for version {version}...")
        results = automation.run_all_tasks(version)
        
        all_success = True
        for task_name, success, message in results:
            status = "✅" if success else "❌"
            print(f"{status} {task_name}: {message}")
            if not success:
                all_success = False
        
        if all_success:
            print(f"🎉 All release automation tasks completed successfully for v{version}")
            sys.exit(0)
        else:
            print("❌ Some release automation tasks failed")
            sys.exit(1)
    else:
        # Run specific task
        print(f"🔧 Running task '{args.task}' for version {version}...")
        success, message = automation.run_task(args.task, version)
        
        status = "✅" if success else "❌"
        print(f"{status} {message}")
        
        if success:
            sys.exit(0)
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()