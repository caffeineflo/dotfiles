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
    z
    zsh-syntax-highlighting
    zsh-autosuggestions
)

# Load oh-my-zsh
source $ZSH/oh-my-zsh.sh

# Load your custom dotfiles
for file in ~/.{path,exports,aliases,functions,extra}; do
    [ -r "$file" ] && [ -f "$file" ] && source "$file"
done
unset file

# Additional zsh settings
setopt NO_CASE_GLOB        # Case insensitive globbing
setopt CORRECT             # Command correction
setopt CORRECT_ALL         # Argument correction