# Florian's dotfiles

This repository captures the current Mac's shell, Git, Vim, tmux, and iTerm preferences. The baseline was refreshed on October 2, 2026, on an Apple Silicon Mac running macOS 27. This Mac is the source of truth for future captures.

`dotfiles.json` lists every file that capture and restore manage. Scripts don't copy arbitrary repository files, framework trees, caches, or authentication databases. Package installation and macOS preference changes have their own explicit commands.

## Restore

Install Xcode Command Line Tools and [Homebrew](https://brew.sh/) first. The scripts use `/usr/bin/python3` from the Command Line Tools and require Git for shell dependency installation.

```bash
git clone https://github.com/caffeineflo/dotfiles.git
cd dotfiles
./bootstrap.sh
```

The default command only previews changes. Run scripts as executables; don't source them into your shell.

For a new home directory, install missing configuration and the Oh My Zsh framework/plugins:

```bash
./bootstrap.sh --apply --install-shell
```

`--apply` preserves differing existing files. Review a diff before choosing to replace them:

```bash
./bootstrap.sh --diff
./bootstrap.sh --replace
```

Replacement saves every affected original under `~/.dotfiles-backups/<timestamp>/` before writing configuration. Backups include symlinks and private values, so keep that directory private. Literal credential exports from replaced shell files move into `~/.dotfiles-private.sh` with mode `600`; Bash and zsh load that file. Existing private exports are retained.

Close iTerm before explicitly replacing its preferences. Open a new login shell after restoration. The installer doesn't restart apps, source shell files, pull Git changes, or upgrade existing plugins.

You can exercise restoration without touching your real home:

```bash
./bootstrap.sh --home /path/to/isolated-home
./bootstrap.sh --home /path/to/isolated-home --apply --install-shell
```

## Update iTerm on another Mac

The restore manifest includes both iTerm preferences and `iterm2/SolarizedDark.json`.
The dynamic profile selects the repaired Solarized palette, Fira Code Nerd Font
Mono 13 with ligatures, a 145x40 window, and close confirmations. Its
`Rewritable: false` setting keeps iTerm from rewriting the profile file.
The fallback profile carries the same appearance,
including 1.1 line spacing, so dynamic profile inheritance doesn't change the look.
Quit confirmation is enabled; Cmd-Q still ends running jobs.

Pull the latest dotfiles, then preview only the iTerm changes:

```bash
git pull --ff-only
brew install --cask font-fira-code-nerd-font
./bootstrap.sh --only iterm2 --diff
```

Quit iTerm normally when your sessions can end, then run this from Terminal.app:

```bash
./bootstrap.sh --only iterm2 --replace
```

This backs up and replaces the managed iTerm files without changing shell, Git,
or Vim configuration. Reopen iTerm to load the new default profile. New windows
use the 145x40 size. Other Macs receive updates when you pull and run this command;
the repository doesn't push settings to running apps automatically.

## Capture changes from this Mac

```bash
./sync-back.sh --check
./sync-back.sh --diff
./sync-back.sh --apply
git diff --check
git diff
```

Capture checks every manifest entry, including custom shell files and iTerm preferences. It removes literal credential exports, adds guards for optional startup dependencies, and omits iTerm command history, window positions, and update caches. Differences in those excluded values don't count as configuration drift.

Use `--only iterm2` with `sync-back.sh` to preview or capture just the iTerm
preferences and dynamic profile. `--only` accepts a repository file or directory
from `dotfiles.json` and also works with `bootstrap.sh`.

Repository files replaced during capture are backed up under `fharr/backups/`. Missing live files are reported and their repository copies are preserved; remove an obsolete entry from both the manifest and Git after reviewing it. Oh My Zsh core and plugin trees, Vim swaps, and local `bin` executables aren't captured.

The repository ignore file and your global ignore file serve different purposes. `git/global-ignore` restores to `~/.gitignore`; the root `.gitignore` protects this checkout's private and generated files.

## Packages and macOS preferences

The `Brewfile` records supported formulae you requested, installed casks, and taps. Dependencies resolve through Homebrew. Unsupported or deprecated installed packages remain documented as comments.

```bash
./brew.sh
./brew.sh --install
./.macos
./.macos --apply
```

Package checks are read-only. Installation doesn't upgrade existing packages or clean their caches. The macOS recipe captures stored preferences from this Mac and requires an explicit apply step; it doesn't rebuild Spotlight or reset application layouts. Read each command's help before applying it on another machine.

## Credentials and companion configuration

Keep `~/.dotfiles-private.sh` outside Git. On a new Mac, create it with mode `600` and supply `METAMCP_API_KEY` and `HOMEBREW_GITHUB_API_TOKEN` through your password manager or Keychain-backed commands. Bootstrap preserves existing credentials but doesn't recover them from Git history.

The shell launchers rely on separately maintained repositories:

- [claude-config](https://github.com/caffeineflo/claude-config) at `~/.claude`, including profiles, writing style, shared MCP configuration, and the API proxy.
- [codex-config](https://github.com/caffeineflo/codex-config) at `~/.codex`, including the launcher profiles.

Restore those repositories through their own setup instructions. Authentication sessions, Keychain items, SSH keys/configuration, Rust installation, and personal application data require separate restoration. Referenced Keychain services are `ha-mcp-token`, `requesty-api-key`, `heineken-rebates-agent-token`, `codex-lb-api-key`, `bedrockclaude-aws-bearer-token`, and `privateclaude-oauth-token`.

The configuration uses `/Volumes/ExternalSSD` for developer caches, Colima, and PlatformIO. Mount that volume or adjust those paths before using the related tools. Display aliases also use this Mac's monitor identifiers. These settings are preserved intentionally.

Some legacy aliases remain because they still exist on this Mac, including Python 2 helpers and old `airport`/screen-lock paths. Capturing them doesn't establish that their commands work on current macOS. Historical `init` presets and `bin/subl` aren't part of the restore manifest.

## Verify changes

```bash
/usr/bin/python3 -m unittest discover -s tests -v
shellcheck -x bootstrap.sh sync-back.sh brew.sh .macos
gitleaks dir --redact --no-banner .
./sync-back.sh --check
```

The restore tests use isolated directories under ignored `fharr/`. They exercise conflict preservation, backups, credential removal and migration, symlink handling, manifest boundaries, and repeated installation.

A Homebrew GitHub API token remains in historical commit `e05d428`. Rotate or revoke it if that's still outstanding. Scanning the current directory is clean; scanning full history still flags that old commit. This update doesn't rewrite published history.

Derived from [Mathias Bynens' dotfiles](https://github.com/mathiasbynens/dotfiles). The original MIT license remains in `LICENSE-MIT.txt`.
