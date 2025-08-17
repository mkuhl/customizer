"""Command line interface for template customizer."""

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from . import __version__
from .core.external_replacements import ExternalReplacementConfig
from .core.parser import CommentParser
from .core.processor import ParameterLoader, TemplateProcessor
from .core.replacers import JSONReplacer, MarkdownReplacer
from .core.scanner import FileScanner
from .core.writer import FileChange, FileWriter
from .utils.file_types import FileTypeDetector
from .utils.validation import ParameterValidator, ProjectValidator
from .utils.version import get_version_info
from .utils.version_bump import VersionCompatibilityChecker

# Initialize rich console for colored output
console = Console()


@click.group()
@click.version_option(version=__version__, prog_name="template-customizer")
@click.option(
    "--project",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    default=None,
    help="Path to project template directory (global option)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    default=None,
    help="Path to configuration file (global option)",
)
@click.pass_context
def main(ctx, project, config):
    """Template Customizer - Process templates using comment-based markers.

    A tool for customizing project templates while keeping them fully functional.
    Uses comment markers like '# variable = {{ expression }}' to identify
    customization points in source code.

    NEW in v0.4.0: Self-referencing configuration values let you build complex
    configurations from simpler values using {{ values.path.to.value }} syntax.

    Examples:
      # Basic usage
      customizer process --project ./template --config ./config.yml --dry-run

      # Self-referencing config example:
      project:
        name: "my-app"
        version: "1.0.0"
      docker:
        image: "{{ values.project.name }}:{{ values.project.version }}"

    See 'customizer process --help' for detailed usage information.
    """
    # Store global options in context
    ctx.ensure_object(dict)
    ctx.obj["project"] = project
    ctx.obj["config"] = config


