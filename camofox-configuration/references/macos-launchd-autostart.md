# macOS Launchd Auto-Start for Camofox

Camofox installed via npm does NOT auto-start. On macOS, use launchd to run it as a persistent background service.

## Setup

### 1. Create plist file

Path: `~/Library/LaunchAgents/com.camofox.browser.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.camofox.browser</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/one/.hermes/node/bin/camofox-browser</string>
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
    </dict>
</dict>
</plist>
```

**Pitfall:** The `ProgramArguments` path must point to the actual binary. Verify with `which camofox-browser` first. The PATH env var in the plist must include the node bin directory or the service won't find dependencies.

### 2. Load the service

```bash
launchctl load ~/Library/LaunchAgents/com.camofox.browser.plist
```

### 3. Verify

```bash
# Check service status
launchctl list | grep camofox
# Expected: <pid>  0  com.camofox.browser

# Health check
curl -s http://localhost:9377/health
```

## Management Commands

```bash
# Stop service
launchctl unload ~/Library/LaunchAgents/com.camofox.browser.plist

# Start service
launchctl load ~/Library/LaunchAgents/com.camofox.browser.plist

# View logs
tail -f ~/.hermes/logs/camofox.log

# View errors
tail -f ~/.hermes/logs/camofox-error.log
```

## Key Points

- `RunAtLoad: true` — starts on login
- `KeepAlive: true` — restarts if it crashes
- Logs go to `~/.hermes/logs/camofox*.log`
- The service replaces any manually started `camofox-browser` process (kill the manual one first)
