# Template Customizer - Troubleshooting Guide

This guide helps you diagnose and resolve common issues with Template Customizer, especially with the new self-referencing YAML values feature (v0.4.0+).

## Quick Diagnostic Commands

### 1. Check Template Customizer Status

```bash
# Verify installation
customizer --version

# Test basic functionality
customizer info

# Check if project has template markers
grep -r "{{ values\." . 2>/dev/null | head -5

# Validate configuration file syntax
python3 -c "import yaml; yaml.safe_load(open('config.yml'))"
```

### 2. Test Reference Resolution

```bash
# Test configuration resolution with verbose output
customizer process --config config.yml --verbose --dry-run

# Test without reference resolution
customizer process --config config.yml --no-resolve-refs --dry-run

# Check for circular dependencies
customizer process --config config.yml --dry-run 2>&1 | grep -i "circular"
```

## Self-Referencing Configuration Issues (v0.4.0+)

### Issue: Circular Dependency Detected

**Symptoms:**
```
❌ Circular dependency detected in configuration file 'config.yml':
   Circular dependency detected: a → b → c → a
```

**Diagnosis:**
```bash
# Find circular references in your configuration
grep -n "{{ values\." config.yml | sort
```

**Solutions:**

1. **Break the cycle** by making one value independent:
```yaml
# Before (circular)
services:
  frontend:
    url: "{{ values.services.api.url }}/app"
  api:
    url: "https://{{ values.services.frontend.name }}.com"

# After (fixed)
base:
  domain: "example.com"
  
services:
  frontend:
    name: "myapp-frontend"
    url: "{{ values.services.api.url }}/app"
  api:
    url: "https://api.{{ values.base.domain }}"
```

2. **Restructure dependencies** to flow in one direction:
```yaml
# Good: Clear dependency hierarchy
project:
  name: "myapp"

computed:
  service_prefix: "{{ values.project.name }}-service"

services:
  api:
    name: "{{ values.computed.service_prefix }}-api"
  frontend:
    name: "{{ values.computed.service_prefix }}-web"
```

### Issue: Reference Not Found

**Symptoms:**
```
❌ Reference resolution failed in configuration file 'config.yml':
   Reference 'values.database.host' not found
```

**Diagnosis:**
```bash
# Find all references in your config
grep -o "{{ values\.[^}]*" config.yml | sort -u

# Check for missing sections
python3 -c "
import yaml
config = yaml.safe_load(open('config.yml'))
references = ['database.host']  # Add your missing references
for ref in references:
    keys = ref.split('.')
    current = config
    try:
        for key in keys:
            current = current[key]
        print(f'✓ {ref}: {current}')
    except:
        print(f'✗ {ref}: MISSING')
"
```

**Solutions:**

1. **Add missing configuration section:**
```yaml
# Add the missing section
database:
  host: "localhost"
  port: 5432
  name: "{{ values.project.name }}_db"
```

2. **Fix typos in reference paths:**
```yaml
# Wrong
api_url: "{{ values.database.hostname }}"  # Should be 'host'

# Correct
api_url: "{{ values.database.host }}"
```

### Issue: Template Syntax Error

**Symptoms:**
```
❌ Template syntax error in configuration file 'config.yml':
   Invalid template syntax: No filter named 'invalid_filter'
```

**Diagnosis:**
```bash
# Validate Jinja2 syntax in configuration
python3 -c "
import yaml
from jinja2 import Template
import re

with open('config.yml') as f:
    config = yaml.safe_load(f)

def check_templates(obj, path=''):
    if isinstance(obj, dict):
        for k, v in obj.items():
            check_templates(v, f'{path}.{k}' if path else k)
    elif isinstance(obj, str) and '{{' in obj:
        try:
            Template(obj)
            print(f'✓ {path}: {obj}')
        except Exception as e:
            print(f'✗ {path}: {obj} - ERROR: {e}')

check_templates(config)
"
```

**Solutions:**