@main.command()
@click.option(
    "--project",
    "-p",
    type=click.Path(exists=True, file_okay=False, dir_okay=True, path_type=Path),
    required=False,
    help="Path to project template directory (overrides global)",
)
@click.option(
    "--config",
    "-c",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, path_type=Path),
    required=False,
    help="Path to configuration file (overrides global)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    help="Output directory (default: modify in place)",
)
@click.option(
    "--include", multiple=True, help="File patterns to include (e.g., *.py, *.js)"
)
@click.option("--exclude", multiple=True, help="Additional file patterns to exclude")
@click.option(
    "--dry-run", "-d", is_flag=True, help="Preview changes without modifying files"
)
@click.option(
    "--verbose", "-v", is_flag=True, help="Show detailed processing information"
)
@click.option(
    "--yes",
    "-y",
    is_flag=True,
    help="Automatically apply changes without confirmation prompt",
)
@click.option(
    "--no-resolve-refs",
    is_flag=True,
    help="Disable resolution of self-references in configuration files",
)
@click.pass_context
def process(
    ctx,
    project: Optional[Path],
    config: Optional[Path],
    output: Optional[Path],
    include: tuple,
    exclude: tuple,
    dry_run: bool,
    verbose: bool,
    yes: bool,
    no_resolve_refs: bool,
):
    """Process template markers in project files.

    This command scans the project directory for files containing template
    markers in comments and replaces the following lines with rendered values
    from the configuration file.

    Template markers use comment syntax: # variable = {{ values.expression }}

    NEW in v0.4.0: Self-referencing configuration values allow building complex
    configurations from simpler values.

    Examples:

    \b
    # Basic processing
    customizer process --project ./template --config ./config.yml --dry-run

    \b
    # Apply changes without confirmation
    customizer process --project ./template --config ./config.yml --yes

    \b
    # Verbose mode with self-reference resolution details
    customizer process --project ./template --config ./config.yml --verbose --dry-run

    \b
    # Disable self-reference resolution (compatibility mode)
    customizer process --project ./template --config ./config.yml --no-resolve-refs

    \b
    # Filter specific file types
    customizer process --include "*.py,*.js,*.yml" --exclude "*test*" --dry-run

    \b
    # Self-referencing configuration example:
    # config.yml:
    project:
      name: "my-microservice"
      version: "1.2.0"
      environment: "production"
    docker:
      registry: "ghcr.io/company"
      image: "{{ values.docker.registry }}/{{ values.project.name }}:v1.0"
    database:
      name: "{{ values.project.name | replace('-', '_') }}_db"
      host: "{{ values.project.name }}-cluster.amazonaws.com"

    \b
    # Template file example (app.py):
    # app_name = {{ values.project.name | quote }}
    app_name = "default-app"

    # docker_image = {{ values.docker.image | quote }}
    docker_image = "default:latest"
    """
    try:
        # Use global options if local ones aren't provided
        if project is None:
            project = ctx.obj.get("project")
        if config is None:
            config = ctx.obj.get("config")

        # Validate project is provided
        if project is None:
            console.print("[red]Error:[/red] Project directory not specified")
            console.print("Use --project option globally or with process command")
            sys.exit(1)

        # Auto-detect config file if not provided
        if config is None:
            config = _find_config_file(project, verbose)
            if config is None:
                console.print(
                    "[red]Error:[/red] No configuration file specified and "
                    "none found in project root."
                )
                console.print(
                    "Expected files: config.yml, config.yaml, "
                    "template-config.yml, template-config.yaml, "
                    "customizer-config.yml, customizer-config.yaml"
                )
                sys.exit(1)

        # Initialize components
        validator = ProjectValidator()
        param_validator = ParameterValidator()

        # Validate inputs
        if verbose:
            console.print("[blue]Validating inputs...[/blue]")

        project_errors = validator.validate_project_path(project)
        config_errors = validator.validate_config_file(config)

        if project_errors or config_errors:
            for error in project_errors + config_errors:
                console.print(f"[red]Error:[/red] {error}")
            sys.exit(1)

        # Load configuration
        if verbose:
            console.print(f"[blue]Loading configuration from {config}...[/blue]")

        param_loader = ParameterLoader(
            config, resolve_references=not no_resolve_refs, verbose=verbose
        )
        try:
            parameters = param_loader.load()
        except Exception as e:
            console.print(f"[red]Error loading configuration:[/red] {e}")
            sys.exit(1)

        # Check version compatibility
        try:
            current_version, _ = get_version_info()
            is_compatible, warning = (
                VersionCompatibilityChecker.check_config_compatibility(
                    config, current_version
                )
            )
            if not is_compatible and warning:
                console.print(f"[yellow]Warning:[/yellow] {warning}")
                if not yes and not click.confirm("Continue anyway?"):
                    console.print("[yellow]Operation cancelled by user[/yellow]")
                    sys.exit(1)
        except Exception:
            # If version checking fails, continue silently
            pass

        # Validate parameters
        param_errors = param_validator.validate_parameters(parameters)
        if param_errors:
            for error in param_errors:
                console.print(f"[red]Configuration error:[/red] {error}")
            sys.exit(1)

        # Handle output directory
        if output:
            if not dry_run:
                if output.exists() and any(output.iterdir()):
                    if not yes and not click.confirm(
                        f"Output directory {output} is not empty. Continue?"
                    ):
                        console.print("[yellow]Operation cancelled by user[/yellow]")
                        sys.exit(1)
                else:
                    output.mkdir(parents=True, exist_ok=True)

        # Initialize processors
        scanner = FileScanner(
            project_path=project,
            include_patterns=list(include) if include else None,
            exclude_patterns=list(exclude) if exclude else None,
        )

        parser = CommentParser()
        processor = TemplateProcessor(parameters)
        writer = FileWriter(backup_enabled=not dry_run)
        file_detector = FileTypeDetector()

        # Show configuration summary
        _show_processing_summary(
            project, config, parameters, dry_run, include, exclude, output
        )

        # Process files
        all_changes = []
        processed_files = 0
        skipped_files = 0
        files_to_copy = set()  # Track all files that need to be copied

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True,
        ) as progress:
            scan_task = progress.add_task("Scanning files...", total=None)

            files_to_process = list(scanner.scan())
            progress.update(
                scan_task, description=f"Found {len(files_to_process)} files to scan"
            )

            process_task = progress.add_task(
                "Processing files...", total=len(files_to_process)
            )

            for file_path in files_to_process:
                progress.update(
                    process_task, description=f"Processing {file_path.name}"
                )

                # Check if file type is supported
                if not file_detector.is_supported_file(file_path):
                    skipped_files += 1
                    if verbose:
                        console.print(
                            f"[yellow]Skipped:[/yellow] {file_path} "
                            f"(unsupported file type)"
                        )
                    progress.advance(process_task)
                    continue

                # Parse template markers
                try:
                    markers = parser.parse_file(file_path)
                except Exception as e:
                    console.print(f"[red]Error parsing {file_path}:[/red] {e}")
                    progress.advance(process_task)
                    continue

                if not markers:
                    skipped_files += 1
                    if verbose:
                        console.print(
                            f"[yellow]Skipped:[/yellow] {file_path} "
                            f"(no template markers)"
                        )

                    # If output directory is specified, track file for copying
                    if output:
                        files_to_copy.add(file_path)

                    progress.advance(process_task)
                    continue

                # Process markers
                try:
                    result = processor.process_markers(markers)
                    markers_and_values, marker_errors = result

                    # Display warnings for missing markers
                    if marker_errors:
                        console.print(
                            f"[yellow]⚠ Warning:[/yellow] {file_path.name} has "
                            f"{len(marker_errors)} missing values:"
                        )
                        for marker, error_msg in marker_errors:
                            console.print(
                                f"  [yellow]Line {marker.line_number + 1}:[/yellow] "
                                f"{marker.variable_name} - {error_msg}"
                            )

                    # Determine target file path
                    if output:
                        # Calculate relative path from project root
                        rel_path = file_path.relative_to(project)
                        target_path = output / rel_path
                    else:
                        target_path = file_path

                    changes = writer.prepare_changes(file_path, markers_and_values)

                    if changes:
                        # Update changes to use target path if output directory
                        # is specified
                        if output:
                            changes = [
                                FileChange(
                                    file_path=target_path,
                                    line_number=c.line_number,
                                    old_content=c.old_content,
                                    new_content=c.new_content,
                                    marker=c.marker,
                                )
                                for c in changes
                            ]

                        all_changes.extend(changes)
                        processed_files += 1

                        # Track file for copying
                        if output:
                            files_to_copy.add(file_path)

                        if verbose:
                            console.print(
                                f"[green]Processed:[/green] {file_path} "
                                f"({len(changes)} changes)"
                            )
                    else:
                        # No changes but file has markers (possibly all failed)
                        if markers_and_values or marker_errors:
                            processed_files += 1
                            if verbose:
                                console.print(
                                    f"[yellow]Processed:[/yellow] {file_path} "
                                    f"(0 changes, {len(marker_errors)} errors)"
                                )

                            # Track file for copying
                            if output:
                                files_to_copy.add(file_path)

                except Exception as e:
                    console.print(f"[red]Error processing {file_path}:[/red] {e}")

                progress.advance(process_task)

        # Process external replacements if configured
        ext_config = ExternalReplacementConfig(parameters)
        external_changes = []
        external_processed = 0

        if ext_config.has_replacements():
            console.print("\n[blue]Processing external replacements...[/blue]")

            # Process JSON replacements
            json_replacements = ext_config.get_json_replacements()
            if json_replacements:
                json_replacer = JSONReplacer(parameters)
                for file_str, rules in json_replacements.items():
                    file_path = project / file_str
                    if file_path.exists():
                        try:
                            # Read original content for preview
                            original_content = file_path.read_text()

                            # Get replaced content
                            new_content = json_replacer.replace(file_path, rules)

                            if original_content != new_content:
                                external_processed += 1

                                # For dry-run, just show what would change
                                if verbose or dry_run:
                                    msg = f"[green]External:[/green] {file_str} (JSON)"
                                    console.print(msg)
                                    for jsonpath, _ in rules.items():
                                        msg2 = f"  [blue]JSONPath:[/blue] {jsonpath}"
                                        console.print(msg2)

                                # Store change for application
                                if not dry_run:
                                    external_changes.append((file_path, new_content))
                        except Exception as e:
                            err_msg = f"[red]Error processing {file_str}:[/red] {e}"
                            console.print(err_msg)
                    else:
                        warn = (
                            f"[yellow]Warning:[/yellow] " f"File not found: {file_str}"
                        )
                        console.print(warn)

            # Process Markdown replacements
            md_replacements = ext_config.get_markdown_replacements()
            if md_replacements:
                md_replacer = MarkdownReplacer(parameters)
                for file_str, rules in md_replacements.items():
                    file_path = project / file_str
                    if file_path.exists():
                        try:
                            # Read original content
                            original_content = file_path.read_text()

                            # Get replaced content
                            new_content = md_replacer.replace(file_path, rules)

                            if original_content != new_content:
                                external_processed += 1

                                # For dry-run, just show what would change
                                if verbose or dry_run:
                                    msg = (
                                        f"[green]External:[/green] "
                                        f"{file_str} (Markdown)"
                                    )
                                    console.print(msg)
                                    for pattern, _ in rules.items():
                                        pat_msg = f"  [blue]Pattern:[/blue] {pattern}"
                                        console.print(pat_msg)

                                # Store change for application
                                if not dry_run:
                                    external_changes.append((file_path, new_content))
                        except Exception as e:
                            err_msg = f"[red]Error processing {file_str}:[/red] {e}"
                            console.print(err_msg)
                    else:
                        warn = (
                            f"[yellow]Warning:[/yellow] " f"File not found: {file_str}"
                        )
                        console.print(warn)

            if external_processed > 0:
                msg = (
                    f"[green]✓[/green] Processed {external_processed} "
                    f"files with external replacements"
                )
                console.print(msg)

        # Show results (including external replacements count)
        total_processed = processed_files + external_processed
        _show_results(all_changes, total_processed, skipped_files, dry_run, verbose)

        # Apply changes if not dry run
        if not dry_run and (
            all_changes or external_changes or (output and files_to_copy)
        ):
            should_apply = yes or click.confirm("Apply these changes?")
            if should_apply:
                # If output directory is specified, copy files first
                if output:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                        transient=True,
                    ) as progress:
                        progress.add_task(
                            "Copying files to output directory...", total=None
                        )

                        # Copy all tracked files to output directory
                        for source_file in files_to_copy:
                            rel_path = source_file.relative_to(project)
                            target_file = output / rel_path

                            # Create parent directories
                            target_file.parent.mkdir(parents=True, exist_ok=True)

                            # Copy file
                            import shutil

                            shutil.copy2(source_file, target_file)

                            if verbose:
                                console.print(f"[blue]Copied:[/blue] {rel_path}")

                success = writer.apply_changes(all_changes, dry_run=False)

                # Apply external replacements
                if success and external_changes:
                    for file_path, new_content in external_changes:
                        try:
                            # Create backup if needed
                            if writer.backup_enabled:
                                writer.create_backup(file_path)

                            # Write new content
                            file_path.write_text(new_content)

                            if verbose:
                                msg = (
                                    f"[green]Applied:[/green] "
                                    f"{file_path.name} (external)"
                                )
                                console.print(msg)
                        except Exception as e:
                            err = (
                                f"[red]Failed to apply external "
                                f"changes to {file_path}:[/red] {e}"
                            )
                            console.print(err)
                            success = False

                if success:
                    console.print("[green]✓ All changes applied successfully![/green]")
                else:
                    console.print("[red]✗ Some changes failed to apply[/red]")
                    sys.exit(1)
            else:
                console.print("[yellow]Changes cancelled by user[/yellow]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected error:[/red] {e}")
        if verbose:
            import traceback

            console.print(traceback.format_exc())
        sys.exit(1)


