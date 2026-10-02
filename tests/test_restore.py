"""Exercise file preservation using isolated repository and home directories."""

import json
from pathlib import Path
import plistlib
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parent.parent


class RestoreTest(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "fharr"
        scratch.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temporary.cleanup)
        self.repository = Path(self.temporary.name) / "repo"
        self.home = Path(self.temporary.name) / "home"
        self.repository.mkdir()
        self.home.mkdir()
        shutil.copytree(ROOT / "scripts", self.repository / "scripts")
        for script in ("bootstrap.sh", "sync-back.sh"):
            shutil.copy2(ROOT / script, self.repository / script)
        entries = [
            {"repo": ".zshenv", "home": ".zshenv"},
            {"repo": ".zshrc", "home": ".zshrc"},
            {"repo": "git/global-ignore", "home": ".gitignore"},
        ]
        (self.repository / "dotfiles.json").write_text(json.dumps(entries))
        (self.repository / ".zshenv").write_text("export EDITOR=vim\n")
        (self.repository / ".zshrc").write_text("# captured shell\n")
        (self.repository / "git").mkdir()
        (self.repository / "git/global-ignore").write_text("*.pyc\n")

    def run_script(self, script="bootstrap.sh", *arguments):
        return subprocess.run(
            [str(self.repository / script), "--home", str(self.home), *arguments],
            cwd="/", text=True, capture_output=True,
        )

    def test_default_preview_does_not_write_any_home_files(self):
        result = self.run_script()
        self.assertEqual((result.returncode, list(self.home.iterdir())), (0, []))

    def test_apply_preserves_existing_configuration(self):
        existing = self.home / ".zshrc"
        existing.write_text("# newer local shell\n")
        result = self.run_script("bootstrap.sh", "--apply")
        self.assertEqual((result.returncode, existing.read_text()), (0, "# newer local shell\n"))

    def test_apply_installs_missing_configuration(self):
        result = self.run_script("bootstrap.sh", "--apply")
        self.assertEqual((result.returncode, (self.home / ".zshrc").read_text()), (0, "# captured shell\n"))

    def test_replace_keeps_original_configuration_in_backup(self):
        (self.home / ".zshrc").write_text("# newer local shell\n")
        result = self.run_script("bootstrap.sh", "--replace")
        backups = list((self.home / ".dotfiles-backups").glob("*/.zshrc"))
        self.assertEqual((result.returncode, [p.read_text() for p in backups]), (0, ["# newer local shell\n"]))

    def test_replace_preserves_literal_credentials_in_private_file(self):
        credential = "fixture" + "-credential"
        (self.home / ".zshenv").write_text(f"export METAMCP_API_KEY='{credential}'\n")
        result = self.run_script("bootstrap.sh", "--replace")
        private_file = self.home / ".dotfiles-private.sh"
        self.assertEqual(
            (result.returncode, credential in private_file.read_text(), private_file.stat().st_mode & 0o777,
             credential in result.stdout, credential in (self.home / ".zshenv").read_text()),
            (0, True, 0o600, False, False),
        )

    def test_restore_does_not_copy_unmanaged_repository_files(self):
        (self.repository / "private.env").write_text("private fixture\n")
        result = self.run_script("bootstrap.sh", "--apply")
        self.assertEqual((result.returncode, (self.home / "private.env").exists()), (0, False))

    def test_capture_removes_literal_credentials_from_repository(self):
        credential = "fixture" + "-credential"
        (self.home / ".zshenv").write_text(f"export METAMCP_API_KEY='{credential}'\n")
        result = self.run_script("sync-back.sh", "--apply")
        self.assertEqual((result.returncode, credential in (self.repository / ".zshenv").read_text()), (0, False))

    def test_diff_does_not_print_literal_credentials(self):
        credential = "fixture" + "-credential"
        (self.home / ".zshenv").write_text(f"export METAMCP_API_KEY='{credential}'\n")
        result = self.run_script("bootstrap.sh", "--diff")
        self.assertEqual((result.returncode, credential in result.stdout, credential in result.stderr), (0, False, False))

    def test_capture_checks_custom_files_in_manifest(self):
        manifest = self.repository / "dotfiles.json"
        entries = json.loads(manifest.read_text())
        entries.append({"repo": ".oh-my-zsh/custom/functions.zsh", "home": ".oh-my-zsh/custom/functions.zsh"})
        manifest.write_text(json.dumps(entries))
        custom = self.home / ".oh-my-zsh/custom"
        custom.mkdir(parents=True)
        (custom / "functions.zsh").write_text("# new custom behavior\n")
        result = self.run_script("sync-back.sh", "--check")
        self.assertEqual((result.returncode, "NEW: .oh-my-zsh/custom/functions.zsh" in result.stdout), (0, True))

    def test_restore_replaces_symlink_without_writing_external_target(self):
        outside = Path(self.temporary.name) / "outside"
        outside.write_text("external file\n")
        (self.home / ".zshrc").symlink_to(outside)
        result = self.run_script("bootstrap.sh", "--replace")
        backups = list((self.home / ".dotfiles-backups").glob("*/.zshrc"))
        self.assertEqual(
            (result.returncode, outside.read_text(), (self.home / ".zshrc").is_symlink(), backups[0].is_symlink()),
            (0, "external file\n", False, True),
        )

    def test_restore_refuses_symlinked_parent_before_writing_files(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.home / "Library").symlink_to(outside)
        manifest = self.repository / "dotfiles.json"
        entries = json.loads(manifest.read_text())
        entries.append({"repo": "preferences", "home": "Library/Preferences/config"})
        manifest.write_text(json.dumps(entries))
        (self.repository / "preferences").write_text("preferences\n")
        result = self.run_script("bootstrap.sh", "--replace")
        self.assertEqual((result.returncode, (self.home / ".zshrc").exists(), list(outside.iterdir())), (1, False, []))

    def test_missing_repository_file_fails_before_writing(self):
        (self.repository / ".zshrc").unlink()
        result = self.run_script("bootstrap.sh", "--apply")
        self.assertEqual((result.returncode, list(self.home.iterdir())), (1, []))

    def test_second_restore_is_idempotent(self):
        self.run_script("bootstrap.sh", "--apply")
        result = self.run_script()
        self.assertEqual((result.returncode, "Preview: 0 changed files" in result.stdout), (0, True))

    def test_replace_applies_safety_guards_even_when_normalized_values_match(self):
        (self.home / ".zshenv").write_text("export EDITOR=vim\n")
        result = self.run_script("bootstrap.sh", "--replace")
        self.assertEqual((result.returncode, ".dotfiles-private.sh" in (self.home / ".zshenv").read_text()), (0, True))

    def test_replace_preserves_credential_with_quoted_semicolon(self):
        (self.home / ".zshenv").write_text("export EXAMPLE_API_KEY2='fixture;value';\n")
        result = self.run_script("bootstrap.sh", "--replace")
        self.assertEqual((result.returncode, "fixture;value" in (self.home / ".dotfiles-private.sh").read_text()), (0, True))

    def test_inline_credential_commands_fail_before_restore_writes(self):
        (self.home / ".zshenv").write_text("export EXAMPLE_API_KEY='fixture'; echo extra\n")
        result = self.run_script("bootstrap.sh", "--replace")
        self.assertEqual((result.returncode, (self.home / ".zshrc").exists()), (1, False))

    def test_restore_refuses_vim_symlink_before_configuration_writes(self):
        outside = Path(self.temporary.name) / "outside"
        outside.mkdir()
        (self.home / ".vim").symlink_to(outside)
        result = self.run_script("bootstrap.sh", "--replace")
        self.assertEqual((result.returncode, (self.home / ".zshrc").exists(), list(outside.iterdir())), (1, False, []))

    def test_restore_refuses_repository_alias_as_home(self):
        alias = Path(self.temporary.name) / "alias"
        alias.symlink_to(self.repository, target_is_directory=True)
        result = subprocess.run(
            [str(self.repository / "bootstrap.sh"), "--home", str(alias), "--replace"],
            capture_output=True, text=True,
        )
        self.assertEqual((result.returncode, (self.repository / ".zshrc").read_text()), (2, "# captured shell\n"))

    def test_restore_accepts_binary_iterm_preferences_and_keeps_backup(self):
        manifest = self.repository / "dotfiles.json"
        entries = json.loads(manifest.read_text())
        entries.append({"repo": "iterm.plist", "home": "Library/Preferences/com.googlecode.iterm2.plist"})
        manifest.write_text(json.dumps(entries))
        (self.repository / "iterm.plist").write_bytes(plistlib.dumps({"New Bookmarks": []}))
        preferences = self.home / "Library/Preferences/com.googlecode.iterm2.plist"
        preferences.parent.mkdir(parents=True)
        original = plistlib.dumps({"New Bookmarks": [], "NoSyncRecordedVariables": ["session fixture"]}, fmt=plistlib.FMT_BINARY)
        preferences.write_bytes(original)
        result = self.run_script("bootstrap.sh", "--replace")
        backups = list((self.home / ".dotfiles-backups").glob("*/Library/Preferences/com.googlecode.iterm2.plist"))
        self.assertEqual((result.returncode, backups[0].read_bytes(), plistlib.loads(preferences.read_bytes())), (0, original, {"New Bookmarks": []}))

    def test_sourcing_bootstrap_in_zsh_preserves_the_calling_shell(self):
        result = subprocess.run(
            ["/bin/zsh", "-f", "-c", 'source "$1"; source_status=$?; print shell_alive; exit "$source_status"',
             "test", str(self.repository / "bootstrap.sh")],
            env={"HOME": str(self.home), "ZDOTDIR": str(self.home), "PATH": "/usr/bin:/bin"},
            capture_output=True, text=True,
        )
        self.assertEqual((result.returncode, result.stdout, list(self.home.iterdir())), (1, "shell_alive\n", []))

    def test_sourcing_bootstrap_in_bash_preserves_the_calling_shell(self):
        result = subprocess.run(
            ["/bin/bash", "--noprofile", "--norc", "-c", 'source "$1"; source_status=$?; echo shell_alive; exit "$source_status"',
             "test", str(self.repository / "bootstrap.sh")],
            env={"HOME": str(self.home), "PATH": "/usr/bin:/bin"},
            capture_output=True, text=True,
        )
        self.assertEqual((result.returncode, result.stdout, list(self.home.iterdir())), (1, "shell_alive\n", []))


if __name__ == "__main__":
    unittest.main()