1. **Fix filter names:**
```yaml
# Wrong
name: "{{ values.project.title | invalid_filter }}"

# Correct - use valid Jinja2 filters
name: "{{ values.project.title | lower | replace(' ', '-') }}"
```

2. **Fix template syntax:**
```yaml
# Wrong - missing space after {{
url: "{{values.api.host}}/endpoint"

# Correct
url: "{{ values.api.host }}/endpoint"
```

### Issue: Maximum Recursion Depth Exceeded

**Symptoms:**
```
❌ Maximum recursion depth exceeded during reference resolution
```

**Diagnosis:**
This usually indicates an indirect circular dependency or very deep reference chains.

**Solutions:**

1. **Limit reference depth:**
```yaml
# Avoid very deep chains
# Bad: a → b → c → d → e → f
level_f: "{{ values.level_e }}-suffix"
level_e: "{{ values.level_d }}-suffix"
# ... (too deep)

# Good: Flatten the structure
base:
  prefix: "myapp"

services:
  api: "{{ values.base.prefix }}-api"
  web: "{{ values.base.prefix }}-web"
```

2. **Use intermediate computed values:**
```yaml
# Instead of deep chains, use intermediate values
base:
  name: "myapp"
  env: "prod"

computed:
  app_prefix: "{{ values.base.name }}-{{ values.base.env }}"

services:
  api: "{{ values.computed.app_prefix }}-api"
  worker: "{{ values.computed.app_prefix }}-worker"
```

## Traditional Template Processing Issues

### Issue: No Changes Found

**Symptoms:**
```
ℹ No changes found
✓ Found 0 changes in 0 files
```

**Diagnosis:**
```bash
# Check if template markers exist
grep -r "{{ values\." . 2>/dev/null | wc -l

# Check file patterns
find . -name "*.py" -o -name "*.js" -o -name "*.yml" | head -10

# Verify configuration file exists
ls -la *.yml *.yaml *.json 2>/dev/null
```

**Solutions:**

1. **Add template markers to files:**
```python
# Add markers to your template files
# app_name = {{ values.project.name | quote }}
app_name = "DefaultApp"
```

2. **Check file inclusion patterns:**
```bash
# Include specific file types
customizer process --include "*.py,*.js,*.yml" --dry-run

# Check what files are being scanned
customizer process --verbose --dry-run
```

### Issue: Template Markers Not Found

**Symptoms:**
```
⚠ Warning: config.py has 1 missing values:
  Line 5: app_name - Missing value 'values.project.name'
```

**Diagnosis:**
```bash
# Check marker format
grep -n "{{ values\." your_file.py

# Verify configuration has the required values
python3 -c "import yaml; config = yaml.safe_load(open('config.yml')); print(config.get('project', {}).get('name', 'MISSING'))"
```

**Solutions:**

1. **Fix marker syntax:**
```python
# Wrong - typo in 'values'
# app_name = {{ value.project.name }}

# Correct
# app_name = {{ values.project.name }}
app_name = "DefaultApp"
```

2. **Add missing configuration:**
```yaml
# Add missing configuration section
project:
  name: "MyApp"
  version: "1.0.0"
```

### Issue: JSON/External Replacements Not Working

**Symptoms:**
JSON or Markdown files aren't being updated despite external replacement rules.

**Diagnosis:**
```bash
# Check external replacement syntax
python3 -c "
import yaml
config = yaml.safe_load(open('config.yml'))
print('External replacements:', config.get('replacements', 'MISSING'))
"

# Verify JSONPath syntax (for JSON files)
python3 -c "
from jsonpath_ng import parse
try:
    jsonpath_expr = parse('$.name')
    print('✓ JSONPath syntax valid')
except Exception as e:
    print(f'✗ JSONPath error: {e}')
"
```

**Solutions:**

1. **Fix JSONPath syntax:**
```yaml
# Wrong - invalid JSONPath
replacements:
  json:
    "package.json":
      "name": "{{ values.project.name }}"  # Missing $. prefix

# Correct
replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
```

