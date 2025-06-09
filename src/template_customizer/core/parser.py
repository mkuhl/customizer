"""Comment parsing and template marker extraction module."""

import re
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional


class TemplateMarker(NamedTuple):
    """Represents a template marker found in a comment."""

    line_number: int
    variable_name: str
    template_expression: str
    comment_line: str
    target_line_number: int
    comment_type: Optional[str] = None
    file_path: Optional[Path] = None


class CommentParser:
    """Parses files for comment-based template markers."""

    # Comment syntax patterns for different file types
    COMMENT_PATTERNS = {
        # Single-line comments
        "hash": re.compile(r"^\s*#\s*(.+)$"),  # Python, Shell, YAML
        "double_slash": re.compile(r"^\s*//\s*(.+)$"),  # JavaScript, Java, C++
        "double_dash": re.compile(r"^\s*--\s*(.+)$"),  # SQL, Lua
        # Multi-line comments (single line form)
        "css": re.compile(r"^\s*/\*\s*(.+?)\s*\*/\s*$"),  # CSS, C, Java
        "html": re.compile(r"^\s*<!--\s*(.+?)\s*-->\s*$"),  # HTML, XML
    }

    # Enhanced template marker patterns
    # Primary pattern: variable_name = {{ expression }}
    MARKER_PATTERN = re.compile(r"^(\w+)\s*=\s*\{\{\s*(.+?)\s*\}\}$")

    # Alternative patterns for flexibility
    ALT_MARKER_PATTERNS = [
        # With quotes: "variable_name" = {{ expression }}
        re.compile(r'^["\']?(\w+)["\']?\s*=\s*\{\{\s*(.+?)\s*\}\}$'),
        # With colons (YAML style): variable_name: {{ expression }}
        re.compile(r"^(\w+)\s*:\s*\{\{\s*(.+?)\s*\}\}$"),
        # Spaced braces: variable_name = { { expression } }
        re.compile(r"^(\w+)\s*=\s*\{\s*\{\s*(.+?)\s*\}\s*\}$"),
    ]

    def __init__(self, file_type_detector=None):
        """Initialize comment parser.

        Args:
            file_type_detector: FileTypeDetector instance for comment type detection
        """
        self.file_type_detector = file_type_detector

    def parse_file(self, file_path: Path) -> List[TemplateMarker]:
        """Parse a file for template markers.

        Args:
            file_path: Path to file to parse

        Returns:
            List of TemplateMarker objects found in the file
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File does not exist: {file_path}")

        try:
            with open(file_path, encoding="utf-8") as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Skip binary files
            return []

        # Determine comment type for this file
        comment_type = None
        if self.file_type_detector:
            comment_type = self.file_type_detector.detect_comment_type(file_path)

        markers = []

        for i, line in enumerate(lines):
            comment_content = self._extract_comment_content(line, comment_type)
            if comment_content:
                marker_match = self._extract_template_marker(comment_content.strip())
                if marker_match:
                    variable_name, template_expression = marker_match

                    # Target line is the next line after the comment
                    target_line_number = i + 1

                    marker = TemplateMarker(
                        line_number=i,
                        variable_name=variable_name,
                        template_expression=template_expression,
                        comment_line=line.rstrip(),
                        target_line_number=target_line_number,
                        comment_type=comment_type,
                        file_path=file_path,
                    )
                    markers.append(marker)

        return markers

    def _extract_comment_content(
        self, line: str, comment_type: Optional[str] = None
    ) -> Optional[str]:
        """Extract content from comment line.

        Args:
            line: Line to check for comments
            comment_type: Specific comment type to check, or None to try all

        Returns:
            Comment content if found, None otherwise
        """
        # If we know the comment type, check that pattern first
        if comment_type and comment_type in self.COMMENT_PATTERNS:
            pattern = self.COMMENT_PATTERNS[comment_type]
            match = pattern.match(line)
            if match:
                return match.group(1)

        # Fallback: try all comment patterns
        for pattern in self.COMMENT_PATTERNS.values():
            match = pattern.match(line)
            if match:
                return match.group(1)

        return None

    def _extract_template_marker(self, comment_content: str) -> Optional[tuple]:
        """Extract template marker from comment content.

        Args:
            comment_content: Content of the comment to parse

        Returns:
            Tuple of (variable_name, template_expression) if found, None otherwise
        """
        content = comment_content.strip()

        # Try primary pattern first
        match = self.MARKER_PATTERN.match(content)
        if match:
            var_name, expr = match.groups()
            if self._is_valid_variable_name(var_name) and self._is_valid_expression(
                expr
            ):
                return (var_name, expr)

        # Try alternative patterns
        for pattern in self.ALT_MARKER_PATTERNS:
            match = pattern.match(content)
            if match:
                var_name, expr = match.groups()
                if self._is_valid_variable_name(var_name) and self._is_valid_expression(
                    expr
                ):
                    return (var_name, expr)

        return None

    def _is_valid_variable_name(self, var_name: str) -> bool:
        """Check if variable name is valid.

        Args:
            var_name: Variable name to validate

        Returns:
            True if valid variable name
        """
        import keyword

        # Must be valid Python identifier, not start with underscore,
        # and not be a keyword
        return (
            var_name.isidentifier()
            and not var_name.startswith("_")
            and not keyword.iskeyword(var_name)
        )

    def _is_valid_expression(self, expression: str) -> bool:
        """Check if template expression appears valid.

        Args:
            expression: Template expression to validate

        Returns:
            True if expression appears valid
        """
        expr = expression.strip()

        # Must not be empty
        if not expr:
            return False

        # Should not contain unescaped {{ or }}
        if "{{" in expr or "}}" in expr:
            return False

        # Must contain at least one valid character
        return len(expr) > 0

    def get_marker_statistics(self, markers: List[TemplateMarker]) -> Dict[str, int]:
        """Get statistics about parsed markers.

        Args:
            markers: List of template markers

        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_markers": len(markers),
            "unique_variables": len({m.variable_name for m in markers}),
            "comment_types": {},
        }

        # Count by comment type
        for marker in markers:
            comment_type = marker.comment_type or "unknown"
            stats["comment_types"][comment_type] = (
                stats["comment_types"].get(comment_type, 0) + 1
            )

        return stats

    def validate_template_syntax(self, template_expression: str) -> bool:
        """Validate Jinja2 template syntax.

        Args:
            template_expression: Template expression to validate

        Returns:
            True if syntax is valid, False otherwise
        """
        try:
            from jinja2 import Environment, TemplateSyntaxError

            # Create environment with common filters
            env = Environment()
            env.filters["quote"] = lambda x: f'"{x}"'  # Custom quote filter

            env.from_string(f"{{{{ {template_expression} }}}}")
            return True
        except (TemplateSyntaxError, Exception):
            return False

    def validate_template_syntax_detailed(
        self, template_expression: str
    ) -> tuple[bool, Optional[str]]:
        """Validate Jinja2 template syntax with detailed error information.

        Args:
            template_expression: Template expression to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            from jinja2 import Environment, TemplateSyntaxError, UndefinedError

            # Create environment with common filters
            env = Environment()
            env.filters["quote"] = lambda x: f'"{x}"'  # Custom quote filter

            env.from_string(f"{{{{ {template_expression} }}}}")
            return (True, None)
        except TemplateSyntaxError as e:
            return (False, f"Syntax error: {e}")
        except UndefinedError as e:
            return (False, f"Undefined variable: {e}")
        except Exception as e:
            return (False, f"Template error: {e}")

    def validate_all_markers(
        self, markers: List[TemplateMarker]
    ) -> Dict[str, List[str]]:
        """Validate template syntax for all markers.

        Args:
            markers: List of template markers to validate

        Returns:
            Dictionary with 'valid' and 'invalid' lists of markers with details
        """
        results = {"valid": [], "invalid": []}

        for marker in markers:
            is_valid, error = self.validate_template_syntax_detailed(
                marker.template_expression
            )

            marker_info = {
                "marker": marker,
                "file": str(marker.file_path) if marker.file_path else "unknown",
                "line": marker.line_number + 1,  # 1-based for display
                "variable": marker.variable_name,
                "expression": marker.template_expression,
            }

            if is_valid:
                results["valid"].append(marker_info)
            else:
                marker_info["error"] = error
                results["invalid"].append(marker_info)

        return results
