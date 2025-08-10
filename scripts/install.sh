#!/bin/bash
set -e

# Template Customizer - One-liner Installation Script
# Usage: curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh
# Or: curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh -s -- --help

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Configuration
REPO="mkuhl/customizer"
BINARY_NAME="customizer"
INSTALL_DIR="/usr/local/bin"
TMP_DIR="/tmp/customizer-install-$$"

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
    echo -e "${RED}❌ $1${NC}" >&2
}

print_header() {
    echo -e "${BOLD}${BLUE}"
    echo "╭─────────────────────────────────────────────╮"
    echo "│         Template Customizer Installer      │"
    echo "│           Fast • Native • Reliable          │"
    echo "╰─────────────────────────────────────────────╯"
    echo -e "${NC}"
}

show_help() {
    cat << 'EOF'
Template Customizer Installation Script

USAGE:
    curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh

OPTIONS:
    --help                Show this help message
    --version VERSION     Install specific version (default: latest)
    --dir DIRECTORY       Install to specific directory (default: /usr/local/bin)
    --no-verify           Skip checksum verification
    --force              Overwrite existing installation

EXAMPLES:
    # Install latest version
    curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh
    
    # Install to custom directory
    curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh -s -- --dir ~/.local/bin
    
    # Install specific version
    curl -fsSL https://github.com/mkuhl/customizer/releases/latest/download/install.sh | sh -s -- --version v0.1.6

SYSTEM REQUIREMENTS:
    - Linux x86_64 (Ubuntu 20.04+, RHEL 8+, Debian 11+, or compatible)
    - GLIBC 2.31 or newer
    - curl or wget
    - tar (for extraction)

WHAT THIS SCRIPT DOES:
    1. Detects your system architecture and OS
    2. Downloads the appropriate binary from GitHub Releases
    3. Verifies the download with SHA256 checksum
    4. Installs to /usr/local/bin (or specified directory)
    5. Makes the binary executable
    6. Verifies installation success

For more information, visit: https://github.com/mkuhl/customizer
EOF
}

# Parse command line arguments
VERSION=""
NO_VERIFY=false
FORCE=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            exit 0
            ;;
        --version)
            VERSION="$2"
            shift 2
            ;;
        --dir)
            INSTALL_DIR="$2"
            shift 2
            ;;
        --no-verify)
            NO_VERIFY=true
            shift
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            print_info "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Cleanup function
cleanup() {
    if [[ -d "$TMP_DIR" ]]; then
        rm -rf "$TMP_DIR"
    fi
}
trap cleanup EXIT

# System detection
detect_system() {
    print_info "Detecting system architecture..."
    
    # Detect OS
    case "$(uname -s)" in
        Linux*)
            OS="linux"
            ;;
        Darwin*)
            print_error "macOS support not yet available. Linux x86_64 only for now."
            exit 1
            ;;
        CYGWIN*|MINGW*|MSYS*)
            print_error "Windows support not yet available. Linux x86_64 only for now."
            exit 1
            ;;
        *)
            print_error "Unsupported operating system: $(uname -s)"
            exit 1
            ;;
    esac
    
    # Detect architecture
    case "$(uname -m)" in
        x86_64|amd64)
            ARCH="x64"
            ;;
        aarch64|arm64)
            print_error "ARM64 support not yet available. x86_64 only for now."
            exit 1
            ;;
        *)
            print_error "Unsupported architecture: $(uname -m)"
            print_error "Only x86_64 is currently supported."
            exit 1
            ;;
    esac
    
    print_success "Detected: $OS-$ARCH"
    
    # Check GLIBC version
    if command -v ldd >/dev/null 2>&1; then
        GLIBC_VERSION=$(ldd --version | head -1 | grep -o '[0-9]\+\.[0-9]\+' | head -1)
        if [[ -n "$GLIBC_VERSION" ]]; then
            print_info "GLIBC version: $GLIBC_VERSION"
            # Check if GLIBC is >= 2.31
            if ! printf '%s\n%s\n' "2.31" "$GLIBC_VERSION" | sort -V -C; then
                print_warning "GLIBC $GLIBC_VERSION detected. Minimum required: 2.31"
                print_warning "The binary may not work on this system."
            fi
        fi
    fi
}

