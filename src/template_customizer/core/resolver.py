"""Configuration resolver for self-referencing YAML values.

This module provides the core functionality for resolving self-references within
configuration files, allowing users to build complex configurations from simpler
values using Jinja2 template syntax.

Key Features:
- Automatic dependency graph construction and resolution
- Circular dependency detection with clear error messages
- Topological sorting for optimal resolution order
- Type preservation for pure references vs string interpolation
- Comprehensive error handling with helpful context
- Verbose tracing for debugging reference resolution

Example Usage:
    resolver = ConfigResolver(verbose=True)
    resolved_config = resolver.resolve({
        "project": {"name": "my-app", "version": "1.0.0"},
        "docker": {"image": "{{ values.project.name }}:{{ values.project.version }}"}
    })
    # Result: {"project": {...}, "docker": {"image": "my-app:1.0.0"}}

Supported Reference Patterns:
- Simple references: {{ values.project.name }}
- Chained references: {{ values.computed.base_url }}/api
- With filters: {{ values.name | lower | replace('-', '_') }}
- Type preservation: Pure references maintain original types
- String interpolation: Mixed content becomes strings

Error Handling:
- CircularReferenceError: When references form cycles
- ReferenceResolutionError: When referenced values don't exist
- TemplateSyntaxError: When Jinja2 syntax is invalid
- MaxRecursionError: When reference depth exceeds limits
"""

import re
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional, Set

from jinja2 import BaseLoader, Environment, TemplateError, UndefinedError

from .exceptions import (
    CircularReferenceError,
    MaxRecursionError,
    ReferenceResolutionError,
    TemplateSyntaxError,
)


