# Template Customizer - AI Agent Integration Guide

**PURPOSE**: This document enables AI agents (Claude, GPT, Copilot, etc.) to autonomously detect, configure, and execute the Template Customizer tool for project initialization and configuration tasks.

**OPTIMIZATION**: Structured as executable decision trees with validation checkpoints for deterministic execution.

**VERSION**: 0.3.0 (with External Replacements)
**NATIVE BINARY**: https://github.com/mkuhl/customizer/releases/latest/download/customizer-linux-x64.tar.gz
**METHOD**: Native Linux executable (primary) with Docker fallback (legacy)

## INSTALLATION

### One-Liner Installation (Recommended - Fast ~100ms Startup)

```bash
# Install with single command
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh

# Or install to custom directory
curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh -s -- --dir ~/.local/bin

# Verify installation
customizer --version
```

### Manual Installation (Alternative)

```bash
# Step 1: Download and extract
curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer-linux-x64.tar.gz | tar xz

# Step 2: Make executable and accessible
chmod +x customizer
sudo mv customizer /usr/local/bin/

# Step 3: Verify installation
customizer --version
```

### Installation Validation
```bash
# Verify customizer is available
command -v customizer >/dev/null 2>&1 && echo "✓ Customizer available" || echo "✗ Installation failed"

# Check version
customizer --version 2>/dev/null && echo "✓ Working correctly" || echo "✗ Binary not functioning"

# Test basic functionality
customizer info >/dev/null 2>&1 && echo "✓ Core functions working" || echo "✗ Core functions failing"
```

### System Requirements
- Linux x86_64 (Ubuntu 20.04+, RHEL 8+, Debian 11+, or compatible)
- GLIBC 2.31 or newer (check with: `ldd --version`)
- No Python, Docker, or other dependencies required

## TOOL_IDENTIFICATION

**Purpose**: Batch customize project templates by processing comment-based markers with Jinja2 expressions
**Executable**: Native Linux binary `customizer`  
**Input**: Template directory + YAML/JSON configuration
**Output**: Customized project directory with all markers replaced
**Performance**: ~100ms startup time, 11MB binary size

## DETECTION_PATTERNS

### Marker Detection Commands
```bash
# Quick scan - returns 0 if markers found, 1 if not
grep -r "{{ values\." --include="*.py" --include="*.js" --include="*.yml" --include="*.yaml" --include="*.json" --include="*.html" --include="*.css" --include="*.xml" --include="*.ts" --include="*.jsx" --include="*.tsx" . 2>/dev/null | head -1 && echo "MARKERS_FOUND" || echo "NO_MARKERS"

# Count total markers in project
MARKER_COUNT=$(grep -r "{{ values\." . 2>/dev/null | wc -l)

# List files containing markers
FILES_WITH_MARKERS=$(grep -rl "{{ values\." . 2>/dev/null)
```

### Pattern Recognition Triggers
```
User says: "customize template" → CHECK_FOR_MARKERS
User says: "initialize from template" → CHECK_FOR_MARKERS  
User says: "configure project" → CHECK_FOR_MARKERS
Directory contains: "template/", "scaffold/", "boilerplate/" → CHECK_FOR_MARKERS
Files contain: "{{ values." pattern → USE_CUSTOMIZER
Config files present: "customizer-config.yml", "template.yml" → CHECK_FOR_MARKERS
```

## USAGE_DECISION_TREE

```
START
├─ DETECT: grep -r "{{ values\." . 2>/dev/null | head -1
│  ├─ MARKERS_FOUND
│  │  ├─ CONFIG_EXISTS: test -f config.yml || test -f customizer-config.yml  
│  │  │  ├─ YES → EXECUTE_CUSTOMIZATION
│  │  │  └─ NO → GENERATE_CONFIG → EXECUTE_CUSTOMIZATION
│  │  └─ 
│  └─ NO_MARKERS_FOUND
│     ├─ USER_WANTS_TEMPLATE: Check user intent
│     │  ├─ YES → ADD_MARKERS → GENERATE_CONFIG → EXECUTE_CUSTOMIZATION
│     │  └─ NO → ABORT: "No template markers found. Use standard file operations instead."
│     └─
└─
```

