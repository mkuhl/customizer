#!/bin/bash
set -e

# Docker build script with dynamic versioning
# This script builds the Docker image with proper version handling
# Supports both local and registry builds via DOCKER_REGISTRY env var

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Default registry/image name (can be overridden with DOCKER_REGISTRY env var)
DEFAULT_IMAGE_NAME="template-customizer"
REGISTRY="${DOCKER_REGISTRY:-$DEFAULT_IMAGE_NAME}"

# Extract version from source code
echo "🔍 Extracting version from source..."
VERSION=$(uv run python scripts/get-version.py version)
echo "📦 Building version: $VERSION"
echo "🏷️  Registry/Image: $REGISTRY"

# Get appropriate Docker tags
TAGS=($(uv run python scripts/get-version.py tags))
echo "🏷️  Docker tags: ${TAGS[*]}"

# Build the Docker image with version
echo "🐳 Building Docker image..."
docker build \
    -f docker/Dockerfile \
    --build-arg VERSION="$VERSION" \
    -t "$REGISTRY:$VERSION" \
    .

# Tag with additional tags
for tag in "${TAGS[@]}"; do
    if [ "$tag" != "$VERSION" ]; then
        echo "🏷️  Tagging as: $REGISTRY:$tag"
        docker tag "$REGISTRY:$VERSION" "$REGISTRY:$tag"
    fi
done

echo "✅ Build complete!"
echo "📋 Available images:"

# Extract base image name for filtering (remove registry prefix if present)
BASE_NAME="${REGISTRY##*/}"
if [[ "$REGISTRY" == *"/"* ]]; then
    # If using a registry, show all images with that registry
    docker images "$REGISTRY" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
else
    # If local build, show template-customizer images
    docker images template-customizer --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"
fi

echo ""
echo "🧪 Test the image:"
echo "   docker run --rm $REGISTRY:$VERSION --version"
echo "   docker run --rm $REGISTRY:$VERSION info"
echo ""
if [[ "$REGISTRY" == *"ghcr.io"* ]]; then
    echo "🚀 Pull published image:"
    echo "   docker pull $REGISTRY:latest"
else
    echo "🚀 Run with your templates:"
    echo "   # From your template directory:"
    echo "   ./scripts/docker-run.sh --config config.yml --dry-run"
fi