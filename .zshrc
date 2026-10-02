# If you come from bash you might have to change your $PATH
export PATH="$HOME/bin:$PATH"

# Path to your oh-my-zsh installation
export ZSH="$HOME/.oh-my-zsh"

# Set theme - this is optional, pick your favorite
ZSH_THEME="robbyrussell"

# Add useful oh-my-zsh plugins
plugins=(
    brew
    colorize
    copyfile
    docker
    docker-compose
    git
    gh
    macos
    npm
    history
    colored-man-pages
    vscode
    sudo
    ssh
    universalarchive
    alias-finder
    aliases
    tldr
    z
    iterm2
    zsh-syntax-highlighting
    zsh-autosuggestions
)

# Opt in to iTerm2 shell integration (prompt marks, command status,
# jump-between-prompts, long-command alerts). Must be set before oh-my-zsh loads.
zstyle ':omz:plugins:iterm2' shell-integration yes

# Load oh-my-zsh
if [ -r "$ZSH/oh-my-zsh.sh" ]; then
    source "$ZSH/oh-my-zsh.sh"
fi

# Load your custom dotfiles
for file in ~/.{path,exports,aliases,functions,extra}; do
    [ -r "$file" ] && [ -f "$file" ] && source "$file"
done
unset file

# Load the private rebate agent token only for commands that send data to Dockerhost.
# This keeps the token out of the normal interactive-shell environment.
rebates() {
    case "$1" in
        sync-server|refresh-server)
            local agent_token
            agent_token="$(security find-generic-password -a "$USER" -s heineken-rebates-agent-token -w)" || return
            HEINEKEN_REBATES_SERVER_URL="https://rebates.iflorian.com" \
                HEINEKEN_REBATES_AGENT_TOKEN="$agent_token" command rebates "$@"
            ;;
        *)
            command rebates "$@"
            ;;
    esac
}

# Additional zsh settings
setopt NO_CASE_GLOB        # Case insensitive globbing
# setopt CORRECT             # Command correction
# setopt CORRECT_ALL         # Argument correction

# mise (dev tool version manager)
if command -v mise >/dev/null 2>&1; then
    eval "$(mise activate zsh)"
fi
