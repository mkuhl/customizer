"""Markdown file replacer using pattern matching."""

import re
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, Template

from ..external_replacements import ExternalReplacementError


class MarkdownReplacer:
    """Handles Markdown file replacements using pattern matching."""

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize Markdown replacer with parameters for template rendering.
        
        Args:
            parameters: Configuration parameters for template rendering
        """
        self.parameters = parameters
        self.jinja_env = Environment()

        # Add useful filters for markdown
        self.jinja_env.filters['title'] = lambda s: s.replace('-', ' ').title()
        self.jinja_env.filters['upper'] = lambda s: s.upper()
        self.jinja_env.filters['lower'] = lambda s: s.lower()

    def replace(self, file_path: Path, replacements: Dict[str, str]) -> str:
        """Apply replacements to a Markdown file.
        
        Args:
            file_path: Path to Markdown file
            replacements: Dictionary of patterns to template expressions
            
        Returns:
            Modified Markdown content as string
            
        Raises:
            ExternalReplacementError: If file reading or replacement fails
        """
        try:
            # Read file content
            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Apply each replacement
            for pattern_spec, template_expr in replacements.items():
                # Parse pattern specification
                pattern_type, pattern = self._parse_pattern_spec(pattern_spec)

                # Render the template expression
                rendered_value = self._render_template(template_expr)

                # Apply pattern replacement
                if pattern_type == "pattern":
                    content = self._apply_regex_pattern(content, pattern, rendered_value)
                elif pattern_type == "literal":
                    content = self._apply_literal_pattern(content, pattern, rendered_value)
                else:
                    raise ExternalReplacementError(f"Unknown pattern type: {pattern_type}")

            return content

        except FileNotFoundError as e:
            raise ExternalReplacementError(f"File not found: {file_path}") from e
        except re.error as e:
            raise ExternalReplacementError(f"Invalid regex pattern: {e}") from e
        except Exception as e:
            raise ExternalReplacementError(f"Error processing {file_path}: {e}") from e

    def _parse_pattern_spec(self, pattern_spec: str) -> tuple[str, str]:
        """Parse pattern specification into type and pattern.
        
        Args:
            pattern_spec: Pattern specification ("pattern: foo.*", "literal: [test]")
            
        Returns:
            Tuple of (pattern_type, pattern)
        """
        if pattern_spec.startswith("pattern: "):
            return "pattern", pattern_spec[9:]  # Remove "pattern: " prefix
        elif pattern_spec.startswith("literal: "):
            return "literal", pattern_spec[9:]  # Remove "literal: " prefix
        else:
            # Default to pattern (regex) mode
            return "pattern", pattern_spec

    def _render_template(self, template_expr: str) -> str:
        """Render a Jinja2 template expression.
        
        Args:
            template_expr: Template expression to render
            
        Returns:
            Rendered string value
        """
        # Handle direct values (not templates)
        if not ('{{' in template_expr and '}}' in template_expr):
            return template_expr

        # Render Jinja2 template
        template = Template(template_expr, extensions=['jinja2.ext.do'])
        result = template.render(values=self.parameters)

        return result

    def _apply_regex_pattern(self, content: str, pattern: str, replacement: str) -> str:
        """Apply regex pattern replacement.
        
        Args:
            content: Original content
            pattern: Regex pattern to match
            replacement: Replacement string (may contain backreferences)
            
        Returns:
            Modified content
        """
        try:
            # Check if replacement has backreferences
            if '\\' in replacement and any(f'\\{i}' in replacement for i in range(10)):
                # Use regex replacement with backreferences
                return re.sub(pattern, replacement, content)
            else:
                # Simple replacement
                return re.sub(pattern, replacement, content)
        except re.error as e:
            msg = f"Regex error with pattern '{pattern}': {e}"
            raise ExternalReplacementError(msg) from e

    def _apply_literal_pattern(
        self, content: str, pattern: str, replacement: str
    ) -> str:
        """Apply literal string replacement (no regex).
        
        Args:
            content: Original content
            pattern: Literal string to match
            replacement: Replacement string
            
        Returns:
            Modified content
        """
        # Escape special regex characters in pattern
        escaped_pattern = re.escape(pattern)
        return re.sub(escaped_pattern, replacement, content)