### Decision Logic Commands  
```bash
# Check for markers
HAS_MARKERS=$(grep -r "{{ values\." . 2>/dev/null | head -1 && echo "true" || echo "false")

# Check for config
HAS_CONFIG=$(test -f config.yml || test -f customizer-config.yml && echo "true" || echo "false")

# Decision execution
if [[ "$HAS_MARKERS" == "true" && "$HAS_CONFIG" == "true" ]]; then
    ACTION="EXECUTE_CUSTOMIZATION"
elif [[ "$HAS_MARKERS" == "true" && "$HAS_CONFIG" == "false" ]]; then
    ACTION="GENERATE_CONFIG_THEN_EXECUTE"
elif [[ "$HAS_MARKERS" == "false" ]]; then
    ACTION="ABORT_OR_ADD_MARKERS"
fi
```

### Use Template Customizer When:
- `grep -r "{{ values\." .` returns matches
- Project contains template markers in comments: `# variable = {{ values.expression }}`
- Need to customize multiple files with same configuration values
- Template directory structure should be preserved
- Files contain placeholder values that need systematic replacement

### Do NOT Use When:
- `grep -r "{{ values\." .` returns no matches AND user doesn't want to add markers
- Simple find/replace operations (use sed/awk instead)
- Single file modifications
- No template markers present in project
- Real-time interactive customization needed

## CONFIG_GENERATION

### Auto-Discovery of Required Configuration
```bash
# Extract all required configuration keys from template markers
REQUIRED_KEYS=$(grep -rh "{{ values\." . 2>/dev/null | \
    sed -n 's/.*{{ values\.\([^}|]*\).*/\1/p' | \
    tr '.' '\n' | \
    sort -u)

# Extract with file context for better understanding  
grep -rn "{{ values\." . 2>/dev/null | \
    sed 's/:.*{{ values\.\([^}|]*\).*/: \1/' | \
    sort -u > required_config_map.txt
```

### Generate Minimal Config
```bash
# Basic config generation
cat > config.yml << 'EOF'
# Auto-generated configuration for Template Customizer
# Replace PLACEHOLDER values with actual values

project:
  name: "PLACEHOLDER_PROJECT_NAME"
  version: "1.0.0"
  description: "PLACEHOLDER_DESCRIPTION"

# Add other sections based on discovered markers
EOF

# Advanced: Generate config based on discovered keys
generate_config() {
    echo "# Auto-generated configuration"
    echo "# Update placeholder values below"
    echo ""
    
    grep -rh "{{ values\." . 2>/dev/null | \
        sed -n 's/.*{{ values\.\([^}|]*\).*/\1/p' | \
        sort -u | \
        awk -F'.' '{
            if (NF == 1) {
                print $1 ": \"PLACEHOLDER_" toupper($1) "\""
            } else {
                path = $1
                for (i = 2; i < NF; i++) {
                    path = path "." $i
                    indent = sprintf("%*s", (i-1)*2, "")
                    if (!seen[path]++) {
                        parent = $1
                        for (j = 2; j < i; j++) parent = parent "." $j
                        if (j == 2) print $1 ":"
                        else print sprintf("%*s", (j-2)*2, "") $j ":"
                    }
                }
                indent = sprintf("%*s", (NF-1)*2, "")
                print indent $NF ": \"PLACEHOLDER_" toupper($NF) "\""
            }
        }'
}

generate_config > config.yml
```

### Validation Pattern
```bash
# Verify all markers have corresponding config values
validate_config() {
    MISSING=$(grep -rh "{{ values\." . 2>/dev/null | \
        sed -n 's/.*{{ values\.\([^}|]*\).*/\1/p' | \
        while read key; do
            # Check if key exists in config (using Python for reliable YAML parsing)
            python3 -c "
import yaml, sys
with open('config.yml') as f:
    config = yaml.safe_load(f)
keys = '$key'.split('.')
current = config
try:
    for k in keys:
        current = current[k]
except:
    print('$key')
    sys.exit(1)
" 2>/dev/null || echo "$key"
        done)
    
    if [[ -n "$MISSING" ]]; then
        echo "WARNING: Missing configuration keys:"
        echo "$MISSING"
        return 1
    else
        echo "SUCCESS: All required keys present in config"
        return 0
    fi
}
```

