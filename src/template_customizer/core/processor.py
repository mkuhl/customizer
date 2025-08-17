"""Template processing and rendering module."""

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml
from jinja2 import BaseLoader, Environment, TemplateError, UndefinedError

from .exceptions import (
    CircularReferenceError,
    MaxRecursionError,
    ReferenceResolutionError,
    TemplateSyntaxError,
)
from .parser import TemplateMarker
from .resolver import ConfigResolver


class ParameterLoader:
    """Loads and processes configuration parameters from YAML or JSON files.

    This class handles loading configuration files and optionally resolving
    self-references within the configuration using the ConfigResolver. It supports
    both YAML and JSON formats and provides comprehensive error handling.

    NEW in v0.4.0: Self-referencing configuration values allow building complex
    configurations from simpler values using {{ values.path.to.value }} syntax.

    Features:
    - YAML and JSON configuration file support
    - Self-reference resolution with dependency graph analysis
    - Circular dependency detection and clear error reporting
    - Type preservation for pure references
    - Verbose tracing for debugging reference resolution
    - Backward compatibility with --no-resolve-refs option

    Attributes:
        config_path (Path): Path to the configuration file
        resolve_references (bool): Whether to resolve self-references
        verbose (bool): Whether to output detailed resolution information
        resolver (ConfigResolver): Resolver instance for reference resolution

    Examples:
        Basic usage:
        >>> loader = ParameterLoader(Path("config.yml"))
        >>> config = loader.load()

        With self-reference resolution:
        >>> loader = ParameterLoader(
        ...     Path("config.yml"), resolve_references=True, verbose=True
        ... )
        >>> config = loader.load()  # Shows resolution details

        Compatibility mode (no reference resolution):
        >>> loader = ParameterLoader(Path("config.yml"), resolve_references=False)
        >>> config = loader.load()  # References remain as template strings
    """

    def __init__(
        self, config_path: Path, resolve_references: bool = True, verbose: bool = False
    ):
        """Initialize parameter loader with optional reference resolution.

        Args:
            config_path: Path to configuration file (YAML or JSON)
            resolve_references: Whether to resolve self-references in configuration.
                              When True, processes {{ values.path }} references.
                              When False, leaves references as template strings.
            verbose: Whether to enable verbose output for resolution details.
                    Shows dependency graph, resolution order, and step-by-step
                    resolution process when resolve_references=True.
        """
        self.config_path = Path(config_path)
        self.resolve_references = resolve_references
        self.verbose = verbose
        self.resolver = ConfigResolver(verbose=verbose) if resolve_references else None

    def load(self) -> Dict[str, Any]:
        """Load and process parameters from configuration file.

        This method loads the configuration file, parses it (YAML or JSON), and
        optionally resolves self-references if resolve_references=True. The resolution
        process includes dependency analysis, circular detection, and type preservation.

        Returns:
            Dictionary of configuration parameters with references resolved
            (if enabled).
            Original data types are preserved for pure references, while string
            interpolation converts values to strings.

        Raises:
            FileNotFoundError: If configuration file doesn't exist
            ValueError: If configuration file format is invalid (malformed YAML/JSON)
                       or if reference resolution fails (wraps resolver exceptions)
            CircularReferenceError: If circular dependencies detected in references
            ReferenceResolutionError: If referenced values cannot be found
            TemplateSyntaxError: If Jinja2 template syntax is invalid

        Examples:
            With references resolved:
            >>> loader = ParameterLoader(Path("config.yml"), resolve_references=True)
            >>> config = loader.load()
            >>> # {{ values.project.name }} becomes actual value

            Without reference resolution:
            >>> loader = ParameterLoader(Path("config.yml"), resolve_references=False)
            >>> config = loader.load()
            >>> # {{ values.project.name }} remains as template string
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

        try:
            with open(self.config_path, encoding="utf-8") as f:
                if self.config_path.suffix.lower() in [".yml", ".yaml"]:
                    config = yaml.safe_load(f) or {}
                elif self.config_path.suffix.lower() == ".json":
                    config = json.load(f)
                else:
                    # Try YAML first, then JSON
                    content = f.read()
                    try:
                        config = yaml.safe_load(content) or {}
                    except yaml.YAMLError:
                        config = json.loads(content)

            # Resolve self-references if enabled
            if self.resolve_references and self.resolver:
                try:
                    if self.verbose:
                        print("🔄 Resolving self-references in configuration...")
                    config = self.resolver.resolve(config)
                    if self.verbose:
                        print("✅ Successfully resolved configuration references")
                except CircularReferenceError as e:
                    raise ValueError(
                        f"Circular dependency detected in configuration file "
                        f"'{self.config_path}':\n"
                        f"  {str(e)}\n"
                        f"  Please check your configuration for references that "
                        f"form a loop."
                    ) from e
                except ReferenceResolutionError as e:
                    raise ValueError(
                        f"Reference resolution failed in configuration file "
                        f"'{self.config_path}':\n"
                        f"  {str(e)}\n"
                        f"  Please ensure all referenced values exist in your "
                        f"configuration."
                    ) from e
                except MaxRecursionError as e:
                    raise ValueError(
                        f"Maximum recursion depth exceeded in configuration file "
                        f"'{self.config_path}':\n"
                        f"  {str(e)}\n"
                        f"  This usually indicates a very complex dependency chain "
                        f"or circular references."
                    ) from e
                except TemplateSyntaxError as e:
                    raise ValueError(
                        f"Template syntax error in configuration file "
                        f"'{self.config_path}':\n"
                        f"  {str(e)}\n"
                        f"  Please check your Jinja2 template syntax."
                    ) from e

            return config
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
