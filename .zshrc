# If you come from bash you might have to change your $PATH
export PATH="$HOME/bin:$PATH"

# Path to your oh-my-zsh installation
export ZSH="$HOME/.oh-my-zsh"

ENABLE_CORRECTION="false"

# Set theme - this is optional, pick your favorite
ZSH_THEME="robbyrussell"

# Add useful oh-my-zsh plugins
plugins=(
    brew
    copyfile
    direnv
    git
    gh
    macos
    history
    colored-man-pages
    vscode
    sudo
    z
    zsh-syntax-highlighting
    zsh-autosuggestions
)

# Load oh-my-zsh
source $ZSH/oh-my-zsh.sh

# Load bootstrap custom environment variables
source "$HOME/.bootstrap/env.sh"

# Load your custom dotfiles
for file in ~/.{path,exports,aliases,functions,extra}; do
    [ -r "$file" ] && [ -f "$file" ] && source "$file"
done
unset file

# Additional zsh settings
setopt NO_CASE_GLOB        # Case insensitive globbing
#setopt CORRECT             # Command correction
#setopt CORRECT_ALL         # Argument correction

# Disable automatic title setting
DISABLE_AUTO_TITLE="false"
ZSH_THEME_TERM_TITLE_IDLE="%~"  # Shows current directory