## COMMAND_PATTERNS

### Pattern 1: Standard Execution (markers exist, config exists)
```bash
# Context: Project has markers, config.yml exists
# Pre-check:
test -f config.yml && grep -q "{{ values\." . || exit 1

# Execute dry-run first:
customizer process --config config.yml --dry-run

# If dry-run looks good, execute:
customizer process --config config.yml --yes

# Verify success:
grep -r "{{ values\." . | wc -l  # Should return 0
```

### Pattern 2: Config Generation Flow (markers exist, no config)
```bash
# Context: Template has markers but no configuration
# Step 1: Extract required keys
KEYS=$(grep -rh "{{ values\." . 2>/dev/null | \
    sed -n 's/.*{{ values\.\([^}|]*\).*/\1/p' | sort -u)

# Step 2: Generate skeleton config
cat > config.yml << 'EOF'
# Generated config - update values below
project:
  name: "UPDATE_ME"
  version: "1.0.0"
EOF

# Step 3: Add discovered keys to config
echo "$KEYS" | while read key; do
    echo "  ${key##*.}: \"PLACEHOLDER_${key##*.}\"" >> config.yml
done

# Step 4: Alert user to update config
echo "ACTION_REQUIRED: Update placeholder values in config.yml"

# Step 5: Execute after config updated
customizer process --yes
```

### Pattern 3: Add Markers to Existing Project
```bash
# Context: User wants to templatize existing project
# Identify configuration points (example for Python project)
CONFIG_PATTERNS="localhost|3000|myapp|postgres|redis"
CONFIG_FILES=$(grep -rl "$CONFIG_PATTERNS" --include="*.py" --include="*.yml" .)

# Add markers above identified lines (Python example)
for file in $CONFIG_FILES; do
    # Example: Add marker for database URL
    sed -i '/^DATABASE_URL = /i # database_url = {{ values.database.url | quote }}' "$file"
    
    # Example: Add marker for app name
    sed -i '/^APP_NAME = /i # app_name = {{ values.project.name | quote }}' "$file"
done

# Generate config for new markers
grep -rh "{{ values\." . | sed -n 's/.*{{ values\.\([^}|]*\).*/\1/p' | sort -u
```

### Pattern 4: Multi-Environment Deployment
```bash
# Context: Deploy to multiple environments
for env in dev staging prod; do
    echo "Processing $env environment..."
    
    # Copy template to environment-specific directory
    cp -r template/ "${env}-output/"
    
    # Apply environment-specific config
    customizer process \
        --project "${env}-output/" \
        --config "configs/${env}.yml" \
        --yes
    
    echo "✓ $env deployment ready in ${env}-output/"
done
```

### Pattern 5: CI/CD Integration  
```bash
# Context: GitHub Actions or other CI/CD pipeline
# .github/workflows/customize.yml example
- name: Install Template Customizer
  run: |
    curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer-linux-x64.tar.gz | tar xz
    sudo mv customizer /usr/local/bin/
    customizer --version

- name: Customize Template
  run: |
    customizer process \
      --project . \
      --config "config-${{ matrix.env }}.yml" \
      --yes
    
    # Verify customization
    test $(grep -r "{{ values\." . | wc -l) -eq 0 || exit 1
```

### Pattern 6: External Replacements for JSON/Markdown
```bash
# Context: Project has JSON files and README to customize
# Create config with external replacements
cat > config.yml << 'EOF'
project:
  name: "my-app"
  version: "2.0.0"
  description: "My awesome application"

replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
      "$.version": "{{ values.project.version }}"
      "$.description": "{{ values.project.description }}"
  markdown:
    "README.md":
      "pattern: # Project Name": "# {{ values.project.name | title }}"
      "pattern: Version: .*": "Version: {{ values.project.version }}"
EOF

# Execute customization (JSON and Markdown files updated)
customizer process --config config.yml --yes

# Verify JSON is valid
python3 -m json.tool package.json > /dev/null && echo "✓ JSON valid"
```