2. **Fix Markdown pattern syntax:**
```yaml
# Wrong - unescaped regex characters
replacements:
  markdown:
    "README.md":
      "pattern: # Title (v1.0)": "# {{ values.project.name }}"

# Correct - escape special characters
replacements:
  markdown:
    "README.md":
      "pattern: # Title \\(v1\\.0\\)": "# {{ values.project.name }}"
```

## Installation Issues

### Issue: Command Not Found

**Symptoms:**
```bash
customizer --version
# bash: customizer: command not found
```

**Solutions:**

1. **Install using the one-liner:**
```bash
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh
```

2. **Manual installation:**
```bash
curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer-linux-x64.tar.gz | tar xz
sudo mv customizer /usr/local/bin/
chmod +x /usr/local/bin/customizer
```

3. **Check PATH:**
```bash
echo $PATH
# Make sure /usr/local/bin is in your PATH
```

### Issue: Permission Denied

**Symptoms:**
```
Permission denied: Cannot write to output directory
```

**Solutions:**

1. **Fix directory permissions:**
```bash
chmod -R 755 .
```

2. **Use a writable output directory:**
```bash
mkdir -p /tmp/customizer-output
cp -r . /tmp/customizer-output/
cd /tmp/customizer-output/
customizer process --yes
```

### Issue: GLIBC Version Too Old

**Symptoms:**
```
./customizer: /lib/x86_64-linux-gnu/libc.so.6: version `GLIBC_2.31' not found
```

**Solutions:**

1. **Check GLIBC version:**
```bash
ldd --version
```

2. **Use Docker fallback:**
```bash
# Download Docker wrapper
curl -L -o run-docker-customizer.sh https://github.com/mkuhl/customizer/releases/latest/download/run-docker-customizer.sh
chmod +x run-docker-customizer.sh

# Use Docker version
./run-docker-customizer.sh process --dry-run
```

## Performance Issues

### Issue: Slow Reference Resolution

**Symptoms:**
Resolution takes several seconds for large configuration files.

**Diagnosis:**
```bash
# Test resolution performance
time customizer process --config config.yml --verbose --dry-run
```

**Solutions:**

1. **Reduce reference complexity:**
```yaml
# Instead of many individual references
services:
  api_1: "{{ values.project.name }}-api-1"
  api_2: "{{ values.project.name }}-api-2"
  # ... (100 similar services)

# Use computed base values
computed:
  service_prefix: "{{ values.project.name }}-api"

services:
  api_1: "{{ values.computed.service_prefix }}-1"
  api_2: "{{ values.computed.service_prefix }}-2"
```

2. **Cache frequently used values:**
```yaml
# Compute once, reference many times
docker:
  registry_url: "{{ values.aws.account_id }}.dkr.ecr.{{ values.aws.region }}.amazonaws.com"

images:
  api: "{{ values.docker.registry_url }}/api:{{ values.project.version }}"
  worker: "{{ values.docker.registry_url }}/worker:{{ values.project.version }}"
  web: "{{ values.docker.registry_url }}/web:{{ values.project.version }}"
```

## Configuration File Issues

### Issue: YAML Syntax Error

**Symptoms:**
```
yaml.scanner.ScannerError: while scanning for the next token found character '%' that cannot start any token
```

**Solutions:**

1. **Validate YAML syntax:**
```bash
python3 -c "import yaml; yaml.safe_load(open('config.yml'))"
```

2. **Common YAML fixes:**
```yaml
# Wrong - unquoted special characters
url: http://example.com?param=value&other=123

# Correct - quote strings with special characters
url: "http://example.com?param=value&other=123"

# Wrong - inconsistent indentation
project:
  name: myapp
   version: 1.0  # Wrong indentation

# Correct - consistent indentation
project:
  name: myapp
  version: 1.0
