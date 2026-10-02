# Private credentials stay outside this repository.
if [ -r "$HOME/.dotfiles-private.sh" ]; then
    . "$HOME/.dotfiles-private.sh"
fi

# uv
export PATH="$HOME/.local/bin:$PATH"
if [ -r "$HOME/.cargo/env" ]; then
    . "$HOME/.cargo/env"
fi

# Keep large, disposable developer caches off the internal disk.
export UV_CACHE_DIR="/Volumes/ExternalSSD/DeveloperCaches/uv"
export PLAYWRIGHT_BROWSERS_PATH="/Volumes/ExternalSSD/DeveloperCaches/playwright"
export NPM_CONFIG_CACHE="/Volumes/ExternalSSD/DeveloperCaches/npm"
export GOMODCACHE="/Volumes/ExternalSSD/DeveloperCaches/go-mod"
export GOCACHE="/Volumes/ExternalSSD/DeveloperCaches/go-build"
export GRADLE_USER_HOME="/Volumes/ExternalSSD/DeveloperCaches/gradle"

# MetaMCP
# METAMCP_API_KEY is loaded from ~/.dotfiles-private.sh.

# Claude profile tokens are stored in macOS Keychain and loaded only by the
# platformclaude/bedrockclaude launchers.

# Home Assistant MCP - long-lived token stored in macOS Keychain (service: ha-mcp-token)
# Manage with: security {add,delete,find}-generic-password -s ha-mcp-token
export HA_MCP_TOKEN="$(security find-generic-password -s ha-mcp-token -w 2>/dev/null)"