# Check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check for required tools
    local missing_tools=()
    
    if ! command -v curl >/dev/null 2>&1 && ! command -v wget >/dev/null 2>&1; then
        missing_tools+=("curl or wget")
    fi
    
    if ! command -v tar >/dev/null 2>&1; then
        missing_tools+=("tar")
    fi
    
    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        print_error "Missing required tools: ${missing_tools[*]}"
        case "$(uname -s)" in
            Linux*)
                if command -v apt-get >/dev/null 2>&1; then
                    print_info "Install with: sudo apt-get update && sudo apt-get install curl tar"
                elif command -v yum >/dev/null 2>&1; then
                    print_info "Install with: sudo yum install curl tar"
                elif command -v dnf >/dev/null 2>&1; then
                    print_info "Install with: sudo dnf install curl tar"
                fi
                ;;
        esac
        exit 1
    fi
    
    print_success "All prerequisites satisfied"
}

# Get latest version from GitHub API
get_latest_version() {
    print_info "Getting latest version information..."
    
    local api_url="https://api.github.com/repos/$REPO/releases/latest"
    local version_info
    
    if command -v curl >/dev/null 2>&1; then
        version_info=$(curl -fsSL "$api_url" 2>/dev/null)
    elif command -v wget >/dev/null 2>&1; then
        version_info=$(wget -qO- "$api_url" 2>/dev/null)
    else
        print_error "Neither curl nor wget available for API request"
        exit 1
    fi
    
    if [[ -z "$version_info" ]]; then
        print_error "Failed to get version information from GitHub API"
        print_info "Using fallback version detection..."
        VERSION="latest"
        return
    fi
    
    # Extract version tag from JSON response
    VERSION=$(echo "$version_info" | grep '"tag_name":' | sed -E 's/.*"tag_name": "([^"]+)".*/\1/')
    
    if [[ -z "$VERSION" ]]; then
        print_warning "Could not parse version from API response, using 'latest'"
        VERSION="latest"
    else
        print_success "Latest version: $VERSION"
    fi
}

# Download and install
download_and_install() {
    print_info "Creating temporary directory..."
    mkdir -p "$TMP_DIR"
    cd "$TMP_DIR"
    
    # Construct download URLs
    local base_url="https://github.com/$REPO/releases"
    local download_url
    local checksum_url
    
    if [[ "$VERSION" == "latest" ]]; then
        download_url="$base_url/latest/download/${BINARY_NAME}-${OS}-${ARCH}.tar.gz"
        checksum_url="$base_url/latest/download/checksums.txt"
    else
        download_url="$base_url/download/$VERSION/${BINARY_NAME}-${OS}-${ARCH}.tar.gz"
        checksum_url="$base_url/download/$VERSION/checksums.txt"
    fi
    
    print_info "Downloading $BINARY_NAME from $download_url..."
    
    # Download binary archive
    if command -v curl >/dev/null 2>&1; then
        if ! curl -fsSL -o "${BINARY_NAME}-${OS}-${ARCH}.tar.gz" "$download_url"; then
            print_error "Failed to download binary archive"
            exit 1
        fi
    elif command -v wget >/dev/null 2>&1; then
        if ! wget -q -O "${BINARY_NAME}-${OS}-${ARCH}.tar.gz" "$download_url"; then
            print_error "Failed to download binary archive"
            exit 1
        fi
    fi
    
    print_success "Downloaded binary archive"
    
    # Download and verify checksum if not skipped
    if [[ "$NO_VERIFY" != true ]]; then
        print_info "Downloading checksums for verification..."
        
        if command -v curl >/dev/null 2>&1; then
            curl -fsSL -o checksums.txt "$checksum_url" 2>/dev/null || print_warning "Could not download checksums"
        elif command -v wget >/dev/null 2>&1; then
            wget -q -O checksums.txt "$checksum_url" 2>/dev/null || print_warning "Could not download checksums"
        fi
        
        if [[ -f checksums.txt ]] && command -v sha256sum >/dev/null 2>&1; then
            print_info "Verifying checksum..."
            if grep "${BINARY_NAME}-${OS}-${ARCH}.tar.gz" checksums.txt | sha256sum -c --quiet; then
                print_success "Checksum verification passed"
            else
                print_error "Checksum verification failed!"
                print_error "The downloaded file may be corrupted or tampered with."
                exit 1
            fi
        else
            print_warning "Skipping checksum verification (sha256sum not available)"
        fi
    else
        print_warning "Skipping checksum verification (--no-verify specified)"
    fi
    
    # Extract binary
    print_info "Extracting binary..."
    if ! tar -xzf "${BINARY_NAME}-${OS}-${ARCH}.tar.gz"; then
        print_error "Failed to extract binary archive"
        exit 1
    fi
    
    if [[ ! -f "$BINARY_NAME" ]]; then
        print_error "Binary not found in archive"
        exit 1
    fi
    
    print_success "Binary extracted successfully"
    
    # Check if binary already exists
    if [[ -f "$INSTALL_DIR/$BINARY_NAME" ]] && [[ "$FORCE" != true ]]; then
        print_warning "$BINARY_NAME already exists in $INSTALL_DIR"
        print_info "Current version: $($INSTALL_DIR/$BINARY_NAME --version 2>/dev/null || echo 'unknown')"
        print_info "Use --force to overwrite, or choose a different --dir"
        
        read -p "Overwrite existing installation? [y/N]: " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Installation cancelled"
            exit 0
        fi
    fi
    
    # Create install directory if it doesn't exist
    if [[ ! -d "$INSTALL_DIR" ]]; then
        print_info "Creating install directory: $INSTALL_DIR"
        if ! mkdir -p "$INSTALL_DIR" 2>/dev/null; then
            print_error "Cannot create directory $INSTALL_DIR"
            print_info "Try running with sudo, or use --dir to specify a writable directory"
            exit 1
        fi
    fi
    
    # Install binary
    print_info "Installing $BINARY_NAME to $INSTALL_DIR..."
    if ! cp "$BINARY_NAME" "$INSTALL_DIR/$BINARY_NAME" 2>/dev/null; then
        print_error "Cannot write to $INSTALL_DIR"
        print_info "Try running with sudo, or use --dir to specify a writable directory"
        exit 1
    fi
    
    # Make executable
    chmod +x "$INSTALL_DIR/$BINARY_NAME"
    
    print_success "Installation completed!"
}

# Verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    # Check if binary is executable
    if [[ ! -x "$INSTALL_DIR/$BINARY_NAME" ]]; then
        print_error "Binary is not executable"
        exit 1
    fi
    
    # Test binary execution
    local version_output
    if version_output=$("$INSTALL_DIR/$BINARY_NAME" --version 2>&1); then
        print_success "Installation verified: $version_output"
    else
        print_error "Binary installed but not working correctly"
        print_error "Output: $version_output"
        exit 1
    fi
    
    # Check if binary is in PATH
    if command -v "$BINARY_NAME" >/dev/null 2>&1; then
        print_success "$BINARY_NAME is available in PATH"
    else
        print_warning "$BINARY_NAME is not in PATH"
        print_info "Add $INSTALL_DIR to your PATH to use '$BINARY_NAME' directly"
        print_info "Or run: export PATH=\"$INSTALL_DIR:\$PATH\""
        
        # Check common shell config files
        local shell_config=""
        if [[ -n "$BASH_VERSION" ]] && [[ -f "$HOME/.bashrc" ]]; then
            shell_config="$HOME/.bashrc"
        elif [[ -n "$ZSH_VERSION" ]] && [[ -f "$HOME/.zshrc" ]]; then
            shell_config="$HOME/.zshrc"
        elif [[ -f "$HOME/.profile" ]]; then
            shell_config="$HOME/.profile"
        fi
        
        if [[ -n "$shell_config" ]] && [[ "$INSTALL_DIR" != "/usr/local/bin" ]]; then
            print_info "To permanently add to PATH, add this line to $shell_config:"
            echo "    export PATH=\"$INSTALL_DIR:\$PATH\""
        fi
    fi
}

# Show completion message
show_completion() {
    echo -e "${BOLD}${GREEN}"
    echo "╭─────────────────────────────────────────────╮"
    echo "│          🎉 Installation Complete! 🎉       │"
    echo "╰─────────────────────────────────────────────╯"
    echo -e "${NC}"
    
    print_info "Template Customizer is now installed!"
    echo
    print_info "Quick start:"
    echo "  $BINARY_NAME --help               # Show help"
    echo "  $BINARY_NAME info                 # Show supported file types"
    echo "  $BINARY_NAME version              # Show version"
    echo "  $BINARY_NAME process --dry-run    # Preview template processing"
    echo
    print_info "Documentation: https://github.com/$REPO"
    print_info "Report issues: https://github.com/$REPO/issues"
}

# Main execution
main() {
    print_header
    
    detect_system
    check_prerequisites
    
    # Get version if not specified
    if [[ -z "$VERSION" ]]; then
        get_latest_version
    else
        print_info "Installing version: $VERSION"
    fi
    
    download_and_install
    verify_installation
    show_completion
}

# Run main function
main "$@"