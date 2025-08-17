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

## Self-Referencing Configuration Values (New in v0.4.0)

Template Customizer now supports **self-referencing** values within your configuration files, allowing you to build complex configurations from simpler values and eliminate duplication.

### Basic Self-References

Reference other values in your configuration using the same `{{ values.path }}` syntax:

```yaml
# config.yml
project:
  name: "my-microservice"
  version: "1.2.0"
  environment: "production"

# These values reference other values in the same configuration
docker:
  registry: "ghcr.io/mycompany"
  image: "{{ values.docker.registry }}/{{ values.project.name }}:{{ values.project.version }}"

database:
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.project.environment }}"
  host: "{{ values.project.name }}-{{ values.project.environment }}.cluster.amazonaws.com"
```

### Advanced Examples

#### Microservices Configuration

Perfect for complex deployments where values need to be consistent across services:

```yaml
# config.yml
environment: "production"
region: "us-east-1"
company: "acme"

project:
  name: "ecommerce-platform"
  version: "2.1.0"

# AWS Infrastructure
aws:
  account_id: "123456789012"
  ecr_registry: "{{ values.aws.account_id }}.dkr.ecr.{{ values.region }}.amazonaws.com"

# Service definitions
services:
  api:
    name: "{{ values.project.name }}-api"
    port: 8080
    image: "{{ values.aws.ecr_registry }}/{{ values.services.api.name }}:{{ values.project.version }}"
    url: "https://{{ values.services.api.name }}.{{ values.environment }}.{{ values.company }}.com"
  
  frontend:
    name: "{{ values.project.name }}-web"
    port: 3000
    image: "{{ values.aws.ecr_registry }}/{{ values.services.frontend.name }}:{{ values.project.version }}"
    url: "https://{{ values.services.frontend.name }}.{{ values.environment }}.{{ values.company }}.com"

# Database configuration
database:
  host: "{{ values.project.name }}-{{ values.environment }}.cluster-xyz.{{ values.region }}.rds.amazonaws.com"
  name: "{{ values.project.name | replace('-', '_') }}_{{ values.environment }}"
  url: "postgresql://user:pass@{{ values.database.host }}/{{ values.database.name }}"

# Monitoring and logging
monitoring:
  namespace: "{{ values.project.name }}/{{ values.environment }}"
  alerts:
    api_health: "{{ values.services.api.url }}/health"
    frontend_health: "{{ values.services.frontend.url }}/health"
```

#### Kubernetes/Helm Values Pattern

Common pattern for Kubernetes deployments:

```yaml
# values.yml (Helm-style configuration)
global:
  imageRegistry: "registry.acme.com"
  imageTag: "v1.2.3"
  namespace: "my-app-prod"

app:
  name: "my-application"
  fullName: "{{ values.global.namespace }}-{{ values.app.name }}"
  labels:
    app: "{{ values.app.name }}"
    version: "{{ values.global.imageTag }}"

images:
  api: "{{ values.global.imageRegistry }}/{{ values.app.name }}-api:{{ values.global.imageTag }}"
  worker: "{{ values.global.imageRegistry }}/{{ values.app.name }}-worker:{{ values.global.imageTag }}"
  nginx: "{{ values.global.imageRegistry }}/nginx:stable"

ingress:
  enabled: true
  host: "{{ values.app.name }}.acme.com"

secrets:
  name: "{{ values.app.fullName }}-secrets"
  dockerRegistry: "{{ values.app.fullName }}-registry-secret"

configMaps:
  name: "{{ values.app.fullName }}-config"
```

### Resolution Features

#### Order Independence

References work regardless of definition order:

```yaml
# This works even though 'frontend.url' is defined before 'frontend.name'
frontend:
  url: "https://{{ values.frontend.name }}.example.com"
  name: "my-frontend"

# Also works with deeply nested references
database:
  connection_string: "postgresql://{{ values.database.credentials.username }}:{{ values.database.credentials.password }}@{{ values.database.host }}/{{ values.database.name }}"
  host: "{{ values.project.name }}-db.cluster.amazonaws.com"
  name: "{{ values.project.name | replace('-', '_') }}"
  credentials:
    username: "app_user"
    password: "secure_password"

project:
  name: "my-app"
```

#### Chained References

References can reference other references:

```yaml
base:
  domain: "example.com"
  
api:
  subdomain: "api"
  host: "{{ values.api.subdomain }}.{{ values.base.domain }}"
  
frontend:
  subdomain: "app"
  host: "{{ values.frontend.subdomain }}.{{ values.base.domain }}"
  api_endpoint: "https://{{ values.api.host }}/v1"
  
monitoring:
  healthcheck_urls:
    - "{{ values.frontend.api_endpoint }}/health"
    - "https://{{ values.frontend.host }}/health"
```

#### Type Preservation

Non-string types are preserved in pure references:

```yaml
settings:
  port: 3000              # integer
  debug: true             # boolean
  features: ["auth", "api"] # array

server:
  port: "{{ values.settings.port }}"        # Remains integer: 3000
  debug_mode: "{{ values.settings.debug }}" # Remains boolean: true
  enabled_features: "{{ values.settings.features }}" # Remains array

# String interpolation converts to strings
connection:
  url: "http://localhost:{{ values.settings.port }}"  # String: "http://localhost:3000"
```

### CLI Usage

#### Verbose Mode

See detailed resolution information:

```bash
customizer process --project ./template --config ./config.yml --verbose --dry-run
```

