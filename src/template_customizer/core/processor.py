"""Template processing and rendering module."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from jinja2 import BaseLoader, Environment, TemplateError, UndefinedError

from .parser import TemplateMarker


class ParameterLoader:
    """Loads configuration parameters from YAML or JSON files."""

    def __init__(self, config_path: Path):
        """Initialize parameter loader.

        Args:
            config_path: Path to configuration file
        """
        self.config_path = Path(config_path)

    def load(self) -> Dict[str, Any]:
        """Load parameters from configuration file.

        Returns:
            Dictionary of configuration parameters

        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config file is malformed
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                if self.config_path.suffix.lower() in [".yml", ".yaml"]:
                    return yaml.safe_load(f) or {}
                elif self.config_path.suffix.lower() == ".json":
                    return json.load(f)
                else:
                    # Try YAML first, then JSON
                    content = f.read()
                    try:
                        return yaml.safe_load(content) or {}
                    except yaml.YAMLError:
                        return json.loads(content)
        except (yaml.YAMLError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid configuration file format: {e}") from e


class TemplateProcessor:
    """Processes template markers and renders values."""

    def __init__(self, parameters: Dict[str, Any]):
        """Initialize template processor.

        Args:
            parameters: Configuration parameters for template rendering
        """
        self.parameters = parameters
        self.jinja_env = Environment(loader=BaseLoader())

        # Add custom filters if needed
        self.jinja_env.filters["quote"] = self._quote_filter

    def render_template(self, template_expression: str) -> str:
        """Render a template expression with loaded parameters.

        Args:
            template_expression: Jinja2 template expression

        Returns:
            Rendered string value

        Raises:
            TemplateError: If template rendering fails
        """
        try:
            template = self.jinja_env.from_string(f"{{{{ {template_expression} }}}}")
            result = template.render(values=self.parameters)
            return result
        except UndefinedError as e:
            raise TemplateError(
                f"Undefined variable in template '{template_expression}': {e}"
            ) from e
        except Exception as e:
            raise TemplateError(
                f"Error rendering template '{template_expression}': {e}"
            ) from e

    def process_markers(
        self, markers: List[TemplateMarker]
    ) -> Tuple[List[tuple], List[tuple]]:
        """Process template markers and generate replacement values.

        Args:
            markers: List of template markers to process

        Returns:
            Tuple of (successful_results, errors) where:
            - successful_results: List of tuples (marker, rendered_value)
            - errors: List of tuples (marker, error_message)
        """
        results = []
        errors = []

        for marker in markers:
            try:
                rendered_value = self.render_template(marker.template_expression)
                results.append((marker, rendered_value))
            except TemplateError as e:
                # Collect errors separately for reporting
                error_msg = str(e).replace(
                    "Undefined variable in template", "Missing value"
                )
                errors.append((marker, error_msg))

        return results, errors

    def _quote_filter(self, value: Any) -> str:
        """Custom Jinja2 filter to add quotes around string values."""
        if isinstance(value, str):
            return f'"{value}"'
        return str(value)
