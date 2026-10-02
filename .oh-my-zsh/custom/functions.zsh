# Shared MCP config (single source of truth) used by all claude profiles.
# --strict-mcp-config makes Claude Code ignore each profile's own mcpServers
# and load only this file, so MCP stays identical across profiles.
CLAUDE_SHARED_MCP="$HOME/.claude/shared-mcp.json"

bedrockclaude() {
  AWS_BEARER_TOKEN_BEDROCK="$(security find-generic-password -s bedrockclaude-aws-bearer-token -w 2>/dev/null)" \
    CLAUDE_CONFIG_DIR=~/.claude/profiles/bedrock \
    claude --strict-mcp-config --mcp-config "$CLAUDE_SHARED_MCP" --dangerously-skip-permissions "$@"
}

platformclaude() {
  CLAUDE_CONFIG_DIR=~/.claude/profiles/platform \
    claude --strict-mcp-config --mcp-config "$CLAUDE_SHARED_MCP" --dangerously-skip-permissions "$@"
}



# Launch a dedicated Chrome profile for API discovery with DevTools access enabled.
function api-chrome() {
	local profile_dir="${HOME}/.agent-api-chrome";
	local debug_port="${API_CHROME_PORT:-9222}";

	mkdir -p "${profile_dir}";
	open -na "Google Chrome" --args \
		--user-data-dir="${profile_dir}" \
		--remote-debugging-port="${debug_port}" \
		--no-first-run \
		--no-default-browser-check \
		"$@";
}

# Start the API-discovery Chrome profile, then launch Codex with browser tooling.
function codex-api() {
	api-chrome;
	codex --profile api-capture --search --dangerously-bypass-approvals-and-sandbox "$@";
}

function _load_codex_lb_api_key() {
	if [ -n "${CODEX_LB_API_KEY}" ]; then
		return 0;
	fi;

	local keychain_key;
	keychain_key="$(security find-generic-password -s codex-lb-api-key -w 2>/dev/null)";
	if [ -z "${keychain_key}" ]; then
		return 1;
	fi;

	export CODEX_LB_API_KEY="${keychain_key}";
}

_load_codex_lb_api_key >/dev/null 2>&1 || true;