### Pattern 7: Project Initialization from Template
```bash
# Context: Create new project from template
PROJECT_NAME="$1"
OUTPUT_DIR="$2"

# Create configuration
cat > temp_config.yml << EOF
project:
  name: "${PROJECT_NAME}"
  version: "1.0.0"
  description: "Generated from template"
EOF

# Copy template and customize
cp -r template/ "${OUTPUT_DIR}/"
customizer process \
    --project "${OUTPUT_DIR}/" \
    --config temp_config.yml \
    --yes

# Cleanup
rm temp_config.yml

echo "✓ Project '${PROJECT_NAME}' created in ${OUTPUT_DIR}/"
```

## TEMPLATE_MARKER_SYNTAX

### Supported File Types and Comment Patterns
```
Python (.py):           # variable_name = {{ values.jinja_expression }}
JavaScript (.js):       // variable_name = {{ values.jinja_expression }}
TypeScript (.ts):       // variable_name = {{ values.jinja_expression }}
CSS (.css):             /* variable_name = {{ values.jinja_expression }} */
HTML (.html):           <!-- variable_name = {{ values.jinja_expression }} -->
YAML (.yml,.yaml):      # variable_name = {{ values.jinja_expression }}
Dockerfile:             # variable_name = {{ values.jinja_expression }}
Shell (.sh):            # variable_name = {{ values.jinja_expression }}
```

### Template Marker Rules
- Comment syntax must match file type
- Markers must be on separate lines
- Original comment lines are preserved unchanged
- Only following line content is modified
- Invalid Jinja2 expressions cause file-level warnings

### External Replacements (JSON/Markdown Support)
For files that don't support comments (JSON) or when external configuration is preferred:

#### JSON File Replacements
```yaml
# In config.yml - use JSONPath expressions
replacements:
  json:
    "package.json":
      "$.name": "{{ values.project.name }}"
      "$.version": "{{ values.project.version }}"
      "$.scripts.start": "node {{ values.project.name }}.js"
      "$.dependencies.react": "^18.0.0"
      "$.config.port": "{{ values.server.port }}"
      "$.config.debug": true  # Booleans preserved
```

#### Markdown File Replacements  
```yaml
replacements:
  markdown:
    "README.md":
      "pattern: # Old Title": "# {{ values.project.name | title }}"
      "pattern: Version: .*": "Version: {{ values.project.version }}"
      "literal: [PLACEHOLDER]": "{{ values.project.description }}"
```

Features:
- JSONPath for precise JSON targeting
- Regex patterns for Markdown/text files
- Type preservation (strings, numbers, booleans)
- No comment markers needed in files
- Full Jinja2 template support

### Example Template File Structure
```python
# project_name = {{ values.project.name }}
PROJECT_NAME = "default-project"

# api_version = {{ values.api.version }}
API_VERSION = "v1"

# database_url = {{ values.database.host }}/{{ values.database.name }}
DATABASE_URL = "localhost/default"
```

## CONFIGURATION_STRUCTURE

### YAML Configuration Format
```yaml
project:
  name: "MyProject"
  version: "1.0.0"
  description: "Project description"

api:
  version: "v2"
  base_url: "https://api.example.com"

database:
  host: "prod-db.example.com"
  name: "myproject_prod"
  port: 5432

docker:
  registry: "registry.example.com"
  image: "myproject"
  tag: "latest"
```

### JSON Configuration Alternative
```json
{
  "project": {
    "name": "MyProject",
    "version": "1.0.0"
  },
  "api": {
    "version": "v2"
  }
}
```

## ERROR_HANDLING_PATTERNS

