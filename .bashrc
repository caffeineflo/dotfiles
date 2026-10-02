[ -n "$PS1" ] && source ~/.bash_profile;
if [ -r "$HOME/.cargo/env" ]; then
    . "$HOME/.cargo/env"
fi
