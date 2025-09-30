export EDITOR="/usr/local/bin/code"

# Load MCP credentials
if [ -f "$HOME/.mcp.env" ]; then
    source "$HOME/.mcp.env"
fi