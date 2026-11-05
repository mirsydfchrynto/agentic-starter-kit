---
name: linux-systemd
description: "Fix systemd 203/EXEC errors and handle agent self-restarts."
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [linux, systemd, daemon, services, troubleshooting, python, venv]
---

# Linux Systemd Management

When creating, configuring, or debugging `systemd` services, adhere to these operational constraints and solutions:

## 1. The Agent Self-Restart Block (CRITICAL)

**The Pitfall:** As an autonomous agent, you **cannot** execute commands that restart, stop, or enable the `systemd` service currently hosting your own gateway process (e.g., `systemctl --user restart hermes.service`). The gateway monitors the process tree and will actively block any command that sends a `SIGTERM` to itself to prevent accidental "suicides" during a tool call.

**The Workflow:**
- Write the `.service` file.
- Run `systemctl --user daemon-reload`.
- **STOP.** Do not attempt to run `enable` or `start/restart`.
- Instruct the user to run the final commands in a separate, external terminal outside the active chat session.

## 2. Shell Wrappers vs Systemd Watchdogs

**The Pitfall:** 
- Running watchdog scripts or long-lived daemons via raw background subshells (e.g., `bash script.sh &` via terminal tool) is non-persistent across TTY exits, terminal restarts, or system reboots.
- Creating a `.service` file for a Python/Node application by pointing `ExecStart` to a bash wrapper script frequently fails with a `203/EXEC` status code because `systemd` does not handle shell wrappers and environments the same way a TTY does.

**The Solution:**
- For applications: Bypass the shell wrapper and invoke the interpreter directly from the virtual environment/node path, passing the application entry point as the argument.
  *Wrong:* `ExecStart=/home/user/.local/bin/app_wrapper`
  *Right:* `ExecStart=/home/user/project/.venv/bin/python /home/user/project/main.py`
- For watchdog daemons: Always register them as proper systemd user services (`~/.config/systemd/user/<name>.service`), run `systemctl --user daemon-reload`, and `systemctl --user enable --now <name>.service`.

**Environment Variables:**
Ensure the `PATH` is explicitly declared in the service block so subprocesses spawned by the application can find necessary binaries:
`Environment="PATH=/home/user/.local/bin:/usr/local/bin:/usr/bin:/bin"`

## 3. Persistent User Services (Linger)
If a user-level service needs to start on boot without the user logging into a graphical session or TTY, ensure you instruct the user to enable linger:
`loginctl enable-linger $USER`

## 4. PM2 vs Systemd Resurrection Race (CRITICAL)
**The Pitfall:** A process previously managed by PM2 keeps getting resurrected by the PM2 God Daemon even after you `pkill` it, fix `~/.pm2/dump.pm2`, or delete the process from PM2. The daemon holds the old app list in memory; editing the dump file alone is not enough. This causes a port race with your new systemd unit (`Restart=always`).
**The Fix (in order):**
1. `pm2 delete <app>` (or edit dump via `~/.pm2/dump.pm2` removing the entry).
2. **Stop the PM2 daemon entirely** so it re-reads the dump on next start: `pkill -9 -f "PM2 v"` (kills God Daemon + logrotate child).
3. Kill remaining loose processes: `pkill -9 -f <app-name>`.
4. Verify clean: `ps aux | grep <app> | grep -v grep` → empty, then start your systemd unit.
5. Audit survivors first: `pm2 jlist` may show apps long since replaced by systemd units — remove them and keep the daemon minimal (or `pm2 kill` + `systemctl --user disable pm2-resurrect.service` if nothing else needs PM2).
**Verify port ownership after:** `ss -tlnp | grep <port>` must show the systemd unit's PID, not a PM2 child.

## 5. Sudo from the Agent (Hermes hard-block ladder)
The Hermes terminal **blocks all password-injection routes** for sudo: `sudo -S` stdin piping, `SUDO_PASSWORD=` in `.env` (file is protected from editing), and `SUDO_ASKPASS` wrapper scripts are all refused/blocked by design. Do not attempt them; each attempt burns an approval cycle and can time out.
**The Workflow:** prepare the full copy-paste block (one `bash -c '...'` string with all sudo commands), hand it to the user, and have them run it in their own terminal. Verify the result after they paste output back. Works for journal caps, snap removals, apt cleanups, fstab edits — anything needing root.

**Agent-side fallback (user says "tolong jalankan"):** `pkexec` is the ONE path that works from the agent when sudo is passwordless-NOPASSWD — it shows a GUI approval prompt (no terminal password, no stdin pipe). Verified used for ufw rules (`pkexec ufw ...`) and would be the next attempt for journal/snap/apt when the user insists the agent run them. Do NOT retry `sudo -S`, `.env` SUDO_PASSWORD, or SUDO_ASKPASS wrappers — all hard-blocked (attempting them burns approval cycles and can time out with a "do not retry" block).

## 6. Storage Layout Awareness (loop images + root pressure)
- `/home/irsyad/Gudang` is NOT a separate partition — it is a 99G ext4 image `/mnt/windows/linux_data.img` mounted via loop device (`findmnt /home/irsyad/Gudang` shows `/dev/loop5`). Big caches (.gradle, sdk, .hermes) are symlinked there deliberately. Check `df -h /home/irsyad/Gudang` before assuming root is the only bottleneck.
- Root `/` is a small 63G partition — it fills fast; keep ≥10G headroom. Chrome profile (`~/.config/google-chrome`), `.vscode`, `.npm` are the usual suspects.
- Disk-full rescue ladder with verified commands: see `references/disk-full-rescue.md`.

## 7. Systemd as Sole Process Manager (consolidation pattern)
When a service migrates from PM2/nohup/background-subshell to a systemd unit, make systemd the ONLY owner:
- Create unit with `Restart=always`, `RestartSec=3-5`, `EnvironmentFile` for `.env`, `StandardOutput/StandardError=append:<log>`.
- Kill ALL loose instances before starting the unit (`pkill -9 -f <name>`), otherwise a port race occurs (unit starts, fails "address in use", old process keeps serving).
- Disable/remove any old watchdog service whose only job was restart-on-crash — systemd `Restart=always` supersedes it (verified: `9router-watchdog.service` disabled, `freebuff-proxy` handled by its unit). Keep watchdog cron only for health-check + side-effects (proxy rotation, Telegram alerts), never for nohup-starting the process.
- Verify port ownership after: `ss -tlnp | grep <port>` shows the unit's PID.
- Cross-check `dump.pm2` / PM2 God Daemon for leftover resurrect entries (see §4).