```

### Issue: JSON Syntax Error

**Symptoms:**
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 5 column 2
```

**Solutions:**

1. **Validate JSON syntax:**
```bash
python3 -m json.tool config.json
```

2. **Common JSON fixes:**
```json
// Wrong - trailing comma
{
  "name": "myapp",
  "version": "1.0.0",
}

// Correct - no trailing comma
{
  "name": "myapp",
  "version": "1.0.0"
}
```

## Advanced Debugging

### Enable Debug Mode

```bash
# Maximum verbosity
customizer process --config config.yml --verbose --dry-run

# Check resolution order
customizer process --config config.yml --verbose --dry-run 2>&1 | grep "Resolution order"

# Isolate reference resolution
customizer process --config config.yml --no-resolve-refs --dry-run
```

### Configuration Validation Script

Save this as `validate-config.py`:

```python
#!/usr/bin/env python3
import yaml
import json
import sys
from pathlib import Path
from jinja2 import Template

def validate_config(config_path):
    """Comprehensive configuration validation."""
    path = Path(config_path)
    
    if not path.exists():
        print(f"✗ Config file not found: {config_path}")
        return False
    
    # Load configuration
    try:
        if path.suffix.lower() in ['.yml', '.yaml']:
            with open(path) as f:
                config = yaml.safe_load(f)
        elif path.suffix.lower() == '.json':
            with open(path) as f:
                config = json.load(f)
        else:
            print(f"✗ Unsupported config format: {path.suffix}")
            return False
        print(f"✓ Configuration file syntax valid")
    except Exception as e:
        print(f"✗ Configuration syntax error: {e}")
        return False
    
    # Check for references
    def find_references(obj, path=""):
        refs = []
        if isinstance(obj, dict):
            for k, v in obj.items():
                refs.extend(find_references(v, f"{path}.{k}" if path else k))
        elif isinstance(obj, str) and "{{ values." in obj:
            refs.append((path, obj))
        return refs
    
    references = find_references(config)
    print(f"✓ Found {len(references)} template references")
    
    # Validate template syntax
    errors = 0
    for path, template_str in references:
        try:
            Template(template_str)
            print(f"✓ {path}: {template_str}")
        except Exception as e:
            print(f"✗ {path}: {template_str} - ERROR: {e}")
            errors += 1
    
    if errors == 0:
        print(f"✓ All {len(references)} template references have valid syntax")
        return True
    else:
        print(f"✗ {errors} template syntax errors found")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 validate-config.py config.yml")
        sys.exit(1)
    
    success = validate_config(sys.argv[1])
    sys.exit(0 if success else 1)
```

Use it:
```bash
python3 validate-config.py config.yml
```

## Getting Help

If you're still experiencing issues:

1. **Check the GitHub Issues**: [https://github.com/mkuhl/customizer/issues](https://github.com/mkuhl/customizer/issues)
2. **Create a minimal reproduction case**:
   ```bash
   # Create a simple test case
   mkdir test-case
   cd test-case
   
   # Minimal config
   echo 'project: {name: "test"}' > config.yml
   
   # Minimal template file
   echo '# name = {{ values.project.name }}' > test.py
   echo 'name = "default"' >> test.py
   
   # Test
   customizer process --verbose --dry-run
   ```
3. **Include this information in your issue**:
   - Template Customizer version (`customizer --version`)
   - Operating system and version
   - Complete error message
   - Minimal configuration and template files that reproduce the issue
   - Output of `customizer process --verbose --dry-run`

## Best Practices for Avoiding Issues

1. **Start simple** - Begin with basic references before adding complexity
2. **Use verbose mode** - Always test with `--verbose --dry-run` first
3. **Validate incrementally** - Add references one at a time and test
4. **Follow naming conventions** - Use consistent, descriptive names
5. **Avoid deep nesting** - Keep reference chains reasonable
6. **Document your configuration** - Add comments explaining complex references
7. **Version your configuration** - Track changes and test thoroughly