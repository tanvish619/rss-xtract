import httpx
import logging
from app.services.playwright_fetcher import fetch_page_with_playwright

logger = logging.getLogger("rss_xtract.fetcher")

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": (
        "text/html,application/xhtml+xml,application/xml;q=0.9,"
        "image/avif,image/webp,image/apng,*/*;q=0.8"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"macOS"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

BLOCKED_INDICATORS = [
    "access denied",
    "attention required! | cloudflare",
    "just a moment...",
    "enable javascript and cookies to continue",
    "please turn javascript on and reload the page",
    "please enable javascript",
    "your support id is",
    "incapsula_resource",
    "security check to access",
    "ddos-guard",
    "error 1007",
    "error 1007 id",
    "we are sorry an error has occurred",
    "looks like something went wrong",
    "temporarily unavailable",
    "reference id:",
    "lloyds banking group - error",
    "shieldsquare",
    "perimeterx",
    "captcha-delivery",
    "incapsula",
    "cf-browser-verification",
    "cf-mitigated",
]


def is_challenge_or_blocked(status_code: int, text: str) -> bool:
    if status_code in (401, 403, 404, 429, 503):
        return True
    lowered = text[:50000].lower()
    if any(ind in lowered for ind in BLOCKED_INDICATORS):
        return True
    return False


def is_incomplete_spa_shell(text: str) -> bool:
    """Check if HTML is a lightweight SPA/JS shell requiring browser hydration."""
    if len(text) > 200000:
        return False
    lowered = text.lower()
    spa_markers = [
        '<div id="root"></div>',
        '<div id="app"></div>',
        '<div id="__next"></div>',
        '<app-root></app-root>',
        '<app-root>',
        'class="app-root"',
        'id="spa-root"',
        'filterable-results-litcomplet',
        'filterable-presearch',
        'filterable_presearch',
        'filterable-results',
        'results-parent-container',
        'resultsparentcontainer',
        'prefilterableloader',
        'data-component="filterable-results"',
    ]
    if any(marker in lowered for marker in spa_markers):
        return True
    # If the page has indicators of dynamic client components
    if "<body" in lowered and len(text) < 160000:
        if "data-component" in lowered or "ng-app" in lowered or "v-app" in lowered or "prefilterable" in lowered or "presearch" in lowered:
            return True
    return False


def fetch_page(url: str, rendering_mode: str = "request") -> str:
    """Fetch website HTML using normal HTTP request with automatic browser fallback."""
    if rendering_mode == "js":
        return fetch_page_with_playwright(url)

    # Attempt standard HTTP request first
    http_error = None
    try:
        with httpx.Client(
            headers=BROWSER_HEADERS,
            timeout=25,
            follow_redirects=True,
            verify=False,
        ) as client:
            response = client.get(url)

            # Let httpx handle automatic decompression, with fallback decoding
            try:
                body_text = response.text
            except Exception:
                encoding = response.encoding or "utf-8"
                try:
                    body_text = response.content.decode(encoding, errors="replace")
                except Exception:
                    body_text = response.content.decode("utf-8", errors="replace")

            # Check if blocked by Cloudflare/WAF or received 403/404
            if is_challenge_or_blocked(response.status_code, body_text):
                logger.info(
                    "HTTP status %s or challenge for %s. Falling back to Playwright.",
                    response.status_code,
                    url,
                )
                return fetch_page_with_playwright(url)

            # Check if empty SPA shell
            if is_incomplete_spa_shell(body_text):
                logger.info(
                    "SPA shell detected for %s. Falling back to Playwright.",
                    url,
                )
                return fetch_page_with_playwright(url)

            response.raise_for_status()
            return body_text

    except Exception as exc:
        logger.warning(
            "HTTP fetch failed for %s (%s). Attempting Playwright fallback.",
            url,
            exc,
        )
        http_error = exc

    # Fallback to Playwright if HTTP failed
    try:
        return fetch_page_with_playwright(url)
    except Exception as playwright_exc:
        # If Playwright also fails, re-raise with detailed context
        raise RuntimeError(
            f"Failed to fetch {url}. HTTP error: {http_error}. Playwright error: {playwright_exc}"
        ) from playwright_exc