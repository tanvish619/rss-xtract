import logging

from playwright.sync_api import sync_playwright

logger = logging.getLogger("rss_xtract.playwright")


PLAYWRIGHT_LAUNCH_ARGS = [
    "--disable-blink-features=AutomationControlled",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    "--disable-dev-shm-usage",
    "--disable-web-security",
    "--ignore-certificate-errors",
    "--disable-features=IsolateOrigins,site-per-process",
]


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)


COOKIE_BUTTON_SELECTORS = [
    "#onetrust-accept-btn-handler",
    "#accept-cookies",
    "#accept-all-cookies",
    "#CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll",
    "#didomi-notice-agree-button",
    "#accept-choices",
    ".cookie-accept",
    ".accept-cookies-button",
    "button[data-testid='cookie-accept']",
    "button[id*='cookie'][id*='accept']",
    "button[id*='cookie'][id*='agree']",
    "button:has-text('Accept All')",
    "button:has-text('Accept all')",
    "button:has-text('Accept all cookies')",
    "button:has-text('Tout accepter')",
    "button:has-text('Alle akzeptieren')",
    "button:has-text('Aceptar todas')",
    "button:has-text('Accetta tutti')",
    "button:has-text('Godkänn alla')",
    "button:has-text('Accept')",
    "button:has-text('I Agree')",
    "button:has-text('Agree')",
]


def fetch_page_with_playwright(url: str) -> str:
    """Fetch website HTML using a headless Chromium browser with stealth and dynamic content waiting."""
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=True,
            args=PLAYWRIGHT_LAUNCH_ARGS,
        )

        context = browser.new_context(
            user_agent=USER_AGENT,
            viewport={"width": 1920, "height": 1080},
            locale="en-GB",
            timezone_id="America/New_York",
            ignore_https_errors=True,
            java_script_enabled=True,
            extra_http_headers={
                "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
                "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": '"macOS"',
                "Upgrade-Insecure-Requests": "1",
            },
        )

        page = context.new_page()

        # Stealth: mask webdriver flag and realistic plugins
        page.add_init_script(
            """
            delete navigator.__proto__.webdriver;
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
            Object.defineProperty(navigator, 'languages', { get: () => ['en-GB', 'en-US', 'en'] });
            Object.defineProperty(navigator, 'plugins', { get: () => [1, 2, 3, 4, 5] });
            """
        )

        try:
            try:
                # Load document with networkidle preference, fallback to domcontentloaded
                page.goto(
                    url,
                    wait_until="networkidle",
                    timeout=20000,
                )
            except Exception:
                try:
                    page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=25000,
                    )
                except Exception as goto_err:
                    logger.warning(
                        "Playwright goto warning for %s: %s",
                        url,
                        goto_err,
                    )

            # Give the page an initial opportunity to initialize
            try:
                page.wait_for_timeout(1000)
            except Exception:
                pass

            # Try to automatically dismiss common cookie banners.
            for selector in COOKIE_BUTTON_SELECTORS:
                try:
                    btn = page.locator(selector).first
                    if btn.is_visible(timeout=500):
                        btn.click(timeout=1500)
                        page.wait_for_timeout(500)
                        break
                except Exception:
                    continue

            # Wait for dynamically rendered content and AJAX API requests to populate.
            DYNAMIC_CONTENT_SELECTORS = [
                "a.filterable-results-total-result",
                "[class*='filterable-results-total-result']",
                "main article",
                "article",
                "li.card-article",
                "li.theme-selector-content__item",
                "div.c-company-news-list__wrap",
                "div.tab-item-container",
                "article.ei_cardboarditem",
                "article.has-edit-button",
                "div.sub-article",
                "[class*='press-release']",
                "[class*='news-item']",
            ]

            max_checks = 20  # up to 10 seconds
            stable_checks = 0
            populated_checks = 0
            previous_html_length = -1

            for check_idx in range(max_checks):
                try:
                    # Check if dynamic article cards/results are genuinely populated with content
                    has_populated_cards = False
                    for d_sel in DYNAMIC_CONTENT_SELECTORS:
                        try:
                            substantive_count = page.evaluate(
                                """(selector) => {
                                const els = document.querySelectorAll(selector);
                                let count = 0;
                                for (const el of els) {
                                    if (el.closest('header, nav, footer, .header, .footer, .nav, .menu')) continue;
                                    const txt = (el.innerText || el.textContent || '').trim();
                                    if (txt.length >= 20) count++;
                                }
                                return count;
                            }""",
                                d_sel,
                            )
                            if substantive_count >= 2:
                                has_populated_cards = True
                                break
                        except Exception:
                            continue

                    current_html_length = page.locator("html").evaluate(
                        "(element) => element.outerHTML.length"
                    )

                    if current_html_length == previous_html_length:
                        stable_checks += 1
                    else:
                        stable_checks = 0

                    if has_populated_cards:
                        populated_checks += 1

                    previous_html_length = current_html_length

                    # If populated cards exist with substantive text for at least 2 checks (~1s)
                    if populated_checks >= 2:
                        break

                    # If after at least 5 seconds the DOM is completely stable
                    if check_idx >= 10 and stable_checks >= 4:
                        break

                except Exception as wait_err:
                    logger.debug(
                        "DOM stability check failed for %s: %s",
                        url,
                        wait_err,
                    )
                    break

                page.wait_for_timeout(500)

            # Purge cookie overlays, consent dialogs, and anti-clickjacking styles
            # from the live DOM before capturing final HTML.
            try:
                page.evaluate("""() => {
                    const cookieSels = [
                        "[id*='onetrust']", "[class*='onetrust']", ".onetrust-pc-dark-filter",
                        "[id*='CookieReports']", "[class*='CookieReports']", "[id*='wscr']", "[class*='wscr']",
                        "[id*='cookiebanner']", "[id*='cookie-banner']", "[id*='cookie-consent']", "[id*='CookieConsent']",
                        "[id*='CybotCookiebot']", "[class*='CybotCookiebot']", "#CybotCookiebotDialog",
                        "[id*='didomi']", "[class*='didomi']",
                        "[id*='usercentrics']", "[class*='usercentrics']",
                        "[class*='cookie-overlay']", "[class*='cookie-backdrop']", "[class*='consent-banner']",
                        "[class*='modal-backdrop']", ".modal-backdrop", ".overlay-backdrop",
                        "section.cookie-component", "#onetrust-consent-sdk"
                    ];
                    cookieSels.forEach(s => {
                        document.querySelectorAll(s).forEach(el => el.remove());
                    });
                    document.querySelectorAll("style").forEach(s => {
                        const css = s.textContent || "";
                        if (/body\s*\{[^}]*display\s*:\s*none/i.test(css) && /important/i.test(css)) s.remove();
                    });
                }""")
            except Exception:
                pass

            html = page.content()

            if not html or len(html) < 200:
                raise RuntimeError(
                    f"Playwright returned empty content for {url}"
                )

            logger.info(
                "Playwright rendered %s (%d HTML characters)",
                url,
                len(html),
            )

            return html

        finally:
            try:
                page.close()
            except Exception:
                pass

            try:
                context.close()
            except Exception:
                pass

            try:
                browser.close()
            except Exception:
                pass