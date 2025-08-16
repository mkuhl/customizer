"""JSON file replacer using JSONPath expressions."""

import json
import re
from pathlib import Path
from typing import Any, Dict

from jinja2 import Environment, Template
from jsonpath_ng import parse as parse_jsonpath
from jsonpath_ng.exceptions import JsonPathParserError

from ..external_replacements import ExternalReplacementError


class JSONReplacer:
    """Handles JSON file replacements using JSONPath expressions."""

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize JSON replacer with parameters for template rendering.
        
        Args:
            parameters: Configuration parameters for template rendering
        """
        self.parameters = parameters
        self.jinja_env = Environment()

    def replace(self, file_path: Path, replacements: Dict[str, Any]) -> str:
        """Apply replacements to a JSON file.
        
        Args:
            file_path: Path to JSON file
            replacements: Dictionary of JSONPath to template expressions
            
        Returns:
            Modified JSON content as string
            
        Raises:
            ExternalReplacementError: If JSON parsing or replacement fails
        """
        try:
            # Read and parse JSON file
            with open(file_path, encoding='utf-8') as f:
                content = f.read()
                data = json.loads(content)

            # Detect original formatting
            indent = self._detect_indent(content)

            # Apply each replacement
            for jsonpath, template_expr in replacements.items():
                # Render the template expression
                rendered_value = self._render_template(template_expr)

                # Apply JSONPath replacement
                data = self._apply_jsonpath(data, jsonpath, rendered_value)

            # Convert back to JSON with original formatting
            return json.dumps(data, indent=indent, ensure_ascii=False)

        except json.JSONDecodeError as e:
            raise ExternalReplacementError(f"Invalid JSON in {file_path}: {e}") from e
        except JsonPathParserError as e:
            raise ExternalReplacementError(f"Invalid JSONPath expression: {e}") from e
        except Exception as e:
            raise ExternalReplacementError(f"Error processing {file_path}: {e}") from e

    def _render_template(self, template_expr: Any) -> Any:
        """Render a Jinja2 template expression.
        
        Args:
            template_expr: Template expression to render (can be string, bool, number, etc.)
            
        Returns:
            Rendered value (could be string, number, boolean, etc.)
        """
        # Handle non-string values (already processed values like booleans, numbers)
        if not isinstance(template_expr, str):
            return template_expr

        # Handle direct values (not templates)
        if not ('{{' in template_expr and '}}' in template_expr):
            # Try to parse as JSON value (number, boolean, null)
            try:
                return json.loads(template_expr)
            except json.JSONDecodeError:
                # It's a plain string
                return template_expr

        # Render Jinja2 template
        template = Template(template_expr)
        result = template.render(values=self.parameters)

        # Try to parse result as JSON value
        result_stripped = result.strip()
        if result_stripped.lower() == 'true':
            return True
        elif result_stripped.lower() == 'false':
            return False
        elif result_stripped.lower() == 'null' or result_stripped.lower() == 'none':
            return None
        else:
            try:
                return json.loads(result_stripped)
            except json.JSONDecodeError:
                # Return as string
                return result

    def _apply_jsonpath(self, data: Any, jsonpath: str, value: Any) -> Any:
        """Apply a JSONPath replacement to data.
        
        Args:
            data: JSON data structure
            jsonpath: JSONPath expression
            value: Value to set
            
        Returns:
            Modified data structure
        """
        try:
            jsonpath_expr = parse_jsonpath(jsonpath)
            matches = jsonpath_expr.find(data)

            if matches:
                # Update existing paths
                for match in matches:
                    match.full_path.update(data, value)
            else:
                # Path doesn't exist, try to create it
                self._create_path(data, jsonpath, value)

            return data

        except Exception as e:
            raise ExternalReplacementError(
                f"Failed to apply JSONPath {jsonpath}: {e}"
            ) from e

    def _create_path(self, data: Any, jsonpath: str, value: Any) -> None:
        """Create a new path in JSON data.
        
        Args:
            data: JSON data structure
            jsonpath: JSONPath expression
            value: Value to set
        """
        # Simple implementation for common cases
        # Remove $ prefix
        path = jsonpath.lstrip('$.')

        # Split path into parts
        parts = []
        current = ""
        in_brackets = False

        for char in path:
            if char == '[':
                if current:
                    parts.append(current)
                    current = ""
                in_brackets = True
            elif char == ']':
                if current:
                    parts.append(int(current) if current.isdigit() else current)
                    current = ""
                in_brackets = False
            elif char == '.' and not in_brackets:
                if current:
                    parts.append(current)
                    current = ""
            else:
                current += char

        if current:
            parts.append(current)

        # Navigate/create path
        current_data = data
        for i, part in enumerate(parts[:-1]):
            if isinstance(part, int):
                # Array index
                while len(current_data) <= part:
                    current_data.append(None)
                if current_data[part] is None:
                    # Determine if next part is array or object
                    next_part = parts[i + 1]
                    current_data[part] = [] if isinstance(next_part, int) else {}
                current_data = current_data[part]
            else:
                # Object key
                if part not in current_data:
                    # Determine if next part is array or object
                    next_part = parts[i + 1] if i + 1 < len(parts) else None
                    current_data[part] = [] if isinstance(next_part, int) else {}
                current_data = current_data[part]

        # Set final value
        final_part = parts[-1]
        if isinstance(final_part, int):
            while len(current_data) <= final_part:
                current_data.append(None)
            current_data[final_part] = value
        else:
            current_data[final_part] = value

    def _detect_indent(self, json_content: str) -> int:
        """Detect indentation level from JSON content.
        
        Args:
            json_content: Original JSON content
            
        Returns:
            Number of spaces for indentation (default 2)
        """
        # Look for indentation in first few lines
        lines = json_content.split('\n')[:10]

        for line in lines:
            # Look for lines that start with spaces
            match = re.match(r'^(\s+)"', line)
            if match:
                return len(match.group(1))

        return 2  # Default to 2 spaces
