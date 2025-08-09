# Template Customizer - AI Agent Integration Guide

**PURPOSE**: This document enables AI agents (Claude, GPT, Copilot, etc.) to autonomously detect, configure, and execute the Template Customizer tool for project initialization and configuration tasks.

**OPTIMIZATION**: Structured as executable decision trees with validation checkpoints for deterministic execution.

**VERSION**: 0.1.6
**CONTAINER**: ghcr.io/mkuhl/customizer:latest
**STANDALONE**: https://github.com/mkuhl/customizer/releases/latest/download/customizer

## TOOL_IDENTIFICATION

**Purpose**: Batch customize project templates by processing comment-based markers with Jinja2 expressions
**Container**: `ghcr.io/mkuhl/customizer:latest`
**Method**: Docker-only execution via container (or standalone script as fallback)
**Input**: Template directory + YAML/JSON configuration
**Output**: Customized project directory with all markers replaced

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
- Project contains template markers in comments: `# variable = {{ expression }}`
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

## PREREQUISITES_VERIFICATION

```bash
# Verify Docker available
docker --version

# Verify target directory structure
ls -la /path/to/template/directory

# Verify configuration file exists
cat /path/to/config.yml
```

## COMMAND_PATTERNS

### Pattern 1: Standard Execution (markers exist, config exists)
```bash
# Context: Project has markers, config.yml exists
# Pre-check:
test -f config.yml && grep -q "{{ values\." . || exit 1

# Execute with Docker:
docker run --rm \
  -v "$(pwd):/workdir" \
  ghcr.io/mkuhl/customizer:latest \
  process --config config.yml --dry-run

# If dry-run looks good, execute:
docker run --rm \
  -v "$(pwd):/workdir" \
  ghcr.io/mkuhl/customizer:latest \
  process --config config.yml --yes

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
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --yes
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
    
    # Use environment-specific config
    docker run --rm \
        -v "$(pwd)/template:/workdir:ro" \
        -v "$(pwd)/${env}-output:/output" \
        -v "$(pwd)/configs/${env}.yml:/workdir/config.yml:ro" \
        ghcr.io/mkuhl/customizer:latest \
        process --output /output --yes
    
    echo "✓ $env deployment ready in ${env}-output/"
done
```

### Pattern 5: Standalone Script Fallback (No Docker)
```bash
# Context: Docker not available, use standalone script
# Download standalone customizer
curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer -o customizer
chmod +x customizer

# Execute with standalone script
./customizer process --project . --config config.yml --dry-run

# Apply changes
./customizer process --project . --config config.yml --yes
```

### Pattern 6: CI/CD Integration
```bash
# Context: GitHub Actions or other CI/CD pipeline
# .github/workflows/customize.yml example
- name: Customize Template
  run: |
    docker run --rm \
      -v "${{ github.workspace }}:/workdir" \
      -v "${{ github.workspace }}/config-${{ matrix.env }}.yml:/workdir/config.yml:ro" \
      ghcr.io/mkuhl/customizer:latest \
      process --yes
    
    # Verify customization
    test $(grep -r "{{ values\." . | wc -l) -eq 0 || exit 1
```

## TEMPLATE_MARKER_SYNTAX

### Supported File Types and Comment Patterns
```
Python (.py):           # variable_name = {{ jinja_expression }}
JavaScript (.js):       // variable_name = {{ jinja_expression }}
TypeScript (.ts):       // variable_name = {{ jinja_expression }}
CSS (.css):             /* variable_name = {{ jinja_expression }} */
HTML (.html):           <!-- variable_name = {{ jinja_expression }} -->
YAML (.yml,.yaml):      # variable_name = {{ jinja_expression }}
Dockerfile:             # variable_name = {{ jinja_expression }}
Shell (.sh):            # variable_name = {{ jinja_expression }}
```

### Template Marker Rules
- Comment syntax must match file type
- Markers must be on separate lines
- Original comment lines are preserved unchanged
- Only following line content is modified
- Invalid Jinja2 expressions cause file-level warnings