### Error Type 1: Missing Configuration Values
```bash
# SYMPTOM_PATTERN: "Warning:.*has [0-9]+ missing values"
# Example output:
# ⚠ Warning: config.py has 2 missing values:
#   Line 5: app_name - Missing value 'values.project.name'

# DIAGNOSIS:
missing_keys=$(customizer process --dry-run 2>&1 | \
    grep "Missing value" | \
    sed -n "s/.*'values\.\([^']*\).*/\1/p" | \
    sort -u)

# RECOVERY:
# Step 1: Add missing keys to config
for key in $missing_keys; do
    echo "Adding missing key: $key"
    # Parse key path and add to YAML (example for 2-level nesting)
    IFS='.' read -ra PARTS <<< "$key"
    if [[ ${#PARTS[@]} -eq 1 ]]; then
        echo "${PARTS[0]}: \"PLACEHOLDER\"" >> config.yml
    elif [[ ${#PARTS[@]} -eq 2 ]]; then
        echo "${PARTS[0]}:" >> config.yml
        echo "  ${PARTS[1]}: \"PLACEHOLDER\"" >> config.yml
    fi
done

# Step 2: Update placeholders with actual values
echo "ACTION_REQUIRED: Update PLACEHOLDER values in config.yml"

# Step 3: Retry customization
customizer process --dry-run

# VALIDATION:
test $(grep "Missing value" output.log 2>/dev/null | wc -l) -eq 0 && echo "✓ All values resolved"
```

### Error Type 2: Invalid Jinja2 Syntax  
```bash
# SYMPTOM_PATTERN: "jinja2.exceptions|TemplateSyntaxError"
# Example: jinja2.exceptions.TemplateSyntaxError: unexpected '}'

# DIAGNOSIS:
# Find files with invalid syntax
invalid_files=$(customizer process --dry-run 2>&1 | \
    grep -B2 "jinja2.exceptions" | \
    grep "Processing" | \
    awk '{print $2}')

# Check marker syntax in affected files
for file in $invalid_files; do
    echo "Checking $file:"
    grep -n "{{" "$file" | grep -v "values\."
done

# RECOVERY:
# Fix common syntax errors
sed -i 's/{{ \([^}]*\) }}/{{ values.\1 }}/g' affected_file.py  # Add missing 'values.'
sed -i 's/{{values\./{{ values./g' affected_file.py            # Add space after {{
sed -i 's/\.\*}}/. }}/g' affected_file.py                      # Remove invalid operators

# VALIDATION:
python3 -c "
from jinja2 import Template
import re
with open('affected_file.py') as f:
    for line in f:
        if '{{' in line:
            marker = re.search(r'{{.*}}', line)
            if marker:
                try:
                    Template(marker.group())
                    print(f'✓ Valid: {marker.group()}')
                except Exception as e:
                    print(f'✗ Invalid: {marker.group()} - {e}')
"
```

### Error Type 3: Binary Not Available
```bash
# SYMPTOM_PATTERN: "customizer: command not found"

# DIAGNOSIS:
customizer_status=$(customizer --version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "Customizer not available: $customizer_status"
    RECOVERY="INSTALL_BINARY"
else
    echo "Customizer available"
    RECOVERY="NONE_NEEDED"
fi

# RECOVERY: Install Native Binary
if [[ "$RECOVERY" == "INSTALL_BINARY" ]]; then
    echo "Installing Template Customizer native binary..."
    curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh
fi

# VALIDATION:
command -v customizer >/dev/null 2>&1 && echo "✓ Customizer available" || echo "✗ Installation failed"
```

### Error Type 4: Permission Denied
```bash
# SYMPTOM_PATTERN: "Permission denied|cannot create directory|Read-only file system"

# DIAGNOSIS:
ls -la . | head -5
stat -c "%a %U:%G" .

# RECOVERY:
# Fix permissions
chmod -R 755 .
chown -R $(whoami):$(whoami) .

# Alternative: Use different output directory
mkdir -p /tmp/customizer-output
cp -r . /tmp/customizer-output/
cd /tmp/customizer-output/
customizer process --config config.yml --yes

# VALIDATION:
test -w . && echo "✓ Directory writable" || echo "✗ Still not writable"
```

### Error Type 5: No Changes Detected
```bash
# SYMPTOM_PATTERN: "No changes found|0 files processed"

# DIAGNOSIS:
marker_count=$(grep -r "{{ values\." . 2>/dev/null | wc -l)
config_exists=$(test -f config.yml && echo "YES" || echo "NO")

echo "Markers found: $marker_count"
echo "Config exists: $config_exists"

if [[ $marker_count -eq 0 ]]; then
    echo "ERROR: No template markers in project"
    echo "SOLUTION: Add markers or use different tool"
fi

# RECOVERY:
# Verify correct directory
pwd
ls -la

# Check if markers use different syntax
grep -r "{{" . --include="*.py" --include="*.js" | head -5

# Try with verbose mode to see what's happening
customizer process --verbose --dry-run

# VALIDATION:
customizer process --dry-run 2>&1 | grep "Found.*changes"
```

