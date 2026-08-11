# Camofox Config.yaml Reference

Complete `browser` section in `~/.hermes/config.yaml`:

```yaml
browser:
  inactivity_timeout: 120        # Seconds before auto-closing idle sessions
  command_timeout: 30             # Timeout for browser commands (screenshot, navigate, etc.)
  record_sessions: false          # Auto-record sessions as WebM to ~/.hermes/browser_recordings/
  allow_private_urls: false       # Allow navigating to private/local URLs
  engine: camofox                 # auto | camofox | browserbase | playwright
  auto_local_for_private_urls: true
  cdp_url: ""                     # Optional CDP override for Chromium-family browsers
  dialog_policy: must_respond     # must_respond | auto_dismiss | auto_accept
  dialog_timeout_s: 300           # Auto-dismiss timeout for must_respond
  camofox:
    managed_persistence: false    # true = persist cookies/logins across restarts
    user_id: ""                   # External user ID for shared sessions
    session_key: ""               # Session key for tab matching
    adopt_existing_tab: false     # Reuse existing tab before creating new one
    rewrite_loopback_urls: false  # Docker: rewrite localhost to host.docker.internal
    loopback_host_alias: host.docker.internal
  cloud_provider: local           # local | browserbase
  use_gateway: false
```

## Key Config Paths

| Config Path | Env Var | Effect |
|-------------|---------|--------|
| `browser.engine` | — | Set to `camofox` to force Camofox |
| `browser.camofox.managed_persistence` | — | Keep cookies/logins across restarts |
| `browser.camofox.user_id` | `CAMOFOX_USER_ID` | Shared session identity |
| `browser.camofox.session_key` | `CAMOFOX_SESSION_KEY` | Tab matching key |
| `browser.camofox.adopt_existing_tab` | `CAMOFOX_ADOPT_EXISTING_TAB` | Reuse existing tabs |
| `browser.camofox.rewrite_loopback_urls` | `CAMOFOX_REWRITE_LOOPBACK_URLS` | Docker loopback fix |
| `browser.camofox.loopback_host_alias` | `CAMOFOX_LOOPBACK_HOST_ALIAS` | Loopback alias |

## Managed Persistence

When `managed_persistence: true`:
- Hermes sends a deterministic profile-scoped userId to Camofox
- Server reuses the same Firefox profile across sessions
- Cookies, localStorage, IndexedDB persist between agent tasks
- Login state survives restarts

**Pitfall:** Must be at `browser.camofox.managed_persistence`, NOT top-level. A common mistake:

```yaml
# ❌ Wrong — Hermes ignores this
managed_persistence: true

# ✅ Correct
browser:
  camofox:
    managed_persistence: true
```

## Docker Loopback Rewriting

When Camofox runs in Docker and needs to access host-served apps:

```yaml
browser:
  camofox:
    rewrite_loopback_urls: true
    loopback_host_alias: host.docker.internal
```

This rewrites `http://127.0.0.1:3000` → `http://host.docker.internal:3000` for page navigation only. Does NOT change `CAMOFOX_URL`.
