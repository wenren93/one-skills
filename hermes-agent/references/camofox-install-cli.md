# Camofox Installation & CLI Reference

**Source:** https://github.com/redf0x1/camofox-browser

## CLI Commands (after npm global install)

```bash
# Open a URL
camofox open https://example.com

# Get accessibility snapshot
camofox snapshot

# Click an element by ref
camofox click e5

# Type into an element
camofox type e3 "hello world"

# Full command list
camofox --help
```

## Server Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check — returns `{"ok":true,"running":true,...}` |
| `/tabs` | GET | List open tabs |
| `/snapshot` | POST | Get accessibility tree snapshot |
| `/navigate` | POST | Navigate to URL |
| `/click` | POST | Click element by ref |
| `/type` | POST | Type text into element |
| `/screenshot` | POST | Take screenshot |

## Environment Variables (complete list from docs)

| Variable | Description |
|----------|-------------|
| `CAMOFOX_PORT` | Server port (default: 9377) |
| `CAMOFOX_URL` | Server URL for Hermes to connect |
| `CAMOFOX_HOST` | Bind address (use `0.0.0.0` for Docker) |
| `CAMOFOX_AUTH_MODE` | Auth mode: `auto`, `disabled`, `required` |
| `CAMOFOX_API_KEY` | API key for auth when mode is `required` or `auto` |
| `CAMOFOX_USER_ID` | User ID for multi-user tab management |
| `CAMOFOX_SESSION_KEY` | Session key for tab matching |
| `CAMOFOX_ADOPT_EXISTING_TAB` | Reuse existing tabs |
| `CAMOFOX_REWRITE_LOOPBACK_URLS` | Rewrite localhost URLs for Docker |
| `CAMOFOX_LOOPBACK_HOST_ALIAS` | Target host for loopback rewriting |

## Docker Networking

When running Camofox in Docker, create a dedicated network:

```bash
docker network create camofox-agents
docker run -d \
  --name camofox-browser \
  --network camofox-agents \
  -e CAMOFOX_HOST=0.0.0.0 \
  -e CAMOFOX_AUTH_MODE=disabled \
  -v ~/.camofox:/home/node/.camofox \
  camofox-browser
```

## Makefile Targets (from source)

```bash
make up       # Build + start default container
make down     # Stop + remove container
make reset    # Clean rebuild
make build    # Build image only
make fetch    # Download binaries without building
```