def _show_processing_summary(
    project: Path,
    config: Path,
    parameters: dict,
    dry_run: bool,
    include: tuple,
    exclude: tuple,
    output: Optional[Path] = None,
):
    """Show processing configuration summary."""

    panel_content = []
    panel_content.append(f"📁 Project: {project}")
    panel_content.append(f"⚙️  Config: {config}")
    panel_content.append(
        f"🏃 Mode: {'Dry Run (preview)' if dry_run else 'Live (will modify files)'}"
    )

    if output:
        panel_content.append(f"📂 Output: {output}")

    if include:
        panel_content.append(f"📋 Include: {', '.join(include)}")

    if exclude:
        panel_content.append(f"🚫 Exclude: {', '.join(exclude)}")

    panel_content.append(f"📊 Parameters: {len(parameters)} top-level keys")

    console.print(
        Panel(
            "\n".join(panel_content),
            title="🔧 Template Customizer",
            border_style="blue",
        )
    )


def _show_results(changes, processed_files, skipped_files, dry_run, verbose):
    """Show processing results."""

    if not changes:
        console.print("\n[yellow]No changes to apply[/yellow]")
        return

    # Summary
    console.print(
        f"\n[green]✓ Found {len(changes)} changes in {processed_files} files[/green]"
    )
    console.print(f"[blue]ℹ Skipped {skipped_files} files[/blue]")

    if verbose or dry_run:
        # Show detailed changes
        table = Table(title="Changes to Apply" if not dry_run else "Changes Preview")
        table.add_column("File", style="cyan")
        table.add_column("Line", justify="right", style="magenta")
        table.add_column("Variable", style="green")
        table.add_column("Old Value", style="red")
        table.add_column("New Value", style="green")

        for change in changes[:20]:  # Limit to first 20 for readability
            table.add_row(
                str(change.file_path.name),
                str(change.line_number + 1),  # 1-based line numbers for display
                change.marker.variable_name,
                (
                    change.old_content[:40] + "..."
                    if len(change.old_content) > 40
                    else change.old_content
                ),
                (
                    change.new_content[:40] + "..."
                    if len(change.new_content) > 40
                    else change.new_content
                ),
            )

        console.print(table)

        if len(changes) > 20:
            console.print(f"[blue]... and {len(changes) - 20} more changes[/blue]")


