# Template Customizer

[![CI](https://github.com/mkuhl/customizer/actions/workflows/ci.yml/badge.svg)](https://github.com/mkuhl/customizer/actions/workflows/ci.yml)
[![Version](https://img.shields.io/badge/version-0.3.1-blue.svg)](https://github.com/mkuhl/customizer/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ghcr.io-blue.svg)](https://github.com/mkuhl/customizer/pkgs/container/customizer)

A powerful tool for customizing project templates using comment-based markers while keeping templates fully functional and compileable.

## What is Template Customizer?

Template Customizer transforms project templates into customized, ready-to-use projects by replacing marker comments with configuration values. Unlike traditional templating tools that break your code with placeholder variables, Template Customizer uses comments to mark customization points, keeping your templates **fully functional** during development.

## Why Use Template Customizer?

✅ **Templates Stay Functional** - Your template code runs and compiles during development  
✅ **IDE-Friendly** - No syntax errors from placeholder variables  
✅ **Version Control Friendly** - Clean diffs, reviewable code  
✅ **Multi-Language Support** - Works with Python, JavaScript, YAML, Docker, and more  
✅ **Safe Processing** - Dry-run mode, automatic backups, validation  
✅ **Clear Warnings** - Missing configuration values are clearly reported  

## How It Works

**Before** (template file):
```python
# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"

# port = {{ values.server.port }}
port = 3000
```

**Configuration** (config.yml):
```yaml
project:
  name: "MyAwesomeApp"
server:
  port: 8080
```

**After** (customized file):
```python
# app_name = {{ values.project.name | quote }}
app_name = "MyAwesomeApp"

# port = {{ values.server.port }}
port = 8080
```

The comment markers are preserved, and only the values are updated!

## Quick Start

### 🚀 One-Liner Installation (Easiest!)

Install Template Customizer with a single command:

```bash
# Install to /usr/local/bin (requires sudo)
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh

# Install to custom directory (no sudo needed)
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh -s -- --dir ~/.local/bin

# Use immediately (startup time ~100ms)
customizer --version
customizer process --dry-run
```

### 💾 Manual Installation

If you prefer manual installation:

```bash
# Download and extract the native Linux binary
curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer-linux-x64.tar.gz | tar xz

# Move to system path
sudo mv customizer /usr/local/bin/

# Use immediately
customizer --version
customizer process --dry-run
```

### 🐳 Docker Installation

For cross-platform compatibility or when native binary isn't available:

```bash
# Download the Docker wrapper script  
curl -L -o run-docker-customizer.sh https://github.com/mkuhl/customizer/releases/latest/download/run-docker-customizer.sh
chmod +x run-docker-customizer.sh
sudo mv run-docker-customizer.sh /usr/local/bin/

# Verify installation
run-docker-customizer.sh --version
```

📖 **[Complete Docker Documentation](docs/DOCKER.md)** - Detailed Docker usage, CI/CD integration, and troubleshooting

## Installation Comparison

| Method | Startup Time | Size | Requirements | Best For |
|--------|-------------|------|--------------|----------|
| **One-Liner Install** | ~100ms ⚡ | 11MB | Linux x86_64, GLIBC 2.31+ | Easiest setup, recommended for most users |
| **Manual Binary** | ~100ms ⚡ | 11MB | Linux x86_64, GLIBC 2.31+ | CI/CD pipelines, controlled environments |
| **Docker Methods** | 2-3s | N/A | Docker installed | Cross-platform consistency, CI/CD integration |

### System Requirements

**For Native Binary:**
- Linux x86_64 (Ubuntu 20.04+, RHEL 8+, Debian 11+, or compatible)
- GLIBC 2.31 or newer (check with `ldd --version`)

**For Docker Methods:**
- Docker installed and running  
- See [Docker Documentation](docs/DOCKER.md) for detailed requirements

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

For Docker usage examples, see the **[Docker Documentation](docs/DOCKER.md)**.

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

## Common Use Cases

- **🚀 Project Scaffolding** - Initialize new projects from company templates
- **🔧 Environment Configuration** - Deploy same codebase to dev/staging/prod
- **🏢 Multi-Tenant Applications** - Configure for different clients/tenants
- **🐳 Docker Deployments** - Customize compose files for different environments
- **📦 Package Templates** - Create npm/pip packages with correct metadata
- **⚙️ CI/CD Pipelines** - Generate environment-specific configurations

## Features

- **Comment-based markers** - Templates remain fully functional and compileable
- **External replacements** - JSONPath for JSON files, patterns for Markdown (no comments needed!)
- **Multi-language support** - Python, JavaScript, TypeScript, YAML, HTML, CSS, Docker, and more
- **Rich CLI output** - Progress bars, colored output, and detailed previews
- **Dry-run mode** - Preview changes before applying
- **Safe processing** - Automatic backups and validation
- **Missing value warnings** - Clear warnings for undefined configuration values
- **Flexible filtering** - Include/exclude patterns for selective processing
- **Docker support** - [Complete Docker integration](docs/DOCKER.md) for CI/CD and cross-platform deployment

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

## External Replacements (New in v0.3.0)

For files that don't support comments (like JSON) or when you prefer external configuration, Template Customizer supports external replacement definitions in your config file.

### JSON File Replacements

JSON files don't support comments, so use JSONPath expressions in your config:

```yaml
# config.yml
project:
  name: "my-app"
  version: "2.0.0"
  author: "Jane Developer"

replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
      "$.version": "{{ values.project.version }}"
      "$.author": "{{ values.project.author }}"
      "$.scripts.start": "node {{ values.project.name }}.js"
      "$.dependencies.react": "^18.0.0"
      "$.config.port": "{{ values.server.port }}"
      "$.config.debug": true  # Booleans are preserved
```

### Markdown File Replacements

Replace content in Markdown files using patterns:

```yaml
replacements:
  markdown:
    "README.md":
      "pattern: # Old Title": "# {{ values.project.name | title }}"
      "pattern: Version: .*": "Version: {{ values.project.version }}"
      "pattern: Copyright \\(c\\) \\d+": "Copyright (c) 2024"
      "literal: [PLACEHOLDER]": "{{ values.project.description }}"  # Literal string (no regex)
```

### Features

- **JSONPath Support**: Use standard JSONPath expressions to target any value in JSON files
- **Pattern Matching**: Use regex patterns or literal strings for Markdown/text files
- **Type Preservation**: JSON types (strings, numbers, booleans) are automatically preserved
- **Template Rendering**: Full Jinja2 template support in replacement values
- **No Comment Pollution**: Keep your JSON and other files clean without comment markers

### Example

**Before** (package.json):
```json
{
  "name": "template-project",
  "version": "0.0.0",
  "author": "Template Author"
}
```

**After** (with external replacements):
```json
{
  "name": "my-app",
  "version": "2.0.0",
  "author": "Jane Developer"
}
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

## Contributing

We welcome contributions! Please see our [Development Guide](docs/DEVELOPMENT.md) for setup instructions and guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**💡 Key Innovation**: Template Customizer uses comment-based markers that preserve your template's functionality. Unlike traditional templating tools that break compilation with placeholder variables like `${APP_NAME}` or `{{app_name}}`, your templates remain **fully functional** during development. This means:

- ✅ Your IDE won't show syntax errors
- ✅ Your code compiles and runs during template development
- ✅ Your tests pass before and after customization
- ✅ Your templates are maintainable and debuggable

Start using Template Customizer today and make your templates work **for** you, not against you!