## VALIDATION_SUITE

### Pre-Execution Validation
```bash
validate_prerequisites() {
    local ERRORS=0
    
    # Check for customizer binary
    if ! command -v customizer >/dev/null 2>&1; then
        echo "✗ ERROR: Customizer binary not found"
        echo "Install with: curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh"
        ((ERRORS++))
    else
        echo "✓ Customizer binary available"
    fi
    
    # Check for markers
    if ! grep -r "{{ values\." . >/dev/null 2>&1; then
        echo "✗ ERROR: No template markers found"
        ((ERRORS++))
    else
        echo "✓ Template markers found"
    fi
    
    # Check for config
    if [[ ! -f config.yml && ! -f customizer-config.yml ]]; then
        echo "✗ ERROR: No configuration file"
        ((ERRORS++))
    else
        echo "✓ Configuration file exists"
    fi
    
    # Check config completeness
    if [[ -f config.yml ]]; then
        MISSING=$(grep -rh "{{ values\." . 2>/dev/null | \
            sed -n 's/.*values\.\([^}|]*\).*/\1/p' | \
            while read key; do
                python3 -c "
import yaml
with open('config.yml') as f:
    config = yaml.safe_load(f)
keys = '$key'.split('.')
current = config
try:
    for k in keys:
        current = current[k]
except:
    print('$key')
" 2>/dev/null
            done)
        
        if [[ -n "$MISSING" ]]; then
            echo "⚠ WARNING: Missing config keys:"
            echo "$MISSING" | sed 's/^/    - /'
        else
            echo "✓ All required config keys present"
        fi
    fi
    
    return $ERRORS
}

# Execute validation
validate_prerequisites || { echo "Fix errors before proceeding"; exit 1; }
```

### Post-Execution Validation
```bash
validate_results() {
    local OUTPUT_DIR="${1:-.}"
    local ERRORS=0
    
    echo "Validating results in $OUTPUT_DIR..."
    
    # Check: No remaining markers
    REMAINING=$(grep -r "{{ values\." "$OUTPUT_DIR" 2>/dev/null | wc -l)
    if [[ "$REMAINING" -gt 0 ]]; then
        echo "✗ ERROR: $REMAINING unreplaced markers remain"
        grep -r "{{ values\." "$OUTPUT_DIR" | head -5
        ((ERRORS++))
    else
        echo "✓ All markers replaced"
    fi
    
    # Check: Files exist
    FILE_COUNT=$(find "$OUTPUT_DIR" -type f | wc -l)
    if [[ "$FILE_COUNT" -eq 0 ]]; then
        echo "✗ ERROR: No files in output"
        ((ERRORS++))
    else
        echo "✓ $FILE_COUNT files processed"
    fi
    
    # Check: Python syntax (if Python files exist)
    if find "$OUTPUT_DIR" -name "*.py" | head -1 >/dev/null 2>&1; then
        SYNTAX_ERRORS=$(find "$OUTPUT_DIR" -name "*.py" -exec python3 -m py_compile {} \; 2>&1 | grep -c "SyntaxError" || true)
        if [[ "$SYNTAX_ERRORS" -gt 0 ]]; then
            echo "✗ ERROR: $SYNTAX_ERRORS Python syntax errors"
            ((ERRORS++))
        else
            echo "✓ Python syntax valid"
        fi
    fi
    
    if [[ "$ERRORS" -eq 0 ]]; then
        echo "SUCCESS: All validations passed ✓"
        return 0
    else
        echo "FAILURE: $ERRORS validation errors found ✗"
        return 1
    fi
}

# Execute validation
validate_results "." || { echo "Validation failed"; exit 1; }
```

## COMMON_AUTOMATION_PATTERNS

