"""Integration checks in temporary homes; never modifies the real desktop."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from types import SimpleNamespace

spec = importlib.util.spec_from_file_location('backup', Path(__file__).with_name('backup.py'))
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)

class PortableBackupTests(unittest.TestCase):
    def test_round_trip_and_safety(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder)
            source, repo, target = [base / x for x in ['source', 'repo', 'target']]
            source.mkdir(); repo.mkdir(); target.mkdir()
            roots = ['.config/hypr/hyprland.lua', '.config/hypr/keybindings.lua',
                     '.config/hypr/userprefs.lua', '.local/share/hypr/hyde.lua',
                     '.local/share/hypr/lua/key_binds.lua', '.local/bin/hyde-shell',
                     '.local/lib/hyde/waybar.py', '.local/lib/hyde/wallpaper.sh']
            for name in roots:
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(f'# source home {source}\n')
            (source / '.local/bin/hyde-shell').chmod(0o755)
            for name, content in {'.config/hypr/xdph.conf': 'custom_picker_binary = /old/picker\n',
                                  '.config/sunshine/sunshine.conf': 'output_name = 2\nlocale = en_US\n',
                                  '.config/zsh/.zsh_history': 'PRIVATE HISTORY',
                                  '.config/zsh/.env': 'PRIVATE TOKEN',
                                  '.local/share/fonts/font.ttf': 'FAKE FONT',
                                  '.local/share/icons/miku/cursors/pointer': 'FAKE CURSOR'}.items():
                path = source / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
            (source / '.themes').mkdir()
            (source / '.themes/my-theme').symlink_to(source / '.local/share/themes/my-theme')
            (source / '.local/share/icons/miku/cursors/default').symlink_to('pointer')
            b.snapshot(source, repo)
            manifest = b.verify(repo)
            self.assertNotIn('.config/zsh/.zsh_history', manifest['files'])
            self.assertNotIn('.config/zsh/.env', manifest['files'])
            before = manifest['assets']
            stage2 = base / 'second'; stage2.mkdir()
            self.assertEqual(before, b.snapshot(source, stage2)['assets'])
            # Existing directory link must not redirect writes to another home.
            outside = base / 'outside'; outside.mkdir()
            (outside / 'keybindings.lua').write_text('outside untouched')
            (target / '.config').mkdir()
            (target / '.config/hypr').symlink_to(outside)
            (target / '.zshrc').write_text('previous zsh')
            args = SimpleNamespace(repo=str(repo), target_home=str(target), keep_monitors=False,
                                   apply=False, install_packages=False, rebuild_env=False, enable_services=False)
            with contextlib.redirect_stdout(io.StringIO()): b.restore(args)
            self.assertTrue((target / '.config/hypr').is_symlink())
            args.apply = True
            with contextlib.redirect_stdout(io.StringIO()): b.restore(args)
            self.assertEqual((outside / 'keybindings.lua').read_text(), 'outside untouched')
            self.assertFalse((target / '.config/hypr').is_symlink())
            self.assertIn(str(target), (target / '.config/hypr/keybindings.lua').read_text())
            self.assertIn('preferred', (target / '.config/hypr/monitors.lua').read_text())
            self.assertTrue((target / '.config/hypr/xdph.conf').read_text().startswith('#'))
            self.assertNotIn('output_name', (target / '.config/sunshine/sunshine.conf').read_text())
            self.assertEqual((target / '.local/share/fonts/font.ttf').read_text(), 'FAKE FONT')
            self.assertEqual((target / '.local/share/icons/miku/cursors/default').readlink(), Path('pointer'))
            self.assertEqual((target / '.themes/my-theme').readlink(), target / '.local/share/themes/my-theme')
            self.assertEqual((target / '.local/bin/hyde-shell').stat().st_mode & 0o777, 0o755)
            saved = list((target / '.local/state/hyde-restore-backups').iterdir())
            self.assertTrue((saved[0] / '.config/hypr').is_symlink())
            # Unmanaged destination files survive.
            self.assertEqual((target / '.zshrc').read_text(), 'previous zsh')
            first = repo / 'assets' / before['fonts'][0]['file']
            first.write_bytes(first.read_bytes() + b'corrupt')
            with self.assertRaisesRegex(RuntimeError, 'Archive integrity failed'):
                b.verify(repo)

    def test_unsafe_paths_and_missing_module(self):
        for name in ['../escape', '/etc/passwd', 'a/../../escape']:
            with self.assertRaises(RuntimeError): b.valid_rel(name)
        with tempfile.TemporaryDirectory() as folder:
            home = Path(folder) / 'home'; home.mkdir()
            stage = Path(folder) / 'stage'; stage.mkdir()
            with self.assertRaisesRegex(RuntimeError, 'Required live HyDE files missing'):
                b.snapshot(home, stage)

if __name__ == '__main__': unittest.main()
