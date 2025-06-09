#!/bin/bash
set -e

# Docker build script with dynamic versioning
# This script builds the Docker image with proper version handling

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Extract version from source code
echo "🔍 Extracting version from source..."
VERSION=$(uv run python scripts/get-version.py version)
echo "📦 Building version: $VERSION"

# Get appropriate Docker tags
TAGS=($(uv run python scripts/get-version.py tags))
echo "🏷️  Docker tags: ${TAGS[*]}"

# Build the Docker image with version
echo "🐳 Building Docker image..."
docker build \
    -f docker/Dockerfile \
    --build-arg VERSION="$VERSION" \
    -t "template-customizer:$VERSION" \
    .

# Tag with additional tags
for tag in "${TAGS[@]}"; do
    if [ "$tag" != "$VERSION" ]; then
        echo "🏷️  Tagging as: template-customizer:$tag"
        docker tag "template-customizer:$VERSION" "template-customizer:$tag"
    fi
done

echo "✅ Build complete!"
echo "📋 Available images:"
docker images template-customizer --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

echo ""
echo "🧪 Test the image:"
echo "   docker run --rm template-customizer:$VERSION --version"
echo "   docker run --rm template-customizer:$VERSION info"
echo ""
echo "🚀 Run with your templates:"
echo "   # From your template directory:"
echo "   ./scripts/docker-run.sh --config config.yml --dry-run"