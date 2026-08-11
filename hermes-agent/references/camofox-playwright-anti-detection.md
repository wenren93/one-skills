# Playwright Anti-Detection Patterns

When Camofox is unavailable and you need to scrape bot-protected sites (Cloudflare, Akamai, custom anti-bot), use Playwright with anti-detection measures.

## Prerequisites

```bash
pip3 install playwright
playwright install chromium
```

## Minimal Anti-Detection Template

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True,
        args=['--disable-blink-features=AutomationControlled']
    )
    context = browser.new_context(
        viewport={'width': 1440, 'height': 900},
        user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    )
    page = context.new_page()

    # Hide webdriver flag (key detection vector)
    page.add_init_script('Object.defineProperty(navigator, "webdriver", {get: () => undefined});')

    page.goto('https://target-site.com', timeout=30000)
    page.wait_for_timeout(5000)  # Wait for JS rendering

    page.screenshot(path='/tmp/screenshot.png', full_page=True)
    browser.close()
```

## Key Anti-Detection Techniques

| Technique | Why it matters |
|-----------|---------------|
| `--disable-blink-features=AutomationControlled` | Removes `navigator.automationControlled` flag |
| Custom `user_agent` | Default Playwright UA contains "HeadlessChrome" |
| `navigator.webdriver = undefined` | Many bot detectors check this property |
| `viewport` set explicitly | Default 1280x720 is a common bot fingerprint |
| `page.wait_for_timeout()` | SPA sites need time for JS rendering |

## Site-Specific Notes

### time.geekbang.com (极客时间)
- Requires anti-detection to render at all (returns empty HTML without it)
- Articles behind login/paywall show blank content area even with anti-detection
- API endpoint `https://time.geekbang.org/serv/v1/article` may work with `{"id":"<article_id>"}` POST body, but requires auth cookies

## Generating PDFs from Web Pages

```python
# Playwright can generate PDF directly (Chromium only)
page.pdf(
    path='/tmp/output.pdf',
    format='A4',
    print_background=True,  # Include backgrounds/images
    margin={'top': '20mm', 'bottom': '20mm', 'left': '15mm', 'right': '15mm'}
)
```

**Pitfall:** `page.pdf()` requires headless mode. It also uses Chromium's print layout which may differ from visual rendering. For exact visual reproduction, use `full_page=True` screenshot + convert PNG to PDF with `img2pdf` or similar.

## When to Use This vs Camofox

- **Camofox**: Engine-level fingerprint spoofing, persistent sessions, Firefox-based. Best for heavy bot protection.
- **Playwright anti-detection**: Lighter weight, Chromium-based, no persistent sessions. Good enough for most sites with basic bot detection.
- **Plain Chrome headless**: No anti-detection. Fine for screenshots of non-protected sites.
