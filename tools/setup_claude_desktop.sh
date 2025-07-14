#!/bin/bash

# Setup script for Claude Desktop MCP server configuration
# This script helps configure Claude Desktop to use the Ansible AAP MCP server

set -e

echo "🚀 Setting up Claude Desktop for Ansible AAP MCP Server"
echo "=================================================="

# Detect OS and set config path
if [[ "$OSTYPE" == "darwin"* ]]; then
    CONFIG_DIR="$HOME/Library/Application Support/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    echo "📱 Detected macOS"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CONFIG_DIR="$HOME/.config/claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    echo "🐧 Detected Linux"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    CONFIG_DIR="$APPDATA/Claude"
    CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"
    echo "🪟 Detected Windows"
else
    echo "❌ Unsupported OS: $OSTYPE"
    exit 1
fi

# Get current directory (where MCP server is located)
CURRENT_DIR="$(pwd)"
echo "📁 MCP Server Directory: $CURRENT_DIR"

# Create config directory if it doesn't exist
mkdir -p "$CONFIG_DIR"

# Check if config file exists
if [[ -f "$CONFIG_FILE" ]]; then
    echo "⚠️  Claude Desktop config file already exists at:"
    echo "   $CONFIG_FILE"
    read -p "Do you want to backup and replace it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        echo "✅ Backed up existing config"
    else
        echo "❌ Aborted. Please manually merge the configuration."
        exit 1
    fi
fi

# Load environment variables if .env exists
if [[ -f ".env" ]]; then
    echo "📋 Loading environment variables from .env file..."
    source .env
    
    # Validate required variables
    if [[ -z "$AAP_URL" ]] || [[ -z "$AAP_TOKEN" ]] || [[ -z "$AAP_PROJECT_ID" ]]; then
        echo "❌ Missing required environment variables in .env file"
        echo "   Please ensure AAP_URL, AAP_TOKEN, and AAP_PROJECT_ID are set"
        exit 1
    fi
    
    echo "✅ Environment variables loaded successfully"
    
    # Create config with environment variables
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "ansible-aap": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "$CURRENT_DIR",
      "env": {
        "AAP_URL": "$AAP_URL",
        "AAP_TOKEN": "$AAP_TOKEN",
        "AAP_PROJECT_ID": "$AAP_PROJECT_ID",
        "AAP_VERIFY_SSL": "${AAP_VERIFY_SSL:-True}",
        "AAP_TIMEOUT": "${AAP_TIMEOUT:-30}",
        "AAP_MAX_RETRIES": "${AAP_MAX_RETRIES:-3}"
      }
    }
  }
}
EOF
    
    echo "✅ Created Claude Desktop configuration with environment variables"
    
else
    echo "⚠️  No .env file found. Creating template configuration..."
    
    # Create template config
    cat > "$CONFIG_FILE" << EOF
{
  "mcpServers": {
    "ansible-aap": {
      "command": "uv",
      "args": ["run", "server.py"],
      "cwd": "$CURRENT_DIR",
      "env": {
        "AAP_URL": "https://your-aap-instance.com",
        "AAP_TOKEN": "your-access-token-here",
        "AAP_PROJECT_ID": "your-project-id",
        "AAP_VERIFY_SSL": "True",
        "AAP_TIMEOUT": "30",
        "AAP_MAX_RETRIES": "3"
      }
    }
  }
}
EOF
    
    echo "✅ Created template Claude Desktop configuration"
    echo "⚠️  IMPORTANT: Edit the configuration file and replace placeholder values:"
    echo "   $CONFIG_FILE"
fi

echo ""
echo "🎉 Configuration complete!"
echo ""
echo "Next steps:"
echo "1. 🔧 If using template config, edit: $CONFIG_FILE"
echo "2. 🔄 Restart Claude Desktop completely"
echo "3. 🧪 Test the integration by asking Claude about Ansible templates"
echo "4. 🔍 Run 'python test_mcp_server.py' to validate your setup"
echo ""
echo "Example test questions for Claude:"
echo "- What Ansible templates are available?"
echo "- Show me the job templates from my AAP project"
echo "- Test the AAP connection"
echo ""
echo "Configuration file location: $CONFIG_FILE" 