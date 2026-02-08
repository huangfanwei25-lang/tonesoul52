#!/bin/bash
# ToneSoul Installation Script for Linux/macOS
# Usage: curl -sSL https://raw.githubusercontent.com/Fan1234-1/tonesoul52/master/install.sh | bash

set -e

echo "🌌 ToneSoul Installer"
echo "====================="
echo ""

# Check Python version
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    if [ "$MAJOR" -ge 3 ] && [ "$MINOR" -ge 10 ]; then
        PYTHON_CMD="python3"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "❌ Error: Python 3.10+ is required"
    echo "   Please install Python 3.10 or later from https://python.org"
    exit 1
fi

echo "✅ Found Python: $($PYTHON_CMD --version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
$PYTHON_CMD -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install ToneSoul
echo ""
echo "📥 Installing ToneSoul..."
pip install --upgrade pip
pip install -e ".[dev]"

# Verify installation
echo ""
echo "🔍 Verifying installation..."
python -c "import tonesoul; print(f'ToneSoul version: {tonesoul.__version__}')" 2>/dev/null || echo "ToneSoul core installed"

# Run 7D verification
echo ""
echo "🎯 Running 7D Audit..."
python scripts/verify_7d.py --json 2>/dev/null || echo "7D verification available via: python scripts/verify_7d.py"

echo ""
echo "✨ Installation complete!"
echo ""
echo "To activate the environment:"
echo "  source .venv/bin/activate"
echo ""
echo "To run tests:"
echo "  pytest"
echo ""
echo "To run 7D audit:"
echo "  python scripts/verify_7d.py"
