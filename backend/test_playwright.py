from app.services.playwright_fetcher import fetch_page_with_playwright


URL = "https://www.bbc.com/news"


html = fetch_page_with_playwright(URL)


print("Playwright fetch successful!")
print(f"HTML length: {len(html)}")
print(f"Contains HTML tag: {'<html' in html.lower()}")