@main.command()
@click.pass_context
def info(ctx):
    """Show information about supported file types and syntax."""

    # Display version information
    console.print(f"[blue]Template Customizer v{__version__}[/blue]")
    console.print()

    # Display global options if set
    project = ctx.obj.get("project")
    config = ctx.obj.get("config")

    if project or config:
        console.print("[bold]Global Options:[/bold]")
        if project:
            console.print(f"  Project directory: {project}")
        if config:
            console.print(f"  Configuration file: {config}")
        console.print()

    detector = FileTypeDetector()

    console.print(
        Panel(
            "Template Customizer supports comment-based template markers in "
            "various file types.",
            title="📋 Supported File Types",
            border_style="green",
        )
    )

    # Group extensions by comment type
    comment_types = {}
    for ext, comment_type in detector.EXTENSION_MAP.items():
        if comment_type not in comment_types:
            comment_types[comment_type] = []
        comment_types[comment_type].append(ext)

    for comment_type, extensions in comment_types.items():
        syntax_info = detector.get_comment_syntax_info(comment_type)

        console.print(
            f"\n[bold blue]{syntax_info.get('description', comment_type)}[/bold blue]"
        )
        console.print(f"[green]Syntax:[/green] {syntax_info.get('example', 'N/A')}")
        console.print(f"[cyan]Extensions:[/cyan] {', '.join(sorted(extensions))}")

    # Add information about self-referencing configuration values
    console.print(
        Panel(
            "[bold green]NEW in v0.4.0:[/bold green] Self-Referencing Values\n\n"
            "Build complex configurations from simpler values using references:\n\n"
            "[blue]Example:[/blue]\n"
            "project:\n"
            '  name: "my-app"\n'
            '  version: "1.0.0"\n'
            "docker:\n"
            '  registry: "ghcr.io/company"\n'
            '  image: "{{ values.docker.registry }}/{{ values.project.name }}:v1.0"\n\n'
            "[green]Features:[/green]\n"
            "• Reference any value: {{ values.path.to.value }}\n"
            "• Chain references: {{ values.computed.base_url }}/api\n"
            "• Use Jinja2 filters: {{ values.name | lower | replace('-', '_') }}\n"
            "• Type preservation for pure references\n"
            "• Circular dependency detection\n"
            "• Order-independent resolution",
            title="🔗 Self-Referencing Values",
            border_style="cyan",
        )
    )

    # Add external replacements information
    console.print(
        Panel(
            "[bold green]External Replacements:[/bold green] JSON & Markdown\n\n"
            "For files that don't support comments, define replacements:\n\n"
            "[blue]JSON Example:[/blue]\n"
            "replacements:\n"
            "  json:\n"
            '    "package.json":\n'
            '      "$.name": "{{ values.project.name }}"\n'
            '      "$.version": "{{ values.project.version }}"\n\n'
            "[blue]Markdown Example:[/blue]\n"
            "replacements:\n"
            "  markdown:\n"
            '    "README.md":\n'
            '      "pattern: # Old Title": "# {{ values.project.name | title }}"\n'
            '      "literal: [PLACEHOLDER]": "{{ values.project.description }}"',
            title="📄 External Replacements",
            border_style="magenta",
        )
    )


