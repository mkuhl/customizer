"""Custom exceptions for configuration resolution."""

from typing import List, Optional


class ConfigurationError(Exception):
    """Base class for configuration-related errors."""

    pass


class CircularReferenceError(ConfigurationError):
    """Raised when circular dependencies are detected in configuration references."""

    def __init__(self, cycle_path: List[str], message: Optional[str] = None):
        """Initialize circular reference error.

        Args:
            cycle_path: List of reference keys that form the circular dependency
            message: Optional custom error message
        """
        self.cycle_path = cycle_path

        if message is None:
            cycle_display = " → ".join(cycle_path + [cycle_path[0]])
            message = f"Circular dependency detected: {cycle_display}"

        super().__init__(message)


class ReferenceResolutionError(ConfigurationError):
    """Raised when a reference cannot be resolved."""

    def __init__(
        self,
        reference: str,
        config_path: Optional[str] = None,
        line_number: Optional[int] = None,
        message: Optional[str] = None,
    ):
        """Initialize reference resolution error.

        Args:
            reference: The reference that could not be resolved
            config_path: Path to the configuration file (if known)
            line_number: Line number where reference appears (if known)
            message: Optional custom error message
        """
        self.reference = reference
        self.config_path = config_path
        self.line_number = line_number

        if message is None:
            location_info = ""
            if line_number is not None:
                location_info = f" at line {line_number}"
            if config_path is not None:
                location_info += f" in {config_path}"

            message = f"Reference '{reference}' not found{location_info}"

        super().__init__(message)


class MaxRecursionError(ConfigurationError):
    """Raised when maximum recursion depth is exceeded during resolution."""

    def __init__(self, depth: int, reference: str, message: Optional[str] = None):
        """Initialize max recursion error.

        Args:
            depth: The maximum depth that was exceeded
            reference: The reference being resolved when limit was hit
            message: Optional custom error message
        """
        self.depth = depth
        self.reference = reference

        if message is None:
            message = (
                f"Maximum recursion depth ({depth}) exceeded while resolving "
                f"reference '{reference}'. This may indicate a complex "
                f"dependency chain or circular references."
            )

        super().__init__(message)


class TemplateSyntaxError(ConfigurationError):
    """Raised when template syntax is invalid."""

    def __init__(
        self,
        template: str,
        original_error: Exception,
        line_number: Optional[int] = None,
        message: Optional[str] = None,
    ):
        """Initialize template syntax error.

        Args:
            template: The template expression that caused the error
            original_error: The original Jinja2 template error
            line_number: Line number where template appears (if known)
            message: Optional custom error message
        """
        self.template = template
        self.original_error = original_error
        self.line_number = line_number

        if message is None:
            location_info = ""
            if line_number is not None:
                location_info = f" at line {line_number}"

            message = f"Invalid template syntax{location_info}: {original_error}"

        super().__init__(message)
