# Camofox Browser Configuration

Camofox is an anti-detection browser backend for Hermes Agent, built on Camoufox (Firefox fork with C++ engine-level fingerprint spoofing). No JavaScript injection — anti-detection happens at the browser engine level.

Use when: standard browser tools get blocked by Cloudflare, Akamai, or bot detection; when you need persistent browser sessions with login state; when you need anti-fingerprint browsing.

## Additional References

- `references/camofox-install-cli.md` — CLI commands, server endpoints, Docker networking, Makefile targets
- `references/camofox-setup-notes.md` — Critical setup notes, Firefox binary download (~311MB), macOS launchd autostart, emergency fallbacks
- `references/camofox-playwright-anti-detection.md` — Playwright anti-detection patterns for when Camofox is unavailable
- `references/camofox-macos-launchd.md` — macOS launchd plist for auto-starting Camofox as a background service

## Installation

Camofox requires a running Camofox Browser Server. Three install methods:

### Option A: npm global install (recommended for local use)

```bash
npm install -g camofox-browser
camofox-browser --version  # verify
```

**Pitfall:** npm install can timeout on slow connections. Use `timeout=120` or run it outside Hermes. If it times out but `which camofox-browser` returns a path, it likely succeeded — verify with `--version`.

### Option B: Docker

```bash
git clone https://github.com/redf0x1/camofox-browser.git
cd camofox-browser
make up    # auto-detects arch, starts on port 9377

# Or custom build with VNC + persistence
make build
mkdir -p ~/.camofox-docker
docker run -d \
  --name camofox-browser \
  --restart unless-stopped \
  -p 9377:9377 -p 6080:6080 -p 5901:5900 \
  -e CAMOFOX_PORT=9377 \
  -e ENABLE_VNC=1 -e VNC_BIND=0.0.0.0 -e VNC_RESOLUTION=1920x1080 \
  -e MAX_OLD_SPACE_SIZE=2048 \
  -v ~/.camofox-docker:/root/.camofox \
  camofox-browser:135.0.1-aarch64
```

### Option C: From source

```bash
git clone https://github.com/redf0x1/camofox-browser.git
cd camofox-browser
npm install && npm run build && npm start
```

### Starting the server (npm install)

```bash
# Start in background (Hermes terminal)
terminal(command="camofox-browser", background=true, notify_on_complete=true)

# Health check
curl -s http://localhost:9377/health
# Expected: {"ok":true,"running":true,"engine":"camoufox","version":"2.4.5",...}
```

**Note:** The npm-installed server does NOT auto-start. You must start it manually or set up a launch agent/systemd service. Docker containers with `--restart unless-stopped` auto-restart.

## Quick Start (Configuration)

```bash
# 1. Start the Camofox server (see Installation above)

# 2. Set the server URL in ~/.hermes/.env
echo 'CAMOFOX_URL=http://localhost:9377' >> ~/.hermes/.env

# 3. Switch browser engine
hermes config set browser.engine camofox

# 4. Restart Hermes (new session or /new)
```

## Environment Variables

All set in `~/.hermes/.env`. **Environment variables take precedence over config.yaml.**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CAMOFOX_URL` | **Yes** | — | Camofox server URL (e.g. `http://localhost:9377`) |
| `CAMOFOX_USER_ID` | No | random | User ID for tab management. Setting this enables "externally managed" mode |
| `CAMOFOX_SESSION_KEY` | No | per-task | Session key sent on tab creation, used to match existing tabs during adoption |
| `CAMOFOX_ADOPT_EXISTING_TAB` | No | `false` | Reuse existing tab for the userId before creating new one |
| `CAMOFOX_REWRITE_LOOPBACK_URLS` | No | `false` | Rewrite localhost/127.0.0.1 URLs for Docker networking |
| `CAMOFOX_LOOPBACK_HOST_ALIAS` | No | `host.docker.internal` | Target host for loopback URL rewriting |

## Config.yaml Settings

Path: `browser.camofox` in `~/.hermes/config.yaml`

```yaml
browser:
  engine: camofox              # auto | camofox | browserbase | local
  inactivity_timeout: 120      # Seconds before auto-closing idle sessions
  command_timeout: 30          # Timeout for browser commands
  record_sessions: false       # Auto-record sessions as WebM videos
  cdp_url: ""                  # Optional CDP override
  dialog_policy: must_respond  # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300        # Auto-dismiss timeout under must_respond

  camofox:
    managed_persistence: false   # true = cookies/logins survive across restarts
    user_id: ""                  # External userId (overrides random)
    session_key: ""              # Session key for tab matching
    adopt_existing_tab: false    # Reuse existing tab
    rewrite_loopback_urls: false # Docker loopback rewriting
    loopback_host_alias: host.docker.internal
```

**Pitfall:** `managed_persistence` must be under `browser.camofox.managed_persistence`, NOT top-level. A common mistake is writing it at the wrong path — Hermes silently falls back to random ephemeral userId and login state is lost every session.

## Docker Loopback Rewriting

