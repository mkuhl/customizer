"""External replacements configuration and management."""

from pathlib import Path
from typing import Any, Dict, List, Optional


class ExternalReplacementError(Exception):
    """Base exception for external replacement errors."""
    pass


class ExternalReplacementConfig:
    """Manages external replacement configuration from config files."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize with configuration dictionary.

        Args:
            config: Configuration dictionary with optional 'replacements' section
        """
        self.config = config
        self.replacements = config.get("replacements", {})

    def has_replacements(self) -> bool:
        """Check if any external replacements are defined.

        Returns:
            True if replacements section exists and has content
        """
        return bool(self.replacements)

    def get_json_replacements(self) -> Dict[str, Dict[str, str]]:
        """Get JSON file replacement rules.

        Returns:
            Dictionary mapping file paths to their JSONPath replacements
        """
        return self.replacements.get("json", {})

    def get_markdown_replacements(self) -> Dict[str, Dict[str, str]]:
        """Get Markdown file replacement rules.

        Returns:
            Dictionary mapping file paths to their pattern replacements
        """
        return self.replacements.get("markdown", {})

    def get_files_to_process(self) -> List[Path]:
        """Get list of all files that have replacement rules.

        Returns:
            List of Path objects for files with replacements
        """
        files = []

        # Add JSON files
        for file_path in self.get_json_replacements().keys():
            files.append(Path(file_path))

        # Add Markdown files
        for file_path in self.get_markdown_replacements().keys():
            files.append(Path(file_path))

        return files

    def get_file_type(self, file_path: Path) -> Optional[str]:
        """Determine the replacement type for a given file.

        Args:
            file_path: Path to check

        Returns:
            'json', 'markdown', or None if no replacements defined
        """
        file_str = str(file_path)

        if file_str in self.get_json_replacements():
            return "json"
        elif file_str in self.get_markdown_replacements():
            return "markdown"

        return None

    def get_replacements_for_file(self, file_path: Path) -> Optional[Dict[str, str]]:
        """Get replacement rules for a specific file.

        Args:
            file_path: Path to get replacements for

        Returns:
            Dictionary of replacement rules or None if no rules defined
        """
        file_str = str(file_path)

        json_rules = self.get_json_replacements()
        if file_str in json_rules:
            return json_rules[file_str]

        md_rules = self.get_markdown_replacements()
        if file_str in md_rules:
            return md_rules[file_str]

        return None
