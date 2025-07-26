# Development Guide

This guide covers development setup, contributing guidelines, and project architecture for Template Customizer.

## Development Setup

### VS Code Dev Container (Recommended)

This project includes a complete VS Code dev container setup with all tools pre-configured:

```bash
# Open in VS Code with dev container extension installed
code .
# VS Code will prompt to "Reopen in Container"
```

The dev container includes:
- Python 3.12 with uv package manager
- All development dependencies pre-installed
- Claude Code integration for AI-assisted development
- Modern CLI tools (ripgrep, fd, bat, fzf)
- Automatic environment setup

### Manual Development Setup

```bash
# Clone the repository
git clone https://github.com/mkuhl/customizer.git
cd customizer

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests to verify installation
pytest
```

### Alternative Installation Methods

#### Using uv (recommended for development)
```bash
# Install from PyPI (when published)
uv pip install template-customizer

# Or install in development mode
uv pip install -e .
```

#### Using pip
```bash
pip install template-customizer
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=template_customizer --cov-report=html

# Run specific test file
pytest tests/test_comment_parser.py -v

# Run tests with coverage report
pytest --cov=src/template_customizer --cov-report=term-missing -v
```

## Code Quality

```bash
# Run linting
ruff check src/

# Apply auto-fixes
ruff check src/ --fix

# Run formatting
black src/

# Check formatting without changes
black --check src/

# Type checking
mypy src/
```

## Docker Development

### Building Locally

```bash
# Build the Docker image
./scripts/docker-build.sh

# Run with Docker (interactive mode with confirmation prompts)
./scripts/docker-run.sh process --dry-run

# Run with Docker (batch mode, no prompts)
TEMPLATE_DIR=/path/to/your/template ./scripts/docker-run.sh process --yes

# Show help via Docker
./scripts/docker-run.sh --help
```

### Publishing Docker Images

```bash
# Manual publishing to GHCR
./scripts/docker-publish.sh

# Dry run (see what would be published)
./scripts/docker-publish.sh --dry-run
```

## Architecture

### Core Components

```
src/template_customizer/
├── cli.py                 # Click-based CLI entry point
├── core/
│   ├── scanner.py         # File discovery and filtering
│   ├── parser.py          # Comment marker extraction
│   ├── processor.py       # Template rendering and file processing
│   └── writer.py          # Safe file writing with backups
└── utils/
    ├── file_types.py      # File type detection and comment syntax
    ├── validation.py      # Parameter and template validation
    ├── version.py         # Version management
    └── version_bump.py    # Version bumping utilities
```

### Key Technologies

- **CLI Framework**: Click (not argparse)
- **UI Enhancement**: Rich for progress bars, colors, and formatting
- **Template Engine**: Jinja2
- **Config Format**: YAML/JSON support
- **Package Manager**: uv (consistent with parent project)

## CI/CD Pipeline

- **GitHub Actions**: Complete CI/CD pipeline with 5 parallel jobs
- **Quality Gates**: All code must pass ruff linting, black formatting, mypy type checking, and pytest
- **Docker Build**: Automated Docker image building and testing with dynamic versioning
- **Docker Publish**: Automated publishing to GitHub Container Registry (GHCR) at `ghcr.io/mkuhl/customizer`
- **Release Automation**: Automated GitHub Releases with standalone customizer script on version tags
- **Coverage**: Minimum 50% test coverage required (currently 79%+)

### Workflow Triggers

- **Push to master/main/develop**: Runs full CI pipeline
- **Pull Requests to master**: Runs tests and quality checks
- **Version tags (v*.*.**)**: Triggers release automation
- **Manual workflow dispatch**: Can be triggered manually

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Ensure all quality checks pass (`ruff check src/`, `black --check src/`, `mypy src/`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

### Development Workflow

- **Branch Strategy**: Use `feature-*` branches for new development
- **CI Requirements**: All changes must pass CI checks before merging to master
- **Pull Requests**: Required for all changes to master branch
- **Local Testing**: Run `pytest`, `ruff check src/`, `black --check src/`, `mypy src/` before pushing

### Git Commit Guidelines

- Keep commits short and concise
- Single line for trivial changes, max 3 additional lines with details only when necessary
- Do NOT add "co-authored..." comments to any commits
- Only commit when explicitly asked to do so
- NEVER commit to master unless specifically asked to do so

## Release Process

1. Update version in `src/template_customizer/__init__.py`
2. Create git tag with format `v*.*.*` (e.g., `v0.1.4`)
3. Push tag to trigger automated release creation
4. Automated process will:
   - Create GitHub Release
   - Generate standalone customizer script
   - Publish Docker image to GHCR
   - Update documentation

## Project Guidelines

### Framework and Library Documentation

- **ALWAYS use Context7** when working with frameworks, libraries, or external packages
- When implementing features using Click, Rich, Jinja2, or any other dependency, append "use context7" to get the latest documentation
- This ensures code examples and API usage are current and accurate

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
- Real-world validation with example projects

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure you've installed the package in development mode with `uv pip install -e .`
2. **Test failures**: Check that all dependencies are installed with `uv pip install -e ".[dev]"`
3. **Docker build failures**: Ensure Docker is running and you have sufficient disk space
4. **Permission errors**: Check file permissions, especially for SSH keys and Docker socket

### Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/mkuhl/customizer/issues)
- **Discussions**: For questions and community support
- **Development**: See [CLAUDE.md](../CLAUDE.md) for detailed development guidelines