Output:
```
🔄 Resolving self-references in configuration...
  📊 Built dependency graph with 12 nodes
     services.api.image depends on: aws.ecr_registry, services.api.name, project.version
     services.api.name depends on: project.name
     aws.ecr_registry depends on: aws.account_id, region
  📋 Resolution order: project.name → region → aws.account_id → aws.ecr_registry → services.api.name → services.api.image
  ✅ Resolution completed in 2 iteration(s)
✅ Successfully resolved configuration references
```

#### Disable Resolution

For compatibility or debugging:

```bash
customizer process --project ./template --config ./config.yml --no-resolve-refs --dry-run
```

### Error Handling

Template Customizer provides clear error messages for configuration issues:

#### Circular Dependencies

```yaml
# This will cause an error:
a: "{{ values.b }}"
b: "{{ values.c }}"
c: "{{ values.a }}"
```

Error message:
```
❌ Circular dependency detected in configuration file 'config.yml':
   Circular dependency detected: a → b → c → a
   Please check your configuration for references that form a loop.
```

#### Missing References

```yaml
project:
  name: "myapp"
api:
  url: "{{ values.database.host }}"  # database.host doesn't exist
```

Error message:
```
❌ Reference resolution failed in configuration file 'config.yml':
   Reference 'values.database.host' not found
   Please ensure all referenced values exist in your configuration.
```

#### Template Syntax Errors

```yaml
project:
  name: "myapp"
api:
  url: "{{ values.project.name | invalid_filter }}"  # invalid filter
```

Error message:
```
❌ Template syntax error in configuration file 'config.yml':
   Invalid template syntax: No filter named 'invalid_filter'
   Please check your Jinja2 template syntax.
```

### Best Practices

#### 1. Use Descriptive Base Values

```yaml
# Good: Clear base values
project:
  name: "ecommerce"
  environment: "production"
  region: "us-east-1"

# Then build complex values
database:
  host: "{{ values.project.name }}-{{ values.project.environment }}.{{ values.project.region }}.rds.amazonaws.com"
```

#### 2. Group Related References

```yaml
# Group infrastructure settings
infrastructure:
  vpc_id: "vpc-12345"
  subnet_prefix: "10.0"
  availability_zones: ["us-east-1a", "us-east-1b"]

# Use them in related services
services:
  database:
    subnet_group: "{{ values.infrastructure.vpc_id }}-db-subnet-group"
    security_group: "{{ values.infrastructure.vpc_id }}-db-sg"
```

#### 3. Use Filters for Transformations

```yaml
project:
  name: "My-Awesome-App"

# Use filters to transform values appropriately
docker:
  image_name: "{{ values.project.name | lower | replace(' ', '-') | replace('_', '-') }}"
  # Results in: "my-awesome-app"

database:
  name: "{{ values.project.name | lower | replace('-', '_') | replace(' ', '_') }}"
  # Results in: "my_awesome_app"
```

#### 4. Validate Your Configuration

Always test your configuration with dry-run mode:

```bash
# Test resolution and template processing
customizer process --config config.yml --dry-run --verbose

# Test just the reference resolution
customizer process --config config.yml --no-resolve-refs --dry-run
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

### 📦 External Replacements (JSON/Markdown Support)

Template Customizer now supports external replacements for files that don't support comments well (like JSON) or when you prefer to keep replacement rules in your configuration file.

#### JSON File Replacements

Use JSONPath expressions to target specific values in JSON files:

```yaml
# config.yml
project:
  name: "my-awesome-app"
  version: "2.0.0"
  description: "Built with Template Customizer"

replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
      "$.version": "{{ values.project.version }}"
      "$.description": "{{ values.project.description }}"
      "$.scripts.start": "node {{ values.project.name }}.js"
      "$.dependencies.react": "^18.0.0"
      "$.config.port": 8080
      "$.config.debug": true  # Booleans are preserved
```

**Features:**
- Standard JSONPath syntax for precise targeting
- Automatic type preservation (strings, numbers, booleans)
- Works with nested objects and arrays
- No comment markers needed in JSON files

#### Markdown File Replacements

Use regex patterns or literal strings to update Markdown files:

```yaml
replacements:
  markdown:
    "README.md":
      "pattern: # Old Project Name": "# {{ values.project.name | title }}"
      "pattern: Version: .*": "Version: {{ values.project.version }}"
      "pattern: Copyright \\(c\\) \\d+": "Copyright (c) 2024"
      "literal: [PLACEHOLDER]": "{{ values.project.description }}"  # Literal match
```

**Pattern Types:**
- `pattern:` - Regular expression matching
- `literal:` - Exact string matching (special characters escaped)
- Full Jinja2 template support with filters

#### Example: Complete Project Customization

```yaml
# config.yml
project:
  name: "awesome-api"
  version: "3.0.0"
  author: "Jane Developer"

server:
  port: 8080
  host: "api.example.com"

# Traditional marker-based replacements for Python files
# (These use comment markers in the files)

# External replacements for JSON and Markdown
replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
      "$.version": "{{ values.project.version }}"
      "$.author": "{{ values.project.author }}"
    "tsconfig.json":
      "$.compilerOptions.outDir": "./dist"
  markdown:
    "README.md":
      "pattern: # Template Project": "# {{ values.project.name | title }}"
      "pattern: localhost:3000": "{{ values.server.host }}:{{ values.server.port }}"
```

Run the customization:
```bash
customizer process --config config.yml --dry-run  # Preview changes
customizer process --config config.yml --yes       # Apply changes
```

The foundation is solid and working perfectly! 🚀