# Template Customizer - AI Agent Integration Guide

## TOOL_IDENTIFICATION

**Purpose**: Batch customize project templates by processing comment-based markers with Jinja2 expressions
**Container**: `ghcr.io/mkuhl/customizer:latest`
**Method**: Docker-only execution via container
**Input**: Template directory + YAML/JSON configuration
**Output**: Customized project directory

## USAGE_DECISION_TREE

### Use Template Customizer When:
- Project contains template markers in comments: `# variable = {{ expression }}`
- Need to customize multiple files with same configuration values
- Template directory structure should be preserved
- Files contain placeholder values that need systematic replacement

### Do NOT Use When:
- Simple find/replace operations (use sed/awk instead)
- Single file modifications
- No template markers present in project
- Real-time interactive customization needed

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

### Basic Execution Pattern
```bash
docker run --rm \
  -v "/path/to/template:/input:ro" \
  -v "/path/to/output:/output" \
  -v "/path/to/config.yml:/config.yml:ro" \
  ghcr.io/mkuhl/customizer:latest \
  process --project /input --config /config.yml --output /output
```

### With File Filtering
```bash
docker run --rm \
  -v "/path/to/template:/input:ro" \
  -v "/path/to/output:/output" \
  -v "/path/to/config.yml:/config.yml:ro" \
  ghcr.io/mkuhl/customizer:latest \
  process --project /input --config /config.yml --output /output \
  --include "*.py,*.js,*.yml" --exclude "*test*,*temp*"
```

### Dry Run (Preview Changes)
```bash
docker run --rm \
  -v "/path/to/template:/input:ro" \
  -v "/path/to/config.yml:/config.yml:ro" \
  ghcr.io/mkuhl/customizer:latest \
  process --project /input --config /config.yml \
  --dry-run --verbose
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

### Missing Configuration Values
**Symptom**: Warning messages about missing template values
**Action**: Add missing keys to configuration file
**Recovery**: Re-run with updated configuration

### Permission Errors
**Symptom**: Docker mount permission denied
**Action**: Check directory permissions and SELinux contexts
**Recovery**: Use `chmod 755` and `chcon -t container_file_t`

### Invalid Jinja2 Syntax
**Symptom**: Template rendering errors for specific files
**Action**: Review template marker syntax in reported files
**Recovery**: Fix marker syntax and re-run

### Container Pull Failure
**Symptom**: Unable to pull image
**Action**: Verify internet connectivity and registry access
**Recovery**: Use explicit tag or manual image pull

```bash
# Manual image pull
docker pull ghcr.io/mkuhl/customizer:latest
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