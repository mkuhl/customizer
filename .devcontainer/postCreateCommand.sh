#!/bin/bash
set -e

echo "🔧 Setting up Template Customizer development environment..."

echo "🐳 Fixing Docker permissions..."
sudo chown root:docker /var/run/docker.sock
sudo chmod 660 /var/run/docker.sock

echo "🔑 Fixing SSH permissions..."
if [ -d "/home/vscode/.ssh" ]; then
    sudo chown -R vscode:vscode /home/vscode/.ssh
    chmod 700 /home/vscode/.ssh
    find /home/vscode/.ssh -type f -exec chmod 600 {} \; 2>/dev/null || true
fi

echo "🤖 Installing Claude Code globally..."
npm install -g @anthropic-ai/claude-code

echo "🐍 Setting up Python environment..."
cd /workspace
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

echo "🧪 Running initial tests to verify setup..."
python -m pytest tests/test_basic.py -v

echo "✅ Template Customizer development environment setup complete!"
echo ""
echo "🚀 You can now use:"
echo "   ./customize --help                    # Show CLI help"
echo "   ./customize info                      # Show supported file types"
echo "   ./customize process --help            # Show process command options"
echo ""
echo "🧪 To run tests:"
echo "   python -m pytest                     # Run all tests"
echo "   python -m pytest tests/ -v           # Run tests with verbose output"
echo ""
echo "💡 Claude Code is available for AI-assisted development!"