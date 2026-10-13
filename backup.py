#!/usr/bin/env python3
"""Portable HyDE snapshot/restore. Python standard library only."""
import argparse
import datetime
import fcntl
import fnmatch
import gzip
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile

CONFIGS = '''hypr hyde waybar rofi kitty wlogout uwsm zsh starship fastfetch
Kvantum qt5ct qt6ct gtk-3.0 gtk-4.0 xsettingsd nwg-look btop htop cava dunst
swaync pypr mpv vim nvim fontconfig xdg-desktop-portal autostart systemd/user
mimeapps.list user-dirs.dirs user-dirs.locale xdg-terminals.list kdeglobals
dolphinrc kiorc kservicemenurc electron-flags.conf chromium-flags.conf
code-flags.conf pavucontrol.ini'''.split()
SHARES = 'hypr hyde waybar rofi wallbash fastfetch xdg-desktop-portal kservices5'.split()
ROOTS = [f'.config/{x}' for x in CONFIGS] + [f'.local/share/{x}' for x in SHARES] + [
    '.local/lib/hyde', '.local/bin/hyde-shell', '.local/bin/xdg-terminal-exec',
    '.local/state/hyde/staterc', '.local/state/hyde/lua_state',
    '.local/state/hyde/hyprland.conf', '.local/state/hyde/hypr.conf',
    '.local/state/hyde/hyprsunset', '.local/state/hyde/luarocks_env.json',
    '.config/sunshine/apps.json', '.config/sunshine/sunshine.conf',
    '.zshrc', '.zshenv', '.zprofile', '.bashrc', '.bash_profile', '.bash_logout',
    '.profile', '.Xresources', '.gtkrc-2.0', '.icons', '.themes',
    '.cache/hyde/wall.set', '.cache/hyde/wall.set.png',
    '.cache/hyde/landing/profile.png',
]
ASSETS = {
    'hyde-themes': ['.config/hyde/themes'],
    'fonts': ['.local/share/fonts', '.fonts'],
    'icons': ['.local/share/icons'],
    'gtk-themes': ['.local/share/themes'],
    'zsh-custom': ['.oh-my-zsh/custom'],
}
SKIP = ['.git', '.venv', '__pycache__', '*.pyc', '*.pyo', '*.log', '*.log.*',
        '*.sock', '*.pid', '*history*', '.zcompdump*', '*.zwc', '*.bak',
        '*~', '*.swp', '.env', '.env.*', '*credentials*', '*secret*',
        'sunshine_state.json', '*.pem', '*.key', 'python_env', 'lua_env',
        'node_modules', 'mimeinfo.cache']
CHUNK = 45 * 1024 * 1024
TOOL_DIR = Path(__file__).resolve().parent


def run(args, *, cwd=None, check=True):
    return subprocess.run(args, cwd=cwd, check=check, text=True, capture_output=True)


def output(args):
    if not shutil.which(args[0]):
        return ''
    result = run(args, check=False)
    if result.returncode:
        raise RuntimeError(f'Inventory failed: {args[0]} (exit {result.returncode})')
    return result.stdout


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def excluded(rel):
    return any(fnmatch.fnmatch(part.lower(), p.lower()) for part in rel.parts for p in SKIP)


def files(home, roots, *, omit_assets=False):
    def visit(rel):
        path = home / rel
        if excluded(rel):
            return
        if omit_assets and any(str(rel) == root or str(rel).startswith(root + '/')
                               for group in ASSETS.values() for root in group):
            return
        if path.is_symlink():
            target = os.readlink(path)
            # Keep system unit links and home links, but never copy their targets.
            if target.startswith(('/run/', '/tmp/')) and not target.startswith(str(home) + '/'):
                return
            yield rel
        elif path.is_dir():
            for child in sorted(path.iterdir()):
                yield from visit(child.relative_to(home))
        elif path.is_file():
            yield rel
    seen = set()
    for root in roots:
        for rel in visit(Path(root)):
            if str(rel) not in seen:
                seen.add(str(rel))
                yield rel


