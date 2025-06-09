#!/bin/bash
set -e

# Docker run script with TEMPLATE_DIR mounting
# This script runs template-customizer via Docker with directory mounting

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Set TEMPLATE_DIR to $PWD if not already set
TEMPLATE_DIR="${TEMPLATE_DIR:-$PWD}"

echo "🐳 Running template-customizer via Docker..."
echo "   Template directory: $TEMPLATE_DIR"
echo "   Arguments: $*"

# Get the latest image tag
cd "$REPO_ROOT"
if command -v python >/dev/null 2>&1 && [ -f "scripts/get-version.py" ]; then
    VERSION=$(uv run python scripts/get-version.py version 2>/dev/null || echo "latest")
else
    VERSION="latest"
fi

IMAGE_NAME="template-customizer:$VERSION"

# Check if the image exists
if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
    echo "🔍 Image $IMAGE_NAME not found, trying 'latest'..."
    IMAGE_NAME="template-customizer:latest"
    if ! docker image inspect "$IMAGE_NAME" >/dev/null 2>&1; then
        echo "❌ Error: Docker image not found. Please build it first:"
        echo "   ./scripts/docker-build.sh"
        exit 1
    fi
fi

echo "   Using image: $IMAGE_NAME"

# Run the container with mounted template directory
# The entrypoint automatically sets --project /workdir, so we just pass commands
# Use -it for interactive mode to support confirmation prompts
docker run \
    --rm \
    -it \
    --volume "$TEMPLATE_DIR:/workdir" \
    "$IMAGE_NAME" \
    "$@"

echo "✅ Done!"