When Camofox runs in Docker and needs to access web apps on the host machine:

```yaml
browser:
  camofox:
    rewrite_loopback_urls: true
    loopback_host_alias: host.docker.internal
```

Or via env vars:
```bash
CAMOFOX_REWRITE_LOOPBACK_URLS=true
CAMOFOX_LOOPBACK_HOST_ALIAS=host.docker.internal
```

**How it works:** Page URLs like `http://127.0.0.1:3000` get rewritten to `http://host.docker.internal:3000` inside the container. Only applies to page navigation URLs with loopback hosts (localhost, 127.0.0.1, ::1). Does NOT change CAMOFOX_URL itself.

**When to disable:** Non-Docker installs where the browser runs on the host — loopback URLs are already correct.

## Persistent Browser Sessions

By default, each Camofox session gets a random identity — cookies and logins don't survive across agent restarts.

To enable persistence:

```yaml
browser:
  camofox:
    managed_persistence: true
```

What Hermes does:
1. Sends a deterministic profile-scoped userId to Camofox
2. Skips server-side context destruction on cleanup
3. Cookies and logins survive between agent tasks

Requires full Hermes restart after config change.

## Multi-User Tab Adoption

When multiple agents share one Camofox server, or you want to see/interact with what the agent is doing:

| Setting | Env var | Effect |
|---------|---------|--------|
| `browser.camofox.user_id` | `CAMOFOX_USER_ID` | UserId for tab creation. Enables "externally managed" mode |
| `browser.camofox.session_key` | `CAMOFOX_SESSION_KEY` | Session key for tab matching during adoption |
| `browser.camofox.adopt_existing_tab` | `CAMOFOX_ADOPT_EXISTING_TAB` | Reuse existing tab before creating new one |

```yaml
browser:
  camofox:
    user_id: shared-camofox
    session_key: visible-tab
    adopt_existing_tab: true
```

When `user_id` is set:
- Hermes skips destructive cleanup at task end
- Existing tabs with matching userId can be reused
- Useful for VNC observation of agent actions

## Troubleshooting

### `browserConnected: false` / `/tabs` returns 500

The most common failure: Camofox server is running but the underlying Firefox browser process is disconnected. All `browser_navigate` calls fail with `500 Server Error: Internal Server Error for url: http://localhost:9377/tabs`.

**Diagnosis:**
```bash
# Check server health — look at browserConnected field
curl -s http://localhost:9377/
# {"ok":true,"running":true,"engine":"camoufox","version":"2.4.5","browserConnected":false,...}

# Check logs for errors
cat ~/.hermes/logs/camofox*.log 2>/dev/null | tail -30
```

**Fixes (try in order):**
1. **Kill and let Hermes restart the process:** `pkill -f camofox-browser` — Hermes auto-restarts it; wait 3-5 seconds, then retry browser_navigate
2. **Check if Camofox Firefox binary is present:** The server starts but can't launch Firefox if the binary is missing or corrupted. Reinstall with `npm install -g camofox-browser`.
3. **Resource issues:** Check `ps aux | grep camo` — if memory usage is very high, the Firefox process may have been OOM-killed. Restart the server.
4. **Switch engine as fallback:** `hermes config set browser.engine auto`

### Chrome Headless Fallback (macOS)

When Camofox is completely broken and you need a screenshot NOW:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --disable-gpu \
  --screenshot=/tmp/screenshot.png \
  --window-size=1920,1080 \
  --no-sandbox \
  "https://target-url.com"
```

### Logs Location

Camofox logs: `~/.hermes/logs/camofox*.log` (JSON lines format).
Hermes agent logs: `hermes logs` command or `~/.hermes/logs/hermes*.log`.

## Pitfalls

1. **Wrong config path for managed_persistence** — Must be `browser.camofox.managed_persistence`, not top-level. Hermes silently ignores the wrong path.
2. **Missing CAMOFOX_URL** — Without this, browser tools fall back to Browserbase or local agent-browser.
3. **Docker loopback not rewritten** — If Camofox can't reach host services, check `rewrite_loopback_urls` setting.
4. **Stale config after changes** — Browser config changes need `/new` or full Hermes restart to take effect.
5. **Engine mismatch** — If `browser.engine` is set to `local` or `browserbase`, Camofox settings are ignored even if CAMOFOX_URL is set.
6. **`browserConnected: false` after restart** — If killing and restarting doesn't fix it, the Firefox binary itself may be corrupted. Reinstall camofox-browser package.
7. **Don't loop on `browser_navigate` failures** — If it fails 2+ times with the same error, switch strategy (kill process, change engine, use Chrome headless fallback) instead of retrying.
8. **`.env` changes are NOT live** — The browser tool reads `CAMOFOX_URL` at session start. Commenting it out or changing it mid-session does NOT redirect the browser tool away from Camofox. You must start a new Hermes session (or restart the app) for `.env` changes to take effect.
9. **Install/cache issues** — Binary missing, cache cleanup loops, SIGKILL from Gatekeeper, and launchd configuration are covered in `references/camofox-setup-notes.md`.
