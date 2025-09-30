# MCP server management functions

# MCP server definitions (edit these as needed)
# Set these environment variables in your .zshrc or .env file:
# export CONTEXT7_API_KEY="your-api-key"
# export GITHUB_MCP_TOKEN="your-github-token"

declare -A MCP_SERVERS
MCP_SERVERS[context7]="{
  \"type\": \"http\",
  \"url\": \"https://mcp.context7.com/mcp\",
  \"headers\": {
    \"CONTEXT7_API_KEY\": \"${CONTEXT7_API_KEY:-}\"
  }
}"

MCP_SERVERS[figma]='{
  "type": "http",
  "url": "http://127.0.0.1:3845/mcp"
}'

MCP_SERVERS[sentry]='{
  "type": "http",
  "url": "https://mcp.sentry.dev/mcp"
}'

MCP_SERVERS[atlassian]='{
  "type": "sse",
  "url": "https://mcp.atlassian.com/v1/sse"
}'

MCP_SERVERS[github]="{
  \"type\": \"http\",
  \"url\": \"https://api.githubcopilot.com/mcp\",
  \"headers\": {
    \"Authorization\": \"Bearer ${GITHUB_MCP_TOKEN:-}\"
  }
}"

# Enable MCP server
mcp-enable() {
    local config_file="$HOME/.mcp.json"
    local server="$1"

    if [ -z "$server" ]; then
        echo "Usage: mcp-enable <server>"
        echo "Available: ${(k)MCP_SERVERS[@]}"
        return 1
    fi

    if [ -z "${MCP_SERVERS[$server]}" ]; then
        echo "✗ Unknown server: $server"
        echo "Available: ${(k)MCP_SERVERS[@]}"
        return 1
    fi

    jq ".mcpServers.${server} = ${MCP_SERVERS[$server]}" "$config_file" > "${config_file}.tmp" \
        && mv "${config_file}.tmp" "$config_file"

    echo "✓ Enabled: $server"
}

# Disable MCP server
mcp-disable() {
    local config_file="$HOME/.mcp.json"
    local server="$1"

    if [ -z "$server" ]; then
        echo "Usage: mcp-disable <server>"
        return 1
    fi

    jq "del(.mcpServers.${server})" "$config_file" > "${config_file}.tmp" \
        && mv "${config_file}.tmp" "$config_file"

    echo "✓ Disabled: $server"
}

# List enabled servers
mcp-list() {
    jq -r '.mcpServers | keys[]' "$HOME/.mcp.json"
}
