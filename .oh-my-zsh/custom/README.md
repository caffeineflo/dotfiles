# Oh My Zsh Custom Configuration

This directory contains custom Oh My Zsh configurations including aliases, functions, and environment setup.

## Files

- **aliases.zsh** - Custom shell aliases
- **env.zsh** - Environment variable exports and configurations
- **mcp.zsh** - MCP (Model Context Protocol) server management functions

## MCP Server Management

The `mcp.zsh` file provides functions to dynamically enable/disable Claude Code MCP servers.

### Setup

1. Create a `~/.mcp.env` file with your credentials:

```bash
# ~/.mcp.env
export CONTEXT7_API_KEY="your-context7-api-key"
export GITHUB_MCP_TOKEN="your-github-token"
```

2. Set restrictive permissions:

```bash
chmod 600 ~/.mcp.env
```

3. Ensure `~/.mcp.env` is in your global gitignore:

```bash
echo ".mcp.env" >> ~/.gitignore_global
git config --global core.excludesfile ~/.gitignore_global
```

### Usage

```bash
# Enable a specific MCP server
mcp-enable context7
mcp-enable github

# Disable an MCP server
mcp-disable figma

# List currently enabled servers
mcp-list
```

### Available Servers

- `context7` - Context7 documentation server (requires CONTEXT7_API_KEY)
- `figma` - Figma MCP server (local)
- `sentry` - Sentry MCP server
- `atlassian` - Atlassian MCP server
- `github` - GitHub MCP server (requires GITHUB_MCP_TOKEN)

### Security Notes

- **Never commit `~/.mcp.env`** - It contains sensitive API keys and tokens
- The functions read server configurations from environment variables
- Credentials are injected at runtime, not stored in version control
- Edit the `MCP_SERVERS` definitions in `mcp.zsh` to add/modify server configs
