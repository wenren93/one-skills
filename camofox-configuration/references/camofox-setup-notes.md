# Camofox Setup Notes (from camofox-setup skill)

## Camoufox Firefox Binary Download (~311MB) ⚠️ CRITICAL

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

## Profile Compatibility Errors / "Camoufox version could not be determined"

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

## macOS Auto-Start (launchd)

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

## Emergency Fallback — Playwright Python

If Camofox is completely broken and you need a browser NOW:

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

## Emergency Fallback — Chrome Headless (macOS)

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new \
  --disable-gpu \
  --screenshot=/tmp/screenshot.png \
  --window-size=1920,1080 \
  --no-sandbox \
  "https://target-url.com"
```

Notes:
- Output is a full-page PNG at the specified resolution.
- `--headless=new` is the modern headless mode (preferred over old `--headless`).
- No anti-detection — this is plain Chrome. Fine for screenshots of non-protected sites.
