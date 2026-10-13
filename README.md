# My portable Hyprland + HyDE desktop

This snapshot restores my current **Lua-based** HyDE desktop after installing
Arch Linux, a compatible Lua-enabled Hyprland, and HyDE. The recorded system
uses Hyprland 0.56.2; the exact package versions and local HyDE commit are in
`metadata/`. A newer HyDE installer may change APIs. Restore these files after
the installer, rebuild the environments, and check the configuration before login.

## On another PC

```bash
git clone https://github.com/amadeus177153/My-dotfiles.git
cd My-dotfiles
./restore.sh                        # verify and preview; no changes
./restore.sh --apply --install-packages --rebuild-env --enable-services
```

Run as your normal user, not root. The package step calls sudo for Arch's
recorded desktop packages; AUR packages require yay or paru. Install HyDE first.
The restore copies the snapshot, rebuilds HyDE's Python/Lua environments, updates
the font cache, and checks Hyprland when its executable is available. It does
not change GPU drivers, boot settings, disks, system PAM, or your login shell.
Use your preferred UWSM/HyDE login session, then log out/in when setup finishes.

`./restore.sh --apply` is enough when the packages and HyDE environments are
already installed. `--keep-monitors` keeps my original HDMI-A-1/DP-1 layout;
the default uses every monitor's preferred mode and automatic placement.
A new PC's Sunshine uses the normal screen picker until its output is selected.
Review `.config/hypr/scripts/sunshine_res.sh` before using its original streaming
resolution commands: these deliberately refer to my two physical displays.
Keyboard layout remains `latam` and all my custom shortcuts remain intact.

Existing destination files are moved into
`~/.local/state/hyde-restore-backups/<timestamp>/` before replacement. The
restore journal lists replaced and newly created paths. Previous dconf appearance
preferences are also saved when restoring to your actual home. Unrelated destination
files are preserved. Run from a TTY or before entering Hyprland when possible.
For inspection without touching the real home:

```bash
./restore.sh --apply --target-home /tmp/my-hyde-preview
python3 backup.py verify
python3 test_backup.py              # isolated integration checks
```

## Back up this PC

```bash
~/respaldo_hyde.sh                 # snapshot, commit changes, push current branch
~/respaldo_hyde.sh --no-push       # snapshot and commit locally
~/respaldo_hyde.sh --dry-run       # build/check temporary snapshot only
```

After cloning on another PC, use `./respaldo_hyde.sh --repo "$PWD"` from the repo.
The default location is `~/My-dotfiles`. The tool requires a Git repository,
refuses unrelated staged changes, serializes concurrent backups, stops on errors,
and reports a failed push accurately. It never force-pushes. Missing optional
configs are skipped. Snapshot directories are refreshed so deleted source files
do not persist in the newest snapshot. Git history retains older backups.

## What is included

- User Hyprland Lua/conf modules, shortcuts, rules, animations, scripts, Hyprlock,
  HyDE configuration, all installed HyDE themes and their wallpapers.
- Active `~/.local/share/hypr` entrypoint and default modules, shared HyDE/Waybar/
  Rofi/wallbash resources, and patched `~/.local/lib/hyde` helpers plus hyde-shell.
  This includes the wallpaper randomization, Waybar restart, launcher, screenshot,
  logout menu, cursor, and native lockscreen fixes from this working desktop.
- Fonts, icons/cursors (including Miku and Teto), GTK themes, Qt/Kvantum settings,
  terminal/shell config, custom Zsh plugins, Fastfetch, application associations,
  desktop launchers, user units and enable links, and the dconf desktop appearance
  preferences (fonts, cursors, dark mode).
- HyDE's theme/layout/color state, selected wallpaper and static lockscreen
  background/avatar. Recent media/clipboard/history caches are excluded.
- Sunshine app/settings files only. Pairing/authentication must be set up again
  on the new PC. Source-machine output/network settings are removed on restore
  unless `--keep-monitors` is supplied.
- Arch native/AUR package inventories, package versions, Flatpak application IDs,
  enabled user/system service inventories, and the local HyDE commit ID.

`--install-packages` installs the recorded **desktop subset**, not every package
on the old PC. The complete package and Flatpak lists are references for extra
applications, games and development tools you want to reinstall. System services
are inventoried only. User enable symlinks are copied; missing unit providers
must be installed. `--enable-services` reloads user units and enables Sunshine
if installed; it does not start a streaming session. Third-party application
binaries, game data, browser profiles and system installations are not included.

`metadata/backup-scope.txt` gives the exact roots and exclusions.
`metadata/manifest.json` records SHA-256 hashes, permissions and symbolic links.
Large visual assets are deterministic gzip/tar archives split into 45 MiB parts,
so ordinary Git can track them below GitHub's per-file limits without Git LFS.
See [GitHub's file-size documentation](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).
Archives are verified and unpacked automatically. Unchanged assets do not produce
new blobs; changing large asset collections will increase repository history.

Home paths in text files and symlinks are adapted to the destination user. The
snapshot uses the standard `~/.config`, `~/.local/share` and `~/.local/state`
locations. Custom XDG locations need manual adjustment.

## Private data excluded

SSH/GPG keys, Sunshine credentials/certificates/pairing state, browser sessions,
password stores, shell history, API environment files, logs, clipboard databases,
package caches, Python/Lua virtual environments, and personal documents are not
in the managed snapshot. Name-based exclusions cannot recognize every possible
secret pasted into a custom config; keep private values in separate `.env` or
credential files and inspect config changes before publishing.

## Previous backups

The older configurations under `OLD/` were recovered from the accidentally
deleted repository and remain as historical references.
**Only `home/`, `assets/` and `metadata/` are used by the new restore.** The new
snapshot never sources a configuration from those older reference directories.
The original Git history is retained; it has not been rewritten or erased.
