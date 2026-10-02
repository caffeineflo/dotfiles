# Custom shell configuration

These files capture the current Mac's Oh My Zsh aliases, launcher functions, environment setup, and prompt theme. The restore manifest copies only those named files; it never imports the full framework or plugin directories.

Literal credentials belong in `~/.dotfiles-private.sh`, loaded from `.zshenv`. Other launchers retrieve their credentials from macOS Keychain. The old `mcp-enable` configuration has been removed because this Mac now uses shared MCP configuration in the separate `~/.claude` repository.

See the root README for restoration, companion repositories, and Keychain requirements.