### Example Template File Structure
```python
# project_name = {{ project.name }}
PROJECT_NAME = "default-project"

# api_version = {{ api.version }}
API_VERSION = "v1"

# database_url = {{ database.host }}/{{ database.name }}
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

## WORKFLOW_INTEGRATION_STEPS

### Step 1: Identify Template Project
```bash
# Check for template markers
grep -r "{{ " /path/to/template/ || echo "No markers found"
```

### Step 2: Create Configuration
```bash
# Create config based on found markers
cat > config.yml << EOF
project:
  name: "$(basename $PWD)"
  version: "1.0.0"
EOF
```

### Step 3: Execute Customization
```bash
# Run customizer with proper mounts
docker run --rm \
  -v "$(pwd)/template:/input:ro" \
  -v "$(pwd)/output:/output" \
  -v "$(pwd)/config.yml:/config.yml:ro" \
  ghcr.io/mkuhl/customizer:latest \
  process --project /input --config /config.yml --output /output
```

### Step 4: Verify Results
```bash
# Check output directory structure
ls -la output/

# Verify customizations applied
grep -r "MyProject" output/ || echo "Customization may have failed"
```

## ERROR_HANDLING_PATTERNS

### Error Type 1: Missing Configuration Values
```bash
# SYMPTOM_PATTERN: "Warning:.*has [0-9]+ missing values"
# Example output:
# ⚠ Warning: config.py has 2 missing values:
#   Line 5: app_name - Missing value 'values.project.name'

