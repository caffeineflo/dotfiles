"""Preview, capture, or restore the explicit list of managed configuration files."""

import argparse
from datetime import datetime
import difflib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import tempfile

from snapshot import normalize, private_exports


ROOT = Path(__file__).resolve().parent.parent


def check_destination(path, boundary):
    for parent in path.parents:
        if parent == boundary:
            break
        if parent.is_symlink():
            raise RuntimeError(f"Refusing to write through symlinked directory: {parent}")
        if parent.exists() and not parent.is_dir():
            raise NotADirectoryError(f"Destination parent isn't a directory: {parent}")


def write_file(path, data, mode):
    path.parent.mkdir(parents=True, exist_ok=True)
    # Replace the directory entry itself, so an existing symlink isn't followed.
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
        os.fchmod(stream.fileno(), mode)
    try:
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def install_shell(home):
    destinations = {
        home / ".oh-my-zsh": "ohmyzsh/ohmyzsh",
        home / ".oh-my-zsh/custom/plugins/zsh-syntax-highlighting":
            "zsh-users/zsh-syntax-highlighting",
        home / ".oh-my-zsh/custom/plugins/zsh-autosuggestions":
            "zsh-users/zsh-autosuggestions",
    }
    for destination in destinations:
        check_destination(destination, home)
        if destination.is_symlink():
            raise RuntimeError(f"Refusing to install through symlink: {destination}")
    for destination, repository in destinations.items():
        if destination.exists():
            marker = "oh-my-zsh.sh" if repository == "ohmyzsh/ohmyzsh" else ".git"
            if not (destination / marker).exists():
                raise RuntimeError(f"Incomplete shell dependency: {destination}")
            print(f"PRESERVED shell dependency: {destination}")
            continue
        destination.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(
            ["git", "clone", "--depth", "1", f"https://github.com/{repository}.git",
             str(destination)], check=True,
        )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["install", "capture"])
    parser.add_argument("--home", type=Path, default=Path.home())
    actions = parser.add_mutually_exclusive_group()
    actions.add_argument("--apply", action="store_true", help="Write changes; preserve existing restore conflicts")
    actions.add_argument("--replace", "--force", "-f", action="store_true", help="Write changes with backups, including restore conflicts")
    actions.add_argument("--check", "-c", action="store_true", help="Preview changes (the default)")
    actions.add_argument("--diff", "-d", action="store_true", help="Preview normalized configuration differences")
    parser.add_argument("--install-shell", action="store_true", help="Install missing Oh My Zsh dependencies before restoring")
    args = parser.parse_args()
    home = args.home.expanduser().resolve()
    writing = args.apply or args.replace
    if home == ROOT:
        parser.error("The destination home must be different from the repository")
    if args.install_shell and (args.operation != "install" or not writing):
        parser.error("--install-shell requires install --apply or --replace")

    entries = json.loads((ROOT / "dotfiles.json").read_text())
    changes = []
    for entry in entries:
        repository_file = ROOT / entry["repo"]
        home_file = home / entry["home"]
        source, target = (home_file, repository_file) if args.operation == "capture" else (repository_file, home_file)
        if not source.is_file():
            if args.operation == "install":
                raise FileNotFoundError(f"Missing managed repository file: {source}")
            print(f"MISSING in home (repository copy preserved): {entry['home']}")
            continue
        data = normalize(entry["home"], source.read_bytes())
        existing = target.read_bytes() if target.is_file() else None
        comparable = normalize(entry["home"], existing) if existing is not None else None
        if not target.is_symlink() and data == existing:
            continue
        status = "MODIFIED" if target.exists() or target.is_symlink() else "NEW"
        print(f"{status}: {entry['home']}")
        if args.diff and comparable is not None:
            for line in difflib.unified_diff(
                comparable.decode().splitlines(), data.decode().splitlines(),
                fromfile=str(target), tofile=str(source), lineterm="",
            ):
                print(line)
        changes.append((entry, source, target, data))

    if not writing:
        print(f"Preview: {len(changes)} changed files. No files written.")
        return
    boundary = home if args.operation == "install" else ROOT
    pending = []
    credentials = {}
    for entry, source, target, data in changes:
        exists = target.exists() or target.is_symlink()
        if args.operation == "install" and exists and not args.replace:
            print(f"PRESERVED: {entry['home']} (use --replace after reviewing)")
            continue
        if exists and target.is_dir():
            raise IsADirectoryError(f"Managed file is a directory: {target}")
        check_destination(target, boundary)
        if exists and args.operation == "install" and target.suffix != ".plist":
            credentials.update(private_exports(target.read_bytes()))
        pending.append((entry, source, target, data))
    private_file = home / ".dotfiles-private.sh"
    if credentials and (private_file.is_symlink() or private_file.is_dir()):
        raise RuntimeError(f"Refusing to replace private credential path: {private_file}")
    backup_base = home / ".dotfiles-backups" if args.operation == "install" else ROOT / "fharr/backups"
    check_destination(backup_base, boundary)
    if backup_base.is_symlink() or (backup_base.exists() and not backup_base.is_dir()):
        raise RuntimeError(f"Invalid backup directory: {backup_base}")
    if args.operation == "install":
        for directory in [".vim/backups", ".vim/swaps", ".vim/undo"]:
            destination = home / directory
            check_destination(destination, home)
            if destination.is_symlink() or (destination.exists() and not destination.is_dir()):
                raise RuntimeError(f"Invalid Vim runtime directory: {destination}")
    if args.install_shell:
        install_shell(home)

    backup_root = None
    for entry, source, target, data in pending:
        if target.exists() or target.is_symlink():
            if backup_root is None:
                backup_base.mkdir(parents=True, exist_ok=True, mode=0o700)
                backup_root = Path(tempfile.mkdtemp(prefix=datetime.now().strftime("%Y%m%d-%H%M%S-"), dir=backup_base))
            relative = entry["home"] if args.operation == "install" else entry["repo"]
            backup = backup_root / relative
            backup.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, backup, follow_symlinks=False)
    if credentials:
        existing = private_file.read_text() if private_file.exists() else "# Local credentials; never commit this file.\n"
        if private_file.exists():
            shutil.copy2(private_file, backup_root / ".dotfiles-private.sh")
        additions = "".join(f"export {name}={shlex.quote(value)}\n" for name, value in credentials.items())
        write_file(private_file, (existing.rstrip() + "\n" + additions).encode(), 0o600)
        print("Preserved literal credentials in ~/.dotfiles-private.sh (mode 600).")
    for entry, source, target, data in pending:
        mode = source.stat().st_mode & 0o777 if args.operation == "capture" else 0o644
        write_file(target, data, mode)
    if args.operation == "install":
        for directory in [".vim/backups", ".vim/swaps", ".vim/undo"]:
            (home / directory).mkdir(parents=True, exist_ok=True)
    if backup_root:
        print(f"Backups: {backup_root}")
    print("Finished. Existing files outside the manifest were preserved.")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f"dotfiles: {error}", file=sys.stderr)
        sys.exit(1)
