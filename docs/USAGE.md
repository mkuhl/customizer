# Template Customizer - Usage Examples

## Quick Start

### 🚀 One-Liner Installation (Easiest!)

The easiest way to install Template Customizer (~100ms startup):

```bash
# Install with one command (to /usr/local/bin)
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh

# Install to custom directory (no sudo needed)
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh -s -- --dir ~/.local/bin

# Verify installation
customizer --version
```

### 💾 Manual Installation

If you prefer manual installation:

```bash
# Download and extract the native binary
curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer-linux-x64.tar.gz | tar xz

# Make it executable and move to PATH
chmod +x customizer
sudo mv customizer /usr/local/bin

# Show help
./customizer --help

# Show version information
./customizer version

# Show supported file types
./customizer info

# Preview changes (dry run)
./customizer process --project ./examples/test-project --config ./examples/config.yml --dry-run

# Apply changes
./customizer process --project ./examples/test-project --config ./examples/config.yml

# Auto-detect config file in project root
./customizer process --project ./examples/test-project --dry-run

# Apply changes without confirmation prompt (for CI/batch)
./customizer process --project ./examples/test-project --yes
```

### 🐳 Docker Usage

For cross-platform compatibility or when native binary isn't available:

```bash
# Download the Docker wrapper script
curl -L -o run-docker-customizer.sh https://github.com/mkuhl/customizer/releases/latest/download/run-docker-customizer.sh
chmod +x run-docker-customizer.sh

# Basic usage (equivalent to native binary)
./run-docker-customizer.sh process --project ./examples/test-project --config ./examples/config.yml --dry-run
```

📖 **[Complete Docker Documentation](DOCKER.md)** - Detailed Docker usage, CI/CD integration, and advanced examples

## Current Status ✅

**Phase 1 Complete** - Foundation & Project Setup is fully implemented and tested:

- ✅ **Rich CLI Interface** with beautiful progress bars and colored output
- ✅ **Multi-language Support** for Python, JavaScript, YAML, CSS, HTML, and more
- ✅ **Template Marker Detection** using comment-based markers
- ✅ **Jinja2 Template Rendering** with custom filters
- ✅ **Dry-run Mode** for safe previewing of changes
- ✅ **File Scanning** with include/exclude patterns
- ✅ **Validation** for parameters and templates
- ✅ **🆕 Auto-config Detection** - Finds config files in project root automatically
- ✅ **🆕 Batch Processing** - `--yes` flag for CI/automation workflows
- ✅ **🆕 Version Management** - Semantic versioning with compatibility checking

## Example Output

When you run the dry-run command, you'll see:

```
╭─────────────────────────── 🔧 Template Customizer ───────────────────────────╮
│ 📁 Project: examples/test-project                                            │
│ ⚙️  Config: examples/config.yml                                               │
│ 🏃 Mode: Dry Run (preview)                                                   │
│ 📊 Parameters: 4 top-level keys                                              │
╰──────────────────────────────────────────────────────────────────────────────╯

✓ Found 7 changes in 2 files
ℹ Skipped 1 files

                                Changes Preview                                 
┏━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━┓
┃ File      ┃ Line ┃ Variable      ┃ Old Value           ┃ New Value           ┃
┡━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━┩
│ app.js    │    4 │ appName       │ const appName =     │ const appName =     │
│           │      │               │ 'DefaultApp';       │ "AwesomeApp"        │
│ config.py │    4 │ app_name      │ app_name =          │ app_name =          │
│           │      │               │ "DefaultApp"        │ "AwesomeApp"        │
└───────────┴──────┴───────────────┴─────────────────────┴─────────────────────┘
```

## Example Files

### Template Markers in Python (`config.py`):
```python
# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"

# version = {{ values.project.version | quote }}  
version = "0.1.0"
```

### Template Markers in JavaScript (`app.js`):
```javascript
// appName = {{ values.project.name | quote }}
const appName = 'DefaultApp';

// apiUrl = {{ values.api.base_url | quote }}
const apiUrl = 'http://localhost:3000';
```

### Configuration File (`config.yml`):
```yaml
project:
  name: "AwesomeApp"
  version: "2.1.0"

api:
  base_url: "https://api.awesomeapp.com"

features:
  debug: false
  metrics: true
```

## Next Steps

Ready to continue with **Phase 2: Comment Parser Engine** to enhance:
- More robust comment parsing
- Better template validation
- Enhanced error handling
- More comprehensive testing

## New Features in Detail

### 🔍 Auto-Config Detection
When you don't specify a `--config` file, the tool automatically looks for configuration files in the project root:

```bash
./customizer process --project ./my-template --dry-run
# Output: ℹ Using config file: config.yml
```

**Supported config file names (in priority order):**
- `config.yml`, `config.yaml`
- `template-config.yml`, `template-config.yaml` 
- `customizer-config.yml`, `customizer-config.yaml`
- `config.json`, `template-config.json`, `customizer-config.json`

### 🤖 Batch Processing
Use the `--yes` flag to skip confirmation prompts, perfect for CI/CD pipelines:

```bash
./customizer process --project ./my-template --yes
# Applies changes immediately without asking "Apply these changes? [y/N]"
```

### 🏷️ Version Management
The template customizer includes comprehensive version management features:

```bash
# Show detailed version information
./customizer version
```

**Version Features:**
- **Semantic Versioning** - Follows semver.org specification (MAJOR.MINOR.PATCH)
- **Version Compatibility Checking** - Warns when config files were created for different major versions
- **Dynamic Versioning** - Version information is centralized in `__init__.py`
- **Rich Version Display** - Shows version, environment, and dependencies

**Configuration Version Compatibility:**
You can specify version requirements in your configuration files:

```yaml
# config.yml
customizer_version: "0.1.0"  # or tool_version, or version
project:
  name: "MyApp"
```

If there's a major version mismatch, you'll see a warning:
```
⚠️  Warning: Configuration was created for version 1.0.0 but you're using version 2.0.0. There may be compatibility issues.
Continue anyway? [y/N]
```

The foundation is solid and working perfectly! 🚀