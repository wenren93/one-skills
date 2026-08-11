---
name: camofox-setup
description: "Install and configure Camofox anti-detection browser for Hermes Agent — npm install, launchd auto-start, environment variables, config.yaml, and troubleshooting."
version: 1.0.0
author: super-xiaoi
platforms: [macos, linux]
metadata:
  hermes:
    tags: [browser, camofox, automation, anti-detection, launchd, setup]
    related_skills: [hermes-agent]
---

# Camofox Browser Setup

Install and configure [Camofox Browser Server](https://github.com/redf0x1/camofox-browser) — an anti-detection browser engine for Hermes Agent. Camofox wraps Camoufox (Firefox fork with C++ engine-level fingerprint spoofing) behind a REST API.

## When to Use

- Setting up Camofox on a new machine
- Configuring Hermes to use Camofox as browser engine
- Troubleshooting Camofox startup or profile issues
- Setting up macOS auto-start via launchd

## Quick Reference

```bash
# Install globally
npm install -g camofox-browser

# Set environment variable
echo 'CAMOFOX_URL=http://localhost:9377' >> ~/.hermes/.env

# Set browser engine
hermes config set browser.engine camofox

# Start server
camofox-browser

# Health check
curl http://localhost:9377/health
```

## Step-by-Step

### 1. Install Camofox

```bash
npm install -g camofox-browser
```

**Pitfall: npm install may appear to time out** (120s+) but actually complete successfully. Always verify:

```bash
camofox-browser --version
# or check symlink exists:
ls -la ~/.hermes/node/bin/camofox-browser
```

If symlink exists but target is missing (happens after interrupted installs), reinstall:

```bash
npm cache clean --force
npm install -g camofox-browser --verbose
```

### 1b. Download Camoufox Firefox Binary (~311MB) ⚠️ CRITICAL

After npm install, you MUST fetch the Camoufox Firefox binary:

```bash
npx camoufox-js fetch
```

**⚠️ This downloads ~311MB and can be VERY slow without a proxy.** On typical China networks, ETA can be 2-3 hours.

**Workaround with proxy:**
```bash
export https_proxy=http://127.0.0.1:7890  # or your proxy
npx camoufox-js fetch
```

**⚠️ Downloads from GitHub** — the binary is hosted on `github.com/daijro/camoufox/releases` and the mmdb on `github.com/P3TERX/GeoLite.mmdb/releases`. From China mainland, GitHub may be completely unreachable (connection timeout after 10s). Signs: `ConnectTimeoutError: Connect Timeout Error (attempted address: github.com:443, timeout: 10000ms)`. If no proxy is available, consider downloading via a mirror or on another machine and copying the `~/Library/Caches/camoufox/` directory manually.

The binary is cached in `~/Library/Caches/camoufox/` (macOS).

**Without this binary, Camofox will fail with:**
> "Cannot verify profile compatibility for user ... installed Camoufox version could not be determined"

This error is NOT a profile issue — it means the Firefox binary is missing.

### 2. Configure Environment

Add to `~/.hermes/.env`:

```
CAMOFOX_URL=http://localhost:9377
```

### 3. Set Browser Engine

```bash
hermes config set browser.engine camofox
```

This sets `browser.engine: camofox` in `~/.hermes/config.yaml`.

**Pitfall: Config may revert to `playwright`** after `hermes update` or config migration. Always verify after updates:

```bash
grep "engine:" ~/.hermes/config.yaml | head -1
```

### 4. Start and Verify

```bash
camofox-browser
# In another terminal:
curl http://localhost:9377/health
```

Expected response:
```json
{"ok":true,"running":true,"engine":"camoufox","version":"2.4.5",...}
```

### 5. macOS Auto-Start (launchd)

Create `~/Library/LaunchAgents/com.camofox.browser.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.camofox.browser</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Users/one/.hermes/node/bin/node</string>
        <string>/Users/one/.hermes/node/lib/node_modules/camofox-browser/bin/camofox-browser.js</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardOutPath</key>
    <string>/Users/one/.hermes/logs/camofox.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/one/.hermes/logs/camofox-error.log</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>PATH</key>
        <string>/Users/one/.hermes/node/bin:/usr/local/bin:/usr/bin:/bin</string>
        <key>HOME</key>
        <string>/Users/one</string>
    </dict>
</dict>
</plist>
```

**Pitfall: Use full node path, not symlink.** Background processes cannot resolve symlinks in `~/.hermes/node/bin/`. The plist must use:
- `/Users/one/.hermes/node/bin/node` as the executable
- `/Users/one/.hermes/node/lib/node_modules/camofox-browser/bin/camofox-browser.js` as the argument

NOT just the symlink `/Users/one/.hermes/node/bin/camofox-browser` — this will fail with "No such file or directory".

Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.camofox.browser.plist
```

Management commands:

```bash
# Check status
launchctl list | grep camofox

# Stop
launchctl unload ~/Library/LaunchAgents/com.camofox.browser.plist

# Start
launchctl load ~/Library/LaunchAgents/com.camofox.browser.plist

# View logs
tail -f ~/.hermes/logs/camofox.log
tail -f ~/.hermes/logs/camofox-error.log
```

## Pitfalls

### Profile compatibility errors / "Camoufox version could not be determined"

**Symptom:** `Cannot verify profile compatibility for user "xxx": installed Camoufox version could not be determined`

**Root cause:** The Camoufox Firefox binary has NOT been downloaded. This is NOT a profile issue despite the error message mentioning "profile".

**⚠️ CRITICAL: Service cleans cache on startup!**
The Camofox service deletes `~/Library/Caches/camoufox/` when it starts. If you download the binary while the service is running, it will be deleted immediately. You MUST follow this exact order:

**Fix:**
```bash
# 1. STOP the service first
launchctl unload ~/Library/LaunchAgents/com.camofox.browser.plist
sleep 2

# 2. Download the binary (service must be stopped!)
npx camoufox-js fetch

# If download is too slow, use proxy
export https_proxy=http://your-proxy:port
npx camoufox-js fetch

# 3. Remove macOS quarantine attribute
xattr -rd com.apple.quarantine ~/Library/Caches/camoufox/

# 4. Clean old profiles
rm -rf ~/.camofox/profiles/*

# 5. START the service
launchctl load ~/Library/LaunchAgents/com.camofox.browser.plist
```

**Never download while the service is running** — it will delete the cached binary and you'll be stuck in a download-delete loop.

If the binary download fails repeatedly, check `~/Library/Caches/camoufox/` — if empty, the binary was never fetched.

**Verification after download** (always check before proceeding):
```bash
# Expected: ~697MB total, 3 items
du -sh ~/Library/Caches/camoufox/
ls ~/Library/Caches/camoufox/  # should have: Camoufox.app/ GeoLite2-City.mmdb version.json
cat ~/Library/Caches/camoufox/version.json  # e.g. {"version":"150.0.2","release":"alpha.25"}
```

**Disk space:** Camoufox cache requires ~700MB. Profiles add ~50-100MB each.

**Partial downloads:** The GeoLite2-City.mmdb (63MB) and the main Camoufox.app (633MB) download separately. If the mmdb fails (different GitHub repo: `P3TERX/GeoLite.mmdb`), the main binary may still be usable — the mmdb is for locale/geo features only.

### Server won't start after plist load

**Check:** Is the process running?
```bash
ps aux | grep camofox | grep -v grep
```

**Check:** Any errors in log?
```bash
cat ~/.hermes/logs/camofox-error.log | tail -20
```

**Common cause:** Symlink resolution failure. Update plist to use full node path (see Step 5).

### CAMOFOX_API_KEY warning

The warning `CAMOFOX_API_KEY not set — protected endpoints are only intended for loopback-only deployments` is **expected for local-only setups**. Only set CAMOFOX_API_KEY if exposing the server beyond localhost.

### Switching away from Camofox when it's broken

If Camofox is broken (e.g. missing Firefox binary) and you need browser functionality NOW, changing `browser.engine` alone is **NOT enough**. The Hermes browser tool checks `CAMOFOX_URL` from `~/.hermes/.env` first and routes to the Camofox server regardless of the engine setting.

**Correct sequence to fully switch away:**

```bash
# 1. Comment out CAMOFOX_URL in .env
sed -i '' 's/^CAMOFOX_URL=/#CAMOFOX_URL=/' ~/.hermes/.env

# 2. Change engine
hermes config set browser.engine playwright

# 3. Restart the Hermes session (the .env is loaded at session start)
```

Without restarting the session, the browser tool may still try to connect to `localhost:9377`.

**Emergency fallback — Playwright Python (no session restart needed):**

If you need a browser screenshot or page interaction immediately and can't restart:

```bash
pip3 install playwright
playwright install chromium
```

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com')
    page.screenshot(path='/tmp/screenshot.png')
    browser.close()
```

This bypasses the Hermes browser tool entirely and works standalone. Useful for screenshots, page content extraction, and basic automation when the configured browser engine is unavailable.

See `references/browser-fallback-playwright.md` for a full quick-reference.

**For bot-protected sites**, see `references/playwright-anti-detection.md` — includes anti-detection args, user-agent spoofing, and webdriver hiding needed to bypass Cloudflare/Akamai/custom bot detection.

## Environment Variables Reference

| Variable | Config Equivalent | Description |
|----------|-------------------|-------------|
| `CAMOFOX_URL` | — | Server URL (e.g., `http://localhost:9377`) |
| `CAMOFOX_USER_ID` | `browser.camofox.user_id` | External user ID for shared sessions |
| `CAMOFOX_SESSION_KEY` | `browser.camofox.session_key` | Session key for tab matching |
| `CAMOFOX_ADOPT_EXISTING_TAB` | `browser.camofox.adopt_existing_tab` | Reuse existing tabs |
| `CAMOFOX_REWRITE_LOOPBACK_URLS` | `browser.camofox.rewrite_loopback_urls` | Docker loopback rewriting |
| `CAMOFOX_LOOPBACK_HOST_ALIAS` | `browser.camofox.loopback_host_alias` | Loopback alias (default: `host.docker.internal`) |

**Priority:** Environment variables take precedence over config.yaml.
