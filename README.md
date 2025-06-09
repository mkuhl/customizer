# Template Customizer

[![Tests](https://github.com/username/template-customizer/actions/workflows/test.yml/badge.svg)](https://github.com/username/template-customizer/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful tool for customizing project templates using comment-based markers while keeping templates fully functional and compileable.

## Overview

Template Customizer revolutionizes template management by using comment-based markers that preserve your template's functionality. Unlike traditional templating tools that require placeholder variables and break compilation, this tool processes comments to identify customization points and replaces the following lines with rendered values.

## Installation

### Using uv (recommended)
```bash
# Install from PyPI (when published)
uv pip install template-customizer

# Or install in development mode
uv pip install -e .
```

### Using pip
```bash
pip install template-customizer
```

### Development Setup
```bash
# Clone the repository
git clone https://github.com/username/template-customizer.git
cd template-customizer

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"

# Run tests to verify installation
pytest
```

## Quick Start

1. **Add template markers to your template files:**

```python
# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"

# version = {{ values.project.version | quote }}
version = "0.1.0"
```

2. **Create a configuration file:**

```yaml
# config.yml
project:
  name: "MyAwesome App"
  version: "1.2.0"
  description: "Built from template"

api:
  base_url: "https://api.myapp.com"
```

3. **Run the customizer:**

```bash
# Preview changes
template-customizer process --project ./my-template --config ./config.yml --dry-run

# Apply changes
template-customizer process --project ./my-template --config ./config.yml
```

## Features

- **Comment-based markers** - Templates remain functional
- **Multi-language support** - Python, JavaScript, YAML, HTML, CSS, and more
- **Rich CLI output** - Progress bars, colored output, and detailed previews
- **Dry-run mode** - Preview changes before applying
- **Safe processing** - Automatic backups and validation
- **Flexible filtering** - Include/exclude patterns for files

## Supported File Types

- Python (`.py`) - `# marker = {{ expression }}`
- JavaScript/TypeScript (`.js`, `.ts`) - `// marker = {{ expression }}`
- CSS/SCSS (`.css`, `.scss`) - `/* marker = {{ expression }} */`
- HTML/XML (`.html`, `.xml`) - `<!-- marker = {{ expression }} -->`
- YAML (`.yml`, `.yaml`) - `# marker = {{ expression }}`
- And many more...

## Usage

### Command Line Interface

```bash
# Basic usage
template-customizer process -p ./template -c ./config.yml

# With filtering
template-customizer process -p ./template -c ./config.yml \
  --include "*.py,*.js" --exclude "*test*"

# Dry run with verbose output
template-customizer process -p ./template -c ./config.yml --dry-run --verbose

# Show supported file types
template-customizer info
```

### Docker Usage

Run template-customizer via Docker without installing it locally:

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

**Docker Features:**
- No local Python installation required
- Automatic config file detection in template directory
- Interactive confirmation prompts work correctly
- Mount any template directory with `TEMPLATE_DIR` environment variable

## Template Marker Format

Template markers follow this pattern:
```
# variable_name = {{ jinja2_expression }}
actual_value = "default_value"
```

The tool will:
1. Find the comment line with the marker
2. Render the Jinja2 expression using your config values
3. Replace the next line with the rendered result
4. Preserve the comment line unchanged

## Configuration File

Supports both YAML and JSON formats:

```yaml
project:
  name: "MyApp"
  version: "1.0.0"
  description: "My application"

database:
  host: "localhost"
  port: 5432

features:
  auth_enabled: true
  metrics_enabled: false
```

Access nested values in templates:
```python
# db_host = {{ values.database.host | quote }}
db_host = "localhost"

# app_name = {{ values.project.name | quote }}
app_name = "MyApp"
```

## Development

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
# Install development dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linting and formatting
ruff check .
black .

# Type checking
mypy src/
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=template_customizer --cov-report=html

# Run specific test file
pytest tests/test_comment_parser.py -v
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run the test suite (`pytest`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: See [USAGE.md](USAGE.md) for detailed usage examples
- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/username/template-customizer/issues)
- **Development**: See [CLAUDE.md](CLAUDE.md) for development guidelines