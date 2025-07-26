# Template Customizer

[![CI](https://github.com/mkuhl/customizer/actions/workflows/ci.yml/badge.svg)](https://github.com/mkuhl/customizer/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful tool for customizing project templates using comment-based markers while keeping templates fully functional and compileable.

## Quick Start

**Standalone script installation:**

```bash
# Download and install the latest version
curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer -o customizer
chmod +x customizer
sudo mv customizer /usr/local/bin/

# Verify installation
customizer --version
```

**Docker usage:**

```bash
# Run with Docker
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run
```

## Usage Examples

### Basic Template Customization

1. **Add markers to your template files:**

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
```

3. **Customize your template:**

```bash
# Preview changes
customizer process --project ./my-template --config ./config.yml --dry-run

# Apply changes
customizer process --project ./my-template --config ./config.yml --yes
```

### Docker Usage

Using Docker requires no local Python installation:

```bash
# Pull the latest image
docker pull ghcr.io/mkuhl/customizer:latest

# Preview changes with auto-detected config
docker run --rm -v "/path/to/template:/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run

# Apply changes
docker run --rm -v "/path/to/template:/workdir" ghcr.io/mkuhl/customizer:latest process --yes

# Use custom configuration file
docker run --rm -v "/path/to/template:/workdir" ghcr.io/mkuhl/customizer:latest process --config custom-config.yml --dry-run

# Generate output to a separate directory
docker run --rm -v "/path/to/template:/workdir" -v "/path/to/output:/output" ghcr.io/mkuhl/customizer:latest process --output /output --yes
```

### Advanced Examples

**Filter files by pattern:**
```bash
# Only process Python and JavaScript files
customizer process --project ./template --config ./config.yml --include "*.py,*.js" --dry-run

# Exclude test files
customizer process --project ./template --config ./config.yml --exclude "*test*,*spec*" --dry-run
```

**Verbose output with warnings:**
```bash
# See detailed processing information and missing value warnings
customizer process --project ./template --config ./config.yml --verbose --dry-run
```

**Batch processing:**
```bash
# Process without interactive prompts
customizer process --project ./template --config ./config.yml --yes
```

## Features

- **Comment-based markers** - Templates remain fully functional and compileable
- **Multi-language support** - Python, JavaScript, TypeScript, YAML, HTML, CSS, Docker, and more
- **Rich CLI output** - Progress bars, colored output, and detailed previews
- **Dry-run mode** - Preview changes before applying
- **Safe processing** - Automatic backups and validation
- **Missing value warnings** - Clear warnings for undefined configuration values
- **Flexible filtering** - Include/exclude patterns for selective processing
- **Docker support** - Pre-built images for deployment and CI/CD integration

## Template Marker Format

Template markers use comment syntax that preserves functionality:

```python
# variable_name = {{ jinja2_expression }}
actual_value = "default_value"
```

**Supported file types and comment syntax:**
- Python/Shell: `# marker = {{ expr }}`
- JavaScript/TypeScript: `// marker = {{ expr }}`
- CSS/SCSS: `/* marker = {{ expr }} */`
- HTML/XML: `<!-- marker = {{ expr }} -->`
- YAML: `# marker = {{ expr }}`
- Dockerfile: `# marker = {{ expr }}`

The tool will:
1. Find the comment line with the marker
2. Render the Jinja2 expression using your config values
3. Replace the following line with the rendered result
4. Preserve the comment line unchanged

## Configuration

Configuration files support both YAML and JSON formats with nested structure:

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
  
docker:
  registry: "ghcr.io"
  image_name: "myapp"
```

Access nested values in templates using dot notation:

```python
# db_host = {{ values.database.host | quote }}
db_host = "localhost"

# app_name = {{ values.project.name | quote }}
app_name = "MyApp"

# port = {{ values.database.port }}
port = 5432

# registry = {{ values.docker.registry | quote }}
registry = "ghcr.io"
```

## Missing Values Handling

Template Customizer gracefully handles missing configuration values:

```bash
⚠ Warning: docker-compose.yml has 3 missing values:
  Line 5: web_image - Missing value 'values.docker.web_image': 'dict object' has no attribute 'docker'
  Line 8: api_port - Missing value 'values.docker.api_port': 'dict object' has no attribute 'docker'
  Line 12: debug_mode - Missing value 'values.environment.debug': 'dict object' has no attribute 'environment'

✓ Found 7 changes in 4 files
ℹ Processed 2 files with warnings
```

Files with missing values are still copied to the output directory, allowing you to incrementally build your configuration.

## Documentation

- **[Usage Guide](docs/USAGE.md)** - Detailed examples and advanced usage
- **[Development Guide](docs/DEVELOPMENT.md)** - Contributing and development setup
- **[API Documentation](docs/)** - Complete API reference

## Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/mkuhl/customizer/issues)
- **Discussions**: For questions and community support
- **Examples**: Check the `examples/` directory for template samples

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

Template Customizer uses comment-based markers that preserve your template's functionality, unlike traditional templating tools that use placeholder variables and break compilation. Your templates remain fully functional during development and can be customized without breaking the build process.