@main.command()
def version():
    """Show detailed version information."""
    try:
        version_string, version_obj = get_version_info()

        console.print(
            Panel(
                f"[bold green]Template Customizer[/bold green]\n"
                f"[blue]Version:[/blue] {version_string}\n"
                f"[blue]Major:[/blue] {version_obj.major}\n"
                f"[blue]Minor:[/blue] {version_obj.minor}\n"
                f"[blue]Patch:[/blue] {version_obj.patch}"
                + (
                    f"\n[blue]Prerelease:[/blue] {version_obj.prerelease}"
                    if version_obj.prerelease
                    else ""
                )
                + (
                    f"\n[blue]Build:[/blue] {version_obj.build}"
                    if version_obj.build
                    else ""
                ),
                title="🏷️ Version Information",
                border_style="green",
            )
        )

        # Show Python and dependencies info
        import platform
        import sys

        console.print(
            Panel(
                f"[blue]Python:[/blue] {sys.version.split()[0]} "
                f"({platform.python_implementation()})\n"
                f"[blue]Platform:[/blue] {platform.platform()}\n"
                f"[blue]Architecture:[/blue] {platform.machine()}",
                title="🐍 Environment",
                border_style="blue",
            )
        )

        # Show core dependencies
        deps_info = []
        try:
            import jinja2

            deps_info.append(f"[blue]Jinja2:[/blue] {jinja2.__version__}")
        except ImportError:
            deps_info.append("[red]Jinja2:[/red] Not installed")

        try:
            import yaml

            deps_info.append(f"[blue]PyYAML:[/blue] {yaml.__version__}")
        except ImportError:
            deps_info.append("[red]PyYAML:[/red] Not installed")

        try:
            import click

            deps_info.append(f"[blue]Click:[/blue] {click.__version__}")
        except ImportError:
            deps_info.append("[red]Click:[/red] Not installed")

        try:
            import rich

            deps_info.append(f"[blue]Rich:[/blue] {rich.__version__}")
        except ImportError:
            deps_info.append("[red]Rich:[/red] Not installed")

        if deps_info:
            console.print(
                Panel(
                    "\n".join(deps_info),
                    title="📦 Dependencies",
                    border_style="cyan",
                )
            )

    except Exception as e:
        console.print(f"[red]Error getting version information:[/red] {e}")


def _find_config_file(project_path: Path, verbose: bool = False) -> Optional[Path]:
    """Find configuration file in project root directory.

    Args:
        project_path: Path to project directory
        verbose: Whether to show verbose output

    Returns:
        Path to config file if found, None otherwise
    """
    # Common config file names to look for
    config_names = [
        "config.yml",
        "config.yaml",
        "template-config.yml",
        "template-config.yaml",
        "customizer-config.yml",
        "customizer-config.yaml",
        "config.json",
        "template-config.json",
        "customizer-config.json",
    ]

    for config_name in config_names:
        config_path = project_path / config_name
        if config_path.exists() and config_path.is_file():
            if verbose:
                console.print(
                    f"[blue]INFO:[/blue] Found configuration file: {config_path}"
                )
            else:
                console.print(f"[blue]ℹ Using config file:[/blue] {config_path.name}")
            return config_path

    return None


if __name__ == "__main__":
    main()