### Pattern 1: Project Initialization
```bash
#!/bin/bash
TEMPLATE_DIR="$1"
PROJECT_NAME="$2"  
OUTPUT_DIR="$3"

# Create configuration
cat > temp_config.yml << EOF
project:
  name: "${PROJECT_NAME}"
  version: "1.0.0"
EOF

# Copy template and customize
cp -r "${TEMPLATE_DIR}" "${OUTPUT_DIR}"
customizer process \
    --project "${OUTPUT_DIR}" \
    --config temp_config.yml \
    --yes

# Cleanup
rm temp_config.yml
```

### Pattern 2: Multi-Environment Deployment
```bash
#!/bin/bash
for env in dev staging prod; do
  cp -r template/ "${env}-output/"
  customizer process \
    --project "${env}-output/" \
    --config "configs/${env}.yml" \
    --yes
done
```

## INTEGRATION_WITH_AI_WORKFLOWS

### When Creating New Projects:
1. Use template project as base
2. Generate configuration from user requirements
3. Execute customizer via native binary
4. Verify output structure and content
5. Proceed with project-specific modifications

### When Modifying Existing Templates:
1. Add template markers to files needing customization
2. Update configuration schema as needed
3. Test with dry-run before actual execution
4. Document new markers for future use

### File Operation Sequence:
```bash
# 1. Prepare workspace
mkdir -p project-output

# 2. Create configuration
echo "project: {name: 'NewProject'}" > config.yml

# 3. Copy template and customize
cp -r template/ project-output/
customizer process \
    --project project-output/ \
    --config config.yml \
    --yes

# 4. Verify and continue with project work
cd project-output
```

## CONTEXT_RECOGNITION

### Quick Recognition Function
```bash
is_template_project() {
    # Check for explicit markers (fastest)
    if grep -r "{{ values\." . >/dev/null 2>&1; then
        echo "TEMPLATE_MARKERS_FOUND"
        return 0
    fi
    
    # Check for template directories
    if [[ -d template || -d scaffold || -d boilerplate ]]; then
        echo "TEMPLATE_DIRECTORY_FOUND"
        return 0
    fi
    
    # Check for config files
    if [[ -f customizer-config.yml || -f .template.yml || -f template.config ]]; then
        echo "TEMPLATE_CONFIG_FOUND"
        return 0
    fi
    
    echo "NOT_A_TEMPLATE"
    return 1
}
```

### Context-Based Decision Making
```bash
# Main decision function for AI agents
should_use_customizer() {
    local USER_INTENT="$1"
    local CURRENT_DIR="${2:-.}"
    
    # Step 1: Check if markers exist
    local HAS_MARKERS=$(grep -r "{{ values\." "$CURRENT_DIR" 2>/dev/null | head -1 && echo "true" || echo "false")
    
    # Step 2: Check user intent
    local WANTS_TEMPLATE=$(echo "$USER_INTENT" | grep -iE "template|customize|configure|initialize" && echo "true" || echo "false")
    
    # Step 3: Check for config
    local HAS_CONFIG=$(test -f "$CURRENT_DIR/config.yml" -o -f "$CURRENT_DIR/customizer-config.yml" && echo "true" || echo "false")
    
    # Decision matrix
    if [[ "$HAS_MARKERS" == "true" ]]; then
        echo "USE_CUSTOMIZER: Template markers detected"
        return 0
    elif [[ "$WANTS_TEMPLATE" == "true" ]] && is_template_directory "$CURRENT_DIR"; then
        echo "CONSIDER_CUSTOMIZER: Template directory structure detected"
        return 0
    elif [[ "$HAS_CONFIG" == "true" ]] && [[ "$WANTS_TEMPLATE" == "true" ]]; then
        echo "CHECK_FOR_MARKERS: Config exists, check if markers needed"
        return 2
    else
        echo "DO_NOT_USE_CUSTOMIZER: No indicators present"
        return 1
    fi
}
```

## DOCKER_FALLBACK

*Note: Native binary is strongly preferred for performance (~100ms vs 2-3s startup). Use Docker for cross-platform consistency or when native binary is unavailable.*

```bash
# Only use if native binary installation fails or cross-platform consistency needed
if ! command -v customizer >/dev/null 2>&1; then
    echo "Falling back to Docker method..."
    docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run
fi
```

📖 **[Complete Docker Documentation](DOCKER.md)** - Detailed Docker usage, CI/CD integration, and troubleshooting