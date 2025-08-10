# Template Customizer - Claude Instructions

## Project Context
This is the **Template Customizer** - a standalone Python tool for customizing project templates using comment-based markers. This is now an independent project focused solely on template processing capabilities.

## Key Project Information
- **Language**: Python 3.8+
- **CLI Framework**: Click (not argparse)
- **UI Enhancement**: Rich for progress bars, colors, and formatting
- **Template Engine**: Jinja2
- **Config Format**: YAML/JSON support
- **Package Manager**: Use `uv` (consistent with parent project)

## Core Architecture
```
customizer/
├── src/template_customizer/
│   ├── cli.py                 # Click-based CLI entry point
│   ├── core/
│   │   ├── scanner.py         # File discovery and filtering
│   │   ├── parser.py          # Comment marker extraction
│   │   ├── processor.py       # Template rendering and file processing
│   │   └── writer.py          # Safe file writing with backups
│   └── utils/
│       ├── file_types.py      # File type detection and comment syntax
│       └── validation.py      # Parameter and template validation
└── tests/                     # Comprehensive test suite
```

## Development Guidelines

### CLI Design with Click
- Use Click decorators for commands and options
- Implement rich help formatting
- Support both short and long option forms
`- Use Click's built-in validation where possible
`
### Rich Integration
- Use Rich progress bars for file processing
- Implement colored output for different message types:
  - Green: Success/completion
  - Yellow: Warnings
  - Red: Errors
  - Blue: Information
- Use Rich tables for change summaries
- Implement rich console output for dry-run previews

### Template Marker Format
The tool processes comment-based markers in this format:
```python
# variable_name = {{ jinja2_expression }}
actual_value = "default_value"
```

### File Type Support
Support comment syntax for:
- Python/Shell: `# marker = {{ expr }}`
- JavaScript/TypeScript: `// marker = {{ expr }}`
- CSS: `/* marker = {{ expr }} */`
- HTML/XML: `<!-- marker = {{ expr }} -->`
- YAML: `# marker = {{ expr }}`
- Dockerfile: `# marker = {{ expr }}`

### Safety Requirements
- Always preserve comment lines unchanged
- Implement dry-run mode for preview
- Create file backups before modifications
- Validate Jinja2 syntax before processing
- Handle missing variables gracefully

### Testing Strategy
- Unit tests for each component
- Integration tests with sample projects
- Performance tests for large directories
- Error handling and edge case tests
- Real-world validation with py-ang project

## Command Structure
```bash
# Basic usage with rich output
customizer process --project ./template --config ./config.yml

# Dry run with detailed preview
customizer process --project ./template --config ./config.yml --dry-run

# With filtering and verbose rich output
customizer process --project ./template --config ./config.yml \
  --include "*.py,*.js,*.yml" --exclude "*test*" --verbose
```

## Configuration File Example
```yaml
# customizer-config.yml
project:
  name: "MyAwesome App"
  version: "1.2.0"
  description: "Built from py-ang template"

docker:
  registry: "myregistry.com"
  image_name: "myapp"

api:
  base_url: "https://api.myapp.com"
  version: "v1"
```

## Validation with Parent Project
Use the py-ang project as validation target by:
1. Adding template markers to key files
2. Creating configuration for customization
3. Running customizer and verifying results
4. Ensuring customized project still builds/runs

## Dependencies
- **jinja2**: Template rendering
- **pyyaml**: YAML configuration parsing
- **click**: Modern CLI framework
- **rich**: Beautiful terminal output
- **pathlib**: File system operations (built-in)

## IDE Integration and Tools

### IntelliJ MCP Server
- **IntelliJ MCP Integration**: ✅ Fully configured and operational
- **Preferred Tool Usage**: Always use IntelliJ MCP tools when available for better IDE integration
- **Key MCP Tools to Use**:
  - `mcp__jetbrains__get_file_text_by_path`: Read files (prefer over basic Read tool)
  - `mcp__jetbrains__search_in_files_by_text`: Search codebase (faster than grep)
  - `mcp__jetbrains__list_directory_tree`: Explore project structure
  - `mcp__jetbrains__get_project_problems`: Check for issues/errors
  - `mcp__jetbrains__replace_text_in_file`: Edit files with IDE awareness
  - `mcp__jetbrains__reformat_file`: Apply code formatting
  - `mcp__jetbrains__rename_refactoring`: Safe symbol renaming
  - `mcp__jetbrains__execute_terminal_command`: Run commands in IDE terminal
- **When to Use MCP**: Prefer MCP tools for all file operations, searches, and code analysis when working in the IDE environment
- **Fallback**: Use standard tools only when MCP equivalent is not available

### Framework and Library Documentation
- **ALWAYS use Context7** when working with frameworks, libraries, or external packages
- When implementing features using Click, Rich, Jinja2, or any other dependency, append "use context7" to get the latest documentation
- This ensures code examples and API usage are current and accurate
- Example: "How do I create a progress bar with Rich? use context7"

## Important Notes
- This is a **standalone project** - no dependencies on parent py-ang
- Use `uv` for Python package management
- Focus on user experience with rich output
- Maintain comprehensive test coverage
- Document all rich formatting features

## CI/CD Pipeline
- **GitHub Actions**: ✅ Complete CI/CD pipeline with 6 parallel jobs (test, quality, docker-build, native-linux, docker-publish, release) - **ACTIVE ON MASTER**
- **Quality Gates**: All code must pass ruff linting, black formatting, mypy type checking, and pytest
- **Scope**: Code quality checks limited to `src/` directory only
- **Native Binary Build**: Automated PyInstaller-based Linux x86_64 executable generation with ~100ms startup
- **Docker Build**: Automated Docker image building and testing with dynamic versioning
- **Docker Publish**: Automated publishing to GitHub Container Registry (GHCR) at `ghcr.io/mkuhl/customizer`
- **Release Automation**: Automated GitHub Releases with native binary, Docker wrapper, and install script
- **Coverage**: Minimum 50% test coverage required (currently 79%+)
- **MyPy Configuration**: Pragmatic settings for CI compatibility (some modules excluded temporarily)
- **Status**: ✅ All checks passing on master branch

## Development Workflow
- **Branch Strategy**: Use `feature-*` branches for new development
- **CI Requirements**: All changes must pass CI checks before merging to master
- **Pull Requests**: Required for all changes to master branch
- **Local Testing**: Run `pytest`, `ruff check src/`, `black --check src/`, `mypy src/` before pushing
- **Native Binary Testing**: Use `./scripts/build-native.sh` to test native executable locally
- **Docker Testing**: Use `./scripts/docker-build.sh` to test Docker integration locally
- **Manual Publishing**: Use `./scripts/docker-publish.sh` for manual Docker image publishing to GHCR
- **Release Process**: Update version in `__init__.py` → create git tag `v*.*.*` → automated release with multi-asset distribution

## Git Commits
- Always use the mkuhl and mkuhl@softmachine.at as git user
- Keep them short and concise. Single line for trivial changes, max 3 additional lines with details only when necessary
- Do NOT add "co-authored..." comments to any commits
- Only commit when explicitly asked to do so by the user
- NEVER commit to master unless specifically asked to do so. Changes to master should always be merged from feature branches
- When committing, use simple commit messages without the automated "Generated with Claude Code" footer