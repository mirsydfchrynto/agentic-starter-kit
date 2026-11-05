# Disk Full Rescue — Verified Ladder (Irsyad laptop, 2026-08)

Scenario: root `/` at 97% (1.9G free), swap pressure, services at risk. Freed 1.9G → 8.9G without sudo, then handed sudo block to user.

## Audit order (read-only first, batch)
```bash
df -h | grep -vE "tmpfs|udev|loop|efivarfs"        # all partitions
du -x -h --max-depth=1 / 2>/dev/null | sort -rh | head -12   # root breakdown
du -h --max-depth=1 /home/irsyad 2>/dev/null | sort -rh | head -15
du -h --max-depth=1 /var/log 2>/dev/null | sort -rh | head   # journal lives here
journalctl --disk-usage
ps aux --sort=-%mem | head -12                      # RAM hogs (chrome renderers)
```

## No-sudo wins (do these first, biggest safe gains)
- `rm -rf ~/.cache/google-chrome/*` — skip if chrome running (fails harmlessly)
- `rm -rf ~/.cache/puppeteer/* ~/.cache/ms-playwright/* ~/.cache/pnpm/* ~/.cache/Google/*`
- `rm -rf ~/.npm` (npm cache, re-downloadable)
- Old duplicate VS Code extensions: `~/.vscode/extensions/<name>-<oldver>` — keep newest per publisher (geminicodeassist, copilot-chat, vscjava.migrate-java-to-azure had 4–8 stale versions)
- `rm -rf ~/.m2/repository` only if no Java process runs
- Old agent logs: `rm -f ~/.hermes/logs/*.log.[1-9]` (rotated)

## Sudo block (hand to user as one copy-paste block)
```bash
sudo mkdir -p /etc/systemd/journald.conf.d
echo -e "[Journal]\nSystemMaxUse=500M\nSystemKeepFree=2G\nRuntimeMaxUse=200M" | sudo tee /etc/systemd/journald.conf.d/10-size.conf > /dev/null
sudo systemctl restart systemd-journald
sudo journalctl --vacuum-size=500M --quiet
journalctl --disk-usage
sudo snap remove android-studio --revision=236   # older snap rev, keep newest
sudo apt-get autoclean -y
df -h /
```
Journal default is UNBOUNDED — cap it permanently, vacuum once. Snap keeps old revisions mounted as loop devices (`losetup -a` shows them).

## Verify
`df -h /` before/after each batch. Report delta honestly.

## Pitfall: don't delete without confirming
User explicitly asked for confirmation BEFORE deleting anything ambiguous (a whole 1.4G app dir was deleted without confirmation — user correction). For non-cache dirs: state what it is, whether anything references it, whether it can be restored, then WAIT for user go-ahead.