def copy_entry(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    if src.is_symlink():
        dst.symlink_to(os.readlink(src))
    else:
        shutil.copy2(src, dst)


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True) + '\n')


def archive(home, roots, dest, name):
    members = list(files(home, roots))
    if not members:
        return []
    with tempfile.TemporaryFile() as stream:
        with gzip.GzipFile(fileobj=stream, mode='wb', filename='', mtime=0) as zipped:
            with tarfile.open(fileobj=zipped, mode='w|', format=tarfile.PAX_FORMAT) as tar:
                for rel in members:
                    info = tar.gettarinfo(str(home / rel), arcname=str(rel))
                    # Stable archives, independent of ownership and file timestamps.
                    info.uid = info.gid = info.mtime = 0
                    info.uname = info.gname = ''
                    info.pax_headers = {}
                    if info.isfile():
                        with (home / rel).open('rb') as source:
                            tar.addfile(info, source)
                    else:
                        tar.addfile(info)
        stream.seek(0)
        parts = []
        index = 0
        while block := stream.read(CHUNK):
            path = dest / f'{name}.tar.gz.part{index:04d}'
            path.write_bytes(block)
            parts.append({'file': path.name, 'sha256': digest(path), 'bytes': len(block)})
            index += 1
    return parts


def snapshot(home, stage):
    (stage / 'home').mkdir()
    (stage / 'assets').mkdir()
    (stage / 'metadata').mkdir()
    required = ['.config/hypr/hyprland.lua', '.config/hypr/keybindings.lua',
                '.config/hypr/userprefs.lua', '.local/share/hypr/hyde.lua',
                '.local/share/hypr/lua/key_binds.lua', '.local/bin/hyde-shell',
                '.local/lib/hyde/waybar.py', '.local/lib/hyde/wallpaper.sh']
    missing = [name for name in required if not (home / name).is_file()]
    if missing:
        raise RuntimeError('Required live HyDE files missing: ' + ', '.join(missing))
    manifest = {'format': 1, 'source_home': str(home), 'files': {}, 'assets': {}}
    for rel in files(home, ROOTS, omit_assets=True):
        copy_entry(home / rel, stage / 'home' / rel)
        path = stage / 'home' / rel
        manifest['files'][str(rel)] = ({'link': os.readlink(path)} if path.is_symlink()
                                       else {'sha256': digest(path), 'mode': stat.S_IMODE(path.stat().st_mode)})
    # Small user launchers: skip generated app caches and browser/game profiles.
    for rel in files(home, ['.local/share/applications']):
        if rel.suffix == '.desktop':
            copy_entry(home / rel, stage / 'home' / rel)
            manifest['files'][str(rel)] = {'sha256': digest(stage / 'home' / rel),
                                         'mode': stat.S_IMODE((home / rel).stat().st_mode)}
    for name, roots in ASSETS.items():
        print(f'Packing {name}...', flush=True)
        manifest['assets'][name] = archive(home, roots, stage / 'assets', name)
    inventories = {
        'dconf-interface.ini': ['dconf', 'dump', '/org/gnome/desktop/interface/'],
        'packages-native.txt': ['pacman', '-Qqen'],
        'packages-aur.txt': ['pacman', '-Qqem'],
        'packages-versions.txt': ['pacman', '-Q'],
        'flatpaks.tsv': ['flatpak', 'list', '--app', '--columns=application,origin,installation'],
        'user-services.txt': ['systemctl', '--user', 'list-unit-files', '--state=enabled', '--no-legend', '--no-pager'],
        'system-services.txt': ['systemctl', 'list-unit-files', '--state=enabled', '--no-legend', '--no-pager'],
    }
    for name, command in inventories.items():
        (stage / 'metadata' / name).write_text(output(command))
    wanted = '''hyprland hyprlock hyprpaper hypridle hyprsunset waybar rofi-wayland rofi
wlogout uwsm kitty dolphin brave-bin code pavucontrol btop nvtop grim slurp wl-clipboard
cliphist jq imagemagick python uv lua luarocks rsync git zsh zsh-syntax-highlighting
zsh-autosuggestions fastfetch starship fzf dunst swaync qt5ct qt6ct kvantum
xdg-desktop-portal-hyprland xdg-desktop-portal-gtk polkit-gnome playerctl
dconf brightnessctl wireplumber pipewire pipewire-pulse pamixer network-manager-applet
python-pip python-pipx papirus-icon-theme ttf-jetbrains-mono-nerd ttf-cascadia-code-nerd
noto-fonts noto-fonts-cjk noto-fonts-emoji sunshine flatpak base-devel gcc make
pkgconf cmake gobject-introspection python-gobject gtk3 gtk4 lua-lgi lua51
libnotify libpulse qt6-wayland qt5-wayland unzip zip eza oh-my-zsh-git
python-pyqt6 python-pywayland'''.split()
    foreign = set((stage / 'metadata/packages-aur.txt').read_text().split())
    # Include dependencies too, even if pacman doesn't mark them explicitly installed.
    all_packages = {line.split()[0] for line in (stage / 'metadata/packages-versions.txt').read_text().splitlines()}
    for suffix, names in [('native', all_packages - foreign), ('aur', foreign)]:
        (stage / f'metadata/desktop-{suffix}.txt').write_text(''.join(x + '\n' for x in sorted(set(wanted) & names)))
    version = run(['git', '-C', str(home / 'HyDE'), 'rev-parse', 'HEAD'], check=False)
    (stage / 'metadata/hyde-commit.txt').write_text(version.stdout)
    (stage / 'metadata/backup-scope.txt').write_text(
        'HOME roots:\n' + '\n'.join(ROOTS) + '\n\nAsset groups:\n' + str(ASSETS) +
        '\n\nExcluded names:\n' + '\n'.join(SKIP) + '\n')
    json_write(stage / 'metadata/manifest.json', manifest)
    for name in ['backup.py', 'restore.sh', 'README.md', 'test_backup.py']:
        copy_entry(TOOL_DIR / name, stage / name)
    copy_entry(TOOL_DIR / 'respaldo_hyde.sh', stage / 'respaldo_hyde.sh')
    (stage / '.gitignore').write_text('__pycache__/\n*.pyc\n.backup.lock\n')
    return manifest


