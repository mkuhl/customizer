#!/bin/bash
set -e

# Docker publish script for GitHub Container Registry (GHCR)
# This script builds and publishes Docker images to ghcr.io/mkuhl/customizer

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
DRY_RUN=false
FORCE_VERSION=""
REGISTRY="ghcr.io/mkuhl/customizer"

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to show usage
show_usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Build and publish Docker images to GitHub Container Registry (GHCR).

OPTIONS:
    --dry-run           Build images but don't push to registry
    --version VERSION   Force specific version (overrides auto-detection)
    --help              Show this help message

EXAMPLES:
    # Build and push current version
    $0

    # Build only, don't push (dry run)
    $0 --dry-run

    # Force specific version
    $0 --version 0.2.0

AUTHENTICATION:
    This script requires authentication to GHCR. Use one of:
    1. GitHub CLI: 'gh auth login' (recommended)
    2. Docker login: 'docker login ghcr.io'
    3. Environment variable: GITHUB_TOKEN

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN=true
            shift
            ;;
        --version)
            FORCE_VERSION="$2"
            shift 2
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if uv is available
if ! command -v uv &> /dev/null; then
    print_error "uv is required but not found. Please install uv first."
    exit 1
fi

# Check if docker is available
if ! command -v docker &> /dev/null; then
    print_error "Docker is required but not found. Please install Docker first."
    exit 1
fi

# Check authentication if not dry run
if [ "$DRY_RUN" = false ]; then
    print_info "Checking GHCR authentication..."
    
    # Try GitHub CLI first
    if command -v gh &> /dev/null && gh auth status &> /dev/null; then
        print_success "Authenticated via GitHub CLI"
        # Login to Docker registry using gh token
        echo "$(gh auth token)" | docker login ghcr.io -u "$(gh api user --jq .login)" --password-stdin
    elif [ -n "$GITHUB_TOKEN" ]; then
        print_success "Using GITHUB_TOKEN environment variable"
        echo "$GITHUB_TOKEN" | docker login ghcr.io -u "$(echo "$GITHUB_TOKEN" | base64 -d | jq -r .login 2>/dev/null || echo "token")" --password-stdin
    else
        print_warning "No authentication found. Attempting docker login check..."
        if ! docker system info | grep -q "ghcr.io"; then
            print_error "Not authenticated to GHCR. Please use one of:"
            echo "  1. gh auth login"
            echo "  2. docker login ghcr.io"
            echo "  3. export GITHUB_TOKEN=your_token"
            exit 1
        fi
        print_success "Docker already authenticated to GHCR"
    fi
fi

# Extract version information
print_info "Extracting version information..."
if [ -n "$FORCE_VERSION" ]; then
    VERSION="$FORCE_VERSION"
    print_warning "Using forced version: $VERSION"
    # Generate tags for forced version (simplified logic)
    if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        TAGS="$VERSION latest"
    else
        TAGS="$VERSION dev"
    fi
else
    VERSION=$(uv run python scripts/get-version.py version)
    TAGS=$(uv run python scripts/get-version.py tags)
fi

print_success "Version: $VERSION"
print_success "Tags: $TAGS"

# Build the Docker image
print_info "Building Docker image..."
docker build \
    -f docker/Dockerfile \
    --build-arg VERSION="$VERSION" \
    -t "$REGISTRY:$VERSION" \
    .

# Tag with additional tags
for tag in $TAGS; do
    if [ "$tag" != "$VERSION" ]; then
        print_info "Tagging as: $REGISTRY:$tag"
        docker tag "$REGISTRY:$VERSION" "$REGISTRY:$tag"
    fi
done

print_success "Build complete!"

# Show built images
echo ""
print_info "Built images:"
docker images "$REGISTRY" --format "table {{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedAt}}"

# Push images if not dry run
if [ "$DRY_RUN" = true ]; then
    echo ""
    print_warning "DRY RUN: Images built but not pushed to registry"
    print_info "To push these images, run without --dry-run flag"
else
    echo ""
    print_info "Pushing images to GHCR..."
    
    for tag in $TAGS; do
        print_info "Pushing: $REGISTRY:$tag"
        docker push "$REGISTRY:$tag"
    done
    
    print_success "All images pushed successfully!"
    echo ""
    print_success "🌐 Images available at: https://github.com/mkuhl/customizer/pkgs/container/customizer"
    echo ""
    print_info "Pull with:"
    for tag in $TAGS; do
        echo "  docker pull $REGISTRY:$tag"
    done
fi

echo ""
print_success "Operation completed successfully!"