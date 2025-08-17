# Template Customizer Scripts

This directory contains scripts for building, managing, and automating releases of the Template Customizer with centralized version management.

## Release Automation System

The `release-automation.py` script provides a generic, extensible framework for automating release-related tasks that need to happen during releases (like updating version badges, changelogs, etc.).

### Available Tasks
- **`update-version-badge`** - Updates version badge in README.md
- **`update-changelog`** - Updates CHANGELOG.md (placeholder for future implementation)
- **`update-docker-tags`** - Updates Docker documentation (placeholder for future implementation)

### Usage
```bash
# List available automation tasks
python scripts/release-automation.py list

# Run specific task
python scripts/release-automation.py update-version-badge 0.4.0

# Run all automation tasks  
python scripts/release-automation.py all 0.4.0
```

### Adding New Tasks
To add a new release automation task:

1. Add a new method to the `ReleaseAutomation` class in `release-automation.py`
2. Register it in the `self.tasks` dictionary in `__init__`
3. The method should return `Tuple[bool, str]` (success, message)

Example:
```python
def update_my_feature(self, version: str) -> Tuple[bool, str]:
    # Your automation logic here
    return True, f"My feature updated to {version}"

# In __init__:
self.tasks['update-my-feature'] = self.update_my_feature
```

## Version Management

The version is centrally managed in `src/template_customizer/__init__.py` as the single source of truth. All other components (CLI, Docker images, GitHub releases) dynamically reference this version.

### Scripts

#### `get-version.py`
Extracts version information from the source code for use in CI/CD pipelines.

**Usage:**
```bash
# Get version string
uv run python scripts/get-version.py version
# Output: 0.1.0

# Get Docker tags for this version
uv run python scripts/get-version.py tags  
# Output: 0.1.0 latest 0.1

# Get detailed version info
uv run python scripts/get-version.py info
# Output: version=0.1.0, major=0, minor=1, patch=0, is_release=True
```

#### `docker-build.sh`
Builds Docker images with proper version handling and tagging.

**Usage:**
```bash
./scripts/docker-build.sh
```

**Features:**
- Extracts version automatically from source
- Builds image with version as build argument
- Tags image with appropriate tags (version, latest, major.minor)
- Shows build summary and test commands

#### `docker-compose-build.sh`
Builds using docker-compose with version support.

**Usage:**
```bash
./scripts/docker-compose-build.sh
```

#### `docker-run.sh`
Runs template-customizer via Docker with directory mounting and interactive support.

**Usage:**
```bash
# Run with default template directory (current directory)
./scripts/docker-run.sh process --dry-run

# Run with custom template directory
TEMPLATE_DIR=/path/to/template ./scripts/docker-run.sh process --yes

# Show help
./scripts/docker-run.sh --help

# Show version
./scripts/docker-run.sh version
```

**Features:**
- Automatically mounts template directory to `/workdir` in container
- Supports interactive confirmation prompts with `-it` flags
- Auto-detects config files in template directory
- Uses versioned Docker images with fallback to `latest`
- Environment variable `TEMPLATE_DIR` sets the template directory to mount

## Version Flow

1. **Source of Truth**: `src/template_customizer/__init__.py` contains `__version__ = "x.y.z"`
2. **CLI**: Dynamically imports and displays version
3. **Docker**: Build argument passes version to image labels
4. **GitHub Actions**: Scripts extract version for releases and tagging

## GitHub Actions Integration

The version extraction script is designed for GitHub Actions workflows:

```yaml
- name: Get version
  id: version
  run: echo "version=$(uv run python scripts/get-version.py version)" >> $GITHUB_OUTPUT

- name: Get Docker tags
  id: tags
  run: echo "tags=$(uv run python scripts/get-version.py tags)" >> $GITHUB_OUTPUT

- name: Build Docker image
  run: |
    docker build \
      --build-arg VERSION=${{ steps.version.outputs.version }} \
      -t ghcr.io/owner/template-customizer:${{ steps.version.outputs.version }} \
      .
```

## Release Process

1. Update version in `src/template_customizer/__init__.py`
2. Scripts automatically detect new version
3. Docker images get proper version labels
4. GitHub releases can be triggered on version changes

## Version Tagging Strategy

- **Development versions** (with alpha, beta, rc, dev): Tagged as `dev`
- **Release versions**: Tagged as `latest`, `major.minor`, and exact version
- **Major releases** (>= 1.0.0): Also tagged with major version number

Examples:
- `0.1.0` → tags: `0.1.0`, `latest`, `0.1`
- `1.2.3` → tags: `1.2.3`, `latest`, `1.2`, `1`
- `0.2.0-alpha1` → tags: `0.2.0-alpha1`, `dev`