# Playwright Python Browser Fallback

When the Hermes browser tool is unavailable (Camofox broken, server down, config mismatch), Playwright Python provides a standalone browser automation path.

## Setup

```bash
pip3 install playwright
playwright install chromium
```

Binary cache: `~/Library/Caches/ms-playwright/` (~260MB for Chromium + headless shell + FFmpeg)

## Common Operations

### Take a screenshot

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com')
    page.screenshot(path='/tmp/screenshot.png', full_page=True)
    browser.close()
```

### Extract page content

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com')
    content = page.content()  # full HTML
    text = page.inner_text('body')  # visible text only
    browser.close()
```

### Fill form and click

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('https://example.com/search')
    page.fill('input[name="q"]', 'search term')
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')
    page.screenshot(path='/tmp/result.png')
    browser.close()
```

### Use with vision_analyze

After taking a screenshot, use the `vision_analyze` tool to describe/analyze it:
```
vision_analyze(image_url='/tmp/screenshot.png', question='What is on this page?')
```

## Pitfalls

- **Headless mode required** in agent context — no display server available
- **Timeout on slow pages**: add `page.goto(url, timeout=60000)` for 60s timeout
- **Some sites block headless Chromium** — for anti-detection, use `p.chromium.launch(headless=True, args=['--disable-blink-features=AutomationControlled'])` or install `playwright-stealth`
- **`pip3 install playwright` may install to system Python** — check `which python3` first; on macOS with Command Line Tools it's `/usr/bin/python3` (3.9), not the Hermes venv
