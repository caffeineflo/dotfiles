"""Keep captured shell configuration portable without copying credentials."""

import plistlib
import re
import shlex


SECRET_EXPORT = re.compile(r"^[ \t]*export[ \t]+([A-Z_][A-Z0-9_]*)[ \t]*=[ \t]*(.*)$", re.MULTILINE)


def export_value(match):
    name, expression = match.groups()
    if not re.search(r"TOKEN|SECRET|PASSWORD|API_KEY", name) or "$" in expression or "`" in expression:
        return None
    lexer = shlex.shlex(expression, posix=True, punctuation_chars=";&|")
    lexer.whitespace_split = True
    values = list(lexer)
    if values and values[-1] == ";":
        values.pop()
    if len(values) != 1:
        raise ValueError(f"Split the literal credential export {name} onto its own line before capturing")
    return values[0]


def private_exports(data):
    exports = {}
    for match in SECRET_EXPORT.finditer(data.decode("utf-8")):
        value = export_value(match)
        if value is not None:
            exports[match[1]] = value
    return exports


def redact_export(match):
    if export_value(match) is None:
        return match[0]
    return f"# {match[1]} is loaded from ~/.dotfiles-private.sh."


def normalize(target_path: str, data: bytes) -> bytes:
    """Apply the same small safety edits during capture and drift checks."""
    if target_path == "Library/Preferences/com.googlecode.iterm2.plist":
        preferences = plistlib.loads(data)
        for key in list(preferences):
            if key.startswith(("NoSync", "NSWindow Frame", "SU")) or key in (
                "iTerm Version", "CodeReviewSavedPrompts", "Workgroups",
            ):
                del preferences[key]
        return plistlib.dumps(preferences, fmt=plistlib.FMT_XML, sort_keys=True)
    if target_path not in (
        ".aliases", ".bash_profile", ".bash_prompt", ".bashrc", ".curlrc",
        ".editorconfig", ".exports", ".functions", ".gitattributes", ".gitconfig",
        ".gitignore", ".path", ".tmux.conf", ".vimrc", ".wgetrc", ".zshrc",
        ".zshenv", ".zprofile", ".oh-my-zsh/custom/aliases.zsh",
        ".oh-my-zsh/custom/env.zsh", ".oh-my-zsh/custom/functions.zsh",
        ".oh-my-zsh/custom/privateclaude.zsh", ".oh-my-zsh/custom/themes/robbyrussell.zsh-theme",
    ):
        return data
    text = data.decode("utf-8")
    # Literal credentials in any managed shell file belong in the private loader.
    text = SECRET_EXPORT.sub(redact_export, text)
    if target_path in (".zshenv", ".bash_profile"):
        loader = (
            'if [ -r "$HOME/.dotfiles-private.sh" ]; then\n'
            '    . "$HOME/.dotfiles-private.sh"\n'
            "fi\n"
        )
        if loader not in text:
            text = "# Private credentials stay outside this repository.\n" + loader + "\n" + text
    if target_path in (".bash_profile", ".bashrc", ".zshenv"):
        cargo = '. "$HOME/.cargo/env"'
        guard = 'if [ -r "$HOME/.cargo/env" ]; then\n    ' + cargo + "\nfi"
        if guard not in text:
            text = text.replace(cargo, guard)
    if target_path in (".zshenv", ".zprofile"):
        text = text.replace(
            'export PATH="/Users/evils/.local/bin:$PATH"',
            'export PATH="$HOME/.local/bin:$PATH"',
        )
    if target_path == ".zprofile":
        brew = 'eval "$(/opt/homebrew/bin/brew shellenv)"'
        guard = "if [ -x /opt/homebrew/bin/brew ]; then\n    " + brew + "\nfi"
        if guard not in text:
            text = text.replace(brew, guard)
    if target_path == ".path":
        text = text.replace(
            "export PATH=$PATH:$(brew --prefix gnu-sed)/libexec/gnubin",
            "if command -v brew >/dev/null 2>&1; then\n"
            '    gnu_sed_prefix="$(brew --prefix gnu-sed)"\n'
            '    if [ -d "$gnu_sed_prefix/libexec/gnubin" ]; then\n'
            '        export PATH="$PATH:$gnu_sed_prefix/libexec/gnubin"\n'
            "    fi\n"
            "    unset gnu_sed_prefix\n"
            "fi",
        )
    if target_path == ".zshrc":
        text = text.replace(
            "source $ZSH/oh-my-zsh.sh",
            'if [ -r "$ZSH/oh-my-zsh.sh" ]; then\n'
            '    source "$ZSH/oh-my-zsh.sh"\n'
            "fi",
        )
        mise = 'eval "$(mise activate zsh)"'
        guard = "if command -v mise >/dev/null 2>&1; then\n    " + mise + "\nfi"
        if guard not in text:
            text = text.replace(mise, guard)
    if target_path == ".gitignore":
        for pattern in (".dotfiles-private.sh", ".dotfiles-backups/", "fharr/"):
            if pattern not in text.splitlines():
                text = text.rstrip() + "\n" + pattern + "\n"
    return re.sub(r"[ \t]+$", "", text, flags=re.MULTILINE).encode("utf-8")
