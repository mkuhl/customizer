#!/bin/bash
set -e

# Template Customizer Native Build Script
# Builds a standalone Linux executable using PyInstaller

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions for colored output
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

# Script configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DIST_DIR="$PROJECT_ROOT/dist/native"
BINARY_NAME="customizer"

# Change to project root
cd "$PROJECT_ROOT"

print_info "Building native executable for Template Customizer..."
print_info "Project root: $PROJECT_ROOT"

# Check for virtual environment
if [ ! -d ".venv" ]; then
    print_error "Virtual environment not found!"
    print_info "Creating virtual environment..."
    uv venv
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source .venv/bin/activate

# Install project and dependencies
print_info "Installing project dependencies..."
uv pip install -e ".[dev]"

# Install PyInstaller
print_info "Installing PyInstaller..."
uv pip install pyinstaller

# Clean previous builds
print_info "Cleaning previous builds..."
rm -rf build/ dist/ 

# Create distribution directory
mkdir -p "$DIST_DIR"

# Build with PyInstaller using spec file
print_info "Building native executable with PyInstaller..."
if [ -f "template-customizer.spec" ]; then
    print_info "Using spec file: template-customizer.spec"
    pyinstaller \
        --clean \
        --distpath "$DIST_DIR" \
        --workpath ./build \
        template-customizer.spec
else
    print_warning "Spec file not found, using command-line options..."
    pyinstaller \
        --onefile \
        --name "$BINARY_NAME" \
        --strip \
        --clean \
        --distpath "$DIST_DIR" \
        --workpath ./build \
        --optimize 2 \
        --exclude-module tkinter \
        --exclude-module matplotlib \
        --exclude-module numpy \
        --exclude-module pandas \
        --exclude-module scipy \
        --exclude-module PIL \
        --exclude-module sqlite3 \
        --exclude-module test \
        --exclude-module tests \
        --exclude-module unittest \
        --exclude-module xmlrpc \
        --exclude-module email \
        --exclude-module distutils \
        src/template_customizer/cli.py
fi

# Check binary size
print_info "Binary size: $(du -h "$DIST_DIR/$BINARY_NAME" | cut -f1)"

# Test the binary
print_info "Testing the native binary..."

# Basic tests
echo ""
print_info "Version check:"
"$DIST_DIR/$BINARY_NAME" --version

echo ""
print_info "Help output:"
"$DIST_DIR/$BINARY_NAME" --help | head -20

echo ""
print_info "Info command:"
"$DIST_DIR/$BINARY_NAME" info

# Check file size
FILE_SIZE=$(du -h "$DIST_DIR/$BINARY_NAME" | cut -f1)
print_success "Native binary built successfully!"
print_info "Binary location: $DIST_DIR/$BINARY_NAME"
print_info "Binary size: $FILE_SIZE"

# Generate SHA256 checksum
print_info "Generating checksum..."
cd "$DIST_DIR"
sha256sum "$BINARY_NAME" > "$BINARY_NAME.sha256"
print_info "Checksum: $(cat $BINARY_NAME.sha256)"

# Create tarball for distribution
print_info "Creating distribution archive..."
tar -czf "$BINARY_NAME-linux-x64.tar.gz" "$BINARY_NAME" "$BINARY_NAME.sha256"
print_success "Distribution archive created: $BINARY_NAME-linux-x64.tar.gz"

echo ""
print_success "Build complete! 🎉"
print_info "To test the binary directly:"
echo "  $DIST_DIR/$BINARY_NAME --help"
print_info "To test with a project:"
echo "  $DIST_DIR/$BINARY_NAME process --project ./examples/simple --dry-run"