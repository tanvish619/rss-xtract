from playwright.sync_api import sync_playwright


def fetch_page_with_playwright(url: str) -> str:
    with sync_playwright() as playwright:

        browser = playwright.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:
            page.goto(
                url,
                wait_until="networkidle",
                timeout=30000
            )

            html = page.content()

            return html

        finally:
            browser.close()