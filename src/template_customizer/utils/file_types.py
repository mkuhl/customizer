"""File type detection and comment syntax mapping."""

from pathlib import Path
from typing import Dict, List, Optional


class FileTypeDetector:
    """Detects file types and maps them to appropriate comment syntax."""

    # Mapping of file extensions to comment types
    EXTENSION_MAP = {
        # Python
        ".py": "hash",
        ".pyi": "hash",
        # Shell/Bash
        ".sh": "hash",
        ".bash": "hash",
        ".zsh": "hash",
        # YAML/Config
        ".yml": "hash",
        ".yaml": "hash",
        ".toml": "hash",
        ".cfg": "hash",
        ".conf": "hash",
        ".ini": "hash",
        # JavaScript/TypeScript
        ".js": "double_slash",
        ".jsx": "double_slash",
        ".ts": "double_slash",
        ".tsx": "double_slash",
        ".mjs": "double_slash",
        ".vue": "double_slash",
        # Java/C/C++
        ".java": "double_slash",
        ".c": "double_slash",
        ".cpp": "double_slash",
        ".cc": "double_slash",
        ".cxx": "double_slash",
        ".h": "double_slash",
        ".hpp": "double_slash",
        ".cs": "double_slash",
        # Go/Rust/Swift
        ".go": "double_slash",
        ".rs": "double_slash",
        ".swift": "double_slash",
        # Kotlin/Scala
        ".kt": "double_slash",
        ".kts": "double_slash",
        ".scala": "double_slash",
        # Dart/Flutter
        ".dart": "double_slash",
        # PHP (supports both styles, using // for consistency)
        ".php": "double_slash",
        # CSS/SCSS/LESS
        ".css": "css",
        ".scss": "css",
        ".sass": "css",
        ".less": "css",
        # HTML/XML
        ".html": "html",
        ".htm": "html",
        ".xml": "html",
        ".xhtml": "html",
        ".svg": "html",
        # SQL
        ".sql": "double_dash",
        # Lua
        ".lua": "double_dash",
        # Docker
        ".dockerfile": "hash",
        # Makefile
        ".mk": "hash",
        # JSON (technically doesn't support comments, but some tools allow them)
        ".json": "double_slash",
        ".jsonc": "double_slash",
    }

    # Special filename patterns (all lowercase for case-insensitive matching)
    FILENAME_PATTERNS = {
        "dockerfile": "hash",
        "makefile": "hash",
        "rakefile": "hash",
        "gemfile": "hash",
        "gemfile.lock": "hash",
        "pipfile": "hash",
        "pipfile.lock": "hash",
        "requirements.txt": "hash",
        "requirements-dev.txt": "hash",
        ".gitignore": "hash",
        ".dockerignore": "hash",
        ".env": "hash",
        ".env.local": "hash",
        ".env.example": "hash",
        ".env.development": "hash",
        ".env.production": "hash",
        ".env.test": "hash",
        "cargo.toml": "hash",
        "cargo.lock": "hash",
        "pyproject.toml": "hash",
        "poetry.lock": "hash",
        "go.mod": "double_slash",
        "go.sum": "double_slash",
    }

    def __init__(self):
        """Initialize file type detector."""
        pass

    def detect_comment_type(self, file_path: Path) -> Optional[str]:
        """Detect the appropriate comment syntax for a file.

        Args:
            file_path: Path to file

        Returns:
            Comment type string ('hash', 'double_slash', 'css', 'html', 'double_dash')
            or None if not supported
        """
        file_path = Path(file_path)

        # Check special filename patterns first
        filename = file_path.name.lower()
        if filename in self.FILENAME_PATTERNS:
            return self.FILENAME_PATTERNS[filename]

        # Check by file extension
        suffix = file_path.suffix.lower()
        if suffix in self.EXTENSION_MAP:
            return self.EXTENSION_MAP[suffix]

        # Handle files with multiple extensions (e.g., .env.local, config.yml)
        if len(file_path.suffixes) > 1:
            # Check if any part of the filename indicates the file type
            name_parts = file_path.name.lower().split(".")

            # Look for environment files pattern
            if any(part in name_parts for part in ["env", "environment"]):
                return "hash"

            # Check each suffix
            for suffix in file_path.suffixes:
                if suffix.lower() in self.EXTENSION_MAP:
                    return self.EXTENSION_MAP[suffix.lower()]

        # Try content-based detection for files without extensions
        if not file_path.suffix and file_path.exists():
            return self._detect_by_content(file_path)

        return None

    def _detect_by_content(self, file_path: Path) -> Optional[str]:
        """Detect comment type by examining file content.

        Args:
            file_path: Path to file to examine

        Returns:
            Comment type if detected, None otherwise
        """
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                # Read first few lines to detect shebang or content patterns
                first_lines = []
                for i, line in enumerate(f):
                    if i >= 5:  # Only check first 5 lines
                        break
                    first_lines.append(line.strip())

                # Check for shebang patterns
                if first_lines and first_lines[0].startswith("#!"):
                    shebang = first_lines[0].lower()
                    if any(shell in shebang for shell in ["bash", "sh", "zsh", "fish"]):
                        return "hash"
                    elif "python" in shebang:
                        return "hash"
                    elif "node" in shebang or "bun" in shebang:
                        return "double_slash"

                # Check for common file patterns
                content = " ".join(first_lines).lower()
                if any(
                    keyword in content
                    for keyword in ["import ", "from ", "def ", "class "]
                ):
                    return "hash"  # Likely Python
                elif any(
                    keyword in content
                    for keyword in ["const ", "let ", "var ", "function"]
                ):
                    return "double_slash"  # Likely JavaScript

        except (OSError, UnicodeDecodeError):
            # Skip binary files or files we can't read
            pass

        return None

    def is_supported_file(self, file_path: Path) -> bool:
        """Check if file type is supported for template processing.

        Args:
            file_path: Path to file

        Returns:
            True if file type is supported
        """
        return self.detect_comment_type(file_path) is not None

    def get_supported_extensions(self) -> List[str]:
        """Get list of all supported file extensions.

        Returns:
            List of supported file extensions
        """
        return list(self.EXTENSION_MAP.keys())

    def get_comment_syntax_info(self, comment_type: str) -> Dict[str, str]:
        """Get comment syntax information for a comment type.

        Args:
            comment_type: Type of comment ('hash', 'double_slash', etc.)

        Returns:
            Dictionary with comment syntax information
        """
        syntax_info = {
            "hash": {
                "single_line": "#",
                "example": "# variable = {{ expression }}",
                "description": "Hash comments (Python, Shell, YAML)",
            },
            "double_slash": {
                "single_line": "//",
                "example": "// variable = {{ expression }}",
                "description": "Double slash comments (JavaScript, Java, C++)",
            },
            "css": {
                "single_line": "/* */",
                "example": "/* variable = {{ expression }} */",
                "description": "CSS-style comments",
            },
            "html": {
                "single_line": "<!-- -->",
                "example": "<!-- variable = {{ expression }} -->",
                "description": "HTML/XML comments",
            },
            "double_dash": {
                "single_line": "--",
                "example": "-- variable = {{ expression }}",
                "description": "Double dash comments (SQL, Lua)",
            },
        }

        return syntax_info.get(comment_type, {})
