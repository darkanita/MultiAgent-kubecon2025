#!/bin/bash
set -e

echo "🚀 Setting up Multi-Agent KubeCon 2025 Development Environment..."

# Install Azure Developer CLI (azd)
echo "📦 Installing Azure Developer CLI (azd)..."
curl -fsSL https://aka.ms/install-azd.sh | bash

# Add azd to PATH for current session
export PATH=$PATH:/home/vscode/.azd/bin

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -e .

# Install development tools
echo "🔧 Installing development tools..."
pip install black pylint pytest pytest-asyncio httpx

# Verify installations
echo ""
echo "✅ Installation complete! Verifying tools..."
echo ""

echo "Python version:"
python --version

echo ""
echo "Azure CLI version:"
az version --output table

echo ""
echo "Azure Developer CLI version:"
~/.azd/bin/azd version

echo ""
echo "kubectl version:"
kubectl version --client

echo ""
echo "Docker version:"
docker --version

echo ""
echo "Helm version:"
helm version

echo ""
echo "📚 Installed Python packages:"
pip list | grep -E "semantic-kernel|fastapi|uvicorn|azure"

echo ""
echo "🎉 Development environment is ready!"
echo ""
echo "📖 Quick Start:"
echo "  1. Login to Azure: az login --use-device-code"
echo "  2. Set subscription: az account set --subscription <subscription-id>"
echo "  3. Initialize AZD: azd auth login --use-device-code"
echo "  4. Deploy infrastructure: azd up"
echo "  5. Run locally: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📝 See DEPLOYMENT.md for detailed instructions"
echo ""