# DIAGNOSIS:
missing_keys=$(docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run 2>&1 | \
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
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run

# VALIDATION:
test $(grep "Missing value" output.log | wc -l) -eq 0 && echo "✓ All values resolved"
```

### Error Type 2: Invalid Jinja2 Syntax
```bash
# SYMPTOM_PATTERN: "jinja2.exceptions|TemplateSyntaxError"
# Example: jinja2.exceptions.TemplateSyntaxError: unexpected '}'

# DIAGNOSIS:
# Find files with invalid syntax
invalid_files=$(docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run 2>&1 | \
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

### Error Type 3: Docker Not Available
```bash
# SYMPTOM_PATTERN: "docker: command not found|Cannot connect to Docker daemon"

# DIAGNOSIS:
docker_status=$(docker version 2>&1)
if [[ $? -ne 0 ]]; then
    echo "Docker not available: $docker_status"
    FALLBACK="USE_STANDALONE"
else
    echo "Docker available"
    FALLBACK="USE_DOCKER"
fi

# RECOVERY Option 1: Install Docker
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "Install Docker with: curl -fsSL https://get.docker.com | sh"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "Install Docker Desktop from https://www.docker.com/products/docker-desktop"
fi

# RECOVERY Option 2: Use Standalone Script
if [[ "$FALLBACK" == "USE_STANDALONE" ]]; then
    # Download standalone customizer
    curl -L https://github.com/mkuhl/customizer/releases/latest/download/customizer -o customizer
    chmod +x customizer
    
    # Use standalone instead of Docker
    ./customizer process --project . --config config.yml --dry-run
fi

# VALIDATION:
command -v docker >/dev/null 2>&1 && echo "✓ Docker available" || echo "✓ Using standalone"
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

# For SELinux systems
if command -v getenforce >/dev/null 2>&1 && [[ $(getenforce) != "Disabled" ]]; then
    chcon -Rt svirt_sandbox_file_t .
fi

# Alternative: Use different output directory
mkdir -p /tmp/customizer-output
docker run --rm \
    -v "$(pwd):/workdir:ro" \
    -v "/tmp/customizer-output:/output" \
    ghcr.io/mkuhl/customizer:latest \
    process --output /output --yes

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
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest \
    process --verbose --dry-run

# VALIDATION:
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest \
    process --dry-run 2>&1 | grep "Found.*changes"
```

## VALIDATION_SUITE

### Pre-Execution Validation
```bash
validate_prerequisites() {
    local ERRORS=0
    
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
    
    # Check Docker
    if ! docker version >/dev/null 2>&1; then
        echo "⚠ WARNING: Docker not available, will use standalone"
    else
        echo "✓ Docker available"
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
    
    # Check: JSON validity (if JSON files exist)
    if find "$OUTPUT_DIR" -name "*.json" | head -1 >/dev/null 2>&1; then
        JSON_ERRORS=0
        for json_file in $(find "$OUTPUT_DIR" -name "*.json"); do
            if ! python3 -m json.tool "$json_file" >/dev/null 2>&1; then
                echo "✗ ERROR: Invalid JSON in $json_file"
                ((JSON_ERRORS++))
            fi
        done
        if [[ "$JSON_ERRORS" -eq 0 ]]; then
            echo "✓ JSON files valid"
        else
            ((ERRORS++))
        fi
    fi
    
    # Check: YAML validity (if YAML files exist)
    if find "$OUTPUT_DIR" -name "*.yml" -o -name "*.yaml" | head -1 >/dev/null 2>&1; then
        YAML_ERRORS=0
        for yaml_file in $(find "$OUTPUT_DIR" \( -name "*.yml" -o -name "*.yaml" \)); do
            if ! python3 -c "import yaml; yaml.safe_load(open('$yaml_file'))" 2>/dev/null; then
                echo "✗ ERROR: Invalid YAML in $yaml_file"
                ((YAML_ERRORS++))
            fi
        done
        if [[ "$YAML_ERRORS" -eq 0 ]]; then
            echo "✓ YAML files valid"
        else
            ((ERRORS++))
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

### Quick Validation Commands
```bash
# Check if customization is needed
needs_customization() {
    grep -r "{{ values\." . >/dev/null 2>&1
}

# Check if customization succeeded
customization_complete() {
    ! grep -r "{{ values\." . >/dev/null 2>&1
}

# Count files with markers
files_with_markers() {
    grep -rl "{{ values\." . 2>/dev/null | wc -l
}

# Count total markers
total_markers() {
    grep -r "{{ values\." . 2>/dev/null | wc -l
}

# List missing config keys
missing_config_keys() {
    grep -rh "{{ values\." . 2>/dev/null | \
        sed -n 's/.*values\.\([^}|]*\).*/\1/p' | \
        sort -u | \
        while read key; do
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
" 2>/dev/null
        done
}
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

# Execute customization
docker run --rm \
  -v "${TEMPLATE_DIR}:/input:ro" \
  -v "${OUTPUT_DIR}:/output" \
  -v "$(pwd)/temp_config.yml:/config.yml:ro" \
  ghcr.io/mkuhl/customizer:latest \
  process --project /input --config /config.yml --output /output

# Cleanup
rm temp_config.yml
```

### Pattern 2: Multi-Environment Deployment
```bash
#!/bin/bash
for env in dev staging prod; do
  docker run --rm \
    -v "$(pwd)/template:/input:ro" \
    -v "$(pwd)/${env}-output:/output" \
    -v "$(pwd)/configs/${env}.yml:/config.yml:ro" \
    ghcr.io/mkuhl/customizer:latest \
    process --project /input --config /config.yml --output /output
done
```

## INTEGRATION_WITH_AI_WORKFLOWS

### When Creating New Projects:
1. Use template project as base
2. Generate configuration from user requirements
3. Execute customizer via docker
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

# 3. Execute customization
docker run --rm \
  -v "/path/to/template:/input:ro" \
  -v "$(pwd)/project-output:/output" \
  -v "$(pwd)/config.yml:/config.yml:ro" \
  ghcr.io/mkuhl/customizer:latest \
  process --project /input --config /config.yml --output /output

# 4. Verify and continue with project work
cd project-output
```

## CONTEXT_RECOGNITION

### Trigger Keywords in User Requests
```bash
# Keywords that suggest Template Customizer usage
TEMPLATE_KEYWORDS="template|scaffold|boilerplate|customize|configure|initialize from|setup from|create from"
ACTION_KEYWORDS="create project|new app|setup|initialize|configure|deploy"

# Check user request for triggers
check_user_intent() {
    local USER_REQUEST="$1"
    echo "$USER_REQUEST" | grep -iE "$TEMPLATE_KEYWORDS|$ACTION_KEYWORDS" >/dev/null 2>&1
}
```

### Directory Pattern Recognition
```bash
# Indicators that suggest a template project
is_template_directory() {
    local DIR="${1:-.}"
    
    # Check for template directories
    [[ -d "$DIR/template" || -d "$DIR/scaffold" || -d "$DIR/boilerplate" || -d "$DIR/archetype" ]] && {
        echo "TEMPLATE_DIR_FOUND"
        return 0
    }
    
    # Check for template config files
    [[ -f "$DIR/.template.yml" || -f "$DIR/template.config" || -f "$DIR/customizer-config.yml" ]] && {
        echo "TEMPLATE_CONFIG_FOUND"
        return 0
    }
    
    # Check for multiple placeholder values (indicates template)
    local PLACEHOLDERS=$(grep -r "MyApp\|localhost:3000\|example.com\|PLACEHOLDER" "$DIR" 2>/dev/null | wc -l)
    [[ "$PLACEHOLDERS" -gt 10 ]] && {
        echo "PLACEHOLDER_PATTERN_FOUND"
        return 0
    }
    
    return 1
}
```

### File Pattern Recognition
```bash
# Quick scan for template markers
detect_template_markers() {
    local PATTERNS=(
        '# \w+ = {{ values\.'           # Python/Shell/YAML
        '// \w+ = {{ values\.'           # JavaScript/TypeScript
        '/\* \w+ = {{ values\.'          # CSS
        '<!-- \w+ = {{ values\.'         # HTML/XML
        '{{ values\.'                    # Any Jinja2 template
    )
    
    for pattern in "${PATTERNS[@]}"; do
        if grep -rE "$pattern" . >/dev/null 2>&1; then
            echo "PATTERN_MATCH: $pattern"
            return 0
        fi
    done
    
    return 1
}
```

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
    
    # Check for README mentioning template
    if grep -i "template\|scaffold\|boilerplate\|customize" README* 2>/dev/null | head -1 >/dev/null; then
        echo "TEMPLATE_MENTIONED_IN_README"
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
        return 0
    else
        echo "DO_NOT_USE: No template indicators found"
        return 1
    fi
}
```

### Usage Examples for AI Agents
```bash
# Example 1: User says "create a new project from the template"
USER_REQUEST="create a new project from the template"
if should_use_customizer "$USER_REQUEST" .; then
    echo "→ Execute Template Customizer workflow"
fi

# Example 2: Detect if current directory is a template
if is_template_project; then
    echo "→ This is a template project, suggest customization"
fi

# Example 3: Check specific directory
if is_template_directory "/path/to/project"; then
    echo "→ Template indicators found, check for markers"
fi
```

## SUCCESS_VALIDATION_COMMANDS

```bash
# Check customization applied
find output/ -type f -exec grep -l "{{ " {} \; | wc -l  # Should be 0

# Verify configuration values applied
grep -r "MyProject" output/ | head -5

# Check file structure preserved
diff -r template/ output/ --exclude="*.pyc" | grep "Only in template"

# Validate no broken references
find output/ -name "*.py" -exec python -m py_compile {} \; 2>&1 | grep -v "Compiling"
```

## TROUBLESHOOTING_QUICK_REFERENCE

| Issue | Check | Solution |
|-------|-------|----------|
| No files changed | Template markers present | Add markers to template files |
| Permission denied | Mount paths readable | Use absolute paths, check permissions |
| Missing values warning | Configuration complete | Add missing keys to config file |
| Container not found | Image available | Run `docker pull ghcr.io/mkuhl/customizer:latest` |
| Jinja2 errors | Template syntax | Fix `{{ expression }}` syntax |

## OUTPUT_EXPECTATIONS

- **Success**: All template markers replaced, directory structure preserved
- **Warnings**: Missing configuration values logged but files still copied
- **Errors**: Invalid syntax prevents file processing, original preserved
- **Performance**: ~100 files/second processing speed
- **File Handling**: Original files never modified, output is clean copy