def backup(args):
    home = Path(args.source_home).resolve()
    repo = Path(args.repo).resolve()
    if repo == home or repo == Path('/') or home.is_relative_to(repo):
        raise RuntimeError('The backup repository must be a separate directory inside/outside HOME.')
    if not (repo / '.git').is_dir():
        raise RuntimeError(f'{repo} is not a Git repository. Clone/init it first.')
    if run(['git', 'diff', '--cached', '--quiet'], cwd=repo, check=False).returncode:
        raise RuntimeError('Unrelated staged changes exist; commit or unstage them first.')
    lock = (repo / '.backup.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    with tempfile.TemporaryDirectory(prefix='hyde-snapshot-', dir=repo.parent) as folder:
        stage = Path(folder)
        manifest = snapshot(home, stage)
        verify(stage)
        if args.dry_run:
            print(f'Preview: {len(manifest["files"])} config/helper files plus asset archives. Repository unchanged.')
            return
        # Replace only managed snapshot directories; retain previous Git history/legacy files.
        for name in ['home', 'assets', 'metadata']:
            target = repo / name
            if target.is_symlink():
                raise RuntimeError(f'Refusing managed symlink directory: {target}')
            if target.exists():
                shutil.rmtree(target)
            shutil.move(stage / name, target)
        for name in ['backup.py', 'restore.sh', 'respaldo_hyde.sh', 'README.md', 'test_backup.py', '.gitignore']:
            shutil.copy2(stage / name, repo / name)
    managed = ['home', 'assets', 'metadata', 'backup.py', 'restore.sh', 'respaldo_hyde.sh', 'README.md', 'test_backup.py', '.gitignore']
    if not args.no_commit:
        run(['git', 'add', '-A', '--'] + managed, cwd=repo)
        if run(['git', 'diff', '--cached', '--quiet'], cwd=repo, check=False).returncode:
            stamp = datetime.datetime.now().astimezone().isoformat(timespec='seconds')
            print(run(['git', 'commit', '-m', f'Portable HyDE backup: {stamp}'], cwd=repo).stdout)
        else:
            print('No backup changes to commit.')
    if not args.no_push and not args.no_commit:
        branch = run(['git', 'branch', '--show-current'], cwd=repo).stdout.strip()
        if not branch:
            raise RuntimeError('Cannot push detached HEAD.')
        result = run(['git', 'push', 'origin', branch], cwd=repo, check=False)
        if result.returncode:
            print(result.stderr, file=sys.stderr)
            raise RuntimeError('GitHub push failed; the complete backup remains committed locally.')
        print('Backup pushed to GitHub.')
    print(f'Backup ready: {repo} ({len(manifest["files"])} config/helper files).')


def valid_rel(name):
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or not rel.parts:
        raise RuntimeError(f'Unsafe snapshot path: {name}')
    return rel


def verify(repo):
    manifest = json.loads((repo / 'metadata/manifest.json').read_text())
    if manifest['format'] != 1:
        raise RuntimeError('Unsupported snapshot format.')
    for name, info in manifest['files'].items():
        valid_rel(name)
        path = repo / 'home' / name
        if 'link' in info:
            if not path.is_symlink() or os.readlink(path) != info['link']:
                raise RuntimeError(f'Link integrity failed: {name}')
        elif (path.is_symlink() or not path.is_file() or digest(path) != info['sha256']
              or stat.S_IMODE(path.stat().st_mode) != info['mode']):
            raise RuntimeError(f'File integrity failed: {name}')
    for name in manifest['files']:
        path = repo / 'home' / name
        if not path.is_symlink() and path.stat().st_size >= 100 * 1024 * 1024:
            raise RuntimeError(f'File exceeds regular GitHub size limit: {name}')
    for parts in manifest['assets'].values():
        for info in parts:
            valid_rel(info['file'])
            path = repo / 'assets' / info['file']
            if path.is_symlink() or not path.is_file() or digest(path) != info['sha256']:
                raise RuntimeError(f'Archive integrity failed: {info["file"]}')
    return manifest


def unpack_assets(repo, manifest, stage):
    for parts in manifest['assets'].values():
        if not parts:
            continue
        with tempfile.TemporaryFile() as stream:
            for info in parts:
                with (repo / 'assets' / info['file']).open('rb') as source:
                    shutil.copyfileobj(source, stream)
            stream.seek(0)
            with tarfile.open(fileobj=stream, mode='r:gz') as tar:
                for member in tar:
                    rel = valid_rel(member.name)
                    target = stage / str(rel)
                    if target.exists() or target.is_symlink():
                        raise RuntimeError(f'Duplicate asset path: {member.name}')
                    # Never traverse archive-created symlink parents.
                    if any(p.is_symlink() for p in target.parents if p != stage):
                        raise RuntimeError(f'Symlink parent in archive: {member.name}')
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if member.issym():
                        target.symlink_to(member.linkname)
                    elif member.isfile():
                        with tar.extractfile(member) as source, target.open('wb') as dest:
                            shutil.copyfileobj(source, dest)
                        target.chmod(member.mode & 0o777)
                    else:
                        raise RuntimeError(f'Unsupported archive entry: {member.name}')


def adapt(stage, old_home, new_home, keep_monitors):
    for path in stage.rglob('*'):
        if path.is_symlink():
            target = os.readlink(path).replace(old_home, str(new_home))
            path.unlink()
            path.symlink_to(target)
        elif path.is_file():
            data = path.read_bytes()
            if b'\0' not in data:
                try:
                    text = data.decode('utf-8')
                except UnicodeDecodeError:
                    continue
                changed = text.replace(old_home, str(new_home))
                if changed != text:
                    path.write_text(changed)
    if not keep_monitors:
        (stage / '.config/hypr/monitors.lua').write_text(
            '-- Portable default: preferred mode on every connected display.\n'
            'hl.monitor({output = "", mode = "preferred", position = "auto", scale = 1.0})\n')
        (stage / '.config/hypr/monitors.conf').write_text('monitor = , preferred, auto, 1\n')
        # The source PC uses an automatic Sunshine selector hardcoded to DP-1.
        # Use the normal picker on a new machine until the user selects an output.
        xdph = stage / '.config/hypr/xdph.conf'
        if xdph.exists():
            xdph.write_text('\n'.join('# New PC: ' + line if 'custom_picker_binary' in line else line
                                       for line in xdph.read_text().splitlines()) + '\n')
        sunshine = stage / '.config/sunshine/sunshine.conf'
        if sunshine.exists():
            sunshine.write_text('\n'.join(line for line in sunshine.read_text().splitlines()
                                         if not line.strip().startswith(('output_name', 'csfr_allowed_origins'))) + '\n')
        # Display-manager presets can also reapply the source machine's layout.
        shutil.rmtree(stage / '.config/nwg-displays', ignore_errors=True)
    # Native lock layout needs static art before its first use; media art is runtime data.
    profile = stage / '.cache/hyde/landing/profile.png'
    if profile.exists():
        shutil.copy2(profile, profile.with_name('mpris.png'))


def install_packages(repo):
    if not shutil.which('pacman'):
        raise RuntimeError('Package installation is supported on Arch only.')
    names = (repo / 'metadata/desktop-native.txt').read_text().split()
    if names:
        subprocess.run(['sudo', 'pacman', '-S', '--needed'] + names, check=True)
    foreign = (repo / 'metadata/desktop-aur.txt').read_text().split()
    if foreign:
        helper = shutil.which('yay') or shutil.which('paru')
        if not helper:
            raise RuntimeError('Install yay/paru for the recorded AUR desktop packages, then rerun.')
        subprocess.run([helper, '-S', '--needed'] + foreign, check=True)


def restore(args):
    repo = Path(args.repo).resolve()
    home = Path(args.target_home).resolve()
    manifest = verify(repo)
    if home == Path('/') or repo == home or repo.is_relative_to(home / '.config'):
        raise RuntimeError('Unsafe restore destination.')
    if args.target_home != str(Path.home()) and (args.install_packages or args.rebuild_env or args.enable_services):
        raise RuntimeError('Package/environment/service setup requires the current user HOME.')
    with tempfile.TemporaryDirectory(prefix='hyde-restore-') as folder:
        stage = Path(folder)
        shutil.copytree(repo / 'home', stage, dirs_exist_ok=True, symlinks=True)
        unpack_assets(repo, manifest, stage)
        adapt(stage, manifest['source_home'], home, args.keep_monitors)
        entries = [p for p in stage.rglob('*') if p.is_symlink() or p.is_file()]
        print(f'Verified snapshot. Restore {len(entries)} files/links to {home}.')
        if not args.apply:
            print('Preview only. Add --apply to restore. Existing files will be saved first.')
            return
        if args.install_packages:
            install_packages(repo)
        stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        rollback = home / '.local/state/hyde-restore-backups' / stamp
        rollback.mkdir(parents=True, mode=0o700)
        journal = []
        for src in entries:
            rel = src.relative_to(stage)
            dst = home / rel
            # A pre-existing .config/foo link must not redirect writes outside HOME.
            for parent in reversed(dst.parents):
                if parent == home or not parent.is_relative_to(home):
                    continue
                if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                    saved = rollback / parent.relative_to(home)
                    saved.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(parent), saved)
                    parent.mkdir()
                    journal.append({'path': str(parent.relative_to(home)), 'saved_parent': True})
            if dst.exists() or dst.is_symlink():
                saved = rollback / rel
                saved.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(dst), saved)
                journal.append({'path': str(rel), 'replaced': True})
            else:
                journal.append({'path': str(rel), 'replaced': False})
            copy_entry(src, dst)
        json_write(rollback / 'restore-journal.json', journal)
    failures = []
    interface = repo / 'metadata/dconf-interface.ini'
    if home == Path.home() and shutil.which('dconf') and interface.exists():
        (rollback / 'dconf-interface.before.ini').write_text(
            output(['dconf', 'dump', '/org/gnome/desktop/interface/']))
        result = subprocess.run(['dconf', 'load', '/org/gnome/desktop/interface/'],
                                input=interface.read_text(), text=True)
        if result.returncode:
            failures.append('desktop appearance preferences (dconf)')
    if args.rebuild_env:
        for helper in ['python_env.py', 'lua_env.py']:
            result = subprocess.run(['python3', str(home / '.local/lib/hyde/pyutils' / helper), 'sync'])
            if result.returncode:
                failures.append(helper)
    if shutil.which('fc-cache'):
        subprocess.run(['fc-cache', '-f'], check=True)
    if shutil.which('Hyprland') and home == Path.home():
        result = run(['Hyprland', '--verify-config', '-c', str(home / '.local/share/hypr/hyde.lua')], check=False)
        if result.returncode:
            print(result.stdout + result.stderr)
            failures.append('Hyprland config verification (requires compatible Lua-enabled Hyprland)')
    if args.enable_services:
        names = ['app-dev.lizardbyte.app.Sunshine.service']
        available = output(['systemctl', '--user', 'list-unit-files', '--no-legend', '--no-pager'])
        # Preserve service enable links. Do not start remote streaming during restore.
        subprocess.run(['systemctl', '--user', 'daemon-reload'], check=True)
        for name in names:
            if name in available:
                subprocess.run(['systemctl', '--user', 'enable', name], check=True)
    print(f'Restored. Previous files: {rollback}')
    print('Log out/in after setup. Review monitor selection for Sunshine on this PC.')
    if failures:
        raise RuntimeError('Files restored, but setup still needs attention: ' + ', '.join(failures))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    b = commands.add_parser('backup')
    b.add_argument('--repo', default=str(Path.home() / 'My-dotfiles'))
    b.add_argument('--source-home', default=str(Path.home()))
    b.add_argument('--dry-run', action='store_true')
    b.add_argument('--no-push', action='store_true')
    b.add_argument('--no-commit', action='store_true')
    r = commands.add_parser('restore')
    r.add_argument('--repo', default=str(TOOL_DIR))
    r.add_argument('--target-home', default=str(Path.home()))
    r.add_argument('--apply', action='store_true')
    r.add_argument('--keep-monitors', action='store_true')
    r.add_argument('--install-packages', action='store_true')
    r.add_argument('--rebuild-env', action='store_true')
    r.add_argument('--enable-services', action='store_true')
    v = commands.add_parser('verify')
    v.add_argument('--repo', default=str(TOOL_DIR))
    args = parser.parse_args()
    try:
        if args.command == 'backup':
            backup(args)
        elif args.command == 'restore':
            restore(args)
        else:
            manifest = verify(Path(args.repo))
            print(f'Integrity OK: {len(manifest["files"])} config files and all archive parts.')
    except (OSError, RuntimeError, subprocess.CalledProcessError, ValueError, tarfile.TarError) as error:
        print(f'ERROR: {error}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
