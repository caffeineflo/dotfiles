#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE}")";

# Files to sync back from home directory
DOTFILES=(
    ".aliases"
    ".bash_profile"
    ".bash_prompt"
    ".bashrc"
    ".curlrc"
    ".editorconfig"
    ".exports"
    ".functions"
    ".gitattributes"
    ".gitconfig"
    ".gitignore"
    ".path"
    ".tmux.conf"
    ".vimrc"
    ".wgetrc"
    ".zshrc"
)

# Directories to sync back
DOTDIRS=(
    ".vim"
    ".oh-my-zsh"
    "bin"
)

function syncBack() {
    echo "Syncing dotfiles back from home directory..."
    
    # Sync individual files
    for file in "${DOTFILES[@]}"; do
        if [ -f "$HOME/$file" ]; then
            if [ -f "./$file" ]; then
                # Check if files are different
                if ! cmp -s "$HOME/$file" "./$file"; then
                    echo "Updating $file"
                    cp "$HOME/$file" "./$file"
                else
                    echo "$file is up to date"
                fi
            else
                echo "New file: $file"
                cp "$HOME/$file" "./$file"
            fi
        fi
    done
    
    # Sync directories (excluding certain subdirectories)
    for dir in "${DOTDIRS[@]}"; do
        if [ -d "$HOME/$dir" ]; then
            echo "Syncing directory $dir"
            rsync -av --exclude=".git/" \
                --exclude="custom/plugins/zsh-syntax-highlighting/" \
                --exclude="custom/plugins/zsh-autosuggestions/" \
                "$HOME/$dir/" "./$dir/"
        fi
    done
    
    # Sync iTerm2 preferences
    if [ -f "$HOME/Library/Preferences/com.googlecode.iterm2.plist" ]; then
        echo "Syncing iTerm2 preferences..."
        mkdir -p ./iterm2
        cp "$HOME/Library/Preferences/com.googlecode.iterm2.plist" "./iterm2/com.googlecode.iterm2.plist"
    fi
    
    echo "Sync complete!"
}

function showChanges() {
    echo "Checking for changes..."
    
    # Check individual files
    for file in "${DOTFILES[@]}"; do
        if [ -f "$HOME/$file" ] && [ -f "./$file" ]; then
            if ! cmp -s "$HOME/$file" "./$file"; then
                echo "MODIFIED: $file"
                if [ "$1" == "--diff" ]; then
                    echo "--- Repo version"
                    echo "+++ Home version"
                    diff "./$file" "$HOME/$file" || true
                    echo ""
                fi
            fi
        elif [ -f "$HOME/$file" ] && [ ! -f "./$file" ]; then
            echo "NEW: $file"
        fi
    done
    
    # Check iTerm2 preferences
    if [ -f "$HOME/Library/Preferences/com.googlecode.iterm2.plist" ]; then
        if [ -f "./iterm2/com.googlecode.iterm2.plist" ]; then
            if ! cmp -s "$HOME/Library/Preferences/com.googlecode.iterm2.plist" "./iterm2/com.googlecode.iterm2.plist"; then
                echo "MODIFIED: iTerm2 preferences"
            fi
        else
            echo "NEW: iTerm2 preferences"
        fi
    fi
}

case "$1" in
    "--check" | "-c")
        showChanges
        ;;
    "--diff" | "-d")
        showChanges --diff
        ;;
    "--force" | "-f")
        syncBack
        ;;
    *)
        echo "Usage: $0 [--check|-c] [--diff|-d] [--force|-f]"
        echo ""
        echo "  --check, -c    Show which files have changed"
        echo "  --diff, -d     Show changes with diff output"
        echo "  --force, -f    Sync changes back to repo"
        echo ""
        showChanges
        echo ""
        read -p "Sync these changes back to the repo? (y/n) " -n 1;
        echo "";
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            syncBack;
        fi;
        ;;
esac