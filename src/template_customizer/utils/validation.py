"""Validation utilities for parameters and templates."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Template, TemplateError


class ParameterValidator:
    """Validates configuration parameters."""

    def __init__(self):
        """Initialize parameter validator."""
        pass

    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """Validate configuration parameters.

        Args:
            parameters: Configuration parameters to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors: List[str] = []

        if not isinstance(parameters, dict):
            errors.append("Configuration must be a dictionary/object")
            return errors

        # Check for common required fields (customize as needed)
        self._validate_structure(parameters, errors)

        return errors

    def _validate_structure(self, parameters: Dict[str, Any], errors: List[str]):
        """Validate parameter structure."""
        # This can be extended with schema validation
        # For now, just basic checks

        def check_nested_dict(obj: Any, path: str = ""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key

                    # Check key naming
                    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", key):
                        errors.append(
                            f"Invalid parameter name '{current_path}': "
                            f"must be valid identifier"
                        )

                    # Recursively check nested objects
                    check_nested_dict(value, current_path)
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    check_nested_dict(item, f"{path}[{i}]")

        check_nested_dict(parameters)


class TemplateValidator:
    """Validates Jinja2 template expressions."""

    def __init__(self):
        """Initialize template validator."""
        pass

    def validate_template_expression(self, expression: str) -> Optional[str]:
        """Validate a Jinja2 template expression.

        Args:
            expression: Template expression to validate

        Returns:
            Error message if invalid, None if valid
        """
        try:
            # Create a template to check syntax
            Template(f"{{{{ {expression} }}}}")
            return None
        except TemplateError as e:
            return f"Invalid template syntax: {e}"
        except Exception as e:
            return f"Template validation error: {e}"

    def validate_variable_reference(
        self, expression: str, available_variables: Dict[str, Any]
    ) -> Optional[str]:
        """Validate that template expression uses available variables.

        Args:
            expression: Template expression to check
            available_variables: Available configuration variables

        Returns:
            Error message if invalid references found, None if valid
        """
        # Extract variable references from expression
        variable_pattern = re.compile(
            r"values\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)"
        )

        matches = variable_pattern.findall(expression)

        for var_path in matches:
            if not self._check_variable_exists(var_path, available_variables):
                return f"Variable 'values.{var_path}' not found in configuration"

        return None

    def _check_variable_exists(self, var_path: str, variables: Dict[str, Any]) -> bool:
        """Check if a dotted variable path exists in the variables dict."""
        parts = var_path.split(".")
        current = variables

        try:
            for part in parts:
                if isinstance(current, dict) and part in current:
                    current = current[part]
                else:
                    return False
            return True
        except (TypeError, KeyError):
            return False


class ProjectValidator:
    """Validates project structure and files."""

    def __init__(self):
        """Initialize project validator."""
        pass

    def validate_project_path(self, project_path: Path) -> List[str]:
        """Validate project directory.

        Args:
            project_path: Path to project directory

        Returns:
            List of validation error messages
        """
        errors = []

        project_path = Path(project_path)

        if not project_path.exists():
            errors.append(f"Project path does not exist: {project_path}")
            return errors

        if not project_path.is_dir():
            errors.append(f"Project path is not a directory: {project_path}")
            return errors

        # Check if directory is readable
        try:
            list(project_path.iterdir())
        except PermissionError:
            errors.append(f"No permission to read project directory: {project_path}")

        return errors

    def validate_config_file(self, config_path: Path) -> List[str]:
        """Validate configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            List of validation error messages
        """
        errors = []

        config_path = Path(config_path)

        if not config_path.exists():
            errors.append(f"Configuration file does not exist: {config_path}")
            return errors

        if not config_path.is_file():
            errors.append(f"Configuration path is not a file: {config_path}")
            return errors

        # Check file extension
        valid_extensions = [".yml", ".yaml", ".json"]
        if config_path.suffix.lower() not in valid_extensions:
            errors.append(
                f"Configuration file should have one of these extensions: "
                f"{', '.join(valid_extensions)}"
            )

        return errors
