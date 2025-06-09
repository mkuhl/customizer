"""Version bumping utilities for development workflow."""

import re
from pathlib import Path
from typing import Optional

from .version import VersionManager, VersionParser


class VersionBumper:
    """Utility for bumping version numbers in source files."""
    
    def __init__(self, project_root: Path):
        """Initialize version bumper.
        
        Args:
            project_root: Path to project root directory
        """
        self.project_root = Path(project_root)
        self.init_file = self.project_root / "src" / "template_customizer" / "__init__.py"
        self.pyproject_file = self.project_root / "pyproject.toml"
    
    def get_current_version(self) -> str:
        """Get current version from __init__.py file.
        
        Returns:
            Current version string
            
        Raises:
            FileNotFoundError: If __init__.py file not found
            ValueError: If version not found in file
        """
        if not self.init_file.exists():
            raise FileNotFoundError(f"__init__.py not found at {self.init_file}")
        
        content = self.init_file.read_text(encoding="utf-8")
        
        # Look for __version__ = "x.y.z" pattern
        version_pattern = r'__version__\s*=\s*["\']([^"\']+)["\']'
        match = re.search(version_pattern, content)
        
        if not match:
            raise ValueError("Version not found in __init__.py")
        
        return match.group(1)
    
    def bump_version(self, bump_type: str, dry_run: bool = False) -> str:
        """Bump version in project files.
        
        Args:
            bump_type: Type of bump ('major', 'minor', 'patch')
            dry_run: If True, don't actually write files
            
        Returns:
            New version string
            
        Raises:
            ValueError: If bump_type is invalid or current version is invalid
            FileNotFoundError: If required files not found
        """
        current_version = self.get_current_version()
        new_version = VersionManager.get_next_version(current_version, bump_type)
        
        if not dry_run:
            self._update_init_file(new_version)
            self._update_pyproject_file(new_version)
        
        return new_version
    
    def _update_init_file(self, new_version: str) -> None:
        """Update version in __init__.py file.
        
        Args:
            new_version: New version string
        """
        content = self.init_file.read_text(encoding="utf-8")
        
        # Replace __version__ = "old_version" with __version__ = "new_version"
        version_pattern = r'(__version__\s*=\s*["\'])([^"\']+)(["\'])'
        updated_content = re.sub(
            version_pattern,
            f"\\g<1>{new_version}\\g<3>",
            content
        )
        
        self.init_file.write_text(updated_content, encoding="utf-8")
    
    def _update_pyproject_file(self, new_version: str) -> None:
        """Update version in pyproject.toml file if it contains static version.
        
        Args:
            new_version: New version string
        """
        if not self.pyproject_file.exists():
            return
        
        content = self.pyproject_file.read_text(encoding="utf-8")
        
        # Only update if there's a static version (not dynamic)
        version_pattern = r'(version\s*=\s*["\'])([^"\']+)(["\'])'
        if re.search(version_pattern, content):
            updated_content = re.sub(
                version_pattern,
                f"\\g<1>{new_version}\\g<3>",
                content
            )
            self.pyproject_file.write_text(updated_content, encoding="utf-8")


class VersionCompatibilityChecker:
    """Utility for checking version compatibility."""
    
    @staticmethod
    def check_config_compatibility(
        config_path: Path,
        tool_version: str
    ) -> tuple[bool, Optional[str]]:
        """Check if configuration file is compatible with tool version.
        
        Args:
            config_path: Path to configuration file
            tool_version: Current tool version string
            
        Returns:
            Tuple of (is_compatible, warning_message)
        """
        try:
            # For now, we'll implement basic compatibility checking
            # This can be extended based on specific requirements
            
            # Parse the tool version
            tool_version_obj = VersionParser.parse(tool_version)
            
            # Read config file to look for version info
            config_content = config_path.read_text(encoding="utf-8")
            
            # Look for version information in config
            version_patterns = [
                r'customizer[_-]?version\s*:\s*["\']?([^"\'\\s]+)["\']?',
                r'tool[_-]?version\s*:\s*["\']?([^"\'\\s]+)["\']?',
                r'version\s*:\s*["\']?([^"\'\\s]+)["\']?',
            ]
            
            config_version = None
            for pattern in version_patterns:
                match = re.search(pattern, config_content, re.IGNORECASE)
                if match:
                    try:
                        config_version = VersionParser.parse(match.group(1))
                        break
                    except ValueError:
                        continue
            
            if config_version is None:
                # No version specified in config - assume compatible
                return True, None
            
            # Check compatibility
            if not tool_version_obj.is_compatible_with(config_version):
                warning = (
                    f"Configuration was created for version {config_version} "
                    f"but you're using version {tool_version}. "
                    f"There may be compatibility issues."
                )
                return False, warning
            
            return True, None
            
        except Exception:
            # If we can't check compatibility, assume it's fine
            return True, None


def get_version_changelog_entry(version: str, changes: list[str]) -> str:
    """Generate a changelog entry for a version.
    
    Args:
        version: Version string
        changes: List of changes/features
        
    Returns:
        Formatted changelog entry
    """
    from datetime import datetime
    
    header = f"## [{version}] - {datetime.now().strftime('%Y-%m-%d')}"
    
    if not changes:
        body = "- No changes recorded"
    else:
        body = "\n".join(f"- {change}" for change in changes)
    
    return f"{header}\n\n{body}\n"