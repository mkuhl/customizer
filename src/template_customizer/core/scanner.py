"""File scanning and discovery module."""

from pathlib import Path
from typing import List, Set, Iterator
import fnmatch


class FileScanner:
    """Scans directories for files to process, with filtering capabilities."""
    
    DEFAULT_EXCLUDES = {
        "*.git*",
        "*node_modules*",
        "*__pycache__*",
        "*.pyc",
        "*.pyo",
        "*dist*",
        "*build*",
        "*venv*",
        "*.venv*",
        "*htmlcov*",
        "*.coverage*",
        "*pytest_cache*",
        "*mypy_cache*",
        "*ruff_cache*",
        "*.egg-info*",
        "*target*",  # Rust/Java builds
        "*bin*",
        "*obj*",     # .NET builds
    }
    
    def __init__(
        self,
        project_path: Path,
        include_patterns: List[str] = None,
        exclude_patterns: List[str] = None,
    ):
        """Initialize file scanner.
        
        Args:
            project_path: Root directory to scan
            include_patterns: File patterns to include (e.g., ["*.py", "*.js"])
            exclude_patterns: Additional patterns to exclude
        """
        self.project_path = Path(project_path)
        self.include_patterns = include_patterns or ["*"]
        self.exclude_patterns = set(exclude_patterns or []) | self.DEFAULT_EXCLUDES
    
    def scan(self) -> Iterator[Path]:
        """Scan for processable files.
        
        Yields:
            Path objects for files that match criteria
        """
        if not self.project_path.exists():
            raise FileNotFoundError(f"Project path does not exist: {self.project_path}")
        
        if not self.project_path.is_dir():
            raise ValueError(f"Project path is not a directory: {self.project_path}")
        
        for file_path in self._walk_directory(self.project_path):
            if self._should_include(file_path):
                yield file_path
    
    def _walk_directory(self, directory: Path) -> Iterator[Path]:
        """Recursively walk directory tree."""
        try:
            for item in directory.iterdir():
                if item.is_file():
                    yield item
                elif item.is_dir() and not self._is_excluded_directory(item):
                    yield from self._walk_directory(item)
        except PermissionError:
            # Skip directories we can't read
            pass
    
    def _should_include(self, file_path: Path) -> bool:
        """Check if file should be included based on patterns."""
        relative_path = file_path.relative_to(self.project_path)
        path_str = str(relative_path)
        
        # Check exclusion patterns first
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return False
        
        # Check inclusion patterns
        for pattern in self.include_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True
        
        return False
    
    def _is_excluded_directory(self, directory: Path) -> bool:
        """Check if directory should be excluded from traversal."""
        dir_name = directory.name
        relative_path = directory.relative_to(self.project_path)
        path_str = str(relative_path)
        
        for pattern in self.exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern) or fnmatch.fnmatch(dir_name, pattern):
                return True
        
        return False