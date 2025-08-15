# Docker Usage Guide

Template Customizer provides comprehensive Docker support for cross-platform compatibility and CI/CD integration. While the native binary offers faster startup times (~100ms vs 2-3s), Docker ensures consistent behavior across all platforms.

## Quick Start

### Pull the Latest Image

```bash
docker pull ghcr.io/mkuhl/customizer:latest
```

### Basic Usage

```bash
# Preview changes with auto-detected config
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run

# Apply changes
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --yes
```

## Installation Methods

### 1. Docker Wrapper Script (Recommended)

The wrapper script provides a native-like experience while using Docker internally:

```bash
# Download the Docker wrapper script  
curl -L -o run-docker-customizer.sh https://github.com/mkuhl/customizer/releases/latest/download/run-docker-customizer.sh
chmod +x run-docker-customizer.sh
sudo mv run-docker-customizer.sh /usr/local/bin/

# Verify installation (pulls Docker image on first run)
run-docker-customizer.sh --version

# Use like the native binary
run-docker-customizer.sh process --project ./template --config ./config.yml --dry-run
```

### 2. Direct Docker Commands

For integration with existing Docker workflows:

```bash
# Run with Docker directly
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run

# Or use a specific version
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:0.2.0 process --dry-run
```

## Available Images and Tags

All images are hosted on GitHub Container Registry (GHCR):

- `ghcr.io/mkuhl/customizer:latest` - Latest stable release
- `ghcr.io/mkuhl/customizer:0.2.0` - Specific version (replace with desired version)
- `ghcr.io/mkuhl/customizer:0.2` - Major.minor version tracking

### Image Details

- **Base Image**: Python 3.12 slim
- **Size**: ~150MB compressed
- **Architecture**: linux/amd64
- **Working Directory**: `/workdir`
- **User**: Non-root user for security

## Usage Examples

### Basic Template Customization

```bash
# Preview changes with auto-detected configuration
docker run --rm -v "/path/to/template:/workdir" ghcr.io/mkuhl/customizer:latest process --dry-run

# Apply changes
docker run --rm -v "/path/to/template:/workdir" ghcr.io/mkuhl/customizer:latest process --yes

# Use specific configuration file
docker run --rm -v "/path/to/template:/workdir" ghcr.io/mkuhl/customizer:latest process --config custom-config.yml --dry-run
```

### Output to Separate Directory

```bash
# Generate customized files to a separate output directory
docker run --rm \
  -v "/path/to/template:/workdir" \
  -v "/path/to/output:/output" \
  ghcr.io/mkuhl/customizer:latest process --output /output --yes
```

### Filtering and Advanced Options

```bash
# Only process Python and JavaScript files
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest \
  process --include "*.py,*.js" --dry-run

# Exclude test files
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest \
  process --exclude "*test*,*spec*" --dry-run

# Verbose output with detailed warnings
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest \
  process --verbose --dry-run
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Customize Template
on: [push]

jobs:
  customize:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Customize template
        run: |
          docker run --rm -v "${{ github.workspace }}:/workdir" \
            ghcr.io/mkuhl/customizer:latest \
            process --config .github/config.yml --yes
```

### GitLab CI Example

```yaml
customize_template:
  image: docker:latest
  services:
    - docker:dind
  script:
    - docker run --rm -v "$PWD:/workdir" 
        ghcr.io/mkuhl/customizer:latest 
        process --config gitlab-config.yml --yes
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Customize Template') {
            steps {
                sh '''
                    docker run --rm -v "$WORKSPACE:/workdir" \
                        ghcr.io/mkuhl/customizer:latest \
                        process --config jenkins-config.yml --yes
                '''
            }
        }
    }
}
```

## Volume Mounting

### Required Mounts

- **Template Directory**: Mount your template directory to `/workdir`
  ```bash
  -v "/path/to/template:/workdir"
  ```

### Optional Mounts

- **Output Directory**: Mount output directory for separate output
  ```bash
  -v "/path/to/output:/output"
  ```

- **Configuration Files**: Mount external config files
  ```bash
  -v "/path/to/configs:/configs"
  ```

### Example with Multiple Mounts

```bash
docker run --rm \
  -v "/home/user/my-template:/workdir" \
  -v "/home/user/output:/output" \
  -v "/home/user/configs:/configs" \
  ghcr.io/mkuhl/customizer:latest \
  process --config /configs/production.yml --output /output --yes
```

## Environment Variables

You can pass environment variables to customize behavior:

```bash
# Set custom working directory (if needed)
docker run --rm -e WORKDIR="/custom/workdir" \
  -v "$(pwd):/custom/workdir" \
  ghcr.io/mkuhl/customizer:latest process --dry-run
```

## Troubleshooting

### Permission Issues

If you encounter permission issues with file access:

```bash
# Run with current user ID
docker run --rm --user "$(id -u):$(id -g)" \
  -v "$(pwd):/workdir" \
  ghcr.io/mkuhl/customizer:latest process --dry-run
```

### File Not Found Errors

Ensure your paths are correctly mounted:

```bash
# Check if files are accessible inside container
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest ls -la

# Verify config file path
docker run --rm -v "$(pwd):/workdir" ghcr.io/mkuhl/customizer:latest cat config.yml
```

### Network Issues

If you can't pull the image, try:

```bash
# Pull with verbose output
docker pull ghcr.io/mkuhl/customizer:latest --verbose

# Check Docker daemon status
docker info
```

## Performance Considerations

### Startup Time Comparison

| Method | Startup Time | Best Use Case |
|--------|-------------|---------------|
| Native Binary | ~100ms ⚡ | Development, frequent use |
| Docker | ~2-3s | CI/CD, cross-platform consistency |

### Optimization Tips

1. **Use specific version tags** instead of `latest` in CI/CD for consistency
2. **Pre-pull images** in CI/CD workflows to reduce job time
3. **Use wrapper script** for native-like experience in development
4. **Mount only necessary directories** to reduce startup overhead

## Image Maintenance

### Updating

```bash
# Pull latest version
docker pull ghcr.io/mkuhl/customizer:latest

# Remove old images to save space
docker image prune
```

### Version Management

```bash
# List available tags
docker search ghcr.io/mkuhl/customizer --limit 10

# Use specific versions for stability
docker run --rm ghcr.io/mkuhl/customizer:0.2.0 --version
```

## Security Considerations

- Images run with **non-root user** by default
- **No network access** required for processing (after image download)
- **Read-only container** recommended for production use:
  ```bash
  docker run --rm --read-only -v "$(pwd):/workdir" \
    ghcr.io/mkuhl/customizer:latest process --dry-run
  ```

## Getting Help

- **Image Issues**: Report on [GitHub Issues](https://github.com/mkuhl/customizer/issues)
- **Docker Hub**: Images are available at `ghcr.io/mkuhl/customizer`
- **Version History**: Check [Releases](https://github.com/mkuhl/customizer/releases) for changelog

---

For users who want faster performance and don't need cross-platform consistency, consider using the [native binary installation method](../README.md#-one-liner-installation-easiest) instead.