class ConfigResolver:
    """Resolves self-references in configuration dictionaries.

    This class implements a sophisticated reference resolution system that can handle
    complex dependency graphs with circular detection, type preservation, and
    comprehensive error reporting.

    The resolver works by:
    1. Scanning the configuration for reference patterns
    2. Building a dependency graph of all references
    3. Detecting circular dependencies using depth-first search
    4. Topologically sorting dependencies for optimal resolution order
    5. Resolving references in multiple passes if needed
    6. Preserving original data types for pure references

    Attributes:
        max_depth (int): Maximum allowed reference chain depth (default: 10)
        verbose (bool): Whether to output detailed resolution information
        resolution_cache (Dict[str, Any]): Cache of resolved values
        resolution_stack (List[str]): Current resolution stack for cycle detection
        resolution_trace (List[str]): Trace of resolution steps for debugging
        jinja_env (Environment): Jinja2 environment for template rendering

    Examples:
        Basic resolution:
        >>> resolver = ConfigResolver()
        >>> config = {
        ...     "base": {"name": "app", "version": "1.0"},
        ...     "docker": {"image": "{{ values.base.name }}:{{ values.base.version }}"}
        ... }
        >>> result = resolver.resolve(config)
        >>> result["docker"]["image"]
        'app:1.0'

        With type preservation:
        >>> config = {
        ...     "settings": {"port": 3000, "debug": True},
        ...     "server": {"port": "{{ values.settings.port }}"}
        ... }
        >>> result = resolver.resolve(config)
        >>> isinstance(result["server"]["port"], int)
        True

        With verbose tracing:
        >>> resolver = ConfigResolver(verbose=True)
        >>> resolver.resolve(config)  # Outputs resolution steps
    """

    # Pattern to match Jinja2 references like {{ values.project.name }}
    REFERENCE_PATTERN = re.compile(r"\{\{\s*values\.([^}]+?)\s*\}\}")

    def __init__(self, max_depth: int = 10, verbose: bool = False):
        """Initialize resolver with maximum recursion depth.

        Args:
            max_depth: Maximum levels of reference chaining allowed
            verbose: Whether to enable verbose tracing output
        """
        self.max_depth = max_depth
        self.verbose = verbose
        self.resolution_cache: Dict[str, Any] = {}
        self.resolution_stack: List[str] = []
        self.resolution_trace: List[str] = []
        self.jinja_env = Environment(loader=BaseLoader())

        # Add common Jinja2 filters
        self.jinja_env.filters.update(
            {
                "lower": str.lower,
                "upper": str.upper,
                "title": str.title,
                "replace": lambda s, old, new: str(s).replace(old, new),
            }
        )

    def resolve(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Resolve all references in the configuration.

        This is the main entry point for configuration resolution. It performs
        a multi-step process to safely resolve all self-references:

        1. Builds a dependency graph of all references in the configuration
        2. Detects circular dependencies using depth-first search
        3. Topologically sorts dependencies for optimal resolution order
        4. Resolves references in multiple passes if needed
        5. Preserves original data types for pure references

        The method is designed to handle complex scenarios including:
        - Chained references (A references B which references C)
        - Mixed string interpolation and pure references
        - Nested configuration structures
        - Type preservation for numbers, booleans, and arrays

        Args:
            config: Raw configuration dictionary containing potential references
                   using {{ values.path.to.value }} syntax

        Returns:
            Deep copy of configuration with all references resolved to their
            final values. Original data types are preserved for pure references.

        Raises:
            CircularReferenceError: If circular dependency detected in references
            ReferenceResolutionError: If a referenced value cannot be found
            MaxRecursionError: If reference chain depth exceeds max_depth limit
            TemplateSyntaxError: If Jinja2 template syntax is invalid

        Example:
            >>> resolver = ConfigResolver()
            >>> config = {
            ...     "project": {"name": "myapp", "version": "1.0"},
            ...     "docker": {
            ...         "registry": "ghcr.io/company",
            ...         "image": "{{ values.docker.registry }}/{{ values.project.name}}"
            ...     }
            ... }
            >>> resolved = resolver.resolve(config)
            >>> resolved["docker"]["image"]
            'ghcr.io/company/myapp:1.0'
        """
        if not config:
            return config

        # Reset state for new resolution
        self.resolution_cache.clear()
        self.resolution_stack.clear()
        self.resolution_trace.clear()

        # Build dependency graph
        dependency_graph = self._build_dependency_graph(config)
        if self.verbose:
            self.resolution_trace.append(
                f"📊 Built dependency graph with {len(dependency_graph)} nodes"
            )
            for node, deps in dependency_graph.items():
                if deps:
                    self.resolution_trace.append(
                        f"   {node} depends on: {', '.join(deps)}"
                    )

        # Check for circular dependencies
        cycle = self._detect_circular_dependencies(dependency_graph)
        if cycle:
            raise CircularReferenceError(cycle)

        # Get resolution order
        resolution_order = self._topological_sort(dependency_graph)
        if self.verbose:
            self.resolution_trace.append(
                f"📋 Resolution order: {' → '.join(resolution_order)}"
            )

        # Create a deep copy for resolution
        resolved_config = self._deep_copy(config)

        # Resolve references in order, with multiple passes if needed
        max_iterations = 5  # Prevent infinite loops
        iteration = 0

        while iteration < max_iterations:
            changes_made = False
            self.resolution_cache.clear()  # Clear cache each iteration

            for key_path in resolution_order:
                old_value = self._get_nested_value_safe(resolved_config, key_path)
                self._resolve_key_path(key_path, resolved_config, config)
                new_value = self._get_nested_value_safe(resolved_config, key_path)
                if old_value != new_value:
                    changes_made = True

            if not changes_made:
                break
            iteration += 1

        if self.verbose:
            self.resolution_trace.append(
                f"✅ Resolution completed in {iteration} iteration(s)"
            )
            for trace_line in self.resolution_trace:
                print(f"  {trace_line}")

        return resolved_config

    def _get_nested_value_safe(self, config: Dict[str, Any], key_path: str) -> Any:
        """Get nested value safely, returning None if not found."""
        try:
            return self._get_nested_value(config, key_path)
        except KeyError:
            return None

    def _detect_references(self, value: Any) -> List[str]:
        """Find Jinja2 references in a value.

        Args:
            value: Value to scan for references

        Returns:
            List of reference paths found (e.g., ['project.name', 'api.host'])
        """
        if not isinstance(value, str):
            return []

        matches = self.REFERENCE_PATTERN.findall(value)
        return [match.strip() for match in matches]

    def _build_dependency_graph(self, config: Dict[str, Any]) -> Dict[str, Set[str]]:
        """Build dependency graph from configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Dictionary mapping key paths to their dependencies
        """
        graph = defaultdict(set)

        def scan_dict(
            obj: Dict[str, Any],
            prefix: str = "",
            path_components: Optional[List[str]] = None,
        ):
            if path_components is None:
                path_components = []

            for key, value in obj.items():
                current_components = path_components + [key]
                current_path = ".".join(current_components)

                if isinstance(value, dict):
                    scan_dict(value, current_path, current_components)
                elif isinstance(value, list):
                    # For lists, we track dependencies at the list level
                    for item in value:
                        if isinstance(item, dict):
                            scan_dict(item, current_path, current_components)
                        else:
                            refs = self._detect_references(item)
                            graph[current_path].update(refs)
                else:
                    refs = self._detect_references(value)
                    graph[current_path].update(refs)

        scan_dict(config)
        return dict(graph)

    def _topological_sort(self, graph: Dict[str, Set[str]]) -> List[str]:
        """Perform topological sort to determine resolution order.

        Args:
            graph: Dependency graph

        Returns:
            List of key paths in resolution order
        """
        # Calculate in-degrees - how many dependencies each node has
        in_degree = defaultdict(int)
        all_nodes = set(graph.keys())

        # Add all referenced nodes to all_nodes
        for node in graph:
            for dependency in graph[node]:
                all_nodes.add(dependency)

        # Calculate in-degrees for all nodes
        for node in all_nodes:
            in_degree[node] = 0  # Initialize

        for node in graph:
            for _dependency in graph[node]:
                in_degree[node] += 1

        # Initialize queue with nodes that have no dependencies
        queue = deque([node for node in all_nodes if in_degree[node] == 0])
        result = []

        while queue:
            node = queue.popleft()
            result.append(node)

            # Reduce in-degree for nodes that depend on this node
            for dependent in graph:
                if node in graph[dependent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        return result

    def _detect_circular_dependencies(
        self, graph: Dict[str, Set[str]]
    ) -> Optional[List[str]]:
        """Detect circular dependencies using DFS.

        Args:
            graph: Dependency graph

        Returns:
            List representing the circular dependency path, or None if no cycles
        """
        visited = set()
        rec_stack = set()

        def dfs(node: str, path: List[str]) -> Optional[List[str]]:
            if node in rec_stack:
                # Found cycle - return the cycle path
                cycle_start = path.index(node)
                return path[cycle_start:]

            if node in visited:
                return None

            visited.add(node)
            rec_stack.add(node)

            for dependency in graph.get(node, set()):
                cycle = dfs(dependency, path + [dependency])
                if cycle:
                    return cycle

            rec_stack.remove(node)
            return None

        for node in graph:
            if node not in visited:
                cycle = dfs(node, [node])
                if cycle:
                    return cycle

        return None

    def _resolve_key_path(
        self,
        key_path: str,
        resolved_config: Dict[str, Any],
        original_config: Dict[str, Any],
    ) -> None:
        """Resolve a specific key path in the configuration.

        Args:
            key_path: Dot-separated key path (e.g., 'project.name')
            resolved_config: Configuration being resolved
            original_config: Original configuration for reference
        """
        if key_path in self.resolution_cache:
            return

        if len(self.resolution_stack) >= self.max_depth:
            raise MaxRecursionError(self.max_depth, key_path)

        # Get the value to resolve
        try:
            value = self._get_nested_value(resolved_config, key_path)
        except KeyError:
            # Key might not exist in config, skip resolution
            return

        self.resolution_stack.append(key_path)

        try:
            resolved_value = self._resolve_value(value, resolved_config)
            self._set_nested_value(resolved_config, key_path, resolved_value)
            self.resolution_cache[key_path] = resolved_value
        finally:
            self.resolution_stack.pop()

    def _resolve_value(self, value: Any, resolved_config: Dict[str, Any]) -> Any:
        """Resolve a single value with its references.

        Args:
            value: Value to resolve
            resolved_config: Current state of resolved configuration

        Returns:
            Resolved value
        """
        if isinstance(value, dict):
            # Recursively resolve dictionary values
            result = {}
            for k, v in value.items():
                result[k] = self._resolve_value(v, resolved_config)
            return result
        elif isinstance(value, list):
            # Recursively resolve list items
            return [self._resolve_value(item, resolved_config) for item in value]
        elif not isinstance(value, str):
            return value

        references = self._detect_references(value)
        if not references:
            return value

        # Check if this is a pure reference (no additional text or filters)
        pure_reference_match = re.match(
            r"^\s*\{\{\s*values\.([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*\}\}\s*$",
            value,
        )
        if pure_reference_match:
            ref_path = pure_reference_match.group(1).strip()
            try:
                ref_value = self._get_nested_value(resolved_config, ref_path)
                # For pure references, preserve the original type
                return ref_value
            except KeyError as e:
                raise ReferenceResolutionError(f"values.{ref_path}") from e

        # For string interpolation or templates with filters, render as template
        try:
            template = self.jinja_env.from_string(value)
            return template.render(values=resolved_config)
        except UndefinedError as e:
            # Extract the undefined variable name
            undefined_var = str(e).split("'")[1] if "'" in str(e) else "unknown"
            raise ReferenceResolutionError(undefined_var) from e
        except TemplateError as e:
            raise TemplateSyntaxError(value, e) from e

    def _get_nested_value(self, config: Dict[str, Any], key_path: str) -> Any:
        """Get a nested value from configuration using dot notation.

        Args:
            config: Configuration dictionary
            key_path: Dot-separated key path

        Returns:
            Value at the specified path

        Raises:
            KeyError: If path does not exist
        """
        keys = key_path.split(".")
        current = config

        for key in keys:
            if not isinstance(current, dict) or key not in current:
                raise KeyError(f"Key path '{key_path}' not found")
            current = current[key]

        return current

    def _set_nested_value(
        self, config: Dict[str, Any], key_path: str, value: Any
    ) -> None:
        """Set a nested value in configuration using dot notation.

        Args:
            config: Configuration dictionary
            key_path: Dot-separated key path
            value: Value to set
        """
        keys = key_path.split(".")
        current = config

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

    def _deep_copy(self, obj: Any) -> Any:
        """Create a deep copy of an object.

        Args:
            obj: Object to copy

        Returns:
            Deep copy of the object
        """
        if isinstance(obj, dict):
            return {key: self._deep_copy(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._deep_copy(item) for item in obj]
        else:
            return obj
