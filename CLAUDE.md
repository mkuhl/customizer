# Template Customizer - Claude Instructions

## Project Context
This is the **Template Customizer** - a standalone Python tool for customizing project templates using comment-based markers. This is now an independent project focused solely on template processing capabilities.

## Key Project Information
- **Language**: Python 3.8+
- **CLI Framework**: Click (not argparse)
- **UI Enhancement**: Rich for progress bars, colors, and formatting
- **Template Engine**: Jinja2
- **Config Format**: YAML/JSON support
- **Package Manager**: Use `uv` (consistent with parent project)

## Core Architecture
```
customizer/
├── src/template_customizer/
│   ├── cli.py                 # Click-based CLI entry point
│   ├── core/
│   │   ├── scanner.py         # File discovery and filtering
│   │   ├── parser.py          # Comment marker extraction
│   │   ├── processor.py       # Template rendering and file processing
│   │   └── writer.py          # Safe file writing with backups
│   └── utils/
│       ├── file_types.py      # File type detection and comment syntax
│       └── validation.py      # Parameter and template validation
└── tests/                     # Comprehensive test suite
```

## Development Guidelines

### CLI Design with Click
- Use Click decorators for commands and options
- Implement rich help formatting
- Support both short and long option forms
`- Use Click's built-in validation where possible
`
### Rich Integration
- Use Rich progress bars for file processing
- Implement colored output for different message types:
  - Green: Success/completion
  - Yellow: Warnings
  - Red: Errors
  - Blue: Information
- Use Rich tables for change summaries
- Implement rich console output for dry-run previews

### Template Marker Format
The tool processes comment-based markers in this format:
```python
# variable_name = {{ jinja2_expression }}
actual_value = "default_value"
```

### File Type Support
Support comment syntax for:
- Python/Shell: `# marker = {{ expr }}`
- JavaScript/TypeScript: `// marker = {{ expr }}`
- CSS: `/* marker = {{ expr }} */`
- HTML/XML: `<!-- marker = {{ expr }} -->`
- YAML: `# marker = {{ expr }}`
- Dockerfile: `# marker = {{ expr }}`

### Safety Requirements
- Always preserve comment lines unchanged
- Implement dry-run mode for preview
- Create file backups before modifications
- Validate Jinja2 syntax before processing
- Handle missing variables gracefully

### Testing Strategy
- Unit tests for each component
- Integration tests with sample projects
- Performance tests for large directories
- Error handling and edge case tests
- Real-world validation with py-ang project

## Command Structure
```bash
# Basic usage with rich output
template-customizer process --project ./template --config ./config.yml

# Dry run with detailed preview
template-customizer process --project ./template --config ./config.yml --dry-run

# With filtering and verbose rich output
template-customizer process --project ./template --config ./config.yml \
  --include "*.py,*.js,*.yml" --exclude "*test*" --verbose
```

## Configuration File Example
```yaml
# customizer-config.yml
project:
  name: "MyAwesome App"
  version: "1.2.0"
  description: "Built from py-ang template"

docker:
  registry: "myregistry.com"
  image_name: "myapp"

api:
  base_url: "https://api.myapp.com"
  version: "v1"
```

## Validation with Parent Project
Use the py-ang project as validation target by:
1. Adding template markers to key files
2. Creating configuration for customization
3. Running customizer and verifying results
4. Ensuring customized project still builds/runs

## Dependencies
- **jinja2**: Template rendering
- **pyyaml**: YAML configuration parsing
- **click**: Modern CLI framework
- **rich**: Beautiful terminal output
- **pathlib**: File system operations (built-in)

## Important Notes
- This is a **standalone project** - no dependencies on parent py-ang
- Use `uv` for Python package management
- Focus on user experience with rich output
- Maintain comprehensive test coverage
- Document all rich formatting features

## Git Commits
- Keep them short and concise. Single line for trivial changes, max 3 additional lines with details only when necessary
- Do NOT add "co-authored..." comments to any commits
- Only commit when explicitly asked to do so by the user
- NEVER commit to master unless specifically asked to do so. Changes to master should always be merged from feature branches
- When committing, use simple commit messages without the automated "Generated with Claude Code" footer