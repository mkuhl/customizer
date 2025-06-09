# Template Customizer - Usage Examples

## Quick Start

Use the wrapper script to run the template customizer:

```bash
# Show help
./customize --help

# Show supported file types
./customize info

# Preview changes (dry run)
./customize process --project ./examples/test-project --config ./examples/config.yml --dry-run

# Apply changes
./customize process --project ./examples/test-project --config ./examples/config.yml

# 🆕 NEW: Auto-detect config file in project root
./customize process --project ./examples/test-project --dry-run

# 🆕 NEW: Apply changes without confirmation prompt (for CI/batch)
./customize process --project ./examples/test-project --yes
```

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
./customize process --project ./my-template --dry-run
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
./customize process --project ./my-template --yes
# Applies changes immediately without asking "Apply these changes? [y/N]"
```

The foundation is solid and working perfectly! 🚀