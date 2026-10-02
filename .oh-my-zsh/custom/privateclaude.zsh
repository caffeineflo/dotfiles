privateclaude() {
  if ! lsof -i :8443 >/dev/null 2>&1; then
    node ~/.claude/bin/api-proxy.mjs >/dev/null 2>&1 &
    sleep 1
  fi

  env \
    -u ANTHROPIC_API_KEY \
    -u ANTHROPIC_AUTH_TOKEN \
    -u AWS_BEARER_TOKEN_BEDROCK \
    -u MY_ANTHROPIC_API_KEY \
    CLAUDE_CODE_OAUTH_TOKEN="$(security find-generic-password -s privateclaude-oauth-token -w 2>/dev/null)" \
    ANTHROPIC_BASE_URL="http://127.0.0.1:8443" \
    HTTPS_PROXY="" \
    HTTP_PROXY="" \
    CLAUDE_CONFIG_DIR="$HOME/.claude/profiles/private" \
    claude --strict-mcp-config --mcp-config "$HOME/.claude/shared-mcp.json" --dangerously-skip-permissions "$@"
}

alias privateclaude-stop='pkill -f "[a]pi-proxy.mjs" 2>/dev/null && echo "Stopped" || echo "Not running"'